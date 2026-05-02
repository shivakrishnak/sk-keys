---
layout: default
title: "synchronized"
parent: "Java Concurrency"
nav_order: 338
permalink: /java-concurrency/synchronized/
number: "0338"
category: Java Concurrency
difficulty: ★★☆
depends_on: Thread (Java), Thread Lifecycle, Memory Barrier, Happens-Before
used_by: wait / notify / notifyAll, Thread States, ReentrantLock
related: volatile, ReentrantLock, Memory Barrier
tags:
  - java
  - concurrency
  - synchronization
  - intermediate
  - thread-safety
---

# 0338 — synchronized

⚡ TL;DR — `synchronized` ensures mutual exclusion (only one thread executes a block at a time) AND establishes a happens-before relationship, making all writes by the lock-releasing thread visible to the next thread that acquires the same lock.

| #0338 | Category: Java Concurrency | Difficulty: ★★☆ |
|:---|:---|:---|
| **Depends on:** | Thread (Java), Thread Lifecycle, Memory Barrier, Happens-Before | |
| **Used by:** | wait / notify / notifyAll, Thread States, ReentrantLock | |
| **Related:** | volatile, ReentrantLock, Memory Barrier | |

---

### 🔥 The Problem This Solves

WORLD WITHOUT IT:
Two threads modify a shared counter simultaneously. Thread T1: reads `count=5`, adds 1, writes `count=6`. Thread T2: simultaneously reads `count=5`, adds 1, writes `count=6`. Both incremented, but count went from 5 to 6, not 7. This is a race condition — the check-then-act sequence is not atomic. Without mutual exclusion, any read-modify-write operation on shared state is a potential race condition.

THE BREAKING POINT:
A banking service processes concurrent withdrawals. Two threads both pass the "sufficient funds" check simultaneously, then both deduct. Result: account balance goes negative. Funds are lost or duplicated. This is not a corner case — all concurrent systems face this problem with ANY shared mutable state.

THE INVENTION MOMENT:
This is exactly why **`synchronized`** was created — to enforce that only one thread at a time executes a critical section, and to guarantee that all changes made inside the critical section are visible to the next thread entering the same section.

---

### 📘 Textbook Definition

**`synchronized`** is a Java keyword that uses an intrinsic monitor lock (or "mutex") associated with every Java object to enforce mutual exclusion. When a thread enters a `synchronized` block or method, it acquires the monitor lock of the specified object (or `this` for instance methods, or the class object for static methods). Other threads attempting to acquire the same lock are put in BLOCKED state until the lock is released. `synchronized` also establishes a **happens-before** relationship: all actions in the releasing thread prior to unlocking are visible to the thread that subsequently acquires the same lock.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
`synchronized` means "only one thread at a time, and whatever the previous thread did is visible to the next."

**One analogy:**
> A restaurant bathroom with one key. Only one person has the key (lock) at a time. The next person waits outside (BLOCKED). When the previous person leaves and hangs back the key (releases lock), the waiting person can enter and see the bathroom in the state it was left (happens-before guarantee: all state changes are visible).

**One insight:**
`synchronized` does TWO things: (1) mutual exclusion — one thread at a time; (2) memory visibility — the next thread sees all writes from the previous thread in the critical section. Both are required for correct concurrent programs. Using `volatile` alone provides only visibility (no mutual exclusion); `synchronized` provides both.

---

### 🔩 First Principles Explanation

CORE INVARIANTS:
1. A monitor lock is associated with every Java object — `synchronized(obj)` uses `obj`'s lock.
2. Only one thread holds the lock at a time — all others attempting to acquire the SAME lock are BLOCKED.
3. `synchronized` is reentrant — a thread holding a lock can enter another `synchronized` block on the SAME lock without deadlocking.
4. Acquiring and releasing a lock inserts a memory barrier — all writes visible before release are visible after the next acquisition.

DERIVED DESIGN:
Given invariant 3 (reentrancy): a `synchronized` method can call another `synchronized` method on the same `this` without deadlock. The JVM counts reentrant acquisitions.

Given invariant 4: without the memory barrier, a CPU could cache values in registers and the "next thread" might see stale data even after acquiring the lock. `synchronized` forces a full flush/sync of the CPU cache at release and a reload at acquisition.

```
┌────────────────────────────────────────────────┐
│     synchronized Block Execution              │
│                                                │
│  Thread T1:                  Thread T2:        │
│  synchronized(lock) {        synchronized(lock){│
│    // critical section         // BLOCKED here │
│    count++;                                    │
│    // write barrier            // waits...     │
│  } // release lock                            │
│                              // T2 UNBLOCKED  │
│                              // load barrier  │
│                              count++;           │
│                              // sees T1's write │
│                              }                 │
└────────────────────────────────────────────────┘
```

THE TRADE-OFFS:
Gain: Mutual exclusion + memory visibility in one construct; simple model; JVM-native (no library needed); reentrancy.
Cost: Coarse granularity (whole method or block); no timeout (can block indefinitely); no ability to interrupt a waiting thread; no distinguish between read and write (readers block each other unnecessarily); can cause deadlock with improper lock ordering.

---

### 🧪 Thought Experiment

SETUP:
A shared counter incremented by 1,000 threads, 1,000 times each. Expected: 1,000,000.

WITHOUT synchronized:
```java
private int count = 0;
void increment() { count++; } // NOT atomic!
// count++ = read-modify-write in 3 JVM operations
// Result: ~800,000 (lost increments from race)
// Non-deterministic — varies per run
```

WITH synchronized:
```java
private int count = 0;
synchronized void increment() { count++; }
// Only one thread in method at a time → no lost increments
// Result: always exactly 1,000,000
```

ALTERNATIVE (AtomicInteger):
```java
private AtomicInteger count = new AtomicInteger(0);
void increment() { count.incrementAndGet(); }
// Uses CAS (hardware atomic) — faster than synchronized for single ops
```

THE INSIGHT:
`synchronized` guarantees correctness at the cost of contention overhead. `AtomicInteger` achieves the same correctness with better performance for simple operations. For complex multi-step operations, `synchronized` is still required.

---

### 🧠 Mental Model / Analogy

> `synchronized` is like a single-toilet office bathroom with a key:
1. First person takes the key and enters (acquires lock).
2. Second person finds no key — waits outside (BLOCKED).
3. First person finishes, replaces the key (releases lock, write barrier).
4. Second person takes the key (acquires lock, read barrier) and enters — sees the bathroom as left.

"Taking the key" → acquiring the monitor lock.
"Waiting outside" → BLOCKED state.
"Replacing the key" → releasing with write barrier.
"Seeing bathroom state" → happens-before: reads see previous writes.

Where this analogy breaks down: The bathroom key analogy doesn't convey reentranacy. A synchronized block allows the same thread to re-enter — as if the person already inside can open another door within the same bathroom (reentrant).

---

### 📶 Gradual Depth — Four Levels

**Level 1:** `synchronized` means "only one thread can run this code at a time."

**Level 2 — How to use it:** Three forms: `synchronized(object) { ... }` — explicit object lock; `synchronized void method()` — locks `this`; `static synchronized void method()` — locks the class. Use the minimal locking scope (small blocks, not whole methods) to reduce contention.

**Level 3 — How it works:** Each Java object has a monitor. In HotSpot JVM, monitors start as "biased" (single-thread optimised), become "thin locks" on first contention, then "fat locks" (inflated to OS mutex) on sustained contention. Monitor entry uses `monitorenter` bytecode; exit uses `monitorexit`. The JVM inserts a hardware memory barrier (e.g., `mfence` on x86) at lock release and acquisition.

**Level 4 — Why still use it?** `synchronized` has the advantage of automatic lock release on exceptions (the JVM always calls `monitorexit` even if an exception is thrown) and simplicity. `ReentrantLock` provides more control (timed try, interruptible, condition variables) at the cost of manual `try/finally` lock release. For simple atomic operations, prefer `Atomic*` classes. For complex state transitions, `synchronized` remains the clearest option.

---

### ⚙️ How It Works (Mechanism)

**Three synchronized forms:**
```java
class BankAccount {
    private double balance = 1000.0;

    // 1. Synchronized method: locks `this`
    public synchronized boolean withdraw(double amount) {
        if (balance >= amount) {
            balance -= amount;
            return true;
        }
        return false;
    }

    // 2. Synchronized block: explicit lock
    private final Object lock = new Object();
    public boolean deposit(double amount) {
        synchronized (lock) { // finer control than 'this'
            balance += amount;
            return true;
        }
    }

    // 3. Static synchronized: locks the class object
    private static int openAccounts = 0;
    public static synchronized void register() {
        openAccounts++;
    }
}
```

**Reentrancy example:**
```java
class Counter {
    private int count = 0;

    public synchronized void incrementTwice() {
        increment(); // calls synchronized method on same this
        increment(); // reentrant — not deadlocked
    }

    public synchronized void increment() {
        count++; // same lock as incrementTwice — reentrant OK
    }
}
```

**Lock scope best practice:**
```java
// BAD: whole method locked — readers block each other
public synchronized List<Order> getOrders() {
    return new ArrayList<>(orders); // read-only
}

// GOOD: lock only the mutation; reads can use separate lock
private final ReadWriteLock rwLock = new ReentrantReadWriteLock();
public List<Order> getOrders() {
    rwLock.readLock().lock();
    try { return new ArrayList<>(orders); }
    finally { rwLock.readLock().unlock(); }
}
```

---

### 🔄 The Complete Picture — End-to-End Flow

NORMAL FLOW:
```
[Thread T1: enters synchronized(sharedObj)]
    → [JVM: monitorenter — acquires monitor]  ← YOU ARE HERE
    → [T2: attempts monitorenter — BLOCKED]
    → [T1: modifies state atomically]
    → [T1: exits block — JVM: monitorexit]
    → [Write barrier: T1's writes flushed]
    → [T2: acquires monitor — UNBLOCKED]
    → [Read barrier: T2 sees T1's writes]
    → [T2: reads consistent state]
```

FAILURE PATH (deadlock):
```
[T1 holds lock A, tries to acquire lock B]
    → [T2 holds lock B, tries to acquire lock A]
    → [Both BLOCKED — circular dependency]
    → [DEADLOCK: never resolves]
    → [Fix: consistent lock ordering, or use tryLock]
```

WHAT CHANGES AT SCALE:
At high concurrency, `synchronized` on a single object becomes a bottleneck — all threads serialize through the critical section. Solutions: reduce lock scope (fine-grained locking), use `ReadWriteLock` for read-heavy workloads, use lock striping (ConcurrentHashMap approach), or use lock-free algorithms (`AtomicReference`, CAS).

---

### 💻 Code Example

Example 1 — Simple counter:
```java
public class SafeCounter {
    private int count = 0;

    public synchronized void increment() { count++; }
    public synchronized int get() { return count; }
}
```

Example 2 — Double-checked locking (Java 5+):
```java
public class Singleton {
    private volatile Singleton instance; // volatile required!

    public Singleton getInstance() {
        if (instance == null) {
            synchronized (this) {
                if (instance == null) {
                    instance = new Singleton(); // full init before visible
                }
            }
        }
        return instance;
    }
}
```

Example 3 — Explicit lock object (preferred over `this`):
```java
public class Cache<K, V> {
    private final Map<K, V> map = new HashMap<>();
    private final Object lock = new Object();

    public void put(K key, V value) {
        synchronized (lock) { map.put(key, value); }
    }
    public V get(K key) {
        synchronized (lock) { return map.get(key); }
    }
}
```

---

### ⚖️ Comparison Table

| Approach | Mutual Exclusion | Memory Visibility | Timeout | Interruptible | Best For |
|---|---|---|---|---|---|
| `synchronized` | Yes | Yes | No | No | Simple critical sections |
| `ReentrantLock` | Yes | Yes | Yes (tryLock) | Yes | Complex locking scenarios |
| `volatile` | No | Yes | N/A | N/A | Single-variable flags |
| `AtomicInteger` | Yes (CAS) | Yes | N/A | N/A | Counter/single-value ops |
| `ReadWriteLock` | Writers only | Yes | Yes | Yes | Read-heavy workloads |

How to choose: Use `synchronized` for simple critical sections. Use `ReentrantLock` when you need timeout, interruption, or multiple conditions. Use `volatile` for simple flags with no compound operations. Use `Atomic*` for single-variable atomic operations.

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| synchronized on different instances of the same class share a lock | Each object has its OWN monitor. `synchronized(this)` on two different instances = two different locks — NO mutual exclusion between them |
| synchronized provides only mutual exclusion, not visibility | `synchronized` provides BOTH. The memory barrier at lock release/acquisition ensures visibility of all writes in the critical section |
| `volatile` is a lighter version of `synchronized` | `volatile` provides visibility only — no mutual exclusion. `count++` on a volatile field is STILL a race condition (read-modify-write is not atomic). `synchronized` (or `AtomicInteger`) is required |
| nested synchronized blocks on different objects are reentrancy | Reentrancy is same-thread acquiring the SAME lock recursively. Acquiring a different object's lock in sequence is not reentrancy — it's nested locking (potential deadlock risk) |
| synchronized guarantees ordering between unrelated threads | `synchronized` guarantees happens-before ONLY between threads sharing the SAME lock. Two threads using different locks have no ordering guarantee relative to each other |

---

### 🚨 Failure Modes & Diagnosis

**Deadlock**

Symptom: Some threads BLOCKED indefinitely. Application hangs.

```bash
jstack <pid> | grep "DEADLOCK" -A20
# JVM auto-detects intrinsic lock deadlocks
```

Fix: Enforce consistent lock acquisition order. Use `ReentrantLock.tryLock(timeout)`.

---

**Lock Contention / Performance Degradation**

Symptom: CPU spikes but throughput low. Profiler shows threads queuing at synchronized.

```bash
# Async profiler lock profiling:
./asprof -e lock -d 30 <pid>
# Shows which locks are hottest, which threads wait
```

Fix: Reduce critical section scope. Use `ConcurrentHashMap`. Consider lock striping.

---

**Missed Visibility (using synchronized only for mutual exclusion)**

Symptom: Thread T2 reads stale value of a variable written by T1.

Root Cause: Developer assumed mutual exclusion was sufficient but the variable is read outside synchronized.

Fix: All reads AND writes of shared mutable state must be synchronized on the same lock (or use volatile for single variables with no compound operations).

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**
- `Thread (Java)` — synchronized is meaningless without threads; understanding threads is prerequisite
- `Memory Barrier` — synchronized's visibility guarantee is implemented via memory barriers
- `Happens-Before` — the formal specification of what visibility synchronized provides

**Builds On This (learn these next):**
- `volatile` — visibility-only analogue of synchronized for simple single-variable cases
- `ReentrantLock` — more powerful and flexible alternative to synchronized
- `wait / notify / notifyAll` — thread coordination mechanism that requires synchronized to work

**Alternatives / Comparisons:**
- `volatile` — lightweight visibility-only; no mutual exclusion
- `ReentrantLock` — full-featured alternative to synchronized with timeout and condition variables

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ WHAT IT IS   │ Intrinsic lock ensuring mutual exclusion  │
│              │ + memory visibility for critical sections │
├──────────────┼───────────────────────────────────────────┤
│ PROBLEM IT   │ Race conditions on shared mutable state   │
│ SOLVES       │ + stale reads between concurrently        │
│              │   executing threads                       │
├──────────────┼───────────────────────────────────────────┤
│ KEY INSIGHT  │ Does TWO things: only 1 thread at a time, │
│              │ AND makes writes visible across threads.  │
│              │ volatile does ONLY visibility, not both.  │
├──────────────┼───────────────────────────────────────────┤
│ USE WHEN     │ Multi-step read-modify-write operations   │
│              │ on shared mutable state                   │
├──────────────┼───────────────────────────────────────────┤
│ AVOID WHEN   │ Simple flags (volatile); read-heavy data  │
│              │ (ReadWriteLock); single atomic ops (Atomic)│
├──────────────┼───────────────────────────────────────────┤
│ TRADE-OFF    │ Correctness vs contention overhead;       │
│              │ simple vs flexible (use ReentrantLock)    │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "One thread at a time, and no stale reads"│
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ volatile → ReentrantLock → wait/notify →  │
│              │ ReadWriteLock                             │
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** Two developers debate: Developer A says a `HashMap` should be wrapped in `synchronized` on `this` for thread safety. Developer B says `ConcurrentHashMap` is always better. Construct a specific scenario where Developer A's approach is CORRECT and `ConcurrentHashMap` would give wrong results — specifically involving a compound operation (check-then-act on the map) — and then construct a different scenario where `ConcurrentHashMap`'s internal lock striping makes it dramatically outperform `synchronized HashMap` at a specific thread count threshold.

**Q2.** Java's `synchronized` is implemented with `monitorenter`/`monitorexit` bytecodes. HotSpot JVM optimises monitors through biased locking, thin locking, and lock inflation. Describe what happens at each stage as lock contention increases from zero to high: exactly what data structure change occurs in the object header (mark word) at each optimisation level, what the memory cost per object is at each level, and under what specific workload conditions HotSpot decides to "inflate" a thin lock to a full OS mutex (fat lock) — including the role of safepoints in this decision.

