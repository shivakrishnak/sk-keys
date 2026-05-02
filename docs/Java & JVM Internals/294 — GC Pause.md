---
layout: default
title: "GC Pause"
parent: "Java & JVM Internals"
nav_order: 294
permalink: /java/gc-pause/
number: "0294"
category: Java & JVM Internals
difficulty: ★★★
depends_on:
  - Stop-The-World (STW)
  - Minor GC
  - Full GC
  - GC Logs
  - Safepoint
used_by:
  - GC Tuning
  - Throughput vs Latency (GC)
  - G1GC
  - ZGC
related:
  - Stop-The-World (STW)
  - GC Tuning
  - Throughput vs Latency (GC)
  - Safepoint
  - GC Logs
tags:
  - jvm
  - garbage-collection
  - latency
  - java-internals
  - performance
---

# 0294 — GC Pause

## 1. TL;DR
> A **GC Pause** is the period during which all application threads are suspended (Stop-The-World) for garbage collection work. It is the primary latency impact metric for GC-related performance. GC pause duration includes both the **time to reach safepoint** (TTSP) and the **actual GC work time**. Minimizing GC pause duration is a central goal of modern garbage collector design.

---

## 2. Visual: How It Fits In

```
GC Pause = TTSP + GC Work Time

Timeline:
─────────────┬────────────────────────────────────┬──────────────
App running  │◄── TTSP ──►│◄────── GC Work ───────►│ App resumed
             │            │                         │
     Safepoint       All threads        GC phases    Threads
     requested       reached safepoint  complete     unblocked

Total GC Pause = time from "safepoint requested" to "threads resume"

TTSP (Time to Safepoint): often overlooked but can dominate pause
GC Work: actual garbage collection phases (mark, sweep, compact)
```

---

## 3. Core Concept

GC pause is not a single atomic event — it breaks down into:

1. **Time to Safepoint (TTSP):** How long from when the JVM requests a safepoint until ALL threads have reached their safepoint check point. Long TTSP usually indicates threads deep in JNI calls or tight loops.

2. **GC Work Time:** The actual time GC threads spend doing mark/copy/sweep/compact work. This is what tuning flags like `MaxGCPauseMillis` target.

3. **Reference Processing:** Processing of soft/weak/phantom references and finalizers — often overlooked but can significantly extend pause time.

4. **Class Unloading:** During Full GC, unloading dead classes extends the pause.

### Why pause time matters more than pause frequency

For user-facing applications, a single 500ms pause is far more impactful than 100 pauses of 5ms each. P99 and P999 latency percentiles directly reflect GC pause behavior, and this is what SLAs measure.

---

## 4. Why It Matters

Every GC pause is:
- A period of complete application unavailability
- Potential HTTP request timeout (if pause > timeout threshold)
- Load balancer health check failure risk
- Cascading retry storm in microservices
- Direct violation of latency SLAs

For a service with 99.9% availability SLA ≈ 8.7 hours downtime/year, a single 10-second Full GC is 0.1% of a day's downtime budget.

---

## 5. Key Properties / Behavior Table

| Property | Value |
|----------|-------|
| Components | TTSP + GC Work + Reference Processing |
| Measured | Wall-clock time from safepoint request to thread resume |
| Logged via | `-Xlog:gc*` (pause duration at end of each event) |
| TTSP logging | `-Xlog:safepoint*` |
| G1GC target | `MaxGCPauseMillis=200` (default) |
| ZGC typical | < 1ms total across all sub-pauses |
| Shenandoah typical | < 1ms total |
| Parallel GC typical | 100ms – seconds |
| Serial GC typical | Seconds (large heap) |
| Reference processing | Can add 10–200ms to pause in reference-heavy apps |

---

## 6. Real-World Analogy

> A GC pause is like a fire drill in an office building. Every fire drill (safepoint request) requires all employees (threads) to stop what they're doing (TTSP) and assemble in the parking lot (safepoint). Once everyone is outside, the fire safety team (GC threads) inspects the building (GC work). The total drill time = "time for stragglers to get out" + "building inspection time." Modern buildings (ZGC/Shenandoah) redesigned the fire safety system so inspections can happen with people still inside — only the assembly check itself requires a brief pause.

---

## 7. How It Works — Step by Step

```
GC Pause Lifecycle:

1. JVM decides STW needed (allocation failure, IHOP threshold, etc.)
2. Safepoint requested:
   - JVM sets safepoint flag
   - TTSP timer starts
3. Each thread polls safepoint:
   - Running threads: reach poll point, block
   - JNI threads: wait until returning to Java code
   - Blocked threads: already safe
4. All threads at safepoint → TTSP timer ends, GC work begins
5. GC phases execute (vary by collector):
   - Parallel GC: Mark + Compact (all STW)
   - G1GC: Evacuation pause, or Remark, or Cleanup
   - ZGC: Pause Mark Start/End, Pause Relocate Start (each < 1ms)
6. Reference processing (soft/weak/phantom refs, finalizers)
7. Class unloading (if Full GC)
8. GC work complete → threads resume
9. Pause duration logged in GC log
```

---

## 8. Under the Hood (Deep Dive)

### Measuring GC pauses

```bash
# Java 11+ — GC pause in log:
[0.234s][info][gc] GC(5) Pause Young (Normal) (G1 Evacuation Pause) 512M->128M(2048M) 45.234ms
#                                                                                       ^^^^^^^^ TOTAL pause

# Safepoint log for TTSP breakdown:
[0.234s][info][safepoint] Entering safepoint region: G1 Evacuation Pause
[0.235s][info][safepoint] Leaving safepoint region
[0.235s][info][safepoint] Total time for which application threads were stopped: 0.045234 seconds
[0.235s][info][safepoint]   Stopping threads took: 0.000123 seconds  ← TTSP
```

### Reference processing extending pauses

```java
// Problem: large soft reference caches extending GC pause
// When GC runs, it must process ALL soft references to decide which to clear

class ImageCache {
    // Huge cache of SoftReferences
    Map<String, SoftReference<Image>> cache = new HashMap<>();
    // 100,000+ entries → reference processing adds 100ms+ to GC pause
}

// Fix: use explicit size-bounded cache (LRU, Caffeine)
// instead of relying on GC to evict
LoadingCache<String, Image> cache = Caffeine.newBuilder()
    .maximumSize(1000)
    .build(key -> loadImage(key));
```

### JVM metrics for GC pause tracking

```java
// Programmatic GC pause monitoring
import java.lang.management.*;

// Listen for GC notifications
for (GarbageCollectorMXBean gc : ManagementFactory.getGarbageCollectorMXBeans()) {
    ((NotificationEmitter) gc).addNotificationListener(
        (notification, handback) -> {
            GarbageCollectionNotificationInfo info =
                GarbageCollectionNotificationInfo.from(
                    (CompositeData) notification.getUserData());
            long pauseMs = info.getGcInfo().getDuration();
            System.out.println("GC: " + info.getGcName() + " pause: " + pauseMs + "ms");
        }, null, null);
}
```

### G1GC pause components

```
G1 Evacuation Pause breakdown (from GC log with gc+phases=debug):

[gc+phases] GC(5) Pre Evacuate Collection Set: 0.5ms   ← setup
[gc+phases] GC(5) Merge Heap Roots: 1.2ms             ← root scan
[gc+phases] GC(5) Evacuate Collection Set: 38.4ms      ← object copy
[gc+phases] GC(5) Post Evacuate Collection Set: 4.8ms  ← cleanup  
[gc+phases] GC(5) Other: 0.3ms
Total: 45.2ms

The "Evacuate Collection Set" step dominates and scales with
number of live objects being moved.
```

---

## 9. Comparison Table

| Collector | Typical Pause | Max Pause | Pause Scales With |
|-----------|-------------|-----------|-------------------|
| Serial GC | 100ms–seconds | Minutes | Heap size |
| Parallel GC | 100ms–seconds | Minutes | Heap size |
| G1GC | 50–200ms | Seconds (Full GC) | Collection Set size |
| ZGC | 0.1–1ms | ~1ms | Root count only |
| Shenandoah | 0.1–1ms | ~1ms | Root count only |

---

## 10. When to Use / Avoid

| Target | Guidance |
|--------|----------|
| P99 pause < 200ms | G1GC with `MaxGCPauseMillis=100` |
| P99 pause < 10ms | Must use ZGC or Shenandoah |
| P99 pause < 1ms | ZGC or Shenandoah (measure carefully) |
| Batch: pause OK | Parallel GC for throughput |

---

## 11. Common Pitfalls & Mistakes

```
❌ Measuring only average GC pause, not P99/P999
   → Averages hide outliers; SLA breaches live in the tail

❌ Ignoring TTSP in safepoint logs
   → What looks like "100ms GC" might be "2ms GC + 98ms waiting for JNI thread"

❌ Having large SoftReference caches in reference-heavy apps
   → Reference processing adds unpredictable pause extension

❌ Not correlating GC pause events with application latency metrics
   → Hard to diagnose until you overlay the GC log on your APM timeline
```

---

## 12. Code / Config Examples

```bash
# Log pauses with full breakdown
-Xlog:gc*,gc+phases=debug,safepoint*:file=gc.log:time,uptime

# G1: target 100ms max pause
-XX:+UseG1GC -XX:MaxGCPauseMillis=100

# ZGC for sub-ms pauses
-XX:+UseZGC  # Java 15+

# Enable reference processing parallelism (reduces reference processing pause)
-XX:+ParallelRefProcEnabled
```

---

## 13. Interview Q&A

**Q: What is a GC pause and what does it consist of?**
> A GC pause is the total period application threads are suspended during a GC event. It consists of: (1) TTSP — time for all threads to reach safepoints; (2) GC work — actual collection phases (mark, copy, compact); (3) reference processing (soft/weak/phantom ref finalization); (4) class unloading (in Full GC). The GC log reports total wall-clock pause including all these components.

**Q: Why is P99 latency more important than average GC pause?**
> Average pause hides outliers. A service might have 99 pauses of 5ms and 1 pause of 500ms — the average is ~10ms but 1% of users experience 500ms latency spikes. SLAs and user experience are defined by tail latency, not averages.

**Q: How can you reduce GC pause duration without changing the collector?**
> (1) Reduce object allocation rate — less garbage = fewer collections. (2) Replace SoftReference caches with explicit bounded caches (Caffeine). (3) Avoid finalizers. (4) Enable `-XX:+ParallelRefProcEnabled` for reference processing. (5) Fix TTSP by minimizing JNI call duration. (6) Right-size heap to avoid collection frequency.

---

## 14. Flash Cards

| Front | Back |
|-------|------|
| GC pause = ? + ? | TTSP + GC Work + Reference Processing |
| What is TTSP? | Time-To-Safepoint: time for all threads to reach safepoint |
| What GC flag targets max pause in G1? | `-XX:MaxGCPauseMillis=N` |
| What extends GC pause beyond mark/sweep? | Reference processing (SoftRef/WeakRef) and class unloading |
| How to log TTSP separately? | `-Xlog:safepoint*` |

---

## 15. Quick Quiz

**Question 1:** A G1GC service shows a 250ms GC pause in logs, but safepoint logs show 200ms TTSP. How long was the actual GC work?

- A) 250ms
- B) ✅ ~50ms (250ms total - 200ms TTSP)
- C) 200ms
- D) Cannot determine

**Question 2:** Which of these most effectively reduces GC pause without changing the collector?

- A) Increasing `-Xmx`
- B) ✅ Replacing large SoftReference caches with Caffeine bounded caches
- C) Adding more CPU cores
- D) Increasing `MaxGCPauseMillis`

---

## 16. Anti-Patterns

```
🚫 Anti-Pattern: Setting MaxGCPauseMillis to 10ms with G1GC
   Problem:  G1 cannot achieve < 50ms; JVM ignores unrealistic targets
   Fix:      Use ZGC for < 10ms targets

🚫 Anti-Pattern: Deploying with large unbounded SoftReference caches
   Problem:  Reference processing adds unpredictable pause extensions
   Fix:      Use Caffeine/Guava caches with explicit size bounds
```

---

## 17. Related Concepts Map

```
GC Pause
├── component ───────► Stop-The-World (STW) [#285]
│                  ──► Safepoint [#307]
├── logged by ───────► GC Logs [#293]
├── minimized by ────► ZGC [#290]
│                  ──► Shenandoah GC [#291]
│                  ──► G1GC [#289] (best-effort target)
├── tuned via ───────► GC Tuning [#292]
└── relates to ──────► Throughput vs Latency (GC) [#295]
```

---

## 18. Further Reading

- [Oracle GC Tuning: Understanding Pauses](https://docs.oracle.com/en/java/javase/21/gctuning/)
- [TTSP analysis — Nitsan Wakart](http://psy-lob-saw.blogspot.com/2015/12/safepoints.html)
- [How to measure GC pause impact on latency](https://blog.gceasy.io/2019/04/why-do-gc-pauses-cause-latency/)

---

## 19. Human Summary

GC pause is the number that directly matters to your users. Every millisecond paused is a millisecond where no response was sent, no trade was processed, no game state was updated. Understanding that GC pause = TTSP + GC work + reference processing gives you three separate levers to pull — and often the biggest win comes from a non-obvious source like reference processing overhead or JNI thread delays inflating TTSP.

Modern collectors (ZGC, Shenandoah) have essentially solved the GC pause problem for most workloads. If you're still fighting with 200ms+ pauses in 2025, the answer is likely upgrading to Java 21 and enabling ZGC — not tuning 20 G1GC flags.

---

## 20. Tags

`jvm` `garbage-collection` `latency` `java-internals` `performance` `stop-the-world` `safepoint`

