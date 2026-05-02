---
layout: default
title: "CAS (Compare-And-Swap)"
parent: "Java Concurrency"
nav_order: 347
permalink: /java-concurrency/cas-compare-and-swap/
number: "0347"
category: Java Concurrency
difficulty: ★★★
depends_on: Race Condition, Java Memory Model (JMM), Atomic Classes, volatile
used_by: Atomic Classes, ConcurrentHashMap, VarHandle
related: Atomic Classes, Optimistic Locking (Java), volatile
tags:
  - java
  - concurrency
  - cas
  - deep-dive
  - lock-free
---

# 0347 — CAS (Compare-And-Swap)

⚡ TL;DR — CAS is a hardware-level atomic instruction that reads a variable, compares it to an expected value, and updates it only if they match — the foundation of all Java lock-free algorithms, enabling `AtomicInteger`, `ConcurrentHashMap`, and non-blocking concurrent data structures.

| #0347 | Category: Java Concurrency | Difficulty: ★★★ |
|:---|:---|:---|
| **Depends on:** | Race Condition, Java Memory Model (JMM), Atomic Classes, volatile | |
| **Used by:** | Atomic Classes, ConcurrentHashMap, VarHandle | |
| **Related:** | Atomic Classes, Optimistic Locking (Java), volatile | |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
`synchronized` solves race conditions but has costs: acquiring a lock requires an OS-level system call when contended, parking and unparking threads introduces context switches (~1-2μs), and lock acquisition serialises all threads. For highly contended counters, a `synchronized` increment means 1 thread works while all others queue — throughput limited to one increment per lock cycle.

**THE BREAKING POINT:**
A metrics collection service receives 1,000,000 HTTP requests/second, each incrementing 5 different counters. With `synchronized`, each counter serialises 1M operations/second. Increments take ~500ns each under contention = 2.5 billion nanoseconds/second = 2.5 seconds/second of work for counters alone — impossible.

**THE INVENTION MOMENT:**
This is exactly why **CAS** was created — to perform a compare-and-update atomically at the hardware level, without the overhead of OS-managed locks, enabling **lock-free** concurrent algorithms.

---

### 📘 Textbook Definition

**Compare-And-Swap (CAS)** is an atomic CPU instruction that does in one hardware operation: read a memory location, compare it with an expected value, and if equal, write a new value — returning whether the swap succeeded. In Java: `Unsafe.compareAndExchangeInt(obj, offset, expect, update)` (raw access), or `AtomicInteger.compareAndSet(expected, update)` (public API), or `VarHandle.compareAndSet(obj, expect, update)` (modern low-level API). CAS returns false if the value has changed since reading (another thread wrote it) — the caller retries: this is the **CAS loop** pattern.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
CAS = "update this value, but ONLY if it's still what I expect — tell me if someone beat me to it."

**One analogy:**
> A bank vault combination lock with a ledger. You note the current combination (read). Then you tell the vault: "change to new combination ONLY if it's still the original one I noted." If someone else changed it meanwhile, you retry. The vault takes one atomic step — it can't be interrupted between checking and updating.

**One insight:**
CAS resolves the race condition problem without a lock. If ten threads all try CAS on the same variable simultaneously, exactly one succeeds (the hardware guarantees this). The nine that fail retry — no thread is blocked, no context switch — they just spin briefly and try again. For low-contention workloads, this is dramatically faster than locking.

---

### 🔩 First Principles Explanation

**CORE INVARIANTS:**
1. CAS is a single atomic instruction — no thread can interleave between compare and swap.
2. CAS either succeeds (value matched, was swapped) or fails (value changed, no modification) — no partial update.
3. CAS does not prevent all concurrency issues — it's the basis for building lock-free algorithms, not a general replacement for all locks.

**CAS pseudocode (atomic at hardware level):**
```
CAS(memory_location, expected_value, new_value):
    // all atomically:
    current = *memory_location
    if current == expected_value:
        *memory_location = new_value
        return true  // success
    else:
        return false // failure — retry
```

**CAS loop for counter increment:**
```java
AtomicInteger counter = new AtomicInteger(5);

// CAS loop: retry until success
int current, update;
do {
    current = counter.get();        // read current value: 5
    update  = current + 1;          // compute new value: 6
} while (!counter.compareAndSet(current, update));
// If two threads both read 5: only ONE's CAS succeeds (5→6)
// Other thread: CAS fails (current now 6, not expected 5)
// Other thread: retry loop — reads 6, computes 7, CAS 6→7: success
```

**THE TRADE-OFFS:**
**Gain:** No OS lock overhead; threads spin instead of park (no context switch for uncontended + briefly contested); enables lock-free algorithms; scales better than synchronized under moderate contention.
**Cost:** ABA problem (value changed from A→B→A — CAS doesn't detect); high contention = CAS spinning wastes CPU; no guarantee of fairness (starvation possible); complex to implement correct lock-free algorithms.

---

### 🧪 Thought Experiment

**SETUP:**
A counter serving 1M increments/second from 100 threads.

WITH synchronized:
```
- Thread acquires mutex (OS call if contended: ~1μs)
- 99 threads BLOCKED, context-switched out
- Increment (1ns)
- Release mutex, wake 1 thread (OS call: ~1μs)
- Effective throughput: limited by lock overhead
- Under high contention: throughput flattens at ~500K/sec
```

WITH CAS (AtomicInteger.incrementAndGet()):
```
- Read current value (1ns)
- Compute current+1 (1ns)
- CAS: hardware CMPXCHG (5-10ns)
- If fail: retry (2-3 attempts on average at high contention)
- No OS call, no context switch
- Under 100-thread contention: ~200ns/operation vs ~2000ns
- Throughput: ~5M ops/sec vs ~500K ops/sec with mutex
```

**THE INSIGHT:**
CAS eliminates the OS overhead for uncontended and briefly-contended operations. Under very high contention (hundreds of threads spinning), CAS loops waste CPU — at that point, contention avoidance (partitioning the counter) is more effective than either lock or CAS.

---

### 🧠 Mental Model / Analogy

> CAS is like optimistic ticket buying. You see ticket row-5-seat-3 is available (read). You try to book it: "book row-5-seat-3 IF it's still available" (CAS). If someone else booked it millisecond before you (failure), you try another strategy — maybe row-5-seat-4 (retry). No theater staff blocking the seat for you (no lock) — you either succeed instantly or try again. The ticket system (hardware) guarantees two people can't book the exact same seat simultaneously.

- "Checking if seat available" → reading current value.
- "Booking if still available" → compareAndSet.
- "Other person booked first" → CAS failure.
- "Trying again" → CAS loop retry.

Where this analogy breaks down: In ticket booking with many users, you eventually find a seat. In CAS under extreme contention, you might spend many retries before succeeding. This is why `LongAdder` (striped counters) beats `AtomicLong` under truly extreme contention.

---

### 📶 Gradual Depth — Four Levels

**Level 1:** CAS is a single atomic operation that checks a value and updates it, failing gracefully if the value changed since you checked. No locks needed.

**Level 2:** Use `AtomicInteger.compareAndSet(expected, update)` — returns `true` if updated, `false` if current value ≠ expected. Use `AtomicInteger.incrementAndGet()` which is a CAS loop internally. For complex state, use `AtomicReference<T>` to swap entire objects atomically with CAS.

**Level 3:** CAS uses the hardware `CMPXCHG` instruction (x86) or `STXR/LDREX` pair (ARM). Java exposes it through `sun.misc.Unsafe.compareAndSwapInt` (direct hotspot intrinsic) and `VarHandle` API (Java 9+). `AtomicInteger` wraps a `volatile int value` field and uses `Unsafe.compareAndSetInt()`. The JIT compiles `AtomicInteger.incrementAndGet()` to a single `LOCK XADD` instruction on x86 — no JVM loop.

**Level 4:** CAS enables building lock-free data structures: `ConcurrentLinkedQueue`, `ConcurrentHashMap`, lock-free stacks, and skip lists. These are defined by: (1) non-blocking — every thread makes progress in finite steps; (2) wait-free — every thread completes in a bounded number of steps regardless of other threads. The ABA problem (A→B→A looks like no change to CAS) is solved using `AtomicStampedReference` or `AtomicMarkableReference`.

---

### ⚙️ How It Works (Mechanism)

**AtomicInteger CAS API:**
```java
AtomicInteger counter = new AtomicInteger(0);

// increments and returns new value — CAS loop internally
int newValue = counter.incrementAndGet();

// Manual CAS loop for complex updates:
int current, updated;
do {
    current = counter.get();
    updated = Math.max(current, newCandidate); // idempotent update
} while (!counter.compareAndSet(current, updated));

// compareAndSet: true = success, false = retry
System.out.println(counter.compareAndSet(5, 10)); // true if == 5
System.out.println(counter.compareAndSet(5, 10)); // false — now 10
```

**AtomicReference for object swaps:**
```java
AtomicReference<List<String>> listRef =
    new AtomicReference<>(new ArrayList<>());

// Add to immutable list atomically:
List<String> oldList, newList;
do {
    oldList = listRef.get();
    newList = new ArrayList<>(oldList);
    newList.add("item");
} while (!listRef.compareAndSet(oldList, newList));
// Thread-safe: replace entire list atomically
```

**ABA problem and solution:**
```java
// ABA: A→B→A — CAS thinks nothing changed
AtomicInteger ref = new AtomicInteger(5);
// T1 reads 5 (A)
// T2: 5 → 6 (B), then 6 → 5 (A) — ref is 5 again
// T1: CAS(5, 10) → succeeds! But state did change

// Fix: AtomicStampedReference adds version counter
AtomicStampedReference<Integer> stamped =
    new AtomicStampedReference<>(5, 0);

int[] stamp = new int[1];
Integer val = stamped.get(stamp);
// T2 changes: stamp increments even if value returns to 5
stamped.compareAndSet(val, 10, stamp[0], stamp[0] + 1);
// Now CAS includes stamp — A→B→A detected!
```

**x86 bytecode (JIT output):**
```bash
# AtomicInteger.incrementAndGet() compiles to:
# LOCK XADD [rsi+0x10], eax  (1 instruction, atomic on x86)
# vs synchronized: multiple instructions + potential OS call
```

---

### 🔄 The Complete Picture — End-to-End Flow

NORMAL FLOW (AtomicInteger.incrementAndGet):
```
[Thread T1: reads counter.value = 5]       ← YOU ARE HERE
    → [T1: computes 5+1 = 6]
    → [T1: CMPXCHG(addr, expected=5, new=6)]
    → [Hardware: value==5? YES → write 6, return success]
    → [T1: returns 6]
```

CONTENTION FLOW (two threads):
```
[T1 reads 5, T2 reads 5 simultaneously]
    → [T1: CMPXCHG(5→6): wins — value becomes 6]
    → [T2: CMPXCHG(expected=5, new=6): FAILS — value=6, not 5]
    → [T2: retry: reads 6, computes 7]
    → [T2: CMPXCHG(6→7): wins — value becomes 7]
    → [Final: 7 (both increments counted)]
```

**WHAT CHANGES AT SCALE:**
At extreme scale (1000+ threads contending on one CAS), retry loops dominate — cache line bouncing causes `MESI` protocol invalidations across cores, adding ~100ns per CAS. Solution: `LongAdder` (Java 8) uses striped counters — each thread typically updates its own stripe, combining at read time. `LongAdder.increment()` under extreme contention is 10-100× faster than `AtomicLong.incrementAndGet()`.

---

### 💻 Code Example

Example 1 — Compare AtomicInteger vs synchronized:
```java
// synchronized counter (blocking)
class SyncCounter {
    private int count = 0;
    synchronized void increment() { count++; }
    synchronized int get() { return count; }
}

// CAS counter (non-blocking)
class CASCounter {
    private final AtomicInteger count = new AtomicInteger(0);
    void increment() { count.incrementAndGet(); } // CAS loop
    int get() { return count.get(); }
}

// Under 100 threads, 1M increments:
// SyncCounter: ~5 seconds
// CASCounter: ~0.5 seconds
// LongAdder: ~0.1 seconds (for extreme contention)
```

Example 2 — Lock-free stack using CAS:
```java
class ConcurrentStack<T> {
    private final AtomicReference<Node<T>> head =
        new AtomicReference<>(null);

    void push(T val) {
        Node<T> newHead = new Node<>(val);
        Node<T> current;
        do {
            current = head.get();
            newHead.next = current;
        } while (!head.compareAndSet(current, newHead));
        // CAS: new head points to old head if old head unchanged
    }

    T pop() {
        Node<T> current, newHead;
        do {
            current = head.get();
            if (current == null) return null;
            newHead = current.next;
        } while (!head.compareAndSet(current, newHead));
        return current.value;
    }
}
```

---

### ⚖️ Comparison Table

| Mechanism | Overhead | Blocking | Fairness | Scalability | Best For |
|---|---|---|---|---|---|
| `synchronized` | OS lock | Yes (BLOCKED) | No | Poor at high contention | Complex multi-field state |
| **CAS (AtomicInteger)** | Spin (brief) | No | No | Good at moderate contention | Single-variable atomic ops |
| LongAdder | Minimal | No | No | Excellent under contention | Pure counters |
| ReentrantLock | OS lock | Yes (WAITING) | Optional | Poor at high | Complex locking with timeout |

How to choose: CAS (`AtomicInteger`, `AtomicReference`) for single-variable atomic operations. `LongAdder` for counters under extreme contention. `synchronized`/`ReentrantLock` for multi-step operations on multiple variables.

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| CAS is always faster than synchronized | For zero contention, uncontended `synchronized` with biased locking can be faster. CAS wins at low-to-moderate contention. At extreme contention (100+ threads on one variable), both degrade and `LongAdder` wins |
| CAS is sufficient for all concurrent problems | CAS solves single-variable atomicity. For coordinating updates to multiple variables, a lock is still needed. The ABA problem can corrupt CAS-based algorithms without `AtomicStampedReference` |
| A failed CAS discards my work | A failed CAS means "the value changed since I read it — start over." No data corruption occurs; the failed thread simply retries with the current value |
| CAS is equivalent to `volatile` | `volatile` ensures visibility. CAS provides atomic compare-and-update. They solve different aspects of concurrency — CAS also has implicit `volatile` semantics but does more |

---

### 🚨 Failure Modes & Diagnosis

**Spinning Threads Under High CAS Contention**

**Symptom:** CPU 100%, throughput not improving with more threads.

**Root Cause:** Too many threads contending on one CAS variable — retry loops dominate.

**Diagnostic:**
```bash
# Async profiler: CPU flamegraph shows CAS retry loops
./asprof -e cpu -d 30 <pid>
# Look for AtomicInteger.incrementAndGet in hot path
```

**Fix:**
- Replace `AtomicLong` with `LongAdder` for pure counters.
- Shard the atomic variable across `N` variables; combine on read.
- Redesign to reduce contention (separate per-thread accumulation, batch updates).

---

**ABA Problem Corruption**

**Symptom:** Lock-free data structure invariants violated — impossible values or missing elements.

**Root Cause:** ABA sequence: CAS succeeded but the "unchanged" value actually changed and reverted.

**Fix:**
```java
// Use AtomicStampedReference to attach a version counter:
AtomicStampedReference<Node<T>> head =
    new AtomicStampedReference<>(initNode, 0);

// During update, increment the stamp:
int[] stamp = new int[1];
Node<T> current = head.get(stamp);
head.compareAndSet(current, newNode, stamp[0], stamp[0] + 1);
```

**Prevention:** Always examine lock-free algorithms for ABA susceptibility. Use `AtomicStampedReference` or `AtomicMarkableReference` when ABA is possible.

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**
- `Race Condition` — CAS solves the race condition at single-variable atomicity level
- `Java Memory Model (JMM)` — CAS has implicit volatile semantics; JMM defines when CAS is visible
- `volatile` — CAS includes volatile read/write semantics

**Builds On This (learn these next):**
- `Atomic Classes` — Java's public API for CAS operations (`AtomicInteger`, `AtomicReference`, etc.)
- `VarHandle` — modern low-level CAS access API (Java 9+)

**Alternatives / Comparisons:**
- `synchronized` — lock-based alternative; simpler but blocking
- `Optimistic Locking (Java)` — database-level CAS analogue using version numbers

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ WHAT IT IS   │ Hardware atomic: read-compare-write in    │
│              │ one uninterruptible instruction           │
├──────────────┼───────────────────────────────────────────┤
│ PROBLEM IT   │ Locks have OS overhead; simultaneous      │
│ SOLVES       │ read-modify-write creates race conditions │
├──────────────┼───────────────────────────────────────────┤
│ KEY INSIGHT  │ No blocking — failed CAS retries.         │
│              │ ABA problem: A→B→A looks unchanged.       │
│              │ Extreme contention → use LongAdder        │
├──────────────┼───────────────────────────────────────────┤
│ USE WHEN     │ Single-variable atomic operations;        │
│              │ building lock-free data structures        │
├──────────────┼───────────────────────────────────────────┤
│ AVOID WHEN   │ Multi-variable compound operations;       │
│              │ extreme contention (use LongAdder)        │
├──────────────┼───────────────────────────────────────────┤
│ TRADE-OFF    │ No blocking + lower latency vs            │
│              │ spinning + ABA problem                   │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "Update only if unchanged — retry if      │
│              │  someone beat me to it"                   │
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ Atomic Classes → LongAdder → VarHandle    │
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** `AtomicInteger.incrementAndGet()` is implemented as a CAS loop: read, add 1, CAS. The JIT on x86 compiles this to a single `LOCK XADD` instruction. Explain: why `LOCK XADD` is correctly translated as a CAS (it doesn't have a compare step) — what difference from `LOCK CMPXCHG` makes `LOCK XADD` correct for increment, why these two instructions are not interchangeable, and what specific optimization the JIT is making that is NOT a CAS semantically but IS equivalent for the specific use case of increment.

**Q2.** A developer builds a lock-free set using `AtomicReference<Set<E>>`. The pattern is: `do { old = ref.get(); newSet = new HashSet<>(old); newSet.add(element); } while (!ref.compareAndSet(old, newSet))`. Analyze: what is the time complexity of a single successful `add()` in terms of concurrent contenders (call it N), what is the total work done across ALL N threads when all try to add simultaneously (show the steps each thread takes), and explain why this implementation is correct-but-impractical at scale and what the correct lock-free set implementation strategy is.

