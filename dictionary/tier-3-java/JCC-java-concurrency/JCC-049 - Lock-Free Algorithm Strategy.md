---
id: JCC-049
title: Lock-Free Algorithm Strategy
category: Java Concurrency
tier: tier-3-java
folder: JCC-java-concurrency
difficulty: ★★★
depends_on: JCC-022, JCC-023, JCC-039, JCC-038
used_by: JCC-052
related: JCC-022, JCC-038, JCC-052
tags:
  - java
  - concurrency
  - advanced
  - algorithm
  - performance
  - bestpractice
status: complete
version: 1
layout: default
parent: "Java Concurrency"
grand_parent: "Technical Dictionary"
nav_order: 49
permalink: /jcc/lock-free-algorithm-strategy/
---

# JCC-049 - Lock-Free Algorithm Strategy

⚡ TL;DR - Lock-free algorithms use Compare-And-Swap (CAS) loops to achieve thread safety without blocking any thread - eliminating deadlock, priority inversion, and lock contention at the cost of higher implementation complexity.

| Metadata        |                                    |     |
| :-------------- | :--------------------------------- | :-- |
| **Depends on:** | JCC-022, JCC-023, JCC-039, JCC-038 |     |
| **Used by:**    | JCC-052                            |     |
| **Related:**    | JCC-022, JCC-038, JCC-052          |     |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
Every shared data structure needs a lock for thread safety. Under contention, threads wait for the lock. A thread holding the lock that is preempted, paused by GC, or running slowly causes ALL other threads to wait. This is lock contention. At high concurrency (hundreds of threads competing for one lock), throughput collapses as threads spend more time waiting than working.

**THE BREAKING POINT:**
A high-throughput counter shared by 1,000 threads. With `synchronized`, threads queue for the lock. Throughput: ~50M increments/second. With `AtomicLong` (lock-free CAS): ~400M increments/second. An 8x throughput difference - purely from eliminating lock contention.

**THE INVENTION MOMENT:**
Lock-free algorithms leverage hardware support - the Compare-And-Swap (CAS) instruction available on all modern CPUs. CAS atomically checks a value and updates it only if it matches the expected value. If another thread changed the value, CAS fails and the operation retries. No thread ever blocks - they retry instead. This trades blocking for retrying, which is far more scalable.

**EVOLUTION:**
Java 5: `AtomicInteger`, `AtomicLong`, `AtomicReference` (lock-free using `sun.misc.Unsafe`). Java 9: `VarHandle` provides standardized, safe CAS operations without `Unsafe`. Java 21: Virtual Threads reduce the cost of blocking, making lock-free less critical for I/O-bound code, but it remains essential for CPU-intensive concurrent operations.

---

### 📘 Textbook Definition

**Lock-free algorithms** are concurrent algorithms where at least one thread makes progress at any point in time, regardless of what other threads are doing. They achieve thread safety without mutual exclusion locks by using atomic hardware instructions (CAS). The key property is **non-blocking**: no thread can prevent another from making progress indefinitely. In Java, lock-free algorithms are implemented using `AtomicInteger`, `AtomicLong`, `AtomicReference`, `VarHandle`, or the lower-level `sun.misc.Unsafe` (internal). The strategy involves: read current value, compute new value, CAS to apply - and retry if CAS fails.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
Lock-free = use CAS to update shared state without blocking: read, compute, CAS, retry if someone else changed it first.

**One analogy:**

> Lock-free algorithms are like optimistic bank tellers: instead of locking the vault (blocking everyone), each teller reads the balance, computes the new balance, and posts the update - but only if the balance has not changed since they read it. If it changed (another teller updated first), they re-read and try again. No one waits for a vault key.

**One insight:**
Lock-free does not eliminate contention - it transforms it from blocking (thread sleeps waiting for lock) to spinning (thread retries CAS). At low-to-moderate contention, retries are rare and throughput is high. At extreme contention, retries multiply and lock-free may not outperform locked.

---

### 🔩 First Principles Explanation

**CORE INVARIANTS:**

1. **CAS is the fundamental primitive** - `compareAndSet(expected, update)` succeeds only if current value equals `expected`; otherwise fails atomically. This provides check-and-act atomicity without a lock.
2. **Lock-free guarantees system-wide progress** - at least one thread makes progress always. Under lock, a paused thread blocks all others. Under lock-free, a paused thread just fails to update; others succeed.
3. **The ABA problem is a real hazard** - if value changes A -> B -> A, a CAS expecting A will succeed even though the state changed. Use `AtomicStampedReference` to detect intermediate changes.
4. **Lock-free does not mean wait-free** - lock-free guarantees progress for the system; wait-free guarantees progress for every individual thread. Lock-free algorithms have retry loops; wait-free do not.

**DERIVED DESIGN:**
Given invariant 3 (ABA): any lock-free algorithm on references must assess whether intermediate mutation matters. For immutable objects, ABA is harmless. For mutable objects (lists, trees), ABA can corrupt structure. Use `AtomicStampedReference` with a version counter.

Given invariant 1 (CAS primitive): the universal lock-free template is:

```
do {
    expected = read current value
    newValue  = compute(expected)
} while (!CAS(expected, newValue));
```

**THE TRADE-OFFS:**
**Gain:** No deadlock possible, no priority inversion, no lock convoy, high throughput under moderate contention.
**Cost:** Higher implementation complexity, ABA hazard, starvation possible, harder to compose multiple operations atomically.

**ESSENTIAL vs ACCIDENTAL COMPLEXITY:**
**Essential:** Concurrent modification of shared state requires some form of coordination.
**Accidental:** CAS retry loops and ABA detection. `java.util.concurrent.atomic` package hides most of this for common cases.

---

### 🧪 Thought Experiment

**SETUP:**
Implement a thread-safe counter that 100 threads increment 1,000,000 times each. Target: correctness and maximum throughput.

**WITH `synchronized` (lock-based):**

```java
private long count = 0;
public synchronized void increment() { count++; }
// Throughput: ~50M ops/sec
// 99 threads wait while 1 holds the lock
```

**WITH `AtomicLong` (lock-free CAS):**

```java
private AtomicLong count = new AtomicLong(0);
public void increment() {
    count.incrementAndGet(); // CAS loop internally
}
// Throughput: ~400M ops/sec
// No thread blocks another
```

**WITH `LongAdder` (striped lock-free):**

```java
private LongAdder count = new LongAdder();
public void increment() {
    count.increment(); // per-core cell, minimal CAS failure
}
// Throughput: ~2B ops/sec
// sum() aggregates all cells
```

**THE INSIGHT:**
For high-contention increment, `LongAdder` wins by reducing contention per cell. `AtomicLong` is better when you need the current value frequently. `synchronized` is the slowest for increment-only workloads.

---

### 🧠 Mental Model / Analogy

> Lock-free algorithms are like online flight seat booking without a lock. Two customers simultaneously see seat 12A available. Customer A's booking succeeds (CAS succeeds - seat was available). Customer B's booking fails (CAS fails - seat now taken). Customer B retries, finds 12B available, and books it. Neither was blocked. Both made progress.

Element mapping:

- **Checking seat availability** = reading current state
- **Booking attempt** = CAS operation
- **"Seat taken" failure** = CAS failure (another thread updated first)
- **Retrying with another seat** = retry loop with re-read
- **No waiting** = the lock-free property

Where this analogy breaks down: booking two seats atomically together requires composing operations - which lock-free cannot do across multiple values without careful design.

---

### 📶 Gradual Depth - Four Levels

**Level 1 - What it is (anyone can understand):**
Lock-free means threads do not wait for each other. Instead of one thread locking a door while others wait, all threads try simultaneously. If two conflict, one retries instantly - no sleeping.

**Level 2 - How to use it (junior developer):**
Use `java.util.concurrent.atomic` classes. For counters: `AtomicLong` or `LongAdder`. For object references: `AtomicReference`.

```java
AtomicInteger count = new AtomicInteger(0);
count.incrementAndGet();
count.compareAndSet(10, 20); // set to 20 if currently 10
```

**Level 3 - How it works (mid-level engineer):**
`AtomicInteger.incrementAndGet()` calls `VarHandle.compareAndSet(this, expected, expected+1)` in a loop. The CAS is a single CPU instruction (`CMPXCHG` on x86). If the cache line containing the value is uncontested, CAS succeeds first try (2-3 CPU cycles). Under contention, cache coherency protocol causes cache line bouncing between cores.

**Level 4 - Why it was designed this way (senior/staff):**
Lock-free is faster because acquiring a contended lock causes the OS to sleep the thread (context switch ~100 microseconds). CAS failure causes a CPU retry (~2-10 nanoseconds). The 10,000x latency difference makes CAS-based retry far cheaper than sleep/wakeup for short-duration operations. This is why lock-free is optimal for nanosecond operations but wasteful for millisecond critical sections.

**Expert Thinking Cues:**

- "How long is the critical section? Nanoseconds: lock-free. Milliseconds: mutex."
- "Is ABA a concern? If the value represents a reference to a mutable object, use `AtomicStampedReference`."
- "High-write-low-read? Use `LongAdder`. Balanced read/write? Use `AtomicLong`."

---

### ⚙️ How It Works (Mechanism)

**THE UNIVERSAL CAS LOOP:**

```java
AtomicReference<State> stateRef =
    new AtomicReference<>(initial);

// Lock-free update template
public void update(Function<State, State> transform) {
    State current, next;
    do {
        current = stateRef.get();      // read
        next    = transform(current);  // compute (pure)
    } while (
        !stateRef.compareAndSet(current, next) // CAS
    );
}
```

**ABA PROBLEM AND FIX:**

```java
// Problem: A -> B -> A fools CAS
AtomicReference<Node> head = new AtomicReference<>(nodeA);
// Thread 1 reads head=A, prepares to swap to nodeC
// Thread 2: removes A, removes B, re-adds A
// Thread 1's CAS(nodeA, nodeC) wrongly succeeds

// Fix: version counter via AtomicStampedReference
AtomicStampedReference<Node> head =
    new AtomicStampedReference<>(nodeA, 0);
int[] stamp = new int[1];
Node current = head.get(stamp);
head.compareAndSet(
    current, newNode, stamp[0], stamp[0] + 1
);
```

---

### 🔄 The Complete Picture - End-to-End Flow

**LOCK-FREE CAS FLOW:**

```
Thread A: atomicLong.incrementAndGet()
    |
    +- Read current value (e.g., 42)
    +- Compute new value (43)
    +- CAS(42, 43)
         |
         +- If cache line uncontested:
         |    CAS succeeds -> return 43
         |
         +- If Thread B updated concurrently:
              CAS fails (value is now 43, not 42)
              Retry: read 43, compute 44
                           <- YOU ARE HERE
              CAS(43, 44) -> succeeds
```

**FAILURE PATH:**
Extreme contention (1,000 threads, one `AtomicLong`): most CAS attempts fail on first try. Threads spin in retry loops. CPU usage high; useful work low. Fix: `LongAdder` (strips contention) or reduce thread count competing for the value.

**WHAT CHANGES AT SCALE:**
At distributed scale, CAS semantics do not cross JVM boundaries. Distributed lock-free requires distributed coordination algorithms (Raft, optimistic DB transactions, ETags).

---

### ⚖️ Comparison Table

| Approach                 | Blocking | Deadlock-free | ABA Risk          | Best For                              |
| ------------------------ | -------- | ------------- | ----------------- | ------------------------------------- |
| `synchronized`           | Yes      | No            | No                | Complex logic, long critical sections |
| `AtomicLong`             | No       | Yes           | No (primitives)   | Counters, flags                       |
| `AtomicReference`        | No       | Yes           | Yes (mutable obj) | Single reference                      |
| `AtomicStampedReference` | No       | Yes           | No                | ABA-sensitive references              |
| `LongAdder`              | No       | Yes           | No                | High-write counters                   |
| `VarHandle`              | No       | Yes           | Depends           | Custom lock-free structures           |

---

### ⚠️ Common Misconceptions

| Misconception                           | Reality                                                                                                                                                   |
| --------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------- |
| "Lock-free is always faster than locks" | Lock-free is faster under moderate contention. For long critical sections, OS-managed sleep is more efficient than CPU spinning on repeated CAS failures. |
| "Lock-free means no contention"         | Lock-free eliminates blocking, not contention. Under high contention, CAS failure rates rise and CPUs burn on retry loops.                                |
| "All lock-free algorithms are ABA-safe" | ABA is a specific hazard for lock-free linked structures. Simple counter operations have no ABA risk. Reference-based stacks and queues are vulnerable.   |
| "`volatile` makes a variable lock-free" | `volatile` provides visibility but not atomicity. `volatile++` is read + compute + write (3 ops, not atomic). Use `AtomicInteger` for atomic increment.   |
| "CAS is a Java concept"                 | CAS is a CPU instruction (`CMPXCHG` on x86). Java exposes it through `AtomicXxx` and `VarHandle`. It exists in every modern language and OS.              |

---

### 🚨 Failure Modes & Diagnosis

**Failure Mode 1: Livelock from CAS Spinning**
**Symptom:** High CPU, near-zero throughput. Thread dumps show tight retry loops.
**Root Cause:** Extreme CAS contention. Many threads invalidate each other's CAS attempts continuously.
**Diagnostic:**

```bash
# CPU profiler shows time in CAS loops
async-profiler -d 30 -f profile.html <pid>
# Hot: sun.misc.Unsafe.compareAndSwapLong
```

**Fix:**

```java
// BAD: 1000 threads on one AtomicLong
AtomicLong counter = new AtomicLong();

// GOOD: LongAdder strips contention
LongAdder counter = new LongAdder();
```

**Prevention:** For high-write counters with many threads, prefer `LongAdder` over `AtomicLong`.

---

**Failure Mode 2: ABA Corruption in Lock-Free Structure**
**Symptom:** Intermittent data loss or corruption in concurrent push/pop operations.
**Root Cause:** Node A removed, B pushed, A re-added. CAS on old A-pointer succeeds incorrectly.
**Diagnostic:**

```bash
# Add version counters to all reference updates
# Log CAS operations for post-mortem analysis
```

**Fix:**

```java
// BAD: AtomicReference stack - ABA vulnerable
AtomicReference<Node<T>> top = new AtomicReference<>();

// GOOD: AtomicStampedReference with version
AtomicStampedReference<Node<T>> top =
    new AtomicStampedReference<>(null, 0);
```

**Prevention:** Any lock-free structure using `AtomicReference` to nodes that can be removed and re-added must use versioned references.

---

**Failure Mode 3: Non-Atomic Compound Operation**
**Symptom:** Race condition despite using `AtomicReference`. Two threads take concurrent action on what appears to be a valid state.
**Root Cause:** Check and act are two separate operations. Another thread intervenes between them.
**Diagnostic:**

```bash
grep -rn "get().*if.*compareAndSet" src/
# Find check-then-act patterns on atomic values
```

**Fix:**

```java
// BAD: check-then-act - not atomic
if (ref.get().isValid()) {
    ref.set(newValue); // gap: another thread intervenes
}

// GOOD: encode check in CAS expected value
State current = ref.get();
if (current.isValid()) {
    ref.compareAndSet(current, current.withValue(newValue));
}
```

**Prevention:** Compound check-and-act on atomic state must be expressed as a single CAS where the check is encoded in the expected value.

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**

- [[JCC-022 - CAS (Compare-And-Swap)]] - the hardware primitive underlying all lock-free algorithms
- [[JCC-038 - Atomic Classes]] - the standard library lock-free implementations

**Builds On This (learn these next):**

- [[JCC-052 - Lock-Free Data Structure Design]] - applying the strategy to complete data structures

**Alternatives / Comparisons:**

- [[JCC-016 - ReentrantLock]] - when locks outperform lock-free (long critical sections)
- [[JCC-023 - Optimistic Locking (Java)]] - related optimistic approach at a higher level

---

### 📌 Quick Reference Card

```
┌────────────────────────────────────────────────────┐
│ WHAT IT IS    │ CAS-based thread safety without    │
│               │ blocking any thread                │
│ PROBLEM       │ Lock contention at high concurrency│
│ KEY INSIGHT   │ Retry is cheaper than sleep/wakeup │
│ USE WHEN      │ Short ops, high-contention counters│
│ AVOID WHEN    │ Long critical sections (use lock)  │
│ TRADE-OFF     │ Complexity + ABA risk vs. throughput│
│ ONE-LINER     │ Read, compute, CAS, retry on fail  │
│ NEXT EXPLORE  │ JCC-052 Lock-Free Data Structures  │
└────────────────────────────────────────────────────┘
```

**If you remember only 3 things:**

1. Lock-free = CAS loop: read, compute, CAS, retry if CAS fails. No thread ever blocks.
2. ABA hazard: if a value can change A->B->A, use `AtomicStampedReference` to detect it.
3. For high-write counters, `LongAdder` outperforms `AtomicLong` by striping contention across multiple cells.

**Interview one-liner:**
"Lock-free algorithms use Compare-And-Swap to update shared state atomically without blocking any thread - if the CAS fails (another thread updated first), retry from scratch - trading blocking for retrying, which eliminates deadlock and scales better under moderate contention."

---

### 💎 Transferable Wisdom

**Reusable Engineering Principle:**
Optimistic concurrency: read without locking, compute the new state, attempt to commit, and retry if the world changed since you read it. This pattern appears at every level - from CPU CAS instructions to database optimistic locking to distributed transaction protocols.

**Where else this pattern appears:**

- **Database optimistic locking:** Read a record with a version field. Update only if version has not changed (equivalent to CAS on the row). Used by Hibernate, JPA, and SQL `UPDATE WHERE version = ?`.
- **Git pushes:** A push succeeds only if the remote HEAD matches the local base. If another commit was pushed first, the push is rejected and you must pull/rebase (retry with updated state).
- **HTTP ETags:** A conditional PUT (`If-Match: <etag>`) updates a resource only if the ETag matches the current version. Same CAS pattern at the HTTP protocol level.

---

### 💡 The Surprising Truth

The `ConcurrentLinkedQueue` - one of the most commonly used lock-free data structures in Java - is based on a 1996 paper by Maged Michael and Michael Scott: "Simple, Fast, and Practical Non-Blocking and Blocking Concurrent Queue Algorithms." The algorithm handles the ABA problem through careful ordering of pointer updates. The core algorithm fits on one page, yet it took researchers years to formally prove its correctness. This illustrates a key truth about lock-free algorithms: they are often short in code but extremely subtle in reasoning. The code is simple; the correctness argument is not.

---

### 🧠 Think About This Before We Continue

**Q1 (E - First Principles):** `volatile++` is not atomic, but `AtomicInteger.incrementAndGet()` is. Both use `volatile` fields internally. What specifically makes the `AtomicInteger` version atomic when `volatile++` is not?
_Hint:_ Count the number of memory operations in each case. `volatile++` is read + compute + write (3 separate operations). What does `incrementAndGet()` do differently at the hardware level?

**Q2 (B - Scale):** A `LongAdder` has 16 cells under high contention. If 1,000 threads all increment simultaneously, how are they mapped to cells? What does `sum()` guarantee - exact current value or approximate?
_Hint:_ Look at `LongAdder.sum()` - it does not lock. Consider what happens if threads keep incrementing while `sum()` is adding cells.

**Q3 (C - Design Trade-off):** A service has a cache stored as `AtomicReference<Map<String, Profile>>`. Reads are frequent. Updates are infrequent (once per minute). Should you use lock-free CAS on the reference, or a `ReadWriteLock`? What is the key decision factor?
_Hint:_ Consider read-to-write ratio and the cost of creating a new map copy on each CAS-based write. Compare with `ReadWriteLock.readLock()` which allows concurrent reads without copying.
