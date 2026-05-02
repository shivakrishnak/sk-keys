---
layout: default
title: "False Sharing"
parent: "Operating Systems"
nav_order: 113
permalink: /operating-systems/false-sharing/
number: "0113"
category: Operating Systems
difficulty: ★★★
depends_on: Cache Line, NUMA, Concurrency vs Parallelism
used_by: Lock-Free Data Structures, Java volatile, Thread-per-core patterns
related: Cache Line, @Contended, perf c2c, MESI protocol
tags:
  - os
  - hardware
  - concurrency
  - performance
  - deep-dive
---

# 113 — False Sharing

⚡ TL;DR — False sharing occurs when two threads write to different variables that happen to share a 64-byte cache line, causing invisible cache-coherence serialisation that mimics lock contention.

| #0113           | Category: Operating Systems                                        | Difficulty: ★★★ |
| :-------------- | :----------------------------------------------------------------- | :-------------- |
| **Depends on:** | Cache Line, NUMA, Concurrency vs Parallelism                       |                 |
| **Used by:**    | Lock-Free Data Structures, Java volatile, Thread-per-core patterns |                 |
| **Related:**    | Cache Line, @Contended, perf c2c, MESI protocol                    |                 |

---

### 🔥 The Problem This Solves

WORLD WITHOUT IT:
You add parallelism to your code — two threads each increment their own counter. No shared state, no locks. You expect 2× throughput on 2 CPUs. You benchmark: you get 20% throughput improvement, not 200%. The code is logically correct and lock-free. Where is the slowdown?

THE BREAKING POINT:
The counters are adjacent in memory. Both fit in the same 64-byte cache line. When Thread 0 writes counter0, the cache line is marked "Modified" on CPU 0 — CPU 1's copy of that line is invalidated. Thread 1 then writes counter1 (in the same line) — must acquire the line from CPU 0 first. This repeats every increment. Two "independent" operations are serialised by the cache coherence protocol. The code looks lock-free, but the hardware inserted an invisible lock.

THE INVENTION MOMENT:
This problem was formally described in the early 1990s as multi-core systems became common. The term "false sharing" distinguishes it from "true sharing" (where threads actually share data). The fix — cache-line padding — was adopted in the JDK itself: `java.util.concurrent.atomic.LongAdder` (JDK 8), `ForkJoinPool`, and `ConcurrentHashMap` all use `@Contended` padding.

---

### 📘 Textbook Definition

**False sharing** is a cache coherence performance hazard that occurs when multiple CPU cores repeatedly write to different variables that reside within the same cache line. Even though the variables are logically independent, the hardware coherence protocol (e.g., MESI) enforces ownership of the entire cache line — not individual bytes. Consequently, every write by one core invalidates the cache line in all other cores, forcing them to re-acquire ownership before their next write. The result is serialised writes despite no logical data dependency, causing throughput degradation of 4–20× compared to code without contention.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
Two threads writing different variables in the same 64-byte block cause the hardware to silently serialise them as if they shared a lock.

**One analogy:**

> Two colleagues share a single whiteboard (cache line) divided into two columns (two variables). Every time one writes in their column, an office policy (MESI protocol) requires erasing the other person's copy of the entire whiteboard and handing it to them first. Neither person is overwriting the other's work — but they can't write simultaneously because of the policy. The whiteboard is "falsely" shared.

**One insight:**
False sharing is uniquely dangerous because it is invisible. No lock appears in code review. Profilers show CPU utilization at 100%. The bug manifests only under load on multi-core hardware, making it hard to reproduce in single-threaded tests or low-concurrency environments.

---

### 🔩 First Principles Explanation

CORE INVARIANTS:

1. Cache coherence is enforced per cache line (64 bytes), not per byte.
2. Only one CPU can hold a cache line in Modified state at a time.
3. A write requires Modified state; acquiring Modified state invalidates all other CPU copies.
4. False sharing occurs when the cache line contains both Thread A's write target and Thread B's write target simultaneously.

DERIVED DESIGN:
The MESI protocol state transitions for false sharing:

```
Initial: both CPUs cache the line in S(hared) state
CPU 0 writes var0: S → M (sends BusUpgr, invalidates CPU 1)
CPU 1 writes var1: I → M (sends BusRd, CPU 0 flushes to L3)
CPU 0 writes var0: I → M (sends BusRd, CPU 1 flushes to L3)
...
```

Each write cycle: ~100–200ns of cache coherence traffic (L3 or memory round trip), vs 4ns for an L1 cache hit. At 1 billion iterations per second, the coherence overhead consumes the entire CPU budget.

THE TRADE-OFFS:
Cost of false sharing: 10–40× slowdown on contended cache lines.
Cost of fix (padding): memory per padded object increases by 60 bytes (per 64-byte line).
Trade-off decision: always pad in hot-path concurrent data structures; evaluate memory cost for large arrays.

---

### 🧪 Thought Experiment

SETUP:

```
long[] counters = {0, 0};  // indices 0 and 1
Thread A: while (true) counters[0]++;  // on CPU 0
Thread B: while (true) counters[1]++;  // on CPU 1
counters[0] at heap offset 24 (header=12, pad=4, first_elem=8)
counters[1] at heap offset 32 — same cache line as [0]!
```

PROFILING OUTPUT:

```
No false sharing: 1,200,000,000 increments/sec (each thread)
With false sharing: 90,000,000 increments/sec (each thread)
→ 13× slowdown for a logically lock-free operation
→ CPU utilization: 100% (spinning on cache coherence, not doing work)
```

THE INSIGHT:
The CPU is not "idle" — it's 100% busy transferring cache line ownership. From the OS and profiler perspective, both CPUs are saturated. No lock is visible. The degradation looks like an algorithmic issue, not a hardware one.

---

### 🧠 Mental Model / Analogy

> Think of a cache line as a shared hotel key card (one per room). Two guests (two threads) in the same room share one key card. Guest A needs the card to enter (modify their side of the room). While A has the card, Guest B (also in the same room but accessing their own dresser) must wait. Even though neither person is touching the other's belongings, they share the access mechanism.

> The fix: give each guest their own room — pad variables to different cache lines. Each guest has their own key card.

Where the analogy breaks down: in the real hardware, the "room" (cache line) can hold 64 bytes and multiple guests can read from it simultaneously (Shared state). The contention only arises when a guest needs to WRITE. Pure read-sharing is efficient; it's write-write contention that causes false sharing.

---

### 📶 Gradual Depth — Four Levels

**Level 1 — What it is (anyone can understand):**
Even if two threads write to different variables, if those variables are close together in memory (within 64 bytes), the CPU treats them as the same block. Each write forces the other CPU to give up its copy first. This is like two people constantly passing a single notebook back and forth even though they're writing on different pages.

**Level 2 — How to use it (junior developer):**
Detect with `perf c2c report` (Linux) or Intel VTune's memory profiling. Fix in Java: annotate hot fields with `@sun.misc.Contended` and run with `-XX:-RestrictContended`. In JDK 17+, use `@jdk.internal.vm.annotation.Contended`. Fix in C/C++: add `alignas(64)` and explicit padding. Look for false sharing in: per-thread statistics/counters, header fields in concurrent queues, flags in concurrent data structures.

**Level 3 — How it works (mid-level engineer):**
`perf c2c` (cache-to-cache) works by recording `MEM_LOAD_L3_MISS` events (sample at 100Hz) and correlating the loading address with the modifying CPU via HITM (Hit in Modified state) events. A high HITM rate for a specific cache line + multiple different CPUs = false sharing. The RFO (Request For Ownership) is the hardware message that implements write: CPU sends RFO to the cache hierarchy; the cache controller finds the line in Modified state on another CPU, notifies it to write back, then grants ownership to the requesting CPU. RFO latency: ~40ns for L3, ~150ns for cross-socket (NUMA).

**Level 4 — Why it was designed this way (senior/staff):**
The MESI protocol enforces coherence at cache-line granularity because sub-line coherence would require tracking the state of every byte — an exponential increase in control overhead. At 64-byte lines, a 4MB L1 has 65,536 entries, each needing 2 MESI bits + tags. Byte-level coherence of a 4MB L1 would need 4M state bits + vastly more complex coherence messages. The 64-byte granularity is the engineering balance between tracking overhead and false sharing probability. Hardware vendors considered word-level coherence (8 bytes) for some designs but rejected it due to 8× increase in coherence traffic for read-sharing scenarios.

---

### ⚙️ How It Works (Mechanism)

```
┌────────────────────────────────────────────────────────┐
│              FALSE SHARING TIMELINE                    │
├────────────────────────────────────────────────────────┤
│  Memory: [var0=0][var1=0]....[padding 48B] = 64 bytes  │
│                  ← same cache line ─────────────────→  │
│                                                        │
│  CPU 0 (has cache line, state=S):                      │
│    write var0++                                        │
│    → send BusUpgr (invalidate other copies)            │
│    → state = M(odified)                                │
│    → write completes (L1 hit)                          │
│                                                        │
│  CPU 1 (cache line now I=Invalid):                     │
│    write var1++                                        │
│    → send RFO (Request For Ownership)                  │
│    → CPU 0 receives RFO, writes back to L3             │
│    → CPU 0 state: M → I                                │
│    → CPU 1 reads line from L3 (50+ cycles)             │
│    → CPU 1 state: I → M                                │
│    → write completes                                   │
│                                                        │
│  CPU 0: next write var0 → I → RFO cycle again          │
│  [Both CPUs ping-pong cache line ownership forever]    │
└────────────────────────────────────────────────────────┘
```

---

### 🔄 The Complete Picture — End-to-End Flow

BEFORE FIX:

```
ConcurrentHashMap.CounterCell[] cells = new CounterCell[32];
Thread 0 writes cells[0].value  ─┐
Thread 1 writes cells[1].value  ─┤── same cache line (no padding)
Thread 2 writes cells[2].value  ─┤── all 32 cells might share lines
...                              ─┘
→ All 32 threads serialising through cache coherence
→ increment() is effectively single-threaded
```

AFTER FIX (JDK LongAdder implementation):

```java
@sun.misc.Contended  // 128-byte padding around each Cell
static final class Cell {
    volatile long value;
    Cell(long x) { value = x; }
    ...
}
```

```
Thread 0 writes Cell[0].value   → cache line [0..63]
Thread 1 writes Cell[1].value   → cache line [256..319]  (128B padding)
Thread 2 writes Cell[2].value   → cache line [512..575]
→ Each thread has exclusive cache line
→ No coherence traffic between threads
→ N threads: N× throughput
```

---

### 💻 Code Example

Example 1 — Demonstrate and fix false sharing in Java:

```java
import jdk.internal.vm.annotation.Contended;  // JDK 9+
// Or: @sun.misc.Contended  // JDK 8, with -XX:-RestrictContended

// BAD: false sharing
class FalseSharedCounters {
    volatile long counter0 = 0;  // offset ~12
    volatile long counter1 = 0;  // offset ~20 — same cache line
}

// GOOD: padded counters — each on its own cache line
class PaddedCounters {
    @Contended volatile long counter0 = 0;
    @Contended volatile long counter1 = 0;
}

// BENCHMARK (typical results on 2-core machine):
// FalseSharedCounters: ~100M increments/sec per thread
// PaddedCounters:      ~800M increments/sec per thread
// Improvement: ~8×
```

Example 2 — Manual padding in C (no language support):

```c
// Padding struct to cache line size
typedef struct {
    long value;
    char _pad[56];  // 8 + 56 = 64 bytes = 1 cache line
} __attribute__((aligned(64))) CacheLinePadded;

CacheLinePadded counters[MAX_THREADS];

// Thread i only writes counters[i].value
// All counters[i] are on distinct cache lines
// Zero false sharing
void thread_func(int thread_id) {
    for (long i = 0; i < 1000000000L; i++) {
        counters[thread_id].value++;
    }
}
```

Example 3 — Detect false sharing with perf c2c:

```bash
# Record cache-to-cache transfer events
perf c2c record --call-graph dwarf -- ./my_benchmark

# Analyze false sharing
perf c2c report -NN -g --stdio 2>/dev/null | head -80
# Look for:
#   HITM  Cnt        Object     Symbol   Shared Cache Line Data
#   Total  HITM  Local  Lcl Hitm  Remote  CPU    Object
#   High HITM count + multiple CPUs = false sharing
#   "Rmt Hit" = cross-NUMA false sharing (worst case)

# With vtune (Intel):
vtune -collect memory-access -result-dir vtune_result ./my_benchmark
vtune -report hotspots -result-dir vtune_result
# Shows "False Sharing" in memory access analysis
```

Example 4 — LongAdder internals (JDK pattern to copy):

```java
// JDK's LongAdder avoids false sharing by padding each Cell
// This pattern is reusable for any high-contention counter

public class NUMAFriendlyCounter {
    // Each thread has its own Cell on its own cache line
    @Contended
    static final class Cell {
        volatile long value;
        Cell(long x) { value = x; }
        boolean cas(long cmp, long val) {
            return VALUE.compareAndSet(this, cmp, val);
        }
        private static final VarHandle VALUE;
        static {
            VALUE = MethodHandles.lookup().findVarHandle(
                Cell.class, "value", long.class);
        }
    }

    private volatile Cell[] cells;
    private volatile long base;

    public void add(long x) {
        Cell[] as; long b, v; int m; Cell a;
        if ((as = cells) != null || !casBase(b = base, b + x)) {
            // Use per-thread cell to avoid contention
            int i = (int)(Thread.currentThread().getId() % as.length);
            a = as[i];
            if (!a.cas(v = a.value, v + x)) {
                // contention — probe other cells
            }
        }
    }

    public long sum() {
        Cell[] as = cells; long sum = base;
        if (as != null)
            for (Cell a : as) sum += a.value;
        return sum;
    }
}
```

---

### ⚖️ Comparison Table

| Scenario                                              | Sharing Type      | Cause                         | Fix                                |
| ----------------------------------------------------- | ----------------- | ----------------------------- | ---------------------------------- |
| Two threads write same variable                       | True sharing      | Intentional shared state      | Synchronisation, lock-free         |
| **Two threads write different vars, same cache line** | **False sharing** | **Memory layout coincidence** | **Cache line padding**             |
| Two threads read same cache line                      | Read sharing      | —                             | No fix needed (S state, efficient) |
| Two threads: one reads, one writes same line          | Mixed sharing     | Could be true sharing         | Validate logic first; then pad     |

---

### ⚠️ Common Misconceptions

| Misconception                                 | Reality                                                                                                                   |
| --------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------- |
| "Lock-free code can't have contention"        | False sharing is hardware-level contention; no lock exists in code, but the cache line IS the lock                        |
| "volatile eliminates false sharing"           | volatile ensures visibility but doesn't change memory layout; false sharing still occurs with volatile fields             |
| "@Contended always works in application code" | In JDK 8–17, @Contended is restricted to JDK internal classes by default; use -XX:-RestrictContended for application code |
| "Only concurrent code has false sharing"      | False sharing requires concurrent writes; purely sequential single-threaded code has no false sharing                     |
| "Padding to 64 bytes is always enough"        | ARM's L3 may have 128-byte prefetch lines; AMD EPYC within-socket topology complicates this; 128-byte padding is safer    |

---

### 🚨 Failure Modes & Diagnosis

**1. Lock-Free Counter Array Performing Like a Lock**

Symptom: Adding thread-local counters to reduce contention makes performance worse as thread count increases.

Root Cause: Counter array elements are adjacent in memory; incrementing counters[i] invalidates the cache line for counters[i±1..7].

Diagnostic:

```bash
# JVM: JOL (Java Object Layout) shows field positions
import org.openjdk.jol.info.ClassLayout;
System.out.println(ClassLayout.parseClass(Counter[].class)
    .toPrintable());
# Look for: adjacent fields within 64 bytes

# perf c2c (Linux)
perf c2c record -g -- java -cp . FalseSharingBenchmark
perf c2c report | grep -A 5 "HITM"
```

Fix: Use `@Contended` on each Counter object's value field, or space array elements by 8 (longs) instead of 1.

---

**2. ConcurrentHashMap Throughput Lower Than Expected**

Symptom: ConcurrentHashMap write throughput doesn't scale with thread count; profiling shows no apparent lock contention.

Root Cause: The `size` and `modCount` counters in older ConcurrentHashMap implementations shared cache lines with frequently-written segment locks.

Diagnostic: (Rarely seen in JDK 8+, but illustrative)

```bash
perf c2c report
# Shows HITM hits on ConcurrentHashMap internal fields
```

Fix: JDK 8 rewrote ConcurrentHashMap to use LongAdder-based size counting with @Contended padding. Use JDK 8+.

Prevention: Prefer JDK 8+ collections; validate upgrade resolves issue with `perf c2c`.

---

**3. False Sharing in Off-Heap Byte Buffer (Netty ByteBuf)**

Symptom: Netty application with high write throughput shows unexpected CPU saturation; cache misses dominate profiler output.

Root Cause: Multiple threads writing to adjacent regions of a large `ByteBuf` (Netty's off-heap buffer); adjacent write positions within 64 bytes cause false sharing at cache level.

Diagnostic:

```bash
# Linux perf c2c for Netty
perf c2c record -g -- java -cp netty-all.jar ... MyNettyApp
perf c2c report | head -50
# Look for HITM hits on ByteBuf backing memory
```

Fix: Align each thread's write region to 64-byte boundaries; use `ByteBuf.slice()` with 64-byte-aligned offsets.

Prevention: When allocating per-thread regions in shared buffers, always round start offset up to next 64-byte boundary.

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**

- `Cache Line` — false sharing is a consequence of cache line granularity; must understand cache lines first
- `NUMA` — cross-NUMA false sharing (remote HITM) is 3–5× more expensive than local false sharing
- `Concurrency vs Parallelism` — false sharing is a concurrency bug that appears in parallel code

**Builds On This (learn these next):**

- `Lock-Free Data Structures` — CAS operations still suffer from false sharing; understanding both is necessary for correct implementation
- `Java volatile` — volatile fields trigger cache line flush/invalidate, compounding false sharing
- `Thread-per-core patterns` — pinning threads to cores can reduce cross-NUMA false sharing

**Alternatives / Comparisons:**

- `True sharing` — intentional shared data with proper synchronisation; distinct from false sharing in cause and fix
- `ThreadLocal` — JVM's per-thread heap segments; naturally avoids false sharing for thread-local data
- `Disruptor (LMAX)` — ring buffer design explicitly designed to eliminate false sharing; benchmark reference for false-sharing-free concurrent queue

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ WHAT IT IS   │ Two threads write different vars in the  │
│              │ same 64-byte cache line → serialisation  │
├──────────────┼───────────────────────────────────────────┤
│ PROBLEM IT   │ Lock-free code has invisible hardware     │
│ SOLVES       │ contention; fix: cache-line padding       │
├──────────────┼───────────────────────────────────────────┤
│ KEY INSIGHT  │ Cache coherence is per line, not per      │
│              │ byte — memory layout creates the lock    │
├──────────────┼───────────────────────────────────────────┤
│ USE WHEN     │ Diagnosing poor parallel performance;     │
│              │ designing per-thread counters/queues      │
├──────────────┼───────────────────────────────────────────┤
│ AVOID WHEN   │ N/A — eliminate it whenever detected;    │
│              │ memory cost of padding is always worth it │
├──────────────┼───────────────────────────────────────────┤
│ TRADE-OFF    │ Zero cache coherence traffic vs extra     │
│              │ memory per padded field (60 bytes/field)  │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "Separate per-thread writes by 64 bytes  │
│              │  or the cache line becomes your lock"    │
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ @Contended → LongAdder → Disruptor        │
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** The LMAX Disruptor ring buffer uses a clever layout to prevent false sharing: each producer claims a slot by atomically incrementing a sequence, writes to that slot, then publishes by updating the cursor. All three fields (sequence, ring buffer slot, cursor) need cache-line isolation from each other. Design the exact memory layout of a 1024-slot Disruptor ring buffer showing: the byte offset of each element, which elements share cache lines, and why the "false sharing between adjacent ring buffer slots" problem doesn't occur for producers/consumers that process at different speeds.

**Q2.** Modern Intel CPUs (Skylake+) implement "LLC (Last Level Cache) Interconnect" via a ring bus or mesh topology where each core's L3 slice is connected to adjacent slices. If Thread A (on Core 0) and Thread B (on Core 15) both write to adjacent variables in the same cache line, the coherence message must traverse 15 hops. Compare the coherence latency for: (a) adjacent cores (1 hop), (b) diagonal cores (7 hops on a ring), and (c) two sockets (UPI). At what write frequency does the hop count stop mattering (prefetcher masks the latency) and at what frequency does it dominate throughput?
