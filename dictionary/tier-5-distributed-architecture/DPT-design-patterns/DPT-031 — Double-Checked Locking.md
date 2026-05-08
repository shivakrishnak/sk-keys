---
layout: default
title: "Double-Checked Locking"
parent: "Design Patterns"
grand_parent: "Technical Dictionary"
nav_order: 31
permalink: /design-patterns/double-checked-locking/
id: DPT-031
category: Design Patterns
difficulty: ★★★
depends_on: Singleton, Java Memory Model (JMM), volatile, Happens-Before, Concurrency
used_by: Singleton Pattern, Lazy Initialisation, Cache Initialisation, JVM Internals
related: Singleton, volatile, AtomicReference, Initialization-on-Demand Holder, Lazy Loading
tags:
  - pattern
  - deep-dive
  - java
  - concurrency
  - internals
---

# DPT-031 — Double-Checked Locking

⚡ TL;DR — Double-Checked Locking initialises a shared resource lazily with minimal synchronisation overhead by checking for null twice — once without a lock and once inside a lock.

| #791 | Category: Design Patterns | Difficulty: ★★★ |
|:---|:---|:---|
| **Depends on:** | Singleton Pattern, Java Memory Model (JMM), volatile, Happens-Before, Concurrency | |
| **Used by:** | Singleton Pattern, Lazy Initialisation, Cache Initialisation, JVM Internals | |
| **Related:** | Singleton, volatile, AtomicReference, Initialization-on-Demand Holder, Lazy Loading | |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
A `DatabaseConnectionPool` singleton is lazily initialised because it's expensive. The naive thread-safe implementation: `synchronized getInstance()` — every single call acquires the lock, even after initialisation is complete. At 10,000 requests/second, 10,000 threads compete to acquire a lock that protects an already-initialised object. Lock contention becomes a bottleneck that does not disappear after warm-up.

**THE BREAKING POINT:**
Profiling shows 30% of request time is spent waiting on `getInstance()` lock, even though the pool was initialised on the first request. The synchronisation tax is paid on every call, not just the first. Removing synchronisation entirely causes multiple threads to initialise the pool simultaneously — connection exhaustion and data corruption.

**THE INVENTION MOMENT:**
This is exactly why Double-Checked Locking was created. The first check (outside the lock) handles the common case: after initialisation, return immediately with no locking. Only the uncommon case (first-time initialisation) pays the synchronisation cost.

---

### 📘 Textbook Definition

**Double-Checked Locking (DCL)** is an idiom for lazy initialisation with minimal synchronisation overhead. It performs two null checks on the lazily initialised field: the first outside a `synchronized` block (fast, unsynchronised) and the second inside the `synchronized` block (safe, under lock). Without `volatile` on the field, DCL is a broken pattern on modern CPUs due to instruction reordering in the Java Memory Model. With `volatile`, DCL is correct in Java 5+. The pattern is a concurrency microoptimisation that trades code complexity for reduced lock contention on the hot path.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
Check twice: once fast without locking, once safe with locking — pay the lock cost only on the first initialisation.

**One analogy:**
> A bathroom has a "In Use" sign on the door. You first look at the sign from the hall — if it's free, enter immediately (no waiting). If the sign is ambiguous, you knock and wait for confirmation. Most of the time the bathroom is free and you don't wait at all. The knock (lock acquisition) only happens for the rare "ambiguous" case.

**One insight:**
The first check is an optimistic fast path: "has this already been initialised?" — if yes, skip the lock entirely. The second check inside the lock is the correctness guard: "in the time it took me to acquire the lock, did another thread already initialise this?" — prevents double initialisation. The `volatile` keyword makes the initialised value visible across all CPU caches.

---

### 🔩 First Principles Explanation

**CORE INVARIANTS:**
1. The expensive object must be initialised at most once (correctness).
2. After initialisation, every read must be lock-free (performance).
3. The half-constructed object must never be visible to other threads (safety).

**DERIVED DESIGN:**
Given invariant 1+2: checking the field outside the lock handles the common post-initialisation case without contention. The check inside the lock handles the rare race where two threads simultaneously pass the first check.

Given invariant 3 — the tricky part: without `volatile`, the JIT compiler and CPU may reorder the assignment `instance = new T()` such that the reference is published (visible) before the constructor completes. Another thread sees a non-null `instance` but reads uninitialised fields. This was DCL's fatal flaw pre-Java 5. The Java Memory Model (Java 5+) guarantees that a `volatile` write happens-before any subsequent `volatile` read — preventing the partially-constructed object from being observed.

**THE TRADE-OFFS:**
**Gain:** Lock-free reads after initialisation; correct lazy initialisation under concurrency; minimal synchronisation overhead at scale.
**Cost:** Requires `volatile` (correctly); code is complex and easy to get wrong; Initialization-on-Demand Holder (Holder idiom) achieves the same result more simply; DCL is unnecessary in most application code where static final fields are simpler.

---

### 🧪 Thought Experiment

**SETUP:**
500 threads start simultaneously and each calls `Singleton.getInstance()`. The singleton is lazily initialised. CPU has 8 cores.

**WHAT HAPPENS WITHOUT DCL (full synchronisation):**
Each of 500 threads serialises through `synchronized getInstance()`. After initialisation, 499 remaining threads wait in a queue before they can read an already-set reference. Lock contention is O(n) threads.

**WHAT HAPPENS WITH BROKEN DCL (no volatile):**
Two threads A and B simultaneously see `instance == null`. Thread A enters the lock, creates the object, and writes the reference. Due to CPU reordering, Thread B sees a non-null `instance` but the object's fields are not yet written (constructor not visible yet). Thread B reads uninitialised fields — corruption.

**WHAT HAPPENS WITH CORRECT DCL (volatile):**
`volatile` on `instance` ensures Thread A's constructor completion happens-before Thread B's read of `instance`. Thread B sees either null (initialises itself) or the fully-constructed object. 498 subsequent threads read `instance` non-null in the first check and return with zero lock contention.

**THE INSIGHT:**
DCL's correctness depends entirely on `volatile`. Without it, it's visibly safe on some JVMs but subtly broken — one of the most famous examples of a pattern that appears to work and then fails randomly under load.

---

### 🧠 Mental Model / Analogy

> DCL is like a coffee shop with a sign outside: "Coffee ready." When the sign is up, you walk straight in — no waiting. When the sign is down (opening time), you queue and the first person through confirms coffee is brewing, starts the process, and flips the sign. Everyone behind walks straight in after that. The `volatile` keyword is what ensures the sign is readable (memory-coherent) from every street corner simultaneously, not just the corner you're standing on.

- "Coffee ready sign" → `volatile instance` field (visible to all CPUs)
- "Walk straight in" → first null check passing (no lock acquired)
- "Queue and confirm" → acquiring `synchronized` and second null check
- "First person starts the process" → thread that initialises the instance
- "Flipping the sign atomically" → `volatile` write happens-before all subsequent reads

Where this analogy breaks down: the sign is flipped after coffee is fully ready. Without `volatile`, in the code the "sign" (reference) can appear flipped before the object behind it is fully constructed — the analogy hides this subtlety.

---

### 📶 Gradual Depth — Four Levels

**Level 1 — What it is (anyone can understand):**
Double-Checked Locking is a way to create a shared object exactly once, safely, in a multi-threaded program — without paying the cost of a lock on every access. It checks "has it been created?" twice to be sure, using a lock only when creating.

**Level 2 — How to use it (junior developer):**
Declare the field as `private static volatile T instance`. In `getInstance()`: first check `if (instance == null)` without synchronisation. If null, enter `synchronized (T.class)`. Second check `if (instance == null)`. If still null, create the object and assign. Return `instance`. Always use the Holder idiom instead if possible — it is simpler and correct by default.

**Level 3 — How it works (mid-level engineer):**
The `volatile` keyword in Java 5+ provides two guarantees for DCL: (1) visibility — a write to a volatile field is immediately visible to all threads (no CPU cache lag); (2) ordering — the write cannot be reordered before the constructor completes (happens-before guarantee). Without `volatile`, the JIT can optimise `instance = new T()` to: allocate memory → write reference to `instance` → run constructor. Another thread sees non-null `instance` but unrun constructor. `volatile` prevents this reordering. The second check inside the lock prevents two threads, both passing the first check simultaneously, from both creating the object.

**Level 4 — Why it was designed this way (senior/staff):**
DCL was discussed in Java circles from 1996–2001 and was widely believed to be correct. In 2001, Jeremy Manson and Brian Goetz proved definitively that DCL without `volatile` was broken under the Java Memory Model due to instruction reordering. The fix came with Java 5 (JSR-133), which strengthened the JMM guarantees for `volatile`. The Java Language Specification now formally guarantees that DCL with `volatile` is correct. For most production code, the preferred alternative is the Initialization-on-Demand Holder idiom: a nested static class `Holder { static final T INSTANCE = new T(); }` — JVM class loading guarantees that `INSTANCE` is initialised exactly once (with full happens-before) when `Holder` is first accessed, with zero synchronisation code. JVM class loading itself is already thread-safe. Use DCL only when you cannot use static final initialisation (rare cases involving configurable or replaceable singletons).

---

### ⚙️ How It Works (Mechanism)

```
┌─────────────────────────────────────────────────┐
│  DOUBLE-CHECKED LOCKING — FLOW                  │
│                                                 │
│  Thread A and Thread B call getInstance()       │
│                                                 │
│  Both see instance == null (first check)        │
│                                                 │
│  Thread A acquires lock                         │
│  Thread B waits for lock                        │
│                                                 │
│  Thread A: second check → null → creates obj   │
│  Thread A: instance = new T() (volatile write) │
│  Thread A: releases lock                        │
│                                                 │
│  Thread B: acquires lock                        │
│  Thread B: second check → NOT null → returns   │
│  Thread B: releases lock                        │
│                                                 │
│  Thread C (later): first check → NOT null       │
│  Thread C: returns immediately, NO lock         │
└─────────────────────────────────────────────────┘
```

**Memory model guarantee (volatile):**
```
Thread A: new T() → sets all fields → volatile write
         |→ HAPPENS-BEFORE →|
Thread B: volatile read → sees fully constructed T
```

Without `volatile`:
```
Thread A: allocates memory → volatile write to instance
                           → (constructor may run later!)
Thread B: volatile read → non-null but unfinished object!
```

---

### 🔄 The Complete Picture — End-to-End Flow

**NORMAL FLOW (after warmup):**
```
10,000 concurrent requests call getInstance()
  → first check: instance != null
                 ← YOU ARE HERE (fast path, no lock)
  → return instance (volatile read only)
  → zero lock contention after first init
```

**FIRST-INIT FLOW:**
```
Request 1 sees null → acquires lock
                     ← YOU ARE HERE (init path)
  → second check confirms null
  → creates expensive object
  → volatile write publishes it
  → releases lock
Requests 2-N: first check now non-null → fast path
```

**FAILURE PATH (volatile missing):**
```
Thread B reads instance != null (first check passes)
  → reads partially constructed object
  → NullPointerException on uninitialised field
  → or: silent data corruption with wrong initial values
  → intermittent, load-dependent, very hard to reproduce
```

**WHAT CHANGES AT SCALE:**
At very high throughput (100,000+ req/s), the `volatile` read on every `getInstance()` call has measurable overhead — a volatile read is ~10-40 ns due to memory barrier. For extreme performance, assign `instance` to a local variable after the first check and use the local thereafter to avoid repeated volatile reads in the same method.

---

### 💻 Code Example

**Example 1 — BROKEN DCL (missing volatile — DO NOT USE):**
```java
// BAD: missing volatile — BROKEN on modern CPUs
public class BrokenSingleton {
    private static BrokenSingleton instance; // NOT volatile!

    private BrokenSingleton() { }

    public static BrokenSingleton getInstance() {
        if (instance == null) {               // check 1
            synchronized (BrokenSingleton.class) {
                if (instance == null) {       // check 2
                    instance = new BrokenSingleton();
                    // CPU can reorder: reference written
                    // BEFORE constructor completes!
                }
            }
        }
        return instance;
        // Another thread may see non-null but
        // with uninitialised fields — DATA CORRUPTION
    }
}
```

**Example 2 — CORRECT DCL with volatile:**
```java
// GOOD: volatile ensures correct visibility+ordering
public class Singleton {
    // volatile: prevents instruction reordering
    private static volatile Singleton instance;

    private Singleton() {
        // expensive initialisation
    }

    public static Singleton getInstance() {
        // Fast path: no lock for already-initialised
        if (instance == null) {
            synchronized (Singleton.class) {
                // Slow path: locked re-check
                if (instance == null) {
                    instance = new Singleton();
                    // volatile write → happens-before
                    // any subsequent volatile read
                }
            }
        }
        return instance;
    }
}
```

**Example 3 — PREFERRED: Initialization-on-Demand Holder:**
```java
// BEST: Holder idiom — simpler, just as fast, always correct
// No volatile, no synchronized, no DCL complexity
public class PreferredSingleton {

    private PreferredSingleton() { }

    // JVM initialises Holder class lazily, thread-safely
    // Class loading guarantees exactly-once init
    private static class Holder {
        static final PreferredSingleton INSTANCE =
            new PreferredSingleton();
    }

    // No synchronisation needed — JVM handles it
    public static PreferredSingleton getInstance() {
        return Holder.INSTANCE;
    }
}
// Holder is loaded ONLY when getInstance() is first called
// JVM guarantees thread-safe, exactly-once initialisation
```

**Example 4 — AtomicReference alternative:**
```java
// If instance may need replacement (non-standard singleton):
public class ReplacableSingleton {
    private static final AtomicReference<ReplacableSingleton>
        INSTANCE = new AtomicReference<>();

    public static ReplacableSingleton getInstance() {
        ReplacableSingleton current = INSTANCE.get();
        if (current != null) return current;

        ReplacableSingleton created = new ReplacableSingleton();
        // compareAndSet: only one thread wins; others discard
        if (INSTANCE.compareAndSet(null, created)) {
            return created;
        }
        return INSTANCE.get(); // loser returns winner's instance
    }
}
```

---

### ⚖️ Comparison Table

| Approach | Thread Safe | Performance | Complexity | Best For |
|---|---|---|---|---|
| Eager init (static final) | Yes | Best | Minimal | Always-needed singletons |
| **DCL (volatile)** | Yes | Very good | High | Performance-sensitive lazy init |
| Holder idiom | Yes | Best (lazy) | Low | Preferred lazy singleton |
| synchronized method | Yes | Poor (lock on every call) | Low | Not recommended |
| AtomicReference | Yes | Good | Medium | Replaceable instances |

How to choose: use Holder idiom for lazy singletons — simpler and just as fast. Use DCL only when you have a profiled lock-contention problem on a hot lazy-init path. Use eager init when startup cost is acceptable.

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| DCL without volatile is fine on modern hardware | Modern CPUs and JIT compilers can reorder instructions; DCL without volatile is broken per the Java Memory Model regardless of hardware |
| DCL is necessary for high-performance singletons | The Holder idiom is equally fast, simpler, always correct, and requires no volatile or synchronized |
| volatile is expensive | A volatile read is ~10-40 ns — negligible for objects initialised once and read millions of times. The benefit far exceeds the cost |
| DCL prevents multiple initialisation attempts in all cases | Two threads simultaneously passing the first check both try to acquire the lock. One waits. The second check inside the lock prevents double initialisation — but both threads attempted to acquire the lock |
| Java's synchronized keyword on the field prevents this | `synchronized` on the getInstance() method is the naive approach but creates lock contention on every call. It's thread-safe but slow at scale |

---

### 🚨 Failure Modes & Diagnosis

**1. DCL Without volatile — Partial Construction Read**

**Symptom:** Intermittent `NullPointerException` or `IllegalStateException` from fields of the singleton. Reproducible under heavy load but not in single-threaded tests.

**Root Cause:** `instance` field is not `volatile`. JIT reordered the constructor and reference publication. A thread reads the non-null reference and accesses uninitialised fields.

**Diagnostic:**
```bash
# Enable JVM flag to detect unsynchronised access (JVM TI)
java -XX:+PrintCompilation -Xss512k AppClass 2>&1 \
     | grep "Singleton.getInstance"
# Run with thread sanitizer tools:
# -javaagent:thread-weaver.jar (ThreadWeaver for Java)
# Or: reproduce by injecting sleep between allocation + init
```

**Fix:**
```java
// Add volatile to the instance field:
private static volatile Singleton instance;
```

**Prevention:** Code review rule: any DCL implementation without `volatile` on the shared field is a defect. Check `private static Singleton` → must be `private static volatile Singleton`.

---

**2. Lock on Different Objects — DCL Fails**

**Symptom:** Multiple instances of the "singleton" created under load.

**Root Cause:** Multiple threads synchronise on different objects: one on `this`, one on `Singleton.class` — they don't contend and both proceed through the second check simultaneously.

**Diagnostic:**
```bash
# Add instance creation counter
private static final AtomicInteger initCount =
    new AtomicInteger();
// In constructor: initCount.incrementAndGet()
# If initCount > 1 after startup: multiple inits
```

**Fix:**
```java
// Always synchronise on the class object, not this
synchronized (Singleton.class) { // correct
// never: synchronized (this) — wrong for static methods
```

**Prevention:** Static DCL must always synchronise on the class literal (`ClassName.class`) or a dedicated static lock object.

---

**3. Performance Regression — volatile on Every Read**

**Symptom:** getInstance() is called 50 million times per second in a tight loop. Profiler shows 15% time in volatile memory barrier.

**Root Cause:** Every call reads the volatile field, triggering a memory barrier even when the instance has been initialised for hours.

**Diagnostic:**
```bash
# Profiler: look for memory barrier overhead
async-profiler -e cpu -d 10 -f prof.html <PID>
# Look for getInstance in hot paths
```

**Fix:**
```java
// Optimisation: assign to local to avoid repeated volatile reads
public static Singleton getInstance() {
    Singleton local = instance; // one volatile read
    if (local == null) {
        synchronized (Singleton.class) {
            local = instance; // read again under lock
            if (local == null) {
                local = new Singleton();
                instance = local; // one volatile write
            }
        }
    }
    return local; // return local (not volatile re-read)
}
```

**Prevention:** For extreme performance, consider the Holder idiom (no volatile reads) or pre-initialise eagerly.

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**
- `Java Memory Model (JMM)` — DCL correctness hinges on JMM happens-before guarantees; without understanding JMM, why `volatile` is required is not obvious
- `volatile` — the field modifier that makes DCL correct; understanding its visibility and ordering guarantees is essential
- `Happens-Before` — the formal JMM relationship that `volatile` establishes between writer and reader threads

**Builds On This (learn these next):**
- `Initialization-on-Demand Holder` — the simpler, correct alternative to DCL; uses JVM class loading as the synchronisation mechanism with zero explicit locking
- `AtomicReference` — a CAS-based alternative for lazy initialisation that avoids both volatile complexity and lock contention
- `Singleton` — DCL is typically used to implement lazy Singleton; understanding Singleton motivates DCL

**Alternatives / Comparisons:**
- `Singleton with static final` — eager initialisation; simpler and safe; only use DCL if startup cost genuinely matters
- `Holder Idiom` — lazy, lock-free, correct by JVM spec; always prefer over DCL
- `enum Singleton` — Joshua Bloch's preferred Singleton (Effective Java); serialisation-safe, thread-safe, simpler than DCL

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ WHAT IT IS   │ Two-check lazy init: fast no-lock read    │
│              │ + slow locked init for first-time only    │
├──────────────┼───────────────────────────────────────────┤
│ PROBLEM IT   │ Full sync on getInstance() serialises     │
│ SOLVES       │ all threads even after object is ready    │
├──────────────┼───────────────────────────────────────────┤
│ KEY INSIGHT  │ volatile is REQUIRED — without it, the    │
│              │ constructor can be reordered past the ref │
├──────────────┼───────────────────────────────────────────┤
│ USE WHEN     │ Lazy init of expensive singleton with     │
│              │ lock-contention performance concern       │
├──────────────┼───────────────────────────────────────────┤
│ AVOID WHEN   │ Use Holder idiom instead — simpler, same  │
│              │ performance, correct by default           │
├──────────────┼───────────────────────────────────────────┤
│ TRADE-OFF    │ Lock-free hot path vs code complexity     │
│              │ and volatile-correctness requirement      │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "Check outside cheap; check inside safe;  │
│              │  volatile makes it visible."              │
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ Holder Idiom → volatile →                 │
│              │ Java Memory Model                         │
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** A team implements a `ConfigurationManager` singleton with correct DCL (using `volatile`). The class is loaded by a custom ClassLoader in a plugin framework. Each plugin gets its own ClassLoader. Explain what happens to the "singleton guarantee" in this scenario, trace the exact mechanism by which multiple instances can be created, and describe what change to the design would actually enforce single-instance semantics in a multi-ClassLoader environment.

**Q2.** A developer argues: "I'll skip volatile and just flush the CPU cache manually using an `AtomicInteger` increment before returning the instance — that provides the same memory visibility." Is this correct? Trace the exact guarantee provided by `AtomicInteger.incrementAndGet()` vs `volatile`, and identify whether the developer's approach correctly prevents the partial construction visibility problem. If it doesn't, explain exactly why.

