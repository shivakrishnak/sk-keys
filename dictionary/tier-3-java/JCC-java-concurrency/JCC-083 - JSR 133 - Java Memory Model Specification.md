---
id: JCC-033
title: "JSR 133 - Java Memory Model Specification"
category: Java Concurrency
tier: tier-3-java
folder: JCC-java-concurrency
difficulty: ★★★
depends_on: JCC-078, JCC-016, JCC-042
used_by: JCC-088
related: JCC-061, JCC-047, JCC-079
tags:
  - java
  - concurrency
  - internals
  - advanced
  - foundational
status: complete
version: 3
layout: default
parent: "Java Concurrency"
grand_parent: "Technical Dictionary"
nav_order: 83
permalink: /java-concurrency/jsr-133-java-memory-model-specification/
---

# JCC-083 - JSR 133 - JAVA MEMORY MODEL SPECIFICATION

⚡ **TL;DR** - JSR 133 is the Java Specification Request that
formalised the Java Memory Model in Java 5, defining exactly which
writes are visible to which reads and fixing pre-Java-5 `volatile`
and `double-checked locking` bugs.

---

| Field      | Value                                              |
|------------|----------------------------------------------------|
| Depends on | JCC-078 JMM Happens-Before Deep Rules, JCC-016 Java Memory Model, JCC-042 volatile |
| Used by    | JCC-088 Lock-Free Algorithm Theory                 |
| Related    | JCC-061 VarHandle, JCC-047 CAS (Compare-And-Swap), JCC-079 Lock-Free Data Structures |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
Java's original memory model (JDK 1.0-1.4) was informally specified.
Key problems:
1. `volatile` was documented to prevent caching but NOT reordering
   - compilers could legally reorder volatile writes with earlier
   non-volatile writes.
2. Double-checked locking was universally broken (even with
   `volatile`) because the JMM allowed partially-constructed objects
   to be published.
3. `final` fields had no publication guarantee - a thread could
   observe `final int x = 5` as `x = 0` if it obtained a reference
   before construction completed.

**THE BREAKING POINT:**
Jeremy Manson (then a PhD student) and Brian Goetz published
empirical evidence that the original JMM was too weak to support
safe publication patterns that every Java developer assumed worked.
The singleton double-checked locking pattern, used in millions of
codebases, was fundamentally broken on all JDK versions before 5.

**THE INVENTION MOMENT:**
Bill Pugh, Jeremy Manson, and Doug Lea led the JSR 133 Expert Group
(2002-2004). The resulting specification, incorporated into Java 5,
provided a formal mathematical model: happens-before partial order,
correct `final` field semantics, `volatile` with full ordering
guarantees, and formal rules for `synchronized`.

**EVOLUTION:**
- **1995-2004:** Original weak JMM (JDK 1.0-1.4)
- **2004 / Java 5:** JSR 133 incorporated (`volatile` fixed, `final`
  fixed, happens-before formalised)
- **2011 / Java 7:** JMM Chapter 17 in JLS updated
- **2017 / Java 9:** JSR 133 extended via `VarHandle` with access
  modes (plain, opaque, acquire/release, volatile)

---

### 📘 Textbook Definition

**JSR 133** (2002-2004, incorporated in Java 5) is the formal
specification of the Java Memory Model. It defines:

1. **Happens-before (HB):** A partial order on program actions.
   If A HB B, writes visible at A are visible at B.
2. **Synchronisation Order:** A total order on all synchronisation
   actions (monitor lock/unlock, volatile read/write, thread
   start/join).
3. **Causality Requirements:** Cycles involving speculative writes
   are forbidden (prevents certain JVM over-optimisations).
4. **`final` Field Semantics:** All writes to `final` fields before
   the constructor completes are visible to all threads that see
   the object reference.
5. **Corrected `volatile` Semantics:** A `volatile` write HB any
   subsequent `volatile` read of the same variable, and prevents
   reordering with adjacent non-volatile reads/writes.

---

### ⏱️ Understand It in 30 Seconds

**One line:** JSR 133 is the formal rulebook that makes Java's
concurrency primitives safe and predictable across all JVM
implementations and CPU architectures.

**One analogy:**
> Before JSR 133, thread communication was like verbal agreements -
> mostly worked, but no enforceable contract. JSR 133 is the written
> legal contract: exact definitions, enforceable by the JVM, binding
> for all implementations from ARM to x86 to z/Architecture.

**One insight:** JSR 133's most important fix was making `final`
fields safe for concurrent access without synchronisation - enabling
immutable object patterns to work correctly on all JVMs.

---

### 🔩 First Principles Explanation

**CORE INVARIANTS:**

1. The JMM specifies *what a program is allowed to observe*, not
   what CPUs must do. Any CPU execution that produces results
   consistent with the JMM is legal.
2. The HB relation must be a partial order: irreflexive, asymmetric,
   transitive.
3. The Synchronisation Order must be consistent with (a refinement
   of) Program Order for each thread.
4. Every read must see the most recent write in HB order, not any
   arbitrary past write.
5. `final` field writes are guaranteed visible after constructor
   completion via a *freeze action* - even without synchronisation.

**DERIVED DESIGN:**
JVM implementers (HotSpot, OpenJ9) must emit memory barriers at
exactly the points where JSR 133 requires HB edges. The beauty:
they have full freedom to optimise everything else. JSR 133 is a
*contract* between the JMM specification and all JVM implementations.

**THE TRADE-OFFS:**

**Gain:** Correct double-checked locking, safe immutable objects,
`volatile` with ordering, formal basis for lock-free algorithms.

**Cost:** More expensive `volatile` (full memory barriers on x86
for writes; cheap reads). Pre-Java-5 codebases had subtle bugs
that became visible after JVM upgrades changed barrier placement.

**ESSENTIAL vs ACCIDENTAL COMPLEXITY:**

**Essential:** A formal memory model is mathematically required
to write correct concurrent code on modern hardware that reorders
at will.

**Accidental:** The causality requirements section of JSR 133 is
acknowledged as one of the most complex parts; even the spec
authors described it as "difficult to understand." VarHandle
(Java 9) introduced cleaner access modes as a more principled API.

---

### 🧪 Thought Experiment

**SETUP:** Double-checked locking singleton, pre-Java-5.

```java
class Singleton {
    private static Singleton instance;

    static Singleton get() {
        if (instance == null) {           // check 1 (no lock)
            synchronized (Singleton.class) {
                if (instance == null) {   // check 2 (with lock)
                    instance = new Singleton(); // BROKEN pre-Java 5
                }
            }
        }
        return instance;
    }
}
```

**WHAT HAPPENS WITHOUT JSR 133:**
The JVM (pre-Java-5) can execute `instance = new Singleton()` as:
1. Allocate memory for object
2. Write the reference to `instance` (the field, now non-null)
3. Run the constructor (writes to fields)

Step 3 can be reordered after step 2 by the compiler/CPU. Thread 2
sees `instance != null` (step 2 done) but reads uninitialised fields
(step 3 not yet done). Broken.

**WHAT HAPPENS WITH JSR 133:**
`instance` declared `volatile`. `volatile` write HB any subsequent
read. Constructor completes before `volatile` write (`instance =`).
All writes inside constructor HB the volatile write HB any subsequent
read. Thread 2 sees a fully initialised object. Fixed.

**THE INSIGHT:** JSR 133 made `volatile` provide both visibility
AND ordering - the combination that enables correct safe publication.

---

### 🧠 Mental Model / Analogy

> JSR 133 is a constitutional amendment. The original Java memory
> constitution was vague on key rights. JSR 133 added explicit
> amendments: "final fields shall be readable by all citizens after
> the constructor completes," "volatile writes shall create a
> happens-before edge with all subsequent reads." These amendments
> are binding on all JVM implementations (courts), regardless of
> the CPU architecture they run on.

**Element mapping:**
- Original Java memory contract = pre-Java-5 JMM
- JSR 133 amendments = happens-before rules, volatile fix, final fix
- JVM implementations = courts interpreting the constitution
- CPU reorderings = local customs that must conform to constitutional rights
- `volatile` field = constitutionally protected synchronisation point

Where this analogy breaks down: constitutional amendments are hard
to change; JSR 133 was extended by Java 9's `VarHandle` modes,
showing that the memory model continues to evolve.

---

### 📶 Gradual Depth - Four Levels

**Level 1 - What it is (anyone can understand):**
The formal rulebook that every Java program and JVM must follow
when threads share data, so that concurrent code works the same
way on every computer and JVM.

**Level 2 - How to use it (junior developer):**
JSR 133 is the reason these patterns work in Java 5+:
- `volatile` singleton: correct because volatile has ordering
- Immutable objects: safe because `final` has publication guarantee
- `synchronized` blocks: correct because unlock HB next lock

**Level 3 - How it works (mid-level engineer):**
JSR 133 defines rules in terms of actions (reads, writes, locks,
etc.) and orders between them. For each program execution, the JMM
requires that each read `r` of variable `v` sees a write `w` such
that: (a) `w` is to `v`, (b) `w` HB `r`, and (c) there is no
intervening write `w'` (also HB `r`) that "shadows" `w`. If no HB
write exists, any previous write may be observed - hence the
requirement to establish HB for any shared variable communication.

**Level 4 - Why it was designed this way (senior/staff):**
The JSR 133 team chose a formal denotational semantics (describing
what legal executions are, not how CPUs must implement them) instead
of an operational model (step-by-step rules). This gives JVM
implementers maximum freedom to optimise while giving developers
a precise correctness model. The DRF-SC (Data-Race-Free guarantees
Sequential Consistency) theorem states: if every pair of conflicting
accesses is protected by HB, the program appears to execute
sequentially consistently. This is the informal contract: write
race-free code, get sequential consistency.

**Expert Thinking Cues:**
- Pre-Java-5 code using double-checked locking (without volatile)
  is broken. Period. Even if it "works" on your JVM and CPU, the
  JMM allows a compliant JVM to expose the bug.
- JSR 133 is not JDK implementation documentation - it is the
  specification that constrains ALL JVM implementations.
- JLS Chapter 17 is the normative text incorporating JSR 133.
- `VarHandle` (Java 9) provides access modes that map precisely to
  JSR 133's memory ordering levels (plain, release/acquire, volatile).

---

### ⚙️ How It Works (Mechanism)

**JSR 133 formal action types:**
```
Read(v)      - read variable v's value
Write(v, x)  - write value x to variable v
Lock(m)      - acquire monitor m
Unlock(m)    - release monitor m
Start(t)     - start thread t
Join(t)      - join on thread t terminating
```

**JSR 133 HB rules (formal):**
```
1. Program Order: A <HB B if A comes before B in same thread
2. Monitor Lock: unlock(m) <HB lock(m) for any later lock
3. Volatile:     write(v) <HB read(v) for any later volatile read
4. Thread Start: start(t) <HB any action in thread t
5. Thread Join:  any action in t <HB return from join(t)
6. Transitivity: A<HB B and B<HB C implies A<HB C
```

**The `final` field guarantee:**
```
Constructor:
  write(this.f = 5) [any type]
  freeze action (implicit at constructor end)

Observer thread:
  read(objectRef)   [sees non-null ref]
  read(objectRef.f) [guaranteed 5, not 0]
```

---

### 🔄 The Complete Picture - End-to-End Flow

**NORMAL FLOW (JSR 133 analysis of volatile pattern):**
```
Thread 1: write x = 42 (non-volatile)  <- YOU ARE HERE
Thread 1: write volatile flag = true
  -> happens-before edge created
       |
Thread 2: read volatile flag -> sees true
  -> volatile read
  -> HB edge consumed
Thread 2: read x
  -> HB chain: write(x) <HB write(flag) <HB read(flag) <HB read(x)
  -> x is guaranteed 42
```

**FAILURE PATH (no HB - broken communication):**
```
Thread 1: write x = 42 (non-volatile, no flag)
Thread 2: read x
-> No HB edge -> JMM allows Thread 2 to see x = 0 (old value)
   even after "sufficient time has passed"
```

**WHAT CHANGES AT SCALE:**
- JSR 133 rules apply equally to single-JVM and... single JVM only.
  Distributed systems crossing process boundaries have no JMM
  guarantee. Distributed HB requires explicit messaging.

---

### 💻 Code Example

**BAD - broken pre-Java-5 double-checked locking:**
```java
// BAD: broken before Java 5 (even with volatile in pre-5 JVM)
// field could be partially initialised when read
private static Singleton instance; // NOT volatile

static Singleton get() {
    if (instance == null) {
        synchronized (Singleton.class) {
            if (instance == null) {
                instance = new Singleton(); // reordering risk!
            }
        }
    }
    return instance; // may return partially constructed!
}
```

**GOOD - JSR 133 correct double-checked locking (Java 5+):**
```java
// GOOD: volatile creates HB edge covering all constructor writes
private static volatile Singleton instance;

static Singleton get() {
    if (instance == null) {
        synchronized (Singleton.class) {
            if (instance == null) {
                instance = new Singleton();
                // volatile write: all constructor writes HB this
            }
        }
    }
    return instance; // volatile read: all HB writes visible
}
```

**GOOD - holder class idiom (no volatile needed):**
```java
// GOOD: class loading provides HB - JLS 12.4.2
// (JSR 133 guarantees class initialisation is thread-safe)
class Singleton {
    private static class Holder {
        static final Singleton INSTANCE = new Singleton();
    }
    static Singleton get() { return Holder.INSTANCE; }
}
```

**How to verify:**
```java
// Use JCStress (Java Concurrency Stress tests) to verify
// your concurrent code against JSR 133 rules
// https://github.com/openjdk/jcstress
@JCStressTest
@Outcome(id = "1, 1", expect = ACCEPTABLE,   desc = "Both threads see 1")
@Outcome(id = "0, 0", expect = FORBIDDEN,    desc = "Should not see 0,0")
@State
public class VolatileTest {
    volatile int x;
    int y;
    // Actors and arbiters defined per JCStress API
}
```

---

### ⚖️ Comparison Table

| Memory Model | Language | Formalism | Volatile/atomic | Final/const |
|-------------|---------|-----------|-----------------|-------------|
| JSR 133 (Java) | Java 5+ | HB partial order | Full barriers | Constructor HB |
| C++11 memory model | C++ | Same HB concept | std::atomic modes | constexpr |
| Go memory model | Go | HB, channel-based | sync/atomic | var final (no explicit) |
| ECMA-262 memory model | JavaScript/WASM | Agent-based | SharedArrayBuffer | Immutable binding |
| POSIX pthreads model | C | mutex/CV based | atomic ops | Const (no runtime init) |

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| "JSR 133 is only relevant for library authors" | Every developer who uses `static`, `singleton`, `lazy init`, or any shared mutable state depends on JSR 133. Double-checked locking was broken in EVERY Java 1.4 application. |
| "My code works fine without volatile - JSR 133 doesn't matter" | It appears to work on your JVM with your CPU. JSR 133 explicitly allows compliant JVMs to expose the bug. A different JVM version or architecture can expose it. |
| "`final` fields are only for primitives" | JSR 133's `final` field freeze guarantee applies to ALL types: primitives, reference types, and array references (but NOT array elements). |
| "JSR 133 was replaced by a newer specification" | JSR 133 was incorporated into the JLS (Chapter 17). It was extended (not replaced) by `VarHandle` in Java 9 which added finer-grained access modes. |
| "volatile is enough for atomicity too" | `volatile` provides visibility and ordering. It does NOT provide atomicity for compound actions like `i++` (read-modify-write). Use `AtomicInteger` for compound-atomic operations. |

---

### 🚨 Failure Modes & Diagnosis

**Failure Mode 1: Pre-Java-5 double-checked locking in production**

**Symptom:** NullPointerException on a singleton field; partially
initialised object in rare production logs.

**Root Cause:** Singleton field not `volatile`; constructor writes
reordered after object reference publication.

**Fix:** Add `volatile` to the singleton reference field (Java 5+).

---

**Failure Mode 2: Broken concurrent initialisation of final-like fields**

**Symptom:** A field initialised once and then read-only appears
as `null` in other threads despite being set in the constructor.

**Root Cause:** Field is NOT declared `final` - it's just never
written after construction. JSR 133's `final` freeze guarantee only
applies to fields declared `final`. Non-final fields that happen
to be written only in the constructor have NO publication guarantee.

**Fix:** Declare the field `final` to get the JSR 133 constructor
HB guarantee. Or add `volatile` / `synchronized` for non-final
fields.

---

**Failure Mode 3: Relying on JVM-specific behaviour across versions**

**Symptom:** Community reports that updating from JDK 8 to JDK 17
breaks a singleton or lazy-init pattern that worked for years.

**Root Cause:** JDK 8 HotSpot JIT happened to emit barriers that
masked the bug. JDK 17 JIT with newer optimisations exposed the
JSR 133 violation that was always latent.

**Fix:** Fix the underlying JSR 133 violation (missing `volatile`
or `synchronized`). Never rely on JVM version-specific barrier
placement.

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**
- [[JCC-078 - JMM Happens-Before - Deep Rules]] - the main rules
  JSR 133 formalises
- [[JCC-016 - Java Memory Model (JMM)]] - the practical application
- [[JCC-042 - volatile]] - the primary declaration that maps to
  JSR 133 happens-before edges

**Builds On This (learn these next):**
- [[JCC-088 - Lock-Free Algorithm Theory (CAS Foundations)]] - proof
  techniques built on JSR 133 formal model
- [[JCC-061 - VarHandle]] - Java 9 extension to JSR 133 access modes

**Alternatives / Comparisons:**
- C++11 memory model: same HB concept, explicit `memory_order`
  annotations
- POSIX pthreads: mutex/CV-based HB, no language-level model

---

### 📌 Quick Reference Card

```
+--------------------------------------------------+
| WHAT IT IS   | Formal specification of Java's     |
|              | memory model; incorporated Java 5  |
+--------------+------------------------------------+
| PROBLEM      | Pre-Java-5 volatile, double-checked|
|              | locking, and final were all broken |
+--------------+------------------------------------+
| KEY INSIGHT  | HB + volatile ordering + final     |
|              | freeze = provably correct concurrency|
+--------------+------------------------------------+
| USE WHEN     | Understanding why volatile/sync    |
|              | work; auditing concurrent patterns |
+--------------+------------------------------------+
| AVOID WHEN   | N/A: understanding it prevents bugs|
|              | that cost weeks to diagnose        |
+--------------+------------------------------------+
| TRADE-OFF    | Formal correctness / more expensive|
|              | volatile on weaker-model CPUs (ARM)|
+--------------+------------------------------------+
| ONE-LINER    | Java 5 JSR 133: volatile=HB+order,|
|              | final=safe publish, DCL now correct|
+--------------+------------------------------------+
| NEXT EXPLORE | JCC-088 Lock-Free Algorithm Theory,|
|              | JLS Chapter 17                     |
+--------------------------------------------------+
```

**If you remember only 3 things:**
1. JSR 133 fixed `volatile` in Java 5: it now provides both
   visibility AND ordering (prevents reordering). Pre-Java-5
   volatile was broken.
2. `final` fields are safely published after constructor completion
   per JSR 133 - no synchronisation needed to READ a final field.
3. Double-checked locking requires `volatile` on the singleton
   reference field. Without it, the JMM ALLOWS partially constructed
   objects to be observed.

**Interview one-liner:** "JSR 133 (Java 5) formalised the JMM:
`volatile` now provides happens-before ordering (not just no-cache),
`final` fields are safely published after construction, and
happens-before provides the complete framework for correct
concurrent Java code."

---

### 💎 Transferable Wisdom

**Reusable Engineering Principle:** Informal behavioral contracts
are insufficient for systems with observable concurrency. Formal
specifications (even difficult ones) are preferable to "works in
practice" assumptions that depend on specific JVM versions or CPU
architectures.

**Where else this pattern appears:**
- **C++11 memory model:** Introduced `std::atomic` and `memory_order`
  to fix the same problem C++ had before 2011 - no formal memory
  model meant concurrent C++ code was undefined behaviour on
  compiler reorderings.
- **Go memory model:** The Go team published a formal memory model
  update in 2022, explicitly acknowledging unsafe patterns that
  "appeared to work" in practice but were not guaranteed.
- **Kafka offset commit semantics:** Kafka's specification precisely
  defines what happens-before relationships hold between produce
  and consume acknowledgements - the distributed equivalent of JSR 133.

---

### 💡 The Surprising Truth

Every Java developer using double-checked locking before 2004 was
running broken code - including code in production enterprise
systems, popular frameworks, and textbooks. The pattern appeared
to work because the specific JVM and CPU combinations of that era
happened to emit barriers that masked the bug. When Sun published
the JSR 133 analysis showing the pattern was broken, the Java
community went through a genuine crisis: an idiom taught in Java
books, recommended in performance guides, and used in every major
framework was formally provably incorrect. The fix (add `volatile`)
was one character change, but finding and fixing every instance in
production codebases took years.

---

### 🧠 Think About This Before We Continue

**Question 1 (First Principles):** JSR 133 requires that reads
see the "most recent write in HB order." What does "most recent"
mean when two writes from different threads are both HB a read
but are not ordered with each other (concurrent writes)? Is the
program in a data race?

*Hint:* Read about data-race-free programs and how JSR 133 defines
legal executions for programs WITH data races (any value can be
observed) vs programs WITHOUT data races (sequential consistency
applies).

---

**Question 2 (Design Trade-off):** JSR 133 guarantees `final`
fields of an object are visible after the constructor completes.
If you publish an object reference via a plain (non-volatile,
non-synchronized) field, can another thread observe the object
with uninitialised `final` fields? Trace the exact HB chain.

*Hint:* The `final` freeze guarantee maps the constructor end to
a freeze action HB a "freeze observation" in other threads. The
publication of the reference itself (via a plain field) has no HB
chain. Research the subtlety: the freeze is visible only to threads
that observe the reference through a HB-ordered publication.

---

**Question 3 (Root Cause):** A colleague claims: "I don't need
`volatile` on my singleton because the JVM always initialises
static fields before any class method runs - so the singleton is
always fully initialised before any thread can call `get()`."
Evaluate this claim using JSR 133 and JLS Chapter 12.4.

*Hint:* JLS 12.4 defines class initialisation locking. The class
initialiser (`<clinit>`) runs once with a lock. But a `static`
field initialised in a static block vs in the field declaration vs
in a lazy `get()` method has different HB guarantees. Which case
makes the colleague's claim correct, and which makes it wrong?

