---
layout: default
title: "Major GC"
parent: "Java & JVM Internals"
nav_order: 283
permalink: /java/major-gc/
number: "0283"
category: Java & JVM Internals
difficulty: ★★★
depends_on: Old Generation, Minor GC, GC Roots, Stop-The-World
used_by: Full GC, G1GC, ZGC, GC Tuning, GC Pause
related: Minor GC, Full GC, Stop-The-World, G1GC
tags:
  - java
  - jvm
  - gc
  - performance
  - deep-dive
---

# 283 — Major GC

⚡ TL;DR — Major GC collects the Old Generation — significantly more expensive than Minor GC because Old Gen is large, mostly-live, and cannot use a simple copying collector.

| #283 | Category: Java & JVM Internals | Difficulty: ★★★ |
|:---|:---|:---|
| **Depends on:** | Old Generation, Minor GC, GC Roots, Stop-The-World | |
| **Used by:** | Full GC, G1GC, ZGC, GC Tuning, GC Pause | |
| **Related:** | Minor GC, Full GC, Stop-The-World, G1GC | |

### 🔥 The Problem This Solves

WORLD WITHOUT IT:
After months of running a Java application, Old Generation fills with long-lived objects. Some of these objects eventually become unreachable (sessions expire, caches evict, large graphs are released). Without Major GC, Old Gen grows until it reaches `-Xmx`, then the JVM cannot allocate more objects and throws `OutOfMemoryError`. Even applications with zero memory leaks would eventually need Old Gen cleaned.

THE BREAKING POINT:
Old Gen objects need collection, but applying Minor GC's "copy the survivors" strategy to a multi-gigabyte Old Gen would require an equivalently-sized empty region as copy destination — doubling memory requirements to 2× `Xmx`. For large heaps, this is impractical.

THE INVENTION MOMENT:
Major GC uses mark-sweep-compact (or concurrent variants) — an algorithm that identifies dead objects in place and compacts live objects without requiring an equally-sized empty region. This is why Major GC exists as a distinct algorithm from Minor GC.

### 📘 Textbook Definition

Major GC (also called Old Gen GC or Tenured GC) is a garbage collection event targeting the Old Generation. It is triggered when Old Gen space is insufficient to accommodate new promotions from Minor GC. Major GC algorithms differ from Minor GC: they use mark-sweep-compact (or concurrent marking) rather than copying collection, because Old Gen is large and mostly live — copying would require an equally sized free region. A "Major GC" may refer specifically to an Old Gen pass (as in CMS) or may include Young Gen collection as well (as in the HotSpot definition). In modern collectors (G1GC), the equivalent is a sequence of concurrent marking followed by "mixed GC" cycles that collect Old Gen regions incrementally.

### ⏱️ Understand It in 30 Seconds

**One line:**
Major GC is the deep-clean of the Old Generation — infrequent but slow when it happens.

**One analogy:**
> Major GC is like a company's annual audit. Day-to-day paperwork disposal (Minor GC) handles the regular flow. Once a year, a team reviews ALL filing cabinets (Old Gen), identifies and disposes of obsolete records (unreachable objects), and reorganises the remaining files compactly (compaction). The audit disrupts business for hours, but without it, the cabinets would overflow.

**One insight:**
Major GC is the primary target for latency optimisation in JVM applications. Minor GC is fast (1–20ms). Major GC can take hundreds of milliseconds to many seconds depending on live object set size and collection algorithm. All major JVM innovations in the past decade (G1GC, ZGC, Shenandoah) have focused primarily on reducing Major GC pause times by making Old Gen collection concurrent.

### 🔩 First Principles Explanation

CORE INVARIANTS:
1. Major GC must collect the Old Generation without requiring a copy-destination of equal size.
2. Major GC must be able to compact the remaining live objects to prevent fragmentation.
3. Major GC cost is proportional to live object set size (unlike Minor GC which is proportional to surviving count).

DERIVED DESIGN:
Invariant 1 mandates mark-sweep (in-place identification of garbage) rather than copying. Invariant 2 requires compaction — moving live objects to eliminate fragmentation gaps. Invariant 3 means increasing live set (larger application state) directly increases Major GC pause. This drives the need for concurrent collectors: if marking can proceed while the application runs, the stop-the-world pause shrinks to only the compaction phase.

THE TRADE-OFFS:
Gain: Reclaims Old Gen; prevents OOM; compaction eliminates fragmentation.
Cost: Long stop-the-world pause (STW collectors); CPU overhead from concurrent marking (concurrent collectors); application threads occasionally stalled waiting for STW phases.

### 🧪 Thought Experiment

SETUP:
5 GB Old Gen, 4.5 GB live objects, 500 MB garbage. STW Major GC (Parallel GC).

WHAT HAPPENS WITHOUT CONCURRENCY:
1. All application threads freeze.
2. GC marks all 4.5 GB of live objects — must visit every pointer of every live object.
3. GC identifies 500 MB of garbage.
4. GC compacts: moves all 4.5 GB of live objects to be contiguous.
5. Updates all references to moved objects (another full scan).
6. Total pause: ~10 seconds (rough estimate: ~2ms per MB of live data).
7. Application appears frozen for 10 seconds → request timeouts, SLA violations.

WHAT HAPPENS WITH CONCURRENT MARKING (G1GC):
1. GC starts CONCURRENT MARKING while application runs: marks most of 4.5 GB while threads run.
2. Short STW pause to handle objects modified during marking (remark phase): ~100ms.
3. After marking: G1 knows which Old regions are garbage-dense.
4. G1 mixed GC: collects those regions in several short STW cycles of 200ms each.
5. Total visible pause: 4 × 200ms = 800ms spread over 30 seconds = less than 30ms average pause.

THE INSIGHT:
The key insight of modern GC design: move as much work as possible to concurrent phases (no application pause), then minimise the STW phases to just what requires a consistent heap snapshot.

### 🧠 Mental Model / Analogy

> Major GC is like a library conducting an inventory audit. The library stays open during the first phase (concurrent marking — staff check shelves while patrons use the library). Then the library closes briefly (STW remark) to catch any changes made while auditing. Then a few aisles are closed at a time for reorganisation (G1 mixed GC — collect the worst aisles first). Patrons (application threads) experience brief interruptions, not an all-day closure.

"Library open during audit" → concurrent marking (no app pause)
"Library closes briefly" → stop-the-world remark phase
"Aisles closed for reorganisation" → mixed GC collecting Old Gen regions
"All-day closure (STW Major GC)" → traditional Parallel GC approach

Where this analogy breaks down: unlike a physical library, the JVM must ensure that every reference to a moved object is updated — this "forwarding pointer" maintenance has no physical analogy.

### 📶 Gradual Depth — Four Levels

**Level 1 — What it is (anyone can understand):**
After collecting short-lived objects frequently, the JVM also needs to periodically clean up long-lived memory. Major GC is this deeper cleanup — it takes longer because there's much more to examine, but it happens rarely. Think of it as the annual spring cleaning vs daily dish washing.

**Level 2 — How to use it (junior developer):**
Monitor Major GC with `jstat -gc <pid>`: `OGC`/`OGCT` = Old Gen collection count/time. Healthy production services should have minimal Major GC. If `OGC` increases frequently, Old Gen is filling too fast (possible leak, premature promotion, or undersized Old Gen). Use `-Xlog:gc:file=/tmp/gc.log` to see Major GC events and pauses.

**Level 3 — How it works (mid-level engineer):**
Mark-sweep-compact for Parallel GC (STW): (1) Mark — traverse from GC roots, mark all reachable objects; (2) Sweep — identify unmarked objects; (3) Compact — move all live objects to bottom of Old Gen. All phases are stop-the-world. G1GC's equivalent: (1) Initial mark (STW, piggybacks on Minor GC); (2) Concurrent marking (concurrent); (3) Remark (STW, processes outstanding SATB references); (4) Cleanup (STW, selects which regions to include in mixed GC); (5) Mixed GC (STW — multiple cycles, each collecting a set of Old Gen regions).

**Level 4 — Why it was designed this way (senior/staff):**
The evolution of Major GC algorithms reflects the growing importance of tail latency. CMS (1999) introduced concurrent marking for Old Gen, dramatically reducing Major GC pauses. G1GC (default since Java 9) replaced CMS with region-based collection, enabling better pause prediction. ZGC (experimental Java 11, production Java 15) took the final step: almost all of Major GC (even compaction) runs concurrently, achieving <1ms pauses for terabyte heaps. Each generation of algorithm traded throughput for lower and more predictable tail latency. ZGC's "coloured pointers" (using unused bits in 64-bit pointers as metadata) eliminated the need for stop-the-world phases in most of the collection cycle.

### ⚙️ How It Works (Mechanism)

**Parallel GC Major GC (Traditional STW):**

```
┌─────────────────────────────────────────────┐
│    PARALLEL GC MAJOR GC (FULL STW)          │
├─────────────────────────────────────────────┤
│  Phase 1: Mark (STW)                        │
│  - Trace all GC roots → mark live objects   │
│  - Uses multiple GC threads in parallel     │
│  → Duration: O(live set size)               │
│                                             │
│  Phase 2: Sweep (STW)                       │
│  - Walk heap, identify dead objects         │
│  - Build free list (or just measure gaps)   │
│  → Duration: O(total Old Gen size)          │
│                                             │
│  Phase 3: Compact (STW)                     │
│  - Move live objects to eliminate gaps      │
│  - Update all references to moved objects   │
│  → Duration: O(live set size) — expensive   │
│                                             │
│  Total: 100ms–10s+ depending on live set    │
└─────────────────────────────────────────────┘
```

**G1GC Equivalent (Concurrent + Incremental):**

```
┌─────────────────────────────────────────────┐
│    G1GC MAJOR COLLECTION PHASES             │
├─────────────────────────────────────────────┤
│  1. Initial Mark (STW, 5-50ms)              │
│     Piggybacks on concurrent Minor GC pause │
│                                             │
│  2. Root Region Scan (concurrent)           │
│     Scan Survivor regions for Old Gen refs  │
│                                             │
│  3. Concurrent Marking (concurrent)         │
│     Mark all live objects in Old Gen        │
│     Application runs concurrently           │
│     Duration: seconds, but no pause         │
│                                             │
│  4. Remark / SATB processing (STW, 10-50ms) │
│     Handle modifications made during phase 3│
│                                             │
│  5. Cleanup (STW, 1-5ms)                    │
│     Calculate region liveness statistics    │
│     Free 100%-garbage regions               │
│                                             │
│  6. Mixed GC (multiple STW cycles, 50-200ms)│
│     Collect Eden + Survivor + best Old Regs │
│     Repeat until sufficient Old Gen freed   │
└─────────────────────────────────────────────┘
```

### 🔄 The Complete Picture — End-to-End Flow

NORMAL FLOW:
```
Old Gen fills via promotions from Minor GC
  → GC detects heap occupancy > threshold
    (G1: InitiatingHeapOccupancyPercent=45%)
  → Concurrent marking begins ← YOU ARE HERE
  → Application continues running
  → Remark STW phase (brief)
  → Mixed GC phases begin (each 50-200ms)
  → Old Gen garbage regions collected
  → Heap occupancy drops below threshold
  → Cycle complete; normal Minor GC resumes
```

FAILURE PATH:
```
Concurrent marking too slow / Old Gen fills before cleanup:
  → "Concurrent Mode Failure" (CMS)
  → "Evacuation Failure" (G1GC)
  → Falls back to STW Full GC
  → All threads paused for full heap collection
  → seconds-long pause → SLA violation
  → Diagnosis: "to-space exhausted" in GC logs
```

WHAT CHANGES AT SCALE:
At terabyte heaps, even concurrent marking takes tens of seconds. The concurrent marking threads must keep up with the application's object modification rate. If the application creates and modifies references faster than the GC can mark (known as "floating garbage" and "concurrent marking failure"), the GC falls back to STW. ZGC with coloured pointers solves this by intersecting GC state into the reference itself, enabling sub-millisecond phases even at terabyte scale.

### 💻 Code Example

Example 1 — Monitor Major GC:
```bash
# jstat: Major GC count and time
jstat -gc <pid> 1000
# OGC = Old Gen GC count (Major GC)
# OGCT = Total time in Major GC

# GC log: filter Major GC events
java -Xlog:gc:file=/tmp/gc.log:time -jar myapp.jar
grep "Pause Full\|Pause Old\|Concurrent" /tmp/gc.log
```

Example 2 — Configure G1GC Major GC thresholds:
```bash
# G1GC starts concurrent marking at:
# IHOP (InitiatingHeapOccupancyPercent) - default 45%
# Too high → less time to complete before OldGen fills
# Too low → unnecessary major GC cycles

java -XX:+UseG1GC \
     -XX:InitiatingHeapOccupancyPercent=35 \  # Start earlier
     -XX:MaxGCPauseMillis=200 \
     -XX:G1ReservePercent=15 \  # Headroom for promotions
     -Xmx4g \
     -jar myapp.jar
```

Example 3 — Force Major GC for testing (never in production):
```java
// Trigger Major GC for heap analysis (dev/test only)
System.gc(); // requests Full GC (suggestion, may be ignored)

// More reliable: use jcmd
// jcmd <pid> GC.run
// Or: use -XX:+DisableExplicitGC to block System.gc()
// in production to prevent accidental GC triggers
```

Example 4 — Diagnose Major GC causing latency spikes:
```bash
# Find Major GC pauses in production
java -Xlog:gc*:file=/tmp/gc.log:time,level,tags \
     -jar myapp.jar

# Find long Major GC-related pauses
grep -E "Pause|Concurrent" /tmp/gc.log | \
  awk '$NF~/ms/ && $NF+0 > 100 {print}' | tail -30
# Prints lines where GC pause > 100ms

# Correlate with request latency (e.g., from HAProxy logs)
# to confirm GC is the latency spike cause
```

### ⚖️ Comparison Table

| GC Algorithm | Major GC Max Pause | Throughput | Memory Overhead | Best For |
|---|---|---|---|---|
| Serial GC | Very long (seconds) | Highest | Lowest | Embedded, single-core |
| Parallel GC | Long (100ms–5s) | Highest | Low | Batch jobs, throughput |
| CMS | Short STW + long concurrent | Medium | Medium | Legacy low-latency |
| **G1GC** | Predictable (100–500ms) | High | Medium | General purpose |
| ZGC | <1ms (coloured ptrs) | Medium | Higher | Sub-ms latency, large heap |
| Shenandoah | <10ms (concurrent compact) | Medium | Higher | Low-latency, mid-size heap |

How to choose: G1GC for most production services (Java 9+ default). ZGC for strict latency SLAs (<1ms) or heaps >16 GB. Avoid CMS (deprecated/removed).

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| "Major GC = Full GC" | Not exactly. Major GC collects primarily Old Gen. Full GC collects the entire heap (Young + Old + Metaspace). CMS Major GC does not collect Young Gen; Parallel GC Full GC does. G1 mixed GC collects Young + selective Old. |
| "Major GC is always stop-the-world" | G1GC, ZGC, and Shenandoah perform most Major GC work concurrently while the application runs. Only specific STW phases (initial mark, remark) pause all threads. |
| "Frequent Major GC = memory leak" | Frequent Major GC can also result from undersized Old Gen, premature promotion, or legitimate high live-object count. Memory leak is only one cause. |
| "System.gc() in production is harmless" | `System.gc()` usually triggers a Full GC — the most expensive event. Always use `-XX:+DisableExplicitGC` in production to block accidental calls. |

### 🚨 Failure Modes & Diagnosis

**1. "Concurrent Mode Failure" (G1GC: "to-space exhausted")**

Symptom: GC log shows "Concurrent mode failure" (CMS) or "to-space exhausted" (G1); followed by full STW GC; long application pause.

Root Cause: Old Gen fills up before concurrent marking completes. The GC cannot find space for promotions from Minor GC and falls back to a full STW collection.

Diagnostic:
```bash
grep "concurrent mode failure\|to-space exhausted\|Evacuation Failure" \
  /tmp/gc.log
# These messages indicate concurrent GC was too slow
```

Fix:
```bash
# Option 1: Start concurrent marking earlier
java -XX:InitiatingHeapOccupancyPercent=30 -jar myapp.jar
# Option 2: Increase heap
java -Xmx8g -jar myapp.jar  
# Option 3: Reduce promotion rate (tune Young Gen)
```

Prevention: Monitor heap occupancy trend; ensure concurrent marking starts with sufficient headroom for the expected promotion volume.

**2. Multiple Back-to-Back Major GC Cycles**

Symptom: GC log shows 3+ Major GC cycles within 30 seconds; application latency spikes repeatedly; heap never recovers to pre-GC utilisation.

Root Cause: Live set is too large relative to heap size — Major GC reclaims little because most Old Gen is live. Likely memory leak or undersized heap.

Diagnostic:
```bash
# Compare Old Gen usage before and after Major GC
grep "Before GC\|After GC\|Pause Full" /tmp/gc.log | head -20
# If "after" is nearly the same as "before" → not enough garbage
# → memory leak or heap too small
```

Fix:
```bash
# Take heap dump to find what's live in Old Gen
jcmd <pid> GC.heap_dump /tmp/heap.hprof
# Analyse in Eclipse MAT → Dominator Tree
```

Prevention: Right-size heaps; detect and fix memory leaks proactively in staging.

**3. Long Remark Phase in G1**

Symptom: G1GC's final `Remark` STW phase takes >200ms and dominates total Major GC pause time.

Root Cause: During concurrent marking, the application modified many references. The remark phase must reprocess all "dirty" (modified) references. High object modification rate = long remark.

Diagnostic:
```bash
java -Xlog:gc+phases=debug:file=/tmp/gc.log -jar myapp.jar
grep "Remark" /tmp/gc.log | awk '{print $NF}'
# Long Remark durations = high reference modification rate
```

Fix:
```java
// Reduce object churn during concurrent marking:
// - Use immutable objects where possible
// - Reduce large data structure mutations in hot paths
// - Consider ConcGCThreads increase (more GC parallelism)
java -XX:ConcGCThreads=4 -jar myapp.jar  # default = CPU/4
```

### 🔗 Related Keywords

**Prerequisites (understand these first):**
- `Old Generation` — the heap region that Major GC collects
- `Minor GC` — the frequent counterpart to Major GC, for Young Generation
- `GC Roots` — the starting points for Major GC's marking phase
- `Stop-The-World` — the pause mechanism used in Major GC phases

**Builds On This (learn these next):**
- `Full GC` — the "everything" collection that includes Major GC plus Young Gen
- `G1GC` — the modern algorithm replacing traditional Major GC with incremental concurrent mixed GC
- `ZGC` — the next-generation algorithm that makes Major GC effects nearly pause-free
- `GC Pause` — the observable latency impact of Major GC's stop-the-world phases

**Alternatives / Comparisons:**
- `Minor GC` — fast Young Gen collection — contrast with slow Major GC
- `Full GC` — complete heap collection; Major GC is sometimes a component of Full GC

### 📌 Quick Reference Card

┌──────────────────────────────────────────────────────────┐
│ WHAT IT IS   │ Old Generation collection using           │
│              │ mark-sweep-compact (or concurrent variant)│
├──────────────┼───────────────────────────────────────────┤
│ PROBLEM IT   │ Old Gen fills over time; copying          │
│ SOLVES       │ collector impractical for large region    │
├──────────────┼───────────────────────────────────────────┤
│ KEY INSIGHT  │ Modern GCs (G1, ZGC) made Major GC        │
│              │ concurrent; the final STW pause is now    │
│              │ 10–200ms not 10 seconds                   │
├──────────────┼───────────────────────────────────────────┤
│ USE WHEN     │ Old Gen fills with promoted objects.      │
│              │ Tune to delay by sizing Old Gen correctly │
├──────────────┼───────────────────────────────────────────┤
│ AVOID WHEN   │ Frequent Major GC = symptom. Fix leak     │
│              │ or increase heap; don't just increase GC  │
│              │ frequency                                 │
├──────────────┼───────────────────────────────────────────┤
│ TRADE-OFF    │ Concurrent GC (lower pause) vs STW GC     │
│              │ (higher throughput, simpler logic)        │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "Major GC: the annual deep-clean —        │
│              │ rare, disruptive, but necessary; modern   │
│              │ GCs made it run while you work"           │
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ Full GC → G1GC → ZGC → GC Tuning          │
└──────────────────────────────────────────────────────────┘

---
### 🧠 Think About This Before We Continue

**Q1.** G1GC starts concurrent marking when heap occupancy reaches `InitiatingHeapOccupancyPercent` (IHOP, default 45%). A service's live set is 3 GB on a 4 GB heap (75% occupied). After IHOP is exceeded, G1 starts concurrent marking. But the application allocates objects faster than concurrent marking can process them, and Old Gen fills before marking completes — triggering "to-space exhausted" and a fallback STW Full GC. Given a fixed heap of 4 GB, what configuration changes (IHOP, GC threads, heap ratio) could you make to prevent this, and what fundamental trade-off does each change represent?

**Q2.** ZGC achieves <1ms pauses by using "coloured pointers" — storing GC metadata (marked, remapped, finalizable state) in the unused upper bits of 64-bit object references. This means every reference load goes through a "load barrier" that checks these bits. Compare the overhead model of ZGC's load barriers vs G1GC's write barriers: which operations have overhead in each model, and for a read-heavy workload vs a write-heavy workload, which GC has lower overhead and why?

