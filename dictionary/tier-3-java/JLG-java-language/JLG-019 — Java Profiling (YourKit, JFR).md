---
layout: default
title: "Java Profiling (YourKit, JFR)"
parent: "Java & JVM Internals"
grand_parent: "Technical Dictionary"
nav_order: 19
permalink: /java/java-profiling-yourkit-jfr/
id: JLG-019
category: Java & JVM Internals
difficulty: ★★★
depends_on: JVM, Java Memory Management (Stack vs Heap Practical), Thread (Java)
used_by: Java Performance Tuning, Observability & SRE
related: JVM Flags, GC Logs, Thread Dump
tags:
  - java
  - jvm
  - performance
  - observability
  - advanced
---

# JLG-019 — Java Profiling (YourKit, JFR)

⚡ **TL;DR —** Java profiling is the discipline of recording CPU hotspots, memory allocations, GC activity, and thread states at runtime so you can fix the 3% of code responsible for 97% of the performance problem.

| | |
|---|---|
| **Depends on** | JVM, Java Memory Management (Stack vs Heap Practical), Thread (Java) |
| **Used by** | Java Performance Tuning, Observability & SRE |
| **Related** | JVM Flags, GC Logs, Thread Dump |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:** Developers optimise by intuition — rewriting loops, adding caches, switching data structures — without measuring whether those paths are actually slow. The result: weeks of effort improving code that runs in 2% of requests, while the real 500 ms bottleneck (a synchronised `Map` being accessed by 400 threads) goes untouched.

**THE BREAKING POINT:** A production API endpoint has a p99 latency of 1.8 seconds. The team has spent three sprints optimising database queries. Latency improves by 80 ms. Meanwhile, async-profiler reveals that 74% of CPU time is spent in `String.format()` inside a logging statement that fires on every request — a 3-line fix that reduces p99 to 210 ms.

**THE INVENTION MOMENT:** Profilers solve this by measuring *where the program actually spends time* — not where developers think it does. Profiling data makes performance work scientific: you establish a baseline, identify the real hotspot, fix it, and measure the improvement.

---

### 📘 Textbook Definition

**Java profiling** is the collection and analysis of runtime performance data from a JVM process. It encompasses CPU profiling (identifying which methods consume CPU time), allocation profiling (which code paths allocate the most heap), GC analysis (pause duration, frequency, promoted bytes), thread analysis (lock contention, blocked states), and I/O profiling. Tools include: **Java Flight Recorder (JFR)** (built-in, low-overhead, production-safe), **YourKit** (commercial, instrumentation + sampling), **async-profiler** (open-source, native sampling, FlameGraph output), and **JDK CLI tools** (`jcmd`, `jstack`, `jmap`, `jstat`).

---

### ⏱️ Understand It in 30 Seconds

**One line:** Profiling tells you *what* your JVM is actually doing — not what you think it is.

> Profiling a JVM is like fitting a GPS tracker to every car in a city to find the real traffic bottlenecks — rather than guessing which road is busy.

**One insight:** Every performance investigation should start with profiling data. Optimising without profiling is like treating a patient without a diagnosis — you might improve one symptom while missing the actual disease.

---

### 🔩 First Principles Explanation

**CORE INVARIANTS:**
1. You cannot reliably identify a performance bottleneck without measurement.
2. Sampling profilers interrupt the JVM at intervals and record the current call stack — low overhead, statistical accuracy.
3. Instrumentation profilers inject bytecode into every method entry/exit — precise, but >10% overhead, unsuitable for production.
4. JFR is a sampling profiler built into HotSpot with <2% overhead — safe for always-on production recording.
5. A FlameGraph visualises the sampled call stacks — width = CPU time, height = call depth.

**DERIVED DESIGN:**
- JFR records events (GC, JIT compilation, thread park/unpark, object allocation, exception throw) in a circular buffer, written to `.jfr` file on demand.
- YourKit attaches as a JVMTI agent and can switch between sampling and instrumentation modes.
- async-profiler bypasses the safepoint bias of HotSpot sampling by using `perf_events` (Linux) and `AsyncGetCallTrace` — more accurate for I/O and native-code hotspots.
- `jstack` produces a thread dump: a snapshot of all threads' call stacks — invaluable for deadlock and contention diagnosis.

**THE TRADE-OFFS:**
**Gain:** Profiling pinpoints the real bottleneck; seconds of analysis can save weeks of speculative refactoring.
**Cost:** Profilers add some overhead; instrumentation mode can distort timing. Sampling profilers have *safepoint bias* (HotSpot only samples at safepoints, missing some native/JNI time — async-profiler addresses this).

---

### 🧪 Thought Experiment

**SETUP:** Your REST service has 200 ms average latency. Your team suspects the Hibernate query layer. You add read replicas and query caches — latency drops to 185 ms. Still too slow.

**WHAT HAPPENS WITHOUT PROFILING:** The team continues iterating on guesses. Redis cache is added. Latency drops to 178 ms. The service is rewritten to use reactive streams. Latency drops to 165 ms. Three months later the service is still 40 ms above target.

**WHAT HAPPENS WITH PROFILING:** You attach JFR for 60 seconds under load. The flamegraph shows 38% of CPU in `com.fasterxml.jackson.databind.ser.BeanSerializer` — Jackson serialising a deep nested object graph on every response. You add `@JsonIgnore` to two circular references and enable `JsonMapper` caching. Latency drops to 120 ms in one PR, one afternoon.

**THE INSIGHT:** Performance work without profiling is art. Performance work with profiling is engineering. Profile first. Always.

---

### 🧠 Mental Model / Analogy

> A profiler is a doctor running a full blood panel instead of guessing what illness you have. JFR is the always-on ECG monitor already attached to the patient. YourKit is the specialist called in for deep investigation. async-profiler is the surgeon's precision imaging — showing you exactly where the blockage is.

- **Blood panel (profiler)** → measures actual runtime behaviour
- **ECG monitor (JFR)** → always-on, continuous, low-intrusion
- **Specialist (YourKit)** → deep, interactive, instrumentation-capable
- **Precision imaging (async-profiler)** → eliminates safepoint bias, shows native code
- **Treating without diagnosis** → optimising without profiling

Where this analogy breaks down: unlike a patient, a JVM under a profiler may behave differently due to JIT deoptimisation triggered by profiler instrumentation — especially in instrumentation mode.

---

### 📶 Gradual Depth — Four Levels

**Level 1 — What it is (anyone can understand):**
A profiler watches your Java program while it runs and reports which parts of the code are taking the most time or using the most memory. Like a stopwatch on every method at once.

**Level 2 — How to use it (junior developer):**
Run `jcmd <pid> JFR.start duration=60s filename=app.jfr`, then open `app.jfr` in JDK Mission Control (JMC). Look at the "Method Profiling" tab for CPU hotspots and "Allocations" tab for memory hotspots. For a thread dump: `jstack <pid> > threads.txt`. Look for threads in `BLOCKED` state to find lock contention.

**Level 3 — How it works (mid-level engineer):**
JFR uses a low-overhead ring buffer in the JVM to record events. Sampling fires every 10 ms (by default), capturing the active call stacks of all threads. JMC aggregates these samples into method-level CPU percentages. For allocation profiling, JFR uses TLAB retirement events — every time a TLAB is exhausted and a new one allocated, the allocation stack is recorded. async-profiler uses OS-level `perf_events` to sample at the CPU instruction pointer level, bypassing HotSpot's safepoint requirement and capturing JNI, GC, and native thread activity that JFR may miss.

**Level 4 — Why it was designed this way (senior/staff):**
HotSpot's built-in sampling fires only at *safepoints* — locations where the JVM has stopped all threads for GC or deoptimisation. This creates *safepoint bias*: long-running native operations between safepoints are invisible to HotSpot sampling. async-profiler, by using `AsyncGetCallTrace` (an undocumented HotSpot API) combined with Linux `perf_events` signals, can interrupt threads at any point — not just safepoints. This is why async-profiler catches I/O and native-call hotspots that JFR misses. Understanding safepoint bias is the difference between a profiler showing you 12% in `Thread.sleep()` (visible) versus a missing 30% in `SocketInputStream.read()` (invisible to safepoint-based profilers).

---

### ⚙️ How It Works (Mechanism)

```
  JVM Process (running)
  ┌───────────────────────────────────┐
  │  Application Threads              │
  │  ┌──────────┐  ┌──────────┐       │
  │  │ Thread-1 │  │ Thread-2 │  ...  │
  │  └────┬─────┘  └────┬─────┘       │
  │       │              │             │
  │  JFR Event Engine (ring buffer)   │
  │  ← CPU samples every 10ms         │
  │  ← Alloc events (TLAB exhausted)  │
  │  ← GC pause start/end events      │
  │  ← Lock contention events         │
  └──────────────────┬────────────────┘
                     │ jcmd JFR.dump
                     ▼
              app.jfr (binary file)
                     │
                     ▼
          JDK Mission Control (JMC)
          → Method Profiling tab
          → Garbage Collections tab
          → Memory → Allocations tab
          → Threads → Lock Instances tab
```

---

### 🔄 The Complete Picture — End-to-End Flow

**NORMAL FLOW:**
```
  1. IDENTIFY: "Service latency increased"
     Monitor: Prometheus p99 alert fires
     │
     ▼
  2. CAPTURE: Start JFR recording       ← YOU ARE HERE
     jcmd <pid> JFR.start \
       duration=120s filename=app.jfr
     │
     ▼
  3. ANALYSE: Open in JMC
     → Method Profiling: find CPU hotspot
     → Allocations: find alloc pressure
     → GC: check pause frequency/duration
     → Threads: find BLOCKED/contention
     │
     ▼
  4. HYPOTHESISE: "Hotspot is method X"
     Confirm with async-profiler flamegraph
     │
     ▼
  5. FIX: Targeted code change
     │
     ▼
  6. VERIFY: Re-capture JFR, compare
     Confirm hotspot reduced/gone
     Confirm p99 latency improved
```

**FAILURE PATH:**
- JFR records but JMC shows flat profile → JIT inlining merged methods; use `-XX:+UnlockDiagnosticVMOptions -XX:+PrintInlining` to understand.
- async-profiler shows native frames → problem is in JNI or OS layer, not JVM code.
- `jstack` shows all threads `RUNNABLE` but CPU is 100% → likely a spinning loop; async-profiler CPU mode will catch it.

**WHAT CHANGES AT SCALE:**
At scale, individual JFR files are useless. Integrate with Elastic APM, Datadog Continuous Profiler, or Pyroscope to aggregate profiling data across all pod replicas and over time. Continuous profiling shows you which methods regress between deployments — automatically.

---

### 💻 Code Example

```bash
# BAD — guessing without data
# Developer assumes DB is the bottleneck
# Adds caching everywhere, latency unchanged

# GOOD — profile first, then act

# 1. Start JFR recording (safe on production)
jcmd $(pgrep java) JFR.start \
  name=myrecording \
  duration=60s \
  filename=/tmp/app.jfr \
  settings=profile

# 2. Dump on demand (no duration set)
jcmd $(pgrep java) JFR.dump \
  name=myrecording \
  filename=/tmp/app.jfr

# 3. async-profiler flamegraph (Linux)
./profiler.sh \
  -d 30 \
  -e cpu \
  -f /tmp/flame.html \
  $(pgrep java)

# 4. Heap histogram — top allocating classes
jmap -histo:live $(pgrep java) | head -20

# 5. Thread dump for contention analysis
jstack $(pgrep java) > /tmp/threads.txt
grep -A5 "BLOCKED" /tmp/threads.txt

# 6. GC statistics every second
jstat -gcutil $(pgrep java) 1000
# S0   S1    E     O     M   CCS  YGC  YGCT  FGC
# 0.00 50.0  80.2  33.4  97  —   1204  6.22    2
# E (Eden) near 80 → Minor GC likely soon
```

```java
// Enabling JFR programmatically (Java 14+)
import jdk.jfr.Recording;
import jdk.jfr.consumer.RecordingFile;

try (Recording recording = new Recording()) {
    recording.enable("jdk.CPUSample")
             .withPeriod(Duration.ofMillis(10));
    recording.enable("jdk.ObjectAllocationInNewTLAB");
    recording.start();

    // Run workload under test
    runLoadTest();

    recording.dump(Path.of("/tmp/test.jfr"));
}
// Open /tmp/test.jfr in JMC for analysis
```

---

### ⚖️ Comparison Table

| Tool | Type | Overhead | Production Safe | Best For |
|---|---|---|---|---|
| JFR + JMC | Sampling (built-in) | < 2% | Yes | Always-on recording; GC, alloc, threads |
| async-profiler | Sampling (native) | < 3% | Yes | CPU flamegraphs; no safepoint bias |
| YourKit | Sampling + Instrumentation | 5–30% | No (dev/staging) | Deep interactive investigation |
| `jstack` | Thread dump | Negligible | Yes | Deadlock, contention, thread states |
| `jmap -histo` | Heap histogram | Brief pause | With care | Identifying memory hogs quickly |
| `jstat` | JVM counters | Negligible | Yes | GC rate, Eden fill, metaspace trend |
| Pyroscope / Datadog | Continuous profiling | < 5% | Yes | Fleet-wide CPU regression detection |

---

### 🔁 Flow / Lifecycle

```
Phase 1: SYMPTOM OBSERVED
  Alert fires: p99 > SLA
  Metrics: CPU / memory / GC anomaly
    │
    ▼
Phase 2: CAPTURE PROFILING DATA
  JFR: jcmd <pid> JFR.start duration=60s
  async-profiler: ./profiler.sh -d 30 <pid>
  Thread dump: jstack <pid>
    │
    ▼
Phase 3: ANALYSE
  JMC: Method Profiling, Allocations, GC
  FlameGraph: identify wide frames
  Thread dump: grep BLOCKED
    │
    ▼
Phase 4: IDENTIFY ROOT CAUSE
  "74% CPU in StringUtils.format"
  "800 MB/s alloc in ResponseBuilder"
  "32 threads BLOCKED on ReentrantLock"
    │
    ▼
Phase 5: IMPLEMENT FIX
  Targeted change to hotspot method
    │
    ▼
Phase 6: VERIFY IMPROVEMENT
  Re-capture JFR after fix
  Compare method % before/after
  Confirm p99 latency improved
```

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| "JFR is too risky for production" | JFR was designed for always-on production use with < 2% overhead. Oracle, Red Hat, and Azul have run it in production for years. |
| "Sampling profilers are inaccurate" | Statistical sampling over 60s at 100 Hz captures thousands of stack samples — accurate enough for all practical hotspot identification. Only micro-benchmarks need nanosecond precision. |
| "A thread in RUNNABLE state is doing CPU work" | `RUNNABLE` means the thread is not blocked on a Java lock. It could be doing CPU work OR blocking on I/O or a native call — `jstack` alone cannot distinguish. Use async-profiler for CPU specifics. |
| "High GC frequency always means a memory leak" | High Minor GC frequency usually means high allocation rate of short-lived objects — normal but potentially tunable. Memory leaks show Old Gen growing monotonically. They are different problems. |
| "Profiling in production changes the behaviour" | JFR's overhead is low enough that production behaviour is preserved. Instrumentation-mode profiling (YourKit) does change timings and should not be used in production. |

---

### 🚨 Failure Modes & Diagnosis

**Mode 1: JFR recording has no CPU samples**
**Symptom:** JFR file opens in JMC but Method Profiling tab shows no data or only JVM internal frames.
**Root Cause:** JFR was started with default `continuous` settings instead of `profile` settings; CPU sampling is not enabled by default.
**Diagnostic:**
```bash
# Check active JFR settings
jcmd <pid> JFR.check

# Restart with profile settings
jcmd <pid> JFR.stop
jcmd <pid> JFR.start \
  settings=profile \
  duration=60s \
  filename=/tmp/app.jfr
```
**Fix:** Always use `settings=profile` for CPU hotspot analysis. `settings=default` is for low-overhead GC and allocation monitoring only.
**Prevention:** Create a standard JFR configuration file (`jfr.xml`) in your repo's `scripts/` directory and document the correct start command in your runbook.

**Mode 2: async-profiler shows `[unknown]` frames**
**Symptom:** FlameGraph has large `[unknown]` sections, obscuring the actual hotspot.
**Root Cause:** JVM was started without `-XX:+PreserveFramePointer`; native frame pointers are not preserved, making stack unwinding impossible for the OS profiler.
**Diagnostic:**
```bash
# Check if frame pointers are enabled
java -XX:+PrintFlagsFinal -version \
  | grep PreserveFramePointer
# If false, native frames will be [unknown]
```
**Fix:** Add `-XX:+PreserveFramePointer` to JVM startup flags and restart.
**Prevention:** Add `-XX:+PreserveFramePointer` to your standard production JVM flags template. Cost is approximately 1–3% CPU.

**Mode 3: `jstack` hangs on a JVM with `-XX:+UseZGC`**
**Symptom:** `jstack <pid>` hangs indefinitely; no output.
**Root Cause:** `jstack` uses the `attach` API which may conflict with certain ZGC configurations or low-disk-space conditions on `/tmp`.
**Diagnostic:**
```bash
# Alternative: use jcmd which is more robust
jcmd <pid> Thread.print > /tmp/threads.txt

# Check /tmp space (attach mechanism uses tmp)
df -h /tmp

# Check JVM is responsive
jcmd <pid> VM.version
```
**Fix:** Use `jcmd <pid> Thread.print` instead of `jstack`. Ensure `/tmp` has at least 100 MB free.
**Prevention:** Replace all `jstack` references in runbooks with `jcmd Thread.print`. Add a `/tmp` space check to your operational health checks.

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**
- JVM — the runtime being profiled
- Java Memory Management (Stack vs Heap Practical) — what the allocation profiler is measuring
- Thread (Java) — what the thread dump and contention analysis refers to

**Builds On This (learn these next):**
- Java Performance Tuning — applying profiling findings to JVM flags and code changes
- Observability & SRE — integrating continuous profiling into production monitoring
- GC Logs — complementary low-level GC timing data

**Alternatives / Comparisons:**
- JVM Flags (`-verbose:gc`) — low-level GC logging without a full profiler
- APM tools (Datadog, New Relic) — distributed tracing for service-level latency, not JVM internals
- Linux `perf` — OS-level CPU profiling for JNI/native-heavy workloads

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────┐
│ WHAT IT IS    Runtime measurement of JVM state   │
│ PROBLEM SOLVED Identify real hotspot, not guesses│
│ KEY INSIGHT   Profile first; optimise second     │
│ USE WHEN      Latency spike, OOM, CPU runaway    │
│ AVOID WHEN    — (always useful; JFR is free)     │
│ TRADE-OFF     Overhead vs accuracy (sampling vs  │
│               instrumentation)                   │
│ ONE-LINER     JFR=safe; async-prof=accurate      │
│ NEXT EXPLORE  Java Performance Tuning, GC Logs   │
└──────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

1. **(D — Root Cause)** A flamegraph shows 55% of CPU time in `sun.security.ssl.SSLSocketImpl.read()`. The application is an HTTP client calling an external API. `jstack` shows the thread as `RUNNABLE` but async-profiler shows it blocked on I/O. What JVM sampling bias explains the discrepancy between what `jstack` reports and what async-profiler reports — and how does async-profiler work around this?

2. **(B — Scale)** You have 200 JVM pods in Kubernetes. A p99 latency regression appeared after the last deployment but affects only 15% of pods. Individual JFR files are impractical to analyse. What continuous profiling architecture would you deploy to detect which method changed its CPU profile between the two deployments across the entire fleet?

3. **(C — Design Trade-off)** YourKit in instrumentation mode is 100% accurate for method timing but introduces 20–30% overhead. async-profiler is statistical with < 3% overhead. For each of these scenarios — (a) finding a production CPU regression at 2 AM, (b) benchmarking a new algorithm in a load test, (c) debugging a reported 50 ms latency spike in a specific endpoint — which tool is appropriate and why?
