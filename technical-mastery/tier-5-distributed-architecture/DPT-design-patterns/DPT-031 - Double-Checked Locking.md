---
id: DPT-031
title: Double-Checked Locking
category: Design Patterns
tier: tier-5-distributed-architecture
folder: DPT-design-patterns
difficulty: ★★★
depends_on: DPT-001, DPT-005, DPT-006
used_by: DPT-033, DPT-064
related: DPT-006, DPT-032, DPT-033, DPT-035
tags:
  - pattern
  - concurrency
  - advanced
  - singleton
  - java-memory-model
  - volatile
  - lazy-initialization
status: complete
version: 4
layout: default
parent: "Design Patterns"
grand_parent: "Technical Mastery"
nav_order: 31
permalink: /technical-mastery/design-patterns/double-checked-locking/
---

⚡ TL;DR - Double-Checked Locking is a concurrency pattern
for lazy initialization that avoids the performance cost
of synchronization after the object is initialized, using
two `null` checks: one outside and one inside a
synchronized block, with `volatile` to ensure visibility.

| #31 | Category: Design Patterns | Difficulty: ★★★ |
|:---|:---|:---|
| **Depends on:** | DPT-001, DPT-005, DPT-006 | |
| **Used by:** | DPT-033, DPT-064 | |
| **Related:** | DPT-006, DPT-032, DPT-033, DPT-035 | |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
A thread-safe lazy singleton: create the object the first
time it is requested, then reuse it. Two naive approaches:

**Approach A - Synchronized method (correct, slow):**
```java
class HeavyConnection {
    private static HeavyConnection INSTANCE;

    static synchronized HeavyConnection getInstance() {
        if (INSTANCE == null) {
            INSTANCE = new HeavyConnection(); // expensive
        }
        return INSTANCE;
    }
}
```
Correct, but EVERY call acquires the lock - even after
the instance exists. Under high concurrency (1000 threads
calling `getInstance()`), this becomes a bottleneck.
`synchronized` on a method: each call acquires and
releases the monitor lock even when no initialization is needed.

**Approach B - Unsynchronized (fast, broken):**
```java
static HeavyConnection getInstance() {
    if (INSTANCE == null) {
        INSTANCE = new HeavyConnection(); // no synchronization!
    }
    return INSTANCE;
}
```
Race condition: two threads see `INSTANCE == null`
simultaneously, both create a new instance. Worse:
without `volatile`, the JVM may reorder the write to
`INSTANCE` before the constructor finishes, causing
a thread to see a partially-initialized object.

**THE INVENTION MOMENT:**
Double-Checked Locking: check for null OUTSIDE the
synchronized block (fast path for post-init calls),
lock only for initialization, check again INSIDE
(handles race between threads that both saw null),
and mark the field `volatile` (prevents reordering).

---

### 📘 Textbook Definition

**Double-Checked Locking (DCL)** is a concurrency design
pattern that reduces the overhead of synchronization
by checking a condition (typically a null check) outside
and inside a synchronized block. The outer check avoids
the cost of acquiring a lock for post-initialization reads.
The inner check handles the race condition where multiple
threads concurrently see the null condition before the
lock is acquired. In Java, the field must be declared
`volatile` to prevent the Java Memory Model (JMM) from
reordering the construction of the object and the
assignment of the reference, which would allow other
threads to observe a partially-initialized instance.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
Double-Checked Locking checks once outside the lock
(fast: avoids synchronization overhead post-init) and
once inside the lock (correct: handles concurrent init),
with `volatile` to close the JMM reordering gap.

**One analogy:**
> Entering a room (getting the instance). Step 1: glance
> through the window - if someone is inside (already initialized),
> just open the door and enter (no lock needed). If no
> one is visible: Step 2: stand in the queue (acquire lock).
> Step 3: when your turn comes, look through the window again
> (second check, inside lock). If someone entered while you
> waited: join them. If still empty: go in first (initialize).

**One insight:**
The `volatile` keyword is what makes Double-Checked Locking
correct. Without `volatile`, the JVM may publish the
reference to `INSTANCE` before the constructor completes
its writes. A second thread then reads `INSTANCE != null`
(outer check passes), bypasses the lock, and accesses a
partially-constructed object. `volatile` adds a "happens-before"
guarantee: the full construction is visible before the
reference is visible to other threads.

---

### 🔩 First Principles Explanation

**JAVA MEMORY MODEL (JMM) ESSENTIALS:**
Absent synchronization, the JVM is free to reorder
instructions and cache writes. A thread T1 writing to
a field may not be immediately visible to thread T2.

Key guarantees:
- `synchronized`: establishes happens-before for all
  operations in the synchronized block. Slow (lock
  acquisition/release on every access).
- `volatile`: guarantees visibility (writes are immediately
  flushed to main memory) and prevents certain reorderings.
  Cheaper than `synchronized` for reads.

**WHY DCL REQUIRES `volatile`:**
Without `volatile`, `INSTANCE = new HeavyConnection()`
can be compiled/reordered as:
1. Allocate memory for `HeavyConnection`
2. Assign reference to `INSTANCE` (visible to other threads!)
3. Call constructor to initialize fields

A thread that reads `INSTANCE` after step 2 but before
step 3 sees a non-null but uninitialized instance.
With `volatile`: the write to `INSTANCE` cannot be
reordered before the constructor completes.

**DERIVED DESIGN:**
```java
class Singleton {
    private volatile static Singleton INSTANCE; // MUST be volatile

    static Singleton getInstance() {
        if (INSTANCE == null) {         // First check (no lock)
            synchronized (Singleton.class) {
                if (INSTANCE == null) { // Second check (with lock)
                    INSTANCE = new Singleton();
                }
            }
        }
        return INSTANCE;
    }
}
```

**TRADE-OFFS:**

**Gain:** Correct and efficient lazy singleton. After
initialization, reads are unsynchronized (just a volatile
read, which is cheaper than a mutex). No synchronized
overhead on the hot path.

**Cost:** Complex, error-prone pattern. Easy to get wrong
(missing `volatile`, missing inner check). Java 5+ only
(pre-Java 5 JMM was insufficient). Modern alternative:
Initialization-on-Demand Holder (IODH) is simpler, equally
correct, and more readable.

---

### 🧪 Thought Experiment

**SETUP:**
`DatabaseConnectionPool` singleton. Initialization takes
500ms (heavy resource setup). 10,000 RPS. Synchronized
`getInstance()` creates a bottleneck for all requests.

**SYNCHRONIZED (correct, slow):**
Every request acquires the lock - 10,000 lock acquisitions
per second even after the pool exists.

**DCL (correct, fast):**
After initialization (one time): reads go through the
volatile read only. Volatile reads are cheap (no mutex).
10,000 RPS: all hit the fast path.

---

### 🧠 Mental Model / Analogy

> DCL is a DOUBLE-LOCK DOOR on a safe room. The room has
> an outer door (no lock, fast) and an inner vault door
> (lock, slow). You open the outer door and check if the
> vault is filled (first null check). If filled: take
> your item and leave (no vault access needed). If empty:
> go to the vault door, queue (synchronize), get your turn,
> check again if the vault is still empty (second check),
> if still empty: fill the vault (initialize). After first
> fill: everyone uses the outer door only.

- "Outer door check" = first null check (unsynchronized)
- "Vault door queue" = synchronized block
- "Second check inside vault" = inner null check
- "Fill the vault" = initialization
- "volatile" = ensures vault contents visible when outer
  door check sees "filled"

---

### 📶 Gradual Depth - Five Levels

**Level 1 - What it is (anyone can understand):**
DCL is a way to safely create a shared object the first
time it is needed, in a multi-threaded program, without
slowing down every subsequent access with a lock.
Check once without locking (fast), then lock and check
again for the first-time creation.

**Level 2 - How to use it (junior developer):**
Two `null` checks, one outside, one inside a synchronized
block. Mark the field `volatile`. Never omit either check
or `volatile`. For Singletons in modern Java: prefer the
Holder pattern (see Level 4) - it achieves the same goal
without DCL complexity.

**Level 3 - How it works (mid-level engineer):**
`volatile` prevents the "publish before construction"
reordering. Java 5+ JMM guarantees: a volatile write
happens-before any subsequent volatile read of the same
field by another thread. So when T2 reads `INSTANCE != null`
(volatile read), all writes made by T1 before the volatile
write (including the constructor) are visible to T2.
Without `volatile`: T2 could read `INSTANCE != null`
but observe partially initialized fields (null fields,
zero numerics, etc.) because the constructor writes were
not flushed before the reference was published.

**Level 4 - Why it was designed this way (senior/staff):**
DCL was popularized as the "correct" lazy singleton pattern
before Java 5. Pre-Java 5, even `volatile` was not sufficient
(JMM was not well-defined enough). Post Java 5: DCL with
`volatile` is correct. However, the simpler alternative
is the **Initialization-on-Demand Holder (IODH)** idiom:
```java
class Singleton {
    private Singleton() {}

    private static class Holder {
        static final Singleton INSTANCE = new Singleton();
    }

    static Singleton getInstance() {
        return Holder.INSTANCE;
    }
}
```
The JVM guarantees class initialization is thread-safe.
`Holder` is only loaded when `getInstance()` is first
called. No `volatile`, no `synchronized`, no two checks.
IODH is preferred over DCL in modern Java for singletons.
DCL is still relevant for non-singleton lazy initialization
where a field (not a static) needs lazy initialization.

**Level 5 - Mastery (distinguished engineer):**
DCL is a case study in the danger of "performance optimization
without formal model verification." Before Java 5, DCL
was widely used and almost universally broken (no memory
model guarantee even with `volatile` on some JVMs).
The pattern was declared "broken" in a famous paper
("The 'Double-Checked Locking is Broken' Declaration").
Java 5's revised JMM (JSR-133) fixed this by providing
strong semantics for `volatile`. DCL is now correct in
Java 5+. This history illustrates a critical principle:
concurrency correctness requires a formal memory model;
"it seems to work" is insufficient. The lesson applies
to all lock-free data structures: always analyze under
the JMM, not just from sequential reasoning.

---

### ⚙️ How It Works (Mechanism)

```
Double-Checked Locking - Thread Interleaving
┌─────────────────────────────────────────────────────────┐
│ Thread T1                   Thread T2                   │
│                                                         │
│ getInstance():              getInstance():              │
│ check INSTANCE == null      check INSTANCE == null      │
│ (both see null)             (both see null)             │
│                                                         │
│ T1 acquires lock ──────────────────────────────────────►│
│ T1 checks INSTANCE == null  T2 BLOCKED (waiting for lock│
│ T1: still null → init                                   │
│ INSTANCE = new Singleton()                              │
│   (volatile write: full                                 │
│    construction flushed)                                │
│ T1 releases lock ──────────────────────────────────────►│
│                             T2 acquires lock            │
│                             T2 checks INSTANCE == null  │
│                             T2: NOT null (T1 wrote it)  │
│                             T2: returns existing instanc│
│                             T2 releases lock            │
│                                                         │
│ T3 arrives AFTER init:                                  │
│ check INSTANCE == null (volatile read: sees full object)│
│ NOT null → return directly  (no lock acquired)          │
└─────────────────────────────────────────────────────────┘
```

---

### 🔄 The Complete Picture - End-to-End Flow

```
First call (T1):
  INSTANCE == null? YES (no lock)
  → enter synchronized block
  → INSTANCE == null? YES (with lock)
  → new HeavyConnection() (full constructor)
  → volatile write to INSTANCE
  → exit synchronized block
  → return INSTANCE

Race: T2 also saw INSTANCE == null before T1 finished:
  T2 BLOCKED waiting for lock
  T2 acquires lock after T1 releases
  T2: INSTANCE == null? NO → return existing
  T2 releases lock immediately

All subsequent calls (T3, T4, T5...):
  INSTANCE == null? NO (volatile read: T1's write is
    visible)
  → return INSTANCE directly (no lock, no synchronized)
```

---

### 💻 Code Example

**Example 1 - Broken DCL (missing volatile):**

```java
// BAD: missing volatile - broken in Java 5+ JMM
class BrokenSingleton {
    private static BrokenSingleton INSTANCE; // NOT volatile

    static BrokenSingleton getInstance() {
        if (INSTANCE == null) {
            synchronized (BrokenSingleton.class) {
                if (INSTANCE == null) {
                    INSTANCE = new BrokenSingleton();
                    // JVM may reorder: publish ref BEFORE constructor
                    // T2 sees non-null but uninitialized object
                }
            }
        }
        return INSTANCE; // T2 may return partially-initialized object
    }
}
```

**Example 2 - Correct DCL with volatile:**

```java
// GOOD: correct DCL with volatile

class HeavyConnectionPool {
    private volatile static HeavyConnectionPool INSTANCE; // volatile

    private final int maxConnections;
    private final String jdbcUrl;

    private HeavyConnectionPool() {
        // expensive initialization: 500ms
        this.maxConnections = Integer.parseInt(
            System.getProperty("db.maxConnections", "10"));
        this.jdbcUrl = System.getProperty("db.url");
        initializePool();
    }

    static HeavyConnectionPool getInstance() {
        if (INSTANCE == null) {               // first check (no lock)
            synchronized (HeavyConnectionPool.class) {
                if (INSTANCE == null) {       // second check (lock)
                    INSTANCE = new HeavyConnectionPool();
                    // volatile write: full construction visible
                }
            }
        }
        return INSTANCE;                      // hot path: no lock
    }
}
```

**Example 3 - IODH (preferred over DCL for singletons):**

```java
// BEST: Initialization-on-Demand Holder idiom
// Same lazy init guarantee, simpler, no volatile needed

class HeavyConnectionPool {
    private HeavyConnectionPool() {
        // expensive initialization
    }

    // JVM loads Holder only when getInstance() is first called
    // Class loading is thread-safe: guaranteed by JVM spec
    private static final class Holder {
        static final HeavyConnectionPool INSTANCE =
            new HeavyConnectionPool();
    }

    static HeavyConnectionPool getInstance() {
        return Holder.INSTANCE; // no null check, no volatile, no lock
    }
}
// Thread-safe, lazy, efficient, readable.
// Prefer IODH over DCL for static singleton lazy initialization.
```

**Example 4 - DCL for instance-level lazy field (where IODH does not apply):**

```java
// Use case: instance field (not static) - IODH doesn't apply here

class CachedAnalyzer {
    private volatile AnalysisResult cachedResult; // volatile

    AnalysisResult getResult() {
        if (cachedResult == null) {          // first check
            synchronized (this) {
                if (cachedResult == null) {  // second check
                    cachedResult = computeExpensiveAnalysis();
                }
            }
        }
        return cachedResult;
    }

    private AnalysisResult computeExpensiveAnalysis() {
        // heavy computation - only runs once
        return new AnalysisResult(/* ... */);
    }
}
```

---

### ⚖️ Comparison Table

| Pattern | Thread-safe | Lazy | Lock on every call | Complexity |
|---|---|---|---|---|
| **DCL with volatile** | Yes | Yes | No (hot path: volatile read only) | High |
| IODH | Yes | Yes | No | Low |
| Eager static init | Yes | No | No | None |
| Synchronized method | Yes | Yes | Yes (always) | Low |
| Enum singleton | Yes | No | No | None |

**Recommendation order for singletons:**
1. Enum singleton (simplest, serialization-safe)
2. IODH (lazy, readable)
3. DCL with volatile (for instance fields, non-singleton lazy init)
4. Synchronized method (when simplicity > performance)

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| DCL is a historical pattern, not relevant in modern Java | DCL is still the correct pattern for lazy initialization of INSTANCE FIELDS (where IODH does not apply - static inner class is not applicable). Example: a cache field computed on first access in a service bean. IODH is only applicable to static fields |
| synchronized alone is sufficient | Synchronized without volatile is ALSO broken for DCL because the inner check relies on visibility: when T2 acquires the lock and sees T1's assignment, that visibility comes from the happens-before of unlock/lock, not from volatile. Actually, synchronized DOES guarantee visibility for threads that acquire the lock - synchronized alone IS sufficient inside the locked block. The problem is the OUTER check which runs WITHOUT synchronization - that check requires volatile |
| volatile is expensive, avoid it | In modern JVMs, a volatile read is typically the same cost as a normal read on x86 (just prevents compiler reordering). A volatile write is slightly more expensive (memory barrier). DCL's volatile cost is: one volatile read per call after initialization. This is negligible |

---

### 🚨 Failure Modes & Diagnosis

**Partially Initialized Object Observed**

**Symptom:**
`NullPointerException` inside the constructor of the
singleton class, with stack traces showing the NPE
occurs on fields that should be initialized. The object
was "seen" before the constructor completed.

**Root Cause:**
`volatile` missing from the `INSTANCE` field. The JMM
allows the reference assignment to be visible before
the constructor completes.

**Diagnosis:**
- Check: is the field declared `volatile`?
- Check: is the field static and being initialized with DCL?
- Thread dump: are any threads inside the constructor while
  other threads see INSTANCE != null?

**Fix:**
Add `volatile`:
```java
private volatile static Singleton INSTANCE;
```

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**
- `Singleton` - DPT-006; DCL is most commonly used to
  implement lazy, thread-safe Singletons

**Builds On This (learn these next):**
- `Thread Pool Pattern` - DPT-033; thread pool initialization
  often uses DCL or IODH
- `Read-Write Lock Pattern` - DPT-035; related concurrency
  pattern for read-heavy data structures

---

### 📌 Quick Reference Card

```
┌─────────────────────────────────────────────────────────┐
│ PATTERN      │ 1st check (no lock) + synchronized +     │
│              │ 2nd check (with lock) + volatile field   │
├──────────────┼──────────────────────────────────────────┤
│ volatile WHY │ Prevents partial-init object publish:    │
│              │ constructor must complete before ref seen│
├──────────────┼──────────────────────────────────────────┤
│ ALTERNATIVE  │ IODH preferred for static singletons:    │
│              │ inner static Holder class, zero complexit│
├──────────────┼──────────────────────────────────────────┤
│ USE DCL WHEN │ Instance field lazy init (IODH inapplicab│
├──────────────┼──────────────────────────────────────────┤
│ BROKEN IF    │ Missing volatile → partial init visible  │
│              │ Missing 2nd check → double initialization│
├──────────────┼──────────────────────────────────────────┤
│ NEXT EXPLORE │ Producer-Consumer → Thread Pool Pattern  │
└─────────────────────────────────────────────────────────┘
```

**If you remember only 3 things:**
1. DCL requires `volatile` - without it, the JVM may publish
   the reference before the constructor finishes. A thread
   can then see a non-null but uninitialized instance.
   This is the entire reason DCL was declared "broken"
   before Java 5.
2. For static singletons: use IODH (inner static Holder
   class) instead of DCL. Same performance, no `volatile`
   needed, no two checks, cleaner code.
3. DCL is still needed for INSTANCE-LEVEL lazy fields
   (where IODH does not apply). Pattern: `volatile` field +
   outer null check + synchronized block + inner null check.

