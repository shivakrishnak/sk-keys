---
layout: default
title: "Thread Safety Patterns"
parent: "Java Concurrency"
nav_order: 102
permalink: /java-concurrency/thread-safety-patterns/
number: "102"
category: Java Concurrency
difficulty: ★★★
depends_on: synchronized, volatile, Immutability, ThreadLocal, ConcurrentHashMap
used_by: All Concurrent Code, API Design, Library Design
tags: #java, #concurrency, #patterns, #thread-safety, #design
---

# 102 — Thread Safety Patterns

`#java` `#concurrency` `#patterns` `#thread-safety` `#design`

⚡ TL;DR — Thread safety is achieved through six complementary strategies: immutability, confinement, synchronisation, lock-free operations, concurrent collections, and safe publication — choosing the right strategy for each data access pattern eliminates races without sacrificing performance.

| #102 | Category: Java Concurrency | Difficulty: ★★★ |
|:---|:---|:---|
| **Depends on:** | synchronized, volatile, Immutability, ThreadLocal, ConcurrentHashMap | |
| **Used by:** | All Concurrent Code, API Design, Library Design | |

---

### 📘 Textbook Definition

Thread safety is the property of a class or operation that guarantees correct behaviour when accessed from multiple threads simultaneously, without requiring external synchronisation. The principal strategies to achieve thread safety: (1) **Immutability** — objects cannot change state; (2) **Thread confinement** — state accessible to only one thread; (3) **Synchronisation** — explicit mutual exclusion; (4) **Lock-free operations** — CAS-based atomics; (5) **Thread-safe delegating** — composing immutable + thread-safe components; (6) **Safe publication** — ensuring written objects are fully visible before any reader sees them.

---

### 🟢 Simple Definition (Easy)

Six tools for making code safe from concurrent bugs:
1. **Immutability**: can't change = can't race
2. **Confinement**: one thread owns it = no sharing
3. **Locking**: take turns = no collision
4. **Atomics**: hardware-level safe operations
5. **Concurrent collections**: thread-safe by design
6. **Safe publication**: ensure object is complete before sharing

---

### 🔵 Simple Definition (Elaborated)

Most concurrency bugs come from shared mutable state. The single most effective strategy is eliminating the "mutable" or the "shared" part. Immutable objects (records, String, BigDecimal) solve the mutable part — no synchronisation ever needed. Thread confinement (ThreadLocal, stack-confined locals) solves the shared part. Only when you truly need shared mutable state do you reach for locking or atomics.

---

### 🔩 First Principles Explanation

```
Strategy 1: IMMUTABILITY
  All fields final; state set in constructor only
  No setters; any "change" creates a new object
  Examples: String, BigDecimal, LocalDate, Record classes
  Benefit: share freely across threads — no synchronisation ever needed
  Cost: extra object allocations

Strategy 2: THREAD CONFINEMENT
  Stack confinement: local variables → never shared (stack is per-thread)
  ThreadLocal: per-thread copy; never cross-thread visible
  Object confinement: object created + used within single thread
  Benefit: no synchronisation needed; no sharing at all
  Cost: can't share work results across threads without handoff

Strategy 3: SYNCHRONISATION
  synchronized, ReentrantLock, ReadWriteLock
  One thread at a time in critical section
  Benefit: any code can be made safe; well-understood
  Cost: blocking; contention; deadlock risk; reduced throughput

Strategy 4: LOCK-FREE / ATOMIC
  AtomicInteger, ConcurrentHashMap, CAS operations
  No mutex; hardware-level atomicity
  Benefit: non-blocking; high throughput; no deadlock
  Cost: only for simple state; complex invariants still need locks

Strategy 5: CONCURRENT COLLECTIONS
  ConcurrentHashMap, CopyOnWriteArrayList, BlockingQueue
  Thread-safe by design; avoid reinventing
  Benefit: battle-tested, efficient, composable
  Cost: some trade-offs (COW write cost, eventual size())

Strategy 6: SAFE PUBLICATION
  Publish objects through: volatile, static initialiser, synchronized, final
  Ensures all fields written in constructor are visible to readers
  Benefit: correct visibility without synchronising every access
  Cost: requires discipline in choosing publication mechanism
```

---

### 🧠 Mental Model / Analogy

> Building a concurrent system is like managing a shared office. Immutability = laminated read-only signs (nobody can change them). Confinement = each person has their own desk (no sharing). Locking = one-at-a-time access to the shared printer. Atomics = a ticket dispenser that gives unique numbers to anyone instantly. Concurrent collections = the filing room with built-in access control. Safe publication = the announcement board where you only post completed documents.

---

### ⚙️ How It Works — Decision Framework

```
Question for every shared field/object:

1. Does it need to change after construction?
   NO → make it IMMUTABLE (final + defensive copy if needed)
   YES → continue...

2. Can it be accessed by only ONE thread?
   YES → use THREAD CONFINEMENT (stack local, ThreadLocal, ownership transfer)
   NO → continue...

3. Is it a single value (counter, flag, reference)?
   YES → use ATOMIC VARIABLE (AtomicInteger, AtomicReference)
   NO → continue...

4. Is it a standard collection or map?
   YES → use CONCURRENT COLLECTION (ConcurrentHashMap, BlockingQueue)
   NO → continue...

5. Need complex multi-step invariant?
   YES → use SYNCHRONIZATION (synchronized, ReentrantLock)
   → minimise scope; document lock ordering; prevent deadlock

6. How is the object published from constructor to consumers?
   → Use SAFE PUBLICATION: final, volatile, static, or synchronized
```

---

### 🔄 How It Connects

```
Thread Safety Strategies
  │
  ├─ Immutability    → Record, String, Collections.unmodifiable*
  ├─ Confinement     → ThreadLocal, local variables, stack allocation
  ├─ Synchronisation → synchronized, ReentrantLock, ReadWriteLock
  ├─ Lock-free       → AtomicInteger, CAS, LongAdder
  ├─ Concurrent Coll → ConcurrentHashMap, CopyOnWriteArrayList, BlockingQueue
  └─ Safe Publication→ volatile, static init, final, synchronized publication
```

---

### 💻 Code Example

```java
// Strategy 1: Immutability — Java 16+ Record
public record Money(BigDecimal amount, Currency currency) {
    // All fields implicitly final; no setters; safe to share freely
    public Money add(Money other) {
        if (!this.currency.equals(other.currency)) throw new IllegalArgumentException();
        return new Money(this.amount.add(other.amount), this.currency);
        // Returns NEW Money — original unchanged
    }
}
// Share Money instances freely across threads — zero synchronisation needed
```

```java
// Strategy 2: Thread Confinement — ThreadLocal
private static final ThreadLocal<SimpleDateFormat> DateFormat =
    ThreadLocal.withInitial(() -> new SimpleDateFormat("yyyy-MM-dd"));

public String formatDate(Date d) {
    return DateFormat.get().format(d);  // each thread has its own SDF instance
}
```

```java
// Strategy 6: Safe Publication — static initialiser (classloader-safe)
public class Singleton {
    private static class Holder {
        static final Singleton INSTANCE = new Singleton(); // init-on-demand
    }
    public static Singleton getInstance() { return Holder.INSTANCE; }
}
// Class Holder not loaded until getInstance() called
// Static initialiser guaranteed by classloader to run exactly once
// All fields of INSTANCE guaranteed visible (classloader hb guarantee)
```

```java
// Anti-pattern: Unsafe publication
class UnsafePublication {
    private int x, y;

    UnsafePublication(int x, int y) { this.x = x; this.y = y; }

    // BUG: publishing reference before construction is complete
    public static UnsafePublication create() {
        UnsafePublication p = new UnsafePublication(1, 2);
        // If this reference is published via non-volatile/non-synchronized field,
        // another thread may see p != null but x=0, y=0 (constructor writes not yet visible)
        return p;
    }
}

// Fix: publish via volatile, synchronized, or final fields
class SafePublication {
    public final int x;  // final guarantees visibility of value after construction
    public final int y;
    SafePublication(int x, int y) { this.x = x; this.y = y; }
}
```

---

### ⚠️ Common Misconceptions

| ❌ Wrong Belief | ✅ Correct Reality |
|---|---|
| `synchronized` everywhere makes code thread-safe | Over-synchronisation leads to deadlock and poor performance; choose the right strategy |
| Immutability requires final everything | `final` fields are the mechanism; the PATTERN is: no mutation after construction |
| Thread-safe means serialised | Only synchronisation serialises; immutability + confinement allow full parallelism |
| Local variables are always safe | True for primitives; object REFERENCES on the stack are safe, but the objects they POINT TO are shared if the reference is shared |

---

### 🔥 Pitfalls in Production

**Pitfall: Partially thread-safe class — some methods synchronised, some not**

```java
public class Counter {
    private int count = 0;
    public synchronized void increment() { count++; }
    public int get() { return count; }    // ❌ unsynchronised read → stale value
}
// Fix: synchronise ALL accesses to shared mutable state with the SAME lock
public synchronized int get() { return count; }  // ✅
```

**Pitfall: Escaping `this` in constructor — unsafe publication**

```java
public class EventListener {
    EventListener() {
        EventBus.register(this);  // ❌ 'this' escapes before constructor finishes
        // Another thread may call our methods before all fields are initialised
    }
}
// Fix: factory method — register AFTER construction completes
static EventListener create() {
    var l = new EventListener();
    EventBus.register(l);  // ✅ construction complete
    return l;
}
```

---

### 🔗 Related Keywords

- **[Race Condition](./072 — Race Condition.md)** — what all strategies prevent
- **[synchronized](./069 — synchronized.md)** — strategy 3
- **[volatile](./070 — volatile.md)** — safe publication mechanism
- **[ThreadLocal](./073 — ThreadLocal.md)** — thread confinement
- **[ConcurrentHashMap](./082 — ConcurrentHashMap.md)** — strategy 5
- **[Atomic Variables](./077 — Atomic Variables.md)** — strategy 4
- **Java Memory Model** — the formal foundation for safe publication

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────────┐
│ KEY IDEA     │ 6 strategies: immutable, confined, sync,      │
│              │ lock-free, concurrent collections, safe pub   │
├──────────────┼───────────────────────────────────────────────┤
│ DECISION     │ No change? → immutable                        │
│              │ One thread? → confine                         │
│              │ Single value? → atomic                        │
│              │ Collection? → concurrent                      │
│              │ Complex invariant? → synchronise             │
├──────────────┼───────────────────────────────────────────────┤
│ AVOID WHEN   │ Never synchronise everywhere blindly; prefer  │
│              │ immutability and confinement first            │
├──────────────┼───────────────────────────────────────────────┤
│ ONE-LINER    │ "Don't share, or don't mutate —               │
│              │  only if you must do both, then synchronise"  │
├──────────────┼───────────────────────────────────────────────┤
│ NEXT EXPLORE │ Safe Publication → JMM → Immutability →       │
│              │ Java Concurrency in Practice (Goetz et al.)   │
└──────────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** A class has a mutable `List<String>` field. You want it to be thread-safe. Walk through the decision framework: should you use immutability, confinement, synchronisation, or a concurrent collection? What factors determine which one you choose?

**Q2.** "Safe publication" is required even for immutable objects in some cases. When would an immutable object require safe publication? (Hint: think about `final` field semantics and the JMM.)

**Q3.** The "this escaping" constructor anti-pattern is a safe publication violation. Why is it dangerous even if the object appears fully initialised by the time another thread uses it? What happens if the other thread caches a reference obtained during construction?

