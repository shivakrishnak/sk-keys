---
id: JVM-065
title: "JVM Selection Framework (HotSpot vs GraalVM)"
category: Java & JVM Internals
tier: tier-3-java
folder: JVM-java-jvm-internals
difficulty: ★★★
depends_on: JVM-052, JVM-053, JVM-060
used_by:
related: JVM-045, JVM-051, JVM-069
tags:
  - jvm
  - java
  - architecture
  - advanced
status: complete
version: 2
layout: default
parent: "Java & JVM Internals"
grand_parent: "Technical Dictionary"
nav_order: 61
permalink: /jvm/jvm-selection-framework-hotspot-vs-graalvm/
---

# JVM-061 - JVM Selection Framework (HotSpot vs GraalVM)

**⚡ TL;DR** - HotSpot JIT is the right default for long-running services; GraalVM Native Image is right for serverless/CLI/startup-critical workloads; GraalVM JIT mode is a drop-in upgrade for peak throughput.

| Field | Value |
|---|---|
| **Depends on** | [[JVM-052 - GraalVM]], [[JVM-053 - Native Image]], [[JVM-060 - JVM Architecture Decisions at Scale]] |
| **Used by** | (none - decision framework entry) |
| **Related** | [[JVM-045 - JIT Compiler]], [[JVM-051 - AOT Compilation]], [[JVM-069 - Performance Intuition via JVM Internals]] |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
Teams default to "just use Java with the JDK" without evaluating whether GraalVM Native Image would be more appropriate. Conversely, teams hype Native Image and migrate all services before discovering that 40% of their services use reflection patterns incompatible with Native Image's closed-world assumption. A framework for systematic decision-making prevents both defaultism and hype-driven migrations.

**THE BREAKING POINT:**
A platform team at a mid-size SaaS company migrated 150 Spring Boot services to GraalVM Native Image based on startup time benchmarks. 30 of those services used dynamic proxies, runtime code generation, or native library access via JNI - all incompatible with Native Image without significant refactoring. The migration stalled for six months. A selection framework would have identified these services in a day.

**THE INVENTION MOMENT:**
As the JVM ecosystem split into HotSpot JVM, GraalVM JIT mode, and GraalVM Native Image, engineering teams needed a systematic way to make the selection. The framework emerges from accumulated migration experience: classifying workloads by startup sensitivity, throughput requirements, heap constraints, and framework compatibility.

**EVOLUTION:**
- 2018: GraalVM 1.0 - Native Image as experimental technology
- 2019-2022: Early adopters (Micronaut, Quarkus) build Native Image compatibility first
- 2023: Spring Boot 3.0+ with GraalVM Native Image support (AOT processing)
- 2024: Generational ZGC in OpenJDK 21+ narrows the throughput gap favouring HotSpot
- Today: Most new microservice frameworks default-support both JVM and native modes

---

### 📘 Textbook Definition

The **JVM selection framework** is a structured decision process for choosing between HotSpot JIT (standard JVM), GraalVM JIT mode, and GraalVM Native Image for a given application. The decision is driven by four axes: (1) **Startup sensitivity**: Native Image for <100ms startup requirements; HotSpot for applications where startup latency is acceptable. (2) **Throughput at steady state**: HotSpot C2 or GraalVM JIT for peak throughput in long-running services; Native Image lacks adaptive JIT for peak optimisation. (3) **Memory footprint**: Native Image for memory-constrained environments; HotSpot for applications where JIT-optimised throughput justifies higher memory. (4) **Framework and reflection compatibility**: Native Image requires closed-world assumption compliance; HotSpot runs any bytecode.

---

### ⏱️ Understand It in 30 Seconds

**One line:** Choose HotSpot for long-running throughput, GraalVM Native Image for startup-critical or memory-constrained, GraalVM JIT as a drop-in throughput upgrade.

> Like choosing between a diesel truck (HotSpot JIT - high sustained throughput, expensive to start), an electric scooter (Native Image - instant startup, limited range), and a hybrid (GraalVM JIT - best of both, but complex).

**One insight:** The single most important selection criterion is whether your workload is "long-running service" or "short-lived execution." Long-running services (servers, APIs, workers) benefit from JIT's progressive optimisation. Short-lived executions (CLI tools, Lambda functions, FaaS) pay JVM startup cost for every invocation - Native Image eliminates that cost entirely.

---

### 🔩 First Principles Explanation

**CORE INVARIANTS:**
1. JIT compilation requires execution time to profile and optimise - it pays off over thousands of invocations
2. Native Image compiles everything at build time - no warm-up, but no adaptive optimisation
3. The closed-world assumption means Native Image must see all reachable code at build time
4. Throughput and startup latency optimise different variables; the winner depends on invocation frequency

**DERIVED DESIGN:**
From invariant 1: JIT is optimal for services invoked millions of times. The 30-120 second warm-up is amortised over millions of calls.
From invariant 2: Native Image is optimal when each invocation is independent (FaaS, CLI) - the warm-up cannot be amortised.
From invariant 3: any application using `Class.forName()`, dynamic proxies, or JNI with unknown types requires extra Native Image configuration.
From invariant 4: for a service that runs for 30 days continuously, HotSpot C2 throughput dominates; for a function that runs for 100ms per day, native startup dominates.

**THE TRADE-OFFS:**
**HotSpot Gain:** Adaptive JIT produces optimal native code; any Java bytecode works; best ecosystem support
**HotSpot Cost:** 50-200ms startup; 200-500MB RAM minimum; warm-up latency under load

**Native Image Gain:** <10ms startup; 50-150MB RAM; no JVM needed at runtime; smaller attack surface
**Native Image Cost:** No JIT (peak throughput 15-30% below HotSpot at steady state); build-time AOT requires reflection config; build time 2-5 minutes

**GraalVM JIT Gain:** Drop-in HotSpot replacement; 10-30% better peak throughput on some workloads via Graal compiler
**GraalVM JIT Cost:** Same startup as HotSpot; slightly higher memory; commercial EE version for best results

**ESSENTIAL vs ACCIDENTAL COMPLEXITY:**
**Essential:** Different workload patterns have different optimal execution models. This trade-off is irreducible.
**Accidental:** The reflection configuration requirement for Native Image is accidental complexity. Frameworks like Quarkus and Micronaut eliminate it by generating the config automatically at build time.

---

### 🧪 Thought Experiment

**SETUP:** Two applications: App A is a Spring Boot REST API receiving 50,000 requests/day, running 24/7. App B is a Java Lambda function that processes S3 events, averaging 3 invocations/hour.

**WHAT HAPPENS IF BOTH USE HOTSPOT:**
App A: warm-up in first 2 minutes, then JIT-optimised for 24 hours. Warm-up cost: 120 seconds / 86,400 seconds/day = 0.14% overhead. Excellent choice.
App B: each Lambda invocation starts a fresh JVM. Startup: 800ms. Function execution: 50ms. JVM startup = 94% of total runtime. On a 100ms invocation budget, impossible. Cold starts dominate cost.

**WHAT HAPPENS IF BOTH USE NATIVE IMAGE:**
App A: instant startup, but no adaptive JIT. At 50,000 requests/day peak, throughput is 15% lower than HotSpot at steady state. For a throughput-bound API, this means either more servers or slower response times.
App B: startup <10ms. Function execution: 50ms. JVM startup = 17% of total runtime - acceptable. Cold start problem solved.

**THE INSIGHT:**
The selection is not about which runtime is "better" - it is about which runtime's strengths match the workload's characteristics. Invocation frequency and lifetime are the decisive variables.

---

### 🧠 Mental Model / Analogy

> Think of HotSpot JIT as hiring a full-time employee who gets better at the job over time - slow to onboard but eventually performs at expert level. GraalVM Native Image is a contractor who arrives fully trained for a specific task but cannot adapt to new requirements that weren't in the original brief. GraalVM JIT is a more talented full-time employee who commands a premium but reaches expert level faster.

Element mapping:
- Employee = JVM runtime
- Onboarding period = warm-up / JIT compilation phase
- Expert performance = C2-compiled native execution
- Contractor's specific training = AOT compilation at build time
- New requirements = runtime reflection / dynamic class loading

Where this analogy breaks down: unlike employees, you can have millions of copies of the same runtime simultaneously. The "hiring cost" (startup latency) matters at a different scale in software than in human staffing.

---

### 📶 Gradual Depth - Four Levels

**Level 1 - What it is (anyone can understand):**
There are different ways to run Java programs. The standard JVM starts a bit slowly but gets very fast after running for a while. GraalVM can compile Java into a native program that starts instantly but doesn't get faster over time. The choice depends on whether your program runs constantly (use standard JVM) or needs to start fast each time (use native).

**Level 2 - How to use it (junior developer):**
Use this decision checklist: (1) Does startup time matter? Serverless/Lambda/CLI: yes, use Native Image. Long-running service: no, use HotSpot. (2) Does your framework support Native Image? Spring Boot 3+ yes; older Spring no. Quarkus/Micronaut yes. Custom frameworks: unknown until tested. (3) Do you have dynamic class loading, JNI, or extensive reflection? If yes, Native Image requires extra work. (4) Is memory a hard constraint? Native Image uses 50-150MB; HotSpot uses 200-500MB minimum.

**Level 3 - How it works (mid-level engineer):**
The selection has three GraalVM modes to distinguish: (1) GraalVM JVM mode (default `java` command on GraalVM) - uses the Graal JIT compiler instead of HotSpot C2. Drop-in replacement. TCK-compatible. 10-30% throughput improvement on compiler-intensive workloads. (2) GraalVM Native Image - `native-image` tool produces a standalone binary. Requires AOT processing (reflection config, serialisation config). No JVM at runtime. (3) GraalVM Native Image with PGO (Profile-Guided Optimisation) - instruments the binary, collects real traffic profiles, recompiles with profile data. Narrows the throughput gap with HotSpot JIT but requires two build stages.

**Level 4 - Why it was designed this way (senior/staff):**
The HotSpot vs Native Image trade-off is a fundamental tension between adaptive vs predictive compilation. HotSpot's C2 can perform speculative optimisations (inline virtual calls, eliminate type checks) based on observed runtime behaviour - optimisations impossible without execution data. GraalVM Native Image's AOT compiler has only static type information. It can apply safe optimisations (inlining of known-final methods, devirtualisation of sealed hierarchies) but cannot speculate. Profile-Guided Optimisation bridges this gap for workloads with representative training data - but only for homogeneous traffic patterns. Services with high traffic diversity see less PGO benefit. This explains why Native Image is most effective for short-lived, task-specific executables rather than general-purpose, variable-traffic APIs.

**Expert Thinking Cues:**
- `native-image --initialize-at-build-time` vs `--initialize-at-run-time` controls class initialisation - critical for frameworks using static initialisation
- GraalVM JIT mode: can replace HotSpot with a one-line Docker image change (`FROM ghcr.io/graalvm/jdk:21`) - test first
- Native Image `--no-fallback` vs `--fallback`: without `--no-fallback`, build failures silently produce a JVM-dependent fallback binary

---

### ⚙️ How It Works (Mechanism)

**Selection Decision Tree:**
```
  Is startup time critical? (<100ms)
       |
  YES                  NO (long-running service)
   |                         |
  Use Native Image      Throughput SLA?
   |                    (>100K req/s)
  Check compatibility:       |
  - Reflection?         YES           NO
  - JNI/FFI?             |             |
  - Dynamic proxies?   GraalVM JIT  HotSpot G1/ZGC
   |                   (drop-in)    (default)
  All pass: proceed
  Any fail: add config
  or use HotSpot
```

**Native Image Compatibility Check Process:**
```bash
# 1. Run with native-image-agent to detect
#    dynamic features at runtime
java -agentlib:native-image-agent=\
  config-output-dir=native-config \
  -jar app.jar

# 2. Run representative load test while agent runs
# 3. Config files generated in native-config/

# 4. Build Native Image with generated config
native-image --no-fallback \
  -H:ReflectionConfigurationFiles=\
  native-config/reflect-config.json \
  -jar app.jar
```

**Performance Profile by Mode:**
```
  Startup     Peak Throughput    Memory
  -------     ---------------    ------
  HotSpot:
  200ms       100% (baseline)    300MB+

  GraalVM JIT:
  200ms       110-130%           320MB+

  Native Image:
  <10ms       70-85%             50-150MB

  Native Image + PGO:
  <10ms       85-95%             50-150MB
```

---

### 🔄 The Complete Picture - End-to-End Flow

**NORMAL FLOW (Native Image path):**
```
  Assess workload               <- YOU ARE HERE
  (startup/throughput/memory)
       |
  Run compatibility check
  (native-image-agent)
       |
  Configure reflection/JNI
  (or use compatible framework)
       |
  Build: native-image -jar app.jar
  (2-5 minute build)
       |
  Test binary compatibility
       |
  Deploy (no JVM needed)
       |
  Monitor (different metrics:
  no GC, no JIT events)
```

**FAILURE PATH:**
- Build fails: `No instances of ... are allowed in the image heap` - static state with complex initialisation
- Runtime crash: `Missing registration for reflection access` - undiscovered reflection usage
- Performance regression: Native Image throughput below HotSpot after native migration of throughput-bound service

**WHAT CHANGES AT SCALE:**
At fleet scale, Native Image adoption requires a new CI pipeline stage (native image build is slow: 2-5 minutes vs 30 seconds for JVM). Fleet monitoring must handle two modes: JVM services (GC events, JIT events, heap metrics) and native services (OS-level memory, no GC pauses, no JIT warm-up curves).

---

### 💻 Code Example

**BAD - choosing Native Image for throughput-bound API without evaluation:**
```bash
# Migrated long-running trading engine to Native Image
# because "startup is faster"
native-image -jar trading-engine.jar
# Result: 25% throughput reduction at steady state
# JIT's speculative inlining eliminated -> virtual dispatch overhead
# Trading SLA breached under peak load
```

**GOOD - systematic evaluation before migration:**
```bash
# Step 1: Profile HotSpot baseline
java -jar service.jar &
# Run load test: 10K req/s for 5 minutes
# Record: p99 latency, throughput, memory

# Step 2: Profile GraalVM JIT (drop-in)
# Change Docker base: FROM ghcr.io/graalvm/jdk:21
java -jar service.jar &
# Same load test
# Record deltas: usually 10-20% throughput improvement

# Step 3: Test Native Image IF startup matters
java -agentlib:native-image-agent=\
  config-output-dir=native-config -jar service.jar
# Run representative traffic for 30 minutes
native-image --no-fallback \
  -H:ReflectionConfigurationFiles=\
  native-config/reflect-config.json \
  -jar service.jar
# Load test native binary
# Record startup time, throughput, memory

# Step 4: Compare all three; choose based on SLA
```

**How to test / verify correctness:**
```bash
# Compare startup times
time java -jar app.jar --spring.main.web-application-type=none
time ./app --spring.main.web-application-type=none

# Compare memory at idle
ps -o pid,rss,vsz -p $(pgrep java)
ps -o pid,rss,vsz -p $(pgrep app)

# Compare throughput (use wrk or hey)
hey -n 100000 -c 100 http://localhost:8080/api/test
```

---

### ⚖️ Comparison Table

| Criterion | HotSpot JIT | GraalVM JIT | Native Image |
|---|---|---|---|
| Startup time | 200-500ms | 200-500ms | <10ms |
| Peak throughput | 100% | 110-130% | 70-95% |
| Memory (idle) | 200-500MB | 250-550MB | 50-150MB |
| Warm-up required | Yes (30-120s) | Yes (30-120s) | No |
| Dynamic reflection | Full support | Full support | Config required |
| Build time | 30-60s | 30-60s | 2-5 minutes |
| Best for | Long-running API | Long-running high-throughput | Serverless/CLI |

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| "Native Image is always faster" | Native Image starts faster. At steady state, HotSpot C2 is faster for throughput. Native Image lacks adaptive JIT. |
| "Native Image works with any Spring Boot app" | Spring Boot 3.0+ supports Native Image via AOT processing. Older Spring versions, and apps with extensive runtime proxies, require significant work. |
| "GraalVM JIT is risky / experimental" | GraalVM JIT mode is TCK-compliant and production-ready. It is a drop-in HotSpot replacement. GraalVM EE is used in production at Oracle, AWS, and others. |
| "Native Image has no GC" | Native Image includes a GC (Serial or Epsilon). It just has no JIT. Memory is still managed. |
| "AOT and Native Image are the same thing" | AOT is ahead-of-time compilation, a technique. Native Image is GraalVM's tool that uses AOT to produce a self-contained binary. They are not synonymous. |

---

### 🚨 Failure Modes & Diagnosis

**Failure Mode 1: Native Image runtime crash on missing reflection config**
**Symptom:** Application crashes with `java.lang.reflect.InaccessibleObjectException` or `Missing registration for reflection access to class`
**Root Cause:** Code uses reflection at runtime for a class not registered in the Native Image reflection config
**Diagnostic:**
```bash
# Run with tracing agent first
java -agentlib:native-image-agent=\
  config-output-dir=native-config \
  -jar app.jar
# Run ALL code paths during this trace session
# Then rebuild native image with generated config
```
**Fix:** Add missing class/method to `reflect-config.json`; or annotate with `@RegisterForReflection` (Quarkus) or add to `reflect-config.json` (Spring AOT)
**Prevention:** Trace agent is mandatory; do not skip; run against full integration test suite

**Failure Mode 2: Native Image performance regression vs HotSpot**
**Symptom:** Native Image service handles 30% fewer requests/second than equivalent HotSpot service
**Root Cause:** Native Image lacks C2 JIT speculative inlining; virtual dispatch overhead dominates hot paths
**Diagnostic:**
```bash
# Profile native binary (system perf)
perf record -g ./app &
# Run load test
perf report
# Look for: vtable_dispatch, virtual call overhead in hot paths
```
**Fix:** Enable PGO (Profile-Guided Optimisation):
```bash
# Stage 1: instrument binary
native-image --pgo-instrument -jar app.jar
./app  # run with representative traffic
# Stage 2: compile with profile data
native-image --pgo=default.iprof -jar app.jar
```
**Prevention:** Benchmark both modes before migration; set throughput acceptance criteria

**Failure Mode 3: Static initialiser incompatible with Native Image**
**Symptom:** Build fails: `An error occurred during class initialization ... must not be initialised during image building`
**Root Cause:** Class static initialiser runs at build time and accesses resources unavailable at build time (environment variables, network, files)
**Diagnostic:**
```bash
native-image ... 2>&1 | grep "initialize"
# Shows which class and why it failed at build time
```
**Fix:** Add `--initialize-at-run-time=com.example.ProblematicClass` to defer initialisation
**Prevention:** Use `--initialize-at-build-time` only for pure data classes; defer all I/O-dependent static initialisers

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**
- [[JVM-052 - GraalVM]] - GraalVM architecture
- [[JVM-053 - Native Image]] - Native Image mechanics
- [[JVM-060 - JVM Architecture Decisions at Scale]] - Fleet-level context

**Builds On This (learn these next):**
- [[JVM-069 - Performance Intuition via JVM Internals]] - Predicting performance differences

**Alternatives / Comparisons:**
- [[JVM-045 - JIT Compiler]] - HotSpot JIT compilation details
- [[JVM-051 - AOT Compilation]] - AOT compilation concepts

---

### 📌 Quick Reference Card

```
+--------------------------------------------------+
| WHAT IT IS    | Structured framework for         |
|               | HotSpot vs GraalVM selection      |
+--------------------------------------------------+
| PROBLEM       | Random runtime selection; failed |
|               | Native Image migrations           |
+--------------------------------------------------+
| KEY INSIGHT   | Long-running: HotSpot JIT;       |
|               | Short-lived: Native Image         |
+--------------------------------------------------+
| USE WHEN      | Starting a new service; evaluating|
|               | Native Image adoption             |
+--------------------------------------------------+
| AVOID WHEN    | One-size-fits-all decisions;      |
|               | migrating without benchmarks      |
+--------------------------------------------------+
| TRADE-OFF     | Startup+memory vs               |
|               | peak throughput+compatibility     |
+--------------------------------------------------+
| ONE-LINER     | Startup critical? Native Image.  |
|               | Long-running? HotSpot. Drop-in   |
|               | upgrade? GraalVM JIT.            |
+--------------------------------------------------+
| NEXT EXPLORE  | JVM-053 Native Image,            |
|               | JVM-069 performance intuition     |
+--------------------------------------------------+
```

**If you remember only 3 things:**
1. Startup critical (FaaS/CLI): Native Image. Long-running (API/worker): HotSpot JIT
2. GraalVM JIT mode is a drop-in HotSpot replacement - test first, worth 10-30% throughput
3. Always run `native-image-agent` before attempting Native Image build

**Interview one-liner:** "HotSpot JIT for long-running services needing adaptive optimisation; GraalVM Native Image for startup-critical serverless or CLI tools; GraalVM JIT as a throughput-improvement drop-in for HotSpot."

---

### 💎 Transferable Wisdom

**Reusable Engineering Principle:** Choose your execution model based on invocation frequency and lifetime, not on benchmarks for a different workload pattern. Throughput optimisations and startup optimisations are opposing forces; the optimal choice depends on the ratio of execution time to initialisation time.

**Where else this pattern appears:**
- Lambda vs long-running container: same trade-off; FaaS optimises for startup, containers optimise for sustained throughput
- Browser JS: V8 JIT for long-running SPAs; AOT compiled Wasm for startup-critical edge functions
- Python: CPython for general use; Cython/Nuitka AOT for hot paths or startup-critical scripts

---

### 💡 The Surprising Truth

GraalVM Native Image is not just faster to start - it can sometimes produce smaller CPU instruction traces for specific workloads because the AOT compiler knows the complete call graph at build time and can eliminate dead code more aggressively than JIT can. JIT compilation happens in 10-100ms windows and cannot afford full program analysis. GraalVM's build-time analysis has unlimited time to analyse the entire program, producing smaller, more cache-friendly native code. This is why some compute-intensive, reflection-free workloads (like cryptography or graph algorithms) actually run faster under Native Image despite lacking adaptive JIT - the code-size reduction improves CPU instruction cache utilisation enough to offset the lack of runtime type-feedback optimisations.

---

### 🧠 Think About This Before We Continue

**Q1 (Design Trade-off):** A service starts 1,000 times per day (every 90 seconds due to autoscaling). Each instance runs for 90 seconds then shuts down. With HotSpot, JIT warm-up takes 30 seconds, meaning 33% of each instance's lifetime is spent warming up. What is the mathematical break-even point (in seconds of instance lifetime) where Native Image's constant startup advantage disappears for a service with this traffic pattern?
*Hint:* Model the total CPU-seconds of useful work per day for each mode, accounting for warm-up overhead and steady-state throughput difference (Native Image = 85% of HotSpot steady-state).

**Q2 (System Interaction):** You deploy a Spring Boot 3 service as GraalVM Native Image. At 3am, a new library is loaded via a plugin system that uses `Class.forName()` with a class name determined at runtime. What happens, and what architectural change removes the coupling between plugin loading and the closed-world assumption?
*Hint:* Consider the impact of the closed-world assumption on dynamic class loading, and what architectural patterns (proxy approach, gRPC out-of-process plugins) avoid this constraint entirely.

**Q3 (Scale):** You have 200 services to evaluate for Native Image migration. You need to prioritise. What single metric, measurable from existing production data without any code changes, best predicts which services will benefit most from Native Image adoption?
*Hint:* Think about the ratio of startup time to average instance lifetime in your Kubernetes deployment logs. Services that restart frequently relative to their runtime are the highest-value candidates.
