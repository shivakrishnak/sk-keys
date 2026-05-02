---
layout: default
title: "Java Memory Model (JMM)"
parent: "Java Concurrency"
nav_order: 345
permalink: /java-concurrency/java-memory-model/
number: "0345"
category: Java Concurrency
difficulty: ★★★
depends_on: volatile, synchronized, Memory Barrier, Thread (Java)
used_by: volatile, synchronized, Happens-Before, Race Condition
related: volatile, synchronized, Happens-Before
tags:
  - java
  - concurrency
  - memory-model
  - deep-dive
  - jvm
---

# 0345 — Java Memory Model (JMM)

⚡ TL;DR — The Java Memory Model defines exactly which writes are visible to which reads in a multi-threaded program — specifying the rules that synchronization (`synchronized`, `volatile`, `final`) must follow to guarantee correctness across all JVMs and all hardware architectures.

| #0345 | Category: Java Concurrency | Difficulty: ★★★ |
|:---|:---|:---|
| **Depends on:** | volatile, synchronized, Memory Barrier, Thread (Java) | |
| **Used by:** | volatile, synchronized, Happens-Before, Race Condition | |
| **Related:** | volatile, synchronized, Happens-Before | |

### 🔥 The Problem This Solves

WORLD WITHOUT IT:
Different CPUs have different memory ordering guarantees (x86: strong; ARM: weak). A program using `synchronized` correctly on an Intel server might inadvertently rely on x86's strong ordering, then break when deployed to an ARM server because the JVM is allowed to use the weaker ordering ARM hardware provides. Without a formal memory model, "thread safety" has no precise meaning — correctness depends on the hardware, JVM, and JIT compiler implementation.

THE BREAKING POINT:
"Platform write once, run anywhere" breaks if memory ordering is platform-specific. A double-checked locking implementation worked on HotSpot JVM 1.4 due to implementation-specific behavior but was formally incorrect under the JMM — meaning any JVM could choose to break it. This ambiguity led to widespread production bugs.

THE INVENTION MOMENT:
The **Java Memory Model** (JMM, JSR 133, Java 5) was created to specify precisely what visibility guarantees Java programs have, independent of hardware — defining the minimum ordering rules all compliant JVMs must enforce, and explicitly allowing JVMs and hardware to reorder instructions UNLESS synchronisation is used.

### 📘 Textbook Definition

The **Java Memory Model (JMM)** is a specification (JLS §17.4) defining the allowed behaviors of multithreaded programs. The JMM defines: (1) the **happens-before (HB)** partial order — action A happens-before action B if B is guaranteed to see A's effects; (2) which synchronization actions establish HB (monitor lock/unlock, volatile read/write, thread start/join, `final` field init); (3) that under data races (accesses to the same variable without HB ordering), the JVM may present arbitrary values to readers. A program is **sequentially consistent** if all its synchronised accesses form a consistent global ordering.

### ⏱️ Understand It in 30 Seconds

**One line:**
The JMM is the contract: "use `synchronized` or `volatile`, and all threads see a consistent view of memory — otherwise, anything goes."

**One analogy:**
> The JMM is like postal delivery guarantees. Without a guaranteed service (synchronization), your letter might arrive out of order, be delayed, or not arrive at all. With "next-day guaranteed delivery" (synchronized), the recipient receives your letter before tomorrow. The JMM specifies which "postal guarantees" (synchronization constructs) ensure what delivery times (visibility).

**One insight:**
The JMM allows JVMs to reorder and cache anything that doesn't break happens-before guarantees. This means: two threads reading a non-volatile variable might see different values at the same instant — "current" on Thread 1's CPU is not "current" on Thread 2's CPU. Synchronization is not just about mutual exclusion — it's about making writes visible.

### 🔩 First Principles Explanation

CORE INVARIANTS:
1. Without synchronization, threads have no visibility guarantee — writes may be invisible, reordered, or speculated.
2. The happens-before relation is transitive: if A HB B and B HB C, then A HB C.
3. A program with **no data races** (all shared mutable accesses happen-before each other) behaves as if sequentially consistent.

DERIVED DESIGN:
The happens-before rules from the JMM:
- **Program order**: within a thread, each action happens-before the next (single-thread ordering).
- **Monitor lock/unlock**: unlock on a monitor HB every subsequent lock on the same monitor.
- **Volatile variable**: write to volatile field HB every subsequent read of that volatile field.
- **Thread start**: `Thread.start()` HB any action in the started thread.
- **Thread join**: any action in a thread HB `Thread.join()` return.
- **Final fields**: all writes to `final` fields in constructor HB any read of those fields if the constructor completes without leaking `this`.

```
Happens-Before (HB) Examples:

  synchronized block:
    write(sharedVar) → unlock(monitor)
    ↓ HB
    lock(monitor) → read(sharedVar)
    → write IS visible to read

  volatile:
    write(volatileVar)
    ↓ HB
    read(volatileVar)
    → write IS visible to read

  No HB:
    write(nonVolatileVar) — thread T1
    read(nonVolatileVar) — thread T2
    → Write may NOT be visible; any value possible
```

THE TRADE-OFFS:
The JMM's weakness is that it specifies minimal guarantees — JVMs may provide MORE ordering than required. Code that "works" because of JVM-specific behavior may break on a different JVM. Always reason from the JMM specification, not from observed behavior.

### 🧪 Thought Experiment

SETUP:
Classic JMM visibility test:
```java
int value = 0;
boolean ready = false;

// Thread 1:
value = 42;
ready = true;

// Thread 2:
if (ready) {
    System.out.println(value); // Could print 0!
}
```

WITHOUT HB GUARANTEE:
- `ready = true` may become visible to T2 before `value = 42` (reordering).
- T2 sees `ready = true` but `value` still 0.
- Prints "0" — data race, undefined behavior.

WITH HB (volatile ready):
```java
volatile boolean ready = false;
// Now: write(value) → write(ready=true) ← HB chain through volatile
// T2: read(ready) → read(value=42)
// Guaranteed: if T2 sees ready=true, it also sees value=42
```

THE INSIGHT:
The HB chain through `volatile ready` also extends to ALL writes before `volatile ready` (program order + transitivity). This is the "piggyback" JMM property — one volatile write can make non-volatile writes visible.

### 🧠 Mental Model / Analogy

> The JMM is like a musical score with timing rules. Musicians (threads) play simultaneously, but certain notes have timing relationships: "drum beat N happens before violin note M." Between unmarked notes, musicians are free to play whenever is efficient. The JMM marks which operations have cross-thread timing relationships (happens-before); everything else is unordered.

"Drum beat N → violin note M" → write(volatile) → read(volatile).
"Free timing" → non-volatile reads/writes are unordered.
"Musical score" → JMM specification.

Where this analogy breaks down: Music is continuous; the JMM's happens-before is partial — two actions without a HB relationship are unordered but may still coincidentally appear ordered. The JMM only guarantees no ordering for races; it doesn't guarantee any particular wrong value.

### 📶 Gradual Depth — Four Levels

**Level 1:** In multi-threaded programs, one thread's writes might not be seen by other threads unless you use `synchronized` or `volatile`. The JMM defines when writes ARE guaranteed visible.

**Level 2:** Use `synchronized` or `volatile` for all access to shared mutable state. The JMM guarantees that `synchronized` blocks ensure all writes before unlock are visible after the next lock. `volatile` ensures all writes before the volatile write are visible after the volatile read. `final` fields safely published through constructors are always visible. Without these, writes may be invisible or reordered.

**Level 3:** The JMM defines happens-before as a partial order. Without HB, data races are possible. A data race means the outcome is undefined per the JMM — the JVM is free to return any value, cache in registers, or reorder instructions. JIT compilers exploit undefined data-race behavior for optimization (register allocation, loop unrolling).

**Level 4:** The JMM revision in Java 5 (JSR 133) was necessary because the original Java 1.0 memory model was ambiguous and broken in ways that made double-checked locking patterns unreliable and compiler optimizations incorrect for concurrent code. The new JMM formally defines causality constraints to prevent "out-of-thin-air" values (a thread reading a value that was never written anywhere), ensuring the memory model is both performant and correct.

### ⚙️ How It Works (Mechanism)

**JMM visibility examples:**
```java
// Correct: synchronized ensures HB
class Safe {
    private int value = 0;
    synchronized void set(int v) { value = v; }
    synchronized int get() { return value; }
}

// Correct: volatile ensures HB
class VolatileSafe {
    volatile int value = 0;
    // set/get not needed — direct field access visible
}

// INCORRECT: no synchronization, no HB
class Unsafe {
    int value = 0; // shared without any synchronization
    // write in T1 may NOT be visible to T2
    // JIT free to cache 'value' in register forever
}
```

**Final field safety (constructor completion):**
```java
class ImmutablePoint {
    final int x;
    final int y;
    ImmutablePoint(int x, int y) { this.x = x; this.y = y; }
}
// Any thread that obtains a reference to a properly constructed
// ImmutablePoint is guaranteed to see x and y initialized
// Requires: reference not leaked during construction (this escape)
```

**Happens-before chain piggybacking:**
```java
int data = 0;
volatile boolean flag = false;

// T1:
data = 42;        // program order: HB flag=true
flag = true;      // volatile write

// T2:
if (flag) {       // volatile read
    use(data);    // guaranteed to see data=42
}
// Because: write(data) HB(prog order) write(flag) HB(volatile) read(flag) HB(prog order) read(data)
```

### 🔄 The Complete Picture — End-to-End Flow

```
[T1: write(x=42) then write(volatile flag=true)]
    → [JMM: write(x) HB write(flag) by program order]  ← YOU ARE HERE
    → [JMM: write(flag=true) HB read(flag=true) by volatile rule]
    → [T2: read(volatile flag) = true]
    → [JMM: read(flag) HB read(x) by program order]
    → [T2: read(x) = 42 — GUARANTEED visible]
    → [HB chain: T1.write(x) → T1.write(flag) → T2.read(flag) → T2.read(x)]
```

FAILURE PATH (broken HB):
```
[T1: write(x=42) then write(flag=true) — both non-volatile]
    → [No HB chain — JMM allows any reordering]
    → [T2: read(flag=true) but read(x=0) — valid JMM behavior]
    → [Program has a data race — undefined behavior]
```

WHAT CHANGES AT SCALE:
At scale, understanding the JMM helps diagnose concurrency bugs that appear only under load. A `volatile` flag that "works" in single-threaded tests but fails in production at 10K RPS is a JMM issue — the JIT aggressively reordering code with no synchronization. Memory model issues are the hardest-to-reproduce production bugs.

### 💻 Code Example

Example 1 — Safe lazy initialization using volatile (JMM-correct DCL):
```java
class SafeSingleton {
    private static volatile SafeSingleton instance;
    private final int data;

    private SafeSingleton() {
        this.data = expensiveInit();
    }

    static SafeSingleton get() {
        if (instance == null) {
            synchronized (SafeSingleton.class) {
                if (instance == null) {
                    instance = new SafeSingleton();
                }
            }
        }
        return instance;
    }
}
```

Example 2 — Safe publication via final fields:
```java
// ImmutableConfig is safely shareable across threads
// because all final fields are initialized before
// the constructor returns (JMM guarantee)
class ImmutableConfig {
    final Map<String, String> settings;
    ImmutableConfig(Map<String, String> settings) {
        // defensive copy ensures immutability
        this.settings = Collections.unmodifiableMap(
            new HashMap<>(settings)
        );
    }
}
// Can share safely without synchronization:
ImmutableConfig sharedConfig = new ImmutableConfig(rawSettings);
// Any thread that gets sharedConfig reference sees full Map
```

### ⚖️ Comparison Table

| Mechanism | Visibility Guarantee | Mutual Exclusion | Ordering | Best For |
|---|---|---|---|---|
| `synchronized` | Yes (full barrier) | Yes | Total within lock | Multi-step critical sections |
| `volatile` | Yes (acquire/release) | No | HB across volatile | Single variable flags |
| `final` field | Yes (constructor) | N/A | Construction-time | Immutable object publication |
| **none** | None | No | Undefined | Single-threaded only |

How to choose: Use `synchronized` for compound operations. Use `volatile` for single-variable visibility. Use `final` for safe immutable object publication. Use nothing for thread-local state.

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| Multi-core = one shared memory = automatically consistent | Modern CPUs use multi-level caches and store buffers. Without memory barriers, each core may see stale values. "Consistent" requires explicit ordering |
| A write eventually becomes visible to all threads | Without HB, the JMM allows a write to NEVER become visible to another thread. The JIT can legally cache a value in a register indefinitely |
| synchronized is only about mutual exclusion | synchronized also inserts memory barriers preventing reads of stale values. Without the visibility aspect, synchronized would be insufficient for thread safety |
| Final fields are always thread-safe | Only if the object's `this` reference doesn't escape the constructor. "This escape" (posting `this` to a shared field during construction) can expose partially initialized objects |

### 🚨 Failure Modes & Diagnosis

**Data Race — Inconsistent View**

Symptom: Intermittent wrong values, NullPointerExceptions, corrupted state — hard to reproduce.

Root Cause: Shared variable accessed without HB guarantee. JIT caches value in register.

Diagnostic:
```bash
# Run with Thread Sanitizer (OpenJDK TSAN support):
# Or: Java Race Condition Detector
# https://github.com/google/sanitizers/wiki/ThreadSanitizerJavaBenchmarks

# EnablePrintOrderedFlags in JVM to see lock ordering:
java -XX:+PrintCompilation MyApp 2>&1 | grep "data race"
```

Fix: Add `synchronized` or `volatile` to all accesses of the shared variable. Ensure all paths to the variable establish HB.

### 🔗 Related Keywords

**Prerequisites (understand these first):**
- `volatile` — implements JMM's volatile-read/write happens-before rule
- `synchronized` — implements JMM's monitor lock/unlock happens-before rule
- `Memory Barrier` — the hardware/JVM mechanism that enforces JMM's ordering rules

**Builds On This (learn these next):**
- `Race Condition` — what happens when JMM's HB rules are violated
- `Happens-Before` — the formal partial order that JMM's guarantees are expressed in

**Alternatives / Comparisons:**
- C++ Memory Order — equivalent concept in C++; `std::memory_order` is the C++ JMM
- Rust ownership/borrow — Rust prevents data races at compile time rather than specifying them at runtime

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ WHAT IT IS   │ Specification defining when writes in one │
│              │ thread are guaranteed visible in another  │
├──────────────┼───────────────────────────────────────────┤
│ PROBLEM IT   │ Without a formal model, thread safety is  │
│ SOLVES       │ undefined across JVMs and hardware        │
├──────────────┼───────────────────────────────────────────┤
│ KEY INSIGHT  │ Without synchronized/volatile:            │
│              │ any ordering is legal — writes may never  │
│              │ be visible. HB is transitive — volatile   │
│              │ write "pulls along" all prior writes      │
├──────────────┼───────────────────────────────────────────┤
│ USE WHEN     │ Reasoning about concurrent correctness;   │
│              │ diagnosing visibility bugs under load     │
├──────────────┼───────────────────────────────────────────┤
│ AVOID WHEN   │ N/A — JMM applies to all Java concurrent  │
│              │ code whether you think about it or not    │
├──────────────┼───────────────────────────────────────────┤
│ TRADE-OFF    │ Formal correctness vs performance;        │
│              │ strong guarantees vs optimization freedom │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "Synchronize or expect any value;         │
│              │  the JMM defines exactly what you get"   │
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ Race Condition → CAS → volatile           │
└──────────────────────────────────────────────────────────┘
```

---
### 🧠 Think About This Before We Continue

**Q1.** Benign data races are data races that appear to be harmless — e.g., a counter that might occasionally miss an increment but doesn't cause crashes. The JMM says benign races are still undefined behavior. Explain: why the JMM's treatment of data races as undefined behavior (even apparently harmless ones) is necessary for JIT compiler correctness, give a concrete example where a "benign race" allows a JIT compiler to generate code that produces a result NO programmer intended under the JMM spec, and explain what a real-world library (e.g., ConcurrentHashMap or OpenJDK's HashMap) would need to document to claim a specific race is "benign" within the JMM.

**Q2.** The JMM's happens-before relation is a partial order, not a total order. Unlike a database's total ordering of transactions, two concurrent threads writing to different variables have NO happens-before relationship between them. Explain why it is CORRECT for the JMM to allow two threads to simultaneously write to different variables without ordering, what specific property of each-thread's writes being HB-related within the thread (program order) while cross-thread writes have no HB unless synchronized makes concurrent programming safe despite the partial order, and where this model breaks down (the one class of programs it cannot reason about safely even with correct synchronization).

