---
layout: default
title: "TLAB (Thread Local Allocation Buffer)"
parent: "Java & JVM Internals"
nav_order: 306
permalink: /java/tlab-thread-local-allocation-buffer/
number: "0306"
category: Java & JVM Internals
difficulty: ★★★
depends_on:
  - Heap Memory
  - Young Generation
  - Eden Space
  - Thread (Java)
  - GC Roots
used_by:
  - Minor GC
  - Escape Analysis
  - GC Tuning
related:
  - Eden Space
  - Minor GC
  - Escape Analysis
  - Heap Memory
tags:
  - jvm
  - gc
  - memory
  - concurrency
  - deep-dive
---

# 0306 — TLAB (Thread Local Allocation Buffer)

⚡ TL;DR — TLAB gives each thread its own private chunk of Eden heap so object allocation requires no synchronization — making `new Object()` almost as cheap as a stack pointer bump.

| #0306 | Category: Java & JVM Internals | Difficulty: ★★★ |
|:---|:---|:---|
| **Depends on:** | Heap Memory, Young Generation, Eden Space, Thread (Java), GC Roots | |
| **Used by:** | Minor GC, Escape Analysis, GC Tuning | |
| **Related:** | Eden Space, Minor GC, Escape Analysis, Heap Memory | |

### 🔥 The Problem This Solves

WORLD WITHOUT IT:
Every object allocation in Java reserves memory in the shared Eden heap. If all threads allocate into the same shared memory region, every `new` keyword requires acquiring a lock or using a CAS operation to advance the shared allocation pointer. At 20 threads each allocating 1,000 objects per millisecond, that is 20,000 CAS collisions per millisecond. The heap becomes a serialization point — the anti-pattern of concurrent programming.

THE BREAKING POINT:
A high-throughput trading system allocates 50 million objects per second across 32 threads. Without TLAB, every allocation contends for the heap's bump pointer — causing 50 million lock/CAS operations per second. Thread scheduling collisions and cache thrashing make allocation the bottleneck. 80% of CPU time is spent on allocation overhead, not on financial calculations.

THE INVENTION MOMENT:
This is exactly why **TLAB** was created — to eliminate heap allocation contention by giving each thread a pre-reserved private chunk of Eden. Within a thread's TLAB, object allocation is a single pointer increment — zero synchronization, zero contention.

### 📘 Textbook Definition

A **Thread Local Allocation Buffer (TLAB)** is a thread-private region of the JVM's Eden heap space that each thread uses for its own object allocations. When a thread creates a new object, the JVM first attempts to satisfy the allocation within the thread's current TLAB by advancing its internal pointer — an operation requiring no synchronization. Only when the TLAB is exhausted (or the object is too large for the remaining TLAB space) does the thread interact with the shared Eden space to acquire a new TLAB or perform a slow-path allocation. TLAB size is dynamically tuned by the JVM based on observed allocation rates.

### ⏱️ Understand It in 30 Seconds

**One line:**
Each thread gets its own private memory pad so it can allocate objects without asking anyone else.

**One analogy:**
> Imagine 20 cashiers sharing one till (cash register). Every time any cashier needs change, they must wait for access to the till. TLAB is like giving each cashier their own small cash drawer with a pre-counted float. Each cashier handles their own transactions independently. Only when their drawer runs low do they visit the central till — much less often.

**One insight:**
TLAB makes `new Object()` a two-instruction operation: load a pointer and increment it. There is no lock, no atomic, no fence. This is why Java can allocate millions of objects per second per thread at minimal CPU cost — allocation speed rivals C's `malloc` despite Java's managed runtime. The cost of this design is that each thread "wastes" some TLAB space that it may not fully use before GC reclaims it.

### 🔩 First Principles Explanation

CORE INVARIANTS:
1. Object allocation is the most frequent operation in any Java program — it must be as cheap as possible.
2. Shared mutable state requires synchronization — shared allocation pointers are contended under concurrent allocation.
3. Memory locality matters — allocating from the same region as your thread's recently-used objects improves cache performance.

DERIVED DESIGN:
Eden heap → divided into N TLABs (one per active thread) + a shared remainder.

For each new object allocation:
1. Fast path: check if `(tlab.end - tlab.top) >= allocationSize`. If yes, set `object_address = tlab.top; tlab.top += allocationSize; return object_address`. This is 2 instructions. No atomic. No fence.
2. TLAB retirement: when TLAB fills, "retire" it (mark remaining space as padding with a dummy array so GC can scan the TLAB linearly), then request a new TLAB from Eden.
3. Slow path: large objects (> TLAB maximum size) are allocated directly in Eden using an atomic CAS on the shared Eden pointer.

```
┌─────────────────────────────────────────────────┐
│              Eden Heap with TLABs               │
│                                                 │
│  ┌─────────┬─────────┬─────────┬─────────────┐  │
│  │ TLAB T1 │ TLAB T2 │ TLAB T3 │  Free Eden  │  │
│  │ used/   │ used/   │ used/   │  (shared)   │  │
│  │ waste   │ waste   │ waste   │             │  │
│  └─────────┴─────────┴─────────┴─────────────┘  │
│                                                 │
│  T1 allocates: tlab.top += size (no lock!)      │
│  T2 allocates: tlab.top += size (no lock!)      │
│  TLAB exhausted → request new chunk from        │
│  free Eden using atomic CAS (once per TLAB)     │
└─────────────────────────────────────────────────┘
```

THE TRADE-OFFS:
Gain: Lock-free per-thread allocation; near-zero allocation cost; better cache locality; eliminates allocation bottleneck.
Cost: TLAB waste (unused space at end of TLAB when retired); larger effective Eden needed to accommodate all TLABs; objects from different threads are not co-located in memory (reducing cross-thread object co-locality).

### 🧪 Thought Experiment

SETUP:
Two implementations of a simple message-processing pipeline. Each of 16 threads processes 10,000 messages/second, creating 3 small objects per message (30,000 objects/sec per thread, 480,000 objects/sec total).

WITHOUT TLAB (shared Eden pointer):
Each object allocation: CAS on shared pointer. On 16 threads, CAS retry rate: ~60% (contention). Each contested allocation: ~50ns. Total allocation overhead: 480,000 × 50ns = 24ms/second of allocation overhead. At 480,000 objects/second, 24ms/s = 2.4% CPU time per second lost to allocation. Doesn't sound bad — but at 100 threads it scales to 24%+ CPU.

WITH TLAB:
Thread requests new TLAB (1 CAS) for 512KB (~170,000 small objects). Per-object allocation: 2 instructions ≈ 1ns. Total: 480,000 × 1ns = 0.48ms/second. Speedup: 50x. TLAB exhaustion rate: ~3 TLAB requests per second per thread (very infrequent CAS).

THE INSIGHT:
TLAB converts O(allocations) synchronization operations to O(TLABs) operations — reducing synchronization by 1,000-100,000x for typical workloads. This makes Java's managed allocation competitive with C's bump allocator.

### 🧠 Mental Model / Analogy

> Each thread has a checkbook (TLAB). The thread writes checks freely without going to the bank for each transaction. When the checkbook runs out, the thread visits the bank (Eden) once to get a new checkbook. The bank visit requires locking (CAS), but it happens only once per 1,000 checks rather than once per check.

"Checkbook" → TLAB (private allocation buffer).
"Writing a check" → `tlab.top += size` (pointer increment).
"Bank visit" → CAS on Eden's shared allocation pointer.
"Checkbook page" → TLAB segment.
"Bank runs out of checks" → Eden full → Minor GC triggered.

Where this analogy breaks down: Unused checks at the end of a checkbook are wasted. TLABs have the same waste problem — the unused space at the end of a TLAB when it is retired is filled with a dummy object and counted as "TLAB waste" in GC statistics.

### 📶 Gradual Depth — Four Levels

**Level 1 — What it is (anyone can understand):**
When Java creates new objects, it puts them in a shared memory area. To avoid threads fighting over that area, each thread gets its own small reserved space to put objects in without asking anyone. When that space fills up, the thread claims a new chunk.

**Level 2 — How to use it (junior developer):**
TLAB is automatic and on by default (`-XX:+UseTLAB`, enabled by default). You generally don't tune it directly. Signs of TLAB pressure: high "TLAB waste" in GC logs, frequent TLAB refills. If allocation-heavy code is running on many threads, ensure heap is large enough to accommodate all TLABs simultaneously.

**Level 3 — How it works (mid-level engineer):**
Each thread maintains three pointers: `tlab.start`, `tlab.top` (current allocation point), `tlab.end` (end of TLAB region). For allocation: check `end - top >= size`; if yes, `object = top; top += size`. Atomic CAS on Eden is only needed to claim a new TLAB. TLAB size is dynamically adaptive: the JVM tracks each thread's allocation rate and adjusts TLAB size accordingly (larger TLABs for high-rate threads to reduce refill frequency; smaller for low-rate threads to reduce waste). JVM command: `java -XX:+PrintTLAB` shows per-thread TLAB statistics.

**Level 4 — Why it was designed this way (senior/staff):**
TLAB waste is the fundamental trade-off. When a new TLAB is acquired, the old TLAB's remaining space may be non-trivially large. If the remaining space cannot fit the new allocation but could fit future smaller allocations, the JVM has a choice: waste the space (retire the TLAB) or walk through the remaining space looking for a fit. Walking is O(n) and breaks the O(1) allocation guarantee. The JVM uses a "TLAB allocation fraction" heuristic: if the remaining space is less than `TLABWasteTargetPercent` (default 1%) of TLAB size, retire and get a new TLAB. If remaining space is large, request the new larger allocation directly from Eden (slow path, one CAS) without retiring the TLAB. G1GC and ZGC have per-region allocation variants of TLAB for their concurrent compaction models.

### ⚙️ How It Works (Mechanism)

**Fast-path allocation sequence:**
```
[new SomeObject() invoked]
    → [HotSpot allocation stub]
    → load Thread.tlab_top, Thread.tlab_end
    → check: (tlab_end - tlab_top) >= sizeof(SomeObject)?
    → YES: 
        write object header at tlab_top
        object_ref = tlab_top
        tlab_top += sizeof(SomeObject) 
        zero-fill object fields
        return object_ref
    → NO: call tlab_refill (slow path)
```

**TLAB refill (slow path):**
```
[TLAB exhausted or object too large]
    → fill remaining TLAB space with int[] dummy (TLAB waste)
    → CAS on Eden.top to claim new TLAB of computed size
    → if CAS succeeds: update thread TLAB pointers
    → if Eden full: trigger Minor GC
    → retry allocation in new TLAB
```

**Adaptive TLAB sizing:**
```
Each refill event: record [allocation_rate, refill_time]
At Minor GC: compute new TLAB sizes:
  desired_tlab_size = 
    (time_between_GCs × thread_alloc_rate) /
    (threads × TLABRefillWasteLimit)
  
  Clamped to [min_tlab_size, max_tlab_size]
  
Result: High-allocation threads get large TLABs;
        Low-allocation threads get small TLABs
```

**TLAB in G1GC:**
G1GC uses per-region allocation. TLABs are allocated within G1's regions (regions are typically 1–32MB). When a TLAB extends across a G1 region boundary, G1 ensures the TLAB stays within a single region (allocates smaller TLAB at region end). This maintains G1's invariant that regions are independently collectible.

### 🔄 The Complete Picture — End-to-End Flow

NORMAL FLOW:
```
[Thread creates object]
    → [Check TLAB fast path]  ← YOU ARE HERE
    → [Pointer bump: 2 instructions]
    → [Object at known address in Eden]
    → [Thread continues without lock]

TLAB REFILL:
    → [TLAB full: fill with dummy, retire]
    → [CAS on Eden top to claim new TLAB]
    → [Allocation continues in new TLAB]

EDEN FULL:
    → [CAS on Eden fails: Eden exhausted]
    → [Minor GC triggered]
    → [Survivor or Old Gen promotion]
    → [Eden reset, new TLABs claimed]
```

FAILURE PATH:
```
[Thread allocation rate > TLAB size capacity]
    → [TLAB waste too high (unused end of TLABs)]
    → [Minor GC runs too frequently]
    → [GC logs show "TLAB waste NN%"]
    → [Tune: -XX:TLABSize=NN or -XX:TLABWasteTargetPercent]
```

WHAT CHANGES AT SCALE:
With 1,000 threads (common in virtual thread workloads — Java 21+), 1,000 simultaneous TLABs could consume 1,000 × default_TLAB_size = 1,000 × 512KB = 512MB of Eden — before any actual object allocation. The JVM's adaptive TLAB resizing reduces this by giving smaller TLABs to threads with low allocation rates. Monitor via `-XX:+PrintTLAB` to ensure virtual thread workloads don't exhaust Eden with TLAB overhead.

### 💻 Code Example

Example 1 — Observing TLAB statistics in GC log:
```bash
# Enable TLAB logging:
java -XX:+PrintTLAB \
     -Xlog:gc+tlab=debug \
     MyApp 2>&1 | grep TLAB

# Sample output per thread:
# [TLAB] thread: 0x... desired_size: 32768  refills: 47
#        waste (fast): 1.2%  waste (slow): 0.3%
#        alloc: 1,234,567  refill: 47
```

Example 2 — Setting TLAB size explicitly:
```bash
# Fix TLAB size (overrides adaptive sizing):
java -XX:TLABSize=256k \       # 256KB per thread
     -XX:MinTLABSize=64k \
     MyApp

# WARNING: Fixed TLAB size disables adaptive sizing.
# Consider: only set if adaptive sizing produces poor results.
```

Example 3 — Detecting TLAB waste in GC log:
```bash
java -Xlog:gc*,tlab*=debug MyApp 2>&1 | grep "tlab"

# Look for:
# [tlab] gc_id=7 thread=... alloc=1.1MB waste=52KB
# High waste = TLAB too large for allocation pattern
# Fix: -XX:TLABWasteTargetPercent=5 (allow more waste)
# Or: reduce object allocation size in hot path
```

Example 4 — Monitoring TLAB via JFR:
```bash
java -XX:StartFlightRecording=
  filename=tlab.jfr,settings=default MyApp

# In JMC: Memory → TLAB Allocation tab
# Shows: thread-level allocation rates,
# TLAB refill frequency, waste percentage
```

### ⚖️ Comparison Table

| Allocation Strategy | Synchronization | Speed | Waste | GC Collection |
|---|---|---|---|---|
| **TLAB (fast path)** | None | ~1ns (ptr bump) | ~1% | Next Minor GC |
| Large object (Eden direct) | 1 CAS | ~10ns | None | Next Minor GC |
| Old Gen allocation | 1 CAS | ~15ns | None | Next Major GC |
| Stack allocation (escape analysis) | None | ~0ns | None | Never (stack unwound) |
| Off-heap (Unsafe/ByteBuffer) | Manual | ~10ns | Manual | Never (manual free) |

How to choose: TLAB covers 95%+ of all Java object allocations automatically. Only care about the alternatives when profiling shows allocation as a bottleneck or when using off-heap patterns for GC-free designs.

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| TLAB is per-thread heap memory that persists across GCs | TLAB space is reclaimed at each Minor GC. The objects inside TLABs may survive (promoted), but the TLAB regions themselves are reset and re-carved from a fresh Eden |
| TLAB allocation never requires synchronization | Only the fast path (within TLAB) is synchronization-free. TLAB refill (getting a new TLAB from shared Eden) uses a CAS. Under extreme allocation pressure, multiple TLAB refills per second per thread can still cause measurable contention |
| Objects in a TLAB have better cache locality than objects from different TLABs | Objects within a single thread's TLAB do have good cache locality for that thread. However, objects created by different threads are in different TLAB regions — cross-thread object references may span cache lines and NUMA nodes |
| Increasing TLAB size always improves performance | Larger TLABs reduce refill frequency but increase waste (unused space at retirement). Too large: Eden fills with waste without actually storing live objects → more frequent GC |
| TLAB is unique to HotSpot JVM | TLAB-like mechanisms exist in most high-performance managed runtimes: CLR (.NET), V8 (JavaScript), and Go's runtime all use thread-local allocation caching concepts |
| Setting TLABSize=0 disables TLAB | `-XX:-UseTLAB` disables TLAB entirely. Setting `TLABSize=0` makes the JVM compute an adaptive initial size (not disable it) |

### 🚨 Failure Modes & Diagnosis

**TLAB Waste Causing Premature Minor GC**

Symptom:
GC logs show Minor GC running more frequently than expected. Eden appears to fill quickly but heap usage is not proportional to object creation rate. `PrintTLAB` shows high waste percentages.

Root Cause:
Many threads with low allocation rates receive TLABs that are too large for their actual usage pattern. Most of each TLAB is wasted (filled with dummy int[] at retirement). Eden fills with waste rather than live objects.

Diagnostic Command / Tool:
```bash
java -Xlog:gc+tlab*=debug MyApp 2>&1 | grep "waste"
# Look for waste > 5% on most threads

# Or via JFR TLAB report
```

Fix:
```bash
# Reduce maximum TLAB size:
java -XX:TLABSize=64k MyApp

# Or tighten the waste tolerance (more refills, less waste):
java -XX:TLABWasteTargetPercent=1 MyApp
```

Prevention:
Profile TLAB waste in load testing. Alert if GC log shows consistent waste > 3%.

---

**Contention on Eden When TLAB Refilling Under Load**

Symptom:
Under heavy multi-threaded load (100+ threads), GC logs show very high Minor GC frequency. CPU shows significant time in `ParNew` or parallel GC threads. JFR shows high TLAB refill count per thread.

Root Cause:
With many threads all refilling TLABs simultaneously, CAS contention on the Eden pointer increases. Under extreme load, this manifests as high CAS retry counts and elevated allocation path latency.

Diagnostic Command / Tool:
```bash
# Perf record to see allocation-related stalls:
# Linux: perf stat -e cas:cpu_cycles_waiting java MyApp
# JFR: look for "Allocation Stall" events
jcmd <pid> JFR.start filename=alloc.jfr
# In JMC: Memory → TLAB → Allocation Stalls
```

Fix:
Increase Eden size (reduces refill frequency):
```bash
java -Xmn2g MyApp   # Set Young Gen to 2GB
```
Or reduce thread count if possible.

Prevention:
Load test with production-representative thread pool sizes. Tune Eden size to achieve <1 TLAB refill/second per thread.

---

**Virtual Threads TLAB Exhausting Eden**

Symptom:
Spring Boot 3 application with virtual threads (Java 21+) shows unexpected OOM or high GC frequency when executing 10,000 concurrent requests.

Root Cause:
Virtual threads are mounted on carrier threads. If 100 carrier threads each have a TLAB, and each virtual thread resets the TLAB state on park/unpark, TLAB overhead per carrier thread is multiplied.

Diagnostic Command / Tool:
```bash
# Check carrier thread count and TLAB state:
java -XX:+PrintTLAB \
     --enable-preview \
     -jar myapp.jar 2>&1 | grep "TLAB.refills"
```

Fix:
Tune carrier thread count and Eden size for virtual thread workloads:
```bash
java -Djdk.virtualThreadScheduler.parallelism=16 \
     -Xmn4g MyApp   # larger Eden for TLAB multiplied by carriers
```

Prevention:
Load test virtual thread applications specifically for TLAB pressure with representative concurrent load.

### 🔗 Related Keywords

**Prerequisites (understand these first):**
- `Eden Space` — TLAB is a sub-division of Eden; understanding Eden's role in the generational GC is prerequisite
- `Heap Memory` — TLAB is part of the heap memory organization; the larger context of heap structure
- `Young Generation` — TLABs exist exclusively within the Young Generation (specifically Eden); understanding generational GC explains why

**Builds On This (learn these next):**
- `Minor GC` — TLAB exhaustion ultimately triggers Minor GC; understanding how Minor GC reclaims TLAB space completes the picture
- `Escape Analysis` — when escape analysis proves an object doesn't escape, the JIT can stack-allocate instead of TLAB-allocate; the optimization that makes TLAB unnecessary for short-lived locals
- `GC Tuning` — TLAB waste and refill rates are GC tuning parameters; understanding TLAB is prerequisite to tuning GC allocation behavior

**Alternatives / Comparisons:**
- `Escape Analysis` — stack allocation via escape analysis bypasses TLAB entirely; the ideal outcome when it applies
- `Off-heap allocation (Unsafe)` — bypasses both GC and TLAB; used for GC-free, allocation-critical code in specialized libraries

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ WHAT IT IS   │ Per-thread private Eden chunk enabling    │
│              │ lock-free object allocation               │
├──────────────┼───────────────────────────────────────────┤
│ PROBLEM IT   │ Shared Eden pointer causes CAS contention │
│ SOLVES       │ under concurrent multi-threaded allocation │
├──────────────┼───────────────────────────────────────────┤
│ KEY INSIGHT  │ Fast-path allocation is just 2 asm instrs │
│              │ (load + store), zero synchronization.     │
│              │ Only TLAB refill needs 1 CAS per ~100K    │
│              │ allocations                               │
├──────────────┼───────────────────────────────────────────┤
│ USE WHEN     │ Always-on by default; tune size for       │
│              │ high-thread or high-allocation workloads  │
├──────────────┼───────────────────────────────────────────┤
│ AVOID WHEN   │ Never turn off; stack-allocate instead    │
│              │ with escape analysis for hot-path objects  │
├──────────────┼───────────────────────────────────────────┤
│ TRADE-OFF    │ Lock-free speed vs TLAB waste (unused end) │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "Each cashier gets their own float —      │
│              │  much less time visiting the central till" │
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ Minor GC → Escape Analysis → GC Tuning    │
└──────────────────────────────────────────────────────────┘
```

---
### 🧠 Think About This Before We Continue

**Q1.** A Java service migrates from 100 platform threads to 100,000 virtual threads (Java 21+) to handle concurrent HTTP connections. Assuming 16 carrier threads, trace the impact on TLAB behavior: how many TLABs are active simultaneously, what happens to a TLAB when a virtual thread parks (e.g., during an I/O await), and what is the net impact on Eden consumption compared to the 100-thread model at equivalent throughput?

**Q2.** JVM escape analysis can eliminate TLAB allocation for objects provably non-escaping. A code review reveals a hot method that allocates a `Rectangle(x, y, width, height)` object per iteration of a loop running 50 million times per second, uses it for a single calculation, and discards it. Explain the exact conditions the JIT requires to stack-allocate this Rectangle instead of TLAB-allocating it, and describe a common coding pattern that would cause escape analysis to fail and force the object to the heap despite appearing "local."

