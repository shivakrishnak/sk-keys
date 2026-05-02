---
layout: default
title: "TLAB (Thread Local Allocation Buffer)"
parent: "Java & JVM Internals"
nav_order: 306
permalink: /java/tlab-thread-local-allocation-buffer/
number: "0306"
category: Java & JVM Internals
difficulty: ★★★
depends_on: Heap Memory, Young Generation, Eden Space
used_by: Minor GC, Escape Analysis, GC Tuning
related: Eden Space, Young Generation, Escape Analysis
tags:
  - java
  - jvm
  - memory
  - gc
  - internals
  - deep-dive
---

# 306 — TLAB (Thread Local Allocation Buffer)

⚡ TL;DR — TLAB gives each thread its own private chunk of Eden space so that object allocation never requires synchronization, making Java's memory allocation nearly as fast as a pointer bump.

┌─────────────────────────────────────────────────────────────────────────────────┐
│ #306 │ Category: Java & JVM Internals │ Difficulty: ★★★ │
├──────────────┼──────────────────────────────────────┼──────────────────────────┤
│ Depends on: │ Heap Memory, Young Generation, │ │
│ │ Eden Space │ │
│ Used by: │ Minor GC, Escape Analysis, GC Tuning │ │
│ Related: │ Eden Space, Young Generation, │ │
│ │ Escape Analysis │ │
└─────────────────────────────────────────────────────────────────────────────────┘

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
Java allocates millions of objects per second. Every `new Object()`, every method
call (stack frame), every string concatenation — all allocate from the same heap.
Without TLAB, every allocation requires a CAS (Compare-And-Swap) on the shared
heap pointer to atomically advance it. In a server with 200 concurrent threads,
each `new Object()` involves 200 threads contending for the same atomic variable.
The contention is catastrophic — thread stalls, CPU cache line bouncing, and
allocation throughput that approaches zero as concurrency increases.

**THE BREAKING POINT:**
A microservice with 100 concurrent request-handling threads allocates 10 million
objects/second total. Each allocation requires a lock on the shared Eden pointer.
Lock contention results in threads spending 70% of their time waiting to allocate
— not doing actual work. Adding more CPU cores makes things worse, not better,
because more cores = more contention on the single allocation pointer.

**THE INVENTION MOMENT:**
This is exactly why **TLAB** was created: give each thread its own private slab
of Eden space. Allocation within the TLAB is a trivial pointer bump — no
synchronization, no CAS, no cache misses. Only when a TLAB is exhausted does
the thread need to interact with the shared heap (to get a new TLAB slab).

---

### 📘 Textbook Definition

A Thread Local Allocation Buffer (TLAB) is a thread-private region within the
JVM's Eden (Young Generation) where objects are allocated without synchronization.
Each thread receives a TLAB of configurable size from the Eden space. Object
allocation within the TLAB is a simple top-of-pointer increment — `top += size;`.
When the TLAB fills, the thread requests a new TLAB from Eden using an atomic
operation; if Eden is full, a Minor GC is triggered. TLAB size is dynamically
adjusted by the JVM based on allocation rate and Eden capacity. TLABs eliminate
heap allocation contention in concurrent workloads and are a prerequisite for
high-throughput object allocation.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
TLAB gives each thread its own memory slab so object allocation is just a pointer addition.

**One analogy:**

> Imagine 100 bank tellers sharing one cash drawer — they spend all day waiting
> for each other to finish counting change. TLAB is like giving each teller
> their own cash drawer. They serve customers independently; they only visit
> the vault (Eden space) occasionally to refill.

**One insight:**
TLAB turns object allocation from a shared-state concurrency problem into a
purely local operation. The most common Java operation (`new`) becomes a 1–2
nanosecond operation instead of a 50–100ns synchronized operation under
contention. This is why Java object allocation can be faster than C++'s `malloc`.

---

### 🔩 First Principles Explanation

**CORE INVARIANTS:**

1. Object allocation requires advancing a "top of heap" pointer by the object size.
2. Multiple threads sharing one pointer require synchronization on each advance.
3. Synchronization overhead grows with concurrency.
4. Thread-local state requires zero synchronization.

**DERIVED DESIGN:**
Partition Eden into thread-local chunks. Each thread owns one chunk at a time.
At allocation time:

```
if (top + objectSize <= end) {
    addr = top;
    top += objectSize;  // no synchronization needed
    return addr;        // ~1ns
}
// TLAB full: request new TLAB (rare, ~1000 allocations between refills)
requestNewTLAB();       // ~50ns, amortized negligible
```

Key parameters:

- `TLABSize`: initial size (default: adaptive, typically 512KB–2MB)
- `ResizeTLAB`: whether the JVM adapts size based on allocation patterns (default: true)
- `MinTLABSize`: minimum TLAB (default: 2KB)

The JVM tracks TLAB allocation statistics per thread and adjusts size to
minimize both: TLAB refill frequency (too small) and Eden fragmentation
(too large → too much wasted space at TLAB end when refilled before full).

**THE TRADE-OFFS:**

- Gain: allocation within TLAB is O(1), L1-cache-local, ~1ns.
- Gain: no thread contention for allocation pointer.
- Cost: TLAB end waste — when a thread's TLAB has insufficient space for an
  object, it requests a new TLAB, wasting the unused tail (TLAB tail).
- Cost: Eden utilization is slightly lower than theoretical maximum due to tail waste.
- Cost: Large objects (>TLABSize) bypass TLAB and allocate directly in Eden or
  Old Gen with synchronization.

---

### 🧪 Thought Experiment

**SETUP:**
A web server has 50 concurrent threads. Each handles an HTTP request in 5ms.
During those 5ms, each thread allocates 10,000 objects (for JSON parsing,
request/response building, etc.).

**WITHOUT TLAB:**
All 50 threads compete for the single Eden allocation pointer. 50 × 10,000
= 500,000 CAS operations/5ms = 100M CAS/second on a single cache line.
At 50ns per contended CAS: 100M × 50ns = 5 seconds of pure CAS overhead
for 5ms of useful work. The CPU is 99% stalled on allocation contention.
The server becomes essentially single-threaded due to the shared pointer.

**WITH TLAB (reality):**
Each thread has a 1MB TLAB containing ~5,000 small objects. The 50 threads
allocate independently. 10,000 allocations per thread = ~2 TLAB refills per
request. Each refill costs 1 CAS (~50ns). Total CAS overhead: 50 threads ×
2 refills = 100 CAS operations/5ms = 20,000 CAS/second. At 50ns each: 1ms.
CAS overhead: 0.02% of execution time (compared to 99% without TLAB).

**THE INSIGHT:**
TLAB converts 500,000 contended CAS operations into 2 per thread. The
99.998% reduction in synchronization is what enables Java to scale allocation
across hundreds of threads without degradation.

---

### 🧠 Mental Model / Analogy

> TLAB is like a grocery store checkout strategy. If all 200 shoppers use one
> shared cash register (shared heap pointer), there's a 200-person queue.
> If each shopper gets their own self-checkout lane (TLAB), they all check out
> simultaneously. Occasionally, a shopper needs to reload the lane's receipt
> tape (new TLAB) — a 5-second pause — but most of the time, they're fully
> independent.

- "200 shoppers at one register" → threads contending on shared Eden pointer
- "Self-checkout lane" → TLAB (private allocation region)
- "Reload receipt tape" → request new TLAB from Eden
- "Checkout independently" → allocation within TLAB (no synchronization)
- "One large item needs the cashier" → large object bypasses TLAB

**Where this analogy breaks down:** All checkout lanes (TLABs) eventually
empty into the same store's inventory room (GC when Eden fills). The
parallelism is in the allocation, not in the GC — GC still stops all threads.

---

### 📶 Gradual Depth — Four Levels

**Level 1 — What it is (anyone can understand):**
When Java creates new objects, it doesn't fight with other threads for memory.
Each thread has its own little block of memory (TLAB) — it fills it up privately,
then gets a new block. Simple, fast, no waiting.

**Level 2 — How to use it (junior developer):**
TLAB is automatic and transparent. To observe it: use `-XX:+PrintTLAB` or
look at GC logs for "TLAB" entries. For performance tuning: if allocation
contention appears in profiles, TLAB is the reason Java handles it well.
If objects are large and bypassing TLAB (G1GC log shows `humongous` allocations),
review object size to reduce large-object allocations.

**Level 3 — How it works (mid-level engineer):**
The JVM maintains per-thread `tlab_top` and `tlab_end` pointers. Allocation:
`if (tlab_top + size < tlab_end) { addr = tlab_top; tlab_top += size; return addr; }`
TLAB refill: `tlab_end = eden_top.CAS(eden_top + newTLABSize);` — one CAS for
potentially thousands of allocations. The JVM's heap initializer zeroes TLAB
memory in bulk during refill, not per-object. TLAB size is recomputed after
each Minor GC using exponential moving average of per-thread allocation rates.

**Level 4 — Why it was designed this way (senior/staff):**
The TLAB design was inspired by thread-local storage patterns from concurrent
memory allocator research (particularly jemalloc and TCMalloc). The key insight
from the JVM designers is that "waste tail" (unused TLAB bytes when refilling)
is actually beneficial: it acts as natural padding between thread-local regions,
preventing false sharing between objects allocated by different threads. The
adaptive TLAB sizing is the real engineering achievement — a TLAB too small
means too many expensive Eden CAS operations; too large means excess waste and
less Eden for other threads. The JVM tracks per-thread allocation rates across
GC cycles and converges on the optimal size, often without any manual tuning.

---

### ⚙️ How It Works (Mechanism)

```
┌──────────────────────────────────────────────────────────┐
│         TLAB ALLOCATION MECHANISM                        │
├──────────────────────────────────────────────────────────┤
│  Eden Space:                                             │
│  ┌──────────────────────────────────────────────────┐   │
│  │Thread 1 TLAB│Thread 2 TLAB│Thread 3 TLAB│ Free  │   │
│  └─────────────┴─────────────┴─────────────┴───────┘   │
│       ↓                                                   │
│  WITHIN Thread 1's TLAB:                                 │
│  ┌────────────────────────────────────────────────┐      │
│  │ Obj1 │ Obj2 │ Obj3 │ ... │ top↑ │    free    │ end│   │
│  └────────────────────────────────────────────────┘      │
│                                                          │
│  ALLOCATION (fast path, ~1ns):                          │
│    addr = tlab_top                                       │
│    tlab_top += objectSize                                │
│    zero-fill(addr, objectSize)                           │
│    return addr                                           │
│                                                          │
│  TLAB REFILL (slow path, ~50ns):                        │
│    retire current TLAB (fill with dummy object)         │
│    new_start = eden_top.CAS(eden_top + newSize)         │
│    tlab_top = new_start                                  │
│    tlab_end = new_start + newSize                        │
│                                                          │
│  EDEN FULL PATH:                                         │
│    All TLABs returned to Eden                           │
│    Minor GC triggered                                   │
│    Eden emptied; all threads get fresh TLABs            │
└──────────────────────────────────────────────────────────┘
```

The "dummy object" fill on TLAB retirement ensures the heap remains parseable
by GC — no gaps in the heap that would confuse the garbage collector's scan.

---

### 🔄 The Complete Picture — End-to-End Flow

```
┌──────────────────────────────────────────────────────────┐
│         TLAB IN THE GC LIFECYCLE                         │
├──────────────────────────────────────────────────────────┤
│  Thread-N: new MyObject()                               │
│       ↓ check tlab_top + size ≤ tlab_end               │
│       YES: bump tlab_top, return ← YOU ARE HERE (fast) │
│       ↓                                                  │
│       NO: TLAB full — refill TLAB ← YOU ARE HERE (rare) │
│       ↓ CAS on Eden top                                 │
│       ↓                                                  │
│  Eden fills up →                                         │
│  Minor GC triggered ← all TLABs returned               │
│  Young Gen: Eden + Survivors GC'd                       │
│  Live objects promoted or copied to Survivor           │
│  Eden cleared → Fresh TLABs distributed                 │
│       ↓                                                  │
│  Thread-N: resumes with fresh TLAB                      │
└──────────────────────────────────────────────────────────┘
```

**FAILURE PATH:**
Eden exhaustion under extreme allocation rate → Minor GC fires before TLAB
fill completes → application thread must wait for GC → allocation latency spike.
Observable: GC logs show high Minor GC frequency with short pauses.

**WHAT CHANGES AT SCALE:**
At 1000 threads, TLAB's benefit is most visible. Each thread's 1MB TLAB means
1000 × 1MB = 1GB of Eden reserved as TLABs. Eden sizing must account for TLAB
reservation: insufficient Eden → TLAB sizes shrink → refill frequency increases.
For high-thread-count systems, larger Eden (via `-Xmn`) is often required.

---

### 💻 Code Example

```bash
# Example 1 — Observe TLAB statistics
java -XX:+PrintTLAB -XX:+PrintGCDetails MyApp 2>&1 \
  | grep TLAB | head -20

# Output per GC cycle:
# TLAB: gc thread: 0x... [id: 0]  ...
#   desired_size: 491520B, actual_size: 491520B
#   refills: 847, waste: 0.0%
#   gc_waste: 5.2%, slow_refills: 3
# "refills" = how many TLABs thread requested
# "waste" = % Eden wasted as TLAB tails
```

```bash
# Example 2 — Tune TLAB for high-allocation workloads
# Default TLAB size is adaptive. Override if profiling reveals:
# - High slow_refills: TLAB too small
# - High waste %: TLAB too large

# Force specific TLAB size (use with measurement):
java -XX:TLABSize=2m MyApp
# Disable TLAB resizing (rarely useful):
java -XX:-ResizeTLAB MyApp
# Minimum TLAB size:
java -XX:MinTLABSize=16k MyApp
```

```java
// Example 3 — Identify allocation hotspots causing TLAB pressure
// Use Java Flight Recorder:
// jcmd <pid> JFR.start name=alloc settings=profile \
//   duration=60s filename=/tmp/alloc.jfr
// jcmd <pid> JFR.stop name=alloc

// In JMC: open alloc.jfr → "Allocation in TLAB" event
// Shows: which classes are allocated most, by which methods
// High-allocation classes = candidates for object pooling
// or escape analysis verication (do they escape? if not,
// should be stack-allocated by C2)
```

---

### ⚖️ Comparison Table

| Allocation Path            | Synchronization | Speed  | When Used            | Notes                    |
| -------------------------- | --------------- | ------ | -------------------- | ------------------------ |
| **TLAB fast path**         | None            | ~1ns   | 99%+ of allocations  | Pointer bump within TLAB |
| TLAB refill                | 1 CAS           | ~50ns  | Per TLAB exhaustion  | New TLAB chunk from Eden |
| Large object / Eden direct | CAS             | ~50ns  | Object > TLAB size   | Bypasses TLAB            |
| Old Gen / Humongous        | Lock            | ~500ns | Direct old-gen alloc | G1GC large object        |

**How to choose:** You don't choose — the JVM selects the appropriate path.
Optimize by: keeping most allocations small (TLAB fast path), avoiding large
object allocations on hot paths, and sizing Eden appropriately for your
thread count.

---

### ⚠️ Common Misconceptions

| Misconception                                | Reality                                                                                                  |
| -------------------------------------------- | -------------------------------------------------------------------------------------------------------- |
| New object allocation uses a heap lock       | TLAB fast-path allocation has zero synchronization — it's a local pointer bump, faster than malloc       |
| TLAB is a separate memory region             | TLAB is a partition of Eden space; objects in TLAB are in Eden and collected by Minor GC normally        |
| Large TLABs are always better                | TLAB too large wastes Eden (unused tail on refill) and can cause premature Minor GC from Eden exhaustion |
| TLAB eliminates GC pressure                  | TLAB eliminates allocation contention, not GC pressure; high allocation rate still fills Eden fast       |
| Native Memory Tracking shows TLAB separately | TLAB is part of Eden; NMT shows it under "Java Heap" — not as its own category                           |

---

### 🚨 Failure Modes & Diagnosis

**High TLAB Refill Rate (Allocation Bottleneck)**

Symptom:
`PrintTLAB` shows thousands of refills per GC cycle per thread.
Minor GC fires every 100ms. CPU time in GC exceeds 5%.

Root Cause:
TLAB too small for thread's allocation rate, causing frequent Eden CAS
operations that partially negate TLAB's benefits.

Diagnostic Command / Tool:

```bash
java -XX:+PrintTLAB MyApp 2>&1 | grep refills | sort -k5 -n | tail -10
# Shows threads with highest refill counts
# Or via JFR: look for "TLAB Allocation" event with high count
```

Fix:

```bash
# Increase TLAB size or Eden size:
-XX:TLABSize=4m
# Or increase Eden via Young Gen sizing:
-XX:NewSize=4g -XX:MaxNewSize=4g
```

Prevention:
Profile allocation rate per thread and size TLAB to cover 1000+ allocations
between refills.

---

**TLAB Waste Causing Premature GC**

Symptom:
Eden fills quickly despite modest object allocation rate. Minor GC fires every
few seconds for a low-load application. `PrintTLAB` shows high waste %.

Root Cause:
TLAB too large — threads frequently refill before their TLAB is full.
Unused TLAB tails fill Eden with wasted space (dummy objects).

Diagnostic Command / Tool:

```bash
java -XX:+PrintTLAB -Xms4g -Xmx4g MyApp 2>&1 | grep waste
# High waste % with low refill count = TLAB oversized
```

Fix:

```bash
# Allow JVM to adaptively size (default):
-XX:+ResizeTLAB

# Or manually reduce if adaptive isn't converging:
-XX:TLABSize=512k
```

Prevention:
Enable adaptive TLAB sizing (`-XX:+ResizeTLAB`, which is default) and let
the JVM converge on the right size for your thread and allocation pattern.

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**

- `Heap Memory` — TLAB is a partition of the heap; heap understanding is prerequisite
- `Young Generation` — TLAB exists within Young Generation (Eden space specifically)
- `Eden Space` — TLABs are carved from Eden; Eden fills as TLABs are allocated

**Builds On This (learn these next):**

- `Minor GC` — triggered when Eden (including all TLABs) fills up
- `Escape Analysis` — JIT can eliminate allocations entirely if objects don't escape; complements TLAB
- `GC Tuning` — TLAB size parameters are part of GC tuning

**Alternatives / Comparisons:**

- `Escape Analysis` — peer optimization: TLAB makes allocation fast; escape analysis eliminates it
- `Eden Space` — the parent region from which TLABs are carved

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ WHAT IT IS   │ Per-thread Eden chunk for lock-free alloc  │
├──────────────┼───────────────────────────────────────────┤
│ PROBLEM IT   │ Shared heap pointer causes contention      │
│ SOLVES       │ under concurrent allocation                │
├──────────────┼───────────────────────────────────────────┤
│ KEY INSIGHT  │ One CAS per 1000 allocations vs one CAS   │
│              │ per allocation — a 1000× concurrency gain  │
├──────────────┼───────────────────────────────────────────┤
│ USE WHEN     │ Always (automatic) — all heap allocation   │
│              │ uses TLAB by default                       │
├──────────────┼───────────────────────────────────────────┤
│ AVOID WHEN   │ N/A — only tune size if profiling shows   │
│              │ TLAB waste or high refill rate             │
├──────────────┼───────────────────────────────────────────┤
│ TRADE-OFF    │ Eden fragmentation (tail waste) vs         │
│              │ allocation throughput                      │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "Your own cash drawer, not the bank vault" │
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ Escape Analysis → Minor GC → GC Tuning     │
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** A thread processes a large batch job: it creates 1 billion small objects
(each ~32 bytes) in a tight loop, none of which survive the loop. The JVM's
escape analysis determines all objects are local. Trace the full allocation
lifecycle: what role does TLAB play, what does escape analysis potentially
eliminate, and at what object count does the Young Generation GC trigger?
Include the TLAB fast-path nanosecond math.

**Q2.** Virtual Threads (Project Loom) can create millions of lightweight
threads in a single JVM. If each virtual thread received a standard TLAB
(say, 512KB), the combined TLAB reservation would exceed typical Eden sizes.
What is the adaptive strategy the JVM uses to handle this, and what are the
allocation performance implications of having millions of TLABs simultaneously
active compared to thousands of platform threads?
