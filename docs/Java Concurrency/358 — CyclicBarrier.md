---
layout: default
title: "CyclicBarrier"
parent: "Java Concurrency"
nav_order: 358
permalink: /java-concurrency/cyclicbarrier/
number: "358"
category: Java Concurrency
difficulty: ★★☆
depends_on: Thread, CountDownLatch, Thread Lifecycle
used_by: Parallel Algorithms, Iterative Simulations, Batch Processing
tags: #java, #concurrency, #synchronizer, #barrier, #coordination
---

# 358 — CyclicBarrier

`#java` `#concurrency` `#synchronizer` `#barrier` `#coordination`

⚡ TL;DR — CyclicBarrier makes N threads wait for each other at a common meeting point (barrier), then releases all simultaneously — and unlike CountDownLatch, it resets automatically for the next round.

| #358 | category: Java Concurrency
|:---|:---|:---|
| **Depends on:** | Thread, CountDownLatch, Thread Lifecycle | |
| **Used by:** | Parallel Algorithms, Iterative Simulations, Batch Processing | |

---

### 📘 Textbook Definition

`java.util.concurrent.CyclicBarrier` is initialised with a party count N. Each thread calls `await()` when it reaches the barrier point. When the Nth thread arrives, all N threads are released simultaneously, and the barrier resets to N automatically (hence "cyclic"). An optional `Runnable` barrierAction executes once per cycle, in the last arriving thread, before the others are released.

---

### 🟢 Simple Definition (Easy)

CyclicBarrier is a waiting room: you don't leave until everyone shows up. Once all N arrive, everyone leaves together — and the waiting room is ready for the next group. CountDownLatch was a one-shot event; CyclicBarrier is a recurring rendezvous.

---

### 🔵 Simple Definition (Elaborated)

CyclicBarrier is ideal for parallel algorithms with multiple phases: each thread does its phase-1 work, hits the barrier to wait for all others, then all move to phase-2 together. Repeat for each phase. The barrierAction runs between phases (e.g., merge partial results, reset shared state) — it runs exactly once per cycle in the context of the last arriving thread before all are released.

---

### 🔩 First Principles Explanation

```
CountDownLatch             CyclicBarrier
───────────────────────── ─────────────────────────────
One-shot                  Reusable (cyclic)
Asymmetric: N events,     Symmetric: N parties, all wait
M waiters                 for each other
Cannot reset              Auto-resets after each cycle
No barrierAction          Optional barrierAction per cycle
count can be > waiting    parties must all call await()

CyclicBarrier lifecycle:
  Round 1: T1.await, T2.await, T3.await (3rd = last → releases all)
           ↳ barrierAction runs first (in T3's thread)
           ↳ all 3 threads released
  Round 2: barrier auto-reset to 3 → same sequence repeats
  Round 3: ...
```

---

### 🧠 Mental Model / Analogy

> A pit-stop in a relay race. All N runners must arrive at the pit stop before anyone continues. The last runner to arrive triggers the pit crew action (barrierAction — refuel, change tyres). Then everyone runs the next lap together. Every lap, the pit stop resets.

---

### ⚙️ How It Works

```
new CyclicBarrier(int parties)
new CyclicBarrier(int parties, Runnable barrierAction)

int await()                → wait at barrier; returns arrival index (0=last)
int await(long, TimeUnit)  → timed wait; throws TimeoutException
void reset()               → manually reset (breaks waiting threads — use with care)
int  getNumberWaiting()    → how many have arrived so far (diagnostic)
int  getParties()          → N configured

BrokenBarrierException thrown if:
  → A thread is interrupted while waiting at the barrier
  → reset() called while threads are waiting
  → A Thread threw an exception in the barrierAction
  Once broken, all future await() calls throw BrokenBarrierException
```

---

### 🔄 How It Connects

```
CyclicBarrier
  ├─ vs CountDownLatch  → cyclic, symmetric, same count of parties and waiters
  ├─ vs Phaser          → Phaser more flexible (dynamic parties, multiple phases)
  ├─ barrierAction      → merge results between phases (runs in last arriving thread)
  └─ BrokenBarrierException → propagates to all waiting threads if one fails
```

---

### 💻 Code Example

```java
// Multi-phase parallel computation
int threads = 4;
double[][] data = initData(threads);
CyclicBarrier barrier = new CyclicBarrier(threads, () -> {
    // barrierAction: runs once between each phase (in last arriving thread)
    System.out.println("Phase complete — all threads synced");
    mergePartialResults(data);
});

for (int i = 0; i < threads; i++) {
    final int id = i;
    pool.submit(() -> {
        // Phase 1: parallel computation
        computePhase1(data[id]);
        barrier.await();   // wait for all threads to finish phase 1

        // Phase 2: all threads proceed together
        computePhase2(data[id]);
        barrier.await();   // wait again before phase 3

        // Phase 3: final pass
        computePhase3(data[id]);
    });
}
```

```java
// Detecting broken barrier — always handle BrokenBarrierException
for (int i = 0; i < N; i++) {
    final int id = i;
    pool.submit(() -> {
        try {
            doWork(id);
            barrier.await();
        } catch (InterruptedException e) {
            Thread.currentThread().interrupt();
        } catch (BrokenBarrierException e) {
            // Another thread was interrupted or timed out — abort this phase
            System.err.println("Thread " + id + ": barrier broken, skipping phase");
        }
    });
}
```

---

### ⚠️ Common Misconceptions

| ❌ Wrong Belief | ✅ Correct Reality |
|---|---|
| CyclicBarrier and CountDownLatch are interchangeable | CDL is one-shot and asymmetric; CB is cyclic and symmetric |
| barrierAction runs in a separate thread | It runs in the thread of the LAST party to arrive at the barrier |
| BrokenBarrierException only affects the triggering thread | It propagates to ALL threads currently waiting at the barrier |
| reset() is safe to call while threads are waiting | `reset()` while threads are waiting causes BrokenBarrierException for all of them |

---

### 🔥 Pitfalls in Production

**Pitfall 1: Unequal party participation — one thread misses await()**

```java
// If any thread fails to call await() (exception, early return):
// All others wait forever (or until timed await expires)
// Fix: always use timed await + try/finally
try {
    doWork();
    barrier.await(30, TimeUnit.SECONDS);
} catch (TimeoutException e) {
    barrier.reset(); // or abandon the computation
}
```

**Pitfall 2: Exception in barrierAction breaks all waiting threads**

```java
// If barrierAction throws:
CyclicBarrier barrier = new CyclicBarrier(3, () -> {
    throw new RuntimeException("merge failed"); // ← breaks barrier for all threads
});
// All threads get BrokenBarrierException on their await()
// Fix: handle exceptions in barrierAction, don't propagate
```

---

### 🔗 Related Keywords

- **[CountDownLatch](./078 — CountDownLatch.md)** — one-shot cousin; wait for N events
- **[Phaser](./096 — Phaser.md)** — flexible multi-phase replacement for CyclicBarrier
- **[Semaphore](./080 — Semaphore.md)** — resource permit control
- **[ForkJoinPool](./084 — ForkJoinPool.md)** — alternative for parallel divide-and-conquer

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────────┐
│ KEY IDEA     │ N threads all meet at barrier; all released   │
│              │ together; barrier auto-resets for next round  │
├──────────────┼───────────────────────────────────────────────┤
│ USE WHEN     │ Multi-phase parallel algorithms where all     │
│              │ threads must complete phase N before phase N+1│
├──────────────┼───────────────────────────────────────────────┤
│ AVOID WHEN   │ Waiting for N events (not N threads) →        │
│              │ CountDownLatch; dynamic party count → Phaser  │
├──────────────┼───────────────────────────────────────────────┤
│ ONE-LINER    │ "Everyone waits at the pit stop;              │
│              │  then everyone races the next lap together"   │
├──────────────┼───────────────────────────────────────────────┤
│ NEXT EXPLORE │ CountDownLatch → Phaser → ForkJoinPool →      │
│              │ BrokenBarrierException handling               │
└──────────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** 4 threads use a CyclicBarrier(4). In round 2, one thread throws an exception before calling `await()`. What happens to the other 3 threads waiting at the barrier? How should they handle this?

**Q2.** The `barrierAction` runs in "the last arriving thread." Why does this matter? Could you safely use thread-local variables inside the barrierAction?

**Q3.** When would you choose `Phaser` over `CyclicBarrier`? Give a concrete scenario where CyclicBarrier's fixed party count is a limitation.

