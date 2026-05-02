---
layout: default
title: "C1 / C2 Compiler"
parent: "Java & JVM Internals"
nav_order: 298
permalink: /java/c1-c2-compiler/
number: "0298"
category: Java & JVM Internals
difficulty: ★★★
depends_on: JIT Compiler, Bytecode, Tiered Compilation
used_by: Tiered Compilation, Method Inlining, Deoptimization
related: Tiered Compilation, GraalVM, OSR (On-Stack Replacement)
tags:
  - java
  - jvm
  - internals
  - performance
  - deep-dive
---

# 298 — C1 / C2 Compiler

⚡ TL;DR — C1 compiles fast but shallow; C2 compiles slow but produces near-optimal native code — together they give Java fast startup AND peak performance.

┌─────────────────────────────────────────────────────────────────────────────────┐
│ #298 │ Category: Java & JVM Internals │ Difficulty: ★★★ │
├──────────────┼──────────────────────────────────────┼──────────────────────────┤
│ Depends on: │ JIT Compiler, Bytecode, │ │
│ │ Tiered Compilation │ │
│ Used by: │ Tiered Compilation, Method Inlining, │ │
│ │ Deoptimization │ │
│ Related: │ Tiered Compilation, GraalVM, │ │
│ │ OSR (On-Stack Replacement) │ │
└─────────────────────────────────────────────────────────────────────────────────┘

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
Early JIT compilers had to make a binary choice: compile fast (so startup is snappy)
or compile well (so steady-state is optimal). The fast compiler produced mediocre
code; the slow compiler delayed startup by seconds while it performed deep analysis.
Server applications started slowly. Interactive applications felt sluggish during
the compilation phase. No single compiler could satisfy both requirements.

**THE BREAKING POINT:**
A large enterprise application boots in 45 seconds, and 30 of those are the JIT
compiler performing deep, expensive optimization on every method at startup — even
methods that only run once during initialization. Meanwhile, a web application uses
the fast compiler and runs at 60% of theoretical throughput forever because the
compiler never performs the heavy optimizations that could unlock peak speed.

**THE INVENTION MOMENT:**
This is exactly why two separate compilers — **C1** and **C2** — were created.
C1 handles fast, lightweight compilation for startup and short-lived code. C2
takes over for truly hot code and applies the full arsenal of aggressive
optimizations. Together, they deliver both fast startup and maximum throughput.

---

### 📘 Textbook Definition

C1 (the Client Compiler) and C2 (the Server Compiler) are two distinct JIT
compiler tiers within the HotSpot JVM. C1 performs a fast, limited compilation
pass that produces decent native code quickly, minimizing latency from bytecode
to compiled execution. C2 performs a slow, deeply-optimizing compilation that
can take 10–100× longer than C1 but produces near-optimal native code using
aggressive techniques including speculative inlining, loop transformations, and
escape analysis. In modern JVMs, they operate in a tiered compilation strategy
where C1 compiles first, then C2 recompiles the hottest methods with full
optimization.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
C1 is the fast-but-mediocre compiler; C2 is the slow-but-excellent compiler.

**One analogy:**

> When you hire a contractor to renovate your kitchen, the first crew does a
> "good enough" job quickly — you can use the kitchen immediately. Later, a
> specialist comes back for the 3% that gets used every day (the main cabinet,
> the stove area) and makes it perfect. You don't wait for perfection before
> you can cook.

**One insight:**
C2 would not be valuable without C1. Without C1, you'd wait for C2 to compile
every method before running — which defeats the point of JIT. C1 keeps the JVM
responsive while C2 works on the truly hot methods. The two compilers have
different internal IRs, different optimization passes, and are completely separate
codebases in OpenJDK.

---

### 🔩 First Principles Explanation

**CORE INVARIANTS:**

1. Compilation time is proportional to optimization depth.
2. Optimization quality is proportional to profile data richness.
3. Most methods are called few times — deep optimization wastes time on them.
4. A small fraction of methods (hot methods) execute billions of times — they
   deserve every optimization available.

**DERIVED DESIGN:**
Given invariant 3 and 4, we need two distinct compilation strategies:

- For most methods: compile fast, accept 70%-quality output. (C1)
- For hot methods: compile slowly, accept 5× compilation time for near-100% output. (C2)

C1 builds a simple CFG (Control Flow Graph) IR, performs basic optimizations
(constant folding, basic inlining), and emits native code. Compilation in ~0.1ms.

C2 builds a rich "sea of nodes" IR, performs full escape analysis, aggressive
speculative inlining (using type profiles), loop unrolling, vectorization
(SIMD), and register allocation. Compilation in 10–100ms but produces code
that runs 2–4× faster than C1's output.

**THE TRADE-OFFS:**

- C1: Gain: fast-to-native transition. Cost: non-optimal code.
- C2: Gain: near-optimal native code. Cost: long compilation time, higher memory.
- Together: Gain: fast startup AND peak throughput. Cost: complexity of managing
  two compiler tiers, profiling instrumentation in C1-compiled code.

---

### 🧪 Thought Experiment

**SETUP:**
An application has 10,000 methods. On startup, all 10,000 are called at least once.
During steady-state operation, 50 methods execute 99% of the total CPU time.

**WHAT HAPPENS WITHOUT C1/C2 SPLIT (C2 only):**
At startup, C2 must compile all 10,000 methods. At 50ms per method, that's
500 seconds of compilation before full speed is reached. The application is
unusable for 8 minutes. Worse, C2 wasted ~9,950 compilations on methods that
will never be hot.

**WHAT HAPPENS WITH C1/C2:**
At startup, C1 compiles all 10,000 methods in ~1 second total (0.1ms each).
Application is immediately responsive. In the background, profiling data reveals
the 50 hot methods. C2 recompiles just those 50 — 50 × 50ms = 2.5 seconds.
After 3–5 seconds, all hot methods run at C2-optimized speed.

**THE INSIGHT:**
The compilation budget is won by targeting investment. C1 is cheap insurance —
it covers everything at low cost. C2 is precision surgery — it optimises exactly
what matters.

---

### 🧠 Mental Model / Analogy

> Think of C1 and C2 as two copy editors on a newspaper. The first editor (C1)
> does a fast pass — fixes obvious typos, checks major facts, approves for print.
> Articles are published quickly. The second editor (C2) takes the five most-read
> articles from last week and rewrites them for maximum clarity, precision, and
> impact — they'll be reprinted thousands of times, so perfection pays off.

- "Fast pass for all articles" → C1 compiles all methods quickly
- "Five most-read articles" → the hot methods that C2 targets
- "Rewrite for perfection" → C2's deep optimization pass
- "Published quickly" → application starts and runs without waiting for C2
- "Reprinted thousands of times" → hot methods execute millions of times,
  making C2's investment worthwhile

**Where this analogy breaks down:** Unlike copy editors, C1 leaves profiling
instrumentation in its output — so it actively helps C2 by collecting data
while executing. C1 and C2 are cooperative, not independent.

---

### 📶 Gradual Depth — Four Levels

**Level 1 — What it is (anyone can understand):**
HotSpot has two compilers inside it. The first one (C1) is like a quick-and-dirty
translator — fast but good enough. The second (C2) is like a perfectionist who
takes their time — but produces the most optimized code possible.

**Level 2 — How to use it (junior developer):**
Both compilers are automatic. You can force C2-only with the `-server` JVM flag
(default on modern JVMs) or C1-only with `-client`. For performance tuning,
prefer the default Tiered Compilation (`-XX:+TieredCompilation`) which uses both.
You can observe which compiler produced each method with `-XX:+PrintCompilation`.

**Level 3 — How it works (mid-level engineer):**
C1 uses a Linear Scan register allocator and a simple HIR (high-level IR).
It instruments its output with method invocation counters and type-profile
recording stubs. C2 uses a "sea of nodes" IR (a program dependence graph where
nodes are computations and edges are dependencies), global value numbering,
aggressive inlining, loop transformations, and a Graph Coloring register allocator.
C2's output can be 2–4× faster than C1's, but compilation takes 10–100× longer.

**Level 4 — Why it was designed this way (senior/staff):**
C1 and C2 share no compiler IR — they were designed by different teams with
different goals. The split was a deliberate architectural decision: shared IRs
create coupling that limits each compiler's optimization opportunities. C2's
"sea of nodes" IR is unusual — most compilers use CFG-based IRs. The sea-of-nodes
design enables global optimizations that CFG-based IRs struggle with, at the cost
of being extremely difficult to read and debug (even JVM engineers call it a
"write-only" IR). GraalVM's JIT (written in Java) replaces C2 with a more
maintainable IR while targeting the same optimization quality.

---

### ⚙️ How It Works (Mechanism)

```
┌────────────────────────────────────────────────┐
│       C1 vs C2 — COMPILATION PIPELINE         │
├─────────────────────────┬──────────────────────┤
│ C1 (Client Compiler)    │ C2 (Server Compiler) │
├─────────────────────────┼──────────────────────┤
│ Input: Bytecode         │ Input: Bytecode +     │
│                         │ runtime profile data  │
│ IR: Simple HIR          │ IR: Sea of Nodes      │
│                         │                       │
│ Optimizations:          │ Optimizations:        │
│  - Basic inlining       │  - Aggressive inlining│
│  - Constant folding     │  - Escape analysis    │
│  - Dead code removal    │  - Loop unrolling     │
│  - Linear scan alloc    │  - Vectorization      │
│                         │  - GVN / LICM         │
│                         │  - Graph Coloring     │
│ Compilation: ~0.1ms     │ Compilation: ~10ms    │
│ Code quality: 70%       │ Code quality: ~95%    │
└─────────────────────────┴──────────────────────┘
```

**Profiling instrumentation in C1 output:**
C1-compiled code is not "clean" native code — it contains counters and stubs:

```
// Every C1-compiled call site has a type recording stub:
// Before: virtualcall Transformer::transform
// C1 adds:  if (type != lastSeenType) { recordNewType(type); }
//           lastSeenType = type
//           call transform
// This profile feeds C2's speculative inlining
```

**C2's sea-of-nodes IR:**
Unlike a CFG where basic blocks are nodes, in C2's IR, individual operations
are nodes. Control flow edges and data flow edges are explicit. This allows
global optimizations that cross basic-block boundaries — e.g., hoisting an
invariant computation out of a deeply nested loop by tracing data dependencies
rather than analyzing control flow.

---

### 🔄 The Complete Picture — End-to-End Flow

```
┌────────────────────────────────────────────────┐
│        TIERED COMPILATION TIMELINE             │
├────────────────────────────────────────────────┤
│  t=0: Class loaded                             │
│       ↓                                        │
│  t=0–50ms: Interpreter                         │
│  (counts invocations, records types)           │
│       ↓ threshold: ~2000 calls                 │
│  t=50ms: C1 compiles → YOU ARE HERE           │
│  (fast native code with profiling stubs)       │
│       ↓ C1 code runs, profile accumulates      │
│  t=500ms+: C2 compiles → YOU ARE HERE         │
│  (slow, using C1-gathered profiles)            │
│       ↓                                        │
│  t=1s+: C2-optimised code running             │
│  (maximum performance, stubs removed)          │
└────────────────────────────────────────────────┘
```

**FAILURE PATH:**
C2 compilation thread crashes (OOM, bug) → method falls back to C1 code →
`-XX:+PrintCompilation` shows `COMPILE PROHIBITED` → throughput drops to C1 level
(~70% of optimal) without complete failure.

**WHAT CHANGES AT SCALE:**
At 1000× load, C2 compilation queue grows — CompilerThreads become a bottleneck.
JVM may add compilation threads automatically. Under memory pressure, Code Cache
may evict C2-compiled code, forcing re-compilation. Profiling overhead in C1-compiled
code is measurable at extreme message throughput (millions/sec).

---

### 💻 Code Example

```java
// Example 1 — Force specific compilation tier via flags
// C1 only (no C2 — fast startup, lower peak):
// java -XX:TieredStopAtLevel=1 MyApp

// C2 only (slow startup, max peak):
// java -XX:-TieredCompilation -server MyApp

// Default (C1 then C2 — best of both):
// java MyApp  (TieredCompilation is ON by default)
```

```java
// Example 2 — Observe compilation tiers in output
// Run with: java -XX:+PrintCompilation MyApp
// Output format:
//  timestamp  id  tier  method              size
//    121       42  3     com.Foo::compute    (25 bytes)  ← C1 (tier 3)
//    892       42  4     com.Foo::compute    (25 bytes)  ← C2 (tier 4)
// Tier 3 = C1 with full profile; Tier 4 = C2 compiled
```

```java
// Example 3 — Prevent C2 from wasting time on trivial methods
// Use @ForceInline (JDK internal) or trust JIT's size threshold
// Methods > 325 bytes (default) won't be inlined by C2
// Avoid bloated hot methods — refactor large methods to enable
// C2 inlining:

// BAD: large method can't be inlined by C2
public void processAll() {
    // 500+ lines of code...
}

// GOOD: extract hot inner path to small, inlinable method
public void processAll() {
    for (Item item : items) {
        processSingle(item); // C2 will inline this
    }
}
private void processSingle(Item item) {
    // 20 lines max — C2 inlines this at call site
}
```

---

### ⚖️ Comparison Table

| Compiler        | Compile Time | Code Quality | Profile Use          | Best For                     |
| --------------- | ------------ | ------------ | -------------------- | ---------------------------- |
| **C1 (Client)** | ~0.1ms       | 70%          | Gathers profiles     | Startup, short-lived methods |
| **C2 (Server)** | ~10–100ms    | 95%+         | Consumes profiles    | Long-running hot methods     |
| Interpreter     | 0ms          | 5%           | Gathers basic counts | Very cold methods            |
| GraalVM JIT     | ~10–50ms     | 97%          | Full profiling       | Graal-native workloads       |

**How to choose:** Default tiered compilation (`C1→C2`) is correct for almost all
Java applications. Override only when profiling reveals C2 compilation threads
are a bottleneck (extremely rare) or you need minimized memory footprint.

---

### ⚠️ Common Misconceptions

| Misconception                                           | Reality                                                                                              |
| ------------------------------------------------------- | ---------------------------------------------------------------------------------------------------- |
| C1 and C2 are the same compiler with different settings | They are completely separate codebases with different IRs and optimization pipelines                 |
| C2 always replaces C1 for a method                      | C2 recompiles only the hottest tier-3 (C1) methods; most methods stay at C1 forever                  |
| `-server` flag activates C2 only                        | On modern 64-bit JVMs, tiered compilation (C1+C2) is the default; `-server` is an alias to prefer C2 |
| C1 output doesn't affect C2 quality                     | C1 output includes profiling stubs that record type information C2 uses for speculative optimization |
| C2 is obsolete now that GraalVM exists                  | C2 is the default JIT in all OpenJDK distributions; GraalVM requires a separate JVM                  |

---

### 🚨 Failure Modes & Diagnosis

**C2 Compilation Queue Buildup**

Symptom:
Application throughput is below theoretical peak. CPU usage on
`CompilerThread` threads is high. JIT warm-up takes longer than expected.

Root Cause:
Too many hot methods need C2 compilation simultaneously, but compiler threads
are limited. Common in large applications with many warm paths.

Diagnostic Command / Tool:

```bash
jcmd <pid> Compiler.queue
# Lists methods currently queued for compilation
# or:
-XX:+PrintCompilation | grep "queued"
```

Fix:

```bash
# Increase compiler threads (default is usually adequate)
-XX:CICompilerCount=4  # default: proportional to CPU count
# Or limit what C2 targets:
-XX:CompileThreshold=15000  # raise threshold, fewer C2 targets
```

Prevention:
Profile compilation activity in staging with representative load before production.

---

**C2 Crash / Compilation Abort**

Symptom:
Log shows `C2 compiler detected fatal error in: ...` or method shows
`COMPILE PROHIBITED` in PrintCompilation output. Method runs at C1 speed
forever.

Root Cause:
C2 encountered an internal assertion failure or OOM in the compiler thread.
Rare but possible with complex bytecode or JVM bugs.

Diagnostic Command / Tool:

```bash
# Enable verbose crash info:
-XX:+CrashOnOutOfMemoryError
-XX:ErrorFile=/tmp/jvm_crash_%p.log
# Review hs_err_pid<N>.log for C2 backtrace
```

Fix:
Update JVM to latest patch. If bug is reproducible, report to OpenJDK with
reproduction case. Workaround: exclude specific method from C2:

```bash
-XX:CompileCommand=exclude,com/example/Foo.problematicMethod
```

Prevention:
Stay current with JVM patch releases; C2 bugs are usually fixed promptly.

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**

- `JIT Compiler` — C1 and C2 are the two JIT compiler implementations; JIT is the parent concept
- `Bytecode` — both compilers take bytecode as input
- `JVM` — C1 and C2 are internal JVM subsystems

**Builds On This (learn these next):**

- `Tiered Compilation` — the strategy coordinating when C1 vs C2 is used
- `Method Inlining` — the most impactful C2 optimization
- `Deoptimization` — what happens when C2's speculative assumptions are violated
- `OSR (On-Stack Replacement)` — C2 can replace C1-compiled code mid-execution

**Alternatives / Comparisons:**

- `GraalVM` — alternative JIT written in Java; replaces C2 with a maintainable, pluggable compiler
- `AOT (Ahead-of-Time Compilation)` — compiles before running; no warm-up period

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ WHAT IT IS   │ Two JIT compilers: C1 (fast) + C2 (deep)  │
├──────────────┼───────────────────────────────────────────┤
│ PROBLEM IT   │ No single compiler delivers fast startup   │
│ SOLVES       │ AND peak throughput simultaneously         │
├──────────────┼───────────────────────────────────────────┤
│ KEY INSIGHT  │ C1 also collects the profile data that     │
│              │ enables C2's speculative optimizations     │
├──────────────┼───────────────────────────────────────────┤
│ USE WHEN     │ Default: always; no explicit selection     │
│              │ needed unless tuning compilation threads   │
├──────────────┼───────────────────────────────────────────┤
│ AVOID WHEN   │ Memory-constrained environments where JIT  │
│              │ overhead is unacceptable (use AOT instead) │
├──────────────┼───────────────────────────────────────────┤
│ TRADE-OFF    │ Compilation CPU overhead vs peak runtime   │
│              │ performance                                │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "C1 is the scout; C2 is the sniper"        │
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ Tiered Compilation → Method Inlining       │
│              │ → Deoptimization → GraalVM                 │
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** A microservice is deployed in a Kubernetes cluster with a 15-second
liveness probe timeout. During startup, C2 compilation of framework-heavy Spring
Boot code takes 12 seconds. The liveness probe kills the pod before the
application is healthy. What is the exact mechanism causing this, and what are
three distinct approaches to fix it — ranging from JVM-level to architecture-level?

**Q2.** C2's "sea of nodes" IR enables optimizations that CFG-based IRs cannot
perform easily, yet it is notoriously difficult to read and maintain — even
experienced JVM engineers describe it as nearly write-only. GraalVM replaced C2
with a more conventional IR and achieved comparable or better performance. What
does this imply about the relationship between IR expressiveness and optimization
quality? When is unconventional IR design worth the engineering complexity cost?
