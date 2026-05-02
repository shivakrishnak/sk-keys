---
layout: default
title: "GC Pause"
parent: "Java & JVM Internals"
nav_order: 294
permalink: /java/gc-pause/
number: "294"
category: Java & JVM Internals
difficulty: ★★★
depends_on: Stop-The-World (STW), G1GC, ZGC, GC Logs, Safepoint
used_by: GC Tuning, Throughput vs Latency (GC)
tags:
  - java
  - jvm
  - gc
  - performance
  - internals
  - deep-dive
---

# 294 — GC Pause

`#java` `#jvm` `#gc` `#performance` `#internals` `#deep-dive`

⚡ TL;DR — The stop-the-world interval during which all application threads are suspended while the GC performs work that requires a consistent heap snapshot.

| #294 | Category: Java & JVM Internals | Difficulty: ★★★ |
|:---|:---|:---|
| **Depends on:** | Stop-The-World (STW), G1GC, ZGC, GC Logs, Safepoint | |
| **Used by:** | GC Tuning, Throughput vs Latency (GC) | |

---

### 📘 Textbook Definition

A **GC Pause** (stop-the-world pause) is a period during which all application threads are suspended at safepoints while the garbage collector performs operations requiring a consistent view of the heap — such as root scanning, object graph traversal, remark phases, or object evacuation. Pause duration is the primary latency metric for GC performance, measured as the elapsed wall-clock time between thread suspension and resumption. Modern collectors (G1, ZGC, Shenandoah) minimise pause duration by moving most GC work to concurrent phases.

### 🟢 Simple Definition (Easy)

A GC Pause is a freeze — all your application threads stop completely while the JVM cleans up memory. The shorter the pause, the better your application's responsiveness.

### 🔵 Simple Definition (Elaborated)

When the JVM's garbage collector needs to do certain operations safely — like finding which objects are still alive — it needs the heap to stay still. So it pauses every thread in the application simultaneously. During this pause, your service handles zero requests, database queries time out, and any SLA clock keeps ticking. The length of this pause is the most important GC metric for latency-sensitive applications. Different collectors have very different pause profiles: from multi-second Full GC pauses to sub-millisecond ZGC pauses.

### 🔩 First Principles Explanation

**Why pauses are unavoidable (in some form):** The GC must traverse the object reference graph to determine which objects are reachable. If threads are still running and modifying references while the GC scans, two problems occur:

1. **Missed garbage:** An object the GC considers live may become garbage while scanning; it will be collected next cycle (the GC was conservative).
2. **Collecting live objects (fatal):** A previously dead-looking object may become reachable again via a reference write — if collected, this is a use-after-free bug.

**Safepoints:** Threads don't pause instantly. The JVM injects safepoint polling checks at method entry/exit, loop back-edges, and JNI transitions. When a GC is wanted, the JVM sets a flag; threads reach their next safepoint check and voluntarily suspend. The time to reach a safepoint is called "time to safepoint" — not counted in GC pause time but contributes to total latency impact.

**What operations require STW:**
- Initial root scan (must know all GC roots atomically).
- Final remark (catch mutations during concurrent marking).
- Object evacuation (in G1's Young GC — must move objects with no thread seeing stale pointers).
- Reference queue processing.

**Pause time vs. latency impact:**
```
Total latency impact = time-to-safepoint + GC pause + safepoint exit
                       ─────ignored──────  ─measured─  ─ignored──────
```

Safepoint time issues can look like GC pause problems but won't show in GC logs — they appear in `-Xlog:safepoint*` output.

### ❓ Why Does This Exist (Why Before What)

WITHOUT any GC Pause mechanism:

- Object graph traversal while threads run risks use-after-free: a just-freed object's memory could be overwritten and the pointer followed → JVM crash.
- Read barriers and write barriers could theoretically eliminate all STW, but at a cost to every load/store.

What breaks without managed STW:
1. GC correctness is compromised — live objects may be collected.
2. ZGC/Shenandoah trade-off: they minimise STW by adding per-load or per-object overhead.

WITH GC Pauses:
→ GC correctness guaranteed — all threads see a consistent heap snapshot.
→ Trade-off explicitly measurable and tunable via collector choice and configuration.

### 🧠 Mental Model / Analogy

> GC Pause is like a mandatory fire drill in an office building. The fire marshal (JVM) needs everyone to stop what they're doing, stand in the hallway, and be counted (root scan). While everyone's in the hallway, offices can be rearranged (object relocation). Once the count is done and offices rearranged, everyone goes back to their desk. The shorter the drill, the less productivity lost. Modern fire drills (ZGC) are so fast you barely notice them; older ones (Full GC) closed the building for hours.

"Fire drill" = GC pause, "people in hallway" = suspended threads, "counting" = marking/root scan, "rearranging offices" = compaction/evacuation.

The goal of GC evolution has been: make the drill faster, or move more preparation work before the drill starts.

### ⚙️ How It Works (Mechanism)

**Pause Components — G1GC Young GC Example:**
```
GC Pause Breakdown (G1 Young GC)
┌──────────────────────────────────────────────┐
│ Time to safepoint: 1–5ms                     │
│ ─────────────────────────────────────────    │
│ Root Processing:        5ms                  │
│   - Thread stacks scans                      │
│   - JNI global refs                          │
│   - Static fields                            │
│ Object Evacuation:      45ms                 │
│   - Copy live objects from Eden/S0           │
│   - Update references in CSets               │
│ Reference Processing:   2ms                  │
│ Post-process cleanup:   3ms                  │
│ ─────────────────────────────────────────    │
│ Total STW Pause:        55ms                 │
└──────────────────────────────────────────────┘
```

**Pause Measurement in GC Logs:**
```
[10:00:01.234][info][gc] GC(42) Pause Young 55.3ms
                                              ↑
                              This is the GC pause duration
                   (between all-threads-stopped and all-threads-resumed)
```

**ZGC Pause Profile (Java 17):**
```
Pause Mark Start:    0.012ms  ← STW (root scan only)
Concurrent Mark:     10.2ms   ← concurrent (not a pause!)
Pause Mark End:      0.018ms  ← STW (drain SATB buffers)
Pause Relocate Start:0.015ms  ← STW (update GC roots)
Concurrent Relocate: 15.1ms   ← concurrent
Total STW: 0.045ms — all three pauses combined < 0.1ms
```

**Safepoint Bias Problem:** All threads must reach a safepoint before the pause begins. A thread stuck in a long native call, a poorly compiled loop, or a spinning lock delays the GC pause start for ALL threads — increasing perceived latency without appearing in GC pause time.

```bash
# Detect safepoint delays:
-Xlog:safepoint*:file=safepoint.log:time,uptime
# Look for: "Total time for which application threads were stopped"
# vs. "Stopping threads took:"
# Large "Stopping threads took" = safepoint bias problem
```

### 🔄 How It Connects (Mini-Map)

```
GC triggered (Eden full / threshold / explicit)
           ↓
Safepoint requested → threads reach safepoint
           ↓
   GC Pause begins ← you are here
   (all app threads suspended)
           ↓
GC work (marking, evacuation, remark)
depending on collector:
  Full GC: minutes possible
  G1 Young GC: 50-200ms typical
  ZGC STW phases: < 1ms each
           ↓
Pause ends → threads resume
           ↓
Concurrent GC work continues (if concurrent collector)
```

### 💻 Code Example

Example 1 — Measuring GC pause impact on application latency:

```java
import java.lang.management.*;
import java.util.List;

public class GCPauseMonitor {
    private static final GarbageCollectorMXBean[] gcBeans;

    static {
        List<GarbageCollectorMXBean> beans =
            ManagementFactory.getGarbageCollectorMXBeans();
        gcBeans = beans.toArray(new GarbageCollectorMXBean[0]);
    }

    public static void printGCStats() {
        for (GarbageCollectorMXBean gc : gcBeans) {
            System.out.printf(
                "GC [%s]: count=%d, totalTime=%dms%n",
                gc.getName(),
                gc.getCollectionCount(),
                gc.getCollectionTime()
            );
        }
    }
    // Compare collectionTime before/after request to detect
    // if a GC pause occurred during this request's handling
}
```

Example 2 — Load testing to measure P99 GC pause impact:

```bash
# Run with GC logging enabled
java -XX:+UseG1GC \
     -XX:MaxGCPauseMillis=100 \
     -Xlog:gc*:file=gc.log:time,uptime \
     -jar app.jar &

# Run load for 10 minutes
wrk -t12 -c400 -d600s http://localhost:8080/api/health

# Correlate latency histogram percentiles with GC pause times
# If P99 = 200ms and GC pauses max = 190ms → GC is your P99
```

Example 3 — JVM safepoint analysis:

```bash
# Diagnose time-to-safepoint problem
java -Xlog:safepoint=info:file=sp.log:time,uptime \
     -jar app.jar

# In the log, look for large "Stopping threads took" values:
# [1.234s] Application time: 0.1234567 seconds
# [1.235s] Entering safepoint region: ...
# → If "Stopping threads took" > 10ms, investigate:
#   - Long native method calls
#   - JNI calls without safepoint polls
#   - Large arrays being scanned
```

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| GC pause = total GC time | Total GC time includes concurrent phases; GC pause is only the STW portion where threads are frozen. |
| ZGC/Shenandoah have zero pause time | Both still have brief STW phases (< 1ms each for ZGC). "Zero pause" is marketing shorthand for "negligible pause." |
| MaxGCPauseMillis guarantees pause will never exceed the target | It's a soft target; the JVM makes a best-effort prediction. Evacuation failures or humongous object processing can exceed it. |
| Pause time visible in GC logs includes time-to-safepoint | GC logs measure from safepoint-reached to all-threads-resumed. Time-to-safepoint is separately logged via `-Xlog:safepoint`. |
| Reducing heap size reduces GC pause | Smaller heaps GC more frequently but individual pauses may be shorter. The relationship is non-linear and collector-specific. |
| Only major/full GC causes noticeable pauses | With G1 on large heaps, Young GC pauses can be 100–300ms if Eden size is misconfigured; these are missed without GC log analysis. |
| Concurrent collectors never block on full GC | Any concurrent collector falls back to STW Full GC if it can't keep up with allocation (evacuation failure); these can be the longest pauses. |

### 🔥 Pitfalls in Production

**1. Safepoint Bias: Long Thread Stacks Extending Pauses**

```java
// BAD: Huge stack depths cause longer root scans
void deepRecursion(int depth) {
    if (depth == 0) return;
    Object[] temp = new Object[1000]; // per-frame local refs
    deepRecursion(depth - 1); // 1000+ frames deep
}
// GC must scan ALL stack frames for references
// → pause scales with stack depth × objects per frame

// GOOD: Use iteration instead of deep recursion for hot paths
```

**2. Monitoring GC Pause via -Xmx Without Log Correlation**

```bash
# BAD: setting only -Xmx without GC logging
# When SLA breaches happen, no evidence to diagnose

# GOOD: Always pair heap tuning with GC logging
java -Xmx4g \
     -XX:MaxGCPauseMillis=100 \
     -Xlog:gc*:file=gc.log:time,uptime,level,tags \
     -jar app.jar
```

**3. Time-to-Safepoint Mistaken for Application Bottleneck**

```bash
# Symptom: P99 latency 500ms but GC logs show only 50ms pauses
# Root cause: 450ms time-to-safepoint not counted in GC pause
# Diagnosis:
-Xlog:safepoint*:file=safepoint.log

# Common cause: JNI code without safepoint polls
# Fix: Ensure native code calls VM::safepoint_synchronize
# or restructure to shorter native segments
```

### 🔗 Related Keywords

- `Stop-The-World (STW)` — the mechanism that implements the GC pause.
- `Safepoint` — the thread coordination point where pauses occur.
- `G1GC` — balances pause time with throughput via `MaxGCPauseMillis` target.
- `ZGC` — achieves < 1ms GC pauses via concurrent relocation.
- `GC Logs` — records every pause with exact duration.
- `GC Tuning` — the process of reducing pause frequency and duration.
- `Throughput vs Latency (GC)` — pauses are the latency dimension of this trade-off.

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ KEY IDEA     │ STW freeze where all threads suspend      │
│              │ while GC performs heap-consistent work.   │
├──────────────┼───────────────────────────────────────────┤
│ USE WHEN     │ Measuring: P99 latency under load, SLA    │
│              │ breach investigation, GC tuning baseline. │
├──────────────┼───────────────────────────────────────────┤
│ AVOID WHEN   │ — (unavoidable; only minimisable via      │
│              │ collector choice and tuning)               │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "Every GC pause is a tax on latency;      │
│              │ ZGC makes it a rounding error."           │
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ Safepoint → GC Tuning → GC Logs → ZGC    │
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** A service uses G1GC with `-XX:MaxGCPauseMillis=100`. The SLA requires P99.9 < 150ms. A load test shows P99.9 = 400ms, but GC logs show no pause exceeding 95ms. What is the most likely explanation for the 400ms P99.9, and what specific logging configuration would you add to confirm or refute your hypothesis — without changing any GC or application flags?

**Q2.** ZGC's theoretical maximum STW pause time is bounded by the number of GC roots (thread stacks + static fields + JNI globals) rather than heap size. For a service with 2000 active threads, each with average 50 stack frames and 20 local references per frame, estimate the approximate root scanning time assuming 5ns per reference scan, and explain at what scale this bound becomes practically significant for ZGC's sub-millisecond pause guarantee.

