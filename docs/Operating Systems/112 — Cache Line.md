---
layout: default
title: "Cache Line"
parent: "Operating Systems"
nav_order: 112
permalink: /operating-systems/cache-line/
number: "0112"
category: Operating Systems
difficulty: ★★★
depends_on: Virtual Memory, NUMA, Memory Management Models
used_by: False Sharing, Java volatile, Lock-Free Data Structures
related: CPU cache, L1/L2/L3, Cache Coherence (MESI), @Contended
tags:
  - os
  - hardware
  - memory
  - performance
  - concurrency
---

# 112 — Cache Line

⚡ TL;DR — A cache line (64 bytes on x86) is the smallest unit the CPU transfers between RAM and cache; understanding it explains both peak performance and common multi-threaded bugs.

| #0112           | Category: Operating Systems                             | Difficulty: ★★★ |
| :-------------- | :------------------------------------------------------ | :-------------- |
| **Depends on:** | Virtual Memory, NUMA, Memory Management Models          |                 |
| **Used by:**    | False Sharing, Java volatile, Lock-Free Data Structures |                 |
| **Related:**    | CPU cache, L1/L2/L3, Cache Coherence (MESI), @Contended |                 |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
If CPUs fetched memory one byte at a time, the memory bus would need to handle billions of individual byte-request/response round trips per second. Each round trip has latency overhead (address decoding, bus arbitration, row/column activation in DRAM). The CPU would stall on almost every instruction waiting for a byte.

**THE BREAKING POINT:**
Modern CPUs can execute 4+ instructions per nanosecond. DRAM latency is 60–80ns — that's 240–320 CPU cycles of stall per memory access. If you fetched individual bytes, your 4 GHz CPU would spend 99% of its time waiting for RAM.

**THE INVENTION MOMENT:**
The cache line is the solution: instead of fetching 1 byte, always fetch 64 bytes (the cache line). This exploits **spatial locality** — if you accessed address X, you'll likely access X+1, X+2, ..., X+63 soon. Pay one 60ns round trip to DRAM, fill the cache line, then serve the next 63 accesses from L1 cache at 4 cycles (~1ns).

---

### 📘 Textbook Definition

A **cache line** (also called a **cache block**) is the minimum unit of data transfer between the CPU cache hierarchy and main memory. On x86-64, cache lines are 64 bytes. When a CPU reads any address, the entire 64-byte cache line containing that address is loaded into the L1 (and L2, L3) cache. Subsequent accesses to any address within that 64-byte range are served from cache (nanoseconds) without going to RAM. Cache coherence protocols (e.g., MESI) ensure that when multiple CPUs cache the same line, modifications are propagated correctly — a modified line is either invalidated or updated in all other CPU caches before the modifying CPU writes a new value.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
The CPU always fetches 64 bytes at once from RAM — not just the byte you asked for — because nearby bytes are almost always needed next.

**One analogy:**

> Cache lines are like library book trolleys. Instead of fetching one page from a book (one byte), the librarian brings you the whole trolley of nearby books (64 bytes). Chance is you'll need those books too. The trolley stays at your desk (in cache) until you're done. If another librarian (CPU) also wants books from your trolley, they get a copy — and if they write in one, your copy gets a "stale" stamp.

**One insight:**
The cache line is the reason that iterating an array is 10× faster than iterating a linked list of the same size. An array access loads 8 adjacent `long` values (64 bytes = 8 × 8 bytes) in one DRAM round trip; a linked list pointer may point anywhere in memory — each element might be in a different cache line, requiring a new DRAM round trip for each.

---

### 🔩 First Principles Explanation

**CORE INVARIANTS:**

1. Cache line size: 64 bytes on all modern x86-64 CPUs (since Pentium 4).
2. Memory access granularity: even reading/writing 1 byte causes an entire cache line to be loaded.
3. Cache line ownership: only one CPU can hold a cache line in "Modified" state (MESI protocol).
4. Cache line invalidation: when CPU A modifies a cache line, CPU B's copy is invalidated.

**DERIVED DESIGN:**
Cache lines create two important phenomena:

- **Spatial locality exploitation**: pack related data into 64-byte aligned blocks to maximise cache line utilisation. A 64-byte struct that fits in one cache line requires 1 DRAM access; the same data scattered across 64 different addresses requires 64 DRAM accesses.
- **False sharing**: two CPUs accessing different fields within the same cache line cause cache coherence invalidations even though they're not logically sharing data. CPU A modifies field X, CPU B modifies field Y — but X and Y are in the same 64-byte cache line, so every modification by A invalidates B's cache and vice versa.

**THE TRADE-OFFS:**
**Gain:** Exploits spatial locality dramatically; single DRAM access serves 8 longs / 16 ints / 64 bytes; prefetching can hide DRAM latency entirely for sequential access.
**Cost:** Wasted bandwidth if accessed data has no spatial locality (e.g., pointer-chasing); false sharing in concurrent code causes cache coherence traffic that serialises "independent" operations.

---

### 🧪 Thought Experiment

**SETUP:**
Two threads, each incrementing their own counter 1 billion times.

WITHOUT false sharing:

```java
// Each counter on its own cache line
long[] counters = new long[16];  // 128 bytes → 2 cache lines
// Thread 0 uses counters[0], Thread 1 uses counters[8]
// They're on different cache lines → no interference
// Throughput: 2 threads × ~1 billion/sec = ~2 billion/sec
```

WITH false sharing:

```java
// Adjacent counters — same 64-byte cache line!
long counter0 = 0;  // at offset 0
long counter1 = 0;  // at offset 8 — same 64-byte cache line!
// Thread 0 increments counter0: invalidates cache line on CPU 1
// Thread 1 increments counter1: invalidates cache line on CPU 0
// Both threads wait for cache line ownership transfer each iteration
// Throughput: ~200–500 million/sec (4–10× slower than no sharing!)
// The threads appear to not interfere but suffer as if they share a lock
```

**THE INSIGHT:**
False sharing makes two independent variables behave as if they were sharing a lock, with no lock visible in the code. The "lock" is the cache line itself.

---

### 🧠 Mental Model / Analogy

> Imagine a shared whiteboard (cache line) where two colleagues each own one column. Every time someone writes in their column (modifies their field), the other person's copy of the board is stamped INVALID and they must request a fresh copy before writing again. Even though they never write in each other's column, the board-copying process (cache coherence protocol) serialises their work.

> The solution is to give each person their own whiteboard (pad to a different cache line). Now they can write independently at full speed — their whiteboards are never confused.

Where this analogy breaks down: whiteboards don't have the MESI complexity (Modified, Exclusive, Shared, Invalid states). The real protocol is more nuanced: a line can be "Shared" (read by multiple CPUs, valid) or "Modified" (written by one CPU, all others must invalidate). The "Exclusive" state allows the CPU to know it has the only copy and can upgrade to Modified without a coherence message.

---

### 📶 Gradual Depth — Four Levels

**Level 1 — What it is (anyone can understand):**
The CPU loads 64 bytes at a time from memory, even if you only asked for 1 byte. This is a cache line. If nearby data is needed next (usually is), it's already loaded — fast. But if two threads write different data in the same 64 bytes, they accidentally slow each other down.

**Level 2 — How to use it (junior developer):**
Keep related fields together in structs/classes (spatial locality). Separate frequently-written fields of different threads by 64 bytes (`@sun.misc.Contended` in Java, `__attribute__((aligned(64)))` in C). Prefer arrays over linked lists for sequential access. In Java, `@Contended` (JDK 8+) adds 128 bytes of padding around annotated fields (run with `-XX:-RestrictContended`). In C/C++, `alignas(64)` + padding.

**Level 3 — How it works (mid-level engineer):**
CPU L1 cache is typically 32–48KB, 8-way set-associative, 4-cycle hit latency. Cache lines are 64 bytes. A 32KB L1 holds 512 cache lines. Cache sets are indexed by bits [6:11] of the physical address (for 64-byte lines, 8-way, 32KB); the cache tag is bits [12:N]. An access to a line not in L1: L1 miss → L2 check (12 cycles) → L3 check (50 cycles) → DRAM (300+ cycles). Prefetchers (hardware and software) detect sequential access patterns and pre-load lines into L1 before they're needed. MESI protocol: a core wanting to write a "Shared" cache line sends a BusUpgrade message; all other cores with that line receive an invalidation, change their state to Invalid, and the writing core becomes the sole "Modified" holder.

**Level 4 — Why it was designed this way (senior/staff):**
Cache line size (64 bytes) is an engineering balance between two competing pressures: larger cache lines exploit more spatial locality per DRAM round trip, but waste bandwidth if the extra bytes are never accessed (prefetched but useless). At 8-byte words, a 64-byte line = 8 consecutive longs — empirically the right balance for typical application access patterns. The choice of 64 bytes dates to the Pentium 4 (2000) and has remained stable because: (1) DRAM row access latency dominates (not column latency), so reading 64 vs 32 bytes has minimal extra cost; (2) typical struct fields cluster within 64 bytes; (3) the MESI coherence overhead is per-line, so larger lines reduce coherence message frequency. The alternative (128-byte lines) would double false-sharing impact for most workloads.

---

### ⚙️ How It Works (Mechanism)

```
┌────────────────────────────────────────────────────────┐
│              CACHE LINE MECHANICS                      │
├────────────────────────────────────────────────────────┤
│  Physical address: 0x7FFFD3A00040                      │
│  Cache line start: 0x7FFFD3A00040 (64-byte aligned)    │
│  Cache line bytes: [40..7F] = 64 bytes                 │
│                                                        │
│  Access byte at 0x7FFFD3A0004A:                        │
│    L1 miss → L2 miss → L3 miss → DRAM read             │
│    DRAM returns ALL 64 bytes [40..7F]                  │
│    Cache line stored in L1, L2, L3                     │
│    Byte at 4A served from L1 (4 cycles)                │
│    Next access to any byte in [40..7F]: L1 hit (4 cy)  │
│                                                        │
│  MESI State Machine per cache line per CPU:            │
│  M(odified) → CPU has only copy, dirty                 │
│  E(xclusive) → CPU has only copy, clean                │
│  S(hared) → multiple CPUs have copy, all clean         │
│  I(nvalid) → cache line stale/not present              │
└────────────────────────────────────────────────────────┘
```

---

### 🔄 The Complete Picture — End-to-End Flow

FALSE SHARING FLOW (two threads, same cache line):

```
T=0: Thread 0 (CPU 0): write counter0 → cache line MODIFIED on CPU 0
     Thread 1 (CPU 1): write counter1 → REQUEST ownership
       → CPU 0 receives invalidation request
       → CPU 0 flushes cache line to L3
       → CPU 1 reads cache line from L3
       → CPU 1: MODIFIED on CPU 1
T=1: Thread 0 (CPU 0): write counter0 → REQUEST ownership
       → CPU 1 receives invalidation request
       → CPU 1 flushes cache line to L3
       → CPU 0 reads cache line from L3
       → CPU 0: MODIFIED on CPU 0
[This cycle repeats every increment — serialised by cache line ownership]
```

GOOD LAYOUT (cache-line padded):

```
Thread 0's counter: cache line [0..63]
Thread 1's counter: cache line [64..127]
  → Independent cache lines
  → Both threads: MODIFIED on their own CPU
  → No coherence messages between CPUs
  → Full parallelism
```

---

### 💻 Code Example

Example 1 — Java @Contended to prevent false sharing:

```java
// BAD: counter0 and counter1 on same cache line (adjacent longs)
class SharedCounters {
    volatile long counter0;  // offset 12 (object header)
    volatile long counter1;  // offset 20 — same cache line!
}

// GOOD: @Contended adds 128-byte padding
// Run with: -XX:-RestrictContended
class PaddedCounters {
    @sun.misc.Contended
    volatile long counter0;  // padded to its own cache line

    @sun.misc.Contended
    volatile long counter1;  // padded to its own cache line
}

// Also seen in JDK source: LongAdder, ForkJoinPool, ConcurrentHashMap
// LongAdder.Cell uses @Contended to avoid false sharing between cells
```

Example 2 — C struct layout for cache line efficiency:

```c
// BAD: hot fields spread across multiple cache lines
struct BadRequest {
    char url[200];      // 200 bytes
    int status;         // on 2nd+ cache line
    long timestamp;     // far from status
    int response_code;  // far from timestamp
};
// Accessing status + response_code = 2 cache lines

// GOOD: group hot fields on one cache line
struct GoodRequest {
    // Hot read path — first cache line [0..63]
    int status;         // 4 bytes
    int response_code;  // 4 bytes
    long timestamp;     // 8 bytes
    long latency_ns;    // 8 bytes
    // 24 bytes total — all in one cache line
    char url[200];      // cold data — separate cache lines
};
```

Example 3 — C false sharing fix with alignment:

```c
#include <stddef.h>
// BAD: two counters share a cache line
struct Counters {
    long counter0;   // 8 bytes
    long counter1;   // 8 bytes, offset 8 — same 64-byte cache line
};

// GOOD: each counter on its own cache line
struct PaddedCounter {
    long value;
    char pad[56];  // 56 bytes padding to fill 64-byte cache line
} __attribute__((aligned(64)));

struct PaddedCounter counters[2];
// counters[0].value and counters[1].value: different cache lines
// Each thread writes to its own PaddedCounter — no false sharing
```

Example 4 — Measure false sharing impact:

```bash
# With Linux perf: measure cache coherence traffic
perf stat -e \
  cache-references,\
  cache-misses,\
  LLC-loads,\
  LLC-load-misses \
  ./my_benchmark

# With perf c2c: detect false sharing (Linux 4.10+)
perf c2c record -- ./my_benchmark
perf c2c report
# Shows "True Sharing" and "False Sharing" hotspots with source lines
```

---

### ⚖️ Comparison Table

| Access Pattern                       | Cache Line Efficiency      | Miss Rate      | Performance |
| ------------------------------------ | -------------------------- | -------------- | ----------- |
| Sequential array access              | 100% (all 8 longs used)    | Very low       | Excellent   |
| Random array access                  | ~12% (1 of 8 longs used)   | High           | Poor        |
| Linked list traversal                | ~12% (node + next pointer) | Very high      | Very poor   |
| Packed struct (hot fields first)     | 80–100%                    | Low            | Good        |
| False sharing (adjacent thread data) | 100% loaded, 12% useful    | Coherence miss | Very poor   |

---

### ⚠️ Common Misconceptions

| Misconception                                | Reality                                                                                                                      |
| -------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------- |
| "volatile in Java ensures cache coherence"   | volatile ensures visibility (happens-before) not cache line layout; false sharing still occurs with volatile fields          |
| "Cache lines are 32 bytes"                   | x86-64 cache lines have been 64 bytes since Pentium 4; 32-byte was the Pentium III era                                       |
| "Only concurrent code has cache line issues" | Single-threaded code suffers from poor spatial locality (linked lists, pointer chasing) without any concurrency              |
| "Padding wastes memory"                      | Padding 4 bytes to 64 bytes = 60 bytes wasted but eliminates false sharing; in high-contention paths this is always worth it |
| "@Contended works without JVM flag"          | In JDK 8–15, @Contended is restricted to JDK internal classes by default; needs -XX:-RestrictContended for application use   |

---

### 🚨 Failure Modes & Diagnosis

**1. False Sharing in Thread-Per-Core Counter Array**

**Symptom:** Parallel benchmark with N threads runs slower than N/4 threads; `perf c2c report` shows hot cache line with multiple writers.

**Root Cause:** Thread-local counters allocated adjacent in memory; different CPUs write to the same cache line.

**Diagnostic:**

```bash
# Java: JVM Object layout (with JOL)
# Add dependency: org.openjdk.jol:jol-core
System.out.println(ClassLayout.parseInstance(counters).toPrintable());
# Shows field offsets; check if fields are within 64 bytes of each other

# C: perf c2c
perf c2c record -g ./benchmark
perf c2c report -NN -g --stdio | head -60
```

**Fix:** Java: `@Contended` on each counter field. C: `alignas(64)` + 56-byte pad.

**Prevention:** Design concurrent data structures with explicit cache-line-aligned per-thread state.

---

**2. Struct Layout Causing L3 Pressure**

**Symptom:** Code accessing a specific struct field in a tight loop has unexpectedly high L3 miss rate; other fields in the same struct are "garbage".

**Root Cause:** Cold fields (large buffers, rarely accessed metadata) placed before hot fields in struct; hot field access loads the cold fields' cache lines.

**Diagnostic:**

```bash
perf stat -e L1-dcache-load-misses,LLC-load-misses ./program
# High LLC-load-misses for a hot loop = struct layout issue

# C/C++: check field offsets
offsetof(struct MyStruct, hot_field)  // should be < 64
```

**Fix:** Move hot fields to the beginning of the struct (offset 0–63); group cold fields at the end or in a separate pointer-referenced struct.

---

**3. JVM GC Pointer Tracking Cache Pressure**

**Symptom:** G1 GC pause times increase linearly with heap size even when actual live data is constant; profiling shows time in GC root scanning.

**Root Cause:** GC card table (one byte per 512B heap region) is scanned for dirty cards; if spread across many cache lines, scanning is cache-miss-bound.

**Diagnostic:**

```bash
# GC logging
-Xlog:gc*,gc+phases=debug
# Large "Object Copy" phase with high time = cache miss pressure

# perf for GC threads
perf stat -e cache-misses -t <GC_thread_tid>
```

**Fix:** G1 with region-based GC naturally groups related objects; use `AlwaysPreTouch` to pre-fault pages; tune region size.

**Prevention:** Structure objects to follow field reference chains for GC traversal in same cache lines (memory-efficient object graphs).

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**

- `Virtual Memory` — cache lines are indexed by physical address; TLB translates virtual to physical for cache lookup
- `NUMA` — cache line ownership transfer across NUMA nodes (remote cache hit) is 2–5× more expensive than local
- `Memory Management Models` — understanding how objects are laid out in memory enables cache-line-aware design

**Builds On This (learn these next):**

- `False Sharing` — the direct consequence of multiple threads accessing the same cache line
- `Java volatile` — enforces cache line flush/invalidate on each access; cost is proportional to coherence traffic
- `Lock-Free Data Structures` — CAS operations on cache lines; understanding line ownership is critical

**Alternatives / Comparisons:**

- `Software prefetch` — explicitly hint the CPU to pre-load a cache line before it's needed (`__builtin_prefetch` in GCC)
- `Non-temporal stores` — bypass cache for streaming writes (`_mm_stream_si32` in Intel intrinsics)
- `clflush` — explicitly flush a cache line to memory (used by NVDIMMs and persistent memory)

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ WHAT IT IS   │ 64-byte unit of data transfer between    │
│              │ CPU cache hierarchy and DRAM             │
├──────────────┼───────────────────────────────────────────┤
│ PROBLEM IT   │ DRAM latency (60ns) stalls CPU (1ns/op); │
│ SOLVES       │ cache lines exploit spatial locality      │
├──────────────┼───────────────────────────────────────────┤
│ KEY INSIGHT  │ Coherence is per cache line — fields on   │
│              │ same line create implicit contention      │
├──────────────┼───────────────────────────────────────────┤
│ USE WHEN     │ Designing hot-path data structures;      │
│              │ diagnosing lock-free concurrency bugs     │
├──────────────┼───────────────────────────────────────────┤
│ AVOID WHEN   │ N/A — it's a hardware property you work  │
│              │ with, not avoid                          │
├──────────────┼───────────────────────────────────────────┤
│ TRADE-OFF    │ Spatial locality exploitation vs false    │
│              │ sharing in concurrent writes              │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "64 bytes fetched per access — pack hot  │
│              │  data together, isolate shared writes"   │
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ False Sharing → MESI → Lock-Free DSes    │
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** Intel and AMD use 64-byte cache lines. ARM (Apple M-series, AWS Graviton) uses 64-byte L1/L2 cache lines but 128-byte L3 prefetch granularity. If you pad Java counter objects to 64 bytes (`@Contended` default) and run on Graviton, are you still safe from false sharing at the L3 level? What padding size would you need for both x86 and Graviton L3 false sharing prevention, and what is the memory overhead of applying that padding to a `ConcurrentHashMap` with 1 million entries?

**Q2.** The Java `LongAdder` class avoids contention on a single counter by maintaining per-thread `Cell` objects (each annotated with `@Contended`). `sum()` iterates all Cells and returns the total. This is a classic spatial locality trade-off: faster increments but O(threads) sum cost. Design a data structure that: (1) has O(1) increment with no false sharing, (2) has O(1) read of the current sum (approximate), and (3) uses exactly 2 cache lines of memory regardless of thread count. Specify the exact layout including memory barriers required.
