---
layout: default
title: "Tiered Compilation"
parent: "Java & JVM Internals"
nav_order: 299
permalink: /java/tiered-compilation/
number: "0299"
category: Java & JVM Internals
difficulty: ★★★
depends_on: JIT Compiler, C1 / C2 Compiler, Bytecode
used_by: Method Inlining, Deoptimization, GC Tuning
related: C1 / C2 Compiler, AOT (Ahead-of-Time Compilation), GraalVM
tags:
  - java
  - jvm
  - internals
  - performance
  - deep-dive
---

# 299 — Tiered Compilation

⚡ TL;DR — Tiered Compilation is the JVM strategy of automatically escalating code from interpreter → C1 → C2 as execution frequency increases, delivering fast startup and maximum throughput.

┌─────────────────────────────────────────────────────────────────────────────────┐
│ #299 │ Category: Java & JVM Internals │ Difficulty: ★★★ │
├──────────────┼──────────────────────────────────────┼──────────────────────────┤
│ Depends on: │ JIT Compiler, C1 / C2 Compiler, │ │
│ │ Bytecode │ │
│ Used by: │ Method Inlining, Deoptimization, │ │
│ │ GC Tuning │ │
│ Related: │ C1 / C2 Compiler, AOT Compilation, │ │
│ │ GraalVM │ │
└─────────────────────────────────────────────────────────────────────────────────┘

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
Before tiered compilation (pre-Java 7/8), you chose between `-client` (C1 only)
and `-server` (C2 only). `-client` programs started fast but plateaued at
70%-quality performance forever. `-server` programs hit peak performance but
suffered brutal startup latency as C2 compiled every method upfront before the
profiling data was rich. You picked your poison: either slow startup or
mediocre peak.

**THE BREAKING POINT:**
A web server deployed with `-server` (C2-only): takes 90 seconds to reach full
speed during which it handles requests at 20% of peak throughput. During those
90 seconds, auto-scaling monitors think the instance is slow and spin up
additional instances — wasting money and causing cascading resource exhaustion.
Alternatively, the same server with `-client` handles 100k req/s when it could
handle 200k req/s — hardware is being wasted at steady state.

**THE INVENTION MOMENT:**
This is exactly why **Tiered Compilation** was created: interpret briefly,
compile quickly with C1, then recompile the hottest methods with C2. Each stage
feeds the next with better data — and applications reach peak performance
within seconds rather than minutes.

---

### 📘 Textbook Definition

Tiered Compilation is a JVM execution strategy that progresses methods through
a series of compilation tiers — typically 0 (interpreter), 1–3 (C1 variants
with increasing profile instrumentation), and 4 (C2 optimized native code).
The JVM's compilation broker monitors invocation counts and back-edge counts
per method, determines the appropriate tier for each method, and schedules
compilation on background threads. Methods can move forward (hotter executionpath)
or backward (deoptimization when speculative assumptions fail). Enabled by default
since Java 8 via `-XX:+TieredCompilation`.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
Code automatically escalates from "slow but immediate" to "fast but compiled" as it gets used more.

**One analogy:**

> A city has three types of roads: dirt paths (instant to create, slow to travel),
> paved roads (built overnight, normal speed), and highways (takes weeks to build,
> very fast). The city watches which dirt paths get the most traffic, paves those
> first, and builds highways only for the most-used routes.

**One insight:**
The key insight is that the profile data gathered while code runs at a lower tier
enables better optimization at the higher tier. Without tiered compilation, C2
must compile conservatively because it has no evidence of real-world type usage.
With tiering, C1's instrumented code sends C2 a detailed map of what actually happens.

---

### 🔩 First Principles Explanation

**CORE INVARIANTS:**

1. Methods have call frequencies ranging from 0 to billions.
2. Compilation time increases with optimization depth.
3. Optimization quality increases with available profile data.
4. Profile data quality increases with execution time.
5. You cannot gather profile data without executing the method.

**DERIVED DESIGN:**
These invariants force a staged approach:

- Stage 0: Execute immediately (interpreter). Cost: slow. Benefit: gather counts.
- Stage 1–3: Quick compile with C1. Cost: low compile time. Benefit: 5–10× speedup
  over interpreter, plus richer profile data from instrumented native code.
- Stage 4: Recompile with C2 using full profile. Cost: high compile time. Benefit:
  maximum performance (2–4× better than C1, near-native speed).

The compilation broker decides tier transitions using two metrics:

- `invocation_count`: how many times the method was called
- `back_edge_count`: how many loop iterations executed (for long-running methods)

**THE TRADE-OFFS:**

- Gain: fast startup (interpreter + C1 runs immediately), peak throughput (C2).
- Cost: profiling overhead in C1-compiled code (counters, type stubs).
- Cost: Code Cache stores multiple versions of methods during transitions.
- Cost: Background CompilerThreads consume CPU and memory during warm-up.

---

### 🧪 Thought Experiment

**SETUP:**
A method `processPayment()` is called when users check out. At 9 AM Monday,
no one shops — it's called 0 times. At 10 AM it's called 50 times. At 12 PM
(lunch rush), it's called 15,000 times. At 1 PM it handles 100,000+ calls.

**WHAT HAPPENS WITHOUT TIERED COMPILATION (C2-only):**
The method sits in the compiler queue until it has enough profile data —
but without C1, no profiling stubs exist. C2 compiles it conservatively
(no type info) with a long compile time. During the lunch rush, users experience
slow response times until compilation completes.

**WHAT HAPPENS WITH TIERED COMPILATION:**
9 AM: method runs interpreted (tier 0). 10 AM: 50 calls → C1 tier 1 compiles it.
10:30 AM: 500 calls → C1 tier 3 compiles (richer profiling). 11 AM: 3,000 calls →
C2 triggers. By 12 PM when the rush hits, `processPayment` is running at fully
C2-optimized speed — silently, transparently, with zero configuration.

**THE INSIGHT:**
Tiered compilation is automatic profiling-guided optimization. The system
observes, learns, and improves continuously — matching compilation investment
to execution frequency without any manual intervention.

---

### 🧠 Mental Model / Analogy

> Think of Tiered Compilation as the express checkout system at a grocery store.
> When a new cashier (interpreter) starts, they slowly look up every item's
> price. A regular cashier (C1) knows the common items and is reasonably fast.
> The express lane (C2) handles only the most popular checkout patterns — pre-loaded
> with customers' exact shopping behaviors — and is lightning fast.

- "New cashier" → interpreter (tier 0)
- "Regular cashier" → C1 compiled code (tiers 1–3)
- "Express lane" → C2 optimised code (tier 4)
- "Popular checkout patterns" → hot methods that benefit from C2
- "Pre-loaded with customer behaviors" → type profiles from C1 instrumentation

**Where this analogy breaks down:** Unlike cashiers, a method can be "demoted"
back to a lower tier (deoptimization) if new information invalidates C2's
assumptions — no cashier gets demoted for knowing too much.

---

### 📶 Gradual Depth — Four Levels

**Level 1 — What it is (anyone can understand):**
Tiered compilation means Java starts fast and gets faster over time.
When the application starts, code runs slowly. After a few seconds, the
most-used code is converted to fast native instructions automatically.
You don't do anything — it just happens.

**Level 2 — How to use it (junior developer):**
Tiered compilation is on by default. You can disable it with
`-XX:-TieredCompilation` (rarely useful). You can stop at a specific tier
with `-XX:TieredStopAtLevel=1` (C1-only, for testing startup behavior).
Use `-XX:+PrintCompilation` to watch methods move through tiers.

**Level 3 — How it works (mid-level engineer):**
The JVM has 5 compilation levels:

- Level 0: Interpreter
- Level 1: C1, no profiling (for trivial methods)
- Level 2: C1, only invocation/back-edge counters
- Level 3: C1, full profiling (type profiles, branch profiles)
- Level 4: C2, full optimization using all profiles

The compilation broker (`CompilationBroker`) decides which tier based on
a method's counter values. Trivial short methods may jump from 0→1 or 0→4
directly. Methods in C2 compilation queue that take too long may be "stolen"
by C1 tier 3 first.

**Level 4 — Why it was designed this way (senior/staff):**
The 5-tier model emerged from empirical research showing that C3
(C1 with full instrumentation) produces the optimal trade-off between
profiling overhead and data richness for C2. Tiers 1 and 2 exist for
a specific case: to avoid paying type-profiling overhead for methods
that will never reach C2 (they're called a fixed low number of times).
The compilation broker uses a simple heuristic — "trivial" methods
(< 6 bytecodes) skip directly to tier 1, bypassing profiling. The JDK
engineers evaluated whether more tiers would help and found diminishing
returns beyond 5, with increasing complexity in the broker logic.

---

### ⚙️ How It Works (Mechanism)

```
┌────────────────────────────────────────────────────┐
│        TIERED COMPILATION — TIER TRANSITIONS       │
├────────────────────────────────────────────────────┤
│                                                    │
│  Level 0 (Interpreter)                            │
│  → method invocation counter tracking             │
│       ↓ invocations > ~2000                       │
│  Level 3 (C1 + full profiling)                    │
│  → type profiles, branch profiles recorded        │
│       ↓ invocations > ~10000 (C2 queue)           │
│  Level 4 (C2 — full optimization)                 │
│  → uses accumulated profiles for speculation      │
│                                                    │
│  SHORT-CIRCUIT PATHS:                             │
│  Trivial method → Level 1 (no profiling needed)  │
│  C2 queue full → Level 2 (partial profiling)     │
│  Deoptimization: Level 4 → Level 0              │
│                                                    │
└────────────────────────────────────────────────────┘
```

**The Compilation Broker State Machine:**
Each method has a `CompLevel` field and two counters.
The broker checks counters periodically (on method entry and loop back-edges)
and schedules compilation on the global compilation queue.

When the C2 queue is full, the broker can:

1. Compile the method at C1 tier 3 first (immediate help)
2. Then recompile with C2 when queue drains

This prevents starvation: even if C2 is busy, methods get reasonable code.

**Profile data structure in C1 tier 3:**
Each virtual call site stores a `ReceiverTypeData` that records the last 2
receiver types seen and their frequency. C2 reads this to decide whether to
devirtualize (inline) the call.

---

### 🔄 The Complete Picture — End-to-End Flow

```
┌──────────────────────────────────────────────────┐
│         TIERED COMPILATION TIMELINE              │
├──────────────────────────────────────────────────┤
│  t=0s:   JVM starts. All methods at Level 0.     │
│                                                  │
│  t=0.1s: High-frequency init methods hit         │
│          invocation threshold → C1 tier 3       │
│          ← YOU ARE HERE (startup phase)          │
│                                                  │
│  t=1–5s: Hot app paths identified. C2 queue      │
│          fills. Background CompilerThreads work. │
│          ← YOU ARE HERE (warm-up phase)          │
│                                                  │
│  t=5–30s: C2 compilations complete for major    │
│           hot paths. Performance plateaus near   │
│           theoretical maximum.                   │
│           ← YOU ARE HERE (steady state)          │
│                                                  │
│  Ongoing: Profile data updates. New code paths  │
│           may promote. Deopt events trigger      │
│           re-profiling cycles.                   │
└──────────────────────────────────────────────────┘
```

**FAILURE PATH:**
Code Cache exhaustion → C2 compilation stops → all new hot methods stay at C1 →
throughput limited to ~70% of potential. Observables: `jstat -compiler` shows
compilation count frozen; CPU on application threads increases.

**WHAT CHANGES AT SCALE:**
At 10× load, the warm-up window shrinks dramatically (thresholds reached faster).
This is beneficial. At 100× load with rolling deploys, each new pod warms up while
taking live traffic — the first few seconds of each pod's life sees elevated latency.
Traffic shaping (warm-up delay on load balancer) mitigates this.

---

### 💻 Code Example

```java
// Example 1 — Observe tier progression
// Run with: java -XX:+PrintCompilation -XX:+TieredCompilation App
// Output shows tier in column 3:
//  timestamp  id  tier  flags  method
//    89       23  3           com.App::process @ 234 bytes
//    891      23  4           com.App::process @ 234 bytes
// Method 23 promoted from tier 3 (C1) to tier 4 (C2)
```

```java
// Example 2 — Force C1-only (stop at tier 1) for startup analysis
// java -XX:TieredStopAtLevel=1 com.App
// Use to measure: how slow is the app without C2 optimization?
// Baseline for understanding C2's contribution.
```

```java
// Example 3 — Measure warm-up time in production
// Add a lifecycle listener:
@Component
public class WarmupLogger implements ApplicationListener<
    ApplicationReadyEvent> {

    private final long startTime = System.currentTimeMillis();

    @EventListener
    public void onReady(ApplicationReadyEvent event) {
        // This fires after Spring boot; JIT still warming up
        // Run a warmup request loop here:
        warmupCriticalPaths();
        long elapsed = System.currentTimeMillis() - startTime;
        log.info("App warm-up complete in {}ms", elapsed);
    }

    private void warmupCriticalPaths() {
        // Call hot endpoints/methods 10k times with synthetic data
        for (int i = 0; i < 10_000; i++) {
            criticalService.processRequest(WARMUP_PAYLOAD);
        }
    }
}
```

---

### ⚖️ Comparison Table

| Strategy             | Startup | Peak Perf  | Memory  | Best For                     |
| -------------------- | ------- | ---------- | ------- | ---------------------------- |
| **Tiered (default)** | Fast    | Maximum    | Medium  | General-purpose Java apps    |
| Interpreter-only     | Instant | Minimal    | Minimal | Tiny scripts, test isolation |
| C1-only              | Fast    | Good (70%) | Low     | Short-lived processes        |
| C2-only              | Slow    | Maximum    | High    | Legacy tuning only           |
| AOT (Native Image)   | Instant | High       | Low     | Serverless, containers       |

**How to choose:** Use default tiered compilation for all server applications.
Use AOT (GraalVM Native Image) for functions/containers where cold-start matters
more than peak throughput. Use C1-only only when debugging JIT-related issues.

---

### ⚠️ Common Misconceptions

| Misconception                                | Reality                                                                                  |
| -------------------------------------------- | ---------------------------------------------------------------------------------------- |
| Tiered compilation is a new feature          | Enabled by default since Java 8 (2014); exists since Java 7                              |
| Applications warm up once and stay warm      | Each deployment restarts the JVM — warm-up happens on every restart                      |
| You can't influence warm-up time             | You can warm up explicitly by running representative workloads before accepting traffic  |
| Tiered compilation adds significant overhead | The overhead is < 1% CPU at steady state; profiling stubs are removed when C2 takes over |
| Disabling TieredCompilation speeds things up | Almost always false; disabling it reduces both startup speed and peak throughput         |

---

### 🚨 Failure Modes & Diagnosis

**Long Warm-Up Causing SLA Violations**

Symptom:
P99 latency spikes in the first 10–30 seconds after deployment. Users experience
slow responses. Monitoring alerts trigger on latency, not errors.

Root Cause:
Critical hot paths haven't been compiled to C2 yet. Requests are served by
C1 or interpreted code at 30–70% of peak throughput.

Diagnostic Command / Tool:

```bash
# Monitor compilation activity during warm-up:
jstat -compiler <pid> 1000
# Output: Compiled  Failed  Invalid   Time   FailedType FailedMethod
#         3247       0       0        12.34   0
# Watch "Compiled" count increase during warm-up, then plateau.
```

Fix:

```java
// Implement explicit warm-up before accepting traffic:
// 1. Call critical code paths with representative synthetic data
// 2. Use load balancer health check delay (wait 30s before routing)
// 3. Or use GraalVM Native Image to eliminate warm-up entirely
```

Prevention:
Implement canary deployments — route small traffic percentage to new
pod first, wait for warm-up to complete, then shift full traffic.

---

**Compilation Oscillation**

Symptom:
`PrintCompilation` shows the same method being compiled to tier 4 then
reverting and recompiling multiple times. Throughput is unstable.

Root Cause:
Type profiles collected by C1 change over time (polymorphic call sites see
different types). C2's speculative assumptions get invalidated repeatedly —
deoptimize → re-profile → re-compile cycle.

Diagnostic Command / Tool:

```bash
java -XX:+PrintDeoptimization -XX:+PrintCompilation MyApp 2>&1 \
  | grep -E "(deoptimiz|compile|COMPILE)" | head -50
# Look for the same method appearing multiple times alternating
# between compile and deoptimize
```

Fix:
Reduce polymorphism at hot call sites. Prefer concrete types over interfaces
at performance-critical paths. Use profiling to identify the oscillating method.

Prevention:
Design hot path data types to be stable and monomorphic.

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**

- `JIT Compiler` — tiered compilation is the strategy that governs the JIT
- `C1 / C2 Compiler` — the two compilation engines that tiering coordinates
- `Bytecode` — what the compilers take as input

**Builds On This (learn these next):**

- `Method Inlining` — primary C2 optimization enabled by tiered profiling data
- `Deoptimization` — what happens when tier-4 assumptions fail
- `OSR (On-Stack Replacement)` — tier promotion can happen mid-method execution

**Alternatives / Comparisons:**

- `AOT (Ahead-of-Time Compilation)` — compiles everything before running; no tiers, no warm-up
- `GraalVM` — alternative JIT pipeline with a different tier interpretation

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ WHAT IT IS   │ 5-level compilation escalation strategy    │
├──────────────┼───────────────────────────────────────────┤
│ PROBLEM IT   │ Single-compiler JVMs: either slow startup  │
│ SOLVES       │ OR mediocre peak performance               │
├──────────────┼───────────────────────────────────────────┤
│ KEY INSIGHT  │ Lower tiers gather profile data that       │
│              │ enables better optimization at higher tiers│
├──────────────┼───────────────────────────────────────────┤
│ USE WHEN     │ Always (default) for all Java applications │
├──────────────┼───────────────────────────────────────────┤
│ AVOID WHEN   │ Almost never — unless debugging JIT issues │
├──────────────┼───────────────────────────────────────────┤
│ TRADE-OFF    │ Background compilation CPU vs peak runtime │
│              │ throughput and fast startup                │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "Fast today, faster tomorrow, fastest soon"│
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ Method Inlining → Deoptimization           │
│              │ → OSR → GraalVM                            │
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** A database connection pool library creates a proxy class per connection
using `java.lang.reflect.Proxy`. Each connection.execute() call site sees dozens
of different dynamic proxy types. The application runs 10× slower than expected
after deployment, despite good warm-up metrics. Trace exactly how tiered
compilation interacts with megamorphic virtual dispatch to cause this, and
what you would change.

**Q2.** GraalVM Native Image pre-compiles the entire application to native
code at build time — achieving instant startup at the cost of all runtime
profile-guided optimization. Given that tiered compilation's key advantage is
runtime profile data, under what specific production conditions does a static
profile collected at build time (PGO via an instrumented build) come close to
matching the quality of JVM tiered compilation's runtime profiles? What class
of workloads does this argument fail for?
