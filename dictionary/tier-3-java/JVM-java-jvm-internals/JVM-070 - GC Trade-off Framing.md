---
id: JVM-073
title: GC Trade-off Framing
category: Java & JVM Internals
tier: tier-3-java
folder: JVM-java-jvm-internals
difficulty: ★★★
depends_on: JVM-038, JVM-039, JVM-040, JVM-043
used_by:
related: JVM-059, JVM-065
tags:
  - jvm
  - java
  - gc
  - tradeoff
  - mental-model
status: complete
version: 2
layout: default
parent: "Java & JVM Internals"
grand_parent: "Technical Dictionary"
nav_order: 70
permalink: /jvm/gc-trade-off-framing/
---

# JVM-070 - GC Trade-off Framing

**⚡ TL;DR** - GC algorithm selection is a three-axis trade-off (throughput, pause time, memory footprint); no algorithm wins all three, and workload classification drives the right choice.

| Field | Value |
|---|---|
| **Depends on** | [[JVM-038 - G1GC]], [[JVM-039 - ZGC]], [[JVM-040 - Shenandoah]], [[JVM-043 - Parallel GC]] |
| **Used by** | (none - terminal synthesis entry) |
| **Related** | [[JVM-059 - GC Tuning Strategy for Production JVMs]], [[JVM-065 - GC Algorithm Design Principles]] |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
An engineer is asked "which GC should we use?" and answers "G1GC because that's the default." A colleague switches to ZGC because they heard "ZGC is faster." Another uses Parallel GC because "throughput is most important." None of them can explain why their choice is correct for their specific workload. When latency regressions or OOM events occur, they tune GC flags randomly rather than systematically.

**THE BREAKING POINT:**
Without a decision framework, GC selection is cargo cult: copy what others do without understanding the trade-offs. The consequences: a latency-critical trading system on Parallel GC suffers 500ms pauses that cause order timeouts. A high-throughput batch processor on ZGC wastes 15% CPU on background GC threads. A memory-constrained container on G1GC consumes 400MB more than necessary for remembered sets. Each mismatch has a real cost.

**THE INVENTION MOMENT:**
The GC trade-off triangle (throughput vs pause time vs footprint) is the canonical framing. It asserts: given current GC technology, you can optimise any two axes but not all three simultaneously. Serial GC optimises footprint. Parallel GC optimises throughput. ZGC/Shenandoah optimise pause time. G1GC finds a practical balance between all three. Knowing where your workload sits on this triangle determines the correct algorithm.

**EVOLUTION:**
- 1996: Serial GC only; trade-off awareness not needed (only one option)
- 1999: Parallel GC; first explicit throughput-vs-simplicity choice
- 2002: CMS; first throughput-vs-pause-time choice (CMS is now removed)
- 2009: G1GC; balanced choice becomes available
- 2018: ZGC; sub-10ms pause time becomes achievable at production scale
- 2021: ZGC Generational (JDK 21); lower footprint + lower pause simultaneously
- 2024: G1GC and ZGC continue improving; Shenandoah matures in OpenJDK

---

### 📘 Textbook Definition

**GC trade-off framing** is the analytical framework for selecting a garbage collector by mapping workload characteristics to the GC algorithm that best satisfies them. The three primary trade-off axes are: (1) **Throughput** - the percentage of CPU time spent on application work (not GC); higher throughput means more work done per unit time; maximised by Parallel GC. (2) **Pause time** - the maximum or 99th percentile duration of application thread stops due to GC; minimised by ZGC/Shenandoah. (3) **Memory footprint** - the total RAM consumed by GC metadata (remembered sets, mark bitmaps, card tables) beyond the live object set; minimised by Serial GC. A fourth practical axis, **warmup sensitivity** (how long until GC performs optimally), matters for serverless and container environments.

---

### ⏱️ Understand It in 30 Seconds

**One line:** GC selection is a three-way trade-off: throughput vs pause time vs footprint - no algorithm wins all three simultaneously.

> Like choosing a vehicle for a trip: sports car (Parallel GC) = maximum speed, uncomfortable for long trips, high fuel consumption; luxury sedan (G1GC) = balanced comfort, speed, efficiency; electric city car (ZGC) = smooth, near-silent, great in traffic jams but not the fastest on highways; bicycle (Serial GC) = minimal fuel cost, fine for short distances, unacceptably slow for long ones.

**One insight:** The workload type determines which axis matters most. Latency-sensitive applications (trading, APIs) need sub-10ms pauses; memory-constrained containers need minimal footprint; batch processors need maximum throughput. Identify the constraint first, then choose the algorithm.

---

### 🔩 First Principles Explanation

**CORE INVARIANTS:**
1. GC must eventually pause to update all references when objects move (unless load barriers used)
2. Concurrent GC threads consume CPU that application threads cannot use
3. GC metadata (remembered sets, mark bitmaps) consumes memory beyond the live set
4. Larger heap gives GC more breathing room but makes Full GC pauses longer when they occur

**DERIVED DESIGN:**
From invariant 1: ZGC and Shenandoah use load barriers (colour bits on references) to permit concurrent relocation. This eliminates STW for most GC work. The cost: 1-3% CPU overhead for the load barrier on every reference read.
From invariant 2: ZGC runs 2-4 background GC threads that consume CPU. For CPU-constrained containers, this matters. Parallel GC does all GC work in short, parallel STW phases - all CPU used when needed, none when not.
From invariant 3: G1GC's per-region remembered sets can consume hundreds of MB for large heaps. ZGC has no per-region remembered sets (generational ZGC uses a simpler structure). On memory-constrained environments, this footprint difference is measurable.

**THE TRADE-OFFS:**
**Gain:** Systematic GC selection eliminates performance mismatches between workload requirements and GC behaviour
**Cost:** Understanding the trade-offs requires knowledge of each GC algorithm's internal design

**ESSENTIAL vs ACCIDENTAL COMPLEXITY:**
**Essential:** The trade-off is real and unavoidable with current technology. A GC that eliminates pauses (ZGC) uses load barriers on every reference read - the pause cost is redistributed to application throughput, not eliminated.
**Accidental:** The large number of GC tuning flags (-XX:G1HeapRegionSize, -XX:ZCollectionInterval, -XX:MaxGCPauseMillis) creates the impression of infinite tuning complexity. The actual decision tree is simple: classify workload, choose algorithm, set Xmx, and accept defaults.

---

### 🧪 Thought Experiment

**SETUP:** You have three services to deploy on the same hardware budget. All three run Java 21. Service A: payment API, SLA is p99 < 50ms. Service B: nightly batch job, processes 10TB of data, must complete within 8 hours. Service C: stateless microservice in a 256MB container.

**WITHOUT A TRADE-OFF FRAMEWORK:**
All three services use G1GC (default). Service A: G1GC mixed GC pauses at 200ms occasionally; payment SLA breached. Service B: G1GC's concurrent marking overhead reduces batch throughput by 10%; runs 9 hours instead of 8. Service C: G1GC remembered set metadata uses 80MB of the 256MB container; frequently OOMKilled.

**WITH TRADE-OFF FRAMEWORK:**
Service A: ZGC (-XX:+UseZGC). Rationale: pause time is the binding constraint. ZGC sub-10ms pauses. p99 latency within SLA.
Service B: Parallel GC (-XX:+UseParallelGC). Rationale: throughput is the binding constraint; pauses acceptable during batch window. Parallel GC maximises throughput; batch completes in 7.5 hours.
Service C: SerialGC (-XX:+UseSerialGC) or ZGC with minimal settings. Rationale: footprint is the binding constraint. Serial GC has minimal GC metadata overhead. Container stays within memory limit.

**THE INSIGHT:**
Each service has ONE binding constraint. Identify it. Choose the GC that optimises for it. The other axes are acceptable trade-offs.

---

### 🧠 Mental Model / Analogy

> Think of GC algorithm selection as choosing a shipping method. Standard shipping (Serial GC): cheapest, slowest, minimal overhead. Express courier (Parallel GC): fast throughput, predictable but not immediate. Same-day delivery (G1GC): balanced cost, speed, reliability. Drone delivery (ZGC/Shenandoah): fastest arrival, uses more fuel (CPU), minimal wait time, but more expensive per delivery. The choice depends on: urgency (pause time constraint), volume (throughput requirement), and budget (memory and CPU budget).

Element mapping:
- Shipping method = GC algorithm
- Delivery urgency = pause time SLA
- Package volume = throughput requirement
- Shipping cost = CPU and memory overhead
- Same-day guarantee = low-pause GC
- Cheapest option = Serial GC minimal footprint

Where this analogy breaks down: shipping methods are interchangeable for the same package. GC algorithms have different operational characteristics at different heap sizes - ZGC is more advantageous at large heaps; Serial GC becomes unacceptable above ~1GB heap.

---

### 📶 Gradual Depth - Four Levels

**Level 1 - What it is (anyone can understand):**
Different Java garbage collectors have different strengths. Some are fastest overall but occasionally pause your program for a long time. Others keep pauses very short but use more CPU in the background. Others use the least memory. You pick based on what your specific application needs most.

**Level 2 - How to use it (junior developer):**
GC selection by workload:
- Web API with latency SLA < 100ms: `-XX:+UseZGC` (Java 15+)
- Batch/data processing, throughput is critical: `-XX:+UseParallelGC`
- Containerised service, memory constrained (<512MB): `-XX:+UseSerialGC`
- General-purpose application: G1GC (default, no flag needed)
- Long-running service, large heap (>8GB): `-XX:+UseZGC` or `-XX:+UseShenandoahGC`

**Level 3 - How it works (mid-level engineer):**
Trade-off quantification: **Throughput**: Parallel GC typically achieves 98%+ throughput (2% GC overhead). G1GC typically 95-97%. ZGC typically 97-99% throughput (load barriers cost 1-3%). **Pause time**: Serial/Parallel GC: 50-2000ms STW depending on heap size. G1GC: 10-200ms for mixed GC; 100ms-seconds for rare Full GC. ZGC: sub-10ms at all heap sizes (JDK 15+). Shenandoah: sub-10ms for most GC work. **Footprint**: Serial GC: ~50MB GC overhead for 4GB heap. G1GC: ~200-400MB for 4GB heap (remembered sets). ZGC: ~100-200MB for 4GB heap. These numbers are approximate and workload-dependent; always measure with JFR on your workload.

**Level 4 - Why it was designed this way (senior/staff):**
The fundamental physics: GC must find all live objects. Finding them requires either (1) stopping all threads (STW) to get a consistent heap snapshot, or (2) using write/load barriers to track mutations while marking concurrently. Option 1 (STW) is simpler, uses no additional CPU during normal application execution, but pauses scale with heap size. Option 2 (concurrent with barriers) adds 1-3% CPU overhead at all times but eliminates pause scaling with heap size. This is the core trade-off between Parallel GC (option 1) and ZGC (option 2). The overhead cost is simply redistributed from burst (STW pause) to continuous (barrier overhead). The workload question becomes: does your SLA prefer occasional bursts of overhead (Parallel GC) or continuous small overhead (ZGC)?

**Expert Thinking Cues:**
- G1GC is the right default because most applications do not have extreme requirements on any single axis
- ZGC should replace G1GC for any latency-sensitive service above Java 15
- The switch from G1GC to ZGC on a latency-critical service is often the single highest-leverage performance change possible

---

### ⚙️ How It Works (Mechanism)

**The GC Trade-off Triangle:**
```
            THROUGHPUT
           /           \
          /  Parallel GC \
         /     (max T)    \
        /------------------\
PAUSE  |                    |  FOOTPRINT
TIME   |      G1GC          |  Serial GC
       |    (balanced)      |  (min F)
        \                  /
         \  ZGC/Shenandoah/
          \    (min P)    /
           \             /
            PAUSE TIME

Pick ANY two. The third axis suffers.
```

**Workload Classification Decision Tree:**
```
What is the primary constraint?

1. "p99 latency must be < 50ms"
   -> PAUSE TIME is binding
   -> Use: ZGC or Shenandoah
   -> Flag: -XX:+UseZGC
   
2. "batch job must complete in N hours"
   -> THROUGHPUT is binding
   -> Pauses acceptable in batch window
   -> Use: Parallel GC
   -> Flag: -XX:+UseParallelGC
   
3. "container memory limit is 512MB"
   -> FOOTPRINT is binding
   -> Use: Serial GC or ZGC with minimal settings
   -> Flag: -XX:+UseSerialGC
   
4. "no extreme constraint"
   -> Use: G1GC (default, no flag needed)
   -> Tune: -XX:MaxGCPauseMillis=200
```

**Cost of switching GC algorithms:**
| From -> To | Expected Change | Risk |
|---|---|---|
| G1GC -> ZGC | p99 latency -50%, throughput -1-3% | Low (well-tested) |
| G1GC -> ParallelGC | throughput +2%, pause time 2-5x longer | High for latency SLA |
| G1GC -> SerialGC | footprint -100-200MB, pauses 5-10x longer | Only for constrained containers |
| Any -> ZGC Generational | pause time stays low, throughput improves | JDK 21+ only |

---

### 🔄 The Complete Picture - End-to-End Flow

**GC SELECTION DECISION FLOW:**
```
  New service or GC performance issue <- YOU ARE HERE
       |
  STEP 1: Classify workload
  -> Latency-sensitive? (p99 SLA < 100ms)
  -> Throughput-critical? (batch, no SLA)
  -> Memory-constrained? (<1GB container)
  -> General? (none of above)
       |
  STEP 2: Choose algorithm
  Latency -> ZGC or Shenandoah
  Throughput -> Parallel GC
  Memory -> Serial GC
  General -> G1GC (default)
       |
  STEP 3: Set Xmx (heap size)
  2x live set (minimum)
  75% container limit (for container)
  More = better for GC throughput
       |
  STEP 4: Enable GC logging + JFR
  Measure: pause time, throughput, footprint
       |
  STEP 5: Tune if needed
  Latency: -XX:ZCollectionInterval (ZGC)
  Throughput: -XX:ParallelGCThreads
  Footprint: -XX:G1HeapRegionSize
       |
  STEP 6: Validate against SLA
  -> p99 pause time vs latency SLA
  -> GC overhead % vs throughput target
  -> GC metadata size vs memory budget
```

**FAILURE PATH:**
- Wrong GC for workload: Parallel GC on API service; first high-traffic day causes 1-second pauses; latency SLA breach
- Insufficient heap: any GC algorithm under heap pressure triggers Full GC; tune Xmx first before changing algorithm
- Ignoring warmup: ZGC has warmup period before reaching steady-state pause times; cold start benchmarks mislead

**WHAT CHANGES AT SCALE:**
At very large heaps (>100GB), ZGC is the only viable option. G1GC's remembered sets become too large; Parallel GC's STW pauses scale with heap size; only ZGC's concurrent approach scales to hundreds of GB.

---

### 💻 Code Example

**BAD - GC selected without workload analysis:**
```bash
# No reasoning - just "copy what everyone uses"
java -XX:+UseG1GC \
     -Xmx4g \
     -jar payment-service.jar
# Payment service has p99 latency SLA of 50ms
# G1GC mixed GC pauses: 200ms
# SLA breached 0.1% of requests
# Root cause: wrong GC for latency-critical workload
```

**GOOD - GC selected from workload classification:**
```bash
# Payment API: latency-sensitive, p99 SLA = 50ms
# Classification: PAUSE TIME is binding constraint
# Decision: ZGC
java -XX:+UseZGC \
     -XX:MaxRAMPercentage=75.0 \
     # ZGC: no tuning needed in most cases
     # Defaults are well-calibrated for modern workloads
     -Xlog:gc*:file=/var/log/gc.log:time,uptime,tags:filecount=5,filesize=20m \
     -XX:StartFlightRecording=disk=true,maxage=48h \
     -jar payment-service.jar

# Batch job: throughput-critical, 8-hour window
# Classification: THROUGHPUT is binding
# Decision: Parallel GC
java -XX:+UseParallelGC \
     -XX:MaxRAMPercentage=75.0 \
     -XX:ParallelGCThreads=8 \
     -Xlog:gc*:file=/var/log/gc.log:time \
     -jar batch-processor.jar
```

**Measuring all three axes with JFR:**
```bash
jcmd <pid> JFR.dump filename=/tmp/gc-metrics.jfr maxage=5m

# In JMC (JDK Mission Control):
# 1. Throughput: GC -> GC Overview
#    -> "GC Pause Duration" total vs total time
#    -> Throughput = (total_time - gc_time) / total_time

# 2. Pause time: GC -> Pauses
#    -> Sort by duration descending
#    -> Note p99 pause time

# 3. Footprint: Memory -> Heap Overview
#    -> Note: "GC" memory vs "Live Set"
#    -> Footprint overhead = GC_memory / Live_Set
```

**Comparing algorithms in same environment:**
```bash
# A/B test: two pods with identical load, different GC
# Pod A: G1GC (baseline)
java -XX:+UseG1GC -Xmx4g -jar service.jar

# Pod B: ZGC (candidate)
java -XX:+UseZGC -Xmx4g -jar service.jar

# Compare: p99 latency (Prometheus),
# CPU usage (cAdvisor), memory usage (cAdvisor)
# GC pause time (GC logs)
# Run for 24h under production traffic
```

**How to test / verify correctness:**
```bash
# Verify GC selection:
java -XX:+PrintCommandLineFlags -version 2>&1 \
  | grep "UseGC\|UseZGC\|UseG1\|UseParallel"

# Measure current GC overhead:
jcmd <pid> GC.heap_info
# Note: "GC" overhead = time in GC / total time

# Quick pause measurement (from GC log):
grep -E "Pause|ms" /var/log/gc.log | tail -20
```

---

### ⚖️ Comparison Table

| Algorithm | Throughput | Pause Time | Footprint | Best Workload |
|---|---|---|---|---|
| Serial GC | 95-97% | 50-2000ms (STW, scales with heap) | Minimal | Small heap, single-core, containers |
| Parallel GC | 97-99% | 50-2000ms (STW, parallel) | Low | Batch, throughput-critical, no latency SLA |
| G1GC (default) | 95-97% | 10-200ms typical | Medium | General purpose, balanced |
| ZGC | 97-99% | < 10ms (concurrent) | Medium | Latency-sensitive, large heap |
| Shenandoah | 96-98% | < 10ms (concurrent) | Medium | Latency-sensitive, OpenJDK |
| Epsilon GC | 100% | None (no GC) | None | Testing/benchmark only - always OOM |
| ZGC Generational | 98-99% | < 5ms | Low-Medium | Latency + throughput, JDK 21+ |

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| "ZGC is always better than G1GC" | ZGC has lower pause times but slightly higher throughput overhead (load barriers). For batch or CPU-constrained workloads, G1GC or Parallel GC may perform better. |
| "G1GC's MaxGCPauseMillis is a hard guarantee" | It is a hint, not a guarantee. G1GC targets the pause time but cannot guarantee it. Full GC (rare) ignores this setting. ZGC provides a true (nearly) hard guarantee via concurrent collection. |
| "More GC threads = faster GC" | Parallel GC threads are used only during STW pauses. More GC threads reduce pause duration but don't affect throughput outside GC. Over-provisioning GC threads wastes CPU on non-GC work. |
| "Serial GC is for legacy systems only" | Serial GC is the correct choice for memory-constrained containers (<512MB) or single-core environments. Its minimal GC metadata overhead is a real advantage in these contexts. |
| "Switching GC algorithms requires extensive tuning" | The first step is always just switch the algorithm and measure. Most workloads require no additional tuning beyond `-Xmx`. Complex GC tuning is needed only after the algorithm choice is validated. |

---

### 🚨 Failure Modes & Diagnosis

**Failure Mode 1: GC algorithm mismatch causing SLA breach**
**Symptom:** API service with p99 < 50ms SLA shows occasional 300ms latency spikes; no application code change
**Root Cause:** G1GC mixed GC pause at 300ms; algorithm wrong for latency SLA
**Diagnostic:**
```bash
grep "Pause Mixed\|Full GC" /var/log/gc.log \
  | awk '{print $NF}' | sort -rn | head -10
# Output: 312ms, 287ms, 198ms...
# Correlate timestamps with latency spikes in APM
```
**Fix:** Migrate to ZGC: `-XX:+UseZGC` (Java 15+); validate with A/B test before fleet rollout
**Prevention:** GC algorithm selection as part of service design; include GC pause p99 in capacity planning

**Failure Mode 2: Parallel GC on latency-sensitive service**
**Symptom:** Batch-tuned service reused as an API; intermittent 1-second+ pauses; p99 latency 100x normal
**Root Cause:** Parallel GC was selected for throughput; API traffic now has latency SLA that Parallel GC cannot meet
**Diagnostic:**
```bash
grep "GC Pause" /var/log/gc.log | awk -F"," '{print $NF}' \
  | sort -rn | head -5
# Output: 1234ms, 987ms, 876ms...
# Parallel GC pauses scale with heap size; 8GB = ~2 second pauses
```
**Fix:** Switch to ZGC; verify p99 latency drops; rollout to fleet
**Prevention:** Different service classes (batch vs API) must use different JVM configurations; never reuse batch JVM config for API services

**Failure Mode 3: Memory container OOM from GC metadata**
**Symptom:** Pod OOMKilled; container shows JVM using 400MB more than `-Xmx` setting
**Root Cause:** G1GC remembered set metadata consuming 300-400MB; not included in Xmx; total JVM RSS exceeds container limit
**Diagnostic:**
```bash
# Check JVM native memory:
jcmd <pid> VM.native_memory summary
# Output: GC category shows remembered set size
# Example:
#   GC (reserved=432MB, committed=432MB)
#   Java Heap (reserved=4096MB, committed=4096MB)
# RSS = Heap + GC + Code Cache + Stack + ...
```
**Fix:** Use container-aware sizing: `Xmx = container_limit * 0.60` (not 0.75) if G1GC; or switch to Serial/ZGC for smaller footprint
**Prevention:** Calculate total JVM RSS = Xmx + GC metadata + Code Cache + Metaspace + thread stacks; set container limit to RSS * 1.15

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**
- [[JVM-038 - G1GC]] - The default GC algorithm
- [[JVM-039 - ZGC]] - The low-pause alternative
- [[JVM-040 - Shenandoah]] - Alternative low-pause GC
- [[JVM-043 - Parallel GC]] - The throughput-optimised GC

**Builds On This (learn these next):**
- (none - synthesis and capstone entry for GC section)

**Alternatives / Comparisons:**
- [[JVM-059 - GC Tuning Strategy for Production JVMs]] - Operational tuning of the chosen algorithm
- [[JVM-065 - GC Algorithm Design Principles]] - Why these trade-offs exist

---

### 📌 Quick Reference Card

```
+--------------------------------------------------+
| WHAT IT IS    | GC algorithm selection framework:|
|               | throughput vs pause vs footprint |
|               | trade-off                         |
+--------------------------------------------------+
| PROBLEM       | Random GC selection causes SLA   |
|               | breaches or resource waste        |
+--------------------------------------------------+
| KEY INSIGHT   | One binding constraint per        |
|               | workload; choose GC that wins     |
|               | on that axis                      |
+--------------------------------------------------+
| USE WHEN      | New service design; GC-related   |
|               | performance problems; migration  |
+--------------------------------------------------+
| AVOID WHEN    | Don't change GC under load;      |
|               | always A/B test first            |
+--------------------------------------------------+
| TRADE-OFF     | Better pause time costs 1-3%     |
|               | throughput; better throughput    |
|               | costs longer pauses              |
+--------------------------------------------------+
| ONE-LINER     | Latency: ZGC; Batch: ParallelGC; |
|               | Memory-constrained: SerialGC;    |
|               | General: G1GC (default)           |
+--------------------------------------------------+
| NEXT EXPLORE  | JVM-059 GC tuning strategy,     |
|               | JVM-065 GC algorithm principles  |
+--------------------------------------------------+
```

**If you remember only 3 things:**
1. Identify the binding constraint first: pause time (ZGC), throughput (Parallel GC), or footprint (Serial GC)
2. G1GC is the correct default for general workloads; no flag needed
3. The GC algorithm switch (G1GC to ZGC) is the single highest-leverage change for latency-sensitive services

**Interview one-liner:** "GC selection is a trade-off: Parallel GC maximises throughput (STW), ZGC minimises pause time (concurrent, load barriers), Serial GC minimises footprint (single-threaded STW), G1GC balances all three. Workload classification determines the binding constraint and therefore the correct algorithm."

---

### 💎 Transferable Wisdom

**Reusable Engineering Principle:** Every system component has multiple performance axes that cannot all be maximised simultaneously. Identify the ONE binding constraint for each use case, optimise for it, and accept the trade-offs on other axes. Multi-axis optimisation without a binding constraint produces mediocre results on all axes.

**Where else this pattern appears:**
- CAP theorem: consistency vs availability vs partition tolerance - distributed systems must identify which two to optimise
- Database indexing: read performance vs write performance vs storage - each index is a trade-off; add only indexes for known query patterns
- Network protocols: TCP (throughput + reliability, higher latency) vs UDP (lower latency, no reliability) - protocol selection maps to the binding constraint of the application

---

### 💡 The Surprising Truth

ZGC's "sub-10ms pause time" claim is technically accurate but potentially misleading. ZGC achieves this by relocating objects concurrently using "coloured pointers" - reference bits encode GC state. Every reference dereference in application code requires a load barrier: check the colour bits, and if stale, follow a forwarding pointer to the new location. This barrier adds 1-3 nanoseconds to every reference load in the application. For allocation-heavy code with billions of reference loads per second, this is a measurable (1-3%) throughput overhead that is permanent and unavoidable. Parallel GC has zero throughput overhead during normal execution but periodically pauses for STW collection. The "cost" of ZGC's low pause time is thus paid continuously, not in burst. For most applications, 1-3% continuous overhead is much better than occasional 200ms pauses. But for CPU-bound workloads where every nanosecond counts, Parallel GC's burst-pause model may actually result in higher average throughput despite the occasional pause.

---

### 🧠 Think About This Before We Continue

**Q1 (Design Trade-off):** ZGC uses coloured pointers (bits in the reference value) to track GC state. This approach requires that the JVM's pointer representation uses bits that are not needed for the actual address. On a 64-bit platform, object pointers only need ~44 bits (16TB addressable heap). ZGC uses the remaining bits for GC colour. What is the maximum heap size ZGC can address, and what happens to ZGC if you need a heap larger than this limit?
*Hint:* Research ZGC's documented maximum heap size and the relationship between coloured pointer design and addressable memory range. Consider: if ZGC adds 4 colour bits to a 64-bit pointer, how many bits remain for the actual address?

**Q2 (Scale):** You are running a global trading system with latency requirements of p99.9 < 10ms. You deploy ZGC and achieve p99 < 5ms. But p99.9 is still occasionally 15ms. ZGC's documented pause time is < 10ms. What causes p99.9 ZGC pauses to sometimes exceed the documented sub-10ms guarantee, and what combination of JVM flags and application design changes would reduce p99.9 to < 10ms?
*Hint:* Research ZGC's "load spike" handling, safepoint time-to-reach (TTSP) contribution to apparent pause times, and `-XX:ZCollectionInterval` - note that TTSP is not part of GC pause time but still contributes to application latency.

**Q3 (First Principles):** Project Valhalla aims to introduce "value types" - objects stored by value on the stack or in arrays without heap allocation overhead. If value types succeed, how does this change the GC trade-off triangle? Specifically, if a large class of short-lived objects no longer needs heap allocation, which axis of the triangle improves and by how much?
*Hint:* Consider the relationship between allocation rate, Eden fill rate, minor GC frequency, and CPU overhead. If 50% of allocations are eliminated by value types, what happens to each axis of the throughput/pause/footprint triangle?
