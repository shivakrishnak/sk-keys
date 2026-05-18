---
id: JVM-066
title: Heap Sizing and Memory Planning Strategy
category: Java & JVM Internals
tier: tier-3-java
folder: JVM-java-jvm-internals
difficulty: ★★★
depends_on: JVM-012, JVM-032, JVM-054
used_by: JVM-063
related: JVM-059, JVM-060, JVM-013
tags:
  - jvm
  - java
  - memory
  - production
status: complete
version: 3
layout: default
parent: "Java & JVM Internals"
grand_parent: "Technical Mastery"
nav_order: 62
permalink: /technical-mastery/jvm/heap-sizing-and-memory-planning-strategy/
---

**⚡ TL;DR** - JVM memory = heap + Metaspace + Code Cache + thread stacks + off-heap; size heap at 2-3x live set; leave 25-30% of container RAM for non-heap; measure live set before setting any limits.

| Field | Value |
|---|---|
| **Depends on** | [[JVM-012 - Heap Memory]], [[JVM-032 - GC Roots]], [[JVM-054 - TLAB (Thread Local Allocation Buffer)]] |
| **Used by** | [[JVM-063 - JVM Observability Strategy]] |
| **Related** | [[JVM-059 - GC Tuning Strategy for Production JVMs]], [[JVM-060 - JVM Architecture Decisions at Scale]], [[JVM-013 - Metaspace]] |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
Teams set `-Xmx` to whatever feels large - "the server has 32GB, set Xmx to 30GB." The result: long Full GC pauses (large heaps take longer to collect), OOMKilled containers (JVM heap + non-heap exceeds container limit), or heap undersizing causing constant GC thrashing. Memory planning without understanding the JVM's full memory topology is guesswork with production consequences.

**THE BREAKING POINT:**
A team sets `-Xmx20g` on a pod with 24GB RAM limit. The JVM's non-heap (Metaspace 300MB, Code Cache 512MB, thread stacks 1GB, TLAB overhead) consumes an additional 2-3GB. Total JVM memory: 23GB. OS uses 500MB. Total: 23.5GB. The pod is OOMKilled. The team increases the RAM limit. But the problem is that they never measured their actual live set (5GB) - the service would run fine on 16GB with heap sized correctly.

**THE BREAKING POINT:**
The three most common memory mistakes: (1) setting `-Xmx` = container memory limit (leaves no room for non-heap), (2) never measuring live set (heap sized by instinct), (3) setting `-Xms` much lower than `-Xmx` (JVM grows heap slowly, causing GC pressure during startup).

**EVOLUTION:**
- JDK 8: PermGen for class metadata (fixed size, frequent OOM); tuned with `-XX:MaxPermSize`
- JDK 8u40+: Metaspace replaced PermGen; dynamically sized, no fixed limit by default
- JDK 10+: JVM detects container memory limits automatically; `-XX:MaxRAMPercentage` recommended over absolute `-Xmx`
- JDK 21: virtual threads change thread stack accounting; many more stacks at lower memory cost

---

### 📘 Textbook Definition

**JVM heap sizing** is the process of determining the correct values for `-Xms` (initial heap), `-Xmx` (maximum heap), and related memory region parameters based on the application's measured live set, allocation rate, GC algorithm requirements, and container memory limits. **JVM memory planning** extends heap sizing to account for all JVM memory regions: heap (Eden, Survivor, Old Gen), Metaspace (class metadata), Code Cache (JIT-compiled native code), thread stacks (one per thread), Direct ByteBuffer (off-heap NIO), and OS overhead. The JVM's total resident set size (RSS) = all of these combined. Container limits must accommodate the full RSS, not just the heap.

---

### ⏱️ Understand It in 30 Seconds

**One line:** JVM memory is more than heap: size heap at 2-3x live set, leave 25-30% of container RAM for non-heap.

> Like budgeting a household: the mortgage (heap) is the biggest line item but not the only one. Utilities, food, insurance (Metaspace, Code Cache, thread stacks) consume the rest. Spending 90% of income on mortgage leaves no room for everything else.

**One insight:** The live set is the single most important metric for heap sizing. Everything else derives from it. If you do not know your live set, you are sizing in the dark.

---

### 🔩 First Principles Explanation

**CORE INVARIANTS:**
1. Heap must be large enough to hold the live set plus allocation headroom for GC
2. Non-heap memory is not bounded by `-Xmx` and must be separately estimated
3. Container memory limit must accommodate total JVM RSS, not just heap
4. GC pause duration correlates with heap size; larger heap = longer potential pauses (for stop-the-world GCs)

**DERIVED DESIGN:**
From invariant 1: heap = live_set * N, where N depends on GC algorithm. G1GC: N=2-3. ZGC: N=4 (needs relocation headroom).
From invariant 2: plan non-heap budget explicitly. Typical production values:
- Metaspace: 100-400MB (more for frameworks with heavy proxy generation)
- Code Cache: 240-512MB (JIT compiled native code)
- Thread stacks: ~1MB per OS thread * thread count
- Direct ByteBuffer: application-specific off-heap allocation
From invariant 3: container_limit = heap_max + non_heap_budget + OS_overhead (50-100MB)
From invariant 4: for G1GC, larger heap means more regions to scan; ZGC is not affected.

**THE TRADE-OFFS:**

**Gain (correct sizing):** Eliminates OOM kills, reduces GC overhead, enables capacity planning

**Cost:** Requires measurement (live set profiling); must update with application growth

**ESSENTIAL vs ACCIDENTAL COMPLEXITY:**

**Essential:** Any GC algorithm needs headroom above the live set. This is irreducible.

**Accidental:** Setting `-Xmx` = container limit is accidental complexity from not knowing the memory topology.

---

### 🧪 Thought Experiment

**SETUP:** Your service has 1GB live set at peak traffic. You set `-Xmx2g` (2x live set). Container limit: 2g.

**WHAT HAPPENS:**
JVM heap reaches max 2GB. Metaspace uses 200MB. Code Cache uses 300MB. 100 threads * 1MB = 100MB stacks. OS: 100MB. Total: 2.7GB. Container limit: 2GB. Pod OOMKilled. Application logs show no OutOfMemoryError (heap was fine). The OOM was in the OS, not in the JVM heap. The root cause was not accounting for non-heap memory.

**CORRECT SIZING:**
Container limit: 4GB.
Heap: `-Xmx2g` (2x live set).
Non-heap budget: 700MB.
OS overhead: 300MB.
Total: 3GB. Container limit 4GB provides comfortable headroom.

**THE INSIGHT:**
`-Xmx` is only one of many memory consumers in a JVM process. Sizing the container to match `-Xmx` is the most common and most consequential JVM memory mistake.

---

### 🧠 Mental Model / Analogy

> Think of JVM memory as a multi-compartment train. The heap is the largest carriage (passenger car). Metaspace is the luggage car. Code Cache is the mail car. Thread stacks are the dining car. Off-heap is the freight car attached separately. The train fits on a track (container limit) of fixed length. If you assume only the passenger car matters and buy a track just long enough for it, the other carriages extend beyond the platform and the train cannot stop.

Element mapping:
- Train length = total JVM RSS
- Track length = container memory limit
- Passenger car = heap (-Xmx)
- Luggage car = Metaspace
- Mail car = Code Cache (JIT compiled native code)
- Dining car = thread stacks
- Freight car = off-heap DirectByteBuffer/off-heap allocations
- Platform = what Kubernetes allocates

Where this analogy breaks down: in a real train, all carriages are fixed size. JVM memory regions grow dynamically until they hit their limits. This makes the total RSS variable, which is why monitoring is essential.

---

### 📶 Gradual Depth - Four Levels

**Level 1 - What it is (anyone can understand):**
Java programs need memory for storing objects (the heap) but also for other things like loaded classes and compiled code. When you set the maximum heap size, you are only controlling part of the memory. You need to leave room in your server or container for all the other parts too.

**Level 2 - How to use it (junior developer):**
The quick practical formula: set container memory limit to `Xmx * 1.4 + 500MB`. So if `Xmx=4g`, container limit = `4096 * 1.4 + 500 = 6234MB ≈ 6.5GB`. Prefer `-XX:MaxRAMPercentage=75.0` over absolute `-Xmx` in containerised environments - it automatically scales heap to 75% of container memory, leaving 25% for non-heap. Always set `-Xms = -Xmx` in production to avoid heap resize events.

**Level 3 - How it works (mid-level engineer):**
JVM memory regions:
1. **Java Heap** (`-Xmx`): Young Gen (Eden + 2x Survivor) + Old Gen. GC managed.
2. **Metaspace** (`-XX:MaxMetaspaceSize`): class metadata, method bytecode, symbols. Grows with class loading. Spring Boot typically uses 150-300MB.
3. **Code Cache** (`-XX:ReservedCodeCacheSize`): JIT-compiled native code. Default 240MB; can grow to 512MB under heavy JIT load.
4. **Thread stacks** (`-Xss`): 1MB default per OS thread. 200 threads = 200MB. Virtual threads (Java 21) use 1-10KB each.
5. **Direct ByteBuffer** (`-XX:MaxDirectMemorySize`): off-heap NIO buffers. Not GC-managed. Must be tracked separately.
6. **JVM overhead**: GC data structures, JIT profiles, compiler queues. Typically 50-200MB.

**Level 4 - Why it was designed this way (senior/staff):**
The separation of Metaspace from the heap is a deliberate design from Java 8. PermGen (its predecessor) was part of the heap with a fixed size, leading to `OutOfMemoryError: PermGen space` during hot deployment in application servers. Metaspace is native memory (not part of the Java heap), dynamically sized, and can grow until native memory is exhausted. This eliminates the PermGen OOM class but introduces a different failure mode: unbounded Metaspace growth from class loader leaks. Setting `-XX:MaxMetaspaceSize=512m` caps this leak at the cost of `OutOfMemoryError: Metaspace` if the cap is too low. The design trade-off: bounded but potentially too-small vs unbounded but potentially OOM-killing the host.

**Expert Thinking Cues:**
- `jcmd <pid> VM.native_memory summary` shows all memory regions including non-heap
- Metaspace OOM in a running application usually indicates a class loader leak (often in hot-deploy or plugin systems)
- Setting `-Xms = -Xmx` prevents JVM heap expansion pauses during startup but commits the full heap immediately

---

### ⚙️ How It Works (Mechanism)

**Full JVM Memory Map:**
```
  JVM Process RSS
  +----------------------------------+
  | Java Heap              (-Xmx)   |
  |   Young Gen                     |
  |     Eden                        |
  |     Survivor x2                 |
  |   Old Gen (Tenured)             |
  +----------------------------------+
  | Metaspace              (native) |
  |   Class metadata                |
  |   Method bytecode               |
  +----------------------------------+
  | Code Cache   (ReservedCodeCache)|
  |   C1 compiled methods           |
  |   C2 compiled methods           |
  +----------------------------------+
  | Thread Stacks          (-Xss)   |
  |   1MB x thread_count            |
  +----------------------------------+
  | Direct ByteBuffer      (native) |
  |   MaxDirectMemorySize           |
  +----------------------------------+
  | JVM internals          (native) |
  |   GC data structures            |
  |   JIT profiling data            |
  +----------------------------------+
  | OS overhead                     |
  +----------------------------------+
```

**Sizing Formula:**
```
live_set = measured via jmap -histo:live

heap_max (G1/Parallel) = live_set * 2.5
heap_max (ZGC)         = live_set * 4.0

metaspace_budget = 200-400MB (measure first)
code_cache_budget = 256-512MB
thread_stacks     = thread_count * 1MB
direct_memory     = measure from app logs

container_limit = heap_max
                + metaspace_budget
                + code_cache_budget
                + thread_stacks
                + direct_memory
                + 300MB (JVM + OS overhead)
```

---

### 🔄 The Complete Picture - End-to-End Flow

**NORMAL FLOW:**
```
  Measure live set          <- YOU ARE HERE
  (jmap -histo:live or JFR)
       |
  Calculate heap budget
  (live_set * 2.5)
       |
  Estimate non-heap budget
  (Metaspace + Code Cache
   + thread stacks + DirectBB)
       |
  Sum for container limit
  (heap + non-heap + OS)
       |
  Set -Xms = -Xmx (production)
  Set MaxRAMPercentage=75 (container)
       |
  Monitor and adjust
  (RSS, GC overhead, OOM events)
```

**FAILURE PATH:**
- `OOMKilled`: container limit < total RSS - increase limit or reduce non-heap budgets
- `OutOfMemoryError: Java heap space`: heap too small for live set + allocation headroom
- `OutOfMemoryError: Metaspace`: class loader leak or MaxMetaspaceSize too low
- GC overhead limit exceeded: heap much smaller than live set; GC runs continuously

**WHAT CHANGES AT SCALE:**
At scale, use `-XX:MaxRAMPercentage=75.0` instead of absolute `-Xmx`. This makes heap sizing automatic as container memory limits change (e.g., from horizontal pod autoscaler vertical recommendations). Use resource quotas to prevent accidental memory limit increases. Monitor RSS, not just heap usage.

---

### 💻 Code Example

**BAD - Xmx equal to container limit:**
```yaml
# Container limit = 4GB
# -Xmx4g = 4GB heap
# Non-heap will push total RSS to 5-6GB
# Result: OOMKilled
resources:
  limits:
    memory: "4Gi"
env:
  - name: JAVA_OPTS
    value: "-Xmx4g -Xms4g"
```

**GOOD - heap sized at 75% of container limit:**
```yaml
# Container limit = 4GB
# MaxRAMPercentage=75 -> Xmx=3GB
# Non-heap budget: 1GB
resources:
  limits:
    memory: "4Gi"
  requests:
    memory: "4Gi"   # request = limit for predictable QoS
env:
  - name: JAVA_OPTS
    value: >-
      -XX:MaxRAMPercentage=75.0
      -XX:InitialRAMPercentage=75.0
      -XX:MaxMetaspaceSize=512m
      -XX:ReservedCodeCacheSize=256m
      -Xss512k
      -XX:+UseZGC
      -XX:+HeapDumpOnOutOfMemoryError
      -Xlog:gc*:file=/var/log/gc.log
```

**Measuring live set:**
```bash
# Force full GC then measure live objects
jcmd <pid> GC.run
jmap -histo:live <pid> 2>/dev/null | \
  awk 'NR>3{sum+=$3} END{print "Live set: " sum/1024/1024 " MB"}'

# Or via JFR (lower overhead):
jcmd <pid> JFR.start duration=30s \
  name=livesetcheck settings=default \
  filename=/tmp/livecheck.jfr
# Analyse: JDK Mission Control -> Memory tab -> live set
```

**Monitoring all JVM memory regions:**
```bash
# Native memory tracking (enable at startup)
java -XX:NativeMemoryTracking=summary ...

# Report at runtime
jcmd <pid> VM.native_memory summary

# Output shows:
# Java Heap (committed: 3GB)
# Class (committed: 200MB)
# Code (committed: 240MB)
# Thread (committed: 150MB)
# GC (committed: 100MB)
```

---

### ⚖️ Comparison Table

| Memory Region | JVM Flag | Default | Typical Production | Notes |
|---|---|---|---|---|
| Heap max | `-Xmx` | 25% RAM | 75% container limit | Must include headroom for GC |
| Heap initial | `-Xms` | 1/64 RAM | = Xmx (production) | Avoid resize cost at startup |
| Metaspace | `-XX:MaxMetaspaceSize` | Unlimited | 256-512MB | Cap to prevent leak spiral |
| Code Cache | `-XX:ReservedCodeCacheSize` | 240MB | 256-512MB | Increase for large services |
| Thread stack | `-Xss` | 1MB | 512KB-1MB | Virtual threads: negligible |
| Direct memory | `-XX:MaxDirectMemorySize` | = Xmx | App-specific | Critical for Netty/NIO apps |

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| "-Xmx is the JVM memory limit" | `-Xmx` limits only the heap. Metaspace, Code Cache, thread stacks, and off-heap are separate and not bounded by `-Xmx`. |
| "More heap means fewer GC pauses" | More heap means more objects survive to Old Gen; larger Old Gen means longer potential Full GC pauses. Right-size, don't maximise. |
| "-Xms and -Xmx should be different" | For server applications in production, setting `-Xms = -Xmx` avoids heap expansion overhead and GC pressure during startup. This is recommended for Kubernetes. |
| "Container memory limit = Xmx" | Container memory limit must exceed Xmx by at least the non-heap budget. Rule: container_limit = Xmx * 1.33 + 500MB minimum. |
| "OOMKilled means Java ran out of heap" | OOMKilled is a kernel event from container memory limit breach. The Java heap might have been fine; non-heap grew past the limit. Always check RSS, not just heap. |

---

### 🚨 Failure Modes & Diagnosis

**Failure Mode 1: OOMKilled with no Java OOM error**
**Symptom:** Kubernetes OOMKills the pod (exit code 137); application logs show no `OutOfMemoryError`

**Root Cause:** Non-heap memory (Metaspace/Code Cache/thread stacks) pushed total RSS above container limit

**Diagnostic:**
```bash
# Check OOM reason
kubectl describe pod <pod> | grep -A 5 OOMKilled

# Before it OOMKills again, check RSS
kubectl exec -it <pod> -- cat /proc/1/status | grep VmRSS
# Or:
jcmd 1 VM.native_memory summary
```
**Fix:** Increase container memory limit or cap non-heap regions:
```bash
-XX:MaxMetaspaceSize=256m
-XX:ReservedCodeCacheSize=256m
-Xss512k    # reduce stack size if many threads
```
**Prevention:** Enable NativeMemoryTracking in staging; ensure `container_limit > Xmx + 1GB`

**Failure Mode 2: OutOfMemoryError: Metaspace with no class explosion**
**Symptom:** `java.lang.OutOfMemoryError: Metaspace` after hours of operation; class count appears stable

**Root Cause:** Class loader leak - old ClassLoader instances retained in memory; associated Metaspace not released

**Diagnostic:**
```bash
# Check ClassLoader count over time
jcmd <pid> VM.native_memory summary | grep "Class"
# Increasing "Class" section = class loader leak

# In heap dump: look for ClassLoader instances
jmap -dump:live,format=b,file=heap.hprof <pid>
# Analyse with Eclipse MAT: "ClassLoader Explorer"
```
**Fix:** Find and fix the retained ClassLoader; common in dynamic plugin systems, JSP engines, OSGi

**Prevention:** Set `-XX:MaxMetaspaceSize=512m` to fail fast rather than slowly consuming native memory

**Failure Mode 3: Heap undersized relative to live set (GC thrashing)**
**Symptom:** GC overhead >20% of CPU; frequent OOM errors; application progressively slows

**Root Cause:** Heap smaller than 2x live set; GC collects too often with no headroom

**Diagnostic:**
```bash
# Measure allocation rate and live set
jstat -gcutil <pid> 1000 20
# Columns: S0, S1, E (eden %), O (old %), M (metaspace %)
# If O column stays near 100%, live set > Old Gen capacity

# Force GC and measure live objects
jcmd <pid> GC.run
jmap -histo:live <pid> | head -30 | tail -5
```
**Fix:** Increase `-Xmx` to at least 2.5x live set; investigate if live set has grown beyond expected

**Prevention:** Monitor live set as a production metric; alert when live set exceeds 40% of Xmx

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**
- [[JVM-012 - Heap Memory]] - Heap structure
- [[JVM-032 - GC Roots]] - What determines live set
- [[JVM-054 - TLAB (Thread Local Allocation Buffer)]] - Allocation mechanism

**Builds On This (learn these next):**
- [[JVM-063 - JVM Observability Strategy]] - Monitoring memory in production

**Alternatives / Comparisons:**
- [[JVM-013 - Metaspace]] - Non-heap class metadata
- [[JVM-059 - GC Tuning Strategy for Production JVMs]] - GC algorithm selection

---

### 📌 Quick Reference Card

```
+--------------------------------------------------+
| WHAT IT IS    | Full JVM memory topology and      |
|               | systematic sizing formulae        |
+--------------------------------------------------+
| PROBLEM       | OOMKilled; GC thrashing; unknown  |
|               | live set; Xmx = container limit   |
+--------------------------------------------------+
| KEY INSIGHT   | JVM memory = heap + Metaspace +   |
|               | Code Cache + stacks + off-heap    |
+--------------------------------------------------+
| USE WHEN      | Sizing new services; diagnosing   |
|               | OOMKilled; capacity planning      |
+--------------------------------------------------+
| AVOID WHEN    | Never skip live set measurement   |
+--------------------------------------------------+
| TRADE-OFF     | Larger heap: less GC overhead,    |
|               | longer potential Full GC pauses   |
+--------------------------------------------------+
| ONE-LINER     | container_limit = Xmx * 1.33 +   |
|               | 500MB; Xmx = live_set * 2.5      |
+--------------------------------------------------+
| NEXT EXPLORE  | JVM-063 observability,           |
|               | JVM-059 GC tuning                 |
+--------------------------------------------------+
```

**If you remember only 3 things:**
1. JVM RSS = heap + Metaspace + Code Cache + thread stacks + off-heap
2. Container limit must be 30-40% larger than Xmx
3. Measure live set before setting any heap size - everything else derives from it

**Interview one-liner:** "Heap sizing starts by measuring live set, then sizing heap at 2-3x live set. Container limit must accommodate total JVM RSS: heap plus non-heap budget (Metaspace, Code Cache, thread stacks), typically 30-40% above Xmx."

---

### 💎 Transferable Wisdom

**Reusable Engineering Principle:** When sizing a resource limit, account for all consumers, not just the primary consumer. The primary consumer (heap) is visible; secondary consumers (non-heap) are invisible until they cause failures. Budget for all consumers before setting limits.

**Where else this pattern appears:**
- Kubernetes pod resource limits: CPU request must account for sidecar containers, not just the main application
- Database connection pools: total connections = application pool + monitoring pool + DBA connections + replication - not just application pool
- Thread pool sizing: total threads = application threads + GC threads + JIT compiler threads + monitoring threads

---

### 💡 The Surprising Truth

Setting `-Xms = -Xmx` (same initial and maximum heap) in production is counterintuitive but is explicitly recommended by JVM performance engineers. The common assumption is that a smaller initial heap saves memory. In reality, when the JVM starts with a small heap and grows it during startup, the heap expansion triggers additional GC cycles (to compact before expanding) and requires the OS to allocate new pages. For services under Kubernetes with memory limits, this startup GC pressure can trip readiness probes or cause the service to appear unhealthy during initialisation. Setting `Xms = Xmx` commits the full heap immediately (pre-allocating virtual memory), but actual physical pages are allocated lazily by the OS as objects are created - so memory usage still grows gradually in practice, but the JVM avoids the expansion overhead entirely.

---

### 🧠 Think About This Before We Continue

**Q1 (Root Cause):** Your service is OOMKilled after 6 hours with `-Xmx4g` in a 6GB container. The Java heap usage plateaus at 3.5GB, well within limits. `jcmd <pid> VM.native_memory` was not enabled. What is the most likely non-heap region responsible, and what is the single observation from `kubectl describe pod` that confirms it was not a Java heap OOM?
*Hint:* Look at the exit code in the container status and the Metaspace growth pattern for long-running services that dynamically load classes or generate proxies.

**Q2 (Scale):** You have 200 services. You set `MaxRAMPercentage=75` uniformly. A new service uses Netty with large DirectByteBuffer allocations (off-heap). Under load, its total memory usage exceeds container limit despite heap being within 75%. What is the one flag you must add, and why does `MaxRAMPercentage` not protect against this?
*Hint:* Research `-XX:MaxDirectMemorySize` and what happens when DirectByteBuffer allocation exceeds this limit vs when it silently grows beyond container limit.

**Q3 (Design Trade-off):** Virtual threads (Java 21) use 1-10KB stack space vs 1MB for OS threads. A service runs 10,000 virtual threads. What is the thread stack memory saving compared to OS threads, and what non-heap region grows instead as virtual threads mount/unmount on carrier threads?
*Hint:* Research how virtual thread continuation stacks are stored on the heap (not as thread stacks) when virtual threads are parked, and what this means for heap sizing when migrating from 200 OS threads to 10,000 virtual threads.
