---
layout: default
title: "Race Condition"
parent: "Java Concurrency"
nav_order: 346
permalink: /java-concurrency/race-condition/
---
# 346 — Race Condition

`#java` `#concurrency` `#threading` `#bugs` `#correctness`

⚡ TL;DR — A race condition is a bug where the program's outcome depends on the unpredictable relative timing of threads — caused by unsynchronized access to shared mutable state, producing intermittent and hard-to-reproduce failures.

| #346 | category: Java Concurrency
|:---|:---|:---|
| **Depends on:** | Thread, synchronized, volatile, Java Memory Model | |
| **Used by:** | Deadlock, Atomic Variables, Thread Safety | |

---

### 📘 Textbook Definition

A **race condition** occurs when a program's correctness depends on the interleaving order of operations from two or more threads accessing shared mutable state without adequate synchronization. Two classic patterns: **read-modify-write** (two threads each read a value, modify it, and write back — one write is lost) and **check-then-act** (one thread checks a condition and acts on it, but another thread changes the state between the check and the act).

---

### 🟢 Simple Definition (Easy)

Two threads race to the same finish line — whoever gets there first changes the result for everyone else. The bug only appears sometimes, depending on which thread "wins" the race. That unpredictability is what makes race conditions so dangerous: they pass tests, disappear under a debugger, and then corrupt data silently in production.

---

### 🔵 Simple Definition (Elaborated)

Race conditions are the most common concurrency bug. They don't always produce a crash — they silently corrupt data (a counter that shows the wrong value, a file that gets partially written, money that disappears from a bank account). They're incredibly hard to reproduce because they depend on thread scheduling timing, which varies with CPU load, JVM state, and hardware. The only reliable fix is to eliminate shared mutable state or protect it with proper synchronization — not to "hope the timing works out."

---

### 🔩 First Principles Explanation

**Pattern 1: Read-Modify-Write**

```
Shared: int balance = 100

Thread A: withdraw(50)     Thread B: deposit(200)
  1. READ  balance = 100    1. READ  balance = 100   (same stale read!)
  2. CALC  100 - 50 = 50    2. CALC  100 + 200 = 300
  3. WRITE balance = 50     3. WRITE balance = 300   (overwrites A's result!)

Expected: 100 - 50 + 200 = 250
Actual  : 300  (or 50, depending on who writes last)
Lost update: one operation's effect was completely overwritten
```

**Pattern 2: Check-Then-Act**

```
Shared: Map<String, Object> cache = new HashMap<>()

Thread A:                      Thread B:
  if (!cache.containsKey(k))     if (!cache.containsKey(k))
    ↑ both see "not present"       ↑ checked before A's put
    cache.put(k, compute())        cache.put(k, compute())
                               Both compute and put!
                               compute() called twice — may have side effects
                               Second put overwrites first silently
```

**Why it's hard to detect:**

```
In a debugger: adding breakpoints changes thread scheduling → race disappears
In tests    : deterministic single-thread test never hits the interleaving
In production: higher load → more threads → race manifests under stress

The "Heisenbug" property:
   Observing the bug (adding logging/breakpoints) changes its timing
   → hard to reproduce in isolation → blamed on "flakiness"
```

---

### ❓ Why Does This Exist — Why Before What

```
Root cause chain:
  1. Multi-core CPUs run threads truly in parallel (not just concurrent)
  2. Java Memory Model allows caching and reordering for performance
  3. Compound operations (read-modify-write) are NOT atomic by default
  4. Developer assumes operations are atomic when they're not

Real world consequences:
  Banking: lost deposits/withdrawals
  Inventory: overselling (check stock → order → stock goes to zero before order completes)
  Singleton: two instances created (both threads see uninitialized)
  Counter: request count under-reported
  Collection: ConcurrentModificationException or data corruption in HashMap
```

---

### 🧠 Mental Model / Analogy

> Two people editing the same Google Doc — but offline. Person A downloads it (READ), edits it (MODIFY), uploads it (WRITE). Person B downloads the SAME original version, makes different edits, uploads it. Person B's upload silently overwrites Person A's changes. If they had used real-time collaboration (synchronized / lock), both edits would merge correctly. Race condition = last-write-wins on stale data.

---

### ⚙️ How It Works — Solutions

```
Prevention strategy 1: Synchronization
  synchronized (lock) { balance += amount; }
  → Only one thread in the block → no interleaving

Prevention strategy 2: Atomic operations
  AtomicInteger.incrementAndGet()
  → CAS instruction: single hardware-level instruction
  → No interleaving possible at CPU level

Prevention strategy 3: Immutability
  Use final fields, immutable objects (String, record, BigDecimal)
  → No shared mutable state → no race possible

Prevention strategy 4: Thread confinement
  Each thread gets its own copy (ThreadLocal)
  → Objects never shared → no race possible

Prevention strategy 5: Lock-free concurrent collections
  ConcurrentHashMap, CopyOnWriteArrayList, BlockingQueue
  → Thread-safe by design → use instead of HashMap + synchronized
```

---

### 🔄 How It Connects

```
Race Condition
  │
  ├─ Caused by ──→ Shared mutable state + no synchronization
  ├─ Fixed by  ──→ synchronized / volatile / Atomic / immutability
  ├─ Detected  ──→ Race condition detectors (ThreadSanitizer for C++,
  │                 Java: Helgrind/DRD via JNI, or review)
  ├─ Related   ──→ Deadlock (over-synchronization), Data Race (JMM term)
  └─ Data Race ──→ specific JMM term: unsynchronized access where at
                    least one is a write → undefined behavior in JMM
```

---

### 💻 Code Example

```java
// Classic race condition: lost update on counter
public class UnsafeCounter {
    private int count = 0;

    public void increment() {
        count++;  // ❌ not atomic: read-modify-write in 3 steps
    }

    public int get() { return count; }
}

// Demonstrate the bug:
UnsafeCounter counter = new UnsafeCounter();
ExecutorService pool = Executors.newFixedThreadPool(10);
for (int i = 0; i < 1000; i++) {
    pool.submit(counter::increment);
}
pool.shutdown();
pool.awaitTermination(5, TimeUnit.SECONDS);
System.out.println(counter.get()); // Expected 1000, actual: 950ish (varies!)
```

```java
// Fix 1: synchronized
public class SynchronizedCounter {
    private int count = 0;
    public synchronized void increment() { count++; }
    public synchronized int get()        { return count; }
}

// Fix 2: AtomicInteger (lock-free, preferred)
public class AtomicCounter {
    private final AtomicInteger count = new AtomicInteger(0);
    public void increment() { count.incrementAndGet(); }
    public int  get()       { return count.get(); }
}
```

```java
// Check-then-act race: singleton without proper sync
public class BrokenSingleton {
    private static BrokenSingleton instance;

    public static BrokenSingleton getInstance() {
        if (instance == null) {        // Thread A: sees null
                                       // Thread B: also sees null (before A's write)
            instance = new BrokenSingleton();  // Both create instances!
        }
        return instance;               // Different objects returned to different callers
    }
}

// Fix: synchronized + volatile (double-checked locking)
public class SafeSingleton {
    private static volatile SafeSingleton instance;
    public static SafeSingleton getInstance() {
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

```java
// Race condition in collections: HashMap is NOT thread-safe
Map<String, Integer> map = new HashMap<>();
// Two threads inserting simultaneously can cause infinite loop (Java 7)
// or data loss (Java 8+) due to internal structural modification

// Fix: use thread-safe collection
Map<String, Integer> safeMap = new ConcurrentHashMap<>();
// or Collections.synchronizedMap(new HashMap<>()) for full sync (lower perf)
```

---

### ⚠️ Common Misconceptions

| ❌ Wrong Belief | ✅ Correct Reality |
|---|---|
| Race conditions always cause crashes | They usually cause silent data corruption — no exception thrown |
| Passing tests means no race condition | Tests are often single-threaded or deterministic; races hide in production load |
| `volatile` prevents all race conditions | volatile prevents visibility races but not compound operation races (i++) |
| A `synchronized` read with unsynchronized write is safe | BOTH read AND write must use the same lock — partial sync is not safe |
| Race conditions are rare in Java | They're extremely common; any shared mutable state without synchronization is at risk |

---

### 🔥 Pitfalls in Production

**Pitfall 1: Synchronizing only the write, not the read**

```java
private int count = 0;

public synchronized void increment() { count++; }  // synced
public int get() { return count; }  // ❌ NOT synced — may return stale value

// Fix: synchronize both, or use AtomicInteger
public synchronized int get() { return count; }
```

**Pitfall 2: Race condition in lazy initialization**

```java
// Service is expensive to create — create only when needed
private ExpensiveService service;

public ExpensiveService getService() {
    if (service == null) {          // Thread A and B both see null
        service = new ExpensiveService();  // both create it!
    }
    return service;
}
// Fix: double-checked locking with volatile, or Holder idiom

// Holder idiom (simplest thread-safe lazy init):
private static class ServiceHolder {
    static final ExpensiveService INSTANCE = new ExpensiveService();
}
public static ExpensiveService getService() { return ServiceHolder.INSTANCE; }
```

**Pitfall 3: Iterating over a collection modified by another thread**

```java
List<String> list = new ArrayList<>();
// Thread A iterates, Thread B adds → ConcurrentModificationException or skipped elements
for (String s : list) { ... }  // ❌

// Fix: CopyOnWriteArrayList (reads iterate snapshot, writes copy whole list)
List<String> safe = new CopyOnWriteArrayList<>();
// Or: synchronize on the list for the entire iteration
synchronized (list) { for (String s : list) { ... } }
```

---

### 🔗 Related Keywords

- **[synchronized](./069 — synchronized.md)** — prevents race conditions via mutual exclusion
- **[volatile](./070 — volatile.md)** — prevents visibility races for single fields
- **[Atomic Variables](./077 — Atomic Variables.md)** — lock-free atomic compound ops
- **[Deadlock](./071 — Deadlock.md)** — the opposite hazard (over-synchronization)
- **[ThreadLocal](./073 — ThreadLocal.md)** — eliminate sharing via thread confinement
- **ConcurrentHashMap** — thread-safe map without race conditions

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────────┐
│ KEY IDEA     │ Program outcome depends on thread timing —    │
│              │ shared mutable state + no sync = data corruption│
├──────────────┼───────────────────────────────────────────────┤
│ USE WHEN     │ Diagnosing: intermittent wrong values, silent  │
│              │ lost updates, occasional NPEs under load      │
├──────────────┼───────────────────────────────────────────────┤
│ AVOID WHEN   │ Prevent: immutable objects, thread confinement,│
│              │ synchronized, AtomicInteger, concurrent colls  │
├──────────────┼───────────────────────────────────────────────┤
│ ONE-LINER    │ "If two threads can see AND change the same   │
│              │  data at the same time — you have a race"     │
├──────────────┼───────────────────────────────────────────────┤
│ NEXT EXPLORE │ synchronized → volatile → Atomic Variables →  │
│              │ Immutability → ConcurrentHashMap             │
└──────────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** Two threads each call `map.put(key, value)` on a `HashMap` with DIFFERENT keys at the same time. Can a race condition still occur? What can go wrong internally even when the keys don't overlap?

**Q2.** You add logging to a method suspected of racing: `System.out.println("Before: " + count)` before the increment and `System.out.println("After: " + count)` after. You run it again and the race disappears. Why? (This is the Heisenbug effect — explain the mechanism.)

**Q3.** Is a read-only `HashMap` that is NEVER modified after publication shared between threads safe to access without synchronization? What condition must be met for the initial publication to be safe visibility-wise?

