---
layout: default
title: "Tiered Compilation"
parent: "Java & JVM Internals"
nav_order: 299
permalink: /java/tiered-compilation/
number: "0299"
category: Java & JVM Internals
difficulty: ★★★
depends_on:
  - JIT Compiler
  - C1 / C2 Compiler
  - Bytecode
  - Method Inlining
used_by:
  - Deoptimization
  - GC Tuning
  - GraalVM
related:
  - C1 / C2 Compiler
  - Method Inlining
  - OSR (On-Stack Replacement)
  - AOT (Ahead-of-Time Compilation)
tags:
  - jvm
  - jit
  - performance
  - java-internals
  - deep-dive
---

# 0299 — Tiered Compilation

⚡ TL;DR — Tiered Compilation runs five JVM execution levels automatically, starting with the interpreter and ending with C2's maximum-optimization native code — giving both fast startup and peak throughput from a single JVM.

| #0299 | Category: Java & JVM Internals | Difficulty: ★★★ |
|:---|:---|:---|
| **Depends on:** | JIT Compiler, C1 / C2 Compiler, Bytecode, Method Inlining | |
| **Used by:** | Deoptimization, GC Tuning, GraalVM | |
| **Related:** | C1 / C2 Compiler, Method Inlining, OSR (On-Stack Replacement), AOT | |

---

### 🔥 The Problem This Solves

WORLD WITHOUT IT:
Pre-Java 7, you chose between two JVM modes at startup: `-client` (C1 only: fast startup, low peak performance) or `-server` (C2 only: slow startup, high peak performance). These were mutually exclusive. A web service using `-server` took 60–120 seconds to reach peak throughput while C2 compiled every hot method from scratch. Using `-client` left throughput permanently at 30–40% of what `-server` would have achieved.

THE BREAKING POINT:
A high-traffic e-commerce site rolls out new pods during a traffic surge. Each new pod in `-server` mode takes 90 seconds of poor performance before C2 finishes compiling. The load balancer routes traffic to the new pods too early. CPU hits 100% processing requests in slow interpreted/C1 code. The site experiences a partial outage during the rollout. Engineering team is forced to do rolling deployments at 3 AM when traffic is low.

THE INVENTION MOMENT:
This is exactly why **Tiered Compilation** was created — to automatically orchestrate all compilation levels in a single JVM, starting fast with C1 and progressively improving to C2, handling both startup latency and peak throughput without any configuration.

---

### 📘 Textbook Definition

**Tiered Compilation** is a JVM execution strategy (enabled by default since Java 8 via `-XX:+TieredCompilation`) that organizes code execution into five tiers: Tier 0 (interpreter), Tiers 1–3 (C1 at various profiling levels), and Tier 4 (C2). Methods migrate upward through tiers as their invocation counts cross tier-specific thresholds, with profiling data gathered at each tier feeding the next. The JVM's compilation controller (CompilationPolicy) dynamically manages tier transitions, compile queues, and load-shedding to balance the tradeoff between compilation overhead and execution performance.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
Five training levels — methods start at slowest/cheapest and automatically graduate to fastest as they prove themselves worth the cost.

**One analogy:**
> An athlete's training program: Day 1, they do basic exercises (interpreter). After showing potential, they move to a local gym (C1, no analysis). If they consistently perform well, a coach starts tracking their detailed stats (C1 with profiling). After months of data, an elite trainer designs a fully personalized peak-performance plan (C2). The athlete never has to ask to be promoted — the system watches results and promotes automatically.

**One insight:**
The tier transition is not just "faster code" — each tier transition also changes the *profiling depth*. A method sitting at Tier 3 (C1 with full profiling) is actively gathering rich data that will make Tier 4 (C2) aggressively better. The tiers are a data pipeline, not just a speed ladder.

---

### 🔩 First Principles Explanation

CORE INVARIANTS:
1. Cold code should not pay compilation overhead; hot code must pay it because the payoff is enormous.
2. Better profiling data → better C2 optimization decisions → higher return on compilation investment.
3. JIT compilation consumes CPU; too much compilation overhead kills application responsiveness.

DERIVED DESIGN:

The five tiers and their thresholds:

```
┌────────────────────────────────────────────────────┐
│ Tier │ Engine     │ Profile?  │ Threshold (approx) │
├──────┼────────────┼───────────┼────────────────────┤
│  0   │ Interpreter│ Invocations│ -                 │
│  1   │ C1         │ None       │ ~100 invocations  │
│  2   │ C1         │ Limited    │ ~200 invocations  │
│  3   │ C1         │ Full       │ ~2,000            │
│  4   │ C2         │ Uses prior │ ~15,000           │
└────────────────────────────────────────────────────┘
```

The CompilationPolicy governs transitions:
- If the C2 queue is short (not overloaded), methods skip directly from Tier 0 → Tier 3 → Tier 4.
- If the C2 queue is long (overloaded), methods go Tier 0 → Tier 1 → Tier 2 → stop (C2 not triggered) — this is the **load shedding** mechanism that prevents compilation from overloading the system under startup bursts.

THE TRADE-OFFS:
Gain: Auto-tuning across startup and peak; single JVM mode works for all use cases.
Cost: Added JVM complexity; profiling overhead at Tier 3 (a few percent); more compiler threads needed for optimal performance; Code Cache must accommodate both C1 and C2 code simultaneously.

---

### 🧪 Thought Experiment

SETUP:
Two identical servers start simultaneously at 08:00. Server A: no tiered compilation (C2 only). Server B: tiered compilation. Both receive 5,000 requests/second immediately.

SERVER A (no tiered):
- 08:00–08:02: All methods interpreting. Every request: 500ms. SLAs violated.
- 08:02–08:05: C2 starts compiling hot methods. Performance gradually improves.
- 08:05: C2 compilation complete. Requests: 20ms. Excellent throughput.

SERVER B (tiered):
- 08:00: Methods skip quickly to C1 Tier 1 (100 invocations each). Within 2 seconds, most hot paths have C1 code.
- 08:00:30s: C1 Tier 3 code active. Requests: 80ms. Reasonable.
- 08:01: C1 Tier 3 profiling data ready. C2 starts compiling with profile-guided data.
- 08:02: C2 compilation done. Requests: 20ms. Same peak as Server A.

THE INSIGHT:
Server A has 5 minutes of SLA violations. Server B has 30 seconds of elevated latency, then 90 seconds of acceptable performance, then optimal. Tiered compilation's warmup curve is fundamentally smoother — it never leaves hot code at interpreter speed if any compiled version exists.

---

### 🧠 Mental Model / Analogy

> Think of tiered compilation as an express lane highway system. All cars start in the slowest lane (interpreter). After a few miles (invocations), they can merge into a faster lane (C1, no profiling). After more miles with consistent good driving, GPS traffic analysis kicks in (C1 full profiling). Eventually, frequent drivers get a personalized AI-optimized route suggested (C2). The highway system monitors all lanes in real time and manages congestion (compiler queue load shedding) by temporarily holding some cars in slower lanes when the fast lanes are full.

"Slowest lane" → Tier 0 interpreter.
"Fast lane" → C1 compiled code (Tier 1/2/3).
"AI-optimized route" → C2 profile-guided compilation.
"Congestion management" → CompilationPolicy load shedding.

Where this analogy breaks down: Unlike a highway, tiers are not about physical capacity — a method at Tier 2 can occupy exactly the same CPU as a method at Tier 4. The "lanes" here represent code quality levels, not resource slots.

---

### 📶 Gradual Depth — Four Levels

**Level 1 — What it is (anyone can understand):**
Java programs start slow and get faster over time. Tiered Compilation is the automatic system that manages this process — every piece of code begins simply and, if used enough, gets upgraded to run as fast as possible.

**Level 2 — How to use it (junior developer):**
Tiered Compilation is enabled by default in Java 8+. You do not need to do anything. Know that your service will run slower for the first 30–120 seconds than it will at steady state. Use JMH with warmup iterations for any performance benchmarking. If you need faster warmup, explore `TieredStopAtLevel=1` for development or readiness probe tricks.

**Level 3 — How it works (mid-level engineer):**
Each method has two counters: `invocation_counter` and `backedge_counter` (counting loop back-edges). The CompilationPolicy checks these at compile check points. Tier transitions are made individually per method based on a scoring function. When the compiler queue is full, the policy scales down thresholds to prevent starvation (methods waiting forever vs. spending a little time at a lower tier). The policy is implemented in `tieredThresholdPolicy.cpp` in OpenJDK source.

**Level 4 — Why it was designed this way (senior/staff):**
The tiered compilation design emerged from the recognition that C2 compilation latency (50–500ms) is unacceptable for short-lived methods, but simply using C1 for everything wastes massive peak throughput potential. The profiling tier (Tier 3) is specifically designed to generate the type-feedback and method call site profiles that C2 needs to inline aggressively. The load-shedding behavior under C2 queue pressure is a subtle but critical design: during startup, when dozens of methods all hit C2 threshold simultaneously, the system self-regulates by routing some methods to Tier 2 (cheap, no detailed profiling) rather than flooding the C2 queue — at the cost of those methods never getting C2-optimized unless they stay hot long enough to re-enter the queue.

---

### ⚙️ How It Works (Mechanism)

**Tier Transition Rules:**

The JVM's CompilationPolicy applies these rules at each compile checkpoint:

```
┌─────────────────────────────────────────────────┐
│       Tiered Compilation Transition Graph       │
│                                                 │
│  [Tier 0: Interpreter]                          │
│     │ invocations > T0_threshold                │
│     ▼                                           │
│  [Tier 3: C1 full profiling]                    │
│     │ (C2 queue not overloaded)                 │
│     │ invocations > T3_threshold                │
│     ▼                                           │
│  [Tier 4: C2 optimized]  ← NORMAL PATH         │
│                                                 │
│  UNDER LOAD (C2 queue full):                    │
│  [Tier 0] → [Tier 1: C1 no profiling]           │
│               → [Tier 2: C1 limited profiling]  │
│               (may never reach Tier 4)          │
└─────────────────────────────────────────────────┘
```

**Compilation Thresholds (Java 11+ defaults):**

| Threshold Flag | Default | Meaning |
|---|---|---|
| `Tier0InvokeNotifyFreqLog` | 7 | ~128 interp invocations before first check |
| `Tier3InvocationThreshold` | 200 | C1 profiled after ~200 invocations |
| `Tier4InvocationThreshold` | 5000 | C2 after ~5000 profiled invocations |
| `Tier4BackEdgeThreshold` | 40000 | C2 for loops after ~40K back-edges |

**Compiler Queue Management:**
Each compilation level has its own queue. When Tier 4 (C2) queue depth exceeds a threshold, the policy starts redirecting methods to Tier 2 instead of Tier 3 (to avoid producing profiling data that C2 will take too long to consume). This prevents the profile data from going stale.

---

### 🔄 The Complete Picture — End-to-End Flow

NORMAL FLOW:
```
[Application start]
    → [All methods: Tier 0 (interpreter)]
    → [Hot methods quickly reach Tier 3 (C1 profiling)]
    → [Profiling data accumulates] ← YOU ARE HERE
    → [Tier 3 → Tier 4 (C2 compilation)]
    → [Steady state: hot methods at Tier 4]
    → [New occasionally-called methods: stay Tier 1/2]
```

FAILURE PATH:
```
[Very high startup load]
    → [C2 queue overwhelmed]
    → [Policy routes many methods to Tier 2]
    → [Tier 2 methods never accumulate enough data for C2]
    → [Application runs at 50% of peak throughput indefinitely]
    → [Fix: reduce initial load, or increase CICompilerCount]
```

WHAT CHANGES AT SCALE:
At 100 JVM instances starting simultaneously (Kubernetes rolling deploy), the aggregate compilation load compounds: each JVM runs its own compiler threads, stealing CPU from application threads. With 4 compiler threads per pod and 100 pods on shared nodes, compilation overhead can cause node-level CPU saturation. Modern container-aware JVMs (Java 10+) detect CPU quotas correctly, but `CICompilerCount` should still be explicitly tuned for containerized deployments.

---

### 💻 Code Example

Example 1 — Observing tiered compilation in action:
```bash
# PrintCompilation shows tier numbers in output
java -XX:+PrintCompilation MyApp 2>&1 | tail -20

# Example output:
# 120   12       3  com.example.Foo::parseData (45 bytes)
#                ^-- tier 3 (C1 full profiling)
# 340   13       4  com.example.Foo::parseData (45 bytes)
#                ^-- tier 4 (C2 optimization)
# 341   12       3  made not entrant  (C1 code invalidated)
```

Example 2 — Checking current tier for a method via JFR:
```java
// Enable JDK Flight Recorder compilation events:
// java -XX:StartFlightRecording=
//   filename=app.jfr,settings=profile MyApp

// Then analyze in JMC:
// JVM Internals → Compilations tab shows
// method, tier, duration, size for each compilation
```

Example 3 — Tuning thresholds for faster warmup:
```bash
# Lower Tier 4 threshold for faster C2 compilation:
java -XX:Tier4InvocationThreshold=1000 \
     -XX:Tier4BackEdgeThreshold=10000 MyApp

# Warning: lowers the quality of profiling data
# C2 makes less-informed optimization decisions
# Only do this if startup latency > peak throughput priority
```

Example 4 — Stopping at Tier 1 for development:
```bash
# Maximum C1-speed but no profiling overhead, fast JVM start:
java -XX:TieredStopAtLevel=1 -jar dev-tool.jar

# Use case: IDE build tool, short-lived script, local dev service
# Do NOT use in production for throughput-critical services
```

---

### ⚖️ Comparison Table

| Compilation Mode | Cold Start | Warmup Speed | Peak Throughput | Best For |
|---|---|---|---|---|
| **Tiered (default)** | Fast | Medium (30–120s) | Very high | All production services |
| C2 only (-server) | Very slow | Slow (60–180s) | Very high | Long-running batch; pre-Java 7 servers |
| C1 only (TieredStopAtLevel=1) | Fast | Immediate | Medium | Dev tools, CLIs, short-lived tasks |
| Interpreter only | Fastest | Immediate | Very low | Debugging, profiling |
| GraalVM Native Image (AOT) | Ultrafast | None needed | High | Serverless, CLIs, container cold-start |

How to choose: Default tiered compilation is the right answer for 95% of Java services. Use GraalVM Native Image for CLIs and serverless. Never use C2-only in production.

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| Java always runs with all 5 tiers | Tier transitions are skipped based on compiler queue load — methods may stop at Tier 1 or 2 forever if C2 is too busy |
| Tiered compilation uses more CPU than C2-only | Tiered uses slightly more CPU total (methods compiled twice), but spreads it over a longer time vs C2-only which front-loads massive compilation overhead at startup |
| A method always reaches Tier 4 if called enough | The CompilationPolicy may decide a method is "not hot enough" or the C2 queue is too loaded — stable, moderately-hot methods can live permanently at Tier 3 |
| TieredStopAtLevel=4 is the same as default | Level 4 means C1 with full profiling and C2 enabled — that IS effectively the default. Setting `TieredStopAtLevel=4` explicitly is fine but redundant |
| Tiered compilation was added in Java 8 | Tiered compilation was added in Java 7 as an experimental feature (`-XX:+TieredCompilation`) and became the default in Java 8 |
| Higher tier number = always faster | Tier 3 (C1 + full profiling) can be slightly *slower* than Tier 1 (C1 no profiling) due to instrumentation overhead — Tier 3 is the sacrifice-speed-for-data phase |

---

### 🚨 Failure Modes & Diagnosis

**Stuck at Tier 3 — Peak Performance Never Reached**

Symptom:
`PrintCompilation` shows all important methods at tier 3 but never advancing to tier 4. Throughput plateaus at 40–60% of expected peak.

Root Cause:
C2 compiler queue is saturated. The CompilationPolicy has stopped submitting new methods to C2. Common causes: too many concurrent method compilations, `CICompilerCount` too low for the number of hot methods.

Diagnostic Command / Tool:
```bash
jcmd <pid> Compiler.queue
# If C2 queue is consistently > 50 methods deep, it's overwhelmed

java -XX:+PrintCompilation 2>&1 | grep " 4 " | wc -l
# Count C2 compiled methods — if growing slowly, queue is bottlenecked
```

Fix:
```bash
java -XX:CICompilerCount=8 MyApp
# Or reduce tier 4 threshold:
java -XX:Tier4InvocationThreshold=2000 MyApp
```

Prevention:
Profile compilation queue depth in LoadTest environments. Size `CICompilerCount` proactively.

---

**Compilation Storm During Auto-Scaling**

Symptom:
New pods added by autoscaler immediately show high CPU (>80%). Application throughput is actually lower than before scaling. 

Root Cause:
Each new pod starts cold compilation simultaneously. Compilation threads compete with application threads for CPU, reducing application throughput below the equivalent of fewer, warm pods.

Diagnostic Command / Tool:
```bash
top -H -p <pid>
# Look for JIT threads (named "C1 CompilerThread" or "C2 CompilerThread")
# consuming large CPU slices
```

Fix:
Implement a warm-up delay in readiness probe: only mark pod Ready after 60 seconds of sustained traffic. Or pre-warm pods with a synthetic load script before routing traffic.

Prevention:
Add a readiness probe endpoint that checks JIT progress (e.g., confirm that a set of critical methods have been compiled via MBean metrics).

---

**Tiered Compilation Disabled Accidentally**

Symptom:
JVM starts and stays at consistent, sub-optimal throughput. `PrintCompilation` shows tier 4 compilations never appear.

Root Cause:
`-XX:-TieredCompilation` was set in the JVM startup script (or an environment variable injects it). This disables tiered compilation entirely. All compilations use C2 from scratch or not at all, depending on other flags.

Diagnostic Command / Tool:
```bash
jcmd <pid> VM.flags | grep TieredCompilation
```

Fix:
Remove `-XX:-TieredCompilation` from JVM args.

Prevention:
Document and version-control all JVM startup flags. Add automated checks that validate JVM flags match expected configuration on startup.

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**
- `JIT Compiler` — tiered compilation is a strategy built on top of the JIT compiler concept
- `C1 / C2 Compiler` — the two concrete compilers that tiered compilation orchestrates

**Builds On This (learn these next):**
- `Method Inlining` — the primary optimization C2 performs, enabled by the profiling data tiered compilation collects
- `Deoptimization` — happens when C2's assumptions from tiered profiling turn out to be wrong
- `OSR (On-Stack Replacement)` — the mechanism that allows tier transitions for methods that are *currently running* in a loop

**Alternatives / Comparisons:**
- `AOT (Ahead-of-Time Compilation)` — skips all tiers entirely by compiling before JVM start; no warmup, no adaptive optimization
- `GraalVM` — replaces C2 with a more advanced compiler; tiered compilation still applies with Graal as the Tier 4 engine

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ WHAT IT IS   │ 5-tier auto-escalating JIT strategy:      │
│              │ Interp→C1(noProf)→C1(prof)→C2            │
├──────────────┼───────────────────────────────────────────┤
│ PROBLEM IT   │ Can't have both fast startup AND peak     │
│ SOLVES       │ throughput with a single compiler config  │
├──────────────┼───────────────────────────────────────────┤
│ KEY INSIGHT  │ Tier 3 (C1 full profiling) exists solely  │
│              │ to feed rich data to C2 — it is a         │
│              │ deliberate performance sacrifice for       │
│              │ future gains                              │
├──────────────┼───────────────────────────────────────────┤
│ USE WHEN     │ Always — it is the Java 8+ default        │
├──────────────┼───────────────────────────────────────────┤
│ AVOID WHEN   │ Need instant peak without warmup → AOT    │
├──────────────┼───────────────────────────────────────────┤
│ TRADE-OFF    │ Warmup time vs peak throughput balance    │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "Five gears — the JVM shifts up           │
│              │  automatically as the road demands it"    │
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ Method Inlining → Deoptimization → OSR    │
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** Tiered Compilation includes a load-shedding mechanism that routes methods to lower tiers (1 or 2) when the C2 queue is overloaded. If a microservice starts with a burst of exactly 50,000 requests in the first 10 seconds (a Black Friday surge), and the C2 queue sheds 30% of methods to Tier 2, what is the long-term throughput impact? Specifically: will those Tier-2 methods eventually get promoted to Tier 4, and if not, what condition would need to change for them to reach C2?

**Q2.** Tiered Compilation thresholds are calibrated for typical server workloads where methods are called millions of times. Describe a workload (give a specific example type of application) where the default tiered thresholds would be actively harmful — causing significant JIT overhead with zero benefit — and explain what alternative JVM configuration would be appropriate for that workload and why.

