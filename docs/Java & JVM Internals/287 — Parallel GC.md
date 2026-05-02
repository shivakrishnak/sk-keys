---
layout: default
title: "Parallel GC"
parent: "Java & JVM Internals"
nav_order: 287
permalink: /java/parallel-gc/
number: "0287"
category: Java & JVM Internals
difficulty: ★★☆
depends_on:
  - Serial GC
  - Young Generation
  - Old Generation
  - Stop-The-World (STW)
  - Full GC
used_by:
  - GC Tuning
  - Throughput vs Latency (GC)
  - GC Logs
related:
  - Serial GC
  - CMS (Concurrent Mark Sweep)
  - G1GC
  - GC Tuning
  - Throughput vs Latency (GC)
tags:
  - jvm
  - garbage-collection
  - memory-management
  - java-internals
  - throughput
---

# 0287 — Parallel GC

## 1. TL;DR
> **Parallel GC** (also called Throughput Collector) uses **multiple GC threads** running in parallel to perform garbage collection, but still applies **Stop-The-World** for every phase. It maximizes application throughput by finishing GC faster (using all CPU cores) while minimizing total GC overhead, at the cost of potentially long individual pauses. It was the default GC from Java 7 to Java 8.

---

## 2. Visual: How It Fits In

```
Parallel GC — Multi-threaded, Stop-The-World

Application threads:
T1: ──────────────┤          PAUSED          ├────────────────
T2: ──────────────┤          PAUSED          ├────────────────
T3: ──────────────┤          PAUSED          ├────────────────
T4: ──────────────┤          PAUSED          ├────────────────

GC threads (multiple, run in parallel during STW):
GC1:            ──┤  Mark region A  │  Copy A ├──
GC2:            ──┤  Mark region B  │  Copy B ├──
GC3:            ──┤  Mark region C  │  Copy C ├──
GC4:            ──┤  Mark region D  │  Copy D ├──
                                ^^^^^^^^
                        All finish sooner than 1 thread

vs Serial GC (1 GC thread, same wall clock pause):
GC1:     ──┤  Mark A,B,C,D  │  Copy A,B,C,D  │ (much longer) ├──
```

---

## 3. Core Concept

Parallel GC uses the same phases as Serial GC (Mark-Copy for Young, Mark-Sweep-Compact for Old), but runs them with **N parallel GC threads** (default: number of CPU cores up to 8, then 5/8 of cores). This means:

- STW pause **wall-clock time** is shorter (work done faster by multiple threads)
- **CPU utilization** during GC is maximized
- **Application throughput** (app time / total time) is higher

Parallel GC prioritizes **throughput** over **latency** — it may pause for longer individual collections than G1GC, but spends less total time on GC overhead.

### JVM flags:
```bash
-XX:+UseParallelGC            # Enable Parallel GC
-XX:ParallelGCThreads=N       # Number of GC threads
```

---

## 4. Why It Matters

Parallel GC was the production standard from Java 5–8 for batch processing, data pipelines, and high-throughput services where latency variance was acceptable. It remains the right choice for:

- Batch/ETL workloads
- Single long-running jobs where throughput > latency
- Environments where maximizing application work per second matters more than minimizing any single pause

Understanding Parallel GC bridges the gap between Serial GC's simplicity and the more complex concurrent collectors.

---

## 5. Key Properties / Behavior Table

| Property | Value |
|----------|-------|
| GC threads | Multiple (default = num CPUs up to 8, then 5/8 CPUs) |
| Application threads during GC | Suspended (STW) |
| Young Gen algorithm | Parallel Mark-Copy |
| Old Gen algorithm | Parallel Mark-Sweep-Compact |
| JVM flag | `-XX:+UseParallelGC` |
| Default in | Java 7, Java 8 |
| Best for | Throughput-critical batch workloads |
| Footprint | Low (minimal metadata) |
| Throughput | Highest of STW-only collectors |
| Worst-case pause | Large heap → minutes (but shorter than Serial) |

---

## 6. Real-World Analogy

> Instead of one cleaning crew member (Serial GC), the office now hires a full team. During cleaning time, the office still must empty out (STW) — but four cleaners working simultaneously finish the job four times faster. The total downtime is shorter, and the cleaning team can handle bigger offices. However, the office is still completely empty during cleaning — no one can do any work until the entire team is done.

---

## 7. How It Works — Step by Step

```
Minor GC (Young Generation):
1. STW begins — all application threads paused
2. N GC threads spawn
3. Each GC thread claims a region of Eden/Survivor
4. Parallel mark: identify live objects in parallel
5. Parallel copy: copy live objects to next Survivor/Old
6. GC threads synchronize at completion barrier
7. STW ends — application threads resume

Full GC (Old Generation):
1. STW begins
2. N GC threads spawn
3. Parallel mark phase: concurrent marking of live objects
4. Parallel sweep: identify dead objects
5. Parallel compact: move live objects (complex due to coordination)
6. Metaspace collection
7. STW ends
```

---

## 8. Under the Hood (Deep Dive)

### Thread count calculation

```
Default ParallelGCThreads:
- If ncpus <= 8: ParallelGCThreads = ncpus
- If ncpus > 8:  ParallelGCThreads = 8 + (ncpus - 8) * 5 / 8

Examples:
  4 CPUs  → 4 GC threads
  8 CPUs  → 8 GC threads
  16 CPUs → 8 + (16-8) * 5/8 = 8 + 5 = 13 GC threads
  32 CPUs → 8 + (32-8) * 5/8 = 8 + 15 = 23 GC threads

Override with: -XX:ParallelGCThreads=N
```

### Parallel compaction (PSOL)

```
Parallel Scavenge Old (PSOL) — Old Gen compaction in Parallel GC:

1. Summary phase (single thread, fast):
   - Divide Old Gen into fixed-size regions
   - For each region, compute: "if we compact to here, what's density?"
   - Identify "dense" regions (keep in place) vs "sparse" (relocate)

2. Compact phase (parallel):
   - Multiple threads each handle a separate dense prefix region
   - Objects in sparse regions moved to fill dense regions
   - References updated in parallel

Key: Regions are independent → true parallelism during compaction
```

### Adaptive sizing (ergonomics)

```
Parallel GC implements "GC ergonomics" — auto-tuning:

Goals (in priority order):
  1. Maximum GC pause < -XX:MaxGCPauseMillis (default: no limit)
  2. Throughput goal: GC time < 1/(1 + GCTimeRatio) of total
     -XX:GCTimeRatio=99 means: GC time < 1% (99:1 ratio)
  
Based on these goals, JVM auto-adjusts:
  - Young Gen size (up/down)
  - Old Gen size (up/down)
  - Survivor ratio
  - Tenuring threshold

To disable auto-sizing: -XX:-UseAdaptiveSizePolicy
```

### Parallel GC vs G1GC performance

```
Throughput benchmark (batch processing, large dataset):
  Parallel GC:  95% app time, 5% GC    ← throughput king
  G1GC:         90% app time, 10% GC   ← more GC overhead
  ZGC:          85% app time, 15% GC   ← highest overhead

Latency (P99 pause):
  Parallel GC:  500ms–5s               ← unacceptable for APIs
  G1GC:         50–200ms               ← acceptable for most
  ZGC:          < 1ms                  ← latency champion
```

---

## 9. Comparison Table

| Feature | Serial GC | Parallel GC | G1GC | ZGC |
|---------|-----------|-------------|------|-----|
| GC threads | 1 | N (parallel) | N | N (concurrent) |
| STW | All phases | All phases | Partial | Minimal |
| Throughput | Moderate | **Best** | Good | Good |
| P99 latency | Worst | Bad | Good | Excellent |
| Heap size | < 100MB | Up to 8GB | Up to 32GB+ | Up to 16TB |
| Default Java version | - | Java 7–8 | Java 9+ | Opt-in |

---

## 10. When to Use / Avoid

| Scenario | Guidance |
|----------|----------|
| ETL batch jobs, offline processing | ✅ Parallel GC — throughput first |
| Hadoop/Spark worker nodes | ✅ Parallel GC (batch-oriented) |
| APIs with latency SLAs | ❌ Avoid — use G1/ZGC |
| Interactive applications | ❌ Avoid — pauses too long |
| Old Java 8 apps (legacy) | May already be using this by default |

---

## 11. Common Pitfalls & Mistakes

```
❌ Using Parallel GC for web services expecting low latency
   → Long STW pauses cause HTTP timeouts and poor user experience

❌ Not setting GCTimeRatio correctly
   → Default may allow too much GC overhead; tune for your workload

❌ Setting ParallelGCThreads too high on shared hosts
   → GC threads compete with app threads; can starve application

❌ Assuming Parallel GC equals G1GC
   → Parallel GC has NO concurrent phases; G1 does
```

---

## 12. Code / Config Examples

```bash
# Enable Parallel GC (Java 8 style)
-XX:+UseParallelGC

# Also enable parallel Old Gen collection (default in Java 7+)
-XX:+UseParallelOldGC

# Set explicit GC thread count
-XX:ParallelGCThreads=8

# Throughput goal: GC < 1% of total time
-XX:GCTimeRatio=99

# Heap sizing
-Xms4g -Xmx8g

# Log GC events
-Xlog:gc*:file=parallel-gc.log:time,uptime

# Disable adaptive sizing (for predictable sizing)
-XX:-UseAdaptiveSizePolicy

# Sample Parallel GC log:
# [0.234s][info][gc] GC(0) Pause Young (Allocation Failure) 256M->64M(512M) 45.234ms
# [5.678s][info][gc] GC(1) Pause Young (Allocation Failure) 512M->128M(1024M) 67.891ms
# [15.234s][info][gc] GC(2) Pause Full (Ergonomics) 2048M->512M(4096M) 3456.789ms
```

---

## 13. Interview Q&A

**Q: What is Parallel GC and how does it differ from Serial GC?**
> Parallel GC uses multiple threads to perform garbage collection instead of a single thread. Both are fully Stop-The-World, but Parallel GC completes GC work faster by parallelizing mark, copy, and compaction phases. This reduces pause duration (wall-clock) and increases throughput compared to Serial GC.

**Q: Was Parallel GC the default in Java 8?**
> Yes. `-XX:+UseParallelGC` was the default from Java 7 through Java 8. In Java 9, G1GC became the default. Many applications running on Java 8 may still be using Parallel GC without explicit configuration.

**Q: When would you choose Parallel GC over G1GC?**
> For pure throughput batch workloads (ETL, data processing, overnight jobs) where individual pause times don't matter, only total GC overhead matters. Parallel GC minimizes total GC time spent at the cost of potentially long individual pauses.

---

## 14. Flash Cards

| Front | Back |
|-------|------|
| How many threads does Parallel GC use? | N threads (default = CPUs up to 8, then 5/8 of remaining) |
| Was Parallel GC the Java 8 default? | Yes (default changed to G1GC in Java 9) |
| JVM flag to enable | `-XX:+UseParallelGC` |
| What does GCTimeRatio control? | Ratio of app time to GC time (99 = GC < 1%) |
| What makes Parallel GC different from G1? | Parallel GC is fully STW; G1 has concurrent phases |

---

## 15. Quick Quiz

**Question 1:** On a 16-CPU machine, how many GC threads does Parallel GC use by default?

- A) 16
- B) 8
- C) ✅ 13 (8 + (16-8) × 5/8 = 13)
- D) 4

**Question 2:** Parallel GC is most appropriate for:

- A) Low-latency API with < 50ms P99 SLA
- B) ✅ Overnight batch data processing job
- C) Real-time financial trading system
- D) Interactive mobile backend

---

## 16. Anti-Patterns

```
🚫 Anti-Pattern: Using Parallel GC for high-concurrency API gateway
   Problem:  Pause spikes manifest as 5xx errors and load balancer timeouts
   Fix:      Migrate to G1GC (-XX:+UseG1GC -XX:MaxGCPauseMillis=100)

🚫 Anti-Pattern: Ignoring GCTimeRatio
   Problem:  JVM allows excessive GC overhead; throughput degrades silently
   Fix:      Set -XX:GCTimeRatio=99 and alert when GC overhead > 5%

🚫 Anti-Pattern: Setting ParallelGCThreads = number of app threads
   Problem:  During GC, all requested threads consume CPU for GC work
   Fix:      Keep ParallelGCThreads ≤ half available cores for mixed workloads
```

---

## 17. Related Concepts Map

```
Parallel GC
├── extends ─────────► Serial GC [#286] (adds parallelism)
├── requires ────────► Stop-The-World (STW) [#285]
├── collects ────────► Young Generation [#278]
│                  ──► Old Generation [#281]
├── compared to ─────► G1GC [#289] (adds concurrent phases)
│                  ──► CMS [#288] (concurrent but single-phase)
│                  ──► ZGC [#290] (near-zero STW)
├── optimizes for ───► Throughput vs Latency (GC) [#295]
└── tuned via ───────► GC Tuning [#292]
```

---

## 18. Further Reading

- [Oracle: Parallel Collector](https://docs.oracle.com/en/java/javase/21/gctuning/parallel-collector.html)
- [Java GC Handbook: Parallel GC](https://plumbr.io/handbook/garbage-collection-algorithms-implementations/parallel-gc)
- [GC Ergonomics: Adaptive Sizing](https://docs.oracle.com/javase/8/docs/technotes/guides/vm/gctuning/ergonomics.html)
- [JVM GC Performance Comparison](https://ionutbalosin.com/2020/01/hotspot-jvm-performance-tuning-guidelines/)

---

## 19. Human Summary

Parallel GC was Java's workhorse GC for a decade. By throwing more CPU cores at the stop-the-world problem, it slashed GC pause time compared to Serial GC and maximized throughput for batch workloads. The tradeoff is that it's still completely stop-the-world — great for nightly batch jobs that no one watches, terrible for real-time APIs where every pause is a user experience event.

Modern Java defaults to G1GC (Java 9+), but understanding Parallel GC helps you recognize when you're running a legacy Java 8 app that might be silently running a throughput-tuned collector on a latency-sensitive workload. It also gives you a clear baseline for appreciating what's fundamentally needed in GC design: "what if we used all the CPUs?"

---

## 20. Tags

`jvm` `garbage-collection` `memory-management` `java-internals` `throughput` `parallel-gc`

