---
layout: default
title: "Atomic Classes"
parent: "Java Concurrency"
nav_order: 363
permalink: /java-concurrency/atomic-classes/
number: "0363"
category: Java Concurrency
difficulty: ★★★
depends_on: CAS (Compare-And-Swap), Volatile, Thread Safety, Hardware Memory Model
used_by: Lock-Free Algorithms, Counters, ConcurrentHashMap
related: VarHandle, Volatile, Synchronized
tags:
  - java
  - concurrency
  - deep-dive
  - lock-free
  - hardware
---

# 0363 — Atomic Classes

⚡ TL;DR — Java's atomic classes (`AtomicInteger`, `AtomicLong`, `AtomicReference`, etc.) provide lock-free, thread-safe operations on single variables using hardware CAS (Compare-And-Swap) instructions — enabling counter increments, state transitions, and reference swaps without mutexes.

| #0363           | Category: Java Concurrency                                             | Difficulty: ★★★ |
| :-------------- | :--------------------------------------------------------------------- | :-------------- |
| **Depends on:** | CAS (Compare-And-Swap), Volatile, Thread Safety, Hardware Memory Model |                 |
| **Used by:**    | Lock-Free Algorithms, Counters, ConcurrentHashMap                      |                 |
| **Related:**    | VarHandle, Volatile, Synchronized                                      |                 |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
A web server counts requests per endpoint. The naive increment: `count++` compiles to `read → add 1 → write`. With two threads: Thread A reads 100, Thread B reads 100, Thread A writes 101, Thread B writes 101 — the counter should be 102 but is 101. Lost update.

Fix with `synchronized`: works, but every increment goes through the OS mutex subsystem — thread blocking, context switching, kernel mode transitions. For a simple counter incremented 1,000,000 times per second, this is expensive overhead.

**THE BREAKING POINT:**
`synchronized` for a counter is like using a bank vault door to protect a sticky note. The overhead of acquiring a mutex (parking the thread in kernel space, context switching, waking up) is orders of magnitude more expensive than the actual work of incrementing an integer.

**THE INVENTION MOMENT:**
Modern CPUs have a hardware instruction — CAS (Compare-And-Swap) — that atomically reads a memory location, compares it to an expected value, and writes a new value ONLY if the comparison succeeds. This is a single atomic hardware operation. Java's `java.util.concurrent.atomic` package exposes this hardware capability through a clean Java API: the atomic classes.

---

### 📘 Textbook Definition

**Atomic classes:** A group of classes in `java.util.concurrent.atomic` that support lock-free, thread-safe operations on single variables using hardware CAS (Compare-And-Swap) instructions. The core classes: `AtomicBoolean`, `AtomicInteger`, `AtomicLong`, `AtomicReference<V>`, `AtomicIntegerArray`, `AtomicLongArray`, `AtomicReferenceArray<E>`, `AtomicMarkableReference<V>`, `AtomicStampedReference<V>`.

**CAS (Compare-And-Swap):** A CPU instruction that atomically: (1) reads a memory location, (2) compares it to an expected value, (3) if equal, writes a new value. Returns whether the write succeeded. Forms the basis of lock-free algorithms.

**LongAdder:** A high-throughput alternative to `AtomicLong` for cases where the only needed operation is increment/add, using a striped counter approach to reduce CAS contention under high concurrency.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
Atomic classes give you thread-safe increment/swap/compare on a single variable, backed by a hardware instruction — no locks, no blocking.

**One analogy:**

> Atomic classes are like a turnstile at a subway station. Each person (thread) clicks the turnstile once to enter. The turnstile's mechanism guarantees that only one click advances the counter at a time — there's no "two people click simultaneously and both count as one entry" problem. And the turnstile doesn't need a security guard (mutex/lock) to enforce this — the physical mechanism itself is atomic.

**One insight:**
The power of atomic classes is that they turn a "read-modify-write" operation from three separate steps (each observable by other threads) into a single atomic hardware instruction. No other thread can see the value in the intermediate state between read and write. And critically: threads that fail the CAS simply retry — they're never blocked or parked. They spin (briefly), which is much faster than blocking for lock contention at low-to-medium contention levels.

---

### 🔩 First Principles Explanation

**CAS OPERATION (x86: CMPXCHG):**

```
Before: memory[address] = 5
CAS(address, expected=5, newValue=6):
  If memory[address] == 5:
    memory[address] = 6
    return SUCCESS
  Else:
    return FAILURE (memory value unchanged)

Thread A: CAS(addr, 5, 6) → SUCCESS → addr=6
Thread B: CAS(addr, 5, 6) → FAILURE (addr is now 6, not 5) → retry
Thread B: reads addr=6, CAS(addr, 6, 7) → SUCCESS → addr=7
```

**JAVA ATOMIC CLASSES — KEY OPERATIONS:**

```java
AtomicInteger ai = new AtomicInteger(0);

ai.get()                    // volatile read
ai.set(5)                   // volatile write
ai.getAndSet(5)             // atomic swap: returns old, sets new
ai.compareAndSet(expected, update) // CAS: returns boolean success
ai.getAndIncrement()        // atomic i++
ai.incrementAndGet()        // atomic ++i (returns new value)
ai.getAndDecrement()        // atomic i--
ai.decrementAndGet()        // atomic --i
ai.getAndAdd(delta)         // atomic i += delta
ai.addAndGet(delta)         // atomic i += delta (returns new value)
ai.updateAndGet(fn)         // atomic: apply function, return new value
ai.accumulateAndGet(x, fn)  // atomic: apply binary function with x
```

**AtomicReference:**

```java
AtomicReference<Node> head = new AtomicReference<>(null);

// Lock-free push to stack:
void push(Node newHead) {
    Node oldHead;
    do {
        oldHead = head.get();
        newHead.next = oldHead;
    } while (!head.compareAndSet(oldHead, newHead)); // retry if CAS fails
}
```

**THE TRADE-OFFS:**

**Gain:** No thread blocking (lock-free — threads that fail CAS retry, not sleep). No context switching overhead. Hardware-level atomicity. Very fast at low-to-medium contention.

**Cost:** ABA problem (see Failure Modes). Spin-wait under high contention → CPU waste. Only atomic for SINGLE variable — cannot atomically update two fields. CAS can "fail" spuriously under memory bus contention (rare on x86 but possible on ARM).

---

### 🧪 Thought Experiment

**SETUP:**
1,000 threads all incrementing a shared counter 1,000 times each. Expected final value: 1,000,000.

**WITH `volatile int count`:**

```java
volatile int count = 0;
count++;  // read → increment → write: NOT ATOMIC even with volatile
// volatile only guarantees visibility, not atomicity
// Result: far less than 1,000,000 (lost updates)
```

**WITH `synchronized`:**

```java
synchronized(this) { count++; }
// Correct: 1,000,000 final value
// Cost: 1,000 threads × 1,000 ops = 1,000,000 mutex acquisitions
// At 1μs per acquisition: 1 second of pure lock overhead
```

**WITH `AtomicInteger`:**

```java
AtomicInteger count = new AtomicInteger(0);
count.incrementAndGet();
// Correct: 1,000,000 final value
// Cost: CAS instruction (~5–10ns on uncontended, ~50ns on contended)
// At low contention: 5–10x faster than synchronized
// At extreme contention (1,000 threads): CAS retries increase, may approach synchronized
```

**WITH `LongAdder` (best for pure counters):**

```java
LongAdder count = new LongAdder();
count.increment();
// Correct: 1,000,000 final value (from count.sum())
// Cost: distributed cells reduce contention
// At extreme contention: significantly faster than AtomicLong
// Trade-off: sum() aggregates cells → slightly slower to read than AtomicLong.get()
```

---

### 🧠 Mental Model / Analogy

> Atomic classes are like an optimistic vending machine. When you want to buy an item (modify state), you check the current price, decide to buy, then submit: "if the price is still $1.00, deduct $1.00 and give me the item." If someone else changed the price between when you checked and when you submitted, your transaction fails and you retry with the new price. No cashier (lock) is needed — the machine itself guarantees each transaction is atomic.

Explicit mapping:

- "vending machine" → the atomic variable
- "checking price" → `get()` (volatile read)
- "submitting: if price is $X, deduct $X" → `compareAndSet(expected, newValue)` (CAS)
- "transaction fails, retry" → CAS failure → retry loop
- "no cashier needed" → lock-free (no mutex)
- "two buyers simultaneously" → two threads simultaneously CAS — one wins, one retries

Where this analogy breaks down: the ABA problem — the price could change from $1.00 to $2.00 and back to $1.00, and your "$1.00" check would succeed even though the price changed. This is the ABA problem unique to CAS-based algorithms (see Failure Modes).

---

### 📶 Gradual Depth — Four Levels

**Level 1 — What it is (anyone can understand):**
Atomic classes let multiple threads safely update a single number or reference without using a lock. Instead of saying "only one thread can change this at a time" (lock), they use a hardware-level trick to make the change in one uninterruptible step.

**Level 2 — How to use it (junior developer):**
Use `AtomicInteger` or `AtomicLong` for shared counters. Call `incrementAndGet()` for `++count` and `decrementAndGet()` for `--count`. For conditional updates, use `compareAndSet(expected, newValue)`. For high-throughput counters where only the sum matters (not per-thread current value), prefer `LongAdder.increment()` over `AtomicLong.incrementAndGet()`.

**Level 3 — How it works (mid-level engineer):**
Java's atomic classes use `VarHandle` (Java 9+, or `sun.misc.Unsafe` in older JDK internals) to issue CAS instructions. `compareAndSet(expected, update)` compiles to a `CMPXCHG` instruction on x86 or `LDXR/STXR` pair on ARM. The retry loop pattern: read current value → compute new value → CAS(current, new) → if CAS fails (another thread modified it), re-read and retry. This is an optimistic concurrency strategy — assumes low contention, retries on conflict. The `updateAndGet(fn)` and `accumulateAndGet(x, fn)` methods encapsulate this retry loop for you.

**Level 4 — Why it was designed this way (senior/staff):**
The choice of CAS over test-and-set or fetch-and-add is deliberate: CAS is universal — it can implement all other atomic operations (fetch-and-add, fetch-and-or, etc.) but the converse is not true. CAS also enables lock-free data structures (stacks, queues, linked lists) where the shape of the structure changes, not just a numeric value. `AtomicReference` exposes CAS on object references, enabling lock-free algorithms that modify pointer-based data structures. `AtomicStampedReference` adds a version stamp to address the ABA problem — the stamp is updated with every CAS, so `(value=A, stamp=2)` is distinguishable from `(value=A, stamp=0)` even though the value is the same. `LongAdder` (Java 8+) uses a distributed counter with `@Contended` annotation (padding to prevent false sharing) — under high contention, threads stripe their increments across multiple `Cell` objects, reducing CAS contention from O(threads) to O(cells).

---

### ⚙️ How It Works (Mechanism)

```
AtomicInteger.incrementAndGet():

for (;;) {                         // retry loop
    int current = get();           // volatile read of field
    int next = current + 1;
    if (compareAndSet(current, next))  // CAS instruction
        return next;               // SUCCESS: return new value
    // FAIL: another thread modified it → loop and retry
}

HARDWARE CAS on x86 (simplified):
  LOCK CMPXCHG [address], newValue
  // LOCK prefix: prevents other CPUs from accessing the cache line
  // during the compare-and-exchange operation
  // Single bus-locked instruction → atomic at hardware level

LongAdder.increment() under contention:
  Try to CAS the "base" counter (optimistic path)
  If fails (contention): hash thread ID → pick a Cell
  CAS that Cell's value instead
  sum() = base + sum(cells[])
  → N threads can increment N different cells simultaneously
```

---

### 🔄 The Complete Picture — End-to-End Flow

```
AtomicInteger counter = new AtomicInteger(0);

Thread 1: counter.incrementAndGet()
  read: current = 0
  CAS(0 → 1): SUCCESS
  return 1

Thread 2: counter.incrementAndGet()    [concurrent with Thread 1]
  read: current = 0
  CAS(0 → 1): FAIL (Thread 1 already set it to 1)
  RETRY:
  read: current = 1
  CAS(1 → 2): SUCCESS
  return 2

Final state: counter = 2 ✓ (correct)
No thread was blocked. No kernel calls. No context switch.
```

---

### 💻 Code Example

**Example 1 — Counters and state flags:**

```java
import java.util.concurrent.atomic.*;

// Simple counter
AtomicLong requestCount = new AtomicLong(0);
requestCount.incrementAndGet();          // ++count
requestCount.addAndGet(5);               // count += 5
long snapshot = requestCount.get();      // read

// Boolean state flag (e.g., shutdown signal)
AtomicBoolean shuttingDown = new AtomicBoolean(false);
// Ensure only one thread initiates shutdown:
if (shuttingDown.compareAndSet(false, true)) {
    // This block runs EXACTLY ONCE across all threads
    initiateShutdown();
}

// Lazy initialisation (check-then-act, atomic):
AtomicReference<Connection> conn = new AtomicReference<>(null);
Connection connection = conn.get();
if (connection == null) {
    Connection newConn = createConnection();
    // Only set if still null (first thread wins):
    conn.compareAndSet(null, newConn);
    connection = conn.get(); // get the actual connection (ours or another thread's)
}
```

**Example 2 — Lock-free stack using AtomicReference:**

```java
public class LockFreeStack<T> {
    private static class Node<T> {
        T value;
        Node<T> next;
        Node(T value, Node<T> next) { this.value = value; this.next = next; }
    }

    private final AtomicReference<Node<T>> head = new AtomicReference<>();

    public void push(T value) {
        Node<T> newHead = new Node<>(value, null);
        Node<T> oldHead;
        do {
            oldHead = head.get();
            newHead.next = oldHead;
        } while (!head.compareAndSet(oldHead, newHead)); // retry on CAS fail
    }

    public T pop() {
        Node<T> oldHead;
        Node<T> newHead;
        do {
            oldHead = head.get();
            if (oldHead == null) return null; // empty stack
            newHead = oldHead.next;
        } while (!head.compareAndSet(oldHead, newHead));
        return oldHead.value;
    }
}
```

**Example 3 — LongAdder vs AtomicLong benchmark context:**

```java
// HIGH-CONTENTION COUNTER: prefer LongAdder
LongAdder hits = new LongAdder();
hits.increment();               // fast: spreads across cells
long total = hits.sum();        // aggregates all cells

// AtomicLong: fast to read, slower under extreme contention
AtomicLong atomicHits = new AtomicLong(0);
atomicHits.incrementAndGet();   // may spin under 100+ thread contention
long current = atomicHits.get(); // O(1) accurate read

// Rule of thumb:
// Use LongAdder when: many threads increment, reads are rare
// Use AtomicLong when: few threads increment OR you need compareAndSet
```

---

### ⚖️ Comparison Table

| Mechanism              | Lock-free | Blocking | Scope                             | Best for                                      |
| ---------------------- | --------- | -------- | --------------------------------- | --------------------------------------------- |
| **AtomicInteger/Long** | Yes       | No       | Single variable                   | Counters, flags, version stamps               |
| **AtomicReference**    | Yes       | No       | Single reference                  | Lock-free data structures, state machines     |
| **LongAdder**          | Yes       | No       | Single value (sum)                | High-contention increment-only counters       |
| volatile               | N/A       | No       | Single variable (visibility only) | Published references, simple flags (no R-M-W) |
| synchronized           | No        | Yes      | Any code block                    | Multi-variable compound operations            |
| ReentrantLock          | No        | Yes      | Any code block                    | Multi-variable, try-lock, condition variables |
| VarHandle              | Yes       | No       | Any field                         | Low-level, fine-grained memory ordering       |

How to choose: `AtomicInteger`/`AtomicLong` for counters and numeric state. `AtomicReference` for reference-based lock-free algorithms. `LongAdder` for high-contention increment-only counters. `synchronized`/`ReentrantLock` for compound operations spanning multiple variables.

---

### ⚠️ Common Misconceptions

| Misconception                                          | Reality                                                                                                                                                                                                                             |
| ------------------------------------------------------ | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| "volatile makes increments thread-safe"                | volatile only guarantees visibility (reads see latest write). `count++` is still three steps (read-modify-write). Use AtomicInteger for atomic increment.                                                                           |
| "AtomicInteger is always faster than synchronized"     | At HIGH contention (100+ threads all CAS-ing the same variable), CAS spinning can use more CPU than a mutex (which parks threads). LongAdder is better for high-contention counters.                                                |
| "CAS never fails"                                      | CAS fails whenever the expected value doesn't match the current value (another thread modified it). The retry loop may execute many times under contention. This is expected — but excessive spinning is a sign of design problems. |
| "Atomic operations can protect multi-field invariants" | No. Atomic classes are for single variables only. If you need "atomically update field A AND field B", you need either a lock or an `AtomicReference` to an immutable composite object.                                             |

---

### 🚨 Failure Modes & Diagnosis

**1. ABA Problem**

**Symptom:** A lock-free algorithm produces incorrect results. A variable is "A", changes to "B", changes back to "A". A CAS that checks for "A" succeeds even though the value changed between the read and the CAS.

**Example:**

```
Thread 1: read head → Node A (holds Node A reference)
Thread 1: [scheduled out]
Thread 2: pop A, pop B, push A back
Thread 1: [scheduled in]
Thread 1: CAS(head, NodeA, NodeC) → SUCCESS
// Thread 1 thinks nothing changed since it read NodeA
// But the stack's intermediate state was different
// NodeA.next now points to null (not NodeB as Thread 1 assumed)
// Stack is now corrupted: NodeC → null (lost NodeB)
```

**Root Cause:** CAS only checks VALUE equality, not "has this reference been modified and restored". An "A → B → A" sequence is indistinguishable from "no change" to a plain `AtomicReference`.

**Fix:** Use `AtomicStampedReference<V>` — stores both the reference and a version stamp. CAS requires BOTH the reference AND the stamp to match:

```java
AtomicStampedReference<Node> head = new AtomicStampedReference<>(null, 0);
int[] stampHolder = new int[1];
Node oldHead = head.get(stampHolder);
int oldStamp = stampHolder[0];
head.compareAndSet(oldHead, newHead, oldStamp, oldStamp + 1);
// Now A → B → A is detectable: stamp changes from 0 → 1 → 2
```

**Prevention:** Use `AtomicStampedReference` or `AtomicMarkableReference` for pointer-based lock-free data structures. For simple counters and flags, ABA is not a concern.

---

**2. Excessive CAS Spinning Under High Contention**

**Symptom:** CPU at 100% even though "nothing is happening". Profiler shows hot loops in `AtomicLong.incrementAndGet()`. Throughput drops under high thread count.

**Root Cause:** At high thread counts, many threads fail CAS and retry. Each retry is a wasted CPU cycle. The effective throughput collapses because threads are competing for the same CAS.

**Diagnostic:**

```bash
# Profiler shows hot methods:
async-profiler: AtomicInteger$::incrementAndGet or similar
# CPU usage high but throughput low = CAS contention

# Thread dump: many threads in AtomicInteger retry loop (not BLOCKED — RUNNABLE)
jstack <pid> | grep -A 5 "Unsafe.compareAndSwap"
```

**Fix:** Replace `AtomicLong` with `LongAdder` for pure increment/sum scenarios. This stripes the counter across multiple `Cell` objects — threads increment different cells, reducing CAS contention from O(N threads) to O(N cells, typically 8–64).

**Prevention:** For any counter incremented by > 10 concurrent threads at high frequency, use `LongAdder`. Use `AtomicLong` only when you need `compareAndSet()` semantics.

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**

- `CAS (Compare-And-Swap)` — the hardware instruction underlying all atomic classes
- `Volatile` — atomic classes use volatile semantics for visibility
- `Thread Safety` — the problem atomic classes solve

**Builds On This (learn these next):**

- `VarHandle` — Java 9+ API for fine-grained memory ordering and atomic ops on any field
- `Lock-Free Algorithms` — data structures built using atomic classes (stacks, queues, linked lists)
- `ConcurrentHashMap` — heavily uses CAS internally (bucket inserts, size counter)

**Alternatives / Comparisons:**

- `Volatile` — visibility only, not atomicity; use for read-only published references
- `Synchronized` — blocks threads; use for multi-variable compound operations
- `VarHandle` — lower-level, more flexible memory ordering; not needed for common cases

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ WHAT IT IS   │ Lock-free thread-safe ops on single vars  │
│              │ via CAS hardware instruction              │
├──────────────┼───────────────────────────────────────────┤
│ PROBLEM IT   │ synchronized for single-variable ops      │
│ SOLVES       │ is massive overkill (mutex overhead)      │
├──────────────┼───────────────────────────────────────────┤
│ KEY INSIGHT  │ CAS: atomic read+compare+write in ONE     │
│              │ CPU instruction — no thread parking       │
├──────────────┼───────────────────────────────────────────┤
│ USE WHEN     │ Thread-safe counters, flags, lock-free    │
│              │ data structures, state machine transitions│
├──────────────┼───────────────────────────────────────────┤
│ AVOID WHEN   │ Need to atomically update 2+ fields       │
│              │ (use lock); very high contention (LongAdder)│
├──────────────┼───────────────────────────────────────────┤
│ TRADE-OFF    │ Lock-free performance vs. ABA risk and    │
│              │ CAS spinning under extreme contention     │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "Single-variable mutex-free atomicity     │
│              │  via one uninterruptible CPU instruction."│
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ VarHandle → Lock-Free Algorithms          │
└──────────────┴───────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** Implement a thread-safe bounded counter (min=0, max=100) using only `AtomicInteger` and `compareAndSet()` — no `synchronized`, no locks. The `increment()` method should silently do nothing if the counter is already at max, and `decrement()` should silently do nothing if at min. Write out the complete retry loop logic, and explain why the `updateAndGet(fn)` method is NOT appropriate for this use case.

**Q2.** Your service uses an `AtomicReference<Config>` to store a configuration object. Multiple threads read the config at high frequency. The config is replaced atomically every 30 seconds with a new `Config` object loaded from a file. Explain why this is safe from the ABA problem even though the reference value could in theory return to a previously-seen Config instance. Then explain a scenario where it WOULD be ABA-unsafe even with an immutable Config object.
