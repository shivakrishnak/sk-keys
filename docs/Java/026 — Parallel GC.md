---
layout: default
title: "Parallel GC"
parent: "Java & JVM Internals"
nav_order: 26
permalink: /java/parallel-gc/
number: "026"
category: JVM Internals
difficulty: ★★☆
depends_on: Young Generation, Old Generation, Stop-The-World, Serial GC
used_by: Throughput-first Batch Applications, Default JVM GC (Java 8)
tags: #java, #jvm, #gc, #memory, #parallel
---

# 026 — Parallel GC

`#java` `#jvm` `#gc` `#memory` `#parallel`

⚡ TL;DR — Parallel GC (Throughput Collector) uses multiple GC threads for both Young and Old generation collections, maximising application throughput at the cost of longer but parallel Stop-The-World pauses — the default GC in Java 8.

| #026 | Category: JVM Internals | Difficulty: ★★☆ |
|:---|:---|:---|
| **Depends on:** | Young Generation, Old Generation, Stop-The-World, Serial GC | |
| **Used by:** | Throughput-first Batch Applications, Default JVM GC (Java 8) | |

---

### 📘 Textbook Definition

**Parallel GC** (also called Throughput Collector, `-XX:+UseParallelGC`) is a Stop-The-World collector that uses **N threads** (default: number of CPU cores) for both Minor GC (Young generation) and Major GC (Old generation). The parallelisation reduces pause duration compared to Serial GC while maximising CPU utilisation during collection. Goal: **maximise application throughput** (time mutator runs vs time GC runs) rather than minimise individual pause latency.

---

### 🟢 Simple Definition (Easy)

Serial GC cleans with one janitor — slow. Parallel GC calls in the entire cleaning crew simultaneously. All application threads still pause during cleaning (Stop-The-World), but the cleaning finishes faster because N janitors work in parallel. Better for batch jobs where throughput matters more than individual pause time.

---

### 🔵 Simple Definition (Elaborated)

Parallel GC aims for the best overall throughput: the ratio of time your application runs vs time GC runs. For batch processing, analytics, or build systems, a 500ms pause every 10 minutes is far better than many 50ms pauses. Parallel GC uses all available CPU cores during GC, keeping pause times proportional to heap size divided by thread count. It's the right choice when latency-per-request isn't the primary metric.

---

### 🔩 First Principles Explanation

```
Serial GC:       1 GC thread  → pause proportional to heap size
Parallel GC:  N GC threads  → pause proportional to heap size / N

Example: 4GB heap, 10s collection with Serial GC
  Serial:   1 thread × 10s = 10s pause
  Parallel: 8 threads × 10s/8 ≈ 1.25s pause (ideal)

Throughput calculation:
  App runs 59 seconds, GC runs 1 second → throughput = 59/60 ≈ 98%
  Goal: keep GC overhead under 2% → GC pauses < 1/50 of running time

Configuration:
  -XX:+UseParallelGC           → enable (default Java 8)
  -XX:ParallelGCThreads=N      → override thread count (default: CPU count)
  -XX:MaxGCPauseMillis=200     → target max pause (JVM tries to meet it via adaptive sizing)
  -XX:GCTimeRatio=99           → target: GC uses <1% of time (throughput goal)

Adaptive Sizing Policy:
  JVM monitors: pause times, throughput, heap usage
  Adjusts: Eden size, Survivor sizes, Old gen size
  Goal: achieve the configured MaxGCPauseMillis and GCTimeRatio
```

---

### ❓ Why Does This Exist — Why Before What

```
Serial GC problems for multi-core servers:
  Single GC thread on 8-core machine → 7 cores idle during GC!
  GC pause = O(heap / single_thread) → scales poorly with heap size
  Modern servers have 8-64 cores → serial GC leaves them wasted

Parallel GC solves this:
  All N cores work on GC simultaneously → N× speedup (approximate)
  Pause duration reduced; throughput maximised
  Simple, reliable, well-understood

Why G1 GC replaced it as default in Java 9:
  Parallel GC long pauses grow with heap size: 4GB heap → 1-2s pauses
  G1 GC breaks heap into regions → limits pause to bounded chunk
  → Better latency; Parallel GC better raw throughput for batch
```

---

### 🧠 Mental Model / Analogy

> Cleaning a stadium after an event. Serial GC: one cleaner works alone (slow). Parallel GC: the entire cleaning crew arrives simultaneously — all sections cleaned at once. Stadium locked while cleaning (Stop-The-World) but it finishes faster. G1 GC: clean section by section, opening each section as soon as it's done (lower max pause).

---

### ⚙️ How It Works

```
Young Generation (Minor GC — Parallel Scavenge):
  All app threads paused
  N GC threads scan Eden + Survivor roots in parallel
  Live objects copied to To-Survivor space
  Objects too large or too old promoted to Old Gen
  Eden + From-Survivor cleared

Old Generation (Major GC — Parallel Mark-Sweep-Compact):
  All app threads paused
  N GC threads: mark live objects, sweep dead, compact
  Compaction moves all live objects to one end → no fragmentation

Adaptive Sizing:
  After each GC cycle: JVM checks if pause goal met
  Increase/decrease Eden/Survivor/OldGen sizes accordingly
  Smooths out over time to meet throughput + pause targets
```

---

### 🔄 How It Connects

```
Parallel GC
  ├─ vs Serial GC  → N threads (faster) vs 1 thread (smaller)
  ├─ vs G1 GC      → Parallel = throughput-first; G1 = latency-first (regions)
  ├─ vs ZGC        → ZGC concurrent; Parallel = full STW; ZGC far lower pauses
  ├─ Default in    → Java 8 (replaced by G1 in Java 9+)
  └─ Use case      → batch processing, analytics, build systems
```

---

### 💻 Code Example

```bash
# Enable Parallel GC (explicit, or implicit in Java 8)
java -XX:+UseParallelGC \
     -Xms4g -Xmx4g \
     -XX:ParallelGCThreads=8 \
     -XX:MaxGCPauseMillis=500 \
     -XX:GCTimeRatio=19 \          # target: GC < 1/(1+19) = 5% of time
     -Xlog:gc*:file=gc.log \
     -jar myapp.jar

# Monitor GC:
# jstat -gcutil <pid> 1000         → GC stats every 1s
# jcmd <pid> GC.heap_info          → current heap breakdown
# -Xlog:gc*                        → verbose GC logging (Java 11+)
```

```java
// Programmatic heap monitoring (works with any GC)
for (GarbageCollectorMXBean gc : ManagementFactory.getGarbageCollectorMXBeans()) {
    System.out.printf("GC: %-30s  Collections: %5d  Time: %dms%n",
        gc.getName(), gc.getCollectionCount(), gc.getCollectionTime());
}
// ParallelGC output:
// GC: PS Scavenge (Young)    Collections:   234  Time: 890ms
// GC: PS MarkSweep (Old)     Collections:     3  Time: 1450ms
```

---

### ⚠️ Common Misconceptions

| ❌ Wrong Belief | ✅ Correct Reality |
|---|---|
| Parallel GC has no Stop-The-World pauses | Parallel GC is fully Stop-The-World; "parallel" = multiple GC threads, not concurrent |
| More GC threads always = shorter pauses | Thread coordination overhead; 32 threads on a 4GB heap may be worse than 8 |
| Parallel GC is deprecated | Still available and actively used for batch/throughput-sensitive workloads |
| `-XX:MaxGCPauseMillis=100` guarantees 100ms max | JVM tries to meet it via adaptive sizing; not a hard guarantee |

---

### 🔗 Related Keywords

- **[Serial GC](./025 — Serial GC.md)** — single-threaded predecessor
- **[G1 GC](./027 — G1 GC.md)** — replaced Parallel GC as default in Java 9
- **[Stop-The-World](./024 — Stop-The-World (STW).md)** — the pause mechanism Parallel GC uses
- **[Young Generation](./018 — Young Generation.md)** — where Minor GC runs

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────────┐
│ KEY IDEA     │ N GC threads run in parallel during STW;      │
│              │ pause = heap / N; maximises throughput        │
├──────────────┼───────────────────────────────────────────────┤
│ USE WHEN     │ Batch jobs, analytics, build systems — where  │
│              │ total throughput > per-request latency        │
├──────────────┼───────────────────────────────────────────────┤
│ AVOID WHEN   │ Latency-sensitive services (use G1/ZGC);      │
│              │ very large heaps (10GB+) → pauses too long    │
├──────────────┼───────────────────────────────────────────────┤
│ ONE-LINER    │ "All cleaners work at once — parking lot      │
│              │  still closed, but done faster"               │
├──────────────┼───────────────────────────────────────────────┤
│ NEXT EXPLORE │ G1 GC → ZGC → Shenandoah →                   │
│              │ GC Tuning → jstat → GC logs                  │
└──────────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** Parallel GC uses adaptive sizing to achieve the `MaxGCPauseMillis` target. If load spikes cause allocation rate to increase dramatically, what does adaptive sizing do to Eden size? How does this affect Minor GC frequency vs pause duration?

**Q2.** You have a batch job processing 500GB of data with a 32GB heap. Parallel GC pauses are 8 seconds. Would switching to G1 GC necessarily improve total batch completion time? What are the trade-offs?

**Q3.** `-XX:GCTimeRatio=19` means GC should take less than 5% of total runtime. How does the JVM enforce this goal? What happens to heap sizing when GC time exceeds the ratio?

