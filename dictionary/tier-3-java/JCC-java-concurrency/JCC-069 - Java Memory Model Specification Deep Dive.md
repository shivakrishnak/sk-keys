---
id: JCC-080
title: Java Memory Model Specification Deep Dive
category: Java Concurrency
tier: tier-3-java
folder: JCC-java-concurrency
difficulty: ★★★
depends_on: JCC-044, JCC-014, JCC-038
used_by:
related: JCC-044, JCC-057, JCC-045
tags:
  - java
  - concurrency
  - advanced
  - deep-dive
  - internals
  - memory
status: complete
version: 2
layout: default
parent: "Java Concurrency"
grand_parent: "Technical Dictionary"
nav_order: 69
permalink: /jcc/java-memory-model-specification-deep-dive/
---

# JCC-069 - Java Memory Model Specification Deep Dive

⚡ TL;DR - The JMM formally defines which values a read is allowed to see using happens-before (HB) relations - six rules that determine when one thread's writes are guaranteed visible to another thread's reads.

| Metadata        |                           |     |
| :-------------- | :------------------------ | :-- |
| **Depends on:** | JCC-044, JCC-014, JCC-038 |     |
| **Related:**    | JCC-044, JCC-057, JCC-045 |     |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
You write a concurrent program. Thread A writes to a field. Thread B reads it. Will Thread B see Thread A's write? Without a formal memory model, the answer is "maybe" - it depends on the CPU architecture, JVM implementation, and compiler optimization choices. Different JVMs could give different answers on the same hardware. Code that works on x86 might fail on ARM or SPARC.

**THE BREAKING POINT:**
Java 1.0-1.3 had no formal memory model. Programmers used `synchronized` based on folklore. The `volatile` keyword existed but its semantics were unclear. Programs that "worked" on one JVM broke on another. Double-checked locking (a common optimization) was broken by undefined memory model semantics. This was documented publicly in 2001.

**THE INVENTION MOMENT:**
JSR-133 (2004, Java 5) introduced the formal Java Memory Model. It defines a partial order over program actions called "happens-before" (HB). If action A HB action B, then B is guaranteed to see A's effects. The JMM specifies exactly when HB holds, enabling compilers and hardware to optimize aggressively while guaranteeing correctness when synchronization is used.

**EVOLUTION:**
Java 5 (JSR-133): formal JMM with happens-before semantics. Java 9+: `VarHandle` provides fine-grained memory access modes (plain, opaque, acquire/release, volatile) based on the JMM's memory ordering model.

---

### 📘 Textbook Definition

The **Java Memory Model (JMM) specification** (Java Language Specification, Chapter 17.4) defines the legal results of reads and writes to shared memory in concurrent programs. It introduces **actions** (reads, writes, lock/unlock, thread start/join) and a **happens-before (HB) partial order** over those actions. A read is allowed to observe a write W if W HB the read, or if no HB-intervening write exists between them. The JMM permits compilers and hardware to reorder instructions freely within a single thread (preserving intra-thread semantics) but prohibits reorderings that would violate happens-before guarantees across threads.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
The JMM defines one thing: when can thread B be guaranteed to see thread A's write? The answer: when A's write happens-before B's read.

**One analogy:**

> The JMM is like a postal guarantee. Without a guarantee (no synchronization), a letter sent by A might arrive at B in any order. With a "guaranteed delivery" stamp (happens-before), the postal service promises B receives the letter before any subsequent letters. Without the stamp, the service can reorder or delay letters for efficiency. The JMM defines what stamps exist and what they guarantee.

**One insight:**
The JMM does not say "use `synchronized` to be safe." It says exactly which actions establish happens-before and which reads are guaranteed to see which writes. Understanding the JMM means understanding the exact guarantee - no more, no less.

---

### 🔩 First Principles Explanation

**CORE INVARIANTS:**

1. **Program order within a thread:** If A comes before B in program order within one thread, then A HB B.
2. **Monitor unlock/lock:** An unlock of monitor M HB every subsequent lock of M.
3. **volatile write/read:** A write to volatile field f HB every subsequent read of f.
4. **Thread start:** `thread.start()` HB every action in the started thread.
5. **Thread join:** All actions in a thread HB the return from `thread.join()`.
6. **Transitivity:** If A HB B and B HB C, then A HB C.

**DERIVED DESIGN:**
Given invariants 2 and 3: `synchronized` and `volatile` are the two primary HB-establishing mechanisms. Any correct concurrent program sharing data between threads must use at least one.

Given invariant 6 (transitivity): if Thread A writes to non-volatile fields then writes to a volatile field, and Thread B reads that volatile then reads the non-volatile fields, then B is guaranteed to see A's non-volatile writes. The transitivity carries the guarantee through the volatile as a "piggyback."

**THE TRADE-OFFS:**
**Gain:** Precise guarantees. The JMM tells you exactly what to synchronize, not more. Over-synchronization is unnecessary if you understand the model.
**Cost:** The model is subtle. Most developers operate on simplified mental models. Full JMM reasoning is only required for lock-free or low-level concurrent code.

**ESSENTIAL vs ACCIDENTAL COMPLEXITY:**
**Essential:** Any concurrent system accessing shared memory must have a memory visibility model. The JMM is that model.
**Accidental:** The difficulty of reasoning about JMM guarantees for complex programs. Tools like `jcstress` verify JMM compliance experimentally.

---

### 🧪 Thought Experiment

**SETUP:**
Thread A performs: `x = 1; flag = true;` (both non-volatile, no sync). Thread B: `if (flag) print(x);`. Can B ever print 0?

**WITHOUT JMM UNDERSTANDING:**
"A sets x=1 before flag=true. B checks flag first. If flag is true, x must be 1." This seems correct but is WRONG.

**WITH JMM:**
No happens-before exists between A's write to `x` and B's read of `x`. Therefore:

1. The compiler may reorder A's operations (set `flag=true` before `x=1`).
2. B's CPU core may see A's writes in a different order due to store buffering.
3. B may legitimately see `flag=true` but `x=0`.

**FIX - Make flag volatile:**
A: `x=1` --[PO]--> A: `flag=true` --[volatile HB]--> B: read `flag` --[PO]--> B: read `x`. By transitivity: A's write to `x` HB B's read of `x`. B is guaranteed to see `x=1`.

**THE INSIGHT:**
`volatile` on the flag establishes a happens-before chain that carries the visibility guarantee for ALL earlier writes by A. This is the "volatile as publication mechanism" pattern.

---

### 🧠 Mental Model / Analogy

> The JMM's happens-before is like a causal dependency graph in a distributed system. A message cannot be seen before its causal predecessors (vector clocks). Similarly, Thread B cannot be forced to see write W until a HB chain connects W to B's read. Without that chain (a "message" in the form of a `volatile` read/write or `synchronized` unlock/lock), the visibility guarantee does not exist.

Element mapping:

- **Vector clock message** = HB-establishing action (volatile write, lock release)
- **Causal predecessor** = action A that must be visible before action B
- **Out-of-order delivery** = CPU reordering that the JMM permits without HB
- **Causal consistency** = happens-before guarantees

Where this analogy breaks down: distributed systems have network partitions. JMM issues arise from CPU caching and compiler optimization within a single JVM process.

---

### 📶 Gradual Depth - Four Levels

**Level 1 - What it is (anyone can understand):**
The JMM is Java's rulebook for when one thread's writes are visible to another's reads. Will Thread B see what Thread A wrote? Yes if the code establishes a happens-before chain, no otherwise.

**Level 2 - How to use it (junior developer):**
Practical rules: use `synchronized` for shared mutable state, `volatile` for flags/status fields read/written by multiple threads, `java.util.concurrent` classes for data structures. The JMM guarantees are satisfied by these constructs.

**Level 3 - How it works (mid-level engineer):**
Six rules establish happens-before. Every Java synchronization construct is defined in terms of these rules. `ReentrantLock.unlock()` HB `lock()` (like monitor). `AtomicInteger.set()` is a volatile write. `CompletableFuture.complete()` establishes HB for `join()`.

**Level 4 - Why it was designed this way (senior/staff):**
The JMM is a "weak memory model" allowing significant reordering for performance. x86 TSO allows store-load reordering. ARM allows more. The JMM abstracts over all architectures with a single formal model. `VarHandle` access modes (`getAcquire`, `setRelease`) expose memory barriers at the Java level for maximum performance with minimal barriers. Each access mode corresponds to specific hardware fence instructions.

**Expert Thinking Cues:**

- "Does a happens-before chain exist between this write and that read? If not, the read may see a stale value."
- "Which access mode does this `VarHandle` use? Each has different HB semantics."
- "Can I prove that every required HB is established in this lock-free algorithm?"

---

### ⚙️ How It Works (Mechanism)

**PUBLICATION IDIOM:**

```java
// Safe publication via volatile
class SafePublication {
    private int x;
    private volatile boolean ready;

    // Thread A:
    public void publish() {
        x = 42;         // (1) non-volatile write
        ready = true;   // (2) volatile write -> HB
    }

    // Thread B:
    public void consume() {
        if (ready) {        // (3) volatile read
            print(x);       // (4) guaranteed to see 42
        }
    }
    // HB chain: (1) PO (2) volatile-HB (3) PO (4)
    // => (1) HB (4) by transitivity
}
```

**DOUBLE-CHECKED LOCKING (CORRECT):**

```java
class Singleton {
    // volatile is REQUIRED for DCL correctness
    private static volatile Singleton instance;

    public static Singleton getInstance() {
        if (instance == null) {       // outer check
            synchronized (Singleton.class) {
                if (instance == null) {  // inner check
                    instance = new Singleton();
                }
            }
        }
        return instance; // safe: volatile HB established
    }
}
```

**VARHANDLE MEMORY MODES:**

```java
VarHandle vh = /* ... */;
vh.set(obj, 42);           // plain: no HB guarantee
vh.setOpaque(obj, 42);     // atomic, no ordering
vh.setRelease(obj, 42);    // release barrier (pair w/ acquire)
vh.setVolatile(obj, 42);   // full HB: volatile semantics
```

---

### 🔄 The Complete Picture - End-to-End Flow

**HAPPENS-BEFORE CHAIN ANALYSIS:**

```
Thread A:
  write x=1  --[PO]--> write flag=true(volatile)
                                |
                          [volatile HB]
                                |
Thread B:                       v
  read flag(volatile) --[PO]--> read x
            ^
            |------- YOU ARE HERE (analyzing chain)

Conclusion: A:write(x=1) HB B:read(x) by transitivity
=> B is guaranteed to see x=1
```

**FAILURE PATH:**
`flag` not volatile. No HB from A's writes to B's reads. JMM permits B to see `flag=true` but `x=0` due to CPU store buffering or compiler reordering. May pass all tests on x86 (stronger model) but fail on ARM.

**WHAT CHANGES AT SCALE:**
The JMM becomes critical in lock-free algorithms, custom concurrent data structures, and publication patterns. For everyday application code using `synchronized` and `java.util.concurrent`, the JMM guarantees are automatically satisfied. Explicit JMM reasoning is only required for custom concurrent code.

---

### ⚖️ Comparison Table

| Memory Access Mode | JMM Guarantee           | Typical Use           | VarHandle Mode                  |
| ------------------ | ----------------------- | --------------------- | ------------------------------- |
| Plain read/write   | No cross-thread HB      | Single-thread only    | `get()`/`set()`                 |
| Volatile           | Full HB on every access | Flags, published refs | `getVolatile()`/`setVolatile()` |
| Acquire/Release    | HB for paired ops       | Lock-free algorithms  | `getAcquire()`/`setRelease()`   |
| Opaque             | Atomicity, no HB order  | Monotonic counters    | `getOpaque()`/`setOpaque()`     |
| CAS                | Conditional atomic + HB | Lock-free update      | `compareAndSet()`               |

---

### ⚠️ Common Misconceptions

| Misconception                                               | Reality                                                                                                                                            |
| ----------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------- |
| "`synchronized` makes ALL variables visible to ALL threads" | `synchronized` establishes HB between unlock and subsequent lock of the SAME monitor. Only state in that block is covered.                         |
| "`volatile` makes a variable thread-safe"                   | `volatile` establishes HB for reads/writes of that variable. It does NOT make compound operations (like `++`) atomic.                              |
| "The JMM only matters for lock-free code"                   | The JMM is relevant for all concurrent code. `synchronized` and `java.util.concurrent` implement JMM rules - understanding why requires the model. |
| "Tests prove JMM correctness"                               | Tests on x86 may pass. The same code may fail on ARM. Use `jcstress` for JMM correctness testing.                                                  |
| "The JMM guarantees a total order of operations"            | The JMM defines a PARTIAL order (happens-before). Operations without an HB relationship have undefined relative order.                             |

---

### 🚨 Failure Modes & Diagnosis

**Failure Mode 1: Visibility Bug - Non-Volatile Flag**
**Symptom:** Background thread keeps running after `stop = true` is set. Loop runs forever.
**Root Cause:** `stop` field is not `volatile`. Thread's CPU caches the value; Thread A's write is in store buffer but not visible to B.
**Diagnostic:**

```bash
# JIT may hoist non-volatile read out of loop
-XX:+PrintCompilation
# Thread dump: check background thread in tight loop
jstack <pid> | grep -A 10 "background-thread"
```

**Fix:**

```java
// BAD: non-volatile stop flag
private boolean stop = false;

// GOOD: volatile ensures visibility
private volatile boolean stop = false;
```

**Prevention:** All fields written by one thread and read by another must use `volatile`, `synchronized`, or `java.util.concurrent`.

---

**Failure Mode 2: Broken Double-Checked Locking**
**Symptom:** `getInstance()` occasionally returns an incompletely initialized object. NPE or incorrect field values.
**Root Cause:** Without `volatile` on the instance field, JIT may publish the reference before the constructor completes.
**Diagnostic:**

```bash
grep -rn "instance == null.*synchronized" src/
# Check: is instance field volatile?
```

**Fix:** Add `volatile` to instance field (Java 5+), or use initialization-on-demand holder idiom:

```java
private static class Holder {
    static final Singleton INSTANCE = new Singleton();
}
public static Singleton getInstance() {
    return Holder.INSTANCE; // class loading = safe pub
}
```

**Prevention:** Never implement DCL manually. Use holder idiom or `enum` singleton.

---

**Failure Mode 3: Reordering Bug on ARM/POWER**
**Symptom:** Lock-free code passes all tests on x86 but fails on ARM or POWER architectures.
**Root Cause:** x86 TSO prevents most reorderings that the JMM permits. Code implicitly relying on x86 ordering breaks on weaker architectures.
**Diagnostic:**

```bash
# Run jcstress on ARM emulator or cross-compile target
mvn verify -pl jcstress-tests
# Reports observed states violating JMM guarantees
```

**Fix:** Use appropriate `VarHandle` access modes or `volatile` for all cross-thread state. Never rely on "worked on x86" for JMM correctness.
**Prevention:** Use `jcstress` in CI for any lock-free code.

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**

- [[JCC-044 - Java Memory Model (JMM)]] - the foundational JMM entry
- [[JCC-014 - synchronized]] - implements JMM monitor rules
- [[JCC-038 - volatile]] - implements JMM volatile rules

**Builds On This (learn these next):**

- [[JCC-057 - VarHandle]] - fine-grained JMM access modes
- [[JCC-045 - CAS (Compare-And-Swap)]] - CAS semantics under the JMM

**Alternatives / Comparisons:**

- [[JCC-040 - ReentrantLock]] - lock semantics equivalent to monitor in JMM terms

---

### 📌 Quick Reference Card

```
┌────────────────────────────────────────────────────┐
│ WHAT IT IS    │ Formal rules for cross-thread      │
│               │ memory visibility in Java (JLS 17) │
│ PROBLEM       │ When does B see what A wrote?      │
│ KEY INSIGHT   │ Happens-before chain = visibility  │
│ USE WHEN      │ Writing lock-free/low-level code   │
│ AVOID WHEN    │ N/A: always applies to shared state│
│ TRADE-OFF     │ Performance vs. memory barrier cost│
│ ONE-LINER     │ A HB B = B sees A's effects;       │
│               │ no HB = undefined result           │
│ NEXT EXPLORE  │ JCC-057 VarHandle                  │
└────────────────────────────────────────────────────┘
```

**If you remember only 3 things:**

1. Happens-before (HB): the only guarantee of cross-thread visibility in Java. No HB = no guarantee.
2. Six HB rules: program order, monitor, volatile, thread start, thread join, transitivity.
3. A volatile "flag" write carries happens-before for ALL earlier non-volatile writes by the same thread.

**Interview one-liner:**
"The JMM defines when Thread B is guaranteed to see Thread A's writes using happens-before relations - six rules including: synchronized unlock/lock, volatile write/read, thread start, thread join, program order, and transitivity."

---

### 💎 Transferable Wisdom

**Reusable Engineering Principle:**
Every concurrent system sharing state between threads needs a formal specification of when writes become visible to readers. Without one, behavior depends on CPU architecture and compiler optimization - making correctness untestable. The JMM is Java's such specification. Understanding it prevents a class of correctness bugs that appear only under specific hardware/JVM conditions.

**Where else this pattern appears:**

- **C++11 memory model:** `std::atomic` with `memory_order_acquire/release/seq_cst` is the C++ equivalent of `VarHandle` access modes - the same concept of happens-before ordering.
- **Linux kernel memory model (LKMM):** `smp_rmb()`, `smp_wmb()`, `smp_mb()` fence instructions map to the same acquire/release/full fence concepts.
- **Database isolation levels:** READ COMMITTED, REPEATABLE READ, SERIALIZABLE are visibility models for concurrent transactions - the same fundamental question as the JMM: what values can a read observe?

---

### 💡 The Surprising Truth

The famous double-checked locking idiom was published in Pattern Languages of Program Design 3 (1998) and was considered a standard Java optimization for years. In 2001, Bill Pugh published "The Java Memory Model is Broken" demonstrating that double-checked locking was fundamentally unsafe in Java 1.0-1.4 due to the lack of a formal memory model. Hundreds of production systems were using broken code. The fix required Java 5's JSR-133 and adding `volatile` to the instance field. This single bug, affecting a widely-used optimization pattern, was the primary driver for formalizing the JMM in Java 5. The JMM exists largely because of double-checked locking.

---

### 🧠 Think About This Before We Continue

**Q1 (E - First Principles):** The JMM says a write to volatile field `f` happens-before every SUBSEQUENT read of `f`. What does "subsequent" mean in a concurrent system with no global clock? How does the JMM define "subsequent" without a total order over all operations?
_Hint:_ "Subsequent" in the JMM means the read OBSERVES the write (or a later write to `f`). The JMM defines which reads can observe which writes, not a global time ordering.

**Q2 (A - System Interaction):** `AtomicInteger.incrementAndGet()` returns the new value atomically. Under the JMM, what memory ordering does this operation provide? Can it serve as a happens-before mechanism to ensure visibility of non-atomic operations performed before the increment?
_Hint:_ Atomic operations in `java.util.concurrent.atomic` use volatile semantics in Java. `incrementAndGet()` has the memory ordering of a volatile read followed by a volatile write. Trace the HB chain.

**Q3 (C - Design Trade-off):** `VarHandle` provides four memory access modes: plain, opaque, acquire/release, and volatile (full fence). Why would you ever use a weaker mode instead of always using volatile? What do you lose by using plain mode, and what do you gain?
_Hint:_ A volatile access on x86 requires a full memory barrier instruction. Plain access requires none. The cost of unnecessary barriers in a hot loop is measurable. When is the weaker guarantee sufficient (e.g., single-threaded access with volatile for publication only)?
