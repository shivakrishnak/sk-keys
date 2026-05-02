---
layout: default
title: "GC Tuning"
parent: "Java & JVM Internals"
nav_order: 292
permalink: /java/gc-tuning/
number: "292"
category: Java & JVM Internals
difficulty: ★★★
depends_on: G1GC, ZGC, Shenandoah GC, GC Pause, GC Logs, Throughput vs Latency (GC)
used_by: GC Logs, GC Pause, Throughput vs Latency (GC)
tags:
  - java
  - jvm
  - gc
  - performance
  - internals
  - deep-dive
---

# 292 — GC Tuning

`#java` `#jvm` `#gc` `#performance` `#internals` `#deep-dive`

⚡ TL;DR — The systematic process of selecting and configuring a JVM garbage collector to meet specific latency, throughput, and memory footprint targets.

| #292 | Category: Java & JVM Internals | Difficulty: ★★★ |
|:---|:---|:---|
| **Depends on:** | G1GC, ZGC, Shenandoah GC, GC Pause, GC Logs, Throughput vs Latency (GC) | |
| **Used by:** | GC Logs, GC Pause, Throughput vs Latency (GC) | |

---

### 📘 Textbook Definition

**GC Tuning** is the iterative process of configuring JVM memory regions, selecting an appropriate garbage collector, and adjusting GC-specific parameters to satisfy application service-level objectives (SLOs). It involves profiling GC behaviour, identifying bottlenecks (excessive Full GCs, high promotion rates, fragmentation), and adjusting flags such as heap sizes, generation ratios, pause-time targets, and concurrency thread counts to achieve the desired balance of latency, throughput, and memory usage.

### 🟢 Simple Definition (Easy)

GC Tuning is telling the JVM how to manage memory in a way that matches your application's needs — whether that's fewer pauses, more work per second, or less memory used.

### 🔵 Simple Definition (Elaborated)

The JVM's default GC settings work reasonably for many applications but poorly for production workloads with specific requirements. A low-latency API service needs pauses under 50ms; a batch processor needs maximum throughput; a microservice on a container needs minimal memory. GC tuning involves measuring actual GC behaviour (what collector is used, how long pauses are, how often), identifying what SLO is violated, and changing the right JVM flags to fix it. Done poorly, tuning creates new problems. Done well, it can eliminate 90% of latency spikes.

### 🔩 First Principles Explanation

**The GC Trilemma:** Every GC decision involves three competing goals:
1. **Throughput** — fraction of CPU time doing useful work (not GC).
2. **Latency** — maximum pause time per GC event.
3. **Footprint** — amount of heap memory used.

You can optimise for any two, but trade off the third. This is the fundamental constraint of GC tuning.

**Tuning Process:**

**Step 1 — Measure, don't guess.** Enable GC logging before tuning anything.
```bash
-Xlog:gc*:file=gc.log:time,uptime,level,tags
```

**Step 2 — Identify the bottleneck.** Read the logs with GCViewer or GCEasy:
- Frequent Minor GC → Eden too small, or allocation rate too high.
- Frequent Full GC → Old Gen too small, memory leak, or fragmentation.
- Long Remark/Clean pauses → High mutation rate, CMS → migrate to G1.
- Promotion failures → Old Gen has no room for promotions.

**Step 3 — Choose the right collector:**
```
Workload              → Recommended Collector
Batch/throughput      → Parallel GC (-XX:+UseParallelGC)
General/large heap    → G1GC (default Java 9+)
Ultra-low latency     → ZGC (-XX:+UseZGC, Java 15+)
Low-pause alternative → Shenandoah (-XX:+UseShenandoahGC)
Tiny JVM footprint    → Serial GC (-XX:+UseSerialGC)
```

**Step 4 — Size the heap correctly:**
```
Heap sizing rules of thumb:
- Minimum: 2× live data size
- Maximum: 4× live data size (more headroom = fewer GCs)
- Young Gen: 25–33% of total heap (default NewRatio=2)
- Container: set -Xmx to 70-80% of container memory limit
```

**Step 5 — Tune collector-specific parameters:**
- G1GC: `MaxGCPauseMillis`, `InitiatingHeapOccupancyPercent`, `G1HeapRegionSize`
- ZGC: `ConcGCThreads`, heap headroom (ZGC sizes itself).
- Parallel: `GCTimeRatio`, `MaxGCPauseMillis`.

**Step 6 — Validate, load test, repeat.** GC tuning is empirical — always validate changes under production-like load.

### ❓ Why Does This Exist (Why Before What)

WITHOUT GC Tuning (default settings in production):

- Default heap (256 MB max on many JDKs) causes OOM under production load.
- Default G1 pause target (200ms) may violate 50ms P99 SLA requirements.
- Default Young Gen sizing may cause violent swings in promotion rates.
- Default Parallel GC for the wrong workload causes 2-second API pauses.

What breaks without it:
1. Production incidents from OOM or excessive GC overhead (> 10% CPU on GC).
2. Missed SLAs despite sufficient hardware, because tuning was neglected.

WITH GC Tuning:
→ GC overhead drops from 20% to < 5% CPU for many workloads.
→ P99 pause time reduced from seconds to milliseconds via correct collector selection.
→ Predictable, bounded GC behaviour under peak load.

### 🧠 Mental Model / Analogy

> GC tuning is like adjusting the waste collection schedule for a city. You have fixed garbage trucks (GC threads), varying amounts of trash (allocations), and residents who hate being disturbed (latency SLA). You can collect trash very frequently (low latency, high CPU), once a week (low CPU, occasional large collection events), or in a rolling neighbourhood-by-neighbourhood approach (G1/ZGC region-based). The right schedule depends on your residents' tolerance.

The analogy: frequency = GC frequency, truck count = GC threads, neighbourhood-by-neighbourhood = region-based collectors, residents being disturbed = application pauses.

There is no universally "right" schedule — it depends entirely on the specific trade-offs your application needs.

### ⚙️ How It Works (Mechanism)

**Key GC Flags Reference:**

```bash
# ─── HEAP SIZING ──────────────────────────────────
-Xms<size>          # min heap (set equal to -Xmx to avoid resize pauses)
-Xmx<size>          # max heap
-Xmn<size>          # young gen size (or use -XX:NewRatio)
-XX:NewRatio=2      # Old:Young = 2:1 (Young = 33% of heap)
-XX:SurvivorRatio=8 # Eden:Each Survivor = 8:1

# ─── COLLECTOR SELECTION ─────────────────────────
-XX:+UseG1GC           # G1GC (default Java 9+)
-XX:+UseZGC            # ZGC (Java 15+)
-XX:+UseShenandoahGC   # Shenandoah (OpenJDK 12+)
-XX:+UseParallelGC     # Parallel (throughput)
-XX:+UseSerialGC       # Serial (single-core/embedded)

# ─── G1GC TUNING ─────────────────────────────────
-XX:MaxGCPauseMillis=200           # soft pause target
-XX:InitiatingHeapOccupancyPercent=45 # when to start marking
-XX:G1HeapRegionSize=4m            # 1-32m; auto if not set
-XX:G1NewSizePercent=20            # min young gen % of heap
-XX:G1MaxNewSizePercent=60         # max young gen % of heap
-XX:ConcGCThreads=4                # concurrent marking threads

# ─── ZGC TUNING ──────────────────────────────────
-XX:+UseZGC
-XX:+ZGenerational       # Java 21+: enable generational ZGC
-XX:ConcGCThreads=4      # concurrent GC threads

# ─── LOGGING (Java 11+) ──────────────────────────
-Xlog:gc*:file=gc.log:time,uptime,level,tags
-Xlog:gc+heap=debug:file=heap.log
```

**GC Overhead Calculation:**

```
GC Overhead = Total GC time / Total elapsed time × 100%

Target thresholds:
< 5%   → healthy
5-10%  → acceptable peak load
> 10%  → investigate and tune
> 30%  → GC thrashing; critical issue
```

### 🔄 How It Connects (Mini-Map)

```
Measure: GC Logs + JFR → identify bottleneck
               ↓
   ┌─────────────────────────────┐
   │ Bottleneck: Pause too long? │
   │  → G1/ZGC/Shenandoah        │
   │ Bottleneck: Too many GCs?   │
   │  → Increase heap            │
   │ Bottleneck: Full GC?        │
   │  → Fix leak / increase Old  │
   └─────────────────────────────┘
               ↓
    GC Tuning ← you are here
               ↓
   Load test → validate → iterate
```

### 💻 Code Example

Example 1 — GC tuning for a high-throughput REST API (Java 21):

```bash
java -Xms4g -Xmx4g \
     -XX:+UseZGC \
     -XX:+ZGenerational \
     -XX:ConcGCThreads=4 \
     -Xlog:gc*:file=/logs/gc.log:time,uptime:filecount=10,filesize=50m \
     -XX:+HeapDumpOnOutOfMemoryError \
     -XX:HeapDumpPath=/tmp/heap.hprof \
     -jar app.jar
```

Example 2 — Analysing GC logs with gceasy.io or GCViewer:

```bash
# Parse GC log for pause time statistics
# Install GCViewer (open-source):
java -jar gcviewer.jar gc.log

# Key metrics to extract:
# - Pause times: avg, P99, max
# - GC overhead %
# - Full GC count (should be 0 or near-0)
# - Heap occupancy after GC (trend)
```

Example 3 — Detecting memory leak through GC trend analysis:

```bash
# In GC logs, collect heap-after-GC values over time
grep "Heap" gc.log | awk '{print $NF}'

# If heap-after-GC increases monotonically:
# → Memory leak or unbounded cache
# Confirm with heap dump:
jcmd <pid> GC.heap_dump /tmp/heap.hprof
# Analyse with Eclipse MAT or VisualVM
```

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| More heap always means better GC performance | Larger heaps reduce GC frequency but increase pause duration for collecting collectors. Optimal sizing exists. |
| The default GC settings are good for production | Defaults are designed for developer machines; production services almost always benefit from explicit tuning. |
| -server flag enables all optimisations | -server enables JIT optimisations, not GC tuning. They are separate concerns. |
| GC tuning is only about flags | Object allocation patterns (allocation rate, object lifetime distribution) matter more than flags; profiling comes before flag changes. |
| Setting -Xms=-Xmx prevents resizing overhead | This prevents resize pauses but also commits the full heap at startup, which may not be desirable in containers. |
| Disabling GC altogether is possible | No; you can delay GC (epsilon GC for micro-benchmarks) but eventually the heap fills and the JVM crashes. |
| GC tuning is a one-time activity | Application behaviour changes with load patterns and code changes; GC tuning should be revisited with each major release or load profile change. |

### 🔥 Pitfalls in Production

**1. Setting -Xmx Higher Than Container Memory Limit**

```bash
# BAD: Container limit 4GB, but JVM can grow to 8GB
docker run -m 4g java -Xmx8g -jar app.jar
# → OOMKilled by container orchestrator

# GOOD: Set to 75% of container memory
# Java 10+ respects container limits automatically:
java -XX:MaxRAMPercentage=75 -jar app.jar
# Explicitly for older Java:
java -Xmx3g -jar app.jar  # for 4GB container
```

**2. Ignoring GC Overhead Under Load — Discovering it in Production**

```bash
# GOOD: Always test GC behaviour under production-like load
# Run load test for 30+ minutes and collect GC logs
# Check: is GC overhead < 5%? Are Full GC counts growing?

# Enable GC overhead circuit breaker (JVM internal):
-XX:GCTimeLimit=30       # throw OOM if >30% time in GC
-XX:GCHeapFreeLimit=5    # throw OOM if <5% freed per GC
```

**3. Tuning the Wrong Metric**

```bash
# BAD: Tuning for throughput when SLA is latency
# → Parallel GC with huge heap: great ops/sec, 3s pauses

# GOOD: Align collector choice with primary SLO
# Latency SLO (P99 < 100ms) → ZGC or G1 with MaxGCPauseMillis
# Throughput SLO (ops/sec) → Parallel GC with large heap
```

**4. Not Pinning -Xms=-Xmx in Kubernetes**

```bash
# BAD: JVM heap shrinks during low-traffic periods,
# then must regrow under traffic spikes, causing GC storms

# GOOD: In Kubernetes with memory limits, pin heap size
java -Xms2g -Xmx2g -jar app.jar
# Combined with resource.limits.memory = 3Gi in k8s spec
```

### 🔗 Related Keywords

- `G1GC` — the primary tuning target for most Java production services.
- `ZGC` — the choice when latency headroom is tight and Java 15+ is available.
- `GC Logs` — essential data source for diagnosis before any flag changes.
- `GC Pause` — the primary metric GC tuning aims to reduce.
- `Throughput vs Latency (GC)` — the fundamental trade-off framing all GC decisions.
- `Heap Memory` — sizing heap correctly is the first GC tuning lever.
- `Old Generation` — often the source of Full GC problems.
- `Escape Analysis` — JVM optimisation that reduces allocation pressure.

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ KEY IDEA     │ Measure → identify bottleneck → choose    │
│              │ collector → size heap → validate.         │
├──────────────┼───────────────────────────────────────────┤
│ USE WHEN     │ GC overhead > 5%, pause SLAs violated,    │
│              │ OOM errors, Full GC more than once/hour.  │
├──────────────┼───────────────────────────────────────────┤
│ AVOID WHEN   │ "Tuning" without profiling data first —   │
│              │ flag changes without measurement cause    │
│              │ more problems than they solve.            │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "GC tuning without GC logs is             │
│              │ surgery without an X-ray."                │
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ GC Logs → GC Pause → Safepoint → TLAB     │
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** A Spring Boot service processes 10,000 HTTP requests per second, each creating approximately 50 KB of short-lived objects. After 6 hours of production traffic, Minor GC frequency increases from once per second to once every 100ms without any change in request rate or size. Eden size is 512 MB. List the three most likely causes for this change in GC behaviour and how you would differentiate between them using GC logs and heap dumps.

**Q2.** You're tuning a service that must satisfy both a throughput SLO (99% of requests complete within 200ms) and a memory footprint constraint (max 2 GB heap in a container). With G1GC at default settings, P99 is 180ms (barely acceptable) but heap usage is stable. Switching to ZGC drops P99 to 5ms but heap usage grows to 2.4 GB because ZGC needs more headroom. How would you evaluate whether this trade-off is worth making, and what architectural changes could let you satisfy both constraints simultaneously?

