---
layout: default
title: "Happens-Before"
parent: "Java & JVM Internals"
nav_order: 275
permalink: /java/happens-before/
number: "0275"
category: Java & JVM Internals
difficulty: ★★★
depends_on: Java Memory Model, Memory Barrier, Thread, volatile, synchronized
used_by: volatile, synchronized, Race Condition, CAS, Thread Lifecycle
related: Memory Barrier, Java Memory Model, Race Condition, volatile
tags:
  - java
  - jvm
  - concurrency
  - internals
  - deep-dive
---

# 275 — Happens-Before

⚡ TL;DR — Happens-Before is the JMM's formal guarantee that if action A happens-before action B, every thread will see A's effects before B executes — the foundational rule of Java concurrency correctness.

| #275 | Category: Java & JVM Internals | Difficulty: ★★★ |
|:---|:---|:---|
| **Depends on:** | Java Memory Model, Memory Barrier, Thread, volatile, synchronized | |
| **Used by:** | volatile, synchronized, Race Condition, CAS, Thread Lifecycle | |
| **Related:** | Memory Barrier, Java Memory Model, Race Condition, volatile | |

---

### 🔥 The Problem This Solves

WORLD WITHOUT IT:
Before JSR-133 (2004) formalised the Java Memory Model, Java's concurrency specification was ambiguous about what multi-threaded programs could actually guarantee. Compilers and JVMs were free to reorder any operations that appeared safe from a single-thread perspective. This meant well-intentioned concurrent code could be "broken" by any good-faith JVM implementation. developers had no formal model to reason about correctness, and JVM vendors had no specification to implement against.

THE BREAKING POINT:
The lack of formal semantics meant two things: (1) a concurrent program that worked on JVM A could be silently wrong on JVM B; (2) JVM vendors couldn't optimise aggressively without risking breaking programs, because there was no clear specification of what transformations were legal. Both program correctness and platform optimisation suffered.

THE INVENTION MOMENT:
JSR-133 introduced happens-before as the core semantic abstraction. Instead of specifying exactly when writes become visible (which depends on hardware), JSR-133 defines conditions under which a write is guaranteed to be visible — the happens-before relationship. Programs with all required happens-before edges are data-race-free and execute correctly. Programs without them have undefined behaviour per the JMM. This is exactly why happens-before was formalised: it provides a precise, hardware-independent contract for concurrent Java code.

---

### 📘 Textbook Definition

The Happens-Before relation (→_hb) is a formal partial order defined by the Java Memory Model (JMM) over memory actions (reads and writes) in a Java program. If action A happens-before action B (written A →_hb B), then all effects of A are guaranteed to be visible to B. The JMM specifies the conditions that establish a happens-before edge: (1) program order within a thread; (2) monitor release → monitor acquisition; (3) volatile write → volatile read of the same variable; (4) thread start → first action in the started thread; (5) last action in a thread → thread join; (6) happens-before is transitive. A program is data-race-free if and only if every conflicting access pair (same variable, at least one write, different threads) is ordered by happens-before.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
Happens-Before is a promise: if A happens-before B, then B is guaranteed to see everything A did.

**One analogy:**
> A legal contract stamped and delivered before a meeting happens-before the meeting — it is guaranteed that attendees have seen the contract's terms before the meeting starts. Happens-Before is Java's contract chain: certain actions (locking, unlocking, volatile writes) are legal stamps that guarantee visibility before the next stamped action.

**One insight:**
The crucial insight is that happens-before is not about physical time — it's about visibility guarantees. Two actions can happen "at the same time" (on different CPU cores) without happens-before ordering, and either one can see the other's effects or not. Happens-before is the only tool programmers have to reason about what is guaranteed to be visible in concurrent code.

---

### 🔩 First Principles Explanation

CORE INVARIANTS:
1. Within a single thread, all actions are ordered by happens-before (program order).
2. happens-before is transitive: if A →_hb B and B →_hb C, then A →_hb C.
3. happens-before is NOT a statement about execution order — it is a statement about visibility.

DERIVED DESIGN:
Invariant 1 means single-threaded code behaves as written — predictable. Invariant 2 enables composability: you establish A →_hb B using a `volatile` write, and separately B →_hb C using a `synchronized` exit. By transitivity, A →_hb C, meaning A's writes are visible when C executes. Invariant 3 is the common misunderstanding: two actions ordered by happens-before must have A's writes visible to C, but A may actually execute after C in physical wall-clock time — happens-before is about observable effects, not timestamps.

THE TRADE-OFFS:
Gain: A precise, hardware-independent language for reasoning about concurrent visibility; clear contract for what "correctly synchronised" means in Java.
Cost: Abstract — does not tell programmers the exact mechanism (memory barriers, synchronisation protocols) behind the guarantee; easy to build incorrect intuitions about "time" from happens-before ordering.

---

### 🧪 Thought Experiment

SETUP:
Thread A runs: `data = 42; flag.set(true);` (using `AtomicBoolean`).
Thread B runs: `while (!flag.get()) {}; assert data == 42;`.

DO THESE SHARE A HAPPENS-BEFORE RELATIONSHIP?

Step 1: Within Thread A, `data = 42` happens-before `flag.set(true)` (program order rule).

Step 2: `flag.set(true)` is a write to a volatile variable (AtomicBoolean is backed by volatile). The JMM rule: volatile write →_hb volatile read of the same variable that observes the write.

Step 3: Thread B's `flag.get()` returns `true` (observes the write). Therefore: `flag.set(true)` →_hb `flag.get()=true`.

Step 4: `flag.get()=true` happens-before `data == 42` check (program order in Thread B).

Step 5: Transitivity: `data = 42` →_hb `flag.set(true)` →_hb `flag.get()=true` →_hb `assert data == 42`.

CONCLUSION: The assert is guaranteed to see `data = 42`. The chain of happens-before edges flows from the write through the volatile publication point to the read. This is the "publication idiom" — volatile flag used to safely publish a non-volatile value.

THE INSIGHT:
A single volatile access can "carry" the happens-before guarantee for all preceding writes in Thread A to all subsequent reads in Thread B. You don't need every shared variable to be volatile — only the publication point.

---

### 🧠 Mental Model / Analogy

> Think of happens-before edges as signed certificates in a legal chain of custody. A write to `data` is a document. Thread A signs it (`volatile write`). Thread B receives and verifies the signature (`volatile read`). Once verified, Thread B is legally bound to acknowledge all documents signed before Thread A's signature. The chain of custody (happens-before chain) guarantees legal standing, regardless of the actual route the documents took.

"Signing a document" → volatile write, synchronized exit, thread start
"Verifying signature" → volatile read, synchronized entry, thread join
"Legal acknowledgement of prior documents" → visibility of all writes before the synchronisation action
"Chain of custody" → transitive happens-before chain

Where this analogy breaks down: unlike legal documents where time is recorded, happens-before has no timeline. A document "signed" at midnight and received at noon still counts — happens-before is enforced regardless of wall-clock timing.

---

### 📶 Gradual Depth — Four Levels

**Level 1 — What it is (anyone can understand):**
When two operations in different Java threads are connected by a happens-before relationship, Java guarantees that the second operation will see all the changes made by the first. Without this relationship, there are no visibility guarantees — the second thread might see stale or corrupted values.

**Level 2 — How to use it (junior developer):**
You establish happens-before edges through: `volatile` field reads/writes, `synchronized` block entry/exit, `Thread.start()`, `Thread.join()`, and all `java.util.concurrent` operations (lock/unlock, `CountDownLatch.countDown()` before `await()`). As long as your data sharing is protected by at least one of these, you have correct concurrent code. If you share data without any of these — you have a data race.

**Level 3 — How it works (mid-level engineer):**
The JMM's formal definition uses "sequentially consistent" semantics for correctly synchronised programs. A program is correctly synchronised if and only if every data race is absent. For correctly synchronised programs, the JMM guarantees that all executions appear to be sequentially consistent — each action appears to happen in some total order, with every read seeing the most recent write in that order. The JIT can reorder, cache, and optimise freely — but the observable result must match some sequentially consistent execution.

**Level 4 — Why it was designed this way (senior/staff):**
The happens-before formulation in JSR-133 was inspired by Leslie Lamport's 1978 paper "Time, Clocks, and the Ordering of Events in a Distributed System," which introduced happens-before as a way to reason about events in distributed systems without a global clock. The connection between distributed systems (no shared memory → must synchronise via messages) and concurrent threads (shared memory → must synchronise via barriers) is deep and formal — both use the same mathematical partial order. This is why the JMM feels "distributed systems"-flavoured: because it is mathematically the same problem.

---

### ⚙️ How It Works (Mechanism)

**The Six Happens-Before Rules (JMM Specification):**

```
┌─────────────────────────────────────────────┐
│      HAPPENS-BEFORE RULES (JMM JSR-133)     │
├─────────────────────────────────────────────┤
│  Rule 1: Program Order                      │
│  Each action in a thread →_hb every action  │
│  later in that thread (by program order)    │
├─────────────────────────────────────────────┤
│  Rule 2: Monitor Lock                       │
│  Monitor UNLOCK →_hb monitor LOCK          │
│  (synchronized exit → synchronized entry)  │
├─────────────────────────────────────────────┤
│  Rule 3: Volatile Variable                  │
│  volatile WRITE →_hb volatile READ          │
│  (of same variable, read sees the write)   │
├─────────────────────────────────────────────┤
│  Rule 4: Thread Start                       │
│  Thread.start() →_hb first action in the   │
│  started thread                             │
├─────────────────────────────────────────────┤
│  Rule 5: Thread Termination                 │
│  Last action in thread →_hb Thread.join()  │
│  returns in joining thread                  │
├─────────────────────────────────────────────┤
│  Rule 6: Transitivity                       │
│  If A →_hb B and B →_hb C, then A →_hb C  │
└─────────────────────────────────────────────┘
```

**Happens-Before Chain Visualization:**

```
Thread A:                    Thread B:
  write(x=42)                 read(x) [must see 42]
  ↓ (Rule 1: prog order)      ↑ (Rule 1: prog order)
  volatile write(flag=true)   volatile read(flag)
                    ↘        ↗
                     (Rule 3: volatile)
```

**What Transitions Create Edges:**

| Java Construct | Creates Edge |
|---|---|
| `volatile write` | write →_hb all subsequent `volatile read`s observing the write |
| `synchronized exit` | exit →_hb all subsequent `synchronized entry`s on same monitor |
| `Thread.start()` | start() →_hb first action in new thread |
| `Thread.join()` | last action of joined thread →_hb join() returns |
| `CountDownLatch.countDown()` | countDown() →_hb await() returns (when count = 0) |
| `Semaphore.release()` | release() →_hb acquire() returns |

---

### 🔄 The Complete Picture — End-to-End Flow

NORMAL FLOW:
```
Thread A writes data       Thread B
  data = 42                  (waiting for publication)
  ↓ [Rule 1: prog order]
  volatile flag = true     volatile read flag == true
  ↓                          ← YOU ARE HERE (edge created)
  [happens-before chain]   ↓ [Rule 3: volatile]
                           transitivity (Rule 6):
                             data=42 seen by Thread B
                           use(data)  // guaranteed 42
```

FAILURE PATH:
```
Missing happens-before edge:
  Thread A writes data=42 (no volatile, no sync)
  Thread B reads data simultaneously
  No edge → data race → JMM: UNDEFINED BEHAVIOUR
  Possible outcomes:
    1. B sees 42 (lucky cache state)
    2. B sees 0 (stale cached value)
    3. B sees partial write (word torn value)
  None guaranteed by specification
```

WHAT CHANGES AT SCALE:
At scale across distributed JVMs, happens-before doesn't extend across JVM boundaries — it's a single-JVM concept. Distributed systems must use message passing, database locking, or distributed consensus to establish cross-JVM ordering. This is why distributed systems theory (Lamport clocks, vector clocks) uses the same happens-before concept but with explicit "message sent / message received" edges instead of Java's synchronisation actions.

---

### 💻 Code Example

Example 1 — Establishing happens-before with volatile:
```java
class Publisher {
    private int data;             // NOT volatile
    private volatile boolean ready; // volatile = HB edge

    void publish(int value) {
        data = value;             // A: write data
        ready = true;             // B: volatile write
        // A happens-before B (program order)
        // B visible → A's effects visible too (transitivity)
    }

    int consume() {
        while (!ready) {}         // C: volatile read (= true)
        // B happens-before C (volatile rule)
        // A happens-before B happens-before C
        // → A's effect (data = value) visible at C!
        return data;              // D: reads data
    }
}
```

Example 2 — Broken (missing happens-before):
```java
// BAD: no synchronisation = no happens-before = data race
class BrokenPublisher {
    private int data;
    private boolean ready;  // NOT volatile!

    void publish(int value) {
        data = value;
        ready = true;  // no happens-before edge created
    }

    int consume() {
        while (!ready) {}  // may loop forever (not volatile!)
        return data;       // may see 0 (no happens-before!)
    }
}
// Result: UNDEFINED BEHAVIOUR per JMM
// May work in practice on x86 but broken per spec
```

Example 3 — Happens-before through CountDownLatch:
```java
// java.util.concurrent respects happens-before
CountDownLatch latch = new CountDownLatch(1);
int[] sharedData = new int[1];

Thread writer = new Thread(() -> {
    sharedData[0] = 42;     // A: write
    latch.countDown();       // B: countDown() creates edge
    // A happens-before B (program order)
});

Thread reader = new Thread(() -> {
    latch.await();           // C: await() sees countDown
    // B happens-before C (CountDownLatch rule)
    // A happens-before C (transitivity)
    assert sharedData[0] == 42; // D: GUARANTEED
});
```

Example 4 — Thread.start and join edges:
```java
int[] sharedData = {0};

// Thread.start() creates happens-before edge:
// all writes before start() are visible in child thread
sharedData[0] = 100;
Thread t = new Thread(() -> {
    // Rule 4: sharedData[0] = 100 happens-before
    // this thread's first action
    assert sharedData[0] == 100;  // GUARANTEED
    sharedData[0] = 200;
});
t.start();

t.join(); // Rule 5: last action in t happens-before join()
assert sharedData[0] == 200; // GUARANTEED (after join)
```

---

### ⚖️ Comparison Table

| Construct | Happens-Before Type | Overhead | Atomicity | Best For |
|---|---|---|---|---|
| `volatile` field | Write →_hb Read | Low (single barrier) | Only for reference/64-bit reads | Simple flag/state publishing |
| `synchronized` | Exit →_hb Enter | Medium (mutex + barriers) | Yes (critical section) | Compound operations + visibility |
| `AtomicInteger` | CAS write →_hb reads | Medium (CAS) | For int operations | Counter, flag, compare-and-set |
| `Thread.start/join` | Program point | High (thread creation) | N/A | Starting tasks, waiting for results |
| `ConcurrentHashMap.put/get` | put →_hb get | Low-medium | Internal | Shared map access |

How to choose: Use `volatile` when visibility is needed without atomicity. Use `synchronized` when atomicity + visibility are both required. Use `java.util.concurrent` classes for complex concurrent patterns — they all respect happens-before internally.

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| "Happens-before means 'happens first in time'" | Happens-before is about VISIBILITY, not TIME. A can happen-before B while physically occurring after B in wall-clock time, as long as B's execution is guaranteed to see A's effects. |
| "volatile makes the code sequential" | volatile ensures happens-before between specific reads and writes. It does not make all operations atomic or prevent compound operations from being interleaved. |
| "synchronized(obj) creates happens-before between any two uses of (obj)" | Only between a RELEASE (exit) and a subsequent ACQUIRE (entry). Two simultaneous synchronized blocks don't create happens-before — only sequential lock/unlock pairs do. |
| "java.util.concurrent classes don't need volatile/synchronized inside them" | They use fine-grained barriers internally. The happens-before guarantees they offer are a result of their internal synchronisation, not magic. |
| "Missing happens-before causes crashes" | Missing happens-before causes DATA RACES — undefined behaviour that may produce wrong values silently without crashing. This makes it more dangerous, not less. |

---

### 🚨 Failure Modes & Diagnosis

**1. Data Race from Missing Happens-Before**

Symptom: Intermittent wrong values; race condition that only manifests under specific timing; passes all unit tests (tests run sequentially) but fails under load.

Root Cause: Two threads access the same variable with at least one write, without any synchronisation establishing happens-before.

Diagnostic:
```bash
# Java race condition detection tools:
# 1. ThreadSanitizer with JNI agent:
java -agentpath:path/to/tsan.so -jar myapp.jar

# 2. FindBugs / SpotBugs static analysis
mvn com.github.spotbugs:spotbugs-maven-plugin:check

# 3. JCStress for testing specific race conditions
# 4. Run with helgrind under Linux perf tools
```

Prevention: Follow the rule: if multiple threads access a variable and at least one writes, it must be protected by volatile, synchronized, or java.util.concurrent.

**2. Stale Read Despite "Previous" Write**

Symptom: Thread B reads a field and sees an old value even though Thread A wrote the new value "before" (in physical time).

Root Cause: "Before in time" is not happens-before. Without a synchronisation action connecting A's write to B's read, there is no happens-before edge, and B may see any cached value.

Diagnostic:
```java
// Add this check: trace happens-before chain from write to read
// Does a synchronized exit / volatile write occur after the
// write in Thread A?
// Does the corresponding entry / volatile read occur before
// the read in Thread B?
// If no: no happens-before → expected stale read.
```

Prevention: Draw the happens-before chain. If there's no continuous chain from the write to the read, add synchronisation at the publication point.

**3. Assuming transitivity with time-based ordering**

Symptom: Complex multi-stage pipeline where Thread A sets data, Thread B processes it, Thread C reads the result. Thread C sees correct data from B but stale data from A.

Root Cause: A→B happens-before chain was established, and B→C chain was established, but the chains were established using different synchronisation objects, breaking transitive chaining.

Diagnostic:
```java
// Check: is the happens-before chain continuous?
// A writes data
// A synchronized(lock1) exit      // A →_hb
// B synchronized(lock1) entry     // →_hb B
// B processes, writes result
// B synchronized(lock2) exit      // B →_hb
// C synchronized(lock2) entry     // →_hb C
// C reads result
// Transitivity: A →_hb B →_hb C via two different locks
// This IS valid transitivity — different locks are OK
// as long as the chain is continuous
```

Prevention: Document the happens-before chain explicitly in concurrent code comments; use tools like JCStress to test the ordering assumptions.

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**
- `Java Memory Model` — the specification that defines happens-before; this entry is an application of JMM rules
- `Memory Barrier` — the hardware mechanism that implements happens-before guarantees at CPU level
- `Thread` — the executing units between which happens-before must be established
- `volatile` — one of the primary mechanisms that creates happens-before edges

**Builds On This (learn these next):**
- `Race Condition` — what happens when happens-before edges are absent between conflicting accesses
- `synchronized` — the construct that creates happens-before via monitor lock/unlock
- `Java Memory Model` — the full formal specification of which programs are data-race-free via happens-before

**Alternatives / Comparisons:**
- `Causal Consistency` — a distributed systems consistency model that uses similar happens-before semantics but across distributed machines
- `Sequential Consistency` — stronger than JMM: all operations appear in some total order visible to all threads; JMM only guarantees this for data-race-free programs

---

### 📌 Quick Reference Card

┌──────────────────────────────────────────────────────────┐
│ WHAT IT IS   │ JMM guarantee: if A happens-before B,     │
│              │ B is guaranteed to see all of A's effects │
├──────────────┼───────────────────────────────────────────┤
│ PROBLEM IT   │ Without a formal ordering model, JVM      │
│ SOLVES       │ optimisations make concurrent code        │
│              │ undefined without clear contracts         │
├──────────────┼───────────────────────────────────────────┤
│ KEY INSIGHT  │ NOT about physical time — about           │
│              │ visibility. A can physically happen later  │
│              │ but guarantee B sees its effects          │
├──────────────┼───────────────────────────────────────────┤
│ USE WHEN     │ Every time two threads share mutable data │
│              │ — verify the happens-before chain         │
├──────────────┼───────────────────────────────────────────┤
│ AVOID WHEN   │ N/A — you must always establish it for    │
│              │ shared mutable state                      │
├──────────────┼───────────────────────────────────────────┤
│ TRADE-OFF    │ Formal correctness guarantee vs requires  │
│              │ explicit synchronisation actions          │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "Happens-before: the chain of formal      │
│              │ stamps that guarantees visibility         │
│              │ across threads"                           │
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ Race Condition → volatile →               │
│              │ Java Memory Model                         │
└──────────────────────────────────────────────────────────┘

---

### 🧠 Think About This Before We Continue

**Q1.** Thread A writes 10 different fields and then does `lock.unlock()`. Thread B does `lock.lock()` and then reads all 10 fields. The JMM guarantees Thread B sees all 10 writes. Now Thread C, without any lock acquisition, reads the same 10 fields "after" Thread B in physical time. Is Thread C guaranteed to see the same values? Explain using happens-before rules, and identify what synchronisation action Thread C would need to establish a valid happens-before chain.

**Q2.** Java's `ForkJoinPool.commonPool()` and `CompletableFuture.supplyAsync()` execute tasks concurrently. A `CompletableFuture` chain like `supplyAsync(...).thenApply(f).thenAccept(g)` implies that `f` sees the result of `supplyAsync` and `g` sees the result of `f`. What JMM mechanism ensures these happens-before edges across the async stages? What happens to the happens-before chain if an exception is thrown midway and the `exceptionally()` handler accesses shared data written by the initial stage?

