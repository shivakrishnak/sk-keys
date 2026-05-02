---
layout: default
title: "Full GC"
parent: "Java & JVM Internals"
nav_order: 284
permalink: /java/full-gc/
number: "0284"
category: Java & JVM Internals
difficulty: ★★★
depends_on:
  - Major GC
  - Minor GC
  - Old Generation
  - Metaspace
  - Stop-The-World (STW)
used_by:
  - GC Tuning
  - GC Pause
  - Throughput vs Latency (GC)
  - GC Logs
  - Serial GC
related:
  - Major GC
  - Stop-The-World (STW)
  - GC Pause
  - G1GC
  - ZGC
tags:
  - jvm
  - garbage-collection
  - memory-management
  - java-internals
  - performance
---

# 0284 — Full GC

## 1. TL;DR
> Full GC is the most comprehensive—and most disruptive—garbage collection event in the JVM. It collects **all heap regions** (Young + Old + Metaspace) in a single **Stop-The-World (STW)** pause, freezing all application threads until completion. Full GCs are a last resort triggered when the JVM cannot reclaim enough memory through lighter collections.

---

## 2. Visual: How It Fits In

```
┌────────────────────────────────────────────────────────────┐
│                       JVM Heap                             │
│  ┌──────────────────────┐   ┌────────────────────────────┐ │
│  │   Young Generation   │   │     Old Generation         │ │
│  │  Eden | S0 | S1      │   │   Long-lived objects       │ │
│  └──────────────────────┘   └────────────────────────────┘ │
│  ┌──────────────────────────────────────────────────────┐   │
│  │             Metaspace (class metadata)               │   │
│  └──────────────────────────────────────────────────────┘   │
│                                                              │
│  Minor GC  ──► Young only      (short pause)                │
│  Major GC  ──► Old only        (longer pause)               │
│  Full GC   ──► ALL regions     (longest STW pause) ◄────┐   │
│                                                          │   │
│  Triggered when: Old Gen full, Metaspace exhausted,      │   │
│  System.gc() called, GC ergonomics demand it             │   │
└──────────────────────────────────────────────────────────┘
```

---

## 3. Core Concept

A **Full GC** is a complete heap collection that:

1. **Stops all application threads** (Stop-The-World)
2. **Collects Young Generation** — Eden and Survivor spaces
3. **Collects Old Generation** — promotes or removes old objects
4. **Collects Metaspace** — purges stale class metadata and class loaders
5. **Compacts memory** (in most collectors) — reduces fragmentation

Full GC is the JVM's nuclear option. It guarantees maximum memory reclamation at the cost of application availability. Modern low-pause collectors (G1, ZGC, Shenandoah) go to great lengths to **avoid** Full GC by performing concurrent work instead.

### Key distinction from Major GC:
| Term | Scope | STW? |
|------|-------|------|
| Minor GC | Young Generation only | Yes (short) |
| Major GC | Old Generation (primarily) | Yes (long) |
| Full GC | Young + Old + Metaspace | Yes (longest) |

> **Note:** The terms "Major GC" and "Full GC" are often conflated in documentation, but technically Full GC also reclaims Metaspace.

---

## 4. Why It Matters

Full GC pauses can last from **milliseconds to minutes** depending on heap size and object count. For production systems:

- A 10-second Full GC = 10 seconds of **zero user requests processed**
- In high-throughput APIs, this manifests as **timeout spikes, connection resets, SLA breaches**
- In stateful services (trading, gaming, telecom), Full GC can cause **cascading failures**

Understanding Full GC is essential for:
- Diagnosing "mystery" latency spikes in production
- Tuning JVM flags to reduce or eliminate Full GC
- Choosing the right GC algorithm for workload characteristics

---

## 5. Key Properties / Behavior Table

| Property | Value |
|----------|-------|
| Scope | Young + Old + Metaspace |
| Application threads | **Suspended (STW)** |
| Typical pause | 100ms – several minutes |
| Triggered by | Old Gen full, Metaspace full, `System.gc()`, GC failure |
| Memory compaction | Yes (most collectors) |
| Frequency goal | As rare as possible (ideally never) |
| Logged as | `[GC (Allocation Failure)] [Full GC ...]` |
| GC algorithms affected | All (Serial, Parallel, CMS, G1, ZGC, Shenandoah) |

---

## 6. Real-World Analogy

> Imagine a busy city where garbage trucks (Minor GC) collect trash from the new residential areas every morning. Occasionally, the city calls a **full city-wide cleanup** (Full GC) — all traffic stops, every road is blocked, and sanitation crews clean *everything* from suburbs to downtown. The city is paralyzed until the cleanup finishes. City planners (JVM engineers) design systems so this full shutdown almost never happens.

---

## 7. How It Works — Step by Step

```
1. Trigger event occurs:
   - Old Generation allocation fails
   - Metaspace threshold exceeded
   - System.gc() / Runtime.gc() called
   - GC algorithm cannot proceed concurrently

2. JVM reaches a global Safepoint:
   - All mutator (application) threads are stopped
   - Only GC threads continue running

3. Young Generation collection:
   - Eden space cleared
   - Live objects in Eden + Survivor copied to other Survivor/Old
   - Unreachable young objects are reclaimed

4. Old Generation collection:
   - Mark phase: GC Roots traversed, all live objects marked
   - Sweep phase: unreachable objects removed
   - Compact phase: remaining live objects moved together

5. Metaspace collection:
   - Class loaders no longer referenced are unloaded
   - Associated class metadata and code cache entries freed

6. Safepoint released:
   - Application threads resume
   - JVM logs Full GC event in GC logs
```

---

## 8. Under the Hood (Deep Dive)

### Triggers in detail

```
Full GC Triggers (JVM Hotspot):
├── Allocation failure in Old Gen (promotion failure)
├── Concurrent GC failure (CMS concurrent mode failure)
├── Metaspace exhaustion (-XX:MetaspaceSize exceeded without growth room)
├── Explicit System.gc() (-XX:+DisableExplicitGC disables this)
├── JVM internal: RMI GC, NIO buffer allocation failures
├── Heap dump request (jmap -dump)
└── G1: evacuation failure (cannot move objects from CSet)
```

### What makes Full GC slow

```
Pause time factors:
1. Heap size          → More objects = more to scan
2. Object count       → More references = longer mark phase  
3. Reference processing → SoftRef/WeakRef/PhantomRef queues
4. Finalization queue  → Objects with finalizers delay reclamation
5. Fragmentation      → Compaction moves many objects
6. Class unloading    → Metaspace scan + code cache purge
```

### Concurrent vs Full GC

```java
// G1GC aims to prevent Full GC via concurrent marking:
// (1) Concurrent Mark: finds live/dead objects while app runs
// (2) Mixed Collections: collect young + some old regions
// If concurrent marking falls behind allocation rate:
//   → "GC overhead limit exceeded" thrown, OR
//   → Fall back to Full GC (serial, STW)

// ZGC / Shenandoah keep STW pauses < 1ms via fully concurrent
// collection — but can still trigger Full GC in extreme cases
```

### Metaspace and Full GC

```
Metaspace Full GC trigger:
- When Metaspace used > MetaspaceSize threshold
- JVM tries to expand Metaspace first
- If MaxMetaspaceSize reached → triggers Full GC
- Full GC unloads dead ClassLoaders → frees Metaspace

Common cause: ClassLoader leaks in web apps (e.g., Tomcat
  relying on new class loaders per hot deploy without 
  proper cleanup)
```

---

## 9. Comparison Table

| Collector | Full GC STW? | Concurrent alternative | Max pause achievable |
|-----------|-------------|----------------------|---------------------|
| Serial GC | Yes | None (all STW) | Seconds |
| Parallel GC | Yes | None (all STW) | Seconds |
| CMS | Yes (fallback) | Concurrent mark/sweep | ~100ms (young) |
| G1GC | Yes (fallback) | Concurrent marking | 50–200ms typical |
| ZGC | Yes (minimal) | Fully concurrent | < 1ms STW |
| Shenandoah | Yes (minimal) | Fully concurrent | < 1ms STW |

---

## 10. When to Use / Avoid

| Scenario | Guidance |
|----------|----------|
| Batch jobs (overnight ETL) | Full GC acceptable — throughput > latency |
| Low-latency APIs (< 10ms SLA) | Must avoid Full GC — use ZGC/Shenandoah |
| Large heaps (> 4 GB) | Full GC severity grows — strongly prefer G1/ZGC |
| Class-heavy apps (reflection, code gen) | Watch Metaspace; tune MaxMetaspaceSize |
| `-XX:+DisableExplicitGC` | Use in production to block `System.gc()` calls |

---

## 11. Common Pitfalls & Mistakes

```
❌ Calling System.gc() in library code
   → Forces Full GC; remove or guard with flag

❌ Unbounded Metaspace (-XX:MaxMetaspaceSize not set)
   → Memory leak via ClassLoader accumulation

❌ Over-allocating heap (-Xmx too large)
   → Full GC has more to scan = longer pause

❌ Many finalizers in object hierarchy
   → Delays object reclamation, promotes to Old Gen

❌ Ignoring GC logs in production
   → Full GC storms go undetected until outage

❌ Assuming G1 never does Full GC
   → G1 falls back to serial Full GC on evacuation failure
```

---

## 12. Code / Config Examples

```bash
# JVM flags to diagnose and tune Full GC

# Enable GC logging (Java 9+)
-Xlog:gc*:file=gc.log:time,uptime,level,tags

# Disable explicit System.gc() calls
-XX:+DisableExplicitGC

# Cap Metaspace to prevent unbounded growth
-XX:MaxMetaspaceSize=512m

# Use G1GC (default Java 9+) with max pause target
-XX:+UseG1GC
-XX:MaxGCPauseMillis=200

# Use ZGC for sub-millisecond pauses (Java 15+ production-ready)
-XX:+UseZGC

# Use Shenandoah for low-latency
-XX:+UseShenandoahGC

# Heap Dump on OOM (captures state just before Full GC fails)
-XX:+HeapDumpOnOutOfMemoryError
-XX:HeapDumpPath=/tmp/heapdump.hprof
```

```java
// Avoid triggering Full GC via System.gc() — anti-pattern
public void clearCaches() {
    cacheMap.clear();
    System.gc(); // ← NEVER do this in production libraries
}

// Better: let GC collect naturally
public void clearCaches() {
    cacheMap.clear(); // objects become unreachable, GC will collect
}
```

```
# Full GC log entry (Java 11+ Unified GC logging):
[2025-05-02T10:15:32.456+0000][info][gc] GC(42) Pause Full (Allocation Failure)
[2025-05-02T10:15:32.456+0000][info][gc,phases] GC(42) Phase 1: Mark live objects 1234.5ms
[2025-05-02T10:15:32.456+0000][info][gc,phases] GC(42) Phase 2: Compute new object addresses 345.2ms
[2025-05-02T10:15:32.456+0000][info][gc,phases] GC(42) Phase 3: Adjust pointers 456.1ms
[2025-05-02T10:15:32.456+0000][info][gc,phases] GC(42) Phase 4: Move objects 234.3ms
[2025-05-02T10:15:34.734+0000][info][gc] GC(42) Pause Full (Allocation Failure) 8192M->2048M(16384M) 2278.1ms
```

---

## 13. Interview Q&A

**Q: What is the difference between Minor GC, Major GC, and Full GC?**
> Minor GC collects only Young Generation; Major GC collects Old Generation; Full GC collects ALL heap regions (Young + Old + Metaspace) in a single STW pause. Full GC is the most disruptive and has the longest pause.

**Q: What triggers a Full GC in G1?**
> G1 triggers a Full GC (serial, STW) when: (1) there is an evacuation failure — live objects from the Collection Set cannot be moved because no free regions exist; (2) concurrent marking cannot keep up with allocation rate. G1 avoids Full GC by preemptively collecting mixed regions.

**Q: How would you eliminate Full GC pauses in a latency-sensitive service?**
> Switch to ZGC or Shenandoah GC (sub-millisecond STW). Eliminate `System.gc()` calls. Tune Old Gen sizing to avoid promotion failures. Fix ClassLoader leaks (Metaspace). Profile and reduce object allocation rate. Set `-XX:+DisableExplicitGC`.

**Q: Can Full GC throw `OutOfMemoryError`?**
> Yes. If Full GC runs but cannot reclaim enough memory (e.g., Old Gen still full after collection), the JVM throws `java.lang.OutOfMemoryError: Java heap space`. Also if `GC overhead limit exceeded` — when more than 98% of time is spent in GC recovering less than 2% of heap.

**Q: What is the `GC overhead limit exceeded` error?**
> It's an OOM error thrown by the JVM when the application spends more than 98% of time doing GC but only frees less than 2% of heap per Full GC cycle. It's a safety mechanism to prevent an infinite GC loop from consuming all CPU.

---

## 14. Flash Cards

| Front | Back |
|-------|------|
| What heap regions does Full GC collect? | Young Generation + Old Generation + Metaspace |
| Is Full GC Stop-The-World? | Yes — all application threads are suspended |
| What JVM flag disables System.gc()? | `-XX:+DisableExplicitGC` |
| What JVM error follows excessive Full GC? | `OutOfMemoryError: GC overhead limit exceeded` |
| Which GC algorithm virtually eliminates Full GC? | ZGC and Shenandoah GC |
| What causes G1GC to fall back to Full GC? | Evacuation failure (no free regions for movement) |

---

## 15. Quick Quiz

**Question 1:** An application sees 5-second pauses every 2 hours, coinciding with GC log entries showing `Pause Full`. The app uses G1GC with a 16 GB heap. What is the most likely root cause?

- A) Minor GC overflow
- B) ✅ G1 evacuation failure or Metaspace exhaustion
- C) Young Generation too small
- D) Insufficient CPU for GC threads

**Question 2:** Which of the following flags prevents explicit Full GC from `System.gc()` calls?

- A) `-XX:GCPolicy=none`
- B) `-XX:+NeverFullGC`
- C) ✅ `-XX:+DisableExplicitGC`
- D) `-XX:+UseG1GC`

---

## 16. Anti-Patterns

```
🚫 Anti-Pattern: Relying on Full GC to "fix" memory leaks
   Problem:  Full GC pauses grow longer as heap fills
   Fix:      Find and fix the actual memory leak (heap profiler)

🚫 Anti-Pattern: Setting -Xmx very large "for safety"
   Problem:  Full GC over a 64 GB heap can pause for minutes
   Fix:      Right-size heap; use concurrent GC if large heap needed

🚫 Anti-Pattern: Calling System.gc() after closing connections
   Problem:  Forces Full GC, impacting all threads
   Fix:      Trust GC scheduler; use reference queues if needed

🚫 Anti-Pattern: Ignoring "Concurrent Mode Failure" in CMS logs
   Problem:  Indicates CMS falling back to Serial Full GC
   Fix:      Migrate to G1GC or tune CMSInitiatingOccupancyFraction
```

---

## 17. Related Concepts Map

```
Full GC
├── causes ──────────► Stop-The-World (STW) [#285]
├── scopes ──────────► Old Generation [#281]
│                  ──► Young Generation [#278]
│                  ──► Metaspace [#268]
├── preceded by ─────► Major GC [#283]
│                  ──► Minor GC [#282]
├── measured by ─────► GC Pause [#294]
│                  ──► GC Logs [#293]
├── avoided by ──────► G1GC [#289]
│                  ──► ZGC [#290]
│                  ──► Shenandoah GC [#291]
└── tuned via ───────► GC Tuning [#292]
```

---

## 18. Further Reading

- [Oracle: HotSpot VM Garbage Collection Tuning Guide](https://docs.oracle.com/en/java/docs/books/performance/index.html)
- [Java GC Handbook — Plumbr](https://plumbr.io/java-garbage-collection-handbook)
- [JVM Unified Logging (`-Xlog:gc*`)](https://openjdk.org/jeps/158)
- [G1GC: Avoiding Full GC](https://www.oracle.com/technical-resources/articles/java/g1gc.html)
- [ZGC: A Scalable Low-Latency GC (JEP 333)](https://openjdk.org/jeps/333)

---

## 19. Human Summary

Full GC is the JVM's most expensive garbage collection event — it freezes every application thread while cleaning the entire heap from top to bottom. Think of it as the JVM going completely offline for cleaning. In small applications or batch jobs, this is fine. But for any service with latency requirements, a Full GC is a production incident waiting to happen.

The best strategy is prevention: use ZGC or Shenandoah for latency-critical workloads, right-size your heap, eliminate `System.gc()` calls, and monitor GC logs continuously. Understanding when and why Full GC occurs transforms you from someone who "got paged for a mystery slowdown" to someone who prevents it from ever happening.

---

## 20. Tags

`jvm` `garbage-collection` `memory-management` `java-internals` `performance` `stop-the-world` `full-gc`

