---
id: JCC-028
title: "JMM Happens-Before - Deep Rules"
category: Java Concurrency
tier: tier-3-java
folder: JCC-java-concurrency
difficulty: ★★★
depends_on: JCC-016, JCC-041, JCC-038
used_by: JCC-079, JCC-080
related: JCC-042, JCC-047, JCC-083
tags:
  - java
  - concurrency
  - internals
  - advanced
  - deep-dive
status: complete
version: 3
layout: default
parent: "Java Concurrency"
grand_parent: "Technical Dictionary"
nav_order: 78
permalink: /java-concurrency/jmm-happens-before-deep-rules/
---

# JCC-078 - JMM HAPPENS-BEFORE - DEEP RULES

⚡ **TL;DR** - The happens-before relation is the Java Memory Model's
formal guarantee that one thread's writes are visible to another
thread's reads - without it, shared variable reads can see stale
values even on modern hardware.

---

| Field      | Value                                              |
|------------|----------------------------------------------------|
| Depends on | JCC-016 Java Memory Model (JMM), JCC-041 synchronized, JCC-038 CompletableFuture |
| Used by    | JCC-079 Lock-Free Data Structures, JCC-080 Memory Visibility Diagnostics |
| Related    | JCC-042 volatile, JCC-047 CAS (Compare-And-Swap), JCC-083 JSR 133 |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
Modern CPUs reorder instructions for performance. Compilers reorder
operations. CPU caches delay writes. Without a formal model, there
is no way to reason about which writes a thread will see. Two
engineers may write code that "obviously" communicates via a shared
variable, but the compiler or CPU may reorder writes so the reading
thread sees stale data - with no error, no warning, just silent
incorrect behaviour.

**THE BREAKING POINT:**
```java
// Thread 1:
data = new HeavyObject(); // write data (1)
ready = true;             // write flag  (2)

// Thread 2:
if (ready) {              // read flag   (3)
    use(data);            // read data   (4) - may see null!
}
```
Without happens-before: the CPU may reorder (1) and (2). Thread 2
sees `ready=true` but `data=null`. The JVM spec explicitly allows
this without synchronisation.

**THE INVENTION MOMENT:**
JSR 133 (Java Memory Model Specification, incorporated in Java 5)
introduced a rigorous happens-before (HB) relation. It defines
exactly which actions are guaranteed to be visible across threads
and which are not. It made `volatile` provide full HB ordering
(previously `volatile` only prevented caching, not reordering).

**EVOLUTION:**
- **JDK 1.4:** `volatile` guarantees only no-cache, not ordering
- **Java 5 / JSR 133:** `volatile` gets full happens-before; JMM
  formalised
- **Java 9:** `VarHandle` introduced with more fine-grained access
  modes (plain, opaque, acquire/release, volatile)

---

### 📘 Textbook Definition

**Happens-before (HB)** is a partial order relation between actions
(reads/writes) in a Java program. If action A *happens-before*
action B, the JMM guarantees that all writes visible to A (including
A itself if it is a write) are visible to B.

**Built-in happens-before rules:**

| Rule | Action A | Action B |
|------|---------|---------|
| Program order | Any action | Later action in same thread |
| Monitor unlock | `synchronized` unlock | Subsequent lock of same monitor |
| Volatile write | Write to `volatile` var | Subsequent read of same var |
| Thread start | `thread.start()` | Any action in the started thread |
| Thread join | Any action in thread T | `T.join()` in joining thread |
| Finalizer | Object constructor end | Finalizer start |
| Transitivity | A HB B and B HB C | A HB C |

---

### ⏱️ Understand It in 30 Seconds

**One line:** "A happens-before B" means: if A writes X, thread B
is guaranteed to see A's write to X when it reads X.

**One analogy:**
> Two people passing notes through a secretary. The secretary hands
> the note only after the writer seals the envelope (HB guarantee).
> Without the secretary (no HB), the writer might seal the envelope
> while the recipient is already opening it.

**One insight:** HB is about *visibility guarantees between threads*,
not just ordering within one thread. Within one thread, program
order always applies. Across threads, only explicit HB edges
provide visibility.

---

### 🔩 First Principles Explanation

**CORE INVARIANTS:**

1. Within a single thread, actions execute in program order - this
   is the trivial HB (thread order rule).
2. HB is transitive: if A HB B and B HB C, then A HB C.
3. A monitor unlock HB any later lock of the *same* monitor.
4. A `volatile` write HB any later read of the *same* variable.
5. `thread.start()` HB all actions in the started thread.
6. All actions in thread T HB `T.join()` returning.
7. Without an HB edge, the reader is allowed to see ANY previously
   written value - including values from before the write occurred.

**DERIVED DESIGN:**
The HB rules correspond directly to CPU memory barriers:
- `volatile` write/read inserts full memory fences
- `synchronized` unlock/lock inserts store/load barriers
- These force the CPU to flush write buffers and invalidate caches
  at defined synchronisation points

**THE TRADE-OFFS:**

**Gain:** Formal reasoning about visibility; correctness guarantees
that hold across all JVM implementations and all CPU architectures.

**Cost:** Getting HB wrong is silent (no exception). The JMM
is complex - engineers often have incorrect mental models.

**ESSENTIAL vs ACCIDENTAL COMPLEXITY:**

**Essential:** CPUs and compilers MUST reorder for performance.
A model that prevents all reordering would make Java unusably slow.
HB provides the minimum set of ordering constraints needed for
correctness.

**Accidental:** The original JDK 1.4 `volatile` specification was
ambiguous and inconsistent. JSR 133 fixed this - but historical
incorrect usage of `volatile` (pre-Java 5) still appears in
legacy code and tutorials.

---

### 🧪 Thought Experiment

**SETUP:** Two threads communicating via a plain (non-volatile) boolean.

```java
boolean ready = false;
Object data = null;

// Thread 1 (writer):
data  = computeHeavyObject(); // step 1
ready = true;                 // step 2

// Thread 2 (reader):
while (!ready) {}             // spin
use(data);                    // step 4
```

**WHAT HAPPENS WITHOUT HB:**
Three possibilities, all legal per JMM:
1. Thread 2 sees `ready=true` and `data` not null (lucky ordering)
2. Thread 2 sees `ready=true` and `data=null` (reordering of 1 & 2)
3. Thread 2 spins forever (`ready` never flushed from write buffer)

**WHAT HAPPENS WITH `volatile ready`:**
`volatile` write (step 2) HB `volatile` read (in while loop).
Transitivity: step 1 HB step 2 (program order) HB step 4 (via HB)
-> step 1 (write data) HB step 4 (read data).
Data is guaranteed visible when `ready` is seen as `true`.

**THE INSIGHT:** `volatile` on the flag gives a HB edge that
"piggybacks" visibility of all prior writes through transitivity.

---

### 🧠 Mental Model / Analogy

> HB is a formal contract between threads: "I guarantee that
> everything I did before crossing this fence will be visible to
> you when you cross your matching fence." The fences are
> `synchronized`, `volatile`, `Thread.start()`, and `Thread.join()`.
> Without a matching pair of fences, there is no contract, and the
> reader may see any snapshot of memory.

**Element mapping:**
- Your side of the fence = actions before the sync point in Thread 1
- Fence = `volatile` write, `synchronized` unlock, `thread.start()`
- Other side of the fence = `volatile` read, `synchronized` lock,
  actions in new thread
- "Visible" = guaranteed to be read as the value written before fence

Where this analogy breaks down: HB is a partial order, not a
sequential line. Two threads can have HB edges on ONLY some variables
while other variables remain unordered. The fence covers all writes
before it in the same thread, not the entire program.

---

### 📶 Gradual Depth - Four Levels

**Level 1 - What it is (anyone can understand):**
"A happens-before B" is Java's promise that if thread A writes a
value, thread B will see that value - but only if they use the
right tools (`volatile`, `synchronized`, or other built-in HB edges).

**Level 2 - How to use it (junior developer):**
Apply these rules to share data safely:
- If thread 1 writes to `volatile X`, any thread reading `volatile X`
  after that write sees all writes from thread 1 before that write.
- `synchronized(lock) { write(data); }` in thread 1 means any
  thread that subsequently does `synchronized(lock) { read(data); }`
  sees the write.

**Level 3 - How it works (mid-level engineer):**
The JVM enforces HB by inserting memory barriers (fences) at
synchronisation points:
- `volatile` write: StoreStore fence before + StoreLoad fence after
- `volatile` read: LoadLoad fence after + LoadStore fence after
- `synchronized` exit: StoreLoad fence
- `synchronized` entry: LoadLoad fence

These barriers prevent CPU out-of-order execution from crossing the
synchronisation point in the relevant directions.

**Level 4 - Why it was designed this way (senior/staff):**
The designers chose a *happens-before* (partial order) model over
a *sequential consistency* model. Sequential consistency would
require total ordering of all operations globally - which is
prohibitively expensive (requires global barriers). HB precision:
it only orders what is necessary for the specific synchronisation
points used, allowing the CPU to freely reorder everything else.
This is the minimum required for safety at maximum performance.

**Expert Thinking Cues:**
- HB does not prevent ALL reordering - only reordering that crosses
  a HB edge. The JVM can still reorder within a single thread and
  between unrelated threads.
- `volatile` gives both visibility AND ordering. Pre-Java 5, it
  only gave visibility (no reordering guarantee). Do not trust
  pre-Java 5 double-checked locking patterns.
- `final` fields: after object construction completes, all threads
  see the correct value of `final` fields (constructor HB rule).
  No synchronisation needed to read a `final` field.
- `AtomicInteger.set()` uses `volatile` semantics; `AtomicInteger.lazySet()`
  uses only store fence (weaker - eventual visibility, not immediate).

---

### ⚙️ How It Works (Mechanism)

**CPU memory barriers corresponding to HB rules:**
```
volatile write (field f):
  [StoreStore barrier]  -- no previous stores reordered past here
  f = value
  [StoreLoad barrier]   -- no subsequent loads appear before here

volatile read (field f):
  value = f
  [LoadLoad barrier]    -- no subsequent loads reordered before here
  [LoadStore barrier]   -- no subsequent stores reordered before here

synchronized exit (monitor M):
  [StoreLoad barrier]   -- flush all writes before releasing

synchronized enter (monitor M):
  [LoadLoad barrier]    -- reload all values after acquiring
```

**HB chain example:**
```
Thread 1:
  write(a)    } program order HB exists within thread
  write(b)    }
  write v=1   <- volatile write: HB edge starts here

Thread 2:
  read v      <- volatile read: if reads 1, HB edge ends here
  read(a)     } via transitivity HB from thread 1's write(a)
  read(b)     }
```

---

### 🔄 The Complete Picture - End-to-End Flow

**NORMAL FLOW (safe publication via volatile):**
```
Thread 1: init object fields    <- YOU ARE HERE
       |  (writes to a, b, c)
       |
  Thread 1: volatile write published = true
       |    [StoreLoad barrier inserted]
       |
  Thread 2: volatile read published == true
       |    [LoadLoad barrier inserted after read]
       |
  Thread 2: reads a, b, c
  -> guaranteed to see Thread 1's writes via HB transitivity
```

**FAILURE PATH (no HB, reading stale data):**
```
Thread 1: writes data=X, then sets ready=true (plain field)
Thread 2: reads ready=true (may be from cache)
Thread 2: reads data -> MAY see null or old value
(No HB edge: no guarantee that data write happened before data read)
```

**WHAT CHANGES AT SCALE:**
- Multi-socket NUMA systems: memory visibility across sockets
  is more expensive than within a socket. `volatile` flushes must
  cross interconnect. Performance impact of volatile fields can be
  2-10x higher on NUMA systems.
- ARM vs x86: x86 has a strong memory model (TSO) where many
  barriers are no-ops. ARM has a weaker model requiring explicit
  barriers that x86 omits. JVM portability means Java code must
  be correct for the weakest architecture.

---

### 💻 Code Example

**BAD - no HB, broken safe publication:**
```java
// BAD: no HB between writer and reader
class Config {
    private boolean initialised = false;
    private String endpoint;
    private int timeout;

    // Thread 1 calls this:
    void init(String ep, int t) {
        endpoint = ep;        // write 1
        timeout = t;          // write 2
        initialised = true;   // write 3 (plain field)
    }

    // Thread 2 calls this:
    String getEndpoint() {
        if (initialised) {    // read 3 - may see true
            return endpoint;  // read 1 - MAY SEE NULL!
        }
        return "default";
    }
}
```

**GOOD - volatile flag establishes HB:**
```java
// GOOD: volatile on flag creates HB edge
class Config {
    private volatile boolean initialised = false;
    private String endpoint;   // non-volatile: covered by HB
    private int timeout;       // non-volatile: covered by HB

    void init(String ep, int t) {
        endpoint = ep;         // write 1
        timeout = t;           // write 2
        initialised = true;    // volatile write 3 = HB edge
        // writes 1&2 HB this volatile write HB any later read
    }

    String getEndpoint() {
        if (initialised) {     // volatile read = HB edge end
            // guaranteed: endpoint and timeout are up-to-date
            return endpoint;
        }
        return "default";
    }
}
```

**GOOD - safe publication via final fields:**
```java
// GOOD: final fields are always safely published
// No synchronisation needed to READ final fields
public class ImmutablePoint {
    public final int x;
    public final int y;

    public ImmutablePoint(int x, int y) {
        this.x = x;
        this.y = y;
        // After constructor: all threads see x and y correctly
        // The JMM guarantees constructor HB for final fields
    }
}
```

**GOOD - correct double-checked locking (Java 5+):**
```java
// GOOD: volatile singleton (Java 5+ only)
public class Singleton {
    private static volatile Singleton instance;

    public static Singleton getInstance() {
        if (instance == null) {
            synchronized (Singleton.class) {
                if (instance == null) {
                    instance = new Singleton(); // volatile write
                }
            }
        }
        return instance; // volatile read - sees fully init'd object
    }
}
```

---

### ⚖️ Comparison Table

| Mechanism | HB guarantee | Scope | Overhead |
|-----------|-------------|-------|---------|
| `volatile` read/write | Full (visibility + ordering) | The variable + all prior writes | Low (fence only) |
| `synchronized` | Full (all prior actions visible after unlock) | All variables | Medium (monitor + fence) |
| `AtomicX.set()` | Volatile semantics | The field | Low |
| `AtomicX.lazySet()` | Store fence only (no volatile read) | The field | Very low |
| `VarHandle` plain | None (like normal field) | The field | None |
| `VarHandle` release/acquire | Acquire-release ordering | The field | Low |
| `final` field | Constructor HB | All final fields | None |

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| "`volatile` makes all shared variables visible" | `volatile` creates a HB edge only between the specific volatile write and the specific volatile read. Non-volatile writes before the volatile write are visible via transitivity - but ONLY if the reader reads the volatile field AFTER the writer writes it. |
| "HB means actions execute in that order on the CPU" | HB is a visibility guarantee, not an execution order constraint. The CPU may execute in any order as long as visibility rules are satisfied. |
| "`synchronized` is always stronger than `volatile`" | `synchronized` provides mutual exclusion AND HB. `volatile` provides HB without mutual exclusion. For pure visibility (no atomicity needed), `volatile` is sufficient and cheaper. |
| "Java pre-5 volatile is safe for double-checked locking" | Java 1.4 `volatile` prevents caching but NOT reordering of constructor writes. Double-checked locking was broken before Java 5/JSR 133. Never trust pre-Java 5 code for this pattern. |
| "`final` fields need synchronisation to be read safely" | No. `final` fields are safely published after the constructor completes. The JMM constructor HB rule guarantees this. |

---

### 🚨 Failure Modes & Diagnosis

**Failure Mode 1: Stale visibility causing inconsistent reads**

**Symptom:** Thread reads a value that was definitely written by
another thread but sees an older or null value. Non-deterministic;
works in tests, fails under load.

**Root Cause:** Missing HB edge between writer and reader. Plain
(non-volatile, non-synchronized) shared field with no coordination.

**Diagnostic:**
```bash
# Use Java thread sanitiser (Helgrind via valgrind, or JCStress)
# JCStress detects HB violations:
# java -jar jcstress.jar -t YourTestClass

# Or: add logging to capture which value was read
log.debug("Read value: {} at {}", val, System.nanoTime());
# Check for out-of-order nanoTime readings vs write ordering
```

**Fix:** Add `volatile` to the flag/field, or wrap reads/writes in
`synchronized`, or use an `AtomicReference`.

---

**Failure Mode 2: Broken singleton from pre-Java-5 double-checked locking**

**Symptom:** Singleton constructor is called multiple times; or
partially constructed object is observed.

**Root Cause:** Pre-Java-5 `volatile` did not prevent instruction
reordering of constructor writes. The JVM could publish the
reference before all constructor writes completed.

**Diagnostic:**
```bash
# Check Java version: if < 5, any double-checked locking is suspect
java -version
# Audit for double-checked locking without volatile
grep -r "instance ==" src/ | grep -v volatile
```

**Fix:** Add `volatile` to the instance field (Java 5+) or use the
holder class idiom (lazy initialisation without volatile):
```java
private static class Holder {
    static final Singleton INSTANCE = new Singleton();
}
```

---

**Failure Mode 3: `lazySet` used where volatile semantics needed**

**Symptom:** Other threads read stale values of atomic variable;
`lazySet` was used to "optimise" updates.

**Root Cause:** `AtomicX.lazySet()` uses only a store fence (no
full volatile barrier). Reads may not see the lazySet value
immediately.

**Diagnostic:**
```java
// lazySet is documented: "may not be immediately visible to other threads"
AtomicBoolean flag = new AtomicBoolean();
flag.lazySet(true); // NOT immediately visible to other threads!
// If other threads read flag.get(), they may still see false
```

**Fix:** Use `flag.set(true)` (volatile semantics) where immediate
visibility is required. Use `lazySet` only for performance-critical
single-writer sequences where eventual visibility is sufficient
(e.g., event counting where no reader depends on immediate updates).

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**
- [[JCC-016 - Java Memory Model (JMM)]] - the overall framework
  within which happens-before is defined
- [[JCC-042 - volatile]] - the primary declaration that creates HB
  edges for individual fields
- [[JCC-041 - synchronized]] - the monitor-based HB mechanism

**Builds On This (learn these next):**
- [[JCC-079 - Lock-Free Data Structures]] - apply HB knowledge to
  design correct lock-free algorithms
- [[JCC-080 - Memory Visibility Diagnostics (jstack, JFR)]] - detect
  HB violations in running systems
- [[JCC-083 - JSR 133 - Java Memory Model Specification]] - the
  formal source document

**Alternatives / Comparisons:**
- [[JCC-047 - CAS (Compare-And-Swap)]] - uses volatile semantics
  internally (provides HB)
- [[JCC-061 - VarHandle]] - fine-grained HB control with access
  modes

---

### 📌 Quick Reference Card

```
+--------------------------------------------------+
| WHAT IT IS   | Formal guarantee that write in     |
|              | thread A is visible to read in B  |
+--------------+------------------------------------+
| PROBLEM      | CPUs and compilers reorder; shared  |
|              | vars may show stale values         |
+--------------+------------------------------------+
| KEY INSIGHT  | volatile write HB volatile read;   |
|              | transitivity covers prior writes   |
+--------------+------------------------------------+
| USE WHEN     | Sharing state across threads;      |
|              | designing lock-free algorithms     |
+--------------+------------------------------------+
| AVOID WHEN   | (Can't avoid - must understand HB  |
|              | to write ANY concurrent Java code) |
+--------------+------------------------------------+
| TRADE-OFF    | HB is minimum needed for safety;   |
|              | more ordering = more barrier cost  |
+--------------+------------------------------------+
| ONE-LINER    | volatile write + volatile read =   |
|              | writer's prior writes visible      |
+--------------+------------------------------------+
| NEXT EXPLORE | JCC-079 Lock-Free Data Structures, |
|              | JCC-083 JSR 133 Specification      |
+--------------------------------------------------+
```

**If you remember only 3 things:**
1. `volatile` write HB any subsequent `volatile` read of the same
   field - making ALL prior writes from the writer visible.
2. HB is transitive: A HB B, B HB C implies A HB C. One volatile
   "piggybacks" visibility for many prior writes.
3. WITHOUT an HB edge between two threads, the reader can see
   any previously written value, including stale or partially-written
   ones.

**Interview one-liner:** "Happens-before (HB) is the JMM's visibility
guarantee: a volatile write or synchronized unlock HB any later
volatile read / lock of the same variable, ensuring all prior writes
are visible - failure to establish HB makes shared variables unsafe."

---

### 💎 Transferable Wisdom

**Reusable Engineering Principle:** Visibility guarantees must be
explicit. Any shared-state communication between components (threads,
processes, services) requires a defined synchronisation point that
both sides honour. Implicit assumptions about ordering, based on
perceived execution sequence, are systematically broken by modern
hardware and compilers.

**Where else this pattern appears:**
- **C++11 `memory_order`:** C++ memory model uses the same HB
  concept with explicit `memory_order_release` (store) and
  `memory_order_acquire` (load) annotations - matching Java's
  volatile semantics.
- **Kafka consumer offset commits:** Writing an offset to Kafka
  establishes an HB edge - any consumer group member that reads
  a committed offset after the commit is guaranteed to see all
  messages before that offset. The offset commit IS the HB fence.
- **Git commit history:** `git push` guarantees that a pull after
  the push sees all committed changes before the push - the push
  is the HB edge in the version control system.

---

### 💡 The Surprising Truth

On x86 processors, Java's happens-before implementation is nearly
free for reads. x86 uses Total Store Order (TSO) - stores are
globally visible in program order by default. A `volatile` read
on x86 compiles to a plain memory load with no fence instruction.
Only `volatile` writes require a fence (an MFENCE instruction) to
drain the store buffer. On ARM, however, both `volatile` reads and
writes require fence instructions because ARM has a much weaker
memory model. This means Java code that is "fast" on x86 (your dev
laptop) can be measurably slower on ARM (your cloud production nodes
which may run on Graviton2/3) purely due to memory barrier costs of
volatile fields - a source of ARM-specific performance regressions
undetectable on x86 development machines.

---

### 🧠 Think About This Before We Continue

**Question 1 (First Principles):** The program order HB rule says
all actions in a thread happen-before later actions in the same
thread. This seems obvious. But the CPU may execute instructions
out of order. How does the JVM reconcile out-of-order CPU execution
with this rule, and why is it safe?

*Hint:* Research the concept of "as-if" serial execution: CPUs
maintain the appearance of sequential in-thread execution via
data dependency tracking, while only allowing reorders that are
invisible to the same thread. The HB rule only cares about
inter-thread visibility.

---

**Question 2 (Design Trade-off):** You are implementing a high-
throughput event counter shared across 100 threads. Three options:
`volatile long`, `AtomicLong`, and `LongAdder`. Order them by
write throughput under high contention, and explain how each
maps to happens-before semantics.

*Hint:* Study `LongAdder`'s cell-per-thread design and when it
sums. Research `AtomicLong`'s CAS loop under contention. Compare
them to `volatile long`'s unconditional fence cost. Consider what
HB each provides to a thread reading the sum.

---

**Question 3 (Root Cause):** You have a service that initialises
a global config map in a `@PostConstruct` method and reads it from
multiple request-handler threads. Without `volatile` or
`synchronized` on the map reference, is this safe? Justify using
happens-before rules and explain exactly which JMM rule makes it
safe or unsafe.

*Hint:* Investigate the happens-before chain from Spring's
`@PostConstruct` invocation (servlet initialisation) to the request
threads. Which specific HB rule from the JMM table applies: Thread
start? Monitor? Or is there none, making it unsafe?

