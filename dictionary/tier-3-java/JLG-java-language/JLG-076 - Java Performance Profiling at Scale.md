---
id: JLG-085
title: Java Performance Profiling at Scale
category: Java Language
tier: tier-3-java
folder: JLG-java-language
difficulty: ★★★
depends_on: JLG-001, JLG-075
used_by:
related: JLG-077, JLG-078, JLG-084
tags:
  - java
  - advanced
  - production
  - observability
status: complete
version: 2
layout: default
parent: "Java Language"
grand_parent: "Technical Dictionary"
nav_order: 76
permalink: /jlg/java-performance-profiling-at-scale/
---

# JLG-076 - Java Performance Profiling at Scale

⚡ TL;DR - Java Flight Recorder (JFR) provides always-on, low-overhead JVM profiling in production; async-profiler and flame graphs diagnose CPU, allocation, and latency issues without safepoint bias distortion.

| Field | Value |
|---|---|
| **Depends on** | [[JLG-001 - What Is Java - History and Philosophy]], [[JLG-075 - Java Modularity Strategy (JPMS)]] |
| **Used by** | (none yet) |
| **Related** | [[JLG-077 - Java in Polyglot Architecture]], [[JLG-078 - Java Language Specification Deep Dive]], [[JLG-084 - Java Ecosystem Selection Framework]] |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**

Before Java Flight Recorder (JFR) was open-sourced in Java 11, profiling a production JVM required commercial Oracle JDK licences or attaching heavyweight profilers that slowed the application by 10-30%. Engineers profiled only in staging environments, where GC pressure, heap sizes, and traffic patterns differed from production.

**THE BREAKING POINT:**

Production performance problems are invisible in staging. A heap allocation hotspot caused by a specific query pattern only appears under real load. A GC pause triggered by long-lived object promotion only manifests with production data volumes. Profiling staging found different problems than production had.

**THE INVENTION MOMENT:**

**Java Flight Recorder (JFR)** was originally a BEA JRockit profiler, acquired by Oracle, and released as open-source in Java 11 (JEP 328). JFR uses a circular buffer in the JVM's native heap to record thousands of events per second with <1% overhead. Safepoint polls were added as JFR events, enabling always-on production profiling without changing deployment.

**EVOLUTION:**

- **2000:** BEA JRockit Mission Control and Flight Recorder (commercial)
- **2008:** Oracle acquires BEA; JFR becomes Oracle JDK-only commercial feature
- **2018:** Java 11 - JFR + JMC open-sourced (JEP 328, JEP 331); available in all OpenJDK builds
- **2020:** Java 14 - JFR Event Streaming API (JEP 349) - real-time events via `RecordingStream`
- **2021:** async-profiler 2.0 - frame pointer profiling eliminating safepoint bias
- **2023:** Java 21 - JFR `jdk.VirtualThreadStart/Stop/Pinned` events for virtual thread profiling

---

### 📘 Textbook Definition

**Java performance profiling** is the systematic measurement of JVM runtime behaviour - CPU usage, heap allocation, GC activity, thread state, I/O latency, and lock contention - to identify bottlenecks. Key tools:

- **JFR (Java Flight Recorder):** low-overhead event recording built into OpenJDK 11+; captures JVM, GC, thread, class loading, socket, and application-defined events into `.jfr` files
- **JMC (Java Mission Control):** GUI tool to analyse `.jfr` recordings with flame graphs, allocation profilers, and GC analysis
- **async-profiler:** Linux/macOS sampling profiler using `AsyncGetCallTrace` API; eliminates safepoint bias; generates flame graphs
- **Flame graphs:** Brendan Gregg visualisation; y-axis = call stack depth; x-axis = sample frequency; widest frames = most CPU time

---

### ⏱️ Understand It in 30 Seconds

**One line:** JFR records JVM events in production with near-zero overhead; async-profiler samples CPU/alloc stacks without safepoint bias for accurate flame graphs.

> JVM profiling is like a flight data recorder in an aircraft. JFR runs continuously, recording thousands of events per second (GC pauses, thread blocks, method entries) into a circular buffer. When the plane (production service) has an incident, you dump the recording and analyse what happened. Async-profiler is the cockpit voice recorder - it captures every decision (stack sample) not just pre-defined events.

**One insight:** Safepoint bias is the most common source of profiling inaccuracy. Traditional profilers (JVisualVM, old YourKit) can only sample at JVM safepoints - but code runs at safepoints only briefly. Long-running loops are never sampled. Async-profiler eliminates this using OS signals (`SIGPROF`), sampling wherever the thread actually is.

---

### 🔩 First Principles Explanation

**CORE INVARIANTS:**

1. Profiling must not change the behaviour being measured; high-overhead profiling invalidates results
2. Safepoint-biased profilers miss long-running tight loops because safepoints occur at method entry/exit, not inside loops
3. Heap allocation profiling reveals object creation hotspots before GC pressure manifests
4. GC log analysis is the first step; profilers are the second step when GC logs show high allocation rate
5. Wall-clock profiling (thread state) and CPU profiling (on-CPU time) reveal different problems; use both

**DERIVED DESIGN:**

From invariant 1 → JFR's <1% overhead design uses native ring buffer; no object allocation in JVM thread; minimal heap pressure.
From invariant 2 → async-profiler uses `AsyncGetCallTrace` (originally for Google Perf Tools) + `SIGPROF` signal handler to sample at arbitrary points.
From invariant 4 → start with `gc.log` to see allocation rate and pause time; only attach profiler if GC analysis is insufficient.

**THE TRADE-OFFS:**

**Gain:** Production-accurate profiling with <1% overhead (JFR) or <5% overhead (async-profiler); identifies real bottlenecks not staging-visible ones; enables data-driven optimisation.

**Cost:** JFR recordings can be large (100MB-1GB for 5-min production recording); async-profiler requires Linux `perf_events` permissions; frame graph interpretation requires experience.

**ESSENTIAL vs ACCIDENTAL COMPLEXITY:**

**Essential:** Understanding safepoint bias is essential; ignoring it leads to false conclusions from profiling data.

**Accidental:** Many JVM profiling tools add their own instrumentation overhead that changes the behaviour; choosing low-overhead tools (JFR, async-profiler) eliminates most accidental complexity.

---

### 🧪 Thought Experiment

**SETUP:** An e-commerce service has 400ms P99 latency. JVM heap is 8GB with 30% old gen. GC logs show only 20ms/min stop-the-world GC time. The team suspects a CPU hotspot but JVisualVM shows `HashMap.get()` taking 40% CPU.

**WHAT HAPPENS WITHOUT ACCURATE PROFILING:**

The team optimises `HashMap.get()` - perhaps replacing it with `ConcurrentHashMap` or reducing map size. The latency remains at 400ms. The HashMap optimisation was real but not the dominant problem. The safepoint-biased profiler missed the tight loop inside a JSON serialiser that never safepointed.

**WHAT HAPPENS WITH ASYNC-PROFILER:**

```bash
async-profiler -d 30 -f flamegraph.html <pid>
```

The flame graph shows `JsonWriter.writeString()` consuming 60% of CPU, with `HashMap.get()` appearing correctly at 15%. The team replaces Jackson reflection-based serialisation with a code-generated serialiser. Latency drops to 80ms P99.

**THE INSIGHT:**

Safepoint bias caused the team to optimise the wrong thing. The profiler was confidently wrong. Always start with async-profiler for CPU profiling.

---

### 🧠 Mental Model / Analogy

> JVM profiling tools are like different kinds of medical diagnostics. GC logs are blood tests - quick, regular, tell you overall metabolic health. JFR is an ECG monitor - continuous recording of vital signs, stored for analysis. Async-profiler is an MRI - detailed internal image of exactly where time is spent. You don't start with an MRI; you start with blood tests, then ECG, then MRI only when needed.

**Element mapping:**
- Patient health → application performance
- Blood tests → GC log analysis (free, always on)
- ECG monitor → JFR recording (low overhead, continuous)
- MRI → async-profiler flame graph (high detail, targeted)
- Specific organ scan → allocation profiling with `-e alloc`

Where this analogy breaks down: in medicine, you run diagnostics on a sick patient. In software, you run profiling continuously in production on healthy applications to catch problems before they become incidents.

---

### 📶 Gradual Depth - Four Levels

**Level 1 - What it is (anyone can understand):**
Profiling tools watch your running Java application and record what it's doing - which code is using most CPU, how much memory is being created, where threads are waiting. The data reveals what to optimise without guessing.

**Level 2 - How to use it (junior developer):**
Start a JFR recording for 60 seconds:
```bash
# Start recording on running JVM:
jcmd <pid> JFR.start duration=60s \
  filename=/tmp/recording.jfr

# Or at JVM startup:
java -XX:StartFlightRecording=duration=60s,\
filename=/tmp/app.jfr -jar app.jar

# Analyse with JMC (GUI):
jmc
```
Open the `.jfr` file in JMC. Look at the Flame Graph view for CPU hotspots, the GC view for pause times, and the Allocation Profile for memory hotspots.

**Level 3 - How it works (mid-level engineer):**
JFR uses a per-thread native buffer. Events are written to the buffer without JVM heap allocation and without locks. Periodically, thread buffers are flushed to a global buffer, then to a file. This design means JFR adds no GC pressure and no lock contention. JFR event types are either periodic (sampled on a schedule) or triggered (on every GC, every class load, every thread start). Async-profiler works differently: it sends `SIGPROF` to all threads at configurable intervals (default 10ms) and collects the stack trace wherever the thread is - not only at safepoints.

**Level 4 - Why it was designed this way (senior/staff):**
The separate allocation profiling (`-e alloc`) mode of async-profiler works by instrumenting `TLAB` (Thread-Local Allocation Buffer) exhaustion events. Since most small objects are allocated inside TLABs, allocation profiling catches only TLAB exhaustion events - which represent a large allocation or end-of-TLAB. This gives statistical accuracy proportional to allocation volume. The JFR `jdk.ObjectAllocationInNewTLAB` and `jdk.ObjectAllocationOutsideTLAB` events provide the same data within JFR recordings, enabling heap allocation profiling without async-profiler.

**Expert Thinking Cues:**
- Virtual thread profiling requires Java 21 JFR events (`jdk.VirtualThreadPinned`) to detect carrier thread pinning; async-profiler supports virtual threads from version 3.0
- JFR `jdk.SafepointBegin` / `jdk.SafepointEnd` events reveal time-to-safepoint - long TTSP means profilers cannot sample during that window
- Production JFR: use `settings=profile` for method sampling; `settings=default` for lower overhead with reduced method data

---

### ⚙️ How It Works (Mechanism)

```
JFR Architecture:

Per-thread native buffer (no heap alloc)
     |
     v
[Event written to thread buffer]
     |
Buffer full or periodic flush
     |
     v
[Global buffer (native memory)]
     |
Async writer thread
     |
     v
[.jfr file (circular or fixed)]

Async-profiler Architecture:

OS kernel sends SIGPROF at 10ms intervals
     |
Signal handler runs in ALL threads
     |
     v
AsyncGetCallTrace API walks stack
(works outside safepoints)
     |
     v
Sample stored in native hash map
     |
Dump: flamegraph.html / collapsed.txt
```

---

### 🔄 The Complete Picture - End-to-End Flow

**NORMAL FLOW:**

```
[Performance complaint: high P99 latency]
     |
     ├─ Step 1: GC log analysis
     |    ← YOU ARE HERE
     |    Check allocation rate, pause time
     |    Tool: GCViewer or GCEasy
     |
     ├─ Step 2: JFR recording (5-10 min)
     |    JVM thread/lock/GC/socket events
     |    jcmd <pid> JFR.start ...
     |
     ├─ Step 3: Analyse JFR in JMC
     |    Flame graph: CPU hotspots
     |    Allocation: memory hotspots
     |    GC: pause patterns
     |
     ├─ Step 4: async-profiler for
     |    confirmation (30s, CPU+alloc)
     |
     └─ Step 5: Targeted fix + verify
          A/B comparison of recordings
```

**FAILURE PATH:**

Profiling under-load in staging: GC allocation rate 50MB/s staging vs 500MB/s production. Profiling reveals different hotspots. Always profile under representative load.

**WHAT CHANGES AT SCALE:**

At large scale (1000+ JVM instances), continuous JFR with streaming (`RecordingStream` API, JEP 349) sends events to a central collector. Percentile latency distributions across fleet reveal which instances have outlier behaviour. Async-profiler in this context runs on 1-5% of instances as a rotating sample.

---

### 💻 Code Example

**JFR programmatic API (Java 14+):**

```java
// BAD: profiling only in staging
// - staging allocation rate differs
// - results don't reflect production

// GOOD: continuous JFR with event streaming
import jdk.jfr.consumer.RecordingStream;

// In production service startup:
try (var rs = new RecordingStream()) {
    rs.enable("jdk.GarbageCollection")
      .withThreshold(Duration.ofMillis(10));
    rs.enable("jdk.CPULoad")
      .withPeriod(Duration.ofSeconds(5));
    rs.enable("jdk.ObjectAllocationInNewTLAB");

    rs.onEvent("jdk.GarbageCollection", e -> {
        long pauseMs = e.getDuration()
          .toMillis();
        if (pauseMs > 100) {
            metrics.recordGcPause(pauseMs);
            logger.warn("GC pause: {}ms",
              pauseMs);
        }
    });
    rs.startAsync();
}
```

**Async-profiler from command line:**

```bash
# CPU flame graph (30 seconds):
./profiler.sh -d 30 \
  -f /tmp/cpu-flame.html <pid>

# Allocation flame graph:
./profiler.sh -d 30 -e alloc \
  -f /tmp/alloc-flame.html <pid>

# Lock contention profiling:
./profiler.sh -d 30 -e lock \
  -f /tmp/lock-flame.html <pid>

# Wall-clock profiling (includes blocking):
./profiler.sh -d 30 -e wall \
  -f /tmp/wall-flame.html <pid>
```

**JVM flags for GC log analysis:**

```bash
# Java 9+ unified GC logging:
-Xlog:gc*:file=/var/log/app-gc.log\
:time,uptime,level,tags\
:filecount=10,filesize=50m
```

**How to test / verify correctness:**

```bash
# Verify JFR is recording:
jcmd <pid> JFR.check

# List available JFR events:
java -XX:+PrintFlagsFinal 2>&1 | grep JFR

# Verify async-profiler can attach:
./profiler.sh check <pid>
# Returns: Perf events: OK
```

---

### ⚖️ Comparison Table

| Tool | Overhead | Safepoint Bias | Allocation | Lock | Platform |
|---|---|---|---|---|---|
| JFR | <1% | Yes (method sampling) | Yes (TLAB events) | Yes | All JDKs 11+ |
| async-profiler | 1-5% | No | Yes (-e alloc) | Yes (-e lock) | Linux/macOS |
| JVisualVM | 5-20% | Yes | Limited | Limited | All |
| YourKit | 5-15% | Varies by mode | Yes | Yes | All (commercial) |
| Arthas | 2-10% | Yes | Yes | Yes | Linux |

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| "JVisualVM shows accurate CPU hotspots" | JVisualVM uses safepoint-biased sampling; tight loops are never sampled; async-profiler is required for accurate CPU profiling |
| "High GC time means memory leak" | High GC time usually means high allocation rate (objects promoted too fast) not a leak. A leak shows growing old-gen that never shrinks after full GC. |
| "Profiling changes performance" | JFR at <1% overhead is safe for continuous production profiling. Attaching javaagent-based profilers can cause 10-30% slowdown. |
| "Flame graph width = call count" | Flame graph x-axis = sample count (time), not call count. A narrow tall spike is a rarely-called slow method. A wide flat bar is a frequently-called fast method. |
| "JFR only works on commercial JDK" | JFR was open-sourced in Java 11. All OpenJDK 11+ distributions include it; no licence required. |

---

### 🚨 Failure Modes & Diagnosis

**Mode 1: Safepoint bias produces misleading profile**

**Symptom:** JVisualVM flame graph shows `ArrayList.get()` as top CPU consumer. Developers optimise collection access. No latency improvement.

**Root Cause:** Profiler can only sample at JVM safepoints. A tight serialisation loop never reaches a safepoint; profiler never captures it. `ArrayList.get()` is sampled at its entry safepoint repeatedly, appearing dominant.

**Diagnostic:**
```bash
# Use async-profiler instead:
./profiler.sh -d 30 \
  -f /tmp/cpu-flame.html <pid>
# Flame graph will show actual hotspot
# without safepoint bias
```

**Fix:** Always use async-profiler for CPU hotspot analysis. Use JFR only for event-based profiling (GC, locks, I/O), not CPU sampling.

**Prevention:** Establish async-profiler as the team standard for CPU profiling. Never trust JVisualVM CPU sampling alone.

---

**Mode 2: Allocation profiling reveals hidden GC pressure**

**Symptom:** Increasing GC pause times under load. Heap inspection shows most objects are short-lived. GC logs: 800MB/s allocation rate.

**Root Cause:** Unknown allocation hotspot creating millions of short-lived objects per second. Source unknown from GC logs alone.

**Diagnostic:**
```bash
# JFR allocation profiling (1 minute):
jcmd <pid> JFR.start \
  settings=profile \
  duration=60s \
  filename=/tmp/alloc.jfr

# Or async-profiler allocation mode:
./profiler.sh -d 30 -e alloc \
  -f /tmp/alloc.html <pid>
# Flame graph shows which code creates
# most heap objects
```

**Fix:** Address top allocation hotspots: reuse objects where possible, use primitives instead of boxed types, reduce string concatenation in hot paths.

**Prevention:** Run allocation profiling monthly on high-traffic services. Allocation rate increase in JFR streaming triggers alerts before GC impact is visible.

---

**Mode 3: Profiler permissions denied in production (Security)**

**Symptom:** `async-profiler` fails with `Failed to inject profiler: Operation not permitted`. JFR.start returns `Unable to open repository`.

**Root Cause:** Container running as non-root user. `perf_events` syscall blocked by seccomp profile. JFR repository directory not writable.

**Diagnostic:**
```bash
# Check perf_events permission:
cat /proc/sys/kernel/perf_event_paranoid
# Values: -1=all, 1=no raw, 2=no kernel
# async-profiler needs value <= 1

# Check JFR repository path:
jcmd <pid> VM.flags | grep FlightRecorder
```

**Fix:** For containers: add `SYS_PERF` capability or set `perf_event_paranoid=1` on host. Mount writable volume for JFR output. Use JFR Event Streaming API which writes to heap buffer, not filesystem.

**Prevention:** Document profiling access requirements as part of container security policy. Use separate profiling-enabled deployment configuration for production diagnostics.

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**
- [[JLG-001 - What Is Java - History and Philosophy]] - JVM architecture and GC concepts
- [[JLG-075 - Java Modularity Strategy (JPMS)]] - module paths affect class loading profiling context

**Builds On This (learn these next):**
- [[JLG-078 - Java Language Specification Deep Dive]] - JVM safepoint semantics
- [[JLG-084 - Java Ecosystem Selection Framework]] - profiling tool selection by environment

**Alternatives / Comparisons:**
- Prometheus + Micrometer - application-level metrics (not JVM internals)
- OpenTelemetry Java agent - distributed tracing at service boundary level
- Arthas - Alibaba JVM diagnostic tool popular in Chinese Java ecosystem

---

### 📌 Quick Reference Card

```
+----------------------------------------------------------+
| WHAT IT IS    | JFR/JMC + async-profiler toolchain for  |
|               | production JVM performance analysis     |
| PROBLEM       | Staging profiling finds different        |
|               | hotspots than production under real load|
| KEY INSIGHT   | Safepoint bias makes traditional         |
|               | profilers confidently wrong for CPU work|
| USE WHEN      | Investigating high P99, GC pressure,     |
|               | allocation rate spikes, lock contention |
| AVOID WHEN    | Replacing metrics/tracing for service    |
|               | health monitoring (use OpenTelemetry)   |
| TRADE-OFF     | JFR <1% overhead, limited CPU accuracy  |
|               | vs async-profiler accurate, needs perms |
| ONE-LINER     | JFR for continuous event recording;      |
|               | async-profiler for accurate CPU/alloc   |
| NEXT EXPLORE  | JLG-078 (JVM internals),                |
|               | JLG-084 (Ecosystem selection)           |
+----------------------------------------------------------+
```

**If you remember only 3 things:**
1. Safepoint bias makes traditional profilers (JVisualVM) miss tight loops - always use async-profiler for CPU flame graphs
2. JFR is available in all OpenJDK 11+ builds with <1% overhead; safe for always-on production profiling
3. Start with GC logs, then JFR, then async-profiler - not all three at once; each reveals different problems

**Interview one-liner:** "Java performance profiling starts with GC log analysis (free, always-on), then JFR recordings for JVM event data (<1% overhead, OpenJDK 11+), then async-profiler for CPU/allocation flame graphs - which eliminates safepoint bias by sampling via OS signals rather than only at JVM safepoints."

---

### 💎 Transferable Wisdom

**Reusable Engineering Principle:** *Measure what actually happens, not what is convenient to measure.* Safepoint-biased profilers measure code at convenient collection points, not where time is actually spent. This principle applies everywhere: latency percentiles (P99 vs mean), representative load testing (production traffic patterns not synthetic), and database query plans (EXPLAIN ANALYZE on real data, not empty tables).

**Where else this pattern appears:**
- **Browser performance profiling:** Chrome DevTools Timeline captures all frame rendering work; sampling profilers miss GPU-stalled frames; use `requestAnimationFrame` callbacks to measure actual rendering time
- **Database query analysis:** `EXPLAIN ANALYZE` runs the actual query and shows real row counts; `EXPLAIN` without `ANALYZE` uses stale statistics that can be misleading
- **Network latency measurement:** histograms (P50/P95/P99) reveal tail latency; averages hide the slow outliers that determine user experience

---

### 💡 The Surprising Truth

Java Flight Recorder was originally a commercial feature requiring an Oracle JDK licence ($25/processor/year). Oracle open-sourced it in Java 11 (2018) under the same conditions as all of OpenJDK. The JFR implementation in OpenJDK is the same code Oracle used in commercial JDK - not a reduced version. This means every Java developer now has access to the same production profiling infrastructure that previously cost thousands of dollars per server per year for enterprise Java shops. Despite this, JFR adoption remains surprisingly low; surveys show less than 20% of Java teams use JFR in production, with most teams discovering performance problems reactively from user complaints rather than proactively from continuous profiling data.

---

### 🧠 Think About This Before We Continue

**Question 1 (B - Scale):** A company runs 5,000 JVM instances across 200 services. Each service runs with JFR continuous recording at `settings=default` overhead profile. Storage cost: 100MB/hour per instance × 5,000 instances × 24 hours = 12TB/day of JFR data. Design an architecture for collecting, storing, and querying this data to answer: "Which 10 services had the highest P99 GC pause time last Tuesday between 14:00 and 15:00?"

*Hint:* JFR Event Streaming API (Java 14+) allows real-time event processing without writing to files. Research whether OpenTelemetry's JMX receiver or JFR streaming can feed metrics into a time-series database, enabling fleet-wide analysis without storing raw JFR files.

**Question 2 (D - Root Cause):** An API service has 200ms P50 response time and 2000ms P99 response time. GC logs show 50ms GC pauses at most. JFR flame graph shows `ObjectInputStream.readObject()` at 30% CPU. The P99 is 10x the P50, which is disproportionately high. Describe what could cause this pattern and which profiling mode would diagnose it.

*Hint:* A factor of 10 between P50 and P99 with low GC pause time suggests thread blocking (lock contention or I/O wait) rather than CPU work or GC. Research the difference between CPU profiling mode and wall-clock profiling mode in async-profiler (`-e cpu` vs `-e wall`), and how wall-clock mode reveals blocking threads.

**Question 3 (C - Design Trade-off):** async-profiler uses `SIGPROF` OS signals to sample threads outside JVM safepoints, which eliminates safepoint bias. However, `SIGPROF` delivery is not guaranteed on all OS schedulers; heavily CPU-bound JVMs may have uneven sampling distribution. JFR method profiling uses safepoints and is biased but has guaranteed, configurable sampling intervals. For a latency-sensitive financial trading system where profiling accuracy is critical, which approach would you choose, and what would you add to compensate for the chosen approach's weaknesses?

*Hint:* Neither tool is universally superior. Research whether async-profiler provides flame graph confidence intervals or sampling rate guarantees. Consider using both tools simultaneously and comparing flame graphs to identify where they agree and where they diverge.
