---
layout: default
title: "Phaser"
parent: "Java Concurrency"
nav_order: 359
permalink: /java-concurrency/phaser/
number: "359"
category: Java Concurrency
difficulty: ★★★
depends_on: CyclicBarrier, CountDownLatch, Thread
used_by: Multi-phase Algorithms, Dynamic Party Registration
tags: #java, #concurrency, #synchronizer, #phaser, #barrier
---

# 359 — Phaser

`#java` `#concurrency` `#synchronizer` `#phaser` `#barrier`

⚡ TL;DR — Phaser is a flexible, reusable synchronisation barrier for multi-phase concurrent algorithms that supports dynamic registration and deregistration of parties — a generalisation of both CyclicBarrier and CountDownLatch.

| #359 | category: Java Concurrency
|:---|:---|:---|
| **Depends on:** | CyclicBarrier, CountDownLatch, Thread | |
| **Used by:** | Multi-phase Algorithms, Dynamic Party Registration | |

---

### 📘 Textbook Definition

`java.util.concurrent.Phaser` is a reusable synchronisation barrier that is more flexible than `CyclicBarrier` or `CountDownLatch`. Key features: parties can register and deregister dynamically; the phase number advances automatically when all registered parties arrive; `onAdvance(phase, parties)` can be overridden to add logic between phases or to terminate the phaser; phasers can be tiered (parent-child) for scalability.

---

### 🟢 Simple Definition (Easy)

Phaser is like CyclicBarrier but flexible: you can add or remove participants at runtime, run any number of phases, and override what happens between phases. Think of it as a programmable multi-phase checkpoint that adapts to varying numbers of workers per phase.

---

### 🔵 Simple Definition (Elaborated)

CyclicBarrier is great but rigid: fixed party count, no way to add/remove participants. Phaser solves this: a task can `register()` when it starts and `deregister()` when it's done — so later phases can run with fewer participants. A tree of Phasers can split large groups (thousands of threads) without a single bottleneck: leaf phasers aggregate to parent phasers.

---

### 🔩 First Principles Explanation

```
CyclicBarrier limitations:
  Fixed party count (set at construction)
  Cannot add parties dynamically
  All parties must participate in every phase
  Single-level: large party counts → single bottleneck

Phaser advantages:
  Dynamic registration:  phaser.register()       (add 1 party)
                         phaser.bulkRegister(n)   (add n parties)
  Dynamic deregistration: phaser.arriveAndDeregister() (last arrive, then leave)
  Phase advance: when all registered parties arrive → phase number increments
  Override onAdvance: phaser overrode → control phase transitions
  Tiered phasers: child.setParent(parent) → scalable for large thread counts

Phase numbering:
  starts at 0, increments each time all parties arrive
  getPhase() → current phase number
  onAdvance(phase, parties) returns boolean:
    true  → terminate the phaser (no more phases)
    false → continue (default)
```

---

### 🧠 Mental Model / Analogy

> A series of concert performances with a flexible cast. Before each act (phase), performers (parties) check in (`arrive()`). Only when all checked-in performers have arrived does the act begin. But performers can join (`register()`) or leave (`deregister()`) between acts — the concert adapts. The conductor (`onAdvance`) can decide after each act whether to continue or end the show.

---

### ⚙️ How It Works

```
Phaser phaser = new Phaser(N)  // start with N parties (or 0 + dynamic register)

arrive()                 → signal arrival, don't wait (async)
arriveAndAwaitAdvance()  → signal arrival AND wait for all parties (like CyclicBarrier.await)
arriveAndDeregister()    → signal arrival AND remove self from future phases
register()               → add 1 registered party
bulkRegister(n)          → add n registered parties

awaitAdvance(int phase)  → wait until phase number > given phase
getPhase()               → current phase number
getRegisteredParties()   → number of registered parties
getArrivedParties()      → how many have arrived this phase

Override onAdvance:
  protected boolean onAdvance(int phase, int registeredParties) {
    return phase >= 4;  // terminate after 5 phases (0-4)
  }
```

---

### 🔄 How It Connects

```
Phaser
  ├─ Generalises → CyclicBarrier (fixed parties, reusable barrier)
  ├─ Generalises → CountDownLatch (one-shot, one-way countdown)
  ├─ Dynamic     → add/remove parties per-phase
  ├─ Tiered      → child/parent for large-scale coordination
  └─ Use cases   → multi-round algorithms, task graphs, phased simulation
```

---

### 💻 Code Example

```java
// Multi-phase simulation with dynamic participants
int initialWorkers = 4;
Phaser phaser = new Phaser(initialWorkers) {
    @Override
    protected boolean onAdvance(int phase, int registeredParties) {
        System.out.println("Phase " + phase + " complete. Parties: " + registeredParties);
        return phase >= 2; // run phases 0, 1, 2 then terminate
    }
};

for (int i = 0; i < initialWorkers; i++) {
    final int id = i;
    new Thread(() -> {
        for (int phase = 0; !phaser.isTerminated(); phase++) {
            doPhaseWork(id, phase);
            phaser.arriveAndAwaitAdvance(); // sync at each phase boundary
        }
    }).start();
}
```

```java
// Dynamic registration — thread joins mid-computation
Phaser phaser = new Phaser(3); // initial 3 participants

// Late-joining task
new Thread(() -> {
    phaser.register();  // join dynamically
    phaser.arriveAndAwaitAdvance(); // participate in next phase
    doWork();
    phaser.arriveAndDeregister();   // leave after contribution
}).start();
```

---

### ⚠️ Common Misconceptions

| ❌ Wrong Belief | ✅ Correct Reality |
|---|---|
| Phaser replaces CyclicBarrier in all cases | CyclicBarrier is simpler for fixed-party scenarios; Phaser adds complexity |
| arriveAndDeregister() waits for the phase to advance | It does NOT wait — it arrives and removes itself; use arriveAndAwaitAdvance() to wait |
| phase number wraps around at Integer.MAX_VALUE | Phase number increments indefinitely (treated as unsigned) |

---

### 🔥 Pitfalls in Production

**Pitfall: arriveAndDeregister() does not wait**

```java
// ❌ If you expect to wait for the phase to advance before proceeding:
phaser.arriveAndDeregister(); // arrives AND deregisters — does NOT wait
nextOperation();              // runs immediately, phase may not have advanced

// ✅ To wait AND then leave:
phaser.arriveAndAwaitAdvance(); // wait for phase advance
phaser.arriveAndDeregister();   // now safely deregister (arrives again!)
// OR: use arrive() + awaitAdvance(phase) then deregister
```

---

### 🔗 Related Keywords

- **[CyclicBarrier](./079 — CyclicBarrier.md)** — simpler; fixed party count
- **[CountDownLatch](./078 — CountDownLatch.md)** — one-shot; Phaser generalises this
- **[ForkJoinPool](./084 — ForkJoinPool.md)** — alternative for recursive parallel decomposition

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────────┐
│ KEY IDEA     │ Reusable multi-phase barrier with dynamic     │
│              │ party registration and onAdvance callbacks    │
├──────────────┼───────────────────────────────────────────────┤
│ USE WHEN     │ Multi-phase algorithms; varying participants  │
│              │ per phase; need to terminate after N phases   │
├──────────────┼───────────────────────────────────────────────┤
│ AVOID WHEN   │ Fixed parties, simple barrier → CyclicBarrier;│
│              │ one-shot → CountDownLatch                     │
├──────────────┼───────────────────────────────────────────────┤
│ ONE-LINER    │ "CyclicBarrier that lets you add or drop      │
│              │  participants and run exactly N phases"       │
├──────────────┼───────────────────────────────────────────────┤
│ NEXT EXPLORE │ CyclicBarrier → CountDownLatch → ForkJoinPool │
│              │ → Structured Concurrency                     │
└──────────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** A Phaser starts with 3 registered parties. Thread A calls `arriveAndDeregister()`, Thread B calls `arriveAndDeregister()`, Thread C calls `arriveAndDeregister()`. Does the phase advance? What is the state of the Phaser after all three calls?

**Q2.** Tiered Phasers (parent-child) are recommended when the party count exceeds several hundred. What happens at the parent level — does the parent's own counter change with every child arrival, or only when a child phaser's phase advances?

**Q3.** How would you implement a "run exactly 5 iterations of a parallel algorithm then stop" pattern using Phaser's `onAdvance` method?

