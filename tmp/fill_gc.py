#!/usr/bin/env python3
"""Fill TODO sections for Java - Garbage Collection.md (4 keywords)."""
import re

FILE = "interview/java/Java - Garbage Collection.md"

KEYWORDS = [
    "GC Algorithms",
    "G1 Garbage Collector",
    "ZGC",
    "GC Tuning",
]

# ── Level 5 ──────────────────────────────────────────────

LEVEL5 = {
    "GC Algorithms": (
        "GC algorithm design embodies a universal engineering "
        "trade-off triangle: throughput vs latency vs memory "
        "footprint. You can optimize any two at the expense of "
        "the third. This same triangle appears in database "
        "indexes (write throughput vs read latency vs storage), "
        "network protocols (bandwidth vs latency vs reliability), "
        "and distributed consensus (consistency vs availability "
        "vs partition tolerance). The expert insight: all GC "
        "algorithms are variations of mark-sweep, mark-compact, "
        "or copying collection - combined with generational "
        "hypothesis optimizations. The generational hypothesis "
        "(most objects die young) is the single most impactful "
        "observation in GC design, enabling 10x throughput "
        "improvements by focusing collection on the young "
        "generation. If redesigning today, you would build "
        "concurrent, region-based collectors from the start "
        "(like ZGC) with automatic tuning via ML-based "
        "heuristics that adapt to workload changes in "
        "real-time.\n\n"
        "**Expert thinking cues:**\n"
        "- \"What's the pause time budget?\" - this determines "
        "the algorithm family\n"
        "- \"Is the generational hypothesis holding?\" - if not "
        "(long-lived caches), generational GC hurts\n"
        "- \"What percentage of CPU can GC consume?\" - concurrent "
        "collectors trade CPU for lower pauses"
    ),
    "G1 Garbage Collector": (
        "G1's region-based design is the JVM equivalent of "
        "database sharding: instead of one large heap to manage, "
        "it breaks the heap into hundreds of equal-sized regions "
        "that can be independently collected. This same approach "
        "appears in SSD firmware (block-based garbage collection), "
        "operating systems (page-based memory management), and "
        "distributed storage (chunk-based replication). The "
        "expert insight: G1's 'Garbage-First' name reveals its "
        "core heuristic - it always collects the region with "
        "the most garbage first, maximizing space reclaimed per "
        "unit of pause time. The remembered sets (RSets) that "
        "track cross-region references consume 5-20% of heap, "
        "which is the hidden cost of region independence. If "
        "redesigning today, you would use load barriers instead "
        "of remembered sets (as ZGC does) to eliminate the "
        "memory overhead at the cost of slight per-reference "
        "CPU overhead.\n\n"
        "**Expert thinking cues:**\n"
        "- \"How many regions are in the collection set?\" - more "
        "regions = longer pause but more space reclaimed\n"
        "- \"Is the RSet overhead acceptable?\" - >20% of heap "
        "in RSets signals too many cross-region references\n"
        "- \"Are mixed collections keeping up?\" - if old gen "
        "grows continuously, collection can't keep pace"
    ),
    "ZGC": (
        "ZGC represents the theoretical endpoint of concurrent "
        "GC design: sub-millisecond pauses regardless of heap "
        "size (tested up to 16TB). It achieves this through "
        "colored pointers (metadata stored in unused pointer "
        "bits) and load barriers (code injected at every heap "
        "reference load). This same colored-pointer technique "
        "appears in tagged architectures (SPARC, ARM MTE for "
        "memory safety), and the load-barrier concept maps to "
        "copy-on-write in OS virtual memory. The expert insight: "
        "ZGC's O(1) pause times (independent of heap/live-set "
        "size) fundamentally changes capacity planning - you can "
        "over-provision heap without pause time penalty. Since "
        "JDK 21, Generational ZGC adds young/old separation, "
        "bringing throughput within 5% of G1 while maintaining "
        "sub-ms pauses. If redesigning today, Generational ZGC "
        "would be the default collector for all workloads.\n\n"
        "**Expert thinking cues:**\n"
        "- \"Is heap size the bottleneck?\" - ZGC lets you use "
        "huge heaps without pause penalty\n"
        "- \"Are we on JDK 21+?\" - Generational ZGC closes the "
        "throughput gap with G1\n"
        "- \"What's the pointer width?\" - ZGC uses 64-bit "
        "pointers only, no compressed oops on <32GB heaps"
    ),
    "GC Tuning": (
        "GC tuning follows the universal performance optimization "
        "principle: measure first, hypothesize second, change one "
        "variable at a time, and verify. This same methodology "
        "appears in database query tuning (EXPLAIN before index), "
        "network optimization (packet capture before firewall "
        "rules), and compiler optimization (profile-guided before "
        "manual). The expert insight: 90% of GC tuning is choosing "
        "the right collector and sizing the heap correctly. The "
        "remaining 10% is fine-tuning specific flags, which has "
        "rapidly diminishing returns and creates fragile configs. "
        "The three most impactful parameters across all collectors "
        "are: `-Xmx/-Xms` (heap size), `-XX:MaxGCPauseMillis` "
        "(pause target), and `-XX:NewRatio` (generational sizing). "
        "If redesigning today, you would build auto-tuning into "
        "the collector that adapts in real-time based on "
        "application behavior (G1 already does this partially "
        "with adaptive IHOP).\n\n"
        "**Expert thinking cues:**\n"
        "- \"What did the GC logs say before tuning?\" - never "
        "tune without baseline data\n"
        "- \"How many flags were changed?\" - >5 GC flags is a "
        "code smell for over-tuning\n"
        "- \"Is the workload stable?\" - tuning for a specific "
        "load pattern breaks when load changes"
    ),
}

# ── Quick Reference Card ─────────────────────────────────

QUICKREF = {
    "GC Algorithms": (
        "**WHAT IT IS:** Automatic memory reclamation strategies "
        "that find and free unreachable objects on the JVM heap\n"
        "**PROBLEM IT SOLVES:** Eliminates manual memory "
        "management (malloc/free) and its bugs: leaks, "
        "use-after-free, double-free\n"
        "**KEY INSIGHT:** All GC is mark-sweep, mark-compact, or "
        "copying - combined with generational hypothesis "
        "optimizations\n"
        "**USE WHEN:** Every Java application uses GC. Choice of "
        "algorithm depends on throughput vs latency requirements\n"
        "**AVOID WHEN:** N/A - GC is mandatory. But avoid wrong "
        "algorithm for workload (e.g., Parallel for latency-"
        "sensitive)\n"
        "**ANTI-PATTERN:** Calling `System.gc()` to force "
        "collection - undermines GC heuristics and causes full "
        "STW pauses\n"
        "**TRADE-OFF:** Throughput (Parallel) vs latency (ZGC) vs "
        "memory footprint (Serial) - pick two\n"
        "**ONE-LINER:** \"GC trades CPU cycles for memory safety, "
        "and the algorithm choice determines the cost "
        "distribution\""
    ),
    "G1 Garbage Collector": (
        "**WHAT IT IS:** Region-based, concurrent, generational "
        "GC that targets configurable pause times (default since "
        "JDK 9)\n"
        "**PROBLEM IT SOLVES:** Balances throughput and latency "
        "for general-purpose workloads with predictable pause "
        "targets\n"
        "**KEY INSIGHT:** Heap is divided into equal-sized regions. "
        "G1 collects the regions with the most garbage first "
        "(Garbage-First)\n"
        "**USE WHEN:** General-purpose applications, 4GB+ heaps, "
        "need predictable pauses without extreme latency "
        "requirements\n"
        "**AVOID WHEN:** Ultra-low latency (<10ms p99) - use ZGC. "
        "Maximum throughput batch jobs - use Parallel GC\n"
        "**ANTI-PATTERN:** Setting `-XX:MaxGCPauseMillis` to "
        "unrealistically low values - G1 can't meet them and "
        "thrashes\n"
        "**TRADE-OFF:** Remembered sets consume 5-20% of heap "
        "memory for cross-region reference tracking\n"
        "**ONE-LINER:** \"G1 breaks the heap into regions and "
        "always collects the most garbage-filled regions first\""
    ),
    "ZGC": (
        "**WHAT IT IS:** Ultra-low latency concurrent GC with "
        "sub-millisecond pauses regardless of heap size (up to "
        "16TB)\n"
        "**PROBLEM IT SOLVES:** Eliminates GC-induced latency "
        "spikes for latency-sensitive applications (APIs, "
        "trading, gaming)\n"
        "**KEY INSIGHT:** Colored pointers + load barriers enable "
        "concurrent relocation without stopping application "
        "threads\n"
        "**USE WHEN:** Latency-critical services, large heaps "
        "(>32GB), applications where p99 latency matters more "
        "than throughput\n"
        "**AVOID WHEN:** JDK <15 (experimental). Memory-"
        "constrained environments (no compressed oops). Maximum "
        "throughput batch\n"
        "**ANTI-PATTERN:** Using ZGC on JDK 11-14 in production "
        "- it was experimental and lacked key optimizations\n"
        "**TRADE-OFF:** No compressed oops = 1.5x memory for "
        "references on heaps <32GB. Higher CPU for load barriers\n"
        "**ONE-LINER:** \"ZGC achieves O(1) pause times by doing "
        "all heavy lifting concurrently with application threads\""
    ),
    "GC Tuning": (
        "**WHAT IT IS:** The practice of configuring JVM garbage "
        "collector settings to optimize for specific workload "
        "requirements\n"
        "**PROBLEM IT SOLVES:** Default GC settings may not match "
        "application needs - wrong settings cause latency spikes "
        "or throughput loss\n"
        "**KEY INSIGHT:** 90% of GC tuning is choosing the right "
        "collector and sizing the heap. Over-tuning creates "
        "fragile configs\n"
        "**USE WHEN:** GC pauses exceed SLA, throughput is below "
        "target, OOM errors, or during capacity planning\n"
        "**AVOID WHEN:** Before measuring baseline. Before "
        "understanding the workload. Premature optimization "
        "without data\n"
        "**ANTI-PATTERN:** Tuning 50+ GC flags without "
        "understanding workload - creates non-portable, fragile "
        "configurations\n"
        "**TRADE-OFF:** More tuning = better fit for current "
        "workload but fragile to workload changes\n"
        "**ONE-LINER:** \"Measure with GC logs, choose the right "
        "collector, size the heap, then stop tuning\""
    ),
}

# ── Comparison Table ─────────────────────────────────────

COMPARISON = {
    "GC Algorithms": (
        "| Algorithm | Type | Pause Model | "
        "Best For |\n"
        "|-----------|------|-------------|"
        "---------|\n"
        "| Serial | Copying + Mark-Compact | Full STW | "
        "Small heaps, single-core |\n"
        "| Parallel | Copying + Mark-Compact | Full STW | "
        "Max throughput, batch |\n"
        "| G1 | Region + Concurrent | Partial STW | "
        "General purpose, balanced |\n"
        "| ZGC | Concurrent + Load barriers | Sub-ms STW | "
        "Ultra-low latency |\n"
        "| Shenandoah | Concurrent + Brooks ptrs | Sub-ms STW | "
        "Low latency (OpenJDK) |"
    ),
    "G1 Garbage Collector": (
        "| Aspect | G1 | Parallel | "
        "ZGC |\n"
        "|--------|----|---------|-"
        "----|\n"
        "| Pause model | Incremental mixed | Full STW | "
        "Sub-ms concurrent |\n"
        "| Heap layout | Regions (1-32MB) | Contiguous gens | "
        "Regions (2MB) |\n"
        "| Default | JDK 9+ | JDK 1-8 | No |\n"
        "| Max pause target | Configurable | No | <1ms |\n"
        "| Memory overhead | RSets (5-20%) | Minimal | "
        "No compressed oops |\n"
        "| Best heap size | 4GB-64GB | Any | Any (up to 16TB) |"
    ),
    "ZGC": (
        "| Feature | ZGC | G1 | "
        "Shenandoah |\n"
        "|---------|-----|----|"
        "------------|\n"
        "| Max pause | <1ms | 200ms target | <10ms |\n"
        "| Concurrent relocation | Yes (load barriers) | "
        "No (STW) | Yes (Brooks pointers) |\n"
        "| Compressed oops | No | Yes | Yes |\n"
        "| Generational (JDK 21+) | Yes | Yes | No |\n"
        "| Max tested heap | 16TB | ~256GB | ~2TB |\n"
        "| JDK production-ready | JDK 15+ | JDK 9+ | "
        "JDK 15+ |"
    ),
    "GC Tuning": (
        "| Approach | Flags Changed | Effort | "
        "Risk |\n"
        "|----------|--------------|--------|"
        "------|\n"
        "| Default settings | 0 | None | "
        "None |\n"
        "| Collector + heap sizing | 2-3 | Low | "
        "Low |\n"
        "| Generation sizing | 3-5 | Medium | "
        "Medium |\n"
        "| Full flag tuning | 10-50 | High | "
        "High (fragile) |\n"
        "| Auto-tuning (G1 ergonomics) | 1 target | Low | "
        "Low |"
    ),
}

# ── Misconceptions ───────────────────────────────────────

MISCONCEPTIONS = {
    "GC Algorithms": [
        ("GC eliminates all memory leaks",
         "GC only collects unreachable objects. If code holds "
         "references to objects no longer needed (listeners, "
         "caches, static collections), they are reachable and "
         "never collected - this is a memory leak."),
        ("More heap always improves GC performance",
         "Larger heap means more live data to scan during full GC. "
         "Doubling heap can double full GC pause time. Right-size "
         "the heap to 2-4x live data set."),
        ("Concurrent GC means no pauses",
         "All JVM GCs have SOME stop-the-world pauses (root "
         "scanning, final marking). Concurrent collectors "
         "minimize pause duration but never eliminate it "
         "entirely."),
        ("GC overhead is always significant",
         "Modern GC typically consumes 1-5% of CPU. For most "
         "applications, GC overhead is negligible compared to "
         "IO, network, and business logic."),
    ],
    "G1 Garbage Collector": [
        ("G1 always meets MaxGCPauseMillis target",
         "MaxGCPauseMillis is a soft target, not a guarantee. "
         "G1 adjusts collection work per cycle to approach "
         "the target but can exceed it during evacuation "
         "failures or humongous allocations."),
        ("G1 doesn't do full GC",
         "G1 can fall back to a full, single-threaded STW "
         "collection if concurrent marking can't keep up with "
         "allocation rate. Full GCs in G1 are a serious "
         "performance problem."),
        ("Region size doesn't matter",
         "Region size (1-32MB, auto-calculated) determines the "
         "humongous object threshold (>50% of region). Wrong "
         "region size causes excessive humongous allocations "
         "that bypass normal collection."),
        ("G1 is always better than Parallel GC",
         "For pure throughput workloads (batch processing, "
         "offline analytics), Parallel GC can deliver 5-15% "
         "higher throughput because it has lower per-object "
         "overhead (no RSets, no barriers)."),
    ],
    "ZGC": [
        ("ZGC has no pauses at all",
         "ZGC has brief STW pauses (<1ms) for root scanning "
         "and thread handshakes. It's sub-millisecond, not "
         "pauseless."),
        ("ZGC is only for huge heaps",
         "ZGC works on any heap size. Since JDK 21 with "
         "generational mode, it's competitive with G1 even "
         "on 2-4GB heaps."),
        ("ZGC always uses more memory than G1",
         "ZGC lacks compressed oops, using 8 bytes per reference "
         "vs 4 bytes. But it doesn't need remembered sets "
         "(5-20% of heap in G1). Net overhead depends on "
         "workload."),
        ("ZGC can't match G1 throughput",
         "Generational ZGC (JDK 21+) achieves throughput within "
         "5% of G1 for most workloads. The throughput gap that "
         "existed in early ZGC versions is largely closed."),
    ],
    "GC Tuning": [
        ("More GC flags = better performance",
         "Over-tuning creates configurations that are optimal "
         "for one specific load pattern but break when load "
         "changes. 2-3 flags is usually sufficient."),
        ("GC tuning should come first in optimization",
         "GC tuning should come LAST. First: fix algorithmic "
         "issues, reduce allocation rate, fix memory leaks. "
         "GC tuning can't compensate for application problems."),
        ("-Xmx and -Xms should be different",
         "For production services, set -Xmx = -Xms. Different "
         "values cause heap resizing pauses and make GC behavior "
         "less predictable."),
        ("System.gc() is a valid tuning technique",
         "System.gc() triggers an uncontrolled full GC that "
         "ignores all tuning flags. It bypasses GC ergonomics "
         "and should almost never be used."),
    ],
}

# ── Failure Modes ────────────────────────────────────────

FAILURES = {
    "GC Algorithms": r"""**Failure Mode 1: Premature promotion (premature tenuring)**
**Symptom:** Old generation fills rapidly. Frequent mixed or full GC cycles. High promotion rate in GC logs.
**Root Cause:** Survivor spaces too small, causing objects to be promoted to old gen before they die. Survivor age threshold too low.
**Diagnostic:**

```
# Check promotion rate and tenuring threshold
jstat -gcutil <pid> 1000
# Look at S0/S1 utilization and O (old gen)
# GC log: -Xlog:gc*,gc+age=debug
```

**Fix:**
```java
// BAD: default survivor sizing may be wrong
// Objects promoted after 1-2 GC cycles

// GOOD: increase survivor space and threshold
// -XX:SurvivorRatio=6 (larger survivors)
// -XX:MaxTenuringThreshold=15
// -XX:+PrintTenuringDistribution (to verify)
```
**Prevention:** Monitor tenuring distribution in GC logs. Size survivors to hold objects that die within 2-5 GC cycles.

**Failure Mode 2: Full GC caused by Metaspace exhaustion**
**Symptom:** Full GC triggered despite heap having free space. GC log shows "Metadata GC Threshold" as cause.
**Root Cause:** Metaspace (class metadata) fills up, triggering full GC to attempt class unloading. Common with heavy reflection, dynamic proxies, or classloader leaks.
**Diagnostic:**

```
jstat -gcmetacapacity <pid>
# Check MCMX (Metaspace max) vs MCMN (used)
jcmd <pid> VM.classloader_stats
```

**Fix:**
```java
// BAD: default MetaspaceSize is too small
// for applications with many classes

// GOOD: size Metaspace appropriately
// -XX:MetaspaceSize=256m
// -XX:MaxMetaspaceSize=512m
// Monitor with JMX: java.lang:type=MemoryPool,
// name=Metaspace
```
**Prevention:** Set `-XX:MetaspaceSize` and `-XX:MaxMetaspaceSize` explicitly. Monitor classloader count for leaks.

**Failure Mode 3: GC thrashing (continuous full GC)**
**Symptom:** Application nearly stops. GC consumes >90% of CPU. `GCTimeRatio` or `GCOverheadLimit` exceeded.
**Root Cause:** Heap is nearly full of live data. GC runs continuously but can barely reclaim any memory.
**Diagnostic:**

```
jstat -gcutil <pid> 1000
# O (old gen) consistently >95%
# GCT (GC time) growing rapidly
# Application: OutOfMemoryError: GC overhead limit
```

**Fix:**
```java
// 1. Immediate: increase heap
// -Xmx (double current value)
// 2. Root cause: find memory leak
// jmap -histo:live <pid> | head -20
// jmap -dump:live,format=b,file=heap.hprof <pid>
// 3. Analyze with Eclipse MAT or VisualVM
```
**Prevention:** Monitor old gen utilization. Alert at 80%. Set `-XX:+HeapDumpOnOutOfMemoryError`. Profile memory usage in staging.""",

    "G1 Garbage Collector": r"""**Failure Mode 1: Humongous allocation fragmentation**
**Symptom:** Unexpected full GCs despite low heap utilization. GC log shows "G1 Humongous Allocation" events.
**Root Cause:** Objects >50% of G1 region size are "humongous" - allocated directly in old gen, spanning multiple contiguous regions. They cause fragmentation and are only collected during full GC (before JDK 8u60) or concurrent cycles.
**Diagnostic:**

```
# Count humongous allocations in GC log
grep -c "humongous" gc.log
# Check region size
java -XX:+PrintFlagsFinal -version | grep G1HeapRegionSize
# Objects > regionSize/2 are humongous
```

**Fix:**
```java
// BAD: default region size with large arrays
// byte[] buf = new byte[4 * 1024 * 1024]; // 4MB
// With 4MB regions, this is humongous

// GOOD: increase region size
// -XX:G1HeapRegionSize=16m
// Or: reduce allocation size
// Use pooled buffers for large arrays
ByteBuffer buf = ByteBuffer.allocateDirect(4_000_000);
```
**Prevention:** Size G1HeapRegionSize so common allocations are <50% of region. Monitor humongous allocation count in GC logs.

**Failure Mode 2: Mixed collection evacuation failure**
**Symptom:** G1 falls back to full GC. GC log shows "to-space exhausted" or "evacuation failure".
**Root Cause:** Not enough free regions to copy live objects during mixed collection. G1 can't complete evacuation and falls back to single-threaded full compaction.
**Diagnostic:**

```
grep -i "evacuation failure\|to-space exhausted" gc.log
# Also check: IHOP (Initiating Heap Occupancy Percent)
grep "Initiate" gc.log
```

**Fix:**
```java
// BAD: IHOP too high, marking starts too late
// Allocation rate > collection rate

// GOOD: trigger marking earlier
// -XX:InitiatingHeapOccupancyPercent=35
// (default 45, lower = earlier marking)
// Increase heap: -Xmx (more breathing room)
// Set -Xms = -Xmx (prevent resizing)
```
**Prevention:** Monitor IHOP and adjust. Keep 20-30% headroom. Set `-XX:-G1UseAdaptiveIHOP` if adaptive IHOP is not converging.

**Failure Mode 3: RSet memory overhead too high**
**Symptom:** Effective heap is 15-25% smaller than -Xmx. GC spends significant time maintaining remembered sets.
**Root Cause:** Many cross-region references (e.g., large interconnected object graphs) cause RSets to consume substantial memory.
**Diagnostic:**

```
# Enable RSet statistics
# -Xlog:gc+remset*=debug
# Look for RSet memory usage in output
jcmd <pid> GC.heap_info
```

**Fix:**
```java
// Reduce cross-region references:
// 1. Co-locate related objects (improve locality)
// 2. Increase region size (fewer cross-region refs)
// -XX:G1HeapRegionSize=16m or 32m
// 3. Consider ZGC if RSet overhead is >15%
// ZGC uses load barriers instead of RSets
```
**Prevention:** Profile object graph connectivity. Choose G1HeapRegionSize to minimize cross-region references. Consider ZGC for highly connected graphs.""",

    "ZGC": r"""**Failure Mode 1: Allocation stall despite low pause times**
**Symptom:** Application threads block waiting for GC to reclaim memory. Latency spikes >100ms but GC pauses are <1ms.
**Root Cause:** ZGC's concurrent collection can't keep up with allocation rate. Application threads stall waiting for free pages.
**Diagnostic:**

```
# GC log shows "Allocation Stall" events
grep "Allocation Stall" gc.log
# Check allocation rate
grep "Allocation Rate" gc.log
# jstat shows Eden constantly full
```

**Fix:**
```java
// BAD: heap too small for allocation rate
// ZGC can't complete cycles fast enough

// GOOD: increase heap for concurrent headroom
// -Xmx (3-5x live data set for ZGC)
// ZGC needs more headroom than G1 because
// collection runs concurrently with allocation

// Or: reduce allocation rate in application
// (profile with: asprof -e alloc <pid>)
```
**Prevention:** Size heap to 3-5x live data set for ZGC. Monitor allocation rate vs GC reclamation rate. Alert on allocation stalls.

**Failure Mode 2: No compressed oops increases memory usage**
**Symptom:** Application uses 40-50% more memory than under G1 for the same workload. Heap usage higher than expected.
**Root Cause:** ZGC uses 64-bit object references (no compressed oops). Each reference is 8 bytes instead of 4 bytes. Reference-heavy workloads see significant overhead.
**Diagnostic:**

```
# Compare heap usage G1 vs ZGC
# G1: java -XX:+UseG1GC -Xmx8g -XX:+PrintFlagsFinal
# ZGC: java -XX:+UseZGC -Xmx8g -XX:+PrintFlagsFinal
# Check UseCompressedOops flag (ZGC = false)
jcmd <pid> VM.flags | grep Compressed
```

**Fix:**
```java
// Accept higher memory for lower latency:
// Size heap 1.5x what G1 needs
// -Xmx12g (instead of -Xmx8g with G1)

// Or: reduce reference count
// Use arrays of primitives instead of objects
// Flatten object hierarchies
// Use value types (JDK Valhalla, future)
```
**Prevention:** Plan for 1.5x memory budget vs G1. Profile reference density. Use Generational ZGC (JDK 21+) which partially mitigates through better young-gen collection.

**Failure Mode 3: ZGC on JDK versions before 15**
**Symptom:** Production instability, crashes, or poor performance with ZGC on JDK 11-14.
**Root Cause:** ZGC was experimental before JDK 15. Missing optimizations, known bugs, and incomplete feature set (no class unloading before JDK 12, no uncommit before JDK 13).
**Diagnostic:**

```
java -version
# If JDK < 15, ZGC is experimental
# Check: -XX:+UnlockExperimentalVMOptions required
```

**Fix:**
```java
// BAD: running ZGC on JDK 11 in production
// -XX:+UnlockExperimentalVMOptions -XX:+UseZGC

// GOOD: upgrade to JDK 17+ (LTS) or JDK 21+
// -XX:+UseZGC (no experimental flag needed)
// JDK 21: -XX:+UseZGC -XX:+ZGenerational
// (generational mode for better throughput)
```
**Prevention:** Use ZGC only on JDK 15+ in production. Prefer JDK 21+ for Generational ZGC. Test thoroughly before production deployment.""",

    "GC Tuning": r"""**Failure Mode 1: Over-tuned configuration breaks under workload change**
**Symptom:** Application performs well under normal load but has severe GC pauses during traffic spikes or changed request patterns.
**Root Cause:** GC flags were tuned for a specific load profile. Fixed-size generation splits, explicit GC timing, and disabled ergonomics prevent adaptation.
**Diagnostic:**

```
# Count GC-related flags
java -XX:+PrintFlagsFinal | grep -c "gc\|GC"
# If many were manually set (non-default), over-tuned
jcmd <pid> VM.flags | grep -v "default"
```

**Fix:**
```java
// BAD: 20+ manually set GC flags
// -XX:NewSize=2g -XX:MaxNewSize=2g
// -XX:SurvivorRatio=8 -XX:MaxTenuringThreshold=5
// ... (fragile, non-adaptive)

// GOOD: minimal flags, let GC adapt
// -XX:+UseG1GC -Xmx8g -Xms8g
// -XX:MaxGCPauseMillis=100
// (3 flags, G1 adapts everything else)
```
**Prevention:** Use adaptive GC ergonomics. Set goals (MaxGCPauseMillis) not mechanisms (generation sizes). Test under variable load.

**Failure Mode 2: Heap sized too small for live data set**
**Symptom:** Constant GC activity. Old gen always >90% full. Frequent full GCs. Eventual OOM.
**Root Cause:** -Xmx is less than 2x the live data set. GC runs continuously trying to reclaim the thin sliver of dead objects.
**Diagnostic:**

```
# After full GC, check old gen occupancy
# If post-GC old gen > 60% of -Xmx, heap is too small
jstat -gcold <pid> 1000
# Or from GC log: post-full-GC heap usage
grep "Full" gc.log | tail -5
```

**Fix:**
```java
// BAD: live data set is 3GB, heap is 4GB
// Only 1GB free after full GC = constant GC

// GOOD: set heap to 3-4x live data set
// -Xmx12g -Xms12g
// Post-GC old gen should be 30-40% of -Xmx
```
**Prevention:** Measure live data set after full GC. Set -Xmx to 3-4x live data. Monitor post-GC occupancy.

**Failure Mode 3: GC logs not enabled in production**
**Symptom:** GC problems occur but there's no data to diagnose. Troubleshooting requires reproducing the issue with logging enabled.
**Root Cause:** GC logging was disabled or not configured. Without logs, root cause analysis is guesswork.
**Diagnostic:**

```
# Check if GC logging is enabled
jcmd <pid> VM.flags | grep "Xlog\|PrintGC"
# If empty, no GC logging
```

**Fix:**
```java
// BAD: no GC logging
// java -Xmx8g -jar app.jar

// GOOD: always enable GC logging
// JDK 9+:
// -Xlog:gc*:file=gc.log:time,level,tags:
//   filecount=5,filesize=100m
// JDK 8:
// -XX:+PrintGCDetails -XX:+PrintGCDateStamps
// -Xloggc:gc.log -XX:+UseGCLogFileRotation
```
**Prevention:** Enable GC logging in ALL environments including production. Overhead is negligible (<0.1%). Rotate log files to manage disk.""",
}

# ── Related Keywords ─────────────────────────────────────

RELATED = {
    "GC Algorithms": r"""**Prerequisites (understand these first):**

- JVM Memory Model - heap structure, generations, object lifecycle
- Object allocation and lifecycle - how objects are created, referenced, and become unreachable

**Builds on this (learn these next):**

- G1 Garbage Collector - the default modern GC with region-based design
- ZGC - ultra-low latency concurrent collector for demanding workloads

**Alternatives / Comparisons:**

- Manual memory management (C/C++) - explicit malloc/free, no GC overhead but error-prone
- Reference counting (Python, Swift) - deterministic destruction but circular reference issues""",

    "G1 Garbage Collector": r"""**Prerequisites (understand these first):**

- GC Algorithms - foundational GC concepts (mark, sweep, compact, copy)
- JVM Heap structure - young gen, old gen, Metaspace, and their purposes

**Builds on this (learn these next):**

- GC Tuning - optimizing G1 flags for specific workload characteristics
- ZGC - alternative collector when G1 pause targets are insufficient

**Alternatives / Comparisons:**

- Parallel GC - higher throughput for batch workloads, simpler design, higher pauses
- ZGC - sub-ms pauses regardless of heap size, but higher memory overhead""",

    "ZGC": r"""**Prerequisites (understand these first):**

- GC Algorithms - understand mark-sweep, copying, concurrent collection concepts
- G1 Garbage Collector - the general-purpose baseline to compare against

**Builds on this (learn these next):**

- GC Tuning for ZGC - heap sizing, allocation rate management for ZGC
- Generational ZGC (JDK 21+) - generational mode that improves throughput

**Alternatives / Comparisons:**

- G1 GC - lower memory overhead, proven track record, good enough for most workloads
- Shenandoah - similar goals to ZGC using Brooks pointers instead of colored pointers""",

    "GC Tuning": r"""**Prerequisites (understand these first):**

- GC Algorithms - understand which algorithms exist and their trade-offs
- JVM Profiling Tools - how to collect and analyze GC logs and metrics

**Builds on this (learn these next):**

- Production performance monitoring - integrating GC metrics into observability stack
- Capacity planning - using GC data to right-size infrastructure

**Alternatives / Comparisons:**

- Application-level optimization - reducing allocation rate is often more effective than GC tuning
- Off-heap memory (DirectByteBuffer, Unsafe) - bypass GC entirely for large data sets""",
}


def apply_all(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    changes = 0

    # Level 5
    level5_old = (
        "[TODO: Cross-domain pattern recognition. "
        "Expert heuristics.\n"
        " What would you change if redesigning today?\n"
        " How does this compose at extreme scale?]"
    )
    for kw in KEYWORDS:
        if level5_old in content and kw in LEVEL5:
            content = content.replace(level5_old, LEVEL5[kw], 1)
            changes += 1

    # Quick Reference Card
    qr_old = (
        "**WHAT IT IS:** [TODO]\n"
        "**PROBLEM IT SOLVES:** [TODO]\n"
        "**KEY INSIGHT:** [TODO]\n"
        "**USE WHEN:** [TODO]\n"
        "**AVOID WHEN:** [TODO]\n"
        "**ANTI-PATTERN:** [TODO]\n"
        "**TRADE-OFF:** [TODO]\n"
        "**ONE-LINER:** [TODO]"
    )
    for kw in KEYWORDS:
        if qr_old in content and kw in QUICKREF:
            content = content.replace(qr_old, QUICKREF[kw], 1)
            changes += 1

    # Comparison Table
    for kw in KEYWORDS:
        ct_old = (
            f"[TODO: Include if 2+ named alternatives exist "
            f"for {kw}. Otherwise remove this section.]"
        )
        if ct_old in content and kw in COMPARISON:
            content = content.replace(ct_old, COMPARISON[kw], 1)
            changes += 1

    # Misconceptions
    mc_pat = re.compile(
        r'\| 1\s*\|\s*\[TODO\]\s*\|\s*\[TODO\]\s*\|\n'
        r'\| 2\s*\|\s*\[TODO\]\s*\|\s*\[TODO\]\s*\|\n'
        r'\| 3\s*\|\s*\[TODO\]\s*\|\s*\[TODO\]\s*\|\n'
        r'\| 4\s*\|\s*\[TODO\]\s*\|\s*\[TODO\]\s*\|'
    )
    for kw in KEYWORDS:
        if kw in MISCONCEPTIONS:
            m = mc_pat.search(content)
            if m:
                rows = MISCONCEPTIONS[kw]
                replacement = "\n".join(
                    f"| {i+1} | {mis} | {real} |"
                    for i, (mis, real) in enumerate(rows)
                )
                content = content[:m.start()] + replacement + \
                    content[m.end():]
                changes += 1

    # Failure Modes
    fm_pat = re.compile(
        r'\*\*Failure Mode 1: \[TODO\]\*\*\n'
        r'\*\*Symptom:\*\* \[TODO\]\n'
        r'\*\*Root Cause:\*\* \[TODO\]\n'
        r'\*\*Diagnostic:\*\*\n'
        r'```\n'
        r'\[TODO: real diagnostic command\]\n'
        r'```\n'
        r'\*\*Fix:\*\* \[TODO: BAD then GOOD\]\n'
        r'\*\*Prevention:\*\* \[TODO\]\n'
        r'\n'
        r'\*\*Failure Mode 2: \[TODO\]\*\*\n'
        r'\*\*Symptom:\*\* \[TODO\]\n'
        r'\*\*Root Cause:\*\* \[TODO\]\n'
        r'\*\*Diagnostic:\*\*\n'
        r'```\n'
        r'\[TODO: real diagnostic command\]\n'
        r'```\n'
        r'\*\*Fix:\*\* \[TODO: BAD then GOOD\]\n'
        r'\*\*Prevention:\*\* \[TODO\]\n'
        r'\n'
        r'\*\*Failure Mode 3: \[TODO\]\*\*\n'
        r'\*\*Symptom:\*\* \[TODO\]\n'
        r'\*\*Root Cause:\*\* \[TODO\]\n'
        r'\*\*Diagnostic:\*\*\n'
        r'```\n'
        r'\[TODO: real diagnostic command\]\n'
        r'```\n'
        r'\*\*Fix:\*\* \[TODO: BAD then GOOD\]\n'
        r'\*\*Prevention:\*\* \[TODO\]'
    )
    for kw in KEYWORDS:
        if kw in FAILURES:
            m = fm_pat.search(content)
            if m:
                content = content[:m.start()] + \
                    FAILURES[kw] + content[m.end():]
                changes += 1

    # Related Keywords
    rk_pat = re.compile(
        r'\*\*Prerequisites \(understand these first\):\*\*\n\n?'
        r'- \[TODO\] - \[why needed\]\n'
        r'- \[TODO\] - \[why needed\]\n'
        r'\n?'
        r'\*\*Builds on this \(learn these next\):\*\*\n\n?'
        r'- \[TODO\] - \[what it adds\]\n'
        r'- \[TODO\] - \[what it adds\]\n'
        r'\n?'
        r'\*\*Alternatives / Comparisons:\*\*\n\n?'
        r'- \[TODO\] - \[when to prefer it\]\n'
        r'- \[TODO\] - \[when to prefer it\]'
    )
    for kw in KEYWORDS:
        if kw in RELATED:
            m = rk_pat.search(content)
            if m:
                content = content[:m.start()] + \
                    RELATED[kw] + content[m.end():]
                changes += 1

    with open(filepath, 'w', encoding='utf-8',
              newline='\n') as f:
        f.write(content)

    remaining = content.count('[TODO')
    print(f"Applied {changes} replacements")
    print(f"Remaining TODOs: {remaining}")


apply_all(FILE)
