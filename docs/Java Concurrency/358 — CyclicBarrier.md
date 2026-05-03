---
layout: default
title: "CyclicBarrier"
parent: "Java Concurrency"
nav_order: 358
permalink: /java-concurrency/cyclicbarrier/
number: "0358"
category: Java Concurrency
difficulty: ★★★
depends_on: Thread, CountDownLatch, Runnable, ExecutorService
used_by: Parallel Algorithms, Phased Computation, Monte Carlo Simulation
related: CountDownLatch, Phaser, Semaphore, Fork/Join
tags:
  - concurrency
  - synchronization
  - barrier
  - java
  - advanced
  - thread
---

# 358 — CyclicBarrier

⚡ TL;DR — CyclicBarrier blocks a fixed number of threads until all have arrived at a common barrier point, then optionally runs a barrier action and releases them all — reusable across multiple phases unlike CountDownLatch.

| #0358           | Category: Java Concurrency                                      | Difficulty: ★★★ |
| :-------------- | :-------------------------------------------------------------- | :-------------- |
| **Depends on:** | Thread, CountDownLatch, Runnable, ExecutorService               |                 |
| **Used by:**    | Parallel Algorithms, Phased Computation, Monte Carlo Simulation |                 |
| **Related:**    | CountDownLatch, Phaser, Semaphore, Fork/Join                    |                 |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
You have 8 threads performing parallel matrix multiplication. Each thread computes its shard of the result. Before phase 2 can begin, ALL 8 threads must finish phase 1 — you can't start combining partial results until every partial result exists. Without a reusable barrier, you'd need to create a new `CountDownLatch(8)` for each of the 4 phases, passing latches around and resetting them manually.

**THE BREAKING POINT:**
`CountDownLatch` is one-shot — once it counts to zero it can't be reset. For algorithms with multiple synchronization phases (matrix operations, game simulations, iterative solvers), you need a barrier that automatically resets after each phase completes, not a disposable latch per phase.

**THE INVENTION MOMENT:**
`CyclicBarrier` encapsulates the pattern: N threads wait → all arrive → optional barrier action runs → all released → barrier resets for next cycle. "Cyclic" means it can be used repeatedly for each phase of a phased computation. No latch disposal. No manual reset. Thread-safe by design.

---

### 📘 Textbook Definition

**CyclicBarrier** is a synchronizer in `java.util.concurrent` that lets a set of threads all wait for each other to reach a common barrier point. Constructed with a party count N and an optional `Runnable` barrier action. Each thread calls `await()` when it reaches the barrier; `await()` blocks until all N threads have called it. When the last thread calls `await()`, the optional barrier action runs in that thread, then all N threads are released simultaneously. The barrier automatically resets after each cycle, making it suitable for algorithms with repeated synchronization phases. If any thread is interrupted or times out at the barrier, the barrier is put in a "broken" state and all waiting threads receive `BrokenBarrierException`.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
N threads each call `await()` — nobody moves until everybody arrives, then everyone moves at once.

**One analogy:**

> CyclicBarrier is like a relay race where each leg's baton handoff requires ALL runners on the team to have finished their previous leg before anyone starts the next. Every runner checks in at the team tent. When the last runner checks in, the coach (barrier action) reviews the splits, then shouts "GO!" and all runners start the next leg simultaneously.

**One insight:**
The "cyclic" in CyclicBarrier is the critical differentiator from CountDownLatch. CountDownLatch is a one-time gate; CyclicBarrier is a repeatable checkpoint. For multi-phase parallel algorithms, CyclicBarrier eliminates the need to create and discard a new synchronizer for each phase.

---

### 🔩 First Principles Explanation

**CORE INVARIANTS:**

1. `CyclicBarrier(int parties)`: create with party count.
2. `await()` blocks the calling thread until all `parties` threads have called `await()`.
3. After all parties arrive, the barrier action (if provided) runs in the last-arriving thread.
4. After release, the barrier resets to the initial count — ready for the next cycle.
5. If any thread times out or is interrupted, all threads at the barrier get `BrokenBarrierException`.

**DERIVED DESIGN:**

```
CYCLICBARRIER LIFECYCLE (3 parties):

Phase 1:
  Thread A: await() → blocks
  Thread B: await() → blocks
  Thread C: await() → ALL arrived → barrier action runs
                    → All 3 threads released simultaneously
                    → Barrier resets (count back to 3)

Phase 2:
  Thread A: await() → blocks
  Thread B: await() → blocks
  Thread C: await() → ALL arrived → barrier action runs
                    → All 3 threads released
```

```
INTERNAL STATE MACHINE:
State: count = parties
  → Thread calls await(): count--
  → count > 0: thread blocks on ReentrantLock condition
  → count == 0: signal all + run barrier action + reset count
  → Broken state (on interrupt/timeout): all awaiters throw
    BrokenBarrierException
```

**THE TRADE-OFFS:**

- **Gain:** Reusable barrier for phased algorithms; atomic "all-or-none" release.
- **Cost:** If even one thread dies or is interrupted, the entire barrier breaks (BrokenBarrierException for all). No partial completion — all-or-nothing synchronization.

---

### 🧪 Thought Experiment

**SETUP:**
A Monte Carlo simulation runs 4 worker threads. Each iteration: each thread computes 1000 random samples, then the barrier aggregates results, then all threads start the next iteration.

**WITHOUT CyclicBarrier:**
You'd need to create `CountDownLatch(4)` before each iteration, pass it to each worker, and after release create another latch for the next iteration. After 10,000 iterations, you've created 10,000 CountDownLatch objects, strained GC, and cluttered code with latch creation and distribution logic.

**WITH CyclicBarrier:**
One `CyclicBarrier(4, aggregationAction)` created once. Workers call `barrier.await()` at the end of each iteration. The aggregation action runs automatically in the last thread. Barrier resets. Next iteration begins. Zero GC pressure from barrier creation; code is clean.

**THE INSIGHT:**
CyclicBarrier's reusability is not just a convenience — at scale (thousands of iterations), it's the difference between O(1) synchronizer creation and O(N) synchronizer creation, with the latter causing measurable GC pressure.

---

### 🧠 Mental Model / Analogy

> CyclicBarrier is a revolving door at a building exit where a security guard counts people going through. Every 10 people must collect in the lobby. When exactly 10 are waiting, the guard (barrier action) checks everyone's badge, then opens the door for all 10 at once. The door then resets — next 10 people start accumulating. Nobody can leave early; nobody is left behind.

- "10 people in lobby" → all N threads calling await()
- "Guard checks badges" → optional Runnable barrier action
- "Door opens for all 10" → simultaneous release of all waiting threads
- "Door resets" → barrier resets its count for the next cycle
- "One person has a medical emergency" → thread interrupted → BrokenBarrierException for everyone

Where this analogy breaks down: in the physical revolving door analogy, late arrivals are delayed to the next group. With CyclicBarrier, if a thread crashes before calling `await()`, the barrier never completes — all waiting threads are stuck (until timeout or interrupted).

---

### 📶 Gradual Depth — Four Levels

**Level 1 — What it is (anyone can understand):**
CyclicBarrier is a waiting point for a fixed group of threads. Every thread in the group must arrive at the barrier before any of them can continue. Once all have arrived, they all proceed together. Then the barrier resets so the group can do it again.

**Level 2 — How to use it (junior developer):**
Create `CyclicBarrier barrier = new CyclicBarrier(N, barrierAction)`. Each thread calls `barrier.await()` when it reaches the sync point. Catch `BrokenBarrierException` — thrown when another thread was interrupted or timed out. Use `barrier.await(timeout, unit)` to avoid indefinite blocking. Always plan for the broken barrier case: log and fail fast, don't silently continue with incomplete data.

**Level 3 — How it works (mid-level engineer):**
Internally, CyclicBarrier uses a `ReentrantLock` and a `Condition`. It tracks current count. Each `await()` decrements count under lock; if count > 0, calls `condition.await()` (releases lock, suspends thread). When count reaches 0: the last thread runs the barrier action, calls `condition.signalAll()`, then resets the generation and count. The `generation` concept (an inner class) tracks which cycle we're in — this is how "broken barrier" state is isolated to one cycle without affecting future cycles. If the barrier is broken, `isBroken()` returns true and subsequent `await()` calls throw immediately.

**Level 4 — Why it was designed this way (senior/staff):**
CyclicBarrier's generation model (an inner `Generation` class that gets replaced at each reset) elegantly handles the race condition between barrier completion and the next cycle's start. Without it, a slow thread could call `await()` for phase 2 while some threads are still in the phase 1 barrier, causing incorrect counting. The generation acts as an epoch: each `await()` registers against the current generation; when the barrier resets, a new generation is created. Any thread that arrives after the reset joins the new generation, not the old one. This also explains why `CyclicBarrier.reset()` (manual reset) is dangerous: it breaks the current generation, forcing any waiting threads to throw `BrokenBarrierException`, which may leave the system in an inconsistent state if not handled carefully.

---

### ⚙️ How It Works (Mechanism)

```java
// CyclicBarrier internal structure (simplified):
class CyclicBarrier {
    private final ReentrantLock lock;
    private final Condition trip;
    private final int parties;      // total parties required
    private final Runnable barrierCommand; // optional action
    private Generation generation;  // tracks current cycle
    private int count;              // remaining threads to wait

    // Each cycle creates a new generation object:
    private static class Generation {
        boolean broken = false;     // was this generation broken?
    }

    public int await() throws BrokenBarrierException {
        lock.lock();
        try {
            final Generation g = generation;
            if (g.broken) throw new BrokenBarrierException();
            int index = --count;
            if (index == 0) {
                // Last thread: run barrier action and reset
                barrierCommand.run(); // if provided
                nextGeneration();     // signal all + reset count
                return 0;
            }
            // Not last: wait until generation changes or broken
            for (;;) {
                trip.await(); // releases lock, suspends
                if (g != generation) return index; // released OK
                if (g.broken) throw new BrokenBarrierException();
            }
        } finally { lock.unlock(); }
    }
}
```

```
TIMING DIAGRAM (4 parties):
Time ─────────────────────────────────────────────►

Thread 1: ──work──│await()─────────────────────────│proceed──
Thread 2: ────work─────│await()─────────────────────│proceed──
Thread 3: ──────────work──────│await()──────────────│proceed──
Thread 4: ───────────────────────────work──│await() │proceed──
                                           barrier  │
                                           action ──┘
                                           runs here (in T4)
```

---

### 🔄 The Complete Picture — End-to-End Flow

```
NORMAL FLOW:
[Algorithm Phase N Start]
→ Each of N threads executes its work shard
→ Each thread calls barrier.await()
→ [CyclicBarrier ← YOU ARE HERE]
→ All N threads blocked until last arrives
→ Barrier action (optional aggregation) runs
→ All N threads released simultaneously
→ Barrier resets → Algorithm Phase N+1 begins

FAILURE PATH:
Thread 3 throws exception before calling await()
→ Thread 3 never arrives at barrier
→ Threads 1, 2, 4 wait indefinitely (unless timeout set)
→ After timeout: BrokenBarrierException thrown in T1, T2, T4
→ Observable: BrokenBarrierException in logs for all awaiting threads
→ Fix: wrap work in try-catch; call barrier.reset() or cancel
       the entire task, then reconstruct and retry

WHAT CHANGES AT SCALE:
With 1000+ parties, the "last thread releases all" design
means the last thread bears the barrier-action cost alone.
Consider moving aggregation outside the barrier action for
expensive operations to avoid blocking the release. Also,
lock contention on the ReentrantLock increases with party
count; Phaser is better for >64 parties.
```

---

### 💻 Code Example

```java
import java.util.concurrent.*;

// Example 1 — Parallel phase computation
int NUM_THREADS = 4;
int NUM_PHASES = 3;
double[] partialResults = new double[NUM_THREADS];

// Barrier action: aggregate partial results after each phase
Runnable aggregator = () -> {
    double total = 0;
    for (double r : partialResults) total += r;
    System.out.println("Phase result: " + total);
};

CyclicBarrier barrier = new CyclicBarrier(NUM_THREADS, aggregator);

ExecutorService pool = Executors.newFixedThreadPool(NUM_THREADS);
for (int t = 0; t < NUM_THREADS; t++) {
    final int threadId = t;
    pool.submit(() -> {
        for (int phase = 0; phase < NUM_PHASES; phase++) {
            // Phase work
            partialResults[threadId] = computeShard(threadId, phase);

            try {
                barrier.await(); // wait for all threads
                // After barrier: aggregator has run, all released
            } catch (InterruptedException e) {
                Thread.currentThread().interrupt();
                return; // bail out cleanly
            } catch (BrokenBarrierException e) {
                System.err.println("Barrier broken, aborting");
                return;
            }
            // All threads now in phase+1 together
        }
    });
}
pool.shutdown();

// Example 2 — Timeout to avoid indefinite blocking
try {
    int arrivalIndex = barrier.await(5, TimeUnit.SECONDS);
    // arrivalIndex: 0 = last to arrive, parties-1 = first
} catch (TimeoutException e) {
    barrier.reset(); // breaks current generation, triggers
                     // BrokenBarrierException for all waiters
} catch (BrokenBarrierException e) {
    // Another thread was interrupted/timed out first
    handleBrokenBarrier();
}
```

---

### ⚖️ Comparison Table

| Synchronizer      | Reusable         | Party Count                   | Barrier Action  | Best For                         |
| ----------------- | ---------------- | ----------------------------- | --------------- | -------------------------------- |
| **CyclicBarrier** | Yes (auto-reset) | Fixed at creation             | Yes (Runnable)  | Fixed-size phased algorithms     |
| CountDownLatch    | No (one-shot)    | Fixed at creation             | No              | One-time event wait              |
| Phaser            | Yes + dynamic    | Dynamic (register/deregister) | Via onAdvance() | Variable-party phased algorithms |
| Semaphore         | Yes              | N/A (count, not parties)      | No              | Resource pool access control     |

**How to choose:** Use `CyclicBarrier` for fixed-N threads with multiple phases. Use `CountDownLatch` for one-time synchronization (e.g., "wait for service to start"). Use `Phaser` when the number of parties changes between phases (e.g., some threads complete early).

---

### ⚠️ Common Misconceptions

| Misconception                                        | Reality                                                                                                                                                                                                                             |
| ---------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| CyclicBarrier is just a resettable CountDownLatch    | CountDownLatch counts down from N to 0; CyclicBarrier counts up from 0 to N (all parties arrive). More importantly, CyclicBarrier has a barrier action and broken-barrier state that CountDownLatch lacks entirely                  |
| The barrier action runs in a separate thread         | The barrier action runs in the LAST thread to call await(). This thread pays the action's execution cost before releasing all others — expensive actions delay all waiting threads                                                  |
| BrokenBarrierException means a programming error     | It means one party was interrupted or timed out. This is a normal operational condition for interruptible computations; handle it by retrying or cancelling the task, not logging it as a bug                                       |
| CyclicBarrier.reset() is a safe way to retry a phase | reset() breaks the current generation, causing BrokenBarrierException for all currently waiting threads. It is safe only when no threads are currently at the barrier — using it while threads are waiting leads to race conditions |

---

### 🚨 Failure Modes & Diagnosis

**Deadlock: Thread Never Reaches Barrier**

**Symptom:** Application hangs; all N-1 threads waiting at barrier indefinitely; one thread stuck in work phase.

**Root Cause:** One party thread throws an uncaught exception or enters an infinite loop before calling `await()`, so the count never reaches N.

**Diagnostic Command:**

```bash
# Find threads blocked at CyclicBarrier.await():
jstack <pid> | grep -A 5 "CyclicBarrier"

# Or with jcmd:
jcmd <pid> Thread.print | grep -A 10 "CyclicBarrier"
```

**Fix:**

```java
// WRONG: Exception before await() leaves others hanging
try {
    result = riskyComputation();
    barrier.await(); // never reached on exception
} catch (Exception e) {
    log.error("Failed", e);
    // barrier.await() skipped! — deadlock
}

// GOOD: Always call await(), even on failure
try {
    result = riskyComputation();
} catch (Exception e) {
    log.error("Failed", e);
    barrier.reset(); // break barrier, notify others
    return;
} finally {
    // Or use barrier.await() in finally to always arrive
}
```

**Prevention:** Use timeout: `barrier.await(30, TimeUnit.SECONDS)`. Or wrap the entire task in a try-finally that calls `barrier.reset()` on unexpected exit.

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**

- `Thread` — each party in a CyclicBarrier is a thread
- `CountDownLatch` — the simpler one-shot synchronizer; understand it first
- `ReentrantLock` — CyclicBarrier is implemented using ReentrantLock + Condition

**Builds On This (learn these next):**

- `Phaser` — generalized version of CyclicBarrier with dynamic party registration
- `Fork/Join Framework` — higher-level parallel decomposition using work-stealing
- `CompletableFuture` — async composition without explicit barriers

**Alternatives / Comparisons:**

- `CountDownLatch` — one-shot, no barrier action, simpler; use when no phase repetition needed
- `Phaser` — dynamic party count; use when threads may join or leave between phases
- `Semaphore` — controls concurrent access count, not synchronization point arrival

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ WHAT IT IS   │ Reusable barrier: N threads wait until    │
│              │ all arrive, then all proceed together     │
├──────────────┼───────────────────────────────────────────┤
│ PROBLEM IT   │ Multi-phase parallel algorithms need      │
│ SOLVES       │ repeated all-threads sync between phases  │
├──────────────┼───────────────────────────────────────────┤
│ KEY INSIGHT  │ Barrier action runs in the LAST thread;   │
│              │ any thread interrupt breaks ALL waiters   │
├──────────────┼───────────────────────────────────────────┤
│ USE WHEN     │ Fixed N threads, multiple sync phases,    │
│              │ optional per-phase aggregation needed     │
├──────────────┼───────────────────────────────────────────┤
│ AVOID WHEN   │ Party count varies per phase (use Phaser);│
│              │ one-shot event (use CountDownLatch)       │
├──────────────┼───────────────────────────────────────────┤
│ TRADE-OFF    │ Clean phased sync vs brittle to failures  │
│              │ (one broken thread breaks entire barrier) │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "A revolving door that only turns when    │
│              │  every expected person has arrived"       │
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ Phaser → Fork/Join → CompletableFuture    │
└──────────────┴───────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** CyclicBarrier's barrier action runs in the last-arriving thread. In a 16-thread Monte Carlo simulation where each phase's barrier action takes 50ms to aggregate results, calculate the total extra latency introduced by the barrier action across 1000 phases — and explain why making the barrier action asynchronous (submitting it to a thread pool instead) could reduce total runtime by a predictable amount.

**Q2.** CyclicBarrier uses a `Generation` inner class to isolate each cycle's broken-barrier state from future cycles. If the JVM thread scheduler preempts the last-arriving thread immediately after it decrements the count to 0 but before it calls `nextGeneration()`, describe the exact state of all N-1 waiting threads during that preemption window — and explain why this is safe despite appearing to be a race condition.
