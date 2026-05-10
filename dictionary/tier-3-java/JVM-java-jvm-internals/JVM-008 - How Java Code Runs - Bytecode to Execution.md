---
id: JVM-009
title: "How Java Code Runs - Bytecode to Execution"
category: Java & JVM Internals
tier: tier-3-java
folder: JVM-java-jvm-internals
difficulty: ★★☆
depends_on: JVM-001, JVM-003
used_by: JVM-009, JVM-045, JVM-046
related: JVM-010, JVM-025, JVM-029
tags:
  - jvm
  - java
  - internals
  - deep-dive
status: complete
version: 3
layout: default
parent: "Java & JVM Internals"
grand_parent: "Technical Dictionary"
nav_order: 8
permalink: /jvm/how-java-code-runs-bytecode-to-execution/
---

# JVM-008 - How Java Code Runs - Bytecode to Execution

**⚡ TL;DR** - Java source is compiled to bytecode by `javac`, then the JVM loads, verifies, interprets (and JIT-compiles) it to native instructions at runtime. The pipeline has six distinct phases.

| Field | Value |
|---|---|
| **Depends on** | [[JVM-001 - What Is the JVM - A Mental Model]], [[JVM-003 - JVM vs JRE vs JDK]] |
| **Used by** | [[JVM-009 - Bytecode]], [[JVM-045 - JIT Compiler]], [[JVM-046 - C1 C2 Compiler]] |
| **Related** | [[JVM-010 - Class Loader]], [[JVM-025 - Stack Frame]], [[JVM-029 - Escape Analysis]] |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
Without understanding the execution pipeline, developers treat the JVM as a black box. They cannot explain why an application is slow at startup, why it speeds up after 60 seconds of traffic, why some code is faster when called many times than when called once, or why adding more threads sometimes reduces throughput. Performance problems become guesswork.

**THE BREAKING POINT:**
When a production JVM application serves 10,000 requests per second and suddenly slows to 1,000 for 30 seconds, the team that understands bytecode-to-execution can read GC logs, check JIT compilation events, and identify a deoptimisation cascade. The team that does not understand the pipeline files a ticket to "restart the server."

**THE INVENTION MOMENT:**
The JVM execution pipeline was designed as a series of safety checkpoints before any code executes. The bytecode verifier prevents malicious or malformed code from reaching the execution engine. The interpretation phase collects profiling data before the JIT spends resources compiling. Each phase serves a distinct purpose in the contract between safety and performance.

**EVOLUTION:**
- JDK 1.0 (1996): pure interpretation - safe but slow
- JDK 1.3 (2000): HotSpot JIT - detects hot methods, compiles to native
- JDK 5 (2004): tiered compilation research begins
- JDK 7 (2011): tiered compilation default (C1 then C2)
- JDK 9 (2017): GraalVM compiler available as experimental JIT backend
- JDK 21 (2023): virtual threads change thread-to-OS mapping in the execution stack

---

### 📘 Textbook Definition

**Java code execution** proceeds through six phases: (1) **Compilation**: `javac` parses Java source, performs type checking, and emits platform-neutral `.class` bytecode. (2) **Class Loading**: the JVM's ClassLoader subsystem locates, reads, and parses `.class` files into in-memory `Class` objects. (3) **Bytecode Verification**: the verifier performs data-flow analysis to guarantee type safety without executing the code. (4) **Interpretation**: the execution engine interprets bytecode one instruction at a time, collecting method invocation counts and branch frequencies as profiling data. (5) **JIT Compilation**: methods crossing invocation-count thresholds are compiled by C1 (quick) then C2 (optimising) compilers to native machine code stored in the Code Cache. (6) **Native Execution**: subsequent invocations of compiled methods execute native code at full CPU speed without JVM overhead.

---

### ⏱️ Understand It in 30 Seconds

**One line:** `javac` compiles Java to bytecode; JVM interprets it first, then JIT-compiles hot paths to native speed.

> Like a chef learning a new recipe: first they read each step slowly (interpretation), then after cooking it twenty times they have it memorised and cook at full speed without looking at the recipe (JIT compilation).

**One insight:** The JVM deliberately runs code slowly at first to collect accurate profiling data. Decisions about what to optimise are based on observed runtime behaviour, not static analysis. This is why JVM code gets faster over time during a running instance - not due to caching, but due to progressive compilation of increasingly hot paths.

---

### 🔩 First Principles Explanation

**CORE INVARIANTS:**
1. Safety must be checked before execution, not relied upon from the compiler
2. Optimisation decisions require runtime data (branch frequencies, type profiles)
3. Compiling everything to native at startup is too expensive; compile progressively
4. Native code must be invalidated (deoptimised) when assumptions it was compiled under no longer hold

**DERIVED DESIGN:**
From invariant 1: bytecode verification runs on every class load, even code compiled by a trusted `javac`. A JVM cannot trust that a `.class` file was produced by a legitimate compiler.
From invariant 2: interpretation precedes JIT to collect profiling data that drives optimisation choices (method inlining targets, branch prediction hints).
From invariant 3: tiered compilation (interpret → C1 → C2) staggers the work over time.
From invariant 4: deoptimisation is a core JVM mechanism, not an edge case.

**THE TRADE-OFFS:**
**Gain:** Progressive compilation means zero cold-start compilation cost; profiling-driven JIT produces better code than AOT static analysis for long-running servers
**Cost:** Warm-up latency (50-120 seconds to full throughput); Code Cache finite (exhaustion causes performance cliff); deoptimisation events cause brief throughput drops

**ESSENTIAL vs ACCIDENTAL COMPLEXITY:**
**Essential:** Any safe execution of untrusted bytecode requires verification. Any adaptive optimisation requires profiling. These are irreducible.
**Accidental:** Warm-up latency is accidental - GraalVM Native Image and AppCDS (Application Class Data Sharing) address it.

---

### 🧪 Thought Experiment

**SETUP:** You are writing a method `sum(int[] data)` that is called 5 million times per second in a financial calculation service. The JVM has not JIT-compiled it yet.

**WHAT HAPPENS WITHOUT JIT (pure interpretation):**
The JVM interprets each bytecode instruction every time `sum` is called. For 5 million calls/second, the interpreter overhead (decode opcode, switch dispatch, update program counter) dominates execution time. A 10ns method becomes 100ns under interpretation. Your service handles 500K requests/second instead of 5M.

**WHAT HAPPENS WITH JIT (after warm-up):**
After ~10,000 invocations, C1 compiles `sum`. After ~10,000 more, C2 compiles it with full optimisations. C2 inlines the array bounds check elimination, removes redundant null checks, and emits SSE/AVX vector instructions for the sum loop. The compiled `sum` runs at 2-5ns, native speed, with no JVM overhead per call.

**THE INSIGHT:**
The JVM's execution pipeline is a pipeline of progressive commitment: the more certain it is that a path is hot, the more it invests in optimising it. This is resource-rational - spending 200ms compiling a method that is called once would be wasteful. The pipeline is designed around the statistical reality that most code is cold; a small fraction of methods account for most CPU time (the hot path).

---

### 🧠 Mental Model / Analogy

> Think of the JVM execution pipeline as a highway on-ramp with acceleration lanes. Cars (code) enter slowly from a stopped position (interpretation), build speed in the acceleration lane (C1 compilation), then merge at full highway speed (C2 optimised native code). Drivers who only travel the road once never need to accelerate fully. Frequent commuters (hot methods) benefit from the full highway speed every day.

Element mapping:
- Car entering highway = method being called for the first time
- Acceleration lane speed = C1 compilation performance tier
- Full highway speed = C2 optimised native execution
- Commuter frequency = method invocation count
- Highway on-ramp toll = JIT compilation cost
- Off-ramp (return to city streets) = deoptimisation

Where this analogy breaks down: in a real highway, acceleration is one-time. In the JVM, a method can be deoptimised and re-compiled multiple times as the type profile changes - it re-enters the on-ramp repeatedly during the lifetime of the JVM.

---

### 📶 Gradual Depth - Four Levels

**Level 1 - What it is (anyone can understand):**
When you write Java code, a compiler first converts it to a special format called bytecode. When you run your program, the JVM reads that bytecode and runs it. Initially it runs slowly while it learns which parts of the code are used most. Those busy parts get converted to fast native instructions. This is why Java applications often get faster after running for a minute.

**Level 2 - How to use it (junior developer):**
You interact with this pipeline via command-line flags and tooling. `javac` compiles source. `java -jar app.jar` starts the JVM. JVM flags `-XX:+PrintCompilation` shows which methods are being JIT-compiled. `-XX:CompileThreshold=10000` sets the invocation count before compilation. GC logs (`-Xlog:gc*`) show collection events. JFR (Java Flight Recorder) captures compilation, GC, and allocation events in production without significant overhead.

**Level 3 - How it works (mid-level engineer):**
The HotSpot execution engine tracks invocation counts per method in a per-method counter. When the counter exceeds `CompileThreshold` (default 10,000 for C2), the method is submitted to the compiler queue. C1 compiles quickly with limited optimisations and inserts profiling probes (type recording, branch frequency). When C1-compiled code exceeds its own threshold, C2 recompiles with aggressive optimisations using the C1-collected profile data: inlining, loop unrolling, escape analysis, null-check elimination, and native vector instructions. The compiled native code is stored in the Code Cache (default 240MB). If the Code Cache fills, JIT compilation stops - a severe performance cliff.

**Level 4 - Why it was designed this way (senior/staff):**
The tiered compilation design (C1 → C2) solves a fundamental tension: fast startup vs. optimal throughput. C1 sacrifices code quality for compilation speed - it compiles quickly so the application stops interpreting soon. C2 sacrifices compilation speed for code quality - it optimises aggressively but takes 10-100ms per method. By separating the roles, the JVM achieves both: fast startup (C1 kicks in within milliseconds) and optimal steady-state performance (C2 produces near-optimal native code after profiling). The type-feedback mechanism (C1 records observed types, C2 speculates on them) enables optimistic optimisations impossible in AOT compilation, where types are not yet known.

**Expert Thinking Cues:**
- `-XX:+PrintCompilation` output showing `made not entrant` = deoptimisation; `made zombie` = code evicted from Code Cache
- Code Cache overflow: `[CodeCache is full. Compiler has been disabled]` in logs - increase with `-XX:ReservedCodeCacheSize=512m`
- `jcmd <pid> Compiler.queue` shows pending JIT compilation work

---

### ⚙️ How It Works (Mechanism)

**Phase 1: javac Compilation**
`javac` parses Java source, resolves names and types, performs type checking, folds constants, and emits `.class` files. It does NOT optimise - that is the JIT's job. The bytecode is intentionally simple and un-optimised to make verification easier.

**Phase 2: Class Loading**
ClassLoader locates the `.class` file, reads its binary format, creates a `Class` object in heap, and stores method bytecode in the Method Area (Metaspace). The class loading subsystem follows parent-delegation: Bootstrap → Extension → Application loader.

**Phase 3: Bytecode Verification**
The verifier performs four passes: (1) format check (valid magic, version), (2) semantic check (valid constant pool references), (3) dataflow analysis (type safety of every instruction sequence), (4) symbolic reference check (referenced classes actually exist). After verification, the bytecode is trusted.

**Phase 4: Interpretation**
The interpreter executes bytecode instructions using a program counter, operand stack, and local variable array (a stack frame). It increments an invocation counter on every method call.

**Phase 5: JIT Compilation**
When `invocation_count >= CompileThreshold`:
- Task queued to C1 or C2 compiler thread
- C1: quick compilation + profiling instrumentation
- C2: aggressive optimisation using C1's type/branch profile
- Output: native code stored in Code Cache

**Phase 6: Deoptimisation**
If a speculative optimisation becomes invalid (e.g., a new subclass appears), the JVM invalidates the compiled native code and reverts to interpretation. The method re-accumulates invocations and eventually re-compiles.

---

### 🔄 The Complete Picture - End-to-End Flow

**NORMAL FLOW:**
```
  Hello.java
      |
  [javac] -> Hello.class
      |
  java -jar app.jar   <- YOU ARE HERE
      |
  [ClassLoader] reads Hello.class
      |
  [Bytecode Verifier] (type safety)
      |
  [Interpreter] <-- slow; counts calls
      | (at 10,000 calls)
  [C1 Compiler] -> native (fast compile)
      | (at 10,000 more calls + profiling)
  [C2 Compiler] -> native (full optimize)
      |
  [CPU executes native code]
```

**FAILURE PATH:**
- `VerifyError`: verification failed - corrupted or hand-crafted bytecode
- `ClassNotFoundException`: class loader cannot find `.class` on classpath
- Code Cache full: JIT disabled, performance degrades to C1 or interpretation
- Deoptimisation storm: type profile invalidated repeatedly - hot code never reaches C2

**WHAT CHANGES AT SCALE:**
At scale, warm-up becomes a deployment operations concern:
- Rolling restart: new JVM instances serve traffic during warm-up at 30-50% throughput
- Solution: AppCDS (saves loaded class data), JFR recordings of compiled methods, or blue-green deployments where new pods warm up before receiving traffic

**CONCURRENCY & DISTRIBUTED IMPLICATIONS:**
JIT compilation runs on dedicated compiler threads concurrently with application threads. A sudden burst of new hot methods (e.g., after a deployment) creates compilation queue pressure. Monitor with `jcmd <pid> Compiler.queue` - a large queue means application threads are running un-optimised code longer than expected.

---

### 💻 Code Example

**BAD - ignoring JIT warm-up in benchmarking:**
```java
// Incorrect benchmark: measures interpreted execution
public static void main(String[] args) {
    long start = System.nanoTime();
    long result = compute(1_000_000);
    long end = System.nanoTime();
    // WRONG: first call is interpreted - 10-100x slower
    System.out.println("Time: " + (end - start) + "ns");
}
```

**GOOD - using JMH for JIT-aware benchmarking:**
```java
@BenchmarkMode(Mode.AverageTime)
@OutputTimeUnit(TimeUnit.NANOSECONDS)
@Warmup(iterations = 5, time = 1)  // let JIT compile
@Measurement(iterations = 5, time = 1)
@Fork(2)
public class ComputeBenchmark {
    @Benchmark
    public long benchmarkCompute() {
        return compute(1_000_000);
    }
}
// JMH runs warmup iterations to drive JIT
// then measures in steady-state (C2 compiled)
```

**Observing the pipeline in action:**
```bash
# See which methods are being JIT compiled
java -XX:+PrintCompilation -jar app.jar 2>&1 | head -50

# See bytecode for a method
javap -c -p ClassName.class

# Observe interpreter vs compiled execution
java -XX:+PrintCompilation \
     -XX:CompileThreshold=100 \  # lower threshold
     -jar app.jar
```

**How to test / verify correctness:**
Use JFR profiling to observe method compilation events:
```java
// Programmatic JFR recording
Configuration config = Configuration.getConfiguration("default");
try (Recording r = new Recording(config)) {
    r.start();
    // run workload
    r.stop();
    r.dump(Path.of("profile.jfr"));
}
// Open profile.jfr in JDK Mission Control
// -> Compiler -> Hot Methods tab
```

---

### ⚖️ Comparison Table

| Phase | Tool/Flag | What to Look For |
|---|---|---|
| Compilation | `javap -c` | Bytecode instruction count, constant pool |
| Class loading | `-verbose:class` | Which classes load, from where |
| Verification | `VerifyError` in logs | Malformed class files |
| JIT compilation | `-XX:+PrintCompilation` | Method compilation tier, deoptimisations |
| Code Cache | `jcmd <pid> CodeCache.heap_info` | Used vs free cache space |
| Runtime profile | JFR, async-profiler | Hot methods, allocation sites |

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| "Java is interpreted" | Java is JIT-compiled. After warm-up, hot paths run as native code with performance comparable to C++. |
| "javac optimises my code" | `javac` intentionally does minimal optimisation. JIT (C2) performs all significant optimisations at runtime. |
| "Calling a method 1,000 times is enough warm-up" | Default `CompileThreshold` is 10,000. Some C2 optimisations require even more profiling data before they trigger. |
| "Deoptimisation is rare" | In applications with polymorphism, deoptimisation happens regularly as type profiles evolve. It is a normal JVM event, not an error. |
| "More Code Cache is always better" | Code Cache is scanned during GC safepoints. Extremely large caches (>1GB) increase safepoint pauses. |

---

### 🚨 Failure Modes & Diagnosis

**Failure Mode 1: Code Cache exhaustion**
**Symptom:** Throughput drops by 50-80% after running well for hours. GC logs show no change.
**Root Cause:** Code Cache is full; JIT compilation disabled; methods fall back to interpreted execution
**Diagnostic:**
```bash
jcmd <pid> CodeCache.heap_info
# Look for: max_used reaching reserved size
# Or in logs: CodeCache is full. Compiler has been disabled.
```
**Fix:**
BAD: Restarting the JVM repeatedly (problem returns)
GOOD: `-XX:ReservedCodeCacheSize=512m` (default 240MB; increase to 512MB or 1GB)
**Prevention:** Monitor Code Cache usage as a production metric; alert at 80% full

**Failure Mode 2: Deoptimisation storm after class loading**
**Symptom:** Throughput drops for 5-30 seconds after a hot deployment or plugin load event
**Root Cause:** New subclass invalidates inlined monomorphic call sites compiled by C2 - mass deoptimisation
**Diagnostic:**
```bash
java -XX:+PrintCompilation 2>&1 | grep "made not entrant"
# High volume of "made not entrant" = deoptimisation events
jcmd <pid> Compiler.queue
# Large queue = recompilation backlog
```
**Fix:** Use `-XX:+UnlockDiagnosticVMOptions -XX:+LogCompilation` to find the specific methods; restructure to avoid monomorphic inlining assumptions at high-value call sites
**Prevention:** In plugin architectures, load plugins before serving traffic; avoid adding new subclasses of frequently-called interfaces after JIT convergence

**Failure Mode 3: Warm-up period causing SLA breach during deployment**
**Symptom:** First 60-90 seconds after pod restart, p99 latency spikes 3-5x above SLA
**Root Cause:** Application serves production traffic during JIT warm-up (interpreted mode)
**Diagnostic:**
```bash
# Observe compilation rate over time
java -XX:+PrintCompilation -jar app.jar 2>&1 | \
  awk '{print NR, $1}' | head -200
# Compilation events taper off = warm-up complete
```
**Fix:**
BAD: Sending traffic immediately after pod readiness probe passes
GOOD: Use AppCDS to pre-populate class data; or configure readiness probe with extended warm-up script before registering in load balancer
**Prevention:** Load test in staging to measure warm-up duration; encode that duration into Kubernetes `initialDelaySeconds`

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**
- [[JVM-001 - What Is the JVM - A Mental Model]] - What the JVM is
- [[JVM-003 - JVM vs JRE vs JDK]] - Component model

**Builds On This (learn these next):**
- [[JVM-009 - Bytecode]] - The intermediate representation in detail
- [[JVM-010 - Class Loader]] - Phase 2 (class loading) in detail
- [[JVM-045 - JIT Compiler]] - Phase 5 (JIT compilation) in detail

**Alternatives / Comparisons:**
- [[JVM-051 - AOT Compilation]] - Compile to native at build time, skip warm-up
- [[JVM-029 - Escape Analysis]] - Key JIT optimisation in Phase 5

---

### 📌 Quick Reference Card

```
+--------------------------------------------------+
| WHAT IT IS    | 6-phase pipeline: compile ->     |
|               | load -> verify -> interpret ->   |
|               | JIT -> native execution          |
+--------------------------------------------------+
| PROBLEM       | Safe execution + optimal perf    |
|               | at the same time                 |
+--------------------------------------------------+
| KEY INSIGHT   | JVM runs code slow first to      |
|               | collect profiling; then compiles  |
+--------------------------------------------------+
| USE WHEN      | Understanding startup latency,   |
|               | benchmarking, perf debugging      |
+--------------------------------------------------+
| AVOID WHEN    | (Must understand for any JVM     |
|               | performance work)                |
+--------------------------------------------------+
| TRADE-OFF     | Warm-up latency vs optimal       |
|               | steady-state throughput           |
+--------------------------------------------------+
| ONE-LINER     | javac -> .class -> load ->       |
|               | verify -> C1 -> C2 -> native     |
+--------------------------------------------------+
| NEXT EXPLORE  | JVM-045 JIT Compiler,            |
|               | JVM-009 Bytecode internals        |
+--------------------------------------------------+
```

**If you remember only 3 things:**
1. Six phases: compile, load, verify, interpret, JIT, native execute
2. JIT runs code slow first to profile, then compiles hot paths
3. Code Cache exhaustion is a silent production killer - monitor it

**Interview one-liner:** "Java code compiles to bytecode, which the JVM loads and verifies before interpreting. After ~10,000 calls, hot methods are JIT-compiled to native code by C1 then C2 for full throughput."

---

### 💎 Transferable Wisdom

**Reusable Engineering Principle:** Defer expensive decisions until you have data. Profiling before optimising - at the cost of temporary inefficiency - produces better outcomes than premature AOT optimisation based on static analysis. This applies to any adaptive system.

**Where else this pattern appears:**
- Database query optimisers: run queries, collect statistics, then generate optimised execution plans
- CDN cache warming: serve slowly from origin first, then cache hot content at edge
- ML model deployment: serve baseline model first, collect real-world data, retrain with production distribution

---

### 💡 The Surprising Truth

The JVM's JIT compiler can produce code faster than hand-optimised C++ in certain workloads. Because the JIT has runtime type information that a C++ compiler lacks, it can make optimistic assumptions - for example, inlining a virtual method call that C++ must dispatch through a vtable. When the assumption holds (it usually does), the JIT-compiled code executes a direct call; C++ executes an indirect vtable lookup. For hot paths with deep call hierarchies and many virtual calls, this advantage compounds. Studies on numeric benchmarks show Java within 10-20% of C++; on object-heavy workloads, Java sometimes outperforms equivalent C++ code. This directly contradicts the common belief that a "managed runtime" is inherently slower.

---

### 🧠 Think About This Before We Continue

**Q1 (Root Cause):** You benchmark a method and find it takes 200ns on the first call, 20ns after 100 calls, and 2ns after 50,000 calls. What three distinct JVM execution states correspond to these three measurements, and which JVM counter triggers the transitions?
*Hint:* Look at the four execution phases (interpret, C1, C2) and the `CompileThreshold` counter mechanism described in this entry.

**Q2 (Scale):** Your application loads 50,000 classes and generates 200,000 JIT compilation events during the first 2 minutes of startup. Under high load, this warm-up slows first requests. What are the two JVM features that can move this work to the build/startup phase rather than the serving phase?
*Hint:* Investigate AppCDS (Application Class Data Sharing) and [[JVM-051 - AOT Compilation]] (GraalVM Native Image profile-guided optimisation).

**Q3 (Design Trade-off):** GraalVM Native Image uses AOT (Ahead-of-Time) compilation: the entire program is compiled to native at build time with no JIT. It has faster startup but permanently foregoes the profiling-driven optimisations described in this entry. For what category of server application is this trade-off clearly wrong, and why?
*Hint:* Consider a long-running Java application that receives highly variable traffic patterns (e.g., different types of requests in bursts), and think about what the JIT adapts to that AOT cannot.
