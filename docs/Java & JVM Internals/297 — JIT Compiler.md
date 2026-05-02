---
layout: default
title: "JIT Compiler"
parent: "Java & JVM Internals"
nav_order: 297
permalink: /java/jit-compiler/
number: "0297"
category: Java & JVM Internals
difficulty: ★★★
depends_on:
  - JVM
  - Bytecode
  - Stack Frame
  - Heap Memory
  - GC Roots
used_by:
  - C1 / C2 Compiler
  - Tiered Compilation
  - Method Inlining
  - Deoptimization
  - OSR (On-Stack Replacement)
related:
  - AOT (Ahead-of-Time Compilation)
  - GraalVM
  - Tiered Compilation
tags:
  - jvm
  - jit
  - performance
  - java-internals
  - deep-dive
---

# 0297 — JIT Compiler

⚡ TL;DR — The JIT compiler watches your bytecode run, identifies hot methods, and compiles them to native machine code on the fly — all while the program keeps running.

| #0297 | Category: Java & JVM Internals | Difficulty: ★★★ |
|:---|:---|:---|
| **Depends on:** | JVM, Bytecode, Stack Frame, Heap Memory, GC Roots | |
| **Used by:** | C1/C2 Compiler, Tiered Compilation, Method Inlining, Deoptimization, OSR | |
| **Related:** | AOT Compilation, GraalVM, Tiered Compilation | |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
Early Java (pre-1.3) executed bytecode through a pure interpreter: the JVM read each bytecode instruction, looked up what it meant, and dispatched to a corresponding C routine. This was safe and portable, but devastatingly slow — 10–50x slower than equivalent C code. Java earned a reputation as a "slow language" not because the language design was flawed, but because execution was interpretation overhead multiplied over every instruction.

**THE BREAKING POINT:**
A financial trading engine written in Java in 1998 processes market data. A critical inner loop executes `checkPrice()` 50 million times per second. Each call: interpreter decodes the bytecode, dispatches to C handlers, crosses the interpreter boundary again on return. Total overhead: ~200ns per call where 5ns is the actual work. The loop is 40x slower than it needs to be. Traders complain. They switch to C++.

**THE INVENTION MOMENT:**
This is exactly why the **JIT (Just-In-Time) Compiler** was created — to bridge the speed gap between portable bytecode and native machine code by compiling hot code paths at runtime, using profiling data that a static compiler could never have.

---

### 📘 Textbook Definition

A **Just-In-Time (JIT) Compiler** is a component of the JVM that monitors bytecode execution at runtime, identifies frequently executed ("hot") methods and loops, and compiles them directly to native machine code specific to the host CPU. Unlike an Ahead-Of-Time (AOT) compiler that compiles before execution, the JIT has access to actual runtime profiling data (call frequencies, type feedback, branch outcomes) enabling aggressive optimizations — method inlining, dead code elimination, loop unrolling — that a static compiler could only approximate. The JIT operates concurrently with the application on background threads.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
A background system that turns slow interpreted bytecode into fast native code while your program runs.

**One analogy:**
> Imagine you're a translator at a live conference. Initially you translate every sentence as it comes. But you notice the speaker keeps repeating the same five phrases. So you prepare a written card with pre-translated versions of those phrases. From now on, instead of translating those phrases live, you just read from the card — ten times faster. The JIT does exactly this for your code's hot loops.

**One insight:**
The JIT's superpower is that it can make stronger assumptions than a static compiler ever could. It may see that a virtual method call always dispatches to one concrete type — so it inlines the entire call. If that assumption later breaks, it deoptimizes back to the interpreter. Static compilers must be conservative; the JIT can be *optimistic with a fallback*.

---

### 🔩 First Principles Explanation

**CORE INVARIANTS:**
1. Bytecode is architecture-neutral — it cannot run at native speed without translation.
2. Most programs spend 80%+ of their time in less than 20% of their code (the "hot path").
3. Runtime profiling data (types, branch directions, call counts) reveals opportunities that static analysis cannot.

**DERIVED DESIGN:**
Given invariant 2 and 3, the optimal strategy is:
- Start interpreting everything cheaply (no compilation cost for cold code).
- Count invocations of each method. When count exceeds a threshold (e.g., 10,000), trigger JIT compilation.
- The JIT compilation runs on a background thread — the interpreter keeps running so the application does not pause.
- When compilation is done, the call table is patched to point to native code. Next invocation hits native code.
- Use profile data gathered during interpretation to guide aggressive optimizations: inline monomorphic callsites, eliminate null checks where profiling shows null never occurred, speculate on branch outcomes.

```
┌───────────────────────────────────────────────┐
│         JIT Compilation Pipeline              │
│                                               │
│  [Bytecode] → [Interpreter]                   │
│                    │                          │
│                    │ (invocation count > N)    │
│                    ▼                          │
│  [Profile Data] → [IR Builder]                │
│                         │                     │
│                         ▼                     │
│  [Optimizer] → [Code Generator]               │
│                              │                │
│                              ▼                │
│  [Native Code] installed in code cache        │
│  [Call table patched] → next call → native    │
└───────────────────────────────────────────────┘
```

**THE TRADE-OFFS:**
**Gain:** Native-speed execution for hot code paths; adaptive to actual workload.
**Cost:** Warmup time (application runs slow initially); JIT background threads consume CPU; code cache has finite size; compiled code may be discarded (deoptimization or cache eviction).

---

### 🧪 Thought Experiment

**SETUP:**
A web server starts and immediately receives 10,000 requests/second. The request handler calls `parseHeaders()`, which calls `validateToken()`, which calls `decodeBase64()`. Each is 50 lines of bytecode.

**WHAT HAPPENS WITHOUT JIT:**
Every single call is interpreted. At 10,000 req/s, `parseHeaders()` is called 10,000 times/s. Each interpreted call: ~500ns overhead. Total interpretation overhead: 5ms/s just for this method. The server runs at 40% of potential throughput. After five minutes, still slow — no improvement.

**WHAT HAPPENS WITH JIT:**
First 1,000 calls: interpreted (profiling gathers type feedback, call counts accumulate). At invocation 10,000: JIT triggers compilation in background. Next 9,000 calls: still interpreted (JIT compiling concurrently). At invocation ~10,100: compiled native code is installed. All subsequent calls: ~50ns each including function call overhead. Throughput improves to 95% of theoretical peak. Server "warms up" in ~2 seconds, then runs fast forever.

**THE INSIGHT:**
JIT delivers native performance with zero programmer effort, but it requires warmup time. This makes JIT-based runtimes temporarily slower at startup and makes performance benchmarks notoriously unreliable if warmup is not accounted for.

---

### 🧠 Mental Model / Analogy

> Picture a chef who has never made a dish. The first time, they read the recipe step by step (interpreter). After making the dish 20 times, they have the steps memorized and can run through them without consulting the recipe — faster, and with personalized shortcuts based on their kitchen layout (JIT-compiled code). But if the restaurant gets a new oven (hardware change), they might need to unlearn some shortcuts.

- "Reading the recipe" → bytecode interpretation.
- "Memorized procedure" → JIT-compiled native code.
- "20 times" → invocation count threshold.
- "Personalized shortcuts" → profile-guided optimizations (inlining based on observed types).
- "New oven deoptimizes" → deoptimization when assumptions become invalid.

Where this analogy breaks down: Unlike the chef, JIT compilation happens fully in parallel — the "reading" never stops until the "memorized procedure" is ready, so there is no interruption to service.

---

### 📶 Gradual Depth — Four Levels

**Level 1 — What it is (anyone can understand):**
Java programs are written once and run on any computer. But to run at full speed, the JVM secretly translates the "universal" code into speed-optimized code for your specific computer while the program is running. That translator is the JIT compiler.

**Level 2 — How to use it (junior developer):**
The JIT is completely automatic — you do not call it. But you can influence it: keep methods short (makes inlining easier), avoid excessive polymorphism in hot paths (enables call-site optimization), use benchmarking frameworks like JMH that properly account for JIT warmup. Avoid writing microbenchmarks in plain `main()` — the JIT may optimize away the code you are measuring.

**Level 3 — How it works (mid-level engineer):**
The JVM uses a two-tier history counter per method: method invocation count + backedge count (loop iterations). When their sum exceeds the `CompileThreshold` (default 10,000 for C2), the method is submitted to the compiler queue. The JIT builds a high-level intermediate representation (IR), runs optimization passes (inlining, escape analysis, loop unrolling, null-check elimination), then emits native code into the Code Cache (`-XX:ReservedCodeCacheSize`, default 240MB in Java 11+). The compiled code is linked via a dispatch table that the interpreter consults on every method entry.

**Level 4 — Why it was designed this way (senior/staff):**
The key design tension is: compilation cost vs quality vs latency. Compiling everything at startup (like C) gives max performance but unacceptable startup time. Interpreting everything (like early Java) gives zero startup but poor peak. The answer is tiered compilation: a fast, lower-quality compiler (C1) for quick wins, and a slow, high-quality optimizer (C2) for truly hot methods. C2's globally optimizing SSA-based IR (the "Sea of Nodes" graph) enables optimizations (global value numbering, alias analysis, vectorization) impossible in a single-pass compiler. The tradeoff: C2 uses significant CPU and memory for compilation, which is why compilation runs on dedicated background threads and is subject to queue depth limits.

---

### ⚙️ How It Works (Mechanism)

**Profiling and Invocation Counting:**
Every method has two hardware counters maintained by the interpreter:
- `InvocationCounter`: incremented on each method entry.
- `BackedgeCounter`: incremented on each loop back-edge.

The JVM periodically checks both. When combined count exceeds the `CompileThreshold`, the method is enqueued.

**Compilation Pipeline:**
```
┌─────────────────────────────────────────────────┐
│            JIT Compilation Stages               │
│                                                 │
│  1. PARSE: Bytecode → Compiler IR (HIR)         │
│  2. INLINE: Inline callees based on profile     │
│  3. OPTIMIZE:                                   │
│     - Null check elimination                    │
│     - Dead code removal                         │
│     - Loop unrolling / vectorization            │
│     - Escape analysis → stack allocation        │
│  4. SCHEDULE: Instruction ordering for CPU      │
│  5. REGALLOC: Map IR to registers               │
│  6. EMIT: Generate native machine code          │
│  7. INSTALL: Linked into Code Cache             │
└─────────────────────────────────────────────────┘
```

**Code Cache:**
All JIT-compiled code lives in the Code Cache — a fixed off-heap memory region. When full, JIT compilation stops (Code Cache is full warning). The JVM may flush cold compiled code to make space. In Java 9+, the Code Cache is split into three regions: non-methods (JVM stubs), profiled (C1 code), non-profiled (C2 code).

**Profile-Guided Optimizations:**
- **Type profiling**: If a virtual call always dispatches to `Dog.speak()`, inline `Dog.speak()` directly with a guard check. 99% of calls skip virtual dispatch.
- **Branch prediction**: If a branch is taken 99.9% of the time, the rare path is moved to "slow path" cold code.
- **Null-check hoisting**: If an object is never null in profiling, the null check is removed from the hot path.

**Deoptimization:**
If a speculative optimization (e.g., "always Dog, never Cat") becomes invalid (a `Cat` object appears), the JIT invalidates the compiled code and falls back to the interpreter — called deoptimization (see entry 0301).

---

### 🔄 The Complete Picture — End-to-End Flow

**NORMAL FLOW:**
```
[JVM starts] → [Method interpreted]
    → [Invocation counter incremented] 
    → [Counter > CompileThreshold?]
    → [YES: Submit to compiler queue] ← YOU ARE HERE
    → [Background JIT thread compiles]
    → [Native code installed in Code Cache]
    → [Next method entry → dispatch table → native code]
    → [~10-50x faster execution]
```

**FAILURE PATH:**
```
[Code Cache full]
    → [JIT stops compiling new methods]
    → [New hot methods stay interpreted]
    → ["CodeCache is full" warning logged]
    → [Performance degrades; never reaches peak]

[Type assumption violated]
    → [Compiled code invalidated]
    → [Deoptimization to interpreter]
    → [Method re-profiled and re-compiled]
```

**WHAT CHANGES AT SCALE:**
With many short-lived JVM instances (serverless functions, Kubernetes pods), warmup time means each instance performs poorly for its entire short lifetime. This drove development of AOT (GraalVM Native Image) and Class Data Sharing (CDS). At 100x scale, JIT compilation threads can themselves become CPU bottlenecks on startup — tune with `-XX:CICompilerCount` to control how many JIT threads run.

---

### 💻 Code Example

Example 1 — JIT compilation flags and monitoring:
```bash
# Print which methods get JIT-compiled:
java -XX:+PrintCompilation MyApp

# Output format:
# [timestamp] [compile_id] [flags] [method] [size] [time]
# 42   1   %  4 java.util.ArrayList::add @ 0 (20 bytes)
#     ^        ^
#     id       % = OSR compilation

# Print inlining decisions:
java -XX:+UnlockDiagnosticVMOptions \
     -XX:+PrintInlining MyApp
```

Example 2 — Proper JMH benchmark (accounts for JIT warmup):
```java
import org.openjdk.jmh.annotations.*;
import java.util.concurrent.TimeUnit;

@BenchmarkMode(Mode.AverageTime)
@OutputTimeUnit(TimeUnit.NANOSECONDS)
@Warmup(iterations = 5, time = 1)   // JIT warmup iterations
@Measurement(iterations = 10, time = 1)
@Fork(2)
public class ParseBenchmark {

    @Benchmark
    public int parseSimple(BenchmarkState state) {
        return Integer.parseInt(state.input);
    }
    // JMH handles warmup, forks, and dead-code elimination
    // Do NOT use a plain main() for benchmarks
}
```

Example 3 — Controlling Code Cache size:
```bash
# Default code cache (Java 11+): 240MB
# For JIT-heavy servers, increase explicitly:
java -XX:ReservedCodeCacheSize=512m \
     -XX:InitialCodeCacheSize=256m MyApp

# Monitor code cache usage:
jcmd <pid> Compiler.codecache

# Output shows: used, max, sweeper stats
```

Example 4 — Inspecting compiled code (assembly output):
```bash
# Requires hsdis (HotSpot disassembler plugin)
java -XX:+UnlockDiagnosticVMOptions \
     -XX:+PrintAssembly \
     -XX:CompileOnly=MyClass::hotMethod \
     MyApp 2>&1 | head -100
```

---

### ⚖️ Comparison Table

| Execution Strategy | Startup Speed | Peak Throughput | Memory Use | Best For |
|---|---|---|---|---|
| **JIT (HotSpot)** | Slow (warmup) | Very high (near-native) | Moderate (code cache) | Long-running services |
| Pure Interpreter | Fast | Low (10-50x slower) | Minimal | Scripting, rare-path code |
| AOT (Native Image) | Very fast | High (no deopt) | Low | CLI tools, serverless, cold start |
| C1 only (client mode) | Medium | Medium | Low | Development, low-latency startup |
| C2 only | Slow | Highest | Highest | Throughput-focused batch |
| Tiered (C1→C2) | Medium | Very high | Moderate | Default production mode |

How to choose: Use default tiered JIT for most applications. Switch to Native Image (GraalVM) for cloud functions or CLI tools where cold start matters more than peak throughput. Never use C1-only in production for data-intensive workloads.

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| JIT-compiled Java is always slower than C++ | Modern JIT can match or beat C++ in long-running workloads by using runtime type data for inlining — static C++ compilers cannot do this |
| The JIT compiles the entire program on startup | The JIT compiles only hot methods (invoked >10,000 times by default). Cold code runs interpreted forever |
| System.gc() triggers JIT recompilation | `System.gc()` only triggers GC. JIT compilation is driven by invocation counters, not GC |
| Increasing thread count always improves JIT performance | More threads = faster compilation, but also more CPU stolen from application threads. The default is usually optimal |
| JIT results are stable and reproducible across runs | JIT decisions are influenced by object allocation patterns, class loading order, and CPU state — perfect reproducibility requires controlled environments |
| JIT compiles to platform-independent bytecode | JIT compiles to native machine code specific to the exact CPU architecture (including SIMD instruction availability) |

---

### 🚨 Failure Modes & Diagnosis

**Code Cache Full — JIT Stops Compiling**

**Symptom:**
Log warning: `CodeCache is full. Compiler has been disabled.` After this, throughput drops to interpreted speed and never recovers for the JVM's lifetime.

**Root Cause:**
All 240MB (default) of Code Cache is exhausted. Can happen with large applications, many lambda expressions compiling many invokedynamic forms, or JIT loops in microservice code where hundreds of service classes each have many hot methods.

**Diagnostic Command / Tool:**
```bash
jcmd <pid> Compiler.codecache
# Look for: "used" close to "max"

# Real-time monitoring:
jstat -compiler <pid> 1000
# Columns: Compiled Failed Invalid Time FailedType FailedMethod
```

**Fix:**
```bash
java -XX:ReservedCodeCacheSize=512m \
     -XX:+UseCodeCacheFlushing MyApp
```

**Prevention:**
Monitor Code Cache usage in Grafana (`jvm_codecache_bytes`). Alert at 80% utilization.

---

**JIT Warmup Causing P99 Latency Spikes**

**Symptom:**
Immediately after deployment, P99 latency is 10x higher for 60-120 seconds, then normalizes. Customer-facing latency SLO is violated during rollout.

**Root Cause:**
During warmup, hot code runs interpreted. Interpreted `parseRequest()` takes 500µs instead of 50µs. First 10,000 requests per method hit interpreted performance.

**Diagnostic Command / Tool:**
```bash
java -XX:+PrintCompilation 2>&1 | \
  awk '{print $4}' | sort | uniq -c | sort -rn | head
# Shows which methods are being compiled in the first minutes
```

**Fix:**
Use CDS (Class Data Sharing) or AOT compilation for frequently-used classes. For critical deployments, do warm-up requests before routing live traffic (e.g., Kubernetes readiness probe hits warm-up endpoint).

**Prevention:**
Implement a warm-up procedure in your service: issue synthetic requests covering all hot paths before marking the pod Ready.

---

**Excessive Deoptimization Causing Performance Cliff**

**Symptom:**
System performs well for hours, then suddenly throughput drops and CPU spikes. JIT has compiled a method with type assumptions that are now wrong.

**Root Cause:**
A new code path introduces a previously-unobserved type into a polymorphic call site. The JIT's optimistic inlining assumption is violated. The compiled code is invalidated, deoptimized to interpreter, and must re-profile and re-compile. During re-compilation, performance is interpretation-speed.

**Diagnostic Command / Tool:**
```bash
java -XX:+TraceDeoptimization \
     -XX:+PrintDeoptimizationDetails MyApp
# Look for frequent deoptimizations of the same method
```

**Fix:**
Reduce polymorphism in hot paths. If your hot loop always processes `ArrayList`, avoid passing `LinkedList` to the same method.

**Prevention:**
Use `-XX:+PrintInlining` in load testing to identify megamorphic callsites and refactor them before production.

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**
- `JVM` — the JIT is a subsystem of the JVM; you need to understand JVM's execution model
- `Bytecode` — JIT compiles bytecode to native code; understanding bytecode structure clarifies what the JIT is transforming
- `Stack Frame` — JIT must manage stack frames during compilation and OSR

**Builds On This (learn these next):**
- `C1 / C2 Compiler` — the two specific compiler tiers that implement JIT in HotSpot JVM
- `Tiered Compilation` — the strategy of using both C1 and C2 in sequence; the full JIT architecture
- `Method Inlining` — the single most impactful optimization the JIT performs; understanding it reveals why JIT beats static compilers
- `Deoptimization` — what happens when JIT optimistic assumptions fail; critical for understanding JIT reliability
- `OSR (On-Stack Replacement)` — JIT's ability to compile a running method and switch to it mid-execution

**Alternatives / Comparisons:**
- `AOT (Ahead-of-Time Compilation)` — compiles before startup; sacrifices adaptiveness for fast cold start
- `GraalVM` — next-generation JIT and AOT compiler written in Java itself

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ WHAT IT IS   │ Runtime compiler that turns hot bytecode  │
│              │ into native machine code on-the-fly       │
├──────────────┼───────────────────────────────────────────┤
│ PROBLEM IT   │ Pure interpretation is 10-50x too slow    │
│ SOLVES       │ for production workloads                  │
├──────────────┼───────────────────────────────────────────┤
│ KEY INSIGHT  │ JIT can be MORE aggressive than a static  │
│              │ compiler because it uses runtime profile  │
│              │ data; it bets on observations with a      │
│              │ fallback (deoptimization)                 │
├──────────────┼───────────────────────────────────────────┤
│ USE WHEN     │ Always (default for JVM); tune thresholds │
│              │ for latency-sensitive or batch workloads  │
├──────────────┼───────────────────────────────────────────┤
│ AVOID WHEN   │ Need predictable cold-start latency →     │
│              │ use AOT / Native Image instead            │
├──────────────┼───────────────────────────────────────────┤
│ TRADE-OFF    │ Peak throughput vs warmup time            │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "The translator that gets faster the      │
│              │  more it hears the same sentence"         │
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ C1/C2 → Tiered Compilation → Inlining    │
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** A microservice deployed on Kubernetes receives traffic for exactly 90 seconds, then the pod is terminated and replaced. Your profiling shows that the JIT only finishes warming up at around 60 seconds. Describe the exact options available to you to improve this service's performance — including how Class Data Sharing, GraalVM AOT profile-guided optimization, and readiness probe timing interact — and the precise trade-offs each approach makes.

**Q2.** The JIT makes the speculative assumption that a virtual method call always dispatches to `ArrayList.add()` and inlines it. Trace the complete sequence of events when a `LinkedList` is passed to that same call site for the first time after 1 million invocations of `ArrayList`. What state must the JVM preserve? What work must the interpreter re-do? How does the JIT decide to recompile, and what happens to threads currently executing the invalidated compiled code?

