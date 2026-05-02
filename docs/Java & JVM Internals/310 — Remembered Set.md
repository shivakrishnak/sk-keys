---
layout: default
title: "Remembered Set"
parent: "Java & JVM Internals"
nav_order: 310
permalink: /java/remembered-set/
number: "0310"
category: Java & JVM Internals
difficulty: ★★★
depends_on:
  - Card Table
  - Write Barrier
  - G1GC
  - Young Generation
  - Old Generation
used_by:
  - G1GC
  - GC Tuning
  - Minor GC
related:
  - Card Table
  - Write Barrier
  - G1GC
  - GC Roots
tags:
  - jvm
  - gc
  - memory
  - java-internals
  - deep-dive
---

# 0310 — Remembered Set

⚡ TL;DR — A Remembered Set (RSet) is a per-region index of all external references into a heap region, allowing G1GC to collect any individual region without scanning the entire heap for incoming references.

| #0310 | Category: Java & JVM Internals | Difficulty: ★★★ |
|:---|:---|:---|
| **Depends on:** | Card Table, Write Barrier, G1GC, Young Generation, Old Generation | |
| **Used by:** | G1GC, GC Tuning, Minor GC | |
| **Related:** | Card Table, Write Barrier, G1GC, GC Roots | |

---

### 🔥 The Problem This Solves

WORLD WITHOUT IT:
G1GC divides the heap into many equal-sized regions (1–32MB each). Its key feature is collecting individual regions incrementally — choosing the "garbage-richest" regions to collect first (the "Garbage First" in G1). But to safely collect a region `R`, the GC must know ALL external references pointing into `R` from other regions. Without tracking these cross-region references, the only option is to scan the ENTIRE heap to find references into `R` — defeating the purpose of incremental collection.

THE BREAKING POINT:
G1GC wants to collect 10 "garbage-rich" regions out of 200 total regions. To safely do so, it needs to find all references from the 190 uncollected regions into the 10 target regions. Without RSet: scan all 190 regions = scan 150GB of heap data. With RSet: look up only the remembered set for each of the 10 target regions — which contains only the relevant cards. Entire root set: scan seconds vs milliseconds.

THE INVENTION MOMENT:
This is exactly why the **Remembered Set** was created — to be the per-region index that lets G1GC collect any subset of regions without scanning the rest.

---

### 📘 Textbook Definition

A **Remembered Set (RSet)** is a per-heap-region data structure in G1GC that records which cards in OTHER regions contain references pointing into this region. When a reference from Region A to Region B is stored (via write barrier), the corresponding card in Region A is added to Region B's RSet. During collection of Region B, the GC only needs to scan the cards listed in Region B's RSet to find all incoming external references — not the entire heap. RSets are maintained incrementally by G1GC's concurrent refinement threads, which process the write barrier's dirty card queue in the background during application execution.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
Every heap region keeps a guest list of all regions that have references pointing into it.

**One analogy:**
> Imagine a school with 50 classrooms. Before fire drill, the principal must know where every child is. Instead of searching every classroom for children belonging to Room 12, Room 12 keeps a list: "children from Room 7, Row 3, Seat 5; children from Room 15, Row 1, Seat 2..." — the RSet. At fire drill (GC), the principal only needs Room 12's list — not all 50 rooms.

**One insight:**
The RSet converts a "scan the world" problem into a "look up the index" problem. Its existence is what makes G1GC's incremental region collection feasible. The cost: every cross-region reference requires maintenance (write barrier → card queue → refinement thread → RSet update). This per-reference maintenance overhead is what G1GC's RSet maintenance threads consume during normal application execution.

---

### 🔩 First Principles Explanation

CORE INVARIANTS:
1. To collect a region `R`, the GC must find ALL live objects in `R` via all incoming references.
2. Live references can exist in ANY other region.
3. Scanning all other regions per collected region = O(heap_size × collected_regions) = unacceptably slow.

DERIVED DESIGN:
Invert the tracking: instead of "what does region A reference?" (card table), track "who references region B?" (RSet).

Structure of RSet:
- **Sparse PRT (Per-Region Table)**: Hash map of (region_index → card_bitmap). For regions with few references: use a hash set of card indices.
- **Fine-grained PRT**: When the sparse table grows large, switch to a dense bitmap covering all cards in the referencing region.
- **Coarse-grained**: When a region has references from too many other regions, switch to a full "scan all cards in that region" marker — trading RSet precision for memory.

```
┌──────────────────────────────────────────────────┐
│        Remembered Set Structure (G1GC)           │
│                                                  │
│  Region R's RSet:                                │
│  {                                               │
│    Region_7:  [card_12, card_45, card_87]        │
│    Region_15: [card_3]                           │
│    Region_23: [ALL] ← coarse-grained (many refs) │
│  }                                               │
│                                                  │
│  To collect Region R:                            │
│   For each entry (region_src, cards):             │
│     For each card:                               │
│       Scan 512 bytes at card_src + offset        │
│       Add any refs to Region R → GC root set    │
│   (Never scan uncited regions at all)            │
└──────────────────────────────────────────────────┘
```

THE TRADE-OFFS:
Gain: Incremental per-region collection; no whole-heap scan per GC cycle; enables G1GC's core "Garbage First" feature.
Cost: RSet memory overhead (5–20% of heap in some workloads); concurrent refinement thread CPU; coarse-grained RSets reduce collection precision; high cross-region reference rates → large RSets → reduced collection efficiency.

---

### 🧪 Thought Experiment

SETUP:
G1GC heap: 4GB, 200 regions of 20MB each. Application: a web service building object graphs where each request creates objects that frequently reference objects from other requests' graphs (cross-region references).

HIGH CROSS-REGION REFERENCE RATE:
Each request creates 1,000 new objects and establishes 500 cross-region references to objects from the "global data" region (Region 0). Region 0's RSet grows. After 1 hour: Region 0 has references from 190 other regions. G1GC switches Region 0's RSet to coarse-grained (scan all 190 source regions during collection). Collecting Region 0 now requires scanning 190 × 20MB = 3.8GB. The RSet's optimization is negated by the high-cardinality case.

LOW CROSS-REGION REFERENCE RATE:
Each request's objects are self-contained (reference only within the same request's region). Cross-region references: only from the "request cache" (5 regions). Each collected region's RSet covers 5 source cards. Collection of any region: 5 × 512B scan = 2.5KB. 1,000x faster collection per region than the high-reference case.

THE INSIGHT:
RSets work best when the reference graph respects region boundaries — when logically-related objects are co-located in the same region. G1GC's region assignment is proximity-based (new allocations fill the same region until it's full), so this often happens naturally. But certain patterns (large shared global objects referenced from many short-lived request objects) create high-cardinality RSets that degrade G1GC's effectiveness.

---

### 🧠 Mental Model / Analogy

> The Remembered Set is like a building guest management system. Each floor (heap region) maintains a visitor log: which visitors (references) came from which other floors. When the building's fire marshal (GC) needs to know who is on Floor 12 (the region being collected), they check Floor 12's visitor log — not every other floor's room-by-room directory.

"Floor" → G1GC heap region.
"Visitor log" → Remembered Set.
"Log entry: 'visitor from Floor 7, Room 3'" → reference from region 7, card 3.
"Checking the log" → GC root scanning via RSet.
"Room-by-room directory scan" → what GC would need without RSet.

Where this analogy breaks down: A real visitor log is append-only. RSet entries are deduplicated and can be "coarsened" — when a floor has too many visitors from one floor, the system simplifies to "scan all rooms on that floor." This coarsening trades precision for memory efficiency.

---

### 📶 Gradual Depth — Four Levels

**Level 1 — What it is (anyone can understand):**
Each chunk of memory in G1GC keeps a list of all other chunks that have pointers into it. When the GC collects a chunk, it knows exactly which other chunks to check for pointers — no need to check everything.

**Level 2 — How to use it (junior developer):**
RSet is automatic. Tune G1GC's RSet parameters if GC logs show high "Update RS" or "Scan RS" phase times:
- High "Update RS": too many cross-region reference writes. Review code for global shared mutable objects.
- High "Scan RS": RSet entries are large (many cards per region). Object graph crosses too many region boundaries.

**Level 3 — How it works (mid-level engineer):**
Write barrier → dirty card queue → G1 concurrent refinement thread → RSet update. The refinement threads run concurrently to process dirty cards from the write barrier queue. They update each RSet: for each dirty card at address `X` in region `A`, they scan the 512 bytes at X for references to other regions, and add those references to the target regions' RSets. If an RSet grows too large (>G1RSetRegionEntries), it switches to coarse-grained mode. `G1RSetSparseRegionEntries` (default 4) controls the threshold between sparse and fine-grained.

**Level 4 — Why it was designed this way (senior/staff):**
The Remembered Set hierarchy (sparse → fine-grained → coarse-grained) is an adaptive data structure design. Sparse (hash set of cards): O(refs) memory, fast iteration. Fine-grained (card bitmap per region): predictable memory (bytes per region), slightly slower iteration over zeros. Coarse-grained (just a bit per source region): minimal memory, requires full region scan on collection. The transitions between modes represent a memory/precision trade-off navigated at runtime. The G1RSet tuning parameters (`G1RSetRegionEntries`, `G1RSetSparseRegionEntries`) allow tuning where these transitions occur. In Java 21's Generational ZGC (experimental), remembered sets take a different form: generation-specific tracking without the region-per-region index overhead of G1.

---

### ⚙️ How It Works (Mechanism)

**RSet Update Pipeline:**
```
[Write barrier: obj.field = new_ref]
    ↓ (if obj and new_ref are in different regions)
[Add to Dirty Card Queue (per-thread buffer)]
    ↓ (when buffer fills)
[Flush to global Dirty Card Queue]
    ↓ (concurrent refinement thread)
[Scan dirty card for cross-region refs]
    ↓
[For each cross-region ref found]
[Update target_region.rset.add(source_card)]
```

**RSet Levels:**
```
Level 0 — Sparse PRT:
  HashMap(region_id → List(card_index))
  Memory: ~64B per entry
  Used when: < G1RSetSparseRegionEntries entries

Level 1 — Fine-grained PRT:
  For each referencing region: BitSet of cards
  Memory: (region_size / card_size) bits per source region
  Used when: many cards from few regions

Level 2 — Coarse-grained:
  BitSet of regions (1 bit per region)
  Memory: (total_regions / 8) bytes
  Used when: too many referencing regions
  Cost: entire source region must be scanned per GC
```

**Concurrent Refinement Threads:**
```bash
# Show refinement thread count:
java -XX:+UseG1GC \
     -XX:G1ConcRefinementThreads=4 MyApp
# Default: ConcGCThreads threads for refinement
```

**GC Phase Timing:**
```
G1GC Pause breakdown:
  Pre-Evacuate Collection Set:
    Retire TLABs [0.5ms]
    Choose Collection Set [0.1ms]
  Evacuate Collection Set:
    Scan Root Regions [2.0ms]  ← scans RSets
    Update RS [3.5ms]          ← finalize dirty cards
    Scan RS [1.8ms]            ← scan RSet-identified cards
    Object Copy [4.2ms]        ← copy live objects
  Post-Evacuate Collection Set:
    Other [0.4ms]
  Total: 12.5ms
```

---

### 🔄 The Complete Picture — End-to-End Flow

NORMAL FLOW:
```
[Mutator: Region A writes reference to Region B object]
    → [Write barrier fires]
    → [Dirty card added to per-thread queue]
    → [Queue flushed to global dirty card queue]
    → [Refinement thread: processes dirty card]  ← YOU ARE HERE
    → [Finds cross-region reference A→B]
    → [Region B RSet updated: add card from Region A]

[G1 Minor Collection: target includes Region B]
    → [Scan Region B's RSet]          ← YOU ARE HERE
    → [For each (Region A, card) in RSet:]
    →   [Scan 512B at Region A[card]]
    →   [Find ref to Region B object → add to roots]
    → [Collect Region B with complete root set]
    → [Data correct, no false collection]
```

FAILURE PATH:
```
[RSet grows coarse-grained due to high cross-region refs]
    → [Collection of Region B requires scanning ALL A's]
    → [Scan phase dominates GC pause time]
    → [G1 falls back to Full GC for severely polluted RSets]
    → [Fix: reduce cross-region reference rate]
    → [Or: increase region size (-XX:G1HeapRegionSize=32m)]
```

WHAT CHANGES AT SCALE:
At 256GB heap with 8MB regions (32,768 regions), RSet overhead per region can be significant. G1GC's coarse-grained mode activates more readily. At scale, teams typically increase `G1HeapRegionSize` to reduce the number of regions, or switch to ZGC (which doesn't use per-region RSets in the same way) to eliminate the RSet overhead for very large heaps.

---

### 💻 Code Example

Example 1 — Monitoring RSet overhead in GC logs:
```bash
java -XX:+UseG1GC \
     -Xlog:gc+phases=info MyApp 2>&1 | \
  grep -E "Update RS|Scan RS|Refine"

# High "Update RS" time = write barrier queue backed up
# High "Scan RS" time = large RSets, many cross-region refs
# Target: Update RS < 1ms, Scan RS < 2ms for 10ms pause budget
```

Example 2 — Tuning RSet refinement for high write rate:
```bash
# Increase refinement threads for write-heavy applications:
java -XX:+UseG1GC \
     -XX:G1ConcRefinementThreads=8 \
     -XX:G1RSetUpdatingPauseTimePercent=10 MyApp

# G1RSetUpdatingPauseTimePercent: percentage of pause budget
# allowed for RSet update (default 10%)
```

Example 3 — Code causing RSet pollution (avoid):
```java
// BAD: Global singleton with references from many request objects
// All request objects reference this → high RSet entries
@Component
public class GlobalContext {
    // This object in Old Gen will have references from
    // every request's Young Gen processing object
    private final Map<String, Object> sharedData = ...;
}

// GOOD: Pass data locally instead of referencing global state
// Reduces cross-region reference cardinality
public Response process(Request req, RequestContext ctx) {
    // ctx is co-local with request objects (same region)
    return computeResponse(req, ctx);
}
```

Example 4 — Increasing region size to reduce RSet overhead:
```bash
# Default G1HeapRegionSize: calculated as heap / 2048
# For 32GB heap: 16MB regions
# For 256GB heap: increase to reduce region count:

java -XX:+UseG1GC \
     -Xmx256g \
     -XX:G1HeapRegionSize=32m \  # 32MB regions
     MyApp
# 256GB / 32MB = 8192 regions (vs 131072 with 2MB regions)
# Fewer regions = less RSet overhead per region
```

---

### ⚖️ Comparison Table

| GC Cross-Region Tracking | Structure | Memory Cost | Scan Efficiency | Used By |
|---|---|---|---|---|
| **Remembered Set (G1)** | Per-region sparse/dense index | 5–20% of heap | O(cross-gen refs) | G1GC |
| Card Table (generational) | Global bitmap | Heap / 512B | O(dirty cards) | All generational GCs |
| ZGC colored pointers | Pointer bits + region map | Near zero | Barrier-based | ZGC, Generational ZGC |
| Region-pair table | 2D region × region matrix | O(regions²) | Direct lookup | Research collectors |

How to choose: RSets are G1GC-specific. If RSet overhead dominates (large heap, high cross-region reference rate), consider ZGC or Shenandoah which handle cross-region references differently.

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| RSet stores references, not cards | RSet stores *cards* (512-byte region granularity from the card table), not individual references. This is why "Scan RS" reads 512 bytes per entry, not just the individual reference |
| Remembered Sets are per-thread | RSets are per-region (one RSet per G1 heap region). They are maintained by concurrent refinement threads (shared), not per-thread |
| Large heap always means larger RSets | RSet size depends on cross-region reference cardinality, not heap size. A 256GB heap with low cross-region references has small RSets; a 4GB heap with high cross-region references may have bloated RSets |
| Disabling write barriers eliminates RSet overhead | Write barriers ARE how RSets are maintained. Disabling them would break RSet correctness and make G1's incremental collection incorrect |
| G1GC collects one region at a time | G1GC collects a "collection set" of multiple regions per pause, not one at a time. The collection set is chosen to maximize garbage collected within the pause time budget using RSets to locate all incoming references |
| RSet maintenance happens during GC pauses only | RSet maintenance happens PRIMARILY during application execution via concurrent refinement threads. GC pauses only finalize the RSet work that couldn't be done concurrently |

---

### 🚨 Failure Modes & Diagnosis

**Bloated RSets Causing Long G1 Pauses**

Symptom:
G1GC "Scan RS" phase takes > 10ms. GC log shows large number of R/Set card scans. Heap usage is moderate but pauses are long.

Root Cause:
Many cross-region references (e.g., one globally-shared region referenced from thousands of short-lived request regions). The shared region's RSet has entries from every other region → coarse-grained → require scanning entire source regions.

Diagnostic Command / Tool:
```bash
java -Xlog:gc+remset*=debug MyApp 2>&1 | \
  grep "RS.*coarse\|coarse_grain"

# Also:
jcmd <pid> GC.heap_info
# Look for regions with high incoming reference counts
```

Fix:
Reduce the number of cross-region references to the hot region:
- Increase region size to co-locate related objects.
- Avoid global mutable singletons with per-request references.
- Consider switching to ZGC for large heaps with high reference cardinality.

Prevention:
Model object reference patterns in design review. High-fan-in objects (many-to-one references) are G1GC enemies.

---

**Refinement Thread Lag Causing GC Pause Spike**

Symptom:
Periodic large G1GC pauses where "Update RS" takes 5–15ms. Refinement threads lag behind the write barrier queue.

Root Cause:
Write barrier dirty card queue grows faster than refinement threads can process. At GC time, the remaining unrefined cards must be processed synchronously in the GC pause.

Diagnostic Command / Tool:
```bash
java -Xlog:gc+refine=debug MyApp 2>&1 | grep "Refinement"
# Look for: "Adjusted thread count from N to M"
# This shows adaptive refinement struggling to keep up
```

Fix:
```bash
java -XX:G1ConcRefinementThreads=12 \
     -XX:G1RSetUpdatingPauseTimePercent=5 MyApp
# More refinement threads + tighter pause budget
```

Prevention:
Monitor dirty card queue depth as a metric. Alert if queue depth consistently > 10,000 cards between GC cycles.

---

**G1 Full GC Triggered by RSet Overflow**

Symptom:
G1GC suddenly performs a Full GC (very long pause, > 1 second). GC log shows "Humongous allocation" or "RSet is overflowed" or "evacuation failure" related to RSet.

Root Cause:
RSet maintenance falls critically behind or corruption occurs (rare but possible under extreme load). G1GC falls back to Full GC as a safety mechanism.

Diagnostic Command / Tool:
```bash
java -Xlog:gc*=debug MyApp 2>&1 | grep "Full GC\|RSSet"
```

Fix:
Increase heap (more region capacity). Reduce object promotion rate (reduce allocation). Switch GC algorithms if recurring.

Prevention:
Never run G1GC >85% heap occupancy. Set `-XX:InitiatingHeapOccupancyPercent=35` to start concurrent marking early.

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**
- `Card Table` — RSets are built on top of the card table concept; understanding card table structure is prerequisite
- `Write Barrier` — RSets are maintained by write barriers; the mechanism that feeds RSet entries
- `G1GC` — RSets are a G1GC-specific structure; understanding G1GC's region-based design explains why RSets exist

**Builds On This (learn these next):**
- `G1GC` — the GC algorithm that uses RSets most prominently; understanding G1's region collection strategy shows RSets in action
- `GC Tuning` — RSet overhead is a key G1GC tuning dimension; understanding RSets is prerequisite to G1GC tuning

**Alternatives / Comparisons:**
- `Card Table` — the global, coarser alternative: tracks dirty cards globally rather than by target region. Card table is simpler; RSet enables incremental collection
- `ZGC` — uses colored pointers and region maps as an alternative to RSets for cross-region tracking; designed for lower overhead at very large heap sizes

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ WHAT IT IS   │ Per-region index: which other regions     │
│              │ hold references INTO this region          │
├──────────────┼───────────────────────────────────────────┤
│ PROBLEM IT   │ Without it, collecting a G1 region        │
│ SOLVES       │ requires scanning the entire heap         │
├──────────────┼───────────────────────────────────────────┤
│ KEY INSIGHT  │ RSet size = cross-region ref cardinality  │
│              │ not heap size. One globally-referenced    │
│              │ object can bloat its region's RSet        │
│              │ to cover every other region               │
├──────────────┼───────────────────────────────────────────┤
│ USE WHEN     │ Automatic (G1GC). Tune for large heaps    │
│              │ or high cross-region reference workloads  │
├──────────────┼───────────────────────────────────────────┤
│ AVOID WHEN   │ ZGC/Shenandoah for ultra-large heaps with │
│              │ high reference fan-out                    │
├──────────────┼───────────────────────────────────────────┤
│ TRADE-OFF    │ Fast incremental collection vs memory     │
│              │ overhead + refinement CPU cost            │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "Every region's guest list — so GC knows  │
│              │  who to inform before the region moves"   │
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ G1GC → ZGC → GC Tuning                    │
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** G1GC's Remembered Set has three granularity levels (sparse, fine-grained, coarse-grained) that adapt automatically based on reference density. Describe a concrete application architecture pattern that would cause a single frequently-accessed region to transition from sparse to coarse-grained, explain the exact threshold conditions in G1's RSet implementation that trigger each transition, and quantify the GC pause impact of a coarse-grained RSet vs. a sparse one for a region that is collected once every 500ms.

**Q2.** Java 21 introduces Generational ZGC (experimental) which adds generational tracking to ZGC. ZGC has historically not needed Remembered Sets because it uses load barriers and colored pointers. Explain what new tracking problem Generational ZGC introduces (that standard ZGC avoids), and describe the data structure Generational ZGC uses instead of traditional RSets — specifically focusing on how colored pointer bits can encode generational membership in a way that reduces Remembered Set overhead compared to G1GC's approach.

