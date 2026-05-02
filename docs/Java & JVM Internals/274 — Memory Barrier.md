---
layout: default
title: "Memory Barrier"
parent: "Java & JVM Internals"
nav_order: 274
permalink: /java/memory-barrier/
number: "0274"
category: Java & JVM Internals
difficulty: ★★★
depends_on: JVM, Java Memory Model, volatile, Thread, Cache Line
used_by: volatile, synchronized, Happens-Before, CAS, VarHandle
related: Happens-Before, volatile, synchronized, False Sharing
tags:
  - java
  - jvm
  - concurrency
  - internals
  - deep-dive
  - memory
---

# 274 — Memory Barrier

⚡ TL;DR — A Memory Barrier is a CPU instruction that prevents the processor and compiler from reordering memory operations across it, ensuring visibility of writes to other threads.

| #274 | Category: Java & JVM Internals | Difficulty: ★★★ |
|:---|:---|:---|
| **Depends on:** | JVM, Java Memory Model, volatile, Thread, Cache Line | |
| **Used by:** | volatile, synchronized, Happens-Before, CAS, VarHandle | |
| **Related:** | Happens-Before, volatile, synchronized, False Sharing | |

---

### 🔥 The Problem This Solves

WORLD WITHOUT IT:
Modern CPUs execute instructions out of order (out-of-order execution) and cache memory writes in CPU-local write buffers before flushing to main memory. Two threads on two separate CPU cores can see a completely different ordering of memory writes than what the source code specifies. Thread A writes `flag = true` after `data = 42`, but Thread B may observe `flag = true` while still seeing `data = 0` — a broken ordering that makes concurrent programming pathologically unreliable.

THE BREAKING POINT:
Without a mechanism to constrain reordering, every concurrent algorithm is potentially broken by default. Algorithms that assume "if B sees flag=true, then B sees data=42" — which is logically guaranteed by program order — are silently wrong on multicore CPUs because the guarantee doesn't hold without explicit barriers.

THE INVENTION MOMENT:
Memory Barriers are CPU-level instructions that enforce ordering constraints: all writes before the barrier must be flushed and visible to other CPUs before any write after the barrier. This is exactly why Memory Barriers exist: they restore the programmer's intuitive ordering expectations in the face of CPU and compiler reordering.

---

### 📘 Textbook Definition

A Memory Barrier (also called a Memory Fence) is a machine instruction that enforces an ordering constraint on memory operations. There are four fundamental types: Load-Load (prevents subsequent loads from appearing before prior loads), Store-Store (ensures prior stores complete before subsequent stores), Load-Store (prevents later stores from being placed before prior loads), and Store-Load (the strongest — ensures prior stores are fully visible before any subsequent load). In Java, the JVM inserts Memory Barriers automatically at `volatile` reads and writes, `synchronized` block entry and exit, and `lock()` / `unlock()` operations — the programmer never inserts CPU barrier instructions directly.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
A Memory Barrier is a fence in execution that says: "all memory operations before me must complete before any operation after me begins."

**One analogy:**
> Imagine an assembly line where workers sometimes rearrange their steps for efficiency — doing step 7 before step 5 if it's faster. A Memory Barrier is a supervisor card placed between steps: "Everyone must finish everything before this card before starting anything after it." The assembly line output must always appear as if the original order was followed.

**One insight:**
The gap between Java's happens-before abstraction and actual CPU instructions is the Memory Barrier. When you write `volatile int flag`, you think in happens-before terms. Under the hood, the JVM emits CPU barrier instructions (`SFENCE`, `LFENCE`, `MFENCE` on x86, `DMB` on ARM) to physically enforce that guarantee. Understanding barriers explains why `volatile` reads/writes have measurable CPU cost compared to non-volatile accesses.

---

### 🔩 First Principles Explanation

CORE INVARIANTS:
1. CPUs and compilers legally reorder memory operations for performance if they appear safe from a single-thread perspective.
2. Reorderings that appear safe in single-threaded context can break multi-threaded invariants.
3. The programmer needs a way to prevent specific reorderings across thread boundaries.

DERIVED DESIGN:
Invariant 1 is the source of the problem. Invariant 2 limits what reorderings are acceptable. Invariant 3 requires an explicit mechanism. The design: insert a barrier instruction at points where ordering must be preserved. The barrier's semantic depends on type: a store-store barrier prevents two stores from swapping order; a store-load barrier (the most expensive, used by `volatile` reads) prevents any subsequent load from executing before all prior stores are globally visible.

THE TRADE-OFFS:
Gain: Correct multi-threaded behaviour; memory writes visible across CPUs as intended.
Cost: CPU barrier instructions flush write buffers, preventing out-of-order execution optimisations in the CPUs — measurable throughput cost on memory-intensive concurrent code.

---

### 🧪 Thought Experiment

SETUP:
Two threads. Thread A: `data = 42; flag = true;`. Thread B in loop: `if (flag) use(data)`.

WHAT HAPPENS WITHOUT MEMORY BARRIER:
CPU A's write buffer has `data = 42` pending. CPU A flushes `flag = true` first (CPU reordering — it's in a different cache line). CPU B reads `flag = true`. CPU B reads `data` — still 0 in its cache. `use(data)` receives 0, not 42. Silent data corruption. No exception. No error. Just a wrong value propagated silently.

WHAT HAPPENS WITH MEMORY BARRIER:
Thread A writes `data = 42` (ordinary write). Thread A executes a store-store barrier (emitted by `volatile int flag` write). The barrier forces all prior stores (including `data = 42`) to be globally visible. Then Thread A writes `flag = true` (`volatile`). Thread B reads `flag = true` (`volatile` read). `volatile` read includes a load-load barrier, ensuring all subsequent loads see the post-barrier memory state. Thread B reads `data` — guaranteed to see `42`.

THE INSIGHT:
Memory Barriers don't just prevent reordering — they ensure cross-CPU cache coherence. Without flushing write buffers and invalidating stale cache lines, correct multi-threaded programming is impossible on modern multicore hardware.

---

### 🧠 Mental Model / Analogy

> A Memory Barrier is like a toll booth on a dual-carriageway merge. All cars (memory operations) from both lanes (before the barrier) must come to a complete stop and pay the toll (flush to main memory) before any car in the lanes beyond the booth can move (subsequent memory operations). The barrier guarantees that every operation before it is fully complete before any operation after it begins.

"Cars before the toll" → memory reads/writes before the barrier
"Paying the toll (stop/flush)" → flushing CPU write buffers, invalidating remote caches
"Cars after the toll" → subsequent memory reads/writes
"Dual carriageway (multiple CPU cores)" → parallel execution across CPUs

Where this analogy breaks down: unlike a toll booth, the cost of a memory barrier is not constant — it varies by type (store-store is cheaper than store-load) and by the amount of pending data in the write buffer.

---

### 📶 Gradual Depth — Four Levels

**Level 1 — What it is (anyone can understand):**
Modern computers are so fast that they sometimes do things in a different order than the code says, as a speed optimisation. This is fine when only one thread is running. When multiple threads share data, this reordering causes bugs. A Memory Barrier is a signal that tells the computer "stop reordering — ensure the correct order here."

**Level 2 — How to use it (junior developer):**
In Java, you never write memory barriers directly. You use `volatile` (which inserts barriers automatically), `synchronized` blocks (which use full barriers at entry and exit), or `java.util.concurrent` classes (which are all barrier-correct). The rule: if two threads share mutable data without synchronisation, you have a data race and your program results are undefined by the JMM.

**Level 3 — How it works (mid-level engineer):**
The JVM's JIT emits specific barrier instructions based on the JMM rules. On x86-64: `volatile` write → `LOCK ADD esp, 0` (a store-load barrier approximation — cheaper than `MFENCE`); `volatile` read → no explicit barrier needed (x86 TSO memory model provides load-order implicitly). On ARM/POWER: `volatile` write → `DMB ISH` (Data Memory Barrier, Inner Shareable); `volatile` read → `DMB ISHLD`. The barrier instructions on ARM are more expensive than on x86 because ARM uses a weaker memory model (more reorderings permitted by hardware).

**Level 4 — Why it was designed this way (senior/staff):**
The Java Memory Model (JMM, JSR-133, 2004) deliberately abstracts over hardware memory models — programmers reason about happens-before relationships, not CPU-specific barriers. The JVM's job is to map happens-before to the minimum set of barriers required by the target CPU's memory model. x86's strong TSO (Total Store Order) model requires fewer explicit barriers than ARM's weak model. This abstraction means Java code is portable across memory models, but the performance of `volatile` operations varies significantly by CPU architecture. On server workloads running on x86-64, the cost is minimal; on ARM-based services, `volatile` hot paths may require profiling.

---

### ⚙️ How It Works (Mechanism)

**x86-64 Barrier Generation for volatile:**

```
┌─────────────────────────────────────────────┐
│     JMM BARRIER GENERATION (HotSpot)        │
├─────────────────────────────────────────────┤
│                                             │
│  volatile WRITE:                            │
│    [LoadStore barrier before write]         │
│    [StoreStore barrier before write]        │
│    WRITE operation                          │
│    [StoreLoad barrier after write]          │
│    ← emitted as: MOV + LOCK XADD on x86    │
│                                             │
│  volatile READ:                             │
│    READ operation                           │
│    [LoadLoad barrier after read]            │
│    [LoadStore barrier after read]           │
│    ← on x86, no instruction needed (TSO)   │
│    ← on ARM: DMB ISHLD instruction         │
│                                             │
│  synchronized entry:                        │
│    [MonitorEnter: implies LoadLoad+LoadStore]│
│                                             │
│  synchronized exit:                         │
│    [MonitorExit: implies StoreLoad+StoreStore│
└─────────────────────────────────────────────┘
```

**Four Barrier Types:**

```
┌──────────────────────────────────────────────┐
│ TYPE         │ PREVENTS                       │
├──────────────┼────────────────────────────────┤
│ LoadLoad     │ Load2 appearing before Load1   │
│ StoreStore   │ Store2 appearing before Store1 │
│ LoadStore    │ Store2 appearing before Load1  │
│ StoreLoad    │ Load2 appearing before Store1  │
│              │ (the most expensive / "full    │
│              │ fence")                        │
└──────────────┴────────────────────────────────┘
```

**Real CPU Instructions:**

On x86-64:
- `MFENCE` — full fence (all barrier types)
- `LFENCE` — load-load
- `SFENCE` — store-store
- `LOCK` prefix on any instruction — acts as full barrier

On ARM64:
- `DMB SY` — full system barrier
- `DMB ISH` — inner-shareable domain barrier
- `DMB ISHLD` — load-load/load-store in inner shareable

---

### 🔄 The Complete Picture — End-to-End Flow

NORMAL FLOW:
```
Thread A writes volatile field
  → JIT emits StoreStore barrier (flush pending stores)
  ← YOU ARE HERE (barrier instruction executes on CPU A)
  → CPU A's write buffer flushed to coherent shared cache
  → Thread B reads volatile field
  → JIT emits LoadLoad barrier after read
  → Thread B's CPU cache coherency protocol delivers
    the latest value (guaranteed to have post-barrier value)
  → happens-before relationship established
```

FAILURE PATH:
```
Missing barrier (no volatile / no synchronized)
  → CPU A's write buffer may hold pending writes
  → CPU B reads stale cached value from its L1 cache
  → Data race: undefined behaviour per JMM
  → May never manifest in development (x86 TSO masks it)
  → Manifests on ARM64 / POWER builds
  → Intermittent wrong results, impossible to reproduce
```

WHAT CHANGES AT SCALE:
At scale with many CPU cores, memory barrier costs increase because flushing write buffers to globally-coherent shared memory (L3 cache / DRAM) involves cache coherency protocol (MESI) messages between all cores. A spin loop with a `volatile` read on a 96-core machine generates 96× the MESI traffic compared to a single-core machine. This is why high-throughput concurrent libraries use techniques like `VarHandle.getAcquire()`/`setRelease()` (weaker but sufficient barriers) instead of full `volatile` semantics.

---

### 💻 Code Example

Example 1 — Classic double-checked locking (incorrect without volatile):
```java
// BAD: missing volatile → broken on multicore
class Singleton {
    private static Singleton instance;
    static Singleton getInstance() {
        if (instance == null) {
            synchronized (Singleton.class) {
                if (instance == null)
                    instance = new Singleton();
                    // CPU may publish reference BEFORE
                    // constructor completes (no barrier!)
            }
        }
        return instance;
    }
}

// GOOD: volatile ensures StoreStore + StoreLoad
// around the write to instance
class Singleton {
    private static volatile Singleton instance;
    static Singleton getInstance() {
        if (instance == null) {
            synchronized (Singleton.class) {
                if (instance == null)
                    instance = new Singleton();
                    // volatile write inserts barriers
                    // ensuring full construction visible
            }
        }
        return instance;
    }
}
```

Example 2 — Barrier semantics via VarHandle (Java 9+):
```java
import java.lang.invoke.*;

class Counter {
    private int value;
    static final VarHandle VALUE;
    static {
        try {
            VALUE = MethodHandles.lookup()
                .findVarHandle(Counter.class,
                               "value", int.class);
        } catch (Exception e) {
            throw new Error(e);
        }
    }

    // Full volatile semantics (StoreLoad barrier)
    void setVolatile(int x) {
        VALUE.setVolatile(this, x);
    }

    // Weaker: only StoreStore + LoadStore (cheaper)
    void setRelease(int x) {
        VALUE.setRelease(this, x);  // ARM: STLR instruct.
    }

    // Weaker: only LoadLoad + LoadStore (cheaper)
    int getAcquire() {
        return (int) VALUE.getAcquire(this); // ARM: LDAR
    }
}
```

Example 3 — Diagnosing data race without barrier:
```bash
# Use ThreadSanitizer (Java TSan via -Xss with native agent)
# Or use Java Flight Recorder to detect data races
java -XX:+UnlockDiagnosticVMOptions \
     -XX:+PrintBarriersForVolatile \
     -jar myapp.jar

# More practical: use JCStress to test memory ordering
# https://github.com/openjdk/jcstress
```

Example 4 — Unsafe barriers (advanced / last resort):
```java
// Direct barrier insertion via Unsafe (expert use only)
import sun.misc.Unsafe;
// Or via VarHandle full fence:
VarHandle.fullFence();    // full barrier (all types)
VarHandle.acquireFence(); // LoadLoad + LoadStore
VarHandle.releaseFence(); // StoreStore + LoadStore
VarHandle.loadLoadFence();  // LoadLoad only (cheapest)
VarHandle.storeStoreFence(); // StoreStore only
```

---

### ⚖️ Comparison Table

| Barrier Type | Reordering Prevented | x86-64 Cost | ARM64 Cost | Java API |
|---|---|---|---|---|
| LoadLoad | Loads from reordering | Free (TSO) | DMB ISHLD | VarHandle.loadLoadFence() |
| StoreStore | Stores from reordering | SFENCE (low) | DMB ISH (medium) | VarHandle.storeStoreFence() |
| LoadStore | Store after load reorder | Free (TSO) | DMB ISH | VarHandle.releaseFence() |
| **StoreLoad (Full)** | All reorderings | LOCK ADD (medium) | DMB SY (high) | volatile write, synchronized |

How to choose: Use `volatile` for simple flag/state sharing. Use `VarHandle.setRelease()`/`getAcquire()` in high-throughput concurrent structures where full `volatile` semantics are overkill. Use `synchronized` when you need both atomicity and barrier semantics together.

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| "Java memory barriers are irrelevant on x86" | x86's strong TSO model means fewer explicit barrier instructions, but the JMM requires them logically. They still exist. The cost difference is x86 emits cheap LOCK-prefixed instructions vs ARM's explicit DMB instructions. |
| "volatile makes a variable atomic" | volatile only provides visibility (barriers) and ordering guarantees. `volatile int` increments (`i++`) are NOT atomic — they are read-modify-write, requiring CAS or synchronized. |
| "synchronized is just a lock" | Synchronized blocks include full memory barrier semantics at entry and exit — they are both a lock and a barrier. The barrier ensures all writes before unlock are visible to the next lock acquirer. |
| "Memory barriers only affect the variable being written" | A store-load barrier after a volatile write flushes ALL pending writes to shared memory — not just the volatile variable's write. This is why a volatile write can "piggyback" ordering for other writes. |

---

### 🚨 Failure Modes & Diagnosis

**1. Data Race from Missing Barrier (Non-volatile Shared Field)**

Symptom: Intermittent wrong values in shared state; bug only reproducible on ARM/POWER hardware or high-core-count x86; never reproducible in development.

Root Cause: Reading a shared mutable field without `volatile` or `synchronized` — no barrier, stale cached value.

Diagnostic:
```bash
# JCStress — test memory ordering correctness
mvn archetype:generate \
  -DarchetypeGroupId=org.openjdk.jcstress \
  -DarchetypeArtifactId=jcstress-java-test-archetype

# Java Flight Recorder memory access profiling
java -XX:StartFlightRecording=settings=profile \
     -XX:FlightRecorderOptions=filename=/tmp/rec.jfr \
     -jar myapp.jar

# Helgrind (Valgrind) for native thread analysis
```

Prevention: All shared mutable state must be protected by `volatile`, `synchronized`, or `java.util.concurrent` classes — no exceptions on multicore systems.

**2. Incorrect Double-Checked Locking**

Symptom: Singleton returns a partially-initialised object; constructor appears to run but fields are not set; extremely rare, only on certain platforms.

Root Cause: Without `volatile` on the singleton reference, the JIT/CPU may publish the reference before the constructor's field stores are visible to other threads.

Diagnostic:
```bash
# JCStress test specifically for DCL:
# See OpenJDK jcstress tests for DoubleCheckedLocking
```

Fix: Make the singleton reference `volatile`. See Code Example 1.

Prevention: Use `volatile` for any pattern where a reference is published to other threads after construction; consider using `static` holder pattern (class initialization guarantee) as an alternative.

**3. Performance Degradation from Unnecessary Volatiles**

Symptom: Benchmark shows 10–50× performance regression in a tight loop after adding `volatile` to a counter.

Root Cause: `volatile` on a hot-path variable inserts StoreLoad barriers, preventing CPU out-of-order execution and causing cache coherency traffic.

Diagnostic:
```bash
# Profile with perf on Linux
perf stat -e cache-references,cache-misses \
          java -jar myapp.jar
# High cache-misses with volatile hot path = barrier cost
```

Fix:
```java
// BAD: volatile on every inner-loop iteration
volatile long counter = 0;
for (long i = 0; i < 1_000_000; i++) counter++;

// GOOD: accumulate locally, publish once
long localCounter = 0;
for (long i = 0; i < 1_000_000; i++) localCounter++;
counter = localCounter;  // one volatile write at end
```

Prevention: Avoid `volatile` in tight inner loops; use `LongAdder` for high-contention counters (uses internal striping to reduce barrier cost).

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**
- `JVM` — the runtime that emits CPU barrier instructions based on the JMM rules
- `Java Memory Model` — the specification that defines when barriers are required in Java programs
- `Cache Line` — the unit of CPU cache coherency; barriers flush cache lines between CPUs
- `Thread` — barriers exist to coordinate between multiple concurrent threads

**Builds On This (learn these next):**
- `volatile` — the primary Java language feature that inserts memory barriers
- `Happens-Before` — the JMM abstraction that barriers implement; reasoning at this level is easier than thinking of raw barriers
- `CAS (Compare-And-Swap)` — atomic operations that include implicit barrier semantics
- `VarHandle` — Java 9+ API providing fine-grained control over barrier types (`acquire`, `release`, `volatile`, `plain` modes)

**Alternatives / Comparisons:**
- `synchronized` — provides both mutual exclusion AND full barrier semantics; more expensive but more complete
- `StampedLock` — provides barriers via its lock/unlock operations with an optimistic no-barrier read mode

---

### 📌 Quick Reference Card

┌──────────────────────────────────────────────────────────┐
│ WHAT IT IS   │ CPU instruction preventing memory         │
│              │ operation reordering across it           │
├──────────────┼───────────────────────────────────────────┤
│ PROBLEM IT   │ CPUs and compilers reorder memory ops     │
│ SOLVES       │ for speed, breaking multi-thread          │
│              │ visibility across cores                   │
├──────────────┼───────────────────────────────────────────┤
│ KEY INSIGHT  │ Java abstracts barriers into 'volatile'   │
│              │ and 'synchronized' — you manage           │
│              │ happens-before, JVM handles barriers      │
├──────────────┼───────────────────────────────────────────┤
│ USE WHEN     │ All shared mutable state: use volatile,   │
│              │ synchronized, or java.util.concurrent     │
├──────────────┼───────────────────────────────────────────┤
│ AVOID WHEN   │ Volatile on hot-path inner loops — use    │
│              │ local accumulators published once at end  │
├──────────────┼───────────────────────────────────────────┤
│ TRADE-OFF    │ Correct concurrent visibility vs CPU      │
│              │ throughput loss from barrier flushing     │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "A Memory Barrier: the toll booth where   │
│              │ all CPU reordering stops to pay the price │
│              │ of correctness"                           │
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ volatile → Happens-Before →               │
│              │ Java Memory Model                         │
└──────────────────────────────────────────────────────────┘

---

### 🧠 Think About This Before We Continue

**Q1.** x86-64 has a Total Store Order (TSO) memory model — processors see their own writes in order, and all CPUs agree on a global store order. ARM64 uses a weaker memory model where stores from different CPUs may be observed in different orders. A Java `volatile` write emits a `LOCK ADD esp, 0` on x86-64 but a `DMB ISH` (Data Memory Barrier, Inner Shareable) on ARM64. Given that TSO already prevents most reorderings, why does the JVM still emit a barrier instruction for `volatile` on x86-64 — and which specific reordering does the x86 TSO model permit that the Java Memory Model forbids without the barrier?

**Q2.** `LongAdder` in Java achieves much higher throughput than `AtomicLong` for concurrent increment operations by using internal "cells" (striped counters) that accumulate locally and are summed only on `sum()`. How does this design reduce memory barrier traffic compared to a single `AtomicLong` — and what correctness trade-off does `LongAdder` accept that makes it unsuitable for use cases where `AtomicLong` is required?

