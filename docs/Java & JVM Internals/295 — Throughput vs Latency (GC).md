---
layout: default
title: "Throughput vs Latency (GC)"
parent: "Java & JVM Internals"
nav_order: 295
permalink: /java/throughput-vs-latency-gc/
number: "295"
category: Java & JVM Internals
difficulty: ★★★
depends_on: GC Pause, G1GC, ZGC, GC Tuning, Stop-The-World (STW)
used_by: GC Tuning
tags:
  - java
  - jvm
  - gc
  - performance
  - internals
  - deep-dive
---

# 295 — Throughput vs Latency (GC)

`#java` `#jvm` `#gc` `#performance` `#internals` `#deep-dive`

⚡ TL;DR — The fundamental GC trade-off: maximising CPU time for application work (throughput) versus minimising individual pause durations (latency) — you cannot fully optimise both simultaneously.

| #295 | Category: Java & JVM Internals | Difficulty: ★★★ |
|:---|:---|:---|
| **Depends on:** | GC Pause, G1GC, ZGC, GC Tuning, Stop-The-World (STW) | |
| **Used by:** | GC Tuning | |

---

### 📘 Textbook Definition

In garbage collection, **throughput** refers to the fraction of total application time spent executing application code rather than performing GC — expressed as `1 - (GC time / elapsed time)`. **Latency** refers to the maximum stop-the-world pause duration observed per GC event. These goals are in fundamental tension: maximising throughput typically requires longer but less frequent GC cycles, while minimising latency requires shorter but more frequent collections, spending more total CPU on GC overhead. Garbage collector selection and configuration determines where on this trade-off spectrum the JVM operates.

### 🟢 Simple Definition (Easy)

Throughput means your app does as much work as possible total; latency means each individual request responds quickly. GC can't perfectly maximise both at once — more of one usually means less of the other.

### 🔵 Simple Definition (Elaborated)

Think of it this way: you can clean your apartment once a week in one long session (high throughput — most time living normally, but one day everything stops) or you can tidy for 5 minutes every hour (low individual disruption but constant overhead). GC faces the same choice. A throughput collector (Parallel GC) runs large, infrequent collections — 95% CPU for your app, but occasional 2-second pauses. A low-latency collector (ZGC) does tiny pauses constantly in the background — pauses under 1ms, but 5–10% of CPU always consumed by concurrent GC work.

### 🔩 First Principles Explanation

**The source of tension:**

Concurrent GC (ZGC, G1 background phases, Shenandoah) performs marking and relocation while application threads run. This eliminates long pauses but:
1. **CPU competition:** GC threads compete with application threads for CPU cores. On an 8-core machine with 4 concurrent GC threads, application gets ~50% of CPU.
2. **Memory overhead:** Concurrent collectors need headroom — the application keeps allocating while the GC is still collecting. Requires 2–3× live-set headroom vs. Parallel GC's 1.5×.
3. **Write barriers:** Every object reference write must notify the GC (card table update, SATB buffer). This adds per-store overhead.

**Throughput collector (Parallel GC) approach:**
- Run application 100% of the time until heap is full.
- Stop everything. Collect all garbage in parallel. Compact.
- Resume. Repeat.
- Result: ~99% application CPU. Pause: scales with live data.

**Low-latency collector (ZGC) approach:**
- Run GC concurrently always, slightly consuming CPU.
- Application paused only for brief root scans (< 1ms).
- Result: ~90–95% application CPU. Pause: < 1ms.

**Quantifying the trade-off:**
```
Metric               Parallel GC   G1GC (200ms)   ZGC
──────────────────────────────────────────────────────
App throughput       ~99%          ~94-97%         ~90-95%
Max GC pause         1-5 seconds   50-300ms        < 1ms
GC CPU overhead      ~1%           ~4-6%           ~5-10%
Heap overhead        1.5× live     2× live         2.5-3× live
Fragmentation        None          Minimal         None
```

**The footprint dimension:** Some sources cite a "three-way trade-off": throughput, latency, AND footprint (heap size). Minimising all three simultaneously is impossible — this is Java's "GC Trilemma."

### ❓ Why Does This Exist (Why Before What)

WITHOUT understanding this trade-off:

- Teams choose ZGC "because it's newest and best" for a batch processor — and waste 10% CPU on concurrent GC with no latency benefit.
- Teams use Parallel GC for a REST API — and get 3-second P99.9 pauses failing SLAs.
- Teams throw more heap at a problem that needs a different collector.

What breaks without it:
1. Mis-matched collector choice makes a service worse-off than the default.
2. Tuning contradictions: trying to reduce pause time on Parallel GC is like trying to make a freight train fast — wrong vehicle for the job.

WITH this understanding:
→ Collector selection aligned with workload type from the start.
→ Tuning effort focused on the right metric for the right collector.
→ SLA contracts written with GC characteristics in mind.

### 🧠 Mental Model / Analogy

> The throughput vs. latency trade-off in GC is like choosing between two cleaning services. **Parallel GC:** a deep cleaning crew comes once a month — the house is fully cleaned in one 4-hour session, but nobody can be home during cleaning. **ZGC:** a live-in assistant tidies throughout the day — the house is always presentable, but the assistant always occupies one room and you always hear some activity. For a hotel (high-throughput batch), monthly deep cleaning is ideal. For a home with constant visitors (latency-sensitive API), the live-in assistant is far better despite the ongoing overhead.

"Hotel" = batch/throughput workload, "home with constant visitors" = latency-sensitive API, "monthly deep cleaning" = Parallel GC, "live-in assistant" = ZGC.

The trade-off is about total value delivered per unit time, not absolute performance.

### ⚙️ How It Works (Mechanism)

**Throughput-optimised configuration (Parallel GC):**

```bash
# Maximum throughput for batch processing
java -XX:+UseParallelGC \
     -Xms8g -Xmx8g \
     -XX:GCTimeRatio=19 \    # target: 95% app / 5% GC
     -XX:ParallelGCThreads=8 \
     -jar batch-processor.jar
```

**Latency-optimised configuration (ZGC on Java 21):**

```bash
# Ultra-low latency for API service
java -XX:+UseZGC \
     -XX:+ZGenerational \
     -Xms6g -Xmx12g \      # generous headroom for concurrency
     -XX:ConcGCThreads=4 \
     -XX:MaxGCPauseMillis=5 \
     -jar api-service.jar
```

**Balanced (G1GC — default):**

```bash
# Good default for most microservices
java -XX:+UseG1GC \
     -Xms4g -Xmx4g \
     -XX:MaxGCPauseMillis=200 \
     -XX:GCTimeRatio=9 \    # target: 90% app / 10% GC
     -jar microservice.jar
```

**Decision matrix:**

```
Workload Type          Primary SLO        Recommended
─────────────────────────────────────────────────────
Batch job              ops/sec            Parallel GC
CLI tool               completion time    Serial or Parallel
Microservice API       P99 < 100ms        G1GC (default)
Trading / gaming       P99.9 < 5ms        ZGC or Shenandoah
In-memory database     P99.99 < 1ms       ZGC (Java 21)
Embedded / IoT         RAM footprint      Serial GC
```

### 🔄 How It Connects (Mini-Map)

```
Application SLO defined
  (throughput target OR latency target)
            ↓
Throughput vs Latency (GC) ← you are here
            ↓
      ┌─────────────────┐
      │ Throughput need │ → Parallel GC
      │ Balanced need   │ → G1GC
      │ Latency need    │ → ZGC / Shenandoah
      └─────────────────┘
            ↓
GC Tuning (collector-specific flag tuning)
            ↓
GC Logs → validate → iterate
```

### 💻 Code Example

Example 1 — Measuring actual GC overhead in a running service:

```java
import java.lang.management.*;
import java.util.List;

public class GCOverheadMonitor {
    public static double getGCOverheadPercent() {
        long totalGCTime = 0;
        List<GarbageCollectorMXBean> gcBeans =
            ManagementFactory.getGarbageCollectorMXBeans();
        for (GarbageCollectorMXBean gc : gcBeans) {
            long time = gc.getCollectionTime();
            if (time > 0) totalGCTime += time;
        }
        // Divide by JVM uptime for percentage
        long uptime =
            ManagementFactory.getRuntimeMXBean()
                             .getUptime();
        return (double) totalGCTime / uptime * 100.0;
    }

    // Alert if GC overhead > 10%
    public static void checkGCHealth() {
        double overhead = getGCOverheadPercent();
        if (overhead > 10.0) {
            System.err.printf(
                "ALERT: GC overhead %.1f%% exceeds 10%%%n",
                overhead);
        }
    }
}
```

Example 2 — Benchmark comparing Parallel vs ZGC for different workloads:

```bash
# Throughput benchmark: Parallel GC
java -XX:+UseParallelGC -Xmx8g -jar throughput-bench.jar
# Result: 125,000 ops/sec, max pause 2100ms

# Throughput benchmark: ZGC
java -XX:+UseZGC -XX:+ZGenerational -Xmx12g \
     -jar throughput-bench.jar
# Result: 118,000 ops/sec, max pause 0.8ms
# Trade-off: 6% throughput loss for 2600x pause reduction
```

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| Low-latency collectors have higher total throughput | Concurrent collectors consume extra CPU for background GC work; total application throughput is lower than Parallel GC for the same workload. |
| G1GC's MaxGCPauseMillis reduces GC overhead | Reducing the pause target causes G1 to collect less per cycle (smaller CSet), potentially increasing GC frequency and total overhead. |
| More heap improves both throughput and latency | Larger heaps reduce GC frequency (throughput benefit) but increase individual pause duration for STW-heavy collectors (latency cost). |
| Throughput and latency are always in opposition | With modern hardware and concurrent collectors, you can often improve both by simply choosing the right collector and sizing heap correctly. |
| GC throughput and application throughput are the same | GC throughput = fraction of time NOT in GC. Application throughput = useful work done. Application CPU efficiency matters too. |
| ZGC is always better than G1GC | For batch workloads, G1GC or Parallel GC often delivers higher absolute throughput. "Better" depends entirely on workload and SLO. |

### 🔥 Pitfalls in Production

**1. Using Parallel GC for Latency-Sensitive APIs**

```bash
# BAD: Parallel GC for HTTP API service
java -XX:+UseParallelGC -Xmx8g -jar api.jar
# → Periodic 2-second Full GC pauses → P99.9 = 2100ms
# → SLA breached; load balancer may mark instance unhealthy

# GOOD: Switch to G1GC or ZGC
java -XX:+UseG1GC -XX:MaxGCPauseMillis=100 -Xmx8g -jar api.jar
```

**2. Using ZGC for a Pure Batch Processor**

```bash
# BAD: ZGC for batch job processing billions of records
java -XX:+UseZGC -Xmx16g -jar batch.jar
# → 8-10% CPU wasted on concurrent GC background threads
# → Batch finishes 9% slower than with Parallel GC

# GOOD: Parallel GC for batch — pauses don't matter for batch
java -XX:+UseParallelGC -Xmx16g -jar batch.jar
```

**3. Tuning Pause Time Without Accounting for Concurrent CPU Cost**

```bash
# BAD: On a 2-vCPU container, using 2 ConcGCThreads for ZGC
# → 50% of CPU consumed by GC threads continuously
# → Application effectively has 1 vCPU

# GOOD: Scale ConcGCThreads to available cores
# ZGC: 1-2 concurrent threads suffice for 2-vCPU containers
-XX:ConcGCThreads=1  # for constrained containers
```

### 🔗 Related Keywords

- `GC Pause` — the latency dimension of this trade-off.
- `G1GC` — the balanced default collector; tunable on both axes.
- `ZGC` — optimises fully for latency at some throughput cost.
- `Parallel GC` — optimises fully for throughput at latency cost.
- `GC Tuning` — the process of moving along the throughput-latency curve.
- `GC Logs` — quantifies actual throughput (GC overhead%) and latency (pause times).

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ KEY IDEA     │ Throughput = max app CPU; Latency = min   │
│              │ pause. Concurrent GC trades one for other.│
├──────────────┼───────────────────────────────────────────┤
│ USE WHEN     │ Choosing a GC collector or setting pause  │
│              │ targets — always know your primary SLO.   │
├──────────────┼───────────────────────────────────────────┤
│ AVOID WHEN   │ Optimising both simultaneously without    │
│              │ measurement — choose ONE primary SLO.     │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "Parallel GC: work hard, rest hard.       │
│              │ ZGC: always on, never noticed."           │
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ GC Tuning → Finalization → JIT Compiler   │
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** A team runs two Java services on the same 8-core, 32 GB machine: a batch processor and a REST API. Both use G1GC with default settings, each configured with `-Xmx12g`. The batch processor finishes 20% faster on a weekend test when the API has reduced traffic. Design the optimal GC strategy for this co-located setup, including collector selection and CPU allocation, assuming you cannot split these services onto separate machines.

**Q2.** The Parallel GC achieves higher throughput than ZGC on identical hardware. However, at exactly which point does a workload's requirements flip the cost-benefit analysis in favour of ZGC — even for a batch-style job that produces no user-facing responses? Consider SLA, dependent service timeouts, and operational monitoring complexity in your reasoning.

