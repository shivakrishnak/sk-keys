---
id: JLG-087
title: Java Language Specification Deep Dive
category: Java Language
tier: tier-3-java
folder: JLG-java-language
difficulty: ★★★
depends_on: JLG-001, JLG-075
used_by: JLG-079, JLG-080
related: JLG-081, JLG-082, JLG-083
tags:
  - java
  - advanced
  - internals
  - deep-dive
status: complete
version: 3
layout: default
parent: "Java Language"
grand_parent: "Technical Dictionary"
nav_order: 78
permalink: /jlg/java-language-specification-deep-dive/
---

# JLG-078 - Java Language Specification Deep Dive

⚡ TL;DR - The Java Language Specification (JLS) and Java Memory Model (JMM) define happens-before ordering; without it, multi-threaded code has undefined behaviour regardless of hardware correctness.

| Field | Value |
|---|---|
| **Depends on** | [[JLG-001 - What Is Java - History and Philosophy]], [[JLG-075 - Java Modularity Strategy (JPMS)]] |
| **Used by** | [[JLG-079 - Project Valhalla - Value Types and Primitives]], [[JLG-080 - Project Panama - Foreign Function and Memory API]] |
| **Related** | [[JLG-081 - Java Language Design History and Rationale]], [[JLG-082 - Java API Design Thinking]], [[JLG-083 - Language Feature Trade-off Framing]] |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**

Early Java (1.0-1.4) had a Java Memory Model that was informally specified and incorrect. The `double-checked locking` idiom for lazy initialisation was widely used and widely broken - it could return a partially initialised object because the JMM did not prohibit JVMs from reordering stores. Code that worked on one JVM with one GC mode would fail non-deterministically on another. There was no authoritative answer to "is this multi-threaded code correct?"

**THE BREAKING POINT:**

Doug Lea (java.util.concurrent author) demonstrated that every concurrent data structure could be incorrect under the old JMM. Multiple JVM vendors implemented memory visibility differently. The Java promise of "write once, run anywhere" was violated for concurrent code.

**THE INVENTION MOMENT:**

**JSR-133** (Jeremy Manson, Brian Goetz, Bill Pugh, 2004) rewrote the Java Memory Model as part of Java 5. The new JMM defines "happens-before" as the formal ordering relation: if action A happens-before action B, then A's effects are visible to B. `synchronized`, `volatile`, `Thread.start()`, `Thread.join()`, and `final` field assignments all create happens-before edges. The JLS became the authoritative specification.

**EVOLUTION:**

- **1996:** Java 1.0 JMM - informal, incorrect; allows double-checked locking bugs
- **2004:** JSR-133 / Java 5 - JMM rewritten with happens-before; `volatile` gets full sequential consistency
- **2006:** JLS §17 (Threads and Locks) finalised
- **2014:** Java 8 - JLS updated for streams, lambdas (no JMM changes)
- **2017:** Java 9 - JLS updated for modules (JPMS); VarHandles add finer-grained access modes
- **2023:** Java 21 - JLS updated for virtual threads; `synchronized` on virtual threads pins carrier thread

---

### 📘 Textbook Definition

The **Java Language Specification (JLS)** is the authoritative formal document defining Java syntax, semantics, and execution model. Key components:

- **JLS §17 - Threads and Locks:** defines the Java Memory Model (JMM), happens-before relation, synchronisation actions, and correct multi-threaded behaviour
- **Java Memory Model (JMM):** defines which writes are visible to which reads across threads; based on happens-before partial order
- **Happens-before:** relation between two actions where action A's result is guaranteed visible to action B; established by: monitor unlock/lock, `volatile` write/read, `Thread.start()`/actions in thread, thread completion/`Thread.join()`

---

### ⏱️ Understand It in 30 Seconds

**One line:** The JMM defines happens-before ordering; without it, the JVM can reorder and cache writes, making multi-threaded code have undefined behaviour.

> The JMM is like postal delivery guarantees. Without guarantees, letters (writes) might arrive out of order or not at all. `synchronized` is like registered mail with tracking - guaranteed delivery in order. `volatile` is like express mail - immediate delivery but no bundling. The JLS is the postal rulebook that all mail carriers (JVM implementations) must follow.

**One insight:** `volatile` does not mean "stored in RAM." It means "no caching, full visibility guarantee" - the JVM cannot store a `volatile` variable in a CPU register and must emit the appropriate memory barrier instruction. On modern CPUs, this is usually a store-load fence.

---

### 🔩 First Principles Explanation

**CORE INVARIANTS:**

1. Modern CPUs execute instructions out of order and cache writes in store buffers; the JMM defines what the JVM must guarantee despite this
2. Without happens-before, a thread can read stale values from another thread indefinitely
3. A happens-before edge requires the JVM to emit a memory barrier instruction that flushes store buffers
4. `final` fields in a properly constructed object are safely published even without synchronisation
5. `double-checked locking` is safe only with `volatile` on the field (guarantees happens-before)

**DERIVED DESIGN:**

From invariant 2 → `volatile` fields always read from main memory (the JVM emits `MFENCE` or `LOCK` prefix on x86).
From invariant 4 → immutable objects can be safely shared across threads without synchronisation, provided their `final` fields are written in the constructor.
From invariant 5 → the fixed double-checked locking pattern requires `private volatile Singleton instance;` to be correct.

**THE TRADE-OFFS:**

**Gain:** Portable concurrent Java code; behaviour is defined by the JLS, not by the JVM implementation or CPU architecture.

**Cost:** Memory barrier instructions have throughput cost (2-20 cycles each); excessive `volatile` or `synchronized` reduces concurrency; the JMM is complex and easy to misapply.

**ESSENTIAL vs ACCIDENTAL COMPLEXITY:**

**Essential:** The JMM itself is essential; without a formal memory model, no concurrent code is portable.

**Accidental:** The complexity of reasoning about individual happens-before chains in complex code is accidental; `java.util.concurrent` abstractions (`ConcurrentHashMap`, `CountDownLatch`, `AtomicReference`) encapsulate correct happens-before chains.

---

### 🧪 Thought Experiment

**SETUP:** Two threads, Thread A and Thread B, share `boolean ready = false` and `int data = 0`. Thread A sets `data = 42` then `ready = true`. Thread B spins on `ready` and reads `data` when ready.

**WHAT HAPPENS WITHOUT JMM (pre-Java 5 or missing volatile):**

Thread B can see `ready == true` and `data == 0`. Why? The CPU store buffer can flush `ready = true` before `data = 42`. The JVM compiler can reorder the stores. Thread B reads a stale `data` value. Code is subtly wrong.

**WHAT HAPPENS WITH CORRECT JMM:**

Mark `ready` as `volatile`. Now: `data = 42` happens-before the volatile write `ready = true`. The volatile read of `ready == true` in Thread B happens-after the volatile write. Therefore `data = 42` happens-before Thread B reads `data`. Thread B is guaranteed to see `data == 42`.

**THE INSIGHT:**

The guarantee is not about RAM. It is about a happens-before chain. The JVM emits a store-load fence after the volatile write, forcing all prior stores out of the CPU store buffer before the next load.

---

### 🧠 Mental Model / Analogy

> The JMM happens-before relation is like a chain of custody in evidence law. Evidence (a write) is only admissible (visible to a thread) if there is a documented chain of custody (happens-before chain) from collection to admission. Breaking the chain (missing synchronisation) means the evidence may be inadmissible (read may see stale data). `volatile` and `synchronized` are the official chain-of-custody seals.

**Element mapping:**
- Evidence write → memory write by one thread
- Chain of custody → happens-before chain
- Evidence admissibility → read visibility guarantee
- Official seal → `volatile`, `synchronized`, `final`
- Broken chain → data race (undefined behaviour)

Where this analogy breaks down: in law, broken chain of custody makes evidence inadmissible; in Java, a data race produces undefined behaviour (the JVM may return any value, not just stale ones).

---

### 📶 Gradual Depth - Four Levels

**Level 1 - What it is (anyone can understand):**
When multiple threads share data, they might read stale values because CPUs use caches. Java has rules (the JMM) that tell the JVM when a write from one thread must be visible to another thread. `volatile` and `synchronized` are the keywords that activate these visibility guarantees.

**Level 2 - How to use it (junior developer):**
```java
// Safe double-checked locking (Java 5+):
class Singleton {
    // volatile required for correctness:
    private volatile Singleton instance;

    public Singleton getInstance() {
        if (instance == null) {     // 1st check
            synchronized (this) {
                if (instance == null) {// 2nd check
                    instance = new Singleton();
                }
            }
        }
        return instance;
    }
}
```
The `volatile` on `instance` creates a happens-before between the write inside `synchronized` and all subsequent reads outside it.

**Level 3 - How it works (mid-level engineer):**
When a thread writes to a `volatile` field, the JVM emits a store-store barrier (ensures prior stores are committed) followed by a store-load barrier (ensures no later load is moved before this store). Reading a `volatile` field emits a load-load barrier and a load-store barrier. On x86, `volatile` reads are free (x86 TSO memory model gives load ordering by default); `volatile` writes require `LOCK ADD [rsp], 0` or equivalent to drain the store buffer.

**Level 4 - Why it was designed this way (senior/staff):**
The JSR-133 JMM was designed to be implementable on all CPU architectures, not just x86. ARM, POWER, and SPARC have weaker memory models than x86; they allow more reordering. The happens-before formalism is architecture-neutral - it specifies the guarantee without requiring x86's total store order. This enables JVM implementations on weak-consistency architectures to be correct by inserting only the barriers that the architecture requires, rather than the strongest possible barriers. The result is a JMM that can be efficiently implemented on all CPUs while still providing portable guarantees.

**Expert Thinking Cues:**
- VarHandles (Java 9+, JEP 193) add `getPlain/getOpaque/getAcquire/getVolatile` access modes exposing the full acquire-release memory ordering hierarchy below `volatile`
- `Unsafe.putOrdered` (used by many low-latency frameworks) is `lazySet` - a weaker store that is cheaper than `volatile` write; no store-load fence
- The `final` field guarantee (JLS §17.5) means that even a reference published through a data race is safe to use if the referenced object's fields are `final`

---

### ⚙️ How It Works (Mechanism)

```
Happens-Before Edges (JLS §17.4.5):

Monitor actions:
  synchronized unlock ──HB──> lock

Volatile variable:
  volatile write ──HB──> volatile read

Thread lifecycle:
  Thread.start() ──HB──> first thread action
  last thread action ──HB──> Thread.join()

Final fields:
  constructor final write ──HB──> any read
  (via safe publication guarantee)

Transitivity:
  if A ──HB──> B and B ──HB──> C
  then A ──HB──> C

JVM Implementation:
  HB edge → memory barrier instruction
  x86: LOCK ADD [rsp],0 after volatile write
  ARM: DMB ISH (data memory barrier)
```

---

### 🔄 The Complete Picture - End-to-End Flow

**NORMAL FLOW:**

```
[Thread A writes shared data]
     |
     ├─ Write data = 42
     |    ← YOU ARE HERE
     |
     ├─ volatile write: ready = true
     |    (store-load fence emitted by JVM)
     |    Creates HB edge
     |
[Thread B reads shared data]
     |
     ├─ volatile read: ready (sees true)
     |    (load-load fence emitted)
     |    HB chain: A write -> A volatile
     |    write -> B volatile read -> B read
     |
     └─ read data (guaranteed to see 42)
```

**FAILURE PATH:**

Missing `volatile` on `ready`: Thread B sees `ready == true` but reads `data == 0`. The JVM is correct per spec - no happens-before chain was established.

**WHAT CHANGES AT SCALE:**

At scale, excessive `volatile` and `synchronized` create memory barrier bottlenecks. Cache-line false sharing (two `volatile` fields in the same 64-byte cache line) causes cache coherence traffic. Solutions: `@Contended` annotation (JVM padding), `VarHandle` with weaker access modes, lock-free algorithms using CAS.

---

### 💻 Code Example

**JMM in practice - common patterns:**

```java
// BAD: data race, no happens-before
class Cache {
    private Object data;
    private boolean ready;

    public void set(Object v) {
        this.data = v;
        this.ready = true; // no HB guarantee
    }
    public Object get() {
        // May return null even if ready=true
        // because no HB chain exists
        if (ready) return data;
        return null;
    }
}

// GOOD: volatile establishes HB chain
class Cache {
    private volatile Object data;
    // volatile write/read creates HB:
    // set(data) HB-before get() sees data

    public void set(Object v) {
        this.data = v; // volatile write
    }
    public Object get() {
        return this.data; // volatile read
    }
}

// GOOD: final fields - no sync needed
record ImmutablePoint(int x, int y) {
    // final fields: safe publication
    // Consumer can read x,y without sync
    // once reference is safely published
}
```

**How to test / verify correctness:**

```bash
# Detect data races with JCStress (OpenJDK):
# JCStress is the authoritative concurrency
# testing framework for JMM compliance

# Run stress test:
java -jar jcstress.jar -t MyStressTest

# Use ThreadSanitizer (Clang-based):
# Not native to Java, but available via
# GraalVM native-image compilation
```

---

### ⚖️ Comparison Table

| Memory Ordering Level | Java Keyword / API | Overhead | Guarantee |
|---|---|---|---|
| None | Plain field access | Zero | No cross-thread visibility |
| Opaque | `VarHandle.getOpaque()` | ~0 | Coherent per-variable |
| Acquire/Release | `VarHandle.getAcquire/Release()` | Low | Acquire-release pairs |
| Sequential Consistency | `volatile` | Medium | Total order |
| Mutual Exclusion | `synchronized` | Higher | Mutual exclusion + HB |

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| "`volatile` means stored in RAM, not CPU cache" | `volatile` means the JVM emits memory barriers; modern CPUs still use L1/L2 cache, but cache coherence protocols ensure visibility. It is about ordering guarantees, not cache bypass. |
| "`synchronized` prevents reordering everywhere" | `synchronized` creates HB at lock/unlock boundaries within the synchronized block. Code outside the `synchronized` block is not protected. |
| "If my unit tests pass, multi-threaded code is correct" | Data races are timing-dependent. Tests rarely trigger the specific interleavings that expose bugs. JCStress and formal reasoning are needed for correctness assurance. |
| "`AtomicInteger` is always faster than `synchronized`" | For highly contended updates, `LongAdder` (Java 8) outperforms both by using per-thread counters that are summed on read. `AtomicInteger` CAS loops spin under high contention. |
| "Java 9 VarHandles replace `volatile`" | VarHandles ADD finer access modes below `volatile`. `volatile` still works and is simpler for most use cases. VarHandles are for expert lock-free algorithm authors. |

---

### 🚨 Failure Modes & Diagnosis

**Mode 1: Visibility bug from missing volatile**

**Symptom:** Thread B loops forever waiting for `running = false` set by Thread A, even after Thread A sets it.

**Root Cause:** JVM hoists `running` check out of loop (valid optimisation without `volatile`). Thread B reads a cached `true` value forever.

**Diagnostic:**
```bash
# Run with JVM optimisation disabled to
# expose the bug in testing:
java -Xint MyApp
# If hang disappears with -Xint but occurs
# normally, confirms JIT-related visibility

# Use FindBugs/SpotBugs:
spotbugs -textui -effort:max classes/
# Detects IS2_INCONSISTENT_SYNC patterns
```

**Fix:** Declare `private volatile boolean running;`

**Prevention:** Code review checklist: all fields shared across threads must be `volatile`, `AtomicXxx`, inside `synchronized`, or `final`.

---

**Mode 2: Broken double-checked locking (pre-Java 5 pattern)**

**Symptom:** Singleton returns a partially initialised object. NPE from a field that should have been set in the constructor.

**Root Cause:** `instance = new Singleton()` is three steps: allocate memory, initialise fields, assign reference. Without `volatile`, the JVM can publish the reference (assign to `instance`) before initialising fields. The second thread sees non-null `instance` but uninitialised fields.

**Diagnostic:**
```java
// Check: is volatile present?
grep -n "volatile" Singleton.java
// If volatile is missing, the pattern is broken
```

**Fix:** Add `volatile` to the `instance` field declaration (see Code Example section).

**Prevention:** Use holder class pattern instead of double-checked locking:
```java
class Singleton {
    private static class Holder {
        // class loading is thread-safe:
        static final Singleton INSTANCE
            = new Singleton();
    }
    public static Singleton get() {
        return Holder.INSTANCE;
    }
}
```

---

**Mode 3: False sharing degrades parallel throughput (Performance)**

**Symptom:** A thread-local counter array runs 5x slower with 8 threads than with 1 thread. The array is `volatile long[] counters = new long[8]`.

**Root Cause:** `counters[0]` and `counters[1]` share a 64-byte CPU cache line. When Thread 0 writes `counters[0]`, it invalidates the cache line for all CPUs. Thread 1 writing `counters[1]` does the same. Ping-pong traffic between CPU caches.

**Diagnostic:**
```bash
# Check cache line contention with perf:
perf stat -e \
  cache-misses,cache-references \
  java MyCounterApp
# High cache-miss ratio with many threads
# indicates false sharing
```

**Fix:**
```java
// Pad each counter to 64 bytes:
@sun.misc.Contended
static final class PaddedCounter {
    volatile long value;
}
PaddedCounter[] counters =
    new PaddedCounter[THREADS];
// JVM flag required:
// -XX:-RestrictContended
```

**Prevention:** Use `LongAdder` which handles striping internally. Avoid `volatile` arrays with per-thread indices.

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**
- [[JLG-001 - What Is Java - History and Philosophy]] - JVM architecture; WORA promise
- [[JLG-075 - Java Modularity Strategy (JPMS)]] - module system knowledge for JLS context

**Builds On This (learn these next):**
- [[JLG-079 - Project Valhalla - Value Types and Primitives]] - JMM implications for value types
- [[JLG-080 - Project Panama - Foreign Function and Memory API]] - FFM memory ordering at native boundary

**Alternatives / Comparisons:**
- C++ Memory Model (C++11) - similar happens-before model; `std::atomic` analogous to Java `volatile`/`VarHandle`
- Go Memory Model - similar formal happens-before; goroutine channels are the primary synchronisation primitive

---

### 📌 Quick Reference Card

```
+----------------------------------------------------------+
| WHAT IT IS    | JLS §17 Java Memory Model defining      |
|               | happens-before visibility guarantees    |
| PROBLEM       | CPUs reorder writes; threads see stale  |
|               | values without explicit synchronisation |
| KEY INSIGHT   | volatile/synchronized create HB edges;  |
|               | without HB, concurrent reads undefined  |
| USE WHEN      | Writing any shared-mutable state across |
|               | threads; reviewing concurrent code      |
| AVOID WHEN    | Over-synchronising; use concurrent utils|
|               | (ConcurrentHashMap, AtomicXxx) instead  |
| TRADE-OFF     | Visibility guarantee costs memory barrier|
|               | instructions (2-20 cycles each on x86)  |
| ONE-LINER     | HB chain: volatile write HB volatile read|
|               | = guaranteed visibility across threads  |
| NEXT EXPLORE  | JLG-079 (Valhalla), JLG-081 (JLS history)|
+----------------------------------------------------------+
```

**If you remember only 3 things:**
1. Without happens-before, reads can return any value - even values that were never written to the variable
2. `volatile` creates happens-before between write and subsequent reads; `synchronized` creates happens-before at unlock/lock pairs
3. The holder class pattern is simpler and always correct lazy initialisation; double-checked locking requires `volatile` and is fragile

**Interview one-liner:** "The Java Memory Model (JLS §17) defines happens-before as the formal visibility ordering relation: a volatile write happens-before all subsequent volatile reads of the same variable; a monitor unlock happens-before subsequent locks; without these edges, the JVM is free to return stale values or reorder stores, making concurrent code non-portable."

---

### 💎 Transferable Wisdom

**Reusable Engineering Principle:** *Formal specifications enable correctness across implementations.* The JSR-133 JMM was designed so any JVM implementation on any CPU architecture could be verified against the spec. The happens-before formalism is architecture-neutral; it specifies the guarantee, not the mechanism. This allows JVMs on x86 (which provides more ordering guarantees by default) to need fewer barriers than JVMs on ARM (which allows more reordering), while both are correct.

**Where else this pattern appears:**
- **Distributed systems consistency models:** linearisability, causal consistency, and eventual consistency are precisely defined ordering relations; the same formal approach as happens-before but at network scale
- **Database isolation levels:** READ COMMITTED, REPEATABLE READ, SERIALIZABLE define exactly which concurrent write visibility anomalies are permitted; the same trade-off between consistency and throughput
- **CPU memory ordering models:** x86 TSO, ARM WMO, RISC-V are formal specs of which instruction reorderings processors are allowed to make; same formalism, hardware level

---

### 💡 The Surprising Truth

The original Java Memory Model (Java 1.0-1.4) was so broken that Doug Lea, author of `java.util.concurrent`, discovered that there was no valid implementation of the double-checked locking pattern in Java. The JMM literally made it impossible to write a correct lazy singleton using double-checked locking. The workarounds (static inner class, eager initialisation) existed precisely because the JMM was formally incorrect. The JSR-133 rewrite in Java 5 not only fixed the formal model but retroactively made the `volatile` double-checked locking pattern correct - meaning code written in 2004 for Java 5 is still the correct approach in Java 21, nineteen years later. The formal specification proved more durable than any "best practice" based on informal reasoning.

---

### 🧠 Think About This Before We Continue

**Question 1 (E - First Principles):** The JMM happens-before relation is transitive: if A HB B and B HB C, then A HB C. This transitivity means that `Thread.start()` creates a HB edge from all actions before the start call to all actions inside the new thread. Explain why this transitivity guarantee is necessary for safe publication of objects from a creating thread to a new thread, and what would go wrong if transitivity did not hold.

*Hint:* Consider a thread that creates an object, populates its fields, then calls `Thread.start()` passing the object. Without transitivity, the field writes before `Thread.start()` might not be visible to the new thread despite `Thread.start()` creating a HB edge. Research the "safe publication" idiom and how final fields provide HB even without explicit synchronisation.

**Question 2 (B - Scale):** A high-throughput order matching engine updates 64 `volatile long` counters (one per instrument) at 1 million updates/second per thread. With 32 threads, total throughput is 32 million updates/second, but measured throughput is only 8 million - a 75% shortfall. All counters are in a `volatile long[64]` array. Identify the root cause and design a data structure that achieves linear throughput scaling across 32 threads.

*Hint:* 64 longs = 64 * 8 = 512 bytes. A CPU cache line is 64 bytes. All 64 counters fit in 8 cache lines. When any thread writes to any counter, it potentially invalidates those cache lines for all other CPU cores. Research `@Contended`, `LongAdder`, and how to size arrays to avoid false sharing.

**Question 3 (C - Design Trade-off):** Java 9 added VarHandle with four access modes: plain, opaque, acquire/release, and volatile. The `acquire/release` mode is weaker than `volatile` but stronger than opaque - it provides directional ordering guarantees (acquire prevents loads from being hoisted above it; release prevents stores from being sunk below it). A lock-free queue uses head/tail pointers. Which VarHandle access mode is appropriate for reading the head pointer (consumer), writing the head pointer after dequeue, and why is `volatile` excessive for this use case?

*Hint:* Research the SPSC (Single Producer Single Consumer) lock-free queue. An acquire-load on head ensures that all queue element loads happen after the head read. A release-store on head ensures that all element reads are complete before the pointer update. Using `volatile` would add store-load barriers that are unnecessary when producer and consumer run on different threads with no shared state other than the pointer.
