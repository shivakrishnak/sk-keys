---
id: CSF-070
title: JIT vs AOT Compilation Deep Dive
category: CS Fundamentals - Paradigms
tier: tier-1-foundations
folder: CSF-cs-fundamentals
difficulty: ★★★
depends_on: CSF-054, CSF-034
used_by:
related: CSF-054, CSF-034, CSF-069, CSF-075
tags: [jit-compilation, aot-compilation, hotspot, graalvm, profile-guided-optimization]
status: complete
version: 4
layout: default
parent: "CS Fundamentals - Paradigms"
grand_parent: "Technical Mastery"
nav_order: 70
permalink: /technical-mastery/csf/jit-vs-aot-compilation-deep-dive/
---

⚡ TL;DR - JIT (Just-In-Time): HotSpot compiles bytecode to native
at runtime, after profiling hot paths (tiered: C1 quick, C2 optimized).
AOT (Ahead-Of-Time): GraalVM Native Image compiles entire app to native
binary at build time. JIT: slow startup + warmup, peak throughput best,
adapts to runtime profile. AOT: instant startup, lower memory, predictable
latency, smaller attack surface but Closed World assumption (no dynamic class
loading, reflection needs config). Choose JIT for long-lived services;
AOT for serverless, CLIs, microservices with rapid scale-up.

| #070 | Category: CS Fundamentals - Paradigms | Difficulty: ★★★ |
|:---|:---|:---|
| **Depends on:** | CSF-054 (Compilers and Interpreters), CSF-034 (OOP) | |
| **Used by:** | (foundation for GraalVM, Quarkus, Micronaut, serverless, containerized microservices) | |
| **Related:** | CSF-054 (Compilers), CSF-034 (OOP), CSF-069 (Metaprogramming), CSF-075 (GC Pause Analysis) | |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**

Before JIT compilation (early JVMs, Java 1.0-1.1): Java bytecode was
INTERPRETED by the JVM. Every bytecode instruction triggered a dispatch
in the interpreter loop. Result: Java was 10-100x slower than C/C++.
Java was called "too slow for serious applications." The Sun engineers
knew interpretation was the bottleneck. The question: how to run Java
fast without giving up the safety and portability of bytecode?

**THE BREAKING POINT:**

Option A - Compile to native at build time: fast execution, but loses platform
independence (must compile separately for Linux-x64, Windows-x64, macOS-arm, etc.).
Option B - Interpret: keeps platform independence, but too slow for production use.
The insight: DEFER COMPILATION UNTIL RUNTIME when the platform is known.
Compile the hot portions (the 10% of code that runs 90% of the time) to native
on the target machine. Use profiling to identify those hot paths.
This is JIT compilation. The JVM knows both the TARGET PLATFORM and the
ACTUAL RUNTIME BEHAVIOR (which branches are taken, which types appear at call sites).
JIT can generate BETTER code than static AOT compilers because it has more information.

**THE INVENTION MOMENT:**

HotSpot JVM (Sun, 1999): first production JIT for Java. Named "HotSpot" because
it identifies and compiles HOT SPOTS - frequently executed code paths.
Tiered compilation (Java 7): C1 (client compiler, quick tier-1 compilation)
+ C2 (server compiler, slow but highly optimized tier-2 compilation for hot methods).
GraalVM Native Image (Oracle Labs, 2019): the opposite direction. AOT compilation
for Java: compile the ENTIRE application (application + JDK + frameworks) to a
single native binary at build time. Tradeoff: no dynamic class loading, no
runtime compilation flexibility, but instant startup and low memory.
The two approaches coexist: JIT for long-lived throughput-critical services,
AOT for serverless/CLI/fast-startup microservices.

---

### 📘 Textbook Definition

**JIT (Just-In-Time) Compilation:** A runtime optimization technique where bytecode
(or intermediate representation) is compiled to native machine code DURING EXECUTION.
JIT compilers observe program behavior (method invocation counts, branch history,
observed types at call sites) and compile hot methods with this PROFILE-GUIDED
OPTIMIZATION that static compilers cannot perform.

**Tiered Compilation (HotSpot C1 + C2):** HotSpot uses multiple compilation tiers:
Tier 0 (interpreted), Tier 1-3 (C1: quick compile, increasing profiling),
Tier 4 (C2: full optimizing compile using profiling data from Tier 1-3).
Methods move up tiers as their invocation count increases.

**AOT (Ahead-Of-Time) Compilation:** Compilation to native machine code before execution.
The compiler must work without runtime profile data but has more time for analysis.
For Java: GraalVM Native Image. Requires CLOSED WORLD ASSUMPTION: all classes,
reflective accesses, proxies, and serialization must be declared at image build time.

**Profile-Guided Optimization (PGO):** JIT optimization that uses RUNTIME PROFILE
data to improve compilation. Example: if an interface call always dispatches to the
same implementation (monomorphic call site), JIT inlines that specific implementation
with a guard check instead of a virtual dispatch. This is devirtualization.

**Escape Analysis:** JIT analysis that determines whether an object reference
can ESCAPE the current method (be stored in a field, returned, passed to another thread).
If not: the object can be STACK ALLOCATED (eliminated from heap) and its locks
can be ELIMINATED (lock elision). GraalVM Native Image also performs escape analysis.

**Deoptimization:** JIT compiled code may have been compiled with optimistic assumptions
(monomorphic dispatch, no null check needed). If those assumptions are later violated
(a second implementation appears at the call site), the JIT DEOPTIMIZES: reverts
the method to interpreted mode. Deoptimization is rare but has high one-time cost.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
JIT: compile the hot 10% of code to native at runtime, AFTER observing actual behavior.
AOT: compile everything to native at build time.
JIT advantage: profile-guided optimization (knows real runtime behavior).
AOT advantage: instant startup, predictable performance, smaller footprint.

**One analogy:**

> JIT: a translator who learns the SPECIFIC DIALECT of the speaker
> (the speaker's actual hot phrases) and memorizes them after the
> first conversation. Subsequent conversations: instant recall.
> First conversation: slower (learning the dialect).
>
> AOT: a translator who learns all possible dialects before the
> conversation (at school, ahead of time). Instant from the
> first word but cannot adapt to rare phrases encountered only
> at runtime.
>
> Profile-guided optimization: the JIT translator doesn't just
> translate - they notice "this speaker says 'can I help you?'
> 90% of the time" and PREPARES that phrase in advance (inlining).
> The AOT translator cannot know this specific speaker's patterns.

**One insight:**

JIT's profile-guided optimization makes it BETTER than AOT for
peak throughput. How? JIT observes that a virtual method call always
dispatches to `ArrayList.get()` (monomorphic). It inlines `ArrayList.get()`
directly at the call site - no virtual dispatch overhead. AOT cannot
know this at build time (any List implementation could appear at runtime).
This is why, after warmup, JVM peak throughput often EXCEEDS C++.
The runtime profile is information that no static compiler has.
The cost: you pay the warmup cost to acquire that information.
For serverless (duration < 1 second): JIT never warms up -> AOT wins.
For long-lived services (hours+): JIT wins after warmup.

---

### 🔩 First Principles Explanation

**HOTSPOT TIERED COMPILATION:**

```
┌──────────────────────────────────────────────────────┐
│ TIER 0: Interpreted                                  │
│   Method called < ~1500 times: pure interpretation  │
│   No compilation. Full profiling data collected.    │
│   Slowest. Zero compilation cost.                   │
│                                                      │
│ TIER 1: C1 compile (no profiling)                   │
│   Simple methods: trivial no-branch methods         │
│   Quick compile. Limited optimization. Fast start.  │
│                                                      │
│ TIER 2: C1 compile (limited profiling)              │
│   Invoked frequently but C2 queue full              │
│   C1 with branch and invocation counters            │
│                                                      │
│ TIER 3: C1 compile (full profiling)                 │
│   Full profile: type feedback, branch history       │
│   Used as "staging" before C2 takes over           │
│                                                      │
│ TIER 4: C2 compile (full optimizing)                │
│   Method called > ~10000 times                      │
│   Uses profiling data from Tier 3 for:             │
│   - Devirtualization (inline most likely target)   │
│   - Loop unrolling and vectorization                │
│   - Escape analysis (stack alloc, lock elision)    │
│   - Inlining (aggressive, profile-guided)          │
│   - Dead code elimination                          │
│   Slowest compile. Best output code.               │
└──────────────────────────────────────────────────────┘
```

**GRAALVM NATIVE IMAGE BUILD:**

```
┌──────────────────────────────────────────────────────┐
│ NATIVE IMAGE BUILD PROCESS:                          │
│                                                      │
│ 1. ANALYSIS (points-to analysis):                   │
│    Statically determines ALL reachable classes,     │
│    methods, and fields from main() entry point.     │
│    Unreachable code: NOT included in binary.        │
│    CLOSED WORLD: cannot add classes at runtime.     │
│                                                      │
│ 2. REFLECT/PROXY CONFIGURATION:                     │
│    Reflective accesses must be declared in:         │
│    reflect-config.json, proxy-config.json, etc.    │
│    OR: use native-image-agent (run + record).       │
│                                                      │
│ 3. COMPILATION:                                     │
│    Graal compiler (same as JIT Graal compiler)      │
│    compiles ALL reachable code to native.           │
│    AOT PGO: available via -pgo flag (run first,     │
│    collect profile, then build with profile).       │
│                                                      │
│ 4. NATIVE BINARY:                                   │
│    Single self-contained executable.                │
│    Includes: application code + JDK subset          │
│    + GC (serial GC or G1 GC option) + runtime.     │
│    No JVM needed on target system.                  │
└──────────────────────────────────────────────────────┘
```

---

### 🧪 Thought Experiment

**THE SERVERLESS FUNCTION COLD START PROBLEM:**

A Java Spring Boot microservice starts in 8 seconds:
- JVM startup: 200ms (load JVM, JDK classes)
- Spring context initialization: 5s (component scan, reflection, proxy creation)
- Warmup: 3s (C1 compilation of Spring hot paths, then C2)
- Ready: after ~8 seconds

This is fine for a long-lived container (pay 8s once, serve for hours).
For AWS Lambda (cold start on every invocation or after scale-down): 8-second
cold start is unacceptable. Users experience 8s+ response time on first request
after any idle period.

GraalVM Native Image (Quarkus/Micronaut):
- Build time: 5 minutes (one-time)
- Native binary size: 50-100MB (vs 200MB+ JAR + JVM)
- Startup time: 10-50ms (context init done at build time)
- Warmup: none needed (native code from start)
- Memory: 50-150MB resident (vs 300-500MB for JVM service)

AWS Lambda pricing: charged per GB-millisecond. Lower memory + faster startup = lower cost.
Kubernetes pod density: native images fit more pods per node (lower memory footprint).

But: development cost is higher (reflection config, closed world constraints,
no dynamic class loading, longer build times: 5 minutes vs 30 seconds for JAR).
Trade-off decision: JIT for throughput-critical services. AOT for cold-start-critical functions.

---

### 🎯 Mental Model / Analogy

**JIT vs AOT DECISION FRAMEWORK:**

```
┌──────────────────────────────────────────────────────┐
│ DECISION CRITERIA:                                   │
│                                                      │
│ Startup time critical? (serverless, CLI, rapid scale)│
│  -> AOT (GraalVM Native Image)                       │
│                                                      │
│ Peak throughput critical? (long-lived service)       │
│  -> JIT (HotSpot C2, profile-guided optimization)   │
│                                                      │
│ Memory footprint critical? (high pod density)        │
│  -> AOT (significantly lower RSS)                   │
│                                                      │
│ Dynamic behavior required?                          │
│  (plugins, OSGi, runtime class loading, JRuby)      │
│  -> JIT only (AOT cannot support open world)        │
│                                                      │
│ Predictable latency (finance, real-time)?            │
│  -> AOT (no JIT compilation pauses, no deoptimization│
│     stalls), or ZGC/Shenandoah JIT + tuned warmup  │
│                                                      │
│ Development velocity priority?                       │
│  -> JIT (fast build, standard tooling, any library) │
│  AOT: longer builds, reflection config, constraints │
└──────────────────────────────────────────────────────┘
```

**MEMORY HOOK:**

"JIT: interpret -> C1 (quick compile, profile) -> C2 (optimized, PGO).
Deoptimization: optimistic assumptions fail -> revert to interpreted.
Escape analysis: object on stack if it doesn't escape -> heap alloc eliminated.
Devirtualization: monomorphic call site -> inline, no virtual dispatch.
AOT: Closed World = all reachable code determined at build time.
Reflection: needs config (native-image-agent records it).
AOT wins: cold start, memory, predictable latency.
JIT wins: peak throughput (knows actual runtime profile), dynamic behavior.
Quarkus/Micronaut: move framework init to build time, AOT-first.
Spring Native (Graal): annotation processors generate reflect-config, proxy-config.
'Peak throughput: JIT often beats C++ after warmup.' (Profile-guided: more info than static compiler.)"

---

### 📊 Gradual Depth - Five Levels

**Level 1 - Child:**
JIT: code runs slowly at first (the JVM is still reading the recipe).
After practice, it memorizes the most common parts and runs them directly (fast!).
AOT: memorize the ENTIRE recipe before running. Always fast from the start.

**Level 2 - Student:**
Viewing JIT compilation flags:
```bash
# Print methods compiled by JIT and their tier:
java -XX:+PrintCompilation -jar myapp.jar
# Output format:
# timestamp  comp-id  tier  method-name  (size bytes)
# 100   1  3  java.lang.String::hashCode (55 bytes)
# 102   2  4  com.example.Order::process (120 bytes)
# ^ tier 4 = C2 compile = highly optimized
```

**Level 3 - Professional:**
Enable JVM escape analysis and verify stack allocation:
```bash
# Escape analysis (eliminates heap allocation for non-escaping objects):
java -XX:+DoEscapeAnalysis  # enabled by default in HotSpot
     -XX:+EliminateAllocations
     -XX:+PrintEscapeAnalysis  # verbose output (diagnostic flags)
     -jar myapp.jar

# Verify: use JMH benchmark + measure allocation rate:
# If escape analysis works: allocation rate drops for short-lived objects.
# bytesAllocated per operation should decrease significantly.
```

**Level 4 - Senior Engineer:**
GraalVM Native Image with reflection configuration:
```bash
# Step 1: run with native-image-agent to record reflection:
java -agentlib:native-image-agent=config-output-dir=\
    src/main/resources/META-INF/native-image \
    -jar myapp.jar
# Run all code paths (tests, startup, key workflows).
# Agent records: reflect-config.json, proxy-config.json,
#   resource-config.json, serialization-config.json.

# Step 2: build native image (Maven with native profile):
./mvnw -Pnative package

# Step 3: run native binary (no JVM needed):
./target/myapp  # starts in ~50ms

# Check image size and startup:
ls -la target/myapp     # native binary size
time ./target/myapp     # measure startup time
```

**Level 5 - Expert:**
JIT profiling for deoptimization detection:
```bash
# Detect deoptimization events (can cause latency spikes):
java -XX:+TraceDeoptimization   # print deopt events
     -XX:+LogCompilation        # detailed compilation log
     -XX:LogFile=jit.log
     -jar myapp.jar
# Analyze jit.log with JITWatch (open source GUI).
# Deoptimization causes: uncommon_trap (class cast, null check violated).
# Frequent deoptimization of a method: re-examine polymorphism.
# A method that is deoptimized too many times: marked "not compilable"
# -> stays in interpreted mode -> performance regression.
```

---

### ⚙️ How It Works

**INLINE CACHES (JIT DEVIRTUALIZATION MECHANISM):**

```
┌──────────────────────────────────────────────────────┐
│ VIRTUAL DISPATCH PROBLEM:                            │
│ List<Item> items = ...; // could be ArrayList, LinkedList│
│ for (Item i : items) process(i); // items.iterator()  │
│ Naive: virtual dispatch to iterator() at every call. │
│ Cost: 2-3 ns overhead per virtual call.              │
│                                                      │
│ JIT INLINE CACHE (MONOMORPHIC DEVIRTUALIZATION):     │
│ After profiling: 99.9% of calls, items is ArrayList. │
│ JIT compiles to (conceptually):                      │
│ if (items.getClass() == ArrayList.class) {           │
│   // inlined ArrayList.iterator() code directly     │
│ } else {                                             │
│   // slow path: real virtual dispatch                │
│ }                                                    │
│ No virtual dispatch for the common case.             │
│ Guard check (class comparison): ~0.3 ns.             │
│ Net effect: ~3x speedup on virtual method-heavy code │
│                                                      │
│ BIMORPHIC: if two types appear at the call site,    │
│ JIT emits two guards. Three or more: megamorphic    │
│ (give up on devirtualization, use vtable dispatch). │
└──────────────────────────────────────────────────────┘
```

---

### 💻 Code Example

**Example 1 - Wrong vs Right: JIT Unfriendly vs Friendly Code**

```java
// BAD: Megamorphic call site (defeats JIT devirtualization)
public void processAll(List<Processor> processors, Item item) {
    for (Processor p : processors) {
        p.process(item); // 10+ different Processor implementations
        // JIT cannot inline: call site is megamorphic
        // HotSpot gives up, uses vtable dispatch for every call
    }
}

// GOOD: Batch by type (helps JIT devirtualize)
public void processAllFast(Map<Class<?>, List<Item>> itemsByType,
                            Processor processor) {
    // Group calls so call sites are monomorphic or bimorphic.
    // JIT inlines the dominant type.
    itemsByType.forEach((type, items) -> {
        if (processor instanceof SpecialProcessor sp) {
            items.forEach(sp::processSpecial); // monomorphic: devirtualized
        } else {
            items.forEach(processor::process); // monomorphic: devirtualized
        }
    });
}
// Real-world implication: Java stream API with polymorphic lambdas can be
// slower than expected if the call site becomes megamorphic.
// Profile with JFR before optimizing.
```

**Example 2 - AOT Reflection Config Failure (Production Bug Pattern)**

```java
// Code that works in JVM mode but fails in GraalVM native image:
// BAD: Reflection without config
@Service
public class DynamicService {
    public Object createByName(String className) throws Exception {
        // Works in JVM: Class.forName finds the class at runtime.
        // FAILS in native image: class metadata pruned by Closed World analysis.
        return Class.forName(className) // ClassNotFoundException in native
                    .getDeclaredConstructor()
                    .newInstance();
    }
}
// Error at runtime (native image): Class not found: com.example.FooImpl
// Root cause: Closed World analysis removed FooImpl (not statically reachable).

// GOOD: Declare reflection explicitly in native-image config:
// src/main/resources/META-INF/native-image/reflect-config.json:
// [{"name": "com.example.FooImpl", "allDeclaredConstructors": true}]

// BETTER: Replace reflection with annotation-processor-generated factory:
// @Service
// public class TypedServiceFactory {
//     private final Map<String, Supplier<Service>> registry = Map.of(
//         "foo", FooImpl::new,  // no reflection: direct reference
//         "bar", BarImpl::new
//     );
//     public Service create(String type) {
//         return registry.getOrDefault(type,
//             () -> { throw new IllegalArgumentException(type); }).get();
//     }
// }
// Zero reflection. Works in GraalVM native image without config.
```

---

### ⚖️ Comparison Table

| Dimension | JIT (HotSpot C2) | AOT (GraalVM Native) |
|---|---|---|
| Startup time | 1-10 seconds | 10-100ms |
| Warmup time | 1-30 seconds (to peak perf) | None (full speed from start) |
| Peak throughput | Very high (PGO + devirt) | High (good, less PGO) |
| Memory footprint | 200-500MB (JVM + heap) | 50-150MB (native + heap) |
| Dynamic class loading | Full support | Not supported |
| Reflection | Any (no config) | Config required |
| Predictable latency | Lower (JIT pauses possible) | High (no JIT pauses) |
| Build time | Seconds (JAR) | Minutes (native image) |
| Debuggability | Excellent (standard tooling) | Limited (native tools) |
| Best for | Long-lived throughput services | Serverless, CLI, fast startup |

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| "JIT compilation is just interpretation with caching" | JIT compilation produces MACHINE CODE - the same quality of native code that a C compiler produces, often BETTER due to profile-guided optimization. A C compiler cannot know at compile time that a virtual call is always monomorphic. JIT can observe this at runtime and inline the callee. Escape analysis in JIT eliminates heap allocations. Loop vectorization uses SIMD intrinsics. JIT-compiled Java code in steady state often outperforms equivalent C++ for object-intensive code because the JIT has runtime type information that the C++ compiler lacks. "Caching with interpretation" is interpretation with memoized results. JIT is code GENERATION producing native machine instructions, not memoization of interpreted results. |
| "AOT (GraalVM native image) is always faster than JIT" | AOT is faster at STARTUP and has LOWER LATENCY for early requests (no warmup). But JIT PEAK THROUGHPUT (after warmup) is typically equal to or BETTER than AOT. Why? JIT's profile-guided devirtualization and inlining produce tighter code for the specific runtime workload. AOT compiles conservatively (cannot inline a virtual call it doesn't know is monomorphic). GraalVM offers PGO for native image (run the application to collect a profile, then rebuild with that profile), which narrows the gap. For throughput-critical, long-lived services: JIT is the right choice. For startup-critical, short-lived functions: AOT wins. The choice depends on the deployment model, not a universal performance claim. |
| "GraalVM native image doesn't support any reflection" | GraalVM native image supports reflection with EXPLICIT CONFIGURATION. Classes, methods, and fields used reflectively must be declared in `reflect-config.json`. The `native-image-agent` automates this: run the application with the agent, all reflection calls are recorded, config is generated automatically. Spring Native (Spring Boot 3.x): Spring's AOT processing automatically generates the reflection config for Spring-managed beans. Quarkus: extension ecosystem provides native-image config for all major libraries. The limitation is DYNAMIC reflection (reflecting on classes loaded at runtime from user input) which is inherently incompatible with the Closed World assumption. Static reflection (fixed set of classes known at build time) is fully supported. |
| "JIT deoptimization is a bug that should never happen" | Deoptimization is a DESIGNED FEATURE of JIT compilation, not a bug. JIT makes OPTIMISTIC ASSUMPTIONS (this call site is always monomorphic, this array access never throws). If those assumptions are violated, the JIT deoptimizes (reverts to interpreted mode) and recompiles with PESSIMISTIC assumptions. This design allows JIT to be aggressively optimistic in the common case (faster code) while gracefully handling edge cases (correctness preserved). The concern: FREQUENT deoptimization of a hot method causes repeated recompilation cycles and performance instability. A method deoptimized many times may be permanently marked "not compilable" by the JVM, forcing it to stay interpreted. This degrades performance significantly. Diagnose with `-XX:+TraceDeoptimization` and JFR (JDK Flight Recorder). Fix: investigate what runtime type is causing the violation and refactor to keep call sites monomorphic. |

---

### 🚨 Failure Modes & Diagnosis

**Failure Mode 1: JIT Warmup Cold Start Under Load (AWS Lambda)**

**Symptom:** First 100 requests take 2-5 seconds each. After 1000 requests,
response time drops to 20ms. Traffic spikes cause latency spikes (Lambda
scales: new instances start cold, take 5-10 requests to warm up).

**Diagnosis:**
```bash
# JFR (Java Flight Recorder) - capture compilation activity:
java -XX:StartFlightRecording=duration=60s,filename=recording.jfr \
     -jar myapp.jar
# Analyze recording.jfr with JDK Mission Control (JMC) or jfr tool:
jfr print --events Compilation recording.jfr | head -50
# Shows: which methods were compiled, when, compilation time.
# Compare: request latency vs compilation timeline.
# If spikes correlate with C2 compilation: warmup is the bottleneck.
```

**Fix options:**
1. GraalVM Native Image (AOT): eliminates warmup entirely.
2. JVM warmup: pre-warm by calling key code paths at startup (dummy requests).
3. JVM `-XX:TieredStopAtLevel=1`: stop at C1 (faster startup, lower peak performance).
4. CRaC (Coordinated Restore at Checkpoint): snapshot JVM after warmup, restore snapshot on demand.
5. AWS Lambda SnapStart: AWS-managed CRaC for Lambda functions.

---

**Security Note:**

AOT compilation with GraalVM Native Image has a smaller attack surface
than JIT compilation for several reasons:
1. NO JIT COMPILER AT RUNTIME: JIT compiler is a significant code path
   that can be exploited (JIT spraying attacks). Native image has no JIT.
2. CLOSED WORLD: only explicitly declared classes are included in the binary.
   An attacker who can trigger arbitrary class loading (via reflection) in a
   JVM application cannot do so in a native image without reflection config.
3. SMALLER BINARY: Native image includes only reachable code. Less attack surface
   from unused standard library code (e.g., remote debugging APIs, JNDI lookups).

JNDI INJECTION (Log4Shell-type vulnerabilities):
Log4Shell (CVE-2021-44228) exploited JNDI lookup + dynamic class loading in Log4j.
GraalVM native image: JNDI lookup is not in the Closed World by default (not reachable),
AND dynamic class loading is not supported. Native image applications are INHERENTLY
resistant to Log4Shell-type JNDI injection vulnerabilities.

This is not just a performance trade-off: AOT has MEANINGFUL SECURITY ADVANTAGES
over JIT for production deployments. When threat modeling a microservice:
native image reduces the runtime attack surface significantly.

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**
- `Compilers and Interpreters` (CSF-054) - how source code is compiled
  and interpreted: the foundation for understanding JIT and AOT compilation
- `Object-Oriented Programming` (CSF-034) - virtual method dispatch (vtable)
  is a key optimization target for JIT devirtualization

**Builds On This (learn these next):**
- `GC Pause Analysis and Production Impact` (CSF-075) - JIT and GC interact:
  GC behavior affects JIT performance (GC pauses cause JIT deoptimization events)
- `Metaprogramming` (CSF-069) - reflection is the primary constraint for AOT
  compilation; understanding metaprogramming explains why reflection config is needed

---

### 📌 Quick Reference Card

```
┌────────────────────────────────────────────────────────┐
│ JIT TIERS    │ 0 interp, 1-3 C1 (profile), 4 C2 PGO  │
├──────────────┼─────────────────────────────────────────┤
│ JIT PGO      │ Devirtualization, inlining, escape ana. │
│              │ Loop unrolling, dead code elim.         │
├──────────────┼─────────────────────────────────────────┤
│ DEOPT        │ Optimistic assume violated -> revert    │
│              │ Diagnose: -XX:+TraceDeoptimization, JFR │
├──────────────┼─────────────────────────────────────────┤
│ ESCAPE ANAL. │ Non-escaping object -> stack alloc      │
│              │ Lock elision on non-escaping lock       │
├──────────────┼─────────────────────────────────────────┤
│ NATIVE IMAGE │ Closed World, no dynamic class loading  │
│              │ Reflection: needs config or agent       │
│              │ Startup: 10-100ms, RSS: 50-150MB        │
├──────────────┼─────────────────────────────────────────┤
│ AOT USE CASE │ Serverless, CLI, rapid scale-up         │
│ JIT USE CASE │ Long-lived throughput-critical services │
├──────────────┼─────────────────────────────────────────┤
│ SECURITY     │ AOT: no JIT spraying, no JNDI injection │
│              │ Closed World = smaller attack surface   │
├──────────────┼─────────────────────────────────────────┤
│ TOOLS        │ JFR + JMC (JIT profiling), jfr CLI     │
│              │ native-image-agent (reflection config)  │
│              │ JITWatch (compile log analysis)         │
├──────────────┼─────────────────────────────────────────┤
│ NEXT EXPLORE │ CSF-075 (GC Pause Analysis)            │
└────────────────────────────────────────────────────────┘
```

**If you remember only 3 things:**

1. HotSpot JIT uses TIERED COMPILATION: interpret (Tier 0) -> quick C1 compile
   with profiling (Tiers 1-3) -> optimized C2 compile using profile data (Tier 4).
   The key insight: C2 has RUNTIME PROFILE information that no static compiler has
   (which branches are taken, which types appear at call sites). This enables
   DEVIRTUALIZATION (inline the actual implementation, no virtual dispatch),
   ESCAPE ANALYSIS (stack-allocate non-escaping objects), and profile-guided
   INLINING. After warmup (~10,000 invocations for a hot method), JIT-compiled
   Java code often outperforms equivalent C++ for object-heavy workloads because
   C++ compilers lack runtime type information.
2. GraalVM Native Image: CLOSED WORLD compilation. Points-to analysis determines
   all reachable code at build time. Everything reachable: compiled to native binary.
   Everything else: excluded. Consequence: no dynamic class loading, reflection
   requires explicit config (`reflect-config.json`, generated by `native-image-agent`).
   Benefits: 10-100ms startup (vs 2-10s JVM), 50-150MB RSS (vs 300-500MB JVM),
   no warmup latency, no JIT-related latency spikes. Cost: 5-10 min build time,
   reflection config maintenance, cannot use libraries that depend on dynamic
   class loading (OSGI, JRuby, some older Spring features).
3. AOT vs JIT DECISION: if the service is LONG-LIVED (running for hours, handling
   sustained traffic): JIT wins on peak throughput (PGO advantage). If the service
   is SHORT-LIVED or COLD-START-SENSITIVE (serverless Lambda, CLI tools, rapid
   scale-out pods): AOT wins (startup + memory). GraalVM AOT also has SECURITY
   ADVANTAGES: no JIT compiler = no JIT spraying attack surface; Closed World =
   dynamic class loading and JNDI injection attacks are inherently prevented
   (no ability to load attacker-controlled classes at runtime).

**Interview one-liner:**
"JIT: tiered compilation (interp -> C1 profile -> C2 PGO). C2 uses runtime profile for devirtualization,
escape analysis, inlining. Peak throughput often beats AOT after warmup. Deoptimization: optimistic assumption
violated -> revert to interpreted. AOT (GraalVM Native Image): Closed World analysis, compile everything
reachable at build time, no dynamic class loading, reflection needs config.
Startup 10-100ms vs 2-10s JVM. Memory 50-150MB vs 300MB+. Choose JIT for throughput-critical long-lived
services; AOT for serverless, CLI, rapid scale-up. AOT security bonus: no JIT spraying, no JNDI injection."

---

### 💎 Transferable Wisdom

**Reusable Engineering Principle:**
THE INFORMATION-TIMING TRADEOFF: JIT has MORE INFORMATION (runtime profile)
but less TIME (must compile during execution). AOT has MORE TIME (minutes at
build time) but less INFORMATION (no runtime profile). This tradeoff recurs
across engineering: ONLINE LEARNING vs BATCH LEARNING in ML (online: adapts
continuously with current data, batch: trained thoroughly on historical data),
ADAPTIVE ALGORITHMS vs STATIC ALGORITHMS (quicksort pivot selection: random
static vs adaptive median-of-three), REACTIVE ARCHITECTURE vs STATIC ARCHITECTURE
(microservices autoscaling: adapts to traffic vs pre-provisioned capacity).
The fundamental question: how much of the decision-relevant information is
available EARLY vs only available LATE? If critical information is only known
at runtime: JIT-like (deferred decision) is necessary. If the domain is
stable and information is available upfront: AOT-like (early commitment) wins.

**Where else this pattern appears:**

- **Database query optimization: JIT vs AOT for query plans** - Query
  planners face the same JIT vs AOT tradeoff. STATIC (AOT-like) query plans:
  PostgreSQL's `PREPARE` statement creates a query plan at prepare time and
  reuses it for all invocations with different parameter values. This is AOT:
  plan generated once, reused many times. Fast for the same query; may be
  suboptimal for parameters that cause different selectivity. ADAPTIVE
  (JIT-like) query plans: PostgreSQL 14+ "generic plan vs custom plan" adaptively
  decides whether to re-plan based on parameter values. For the first 5 executions,
  PostgreSQL uses a custom plan (freshly estimated per parameter). After 5 executions,
  if the estimated cost of generic plan is within threshold: switch to generic.
  This is JIT-like: observe actual parameters, decide on plan dynamically.
  MySQL 8.0 join optimizer: adaptive hash join builds hash table or falls back
  to nested-loop based on memory availability at execution time. This is JIT
  optimization within the query: the execution plan adapts to runtime conditions.
  The parallel to JVM JIT is exact: gather information about the "hot path"
  (most common query shape/parameters) and specialize the plan for it.
- **Webpack bundle splitting: AOT-like optimization at build time** - Webpack's
  code splitting is an AOT (build-time) optimization. Webpack analyzes the ENTIRE
  application dependency graph at build time and generates optimal chunk splits.
  Static imports: deterministically included in the main bundle (known at build time).
  Dynamic `import()`: split into separate chunk (load on demand). This is the
  Closed World principle: Webpack knows at build time which modules are needed for
  each route. It can tree-shake (eliminate dead code: Closed World for JavaScript).
  Contrast with a JS application that `eval()`s code strings at runtime: Webpack
  cannot tree-shake that (open world). GraalVM Native Image's Closed World =
  Webpack's bundle. Both require that all "reachable" code is determined at build time.
  Both break when code is dynamically loaded at runtime. The tradeoff is identical:
  build-time analysis catches more dead code (smaller bundle/binary) but cannot
  handle runtime dynamism. For Webpack: `import()` is the reflection equivalent
  (deferred load, not tree-shakeable). For GraalVM: `Class.forName()` is the
  `import()` equivalent (dynamic, needs config).
- **Kubernetes horizontal pod autoscaler: reactive vs proactive scaling** -
  The HPA (Horizontal Pod Autoscaler) observes CPU/memory/custom metrics and
  scales pod count reactively (JIT-like: react to observed load). This requires
  warmup: newly started pods need JVM warmup time (further worsening cold starts).
  Predictive autoscaling (KEDA, Knative with traffic history): forecast future
  load from historical patterns (AOT-like: scale before the load arrives, based
  on learned patterns). AOT-compiled native images make reactive scaling more
  viable: a native image pod reaches full performance in 50ms instead of 30 seconds.
  The JIT warmup problem makes reactive scaling painful (new pod is slow for the
  first 30 seconds). AOT eliminates this pain: reactive scaling becomes effective
  immediately. This is a second-order benefit of AOT: not just "faster startup"
  but "enables architectural patterns (reactive fine-grained autoscaling) that
  were previously impractical due to warmup cost."

---

### 💡 The Surprising Truth

After JVM warmup, JIT-compiled Java can outperform equivalent C code for
certain workloads - and this is not a fluke or benchmarking artifact. C
compilers compile with CONSERVATIVE assumptions: a virtual function call
COULD dispatch to any implementation, so no inlining is possible. A loop
MIGHT alias memory, so vectorization is restricted. An array access MIGHT
overflow, so bounds checking is needed. JIT has ACTUAL RUNTIME DATA: this
virtual call has only EVER dispatched to `ArrayList.iterator()` in the
last 10,000 invocations. JIT inlines it with a guard check. If C++ used
`final` or `devirtualization hints` for all these cases: it could compete.
But in real codebases, virtual dispatch is ubiquitous. HotSpot C2 handles
this automatically, retroactively, for any code that becomes hot. The
JVM is a self-modifying program that improves its own execution based on
observation. This was the core insight of the HotSpot team: don't ask
programmers to annotate everything - observe and optimize automatically.
The price: the warm-up tax. The reward: often-better-than-C performance
for typical enterprise workloads, with zero programmer effort.

---

### ✅ Mastery Checklist

**You've mastered this when you can:**

1. **[JIT-TIERS]** Explain what happens to a method that starts
   interpreted and becomes hot. Walk through: Tier 0, when C1 kicks in,
   when C2 kicks in, what profile data C2 uses, and what deoptimization
   means for a method that was C2-compiled. At what invocation counts does
   HotSpot promote to C1 and C2 (approximate defaults)?

2. **[PGO]** A service handles `List<Animal>` where `Animal.speak()` is
   called in a tight loop, and in production 98% of calls are `Dog.speak()`.
   How does HotSpot C2 optimize this? What does the compiled code look like?
   What happens if a `Cat.speak()` call suddenly appears?

3. **[ESCAPE-ANALYSIS]** Give an example of an object that HotSpot can
   stack-allocate due to escape analysis. Give an example of an object
   that CANNOT be stack-allocated. What JVM flag enables escape analysis
   (hint: it's on by default)? What is lock elision and when does it apply?

4. **[NATIVE-IMAGE]** A Spring Boot application uses Jackson for JSON
   serialization, Hibernate for ORM, and Spring Security with JWT.
   What are the three main compatibility challenges for GraalVM Native Image?
   Which Spring Boot version introduced AOT support and what does it do?

5. **[DECISION]** You are building: (a) a REST API that handles 50K
   requests/second with SLAs of p99 < 10ms, (b) an AWS Lambda function
   that responds to S3 events with p99 cold start < 200ms requirement.
   Justify your JIT vs AOT choice for each, including trade-offs.

---

### 🧠 Think About This Before We Continue

**Q1.** GraalVM offers a Profile-Guided Optimization (PGO) option for
native image: run the application to collect a profile, then rebuild
with `--pgo=profile.iprof`. Does this close the performance gap with
JIT? What does it still miss?

*Hint: GraalVM AOT PGO narrows the gap SIGNIFICANTLY. Steps:
1. Build an instrumented native image: native-image --pgo-instrument ...
2. Run the instrumented binary under production-representative load (record profile).
3. Rebuild native image: native-image --pgo=profile.iprof ...
Result: the AOT compiler now has a PROFILE of branch probabilities, method
frequencies, and type statistics. It can:
- Inline methods called frequently.
- Reorder code to put hot paths in instruction cache.
- Devirtualize calls that are monomorphic in the profile.

What it still MISSES vs JIT:
1. DYNAMIC profiles: the PGO profile is collected from a SPECIFIC run.
   Production traffic varies. A JIT continuously adapts to the CURRENT traffic.
   An AOT binary compiled with Monday's profile may not be optimal for Friday's traffic.
2. DEOPTIMIZATION-FREE recompilation: JIT can deoptimize + recompile when assumptions
   change. AOT cannot. If a new type appears at a call site that was monomorphic in
   the PGO profile, AOT has no recovery mechanism. The code remains compiled
   with the old (now suboptimal) assumptions.
3. LIVE TYPE INFORMATION: JIT can use type information that is only fully resolved
   at runtime (e.g., interface implementations registered via ServiceLoader at startup).
   AOT PGO captures what was seen during the profile run, but cannot update at runtime.

Result: GraalVM with PGO typically reaches 80-95% of JIT peak throughput for stable
workloads. For long-lived, stable services: JIT is still slightly faster at peak.
For workloads with stable traffic patterns: GraalVM PGO is an excellent option.*

**Q2.** CRaC (Coordinated Restore at Checkpoint) is a newer JVM feature
that snapshots the JVM state and restores it. How does this differ from
GraalVM Native Image, and what problems does it solve that AOT cannot?

*Hint: CRaC (coordinated restore at checkpoint): JVM + application runs normally (with JIT warmup).
At "checkpoint" time: the JVM STATE (including heap, JIT-compiled code, all loaded classes,
all initialized beans) is snapshotted to disk.
At "restore" time: JVM restores from snapshot - starts in a WARM state.
The heap, JIT-compiled code, and initialized beans are all present from byte 1 of execution.
First requests: handled with JIT-optimized code (no warmup lag).

HOW IT DIFFERS FROM AOT:
1. CRaC: full JVM retained. Dynamic class loading works. Reflection works.
   AOT: no JVM. Closed World. No dynamic class loading. Reflection needs config.
2. CRaC: JIT-compiled code in snapshot (full JIT optimization benefit).
   AOT: AOT-compiled code (good but no runtime PGO by default).
3. CRaC: snapshot taken from a RUNNING application -> full warmup benefits.
   AOT: compile-time only -> no runtime profile unless using PGO explicitly.
4. CRaC: snapshot must be rebuilt when application code changes.
   AOT: native image must be rebuilt when application code changes.
   Both: added build/snapshot complexity.

WHAT CRaC SOLVES THAT AOT CANNOT:
1. Libraries with dynamic class loading (OSGI, JRuby, Groovy) - works with CRaC, not with AOT.
2. Full JIT peak performance from first request (AOT cannot reach JIT peak without PGO).
3. Reflection without any configuration (CRaC snapshots the already-reflected state).
4. Applications that run initialization during startup (Spring context, Hibernate schema validation)
   -> checkpointed after init -> restore skips the init entirely.
   AOT can do this too (Quarkus AOT init), but requires explicit AOT support in each library.

PRACTICAL STATUS:
AWS Lambda SnapStart: CRaC-based (checkpoints Lambda container after init handler completes).
Reduces Java Lambda cold start from 8-10 seconds to <1 second.
CRaC requires Linux (CRIU: Checkpoint/Restore In Userspace).
Not yet stable on all platforms (2024: Linux only, macOS experimental).
GraalVM Native Image: fully cross-platform. Better for standalone native binaries.*

---

### 🎯 Interview Deep-Dive

**Q1: "How does JIT compilation work in HotSpot? What is tiered compilation?"**

*Why they ask:* Tests JVM internals knowledge. Common for senior Java roles and platform engineering.

*Strong answer includes:*
- JIT: compiles bytecode to native machine code at runtime, after observing execution.
  The key insight: runtime observation provides information (actual types, branch history)
  that static AOT compilers cannot have.
- Tiered compilation:
  Tier 0: interpreted (all methods start here)
  Tier 1-3: C1 compiler (quick compile, varying profiling detail). Fast startup.
  Tier 4: C2 compiler (slow, highly optimizing). Uses profile data from C1.
  Methods promoted as invocation count increases (~1500 for C1, ~10000 for C2).
- C2 optimizations (key examples):
  Devirtualization: monomorphic call site -> inline with guard, no vtable dispatch.
  Escape analysis: non-escaping objects -> stack allocation, lock elision.
  Loop unrolling: SIMD vectorization for array loops.
  Inlining: aggressive inlining of hot callees (removes call overhead).
- Deoptimization: when optimistic assumption violated -> revert to interpreted, recompile pessimistically.

**Q2: "What is the Closed World assumption in GraalVM Native Image and why does it matter?"**

*Why they ask:* Tests GraalVM understanding. Common for cloud-native/microservices interviews.

*Strong answer includes:*
- Closed World: at native image build time, ALL reachable classes, methods, and fields
  are determined via points-to analysis from main(). Code not reachable: excluded from binary.
  At runtime: no new classes can be loaded (no Class.forName() with unknown classes,
  no URLClassLoader for plugin loading, no JRuby/Groovy dynamic loading).
- Why it matters:
  1. Smaller binary: only reachable code included.
  2. Faster startup: no class loading at startup (all in binary already).
  3. Security: dynamic class loading attacks impossible (JNDI injection, Log4Shell-type).
  4. Memory: all metadata is native data structures, no JVM PermGen/Metaspace.
- Why it's a constraint:
  Reflection: reflective access to a class NOT in the Closed World -> ClassNotFoundException.
  Fix: declare in reflect-config.json, or use native-image-agent to auto-generate.
  Dynamic proxies: Spring CGLIB proxies must be declared at build time.
  Fix: Spring Boot 3 (Spring Native) generates the proxy config via AOT processing.
  Plugin systems: cannot load user-supplied JAR at runtime -> architectural constraint.
- Key implication: Quarkus and Micronaut are designed with the Closed World in mind.
  Spring Boot 3+ has first-class GraalVM native image support via the `spring-aot` plugin.
  Older Spring Boot (2.x) requires manual reflection config.
