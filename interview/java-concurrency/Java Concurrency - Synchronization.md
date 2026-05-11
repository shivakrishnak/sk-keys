---
layout: default
title: "Java Concurrency - Synchronization"
parent: "Java Concurrency"
grand_parent: "Interview Mastery"
nav_order: 2
permalink: /interview/java-concurrency/synchronization/
topic: Java Concurrency
subtopic: Synchronization
keywords:
  - synchronized
  - volatile
  - Java Memory Model
  - ReentrantLock
  - ReadWriteLock and StampedLock
  - Atomic Variables and CAS
  - ThreadLocal
difficulty_range: mixed
status: in-progress
version: 2
---

# synchronized

**TL;DR** - The `synchronized` keyword provides mutual exclusion (only one thread at a time) and memory visibility (changes made by one thread are visible to others) through intrinsic locks (monitors) built into every Java object.

---

### The Problem This Solves

**WORLD WITHOUT IT:**
Two threads increment a counter simultaneously: both read 5, both write 6. One increment is lost. Bank balances go wrong. Data structures corrupt. Programs produce different results on different runs.

**THE BREAKING POINT:**
A shared `HashMap` corrupted by concurrent writes enters an infinite loop during `get()`, pinning a CPU core at 100% forever. No exception, no error - just a silent hang.

**THE INVENTION MOMENT:**
"This is exactly why synchronized was created."

**EVOLUTION:**
synchronized (Java 1.0) -> ReentrantLock (Java 5) -> StampedLock (Java 8) -> Virtual thread-friendly locks (Java 21).

---

### Textbook Definition

`synchronized` acquires the intrinsic lock (monitor) of an object before executing a block, releases it on exit. Only one thread can hold an object's monitor at a time. It provides two guarantees: mutual exclusion (atomicity of the block) and happens-before visibility (writes by the lock holder are visible to subsequent holders).

---

### Understand It in 30 Seconds

**One line:**
synchronized = one thread at a time, and changes are visible to the next thread.

**One analogy:**

> A bathroom with a lock. Only one person inside at a time. When they leave, the next person sees the current state of everything inside.

**One insight:**
Synchronized provides BOTH atomicity AND visibility. Using it for only one purpose (e.g., just atomicity without considering happens-before) is a common source of subtle bugs.

---

### First Principles Explanation

**CORE INVARIANTS:**
1. [TODO: Always true about this concept]
2. [TODO: Always true about this concept]
3. [TODO: Always true about this concept]

**DERIVED DESIGN:**
[TODO: How the invariants force the design.]

**THE TRADE-OFFS:**
**Gain:** [TODO]
**Cost:** [TODO]

**ESSENTIAL vs ACCIDENTAL COMPLEXITY:**
**Essential:** [TODO]
**Accidental:** [TODO]

---

### Mental Model / Analogy

> [TODO: Primary analogy in blockquote.]

- "[TODO: Analogy element]" -> [technical element]
- "[TODO: Analogy element]" -> [technical element]
- "[TODO: Analogy element]" -> [technical element]

Where this analogy breaks down: [TODO: 1 sentence.]

---

### Gradual Depth - Five Levels

**Level 1 - What it is (anyone can understand):**
A lock that ensures only one thread runs a section of code at a time, preventing data corruption from simultaneous access.

**Level 2 - How to use it (junior developer):**

```java
// Method-level lock (locks 'this')
public synchronized void increment() {
    count++;
}

// Block-level lock (more granular)
public void transfer(Account from,
        Account to, int amount) {
    synchronized (from) {
        synchronized (to) {
            from.debit(amount);
            to.credit(amount);
        }
    }
}

// Static method locks the Class object
public static synchronized Config get() {
    if (instance == null)
        instance = new Config();
    return instance;
}
```

**Level 3 - How it works (mid-level engineer):**

Every object has a monitor (header word in object layout):

1. Thread attempts to acquire monitor
2. If free: thread takes ownership, enters block
3. If held by another thread: thread BLOCKS (goes to BLOCKED state)
4. On exit: monitor released, one waiting thread wakes

Lock coarsening and biased locking (JVM optimizations):

- Biased locking: if only one thread ever locks an object, nearly free (just a flag)
- Thin lock: CAS on object header for uncontended access
- Fat lock: OS mutex when contention detected

```
Object header:
+-------------------+
| Mark Word (64bit) |  <- lock state here
+-------------------+
| Class pointer     |
+-------------------+

Mark Word states:
  Unlocked:     [hash|age|0|01]
  Biased:       [thread|epoch|age|1|01]
  Thin locked:  [stack ptr|00]
  Fat locked:   [monitor ptr|10]
```

**Level 4 - Mastery (senior/staff+ engineer):**

Synchronized limitations that drove ReentrantLock:

1. Can't attempt to acquire without blocking (`tryLock`)
2. Can't interrupt a waiting thread
3. Can't have multiple conditions
4. Can't upgrade read lock to write lock
5. No fairness option

Performance reality (modern JVMs):

- Uncontended synchronized is nearly free (biased locking)
- Under contention, performance degrades significantly
- Lock striping (ConcurrentHashMap) is better than one big lock
- Virtual threads: synchronized PINS the carrier thread; prefer ReentrantLock


**Level 5 - Distinguished (expert thinking):**
[TODO: Cross-domain pattern recognition. Expert heuristics.
 What would you change if redesigning today?
 How does this compose at extreme scale?]

---

### How It Works (Mechanism)

[TODO: Internal mechanics. Data flow. Key steps.
 4-8 sentences covering implementation details.]

---

### Complete Picture - End-to-End Flow

**NORMAL FLOW:**
[TODO] -> [TODO] -> [THIS CONCEPT <- YOU ARE HERE]
       -> [TODO]

**FAILURE PATH:**
[TODO: cascade -> observable symptom]

**WHAT CHANGES AT SCALE:**
[TODO: 2-3 sentences on behaviour at 10x/100x/1000x load.]

---

### Code Example

**BAD - Over-synchronization (bottleneck):**

```java
// One lock for everything - serializes all ops
public class UserService {
    private final Map<String, User> cache =
        new HashMap<>();
    private final AtomicLong hits =
        new AtomicLong();

    public synchronized User get(String id) {
        hits.incrementAndGet();
        return cache.get(id);
        // ALL reads serialize on one lock!
    }
}
```

**GOOD - Minimal critical section:**

```java
public class UserService {
    private final ConcurrentHashMap<String, User>
        cache = new ConcurrentHashMap<>();
    private final AtomicLong hits =
        new AtomicLong();

    public User get(String id) {
        hits.incrementAndGet(); // atomic, no lock
        return cache.get(id);  // lock-free read
    }
}
```

---

### Quick Reference Card

**WHAT IT IS:** [TODO]
**PROBLEM IT SOLVES:** [TODO]
**KEY INSIGHT:** [TODO]
**USE WHEN:** [TODO]
**AVOID WHEN:** [TODO]
**ANTI-PATTERN:** [TODO]
**TRADE-OFF:** [TODO]
**ONE-LINER:** [TODO]

**If you remember only 3 things:**

1. synchronized = mutual exclusion + memory visibility (both!)
2. Lock on the minimum scope needed (block > method)
3. With virtual threads, prefer ReentrantLock (synchronized pins carrier)

**Interview one-liner:**
"synchronized provides both atomicity and visibility via the object's intrinsic monitor, but its inability to attempt-lock, interrupt, or support fairness led to ReentrantLock for advanced use cases."

---

### The Surprising Truth

[TODO: 2-4 sentences. One counterintuitive fact.
 Specific. Makes this concept permanently memorable.]

---

### Interview Deep-Dive

**Q1: What is the difference between synchronized method and synchronized block?**

_Why they ask:_ Tests granularity understanding.

_Strong answer:_

Synchronized method locks `this` (or `Class` object for static):

```java
synchronized void foo() { /* locks this */ }
static synchronized void bar() {
    /* locks MyClass.class */
}
```

Synchronized block allows any object as lock and smaller scope:

```java
void foo() {
    // non-critical work (no lock held)
    synchronized (specificLock) {
        // only this part is serialized
    }
    // more non-critical work
}
```

Block is preferred because:

- Lock object can be private (encapsulated)
- Smaller critical section = less contention
- Different locks for different data = more parallelism
- Explicit about WHAT is being protected

---

**Q2: Can you get a deadlock with synchronized? How do you prevent it?**

_Why they ask:_ Tests liveness problem understanding.

_Strong answer:_

Deadlock requires: mutual exclusion + hold-and-wait + no preemption + circular wait.

```java
// DEADLOCK: Thread1 locks A then B
//           Thread2 locks B then A
synchronized (accountA) {
    synchronized (accountB) { transfer(); }
}
// Meanwhile another thread:
synchronized (accountB) {
    synchronized (accountA) { transfer(); }
}
```

Prevention strategies:

1. **Lock ordering:** Always acquire locks in consistent global order

```java
Account first = a.id < b.id ? a : b;
Account second = a.id < b.id ? b : a;
synchronized (first) {
    synchronized (second) { transfer(); }
}
```

2. **tryLock with timeout** (requires ReentrantLock)
3. **Single lock** (coarser granularity, less parallelism)
4. **Lock-free algorithms** (CAS, immutable data)

---

**Q3: Why does synchronized pin virtual threads?**

_Why they ask:_ Tests Java 21 knowledge.

_Strong answer:_

Virtual threads are multiplexed onto platform (carrier) threads. When a virtual thread reaches a blocking point (I/O, sleep, Lock.lock()), it unmounts from the carrier thread, freeing it for other virtual threads.

But `synchronized` uses the OS monitor which is tied to the carrier thread's native stack. While a virtual thread holds a synchronized lock, it CANNOT unmount from the carrier thread. The carrier thread is "pinned" and unavailable for other virtual threads.

Impact: If many virtual threads pin carrier threads, you effectively lose the scalability benefit.

Fix: Replace `synchronized` with `ReentrantLock` in code that virtual threads will execute:

```java
// BAD with virtual threads
synchronized (lock) {
    blockingIO(); // pins carrier!
}

// GOOD with virtual threads
reentrantLock.lock();
try {
    blockingIO(); // can unmount
} finally {
    reentrantLock.unlock();
}
```

---

### Comparison Table

[TODO: Include if 2+ named alternatives exist for synchronized. Otherwise remove this section.]

---

### Common Misconceptions

| # | Misconception | Reality |
|---|---------------|---------|
| 1 | [TODO] | [TODO] |
| 2 | [TODO] | [TODO] |
| 3 | [TODO] | [TODO] |
| 4 | [TODO] | [TODO] |

---

### Failure Modes and Diagnosis

**Failure Mode 1: [TODO]**
**Symptom:** [TODO]
**Root Cause:** [TODO]
**Diagnostic:**
```
[TODO: real diagnostic command]
```
**Fix:** [TODO: BAD then GOOD]
**Prevention:** [TODO]

**Failure Mode 2: [TODO]**
**Symptom:** [TODO]
**Root Cause:** [TODO]
**Diagnostic:**
```
[TODO: real diagnostic command]
```
**Fix:** [TODO: BAD then GOOD]
**Prevention:** [TODO]

**Failure Mode 3: [TODO]**
**Symptom:** [TODO]
**Root Cause:** [TODO]
**Diagnostic:**
```
[TODO: real diagnostic command]
```
**Fix:** [TODO: BAD then GOOD]
**Prevention:** [TODO]

---

### Related Keywords

**Prerequisites (understand these first):**
- [TODO] - [why needed]
- [TODO] - [why needed]

**Builds on this (learn these next):**
- [TODO] - [what it adds]
- [TODO] - [what it adds]

**Alternatives / Comparisons:**
- [TODO] - [when to prefer it]
- [TODO] - [when to prefer it]


---

---

# volatile

**TL;DR** - `volatile` guarantees visibility (all threads see the latest value) and prevents instruction reordering, but does NOT provide atomicity for compound operations like increment.

---

### The Problem This Solves

**WORLD WITHOUT IT:**
Thread A sets `running = false`, but Thread B never sees the change because its CPU cache still holds `true`. Thread B loops forever. The JVM is allowed to cache variables in registers/CPU cache and never re-read from main memory without explicit memory barriers.

**THE INVENTION MOMENT:**
"This is exactly why volatile was created."

---

### Textbook Definition

The `volatile` keyword in Java ensures that reads and writes to a variable go directly to main memory (or more precisely, establish happens-before relationships). Every read of a volatile variable sees the most recent write by any thread. Additionally, volatile prevents compiler and CPU reordering of instructions around volatile accesses.

---

### Understand It in 30 Seconds

**One line:**
[TODO: 15 words max. Zero jargon.]

**One analogy:**
> [TODO: 2-3 sentence real-world analogy.]

**One insight:**
[TODO: What separates knowing the name from understanding it.]

---

### First Principles Explanation

**CORE INVARIANTS:**
1. [TODO: Always true about this concept]
2. [TODO: Always true about this concept]
3. [TODO: Always true about this concept]

**DERIVED DESIGN:**
[TODO: How the invariants force the design.]

**THE TRADE-OFFS:**
**Gain:** [TODO]
**Cost:** [TODO]

**ESSENTIAL vs ACCIDENTAL COMPLEXITY:**
**Essential:** [TODO]
**Accidental:** [TODO]

---

### Mental Model / Analogy

> [TODO: Primary analogy in blockquote.]

- "[TODO: Analogy element]" -> [technical element]
- "[TODO: Analogy element]" -> [technical element]
- "[TODO: Analogy element]" -> [technical element]

Where this analogy breaks down: [TODO: 1 sentence.]

---

### Gradual Depth - Five Levels

**Level 1 - What it is (anyone can understand):**
volatile means "always read the freshest value" - no caching tricks by the CPU or compiler.

**Level 2 - How to use it (junior developer):**

```java
// Classic use: shutdown flag
private volatile boolean running = true;

public void run() {
    while (running) { // always reads latest
        doWork();
    }
}

public void stop() {
    running = false; // visible to all threads
}
```

**Level 3 - How it works (mid-level engineer):**

What volatile guarantees:

1. **Visibility:** Writes are immediately visible to all threads
2. **Ordering:** No reordering of instructions past volatile access

What volatile does NOT guarantee:

- **Atomicity of compounds:** `volatile int count; count++` is NOT atomic (read-modify-write)

```java
// BROKEN: volatile doesn't make ++ atomic
private volatile int count = 0;
count++; // read 5, another thread reads 5,
         // both write 6. Lost update!

// FIX: Use AtomicInteger
private final AtomicInteger count =
    new AtomicInteger(0);
count.incrementAndGet(); // atomic CAS
```

**Level 4 - Mastery (senior/staff+ engineer):**

Volatile's memory semantics (JMM):

- Write to volatile = release fence (all prior writes become visible)
- Read from volatile = acquire fence (all subsequent reads see latest)

This means volatile can be used for "piggybacking" visibility:

```java
int x = 0;          // non-volatile
volatile boolean ready = false;

// Thread A:
x = 42;             // write x
ready = true;       // volatile write (release)

// Thread B:
if (ready) {        // volatile read (acquire)
    assert x == 42; // guaranteed to see 42!
    // All writes before volatile write
    // are visible after volatile read
}
```

Valid uses of volatile:

1. Status flags (running, shutdown, initialized)
2. Double-checked locking (the `instance` field)
3. Publishing immutable objects
4. One writer, multiple readers (no compound ops)


**Level 5 - Distinguished (expert thinking):**
[TODO: Cross-domain pattern recognition. Expert heuristics.
 What would you change if redesigning today?
 How does this compose at extreme scale?]

---

### How It Works (Mechanism)

[TODO: Internal mechanics. Data flow. Key steps.
 4-8 sentences covering implementation details.]

---

### Complete Picture - End-to-End Flow

**NORMAL FLOW:**
[TODO] -> [TODO] -> [THIS CONCEPT <- YOU ARE HERE]
       -> [TODO]

**FAILURE PATH:**
[TODO: cascade -> observable symptom]

**WHAT CHANGES AT SCALE:**
[TODO: 2-3 sentences on behaviour at 10x/100x/1000x load.]

---

### Code Example

**BAD - volatile for compound operations:**

```java
private volatile int sequence = 0;
// Two threads call this:
public int nextSequence() {
    return sequence++; // NOT atomic!
    // read + increment + write = 3 ops
}
```

**GOOD - AtomicInteger for compound operations:**

```java
private final AtomicInteger sequence =
    new AtomicInteger(0);
public int nextSequence() {
    return sequence.getAndIncrement();
    // CAS loop - truly atomic
}
```

---

### Quick Reference Card

**WHAT IT IS:** [TODO]
**PROBLEM IT SOLVES:** [TODO]
**KEY INSIGHT:** [TODO]
**USE WHEN:** [TODO]
**AVOID WHEN:** [TODO]
**ANTI-PATTERN:** [TODO]
**TRADE-OFF:** [TODO]
**ONE-LINER:** [TODO]

**If you remember only 3 things:**

1. volatile = visibility + ordering, NOT atomicity
2. Use for flags and single-writer scenarios only
3. For increment/compare-and-set, use Atomic\* classes

**Interview one-liner:**
"volatile ensures visibility across threads and prevents reordering, but provides no atomicity for compound operations - use Atomic\* classes or locks for read-modify-write."

---

### The Surprising Truth

[TODO: 2-4 sentences. One counterintuitive fact.
 Specific. Makes this concept permanently memorable.]

---

### Interview Deep-Dive

**Q1: What is the difference between volatile and synchronized?**

_Why they ask:_ Tests precision of concurrency understanding.

_Strong answer:_

| Aspect     | volatile                    | synchronized       |
| ---------- | --------------------------- | ------------------ |
| Visibility | Yes                         | Yes                |
| Atomicity  | No (single read/write only) | Yes (entire block) |
| Blocking   | No                          | Yes (contention)   |
| Scope      | Single variable             | Any code block     |
| Lock       | None                        | Monitor required   |

volatile is lighter but weaker. Use volatile when:

- Only one thread writes (or writes are independent)
- No compound read-modify-write operations
- You only need visibility, not mutual exclusion

Use synchronized/Lock when:

- Multiple threads modify shared state
- Compound operations must be atomic
- You need to protect invariants across multiple variables

---

**Q2: Explain double-checked locking and why volatile is needed.**

_Why they ask:_ Tests understanding of memory ordering.

_Strong answer:_

```java
class Singleton {
    private static volatile Singleton instance;

    public static Singleton get() {
        if (instance == null) {         // 1st check
            synchronized (Singleton.class) {
                if (instance == null) { // 2nd check
                    instance = new Singleton();
                }
            }
        }
        return instance;
    }
}
```

Without volatile, `instance = new Singleton()` can be reordered. The JVM may:

1. Allocate memory
2. Assign reference to `instance` (non-null now!)
3. Run constructor (not yet complete!)

Another thread sees non-null `instance` at step 2 and uses a partially constructed object. `volatile` prevents this reordering.

---

### Comparison Table

[TODO: Include if 2+ named alternatives exist for volatile. Otherwise remove this section.]

---

### Common Misconceptions

| # | Misconception | Reality |
|---|---------------|---------|
| 1 | [TODO] | [TODO] |
| 2 | [TODO] | [TODO] |
| 3 | [TODO] | [TODO] |
| 4 | [TODO] | [TODO] |

---

### Failure Modes and Diagnosis

**Failure Mode 1: [TODO]**
**Symptom:** [TODO]
**Root Cause:** [TODO]
**Diagnostic:**
```
[TODO: real diagnostic command]
```
**Fix:** [TODO: BAD then GOOD]
**Prevention:** [TODO]

**Failure Mode 2: [TODO]**
**Symptom:** [TODO]
**Root Cause:** [TODO]
**Diagnostic:**
```
[TODO: real diagnostic command]
```
**Fix:** [TODO: BAD then GOOD]
**Prevention:** [TODO]

**Failure Mode 3: [TODO]**
**Symptom:** [TODO]
**Root Cause:** [TODO]
**Diagnostic:**
```
[TODO: real diagnostic command]
```
**Fix:** [TODO: BAD then GOOD]
**Prevention:** [TODO]

---

### Related Keywords

**Prerequisites (understand these first):**
- [TODO] - [why needed]
- [TODO] - [why needed]

**Builds on this (learn these next):**
- [TODO] - [what it adds]
- [TODO] - [what it adds]

**Alternatives / Comparisons:**
- [TODO] - [when to prefer it]
- [TODO] - [when to prefer it]


---

---

# Java Memory Model (JMM)

**TL;DR** - The JMM defines the rules for when writes by one thread become visible to reads by another thread, using the "happens-before" relationship as its core abstraction.

---

### The Problem This Solves

**WORLD WITHOUT IT:**
Without a memory model, the behavior of multithreaded programs depends on hardware (x86 vs ARM have different memory ordering), JIT compiler optimizations, and OS scheduling. Code that works on your machine silently breaks on another.

**THE INVENTION MOMENT:**
"This is exactly why the Java Memory Model exists."

---

### Textbook Definition

The Java Memory Model (JSR-133, revised in Java 5) specifies which values a read of a shared variable may return given the writes in the program. Its key abstraction is the "happens-before" relationship: if action A happens-before action B, then B is guaranteed to see A's effects.

---

### Understand It in 30 Seconds

**One line:**
[TODO: 15 words max. Zero jargon.]

**One analogy:**
> [TODO: 2-3 sentence real-world analogy.]

**One insight:**
[TODO: What separates knowing the name from understanding it.]

---

### First Principles Explanation

**CORE INVARIANTS:**
1. [TODO: Always true about this concept]
2. [TODO: Always true about this concept]
3. [TODO: Always true about this concept]

**DERIVED DESIGN:**
[TODO: How the invariants force the design.]

**THE TRADE-OFFS:**
**Gain:** [TODO]
**Cost:** [TODO]

**ESSENTIAL vs ACCIDENTAL COMPLEXITY:**
**Essential:** [TODO]
**Accidental:** [TODO]

---

### Mental Model / Analogy

> [TODO: Primary analogy in blockquote.]

- "[TODO: Analogy element]" -> [technical element]
- "[TODO: Analogy element]" -> [technical element]
- "[TODO: Analogy element]" -> [technical element]

Where this analogy breaks down: [TODO: 1 sentence.]

---

### Gradual Depth - Five Levels

**Level 1 - What it is (anyone can understand):**
The JMM is a contract between your code and the JVM: it defines when Thread B can "see" what Thread A wrote to shared memory.

**Level 2 - How to use it (junior developer):**

Rule: If two threads access the same variable and at least one writes, you need synchronization to establish happens-before. Otherwise the read may see a stale value.

**Level 3 - How it works (mid-level engineer):**

**Happens-before rules (the complete list):**

1. **Program order:** Each action happens-before the next in the same thread
2. **Monitor lock:** Unlock happens-before subsequent lock of same monitor
3. **Volatile:** Write to volatile happens-before subsequent read of same variable
4. **Thread start:** `thread.start()` happens-before any action in the started thread
5. **Thread join:** All actions in a thread happen-before `join()` returns
6. **Transitivity:** If A hb B and B hb C, then A hb C

```
Thread A:          Thread B:
x = 42;
lock(m);
  y = 1;
unlock(m);
                  lock(m);
                    // sees x=42, y=1
                    // (hb via unlock->lock)
                  unlock(m);
```

**Level 4 - Mastery (senior/staff+ engineer):**

**What the JMM permits that surprises people:**

1. Reads can see stale values without happens-before
2. Writes can appear reordered to other threads
3. `final` fields have special semantics (safe publication via constructor)
4. Out-of-thin-air values are forbidden but data races are allowed

```java
// Both x and y are 0 initially, non-volatile
// Thread A:      Thread B:
r1 = y;          r2 = x;
x = r1;          y = r2;
// Can r1 == r2 == 42? NO (out-of-thin-air)
// Can r1 == r2 == 0? YES (both read initial)
// Can r1=0, r2=0? YES
```

**The real-world impact:**

- x86 is "almost sequentially consistent" (only store-load reorder)
- ARM/POWER are weakly ordered (almost anything can reorder)
- JMM is your portable guarantee across all hardware


**Level 5 - Distinguished (expert thinking):**
[TODO: Cross-domain pattern recognition. Expert heuristics.
 What would you change if redesigning today?
 How does this compose at extreme scale?]

---

### How It Works (Mechanism)

[TODO: Internal mechanics. Data flow. Key steps.
 4-8 sentences covering implementation details.]

---

### Complete Picture - End-to-End Flow

**NORMAL FLOW:**
[TODO] -> [TODO] -> [THIS CONCEPT <- YOU ARE HERE]
       -> [TODO]

**FAILURE PATH:**
[TODO: cascade -> observable symptom]

**WHAT CHANGES AT SCALE:**
[TODO: 2-3 sentences on behaviour at 10x/100x/1000x load.]

---

### Quick Reference Card

**WHAT IT IS:** [TODO]
**PROBLEM IT SOLVES:** [TODO]
**KEY INSIGHT:** [TODO]
**USE WHEN:** [TODO]
**AVOID WHEN:** [TODO]
**ANTI-PATTERN:** [TODO]
**TRADE-OFF:** [TODO]
**ONE-LINER:** [TODO]

**If you remember only 3 things:**

1. Happens-before is the only guarantee of visibility between threads
2. Without synchronization, reads may see arbitrarily stale values
3. The 6 happens-before rules cover all safe publication patterns

**Interview one-liner:**
"The JMM defines visibility guarantees via happens-before relationships, ensuring portable concurrency semantics regardless of hardware memory ordering."

---

### The Surprising Truth

[TODO: 2-4 sentences. One counterintuitive fact.
 Specific. Makes this concept permanently memorable.]

---

### Interview Deep-Dive

**Q1: What is happens-before and why does it matter?**

_Why they ask:_ Tests fundamental understanding of concurrency correctness.

_Strong answer:_

Happens-before (hb) is a partial order on program actions. If A hb B, then:

- A's memory effects are visible to B
- A is ordered before B (no reordering between them)

Without hb, the JVM/hardware may:

- Cache values in registers (invisible to other threads)
- Reorder instructions (out-of-order execution)
- Delay memory writes (write buffers)

You establish hb through: synchronized, volatile, thread start/join, final field publication, and transitivity of these.

**Practical rule:** If you can't trace a happens-before chain from a write to a read through the program's synchronization actions, the read may see ANY previous value (including the initial default).

---

**Q2: What is safe publication and how do you achieve it?**

_Why they ask:_ Tests understanding of object visibility guarantees.

_Strong answer:_

Safe publication means ensuring that when Thread A creates an object and Thread B reads a reference to it, Thread B sees a fully constructed object (not partially initialized).

Safe publication mechanisms:

1. Store in a `volatile` field or `AtomicReference`
2. Store in a `final` field (constructor must not leak `this`)
3. Store under a lock (synchronized)
4. Store in a concurrent collection (ConcurrentHashMap, etc.)

```java
// UNSAFE: non-volatile, no lock
MyObject obj;

// Thread A:
obj = new MyObject(); // may be partially
                      // constructed when B reads

// Thread B:
if (obj != null) {
    obj.doWork(); // may see uninitialized fields!
}

// SAFE: volatile publication
volatile MyObject obj;
// Now Thread B is guaranteed to see fully
// constructed object if it sees non-null ref
```

---

### Comparison Table

[TODO: Include if 2+ named alternatives exist for Java Memory Model (JMM). Otherwise remove this section.]

---

### Common Misconceptions

| # | Misconception | Reality |
|---|---------------|---------|
| 1 | [TODO] | [TODO] |
| 2 | [TODO] | [TODO] |
| 3 | [TODO] | [TODO] |
| 4 | [TODO] | [TODO] |

---

### Failure Modes and Diagnosis

**Failure Mode 1: [TODO]**
**Symptom:** [TODO]
**Root Cause:** [TODO]
**Diagnostic:**
```
[TODO: real diagnostic command]
```
**Fix:** [TODO: BAD then GOOD]
**Prevention:** [TODO]

**Failure Mode 2: [TODO]**
**Symptom:** [TODO]
**Root Cause:** [TODO]
**Diagnostic:**
```
[TODO: real diagnostic command]
```
**Fix:** [TODO: BAD then GOOD]
**Prevention:** [TODO]

**Failure Mode 3: [TODO]**
**Symptom:** [TODO]
**Root Cause:** [TODO]
**Diagnostic:**
```
[TODO: real diagnostic command]
```
**Fix:** [TODO: BAD then GOOD]
**Prevention:** [TODO]

---

### Related Keywords

**Prerequisites (understand these first):**
- [TODO] - [why needed]
- [TODO] - [why needed]

**Builds on this (learn these next):**
- [TODO] - [what it adds]
- [TODO] - [what it adds]

**Alternatives / Comparisons:**
- [TODO] - [when to prefer it]
- [TODO] - [when to prefer it]


---

---

# ReentrantLock

**TL;DR** - ReentrantLock is an explicit lock that provides the same mutual exclusion as synchronized but adds tryLock, timed waiting, interruptibility, fairness, and multiple condition queues.

---

### The Problem This Solves

**WORLD WITHOUT IT:**
synchronized is all-or-nothing: you can't attempt a lock without blocking, can't time out, can't interrupt a waiting thread, can't have fair ordering, and can't have multiple wait-sets on the same lock.

**THE INVENTION MOMENT:**
"This is exactly why ReentrantLock was created."

---

### Textbook Definition

[TODO: 2-4 sentences. Formal. Technically precise.]

---

### Understand It in 30 Seconds

**One line:**
[TODO: 15 words max. Zero jargon.]

**One analogy:**
> [TODO: 2-3 sentence real-world analogy.]

**One insight:**
[TODO: What separates knowing the name from understanding it.]

---

### First Principles Explanation

**CORE INVARIANTS:**
1. [TODO: Always true about this concept]
2. [TODO: Always true about this concept]
3. [TODO: Always true about this concept]

**DERIVED DESIGN:**
[TODO: How the invariants force the design.]

**THE TRADE-OFFS:**
**Gain:** [TODO]
**Cost:** [TODO]

**ESSENTIAL vs ACCIDENTAL COMPLEXITY:**
**Essential:** [TODO]
**Accidental:** [TODO]

---

### Mental Model / Analogy

> [TODO: Primary analogy in blockquote.]

- "[TODO: Analogy element]" -> [technical element]
- "[TODO: Analogy element]" -> [technical element]
- "[TODO: Analogy element]" -> [technical element]

Where this analogy breaks down: [TODO: 1 sentence.]

---

### Gradual Depth - Five Levels

**Level 1 - What it is (anyone can understand):**
Like synchronized but with more control - you can try the lock, give up after a timeout, and have multiple waiting lines.

**Level 2 - How to use it (junior developer):**

```java
private final ReentrantLock lock =
    new ReentrantLock();

public void transfer(int amount) {
    lock.lock();
    try {
        // critical section
        balance -= amount;
    } finally {
        lock.unlock(); // ALWAYS in finally!
    }
}
```

**Level 3 - How it works (mid-level engineer):**

Key advantages over synchronized:

```java
// 1. tryLock: non-blocking attempt
if (lock.tryLock()) {
    try { doWork(); }
    finally { lock.unlock(); }
} else {
    handleContention();
}

// 2. Timed lock: give up after timeout
if (lock.tryLock(100, MILLISECONDS)) {
    try { doWork(); }
    finally { lock.unlock(); }
} else {
    throw new TimeoutException();
}

// 3. Interruptible lock
try {
    lock.lockInterruptibly();
    try { doWork(); }
    finally { lock.unlock(); }
} catch (InterruptedException e) {
    Thread.currentThread().interrupt();
}

// 4. Condition (replaces wait/notify)
Condition notEmpty = lock.newCondition();
Condition notFull = lock.newCondition();
// Can have multiple conditions per lock!
```

**Level 4 - Mastery (senior/staff+ engineer):**

**Fairness:** `new ReentrantLock(true)` gives fair ordering (longest-waiting thread gets lock next). Costs ~10-20% throughput but prevents starvation.

**Reentrancy:** Same thread can acquire the lock multiple times without deadlocking. Hold count incremented on each lock(), decremented on unlock(). Only fully released when count reaches 0.

**Virtual threads:** ReentrantLock doesn't pin carrier threads (unlike synchronized). Strongly preferred for virtual thread code.

**When to prefer ReentrantLock over synchronized:**

- Need tryLock or timeout
- Need interruptible locking
- Need fairness guarantee
- Need multiple conditions
- Using virtual threads with blocking I/O inside the lock

**When synchronized is fine:**

- Simple, uncontended locking
- No need for advanced features
- Code clarity matters more than flexibility


**Level 5 - Distinguished (expert thinking):**
[TODO: Cross-domain pattern recognition. Expert heuristics.
 What would you change if redesigning today?
 How does this compose at extreme scale?]

---

### How It Works (Mechanism)

[TODO: Internal mechanics. Data flow. Key steps.
 4-8 sentences covering implementation details.]

---

### Complete Picture - End-to-End Flow

**NORMAL FLOW:**
[TODO] -> [TODO] -> [THIS CONCEPT <- YOU ARE HERE]
       -> [TODO]

**FAILURE PATH:**
[TODO: cascade -> observable symptom]

**WHAT CHANGES AT SCALE:**
[TODO: 2-3 sentences on behaviour at 10x/100x/1000x load.]

---

### Code Example

**BAD - Potential deadlock with synchronized:**

```java
// No way to timeout or back off
synchronized (lockA) {
    synchronized (lockB) { // deadlock risk!
        transfer();
    }
}
```

**GOOD - Deadlock prevention with tryLock:**

```java
while (true) {
    if (lockA.tryLock(50, MILLISECONDS)) {
        try {
            if (lockB.tryLock(50, MILLIS)) {
                try {
                    transfer();
                    return;
                } finally {
                    lockB.unlock();
                }
            }
        } finally {
            lockA.unlock();
        }
    }
    Thread.sleep(random.nextInt(50));
}
```

---

### Quick Reference Card

**WHAT IT IS:** [TODO]
**PROBLEM IT SOLVES:** [TODO]
**KEY INSIGHT:** [TODO]
**USE WHEN:** [TODO]
**AVOID WHEN:** [TODO]
**ANTI-PATTERN:** [TODO]
**TRADE-OFF:** [TODO]
**ONE-LINER:** [TODO]

**If you remember only 3 things:**

1. Always unlock in finally block - no exceptions
2. tryLock prevents deadlocks via timeout-and-retry
3. Preferred over synchronized for virtual threads (no pinning)

**Interview one-liner:**
"ReentrantLock adds tryLock, timeout, interruptibility, fairness, and multiple conditions to synchronized's basic mutual exclusion, and is required for virtual thread compatibility."

---

### The Surprising Truth

[TODO: 2-4 sentences. One counterintuitive fact.
 Specific. Makes this concept permanently memorable.]

---

### Interview Deep-Dive

**Q1: When would you choose ReentrantLock over synchronized?**

_Why they ask:_ Tests understanding of tradeoffs.

_Strong answer:_

Choose ReentrantLock when you need:

1. **Non-blocking attempts:** `tryLock()` to avoid waiting
2. **Timeouts:** `tryLock(timeout)` to prevent deadlocks
3. **Interruptibility:** `lockInterruptibly()` for cancellation
4. **Fairness:** Prevent thread starvation
5. **Multiple conditions:** Separate wait queues
6. **Virtual threads:** Avoid carrier pinning

Choose synchronized when:

- None of above apply
- Simplicity matters (auto-unlock, no finally needed)
- Performance is similar (uncontended case)

---

**Q2: What does "reentrant" mean and why does it matter?**

_Why they ask:_ Tests lock semantics understanding.

_Strong answer:_

Reentrant = a thread that already holds the lock can acquire it again without deadlocking. The lock maintains a hold count:

```java
lock.lock();      // hold count = 1
  lock.lock();    // hold count = 2 (reentrant!)
  lock.unlock();  // hold count = 1
lock.unlock();    // hold count = 0 (released)
```

Why it matters: Without reentrancy, a synchronized method calling another synchronized method on the same object would deadlock with itself. Java's `synchronized` is reentrant. So is `ReentrantLock`.

Example: `synchronized hashCode()` calls `synchronized equals()` on the same object during HashMap operations. Without reentrancy, this deadlocks.

---

### Comparison Table

[TODO: Include if 2+ named alternatives exist for ReentrantLock. Otherwise remove this section.]

---

### Common Misconceptions

| # | Misconception | Reality |
|---|---------------|---------|
| 1 | [TODO] | [TODO] |
| 2 | [TODO] | [TODO] |
| 3 | [TODO] | [TODO] |
| 4 | [TODO] | [TODO] |

---

### Failure Modes and Diagnosis

**Failure Mode 1: [TODO]**
**Symptom:** [TODO]
**Root Cause:** [TODO]
**Diagnostic:**
```
[TODO: real diagnostic command]
```
**Fix:** [TODO: BAD then GOOD]
**Prevention:** [TODO]

**Failure Mode 2: [TODO]**
**Symptom:** [TODO]
**Root Cause:** [TODO]
**Diagnostic:**
```
[TODO: real diagnostic command]
```
**Fix:** [TODO: BAD then GOOD]
**Prevention:** [TODO]

**Failure Mode 3: [TODO]**
**Symptom:** [TODO]
**Root Cause:** [TODO]
**Diagnostic:**
```
[TODO: real diagnostic command]
```
**Fix:** [TODO: BAD then GOOD]
**Prevention:** [TODO]

---

### Related Keywords

**Prerequisites (understand these first):**
- [TODO] - [why needed]
- [TODO] - [why needed]

**Builds on this (learn these next):**
- [TODO] - [what it adds]
- [TODO] - [what it adds]

**Alternatives / Comparisons:**
- [TODO] - [when to prefer it]
- [TODO] - [when to prefer it]


---

---

# ReadWriteLock and StampedLock

**TL;DR** - ReadWriteLock allows concurrent reads with exclusive writes (many readers OR one writer); StampedLock adds optimistic reading for even higher read throughput.

---

### The Problem This Solves

**WORLD WITHOUT IT:**
A cache is read 1000x/sec and written 1x/sec. With exclusive locking, all 1000 reads serialize behind each other even though reading is inherently safe when no write is happening.

**THE INVENTION MOMENT:**
"This is exactly why read-write separation was created."

---

### Textbook Definition

[TODO: 2-4 sentences. Formal. Technically precise.]

---

### Understand It in 30 Seconds

**One line:**
[TODO: 15 words max. Zero jargon.]

**One analogy:**
> [TODO: 2-3 sentence real-world analogy.]

**One insight:**
[TODO: What separates knowing the name from understanding it.]

---

### First Principles Explanation

**CORE INVARIANTS:**
1. [TODO: Always true about this concept]
2. [TODO: Always true about this concept]
3. [TODO: Always true about this concept]

**DERIVED DESIGN:**
[TODO: How the invariants force the design.]

**THE TRADE-OFFS:**
**Gain:** [TODO]
**Cost:** [TODO]

**ESSENTIAL vs ACCIDENTAL COMPLEXITY:**
**Essential:** [TODO]
**Accidental:** [TODO]

---

### Mental Model / Analogy

> [TODO: Primary analogy in blockquote.]

- "[TODO: Analogy element]" -> [technical element]
- "[TODO: Analogy element]" -> [technical element]
- "[TODO: Analogy element]" -> [technical element]

Where this analogy breaks down: [TODO: 1 sentence.]

---

### Gradual Depth - Five Levels

**Level 1 - What it is (anyone can understand):**
ReadWriteLock lets multiple readers in simultaneously but makes everyone wait when a writer needs exclusive access.

**Level 2 - How to use it (junior developer):**

```java
ReadWriteLock rwLock =
    new ReentrantReadWriteLock();

// Multiple threads can read concurrently
rwLock.readLock().lock();
try {
    return cache.get(key);
} finally {
    rwLock.readLock().unlock();
}

// Only one thread writes (exclusive)
rwLock.writeLock().lock();
try {
    cache.put(key, value);
} finally {
    rwLock.writeLock().unlock();
}
```

**Level 3 - How it works (mid-level engineer):**

ReadWriteLock rules:

- Multiple readers can hold read lock simultaneously
- Write lock is exclusive (blocks all readers and other writers)
- Write lock can downgrade to read lock (but not vice versa)
- Can be fair or unfair

StampedLock (Java 8) adds optimistic reading:

```java
StampedLock sl = new StampedLock();

// Optimistic read (no actual lock acquired!)
long stamp = sl.tryOptimisticRead();
double x = this.x;
double y = this.y;
if (!sl.validate(stamp)) {
    // A write happened, fall back to real lock
    stamp = sl.readLock();
    try {
        x = this.x;
        y = this.y;
    } finally {
        sl.unlockRead(stamp);
    }
}
return Math.sqrt(x*x + y*y);
```

**Level 4 - Mastery (senior/staff+ engineer):**

**StampedLock vs ReadWriteLock:**

| Feature           | ReentrantReadWriteLock | StampedLock |
| ----------------- | ---------------------- | ----------- |
| Reentrant         | Yes                    | NO          |
| Condition support | Yes                    | NO          |
| Optimistic read   | No                     | Yes         |
| Read throughput   | Good                   | Better      |
| Complexity        | Low                    | High        |

StampedLock is not reentrant - acquiring twice deadlocks. It's a specialized tool for high-read-throughput scenarios (e.g., in-memory caches).

**Decision guide:**

- Read:write ratio < 10:1 -> ReentrantLock is fine
- 10:1 to 100:1 -> ReentrantReadWriteLock
- \> 100:1 and lock-free read is critical -> StampedLock


**Level 5 - Distinguished (expert thinking):**
[TODO: Cross-domain pattern recognition. Expert heuristics.
 What would you change if redesigning today?
 How does this compose at extreme scale?]

---

### How It Works (Mechanism)

[TODO: Internal mechanics. Data flow. Key steps.
 4-8 sentences covering implementation details.]

---

### Complete Picture - End-to-End Flow

**NORMAL FLOW:**
[TODO] -> [TODO] -> [THIS CONCEPT <- YOU ARE HERE]
       -> [TODO]

**FAILURE PATH:**
[TODO: cascade -> observable symptom]

**WHAT CHANGES AT SCALE:**
[TODO: 2-3 sentences on behaviour at 10x/100x/1000x load.]

---

### Quick Reference Card

**WHAT IT IS:** [TODO]
**PROBLEM IT SOLVES:** [TODO]
**KEY INSIGHT:** [TODO]
**USE WHEN:** [TODO]
**AVOID WHEN:** [TODO]
**ANTI-PATTERN:** [TODO]
**TRADE-OFF:** [TODO]
**ONE-LINER:** [TODO]

**If you remember only 3 things:**

1. ReadWriteLock: many readers OR one writer (not both)
2. StampedLock: optimistic reads avoid lock overhead entirely
3. StampedLock is NOT reentrant - use carefully

**Interview one-liner:**
"ReadWriteLock enables concurrent reads with exclusive writes; StampedLock adds optimistic reading for ultra-high read throughput but sacrifices reentrancy and condition support."

---

### The Surprising Truth

[TODO: 2-4 sentences. One counterintuitive fact.
 Specific. Makes this concept permanently memorable.]

---

### Interview Deep-Dive

**Q1: When does ReadWriteLock hurt performance?**

_Why they ask:_ Tests awareness of lock overhead.

_Strong answer:_

ReadWriteLock is worse than ReentrantLock when:

1. Writes are frequent (readers constantly blocked)
2. Read critical sections are very short (lock overhead > actual read time)
3. Low contention (ReentrantLock is simpler and faster)

The read lock has overhead: it must atomically increment a reader count and check for writers. For very short reads (single field access), this overhead exceeds the benefit of concurrency. Use AtomicReference or volatile instead.

---

**Q2: Explain optimistic read in StampedLock.**

_Why they ask:_ Tests advanced locking knowledge.

_Strong answer:_

Optimistic read doesn't actually acquire any lock:

1. Get a stamp (`tryOptimisticRead()`) - just reads a version number
2. Read shared data (no lock held!)
3. Validate stamp (`validate(stamp)`) - checks if any write occurred
4. If valid: use the data (zero lock overhead!)
5. If invalid: fall back to a real read lock

This is ideal for read-dominated workloads where writes are rare. The common path (no concurrent write) has zero locking overhead - just a version number check.

---

### Comparison Table

[TODO: Include if 2+ named alternatives exist for ReadWriteLock and StampedLock. Otherwise remove this section.]

---

### Common Misconceptions

| # | Misconception | Reality |
|---|---------------|---------|
| 1 | [TODO] | [TODO] |
| 2 | [TODO] | [TODO] |
| 3 | [TODO] | [TODO] |
| 4 | [TODO] | [TODO] |

---

### Failure Modes and Diagnosis

**Failure Mode 1: [TODO]**
**Symptom:** [TODO]
**Root Cause:** [TODO]
**Diagnostic:**
```
[TODO: real diagnostic command]
```
**Fix:** [TODO: BAD then GOOD]
**Prevention:** [TODO]

**Failure Mode 2: [TODO]**
**Symptom:** [TODO]
**Root Cause:** [TODO]
**Diagnostic:**
```
[TODO: real diagnostic command]
```
**Fix:** [TODO: BAD then GOOD]
**Prevention:** [TODO]

**Failure Mode 3: [TODO]**
**Symptom:** [TODO]
**Root Cause:** [TODO]
**Diagnostic:**
```
[TODO: real diagnostic command]
```
**Fix:** [TODO: BAD then GOOD]
**Prevention:** [TODO]

---

### Related Keywords

**Prerequisites (understand these first):**
- [TODO] - [why needed]
- [TODO] - [why needed]

**Builds on this (learn these next):**
- [TODO] - [what it adds]
- [TODO] - [what it adds]

**Alternatives / Comparisons:**
- [TODO] - [when to prefer it]
- [TODO] - [when to prefer it]


---

---

# Atomic Variables and CAS

**TL;DR** - Atomic classes (`AtomicInteger`, `AtomicReference`, etc.) provide lock-free thread-safe operations using Compare-And-Swap (CAS), a hardware CPU instruction that atomically updates a value only if it matches an expected value.

---

### The Problem This Solves

**WORLD WITHOUT IT:**
Incrementing a counter requires a lock. Under high contention, threads spend more time waiting for the lock than doing actual work. A simple counter becomes a scalability bottleneck.

**THE INVENTION MOMENT:**
"This is exactly why lock-free CAS operations were created."

---

### Textbook Definition

[TODO: 2-4 sentences. Formal. Technically precise.]

---

### Understand It in 30 Seconds

**One line:**
[TODO: 15 words max. Zero jargon.]

**One analogy:**
> [TODO: 2-3 sentence real-world analogy.]

**One insight:**
[TODO: What separates knowing the name from understanding it.]

---

### First Principles Explanation

**CORE INVARIANTS:**
1. [TODO: Always true about this concept]
2. [TODO: Always true about this concept]
3. [TODO: Always true about this concept]

**DERIVED DESIGN:**
[TODO: How the invariants force the design.]

**THE TRADE-OFFS:**
**Gain:** [TODO]
**Cost:** [TODO]

**ESSENTIAL vs ACCIDENTAL COMPLEXITY:**
**Essential:** [TODO]
**Accidental:** [TODO]

---

### Mental Model / Analogy

> [TODO: Primary analogy in blockquote.]

- "[TODO: Analogy element]" -> [technical element]
- "[TODO: Analogy element]" -> [technical element]
- "[TODO: Analogy element]" -> [technical element]

Where this analogy breaks down: [TODO: 1 sentence.]

---

### Gradual Depth - Five Levels

**Level 1 - What it is (anyone can understand):**
CAS is like a conditional update: "Change this value from 5 to 6, but only if it's still 5. If someone already changed it, tell me and I'll retry."

**Level 2 - How to use it (junior developer):**

```java
AtomicInteger counter = new AtomicInteger(0);

// Thread-safe increment (no lock!)
counter.incrementAndGet();  // atomic
counter.getAndAdd(5);       // atomic

AtomicReference<Config> config =
    new AtomicReference<>(initialConfig);

// Thread-safe swap
config.set(newConfig);
Config old = config.getAndSet(newConfig);
```

**Level 3 - How it works (mid-level engineer):**

CAS is a CPU instruction (CMPXCHG on x86):

```
CAS(address, expectedValue, newValue):
  ATOMICALLY:
    if memory[address] == expectedValue:
        memory[address] = newValue
        return true  // success
    else:
        return false // someone else changed it
```

AtomicInteger.incrementAndGet() is a CAS loop:

```java
public int incrementAndGet() {
    int prev, next;
    do {
        prev = get();        // read current
        next = prev + 1;     // compute new
    } while (!compareAndSet(prev, next));
    // retry if another thread changed it
    return next;
}
```

**Level 4 - Mastery (senior/staff+ engineer):**

**ABA problem:** CAS checks value equality, not identity. If value changes A -> B -> A, CAS thinks nothing happened. Solution: `AtomicStampedReference` (adds version counter).

**CAS vs Lock tradeoffs:**

| Aspect          | CAS                     | Lock             |
| --------------- | ----------------------- | ---------------- |
| Contention      | Spins (wastes CPU)      | Blocks (no CPU)  |
| Low contention  | Faster (no park/unpark) | Slower (OS call) |
| High contention | Degrades (spin storm)   | Fair (queue)     |
| Compound ops    | Must fit in one CAS     | Any complexity   |

**Java 9+ VarHandle for advanced CAS:**

```java
private static final VarHandle COUNT;
static {
    COUNT = MethodHandles.lookup()
        .findVarHandle(MyClass.class,
            "count", int.class);
}
COUNT.compareAndSet(this, expected, newVal);
```

**LongAdder** for high-contention counters:

```java
// Better than AtomicLong under contention
LongAdder adder = new LongAdder();
adder.increment(); // distributes across cells
long total = adder.sum(); // eventual read
```


**Level 5 - Distinguished (expert thinking):**
[TODO: Cross-domain pattern recognition. Expert heuristics.
 What would you change if redesigning today?
 How does this compose at extreme scale?]

---

### How It Works (Mechanism)

[TODO: Internal mechanics. Data flow. Key steps.
 4-8 sentences covering implementation details.]

---

### Complete Picture - End-to-End Flow

**NORMAL FLOW:**
[TODO] -> [TODO] -> [THIS CONCEPT <- YOU ARE HERE]
       -> [TODO]

**FAILURE PATH:**
[TODO: cascade -> observable symptom]

**WHAT CHANGES AT SCALE:**
[TODO: 2-3 sentences on behaviour at 10x/100x/1000x load.]

---

### Code Example

**BAD - Lock for simple counter:**

```java
private int count;
private final Object lock = new Object();
public void increment() {
    synchronized (lock) {
        count++;
    }
}
```

**GOOD - Lock-free with AtomicInteger:**

```java
private final AtomicInteger count =
    new AtomicInteger(0);
public void increment() {
    count.incrementAndGet(); // CAS loop
}
```

**BEST - High contention: LongAdder:**

```java
private final LongAdder count = new LongAdder();
public void increment() {
    count.increment(); // distributed cells
}
public long getCount() {
    return count.sum();
}
```

---

### Quick Reference Card

**WHAT IT IS:** [TODO]
**PROBLEM IT SOLVES:** [TODO]
**KEY INSIGHT:** [TODO]
**USE WHEN:** [TODO]
**AVOID WHEN:** [TODO]
**ANTI-PATTERN:** [TODO]
**TRADE-OFF:** [TODO]
**ONE-LINER:** [TODO]

**If you remember only 3 things:**

1. CAS = "change if unchanged, retry if not" - no lock needed
2. Good for low contention; under high contention LongAdder is better
3. ABA problem exists - use AtomicStampedReference if value identity matters

**Interview one-liner:**
"CAS provides lock-free atomicity via a hardware compare-and-swap instruction, optimal for low-contention updates, but degrades under high contention where LongAdder's cell-based approach excels."

---

### The Surprising Truth

[TODO: 2-4 sentences. One counterintuitive fact.
 Specific. Makes this concept permanently memorable.]

---

### Interview Deep-Dive

**Q1: Explain the ABA problem and how to solve it.**

_Why they ask:_ Tests deep CAS understanding.

_Strong answer:_

ABA: Thread 1 reads value A. Thread 2 changes A->B->A. Thread 1's CAS succeeds because value is A again, but the state may have changed in a way that matters (e.g., a linked list node was removed and re-added).

```java
// Dangerous: node might be recycled
AtomicReference<Node> head = ...;
Node a = head.get();      // reads node A
// Another thread removes A, adds new A
head.compareAndSet(a, newNode); // succeeds!
// But 'a' might point to recycled memory
```

Solution: `AtomicStampedReference<V>`:

```java
AtomicStampedReference<Node> head =
    new AtomicStampedReference<>(node, 0);
int[] stamp = new int[1];
Node ref = head.get(stamp);
// CAS checks BOTH reference AND stamp
head.compareAndSet(ref, newNode,
    stamp[0], stamp[0] + 1);
```

---

**Q2: When would you use LongAdder instead of AtomicLong?**

_Why they ask:_ Tests performance engineering knowledge.

_Strong answer:_

AtomicLong: single memory location, all threads CAS on same value. Under contention, CAS failure rate is high, threads spin-retry, throughput drops.

LongAdder: distributes updates across multiple cells (one per CPU). Each thread increments its own cell. `sum()` aggregates all cells.

- AtomicLong: faster for single-thread, slower under contention
- LongAdder: slower for single-thread (allocation), much faster under contention

Use LongAdder for: counters, metrics, request counts - any high-write, infrequent-read scenario.
Use AtomicLong for: sequences (need exact value), low-contention counters, when `sum()` must be precise at call time.

---

### Comparison Table

[TODO: Include if 2+ named alternatives exist for Atomic Variables and CAS. Otherwise remove this section.]

---

### Common Misconceptions

| # | Misconception | Reality |
|---|---------------|---------|
| 1 | [TODO] | [TODO] |
| 2 | [TODO] | [TODO] |
| 3 | [TODO] | [TODO] |
| 4 | [TODO] | [TODO] |

---

### Failure Modes and Diagnosis

**Failure Mode 1: [TODO]**
**Symptom:** [TODO]
**Root Cause:** [TODO]
**Diagnostic:**
```
[TODO: real diagnostic command]
```
**Fix:** [TODO: BAD then GOOD]
**Prevention:** [TODO]

**Failure Mode 2: [TODO]**
**Symptom:** [TODO]
**Root Cause:** [TODO]
**Diagnostic:**
```
[TODO: real diagnostic command]
```
**Fix:** [TODO: BAD then GOOD]
**Prevention:** [TODO]

**Failure Mode 3: [TODO]**
**Symptom:** [TODO]
**Root Cause:** [TODO]
**Diagnostic:**
```
[TODO: real diagnostic command]
```
**Fix:** [TODO: BAD then GOOD]
**Prevention:** [TODO]

---

### Related Keywords

**Prerequisites (understand these first):**
- [TODO] - [why needed]
- [TODO] - [why needed]

**Builds on this (learn these next):**
- [TODO] - [what it adds]
- [TODO] - [what it adds]

**Alternatives / Comparisons:**
- [TODO] - [when to prefer it]
- [TODO] - [when to prefer it]


---

---

# ThreadLocal

**TL;DR** - ThreadLocal provides per-thread variable storage where each thread has its own independent copy, eliminating synchronization by eliminating sharing.

---

### The Problem This Solves

**WORLD WITHOUT IT:**
`SimpleDateFormat` is not thread-safe. To use it in a multi-threaded server, you either synchronize (bottleneck), create a new instance per call (expensive GC pressure), or somehow give each thread its own instance. ThreadLocal solves the third approach.

**THE INVENTION MOMENT:**
"This is exactly why ThreadLocal was created."

---

### Textbook Definition

[TODO: 2-4 sentences. Formal. Technically precise.]

---

### Understand It in 30 Seconds

**One line:**
[TODO: 15 words max. Zero jargon.]

**One analogy:**
> [TODO: 2-3 sentence real-world analogy.]

**One insight:**
[TODO: What separates knowing the name from understanding it.]

---

### First Principles Explanation

**CORE INVARIANTS:**
1. [TODO: Always true about this concept]
2. [TODO: Always true about this concept]
3. [TODO: Always true about this concept]

**DERIVED DESIGN:**
[TODO: How the invariants force the design.]

**THE TRADE-OFFS:**
**Gain:** [TODO]
**Cost:** [TODO]

**ESSENTIAL vs ACCIDENTAL COMPLEXITY:**
**Essential:** [TODO]
**Accidental:** [TODO]

---

### Mental Model / Analogy

> [TODO: Primary analogy in blockquote.]

- "[TODO: Analogy element]" -> [technical element]
- "[TODO: Analogy element]" -> [technical element]
- "[TODO: Analogy element]" -> [technical element]

Where this analogy breaks down: [TODO: 1 sentence.]

---

### Gradual Depth - Five Levels

**Level 1 - What it is (anyone can understand):**
Each thread gets its own private copy of a variable. No sharing = no race conditions.

**Level 2 - How to use it (junior developer):**

```java
private static final ThreadLocal<SimpleDateFormat>
    dateFormat = ThreadLocal.withInitial(
        () -> new SimpleDateFormat("yyyy-MM-dd"));

public String format(Date date) {
    return dateFormat.get().format(date);
    // Each thread has its own formatter
}
```

**Level 3 - How it works (mid-level engineer):**

Each Thread object has a `ThreadLocalMap`:

```
Thread object:
  threadLocals: ThreadLocalMap
    [ThreadLocal@1] -> "value for this thread"
    [ThreadLocal@2] -> dateFormatter instance
```

`threadLocal.get()`:

1. Get current thread
2. Get that thread's ThreadLocalMap
3. Look up this ThreadLocal instance as key
4. Return the associated value

Common uses:

- Per-thread request context (user, tenant, trace ID)
- Non-thread-safe objects (DateFormat, Random)
- Database connections in non-pool environments
- Transaction context in frameworks

**Level 4 - Mastery (senior/staff+ engineer):**

**Memory leak trap:**
In thread pools, threads are reused. ThreadLocal values persist across task executions. If you set a ThreadLocal but never remove it:

1. The value stays in the thread's map forever
2. If the value references large objects -> memory leak
3. If the value has stale data -> logic bugs

```java
// CRITICAL: Always clean up in thread pools
private static final ThreadLocal<Context> ctx =
    new ThreadLocal<>();

public void handleRequest(Request req) {
    ctx.set(new Context(req));
    try {
        process();
    } finally {
        ctx.remove(); // MUST remove!
    }
}
```

**Virtual threads problem:**
With virtual threads, you might have millions of threads. Each with a ThreadLocal copy = millions of copies = massive memory usage. Java 21 introduces `ScopedValue` as a replacement.

**InheritableThreadLocal:** Child threads inherit parent's values. But with executors, this breaks because the "parent" is whatever thread submitted the task, not logically related. Libraries like `TransmittableThreadLocal` solve this.


**Level 5 - Distinguished (expert thinking):**
[TODO: Cross-domain pattern recognition. Expert heuristics.
 What would you change if redesigning today?
 How does this compose at extreme scale?]

---

### How It Works (Mechanism)

[TODO: Internal mechanics. Data flow. Key steps.
 4-8 sentences covering implementation details.]

---

### Complete Picture - End-to-End Flow

**NORMAL FLOW:**
[TODO] -> [TODO] -> [THIS CONCEPT <- YOU ARE HERE]
       -> [TODO]

**FAILURE PATH:**
[TODO: cascade -> observable symptom]

**WHAT CHANGES AT SCALE:**
[TODO: 2-3 sentences on behaviour at 10x/100x/1000x load.]

---

### Code Example

**BAD - ThreadLocal leak in thread pool:**

```java
ThreadLocal<UserSession> session =
    new ThreadLocal<>();

executor.submit(() -> {
    session.set(currentUser());
    handleRequest();
    // LEAK: never removed!
    // Next task on this thread sees stale session
});
```

**GOOD - Always remove in finally:**

```java
executor.submit(() -> {
    session.set(currentUser());
    try {
        handleRequest();
    } finally {
        session.remove(); // clean up
    }
});
```

---

### Quick Reference Card

**WHAT IT IS:** [TODO]
**PROBLEM IT SOLVES:** [TODO]
**KEY INSIGHT:** [TODO]
**USE WHEN:** [TODO]
**AVOID WHEN:** [TODO]
**ANTI-PATTERN:** [TODO]
**TRADE-OFF:** [TODO]
**ONE-LINER:** [TODO]

**If you remember only 3 things:**

1. ThreadLocal = per-thread copy, no synchronization needed
2. ALWAYS `remove()` in finally with thread pools (memory leak + stale data)
3. With virtual threads, prefer ScopedValue (Java 21)

**Interview one-liner:**
"ThreadLocal provides per-thread isolated storage, eliminating synchronization by eliminating sharing, but requires explicit cleanup in thread pools to prevent leaks and stale data."

---

### The Surprising Truth

ThreadLocal values are stored in the Thread object itself, not in the ThreadLocal variable. When a thread dies, its ThreadLocalMap is garbage collected. But in thread pools, threads never die - so ThreadLocal values accumulate indefinitely unless explicitly removed. This is the #1 cause of memory leaks in Java web applications.

---

### Interview Deep-Dive

**Q1: How does Spring use ThreadLocal internally?**

_Why they ask:_ Tests framework knowledge and practical awareness.

_Strong answer:_

Spring uses ThreadLocal extensively:

1. `RequestContextHolder` - stores current HTTP request/response
2. `TransactionSynchronizationManager` - stores current transaction, connection
3. `SecurityContextHolder` (Spring Security) - stores authenticated user
4. `LocaleContextHolder` - stores current locale

```java
// How Spring Security stores the user
SecurityContext ctx = SecurityContextHolder
    .getContext(); // ThreadLocal.get()
Authentication auth = ctx.getAuthentication();
```

This means: if you spawn a new thread, you lose all Spring context. You must explicitly propagate. In async methods (`@Async`), Spring does this automatically via `DelegatingSecurityContextExecutor`.

---

**Q2: What is ScopedValue and why does it replace ThreadLocal?**

_Why they ask:_ Tests modern Java knowledge.

_Strong answer:_

ScopedValue (Java 21, preview):

1. **Immutable within scope** - set once, can't be changed
2. **Automatically cleaned up** - scope exit removes value
3. **Inherited by child threads** - works with structured concurrency
4. **Memory efficient** - no map per virtual thread

```java
static final ScopedValue<User> CURRENT_USER =
    ScopedValue.newInstance();

ScopedValue.where(CURRENT_USER, user)
    .run(() -> {
        // CURRENT_USER.get() returns user
        handleRequest();
        // Automatically cleaned up at scope exit
    });
```

Benefits over ThreadLocal:

- No memory leak possible (auto-cleanup)
- No stale data bugs (immutable in scope)
- Efficient with millions of virtual threads
- Clear lifecycle (scoped, not unbounded)

---

### Comparison Table

[TODO: Include if 2+ named alternatives exist for ThreadLocal. Otherwise remove this section.]

---

### Common Misconceptions

| # | Misconception | Reality |
|---|---------------|---------|
| 1 | [TODO] | [TODO] |
| 2 | [TODO] | [TODO] |
| 3 | [TODO] | [TODO] |
| 4 | [TODO] | [TODO] |

---

### Failure Modes and Diagnosis

**Failure Mode 1: [TODO]**
**Symptom:** [TODO]
**Root Cause:** [TODO]
**Diagnostic:**
```
[TODO: real diagnostic command]
```
**Fix:** [TODO: BAD then GOOD]
**Prevention:** [TODO]

**Failure Mode 2: [TODO]**
**Symptom:** [TODO]
**Root Cause:** [TODO]
**Diagnostic:**
```
[TODO: real diagnostic command]
```
**Fix:** [TODO: BAD then GOOD]
**Prevention:** [TODO]

**Failure Mode 3: [TODO]**
**Symptom:** [TODO]
**Root Cause:** [TODO]
**Diagnostic:**
```
[TODO: real diagnostic command]
```
**Fix:** [TODO: BAD then GOOD]
**Prevention:** [TODO]

---

### Related Keywords

**Prerequisites (understand these first):**
- [TODO] - [why needed]
- [TODO] - [why needed]

**Builds on this (learn these next):**
- [TODO] - [what it adds]
- [TODO] - [what it adds]

**Alternatives / Comparisons:**
- [TODO] - [when to prefer it]
- [TODO] - [when to prefer it]

