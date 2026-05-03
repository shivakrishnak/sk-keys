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
used_by: Phased Parallel Algorithms, Dynamic Thread Pools, Fork/Join Alternatives
related: CyclicBarrier, CountDownLatch, Fork/Join, CompletableFuture
tags:
  - concurrency
  - synchronization
  - phaser
  - java
  - advanced
  - dynamic
---

# 359 — Phaser

⚡ TL;DR — Phaser is a flexible, reusable synchronization barrier where threads can dynamically register and deregister between phases, making it more powerful than CyclicBarrier for algorithms where the participant count changes.

| #0359           | Category: Java Concurrency                                               | Difficulty: ★★★ |
| :-------------- | :----------------------------------------------------------------------- | :-------------- |
| **Depends on:** | CyclicBarrier, CountDownLatch, Thread, ExecutorService                   |                 |
| **Used by:**    | Phased Parallel Algorithms, Dynamic Thread Pools, Fork/Join Alternatives |                 |
| **Related:**    | CyclicBarrier, CountDownLatch, Fork/Join, CompletableFuture              |                 |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
A parallel tree-traversal algorithm starts with 1 root thread, but spawns variable numbers of child threads as it descends. After each level, some branches are fully explored (threads done) while others spawn more workers. You need to synchronize at each level — but the number of participants changes at every level. `CyclicBarrier(N)` requires a fixed N decided at construction time. You'd have to create a new CyclicBarrier for every level, knowing N in advance — impossible when N is determined at runtime.

**THE BREAKING POINT:**
Both CyclicBarrier and CountDownLatch require the party count to be fixed at creation. Real parallel algorithms often have dynamic participation: tasks complete early, new tasks spawn during execution, or thread pools scale in response to load. No fixed-N barrier can handle this.

**THE INVENTION MOMENT:**
`Phaser` (introduced in Java 7) generalizes both CountDownLatch and CyclicBarrier. Any thread can dynamically register as a party (`register()`), arrive at the current phase (`arrive()`), or deregister (`arriveAndDeregister()`). The phase automatically advances when all currently-registered parties have arrived. This makes Phaser the general-purpose phased synchronizer for algorithms with variable participant counts.

---

### 📘 Textbook Definition

**Phaser** is a reusable synchronization barrier in `java.util.concurrent` that allows threads to dynamically register and deregister between phases. Unlike CyclicBarrier (fixed N) and CountDownLatch (one-shot), Phaser tracks a phase number (starting at 0, incrementing on each barrier completion) and a set of registered parties that can change at runtime. Key operations: `register()` — add a party; `arrive()` — signal arrival without waiting; `arriveAndAwaitAdvance()` — signal arrival and block until phase advances; `arriveAndDeregister()` — signal arrival and remove this party from future phases; `awaitAdvance(phase)` — wait for a specific phase to complete. The overridable `onAdvance(phase, registeredParties)` method is called at each phase completion and can terminate the phaser by returning `true`.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
Phaser is a barrier where threads can join and leave between rounds, and you can use it for any number of rounds without creating new objects.

**One analogy:**

> Phaser is like a group hiking trip where each checkpoint requires all current hikers to check in before everyone moves to the next trail segment. But hikers can join the group mid-hike at any checkpoint, and tired hikers can leave at any checkpoint without breaking the system. The trail guide (onAdvance) decides whether the trip continues or ends.

**One insight:**
Phaser subsumes both CountDownLatch (`Phaser(1)` that terminates after one phase) and CyclicBarrier (fixed-party Phaser without deregistration). The extra power comes with extra complexity — prefer CyclicBarrier for fixed-N cases because it's simpler to reason about.

---

### 🔩 First Principles Explanation

**CORE INVARIANTS:**

1. Phaser tracks: `phase` (current phase number), `registeredParties` (total parties), `arrivedParties` (parties that have arrived this phase), `unarrivedParties = registered - arrived`.
2. Phase advances when `unarrivedParties` reaches 0.
3. `arrive()` returns immediately (non-blocking); `arriveAndAwaitAdvance()` blocks.
4. Parties can be registered/deregistered at any time (between phases is safest).
5. `onAdvance()` runs when phase advances — return `true` to terminate the phaser.

**DERIVED DESIGN:**

```
PHASER INTERNAL STATE:
┌───────────────────────────────────────────────────┐
│ phase: 0                                          │
│ registeredParties: 4                              │
│ arrivedParties: 0                                 │
│ terminated: false                                 │
└───────────────────────────────────────────────────┘

Phase 0 execution:
Thread A: arrive() → arrivedParties=1, unarrived=3
Thread B: arrive() → arrivedParties=2, unarrived=2
Thread C: arriveAndDeregister() → arrived=3, reg=3, unarr=0?
                                 Wait — deregister decrements
                                 registered too:
                                 arrived=3, registered=3
                                 unarrived = 3-3 = 0
                                 → Phase advances! phase=1

Thread D (was still working) finds phase=1 when it checks —
  D was registered, now trying arriveAndAwaitAdvance()
  → waits for phase 2 (phase 1 already passed)

This edge case shows why arrive-and-deregister ordering matters.
```

**THE TRADE-OFFS:**

- **Gain:** Dynamic parties, no pre-declaring N, supports phase-by-phase participant changes.
- **Cost:** More complex API than CyclicBarrier; easy to miscount and advance phase prematurely; hierarchical phasers needed for high party counts (>65535).

---

### 🧪 Thought Experiment

**SETUP:**
A parallel web crawler starts with 1 URL (1 thread). Each page yields 0–5 child URLs. After processing each level, all threads for that level must synchronize before level+1 starts. Thread count varies: level 0: 1, level 1: 5, level 2: 23, level 3: 7 (many 404s).

**WITHOUT Phaser:**
You'd need to know the thread count for each level before starting it — impossible for dynamic link discovery. You'd have to use a central queue and a master coordinator that counts completions, adding complex coordination logic.

**WITH Phaser:**

```
Level 0: phaser.register() for 1 thread
Thread 0 processes root, discovers 5 children
Before spawning: phaser.register() for each child (5 times)
Thread 0 calls arriveAndDeregister() (it's done)
5 new threads run level 1...
(each discovers children: register new threads, arriveAndDeregister self)
```

Phaser tracks the current party count dynamically. Level boundary: all current-level threads deregister; their discovered children registered. Phase advances when last level-N thread deregisters.

**THE INSIGHT:**
Dynamic registration converts what would be a complex custom synchronization protocol into three method calls: `register()`, work, `arriveAndDeregister()`. The phaser handles all the counting, waiting, and advancing.

---

### 🧠 Mental Model / Analogy

> Phaser is like a cruise ship boarding process with multiple departure stages. At stage 1 (main deck): all originally ticketed passengers must board. But passengers who decide to stay ashore can cancel, and last-minute passengers can be added. When all currently-ticketed passengers are aboard, the ship advances to stage 2 (cabin allocation). New passengers can board for stage 2. At any stage, the ship only moves forward when everyone currently on the manifest has arrived.

- "Ticketed passengers" → registered parties
- "Boarding at stage N" → calling `arriveAndAwaitAdvance()`
- "Cancel ticket" → `arriveAndDeregister()`
- "Adding last-minute passenger" → `register()`
- "Ship advances to next stage" → phase number increments
- "Captain decides no more stages" → `onAdvance()` returns `true`

Where this analogy breaks down: threads that `arriveAndDeregister()` mid-phase can cause the phase to advance even if other registered threads haven't arrived yet if the counts align — unlike physical boarding where you can't sail early.

---

### 📶 Gradual Depth — Four Levels

**Level 1 — What it is (anyone can understand):**
Phaser is like a meeting checkpoint for threads. Unlike a fixed-size barrier, threads can join or leave the meeting group at any time. The meeting only moves to the next agenda item when everyone currently in the group has checked in.

**Level 2 — How to use it (junior developer):**
Create `Phaser phaser = new Phaser(initialParties)`. Each participating thread calls `arriveAndAwaitAdvance()` to sync at each phase. To leave: call `arriveAndDeregister()`. To join: call `phaser.register()` before the phase starts. Check `phaser.isTerminated()` to know if the phaser has been stopped. Extend Phaser and override `onAdvance()` to add logic at each phase transition or to stop the phaser.

**Level 3 — How it works (mid-level engineer):**
Phaser's internal state is packed into a single `volatile long` for lock-free updates. The long encodes: phase (upper 32 bits), registered party count (bits 16–31), unarrived count (bits 0–15). Arrivals decrement unarrived via `Unsafe.compareAndSwapLong` (CAS). When unarrived reaches 0: the last thread calls `onAdvance()`, updates the phase (increments upper 32 bits), and unparks all waiting threads via `ForkJoinPool`'s managed blocker interface (or `LockSupport.unpark`). This makes Phaser integration with ForkJoinPool tasks first-class — `arriveAndAwaitAdvance()` is a managed blocking operation that allows ForkJoinPool to spawn compensating threads.

**Level 4 — Why it was designed this way (senior/staff):**
Phaser was designed explicitly to work within the Fork/Join framework's managed blocking model. When a ForkJoinWorkerThread blocks in `arriveAndAwaitAdvance()`, it implements `ManagedBlocker`, signalling the ForkJoinPool to potentially add a spare thread to compensate for the blocked one, maintaining pool parallelism. The hierarchical phaser feature (parent phasers) was added to address scalability: when registeredParties > ~65535, contention on the single CAS-updated long becomes a bottleneck. Grouping N sub-phasers under a parent phaser distributes that contention. The design trades simplicity for composability with Java's broader concurrency infrastructure.

---

### ⚙️ How It Works (Mechanism)

```java
// Key API summary with correct usage patterns:

// 1. Basic fixed-party usage (like CyclicBarrier)
Phaser phaser = new Phaser(3); // 3 parties

// Each of 3 threads:
phaser.arriveAndAwaitAdvance(); // barrier: all 3 arrive → phase 1

// 2. Dynamic registration for tree traversal
Phaser phaser = new Phaser(1); // 1 initial party (root thread)

void processLevel(List<URL> urls, int expectedPhase) {
    // Register one party per URL to process
    urls.forEach(url -> phaser.register());

    for (URL url : urls) {
        List<URL> children = fetch(url);
        // Register children before deregistering self
        children.forEach(child -> phaser.register());
        // Submit child processing...
        phaser.arriveAndDeregister(); // done with this URL
    }
    // Wait for phase to complete (all URLs processed)
    phaser.awaitAdvance(expectedPhase);
}

// 3. Custom onAdvance — terminate after N phases
Phaser phaser = new Phaser(workers.size()) {
    @Override
    protected boolean onAdvance(int phase, int registeredParties) {
        // Return true to terminate after 5 phases
        return phase >= 4 || registeredParties == 0;
    }
};

// 4. Hierarchical phaser for 1000+ parties
Phaser parent = new Phaser();
Phaser child1 = new Phaser(parent, 100); // 100 parties under parent
Phaser child2 = new Phaser(parent, 100); // another 100 parties
// child phasers register themselves with parent automatically
// phase advances in parent only when all child phasers complete
```

---

### 🔄 The Complete Picture — End-to-End Flow

```
NORMAL FLOW (parallel BFS):
Root thread registers 1 party, processes root node
→ Discovers N children, registers N parties
→ Spawns N threads
→ Root calls arriveAndDeregister (level 0 done)
→ [Phaser ← YOU ARE HERE — tracking all level-1 threads]
→ Each level-1 thread discovers children: register + spawn
→ Each level-1 thread calls arriveAndDeregister
→ When last level-1 thread deregisters: phase advances
→ Level-2 threads continue; onAdvance checks termination
→ Returns true when no parties remain → Phaser terminated

FAILURE PATH:
Thread crashes after register() but before arriveAndDeregister()
→ Party count never decrements
→ Phase never advances
→ All other threads wait indefinitely at arriveAndAwaitAdvance()
→ Fix: use try-finally to guarantee arriveAndDeregister()

WHAT CHANGES AT SCALE:
With >65535 parties, the packed-long state word overflows
the party-count field. Use hierarchical phasers (parent/child)
to distribute counting across multiple Phaser instances.
Each child phaser has ≤1000 parties; parent advances when
all children advance — scaling to millions of tasks.
```

---

### 💻 Code Example

```java
import java.util.concurrent.*;

// Example 1 — Iterative parallel computation with Phaser
// (mimics CyclicBarrier but with onAdvance termination)
int THREADS = 4;
int MAX_PHASES = 10;

Phaser phaser = new Phaser(THREADS) {
    @Override
    protected boolean onAdvance(int phase, int parties) {
        System.out.println("Phase " + phase + " complete");
        return phase >= MAX_PHASES - 1; // terminate after 10 phases
    }
};

for (int t = 0; t < THREADS; t++) {
    final int id = t;
    new Thread(() -> {
        while (!phaser.isTerminated()) {
            doPhaseWork(id, phaser.getPhase());
            phaser.arriveAndAwaitAdvance();
        }
    }).start();
}

// Example 2 — Dynamic party registration (web crawler)
Phaser crawlerPhaser = new Phaser(1); // root party

void crawl(String url, Phaser phaser) {
    List<String> links = fetchLinks(url);
    links.forEach(link -> {
        phaser.register(); // register before submitting task
        executor.submit(() -> {
            try {
                crawl(link, phaser);
            } finally {
                phaser.arriveAndDeregister(); // always deregister
            }
        });
    });
}

// Start crawl
crawl(rootUrl, crawlerPhaser);
crawlerPhaser.arriveAndDeregister(); // root deregisters
crawlerPhaser.awaitAdvance(0); // wait for all crawls to finish
```

---

### ⚖️ Comparison Table

| Feature                  | Phaser                      | CyclicBarrier       | CountDownLatch |
| ------------------------ | --------------------------- | ------------------- | -------------- |
| **Reusable**             | Yes                         | Yes (auto-reset)    | No             |
| **Dynamic parties**      | Yes                         | No                  | No             |
| **Barrier action**       | onAdvance() override        | Runnable            | No             |
| **Non-blocking arrive**  | Yes (arrive())              | No                  | countDown()    |
| **ForkJoin integration** | Yes (ManagedBlocker)        | No                  | No             |
| **Best for**             | Dynamic parallel algorithms | Fixed-N phased work | One-time sync  |

**How to choose:** Default to CyclicBarrier for fixed-N multi-phase work — simpler API, less error-prone. Use Phaser when party count changes between phases, when ForkJoin integration matters, or when you need fine-grained control via `onAdvance()`.

---

### ⚠️ Common Misconceptions

| Misconception                                     | Reality                                                                                                                                                                                                                                             |
| ------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Phaser replaces CyclicBarrier for all use cases   | Phaser is more powerful but also more complex. CyclicBarrier is cleaner for fixed-N cases and its BrokenBarrierException model is easier to reason about than Phaser's termination model                                                            |
| register() is thread-safe to call at any time     | While technically safe, calling register() after a phase has started but before it completes can cause the new party to immediately cause the phase to not advance (it has registered but not arrived yet). Always register before the phase starts |
| arriveAndDeregister() and arrive() are equivalent | arrive() signals arrival but keeps the party registered for future phases. arriveAndDeregister() signals arrival and removes the party — if misused, you can permanently reduce the party count and cause premature phase advances                  |
| Phase number wraps at Integer.MAX_VALUE           | Phase number wraps at `Integer.MAX_VALUE / 2` due to the state packing. For algorithms with billions of phases, track the relative phase count, not the absolute phase number                                                                       |

---

### 🚨 Failure Modes & Diagnosis

**Phaser Never Advances (Missing arrive/deregister)**

**Symptom:** Threads blocked in `arriveAndAwaitAdvance()` indefinitely; GC shows Phaser objects alive long after expected completion.

**Root Cause:** A registered party thread threw an exception and exited without calling `arriveAndDeregister()` or `arrive()`. Registered party count is permanently higher than arrivals.

**Diagnostic Command:**

```bash
# Find threads blocked at Phaser.awaitAdvance:
jstack <pid> | grep -B 2 -A 10 "Phaser"

# Check Phaser state programmatically:
System.out.println("Registered: " + phaser.getRegisteredParties());
System.out.println("Arrived: " + phaser.getArrivedParties());
System.out.println("Unarrived: " + phaser.getUnarrivedParties());
System.out.println("Phase: " + phaser.getPhase());
```

**Fix:**

```java
// WRONG: deregister only on success
phaser.register();
doWork(); // throws exception
phaser.arriveAndDeregister(); // skipped! phase stuck

// GOOD: always deregister in finally
phaser.register();
try {
    doWork();
} finally {
    phaser.arriveAndDeregister(); // guaranteed
}
```

**Prevention:** Always pair `register()` with `arriveAndDeregister()` in a try-finally block.

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**

- `CyclicBarrier` — simpler barrier; understand it before Phaser's generalization
- `CountDownLatch` — one-shot synchronizer; Phaser generalizes it
- `Thread` — understand threading model before synchronization primitives

**Builds On This (learn these next):**

- `Fork/Join Framework` — Phaser integrates via ManagedBlocker for ForkJoinPool
- `CompletableFuture` — async composition that avoids explicit phased barriers
- `Structured Concurrency` — Java 21 loom feature that may supersede manual Phaser use

**Alternatives / Comparisons:**

- `CyclicBarrier` — simpler, fixed-N; prefer for known-count scenarios
- `CountDownLatch` — simpler, one-shot; prefer for single synchronization events
- `Semaphore` — controls concurrent access to resources, not phase synchronization

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ WHAT IT IS   │ Dynamic, reusable barrier where parties   │
│              │ can join/leave between phases             │
├──────────────┼───────────────────────────────────────────┤
│ PROBLEM IT   │ Parallel algorithms where thread count    │
│ SOLVES       │ varies per phase (CyclicBarrier can't)    │
├──────────────┼───────────────────────────────────────────┤
│ KEY INSIGHT  │ Phase advances when unarrived == 0;       │
│              │ deregister reduces registered count too   │
├──────────────┼───────────────────────────────────────────┤
│ USE WHEN     │ Dynamic participant count; ForkJoin tasks;│
│              │ need per-phase termination logic          │
├──────────────┼───────────────────────────────────────────┤
│ AVOID WHEN   │ Fixed party count (CyclicBarrier simpler);│
│              │ one-time sync (CountDownLatch simpler)    │
├──────────────┼───────────────────────────────────────────┤
│ TRADE-OFF    │ Flexibility vs complexity; register/      │
│              │ deregister ordering bugs are subtle       │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "A meeting checkpoint where the attendee  │
│              │  list can change between meetings"        │
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ Fork/Join → Structured Concurrency →      │
│              │ CompletableFuture                         │
└──────────────┴───────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** Phaser encodes its entire state (phase, registered parties, unarrived parties) into a single `volatile long` for lock-free updates via CAS. Given that each field is allocated a fixed number of bits, what is the maximum number of parties a single (non-hierarchical) Phaser can support? And why does Phaser use hierarchical phasers (parent-child) rather than simply using a wider integer (e.g., AtomicLong per counter) to solve the scalability problem?

**Q2.** When a ForkJoinWorkerThread calls `phaser.arriveAndAwaitAdvance()`, the Phaser implements `ManagedBlocker`, allowing the ForkJoinPool to spawn a compensating thread. If 8 ForkJoin worker threads all block at a Phaser simultaneously, the pool could spawn up to 8 compensating threads, temporarily doubling pool size. Describe the exact condition under which this compensating behaviour causes more harm than good — specifically when the compensation threads themselves block at the same Phaser.
