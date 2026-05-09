---
id: CSF-050
title: Garbage Collection Algorithms Overview
category: CS Fundamentals - Paradigms
tier: tier-1-foundations
folder: CSF-cs-fundamentals
difficulty: ★★☆
depends_on:
used_by:
related:
tags:
  - csf
  - intermediate
  - deep-dive
  - tradeoff
status: draft
version: 1
layout: default
parent: "CS Fundamentals - Paradigms"
grand_parent: "Technical Dictionary"
nav_order: 50
permalink: /csf/garbage-collection-algorithms-overview/
---

# CSF-050 - Garbage Collection Algorithms Overview

⚡ TL;DR - Garbage collection algorithms differ in how they find dead objects, when they collect, and what pauses they cause; understanding the trade-offs between throughput, latency, and memory overhead drives GC selection.

| CSF-050         | Category: CS Fundamentals - Paradigms | Difficulty: ★★☆ |
| :-------------- | :------------------------------------ | :-------------- |
| **Depends on:** | CSF-023, CSF-015                      |                 |
| **Used by:**    | CSF-049, CSF-059                      |                 |
| **Related:**    | CSF-023, CSF-049, CSF-059             |                 |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
In C/C++, memory management is manual: `malloc`/`free`. Forgetting
to free causes memory leaks. Freeing too early causes use-after-free
(security vulnerability: CVE-2014-6271 Shellshock was partly UAF).
Double-free corrupts the heap. These errors are notoriously hard
to find and fix. GC eliminates this entire class of bugs.

**THE BREAKING POINT:**
As programs grew larger and more concurrent, manual memory
management became untenable. LISP (1958) introduced the first
GC: mark-and-sweep. It worked but paused the program completely
for every collection. For interactive applications, this
"stop-the-world" pause was unacceptable.

**THE INVENTION MOMENT:**
Generational GC (1984, based on the "weak generational hypothesis":
most objects die young) reduced pause times by collecting only
the young generation most of the time. Modern GCs (G1, ZGC,
Shenandoah) achieve near-zero pauses by doing most work
concurrently with the application.

**EVOLUTION:**
JVM GC evolved: Serial → Parallel → CMS → G1 → ZGC/Shenandoah.
Go, Python, and .NET have their own GC designs. The trend:
low-pause concurrent collectors at the cost of higher CPU overhead
and memory footprint.

---

### 📘 Textbook Definition

Garbage collection (GC) is the automatic reclamation of heap
memory occupied by unreachable objects. Key algorithms:
**Mark-and-sweep**: traverse from GC roots, mark reachable;
sweep unreachable. **Copying**: copy live objects to new region;
old region freed in bulk. **Generational**: divide heap into
young (frequently collected) and old (infrequently collected)
generations based on object age. **Concurrent**: perform
mark/sweep phases concurrently with application threads to
reduce stop-the-world pauses.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
GC finds objects no longer reachable from roots and reclaims their memory; the key trade-off is pause time vs throughput vs memory.

**One analogy:**

> GC is like a hotel cleaning service. You can clean rooms as
> guests check out (incremental), only clean rooms after all
> guests leave (stop-the-world), or send cleaners to clean
> occupied rooms during quiet hours without disturbing guests
> too much (concurrent). Each approach trades thoroughness
> for convenience.

**One insight:**
No GC algorithm is universally best. Short pauses (ZGC) cost
more CPU. High throughput (Parallel GC) causes longer pauses.
Choosing a GC is a decision about which resource is most
expensive in your specific application.

---

### 🔩 First Principles Explanation

**CORE INVARIANTS:**

1. An object is _live_ if reachable from any GC root (thread stack, static fields, JNI).
2. An object is _garbage_ if not reachable. Reachability is by reference graph traversal.
3. Compaction moves live objects to eliminate fragmentation; requires updating all references.
4. Stop-the-world (STW) pauses are necessary when threads must see a consistent heap state.
5. Concurrent GC threads work alongside application threads; write barriers track mutations.

**DERIVED DESIGN:**

- **Serial GC** — single-threaded, STW, good for small heaps
- **Parallel GC** — multi-threaded collection, STW, high throughput
- **G1 GC** — region-based, predictable pause targets, generational
- **ZGC** (Java 11+) — concurrent, sub-millisecond pauses, load barriers
- **Shenandoah** — concurrent, sub-millisecond, no generational

**THE TRADE-OFFS:**
**Throughput GC (Parallel):** Maximum throughput; longer pauses.
**Low-latency GC (ZGC/Shenandoah):** Sub-ms pauses; higher CPU.
**Balanced (G1):** Configurable pause target; good default for most apps.

**ESSENTIAL vs ACCIDENTAL COMPLEXITY:**
**Essential:** Dead objects must be found and memory reclaimed.
**Accidental:** Fragmentation (solved by compaction/copying), finalisation latency,
class unloading delays.

---

### 🧪 Thought Experiment

**SETUP:**
Your application: REST API, 2ms P99 target, 4GB heap.

**WITH PARALLEL GC (default pre-Java 9):**

```
GC pause at 500ms intervals: 50-200ms
P99 latency: 200ms (GC pause dominates)
Throughput: excellent
```

**WITH G1 GC (`-XX:MaxGCPauseMillis=10`):**

```
GC pause target: 10ms
P99 latency: 12ms (target mostly met)
Throughput: ~5% lower
```

**WITH ZGC:**

```
GC pause: sub-millisecond (typically 0.1-0.5ms)
P99 latency: 2ms (on target)
Throughput: ~10-15% lower (concurrent work)
Memory overhead: higher (~10-20%)
```

**THE INSIGHT:**
GC choice is a _resource allocation_ decision. ZGC trades CPU
and memory for latency. Parallel GC trades latency for throughput.
For a latency-sensitive service, ZGC's trade-off is worth it.

---

### 🧠 Mental Model / Analogy

> The heap is a car park. GC is the car park management system.
> **Mark-sweep**: check every bay; mark occupied; remove cars
> from empty bays. **Copying collector**: move all cars to one
> half, open the other half completely. **Generational**: a
> fast-turnover short-stay section (young gen, clear hourly)
> and a long-stay section (old gen, clear weekly). **Concurrent**:
> staff walk around checking bays without closing the car park.

**Element mapping:**

- Car park = heap
- Parked cars = live objects
- Empty bays = free memory
- Checking bays = tracing references
- Clearing a section = collection
- Closing the car park = STW pause

Where this analogy breaks down: cars can reference each other
(object graphs); a car that can only be reached via another car
that leaves is also collectable.

---

### 📶 Gradual Depth - Four Levels

**Level 1 - What it is (anyone can understand):**
GC automatically cleans up memory. It finds objects no longer
used and frees their space. Different GCs do this at different
times and with different impacts on application speed.

**Level 2 - How to use it (junior developer):**
Default Java GC (G1 in Java 9+) is fine for most apps.
For latency-sensitive apps: add `-XX:+UseZGC -XX:MaxGCPauseMillis=5`.
For batch/throughput: `-XX:+UseParallelGC`. Monitor with `jstat
-gcutil <pid> 1000` and watch Old gen growth.

**Level 3 - How it works (mid-level engineer):**
G1 divides heap into equal-sized regions (~1-32MB). It tracks
remembered sets: pointers from old gen to young gen regions.
At minor GC: evacuate live objects from young gen regions.
At mixed GC: also evacuate the most garbage-dense old regions.
The pause time target controls how many regions to collect per cycle.

**Level 4 - Why it was designed this way (senior/staff):**
ZGC uses _load barriers_ (not write barriers) to enable
concurrent relocation: when an application thread dereferences
a pointer, the load barrier checks if the object has been
moved and heals the pointer. This allows ZGC to move objects
while the application runs, achieving sub-ms pauses even
for 1TB heaps. The design insight: make the common operation
(read) cheap; make the rare operation (move) concurrent.

**Expert Thinking Cues:**

- GC metrics: Old gen growth rate, Full GC frequency, pause duration at P99
- If P99 latency is dominated by GC pauses: switch to ZGC or Shenandoah
- If throughput is primary goal with no latency constraint: use Parallel GC

---

### ⚙️ How It Works (Mechanism)

**Generational heap (G1 layout):**

```
Eden -> [minor GC] -> Survivor S0 -> Survivor S1 -> Old Gen
Eden: new objects allocated here
Survivor: objects that survived 1+ minor GCs
Old: objects that survived N threshold minor GCs
```

**Concurrent marking (ZGC):**

```
1. STW: initial mark (root scan, ~0.1ms)
2. Concurrent: mark all reachable objects
3. STW: remark (catch mutations during concurrent mark, ~0.1ms)
4. Concurrent: prepare relocation set
5. STW: relocate roots (~0.1ms)
6. Concurrent: relocate objects (app threads heal pointers via load barriers)
```

**Key JVM flags:**

```bash
-XX:+UseG1GC -XX:MaxGCPauseMillis=200  # G1, 200ms target
-XX:+UseZGC                            # ZGC, sub-ms pauses
-XX:+UseParallelGC                     # throughput focus
-Xms4g -Xmx8g                          # heap sizing
```

---

### 🔄 The Complete Picture - End-to-End Flow

**NORMAL FLOW (G1 minor GC):**

```
Eden fills up (young gen full)    ← YOU ARE HERE
  |
STW: minor GC begins (pause ~5ms)
  |-> trace from roots + remembered sets
  |-> copy live young gen objects to Survivor
  |-> dead young gen objects freed in bulk
  |-> Eden regions reset to empty
STW: minor GC ends
  |-> application resumes
  |-> some Survivor objects tenured to Old gen
Old gen fills: mixed GC triggered
  |-> collect both young gen + most-garbage old regions
```

**FAILURE PATH:**

- Full GC: Old gen exhausted; entire heap collected STW (seconds)
- Promotion failure: Survivor full; objects promoted directly to Old
- Concurrent mode failure (CMS): concurrent collection falls behind; STW fallback

---

### ⚖️ Comparison Table

| GC         | Pause                   | Throughput  | Memory Overhead | Use Case                  |
| ---------- | ----------------------- | ----------- | --------------- | ------------------------- |
| Serial     | Long (STW)              | Low         | Low             | Small heaps, batch        |
| Parallel   | Medium (STW)            | High        | Low             | Batch, throughput-focused |
| G1         | Configurable (10-200ms) | Medium-High | Medium          | General purpose           |
| ZGC        | Sub-ms (concurrent)     | Medium      | High            | Latency-sensitive         |
| Shenandoah | Sub-ms (concurrent)     | Medium      | High            | Latency-sensitive         |

---

### ⚠️ Common Misconceptions

| Misconception                      | Reality                                                                                   |
| ---------------------------------- | ----------------------------------------------------------------------------------------- |
| "More heap = less GC"              | More heap delays GC; doesn't prevent leaks; large heaps cause longer Full GC pauses       |
| "GC pauses are random"             | GC pauses are triggered by heap pressure; predictable with proper sizing and GC selection |
| "ZGC is always better"             | ZGC trades throughput and memory for latency; wrong choice for batch jobs                 |
| "Full GC means something is wrong" | Occasional Full GC is normal; frequent Full GC signals a problem                          |
| "G1 is the best GC for Java"       | G1 is a good default; ZGC outperforms it for latency-sensitive apps                       |

---

### 🚨 Failure Modes & Diagnosis

**Mode 1: Frequent Full GC / GC Overhead Limit Exceeded**
**Symptom:** `java.lang.OutOfMemoryError: GC overhead limit exceeded`.
**Root Cause:** GC spends >98% of time but recovers <2% heap.
Caused by a memory leak: live set too large.
**Diagnostic:**

```bash
jstat -gcutil <pid> 1000
# O (Old gen) growing: 60%, 65%, 70%, 75%...
# Solution: heap dump + leak analysis (see CSF-049)
```

**Mode 2: Long G1 Full GC Pause**
**Symptom:** Application pauses for 10-30 seconds.
**Root Cause:** G1 falls back to Full GC because concurrent collection can't keep up.
**Diagnostic:**

```bash
# Enable GC logging
java -Xlog:gc*:file=gc.log:time,uptime,level,tags
# Look for: [Pause Full] lines showing duration
```

**Fix:** Increase heap (`-Xmx`); switch to ZGC; reduce allocation rate.

**Mode 3: Promotion Failure**
**Symptom:** Spike in GC pause; minor GC takes seconds.
**Root Cause:** Old gen too full to accept objects promoted from Survivor.
**Fix:** Increase Old gen size; reduce object promotion rate.

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**

- [[CSF-023 - Stack vs Heap Memory]]
- [[CSF-015 - Memory Management Models]]

**Builds On This (learn these next):**

- [[CSF-049 - Memory Leak Detection and Tooling]]
- [[CSF-059 - GC Pause Analysis and Production Impact]]

**Alternatives / Comparisons:**

- Manual memory management (Rust RAII, C malloc/free)
- Reference counting (Python, Swift, ARC in Obj-C)

---

### 📌 Quick Reference Card

```
┌─────────────────────────────────────────────────────┐
│ WHAT IT IS      Automatic reclamation of unreachable   │
│                 heap objects                         │
│ PROBLEM         Manual memory: leaks + use-after-free  │
│ IT SOLVES       + double-free                        │
│ KEY INSIGHT     No universal best GC: throughput vs   │
│                 latency vs memory is a trade-off      │
│ USE WHEN        All GC-managed languages (Java, Go...) │
│ AVOID WHEN      Real-time systems needing determinism  │
│ TRADE-OFF       Parallel: throughput; ZGC: latency;   │
│                 G1: balanced                         │
│ ONE-LINER       Find dead objects, reclaim memory;    │
│                 pause vs throughput is the dial      │
│ NEXT EXPLORE    CSF-059, ZGC, JFR GC analysis         │
└─────────────────────────────────────────────────────┘
```

**If you remember only 3 things:**

1. GC collects unreachable objects; leaks = objects reachable but logically dead.
2. Parallel GC maximises throughput; ZGC minimises latency; G1 balances both.
3. For latency-sensitive apps use ZGC; enable GC logging for diagnosis.

**Interview one-liner:**
"GC algorithms vary in pause time, throughput, and memory overhead; Parallel GC maximises throughput with longer pauses; G1 balances with configurable pause targets; ZGC/Shenandoah achieve sub-millisecond pauses by doing collection work concurrently."

---

### 💎 Transferable Wisdom

**Reusable Engineering Principle:**
Every resource management system faces the same trade-off:
reclaim aggressively (more pauses, lower memory use) or
reclaim lazily (fewer pauses, higher memory use). This
trade-off applies to GC, to database VACUUM, to cache
eviction, and to log file rotation.

**Where else this pattern appears:**

- **PostgreSQL VACUUM** — reclaims dead tuples; similar pause vs throughput trade-offs
- **Redis LRU/LFU eviction** — reclaims least-used keys when memory fills
- **Browser tab GC** — reclaims memory from detached DOM elements

---

### 💡 The Surprising Truth

The JVM's generational GC is based on the "weak generational
hypothesis": most objects die young. Empirical studies across
many Java programs confirm this: 90-98% of objects never
survive their first minor GC. This is not a universal law
of computation — it's an empirical observation about typical
object-oriented programs. When programs violate this (e.g.,
caching everything in memory long-term), generational GC
performs worse than a simpler non-generational collector.

---

### 🧠 Think About This Before We Continue

**Q1 (Root Cause):** A Java service using G1 GC with 8GB heap
gets a Full GC every 2 hours lasting 20 seconds. The Old gen
growth rate is 100MB/hour. Is this a memory leak, a sizing
problem, or a GC configuration problem? How do you distinguish?

_Hint:_ Calculate: 100MB/hour \* 2 hours = 200MB. G1 should be
able to evacuate 200MB without Full GC. Look at G1 mixed GC
frequency and target pause. Is the concurrent collector
keeping up?

**Q2 (Scale):** Reference counting (Python, Swift) is an
alternative to mark-and-sweep GC. It increments a counter on
assignment and decrements on release; when the counter hits 0,
the object is freed immediately. What is the fundamental
limitation of reference counting, and why does Python need
a cyclic GC in addition to reference counting?

_Hint:_ Consider two objects that reference each other
(`a.ref = b; b.ref = a`). What happens to their reference
counts when no other code holds them?

**Q3 (Design Trade-off):** Rust has no GC: memory is managed
by ownership and RAII. C++ also has RAII. Both achieve
deterministic deallocation: an object is freed exactly when
it goes out of scope. Why doesn't the JVM use RAII instead of GC?
What problem would RAII need to solve differently?

_Hint:_ Consider Java's object sharing semantics: multiple
variables can reference the same object (`List<X>` shared
between two classes). Who is the owner? When does RAII trigger?
