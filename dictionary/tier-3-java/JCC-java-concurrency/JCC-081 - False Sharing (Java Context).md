---
id: JCC-031
title: "False Sharing (Java Context)"
category: Java Concurrency
tier: tier-3-java
folder: JCC-java-concurrency
difficulty: ★★★
depends_on: JCC-016, JCC-078, JCC-076
used_by: JCC-082
related: JCC-047, JCC-079, JCC-060
tags:
  - java
  - concurrency
  - performance
  - advanced
  - internals
status: complete
version: 3
layout: default
parent: "Java Concurrency"
grand_parent: "Technical Dictionary"
nav_order: 81
permalink: /java-concurrency/false-sharing-java-context/
---

# JCC-081 - FALSE SHARING (JAVA CONTEXT)

⚡ **TL;DR** - False sharing occurs when two threads write to
different variables that share the same CPU cache line, causing
constant cache invalidation and destroying parallel performance
despite no logical contention.

---

| Field      | Value                                              |
|------------|----------------------------------------------------|
| Depends on | JCC-016 Java Memory Model (JMM), JCC-078 JMM Happens-Before, JCC-076 Amdahl's Law |
| Used by    | JCC-082 Busy-Wait vs Blocking                      |
| Related    | JCC-047 CAS (Compare-And-Swap), JCC-079 Lock-Free Data Structures, JCC-060 Atomic Classes |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
A parallel counter array is created: one long per thread, each
thread increments only its own counter. This should have zero
contention - each thread owns its counter. But throughput is
identical to a single shared counter. The reason: all per-thread
counters are adjacent in memory, sharing cache lines. Every write
by one CPU invalidates the shared cache line, forcing all other
CPUs to reload.

**THE BREAKING POINT:**
Performance engineers benchmark a parallel benchmark expecting
16x speedup on 16 cores. Measured speedup: 1.2x. Profiling shows
CPU utilisation is high but inter-core cache coherence traffic
(measured by `perf stat -e cache-misses`) is enormous. The "fast"
variables are on the same cache line - a hardware-level contention
invisible in the application code.

**THE INVENTION MOMENT:**
Cache-line padding was discovered empirically in high-performance
C++ and Java code. JDK 8 introduced `@Contended` annotation
(in `jdk.internal.vm.annotation`) allowing the JVM to pad fields
to cache line boundaries. `LongAdder` (Java 8) uses this internally.

**EVOLUTION:**
- **Pre-Java 8:** Manual padding with dummy fields
- **Java 8:** `@sun.misc.Contended` / `@jdk.internal.vm.annotation.Contended`
  with `-XX:+EnableContendedPadding` flag
- **Java 17+:** `@jdk.internal.vm.annotation.Contended` available
  via `--add-opens` in some contexts; third-party equivalents in
  JCTools, Agrona

---

### 📘 Textbook Definition

**False sharing** is a CPU cache coherence performance problem where
two (or more) threads write to different variables that happen to
reside within the same CPU cache line (typically 64 bytes on x86).
When one thread writes, it sends an invalidation message to all
other CPUs holding that cache line, forcing them to reload the
entire line - even though their data was not changed.

False sharing causes: high L1/L2 cache miss rates, high bus
coherence traffic, near-zero parallel speedup for independent
variables sharing a cache line.

---

### ⏱️ Understand It in 30 Seconds

**One line:** Two threads on different CPUs editing different
variables that share one cache line = constant cache wars with no
logical reason.

**One analogy:**
> Two people sharing a notepad. Person A writes in the top half;
> Person B writes in the bottom half. Every time Person A rewrites
> their half, Person B must throw away their half (to get the fresh
> notepad from Person A) and re-copy it from memory, even though
> Person B's content never changed.

**One insight:** The unit of cache coherence is not a byte or a
variable - it is a cache line (64 bytes). "Independent" variables
within 64 bytes of each other are NOT independent from the CPU's
perspective.

---

### 🔩 First Principles Explanation

**CORE INVARIANTS:**

1. CPUs operate on cache lines (typically 64 bytes on modern x86/ARM).
2. When a CPU writes to any byte within a cache line, ALL other
   CPUs' copies of that line are *invalidated* (MESI protocol).
3. Each subsequent read by another CPU requires a cache line reload
   from L3 or main memory - typically 100-200 CPU cycles penalty.
4. False sharing is *invisible in the code* - the two variables are
   logically independent but physically adjacent.
5. False sharing affects only concurrent write scenarios. Concurrent
   reads of the same cache line are fine.

**DERIVED DESIGN:**
Solution: ensure hot independently-written variables reside in
different cache lines. Achieve via:
- Padding: add dummy bytes to fill the rest of the cache line
- `@Contended` annotation: JVM adds padding automatically
- Layout control: place hot variables far apart in arrays

**THE TRADE-OFFS:**

**Gain:** Eliminating false sharing can give 10-100x speedup in
tight parallel loops with independent per-thread state.

**Cost:** Padding wastes memory (one variable per 64-byte cache
line). For hot paths in HFT or low-latency systems, the throughput
gain far outweighs the memory cost.

**ESSENTIAL vs ACCIDENTAL COMPLEXITY:**

**Essential:** Cache line coherence is inherent to multi-core
hardware. It cannot be eliminated.

**Accidental:** Object layout in Java is controlled by the JVM,
not the developer. Variables cannot be explicitly placed in memory
without JVM support (`@Contended` or VarHandle + MemoryLayout -
Project Panama).

---

### 🧪 Thought Experiment

**SETUP:** 8 threads each increment their own counter 10 million times.
All 8 counters are in a `long[]` array.

```java
long[] counters = new long[8];
// Thread i increments counters[i]
// 8 longs = 8 * 8 bytes = 64 bytes = ONE cache line
```

**WHAT HAPPENS (false sharing):**
```
Thread 0 on CPU0 writes counters[0]
-> invalidates cache line on CPU1..CPU7
Thread 1 on CPU1 reads counters[1]
-> cache miss! reload from L3 (~200 cycles)
Thread 1 writes counters[1]
-> invalidates cache line on CPU0,CPU2..CPU7
...all 8 CPUs constantly invalidating each other
```

**WHAT HAPPENS (padded - no false sharing):**
```java
// Each counter on its own 64-byte cache line
long[] counters = new long[8 * 8]; // padded
// Thread i uses counters[i * 8]
```
No invalidation between CPUs. Each CPU's cache line is private.
8x throughput improvement.

**THE INSIGHT:** Memory layout is a performance-critical design
decision in concurrent systems, not just a storage concern.

---

### 🧠 Mental Model / Analogy

> Imagine 8 workers shared a single large table (one cache line).
> Each works in their own section. But every time any worker erases
> and rewrites something, they must announce "the table changed"
> and all other workers must stop, re-examine the table, and copy
> their section onto a new surface before continuing. The fix:
> give each worker their own desk (their own 64-byte region).

**Element mapping:**
- Single table = shared 64-byte cache line
- Worker's section = one `long` field
- "Table changed" announcement = cache invalidation (MESI protocol)
- Re-examine and copy = cache line reload (100-200 cycle penalty)
- Individual desks = padded counters (one per cache line)

Where this analogy breaks down: only the writing worker triggers
the announcement, not reading workers. Readers share the table
without any inefficiency.

---

### 📶 Gradual Depth - Four Levels

**Level 1 - What it is (anyone can understand):**
Two separate pieces of data accidentally sitting too close together
in memory, so every time one thread changes its data, all other
threads must refresh their copies even though their data didn't
change.

**Level 2 - How to use it (junior developer):**
```java
// Suspect false sharing: per-thread counters in tight array
long[] counters = new long[threadCount];  // may share cache lines

// Fix: pad to ensure each counter on its own cache line
long[] counters = new long[threadCount * 16]; // 16 longs = 128 bytes
// Thread i uses counters[i * 16]
```

**Level 3 - How it works (mid-level engineer):**
The MESI (Modified-Exclusive-Shared-Invalid) protocol governs cache
line state across all CPU cores. When core 0 writes to an address,
it sends an "invalidate" bus message. All other cores that hold that
cache line transition their line to Invalid state. The next access by
another core requires a cache line fetch (L3 cache hit ~30 cycles or
DRAM fetch ~200 cycles).

`@Contended` inserts 128 bytes of padding before AND after the
annotated field (configurable via `-XX:ContendedPaddingWidth=128`)
ensuring the field occupies its own cache line exclusively.

**Level 4 - Why it was designed this way (senior/staff):**
`LongAdder` (Java 8) was designed specifically to address false
sharing in high-contention counters. Its `Cell[]` array uses
`@Contended` on each `Cell`. The design allows per-CPU local
increments, aggregating only on `sum()`. This eliminates both the
CAS contention AND false sharing that `AtomicLong` suffers under
high contention - a double elimination of performance bottlenecks.

**Expert Thinking Cues:**
- JVM processes on the same machine can also share cache lines if
  they use shared memory (mmap). A false-sharing between processes
  is the same hardware problem.
- Array element false sharing: `int[]` elements in tight loops on
  parallel streams can false-share. Use `IntStream.range()` with
  work chunks > 64 bytes worth of elements to avoid it.
- `@Contended` requires JVM flag: `-XX:+EnableContendedPadding`
  (application classes) or is always enabled for JDK internal classes.
- async-profiler `perf` mode or Linux `perf stat -e cache-misses`
  reveals false sharing at hardware level.

---

### ⚙️ How It Works (Mechanism)

**x86 MESI protocol states:**
```
M (Modified): one core has the line, it's dirty
E (Exclusive): one core has the line, clean
S (Shared): multiple cores have a clean copy
I (Invalid): line not in this core's cache

Write by core A:
  M -> broadcasts Invalidate to all cores holding the line
  Other cores: S -> I (must reload before next access)
  Reload cost: L3 hit ~30ns, DRAM ~100-200ns
```

**Memory layout of a `long[]`:**
```
long[0]: bytes 0-7   \
long[1]: bytes 8-15   | one cache line (64 bytes)
...                   |
long[7]: bytes 56-63 /

Threads writing long[0] and long[7] share the same cache line
-> every write by any thread invalidates for all others
```

**Padded layout:**
```
long[0]: bytes 0-7   \  cache line 0 (thread 0 only)
padding: bytes 8-63  /
long[1]: bytes 64-71  \ cache line 1 (thread 1 only)
padding: bytes 72-127 /
```

---

### 🔄 The Complete Picture - End-to-End Flow

**DETECTING FALSE SHARING:**
```
Parallel benchmark runs slow    <- YOU ARE HERE
       |
perf stat -e cache-misses,cache-refs -p <pid>
       |
High cache-miss rate (>10%)
with low actual memory usage?
-> Likely false sharing
       |
async-profiler -e cache-misses -d 10 -f fg.html <pid>
       |
Hotspot: per-thread counter array accesses
       |
Apply padding or @Contended fix
       |
Re-run: cache-miss rate drops, throughput improves
```

**FAILURE PATH:**
False sharing is detected only through hardware performance
counters - no Java-level tool shows it directly. Teams that only
use `jstack` or JFR lock events miss it entirely.

**WHAT CHANGES AT SCALE:**
- NUMA (Non-Uniform Memory Architecture) has additional false
  sharing effects across NUMA nodes. Inter-socket cache coherence
  traffic is 3-10x more expensive than intra-socket.
- Network stack false sharing: kernel ring buffers, TCP socket
  buffers, and NIC DMA ring buffers all suffer false sharing at
  the OS level.

---

### 💻 Code Example

**BAD - per-thread counters that false-share:**
```java
// BAD: all counters on same cache line
class FalseSharingCounter {
    // 8 longs = 64 bytes = 1 cache line - all false share!
    long[] counts = new long[8];

    void increment(int threadId) {
        counts[threadId]++;  // false sharing with all other threads
    }
}
```

**GOOD - padded long array:**
```java
// GOOD: each thread's counter on its own cache line
class PaddedCounter {
    // 16 longs per thread = 128 bytes (safe even with 128-byte lines)
    private final long[] counts;
    private static final int STRIDE = 16; // longs per cache line gap

    PaddedCounter(int threads) {
        counts = new long[threads * STRIDE];
    }

    void increment(int threadId) {
        counts[threadId * STRIDE]++;  // separated by 128 bytes
    }

    long get(int threadId) {
        return counts[threadId * STRIDE];
    }
}
```

**GOOD - use LongAdder (JDK built-in, @Contended internally):**
```java
// BEST: LongAdder uses @Contended internally
// No false sharing, no CAS contention, correct semantics
LongAdder counter = new LongAdder();
counter.increment();         // thread-safe, fast
long total = counter.sum();  // aggregate
```

**GOOD - @Contended for custom fields (JVM internals):**
```java
// Note: requires --add-opens for application code in Java 17+
// Or use -XX:+EnableContendedPadding for JDK 8 open classes
import jdk.internal.vm.annotation.Contended;

class PaddedLong {
    @Contended  // adds 128 bytes padding before+after
    volatile long value;
}
// Now: each PaddedLong.value is on its own 64-byte cache line
```

**How to measure / verify:**
```bash
# Before fix:
perf stat -e L1-dcache-load-misses,L1-dcache-loads \
    java FalseSharingBenchmark
# L1-dcache-load-misses/L1-dcache-loads > 5% = likely false sharing

# JMH benchmark comparison:
mvn package && java -jar target/benchmarks.jar \
    -t 8 FalseSharingBenchmark
# Compare throughput: FalseSharing vs Padded
# Expected: 10-100x difference
```

---

### ⚖️ Comparison Table

| Solution | Memory cost | Effort | Correctness risk | JDK version |
|---------|-------------|--------|-----------------|-------------|
| Manual long[] padding | High (8-16x) | Low | Low | Any |
| `@Contended` annotation | Moderate (128 bytes per field) | Low | Very low | 8+ |
| `LongAdder` | Moderate | Very low | None | 8+ |
| Separate objects per thread | High (object header overhead) | Low | None | Any |
| `ThreadLocal<AtomicLong>` | High | Medium | None | Any |

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| "Independent variables in different fields can never false-share" | Fields in the same Java object are laid out adjacently by the JVM. Two `long` fields in the same object very likely share a cache line. |
| "volatile alone prevents false sharing" | `volatile` provides happens-before ordering but does NOT change the physical memory layout. A volatile field can still false-share with adjacent fields. |
| "Only applies to C/C++, Java manages memory" | False sharing is a hardware problem independent of language. Java objects and arrays lay out variables in memory; adjacent writes from different threads cause the same hardware-level invalidation. |
| "Adding more threads always helps with `LongAdder`" | Under very heavy `sum()` calls, `LongAdder` aggregates cells serially. The design optimises increments, not reads. |
| "`@Contended` is available to all application code" | In Java 17+, `@jdk.internal.vm.annotation.Contended` is in a restricted module. Use it only in JDK internal code, or export via module flags. Prefer `LongAdder`/`Striped64` for application code. |

---

### 🚨 Failure Modes & Diagnosis

**Failure Mode 1: Near-zero parallel speedup despite no logical contention**

**Symptom:** Parallel benchmark on 16 cores achieves 1.5x speedup
instead of expected 16x. Each thread writes only its own variable.

**Root Cause:** All per-thread variables share cache lines.

**Diagnostic:**
```bash
# Use perf (Linux):
perf stat -e \
    LLC-load-misses,LLC-loads,\
    cache-misses,cache-references \
    java -cp . Benchmark

# High LLC-load-misses/LLC-loads ratio = false sharing
# Or: use async-profiler with perf events:
# asprof -e cache-misses -o flamegraph -f fg.html <pid>
```

---

**Failure Mode 2: Performance regression after adding a new field**

**Symptom:** Adding a new `volatile long` field to a shared object
causes a 5x throughput regression in unrelated hot paths.

**Root Cause:** The new field shares a cache line with a hot
per-thread field. Adding a single field shifts the layout enough
that a previously-isolated field now shares a cache line.

**Diagnostic:**
Use `JOL` (Java Object Layout) to inspect field positions:
```bash
# Add JOL dependency to pom.xml, then:
System.out.println(ClassLayout.parseInstance(obj).toPrintable());
# Shows offset of each field:
# OFFSET  SIZE   TYPE DESCRIPTION
#      0     4        (object header)
#      4     4        (object header)
#      8     8   long myHotField    <- offset 8
#     16     8   long myNewField    <- offset 16 (SAME cache line!)
```

**Fix:** Use `@Contended` on both fields, or reorder fields to
place unrelated hot fields in separate cache lines.

---

**Failure Mode 3: `AtomicLong` underperforms `AtomicInteger` under contention**

**Symptom:** Replacing `AtomicInteger` with `AtomicLong` in a
tight parallel counter causes throughput to drop by 30%.

**Root Cause:** On JVMs with 4-byte alignment for int vs 8-byte
for long, the `AtomicLong` field requires more padding in the object
layout, potentially pushing a previously-padded field into a shared
cache line with a neighbour.

**Diagnostic:** Compare field offsets using JOL before and after
the type change.

**Fix:** Use `LongAdder` for high-contention counters instead of
`AtomicLong` or `AtomicInteger`. It handles both CAS contention
AND false sharing internally.

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**
- [[JCC-016 - Java Memory Model (JMM)]] - the memory model within
  which cache coherence operates
- [[JCC-078 - JMM Happens-Before - Deep Rules]] - volatile ordering
  that coexists with (but does not solve) false sharing
- [[JCC-076 - Amdahl's Law]] - false sharing is a hidden serial
  fraction that Amdahl's model does not reveal

**Builds On This (learn these next):**
- [[JCC-082 - Busy-Wait vs Blocking]] - busy-wait combined with
  false sharing is catastrophic for performance
- [[JCC-079 - Lock-Free Data Structures]] - `LongAdder`'s Striped64
  uses @Contended to solve false sharing at scale

**Alternatives / Comparisons:**
- [[JCC-060 - Atomic Classes]] - `AtomicLong` still false-shares
  if placed adjacent to other hot fields; `LongAdder` does not
- `ThreadLocal` - achieves the same isolation without padding,
  at higher memory cost (full object per thread)

---

### 📌 Quick Reference Card

```
+--------------------------------------------------+
| WHAT IT IS   | Cache line contention between      |
|              | logically-independent variables    |
+--------------+------------------------------------+
| PROBLEM      | Adjacent memory writes from        |
|              | different threads cause CPU cache  |
|              | invalidation despite no sharing    |
+--------------+------------------------------------+
| KEY INSIGHT  | Unit of coherence = 64-byte cache  |
|              | line, not individual variable      |
+--------------+------------------------------------+
| USE WHEN     | Hot parallel loops with per-thread |
|              | state; HFT / low-latency systems   |
+--------------+------------------------------------+
| AVOID WHEN   | Low concurrency; not a bottleneck  |
|              | (profile first, then pad)          |
+--------------+------------------------------------+
| TRADE-OFF    | 10-100x speedup / wastes memory;   |
|              | @Contended needs JVM flag           |
+--------------+------------------------------------+
| ONE-LINER    | Thread 0: counts[0]++              |
|              | Thread 1: counts[8]++ (skip 64B)   |
+--------------+------------------------------------+
| NEXT EXPLORE | JCC-082 Busy-Wait vs Blocking,     |
|              | JCC-079 Lock-Free Data Structures  |
+--------------------------------------------------+
```

**If you remember only 3 things:**
1. CPU cache lines are 64 bytes. Any two variables within 64 bytes
   that are written by different threads will false-share.
2. Use `LongAdder` for high-contention counters - it handles both
   false sharing AND CAS contention internally with `@Contended`.
3. Detect with hardware counters (`perf stat -e cache-misses`),
   not Java-level tools like jstack or JFR.

**Interview one-liner:** "False sharing is when two threads write
to different variables that share the same 64-byte CPU cache line -
every write by one thread invalidates the other's cache, causing
100-200 cycle reloads despite zero logical contention; fixed by
padding with `LongAdder` or `@Contended`."

---

### 💎 Transferable Wisdom

**Reusable Engineering Principle:** Performance invariants operate
at different levels - logical (only one thread writes field X),
physical (hardware cache lines), and temporal (write frequency).
Optimising at one level while ignoring another yields confusing
results. Always profile at the level of the suspected bottleneck.

**Where else this pattern appears:**
- **Kernel network ring buffers:** Linux kernel developers pad RX/TX
  descriptor rings to cache line boundaries to prevent false sharing
  between CPU cores processing different NIC queues.
- **LMAX Disruptor:** The Disruptor's ring buffer uses extensive
  cache line padding - every sequence counter, every ring buffer
  slot, and the producer/consumer positions are on their own cache
  lines. This is the primary reason Disruptor outperforms standard
  Java queues by 6-10x.
- **Apache Kafka partition assignment:** Kafka partitions are
  processed by separate consumer group threads. The partition
  design is in part motivated by ensuring per-partition state is
  not shared between consumer threads - a software-level analog of
  false sharing prevention.

---

### 💡 The Surprising Truth

False sharing can make a parallel program run SLOWER than its
single-threaded equivalent. A tight CAS loop on `AtomicLong` with
16 threads on a 16-core machine can be 3-5x slower than a sequential
`long++` loop because the CAS creates write contention that
invalidates all 16 cores' cache lines continuously. The 16 threads
actively harm each other through the coherence protocol. Adding
thread 17 makes it worse. The paradox - more parallelism, lower
throughput - is explained entirely by hardware-level false sharing
and CAS contention, not by any application logic. This is why
`LongAdder` (designed precisely for this scenario) can be 100x
faster than `AtomicLong` under identical concurrent increment
workloads.

---

### 🧠 Think About This Before We Continue

**Question 1 (Root Cause):** You benchmark a parallel quicksort
on 16 cores. It divides the array into 16 chunks and sorts each
concurrently, then merges. Under arrays of 1,000 elements per
thread the speedup is 0.8x (slower than sequential). Under 1,000,000
elements per thread the speedup is 14x. What explains the performance
difference, and what role does false sharing play in the small-array
case versus overhead or cache warming effects?

*Hint:* For 1,000 elements per thread (8,000 bytes), all 16 chunks
fit in L2 cache shared by pairs of cores. Investigate whether the
chunks, not just counters, can cause false sharing during the sort
itself and at what element count they overflow to L3.

---

**Question 2 (Design Trade-off):** `LongAdder` uses per-CPU cells
padded with `@Contended`. The `sum()` method iterates all cells.
Under a workload with 10,000 increments per second and `sum()`
called 1,000 times per second by a monitor thread, design the
optimal architecture. Would you use `LongAdder`, `AtomicLong`, or
a custom solution? Under what throughput ratio of write-to-read
does each approach win?

*Hint:* Model `LongAdder.sum()` as O(cells) where cells = min(N,
contention-driven growth). Study cell contraction (it doesn't) and
estimate the cross-cell coherence cost of `sum()` at 1,000 calls/second.

---

**Question 3 (System Interaction):** A Java application and a C++
application run on adjacent CPU cores (NUMA node 0) and share a
memory-mapped file. The Java process writes field A and the C++
process writes field B, which happen to be 32 bytes apart in the
mmap'd region. Describe the exact hardware mechanism causing
degradation and design a file layout protocol that eliminates it.

*Hint:* Research cross-process MESI coherence (invalid state
propagation crosses process boundaries through the L3 cache bus),
and how `posix_memalign` or `alignas` in C++ and
`MemoryLayout.paddingLayout()` / `Arena` in Java (Project Panama)
can enforce 64-byte alignment in shared memory regions.

