---
layout: default
title: "Double-Checked Locking"
parent: "Design Patterns"
nav_order: 790
permalink: /design-patterns/double-checked-locking/
number: "790"
category: Design Patterns
difficulty: ★★★
depends_on: "Singleton Pattern, volatile, Happens-Before, Memory Barrier, Thread Safety"
used_by: "Lazy initialization, Singleton, caches, framework bootstrapping"
tags: #advanced, #design-patterns, #concurrency, #java-memory-model, #volatile, #singleton
---

# 790 — Double-Checked Locking

`#advanced` `#design-patterns` `#concurrency` `#java-memory-model` `#volatile` `#singleton`

⚡ TL;DR — **Double-Checked Locking** is a pattern for lazy initialization of a shared resource that avoids synchronization overhead after the first initialization — checking nullness twice: once without lock (fast path) and once inside the lock (safe initialization), requiring `volatile` to be correct on the Java Memory Model.

| #790            | Category: Design Patterns                                                  | Difficulty: ★★★ |
| :-------------- | :------------------------------------------------------------------------- | :-------------- |
| **Depends on:** | Singleton Pattern, volatile, Happens-Before, Memory Barrier, Thread Safety |                 |
| **Used by:**    | Lazy initialization, Singleton, caches, framework bootstrapping            |                 |

---

### 📘 Textbook Definition

**Double-Checked Locking (DCL)**: a software design idiom used to reduce locking overhead in lazy initialization by checking the initialization condition first without acquiring a lock, and only acquiring the lock and rechecking if the first check indicates initialization hasn't happened. In Java, the `volatile` keyword is required on the field to prevent the JIT compiler from reordering the write to the instance before the constructor completes — a subtle Java Memory Model issue that makes naive DCL incorrect. The pattern became (in)famous because the "obvious" Java implementation was broken in Java 1.4 and earlier, and was fixed by the JSR-133 memory model revision in Java 5 + `volatile`. GoF Singleton with lazy initialization is its canonical application. Java 5+: DCL with `volatile` is correct. Alternative: initialization-on-demand holder (enum/static nested class).

---

### 🟢 Simple Definition (Easy)

You have a Singleton — one shared, expensive instance. You want to create it lazily (only when first needed). Without synchronization: race condition. With full synchronization (`synchronized` method): every access acquires a lock, even after initialization — slow. DCL: check once without lock ("already initialized? skip sync"), check again inside lock ("is REALLY uninitialized? initialize"). After initialization, all threads take the fast path (no lock). `volatile` is required to prevent JIT reordering that would give a thread a half-initialized instance.

---

### 🔵 Simple Definition (Elaborated)

Classic Singleton in Spring: `ConfigManager` is initialized once, lazily, on first access. Without lazy init: initialization at startup (wasteful if never used). With synchronized method: every `getInstance()` acquires a monitor lock — even millions of reads after initialization. DCL: only the initial (rare) initialization is synchronized. After `instance != null`, all reads proceed lock-free. `volatile` on the field: prevents the JVM from making the partially-constructed object visible to other threads before its constructor completes.

---

### 🔩 First Principles Explanation

**Why naive DCL is broken and why `volatile` fixes it:**

```
STEP 1: EAGER INITIALIZATION — ALWAYS SYNCHRONIZES (SLOW):

  class Singleton {
      private static Singleton instance;

      synchronized static Singleton getInstance() {   // lock on EVERY call
          if (instance == null) {
              instance = new Singleton();
          }
          return instance;
      }
  }
  // After initialization: all threads still acquire/release lock.
  // In high-throughput systems: lock contention on every getInstance() call.

STEP 2: BROKEN DCL — NO VOLATILE (WRONG!):

  class Singleton {
      private static Singleton instance;  // ← MISSING volatile — BROKEN

      static Singleton getInstance() {
          if (instance == null) {               // check 1: no lock (fast path)
              synchronized (Singleton.class) {
                  if (instance == null) {       // check 2: inside lock (safe)
                      instance = new Singleton();
                  }
              }
          }
          return instance;
      }
  }

  // WHY IS THIS BROKEN (pre-Java 5, or without volatile):
  //
  // "instance = new Singleton()" compiles to roughly:
  //   1. Allocate memory for Singleton object
  //   2. Write reference to 'instance' field (non-null now!)
  //   3. Execute Singleton() constructor (initialize fields)
  //
  // JIT may reorder steps: 1 → 2 → 3 (write reference BEFORE constructor runs!)
  // Thread A: allocated memory, wrote reference (step 1+2), not yet constructed (step 3)
  // Thread B: check 1 → instance != null (partially constructed!) → returns broken instance
  // Thread B uses Singleton with uninitialized fields → subtle data corruption.

STEP 3: CORRECT DCL — WITH VOLATILE (JAVA 5+):

  class Singleton {
      private static volatile Singleton instance;  // ← volatile REQUIRED

      static Singleton getInstance() {
          if (instance == null) {               // check 1: no lock — fast path for reads
              synchronized (Singleton.class) {
                  if (instance == null) {       // check 2: inside lock — safe init
                      instance = new Singleton();
                      // volatile write: happens-before all subsequent volatile reads
                      // Constructor completes BEFORE reference is visible to other threads
                  }
              }
          }
          return instance;
      }
  }

  // WHY volatile FIXES IT:
  // Java Memory Model: volatile write happens-before any subsequent volatile read.
  // JIT cannot reorder: constructor must complete before volatile write to 'instance'.
  // Thread B reads instance after Thread A's volatile write → sees fully constructed object.

STEP 4: BETTER ALTERNATIVE — INITIALIZATION-ON-DEMAND HOLDER:

  class Singleton {
      // Private static nested class — initialized ONLY when getInstance() is first called
      private static class Holder {
          static final Singleton INSTANCE = new Singleton();  // thread-safe by class loading
      }

      static Singleton getInstance() {
          return Holder.INSTANCE;  // triggers class loading of Holder → initializes INSTANCE
      }
  }
  // JVM class loading is thread-safe by specification.
  // No volatile, no synchronization, lazy, correct.
  // Simpler, cleaner than DCL.

STEP 5: ENUM SINGLETON (SIMPLEST, ALSO THREAD-SAFE):

  enum Singleton {
      INSTANCE;
      // enum initialization is thread-safe.
      // Also: serialization-safe, reflection-safe.
      void doSomething() { ... }
  }

  Singleton s = Singleton.INSTANCE;  // lazy? No — eager. But typically acceptable.

WHEN DCL IS STILL VALUABLE:

  // Lazy initialization with complex condition (not just null check):
  // Cached value that can be reset:
  class ConfigCache {
      private volatile Map<String, String> cache;  // volatile for DCL
      private volatile long lastLoadTime;

      Map<String, String> getConfig() {
          if (cache == null || isStale()) {               // check 1: no lock
              synchronized (this) {
                  if (cache == null || isStale()) {       // check 2: inside lock
                      cache = loadFromDatabase();         // expensive load
                      lastLoadTime = System.currentTimeMillis();
                  }
              }
          }
          return cache;
      }

      private boolean isStale() { return System.currentTimeMillis() - lastLoadTime > TTL; }
  }
  // Holder pattern doesn't work here (must re-initialize on stale/reset).
  // DCL with volatile is the right pattern.
```

---

### ❓ Why Does This Exist (Why Before What)

WITHOUT DCL:

- Eager init: wastes resources if Singleton never used
- Synchronized method: lock acquired on EVERY call — bottleneck in high-throughput code

WITH DCL:
→ Lazy initialization. After first init: fast path — no lock acquired. Only the rare initialization path is synchronized. No performance penalty for the common case (read after init).

---

### 🧠 Mental Model / Analogy

> A coffee shop opening in the morning. Without DCL: the manager locks the whole café every time a customer wants coffee — even mid-afternoon when setup is long done. With DCL: "Is coffee ready? (check without locking the whole café)" → if yes, just pour. Only the first-morning setup gets the full lock — check again inside lock to confirm nobody else set up simultaneously. `volatile` = ensures the setup steps (grind beans, fill water) ALL complete before the "Coffee ready" sign is flipped on.

"Is coffee ready?" = first check (without lock)
"Lock the setup area" = `synchronized` block
"Check again inside lock" = second check (double-checked)
"Coffee ready sign" = the `volatile` field
"`volatile` = setup completes before sign flipped" = memory barrier; no reordering of constructor + reference write

---

### ⚙️ How It Works (Mechanism)

```
DCL EXECUTION FLOW:

  Thread read (common case, after init):
  check1: instance != null → return instance immediately (NO lock)

  Thread write (rare, first time):
  check1: instance == null → acquire lock
  check2: instance == null (inside lock) → create instance → volatile write → release lock

  Why check twice:
  - Between check1 and lock acquisition, another thread may have initialized.
  - Without check2: multiple threads pass check1 → all initialize → lost writes.
  - check2 inside lock: exactly one thread initializes.

  volatile guarantee:
  JIT cannot reorder volatile write before constructor completes.
  All threads that read volatile instance after the write see the fully constructed object.
```

---

### 🔄 How It Connects (Mini-Map)

```
Lazy init with fast path (no-lock) reads and synchronized first-time initialization
        │
        ▼
Double-Checked Locking ◄──── (you are here)
(volatile field + synchronized init + double null check)
        │
        ├── Singleton Pattern: primary use case for DCL
        ├── volatile keyword: essential — without it, DCL is broken on JMM
        ├── Happens-Before: volatile write establishes happens-before for all subsequent reads
        └── Initialization-on-Demand Holder: cleaner alternative for Singleton lazy init
```

---

### 💻 Code Example

```java
// Correct DCL in Java 5+ — with volatile:
public class HeavyResource {
    private static volatile HeavyResource instance;   // volatile: REQUIRED

    private final Map<String, Object> config;

    private HeavyResource() {
        // Expensive: loads config from DB, parses, validates
        this.config = loadConfiguration();
    }

    public static HeavyResource getInstance() {
        if (instance == null) {                        // check 1: fast path (no lock)
            synchronized (HeavyResource.class) {
                if (instance == null) {                // check 2: safe init path
                    instance = new HeavyResource();    // volatile write: constructor completes first
                }
            }
        }
        return instance;
    }
}

// Better alternative — Initialization-On-Demand Holder (no volatile needed):
public class HeavyResourceHolder {
    private HeavyResourceHolder() { /* loaded once by class loader */ }

    private static final class Holder {
        // JVM initializes Holder.INSTANCE only when first accessed (lazy).
        // Class loading is thread-safe — no synchronization or volatile needed.
        static final HeavyResourceHolder INSTANCE = new HeavyResourceHolder();
    }

    public static HeavyResourceHolder getInstance() {
        return Holder.INSTANCE;  // triggers class load → lazy, thread-safe
    }
}
```

---

### ⚠️ Common Misconceptions

| Misconception                                    | Reality                                                                                                                                                                                                                                                                                                                                                                                                                                           |
| ------------------------------------------------ | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| DCL without volatile is fine on modern hardware  | WRONG. DCL without `volatile` is still broken in Java — not due to CPU cache coherence (modern CPUs handle that) but due to JIT compiler reordering. The JIT can reorder the store to `instance` before the constructor completes, creating a window where other threads see a non-null but partially constructed object. `volatile` is a compiler directive preventing this reordering. This is a language-level requirement, not just hardware. |
| Synchronized method is always safe enough        | Yes, `synchronized getInstance()` is always correct, but it's unnecessarily slow for the read-after-init case. In systems where `getInstance()` is called millions of times per second (every request touches a Singleton), synchronized overhead matters. DCL or Holder pattern avoids this.                                                                                                                                                     |
| DCL is the best Singleton initialization pattern | The Initialization-On-Demand Holder pattern (static nested class) is generally preferred over DCL in Java: no volatile, simpler, JVM spec-guaranteed thread safety via class loading. DCL is still useful when the initialized value must be re-settable or has more complex validity conditions (like the stale cache example).                                                                                                                  |

---

### 🔥 Pitfalls in Production

**DCL on non-volatile field causes intermittent corruption:**

```java
// ANTI-PATTERN: missing volatile — causes subtle, intermittent bugs:
public class ServiceRegistry {
    private static ServiceRegistry instance;   // ← NO volatile — WRONG!

    private final Map<String, Service> services = new ConcurrentHashMap<>();

    private ServiceRegistry() {
        services.put("email", new EmailService());
        services.put("payment", new PaymentService());
    }

    public static ServiceRegistry getInstance() {
        if (instance == null) {                    // check 1
            synchronized (ServiceRegistry.class) {
                if (instance == null) {            // check 2
                    instance = new ServiceRegistry();
                }
            }
        }
        return instance;
    }

    public Service getService(String name) { return services.get(name); }
}

// Bug scenario:
// Thread A: creates ServiceRegistry, JIT reorders: writes instance ref BEFORE populating services map
// Thread B: check1 → instance != null → gets instance → calls getService("email") → null!
// NPE in production, intermittent, never reproduces in test (timing-dependent).

// FIX: add volatile:
private static volatile ServiceRegistry instance;   // prevents reordering

// ALSO OK: use Holder:
private static class Holder {
    static final ServiceRegistry INSTANCE = new ServiceRegistry();
}
public static ServiceRegistry getInstance() { return Holder.INSTANCE; }
```

---

### 🔗 Related Keywords

- `Singleton Pattern` — canonical use case for DCL: lazy initialization of one shared instance
- `volatile keyword` — required for correct DCL: prevents JIT reordering of reference write
- `Happens-Before` — volatile write establishes happens-before, making constructor visible to all threads
- `Memory Barrier` — volatile emits a memory barrier: prevents reordering across the barrier
- `Initialization-On-Demand Holder` — cleaner alternative to DCL for Singleton lazy initialization

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ KEY IDEA     │ Check twice: once without lock (fast     │
│              │ path), once inside lock (safe init).     │
│              │ volatile REQUIRED for JMM correctness.   │
├──────────────┼───────────────────────────────────────────┤
│ USE WHEN     │ Lazy singleton init; re-settable cache;  │
│              │ expensive object initialized on demand;  │
│              │ read-heavy; init happens at most once    │
├──────────────┼───────────────────────────────────────────┤
│ AVOID WHEN   │ Holder pattern is applicable (simpler);  │
│              │ object is cheap to init eagerly;         │
│              │ forgetting volatile is a team risk       │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "Morning café setup: check if coffee is  │
│              │  ready before locking the counter —      │
│              │  volatile ensures setup is truly done."  │
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ volatile keyword → Happens-Before →       │
│              │ Memory Barrier → Initialization Holder   │
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** The Initialization-On-Demand Holder (IODH) pattern relies on a subtle JVM guarantee: class initialization is performed by the JVM with a per-class lock (described in JVM Spec §5.5). When `Holder.INSTANCE` is first accessed, the JVM initializes `Holder` exactly once, holding the class initialization lock during initialization, then releasing it. All threads that access `Holder.INSTANCE` after initialization see the fully initialized value. Why is this guarantee automatically correct without any `volatile` or `synchronized` in your code? What JVM mechanism provides the "happens-before" guarantee in IODH?

**Q2.** Spring beans are singletons by default (`@Scope("singleton")`). Spring creates each bean once and caches it in the `ApplicationContext`. Does Spring use DCL internally to manage singleton bean creation? Or is Spring's bean creation thread-safety handled by a different mechanism? If multiple threads simultaneously request a not-yet-created singleton bean, what does Spring do to ensure exactly-once creation? Research hint: `DefaultSingletonBeanRegistry.getSingleton()`.
