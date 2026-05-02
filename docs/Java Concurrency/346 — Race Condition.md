---
layout: default
title: "Race Condition"
parent: "Java Concurrency"
nav_order: 346
permalink: /java-concurrency/race-condition/
number: "0346"
category: Java Concurrency
difficulty: ★★☆
depends_on: Thread (Java), synchronized, Java Memory Model (JMM)
used_by: synchronized, CAS (Compare-And-Swap), Atomic Classes
related: Deadlock Detection (Java), CAS (Compare-And-Swap), synchronized
tags:
  - java
  - concurrency
  - race-condition
  - intermediate
  - bugs
---

# 0346 — Race Condition

⚡ TL;DR — A race condition occurs when program behaviour depends on the relative timing of multiple threads accessing shared state — producing non-deterministic results that are correct by coincidence in testing but fail silently in production under load.

| #0346 | Category: Java Concurrency | Difficulty: ★★☆ |
|:---|:---|:---|
| **Depends on:** | Thread (Java), synchronized, Java Memory Model (JMM) | |
| **Used by:** | synchronized, CAS (Compare-And-Swap), Atomic Classes | |
| **Related:** | Deadlock Detection (Java), CAS (Compare-And-Swap), synchronized | |

### 🔥 The Problem This Solves

WORLD WITHOUT IT (understanding):
Race conditions are the most common and hardest-to-diagnose class of concurrent bugs. They produce non-deterministic failures — the program works correctly 99% of the time and fails mysteriously 1% of the time. Traditional debugging is nearly impossible (adding `println` statements changes timing and makes the bug disappear). Without understanding race conditions as a concept, developers cannot systematically identify, prevent, or fix them.

THE BREAKING POINT:
A race condition in a banking service causes intermittent over-drafting. Two concurrent withdrawal requests both pass "sufficient funds" check simultaneously, then both deduct. The account goes negative. The bug manifests only during high traffic when two withdrawals for the same account arrive within milliseconds. Testing with a single thread — no bug. Testing with two threads at normal load — rare. Bug only manifests under peak load with exact timing.

THE INVENTION MOMENT:
Understanding **race conditions** enables developers to: identify shared mutable state in concurrent code, recognize check-then-act patterns as inherently racy, apply appropriate synchronization mechanisms (`synchronized`, CAS, `AtomicInteger`), and write concurrent code that is correct by construction.

### 📘 Textbook Definition

A **Race Condition** is a software defect where the outcome of a computation depends on the timing or interleaving of multiple threads executing concurrently, such that different orderings produce different (and potentially incorrect) results. Formally in the JMM: a data race occurs when two threads access the same variable concurrently, at least one access is a write, and there is no happens-before ordering between the accesses. Race conditions typically manifest as: **check-then-act** patterns (read-check-write); **read-modify-write** patterns (counter increment); **lazy initialization** patterns (create-if-absent).

### ⏱️ Understand It in 30 Seconds

**One line:**
A race condition is a bug that only shows up when two threads hit the same code at exactly the wrong time.

**One analogy:**
> Two cooks making a sandwich. Cook A checks if there's cheese (check), finds there is (act). Cook B simultaneously checks for cheese (check), also finds there is. Cook A takes the last piece. Cook B tries to take cheese — it's gone. Both checked, but only one can take. The check-then-act sequence is not atomic.

**One insight:**
Race conditions are found at **compound non-atomic operations**. `count++` looks atomic but is read-modify-write (3 operations). `if (cache == null) cache = compute()` looks safe but is check-then-act (2 operations). Any time you have "read, then do something based on the read," with another thread possibly modifying between the read and the action, you have a potential race condition.

### 🔩 First Principles Explanation

CORE INVARIANTS:
1. Any shared mutable state accessed by multiple threads is a potential race condition.
2. A race condition requires at least one write — two concurrent reads are safe.
3. Race conditions are timing-dependent — always possible in theory, but only manifests when threads interleave at the exact wrong point.

THREE CANONICAL PATTERNS:
```
Pattern 1: Check-Then-Act
  T1: check(condition) → true
  T2: check(condition) → true [interleaves here]
  T1: act()  // takes the resource
  T2: act()  // resource GONE — act on stale check

Pattern 2: Read-Modify-Write
  T1: read(count=5) → count+1=6
  T2: read(count=5) → count+1=6 [interleaves]
  T1: write(count=6)  // lost T2's increment
  T2: write(count=6)  // should be 7

Pattern 3: Lazy Initialization

  T1: check(obj==null) → true
  T2: check(obj==null) → true [interleaves]
  T1: obj = new Obj()  // created
  T2: obj = new Obj()  // second creation! Previous lost
```

THE TRADE-OFFS:
Race conditions trade performance (no synchronization overhead) for correctness. The goal is not eliminating all sharing but ensuring all shared mutable state has proper HB guarantees.

### 🧪 Thought Experiment

SETUP:
10,000 threads each increment a shared counter once. Expected: 10,000.

```java
// Racy implementation:
int count = 0;
for (int i = 0; i < 10_000; i++) {
    new Thread(() -> count++).start(); // Race!
}
// Result: 7,843 (or any value < 10,000)

// Why? count++ = 3 operations:
// 1. READ: int temp = count (registers: 5)
//    [another thread reads count=5, increments to 6, writes 6]
// 2. ADD:  temp + 1 = 6
// 3. WRITE: count = 6 (writes 6 — overwrites the 6 written above)
// Lost increment: count goes from 5 to 6 twice instead of 5 to 7
```

THE INSIGHT:
`count++` "looks" atomic from the source code. At the bytecode level it's `getfield`, `iadd`, `putfield` — three separate JVM operations. Any interleaving between these is a race.

### 🧠 Mental Model / Analogy

> A race condition is like two people filling out the last form at a government office. Both check if the form is available (yes). Both start filling it out. Both turn it in — but only one can be processed. The other is invalid. The office didn't coordinate who could take the form — a race condition in form access.

"Checking if form is available" → reading shared state.
"Both taking the form" → both threads proceeding past a non-atomic check.
"Both turning in" → both modifying shared state.
"Only one valid" → one thread's work is lost/overwritten.

Where this analogy breaks down: In the form analogy, one form is invalid and caught. In code, the race condition often produces a silently wrong result with no indication of failure — a counter at 9,999 instead of 10,000 produces no exception.

### 📶 Gradual Depth — Four Levels

**Level 1:** A race condition is a bug caused by two threads doing things "at the same time" that interfere with each other on shared data.

**Level 2:** Identify race-prone patterns: `count++` on shared int, `if (x == null) x = create()`, and `if (balance >= amount) debit(amount)`. Fix with: `AtomicInteger`, `ConcurrentHashMap.computeIfAbsent()`, or `synchronized`. Use `volatile` for visible-but-non-compound access.

**Level 3:** Race conditions in Java are formalised as data races in the JMM. A data race = two threads access the same variable, at least one write, no HB ordering. Data races produce undefined JMM behavior — any value is technically legal. Use static analysis (FindBugs, SpotBugs, ErrorProne) and thread safety testing frameworks (JCStress) to detect races systematically.

**Level 4:** Race conditions are a specific subset of concurrency bugs. Related bugs: **deadlock** (threads wait for each other's locks forever), **livelock** (threads continuously change state in response to each other without progress), **starvation** (a thread can never acquire a needed resource). Race conditions are the most common and best candidates for prevention through lock-free algorithms (CAS, AtomicX) that eliminate the compound operation problem.

### ⚙️ How It Works (Mechanism)

**Race condition examples and fixes:**
```java
// RACE: check-then-act
class BankAccount {
    private double balance = 1000.0;

    // BROKEN: two threads can both pass the if-check
    void withdraw(double amount) {
        if (balance >= amount) {     // check
            balance -= amount;        // act — race between these!
        }
    }

    // FIXED: synchronized makes check-act atomic
    synchronized void withdraw(double amount) {
        if (balance >= amount) {
            balance -= amount;
        }
    }
}

// RACE: read-modify-write
class UnsafeCounter {
    int count = 0;
    void increment() { count++; } // not atomic!
}

// FIXED: CAS-based atomic
class SafeCounter {
    AtomicInteger count = new AtomicInteger(0);
    void increment() { count.incrementAndGet(); }
}

// RACE: lazy init (double-create)
class Registry {
    private Object instance = null;
    Object get() {
        if (instance == null) {          // check
            instance = new Object();     // act — two threads can both create!
        }
        return instance;
    }

    // FIXED: ConcurrentHashMap.computeIfAbsent (atomic)
    // Or: Double-Checked Locking with volatile
    // Or: Class holder pattern (thread-safe lazy init via class loading)
}
```

**Thread-safe patterns summary:**
```java
// 1. Atomic for single-variable operations
AtomicInteger counter = new AtomicInteger();
counter.incrementAndGet();

// 2. synchronized for compound operations
synchronized void transfer(double amount) {
    from.debit(amount);    // these must be atomic together
    to.credit(amount);
}

// 3. Immutability (best when possible)
record Config(String host, int port) {}
// Immutable: share freely with no synchronization

// 4. Concurrent collections
ConcurrentHashMap<K,V> map = new ConcurrentHashMap<>();
map.computeIfAbsent(key, k -> create(k)); // atomic

// 5. Thread confinement (ThreadLocal)
ThreadLocal<Formatter> fmt = ThreadLocal.withInitial(Formatter::new);
// Each thread has own copy — no sharing — no race
```

### 🔄 The Complete Picture — End-to-End Flow

RACE CONDITION FLOW:
```
[T1: balance = 1000, amount = 700]
    → [T1: check: 1000 >= 700 → true]  ← YOU ARE HERE
    → [T2: check: 1000 >= 700 → true (T1 hasn't deducted yet!)]
    → [T1: balance -= 700 → balance = 300]
    → [T2: balance -= 700 → balance = -400!  OVERDRAFT]
    → [Both passed the check — race condition]
```

FIX FLOW:
```
[T1: synchronized withdraw(700)]
    → [T1 acquires lock]
    → [T2 waits: BLOCKED]
    → [T1: check: 1000 >= 700 → true]
    → [T1: balance = 300]
    → [T1: releases lock]
    → [T2 acquires lock]
    → [T2: check: 300 >= 700 → false]
    → [T2: no withdrawal — correct]
```

WHAT CHANGES AT SCALE:
At high concurrency (10K+ requests/second), race conditions that appear 1-in-a-million at 100 RPS become 1-in-a-hundred at 10K RPS. What seems like a "rare edge case" in testing is a near-certain occurrence at scale. The severity of race conditions grows nonlinearly with load.

### 💻 Code Example

Example 1 — ID generation race:
```java
// BROKEN: two threads can get same ID
class IdGenerator {
    private long nextId = 1;
    long next() { return nextId++; } // race: read-add-write

    // FIXED: atomic
    private AtomicLong nextId = new AtomicLong(1);
    long next() { return nextId.getAndIncrement(); }
}
```

Example 2 — Map put-if-absent race:
```java
// BROKEN: two threads may both compute and put
Map<String, Data> cache = new HashMap<>();
void cacheResult(String key) {
    if (!cache.containsKey(key)) {  // check
        cache.put(key, compute(key)); // act — race!
    }
}

// FIXED: atomic compute-if-absent
ConcurrentHashMap<String, Data> cache = new ConcurrentHashMap<>();
void cacheResult(String key) {
    cache.computeIfAbsent(key, k -> compute(k));
}
```

### ⚖️ Comparison Table

| Bug Type | Involves | Result | Detectable | Fix |
|---|---|---|---|---|
| **Race condition** | Shared state + timing | Wrong values, data corruption | Hard (timing-dependent) | Synchronization, CAS, immutability |
| Deadlock | Lock ordering | Hang/freeze | Easier (thread dump) | Lock ordering, tryLock |
| Livelock | Response to other threads | CPU waste, no progress | Moderate | Backoff, random retry |
| Starvation | Resource acquisition | Thread never runs | Moderate | Fair locks, priorities |

How to distinguish: Wrong/corrupted data → race condition. Application hangs, threads BLOCKED → deadlock. CPU high but no progress → livelock.

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| Race conditions are rare and only affect counters | Race conditions affect ANY shared mutable state: collections, objects, bit flags, file access, database queries. Check-then-act is the most dangerous pattern, not just counters |
| Using synchronized everywhere prevents all race conditions | synchronized on different objects provides no mutual exclusion between them. `synchronized(this)` in two different instances of the same class = two different locks = still racy |
| volatile prevents race conditions | volatile provides visibility, not mutual exclusion. `volatile count++` is still a race condition (3-operation non-atomicity) |
| Race conditions always produce incorrect results | Race conditions may produce correct results BY COINCIDENCE (common in low-load tests). This is what makes them dangerous — the program appears correct but is fundamentally wrong |

### 🚨 Failure Modes & Diagnosis

**Race Condition Detection**

Tools:
```bash
# JCStress: Java Concurrency Stress testing
# https://openjdk.org/projects/code-tools/jcstress/
mvn jcstress:run

# Thread Sanitizer (for native code):
java -XX:+EnableThreadSanityCheck MyApp

# FindBugs/SpotBugs: static analysis
mvn spotbugs:check | grep "Race"

# hellgrind (Valgrind): for native threads
```

Fix pattern for all races:
1. Identify shared mutable state.
2. Identify all access points (reads AND writes).
3. Ensure all accesses have HB ordering: add `synchronized`, `volatile`, atomic operations, or immutability.

### 🔗 Related Keywords

**Prerequisites (understand these first):**
- `Thread (Java)` — race conditions require multiple threads
- `synchronized` — the primary mechanism to prevent race conditions
- `Java Memory Model (JMM)` — the formal definition of when race conditions are possible

**Builds On This (learn these next):**
- `CAS (Compare-And-Swap)` — lock-free alternative to synchronized for many race condition patterns
- `Atomic Classes` — Java's built-in CAS-based solutions for common race patterns

**Alternatives / Comparisons:**
- `CAS (Compare-And-Swap)` — hardware-level atomic operation that eliminates many race conditions without locks
- `synchronized` — lock-based solution that prevents races through mutual exclusion

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ WHAT IT IS   │ Bug: program outcome depends on thread    │
│              │ timing — different ordering = wrong result│
├──────────────┼───────────────────────────────────────────┤
│ PATTERNS     │ Check-then-act: if(x) use(x)             │
│              │ Read-modify-write: count++                │
│              │ Lazy init: if(null) x=create()            │
├──────────────┼───────────────────────────────────────────┤
│ KEY INSIGHT  │ Passes tests at low load, fails at scale  │
│              │ — non-deterministic, hard to reproduce    │
├──────────────┼───────────────────────────────────────────┤
│ FIX          │ synchronized, AtomicInteger/Reference,    │
│              │ ConcurrentHashMap, immutability           │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "Works in tests, fails in production —    │
│              │  two threads at exactly the wrong time"   │
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ CAS → AtomicInteger →                     │
│              │ ConcurrentHashMap                         │
└──────────────────────────────────────────────────────────┘
```

---
### 🧠 Think About This Before We Continue

**Q1.** A developer claims their code avoids race conditions by using `ConcurrentHashMap` for all shared state. However, the cache has a subtle race: `computeIfAbsent(key, k -> expensiveCompute(k))` is correct, but the code does `if (!map.containsKey(key)) map.put(key, compute(key))` instead. Explain exactly why this check-then-put pattern has a race condition even with `ConcurrentHashMap`, what specific scenario causes two calls to `compute(key)` simultaneously, why `computeIfAbsent` solves this, and whether `ConcurrentHashMap.computeIfAbsent` guarantees `compute(key)` is called exactly once.

**Q2.** Prove by example that the classic "benign" race condition in HashMap.put() in Java 8 (before the infinite loop fix) was NOT benign: describe the exact sequence of HashMap.put() operations in two threads that caused an infinite loop rather than just a missed put, what internal data structure (HashMap's linked list buckets) was corrupted, and why this infinite loop permanently consumes 100% CPU of one thread even though it's "just a map put" — making it arguably worse than a simple lost update.

