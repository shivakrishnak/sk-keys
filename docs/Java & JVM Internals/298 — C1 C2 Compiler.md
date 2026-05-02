---
layout: default
title: "C1 / C2 Compiler"
parent: "Java & JVM Internals"
nav_order: 298
permalink: /java/c1-c2-compiler/
number: "0298"
category: Java & JVM Internals
difficulty: ★★★
depends_on:
  - JIT Compiler
  - Bytecode
  - Tiered Compilation
  - Method Inlining
used_by:
  - Tiered Compilation
  - Deoptimization
  - GraalVM
related:
  - Tiered Compilation
  - Method Inlining
  - GraalVM
  - AOT (Ahead-of-Time Compilation)
tags:
  - jvm
  - jit
  - performance
  - java-internals
  - deep-dive
---

# 0298 — C1 / C2 Compiler

⚡ TL;DR — HotSpot JVM has two JIT compilers: C1 compiles *fast with light optimization* for quick wins, and C2 *compiles slowly but aggressively* for maximum throughput on proven hot code.

| #0298 | Category: Java & JVM Internals | Difficulty: ★★★ |
|:---|:---|:---|
| **Depends on:** | JIT Compiler, Bytecode, Tiered Compilation, Method Inlining | |
| **Used by:** | Tiered Compilation, Deoptimization, GraalVM | |
| **Related:** | Tiered Compilation, Method Inlining, GraalVM, AOT Compilation | |

### 🔥 The Problem This Solves

WORLD WITHOUT IT:
The JVM shipped two separate modes: "client" mode (fast compilation, modest optimization, suitable for GUIs and short-lived apps) and "server" mode (slow compilation, aggressive optimization, only suitable after long warmup). If you needed a server with both fast startup and high throughput, you had to pick one and accept its downsides. Running `-server` meant the first 60 seconds of production traffic were painfully slow as C2 compiled everything from scratch. Running `-client` meant the server never reached peak performance.

THE BREAKING POINT:
A production API service uses `-server` mode. It handles 2,000 req/s but during a rollout the pod starts cold. For the first 45 seconds, latency is 400ms (CPU-bound interpretation). 99th percentile SLA is 200ms. Alarms fire. Engineers manually delay traffic switching to new pods. Deployment takes 30 minutes instead of 5.

THE INVENTION MOMENT:
This is exactly why **C1 and C2** exist as a two-compiler pipeline within the same JVM — C1 for fast, cheap early compilation to reduce cold-start pain, while C2 handles proven-hot methods with expensive global optimization for peak throughput.

### 📘 Textbook Definition

**C1** (the "client" compiler) and **C2** (the "server" compiler) are the two JIT compilation backends in the HotSpot JVM. C1 performs a linear, method-local optimization pass and produces compiled code quickly (microseconds to milliseconds) with low optimization overhead, sacrificing peak performance. C2 uses an SSA-based intermediate representation ("Sea of Nodes") and performs aggressive global optimizations including global value numbering, alias analysis, loop transformations, and auto-vectorization, producing near-optimal native code but taking tens to hundreds of milliseconds per method. In tiered compilation mode (default since Java 8), both run in sequence: newly hot methods are first compiled by C1, then — if they remain hot — re-compiled by C2.

### ⏱️ Understand It in 30 Seconds

**One line:**
C1 is a "fast sketch" and C2 is a "masterpiece" — you need both because masterpieces take time.

**One analogy:**
> Imagine an art studio where urgent orders get a fast pencil sketch (C1) — usable immediately, not perfect. If the client keeps ordering the same piece, the studio then does a full oil painting (C2) — time-consuming but museum quality. This way clients always get quick results, and popular pieces get the highest quality treatment over time.

**One insight:**
The critical insight is that C1 and C2 are not redundant — C1 produces *instrumented code* that continues profiling the method even after compilation. This profile is what C2 feeds on to make its hyper-optimized decisions. Without C1's profiled output, C2 would be forced to make conservative assumptions, producing code no better than C1's anyway.

### 🔩 First Principles Explanation

CORE INVARIANTS:
1. Fast compiler → low-latency startup; aggressive compiler → high throughput.
2. Profiling data quality increases with more execution time — the more you observe a method running, the better optimization decisions you can make.
3. Compilation is expensive CPU work — the compiler must not steal so many cycles that it hurts the application.

DERIVED DESIGN:
Given these constraints, the optimal architecture is a pipeline:
- **Tier 0** (Interpreter): Gather initial profiling, cheap, triggers on first invocation.
- **Tier 1–2** (C1, minimal/limited profiling): Quick native code for moderately-invoked methods. Reduces interpreter overhead fast.
- **Tier 3** (C1, full profiling): Same fast compilation, but instrumented to gather detailed type and branch profiles.
- **Tier 4** (C2): Use the rich profile from Tier 3 to produce globally-optimized native code.

```
┌─────────────────────────────────────────────────┐
│    C1/C2 Tiered Compilation Pipeline            │
│                                                 │
│  Invocations:  1    1K    10K   100K            │
│                │     │      │      │            │
│  Tier: [0]--->[1]-->[3]--->[4]                  │
│         Interp  C1   C1+   C2                   │
│                     prof                        │
│                                                 │
│  C1 benefits: 2x-5x faster than interpreter    │
│  C2 benefits: 10x-50x faster than interpreter  │
└─────────────────────────────────────────────────┘
```

THE TRADE-OFFS:
Gain: Best of both worlds — fast startup (C1) and peak throughput (C2) in a single JVM.
Cost: Methods hot enough for C2 are compiled twice (C1 then C2), consuming more CPU. Both compilers consume memory (Code Cache). Complex C2 compilation can cause compilation pauses if the compiler queue grows.

### 🧪 Thought Experiment

SETUP:
A REST endpoint `calculateTax()` is called 100,000 times per second. It contains a tight loop with arithmetic, a virtual dispatch, and a conditional.

C1 COMPILATION (at ~100 invocations):
C1 compiles `calculateTax()` in 200µs. The result is ~3x faster than the interpreter. C1-compiled code still includes profiling instrumentation to track which branch is taken and which concrete type the virtual call receives. The counters keep ticking.

C2 COMPILATION (at ~10,000 invocations):
C2 receives the method + C1 profile data. It sees: branch always taken (removes the `if` body from hot path), virtual call always dispatches to `TaxCalculatorImpl` (inlines the entire implementation). C2 produces code 50x faster than the interpreter, 15x faster than C1, with the tax calculation effectively reduced to a few ALU instructions.

THE INSIGHT:
Without C1's profiling instrumentation phase, C2 would be compiling a *cold* method with no type information — forced to include full virtual dispatch and all branch paths. C1's instrumented code is not just a fast interim solution; it is a profiling mechanism that *feeds* C2's optimizer.

### 🧠 Mental Model / Analogy

> Picture a two-round architectural design process. Round 1 (C1): architects produce a quick floor plan sketch — functional, clients can start building immediately, done in hours. Simultaneously, the sketch is used as a real building so architects observe exactly which rooms are used most, which doors are opened constantly, and which hallways are always congested. Round 2 (C2): using those observations, architects produce an optimized final design with wider hallways exactly where needed, smaller rooms nobody uses, and the most-used doors widened into archways.

"Floor plan sketch" → C1 compiled code.
"Observing room usage" → C1 profiling instrumentation (branch and type counters).
"Optimized final design" → C2 compiled code using C1's profile data.
"Most-used doors widened" → method inlining at confirmed monomorphic callsites.

Where this analogy breaks down: Architects do the second pass once. C2 may deoptimize and re-compile multiple times as runtime behavior changes.

### 📶 Gradual Depth — Four Levels

**Level 1 — What it is (anyone can understand):**
The JVM has two translators for Java code: a fast one that works quickly but isn't perfect (C1), and a slow one that takes more time but produces the best possible result (C2). For code that's only run a few times, the fast one is fine. For code run millions of times, the slow one's superior output saves massive time overall.

**Level 2 — How to use it (junior developer):**
You do not choose between C1 and C2 directly — tiered compilation is the default since Java 8. You can force specific modes with `-XX:TieredStopAtLevel=1` (C1 only, e.g., for development or microservice cold-start testing) or `-XX:-TieredCompilation` to disable tiered (uses C2 only, like old `-server` mode). For most production services: leave defaults.

**Level 3 — How it works (mid-level engineer):**
C1 uses a **local** optimization approach: parse bytecode into a high-level IR, run a single optimization pass (constant folding, null-check elimination, inlining of small methods), then emit native code. The process is fast (~0.5ms). C2 uses the **Sea of Nodes** IR — a directed acyclic graph where every value and control dependency is explicit. This global representation enables loop-invariant code motion, scalar replacement via escape analysis, global value numbering, and auto-vectorization (SIMD). C2 compilation takes 50-500ms per method. Both use the same Code Cache.

**Level 4 — Why it was designed this way (senior/staff):**
The Sea of Nodes IR (introduced by Cliff Click in his 1995 Stanford PhD thesis, and the basis for Graal's IR) is elegant but expensive: it merges data flow and control flow into a single graph, allowing optimizations that span loop boundaries and conditional paths. The cost is compilation time — the optimizer must traverse and transform a potentially huge graph. This is why C2 is reserved for *proven-hot* methods (invoked 10,000+ times) where the amortized speedup over millions of invocations justifies the one-time compilation cost. C2's global optimization scope also requires sophisticated deoptimization support: any speculative inline or null-check removal must be reversible if the profiling data turns out to be wrong (rare types appear).

### ⚙️ How It Works (Mechanism)

**C1 Internal Pipeline:**
```
[Bytecode] → [Parse → HIR (High-level IR)]
    → [Optimizations: constant folding, inlining]
    → [LIR (Low-level IR, register representation)]
    → [Register allocation (linear scan)]
    → [Code emission → x86/ARM native code]
```
Total time: ~0.1–5ms depending on method size.

**C2 Internal Pipeline:**
```
[Bytecode + C1 Profile data]
    → [Parse → Sea of Nodes IR]
    → [Global Value Numbering (GVN)]
    → [Loop optimizations (unrolling, vectorization)]
    → [Escape Analysis → stack allocation]
    → [Inlining (profile-guided, monomorphic)]
    → [Null check elimination (profile-guided)]
    → [Schedule + Register allocation]
    → [Code emission → highly optimized native]
```
Total time: ~10–500ms.

**Code Cache Segments (Java 9+):**
```
┌──────────────────────────────────────────────────┐
│ Code Cache Layout (Java 9+ Segmented Cache)      │
├──────────────────────────────────────────────────┤
│ Non-methods (stubs, runtime code):  ~5–10 MB     │
│ Profiled (C1 code, instrumented):   ~100–150 MB  │
│ Non-profiled (C2 code, optimized):  ~200–250 MB  │
└──────────────────────────────────────────────────┘
```
Segmented cache prevents C1 code (which may be evicted when C2 code replaces it) from fragmenting the C2 code region.

**Compilation Threads:**
`-XX:CICompilerCount` controls how many background JIT threads run. Default is 2 for older CPUs, up to `# of cores / 2` capped at 4 on modern hardware. For containers: `CICompilerCount` may be misconfigured if CPU quotas are not properly detected (see Java 10+ fixes for container CPU detection).

### 🔄 The Complete Picture — End-to-End Flow

NORMAL FLOW:
```
[Method first called] → [Tier 0: Interpreted]
    → [Invocation count crosses Tier 1 threshold (~200)]
    → [C1: Fast compile, no profiling] ← YOU ARE HERE (C1 phase)
    → [C1: install, method ~3x faster]
    → [Profiling counters continue]
    → [Invocation count crosses Tier 3 threshold (~2K)]
    → [C1: Recompile with full profiling instrumentation]
    → [Invocation count crosses Tier 4 threshold (~15K)]
    → [C2: Profile-guided compile] ← YOU ARE HERE (C2 phase)
    → [C2: install, method ~20-50x faster than interpreter]
```

FAILURE PATH:
```
[C2 queue backed up under heavy startup load]
    → [Methods stuck at C1 or Tier 3]
    → [Peak performance delayed]
    → [Increase -XX:CICompilerCount to add C2 threads]

[Deoptimization after C2 optimization]
    → [Method falls back to interpreter (Tier 0)]
    → [Re-profiles, eventually re-submits to C2]
    → [Performance temporarily degrades]
```

WHAT CHANGES AT SCALE:
In containerized environments with CPU throttling, the JIT compilation threads compete with application threads for the CPU quota. At scale with many containers, setting `CICompilerCount` too high degrades application throughput during warmup. At 1000+ concurrent JVM instances (microservice fleet), the aggregate compilation overhead is significant — driving adoption of ahead-of-time profiling with JEP 410 (AOT cache) in Java 24+.

### 💻 Code Example

Example 1 — Checking active compilation levels:
```bash
# Show tiered compilation levels for each method:
java -XX:+PrintCompilation MyApp

# Key in output:
# blank = non-tiered
# b     = blocking compilation
# n     = native wrapper
# %     = OSR (on-stack replacement)
# !     = method has exception handler
# s     = synchronized
# 1,2,3 = tier level from C1
# 4     = tier 4 (C2)

# Example output:
# 185   31   3  com.example.Parser::parse (34 bytes)
# 187   32   4  com.example.Parser::parse (34 bytes) <- C2!
```

Example 2 — Forcing C1-only (fast startup, lower peak):
```bash
# Only use C1 (tiered stop at level 1):
java -XX:TieredStopAtLevel=1 MyApp

# Use case: development, short-lived batch jobs,
# or when startup latency trumps throughput
```

Example 3 — Forcing C2-only (old -server behavior):
```bash
# Disable tiered, use C2 exclusively:
java -XX:-TieredCompilation MyApp

# Warning: much slower startup; only for
# very long-running, throughput-critical batch jobs
```

Example 4 — Monitoring Code Cache per tier:
```bash
# Show code cache stats:
jcmd <pid> Compiler.codecache

# Sample output:
# CodeHeap 'non-profiled nmethod'  used=45Mb max=120Mb
# CodeHeap 'profiled nmethod'      used=30Mb max=120Mb
# CodeHeap 'non-methods'           used=8Mb  max=8Mb
```

### ⚖️ Comparison Table

| Compiler | Compilation Speed | Generated Code Speed | Profile Data | Best For |
|---|---|---|---|---|
| Interpreter (Tier 0) | Instant | Slowest (1x) | Yes | First invocations |
| **C1 Tier 1** | Very fast | Fast (2–3x) | None | Infrequent methods |
| **C1 Tier 3** | Very fast | Fast (2–3x) | Full type/branch | Feeds C2 |
| **C2 Tier 4** | Slow | Very fast (10–50x) | Uses C1 profile | Proven hot code |
| Graal JIT | Slower than C2 | Faster than C2 | Yes | Java 17+ via `-XX:+UseJVMCICompiler` |

How to choose: Leave tiered compilation enabled (default). Tune `TieredStopAtLevel=1` only when startup time is the primary constraint and peak throughput is secondary (e.g., serverless functions under 10 seconds lifetime).

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| C1 and C2 produce the same code, just at different times | C2 produces fundamentally different, more optimized code — it can inline multiple levels of method calls, eliminate branches, and vectorize loops that C1 never touches |
| Disabling tiered compilation speeds things up | Disabling tiered forces C2-only, which means ALL methods start at interpreter speed and wait for C2's slow compilation — startup is much slower |
| C1 code is discarded when C2 compiles the same method | C1 code is replaced (overwritten) in the Code Cache by C2 code. The old C1 code entry is marked as not-entrant and garbage collected from the Code Cache over time |
| Adding more C1/C2 threads always helps | More JIT threads steal CPU from the application. On a 2-core container, running 4 JIT threads causes severe application starvation during warmup |
| C2 always produces correct code | C2 relies on speculative optimistic assumptions that can be wrong — this requires deoptimization support. Bugs in C2 (though rare) produce JVM crashes via SIGSEGV in native code |
| GraalVM replaces C2 in standard JDK | As of Java 21, GraalVM JIT (Graal) is available via `-XX:+UseJVMCICompiler` as an experiment but is NOT the default; HotSpot C2 remains the standard |

### 🚨 Failure Modes & Diagnosis

**C2 Compilation Thread Saturation**

Symptom:
During startup or traffic spikes, CPU usage is high but application throughput is low. `PrintCompilation` shows a very long queue of pending C2 compilations.

Root Cause:
The default number of C2 compiler threads (often 2–4) is insufficient for the rate at which hot methods are discovered. Methods queue up waiting for C2 compilation and continue running at C1 speed.

Diagnostic Command / Tool:
```bash
jcmd <pid> Compiler.queue
# Shows methods waiting in compiler queue

jstat -compiler <pid> 1000
# Monitor Compiled count per second
```

Fix:
```bash
java -XX:CICompilerCount=6 MyApp
# Or tune compilation thresholds to defer C2:
java -XX:Tier4CompileThreshold=40000 MyApp
```

Prevention:
Performance test with realistic warmup load. Set `CICompilerCount` based on profiled compilation queue depth.

---

**C2 Deoptimizes Hot Method Repeatedly**

Symptom:
`PrintCompilation` shows the same method compiling at tier 4, then immediately appearing at tier 0, then tier 4 again, cycling every few seconds. Throughput oscillates.

Root Cause:
A type assumption made by C2 is violated repeatedly (e.g., a megamorphic callsite that occasionally receives a rare type). Each violation forces deoptimization and re-compilation.

Diagnostic Command / Tool:
```bash
java -XX:+TraceDeoptimization MyApp 2>&1 | \
  grep "deoptimizing"
# Shows method + deoptimization reason
```

Fix:
Identify the polymorphic callsite in the method. Refactor: separate the rare-type path from the hot main path (method dispatch or explicit type check before submission).

Prevention:
Profile your application's polymorphic callsites. Methods with >3 receiver types at a single callsite will never benefit from C2's type inlining.

---

**Code Cache Fragmentation After GC Integration**

Symptom:
Over time, Code Cache utilization stays high even though application method count is stable. `Compiler.codecache` shows fragmented regions.

Root Cause:
Old C1 (tier 1/3) code that was replaced by C2 (tier 4) leaves "not-entrant" or "zombie" code entries that are not immediately reclaimed. The Code Cache sweeper runs periodically but may not keep pace if code is being invalidated faster than swept.

Diagnostic Command / Tool:
```bash
jcmd <pid> Compiler.codecache
# Check for high "free_blocks" with low "total free" utilization
```

Fix:
```bash
java -XX:+UseCodeCacheFlushing \
     -XX:ReservedCodeCacheSize=512m MyApp
```

Prevention:
Monitor Code Cache waste/free ratio in production dashboards. Alert if used > 80% of reserved.

### 🔗 Related Keywords

**Prerequisites (understand these first):**
- `JIT Compiler` — C1 and C2 are the two concrete implementations of the JIT abstraction
- `Bytecode` — both C1 and C2 compile bytecode as their input representation

**Builds On This (learn these next):**
- `Tiered Compilation` — the framework that orchestrates C1 and C2 in sequence; the complete picture
- `Method Inlining` — C2's most impactful optimization; understanding inlining reveals why C2 is so much faster than C1
- `Deoptimization` — what happens when C2's speculative assumptions are wrong; essential pair with C2 knowledge

**Alternatives / Comparisons:**
- `GraalVM` — replaces C2 with a Java-implemented compiler (Graal JIT) that produces better code for some workloads and enables polyglot compilation
- `AOT (Ahead-of-Time Compilation)` — avoids both C1 and C2 entirely; no runtime compilation, no warmup, but no adaptive optimization either

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ WHAT IT IS   │ Two-tier JIT backend: C1=fast compile,    │
│              │ C2=slow but near-optimal compilation      │
├──────────────┼───────────────────────────────────────────┤
│ PROBLEM IT   │ One compiler cannot optimize for both     │
│ SOLVES       │ fast startup AND maximum throughput       │
├──────────────┼───────────────────────────────────────────┤
│ KEY INSIGHT  │ C1 compiles fast AND collects rich type   │
│              │ profiles; C2 consumes those profiles for  │
│              │ ultra-aggressive optimization             │
├──────────────┼───────────────────────────────────────────┤
│ USE WHEN     │ Default tiered compilation for all        │
│              │ production JVM workloads                  │
├──────────────┼───────────────────────────────────────────┤
│ AVOID WHEN   │ Serverless with <5s lifetime → use AOT    │
├──────────────┼───────────────────────────────────────────┤
│ TRADE-OFF    │ CPU cost (compile threads) vs peak perf   │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "Fast sketch first, masterpiece later —   │
│              │  with the sketch informing the painting"  │
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ Tiered Compilation → Inlining → Deopt     │
└──────────────────────────────────────────────────────────┘
```

---
### 🧠 Think About This Before We Continue

**Q1.** In a tiered compilation model, C1 code is designed to be *profiling instrumented* — it runs slightly slower than un-instrumented C1 code specifically because it is collecting data for C2. If a method is invoked exactly 14,999 times (just below the C2 threshold), it runs at C1 Tier 3 speed forever — slower than C1 Tier 1 (no instrumentation) but without ever getting C2's benefit. What JVM flags could you use to detect and fix this scenario, and what is the performance engineering principle that this threshold tuning problem illustrates?

**Q2.** C2 uses "Sea of Nodes" global IR. Describe a concrete Java method that looks simple but would produce dramatically better native code from C2 than from C1 — explain which specific optimization (escape analysis, loop vectorization, or branch elimination) is responsible, and why that optimization is structurally impossible for C1 to perform with its local, linear IR.

