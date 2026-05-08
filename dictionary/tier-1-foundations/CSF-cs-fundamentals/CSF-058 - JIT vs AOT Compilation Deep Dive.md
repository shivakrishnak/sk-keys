---
id: CSF-058
title: JIT vs AOT Compilation Deep Dive
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
  - production
  - deep-dive
status: draft
version: 1
layout: default
parent: "CS Fundamentals - Paradigms"
grand_parent: "Technical Dictionary"
nav_order: 58
permalink: /csf/jit-vs-aot-compilation-deep-dive/
---

# CSF-058 - JIT vs AOT Compilation Deep Dive

⚡ TL;DR - JIT compilation profiles runtime behaviour to generate highly optimised code adaptively; AOT compiles ahead of time for deterministic startup and performance; the right choice depends on whether adaptive optimisation or startup latency matters more.

| CSF-058         | Category: CS Fundamentals - Paradigms | Difficulty: ★★★ |
| :-------------- | :------------------------------------ | :-------------- |
| **Depends on:** | CSF-023, CSF-050, CSF-055             |                 |
| **Used by:**    | CSF-062, CSF-070                      |                 |
| **Related:**    | CSF-055, CSF-062, CSF-070             |                 |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
The original choice: interpreted or compiled. Interpreted:
flexible, easy, but 10-100x slower (Python). Compiled:
fast, but no runtime adaptability and long build times (C).
Java's original design (1995) attempted a middle path: compile
once to bytecode (portable), run everywhere with JIT.

**THE BREAKING POINT:**
Java's first JVMs in the 1990s were slow: interpreted bytecode.
C-programmers dismissed Java as unusable for performance.
HotSpot JVM (1999) introduced tiered JIT compilation: the JVM
profiled hot methods and compiled them to native machine code.
Java benchmarks suddenly competed with C++. The myth
"Java is slow" became outdated.

**THE INVENTION MOMENT:**
JIT compilation (John Aycock coined the term, but the technique
predates him): compile bytecode to native code at runtime,
using runtime profiling to make optimisations impossible at
static compile time (branch probabilities, virtual call
targets, object shapes). The JVM's tiered compilation (C1 then
C2) balances compile speed vs quality.

**EVOLUTION:**
GraalVM (2018+) provides both: JIT (as HotSpot replacement)
and AOT (native image for serverless). LLVM provides AOT
for C/C++/Rust. Clang's PGO (Profile-Guided Optimisation)
applies runtime profile data to AOT compilation, blurring
the boundary. The debate continues.

---

### 📘 Textbook Definition

**AOT (Ahead-Of-Time) compilation**: source code is fully
compiled to native machine code before execution. The binary
contains native instructions for the target architecture.
Examples: GCC, Clang, Rust `rustc`, Go `go build`.

**JIT (Just-In-Time) compilation**: code is compiled to
intermediate form (bytecode), then compiled to native machine
code during execution, after profiling identifies hot paths.
Examples: JVM HotSpot, V8 (JavaScript), CLR (.NET),
PyPy (Python JIT).

---

### ⏱️ Understand It in 30 Seconds

**One line:**
AOT compiles everything upfront for consistent startup; JIT compiles hot paths at runtime using profiling data to optimise what actually matters.

**One analogy:**

> AOT is like a chef who prepares all dishes before the
> restaurant opens: consistent service time, but they
> guessed what dishes would be ordered. JIT is like a chef
> who starts cooking when you order, but has studied which
> dishes are most popular and pre-heats ingredients
> for those — the first order takes longer but subsequent
> orders are faster than the AOT chef for popular dishes.

**One insight:**
JIT's key advantage: it knows which code paths are _actually_
hot in _this specific deployment_. AOT must conservatively
optimise all paths. JIT can optimise the 10% that runs 90%
of the time with profile-specific optimisations impossible
for AOT.

---

### 🔩 First Principles Explanation

**CORE INVARIANTS:**

1. Interpretation: execute bytecode instruction by instruction; no compilation; lowest throughput.
2. JIT: profile, then compile hot methods to native; adaptive to actual runtime behaviour.
3. AOT: compile entire program to native at build time; conservative optimisations; deterministic.
4. Profiling enables: inlining, devirtualisation, branch prediction, escape analysis.
5. Warm-up time: JIT needs N method invocations before compiling (JVM: ~10,000 by default).

**DERIVED DESIGN:**

- **C1 compiler (client)**: JVM's fast, lightly-optimised JIT; used for short-lived methods
- **C2 compiler (server)**: JVM's optimising JIT; triggered after profiling threshold
- **Deoptimisation**: when assumptions are invalidated (a new class is loaded), JIT falls back to interpreted
- **Escape analysis**: if object doesn't escape a method, allocate on stack (no GC needed)
- **Inlining**: replace virtual calls with direct calls based on observed types

**THE TRADE-OFFS:**
**JIT:** Peak throughput can exceed AOT; long startup; harder to profile (timing varies).
**AOT:** Deterministic startup; consistent P99; no warm-up; limited adaptive optimisation.

**ESSENTIAL vs ACCIDENTAL COMPLEXITY:**
**Essential:** Runtime profiling data enables optimisations impossible at static compile time.
**Accidental:** JVM warm-up time in serverless (solved by GraalVM native image).

---

### 🧪 Thought Experiment

**SETUP:**
Polymorphic call: `animal.speak()` where `Animal` is an
interface with 10 implementations.

**AOT (conservative):**

```
Compiler must handle all 10 implementations:
  -> virtual dispatch table lookup at every call
  -> cannot inline (don't know target at compile time)
  -> branch predictor sees variable targets
  -> worst case: 10-20 ns per call
```

**JIT (profile-guided):**

```
After profiling: 99% of calls are to Dog.speak()
  -> JIT emits:
     if (animal instanceof Dog) { // inline Dog.speak() }
     else { virtual dispatch fallback }
  -> Branch prediction: Dog case predicted
  -> No virtual dispatch in common case
  -> 2-3 ns per call for the hot path
  -> Deoptimise if new Animal implementation loaded
```

**THE INSIGHT:**
JIT's adaptive inlining beats AOT for polymorphic code
when there's a dominant type in practice. This is why
Java benchmarks can match C++ for server workloads.

---

### 🧠 Mental Model / Analogy

> JIT is like a racing driver who adjusts their driving style
> mid-race based on what they observe: which corners the
> competitors take too wide, which straights to use for
> overtaking. AOT is like a race strategist who analyses
> historical data before the race and gives a fixed strategy.
> The JIT driver can adapt; the AOT strategist can only
> use pre-race data. For long races (server workloads), the
> adaptive driver wins. For sprint races (short-lived processes),
> there's no time to adapt.

**Element mapping:**

- Race = workload execution
- Observing mid-race = runtime profiling
- Adjusting driving style = JIT recompilation
- Pre-race analysis = AOT profile-guided optimisation (PGO)
- Sprint race = serverless function (short-lived)

Where this analogy breaks down: JIT's "observation" is measured
in method invocations (counted by hardware counters), not time.

---

### 📶 Gradual Depth - Four Levels

**Level 1 - What it is (anyone can understand):**
AOT compiles your code completely before you run it (like
baking a cake before the party). JIT compiles parts of your
code while it's running, focusing on the parts used most
(like cooking the most popular dishes as orders come in).

**Level 2 - How to use it (junior developer):**
For Java services: use the default JVM (JIT) for long-running
services. For Lambda/Cloud Functions: use GraalVM native image
(`-Pnative` in Spring Boot) to eliminate 1-2s cold start.
For Go: AOT by default; fast startup; good for CLIs and
short-lived containers. For Rust: AOT by default; no warm-up.

**Level 3 - How it works (mid-level engineer):**
JVM tiered compilation: Level 0 (interpreted) -> Level 1-3 (C1)
-> Level 4 (C2). Each level adds more profiling data and
better optimisation. C2 applies: escape analysis (stack
allocation), loop unrolling, SIMD vectorisation, speculative
inlining with deoptimisation guards. JFR can capture
compilation events to see which methods are JIT-compiled.

**Level 4 - Why it was designed this way (senior/staff):**
GraalVM's key insight: the JIT compiler itself can be run
in AOT mode (compiling the Truffle interpreter AOT). GraalVM
native image uses a _closed-world assumption_: all classes
reachable from the entry point are compiled. This enables AOT
compilation of Java programs that normally require dynamic
class loading. The trade-off: no runtime class loading, limited
reflection. GraalVM Enterprise solves this by using runtime
profile data as input to native image compilation (PGO for Java).

**Expert Thinking Cues:**

- JVM warm-up: how many requests before JIT fully kicks in? Typically 5,000-100,000 invocations.
- JIT deoptimisation: after adding a new class implementing an interface, previously JIT-inlined virtual calls are deoptimised. Watch for performance cliff.
- `-XX:+PrintCompilation`: log JVM JIT compilation events; see which methods reach C2.

---

### ⚙️ How It Works (Mechanism)

**JVM compilation pipeline:**

```
Source code -> javac -> .class (bytecode) -> JVM
JVM runtime:
  1. Interpret bytecode (Level 0)
  2. After 2000 invocations: C1 compile (Level 3)
     -> simple optimisations; profiling inserted
  3. After 15000 invocations: C2 compile (Level 4)
     -> full optimisation: inlining, escape analysis, SIMD
C2 output: native machine code (x86/ARM)
```

**GraalVM native image (AOT):**

```bash
# Build Spring Boot native image
mvn -Pnative native:compile
# AOT: reachability analysis -> compile to native binary
# Result: ./target/myapp (no JVM required)
# Startup: 50ms instead of 2s
# Peak throughput: ~80% of JIT (no runtime profiling)
```

**JFR: watch JIT compilation:**

```bash
java -XX:+FlightRecorder \
  -XX:StartFlightRecording=duration=60s,filename=jit.jfr \
  myapp.jar
# Open jit.jfr in JDK Mission Control
# Filter: Compiler -> View compiled methods + inlining depth
```

---

### 🔄 The Complete Picture - End-to-End Flow

**NORMAL FLOW (JVM JIT):**

```
Service starts (cold):               ← YOU ARE HERE
  | Bytecode interpreted (slow)
  | Method invocation counters grow
  | C1 compiles hot methods (5ms per method)
  | C2 compiles hottest methods (50ms per method)
Warm state (after ~1min under load):
  | All hot paths JIT-compiled to native
  | Performance: near-native
  | GC: still pauses (separate concern)
Deoptimisation event:
  | New class implementing hot interface loaded
  | C2-compiled inlined call invalidated
  | Method de-compiled; re-profiled; re-compiled
  | Performance dip of ~100ms, then recovers
```

**FAILURE PATH:**

- JVM never warms up: serverless function killed before reaching C2 threshold
- Deoptimisation storm: many class loads cause repeated deoptimisation
- AOT: reflection not configured -> `ClassNotFoundException` at runtime

---

### ⚖️ Comparison Table

| Dimension       | AOT (Rust, Go, GraalVM native) | JIT (JVM HotSpot, V8)  |
| --------------- | ------------------------------ | ---------------------- |
| Startup         | Fast (ms)                      | Slow (s for JVM)       |
| Warm throughput | High (static optimisation)     | Very high (adaptive)   |
| Cold throughput | Same as warm                   | Low until warm         |
| GC pauses       | None (Rust/Go) or low (Go)     | GC-dependent (JVM)     |
| Adaptability    | None (fixed at compile time)   | High (profile-guided)  |
| Binary size     | Larger (all code included)     | Smaller bytecode + JVM |
| Best for        | Serverless, CLIs, systems      | Long-running services  |

---

### ⚠️ Common Misconceptions

| Misconception                           | Reality                                                                                      |
| --------------------------------------- | -------------------------------------------------------------------------------------------- |
| "Java is slow because it's interpreted" | Modern JVM is JIT-compiled; peak throughput matches C++ for many workloads                   |
| "JIT always beats AOT"                  | For short-lived processes (serverless), AOT wins; JIT never reaches peak performance         |
| "GraalVM native image is always better" | Loses JIT adaptive optimisation; ~10-20% lower peak throughput for long-running services     |
| "AOT compilation = no optimisation"     | LLVM, GCC, and rustc apply extensive AOT optimisations; PGO adds profile guidance            |
| "JIT compilation is free"               | JIT compilation itself consumes CPU at startup; compilation threads compete with application |

---

### 🚨 Failure Modes & Diagnosis

**Mode 1: JVM Never Warms Up (Serverless)**
**Symptom:** Function P99 is consistently high; no performance improvement over time.
**Root Cause:** Serverless function scales to zero; each cold start never warms up.
**Fix:** GraalVM native image; or provision minimum instances (`minInstances=1`).

**Mode 2: Deoptimisation Storm**
**Symptom:** Periodic performance dip after deployment; methods re-compiled repeatedly.
**Root Cause:** Application or framework loading many new classes post-startup.
**Diagnostic:**

```bash
java -XX:+PrintCompilation 2>&1 | grep made_not_entrant
# Lines with 'made_not_entrant' = deoptimised methods
```

**Fix:** Warm up JVM under controlled load after deployment before routing production traffic.

**Mode 3: GraalVM Native Image Reflection Error**
**Symptom:** `ClassNotFoundException` or `MethodNotFoundException` at runtime with native image.
**Root Cause:** Reflection not registered in `reflect-config.json`.
**Fix:** Add to `src/main/resources/META-INF/native-image/reflect-config.json`.

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**

- [[CSF-023 - Stack vs Heap Memory]]
- [[CSF-055 - Language Performance Trade-offs]]

**Builds On This (learn these next):**

- [[CSF-062 - Language Runtime Internals]]
- [[CSF-070 - Compiler/Runtime Selection at Scale]]

**Alternatives / Comparisons:**

- Profile-Guided Optimisation (PGO) for AOT compilers
- V8 TurboFan (JavaScript JIT)

---

### 📌 Quick Reference Card

```
┌─────────────────────────────────────────────────────┐
│ WHAT IT IS      JIT: compile at runtime using profiling; │
│                 AOT: compile before execution          │
│ PROBLEM         Interpreted is slow; AOT can't adapt   │
│ IT SOLVES       JIT bridges throughput + adaptability  │
│ KEY INSIGHT     JIT uses what actually runs; AOT must   │
│                 conservatively handle all paths        │
│ USE WHEN        JIT: long-running server; AOT: serverless│
│ AVOID WHEN      JIT in serverless (no warm-up time)    │
│ TRADE-OFF       JIT: peak throughput; AOT: startup + P99│
│ ONE-LINER       JIT profiles then optimises; AOT is    │
│                 done before runtime                   │
│ NEXT EXPLORE    CSF-062, GraalVM native image, JFR      │
└─────────────────────────────────────────────────────┘
```

**If you remember only 3 things:**

1. JIT compiles hot paths at runtime using profiling; AOT compiles everything before execution.
2. JIT wins for peak throughput of long-running services; AOT wins for startup time and serverless.
3. GraalVM native image is Java AOT; solves the cold-start problem at the cost of adaptive optimisation.

**Interview one-liner:**
"JIT compilation defers compilation to runtime, using profiling to apply adaptive optimisations impossible at static compile time; AOT provides deterministic startup and P99 latency; modern systems (GraalVM) combine both to match workload requirements."

---

### 💎 Transferable Wisdom

**Reusable Engineering Principle:**
Adaptive systems outperform static systems when the distribution
of operations is non-uniform and changes over time. JIT wins
over AOT for server workloads for the same reason a caching
proxy wins over serving from origin: most requests are for
a small set of hot resources that can be optimised adaptively.

**Where else this pattern appears:**

- **Database query planner** — adaptive query planning (PostgreSQL parallel query)
- **CDN edge caching** — cache popular content; serve origin for long-tail
- **HTTP/2 server push** — proactively push resources the server predicts the client needs

---

### 💡 The Surprising Truth

V8, Node.js's JavaScript engine, performs a compilation step
that most developers don't know about: it deoptimises
functions that change their type profile. If a JavaScript
function handles both integers and objects at different times,
V8 generates an optimised version for integers, then
deoptimises when it encounters an object. "Type-stable"
JavaScript — functions that always receive the same types —
runs at near-native speed. "Type-unstable" JavaScript triggers
constant recompilation. This is why TypeScript (which enforces
type stability) can lead to faster JavaScript — not because
of its types themselves, but because they enforce the
conditions V8 needs for optimal JIT.

---

### 🧠 Think About This Before We Continue

**Q1 (System Interaction):** A Spring Boot service uses Hibernate
for ORM. Hibernate generates bytecode at runtime (proxy classes)
for lazy loading. What problem does this cause when compiling
the service to a GraalVM native image, and how is it resolved?

_Hint:_ GraalVM native image uses the closed-world assumption:
only classes known at build time are compiled. Runtime-generated
bytecode (Hibernate proxies) can't be predicted. Research
Spring's AOT processing and how it pre-generates proxies.

**Q2 (Scale):** A JVM microservice receives 10,000 RPS. Each
request uses a different code path through a large switch
statement (50 cases). The JIT's inlining budget is limited.
How does this affect JIT optimisation, and what code-level
changes could help the JIT?

_Hint:_ JIT inlining has a budget (bytecode size limit).
With 50 equally-used branches, no single path is "hot enough"
for aggressive optimisation. Research method inlining thresholds
and how to measure them.

**Q3 (Design Trade-off):** Kotlin compiles to JVM bytecode
and benefits from JIT. Kotlin also compiles to Kotlin/Native
(AOT). A team is deciding: should they use JVM-Kotlin or
Native-Kotlin for their low-latency API?

_Hint:_ Kotlin/Native currently has no JIT; performance is
AOT-limited. JVM Kotlin benefits from JIT optimisation and
has the broader library ecosystem. When would Kotlin/Native's
no-GC model outweigh JVM Kotlin's JIT advantage?
