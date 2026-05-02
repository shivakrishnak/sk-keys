---
layout: default
title: "GC Tuning"
parent: "Java & JVM Internals"
nav_order: 292
permalink: /java/gc-tuning/
number: "0292"
category: Java & JVM Internals
difficulty: ★★★
depends_on:
  - G1GC
  - ZGC
  - Shenandoah GC
  - GC Logs
  - Throughput vs Latency (GC)
used_by:
  - GC Logs
  - GC Pause
  - Full GC
related:
  - GC Logs
  - GC Pause
  - Throughput vs Latency (GC)
  - JIT Compiler
  - Escape Analysis
tags:
  - jvm
  - garbage-collection
  - tuning
  - java-internals
  - performance
---

# 0292 — GC Tuning

## 1. TL;DR
> **GC Tuning** is the practice of configuring JVM garbage collection flags, heap sizes, and collector parameters to meet application-specific throughput and latency goals. Effective GC tuning follows a data-driven approach: measure first (GC logs, profilers), identify the bottleneck, then apply targeted changes — never tune blindly.

---

## 2. Visual: How It Fits In

```
GC Tuning Decision Tree:

Start: What is your PRIMARY concern?
       │
       ├─► Throughput (batch, ETL)?
       │     Use Parallel GC (-XX:+UseParallelGC)
       │     Goal: maximize app CPU time / total time
       │     Tune: -XX:GCTimeRatio=99, heap size
       │
       ├─► Balanced throughput + latency (most apps)?
       │     Use G1GC (default Java 9+)
       │     Goal: -XX:MaxGCPauseMillis=200
       │     Tune: IHOP, region size, heap ratio
       │
       └─► Latency is critical (< 10ms P99)?
             Use ZGC or Shenandoah
             Goal: < 1ms STW pauses
             Tune: heap size (give headroom), allocation rate
```

---

## 3. Core Concept

GC tuning addresses three primary metrics:

1. **Throughput:** Percentage of time application (not GC) runs. Goal: > 95%.
2. **Latency:** STW pause duration. Goal depends on SLA (10–200ms for most, < 1ms for low-latency).
3. **Footprint:** Amount of memory used by JVM/GC metadata.

These largely form a **triangle of trade-offs**: optimizing one often hurts another. The tuning process:

```
1. Enable GC logging  →  Baseline measurements
2. Identify issue     →  Too many Minor GC? Large Full GC? Long pauses?
3. Root cause         →  Object allocation rate? Heap too small? Wrong collector?
4. Apply change       →  One flag at a time
5. Measure again      →  Compare before/after
6. Repeat             →  Until goals met
```

---

## 4. Why It Matters

JVM default settings are designed for a broad range of applications, not yours specifically. Poor GC tuning causes:
- Latency spikes that trigger customer complaints or SLA penalties
- Frequent OOM errors in production
- Wasted cloud compute costs (too much memory provisioned, or too-frequent GC consuming CPU)
- Cascading failures in distributed systems (one node's Full GC causes retry storms)

Good GC tuning is one of the highest-ROI JVM skills.

---

## 5. Key Properties / Behavior Table

| Concern | Relevant Flags |
|---------|---------------|
| Heap size | `-Xms`, `-Xmx`, `-Xmn` |
| Collector choice | `-XX:+UseG1GC`, `-XX:+UseZGC`, etc. |
| G1GC pause target | `-XX:MaxGCPauseMillis=N` |
| G1GC concurrent mark trigger | `-XX:InitiatingHeapOccupancyPercent=N` |
| G1GC region size | `-XX:G1HeapRegionSize=N` |
| Parallel GC threads | `-XX:ParallelGCThreads=N` |
| Concurrent GC threads | `-XX:ConcGCThreads=N` |
| Young Gen sizing | `-XX:NewRatio=N`, `-XX:G1NewSizePercent=N` |
| Survivor behavior | `-XX:SurvivorRatio=N`, `-XX:MaxTenuringThreshold=N` |
| Explicit GC | `-XX:+DisableExplicitGC` |
| Final: log everything | `-Xlog:gc*:file=gc.log:time,uptime` |

---

## 6. Real-World Analogy

> GC tuning is like tuning a car engine. You don't tune by randomly adjusting every bolt — you first diagnose the problem (engine hesitation, poor fuel economy, rough idle). Then you measure (dyno, AFR sensors), understand the cause (fuel mixture, timing), make one targeted adjustment, and measure again. Random "performance tuning" without measurement is just as likely to make things worse as better.

---

## 7. How It Works — Step by Step

```
GC Tuning Methodology:

STEP 1: Enable comprehensive GC logging
  -Xlog:gc*:file=gc.log:time,uptime,level,tags

STEP 2: Collect baseline data (minimum 30 minutes of production load)
  Capture: pause frequencies, pause durations, heap utilization,
           allocation rate, GC overhead %

STEP 3: Analyze with tooling
  - GCEasy (https://gceasy.io) — upload GC log, get analysis
  - GCViewer — local analysis
  - JVM Mission Control (JMC) — Oracle's deep profiler

STEP 4: Identify the dominant problem
  Problem A: Too many Minor GC events
    → Young Gen too small; allocation rate high
    → Fix: increase -Xmn or -XX:G1NewSizePercent

  Problem B: Full GC / evacuation failures
    → Old Gen too small or IHOP too high
    → Fix: increase -Xmx, lower -XX:InitiatingHeapOccupancyPercent

  Problem C: Long STW pauses
    → Using wrong collector
    → Fix: migrate to G1 (from Parallel) or ZGC (from G1)

  Problem D: High GC overhead (> 10% of CPU)
    → Too small heap; too high allocation rate
    → Fix: increase heap; reduce allocation; object pooling

STEP 5: Apply one change at a time
STEP 6: Measure again; confirm improvement
STEP 7: Document changes in runbook/ADR
```

---

## 8. Under the Hood (Deep Dive)

### Heap sizing fundamentals

```
Rule of thumb: heap ≥ 3× live data set
  If application live data = 2 GB → Xmx ≥ 6 GB

Setting Xms = Xmx (fixed heap):
  Pros: Eliminates heap expansion STW; predictable footprint
  Cons: Wastes memory if app has variable load
  Best for: production services with consistent load

Young Gen sizing:
  Default: ~1/3 of heap (G1 manages dynamically)
  Too small Young Gen → frequent Minor GC
  Too large Young Gen → Minor GC pauses grow
  G1: auto-adjusts; manual override:
    -XX:G1NewSizePercent=20 (min 20% of heap is Young)
    -XX:G1MaxNewSizePercent=40 (max 40%)
```

### G1GC tuning recipe

```bash
# 1. Start with defaults — measure first
java -XX:+UseG1GC -Xms4g -Xmx8g \
     -Xlog:gc*:file=gc-baseline.log:time,uptime \
     -jar app.jar

# 2. If Mixed GC pauses too long:
-XX:MaxGCPauseMillis=100    # Tighten pause target

# 3. If concurrent marking starts too late (evacuation failures):
-XX:InitiatingHeapOccupancyPercent=35  # Start marking earlier (default 45)

# 4. If many humongous allocations:
-XX:G1HeapRegionSize=16m  # Increase region size to reduce humongous promotions

# 5. If high GC thread count is causing resource contention:
-XX:ParallelGCThreads=4
-XX:ConcGCThreads=2
```

### Common GC metrics to monitor

```
Metric                  | Alert Threshold
─────────────────────── | ───────────────
GC pause P99             | > 200ms (G1), > 1ms (ZGC)
GC overhead %            | > 5% of total CPU time
Full GC frequency        | > 0 / hour (investigate any Full GC)
Allocation rate          | Sudden > 50% increase (memory leak signal)
Old Gen growth trend     | Steady upward trend → memory leak
Minor GC frequency       | > 1/second (Young Gen may be too small)
Heap utilization         | > 85% consistently → increase Xmx
```

### Object allocation reduction (best fix)

```java
// Too many short-lived objects → high GC pressure
// Often better solution than GC tuning

// Anti-pattern: creating unnecessary objects in hot path
for (int i = 0; i < 1000000; i++) {
    String key = "user:" + userId + ":session:" + sessionId; // new String each time
    cache.get(key);
}

// Better: reuse/intern where safe
static final String KEY_PREFIX = "user:";
// Or use StringBuilder in loop
StringBuilder sb = new StringBuilder();
for (int i = 0; i < 1000000; i++) {
    sb.setLength(0);
    sb.append(KEY_PREFIX).append(userId)...
    cache.get(sb.toString());
}

// Best for hot paths: avoid allocation entirely
// Consider: object pools, value types (Project Valhalla), 
//           off-heap storage (Chronicle Map, etc.)
```

---

## 9. GC Tuning Quick Reference

| Symptom | Likely Cause | First Fix |
|---------|-------------|-----------|
| Frequent Minor GC | Young Gen too small | Increase `-XX:G1NewSizePercent` |
| Full GC / evacuation failure | Old Gen too small | Increase `-Xmx`; lower IHOP |
| Long Mixed GC pauses | Too many Old regions per cycle | Lower `MaxGCPauseMillis`, tune `G1MixedGCCountTarget` |
| GC overhead > 10% | Heap too small / high alloc rate | Increase heap; profile allocations |
| OutOfMemoryError: Heap | Memory leak or heap too small | Heap dump; analyze with MAT/VisualVM |
| OutOfMemoryError: Metaspace | ClassLoader leak | Set `MaxMetaspaceSize`; fix leak |

---

## 10. When to Use / Avoid

| Scenario | Guidance |
|----------|----------|
| Pre-production | Tune in load test environment, not production-first |
| Changing collectors | Test thoroughly; incompatible flags cause silent no-ops |
| Over-tuning | Default G1 is good; only tune when you have a measured problem |
| Legacy Java 8 apps | Migrate to Java 17+ first; GC improvements dwarf tuning gains |

---

## 11. Common Pitfalls & Mistakes

```
❌ Tuning without measuring first
   → Random flag changes can hurt as much as help

❌ Setting -Xms much lower than -Xmx
   → JVM spends time growing heap (STW resizes); set Xms = Xmx for prod

❌ Adding more flags hoping one helps
   → Many flags conflict; start minimal, add one at a time

❌ Tuning GC when the real problem is object allocation rate
   → Profile allocations first; reduce garbage before tuning GC

❌ Assuming JVM flag works on your JVM version
   → Some flags are collector-specific, version-specific; verify with
      java -XX:+PrintFlagsFinal -version | grep <FlagName>
```

---

## 12. Code / Config Examples

```bash
# Complete production G1GC configuration example:
java \
  # Collector
  -XX:+UseG1GC \
  # Heap
  -Xms8g -Xmx8g \                              # Fixed heap = fast startup
  # G1 tuning
  -XX:MaxGCPauseMillis=150 \                    # Pause target
  -XX:InitiatingHeapOccupancyPercent=35 \       # Concurrent mark earlier
  -XX:G1HeapRegionSize=8m \                     # Region size
  -XX:G1NewSizePercent=20 \                     # Min young gen
  -XX:G1MaxNewSizePercent=40 \                  # Max young gen
  # GC threads
  -XX:ParallelGCThreads=8 \
  -XX:ConcGCThreads=4 \
  # Safety
  -XX:+DisableExplicitGC \                      # Block System.gc()
  -XX:+HeapDumpOnOutOfMemoryError \
  -XX:HeapDumpPath=/opt/dumps/ \
  # Logging
  -Xlog:gc*:file=/opt/logs/gc.log:time,uptime,level,tags:filecount=10,filesize=50m \
  -jar service.jar
```

---

## 13. Interview Q&A

**Q: What is your GC tuning process for a Java microservice?**
> Enable GC logging with `-Xlog:gc*`, run under representative load for 30+ minutes, upload to GCEasy for analysis. Identify: (1) pause durations and P99 latency, (2) Full GC frequency, (3) GC overhead %, (4) allocation rate. Then address the biggest bottleneck: resize heap if too small, lower IHOP if evacuation failures, adjust pause target if pauses too long, or switch to ZGC if < 10ms P99 latency needed.

**Q: When should you switch from G1GC to ZGC?**
> When G1GC pauses consistently exceed your latency SLA despite tuning, and you're on Java 15+. ZGC is the right choice when: P99 pause target < 10ms, heap > 32 GB, or application is highly latency-sensitive (trading, gaming, real-time processing). The ~10% throughput cost is usually acceptable.

**Q: What does `-Xms8g -Xmx8g` (same min/max heap) do?**
> It creates a fixed-size heap. The JVM immediately allocates all 8 GB at startup and never grows or shrinks it. This eliminates STW heap expansion events and makes memory usage predictable. It's recommended for production services with consistent load patterns. The downside is higher baseline memory usage even under light load.

---

## 14. Flash Cards

| Front | Back |
|-------|------|
| Three GC tuning goals (triangle) | Throughput, Latency, Footprint |
| Flag to prevent System.gc() in production | `-XX:+DisableExplicitGC` |
| Good online GC log analyzer | GCEasy (gceasy.io) |
| First step in GC tuning | Enable comprehensive GC logging, measure baseline |
| When to use ZGC over G1GC | When P99 pause needs < 10ms; heap > 32 GB |
| What does lowering IHOP do? | Starts concurrent marking earlier → reduces evacuation failures |

---

## 15. Quick Quiz

**Question 1:** An application shows frequent Full GC events after 2 hours of uptime. Old Gen is growing continuously. What is most likely the cause?

- A) Young Gen is too small
- B) ✅ Memory leak — objects accumulating in Old Gen
- C) G1GC pause target too aggressive
- D) Metaspace exhaustion

**Question 2:** Which action should you take FIRST when GC pauses become problematic?

- A) Immediately switch to ZGC
- B) Add more heap
- C) ✅ Enable GC logging and analyze the baseline data
- D) Disable concurrent GC

---

## 16. Anti-Patterns

```
🚫 Anti-Pattern: Cargo-cult flag copying from blog posts
   Problem:  Flags from 2014 Java 7 articles may hurt Java 21 G1/ZGC
   Fix:      Understand each flag; verify relevance to your JVM version

🚫 Anti-Pattern: Fixing GC before fixing allocation rate
   Problem:  Application creates 1 GB/s of garbage; no GC tuning can fix this
   Fix:      Profile allocations (JFR, async-profiler); reduce object creation

🚫 Anti-Pattern: Setting identical Xms and Xmx in development
   Problem:  Dev machines run OOM; masks heap needs
   Fix:      Small Xmx in dev; fixed Xms=Xmx in production

🚫 Anti-Pattern: Not setting HeapDumpOnOutOfMemoryError in production
   Problem:  When OOM occurs, no forensic data available
   Fix:      Always set -XX:+HeapDumpOnOutOfMemoryError -XX:HeapDumpPath=...
```

---

## 17. Related Concepts Map

```
GC Tuning
├── requires ────────► GC Logs [#293]
│                  ──► GC Pause [#294]
│                  ──► Throughput vs Latency (GC) [#295]
├── chooses between ► Serial GC [#286]
│                  ──► Parallel GC [#287]
│                  ──► G1GC [#289]
│                  ──► ZGC [#290]
│                  ──► Shenandoah GC [#291]
├── affects ─────────► Full GC [#284]
│                  ──► Minor GC [#282]
└── tools ───────────► GCEasy, GCViewer, JMC, async-profiler
```

---

## 18. Further Reading

- [Oracle: Java GC Tuning Guide (Java 21)](https://docs.oracle.com/en/java/javase/21/gctuning/index.html)
- [GCEasy — Free GC Log Analyzer](https://gceasy.io)
- [GCViewer — Open Source GC Log Viewer](https://github.com/chewiebug/GCViewer)
- [Java Mission Control (JMC)](https://www.oracle.com/java/technologies/jdk-mission-control.html)
- [Async-Profiler — Allocation Profiling](https://github.com/async-profiler/async-profiler)

---

## 19. Human Summary

GC tuning is fundamentally a diagnostic skill. The engineers who do it well aren't the ones who memorize the most JVM flags — they're the ones who know how to measure, interpret GC logs, and reason about object lifecycle. The most impactful tunings are often: right-sizing the heap, switching to a modern collector, lowering IHOP to prevent evacuation failures, and eliminating System.gc() calls.

The most common mistake is tuning without measuring — adding random flags hoping "more memory" or "different GC" magically fixes problems. Always start with data. Always change one thing at a time. And remember: reducing your application's allocation rate is almost always more impactful than any GC flag you can set.

---

## 20. Tags

`jvm` `garbage-collection` `tuning` `java-internals` `performance` `g1gc` `heap-sizing`

