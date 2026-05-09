---
id: CSF-070
title: Compiler/Runtime Selection at Scale
category: CS Fundamentals - Paradigms
tier: tier-1-foundations
folder: CSF-cs-fundamentals
difficulty: ★★★
depends_on:
used_by:
related:
tags:
  - csf
  - advanced
  - architecture
  - bestpractice
status: draft
version: 1
layout: default
parent: "CS Fundamentals - Paradigms"
grand_parent: "Technical Dictionary"
nav_order: 70
permalink: /csf/compilerruntime-selection-at-scale/
---

# CSF-070 - Compiler/Runtime Selection at Scale

⚡ TL;DR - At scale, compiler and runtime selection decisions affect GC pause distribution, startup latency, native image size, and observability; GraalVM native image, JVM ZGC, and AOT vs JIT tradeoffs are architectural decisions, not configuration choices.

| CSF-070         | Category: CS Fundamentals - Paradigms | Difficulty: ★★★ |
| :-------------- | :------------------------------------ | :-------------- |
| **Depends on:** | CSF-058, CSF-062, CSF-067             |                 |
| **Used by:**    |                                       |                 |
| **Related:**    | CSF-058, CSF-062, CSF-067, CSF-077    |                 |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
A team deploys a Spring Boot service on Kubernetes.
Startup time: 8 seconds. Lambda function: 4-second cold
start. Serverless compute bill: 10x higher than expected
because containers can't scale down (slow startup). GC
pauses cause P99 spikes that exceed SLA. These are
compiler/runtime decisions, not application code decisions.

**THE BREAKING POINT:**
Microservices at Netflix scale: 500+ services, thousands
of pods. If every pod has 300ms GC pauses, the P99 of any
request that crosses 3 services is: `1 - (0.997)^3 = ~0.9%`
cumulative GC impact. At 10,000 RPS, that's 90 requests/sec
hitting GC pauses. Choosing ZGC (sub-1ms pauses) instead
of G1GC is an architectural decision.

**THE INVENTION MOMENT:**
GraalVM (2018): compile Java ahead-of-time to native
executables. Result: 50ms startup, 80% smaller footprint.
Azul Zing JVM: commercial JVM with pauseless GC.
OpenJ9: IBM's JVM with aggressive JIT caching (class
data sharing). Each solves a different scale problem.

**EVOLUTION:**
Java 21+ Virtual Threads (Project Loom): million threads
on JVM without thread-per-request overhead. GraalVM Native
Image: Spring Boot Native (AOT-compiled Spring). Go's
GC: sub-1ms pauses, but stop-the-world still exists.
Rust: zero GC, RAII memory, single-digit microsecond P99.
The selection space is richer than ever.

---

### 📘 Textbook Definition

**Compiler selection** determines how source code is
transformed to executable form: **JIT (Just-In-Time)**
compiles at runtime based on profiling data (HotSpot C2),
enabling aggressive optimisations for actual workloads;
**AOT (Ahead-Of-Time)** compiles before deployment
(GraalVM native image, Rust), providing fast startup
and small footprint at the cost of JIT-profile-based
optimisations. **Runtime selection** determines memory
management, thread model, and I/O dispatch: G1GC
vs ZGC vs Shenandoah affect GC pause distribution;
JVM thread-per-request vs Loom virtual threads vs Go
goroutines affect concurrency capacity.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
At scale, GC algorithm, JIT vs AOT, and thread model are architectural decisions with measurable P99, cost, and capacity trade-offs.

**One analogy:**

> Compiler/runtime selection is like choosing an engine
> for a vehicle fleet. A diesel engine (JIT JVM) is efficient
> at sustained highway speed but needs warm-up time. An
> electric motor (GraalVM native) starts instantly but
> has a different efficiency curve. A turbocharged engine
> (Rust/C++) maximises top-end performance but requires
> skilled maintenance. You choose the engine for the route,
> not for theoretical top speed.

**One insight:**
The JVM's JIT is only better than AOT for long-running
services that actually warm up. For short-lived lambdas
or frequently scaled pods, native image (AOT) is often
faster and cheaper.

---

### 🔩 First Principles Explanation

**CORE INVARIANTS:**

1. JIT: profile-guided optimisation; best peak throughput; slow warmup; GC overhead.
2. AOT: fast startup; small footprint; misses dynamic profile-guided opts; no GC warmup.
3. GC pause duration: G1GC up to 200ms (stop-the-world); ZGC <1ms; Shenandoah <1ms; Go <1ms.
4. Thread model: OS threads (JVM pre-Loom): ~1MB stack/thread; Loom virtual threads: ~kB; goroutines: 2KB.
5. Startup latency: JVM ~300ms; JVM with class-data-sharing ~150ms; GraalVM native ~50ms; Go binary ~5ms.

**EVALUATION DIMENSIONS AT SCALE:**

```
Workload: Short-lived / Lambda / Batch job
  -> Startup time matters most
  -> Choose: GraalVM native, Go binary, Rust binary
  -> Avoid: Standard JVM (300ms startup)

Workload: Long-running / Stateful / High-throughput API
  -> Peak throughput + GC pause matter
  -> Choose: JVM (HotSpot C2 JIT) + ZGC
  -> Or: Go goroutines + GC tuning
  -> Or: Rust (no GC, maximum P99)

Workload: CPU-bound / Latency-critical (<1ms P99)
  -> GC pauses disqualified even at sub-1ms
  -> Choose: Rust (no GC) or C++
  -> Or: Java realtime JVM (Azul Zing)

Workload: Memory-constrained / Edge / IoT
  -> Runtime footprint matters
  -> Choose: GraalVM native, Rust, TinyGo
  -> Avoid: Full JVM or CPython
```

**DERIVED DESIGN:**

- **Spring Boot + GraalVM Native**: `./mvnw spring-boot:build-image -Pnative` → native image; sub-100ms startup
- **JVM + ZGC**: `-XX:+UseZGC -Xmx4g`; sub-1ms GC pauses; suitable for < 10ms P99 SLA
- **Go binaries**: single static binary; 5ms startup; minimal footprint; goroutine scheduler
- **Java Loom**: `-Dspring.threads.virtual.enabled=true` (Spring Boot 3.2+); millions of virtual threads

**ESSENTIAL vs ACCIDENTAL COMPLEXITY:**
**Essential:** Long-running services benefit from profile-guided JIT; serverless functions need fast startup.
**Accidental:** Using JVM defaults for all workloads regardless of startup and GC requirements.

---

### 🧪 Thought Experiment

**SETUP:**
Choose runtime for three workloads:

**Workload A: AWS Lambda function, HTTP trigger, executes in 50ms**

```
JVM (standard): 500ms cold start -> Lambda bill 10x higher
JVM + SnapStart (CRaC): 200ms restored -> still slow
GraalVM native: 50ms cold start -> Lambda bill minimal
Go binary: 10ms cold start -> Lambda bill minimal
```

**Workload B: Real-time trading service, P99 < 2ms, 100k RPS**

```
JVM + G1GC: GC pause up to 200ms -> disqualified
JVM + ZGC: GC pause < 1ms -> P99 potentially achievable
Go: GC pause < 1ms -> viable
Rust: zero GC -> best P99 option; highest dev cost
```

**Workload C: ML batch training, 4-hour jobs**

```
Python + PyTorch: best ML ecosystem; GIL irrelevant (GPU bound)
JVM: poor ML tooling -> not preferred
Rust: no ML ecosystem -> impractical
```

**THE INSIGHT:**
No runtime wins for all three workloads. The answer is
workload-specific selection.

---

### 🧠 Mental Model / Analogy

> Compiler/runtime selection is like transmission choice
> for a race car. Manual transmission (AOT/Rust): full
> driver control; fastest for skilled drivers; highest
> maintenance. Automatic (JVM JIT): self-optimises for
> actual driving conditions; lower driver overhead;
> slightly slower at peak. CVT (Go): smooth, efficient,
> optimised for average conditions. Choose transmission
> for the race, not the spec sheet.

**Element mapping:**

- Transmission type = compiler/runtime
- Driver skill = developer/ops expertise
- Race conditions = actual production workload
- Spec sheet performance = synthetic benchmark
- Actual lap time = production P99

Where this analogy breaks down: in software, you can
change "transmission" (runtime) mid-deployment more
easily than in a physical race.

---

### 📶 Gradual Depth - Four Levels

**Level 1 - What it is (anyone can understand):**
The same Java code can run very differently depending
on how it's compiled and what JVM settings are used.
Choosing the right settings can make services start
faster, use less memory, and avoid pauses.

**Level 2 - How to use it (junior developer):**
Enable ZGC for latency-sensitive services:
`-XX:+UseZGC -Xms1g -Xmx4g`.
Enable Virtual Threads for high-concurrency IO services:
`-Dspring.threads.virtual.enabled=true`.
For lambdas/CLI: evaluate GraalVM native compilation.
Profile before and after: `jstat -gcutil <pid>` for GC stats.

**Level 3 - How it works (mid-level engineer):**
ZGC is concurrent: GC threads run alongside application
threads; most GC work happens without stopping threads.
Pause = only when thread roots are scanned (< 1ms).
G1GC is mostly concurrent but has stop-the-world phases
for full GCs and evacuation. JVM warm-up: C1 (client
compiler) compiles immediately; C2 (server compiler)
compiles after 10,000 invocations with profile data.
GraalVM AOT skips this: optimises based on static
analysis (closed-world assumption).

**Level 4 - Why it was designed this way (senior/staff):**
The JVM's JIT is more powerful than AOT for long-running
services because it can: (1) inline virtual calls based
on actual class frequency (can't predict at AOT compile
time); (2) deoptimise and re-optimise when class frequency
changes (impossible in AOT). GraalVM native image sacrifices
these JIT-specific optimisations for startup speed. This
is why native image is best for short-lived workloads
and JIT JVM is best for long-running, throughput-optimised
services. The choice is determined by workload lifecycle.

**Expert Thinking Cues:**

- Lambda or serverless: always evaluate GraalVM native / Go first
- P99 > SLA and correlated with GC events: switch GC algorithm before code changes
- High thread count (>1000 concurrent): evaluate Loom virtual threads; Go goroutines

---

### ⚙️ How It Works (Mechanism)

**JVM GC selection:**

```bash
# G1GC (default, Java 9+): good throughput, up to 200ms pause
java -XX:+UseG1GC -Xmx4g app.jar

# ZGC (Java 15+): sub-1ms pauses, good for latency-sensitive
java -XX:+UseZGC -Xmx4g app.jar

# Shenandoah (RedHat, OpenJDK): similar to ZGC
java -XX:+UseShenandoahGC -Xmx4g app.jar

# Check GC pause times in logs
java -Xlog:gc*:file=gc.log:time,uptime:filecount=10 app.jar
grep 'Pause' gc.log | awk '{print $NF}' | sort -n | tail -10
```

**GraalVM Native Image (Spring Boot):**

```bash
# Build native image (requires GraalVM JDK)
./mvnw spring-boot:build-image -Pnative
docker run --rm -p 8080:8080 my-app:latest
# Startup: ~100ms vs ~3000ms for JVM
# Memory: ~80MB vs ~350MB for JVM
```

**Java Virtual Threads (Loom, Java 21):**

```java
// Platform thread: ~1MB stack, OS thread per request
Executor executor = Executors.newFixedThreadPool(200);

// Virtual thread: ~kB stack, millions possible, auto-scheduled
Executor vtExecutor = Executors.newVirtualThreadPerTaskExecutor();
// Spring Boot 3.2+: spring.threads.virtual.enabled=true
```

---

### 🔄 The Complete Picture - End-to-End Flow

**RUNTIME SELECTION FLOW:**

```
Define workload requirements:          ← YOU ARE HERE
  Startup latency SLA (lambda vs long-running)
  P99 latency SLA (1ms? 10ms? 100ms?)
  Concurrency model (I/O-bound vs CPU-bound)
  Memory constraints (edge? cloud? cost)
  |
Apply hard vetoes:
  P99 < 1ms: eliminate GC languages (keep Rust/Azul Zing)
  Startup < 100ms: eliminate standard JVM
  CPU-bound + Python: GIL veto (multiprocessing or different lang)
  |
Evaluate remaining options:
  JVM + ZGC: sub-1ms pauses, throughput optimised
  JVM + GraalVM Native: fast startup, smaller footprint
  Go: goroutines, sub-1ms GC, static binary
  Rust: zero GC, microsecond P99, dev cost
  |
Benchmark with realistic load:
  Not synthetic; production-representative traffic
  |
Document in ADR:
  Decision + alternatives + rationale
```

---

### ⚖️ Comparison Table

| Runtime            | Startup  | GC Pause    | Peak Throughput | Best For                   |
| ------------------ | -------- | ----------- | --------------- | -------------------------- |
| JVM HotSpot + G1GC | 300ms    | < 200ms     | High (JIT)      | Long-running APIs          |
| JVM HotSpot + ZGC  | 300ms    | < 1ms       | High (JIT)      | Latency-sensitive APIs     |
| GraalVM Native     | 50-100ms | < 1ms       | Medium (AOT)    | Serverless, CLI, Lambda    |
| Go binary          | 5-10ms   | < 1ms       | High            | Infra, CLIs, K8s ops       |
| Rust               | < 1ms    | None (RAII) | Highest         | Ultra-low latency, systems |
| CPython            | 100ms    | ms range    | Low (GIL)       | ML, scripts, data          |

---

### ⚠️ Common Misconceptions

| Misconception                                  | Reality                                                                                                |
| ---------------------------------------------- | ------------------------------------------------------------------------------------------------------ |
| "GraalVM Native is always faster"              | Native is faster at startup; JIT often wins at peak throughput for long-running services               |
| "ZGC has zero pauses"                          | ZGC has sub-1ms stop-the-world phases for scanning thread roots; not zero but near-zero                |
| "Virtual threads replace goroutines"           | Virtual threads (Loom) and goroutines solve similar problems; goroutines have a longer track record    |
| "Just tune GC; no need for language change"    | GC tuning helps; but for sub-1ms P99 requirements, language/runtime change may be necessary            |
| "AOT compiled code doesn't support reflection" | GraalVM native image supports reflection with metadata configuration; but requires explicit annotation |

---

### 🚨 Failure Modes & Diagnosis

**Mode 1: GC Pause Exceeding P99 SLA**
**Symptom:** P99 spikes every ~5 min; correlates with GC events.
**Diagnostic:**

```bash
java -Xlog:gc*:file=gc.log -jar app.jar
awk '/Pause/ {print $0}' gc.log | sort -k5 -n -t',' | tail -20
# Find longest pause: if >SLA, change GC algorithm
```

**Fix:** `-XX:+UseZGC` (Java 15+) or `-XX:+UseShenandoahGC`.

**Mode 2: Cold Start Latency on Lambda**
**Symptom:** First request on Lambda takes 3-5 seconds.
**Diagnostic:** CloudWatch Lambda logs: `Init Duration` metric.
**Fix:** GraalVM native image compilation; or Lambda SnapStart (JVM resume from snapshot).

**Mode 3: GraalVM Native Reflection Failure**
**Symptom:** `ClassNotFoundException` or `NoSuchMethodException` on native image startup.
**Root Cause:** Reflection not configured for native image; dynamic class loading unsupported.
**Diagnostic:** Run with `-agentlib:native-image-agent` to generate reflection config.
**Fix:** Add `reflect-config.json`; or annotate with `@RegisterReflectionForBinding`.

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**

- [[CSF-058 - JIT vs AOT Compilation Deep Dive]]
- [[CSF-062 - Language Runtime Internals]]
- [[CSF-067 - Language Evaluation Framework]]

**Builds On This (learn these next):**

- [[CSF-077 - Language Design Rationale (Rust, Go, Kotlin)]]

**Alternatives / Comparisons:**

- GraalVM vs OpenJ9 vs HotSpot
- Azul Zing (pauseless JVM) for ultra-latency

---

### 📌 Quick Reference Card

```
┌─────────────────────────────────────────────────────┐
│ WHAT IT IS      GC algorithm, JIT vs AOT, thread model   │
│                 are architectural, not config decisions  │
│ PROBLEM         Default JVM settings wrong for           │
│ IT SOLVES       serverless, low-latency, memory-constrained│
│ KEY INSIGHT     JIT wins at peak throughput; AOT wins    │
│                 at startup; ZGC wins at low latency     │
│ USE WHEN        Lambda: native; latency: ZGC; concurrency:│
│                 Loom or goroutines                     │
│ AVOID           Default G1GC for sub-5ms P99 SLAs        │
│ TRADE-OFF       JIT throughput vs AOT startup            │
│ ONE-LINER       Match runtime to workload lifecycle      │
│ NEXT EXPLORE    ZGC docs, GraalVM native, Loom virtual   │
└─────────────────────────────────────────────────────┘
```

**If you remember only 3 things:**

1. GC algorithm selection (ZGC vs G1GC) is an architectural decision; it directly affects P99 latency distribution.
2. GraalVM native image solves cold start for Lambda/serverless; standard JVM JIT wins at sustained throughput.
3. Java Virtual Threads (Loom) and Go goroutines both solve thread-per-request scalability; the choice depends on ecosystem.

**Interview one-liner:**
"Compiler and runtime selection at scale means choosing between JIT (peak throughput, profile-guided) and AOT (fast startup, small footprint), and between GC algorithms where ZGC's sub-1ms pauses enable latency SLAs that G1GC's stop-the-world phases cannot meet."

---

### 💎 Transferable Wisdom

**Reusable Engineering Principle:**
Default settings are designed for the average case. At
scale, you are not the average case. Every configurable
runtime parameter — GC algorithm, JIT thresholds, thread
pool size, heap ratio — has a correct setting for your
specific workload. The defaults are the starting point
for measurement, not the production configuration.

**Where else this pattern appears:**

- **Database buffer pool** — InnoDB `innodb_buffer_pool_size` defaults to 128MB; production should be 80% of RAM
- **Linux kernel network stack** — `net.core.somaxconn` defaults to 128; high-traffic services need 65535
- **Container resource limits** — default CPU/memory limits often wrong; JVM in container without `-XX:+UseContainerSupport` misreads host RAM

---

### 💡 The Surprising Truth

GraalVM native image can be _slower_ than JVM JIT for
long-running, throughput-sensitive services. This is
because HotSpot C2 JIT performs profile-guided optimisations
that are impossible at AOT compile time: it can observe
that 99% of virtual calls to `Animal.speak()` are actually
`Dog.speak()` and inline the implementation directly
(eliminating vtable lookup). GraalVM native image uses
static analysis and can't observe actual runtime class
frequency. For a 24/7 API service that processes millions
of requests, HotSpot's JIT-optimised steady state often
outperforms GraalVM native image by 20-40% in throughput.
GraalVM native image wins on startup and memory; HotSpot
JIT wins on peak throughput. Neither is universally superior.

---

### 🧠 Think About This Before We Continue

**Q1 (Production):** A Spring Boot service currently uses
G1GC with P99 = 150ms. The SLA is P99 < 10ms. Switching
to ZGC should reduce GC pauses to sub-1ms. But what other
factors besides GC contribute to P99 latency, and how
would you diagnose whether GC is the actual bottleneck?

_Hint:_ Profile first: are P99 spikes correlated with GC
events? Use `-Xlog:gc*` and correlate with application
latency traces. Other P99 contributors: network latency,
DB slow query, thread pool saturation, serialisation.

**Q2 (Scale):** You are architecting a platform that runs
both long-running API services (P99 < 5ms, 24/7) and
short-lived batch jobs (run for 30 seconds, then exit).
Can you use the same JVM configuration for both, or do
you need different runtimes?

_Hint:_ Long-running: JVM JIT + ZGC (peak throughput,
concurrent GC). Short-lived batch: JVM never warms up;
GraalVM native or Go binary is better. You need different
runtime strategies per workload lifecycle.

**Q3 (Design Trade-off):** Java Virtual Threads (Project
Loom) promise to run millions of threads without the
cost of OS threads. Go has had goroutines for 12 years.
If both achieve the same result (cheap concurrency), what
are the remaining differences that would make you choose
one over the other for a new service in 2024?

_Hint:_ Ecosystem (Spring Boot Loom vs Go stdlib), debugging
tools (JVM profilers vs Go pprof), deployment (JVM JAR
vs Go static binary), concurrency model (structured
concurrency in Loom vs goroutine lifecycle in Go). Both
are viable; ecosystem fit and team expertise decide.
