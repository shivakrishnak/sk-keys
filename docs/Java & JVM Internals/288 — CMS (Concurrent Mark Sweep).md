---
layout: default
title: "CMS (Concurrent Mark Sweep)"
parent: "Java & JVM Internals"
nav_order: 288
permalink: /java/cms-concurrent-mark-sweep/
number: "0288"
category: Java & JVM Internals
difficulty: ★★★
depends_on:
  - Old Generation
  - Minor GC
  - Stop-The-World (STW)
  - GC Roots
  - Parallel GC
used_by:
  - GC Tuning
  - GC Logs
  - GC Pause
  - Throughput vs Latency (GC)
related:
  - G1GC
  - Parallel GC
  - Serial GC
  - Full GC
  - Happens-Before
tags:
  - jvm
  - garbage-collection
  - concurrent
  - java-internals
  - latency
---

# 0288 — CMS (Concurrent Mark Sweep)

## 1. TL;DR
> **CMS (Concurrent Mark Sweep)** was the first JVM collector to perform most of Old Generation collection **concurrently** with application threads, dramatically reducing Old Gen STW pauses. However, it was deprecated in Java 9 and removed in Java 14 due to complexity and known failure modes (fragmentation, concurrent mode failure). G1GC is its replacement.

---

## 2. Visual: How It Fits In

```
CMS Old Generation Collection Phases:

App:   ────────────┤PAUSE 1├────────────────────────────────┤PAUSE 2├──────
GC:                ─────────[──Concurrent Mark──][──Conc. Sweep──]─────────
                      ▲                                              ▲
               Initial Mark (STW)                           Final Remark (STW)
               (< 10ms typical)                             (50-200ms typical)

Key: most work (concurrent mark + sweep) happens while app runs
Young Gen still uses same Minor GC (STW) as Parallel GC
No compaction → fragmentation over time → can trigger concurrent mode failure
```

---

## 3. Core Concept

CMS breaks Old Generation collection into phases:

1. **Initial Mark (STW):** Briefly stop app threads; identify GC Roots and objects directly reachable from roots
2. **Concurrent Mark (no STW):** Walk the object graph concurrently with app threads
3. **Concurrent Preclean (no STW):** Handle mutations since concurrent mark
4. **Final Remark (STW):** Catch any remaining mutations from concurrent phases
5. **Concurrent Sweep (no STW):** Reclaim dead objects; no compaction
6. **Concurrent Reset:** Reset data structures for next cycle

**Critical Design Choice: No Compaction**
CMS does NOT compact the Old Gen. Dead objects are freed in place, creating free lists. Over time, heap fragmentation increases. If a large allocation fails despite enough total free space (fragmentation), CMS must fall back to a **serial Full GC** — the "concurrent mode failure."

---

## 4. Why It Matters

CMS proved that concurrent GC was viable and paved the way for G1GC and ZGC. It also introduced key concepts:
- **Incremental marking** — tracking heap mutations during concurrent phases
- **Write barriers** — capturing reference changes while GC runs
- **Concurrency vs pause trade-off** — reduced pauses at the cost of throughput and complexity

CMS's failure mode (concurrent mode failure → serial Full GC) is a critical interview topic and a real production pitfall.

---

## 5. Key Properties / Behavior Table

| Property | Value |
|----------|-------|
| Young Gen | Same as Parallel GC (STW, Parallel) |
| Old Gen phases | 6 phases; most concurrent |
| STW pauses | Initial Mark + Final Remark (~50–200ms) |
| Compaction | ❌ None (free-list based) |
| Fragmentation | Yes — grows over time |
| Failure mode | Concurrent Mode Failure → serial Full GC |
| JVM flag | `-XX:+UseConcMarkSweepGC` |
| Available in | Java 5–13 (deprecated in 9, removed in 14) |
| Heap size | Works well up to ~8 GB |
| Best for | Latency-sensitive apps that can't use G1 (pre-Java 9) |

---

## 6. Real-World Analogy

> Imagine the office now has a cleaner who tidies up WHILE people are still working (Concurrent Mark), only briefly asking everyone to freeze momentarily at the start (Initial Mark) and end (Final Remark) of the tidy. However, the cleaner never reorganizes the filing system (no compaction) — they just remove files and leave gaps. Over months, the filing cabinet has lots of empty holes scattered around. Eventually, a new oversized document can't fit in any gap despite plenty of total free space (fragmentation → concurrent mode failure), forcing a complete shutdown for a full reorganization anyway.

---

## 7. How It Works — Step by Step

```
Phase 1: Initial Mark (STW ~few ms)
  - Stop all app threads briefly
  - Mark objects directly reachable from GC Roots
  - These are the "starting points" for concurrent marking
  - Resume threads

Phase 2: Concurrent Mark (no STW, ~seconds)
  - GC thread traverses object graph from Initial Mark results
  - App threads continue mutating heap concurrently
  - Write barriers capture reference changes during this phase
  - Tri-color marking: white (unvisited), gray (in-progress), black (done)

Phase 3: Concurrent Preclean (no STW)
  - Re-scan cards dirtied by write barriers during Phase 2
  - Helps reduce Final Remark pause

Phase 4: Final Remark (STW ~50-200ms)
  - Stop all app threads
  - Finalize marking: scan any remaining dirty cards
  - Handle reference processing (soft/weak/phantom refs)
  - Resume threads

Phase 5: Concurrent Sweep (no STW, ~seconds)
  - Walk heap; reclaim dead objects
  - Build free lists (not compact — holes remain)
  - App threads continue allocating during sweep

Phase 6: Concurrent Reset (no STW)
  - Reset internal CMS data structures
  - Prepare for next CMS cycle
```

---

## 8. Under the Hood (Deep Dive)

### Concurrent Mode Failure

```
Normal CMS cycle:
  Old Gen: 40% → concurrent marking/sweep → 20%

Failure scenario:
  - Old Gen fills up AS concurrent marking is happening
  - Promotions from Young Gen fill remaining Old Gen space
  - CMS can't keep up → OLD GEN FULL during concurrent mark

Result: "concurrent mode failure"
  → CMS abandons concurrent cycle
  → Falls back to SERIAL single-threaded Full GC (STW, minutes!)
  
Prevention:
  -XX:CMSInitiatingOccupancyFraction=70  (start CMS when 70% full)
  -XX:+UseCMSInitiatingOccupancyOnly     (don't auto-tune this value)
  → Start CMS early enough that it finishes before Old Gen fills
```

### Fragmentation problem

```
After many CMS cycles without compaction:
╔══════╦══╦════════╦══╦══════════════╦══╗
║ LIVE ║▓▓║  LIVE  ║▓▓║     LIVE     ║▓▓║  Old Gen
╚══════╩══╩════════╩══╩══════════════╩══╝
         ▲   free    ▲   free             ← many small holes

Large object allocation (e.g., 1 MB array):
- Total free: 5 MB, but no contiguous 1 MB block
- Allocation fails → concurrent mode failure → serial Full GC

Mitigation: -XX:+CMSFullGCsBeforeCompaction=N
(Compact after N Full GCs — but Full GC is still a long STW)
```

### Write barriers in CMS

```
Problem: What if app thread changes reference DURING concurrent mark?
  Object A (black/done) → points to B → app changes A to point to C
  Now C was never visited by GC → C incorrectly reclaimed as garbage!

Solution: Card Table + Write Barrier
  - Heap divided into 512-byte "cards"
  - Write barrier: when Java code writes a reference field,
    the containing card is marked "dirty"
  - Final Remark re-scans all dirty cards to catch these changes
  
Performance cost:
  - Every reference write has a small overhead (write barrier)
  - Final Remark STW duration ∝ number of dirty cards
```

### Key tuning flags

```bash
-XX:+UseConcMarkSweepGC              # Enable CMS (removed Java 14+)
-XX:CMSInitiatingOccupancyFraction=70 # Start CMS when Old Gen is 70% full  
-XX:+UseCMSInitiatingOccupancyOnly   # Don't override occupancy fraction
-XX:ConcGCThreads=N                  # Concurrent GC thread count
-XX:ParallelCMSThreads=N             # STW phase thread count
-XX:+CMSScavengeBeforeRemark         # Do Minor GC before Final Remark
-XX:CMSFullGCsBeforeCompaction=N     # Compact after N Full GCs
```

---

## 9. Comparison Table

| Feature | CMS | G1GC | ZGC |
|---------|-----|------|-----|
| Old Gen concurrent? | Yes | Yes | Yes |
| Compaction | ❌ No | ✅ Yes | ✅ Yes |
| Fragmentation risk | High (long-running) | Low | Very low |
| STW pauses | Initial+Final remark | Evacuation | < 1ms |
| Failure mode | Concurrent mode failure | Evacuation failure | Rare |
| Status | Removed (Java 14) | Default (Java 9+) | Opt-in |
| Heap size | Up to ~8 GB | Up to 32 GB+ | Up to 16 TB |

---

## 10. When to Use / Avoid

| Scenario | Guidance |
|----------|----------|
| Java 8 legacy apps | CMS was common; plan migration to G1 |
| Java 9+ | ❌ Deprecated; use G1GC |
| Java 14+ | ❌ CMS removed; must use other collectors |
| Understanding GC history | ✅ Learn CMS to understand G1/ZGC design |

---

## 11. Common Pitfalls & Mistakes

```
❌ Not setting CMSInitiatingOccupancyFraction
   → JVM auto-tunes; may start CMS too late → concurrent mode failure

❌ Running CMS on Java 14+ 
   → CMSFlags are ignored; G1 is used by default

❌ Ignoring "ConcurrentModeFailure" in GC logs
   → Each failure = serial Full GC = application freeze

❌ Expecting CMS to compact Old Gen
   → CMS never compacts; only Full GC compacts (as fallback)

❌ Heavy use of soft/weak references with CMS
   → Reference processing in Final Remark can extend STW significantly
```

---

## 12. Code / Config Examples

```bash
# Java 8 CMS configuration (historical reference)
java \
  -XX:+UseConcMarkSweepGC \
  -XX:+CMSParallelRemarkEnabled \
  -XX:CMSInitiatingOccupancyFraction=70 \
  -XX:+UseCMSInitiatingOccupancyOnly \
  -XX:ConcGCThreads=4 \
  -XX:+CMSScavengeBeforeRemark \
  -Xms4g -Xmx8g \
  -Xlog:gc*:file=cms.log:time,uptime \
  -jar app.jar

# Detect concurrent mode failures in logs:
# [GC (Allocation Failure) [CMS: (concurrent mode failure)...]
# This means CMS failed → serial Full GC was triggered

# Migration from CMS to G1 (Java 9+):
# Replace: -XX:+UseConcMarkSweepGC
# With:    -XX:+UseG1GC -XX:MaxGCPauseMillis=200
```

---

## 13. Interview Q&A

**Q: What is CMS and why was it deprecated?**
> CMS was a low-pause GC that performed most Old Generation collection concurrently with application threads. It was deprecated in Java 9 and removed in Java 14 due to inherent design flaws: lack of compaction causing fragmentation, concurrent mode failure fallback to serial Full GC, high complexity, and difficulty maintaining. G1GC provides better guarantees with less complexity.

**Q: What is a "concurrent mode failure" in CMS?**
> It occurs when CMS cannot complete the concurrent marking/sweep cycle before the Old Generation fills up with promoted objects. CMS abandons the concurrent cycle and falls back to a single-threaded, fully Stop-The-World serial Full GC — the exact scenario CMS was designed to prevent.

**Q: How does CMS handle reference mutations during concurrent marking?**
> Via a write barrier and card table. When application code writes a reference field, the containing card (512-byte heap region) is marked "dirty." The Final Remark STW phase re-scans all dirty cards to ensure no live objects were missed during concurrent marking.

**Q: Why doesn't CMS compact the Old Generation?**
> Compacting requires moving objects, which temporarily invalidates all references to those objects. During a concurrent phase where application threads still run and use references, this is unsafe without extraordinarily complex reference tracking. CMS chose the simpler approach of free-list management, accepting fragmentation as a tradeoff.

---

## 14. Flash Cards

| Front | Back |
|-------|------|
| How many phases does CMS use? | 6 (Initial Mark, Concurrent Mark, Preclean, Final Remark, Concurrent Sweep, Reset) |
| Which CMS phases are STW? | Initial Mark and Final Remark |
| Does CMS compact Old Gen? | No — uses free lists; no compaction |
| What is concurrent mode failure? | Old Gen fills during concurrent marking → falls back to serial Full GC |
| Why was CMS deprecated? | Fragmentation, concurrent mode failure, complexity; removed Java 14 |

---

## 15. Quick Quiz

**Question 1:** What causes a "concurrent mode failure" in CMS?

- A) CMS GC thread crashes
- B) ✅ Old Gen fills up before CMS concurrent cycle completes
- C) Minor GC cannot promote to Old Gen
- D) JVM exceeds Metaspace limit

**Question 2:** Which of these is TRUE about CMS?

- A) CMS compacts Old Gen after every cycle
- B) CMS is available in Java 21
- C) ✅ CMS performs concurrent Mark and Sweep but STW on Initial and Final Remark
- D) CMS uses a single GC thread

---

## 16. Anti-Patterns

```
🚫 Anti-Pattern: Using CMS in Java 9+ without explicit enablement
   Problem:  Flag ignored silently; G1 runs instead
   Fix:      Remove CMS flags; explicitly configure G1

🚫 Anti-Pattern: Ignoring fragmentation metrics
   Problem:  CMS runs fine for weeks, then sudden long Full GC pauses
   Fix:      Monitor Old Gen fragmentation; plan GC migration

🚫 Anti-Pattern: Not monitoring for concurrent mode failures
   Problem:  Silent serial Full GC pauses kill latency SLAs
   Fix:      Alert on "ConcurrentModeFailure" in GC logs
```

---

## 17. Related Concepts Map

```
CMS
├── collects ────────► Old Generation [#281]
├── uses ────────────► Write Barrier (card table)
├── requires STW for ► Initial Mark + Final Remark
├── failure mode ────► Full GC [#284] (serial fallback)
├── replaced by ─────► G1GC [#289]
│                  ──► ZGC [#290]
├── similar to ──────► Parallel GC [#287] (for Young Gen)
└── concept seeds ───► Concurrent marking → G1, ZGC, Shenandoah
```

---

## 18. Further Reading

- [Oracle: CMS Collector](https://docs.oracle.com/javase/8/docs/technotes/guides/vm/gctuning/cms.html) (Java 8 docs)
- [JEP 291: Deprecate CMS GC](https://openjdk.org/jeps/291)
- [JEP 363: Remove CMS GC](https://openjdk.org/jeps/363)
- [Understanding Concurrent Mode Failure](https://blog.gceasy.io/2019/06/what-is-cms-concurrent-mode-failure/)

---

## 19. Human Summary

CMS was revolutionary when it launched — it proved you could run GC concurrently with the application and dramatically reduce pauses. Its two-phase STW design (Initial Mark + Final Remark sandwiching concurrent work) became the template for all subsequent concurrent collectors.

But CMS carried a fatal flaw: no compaction. Every GC leaves holes in the Old Generation. Run a busy app for hours, and the Old Gen looks like Swiss cheese — plenty of total free space, but no large contiguous block for big allocations. When that allocation fails, CMS crashes back to a serial Full GC that can pause for minutes. This is why G1GC (and later ZGC) were built: same concurrent marking concept, but with regional memory management and proper compaction.

If you're still running Java 8 with CMS, your top priority should be migrating to G1GC.

---

## 20. Tags

`jvm` `garbage-collection` `concurrent` `java-internals` `latency` `cms` `old-generation`

