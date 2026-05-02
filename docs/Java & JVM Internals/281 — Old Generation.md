---
layout: default
title: "Old Generation"
parent: "Java & JVM Internals"
nav_order: 281
permalink: /java/old-generation/
number: "0281"
category: Java & JVM Internals
difficulty: ★★☆
depends_on: Young Generation, Survivor Space, Heap Memory, JVM
used_by: Major GC, Full GC, G1GC, ZGC, GC Tuning
related: Young Generation, Major GC, Full GC, Metaspace
tags:
  - java
  - jvm
  - gc
  - memory
  - intermediate
---

# 281 — Old Generation

⚡ TL;DR — The Old Generation is the JVM heap region for long-lived objects that have survived multiple Minor GCs — collected infrequently but at high cost.

| #281 | Category: Java & JVM Internals | Difficulty: ★★☆ |
|:---|:---|:---|
| **Depends on:** | Young Generation, Survivor Space, Heap Memory, JVM | |
| **Used by:** | Major GC, Full GC, G1GC, ZGC, GC Tuning | |
| **Related:** | Young Generation, Major GC, Full GC, Metaspace | |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
If there were only one memory region (like Young Generation), long-lived objects (application caches, singleton services, HTTP session pools) would be collected during every Minor GC along with short-lived objects. Scanning these long-lived objects on every collection cycle — even though they are almost never garbage — is pure wasted work. The GC would spend 90% of its time confirming that the same cache objects are still alive.

**THE BREAKING POINT:**
Long-lived objects that survive all Minor GC cycles must live somewhere. They cannot be removed, but they dramatically slow down Young Gen collections if they stay there. They need their own region, collected on a separate, infrequent schedule.

**THE INVENTION MOMENT:**
Separating long-lived objects into their own generation — collected far less frequently than Young Generation — matches collection frequency to the actual death rate of objects in each generation. This is why the Old Generation exists.

---

### 📘 Textbook Definition

The Old Generation (also called the Tenured Generation) is the heap region where long-lived Java objects reside — specifically, objects promoted from the Young Generation after surviving `MaxTenuringThreshold` Minor GC cycles (default: 15), or objects too large for Eden/Survivor (large arrays, humongous objects). The Old Generation is collected by Major GC or Full GC — significantly more expensive operations than Minor GC because the Old Gen is typically large (2–3× the Young Gen) and requires different collection algorithms (mark-sweep-compact rather than copying). Old Generation exhaustion causes `java.lang.OutOfMemoryError: Java heap space`.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
The Old Generation is long-term heap storage — rarely swept, but a slow sweep when it happens.

**One analogy:**
> Office buildings have daily trash pickup from the lobby (Young Gen) but deep floor-by-floor cleaning only every quarter (Old Gen). Most material in the deep floors is permanent (long-lived office equipment). The quarterly cleaning takes all day (Major GC pause) but needs to happen rarely. Daily lobby cleaning takes minutes because it only deals with daily disposables.

**One insight:**
The Old Generation's performance story is about Major GC pauses, not allocation. Because Old Gen is rarely collected but large, when it is collected, the pause is proportional to live object set size — which can be gigabytes. Tuning Old Gen means minimising Major GC frequency AND duration.

---

### 🔩 First Principles Explanation

**CORE INVARIANTS:**
1. Long-lived objects need stable, seldom-disturbed storage — Minor GC should not scan them.
2. Old Generation grows as objects are promoted, shrinks only on Major GC.
3. Old Gen collection must tolerate in-place allocation (no copying collector without two full regions available).

**DERIVED DESIGN:**
Invariant 1 motivates a separate region collected on a different schedule. Invariant 2 means Old Gen size must be monitored for growth trend (indicates memory leak). Invariant 3 means Old Gen algorithms typically use mark-sweep-compact rather than simple copying (copying requires 2× space). G1GC partially overcomes this with region-based incremental compaction.

**THE TRADE-OFFS:**
**Gain:** Minor GC is fast because it ignores Old Gen objects (except via card table for cross-gen refs).
**Cost:** Old Gen Major GC is slow; Old Gen filling too quickly causes frequent Major GC; memory leaks manifest as unbounded Old Gen growth.

---

### 🧪 Thought Experiment

**SETUP:**
An application has 2,000 long-lived HTTP session objects (1 MB each — 2 GB total) and processes 10,000 short-lived request objects per second.

Without Old Generation:
All 2,000 sessions and 10,000 request objects live together in one region. Every GC must scan all 2,000 sessions to confirm they're alive, plus handle 10,000 request objects. Even though 95% of request objects are dead, the GC must touch all 2,000 live sessions — massive wasted scanning.

With Old Generation:
Sessions promoted to Old Gen. Young Gen Minor GC runs every 500ms: scans 10,000 request objects (plus card table for refs from Old Gen). 9,990 are dead → collected. 10 promoted to Old Gen. Minor GC touches zero session objects directly. Old Gen Major GC runs once every 10 minutes: collects any expired sessions. The right thing is collected at the right frequency.

**THE INSIGHT:**
Object death rate determines optimal collection frequency. Young objects die at 99%/cycle — collect every cycle. Old objects die at 0.01%/cycle — collect every 1,000 cycles. Matching collection frequency to death rate is the fundamental insight.

---

### 🧠 Mental Model / Analogy

> Old Generation is like a city's permanent archive building. Records (long-lived objects) are moved here after passing through the temporary files area (Young Gen) and proving they're worth keeping. The archive is cleaned only during scheduled maintenance (quarterly audits / Major GC). Cleaning is thorough but disruptive — the building is closed during the audit (Stop-The-World).

- "Archive building" → Old Generation heap region
- "Records moved here from temp files" → promoted objects from Survivor Space
- "Quarterly audit" → Major GC
- "Building closed during audit" → Stop-The-World GC pause
- "Permanent archive staff (long-lived services)" → application-level caches, singletons

Where this analogy breaks down: unlike a physical archive where records can be sorted in advance, the JVM's Old Gen compaction rearranges objects in memory to eliminate fragmentation — a process that requires moving all live objects.

---

### 📶 Gradual Depth — Four Levels

**Level 1 — What it is (anyone can understand):**
After a Java object has survived several rounds of garbage collection in the "new objects" area, the JVM moves it to a bigger storage area called the Old Generation. Things here live longer and are cleaned up less often — think of it as moving from a studio apartment to a permanent house. The cleaning of this area is thorough but takes longer.

**Level 2 — How to use it (junior developer):**
Monitor Old Gen with `jstat -gc <pid>`: `OC` = capacity, `OU` = used. If `OU` grows continuously over hours, you have a memory leak (objects accumulating in Old Gen). Size Old Gen with `-Xmx` (total heap) and `-XX:NewRatio=N` (ratio of Old Gen to Young Gen; default 2, meaning Old Gen is 2× Young Gen).

**Level 3 — How it works (mid-level engineer):**
Old Gen occupies ~66% of the total heap by default (with `NewRatio=2`). Allocation in Old Gen uses a free-list allocator (unlike Eden's pointer-bump), because Old Gen objects vary in size and are not compacted after every collection. Major GC uses mark-sweep-compact: mark all live objects, sweep (identify dead), compact (move live objects to close gaps). Compaction is expensive but prevents fragmentation. G1GC improves this with incremental region-by-region compaction during several mixed GC cycles.

**Level 4 — Why it was designed this way (senior/staff):**
The Old Generation's existence reflects a critical GC design insight: you cannot change the frequency of an event (object death) to match your collection strategy. You must change your collection strategy to match the object death frequency. The two-generation model was first described by D. Ungar and R. Jackson in 1984 for Smalltalk, validated by empirical studies showing >90% of objects die in the first GC cycle. The decision to use mark-sweep-compact (rather than copying) for Old Gen reflects space constraints: a copying collector needs 2× the live space available as free space. For large heaps, this is prohibitive.

---

### ⚙️ How It Works (Mechanism)

**Old Generation in the Overall Heap:**

```
┌─────────────────────────────────────────────┐
│       HEAP LAYOUT WITH OLD GENERATION       │
├─────────────────────────────────────────────┤
│  Young Generation (~33% of heap)            │
│  [Eden][S0][S1]                             │
├─────────────────────────────────────────────┤
│  Old Generation / Tenured (~66% of heap)    │
│  [promoted objects, large allocs]           │
│                                             │
│  Object filling over time:                  │
│  ████████████████____________________       │
│  ← live objects  ← free space             │
│                                             │
│  After Major GC (compacted):               │
│  ████████____________                       │
│  ← compacted ← freed                      │
└─────────────────────────────────────────────┘
```

**Cross-Generation References (Card Table):**
When a Young Gen object is referenced from Old Gen (e.g., a cache in Old Gen holds a fresh request DTO in Eden), Minor GC must find these cross-gen references. The JVM maintains a "Card Table" — a byte array where each byte covers a 512-byte region of Old Gen. A write barrier marks a card "dirty" whenever a reference from Old Gen to Young Gen is written. During Minor GC, only dirty card regions of Old Gen are scanned for GC roots — not the entire Old Gen.

**Promotion Mechanics:**
1. Survivor overflow → promote regardless of age
2. Age ≥ MaxTenuringThreshold → promote
3. Large allocation (> Eden/2 or TLAB limit) → allocate directly in Old Gen
4. Humongous object (> G1 region/2) in G1GC → humongous region (acts as Old Gen)

---

### 🔄 The Complete Picture — End-to-End Flow

**NORMAL FLOW:**
```
Object survives 15 Minor GC cycles in Survivor Space
  → Promoted to Old Generation ← YOU ARE HERE
  → Lives in Old Gen for hours/days
  → Object eventually becomes unreachable
  → Major GC triggered (Old Gen fills)
  → Mark: all live objects from GC Roots traced
  → Sweep: dead objects identified
  → Compact: live objects moved together
  → Old Gen fragmentation reduced
  → Application resumes
```

**FAILURE PATH:**
```
Memory leak via static collection:
  → Large growing Map/Cache in Old Gen reachable from static field
  → Old Gen grows each request cycle
  → Old Gen exhausted → Full GC → OOM if can't free
  → java.lang.OutOfMemoryError: Java heap space
  → Diagnosis: heap dump → Eclipse MAT → Dominator Tree
```

**WHAT CHANGES AT SCALE:**
At very large heaps (32+ GB), Old Gen Major GC becomes the primary concern. Low-pause collectors (ZGC, Shenandoah) perform Old Gen collection concurrently with the application. At terabyte scale, even G1GC's incremental mixed GC is insufficient — ZGC's scalable concurrent collection is required to avoid minutes-long pauses.

---

### 💻 Code Example

Example 1 — Monitor Old Generation:
```bash
# Watch Old Gen fill rate
jstat -gcutil <pid> 2000
# O% (Old Gen utilization) should be stable
# Growing O% over time = promoted objects accumulating

# GC log analysis
java -Xlog:gc*:file=/tmp/gc.log:time -jar myapp.jar
grep "Pause Full\|Pause Old\|ConcGCThreads" /tmp/gc.log
```

Example 2 — Configure Old Generation sizing:
```bash
# Default: Old Gen = 2× Young Gen (NewRatio=2)
# Total heap = Old + Young; Old = heap * (ratio/(ratio+1))

# For memory-intensive app with large live set:
java -Xmx4g \         # Total heap 4GB
     -XX:NewRatio=3 \ # Young = 1GB, Old = 3GB
     -XX:+UseG1GC \
     -jar myapp.jar

# For allocation-heavy app (many short-lived objects):
java -Xmx4g \
     -XX:NewRatio=1 \ # Young = 2GB, Old = 2GB
     -XX:+UseG1GC \
     -jar myapp.jar
```

Example 3 — Detect Old Gen memory leak:
```bash
# 1. Capture heap dump when Old Gen is >80% full
java -XX:+HeapDumpOnOutOfMemoryError \
     -XX:HeapDumpPath=/var/log/ \
     -jar myapp.jar

# 2. Manually capture heap dump
jcmd <pid> GC.heap_dump /tmp/heap.hprof

# 3. Open in Eclipse MAT → "Leak Suspects Report"
# 4. Check Dominator Tree → find object with large
#    retained heap in Old Gen
# 5. "Path to GC Roots" → reveals the static field holding it
```

Example 4 — G1GC mixed GC (Old Gen collection in G1):
```bash
# G1 collects Old Gen in "mixed GC" cycles
# (Young + some Old regions) after concurrent marking
java -XX:+UseG1GC \
     -XX:InitiatingHeapOccupancyPercent=45 \
     # ^^ Start concurrent marking at 45% heap full
     -XX:G1MixedGCLiveThresholdPercent=65 \
     # ^^ Only collect Old regions >65% garbage
     -XX:MaxGCPauseMillis=200 \
     -jar myapp.jar
```

---

### ⚖️ Comparison Table

| Old Gen Collector | Algorithm | Pause | Throughput | Best For |
|---|---|---|---|---|
| Serial GC | Mark-sweep-compact (STW) | Long | Highest | Single-core, embedded |
| Parallel GC | Parallel mark-sweep-compact (STW) | Medium-Long | Highest | Batch jobs |
| CMS | Concurrent mark-sweep (mostly concurrent) | Short (some STW) | Medium | Low-latency legacy apps |
| **G1GC** | Incremental concurrent mark + mixed GC | Predictable | High | General purpose (Java 9+ default) |
| ZGC | Fully concurrent mark-compact | <1ms | Medium | Low-latency, large heaps |
| Shenandoah | Concurrent compaction | <10ms | Medium | Low-latency |

How to choose: G1GC for most production services. ZGC for strict latency SLAs (<1ms) or very large heaps. Avoid CMS (deprecated Java 9, removed Java 14).

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| "Old Generation is the 'permanent' generation" | PermGen WAS the permanent generation (Java 7). Old Gen is 'tenured' — objects live longer but are still collected. Metaspace replaced PermGen in Java 8. |
| "Increasing heap (-Xmx) always prevents OOM" | Only if the leak is bounded. An unbounded memory leak fills any heap size eventually. Larger heap only delays the OOM. |
| "Old Gen is always 2/3 of the heap" | `NewRatio=2` (default for many collectors) means Old Gen = 2× Young Gen = 2/3 total. But this is configurable. G1GC dynamically adjusts the ratio. |
| "Objects never move in Old Gen" | Incorrect. During Major GC compaction (and G1 mixed GC), live Old Gen objects are moved to compact the region. The JVM updates all references to the moved objects. |

---

### 🚨 Failure Modes & Diagnosis

**1. Old Generation Memory Leak**

**Symptom:** Old Gen (`OU`) grows monotonically over hours/days; heap dumps grow sequentially; OOM eventually.

**Root Cause:** Objects accumulating in Old Gen via unintended GC Root connections (static collection, ThreadLocal not cleaned, event listeners not removed).

**Diagnostic:**
```bash
# Two-snapshot approach:
jcmd <pid> GC.heap_dump /tmp/heap1.hprof
# (wait 30 minutes)
jcmd <pid> GC.heap_dump /tmp/heap2.hprof
# In Eclipse MAT: "Compare Baselines" between heap1 and heap2
# Objects that grew between snapshots = the leak
```

**Prevention:** See GC Roots chapter. Bound all caches; always remove ThreadLocals; use weak/soft references for caches.

**2. Frequent Major GC (Premature Promotion)**

**Symptom:** `jstat` shows FGC/FGCT growing rapidly; Old Gen fills faster than expected; application latency spikes every few minutes.

**Root Cause:** Medium-life objects or Survivor overflow cause many objects to be promoted to Old Gen prematurely. Old Gen fills with objects that should have died in Young Gen.

**Diagnostic:**
```bash
jstat -gcutil <pid> 2000
# OGC (Old Gen collection count) growing fast
java -XX:+PrintTenuringDistribution -jar myapp.jar
# Age 1 objects very large → Survivor overflow → premature promo
```

**Prevention:** Increase Young Gen or Survivor size to reduce overflow. Profile allocation hotspots with async-profiler.

**3. Old Gen Fragmentation Causing Allocation Failure**

**Symptom:** `java.lang.OutOfMemoryError: Java heap space` even though total heap isn't exhausted (many small free chunks scattered in Old Gen but no contiguous block large enough for a new promotion).

**Root Cause:** Fragmentation in Old Gen after many mark-sweep cycles without compaction. Only relevant for CMS (which doesn't always compact).

**Diagnostic:**
```bash
# Check for CMS concurrent mode failure in logs
grep "concurrent mode failure" /tmp/gc.log
# This triggers a fallback STW Full GC
```

**Prevention:** Migrate from CMS to G1GC or ZGC (both compact). If stuck on CMS, use `-XX:+UseCMSCompactAtFullCollection`.

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**
- `Young Generation` — objects come from here; Old Gen is the destination after promotion
- `Survivor Space` — the intermediate stage before Old Gen promotion
- `Heap Memory` — Old Generation is the largest portion of the Java heap

**Builds On This (learn these next):**
- `Major GC` — the collection operation that processes the Old Generation
- `Full GC` — a complete heap collection including both Old and Young Generations
- `G1GC` — modern collector that handles Old Gen via incremental concurrent mixed GC

**Alternatives / Comparisons:**
- `Metaspace` — confused with Old Gen; stores class metadata, not object instances
- `Young Generation` — the complementary region for new objects

---

### 📌 Quick Reference Card

┌──────────────────────────────────────────────────────────┐
│ WHAT IT IS   │ Heap region for long-lived objects:       │
│              │ promoted from Young Gen, collected rarely │
├──────────────┼───────────────────────────────────────────┤
│ PROBLEM IT   │ Long-lived objects slow down Young Gen    │
│ SOLVES       │ GC if mixed with short-lived objects      │
├──────────────┼───────────────────────────────────────────┤
│ KEY INSIGHT  │ Old Gen growing = memory leak.            │
│              │ Stable Old Gen = healthy memory usage.    │
│              │ Monitor OU% trend, not just current value │
├──────────────┼───────────────────────────────────────────┤
│ USE WHEN     │ Always — automatic. Tune NewRatio if      │
│              │ Old Gen fills too fast or is undersized   │
├──────────────┼───────────────────────────────────────────┤
│ AVOID WHEN   │ Avoid unnecessary object promotion by     │
│              │ sizing Survivor spaces correctly          │
├──────────────┼───────────────────────────────────────────┤
│ TRADE-OFF    │ Infrequent Major GC vs long pause when    │
│              │ it occurs (proportional to live set size) │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "Old Gen: the JVM's long-term archive —   │
│              │ rarely cleaned, but costly when needed"   │
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ Major GC → Full GC → G1GC → ZGC           │
└──────────────────────────────────────────────────────────┘

---

### 🧠 Think About This Before We Continue

**Q1.** A microservice uses an in-memory cache of 50,000 customer objects (200 bytes each = 10 MB). The cache is evicted using LRU with a max size of 50,000. Over time, `jstat` shows Old Gen (`OU`) stabilises at ~15 MB and never grows further. Is this a memory leak? Explain how to distinguish between a healthy, stable Old Gen usage and a slowly-growing memory leak — what specific monitoring pattern would distinguish them?

**Q2.** G1GC collects Old Generation incrementally during "mixed GC" cycles rather than collecting the entire Old Gen at once. To select which Old Gen regions to collect first, G1 uses "garbage-first" prioritisation: it estimates the GC efficiency of each region (garbage fraction / expected pause time) and collects the highest-efficiency regions first. Why does this greedy approach not always work — specifically, what type of object graph structure in Old Gen would cause the garbage-first algorithm to systematically underestimate the actual freed memory per region?

