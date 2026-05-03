---
layout: default
title: "Atomic Classes"
parent: "Java Concurrency"
nav_order: 363
permalink: /java-concurrency/atomic-classes/
number: "0363"
category: Java Concurrency
difficulty: ★★★
depends_on: Volatile, CAS (Compare-And-Swap), Thread Safety, Lock-Free Programming
used_by: Counters, Sequence Generators, Lock-Free Data Structures, ConcurrentHashMap
related: VarHandle, LongAdder, Volatile, ReentrantLock, ConcurrentHashMap
tags:
  - concurrency
  - atomic
  - cas
  - java
  - advanced
  - lock-free
---

# 363 — Atomic Classes

⚡ TL;DR — Atomic classes (`AtomicInteger`, `AtomicLong`, `AtomicReference`) provide lock-free thread-safe operations on single variables using CPU-level Compare-And-Swap (CAS), eliminating synchronized blocks for simple counter and reference updates.

| #0363 | Category: Java Concurrency | Difficulty: ★★★ |
|:---|:---|:---|
| **Depends on:** | Volatile, CAS (Compare-And-Swap), Thread Safety, Lock-Free Programming | |
| **Used by:** | Counters, Sequence Generators, Lock-Free Data Structures, ConcurrentHashMap | |
| **Related:** | VarHandle, LongAdder, Volatile, ReentrantLock, ConcurrentHashMap | |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
You have a request counter shared across 1000 threads. `volatile int count` doesn't work — `count++` is three operations (read, increment, write) and not atomic. `synchronized` works but creates a bottleneck: every increment blocks all other threads. At 100,000 increments/second, threads spend more time waiting for the lock than actually incrementing.

**THE BREAKING POINT:**
`volatile` guarantees visibility but not atomicity for compound operations. `synchronized` guarantees both but serializes threads unnecessarily for simple operations. For a single integer counter, serializing 1000 threads to protect three CPU instructions is a 1000x over-synchronization.

**THE INVENTION MOMENT:**
Modern CPUs have atomic instructions: CAS (Compare-And-Swap) — "if this memory location contains expected value X, atomically replace it with new value Y; return whether the swap happened." Java's `AtomicInteger.incrementAndGet()` uses CAS in a loop: read current value, compute new value, CAS(current, new) — if CAS succeeds, done; if another thread changed it first, retry. No OS lock. No thread parking. Hardware-level atomicity in 2–3 CPU cycles. This is `java.util.concurrent.atomic.*`.

---

### 📘 Textbook Definition

**Atomic classes** in `java.util.concurrent.atomic` provide thread-safe non-blocking operations on single values using Compare-And-Swap (CAS) hardware primitives. Key classes: `AtomicInteger`, `AtomicLong`, `AtomicBoolean` (for primitive values); `AtomicReference<V>` (for object references); `AtomicIntegerArray`, `AtomicLongArray`, `AtomicReferenceArray` (for arrays); `AtomicIntegerFieldUpdater`, `AtomicLongFieldUpdater`, `AtomicReferenceFieldUpdater` (for fields of existing objects). Core operation: `compareAndSet(expectedValue, newValue)` — atomically updates to `newValue` if current value equals `expectedValue`, returns `true` on success. Higher-level atomic methods (`getAndIncrement`, `incrementAndGet`, `getAndAdd`, `updateAndGet`, `accumulateAndGet`) are built on CAS.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
Atomic classes use CPU hardware to update a variable in one uninterruptible step — no locks, no blocking, no thread waiting.

**One analogy:**
> CAS is like a bank vault with a note on the door: "If the balance is $100, change it to $150 — signed, Alice." The vault attendant (CPU) checks the current balance. If it's exactly $100, they make the change and give Alice a receipt. If it's not $100 (someone else already changed it), they don't change anything and tell Alice to try again with the new balance. No queue. No waiting room. Just immediate success-or-retry.

**One insight:**
Atomic classes don't eliminate contention — they eliminate blocking. Under high contention, CAS-retry loops spin rather than park threads. For counters under extreme contention (millions of increments/sec), `LongAdder` (which stripes the counter across CPU cores) outperforms `AtomicLong` by eliminating the CAS retry contention entirely.

---

### 🔩 First Principles Explanation

**CORE INVARIANTS:**
1. CAS is a single atomic CPU instruction (`CMPXCHG` on x86).
2. CAS: atomically "if memory[addr] == expected, then memory[addr] = newVal; return success."
3. Atomic classes wrap CAS via `sun.misc.Unsafe` / `VarHandle` (Java 9+).
4. CAS loops: read → compute → CAS → if fail, retry. Correct because each attempt reads fresh state.
5. No thread is ever parked/blocked — "lock-free" means at least one thread always makes progress.

**DERIVED DESIGN:**

```
ATOMIC INCREMENT LOOP (incrementAndGet):

  int current;
  int next;
  do {
    current = get();           // volatile read
    next = current + 1;        // compute new value
  } while (!compareAndSet(current, next));  // CAS retry
  return next;

HARDWARE LEVEL (x86 CMPXCHG):
  LOCK CMPXCHG [memory], reg
  → bus lock or cache line lock (1-2 CPU cycles)
  → atomic: no other CPU can read/write this cache line
  → between CMPXCHG start and end

UNDER CONTENTION — 3 threads incrementing simultaneously:
  T1: read=5, compute 6, CAS(5→6) SUCCESS → returns 6
  T2: read=5, compute 6, CAS(5→6) FAIL (now 6) → retry
      read=6, compute 7, CAS(6→7) SUCCESS → returns 7
  T3: read=5, compute 6, CAS(5→6) FAIL (now 7) → retry
      read=7, compute 8, CAS(7→8) SUCCESS → returns 8
  Final value: 8 = correct (three increments from 5)
```

```
KEY ATOMIC CLASSES:
┌──────────────────────┬───────────────────────────────────┐
│ AtomicInteger        │ int operations: increment, add,   │
│ AtomicLong           │ compareAndSet, getAndUpdate, etc.  │
├──────────────────────┼───────────────────────────────────┤
│ AtomicBoolean        │ boolean flag, compareAndSet        │
├──────────────────────┼───────────────────────────────────┤
│ AtomicReference<V>   │ object reference, compareAndSet   │
│                      │ useful for ABA problem awareness  │
├──────────────────────┼───────────────────────────────────┤
│ AtomicStampedRef     │ AtomicReference + version stamp   │
│                      │ solves ABA problem                │
├──────────────────────┼───────────────────────────────────┤
│ AtomicMarkableRef    │ AtomicReference + boolean mark    │
│                      │ soft-deletion in lock-free structs│
├──────────────────────┼───────────────────────────────────┤
│ LongAdder            │ Striped counter; better than       │
│ LongAccumulator      │ AtomicLong under high contention  │
└──────────────────────┴───────────────────────────────────┘
```

**THE TRADE-OFFS:**
- **Gain:** No thread blocking; lower overhead than synchronized for low-medium contention; hardware-optimized on modern CPUs.
- **Cost:** CAS retry loops under extreme contention → CPU spin → wasted cycles; ABA problem with reference types; not composable (can't atomically update two variables).

---

### 🧪 Thought Experiment

**SETUP:**
10,000 threads all simultaneously call `atomicLong.incrementAndGet()` on a single `AtomicLong`.

**WHAT HAPPENS:**
All 10,000 threads read the current value (e.g., 0). All compute next = 1. All call CAS(0 → 1). ONE succeeds. 9,999 fail — they retry. Now 9,999 threads read the current value (1). All compute next = 2. One succeeds. 9,998 retry... In the worst case, this is O(N²) CAS attempts for N threads.

**THE REAL-WORLD INSIGHT:**
Under true extreme contention, `AtomicLong` performance degrades because of CAS loop retries. `LongAdder` solves this by maintaining an array of `Cell` values (one per CPU core), each independently incremented with low contention, and summing them when `sum()` is called. Total throughput scales linearly with CPU count instead of degrading quadratically.

**KEY DECISION:**
Use `AtomicLong` for low-medium contention counters or when you need the exact current value frequently. Use `LongAdder` for high-contention pure counting (events/sec, requests/sec) where you only need the total periodically.

---

### 🧠 Mental Model / Analogy

> Atomic classes are like a scoreboard in a sports stadium where only electronic updates (no manual board-flipper) are allowed. Every scorer must: read the current score, compute new score, then press an atomic "update" button that either succeeds (score was still what they read) or fails with the new current score shown. On failure, they try again with the fresh reading. No queue. No waiting room. Fast under normal conditions; chaotic if 10,000 people try to score simultaneously.

- "Electronic scoreboard" → volatile memory location
- "Read current score" → volatile read in CAS loop
- "Atomic update button" → CPU CAS instruction
- "Fails, shows new score" → CAS failure returns current value
- "10,000 simultaneous updates" → high contention → CAS thrashing

Where this analogy breaks down: a real scoreboard update would require a person to go back to their seat and try again later. CAS retries happen at CPU speed in a tight loop — microseconds, not minutes.

---

### 📶 Gradual Depth — Four Levels

**Level 1 — What it is (anyone can understand):**
Atomic classes let multiple threads safely increment or update a shared number or object without using `synchronized`. They're faster than locking for simple operations because the CPU handles the safety directly in hardware.

**Level 2 — How to use it (junior developer):**
`AtomicInteger count = new AtomicInteger(0)`. Use `count.incrementAndGet()` instead of `synchronized int counter++`. Use `compareAndSet(expected, update)` for conditional updates: "change to X only if current value is Y." Use `AtomicReference<T>` for thread-safe reference swaps (e.g., updating a shared config object atomically). Avoid reading the value, computing externally, and setting — that's a race condition. Use `updateAndGet(int->int)` or `accumulateAndGet` for composed updates.

**Level 3 — How it works (mid-level engineer):**
Internally: `AtomicInteger` holds `private volatile int value`. Operations are implemented via `Unsafe.compareAndSwapInt` (Java 8) or `VarHandle` (Java 9+). `compareAndSwapInt(object, offset, expected, update)` translates to the x86 `LOCK CMPXCHG` instruction, which acquires an exclusive cache-line lock for the duration of the compare-and-swap. On systems with cache coherence protocols (MESI), this cache line lock ensures no other CPU can read or write the same cache line during the operation. `getAndIncrement()` generates the CAS retry loop in JIT-compiled code; HotSpot can inline and optimise the loop, sometimes eliminating the loop entirely under low contention by detecting uncontended access patterns.

**Level 4 — Why it was designed this way (senior/staff):**
The Java 9 migration from `Unsafe` to `VarHandle` (introduced in JEP 193) was motivated by three problems with `Unsafe`: (1) it bypasses JVM safety checks; (2) it requires hardcoded field offsets computed at initialization; (3) it's not accessible in a module system context. `VarHandle` provides the same CAS semantics with type safety, access mode specification (plain, opaque, acquire, release, volatile), and proper encapsulation. The ABA problem — where a value changes from A to B and back to A, making a CAS check pass incorrectly — is a known hazard for lock-free data structures using `AtomicReference`. `AtomicStampedReference` addresses this by pairing the reference with an integer stamp (version number) that increments on every change, so CAS checks both reference AND stamp.

---

### ⚙️ How It Works (Mechanism)

```
CAS INSTRUCTION FLOW:
┌─────────────────────────────────────────────────────────┐
│  CPU: LOCK CMPXCHG [mem_address], register              │
│                                                         │
│  1. Acquire exclusive ownership of cache line           │
│     containing mem_address (via MESI protocol or bus)   │
│  2. Read current value from mem_address                 │
│  3. Compare with expected value                         │
│  4. If equal: write new value to mem_address            │
│     Set ZF (zero flag) = 1 (success)                    │
│  5. If not equal: do nothing                            │
│     Set ZF = 0 (failure); EAX = current value           │
│  6. Release cache line                                  │
│                                                         │
│  All 6 steps are ATOMIC — no other CPU can observe      │
│  any intermediate state                                 │
└─────────────────────────────────────────────────────────┘

ATOMIC METHOD IMPLEMENTATIONS:
┌───────────────────────────┬─────────────────────────────┐
│ getAndIncrement()         │ CAS loop: read, +1, CAS     │
│ incrementAndGet()         │ CAS loop: read, +1, CAS     │
│ getAndAdd(delta)          │ CAS loop: read, +delta, CAS │
│ compareAndSet(exp, upd)   │ single CAS, true/false      │
│ updateAndGet(fn)          │ CAS loop: read, fn(v), CAS  │
│ accumulateAndGet(x, fn)   │ CAS loop: read, fn(v,x),CAS │
└───────────────────────────┴─────────────────────────────┘
```

---

### 🔄 The Complete Picture — End-to-End Flow

```
NORMAL FLOW (rate counter):
HTTP request arrives
→ requestCount.incrementAndGet() — no lock, 1-3 CPU cycles
→ [AtomicLong CAS ← YOU ARE HERE]
→ CAS succeeds (low contention): done in ~2ns
→ CAS fails (high contention): retry 1-10 times, ~20-100ns
→ Request proceeds without waiting for other threads

FAILURE PATH: ABA Problem with AtomicReference
Thread A reads ref = nodeX
Thread B: removes nodeX, adds nodeY, removes nodeY, re-adds nodeX
Thread A: CAS(nodeX, newNode) SUCCEEDS (sees nodeX) but
          nodeX's state is now different than when A read it
→ Data structure is corrupted silently
→ Fix: use AtomicStampedReference to version-stamp refs

WHAT CHANGES AT SCALE:
At 10M+ increments/sec on a single AtomicLong:
CAS contention causes retry loops and CPU cache
thrashing. Switch to LongAdder for pure counting —
it distributes across CPU-local cells, summing on
demand. Throughput scales linearly with core count
rather than degrading under contention.
```

---

### 💻 Code Example

```java
import java.util.concurrent.atomic.*;

// Example 1 — Basic counter (vs synchronized)
// BAD: volatile doesn't make ++ atomic
volatile int badCount = 0;
badCount++; // read-increment-write = 3 ops, not atomic!

// GOOD: AtomicInteger makes increment atomic
AtomicInteger goodCount = new AtomicInteger(0);
goodCount.incrementAndGet(); // atomic, lock-free

// Example 2 — Conditional update (CAS)
AtomicInteger state = new AtomicInteger(0);
// Transition from IDLE(0) to RUNNING(1) only if currently IDLE:
boolean started = state.compareAndSet(0, 1); // atomic
if (!started) System.out.println("Already running");

// Example 3 — updateAndGet for custom atomic operation
AtomicInteger max = new AtomicInteger(Integer.MIN_VALUE);
// Thread-safe max update:
max.updateAndGet(current -> Math.max(current, newValue));

// Example 4 — AtomicReference for config swap
AtomicReference<Config> configRef =
    new AtomicReference<>(initialConfig);

// Hot-swap config atomically:
configRef.set(newConfig); // volatile write, all readers see it

// Example 5 — ABA problem and fix
AtomicReference<Node> top = new AtomicReference<>(nodeA);
// Thread B may change A→B→A between our read and CAS
// Our CAS(A, newTop) succeeds incorrectly!

// Fix: AtomicStampedReference
AtomicStampedReference<Node> stampedTop =
    new AtomicStampedReference<>(nodeA, 0);
int[] stampHolder = new int[1];
Node current = stampedTop.get(stampHolder);
int currentStamp = stampHolder[0];
// CAS only succeeds if BOTH reference AND stamp match:
stampedTop.compareAndSet(current, newNode,
                          currentStamp, currentStamp + 1);

// Example 6 — LongAdder vs AtomicLong for high contention
LongAdder adder = new LongAdder();    // high contention
AtomicLong atomic = new AtomicLong(); // low contention

// Adding: near-linear throughput scaling with LongAdder
adder.increment();          // distributes across cells
long total = adder.sum();   // sums all cells on demand

atomic.incrementAndGet();   // single CAS, bottleneck at high count
```

---

### ⚖️ Comparison Table

| Approach | Blocking | Contention | Composable | Best For |
|---|---|---|---|---|
| synchronized block | Yes (OS lock) | Low (uncontended) | Yes (guards block) | Complex multi-variable atomicity |
| **AtomicInteger/Long** | No (CAS retry) | Medium | No | Single-variable counters, flags |
| LongAdder | No (striped CAS) | Very high | No | High-throughput pure counting |
| volatile | No | N/A (visibility only) | No | Single-variable visibility without atomicity |
| ReentrantLock | Yes | Medium | Yes (lock scope) | Complex operations with backoff |

**How to choose:** Use Atomic classes for single-variable updates under low-medium contention. Use `LongAdder` for very high contention counters. Use `synchronized`/`ReentrantLock` when you need to atomically update multiple variables together.

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| Atomic classes are always faster than synchronized | Under high contention with many threads, CAS retry loops spin and waste CPU cycles. `synchronized` can actually be more efficient because it parks blocked threads (freeing CPU for other work) rather than spinning |
| volatile int counter++ is atomic | It is not. `volatile` ensures visibility; `counter++` is still three separate operations (read, increment, write). Use `AtomicInteger.incrementAndGet()` for atomic increment |
| AtomicReference.compareAndSet protects against all races | The ABA problem: if a value changes from A to B to A, a CAS checking for A succeeds even though the state has changed. Use `AtomicStampedReference` with a version counter when ABA matters |
| You can atomically update two AtomicIntegers with two CAS calls | Two separate CAS calls are not atomic together. Other threads can observe the state between the two calls. Use synchronized blocks to atomically update multiple variables |

---

### 🚨 Failure Modes & Diagnosis

**CAS Thrashing Under High Contention**

**Symptom:** CPU utilization spikes to 100% with minimal throughput; profiler shows hot methods in `AtomicLong.incrementAndGet`; throughput does not scale with thread count.

**Root Cause:** High thread count competing for the same atomic variable; CAS failure rate is high; threads spin in retry loops consuming CPU without productive work.

**Diagnostic Command:**
```bash
# Profile CAS operations with JFR:
java -XX:StartFlightRecording=duration=60s,filename=app.jfr

# Or check CPU cycles in hot spinloops:
perf record -g java MyApp
perf report | head -30
# Look for high percentage in atomic update methods
```

**Fix:**
```java
// BAD: AtomicLong under extreme contention
AtomicLong counter = new AtomicLong();
// 1000 threads all calling counter.incrementAndGet()

// GOOD: LongAdder distributes across CPU cells
LongAdder counter = new LongAdder();
counter.increment(); // near-zero contention per-cell
long total = counter.sum(); // reads total when needed
```

**Prevention:** Profile under expected load. If counter updates > 100K/sec from many threads, use `LongAdder`.

---

**ABA Problem Corrupting Lock-Free Data Structure**

**Symptom:** Lock-free stack/queue shows occasional incorrect behaviour (missing items, double-processing); only manifests under concurrent stress.

**Root Cause:** Thread reads reference A, another thread removes A, adds B, removes B, re-adds A. First thread's CAS succeeds (still sees A) but A's `next` pointer may have changed.

**Diagnostic Command:**
```bash
# Reproduce with stress test + assertion:
# Add invariant checks to data structure operations
# Run jcstress tests for the data structure
```

**Fix:** Replace `AtomicReference` with `AtomicStampedReference` in lock-free data structures. Increment stamp on every mutation.

**Prevention:** Any lock-free data structure using `AtomicReference` should use `AtomicStampedReference` unless ABA is provably impossible (e.g., GC-managed references that are never reused).

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**
- `Volatile` — atomic classes build on volatile semantics for visibility
- `CAS (Compare-And-Swap)` — the hardware primitive underlying all atomic operations
- `Lock-Free Programming` — the programming model atomic classes enable

**Builds On This (learn these next):**
- `VarHandle` — Java 9+ replacement for Unsafe-based CAS; more flexible access modes
- `LongAdder` — solves CAS contention for pure counting via cell striping
- `Lock-Free Data Structures` — stacks, queues, lists built with atomic classes

**Alternatives / Comparisons:**
- `ReentrantLock` — blocking lock for complex atomic operations across multiple variables
- `LongAdder` — better than `AtomicLong` for high-contention counting
- `Synchronized` — simpler, broader scope; OK for uncontended or complex atomicity

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ WHAT IT IS   │ Lock-free thread-safe variable update     │
│              │ using CPU Compare-And-Swap hardware       │
├──────────────┼───────────────────────────────────────────┤
│ PROBLEM IT   │ Single-variable atomic updates without    │
│ SOLVES       │ synchronized blocking overhead            │
├──────────────┼───────────────────────────────────────────┤
│ KEY INSIGHT  │ CAS spins on failure, not blocks; under   │
│              │ extreme contention LongAdder wins         │
├──────────────┼───────────────────────────────────────────┤
│ USE WHEN     │ Single-variable counters, flags, refs;    │
│              │ low-medium concurrency (<100 threads)     │
├──────────────┼───────────────────────────────────────────┤
│ AVOID WHEN   │ Multi-variable atomicity needed;          │
│              │ extreme contention (use LongAdder)        │
├──────────────┼───────────────────────────────────────────┤
│ TRADE-OFF    │ Lock-free throughput vs CAS spin waste    │
│              │ under high contention                     │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "Hardware-level scoreboard update:        │
│              │  instant if score unchanged, retry if not"│
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ VarHandle → LongAdder → Lock-Free Structs │
└──────────────┴───────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** `AtomicInteger.updateAndGet(IntUnaryOperator)` is described as atomic, but it may call the operator function multiple times (once per CAS retry). This means the operator is called with different values on each retry. Explain what constraints a correct operator function must satisfy — specifically why the operator must be side-effect-free and why a stateful operator (e.g., one that logs or increments a counter on each call) produces incorrect behaviour under contention.

**Q2.** The ABA problem occurs when a CAS check sees value A and concludes "nothing has changed" even though the value changed from A to B and back to A. `AtomicStampedReference` solves this by pairing a reference with an integer stamp. However, stamp overflow is theoretically possible (int wraps from MAX_VALUE to MIN_VALUE). Design a scenario involving a very fast concurrent data structure where stamp overflow causes the ABA problem to reappear, and explain the minimum stamp width needed to make the problem computationally infeasible given realistic CPU speeds.
