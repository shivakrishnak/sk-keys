---
id: CSF-045
title: Garbage Collection Algorithms Overview
category: CS Fundamentals - Paradigms
tier: tier-1-foundations
folder: CSF-cs-fundamentals
difficulty: ★★★
depends_on: CSF-044, JVM-001
used_by: CSF-046, CSF-075, JVM-012
related: OSY-012, CSF-047
tags: [garbage-collection, g1gc, zgc, generational-gc, stop-the-world]
status: complete
version: 4
layout: default
parent: "CS Fundamentals - Paradigms"
grand_parent: "Technical Mastery"
nav_order: 45
permalink: /technical-mastery/csf/garbage-collection-algorithms-overview/
---

⚡ TL;DR - GC algorithms trade throughput, pause time,
and memory footprint. Generational hypothesis: most objects
die young. Java GCs: Serial, Parallel (throughput), G1
(low-latency default), ZGC/Shenandoah (sub-ms pauses).
Choose GC based on latency vs throughput requirements.

| #045 | Category: CS Fundamentals - Paradigms | Difficulty: ★★★ |
|:---|:---|:---|
| **Depends on:** | CSF-044 (Memory Management Models), JVM-001 (JVM Architecture) | |
| **Used by:** | CSF-046 (Memory Leak Detection), CSF-075 (GC Pause Analysis), JVM-012 (GC Tuning) | |
| **Related:** | OSY-012 (Virtual Memory), CSF-047 (Concurrency vs Parallelism) | |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**

With manual memory management (C/C++), memory is freed
explicitly. With early GC (Lisp 1959), a simple mark-and-sweep:
stop the application, mark all reachable objects, sweep
unreachable ones into a free list. For small heaps this
is fine. For a 32GB heap at 10,000 req/s, a multi-second
stop-the-world (STW) pause kills throughput and latency.
Every HTTP request times out during GC. Alarm fires.
Customers complain.

**THE BREAKING POINT:**

1990s-2000s Java applications on multi-GB heaps with
Parallel GC saw STW pauses of 5-30 seconds. These were
not defects; they were the expected behavior of the algorithm.
The only mitigation was "tune the GC" (add more Young Gen,
reduce tenuring threshold). The fundamental problem: GC
must stop all threads while scanning the heap because
live application threads might move objects (update pointers)
during the scan, making the scan inconsistent.

**THE INVENTION MOMENT:**

The key insight that enables concurrent GC: use a READ
BARRIER or WRITE BARRIER (a few instructions on every heap
read/write) to track which objects are modified during
concurrent marking. With barriers, GC can scan the heap
WHILE the application runs. Objects modified during the
scan are re-scanned in a brief STW phase. G1 (2006, Java 7
default 2009) reduced pauses to tens of ms using region-based
heap. ZGC (2018, Java 15 production) uses colored pointers
and load barriers to achieve sub-millisecond pauses on
terabyte heaps. The GC evolution is from blocking to
concurrent to near-zero pause.

---

### 📘 Textbook Definition

**Garbage Collector (GC):** The subsystem that automatically
reclaims heap memory occupied by objects that are no longer
reachable from any GC root.

**Generational Hypothesis:** Most objects die young. A
3-step heuristic: allocate new objects in a small "Young
Generation." Collect Young Generation frequently (cheap: most
objects are garbage). Promote survivors to "Old Generation."
Collect Old Generation infrequently.

**Stop-The-World (STW) pause:** A period during GC when
ALL application threads are suspended. The GC has exclusive
access to the heap. Required for phases that cannot tolerate
concurrent object mutation (compaction, some marking phases).

**Concurrent GC:** GC phases that run concurrently with
application threads. Requires write/read barriers to track
object mutations during the concurrent phase.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
GC algorithms trade: throughput (parallel, stop-the-world)
vs latency (concurrent, low-pause). Generational GC exploits
"most objects die young" to make the common case fast.

**One analogy:**

> Old GC: a library that closes to all patrons every night
> to rearrange all books. Simple; disruptive.
>
> G1 GC: a library organized into rooms (regions). The librarian
> rearranges one room at a time, while patrons use the other
> rooms. Occasional brief closures for the busiest rooms.
>
> ZGC: a librarian who rearranges books while patrons are
> still using them, using colored sticky notes to track which
> books have been moved. Almost never needs to close.

**One insight:**

G1 GC is the default since Java 9 because it balances
throughput and latency for most enterprise workloads.
G1 targets a configurable pause time (`-XX:MaxGCPauseMillis=200`).
It chooses which regions to collect based on which regions
have the most garbage (the "garbage-first" heuristic).
You tell G1 your latency requirement; G1 decides how to
meet it. This is a fundamental shift from "tune the GC to
not pause" to "tell the GC your budget and let it optimize."

---

### 🔩 First Principles Explanation

**GC ALGORITHM FAMILIES:**

```
┌──────────────────────────────────────────────────────┐
│ MARK AND SWEEP (classic):                            │
│   Phase 1 - Mark: traverse from roots, mark reachable│
│   Phase 2 - Sweep: scan heap, reclaim unmarked       │
│   Result: free list (fragmented)                     │
│   Stop-the-world for both phases                     │
│                                                      │
│ MARK-SWEEP-COMPACT:                                  │
│   Phase 1 - Mark                                     │
│   Phase 2 - Sweep                                    │
│   Phase 3 - Compact: slide live objects together     │
│   Result: contiguous free space (fast allocation)    │
│   Stop-the-world; longer due to compaction           │
│                                                      │
│ COPYING (Scavenge for Young Gen):                    │
│   Two semi-spaces: "From" and "To"                   │
│   Copy live objects from "From" to "To"              │
│   Remaining "From" is entirely free (no sweep needed)│
│   Result: no fragmentation; allocation = pointer bump│
│   Trade-off: 50% of space is always reserved         │
│                                                      │
│ GENERATIONAL (combining above):                      │
│   Young Gen: copy collector (scavenge)               │
│   Old Gen: mark-sweep-compact                        │
│   Young GC (Minor): milliseconds to low seconds      │
│   Old GC (Major): tens of seconds (historically)     │
└──────────────────────────────────────────────────────┘
```

**G1 REGION-BASED HEAP:**

```
┌──────────────────────────────────────────────────────┐
│ G1 Heap: divided into equal-sized regions (1MB-32MB) │
│                                                      │
│ [E][E][S][O][O][H][E][O][S][O][ ][ ][H][E][O][O]...│
│  E=Eden  S=Survivor  O=Old  H=Humongous  [ ]=free   │
│                                                      │
│ Young Collection (frequent):                         │
│   - Collect E+S regions                              │
│   - Stop-the-world (but small set of regions)        │
│   - Short pause: <100ms typical                      │
│                                                      │
│ Old/Mixed Collection (when heap fills):              │
│   - Concurrent marking (runs WITH application)       │
│   - Brief STW phases (initial mark, remark)          │
│   - Select regions with most garbage (Garbage-First) │
│   - Evacuate to new regions (concurrent compaction)  │
└──────────────────────────────────────────────────────┘
```

---

### 🧪 Thought Experiment

**WHY GENERATIONAL GC WORKS:**

In a typical Java web application handling HTTP requests,
most objects are created during request processing:
request objects, response builders, temporary strings,
`LocalDateTime` objects, etc. These objects are created,
used during the request (typically 10-100ms), and never
referenced again after the response is sent.

If these objects are all allocated in the Young Generation
and collected every few seconds, the vast majority of the
Young Gen is garbage at collection time. The copy collector
only copies the SURVIVORS (the few objects that outlived
the Young GC). For a Young Gen that is 90% garbage, the
collector only copies 10% of the objects - very fast.

The Old Generation slowly accumulates only the objects
that survive many Young GCs: service beans, configuration,
in-memory caches. These are truly long-lived and do not
need frequent collection. The generational hypothesis
makes the common case (short-lived objects) fast
(millisecond Young GC) and the rare case (long-lived objects)
tolerable (less frequent Old GC).

---

### 🎯 Mental Model / Analogy

**GENERATIONAL GC AS OFFICE MAIL SORTING:**

Young Generation: the incoming mail tray. Every morning,
most of it is sorted and either acted on (survives) or
recycled (garbage). The sorting is fast because the tray
is small.

Old Generation: the filing cabinet. Only the documents
that survived multiple days in the inbox are filed. Filing
cleanup (major GC) is infrequent because most things never
make it here.

**MEMORY HOOK:**

"Generational: most objects die young (Young GC = fast).
G1: regions, garbage-first, concurrent marking.
ZGC: colored pointers, load barriers, sub-ms pauses.
Stop-the-world: all threads paused (compaction, STW mark).
Concurrent: GC runs with app (marking, some compaction).
Trade-off: throughput (Parallel GC) vs latency (ZGC)."

---

### 📊 Gradual Depth - Five Levels

**Level 1 - Child:**
GC is a cleaning robot. It cleans the room (heap) while you
play (application runs). Old-style: everyone stops playing
while it cleans. New-style: it cleans around you without
making you stop. Sometimes it needs a brief moment
("everybody freeze") but then resumes quickly.

**Level 2 - Student:**
Java heap: Young Gen (Eden + Survivor spaces) + Old Gen.
Minor GC collects Young Gen (fast, frequent). Major GC
collects Old Gen (slow, infrequent). Generational: most
objects collected quickly before reaching Old Gen.

**Level 3 - Professional:**
G1 GC phases:
1. Young GC (STW): collect Eden and Survivor regions.
2. Concurrent Mark Cycle: when Old Gen occupancy hits
   `InitiatingHeapOccupancyPercent` (default 45%):
   - Initial Mark (STW, piggybacks on Young GC)
   - Concurrent Root Region Scan
   - Concurrent Mark
   - Remark (STW)
   - Cleanup (STW for accounting, concurrent for free region clearing)
3. Mixed GC: collects Young regions + selected Old regions
   (those with most garbage).

**Level 4 - Senior Engineer:**
GC tuning for low-latency:
`-XX:+UseG1GC -XX:MaxGCPauseMillis=50 -XX:InitiatingHeapOccupancyPercent=35`
Reduce `InitiatingHeapOccupancyPercent` to trigger Old GC
earlier (before heap fills). Increase Young Gen size with
`-XX:G1NewSizePercent=30`. For extreme latency:
`-XX:+UseZGC` with `-XX:SoftMaxHeapSize` to leave GC headroom.
GC log analysis: `jstat -gcutil <pid> 1s` to observe GC frequency
and pause time. Splunk/Datadog: graph `jvm.gc.pause` metric.

**Level 5 - Expert:**
ZGC's colored pointers: the JVM uses spare bits in 64-bit
pointers to encode GC state (marked0, marked1, remapped,
finalizable). When the application loads a reference, the
load barrier checks the pointer color. If the pointer is
not the current GC phase color, the barrier remaps the
pointer (applies the current relocation) before returning.
This allows ZGC to relocate objects CONCURRENTLY: the old
pointer still works (barrier remaps it), and new objects
at the new location get the correct pointer. The application
never sees an inconsistent pointer. The barrier cost: ~6
additional instructions per heap reference load. Acceptable
for most workloads; avoided in Rust (no GC barrier at all).

---

### ⚙️ How It Works (Formal Basis)

**GC PAUSE PHASES IN G1:**

```
┌──────────────────────────────────────────────────────┐
│ G1 YOUNG GC (STW):                                   │
│   All threads pause                                  │
│   Copy live objects from Eden/Survivor to Survivor   │
│   or Old (if old enough)                             │
│   Clear Eden regions (now free)                      │
│   Typical: 10-100ms                                  │
│                                                      │
│ G1 CONCURRENT MARKING:                               │
│   Initial Mark (STW, brief): snapshot root set       │
│   Concurrent Mark: traverse heap concurrently        │
│   Remark (STW, brief): process SATB buffers          │
│   (write barriers record mutations during concurrent) │
│   Cleanup (STW for region accounting): identify      │
│   fully-garbage regions (instantly reclaimed)        │
│                                                      │
│ G1 MIXED GC (STW):                                   │
│   Like Young GC but also includes selected Old regs  │
│   Evacuate live objects to other regions             │
│   Old regions with most garbage selected first       │
└──────────────────────────────────────────────────────┘
```

---

### 💻 Code Example

**Example 1 - GC Configuration Examples**

```bash
# Serial GC (single-threaded; small heaps, embedded)
java -XX:+UseSerialGC -Xmx512m App

# Parallel GC (max throughput; batch jobs)
java -XX:+UseParallelGC -Xmx4g -XX:GCTimeRatio=9 App

# G1 GC (default Java 9+; low-latency enterprise)
java -XX:+UseG1GC \
     -Xms4g -Xmx4g \
     -XX:MaxGCPauseMillis=200 \
     -XX:InitiatingHeapOccupancyPercent=40 \
     -Xlog:gc*:file=gc.log:time,uptime:filecount=5,filesize=20m \
     App

# ZGC (sub-ms pauses; Java 15+ production)
java -XX:+UseZGC \
     -Xms8g -Xmx8g \
     -XX:SoftMaxHeapSize=6g \
     -Xlog:gc*:file=gc.log:time,uptime:filecount=5,filesize=20m \
     App
```

**Example 2 - GC Monitoring Commands**

```bash
# Real-time GC stats (every 1 second)
jstat -gcutil <pid> 1000

# Output columns:
# S0  S1  E   O   M   CCS YGC YGCT FGC FGCT CGC CGCT  GCT
# 0   8   22  55  96  90  14  0.45   2  1.23   4  0.1  1.78
# S0/S1: Survivor usage %
# E: Eden usage %
# O: Old Gen usage %
# YGC/YGCT: Young GC count/time
# FGC/FGCT: Full GC count/time

# Identify GC pauses in GC log:
grep -E "Pause|pause" gc.log | awk '{print $1, $NF}' | sort -k2 -rn | head -20
```

---

### ⚖️ Comparison Table

| GC Algorithm | Java Version | Pause Type | Best For |
|---|---|---|---|
| Serial GC | All | Long STW | Embedded, small heap |
| Parallel GC | All | Medium STW | Batch, throughput |
| CMS (deprecated) | Java 9 deprecated | Short STW + concurrent | Legacy low-latency |
| G1 GC | Java 7+ (default 9+) | Short STW + concurrent | General purpose |
| ZGC | Java 11+ (prod 15+) | Sub-ms STW | Low-latency, large heap |
| Shenandoah | Java 12+ (Red Hat) | Sub-ms STW | Low-latency, large heap |

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| "G1 GC eliminates stop-the-world pauses" | G1 reduces STW pauses to tens of ms but does NOT eliminate them. Initial Mark, Remark, and Cleanup phases are STW. Young GC in G1 is fully STW. G1's "low latency" means pauses are shorter and more predictable, not zero. ZGC achieves sub-millisecond (near-zero) STW. |
| "Increasing heap size always reduces GC pauses" | Larger heap means fewer GC cycles (less pressure). But when GC does run on a large heap, it must scan MORE objects, potentially INCREASING pause time for STW collectors. For G1, the region-based design partially mitigates this. For ZGC, heap size does not significantly affect pause time (concurrent work). Increasing heap beyond what the application needs wastes memory and increases GC overhead. |
| "Full GC (System.gc()) is always bad" | `System.gc()` is a HINT; the JVM may ignore it. Some legitimate use cases: before a heap dump (to get a clean picture of live objects), before a memory-sensitive operation, or in test code to reclaim memory between tests. In production: never call `System.gc()` as a routine optimization - it can trigger Full GC and pause the application. |
| "GC root = garbage" | Exactly the opposite. GC ROOTS are the starting points for reachability analysis. Objects reachable FROM roots are LIVE. Objects not reachable from any root are garbage. Common roots: local variables on active thread stacks, static fields, JNI references. |

---

### 🚨 Failure Modes & Diagnosis

**Failure Mode 1: Concurrent Mode Failure (G1)**

**Symptom:** GC log shows `[GC concurrent-mark-abort]`
or Full GC triggered unexpectedly. Pause time exceeds
target by orders of magnitude (seconds).

**Root Cause:** Old Gen fills up faster than concurrent
marking can complete. GC falls back to a Full STW GC
(Serial or Parallel full heap collection).

**Diagnosis:**
```bash
# Check Old Gen fill rate in jstat output:
jstat -gcutil <pid> 1000
# If O column approaches 100% rapidly -> CMF risk

# In GC log:
grep -i "failure\|abort\|Full GC" gc.log
```

**Fix:**
- Reduce `InitiatingHeapOccupancyPercent` (start concurrent
  marking earlier, default 45% -> try 30-35%).
- Increase heap size to give GC more headroom.
- Profile allocation rate: reduce allocation of large
  long-lived objects that bypass Young Gen.
- Switch to ZGC (immune to CMF - concurrent by design).

---

**Security Note:**

GC behavior can be exploited in timing attacks and
denial-of-service. An attacker who can trigger high
allocation rates (e.g., by sending large payloads that
cause many objects to be created) can force frequent GC
and cause application latency spikes. This is a resource
exhaustion attack (OWASP A05). Defenses: rate limiting
on API endpoints, request size limits, payload validation
before object creation, and GC monitoring alerts on
pause time thresholds. For extremely sensitive latency
requirements (trading systems), some architects move to
GC-free designs (pre-allocated object pools, off-heap
storage) to eliminate the GC as an attack surface.

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**
- `Memory Management Models` (CSF-044) - GC is one model;
  understanding all models gives context for GC's tradeoffs
- `JVM Architecture` (JVM-001) - heap regions, Young/Old Gen,
  Metaspace are JVM-specific concepts

**Builds On This (learn these next):**
- `Memory Leak Detection` (CSF-046) - diagnosing when GC
  cannot reclaim memory (logical leaks, object retention)
- `GC Pause Analysis and Production Impact` (CSF-075) -
  deeper analysis of GC pause behavior in production

---

### 📌 Quick Reference Card

```
┌────────────────────────────────────────────────────────┐
│ GENERATIONAL │ Young (fast) -> Old (slow)              │
│ HYPOTHESIS   │ Most objects die young - exploit this   │
├──────────────┼─────────────────────────────────────────┤
│ G1 GC        │ Default Java 9+. Region-based.          │
│              │ Target: -XX:MaxGCPauseMillis=200         │
│              │ STW: Young GC + brief concurrent phases │
│              │ Concurrent marking with write barriers  │
├──────────────┼─────────────────────────────────────────┤
│ ZGC          │ Java 15+ production. Sub-ms pauses.     │
│              │ Colored pointers + load barriers        │
│              │ Concurrent relocation of objects        │
│              │ Use for latency-sensitive services      │
├──────────────┼─────────────────────────────────────────┤
│ PARALLEL GC  │ Max throughput. Larger STW pauses.      │
│              │ Best: batch processing, scientific      │
├──────────────┼─────────────────────────────────────────┤
│ MONITOR      │ jstat -gcutil <pid> 1000               │
│              │ -Xlog:gc*:file=gc.log (GC log)         │
│              │ Eclipse MAT (heap dump analysis)        │
├──────────────┼─────────────────────────────────────────┤
│ CMF SYMPTOM  │ Full GC in log. Old Gen hits 100%.     │
│              │ Fix: lower InitiatingHeapOccupancy %    │
├──────────────┼─────────────────────────────────────────┤
│ NEXT EXPLORE │ CSF-046 (Memory Leaks), CSF-075 (GC)   │
└────────────────────────────────────────────────────────┘
```

**If you remember only 3 things:**

1. Generational hypothesis: most objects die young. Young Gen
   (Eden + Survivors) is collected frequently with short
   STW pauses (copy collector, only copies survivors).
   Old Gen is collected infrequently. Most GC work is cheap
   because most objects are garbage by the time GC runs.
2. G1 GC (default Java 9+) uses regions and concurrent marking
   to achieve short, predictable STW pauses (target configurable
   with `-XX:MaxGCPauseMillis`). Concurrent Mode Failure (CMF)
   occurs when Old Gen fills faster than concurrent marking
   can complete - signals GC tuning needed.
3. ZGC achieves sub-millisecond pauses using colored pointers
   and load barriers for concurrent object relocation. Choose:
   G1 for general workloads; ZGC for latency-sensitive services;
   Parallel GC for batch/throughput workloads.

**Interview one-liner:**
"GC algorithms trade throughput vs latency. The generational
hypothesis (most objects die young) enables fast Young Gen
collection. G1 (default Java 9+) uses region-based collection
and concurrent marking for low-pause general workloads.
ZGC achieves sub-millisecond pauses via colored pointers
and concurrent relocation. Choose GC based on latency SLA:
G1 for 50-200ms targets, ZGC for sub-10ms."

---

### 💎 Transferable Wisdom

**Reusable Engineering Principle:**
GC algorithms embody the principle of "exploit observed
patterns to optimize the common case." The generational
hypothesis is an empirical observation about program behavior;
generational GC exploits it to make the common case (short-lived
objects) extremely cheap. This principle appears in caching
(Pareto principle: 20% of data serves 80% of requests;
cache the hot 20%), network protocol design (Huffman encoding:
encode common characters with fewer bits), database index
design (index the most-queried columns, not all columns),
and OS scheduling (favor interactive processes with
shorter time quanta for responsiveness). In every case:
observe the distribution of actual behavior, then optimize
the common case even at the cost of the rare case.

**Where else this pattern appears:**

- **JVM JIT compilation (tiered compilation)** - Tiered
  compilation is the JIT equivalent of generational GC.
  All methods start interpreted (cheap, no compilation).
  Frequently called methods (hot methods) are compiled
  by C1 (fast, less optimized). The hottest methods are
  compiled by C2 (slow, highly optimized). The common case
  (most methods, called rarely) gets cheap interpretation.
  The hot path gets maximum optimization. This exploits
  the observation that most code is cold; a small fraction
  accounts for most execution time.
- **CPU cache hierarchy** - L1 (tiny, fast), L2 (medium,
  slower), L3 (large, slow), RAM. CPU designers exploited
  temporal and spatial locality: recently accessed data
  is likely to be accessed again (temporal); nearby data
  is likely to be accessed next (spatial). The cache hierarchy
  is a hardware generational system: "recently touched"
  objects stay in L1 (Young Gen equivalent); others spill
  to L2/L3 (Old Gen equivalent).
- **Kafka log compaction** - Kafka's log compaction keeps
  only the latest value for each key, discarding older
  values. This is a GC for event logs: "dead" records (those
  superseded by newer records with the same key) are collected.
  The compaction algorithm runs in the background concurrently
  with reads and writes - a concurrent GC for the event log.

---

### 💡 The Surprising Truth

The JVM's HotSpot GC is aware of object PROMOTION - when
an object survives a certain number of Young GC cycles
(configurable by `-XX:MaxTenuringThreshold`, default 15),
it is promoted to Old Generation. But there is a subtlety:
if the Survivor space is too full to hold all survivors
of a Young GC, some objects are promoted EARLY to Old Gen
regardless of their age. This is called "premature promotion."
If your application promotes objects prematurely at high
rate, the Old Gen fills quickly, triggering frequent Old
GC. The fix: increase Survivor space (`-XX:SurvivorRatio`).
But the deeper insight: the GC's performance is sensitive
to object LIFETIME PATTERNS. An application that creates
many "medium-lived" objects (survive 2-5 Young GCs but
then die) can confuse the generational collector: too
long-lived for Young GC to collect efficiently, too short-lived
to justify the Old Gen overhead. These "medium-lived" objects
are the GC's worst case. The fix is often application-level:
change the object lifetime pattern (pool and reuse them,
or restructure to make them short-lived).

---

### ✅ Mastery Checklist

**You've mastered this when you can:**

1. **[MONITOR]** Configure GC logging for a Spring Boot
   application (`-Xlog:gc*:file=gc.log`). After running
   a load test, analyze the log to identify: average Young
   GC pause, max Young GC pause, Old GC frequency, any
   Concurrent Mode Failures. State whether the GC configuration
   meets a 200ms P99 latency SLA.

2. **[TUNE]** A service running G1 GC shows frequent Full GCs
   in production (every 10 minutes). The GC log shows
   "concurrent-mark-abort." Diagnose the cause and apply
   3 tuning changes to prevent CMF.

3. **[CHOOSE]** Given: a financial transaction processing
   service with 10,000 TPS and P99 latency requirement of
   20ms. Current GC: G1 with 50ms average Young GC pause.
   Recommend and justify a GC change. Include the JVM flags.

4. **[EXPLAIN]** Draw a diagram of G1 GC's region layout.
   Show the lifecycle of a short-lived object (created in
   Eden, collected in Young GC), a medium-lived object
   (promotes to Survivor then to Old Gen), and a large object
   (Humongous region).

5. **[ANALYZE]** Explain ZGC's colored pointers and load
   barrier mechanism: how does ZGC relocate objects concurrently
   without the application seeing stale pointers? Why does
   this make STW pauses sub-millisecond?

---

### 🧠 Think About This Before We Continue

**Q1.** A Java application configured with G1 GC
(`-XX:MaxGCPauseMillis=100`) shows pause times of 300ms
in production. The GC log shows mostly Young GC pauses.
The heap is set to `-Xms4g -Xmx4g` with 10,000 req/s load.
What could explain why G1 is not meeting its pause target?

*Hint: G1's pause target is a GOAL, not a guarantee.
G1 will try to keep pauses under the target but cannot
always succeed. Reasons G1 exceeds pause targets:
(1) Young Gen is too large: G1 cannot collect a large Young
Gen within the time budget. Fix: set `-XX:G1NewSizePercent`
(min young gen) and `-XX:G1MaxNewSizePercent` (max young gen)
to constrain Young Gen size.
(2) High allocation rate fills Eden faster than GC can free it.
(3) Long-running finalizers or JNI code during GC pause.
(4) Object promotion failure: Survivor spaces full -> forced
evacuation to Old Gen -> longer pause.
(5) System-level interference: JVM competing with other
processes for CPU during GC.*

**Q2.** What is the difference between a "minor GC" and a
"Full GC" in G1? Can a G1 deployment have ZERO Full GCs?
Under what conditions does Full GC occur in G1?

*Hint:
Minor GC (Young GC in G1): collects only Young Gen regions (Eden + Survivor).
STW but typically short (10-100ms for properly tuned G1).
Full GC in G1: collects the ENTIRE heap in a single-threaded
STW operation. This is the fallback when:
(1) Concurrent Mode Failure: Old Gen fills while concurrent
marking is running.
(2) Evacuation Failure: no free regions to evacuate live
objects to during Mixed GC.
(3) Humongous object allocation failure: no contiguous regions.
(4) Explicit `System.gc()` call (unless `-XX:+DisableExplicitGC`).
A well-tuned G1 deployment CAN have zero Full GCs. Target:
tune `InitiatingHeapOccupancyPercent` and heap sizing to
ensure concurrent marking completes before Old Gen fills.
If Full GC occurs in logs, it is always a tuning signal.*

---

### 🎯 Interview Deep-Dive

**Q1: "Explain the Generational Hypothesis and why it matters for GC design."**

*Why they ask:* Fundamental GC theory. Separates candidates
who understand GC deeply from those who only know the JVM flags.

*Strong answer includes:*
- Generational Hypothesis: empirical observation that most
  objects in a program die young (allocated and become
  unreachable within a short time).
- Impact on design: allocate new objects in a small, fast-to-collect
  area (Young Gen). Collect it frequently. The vast majority
  of young objects are dead at collection time -> copying
  collector only copies survivors (small minority) -> very fast.
  Long-lived objects promoted to Old Gen; collected infrequently.
- Trade-off: objects that violate the hypothesis (medium-lived,
  survive many Young GCs but eventually die) are the worst
  case. They congest Old Gen with temporary objects, causing
  premature Old GC.

**Q2: "What is the difference between G1 GC and ZGC?
When would you choose ZGC?"**

*Why they ask:* Modern Java GC knowledge. Relevant for
latency-sensitive service design.

*Strong answer includes:*
- G1 GC (default Java 9+): region-based, concurrent marking,
  targets configurable pause millis. Typical pauses: 10-200ms.
  Concurrent Mode Failure possible under high allocation rate.
- ZGC (Java 15+ production): colored pointers, load barriers,
  concurrent object relocation. Typical pauses: <1ms even on
  terabyte heaps. No Concurrent Mode Failure equivalent.
  Trade-off: ~6 additional instructions per heap load (barrier cost).
  Memory overhead: colored pointer bits reduce addressable space
  on some platforms (not a concern for most deployments).
- Choose ZGC when: latency SLA is under 50ms P99, heap >16GB,
  or workload is latency-sensitive (financial, real-time).
  G1 is sufficient for most enterprise workloads with 200ms
  pause budgets.

**Q3: "How do you diagnose a GC performance problem in production?"**

*Why they ask:* Practical production experience. SRE-level question.

*Strong answer includes:*
1. Enable GC logging: `-Xlog:gc*:file=gc.log:time,uptime:filecount=5,filesize=20m`
2. Observe metrics: `jstat -gcutil <pid> 1000` - watch Young GC
   frequency and pause time, Old Gen fill rate.
3. Look for: Full GC events (always a problem), CMF messages
   (`concurrent-mark-abort`), pause times exceeding SLA.
4. If Full GC: CMF cause? Reduce `InitiatingHeapOccupancyPercent`.
   Evacuation failure? Increase heap. Explicit GC? Add `-XX:+DisableExplicitGC`.
5. If High Young GC frequency: allocation rate too high.
   Profile allocation with async-profiler (`-e alloc`).
   Find top allocation sites. Reduce object creation (caching, pooling, records).
6. Heap dump (for memory leaks): `jmap -dump:format=b,file=heap.hprof <pid>`.
   Analyze with Eclipse MAT: Leak Suspects, dominator tree.
