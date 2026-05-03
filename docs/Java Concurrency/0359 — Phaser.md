---
layout: default
title: "Phaser"
parent: "Java Concurrency"
nav_order: 359
permalink: /java-concurrency/phaser/
number: "0359"
category: Java Concurrency
difficulty: ★★★
depends_on: CyclicBarrier, CountDownLatch, Thread, ExecutorService
used_by: Parallel Algorithms, Structured Concurrency
related: CyclicBarrier, CountDownLatch, ForkJoinPool
tags:
  - java
  - concurrency
  - deep-dive
  - synchronization
  - parallel
---

# 0359 — Phaser

⚡ TL;DR — Phaser is a flexible, reusable multi-thread synchronisation barrier that supports dynamic addition and removal of participating threads between phases — solving the fixed-party-count limitation of `CyclicBarrier`, while also supporting tiered (hierarchical) phasers for very large thread counts.

| #0359           | Category: Java Concurrency                             | Difficulty: ★★★ |
| :-------------- | :----------------------------------------------------- | :-------------- |
| **Depends on:** | CyclicBarrier, CountDownLatch, Thread, ExecutorService |                 |
| **Used by:**    | Parallel Algorithms, Structured Concurrency            |                 |
| **Related:**    | CyclicBarrier, CountDownLatch, ForkJoinPool            |                 |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
A parallel tree traversal has a variable number of threads at each level: 1 thread at the root, 2 at depth 1, 4 at depth 2, 8 at depth 3. At each depth, threads must synchronise before descending. `CyclicBarrier` has a fixed party count — you'd need a new `CyclicBarrier` for every depth level. And some threads complete early (leaf nodes) and should deregister so they don't block the remaining threads. `CyclicBarrier` has no deregistration mechanism — once committed to a party count, it is fixed.

**THE BREAKING POINT:**
Real parallel algorithms are rarely uniform — threads join at different phases, complete at different phases, and the work fan-in/fan-out varies per phase. `CyclicBarrier` requires all N threads to exist for the entire algorithm lifetime, even if half of them finish after Phase 1.

**THE INVENTION MOMENT:**
`Phaser` was introduced in Java 7 to provide `CyclicBarrier`-like multi-phase synchronisation with dynamic parties: threads can `register()` to join a phaser mid-execution and `arriveAndDeregister()` to leave without blocking everyone else.

---

### 📘 Textbook Definition

**Phaser:** A reusable synchronisation barrier (`java.util.concurrent.Phaser`) where threads can dynamically register and deregister as parties. When all registered parties arrive, the phase advances automatically. Key methods: `arrive()` (arrive without waiting), `arriveAndAwaitAdvance()` (arrive and wait), `arriveAndDeregister()` (arrive and permanently leave), `register()` (add a new party), `awaitAdvance(phase)` (wait for a specific phase).

**Phase number:** An integer (starting at 0) that increments automatically when all registered parties arrive. Wraps at `Integer.MAX_VALUE`.

**Tiered Phaser:** A parent-child Phaser hierarchy where a child Phaser's phase advance is propagated to the parent, enabling efficient coordination of very large numbers of threads without all threads contending on a single phaser.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
Phaser is a CyclicBarrier where the guest list can change between phases — threads can RSVP or leave at any time.

**One analogy:**

> A conference has multiple sessions across the day (phases). Attendees can arrive and register for later sessions and leave after the sessions they care about. The session only advances to the next topic (phase) when all registered attendees have confirmed ready. New attendees can join between sessions. This is impossible with a fixed-count meeting room (CyclicBarrier) but natural with a Phaser.

**One insight:**
`Phaser` subsumes both `CountDownLatch` and `CyclicBarrier`: a single-phase `Phaser` with fixed parties is a `CyclicBarrier`. A single-phase `Phaser` that decrements to 0 without waiting is a `CountDownLatch`. Phaser is the most general of the three — use the simpler abstraction when you don't need dynamism.

---

### 🔩 First Principles Explanation

**CORE INVARIANTS:**

1. Phase advances when `arrived == registered` (all registered parties have arrived).
2. `register()` increases the registered count; `arriveAndDeregister()` decrements both arrived and registered.
3. Phase number is monotonically increasing (wraps at Integer.MAX_VALUE).
4. A terminated Phaser (phase == Integer.MAX_VALUE or manually terminated) returns a negative phase number from `arrive()`.

**KEY METHODS:**

```
arrive()               → arrive, don't wait; returns phase number
arriveAndAwaitAdvance() → arrive AND block until phase advances; returns next phase
arriveAndDeregister()  → arrive AND permanently leave the phaser
register()             → add one party (increase registered count)
bulkRegister(n)        → add n parties
awaitAdvance(phase)    → block until phaser advances PAST given phase
getPhase()             → current phase number
getRegisteredParties() → count of currently registered parties
getArrivedParties()    → count that have arrived in current phase
onAdvance(phase, ...)  → override to run barrier action or terminate
```

**TERMINATION:**

```java
// Override onAdvance to auto-terminate after N phases:
Phaser phaser = new Phaser(1) {
    @Override
    protected boolean onAdvance(int phase, int registeredParties) {
        return phase >= 9; // terminate after phase 9 (10 phases total)
        // return true → phaser terminates (phase = Integer.MAX_VALUE)
    }
};
```

**TIERED PHASERS:**

```
Root Phaser ← manages 100 child phasers
  Child Phaser 1 ← 100 threads each
  Child Phaser 2 ← 100 threads each
  ...
  Child Phaser 100 ← 100 threads each

When all threads in Child 1 arrive, Child 1 advances.
When all children advance, Root advances.
→ 10,000 threads coordinated without all contending on one phaser.
```

**THE TRADE-OFFS:**

**Gain:** Dynamic party management (join/leave mid-execution). Tiered hierarchy for massive thread counts. Termination control via `onAdvance()`. Subsumes CountDownLatch and CyclicBarrier.

**Cost:** More complex API than `CyclicBarrier`. Slightly higher overhead (volatile reads on phase + parties). Overkill for fixed-party synchronisation. `onAdvance()` runs while phaser is locked — must be fast.

---

### 🧪 Thought Experiment

**SETUP:**
A divide-and-conquer computation: 1 coordinator thread that fans out to 8 worker threads in Phase 1. In Phase 2, only 4 workers continue (the other 4 computed leaf nodes and are done). In Phase 3, only 2 workers continue. Final aggregation is done by the coordinator.

**WITH CyclicBarrier:**

```
Problem: need 3 different CyclicBarriers (parties=9, parties=5, parties=3).
Create new barriers for each phase.
4 workers that finish Phase 1 must NOT call Phase 2's barrier.
Requires careful logic to differentiate which barrier to call.
Error-prone: if any of the 4 leaf workers accidentally calls Phase 2 barrier,
it will never complete (party count mismatch).
```

**WITH Phaser:**

```java
Phaser phaser = new Phaser(9); // 1 coordinator + 8 workers

// Phase 1: all 9 registered
for (Worker w : allWorkers) {
    w.setPhaser(phaser); w.start();
}
phaser.arriveAndAwaitAdvance(); // coordinator waits for Phase 1

// Phase 2: 4 leaf workers deregister
for (Worker leafWorker : leafWorkers) {
    phaser.arriveAndDeregister(); // arrive (Phase 1) and leave
}
// Now phaser has 5 registered (1 coordinator + 4 continuing workers)
phaser.arriveAndAwaitAdvance(); // Phase 2

// Phase 3: 2 more workers deregister
// ...clean, no new Phaser objects needed
```

---

### 🧠 Mental Model / Analogy

> Phaser is like a muster station on a cruise ship across multiple ports (phases). At each port, all currently registered passengers check in (arrive). After everyone checks in, the ship departs (phase advances). But passengers can board at intermediate ports (register) and disembark at ports before the end (arriveAndDeregister). The ship's manifest (registered parties) changes at each port. A CyclicBarrier would require the same passenger list at every port — no boarding or disembarking.

Explicit mapping:

- "ship departure" → phase advance
- "passenger checks in" → `arrive()` or `arriveAndAwaitAdvance()`
- "passenger disembarks" → `arriveAndDeregister()`
- "passenger boards mid-journey" → `register()` or `bulkRegister()`
- "all checked in" → all registered parties arrived
- "cruise ends" → `onAdvance()` returns `true` (phaser terminates)

Where this analogy breaks down: `arrive()` without waiting means the passenger can run ahead to the next activity without waiting for the ship to depart. This is useful for tasks that don't need to synchronise their start time — only their completion matters for the phase advance.

---

### 📶 Gradual Depth — Four Levels

**Level 1 — What it is (anyone can understand):**
Phaser is like a more flexible version of CyclicBarrier. It coordinates multiple threads across multiple phases, but allows threads to join or leave at any time. You use it when you have a parallel algorithm where different threads participate in different phases.

**Level 2 — How to use it (junior developer):**
Create a `Phaser(N)` for N initial parties. Each thread calls `arriveAndAwaitAdvance()` to complete a phase and wait for others. A thread that is done entirely calls `arriveAndDeregister()` — it contributes its final arrival to the current phase and removes itself from future phases. New threads call `phaser.register()` before starting. The phase number (retrieved via `getPhase()`) tells you which phase you're in.

**Level 3 — How it works (mid-level engineer):**
Phaser uses a single volatile long to encode both `phase` and `counts` (unarrived + registered). This allows atomic reads/updates of both values together via CAS. The phase is the upper 32 bits; the party counts are the lower 32 bits (split into registered and arrived). When `unarrived` reaches 0, the phase advances: `onAdvance()` is called, and if it returns false, the phase increments; if true, the phaser terminates. All waiting threads are unblocked via a lock+condition per phase (Phaser uses an internal queue).

**Level 4 — Why it was designed this way (senior/staff):**
The atomic encoding of phase+counts in a single long is the key implementation insight: it prevents race conditions where a thread reads the phase and counts separately and sees an inconsistent state (e.g., old phase with new count). The downside is that party count is limited to ~65,535 (16-bit field within the long). For larger thread counts, tiered phasers are the solution: child phasers register as a single "party" with the parent, so N child phasers × M threads = N×M total coordination capacity while only N contend on the parent. This scales to millions of threads. The `arrive()` (non-blocking) vs. `arriveAndAwaitAdvance()` (blocking) split enables producers and consumers to decouple: a producer can fire-and-forget its arrival, with a single coordinator thread monitoring the phase via `awaitAdvance()`.

---

### ⚙️ How It Works (Mechanism)

```
Phaser INTERNAL STATE (simplified):
  volatile long state = encode(phase=0, unarrived=N, registered=N)

arrive():
  CAS: state.unarrived--
  if unarrived == 0:
    call onAdvance(phase, registeredParties)
    if onAdvance returns false:
      CAS: phase++, reset unarrived = registered
    else:
      CAS: phase = TERMINATED (Integer.MAX_VALUE)
    signal all waiters

arriveAndAwaitAdvance():
  arrive()
  awaitAdvance(currentPhase)  ← blocks until phase > currentPhase

arriveAndDeregister():
  CAS: unarrived--, registered--
  if unarrived == 0: advance phase (same as above)
  does NOT wait

register():
  CAS: registered++, unarrived++

TIERED:
  Child phaser advances → if all parties of child arrived,
  child calls parent.arrive() on behalf of itself
  (child counts as ONE party to the parent)
```

---

### 🔄 The Complete Picture — End-to-End Flow

```
new Phaser(1)  ← "1" = coordinator registers itself
    ↓
For each worker: phaser.register(); submit to executor
    ↓
Coordinator calls phaser.arriveAndAwaitAdvance()
    ↓
Workers complete Phase 0 work
    ↓
Some workers: phaser.arriveAndDeregister()   ← done, leave
Other workers: phaser.arriveAndAwaitAdvance() ← continue
    ↓
Phase advances (all registered parties arrived)
    ↓
onAdvance(phase=0, ...) called
    ↓
Remaining threads released into Phase 1
    ↓
Repeat until onAdvance returns true
    ↓
Phaser terminates. getPhase() returns negative.
```

---

### 💻 Code Example

**Example 1 — Basic multi-phase with dynamic deregistration:**

```java
import java.util.concurrent.*;

public class PhasedComputation {
    public static void main(String[] args) throws Exception {
        int workers = 8;
        // Register coordinator (+1) and all workers
        Phaser phaser = new Phaser(1 + workers) {
            @Override
            protected boolean onAdvance(int phase, int registeredParties) {
                System.out.println("Phase " + phase
                    + " complete. Remaining parties: " + registeredParties);
                return registeredParties == 0; // terminate when all workers done
            }
        };

        ExecutorService exec = Executors.newFixedThreadPool(workers);
        for (int i = 0; i < workers; i++) {
            final int id = i;
            exec.submit(() -> {
                // Phase 0: all workers participate
                doWork(id, 0);
                phaser.arriveAndAwaitAdvance(); // wait for all

                // Phase 1: only even-id workers continue
                if (id % 2 == 0) {
                    doWork(id, 1);
                    phaser.arriveAndAwaitAdvance();

                    // Phase 2: only id=0 and id=4 continue
                    if (id == 0 || id == 4) {
                        doWork(id, 2);
                        phaser.arriveAndDeregister(); // done
                    } else {
                        phaser.arriveAndDeregister(); // Phase 1 done → leave
                    }
                } else {
                    phaser.arriveAndDeregister(); // Phase 0 done → leave
                }
            });
        }

        // Coordinator drives phases
        phaser.arriveAndDeregister(); // coordinator done (or use awaitAdvance)
        exec.shutdown();
        exec.awaitTermination(1, TimeUnit.MINUTES);
    }
}
```

**Example 2 — Phaser as CountDownLatch:**

```java
// Single-phase Phaser = CountDownLatch
Phaser latch = new Phaser(N + 1) { // N workers + 1 awaiter
    @Override
    protected boolean onAdvance(int phase, int parties) {
        return true; // terminate after first phase advance
    }
};

// Workers: complete work, then signal
for (Worker w : workers) {
    exec.submit(() -> {
        doWork();
        latch.arrive(); // arrive but don't wait (don't block worker thread)
    });
}

// Awaiter: wait for all workers
latch.awaitAdvance(latch.getPhase()); // blocks until all N arrive
```

**Example 3 — Tiered Phaser for 10,000 threads:**

```java
// Root phaser
Phaser root = new Phaser();

// 100 child phasers, each with 100 threads
for (int i = 0; i < 100; i++) {
    Phaser child = new Phaser(root, 100); // auto-registers with root
    for (int j = 0; j < 100; j++) {
        exec.submit(() -> {
            doWork();
            child.arriveAndAwaitAdvance();
            // When all 100 threads in this child arrive,
            // child advances AND notifies root
        });
    }
}
// Root advances when all 100 children advance
root.awaitAdvance(0); // wait for all 10,000 threads complete Phase 0
```

---

### ⚖️ Comparison Table

| Feature         | Phaser                    | CyclicBarrier  | CountDownLatch |
| --------------- | ------------------------- | -------------- | -------------- |
| Reusable        | Yes                       | Yes            | No             |
| Dynamic parties | Yes (register/deregister) | No             | No             |
| Barrier action  | Yes (onAdvance)           | Yes (Runnable) | No             |
| Tiered support  | Yes                       | No             | No             |
| JDK version     | Java 7+                   | Java 5+        | Java 5+        |
| Complexity      | High                      | Medium         | Low            |

How to choose: use `CountDownLatch` for one-shot "wait for N events". Use `CyclicBarrier` for fixed-thread multi-phase computation. Use `Phaser` when parties change between phases, or when you need tiered coordination.

---

### ⚠️ Common Misconceptions

| Misconception                                  | Reality                                                                                                                                                                                                                  |
| ---------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| "arriveAndDeregister() also waits"             | It does NOT wait. It arrives (contributing to phase completion) and removes itself, then immediately returns. If you want the final arrival to wait, use arriveAndAwaitAdvance() but that would block other threads too. |
| "Phaser is always better than CyclicBarrier"   | Phaser is more complex. For simple fixed-party barriers, CyclicBarrier is cleaner and equally performant. Use Phaser only when its additional features are needed.                                                       |
| "getPhase() returns the completed phase count" | It returns the CURRENT phase number (the phase threads are now entering). Phase 0 = first phase. After first advance: phase 1. If terminated: negative value.                                                            |
| "onAdvance runs on a dedicated thread"         | onAdvance runs on the last arriving thread, holding the phaser's internal lock. It must be fast. Any blocking in onAdvance will delay ALL waiting threads from being released.                                           |

---

### 🚨 Failure Modes & Diagnosis

**1. Phaser Never Advances (Stuck Phase)**

**Symptom:** All threads appear to be running but the phase never advances. `getPhase()` remains at the same value indefinitely. `getArrivedParties()` < `getRegisteredParties()`.

**Root Cause:** More parties are registered than have arrived. A thread called `register()` without a matching `arrive()` or `arriveAndDeregister()`. Or a thread threw an exception before calling arrive.

**Diagnostic:**

```java
// Periodic diagnostic (in a monitoring thread):
ScheduledExecutorService monitor = Executors.newSingleThreadScheduledExecutor();
monitor.scheduleAtFixedRate(() -> {
    System.out.printf("Phase: %d, Registered: %d, Arrived: %d, Unarrived: %d%n",
        phaser.getPhase(),
        phaser.getRegisteredParties(),
        phaser.getArrivedParties(),
        phaser.getUnarrivedParties());
}, 5, 5, TimeUnit.SECONDS);
```

**Fix:** Ensure every registered thread eventually calls arrive or deregister. Use try-finally:

```java
phaser.register();
try {
    doWork();
} finally {
    phaser.arriveAndDeregister();
}
```

**Prevention:** Always register immediately before work starts and deregister in a `finally` block.

---

**2. Phase Number Overflow**

**Symptom:** `getPhase()` returns a negative value. `awaitAdvance()` returns a negative value. Appears after very long-running computation.

**Root Cause:** Phase number wrapped around `Integer.MAX_VALUE` (about 2 billion phases). Extremely rare in practice but possible in long-running simulations.

**Diagnostic:** Log phase number periodically. If it approaches `Integer.MAX_VALUE / 2`, consider resetting (creating a new Phaser).

**Fix:** The Phaser specification says phase numbers wrap around (treat negative as terminated — but only if `onAdvance` returned true). For pure wrap-around (not termination), the negative value is a hint to compare against `0xFFFF_FFFF`. Practical fix: create a new Phaser if you need > 2 billion phases.

**Prevention:** Rare enough to ignore in almost all applications. Worth knowing for embedded/simulation systems.

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**

- `CyclicBarrier` — the simpler fixed-party barrier Phaser generalises
- `CountDownLatch` — the simpler single-phase wait Phaser generalises
- `Thread` — Phaser coordinates threads

**Builds On This (learn these next):**

- `ForkJoinPool` — the JDK's parallel framework; uses Phaser-like coordination internally
- `Parallel Algorithms` — multi-phase parallel algorithms that Phaser enables
- `Structured Concurrency` — Java 21 virtual thread-based coordination (conceptually related)

**Alternatives / Comparisons:**

- `CyclicBarrier` — simpler; use when party count is fixed
- `CountDownLatch` — simplest; use for single-phase one-way signal
- `ForkJoinPool` — work-stealing framework for recursive parallel tasks (different model)

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ WHAT IT IS   │ Dynamic reusable multi-phase barrier:     │
│              │ parties can register/deregister freely    │
├──────────────┼───────────────────────────────────────────┤
│ PROBLEM IT   │ CyclicBarrier's fixed party count fails   │
│ SOLVES       │ for algorithms with variable participants │
├──────────────┼───────────────────────────────────────────┤
│ KEY INSIGHT  │ arriveAndDeregister() lets threads leave  │
│              │ without blocking remaining parties        │
├──────────────┼───────────────────────────────────────────┤
│ USE WHEN     │ Threads join/leave between phases; tiered │
│              │ coordination; 10,000+ thread counts       │
├──────────────┼───────────────────────────────────────────┤
│ AVOID WHEN   │ Fixed parties, simple phases → use        │
│              │ CyclicBarrier (simpler API)               │
├──────────────┼───────────────────────────────────────────┤
│ TRADE-OFF    │ Maximum flexibility vs. higher complexity │
│              │ and slightly more overhead than CBr       │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "The guest list changes between meetings; │
│              │  meetings still wait for all guests."     │
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ ForkJoinPool → Parallel Algorithms        │
└──────────────┴───────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** Design a parallel pipeline with 3 stages (Source → Transform → Sink) where: Stage 1 has 8 threads, Stage 2 has 4 threads, Stage 3 has 2 threads. Stage k's output becomes Stage k+1's input. How would you use Phaser to coordinate the pipeline so that Stage 2 doesn't start processing until Stage 1 has produced all its output, and Stage 3 doesn't start until Stage 2 is complete — while also allowing Stage 1's threads to deregister after producing their output?

**Q2.** Phaser's internal state encodes both phase number and party counts in a single `volatile long`. Explain why using two separate `volatile int` fields (one for phase, one for counts) would be incorrect even with volatile semantics. What specific race condition would occur between a phase advance and a new party registration? How does the single-long encoding prevent this?
