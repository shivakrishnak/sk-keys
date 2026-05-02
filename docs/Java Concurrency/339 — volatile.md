---
layout: default
title: "volatile"
parent: "Java Concurrency"
nav_order: 339
permalink: /java-concurrency/volatile/
number: "0339"
category: Java Concurrency
difficulty: ★★★
depends_on: Memory Barrier, Happens-Before, synchronized, JVM
used_by: synchronized, Thread Lifecycle, Double-Checked Locking
related: synchronized, Memory Barrier, Happens-Before
tags:
  - java
  - concurrency
  - memory-model
  - deep-dive
  - jvm
---

# 0339 — volatile

⚡ TL;DR — `volatile` guarantees that reads and writes of a variable are directly from/to main memory (no CPU cache stale reads) and establishes a happens-before relationship — providing visibility across threads without mutual exclusion.

| #0339 | Category: Java Concurrency | Difficulty: ★★★ |
|:---|:---|:---|
| **Depends on:** | Memory Barrier, Happens-Before, synchronized, JVM | |
| **Used by:** | synchronized, Thread Lifecycle, Double-Checked Locking | |
| **Related:** | synchronized, Memory Barrier, Happens-Before | |

### 🔥 The Problem This Solves

WORLD WITHOUT IT:
Modern CPUs have multiple levels of cache (L1/L2/L3). Each CPU core may cache a variable differently. Thread T1 running on Core 1 writes `flag = true`. Thread T2 running on Core 2 reads `flag` — but Core 2's cache is stale, and T2 reads `flag = false`. T1's write is invisible to T2 even though it happened first. Without `volatile`, the JIT compiler may additionally reorder instructions and cache values in registers, making stale reads the default, not the exception.

THE BREAKING POINT:
A classic stop-flag pattern:
```java
boolean running = true;        // NOT volatile
void stop() { running = false; }
void run() {
    while (running) { doWork(); }
    // Might NEVER stop if running is cached in register!
}
```
The JIT compiler sees `running` never changes inside `run()` and optimizes it to `while (true)` — hoisting the read out of the loop forever. The thread runs indefinitely even after `stop()` is called.

THE INVENTION MOMENT:
This is exactly why **`volatile`** was created — to tell the JVM and CPU "this variable is shared across threads — never cache it, always read from and write to main memory, and don't reorder accesses to it."

### 📘 Textbook Definition

**`volatile`** is a Java keyword (part of the Java Memory Model, JMM) that declares a field as directly read from and written to main memory, preventing CPU caches and JIT register optimisation from serving stale values. A write to a volatile variable **happens-before** every subsequent read of that variable by any thread — the JMM guarantees this explicitly. `volatile` INSERT memory barriers: a write-release barrier after each volatile write, and a load-acquire barrier before each volatile read. `volatile` does NOT provide mutual exclusion — concurrent read-modify-write operations (`count++`) are still races.

### ⏱️ Understand It in 30 Seconds

**One line:**
`volatile` means "never cache this — always talk to main memory directly, in order."

**One analogy:**
> Two offices sharing a memo board. Without volatile: each office has its own private copy of the memo, only updated occasionally. With volatile: there's one central memo board, and every time someone reads or writes, they go to the central board. No one is ever reading an outdated private copy.

**One insight:**
`volatile` solves visibility. `synchronized` solves visibility AND mutual exclusion. Using `volatile` for `count++` is still wrong because `count++` is 3 operations (read-add-write). Use `AtomicInteger` for atomic increment, `synchronized` for compound operations, `volatile` for simple flags.

### 🔩 First Principles Explanation

CORE INVARIANTS:
1. Each volatile read reads the most recently written value by any thread.
2. A volatile write happens-before any subsequent volatile read of the same variable.
3. volatile does NOT prevent interleaving of compound operations (volatility is per-read/write, not per sequence).

DERIVED DESIGN:
Given invariant 2 (happens-before): the HB guarantee is transitive. If Thread T1 writes volatile `flag` after updating a non-volatile `data`, and Thread T2 reads volatile `flag` and then reads non-volatile `data` — the HB chain `data write → flag write → flag read → data read` ensures T2 sees T1's `data` value. This is the "piggyback" pattern used for lazy initialization.

```
Java Memory Model volatile semantics:
  Write(v):
    1. Execute write
    2. Store-Store barrier (prevent write reorder above)
    3. Flush to main memory
    4. Store-Load barrier (prevent subsequent load from cache)
  
  Read(v):
    1. Load-Load barrier (prevent load reorder above)
    2. Load from main memory (not cache)
    3. Store-Load barrier (prevent subsequent loads from cache)
```

THE TRADE-OFFS:
Gain: Visibility guarantee; prevents JIT caching in registers; prevents instruction reorder around volatile access; cheaper than `synchronized`.
Cost: No mutual exclusion; compound operations still race; memory barriers add latency (~5-40ns on x86 vs ~1ns for cached reads); heavy use on hot paths can impede JIT optimization.

### 🧪 Thought Experiment

SETUP:
A status flag checked by worker threads that can be set by a control thread.

WITHOUT volatile (broken):
```java
boolean shutdown = false; // NOT volatile

// Worker thread:
while (!shutdown) { doWork(); }

// Control thread sets shutdown = true
// Worker may NEVER see it due to JIT register caching
```

WITH volatile (correct):
```java
volatile boolean shutdown = false;

// Worker thread:
while (!shutdown) { doWork(); }

// Control thread sets shutdown = true
// GUARANTEED: worker sees the write on next read
```

BUT volatile isn't enough for compound operations:
```java
volatile int count = 0;
void increment() { count++; } // STILL a race!
// count++ = read 5 | add 1 | write 6 — non-atomic
// Two threads: both read 5, both write 6 → lost increment
// Fix: AtomicInteger or synchronized
```

THE INSIGHT:
`volatile` makes each individual read/write atomic (for long and double, `volatile` also prevents word tearing). But it doesn't make sequences of reads and writes atomic. `count++` is a sequence — it needs synchronized or AtomicInteger.

### 🧠 Mental Model / Analogy

> `volatile` is like a public whiteboard in a shared workspace vs. a personal notepad. Without volatile: each developer copies info to their notepad and updates it occasionally. With volatile: there's one whiteboard — every read and write happens on the whiteboard directly. You see exactly what others wrote and in the order they wrote it. But if two people simultaneously try to update "count" on the whiteboard (read-add-write), they can still overwrite each other.

"Personal notepad" → CPU register or cache.
"Public whiteboard" → main memory.
"Making it volatile" → forcing all reads/writes to the whiteboard.
"Two people updating simultaneously" → unsynchronized compound operations (still unsafe).

Where this analogy breaks down: Main memory is shared but CPUs can still serve stale cache values without hardware cache coherence. `volatile` triggers memory barriers that force cache coherence — not exactly "all reads go to a single board" but functionally equivalent at the JVM level.

### 📶 Gradual Depth — Four Levels

**Level 1:** `volatile` means "when one thread changes this variable, other threads see the change immediately."

**Level 2:** Use `volatile` for: (1) stop-flags (`volatile boolean running`); (2) singleton publication (double-checked locking's `volatile instance`); (3) state flags checked by multiple threads with no compound logic. Don't use for counters, collections, or any compound operations.

**Level 3:** The JMM specifies that a volatile write happens-before any subsequent volatile read by any thread. This creates a visibility guarantee via transitivity: all writes before the volatile write are visible after the volatile read. The JVM implements this with store-release barriers after writes and load-acquire barriers before reads.

**Level 4 — TSO model:** On x86 hardware (TSO — Total Store Order), every store is already a release store and every load is a load-acquire. Volatile on x86 costs almost nothing for reads (free) and slightly more for writes (need `SFENCE` or `MFENCE`). On ARM (weakly ordered), volatile adds more barriers. The JMM abstracts hardware specifics — code using `volatile` is portable.

### ⚙️ How It Works (Mechanism)

**volatile read/write bytecode:**
```java
// Source:
volatile int counter = 0;
counter = 5;     // volatile write
int val = counter; // volatile read

// javap shows:
// putfield counter → JVM: store-release barrier
// getfield counter → JVM: load-acquire barrier
```

**Memory barrier on x86 (simplified):**
```
volatile write:
  MOV [counter], 5     ; write value
  SFENCE               ; store fence: all stores committed

volatile read:
  ; On TSO/x86: LFENCE often not needed (loads are ordered)
  MOV eax, [counter]   ; read value from memory
```

**Classic double-checked locking (requires volatile):**
```java
class Singleton {
    private static volatile Singleton instance;

    static Singleton get() {
        if (instance == null) {
            synchronized (Singleton.class) {
                if (instance == null) {
                    instance = new Singleton();
                    // volatile write: ensures full construction
                    // visible before 'instance' is non-null
                }
            }
        }
        return instance; // volatile read: no stale null
    }
}
```

**Why volatile is required in DCL:**
`instance = new Singleton()` is three steps:
1. Allocate memory
2. Initialize fields  
3. Assign reference to `instance`

Without `volatile`, a JIT can reorder steps to 1→3→2. Thread T2 reads non-null `instance` but sees uninitialized fields. `volatile` prevents this reorder via the store-release barrier.

### 🔄 The Complete Picture — End-to-End Flow

NORMAL FLOW (stop flag):
```
[T1 sets volatile running = false]
    → [Store-release barrier]         ← YOU ARE HERE
    → [Value flushed to main memory]
    → [T2 next volatile read of running]
    → [Load-acquire barrier]
    → [T2 reads false from main memory]
    → [T2 exits loop: shutdown complete]
```

FAILURE PATH:
```
[Counter uses volatile for count++]
    → [T1: volatile read: count=5]
    → [T2: volatile read: count=5 (simultaneously)]
    → [T1: add 1: count=6]
    → [T2: add 1: count=6]
    → [Both write 6 — T1's increment lost]
    → [Use AtomicInteger or synchronized instead]
```

WHAT CHANGES AT SCALE:
At high-frequency access (millions/second), volatile reads and writes add measurable latency compared to entirely CPU-local data. On x86, reads are free but writes have ~40ns latency (memory fence). On ARM, both can be expensive. Hot-path metrics should never use volatile — use `AtomicLong` with `lazySet()` for metrics that don't need immediate visibility.

### 💻 Code Example

Example 1 — Stop flag (correct volatile use):
```java
public class WorkerService {
    private volatile boolean running = false;
    private Thread workerThread;

    public void start() {
        running = true;
        workerThread = new Thread(() -> {
            while (running) {  // volatile read each iteration
                processNextTask();
            }
        });
        workerThread.start();
    }

    public void stop() {
        running = false; // volatile write — worker sees on next iteration
    }
}
```

Example 2 — Volatile for single-assignment reference:
```java
class ConfigHolder {
    private volatile Config current;

    public void reload() {
        Config newConfig = loadFromFile();
        current = newConfig; // volatile write — atomic publish
    }

    public Config get() {
        return current; // volatile read — always sees latest
    }
}
// Config itself doesn't need to be threadafe if it's immutable
// volatile only guarantees the REFERENCE, not the object's state
```

Example 3 — What volatile CANNOT do:
```java
// BAD: volatile doesn't make compound operations atomic
volatile int count = 0;
count++; // non-atomic: read(count), add 1, write(count)
// FIX: use AtomicInteger
AtomicInteger count = new AtomicInteger(0);
count.incrementAndGet(); // atomic

// BAD: volatile reference to mutable object
volatile List<String> list = new ArrayList<>();
list.add("item"); // not thread-safe! volatile = just the reference
// FIX: use CopyOnWriteArrayList or synchronize add
CopyOnWriteArrayList<String> safeList = new CopyOnWriteArrayList<>();
```

### ⚖️ Comparison Table

| Mechanism | Mutual Exclusion | Visibility | Atomic Compound Ops | Overhead |
|---|---|---|---|---|
| **volatile** | No | Yes | No | Low (barrier) |
| synchronized | Yes | Yes | Yes (critical section) | Medium (lock) |
| AtomicInteger | No (CAS) | Yes | Yes (single variable) | Low-Medium |
| ReentrantLock | Yes | Yes | Yes (critical section) | Medium |

How to choose: `volatile` for simple flag/reference updates checked in multiple threads. `synchronized` for multi-step operations on shared state. `AtomicInteger/Reference` for lock-free single-variable atomic operations: `volatile` is cheapest, `AtomicInteger` is second, `synchronized` is most expensive.

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| volatile makes operations atomic | volatile makes individual reads and writes atomic, NOT compound operations. `volatile count++` is still a race condition |
| volatile is always slower than non-volatile | On x86, volatile reads are FREE (TSO ordering is already acquired-read). Only writes have overhead (store fence). On ARM, both directions have overhead |
| volatile is obsolete since synchronized handles everything | volatile is faster than synchronized for simple visibility cases. The DCL pattern requires volatile, not synchronized, to prevent construction reordering |
| `volatile int[] arr` = each array element is volatile | `volatile` on an array reference means the reference itself is volatile — individual array elements are NOT volatile. Changes to `arr[0]` are not guaranteed visible to other threads |
| volatile prevents all instruction reordering | volatile prevents reordering around the volatile access (the barrier). Reordering between non-volatile reads/writes NOT crossing a volatile access is still allowed |

### 🚨 Failure Modes & Diagnosis

**JIT-Cached Non-volatile Flag (Thread Never Stops)**

Symptom: Worker thread ignores `running = false` and continues forever.

Root Cause: JIT hoisted `running` flag read out of the loop (register caching).

Diagnostic:
```bash
# Run with JIT disabled to confirm:
java -Djava.compiler=NONE MyApp
# If thread stops correctly without JIT, flag is JIT-cached
```

Fix: Add `volatile` keyword to the flag field.

Prevention: All flags read in loops that can be set by another thread must be `volatile`.

---

**Word Tearing on non-volatile long/double**

Symptom: Read of a `long` or `double` field returns a value combining old and new bits (corrupted value).

Root Cause: 64-bit `long`/`double` writes are not atomic on 32-bit JVMs without `volatile`. The write of the upper 32 bits and lower 32 bits can be interleaved.

Fix: Declare `long`/`double` fields `volatile` if shared across threads.

Prevention: Any `long` or `double` field accessed from multiple threads should be `volatile` or synchronized. Modern 64-bit JVMs typically treat 64-bit writes as atomic, but the JMM does not guarantee it without `volatile`.

### 🔗 Related Keywords

**Prerequisites (understand these first):**
- `Memory Barrier` — volatile's visibility guarantee is implemented via hardware/JVM memory barriers; understanding barriers explains why volatile works
- `Happens-Before` — the formal JMM specification of volatile's ordering guarantee
- `synchronized` — the full-exclusion counterpart; understanding synchronized in contrast clarifies what volatile does and doesn't provide

**Builds On This (learn these next):**
- `synchronized` — extends volatile's visibility guarantee to include mutual exclusion and compound atomicity
- `Happens-Before` — the formal guarantee that volatile provides in the Java Memory Model

**Alternatives / Comparisons:**
- `synchronized` — provides both visibility and mutual exclusion; heavier than volatile
- `Memory Barrier` — the low-level hardware instruction that implements volatile

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ WHAT IT IS   │ Field modifier that forces reads/writes   │
│              │ to main memory with happens-before        │
├──────────────┼───────────────────────────────────────────┤
│ PROBLEM IT   │ CPU caches and JIT register optimisation  │
│ SOLVES       │ can make writes invisible to other threads│
├──────────────┼───────────────────────────────────────────┤
│ KEY INSIGHT  │ VISIBILITY only — no mutual exclusion.    │
│              │ count++ is STILL a race on volatile field.│
│              │ Use synchronized or AtomicInteger for ops │
├──────────────┼───────────────────────────────────────────┤
│ USE WHEN     │ Simple flags (stop signals), single-      │
│              │ assignment reference publication          │
├──────────────┼───────────────────────────────────────────┤
│ AVOID WHEN   │ Compound operations (read-modify-write);  │
│              │ collections; complex shared state         │
├──────────────┼───────────────────────────────────────────┤
│ TRADE-OFF    │ Cheap visibility vs no atomicity for      │
│              │ compound operations                       │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "Never cache this — always talk to        │
│              │  main memory, in order"                   │
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ synchronized → Memory Barrier →           │
│              │ Happens-Before → AtomicInteger            │
└──────────────────────────────────────────────────────────┘
```

---
### 🧠 Think About This Before We Continue

**Q1.** The double-checked locking pattern requires `volatile` on the `instance` field. Without `volatile`, a non-null `instance` reference could be returned to a caller before the Singleton's constructor has completed executing. Trace at the JIT instruction level: exactly which JIT reordering makes this possible (name the reordering that moves the reference assignment before field initialisation), what the caller sees when it dereferences the partially-constructed result, and why adding `volatile` prevents this with a specific barrier type (store-store, store-load, load-load, or load-store — which one?).

**Q2.** On x86 hardware with Total Store Order (TSO), volatile reads appear free (no added barrier) and volatile writes add only a store fence. On ARMv7 with weak memory ordering, BOTH reads and writes need barriers. A Java library claiming to be "cache-friendly with minimal volatile overhead" runs benchmarks ONLY on x86 (Intel). A new ARMv8 production deployment shows the library is 3x slower. Explain the fundamental difference in memory ordering guarantees between x86 TSO and ARM weakly-ordered memory, what specific overhead ARM incurs for each volatile operation that x86 does not, and why this is the JMM's deliberate architecture-independence choice rather than a bug.

