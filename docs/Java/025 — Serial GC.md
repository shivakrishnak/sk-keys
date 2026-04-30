---
layout: default
title: "Serial GC"
parent: "Java & JVM Internals"
nav_order: 25
permalink: /java/serial-gc/
number: "025"
category: Java & JVM Internals
difficulty: ★★☆
depends_on: JVM, GC, Stop-The-World, Heap Memory, Young Generation, Old Generation
used_by: Small applications, Single-core environments, GC baseline understanding
tags: #java #jvm #gc #memory #internals #intermediate
---
# 025 — Serial GC

`#java` `#jvm` `#gc` `#memory` `#internals` `#intermediate`

⚡ TL;DR — The simplest JVM garbage collector using a single thread for all GC work — Stop-The-World for every collection, lowest overhead, appropriate only for small single-core or memory-constrained environments.

| #025 | Category: Java & JVM Internals | Difficulty: ★★☆ |
|:---|:---|:---|
| **Depends on:** | JVM, GC, Stop-The-World, Heap Memory, Young Generation, Old Generation | |
| **Used by:** | Small applications, Single-core environments, GC baseline understanding | |

---

### 📘 Textbook Definition

Serial GC is the **simplest JVM garbage collector**, using a single thread for all garbage collection work. It employs a **copy collector** for the Young Generation (Serial collector) and a **mark-sweep-compact** algorithm for the Old Generation (Serial Old collector). All collection is Stop-The-World — application threads are paused for the entire duration of GC. Despite its simplicity, Serial GC has the lowest per-GC overhead and is still the default for single-CPU or very small heap environments and client-class machines.

---

### 🟢 Simple Definition (Easy)

Serial GC is the **simplest, single-threaded GC** — one thread does all the work, everything stops while it runs, and it's best for small programs or environments where GC throughput isn't critical.

---

### 🔵 Simple Definition (Elaborated)

Serial GC does exactly what its name says — collects garbage serially, one object at a time, on a single thread, while all application threads wait. It has no complexity: no concurrent phases, no multiple GC threads to coordinate, no write barriers for concurrent marking. For small heaps (under 256MB) or single-core environments where parallelism doesn't help anyway, its simplicity means lower overhead than more sophisticated collectors. Understanding Serial GC is also the foundation for understanding all other GC algorithms — every other GC is essentially Serial GC with parallelism, concurrency, or incrementalism added.

---

### 🔩 First Principles Explanation

**The simplest correct GC algorithm:**

```
Requirements for correct GC:
  1. Find all live objects (mark)
  2. Reclaim all dead objects (sweep)
  3. Avoid fragmentation over time (compact)
  4. Do this safely (consistent heap view)

Serial GC's solution — brutally simple:
  1. Stop everything (STW)
  2. One thread: walk entire object graph (mark)
  3. One thread: sweep dead objects
  4. One thread: compact live objects
  5. Resume everything

No coordination overhead:
  No thread synchronisation during GC
  No write barriers for concurrent marking
  No incremental phases to coordinate
  Just: stop, clean, go
```

**Why simplicity has value:**

```
More threads = coordination overhead
Concurrent GC = write/read barrier cost
  (every object field write has extra work)
Incremental GC = bookkeeping complexity

For small heaps:
  GC takes 10-50ms either way
  Parallel GC gains: 5ms (saved time)
  Parallel GC costs: barrier overhead ALL the time
  Net gain: near zero for small heap

For small heap or single core:
  Serial GC wins on net throughput
  Parallel threads can't run in parallel
  → Serial is optimal
```

---

### ❓ Why Does This Exist — Why Before What

**Without any GC baseline (Serial is the baseline):**

```
Serial GC is the foundation:
  All other GC algorithms are Serial GC +
  modifications to reduce pause time or
  improve throughput

Understanding Serial GC gives you:
  • The pure algorithm without noise
  • Mental model for copy collection
  • Mental model for mark-sweep-compact
  • Baseline to compare all other GCs against

Without Serial GC as a concept:
  • G1GC's regions are incomprehensible
  • ZGC's concurrent phases have no baseline
  • Pause time comparisons have no reference point
```

**Historical necessity:**

```
Java 1.0-1.3: Serial GC was the ONLY GC
  → Drove JVM adoption on client machines
  → Established that automatic GC was viable

Still relevant today:
  • Default on single-CPU systems
  • Default in small containers (< 2 CPUs detected)
  • Microcontrollers, embedded Java
  • Lambda functions (short-lived, small heap)
  • Test environments (simplest, most predictable)
```

---

### 🧠 Mental Model / Analogy

> Serial GC is **one janitor cleaning an entire office building** while everyone is locked out.
>
> The janitor moves methodically: checks every room (marks live objects), cleans up trash (sweeps dead objects), reorganises furniture to one side (compacts live objects).
>
> **Parallel GC** = same approach but 8 janitors split the work.
> **G1GC** = 8 janitors, but they prioritise the dirtiest rooms first.
> **ZGC** = janitors clean while people are inside, using special rules to avoid conflicts.
>
> Serial GC is the simplest: one janitor, everyone waits. Not fast, but completely correct and zero coordination overhead.

---

### ⚙️ How It Works — Young and Old Collection

| #025 | Category: Java & JVM Internals | Difficulty: ★★☆ |
|:---|:---|:---|
| **Depends on:** | JVM, GC, Stop-The-World, Heap Memory, Young Generation, Old Generation | |
| **Used by:** | Small applications, Single-core environments, GC baseline understanding | |

---

### 🔄 How It Connects

```
Application allocates objects
      ↓
Eden fills → Minor GC triggered
      ↓
Serial GC: single thread does copy collection
  One thread: mark Young Gen live objects
  One thread: copy to Survivor
  One thread: wipe Eden
All other threads: waiting
      ↓
Survivors promoted over time → Old Gen fills
      ↓
Old Gen threshold → Major/Full GC triggered
      ↓
Serial Old: single thread does mark-sweep-compact
  One thread: mark ALL live objects (entire heap)
  One thread: sweep dead objects
  One thread: compact live objects
All other threads: waiting (potentially seconds)
      ↓
Resume — until next GC cycle
```

---

### 💻 Code Example

**Enabling and configuring Serial GC:**
```bash
# Explicitly enable Serial GC:
java -XX:+UseSerialGC MyApp

# Verify which GC is active:
java -XX:+PrintCommandLineFlags -version
# Output includes: -XX:+UseSerialGC or -XX:+UseG1GC etc.

# Serial GC is DEFAULT when:
# 1. Single-CPU system detected
# 2. Heap < some small threshold
# 3. -client JVM flag used (legacy)
# 4. Small containers (docker with 1 CPU)

# Basic Serial GC tuning:
java -XX:+UseSerialGC \
     -Xms64m \           # initial heap: 64MB
     -Xmx256m \          # max heap: 256MB
     -XX:NewRatio=2 \    # Old:Young = 2:1 → Young=85MB
     -XX:SurvivorRatio=8 \ # Eden:S0:S1 = 8:1:1
     MyApp
```

**Comparing Serial GC vs G1GC for small heap:**
```bash
# Small app, 256MB heap
# Test: which GC has lower overhead?

# Serial GC:
java -XX:+UseSerialGC -Xmx256m -XX:+PrintGCDetails MyApp
# [GC (Allocation Failure) DefNew: 69952K->8703K 4.2ms]
# Simple, predictable, low overhead

# G1GC on same small heap:
java -XX:+UseG1GC -Xmx256m -XX:+PrintGCDetails MyApp
# [GC pause (G1 Evacuation Pause) 6.8ms]
# Slightly higher overhead (G1 bookkeeping)
# For 256MB heap: Serial often wins on throughput

# Rule of thumb:
# Heap < 512MB + single core → Serial GC
# Heap > 512MB + multi core  → G1GC minimum
```

**Observing single-threaded behaviour:**
```bash
# During Serial GC Minor GC:
# CPU shows: one core at 100%, all others idle
# This is the single GC thread working

# During Parallel GC Minor GC:
# CPU shows: all cores at 100%
# GC threads using all available parallelism

# Verify with:
java -XX:+UseSerialGC \
     -Xlog:gc*:file=gc.log \
     -XX:+PrintGCDetails \
     MyApp

# Serial GC log format:
# [GC (Allocation Failure) [DefNew      ← "Default New" = Serial Young
#   8192K->1024K(9216K), 0.0054321 secs]
#   [Tenured: 0K->512K(10240K),          ← Old Gen (Serial Old)
#   0.0234567 secs]
#   9216K->1536K(19456K),
#   [Metaspace: 3456K->3456K(4864K)],
#   0.0290123 secs]
```

**When Serial GC is detected in containers:**
```bash
# Docker container with 1 CPU → JVM detects 1 CPU
# → Serial GC chosen as default!
# This surprises many developers

# Check what GC the JVM chose:
java -XX:+PrintFlagsFinal -version 2>&1 | grep GC | grep true

# In container with 1 CPU:
# UseSerialGC = true   ← surprise!

# Force G1GC even in 1-CPU container:
java -XX:+UseG1GC MyApp

# Or: give container more CPUs
docker run --cpus=2 myimage
# JVM now sees 2 CPUs → chooses G1GC by default
```

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| "Serial GC is obsolete" | Still **default on single-CPU** systems and small containers |
| "Serial GC is always worst choice" | For small heaps (< 512MB) on single core it can **outperform G1GC** on throughput |
| "Serial GC uses one CPU" | Uses one CPU — but that's often **optimal for single-core** environments |
| "All modern apps should use G1GC" | Lambda functions, CLI tools, test suites often better with **Serial GC** |
| "Serial GC can't handle large heaps" | It can — but pauses become **unacceptably long** (minutes for 32GB heap) |
| "Serial GC has no tuning options" | Fewer options than G1GC but still tunable with heap sizes and ratios |

---

### 🔥 Pitfalls in Production

**1. Unexpected Serial GC in containers**
```bash
# Kubernetes pod: request=0.5 CPU, limit=1 CPU
# JVM detects 1 CPU → activates Serial GC
# Load increases → GC pauses spike
# Team investigates thinking it's code issue

# Diagnosis:
kubectl exec <pod> -- java -XX:+PrintFlagsFinal \
  -version 2>&1 | grep UseSerialGC

# Fix: always explicitly set GC in containers
# Don't rely on JVM auto-detection
java -XX:+UseG1GC \
     -XX:MaxGCPauseMillis=200 \
     MyApp

# Or: set ActiveProcessorCount explicitly
java -XX:ActiveProcessorCount=4 \
     -XX:+UseG1GC \
     MyApp
```

**2. Using Serial GC for microservices accidentally**
```bash
# Spring Boot microservice deployed in Docker
# Default container: 1 CPU → Serial GC chosen
# Under load: 200ms pause for Minor GC
# p99 latency blown by GC pauses

# Check your Dockerfile/deployment:
ENV JAVA_OPTS="-XX:+UseG1GC -Xmx512m"
CMD java $JAVA_OPTS -jar app.jar

# Or in Spring Boot:
# JAVA_TOOL_OPTIONS="-XX:+UseG1GC"
# Picked up automatically by JVM
```

---

### 🔗 Related Keywords

- `Parallel GC` — Serial GC with multiple GC threads
- `G1GC` — incremental, region-based successor to Serial/Parallel
- `Stop-The-World` — Serial GC is entirely STW
- `Copy Collector` — algorithm used for Young Gen in Serial GC
- `Mark-Sweep-Compact` — algorithm used for Old Gen in Serial GC
- `DefNew` — JVM name for Serial GC's Young Gen collector
- `Serial Old` — JVM name for Serial GC's Old Gen collector
- `Single-core` — Serial GC's optimal environment
- `Container GC` — Serial GC often default in containers
- `ActiveProcessorCount` — JVM flag to override CPU detection

---

### 📌 Quick Reference Card

| #025 | Category: Java & JVM Internals | Difficulty: ★★☆ |
|:---|:---|:---|
| **Depends on:** | JVM, GC, Stop-The-World, Heap Memory, Young Generation, Old Generation | |
| **Used by:** | Small applications, Single-core environments, GC baseline understanding | |

---

### 🧠 Think About This Before We Continue

**Q1.** Serial GC is single-threaded. Parallel GC uses multiple threads for the same STW algorithms. For a 4-core machine with a 512MB Young Gen, if Serial GC Minor collection takes 100ms — would Parallel GC with 4 threads take exactly 25ms? What prevents perfect linear scaling, and what is the actual expected speedup?

**Q2.** A Java Lambda function (AWS Lambda) runs for 500ms, processes one request, then terminates. It has a 256MB heap. Should you use Serial GC, G1GC, or ZGC — and why? What does the Lambda execution model reveal about which GC properties actually matter (throughput vs pause time vs startup time vs memory overhead)?

---