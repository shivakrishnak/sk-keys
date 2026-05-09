---
version: 1
layout: default
title: "Java Performance Tuning"
parent: "Java Language"
grand_parent: "Technical Dictionary"
nav_order: 20
permalink: /java/java-performance-tuning/
id: JLG-020
category: Java & JVM Internals
difficulty: ★★★
depends_on: JVM, Garbage Collection (GC), Java Profiling (YourKit JFR), Java Memory Management (Stack vs Heap Practical)
used_by: Observability & SRE, Cloud - AWS
related: GC Tuning, Thread Pool Tuning, JVM Flags
tags:
  - java
  - jvm
  - performance
  - production
  - advanced
---

# JLG-020 - Java Performance Tuning

⚡ **TL;DR -** Java performance tuning is the disciplined cycle of profiling, identifying the dominant bottleneck (CPU / GC / I/O / lock contention), applying a targeted JVM or code change, and measuring the improvement - repeated until the SLA is met.

| | |
|---|---|
| **Depends on** | JVM, Garbage Collection (GC), Java Profiling (YourKit JFR), Java Memory Management (Stack vs Heap Practical) |
| **Used by** | Observability & SRE, Cloud - AWS |
| **Related** | GC Tuning, Thread Pool Tuning, JVM Flags |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:** A service is slow. Engineers add more hardware - 16 CPUs become 32, 8 GB heap becomes 32 GB. Latency barely moves. Cost doubles. The root cause - 400 threads contending on one `synchronized` method - was never identified. Tuning without a framework wastes money and delivers nothing.

**THE BREAKING POINT:** An e-commerce checkout service spikes to 4 seconds p99 under Black Friday load. The SLA is 500 ms. The team has 48 hours. Without a tuning methodology, the effort is scattered across dozens of speculative changes. With it, three profiling sessions identify three specific bottlenecks that, fixed sequentially, bring p99 to 310 ms.

**THE INVENTION MOMENT:** Performance tuning is not random code improvement. It is an engineering discipline with a repeatable process: establish a baseline, measure, identify the bottleneck type (CPU, GC, memory, I/O, locking), apply the correct category of fix, verify improvement. Guessing is replaced by evidence.

---

### 📘 Textbook Definition

**Java performance tuning** is the systematic process of improving a JVM application's throughput, latency, or resource efficiency by analysing runtime behaviour and applying targeted changes to code, JVM configuration, GC algorithm selection, thread pool sizing, memory layout, or I/O strategy. It encompasses: heap sizing (`-Xms`, `-Xmx`), GC algorithm selection and tuning, JIT compilation hints, thread pool configuration, allocation rate reduction, lock contention elimination, and I/O batching. All tuning decisions must be validated by measuring before and after.

---

### ⏱️ Understand It in 30 Seconds

**One line:** Performance tuning is measurement + targeted fix + re-measurement, repeated until the bottleneck is gone.

> Tuning a JVM without profiling is like tuning a car engine blindfolded - you might turn the right knob by accident, but you will waste hours turning the wrong ones first.

**One insight:** Every JVM has exactly one dominant bottleneck at any moment. Fix that one. The next bottleneck will then surface. Sequential elimination of measured bottlenecks always outperforms parallel speculative changes.

---

### 🔩 First Principles Explanation

**CORE INVARIANTS:**
1. You cannot improve what you have not measured.
2. Every performance problem is one of: CPU (too much computation), GC (too much allocation or retention), I/O (waiting on network/disk), locking (threads waiting on each other), or memory bandwidth (cache misses at hardware level).
3. Fixing the wrong bottleneck improves nothing; it may worsen other metrics.
4. JVM defaults are conservative general-purpose settings - production workloads almost always benefit from explicit configuration.
5. Heap sizing rule: `-Xms` = `-Xmx` (prevents resize pauses); set `-Xmx` to 70–75% of available container memory.

**DERIVED DESIGN:**
- **CPU bottleneck:** Reduce algorithmic complexity; eliminate allocations in hot paths; warm up JIT by running representative load before going live.
- **GC bottleneck:** Reduce allocation rate; pre-size collections; select appropriate GC algorithm for workload (G1 for latency, ZGC for sub-millisecond pauses, Parallel GC for throughput batch jobs).
- **Lock contention bottleneck:** Replace `synchronized` with `java.util.concurrent` locks; use lock-free structures (`ConcurrentHashMap`, `AtomicLong`); reduce critical section size.
- **I/O bottleneck:** Use NIO/async I/O; batch writes; tune connection pool size; add timeouts.

**THE TRADE-OFFS:**
**Gain:** Systematic tuning directly addresses the constraint; improvements are predictable and verifiable.
**Cost:** Profiling takes time; some JVM flags require JVM restart; some GC algorithm changes alter latency profiles unexpectedly under different load shapes.

---

### 🧪 Thought Experiment

**SETUP:** Your service handles 10k RPS. Average GC pause is 300 ms every 90 seconds (Full GC). p99 latency is 2.1 seconds. Teams propose: (A) rewrite in Go, (B) increase heap to 64 GB, (C) switch to ZGC, (D) profile and fix allocation hotspot.

**WHAT HAPPENS WITHOUT METHODOLOGY:** Team votes on (A) and spends 6 months rewriting. The rewrite takes 12 months. Two engineers resign.

**WHAT HAPPENS WITH METHODOLOGY:** You profile and find 900 MB/s allocation rate from a single `ObjectMapper` instantiated per request instead of reused. You fix it (option D): allocation rate drops to 50 MB/s. Eden no longer fills - Full GC disappears. p99 drops to 180 ms. Option C (ZGC) then reduces residual GC pauses to <1 ms. Total effort: 2 days. No rewrite needed.

**THE INSIGHT:** The JVM can be tuned to near-optimal performance for most workloads. Rewrites are rarely the answer. Measurement always is.

---

### 🧠 Mental Model / Analogy

> Tuning a JVM is like diagnosing a slow kitchen in a restaurant. You time each station: chopping (CPU), plating (GC), dishwashing (I/O), waiting for the grill (locking). The slowest station is your constraint. Fix that one station first - the others do not matter until it is fixed.

- **Kitchen throughput** → service throughput (requests/second)
- **Slowest station** → dominant bottleneck
- **Timer on each station** → profiler measuring CPU / GC / lock wait time
- **Adding chefs everywhere** → scaling hardware without identifying the bottleneck
- **Training the slowest station** → targeted fix on the measured hotspot

Where this analogy breaks down: unlike a kitchen, JVM bottlenecks can shift after a fix - the second bottleneck was always there but hidden behind the first one.

---

### 📶 Gradual Depth - Four Levels

**Level 1 - What it is (anyone can understand):**
Java performance tuning is figuring out why your Java program is slow or uses too much memory, then fixing it. You use tools to watch the program run, find the slowest part, and make that part faster.

**Level 2 - How to use it (junior developer):**
Start with `jstat -gcutil <pid> 1000` to check GC frequency. If Old Gen fills regularly, you have a memory growth issue. Use `jmap -histo:live` to find the top object types. Set `-Xms` = `-Xmx` to eliminate heap resize pauses. Switch to G1 GC if not already using it. Pre-size collections with known capacity.

**Level 3 - How it works (mid-level engineer):**
JIT compilation warms up over 5,000–10,000 invocations (C1 compile) and 10,000–15,000 invocations (C2 compile). Until warmup completes, throughput is lower and latency higher - always run load tests for at least 5 minutes before measuring baselines. GC tuning focuses on Eden size (controls Minor GC frequency), Survivor ratio (controls premature promotion), and Old Gen size (controls Full GC frequency). Lock contention analysis via `jstack` or JFR's lock profiling identifies `BLOCKED` threads; the fix is usually reducing critical section scope, upgrading to `ReadWriteLock`, or moving to lockless structures.

**Level 4 - Why it was designed this way (senior/staff):**
JVM performance is dominated by three subsystems that interact non-linearly: JIT, GC, and threading. JIT inlining improves CPU performance but can cause code deoptimisation when object types change (polymorphic inline caches invalidated) - a hidden cause of latency spikes after deployments. GC algorithm selection is a latency vs throughput trade-off baked into the collector design: Parallel GC maximises throughput but pauses are 100–500 ms; G1 targets 200 ms pause goals with moderate throughput impact; ZGC targets <1 ms pauses with ~5–10% throughput overhead. Understanding these trade-offs - not just turning flags - is what distinguishes a senior engineer's performance work.

---

### ⚙️ How It Works (Mechanism)

```
  Bottleneck Taxonomy
  ┌────────────────────────────────────┐
  │  CPU-bound                         │
  │  → High CPU%, slow hot methods     │
  │  → Fix: algo, JIT warm-up, alloc   │
  ├────────────────────────────────────┤
  │  GC-bound                          │
  │  → High GC pause, high alloc rate  │
  │  → Fix: heap size, GC algo, pool   │
  ├────────────────────────────────────┤
  │  Lock-bound                        │
  │  → BLOCKED threads, low CPU usage  │
  │  → Fix: ConcurrentHashMap, RWLock  │
  ├────────────────────────────────────┤
  │  I/O-bound                         │
  │  → Threads WAITING, low CPU        │
  │  → Fix: async I/O, pool sizing     │
  └────────────────────────────────────┘
  Identify category → apply correct fix
  → Measure improvement → repeat
```

---

### 🔄 The Complete Picture - End-to-End Flow

**NORMAL FLOW:**
```
  STEP 1: ESTABLISH BASELINE          ← YOU ARE HERE
    Run load test for 10 min
    Record: p50, p99, CPU%, GC rate
    │
    ▼
  STEP 2: PROFILE
    JFR: cpu, alloc, locks, GC
    async-profiler: flamegraph
    jstat: GC frequency/duration
    │
    ▼
  STEP 3: IDENTIFY BOTTLENECK TYPE
    CPU? GC? Lock? I/O? Memory?
    │
    ▼
  STEP 4: APPLY TARGETED FIX
    CPU  → fix hot method / reduce alloc
    GC   → tune heap / switch GC algo
    Lock → use concurrent structures
    I/O  → async / connection pool
    │
    ▼
  STEP 5: MEASURE IMPROVEMENT
    Repeat load test with same params
    Compare p99, CPU%, GC rate
    │
    ▼
  SLA met? → DONE
  SLA not met? → STEP 2 (next bottleneck)
```

**FAILURE PATH:**
- Tuning without baseline → cannot prove improvement; placebo effect common.
- Changing multiple flags simultaneously → cannot identify which change helped.
- Tuning in dev environment → JIT compilation profile differs; GC behaviour differs under real load patterns. Always tune under production-equivalent load.

**WHAT CHANGES AT SCALE:**
At scale (100+ pods), individual JVM tuning matters less than fleet-wide allocation rate and GC log aggregation. Use Prometheus JVM metrics (`jvm_gc_pause_seconds`, `jvm_memory_used_bytes`) to find outlier pods. A single misconfigured pod with a memory leak can destabilise a service mesh.

---

### 💻 Code Example

```java
// BAD - ObjectMapper created per request (massive alloc)
@GetMapping("/orders/{id}")
public String getOrder(@PathVariable long id) {
    // Creates a new ObjectMapper on every request
    ObjectMapper mapper = new ObjectMapper();
    return mapper.writeValueAsString(
        orderService.find(id));
}

// GOOD - ObjectMapper is thread-safe; share one instance
@RestController
public class OrderController {
    // ObjectMapper is expensive to create; reuse it
    private static final ObjectMapper MAPPER =
        JsonMapper.builder()
            .findAndAddModules()
            .build();

    @GetMapping("/orders/{id}")
    public String getOrder(@PathVariable long id)
            throws JsonProcessingException {
        return MAPPER.writeValueAsString(
            orderService.find(id));
    }
}
```

```bash
# JVM flags for production G1 tuning (Java 17)
# ─────────────────────────────────────────────
# Heap: avoid resize pauses; cap at 75% of RAM
-Xms4g -Xmx4g

# GC: G1 with 200ms pause target
-XX:+UseG1GC
-XX:MaxGCPauseMillis=200
-XX:G1HeapRegionSize=16m

# GC logging (structured, rotation)
-Xlog:gc*:file=/logs/gc.log:time,uptime,tags:filecount=10,filesize=20m

# JIT: enable tiered compilation (default Java 8+)
-XX:+TieredCompilation

# Container awareness (Java 11+)
-XX:+UseContainerSupport

# OOM safety net
-XX:+HeapDumpOnOutOfMemoryError
-XX:HeapDumpPath=/tmp/heap.hprof

# Enable JFR always-on
-XX:StartFlightRecording=\
  filename=/tmp/app.jfr,\
  settings=default,\
  dumponexit=true
```

```java
// BAD - high lock contention on synchronized map
private final Map<String, Integer> counts =
    new HashMap<>();

public synchronized void increment(String key) {
    counts.merge(key, 1, Integer::sum);
    // All threads serialise here - bottleneck!
}

// GOOD - ConcurrentHashMap is lock-free for reads
private final ConcurrentHashMap<String, AtomicInteger>
    counts = new ConcurrentHashMap<>();

public void increment(String key) {
    counts.computeIfAbsent(
        key, k -> new AtomicInteger(0)
    ).incrementAndGet();
    // Contention only on key creation, not reads
}
```

```java
// BAD - String concatenation in loop (N allocations)
public String buildReport(List<String> lines) {
    String result = "";
    for (String line : lines) {
        result += line + "\n"; // new String each iter
    }
    return result;
}

// GOOD - StringBuilder pre-sized to avoid realloc
public String buildReport(List<String> lines) {
    StringBuilder sb =
        new StringBuilder(lines.size() * 80);
    for (String line : lines) {
        sb.append(line).append('\n');
    }
    return sb.toString();
}
```

---

### ⚖️ Comparison Table

| GC Algorithm | Best For | Pause Target | Throughput Cost | Java Version |
|---|---|---|---|---|
| Serial GC | Single-core, tiny heap | N/A (stop-world) | Lowest overhead | All |
| Parallel GC | Batch jobs, throughput | 100–500 ms | Minimal | All |
| G1 GC | General purpose | Configurable (200 ms) | ~5% | Java 9+ default |
| ZGC | Low-latency services | < 1 ms | ~5–10% | Java 15+ production |
| Shenandoah | Low-latency (RedHat JDK) | < 10 ms | ~10% | Java 12+ |
| Epsilon GC | Performance testing only | None (no GC) | Zero | Java 11+ (testing only) |

---

### 🔁 Flow / Lifecycle

```
Phase 1: BASELINE
  10-min load test → record p50/p99/CPU/GC
    │
    ▼
Phase 2: CATEGORISE BOTTLENECK
  CPU? → check flamegraph
  GC?  → check jstat, GC logs
  Lock?→ check jstack BLOCKED count
  I/O? → check thread WAITING count
    │
    ▼
Phase 3: APPLY FIX (ONE AT A TIME)
  CPU:  fix hotspot method
  GC:   tune heap/algo OR fix leak
  Lock: use concurrent structures
  I/O:  async, pool size, timeouts
    │
    ▼
Phase 4: VERIFY
  Repeat identical load test
  Diff: p99 before vs after
  Confirm target metric improved
    │
    ▼
Phase 5: SLA CHECK
  Met → document, ship, monitor
  Not met → return to Phase 2
  (next bottleneck has surfaced)
```

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| "More heap always improves performance" | Larger heaps delay Full GC but make each pause longer. Setting `-Xmx` to 32 GB on a low-allocation service wastes memory and worsens GC pause when it does occur. Right-size to 2× live-set size. |
| "ZGC is always better than G1" | ZGC has ~5–10% throughput overhead and is designed for latency-sensitive services. Batch jobs with no latency requirement should use Parallel GC for maximum throughput. |
| "Setting `-server` flag enables server mode" | In Java 8+, the JVM detects server-class hardware automatically. `-server` and `-client` flags are ignored on modern JVMs. |
| "CPU usage of 80% means the JVM is slow" | High CPU usage for compute-bound work is healthy - it means the JVM is working. Low CPU usage with high latency usually indicates I/O waiting or lock contention. |
| "JVM warm-up only takes a few seconds" | JIT C2 compilation requires ~10,000–15,000 method invocations per method. Under modest load, full warm-up can take 5–15 minutes. Performance test results from the first 2 minutes are not representative. |

---

### 🚨 Failure Modes & Diagnosis

**Mode 1: GC storms - back-to-back Full GCs**
**Symptom:** Service latency spikes every 30–90 seconds; GC log shows `Pause Full` every few minutes reclaiming < 5% of heap.
**Root Cause:** Either a memory leak (Old Gen growing) or heap undersized relative to live object set.
**Diagnostic:**
```bash
# Watch GC in real time
jstat -gcutil $(pgrep java) 2000
# If O% climbs monotonically → memory leak
# If O% stable near 90% → heap undersized

# Heap dump to find retained objects
jcmd $(pgrep java) GC.heap_dump /tmp/heap.hprof
# Open in Eclipse MAT → "Leak Suspects" report
```
**Fix:** If leak: find retained reference chain. If undersized: increase `-Xmx` by 30%, monitor O% stabilisation. Switch to ZGC to eliminate pause spikes while investigating.
**Prevention:** Monitor `jvm_memory_used_bytes{area="heap",id="G1 Old Gen"}` in Prometheus. Alert when Old Gen > 70% of max.

**Mode 2: Thread pool saturation - request queue growing**
**Symptom:** Latency grows linearly with load; CPU is low (20–30%); throughput plateaus well below expected.
**Root Cause:** Thread pool too small for I/O-bound workload; threads are WAITING on downstream calls, not executing.
**Diagnostic:**
```bash
# Count WAITING threads
jstack $(pgrep java) \
  | grep "java.lang.Thread.State: WAITING" \
  | wc -l

# Compare to RUNNABLE threads
jstack $(pgrep java) \
  | grep "RUNNABLE" | wc -l

# If WAITING >> RUNNABLE: I/O bound, pool too small
```
**Fix:**
```java
// BAD - default Tomcat pool of 200 threads
# application.properties (Spring Boot)
# server.tomcat.threads.max=200  # default

// GOOD - tune to I/O wait ratio
# Optimal threads ≈ CPU * (1 + wait_time/cpu_time)
# For 8 CPU cores, 90% I/O wait: 8 * (1 + 9) = 80
# But cap at practical limit: ~300-400 for HTTP
server.tomcat.threads.max=300
server.tomcat.threads.min-spare=50
```
**Prevention:** Use Little's Law to size thread pools: `threads = throughput × latency`. Monitor `executor_pool_active_threads` in actuator metrics.

**Mode 3: JIT deoptimisation spikes - latency spikes after deployment**
**Symptom:** Service has good latency for 5 minutes post-deploy, then spikes every few minutes, then stabilises.
**Root Cause:** JIT's polymorphic inline caches are invalidated when new class implementations are loaded post-warmup - triggering code deoptimisation and recompilation.
**Diagnostic:**
```bash
# Enable JIT deoptimisation logging
-XX:+UnlockDiagnosticVMOptions
-XX:+LogCompilation
-XX:+TraceDeoptimization

# Or via JFR: look for "Deoptimization" events
jcmd $(pgrep java) JFR.start \
  settings=profile duration=120s \
  filename=/tmp/jit.jfr
# Open JMC → Compiler → Compilations tab
```
**Fix:** Implement a JVM warm-up phase that replays representative traffic (e.g., 5% of prod traffic through a canary) before cutting over full load.
**Prevention:** Deploy with a pre-warm script. In Kubernetes, use a `readinessProbe` that only passes after warmup traffic has been served successfully.

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**
- JVM - the execution engine being tuned
- Garbage Collection (GC) - the largest source of JVM latency
- Java Profiling (YourKit, JFR) - how to find what to tune
- Java Memory Management (Stack vs Heap Practical) - what the heap metrics mean

**Builds On This (learn these next):**
- GC Tuning - deep-dive into per-GC-algorithm flags and pause analysis
- Thread Pool Tuning - optimal sizing for CPU-bound vs I/O-bound workloads
- Observability & SRE - wiring JVM metrics into production monitoring

**Alternatives / Comparisons:**
- GraalVM Native Image - AOT compilation, no JVM warmup, lower memory, lower peak throughput
- Virtual Threads (Java 21) - eliminates thread pool sizing for I/O-bound workloads
- Reactive programming (Project Reactor) - non-blocking I/O reduces thread requirements

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────┐
│ WHAT IT IS    Systematic JVM bottleneck removal  │
│ PROBLEM SOLVED Slow service, high GC, low thrput │
│ KEY INSIGHT   Profile → fix ONE bottleneck → re- │
│               measure; never guess               │
│ USE WHEN      Latency/throughput SLA not met     │
│ AVOID WHEN    - (always needed pre-production)   │
│ TRADE-OFF     Tuning time vs hardware cost       │
│ ONE-LINER     Measure → fix hotspot → verify     │
│ NEXT EXPLORE  GC Tuning, Virtual Threads, ZGC    │
└──────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

1. **(B - Scale)** Your Kubernetes deployment has 50 pods each with `-Xmx2g`. During peak load, 10 pods are OOM-killed. A colleague suggests increasing `-Xmx` to 6g. Before doing so, what three profiling measurements would you take to determine whether the correct fix is more heap, less allocation, or a GC algorithm change - and which fix is cheapest in infrastructure cost?

2. **(C - Design Trade-off)** Virtual Threads (Java 21) eliminate the thread pool sizing problem for I/O-bound workloads by using carrier threads. Given that a traditional Tomcat application with 300 threads now runs with 10,000 virtual threads, how does the GC, heap, and memory pressure profile change - and what new tuning concerns emerge that did not exist with platform threads?

3. **(D - Root Cause)** After a code change, p99 latency increases from 120 ms to 800 ms. CPU usage drops from 70% to 25%. GC frequency and pause times are unchanged. What category of bottleneck has most likely appeared - and what is your first profiling command to confirm the hypothesis?
