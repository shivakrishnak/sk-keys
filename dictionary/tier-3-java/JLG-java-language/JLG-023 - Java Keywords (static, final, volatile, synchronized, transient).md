---
version: 2
layout: default
title: "Java Keywords (static, final, volatile, synchronized, transient)"
parent: "Java Language"
grand_parent: "Technical Dictionary"
nav_order: 23
permalink: /java/java-keywords/
id: JLG-064
category: Java & JVM Internals
difficulty: ★★☆
depends_on: Java Language, Java Memory Model (JMM), Thread (Java)
used_by: Java Concurrency, Spring Core, Serialization
related: volatile, synchronized, Java Memory Model (JMM)
tags:
  - java
  - jvm
  - concurrency
  - intermediate
---

# JLG-023 - Java Keywords (static, final, volatile, synchronized, transient)

⚡ TL;DR - Five Java keywords control class-level state, immutability, memory visibility, mutual exclusion, and serialisation exclusion - each with distinct JVM semantics.

| Attribute | Value |
|---|---|
| **Depends on** | Java Language, Java Memory Model (JMM), Thread (Java) |
| **Used by** | Java Concurrency, Spring Core, Serialization |
| **Related** | volatile, synchronized, Java Memory Model (JMM) |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:** Without these keywords, every field would require manual lifecycle management, safety documentation, and runtime guards. Shared mutable state would have no compiler-enforced visibility guarantees. Utility classes would need instances. Serialised objects would expose sensitive fields. Constants could be reassigned.

**THE BREAKING POINT:** Multi-threaded programs without `volatile` or `synchronized` suffer from stale reads, torn writes, and race conditions that are intermittent and nearly impossible to reproduce. Without `final`, defensive copying is required everywhere. Without `static`, there is no way to express class-level state vs instance-level state.

**THE INVENTION MOMENT:** Java's designers embedded these modifiers into the language to make common correctness invariants verifiable at compile time and enforceable at JVM bytecode level - reducing an entire class of runtime bugs to compile errors or clearly documented contracts.

---

### 📘 Textbook Definition

Five Java access and behaviour modifiers with distinct semantics:
- **`static`** - binds a member to the class rather than any instance; shared across all instances
- **`final`** - on variables: prevents reassignment; on methods: prevents overriding; on classes: prevents subclassing
- **`volatile`** - guarantees that reads and writes to a field are visible to all threads; establishes a happens-before relationship without mutual exclusion
- **`synchronized`** - acquires the intrinsic monitor lock of an object before executing a block or method, ensuring mutual exclusion and memory visibility
- **`transient`** - marks a field as excluded from Java's default object serialisation mechanism

---

### ⏱️ Understand It in 30 Seconds

**One line:** Each keyword is a contract: `static` means shared, `final` means fixed, `volatile` means visible, `synchronized` means exclusive, `transient` means invisible-to-serialisation.

> Five security badges for a field or method: `static` is the office master key (one copy, everyone uses it), `final` is a laminated badge (can't be modified), `volatile` is a public noticeboard (everyone sees the latest update), `synchronized` is a room with a single-entry door (one visitor at a time), `transient` is a visitor badge (not kept in the permanent record).

**One insight:** `volatile` gives visibility but not atomicity. `synchronized` gives both visibility AND atomicity - knowing the difference is the most important distinction in Java concurrency.

---

### 🔩 First Principles Explanation

**CORE INVARIANTS:**
1. `static` - one copy per class in the method area; loaded at class initialisation, shared across instances
2. `final` field - must be assigned in the constructor (for instance) or declaration (for static); JIT can inline final values
3. `volatile` - every read goes to main memory; every write flushes to main memory; establishes happens-before with JMM
4. `synchronized` - acquires monitor lock; only one thread enters at a time; also establishes full memory visibility on enter/exit
5. `transient` - `ObjectOutputStream` skips transient fields; they are initialised to default values on deserialisation

**DERIVED DESIGN:** Each keyword maps to specific JVM bytecode or memory-model semantics. `volatile` compiles to memory barrier instructions (`MFENCE` on x86). `synchronized` compiles to `monitorenter`/`monitorexit` bytecodes. `final` fields in constructors get a memory-barrier guarantee - other threads that obtain a reference to the constructed object are guaranteed to see the final fields.

**THE TRADE-OFFS:**
- **Gain:** Compiler-verified contracts, reduced defensive coding, JIT optimisation opportunities (`final`), thread-safety guarantees
- **Cost:** `synchronized` causes contention and context switching under high concurrency; `volatile` prevents JIT reordering optimisations; `static` state makes testing harder (global mutable state)

---

### 🧪 Thought Experiment

**SETUP:** A singleton configuration object is loaded once at startup and read by 100 threads.

**WHAT HAPPENS WITHOUT `volatile`/`final`:** The JIT compiler may cache the `instance` field in a CPU register. Thread B starts before Thread A's write completes. Thread B reads a partially constructed object - fields appear null or zero even though Thread A set them. This is the classic double-checked locking bug.

**WHAT HAPPENS WITH `volatile` on `instance`:** The JVM inserts a write barrier after `instance = new Config()` and a read barrier before each `instance` read. Thread B either sees `null` or the fully constructed object - never a partial state.

**THE INSIGHT:** `volatile` is not about speed - it is about establishing a guarantee that a write by Thread A is visible to Thread B before Thread B reads the field. Without it, the JVM and CPU are free to reorder and cache at will.

---

### 🧠 Mental Model / Analogy

> Think of these five keywords as five different rules for a shared whiteboard in an office. `static` means the board belongs to the room, not any one person. `final` means the content is written in permanent marker. `volatile` means every update is instantly broadcast to everyone's phone. `synchronized` means only one person can approach the board at a time (door lock). `transient` means the board's content is not photographed for the archive.

- `static` → room's whiteboard, not any one person's notepad
- `final` → permanent marker: cannot be erased or overwritten
- `volatile` → instant broadcast notification on every change
- `synchronized` → physical door lock: one person inside at a time
- `transient` → excluded from the end-of-day archive

Where this analogy breaks down: `volatile` guarantees visibility but not atomicity - a single "broadcast" of a 64-bit `long` may still be two 32-bit operations on 32-bit JVMs.

---

### 📶 Gradual Depth - Four Levels

**Level 1 - What it is (anyone can understand):**
These five words tell Java how to treat a variable or method: is it shared? Can it change? Can multiple threads use it at the same time? Should it be saved to disk?

**Level 2 - How to use it (junior developer):**
Use `static` for constants and utility methods. Use `final` for fields that should never change after construction. Use `volatile` for single shared flags read by multiple threads. Use `synchronized` when multiple threads must mutate shared state atomically. Mark `transient` any field that should not be persisted (passwords, derived data, non-serialisable objects).

**Level 3 - How it works (mid-level engineer):**
`volatile` inserts CPU memory barriers: a StoreStore barrier before every write, a LoadLoad barrier before every read. This prevents hardware and compiler reordering around the field. `synchronized` uses the object's monitor (a mutex embedded in the object header). On enter, all cached values are invalidated (Load barrier); on exit, all writes are flushed (Store barrier). `final` fields in a constructor are guaranteed visible to other threads after the constructor completes, even without synchronisation.

**Level 4 - Why it was designed this way (senior/staff):**
The Java Memory Model (JMM, JSR 133 in Java 5) formalised the happens-before relationship. Before Java 5, `volatile` only guaranteed visibility, not ordering - broken double-checked locking was impossible to fix. JSR 133 strengthened `volatile` to also prevent reordering. `synchronized` was retained as the heavier, fully safe tool. `java.util.concurrent` (Doug Lea, Java 5) built higher-level primitives (`ReentrantLock`, `AtomicInteger`) on top of these JVM guarantees, offering better performance profiles for specific concurrency patterns.

---

### ⚙️ How It Works (Mechanism)

**Memory visibility model:**
```
┌────────────────────────────────────────────┐
│  Thread A CPU          Thread B CPU        │
│  ┌──────────┐          ┌──────────┐        │
│  │ L1 Cache │          │ L1 Cache │        │
│  └────┬─────┘          └────┬─────┘        │
│       │                     │              │
│  ┌────▼─────────────────────▼─────┐        │
│  │         Main Memory            │        │
│  │  volatile field: always here   │        │
│  └────────────────────────────────┘        │
│                                            │
│  Non-volatile: may stay in L1 cache        │
│  volatile: read/write bypass cache         │
└────────────────────────────────────────────┘
```

**`synchronized` monitor bytecode:**
```
monitorenter  ← acquire lock + memory barrier
  ... critical section ...
monitorexit   ← release lock + flush writes
```

**`static` initialisation order:**
```
ClassLoader loads MyClass
  → <clinit>() runs once
  → static fields initialised top-to-bottom
  → static { } blocks execute in order
  → class ready for use
```

---

### 🔄 The Complete Picture - End-to-End Flow

**NORMAL FLOW (double-checked locking with volatile):**
```
Thread A                 Thread B
  │                         │
  ├─ read instance          ├─ read instance
  │   ← YOU ARE HERE        │
  ├─ null → enter sync      ├─ null → block on lock
  ├─ re-check null          │
  ├─ new Singleton()        │
  ├─ volatile write         │
  │   (write barrier)       │
  ├─ exit sync              │
  │                         ├─ acquire lock
  │                         ├─ re-check → not null
  │                         └─ return existing
```

**FAILURE PATH:**
- `volatile` without `synchronized` on compound operations → race condition (read-check-write is not atomic)
- `synchronized` on different objects → no mutual exclusion (two different monitors)
- `static` mutable field accessed from multiple threads without synchronisation → data race

**WHAT CHANGES AT SCALE:**
- Replace `synchronized` methods with `ReentrantLock` for tryLock, timed lock, and fairness
- Replace single `volatile` counter with `AtomicLong` for atomic increment
- Replace `static` singletons with Spring-managed beans to improve testability and lifecycle management

---

### 💻 Code Example

**BAD - volatile misused for compound operation, static mutable state:**
```java
// BAD: volatile does not make compound op atomic
private volatile int count = 0;

public void increment() {
    count++; // read-modify-write: NOT atomic!
}

// BAD: static mutable state - global side effect
public class Registry {
    static List<String> items = new ArrayList<>();
}
```

**GOOD - correct usage of each keyword:**
```java
// GOOD: volatile for simple flag (single write, many reads)
private volatile boolean shutdown = false;

public void stop() { shutdown = true; }

public void run() {
    while (!shutdown) { process(); }
}

// GOOD: double-checked locking with volatile (Java 5+)
public class Config {
    private static volatile Config instance;

    public static Config getInstance() {
        if (instance == null) {
            synchronized (Config.class) {
                if (instance == null) {
                    instance = new Config();
                }
            }
        }
        return instance;
    }
}

// GOOD: final for immutable value object
public final class Money {
    private final long amount;
    private final String currency;

    public Money(long amount, String currency) {
        this.amount = amount;
        this.currency = currency;
    }
    // no setters - immutable after construction
}

// GOOD: transient to exclude sensitive field
public class User implements Serializable {
    private static final long serialVersionUID = 1L;
    private String username;
    private transient String passwordHash;
    private transient Connection dbConn;
}

// GOOD: AtomicInteger over volatile for counter
private final AtomicInteger count = new AtomicInteger();
public void increment() { count.incrementAndGet(); }
```

---

### ⚖️ Comparison Table

| Keyword | Scope | JVM Mechanism | Thread Safety | Use Case |
|---|---|---|---|---|
| `static` | Field, method, block | Class area, `<clinit>` | No (unless combined with others) | Shared constants, utility methods |
| `final` (field) | Field | Constructor barrier | Yes (immutable after construction) | Immutable value objects |
| `final` (class/method) | Class, method | Inlining hint to JIT | N/A | Prevent subclassing/overriding |
| `volatile` | Field | Memory barrier | Visibility only (not atomicity) | Single-writer flags, DCL pattern |
| `synchronized` | Method, block | `monitorenter`/`monitorexit` | Full (visibility + atomicity) | Compound operations, critical sections |
| `transient` | Field | ObjectOutputStream skip | N/A | Exclude from serialisation |

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| `volatile` makes operations atomic | `volatile` guarantees visibility only; `count++` on a `volatile int` is still a non-atomic read-modify-write |
| `synchronized` is always slow | Modern JVMs use biased locking and lock elision - an uncontended `synchronized` block is often near-zero overhead |
| `final` class means its fields are immutable | `final` on a class prevents subclassing; the class's own fields can still be mutable unless also declared `final` |
| `static final` is always a compile-time constant | Only for primitives and `String`; `static final List<>` is a constant reference to a mutable list |
| `transient` prevents all serialisation | Only prevents Java's default serialisation; custom `writeObject()` implementations can still serialise transient fields |

---

### 🚨 Failure Modes & Diagnosis

**Mode 1: Race condition on volatile compound operation**

**Symptom:** Counter values are wrong under load - missing increments, negative values, or values below expected minimum. Bug is intermittent and never reproduces in single-threaded tests.

**Root Cause:** `volatile int count; count++` is three operations: read, increment, write. Two threads can both read the same value and both write back, losing one increment.

**Diagnostic:**
```bash
# Use ThreadSanitizer (Java agent or native)
# Or instrument with jcstress (OpenJDK tool)
java -jar jcstress.jar -t VolatileCounterTest
# Expected output: "ACCEPTABLE" or "FORBIDDEN" results
```

**Fix:**
```java
// BAD: volatile for counter
private volatile int count = 0;
public void inc() { count++; } // race!

// GOOD: AtomicInteger
private final AtomicInteger count =
    new AtomicInteger(0);
public void inc() { count.incrementAndGet(); }
```

**Prevention:** Never use `volatile` for read-modify-write operations; use `Atomic*` classes or `synchronized`.

---

**Mode 2: Broken double-checked locking (pre-Java 5 pattern)**

**Symptom:** Singleton returns partially initialised object - fields are null or zero even though the constructor set them. Occurs rarely, typically under high startup concurrency.

**Root Cause:** Without `volatile`, the JIT may reorder the store to `instance` before the stores to its fields. Thread B reads a non-null but incompletely constructed object.

**Diagnostic:**
```bash
# Enable PrintAssembly to inspect JIT output
java -XX:+UnlockDiagnosticVMOptions \
     -XX:+PrintAssembly -cp . MyApp 2>&1 \
     | grep -A5 "instance"
# Look for store reordering around object fields
```

**Fix:**
```java
// BAD: missing volatile - broken DCL
private static Config instance; // not volatile!

// GOOD: volatile on the instance field
private static volatile Config instance;
```

**Prevention:** Always use `volatile` in double-checked locking. Consider the enum singleton pattern (`enum Config { INSTANCE; }`) which the JVM guarantees is initialised exactly once.

---

**Mode 3: Synchronising on wrong object**

**Symptom:** Multiple threads enter a "protected" critical section simultaneously; data corruption occurs. `synchronized` block appears to be in place.

**Root Cause:** Two threads synchronise on different objects. Common causes: synchronising on a reassignable reference, or two methods each synchronise on `this` but on different instances.

**Diagnostic:**
```bash
jstack <pid> | grep -A10 "BLOCKED"
# If two threads are BLOCKED on different lock addresses,
# they are not contending the same monitor
```

**Fix:**
```java
// BAD: lock object is reassignable
private Object lock = new Object();
public void reset() { lock = new Object(); } // breaks!

// BAD: locking on boxed Integer (interning trap)
synchronized (Integer.valueOf(id)) { ... } // same value = same object!

// GOOD: private final dedicated lock
private final Object lock = new Object();
public void criticalSection() {
    synchronized (lock) { ... }
}
```

**Prevention:** Lock objects must be `private`, `final`, and never exposed externally.

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**
- Java Language - variable and method declarations
- Java Memory Model (JMM) - happens-before, reordering rules, visibility guarantees
- Thread (Java) - thread lifecycle, CPU caching, context switching

**Builds On This (learn these next):**
- Java Concurrency - `ReentrantLock`, `AtomicInteger`, `CountDownLatch`, `ConcurrentHashMap`
- Spring Core - Spring beans are singletons by default; `static` and `volatile` interact with DI lifecycle
- Serialization - `transient` and `serialVersionUID` govern what persists across JVM boundaries

**Alternatives / Comparisons:**
- `volatile` vs `synchronized` - choose volatile for single-flag visibility; synchronized for compound operations
- `synchronized` vs `ReentrantLock` - `ReentrantLock` offers try-lock, timed lock, and fairness
- `final` vs `@Immutable` - `final` is JVM-enforced; `@Immutable` is a documentation-only annotation

---

### 📌 Quick Reference Card

```
╔════════════════════════════════════════════════════╗
║ WHAT IT IS   │ 5 keywords: shared/fixed/visible/  ║
║              │ exclusive/hidden-from-serial        ║
║ PROBLEM      │ Race conditions, mutable constants, ║
║              │ leaked sensitive fields             ║
║ KEY INSIGHT  │ volatile=visibility; sync=atomicity ║
║ USE WHEN     │ static: shared state/utils          ║
║              │ final: immutable refs               ║
║              │ volatile: single-writer flag        ║
║              │ sync: compound ops                  ║
║ AVOID WHEN   │ volatile for counter; sync on wrong ║
║ TRADE-OFF    │ Safety vs contention overhead       ║
║ ONE-LINER    │ private static volatile T instance; ║
║ NEXT EXPLORE │ Java Memory Model, AtomicInteger    ║
╚════════════════════════════════════════════════════╝
```

---

### 🧠 Think About This Before We Continue

1. **(E - First Principles)** `volatile` establishes a happens-before relationship in the Java Memory Model. Given that modern CPUs have multi-level caches and out-of-order execution, what physical memory barrier instructions does the JVM emit for a `volatile` write, and why is that sufficient to guarantee visibility without locking?

2. **(C - Design Trade-off)** A `static` field in a Spring `@Service` bean is effectively global mutable state that bypasses Spring's dependency injection. Under what circumstances would you deliberately use a `static` field inside a Spring-managed bean, and how would you ensure it remains safe and testable?

3. **(D - Root Cause)** A production singleton initialised with double-checked locking is returning a corrupted object to one in every 10,000 requests. The code uses `volatile` on the instance field. What alternative causes - beyond missing `volatile` - could produce this symptom, and how would you diagnose each?
