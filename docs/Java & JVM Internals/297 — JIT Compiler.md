---
layout: default
title: "JIT Compiler"
parent: "Java & JVM Internals"
nav_order: 297
permalink: /java/jit-compiler/
number: "0297"
category: Java & JVM Internals
difficulty: ★★★
depends_on: JVM, Bytecode, Class Loader
used_by: C1 / C2 Compiler, Tiered Compilation, Method Inlining, Deoptimization
related: AOT (Ahead-of-Time Compilation), GraalVM, Tiered Compilation
tags:
  - java
  - jvm
  - internals
  - performance
  - deep-dive
---

# 297 — JIT Compiler

⚡ TL;DR — The JIT Compiler turns interpreted bytecode into native machine code at runtime, making long-running Java programs as fast as C++.

┌─────────────────────────────────────────────────────────────────────────────────┐
│ #297 │ Category: Java & JVM Internals │ Difficulty: ★★★ │
├──────────────┼──────────────────────────────────────┼──────────────────────────┤
│ Depends on: │ JVM, Bytecode, Class Loader │ │
│ Used by: │ C1/C2 Compiler, Tiered Compilation, │ │
│ │ Method Inlining, Deoptimization │ │
│ Related: │ AOT Compilation, GraalVM, │ │
│ │ Tiered Compilation │ │
└─────────────────────────────────────────────────────────────────────────────────┘

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
Java's "write once, run anywhere" promise required bytecode — an intermediate
representation that any JVM on any OS could execute. But bytecode is interpreted
line by line. Every time your method runs, the JVM reads bytecode, decodes the
instruction, then executes it. This interpretation overhead is 10–100× slower
than native machine code. In the early days of Java (1995–1996), Java had a
reputation for being "slow" — not because the language was bad, but because
execution was pure interpretation.

**THE BREAKING POINT:**
A web server handling 50,000 requests/second calls the same JSON serialization
method millions of times. Each call pays the interpretation tax. CPU spends 60%
of its time decoding bytecode instructions rather than doing actual work. The
server needs 10× more hardware than an equivalent C++ server.

**THE INVENTION MOMENT:**
This is exactly why the **JIT Compiler** was created. Instead of interpreting
forever, the JVM watches which methods are called frequently ("hot methods"),
compiles them to native machine code once, and executes that native code directly
on all future calls — zero interpretation overhead.

---

### 📘 Textbook Definition

The Just-In-Time (JIT) Compiler is a component of the JVM that identifies
frequently-executed ("hot") bytecode segments and compiles them to optimized
native machine code at runtime. Unlike AOT compilation, JIT operates after the
program starts, using runtime profiling data — actual call frequencies, type
profiles, branch outcomes — to produce more aggressively optimized code than a
static compiler can. The generated native code is cached in the Code Cache region
of the JVM and executed directly by the CPU on subsequent calls.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
JIT watches your code run, finds what's hot, and compiles only that to native machine code.

**One analogy:**

> Imagine a translator who follows you around all day. At first, they translate
> every sentence you say on the spot (slow). After noticing you repeat the same
> phrases constantly, they write those phrases on a card. Now you just hold up
> the card — instant communication, no translation needed.

**One insight:**
JIT's secret weapon is that it compiles with runtime evidence — it knows the
actual types passed to a polymorphic method, the actual branch taken 99% of the
time, and the actual call frequency. A static compiler (like C++) must conservatively
handle all possibilities. JIT can speculatively optimize for the common case and
fall back (deoptimize) only when the assumption breaks.

---

### 🔩 First Principles Explanation

**CORE INVARIANTS:**

1. Bytecode is platform-neutral; native code is platform-specific.
2. Compilation has upfront cost; interpretation has per-execution cost.
3. Runtime profiling reveals what static analysis cannot: actual execution patterns.
4. Hot code concentrates: 80% of execution time is in 20% of methods (Pareto rule).

**DERIVED DESIGN:**
Given these invariants, the optimal strategy is:

- Start by interpreting (zero startup cost, gather profile data).
- Count method invocations and loop back-edge iterations.
- When a method crosses the compilation threshold, compile it to native code.
- Store compiled code in Code Cache; replace the method call stub.
- Use gathered profile data to make aggressive speculative optimizations.

This yields fast startup (no upfront compilation) AND fast steady-state throughput
(native code for hot paths) — the best of both worlds.

**THE TRADE-OFFS:**

- Gain: Near-C++ throughput for long-running applications (servers, batch jobs).
- Cost: Compilation happens on background threads, consuming CPU and memory (Code Cache).
- Gain: Better optimization than AOT because of runtime type information.
- Cost: JVM "warm-up" period (first few seconds run slowly at interpreted speed).

Could we compile everything upfront? Yes — that's AOT. But you lose the runtime
profile data, so optimizations are more conservative, AND you pay compilation cost
even for rarely-called methods. JIT is the right trade-off for server workloads.

---

### 🧪 Thought Experiment

**SETUP:**
You have a method `computeDiscount(Product p)` that's called 10 million times per
hour. It's polymorphic — `p` could be any subclass of `Product`.

**WHAT HAPPENS WITHOUT JIT:**
Every single call: JVM reads bytecode → decodes instruction → calls virtual dispatch
→ executes. The virtual dispatch alone requires a pointer lookup into the vtable,
then a branch. No optimization possible because the JVM doesn't know which subclass
is actually passed. 10M calls × 50ns overhead = 500ms wasted every hour on
interpretation alone.

**WHAT HAPPENS WITH JIT:**
After ~10,000 calls the JVM notices: 99.9% of calls pass `DigitalProduct`.
JIT compiles `computeDiscount` to native code with an inlined, type-specialized
version: no vtable lookup, no virtual dispatch, registers pre-allocated. The 0.1%
case uses a slow-path guard. 10M calls now execute in nanoseconds, not microseconds.

**THE INSIGHT:**
JIT turns the JVM's perceived weakness (it's interpreted) into a strength: because
it observes before it compiles, it can optimise for YOUR specific workload — better
than any static compiler ever could.

---

### 🧠 Mental Model / Analogy

> Think of JIT as a race car pit crew that fine-tunes the car mid-race based on
> telemetry. They don't tune everything — only the parts that are limiting speed
> right now. And they tune it specifically for today's track conditions, not for
> some theoretical average race.

- "Track telemetry" → runtime profiling data (call counts, type profiles)
- "Pit crew" → JIT compiler threads running in background
- "Fine-tuning the car" → compiling bytecode to optimised native code
- "Parts limiting speed" → hot methods / hot loops
- "Mid-race" → compilation happens while the program is running

**Where this analogy breaks down:** A pit crew can physically modify hardware
between laps. JIT cannot always re-compile already-compiled code — it can
deoptimize (revert to interpreter) but re-compiling with new profile data requires
the old compiled version to be invalidated first.

---

### 📶 Gradual Depth — Four Levels

**Level 1 — What it is (anyone can understand):**
JIT makes Java faster over time. When your program starts, it runs slowly while
the JVM watches. After it figures out which code runs the most, it converts that
code into super-fast native instructions, and speed increases dramatically.

**Level 2 — How to use it (junior developer):**
JIT is automatic — you don't call it. But you can influence it: warm up your
application by running representative workloads before handling production traffic.
JVM flags like `-server` enable the more aggressive C2 compiler. Avoid unnecessary
polymorphism and megamorphic call sites (more than 2 implementors) — they prevent
JIT inlining.

**Level 3 — How it works (mid-level engineer):**
The JVM uses an invocation counter per method and a back-edge counter per loop.
When `invocations + back_edges > CompileThreshold` (default: 10,000 for C2),
the method is queued for compilation. The JIT compiler runs on dedicated
`CompilerThread` daemon threads. It builds an SSA (Static Single Assignment) IR,
applies optimizations (inlining, escape analysis, loop unrolling, constant folding),
then emits x86/ARM native code into the Code Cache. The original bytecode entry
point is patched to jump to the native code.

**Level 4 — Why it was designed this way (senior/staff):**
The two-tier design (interpreter → C1 → C2) balances startup latency vs peak
throughput. JVM designers tried pure AOT (gcj), pure interpreter, and single-tier
JIT — each failed in the startup/throughput trade-off. The key insight from the
HotSpot research was that profile-guided optimizations (PGOs) — using observed
type information — can speculate beyond what static analysis permits. This allows
virtual call devirtualization, which is impossible in static compilers where the
call graph is unknown. The cost is deoptimization complexity: the JVM must maintain
enough state to fall back to the interpreter when speculative assumptions are violated.

---

### ⚙️ How It Works (Mechanism)

The JIT pipeline has 5 stages:

```
┌─────────────────────────────────────────────┐
│         JIT COMPILATION PIPELINE            │
├─────────────────────────────────────────────┤
│  1. PROFILING (Interpreter)                 │
│     Count method calls & loop iterations    │
│     Record type profiles at call sites      │
│                    ↓                        │
│  2. THRESHOLD CROSSED                       │
│     invocations > CompileThreshold (10000)  │
│     → enqueue method for compilation        │
│                    ↓                        │
│  3. IR CONSTRUCTION (CompilerThread)        │
│     Bytecode → HIR (High-level IR)          │
│     Apply inlining, escape analysis         │
│     → LIR (Low-level IR)                   │
│                    ↓                        │
│  4. CODE GENERATION                         │
│     LIR → native x86/ARM instructions      │
│     Register allocation                     │
│     Code stored in Code Cache               │
│                    ↓                        │
│  5. ACTIVATION                              │
│     Method entry patched → native code      │
│     All future calls execute native code    │
└─────────────────────────────────────────────┘
```

**Key optimisations applied during JIT:**

- **Method Inlining**: Copy callee body into caller, eliminating call overhead.
- **Escape Analysis**: If an object doesn't escape a method, allocate it on the stack.
- **Loop Unrolling**: Expand loop body N times to reduce branch overhead.
- **Constant Folding**: Evaluate constant expressions at compile time.
- **Dead Code Elimination**: Remove unreachable branches.
- **Speculative Devirtualization**: Inline the most common virtual call target with a guard.

**On the happy path**, a method runs interpreted for a few thousand calls, then
silently switches to native. Performance improves with no code changes.

**When something goes wrong**, the JVMs deoptimization mechanism reverts the
native method back to the interpreter — if, for example, a new subclass is loaded
that violates a previous type assumption. This is transparent but causes a temporary
performance dip.

---

### 🔄 The Complete Picture — End-to-End Flow

```
┌─────────────────────────────────────────────┐
│         JAVA EXECUTION FLOW                 │
├─────────────────────────────────────────────┤
│  [.java source]                             │
│       ↓ javac                              │
│  [.class bytecode]                          │
│       ↓ ClassLoader                        │
│  [Loaded class in JVM]                      │
│       ↓                                     │
│  [Interpreter] ← YOU ARE HERE              │
│  Counts calls, records type profiles        │
│       ↓ threshold crossed                  │
│  [JIT Compiler] ← YOU ARE HERE             │
│  Builds IR, optimises, emits native code   │
│       ↓                                     │
│  [Code Cache]                               │
│  Native code stored, method stub patched   │
│       ↓                                     │
│  [Direct CPU execution — no interpreter]   │
└─────────────────────────────────────────────┘
```

**FAILURE PATH:**
New class loaded → violates type assumption → Deoptimization trap fires →
method reverts to interpreter → profile rebuild starts → re-compile later.
Observable symptom: CPU spike + temporary throughput drop.

**WHAT CHANGES AT SCALE:**
At 1000x load, Code Cache exhaustion becomes a real risk — the JVM runs out of
space for compiled methods and falls back to interpretation entirely (a cliff-edge
performance collapse). Under extreme concurrency, CompilerThread contention can
delay compilations, extending the warm-up window significantly.

---

### 💻 Code Example

```java
// Example 1 — Observing JIT warm-up effect
public class JitWarmup {
    static long compute(int n) {
        long sum = 0;
        for (int i = 0; i < n; i++) sum += i;
        return sum;
    }

    public static void main(String[] args) {
        // First 10k calls: interpreted (slow)
        for (int i = 0; i < 10_000; i++) compute(1000);

        // After threshold: JIT-compiled (fast)
        long start = System.nanoTime();
        for (int i = 0; i < 100_000; i++) compute(1000);
        System.out.println(
            "Hot: " + (System.nanoTime() - start) / 1_000_000 + " ms"
        );
    }
}
```

```java
// Example 2 — Megamorphic call site prevents inlining (BAD)
// JIT can't inline virtual calls with 3+ implementors
interface Transformer { int transform(int x); }
class A implements Transformer { public int transform(int x){return x*2;} }
class B implements Transformer { public int transform(int x){return x+1;} }
class C implements Transformer { public int transform(int x){return x-1;} }

// BAD: 3 different types → megamorphic → JIT won't inline
void process(List<Transformer> list) {
    for (Transformer t : list) t.transform(5); // no inlining
}

// GOOD: keep call sites bimorphic (≤ 2 types)
// or use concrete classes instead of interface where performance matters
```

```java
// Example 3 — JVM flags to observe JIT activity
// Run with: -XX:+PrintCompilation -XX:+CITime
// -XX:+PrintCompilation shows:
//   [timestamp] [compile_id] [flags] method_name @ bytecode_size
// e.g.:
//   247   42 % com.example.App::hotMethod @ 14 (82 bytes)
//   ^     ^  ^  class::method            ^   bytecode size
//   ms    id flags(% = OSR)              loop-back offset
```

---

### ⚖️ Comparison Table

| Mode                 | Startup        | Throughput | Optimization Quality       | Best For                            |
| -------------------- | -------------- | ---------- | -------------------------- | ----------------------------------- |
| **JIT (C2)**         | Slow (warm-up) | Maximum    | Excellent (profile-guided) | Long-running servers                |
| Interpreter only     | Fast           | Poor       | None                       | Tiny scripts, serverless cold start |
| JIT (C1 only)        | Medium         | Good       | Good (no speculation)      | Short-lived apps                    |
| AOT (GraalVM Native) | Instant        | High       | Good (static PGO)          | Containers, CLI, FaaS               |
| Tiered (C1→C2)       | Medium         | Maximum    | Excellent                  | General purpose Java                |

**How to choose:** For server applications running > 30 seconds, tiered JIT (default)
delivers the best throughput. For containerized microservices with frequent cold starts,
GraalVM Native Image (AOT) eliminates warm-up entirely at the cost of some peak throughput.

---

### ⚠️ Common Misconceptions

| Misconception                   | Reality                                                                                                                                     |
| ------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------- |
| JIT always makes Java faster    | JIT hurts startup performance — the first minutes run at interpreted speed; only long-running processes fully benefit                       |
| JIT compiles everything         | Only hot methods above the compilation threshold get compiled; most code stays interpreted forever                                          |
| JIT compiles once, runs forever | JIT can deoptimize and recompile the same method multiple times as type profiles change                                                     |
| More inlining is always better  | Excessive inlining inflates code size, causing instruction-cache misses that hurt performance                                               |
| JIT and AOT are equivalent      | AOT lacks runtime profile data — it cannot speculatively devirtualize or perform type-based optimization                                    |
| Code Cache is unlimited         | Code Cache has a fixed size (default 240MB); when full, JVM logs "CodeCache is full — compiler has been disabled" and performance collapses |

---

### 🚨 Failure Modes & Diagnosis

**Code Cache Exhaustion**

Symptom:
Log contains `CodeCache is full. Compiler has been disabled.` Performance
drops dramatically as all execution reverts to interpretation.

Root Cause:
Code Cache filled up due to too many compiled methods. Often triggered by
frameworks that generate lots of dynamic classes (Spring, Hibernate proxies).

Diagnostic Command / Tool:

```bash
jcmd <pid> VM.native_memory | grep -A3 "Code"
# or JVM flag at startup:
-XX:+PrintCodeCache
# Output: CodeCache: size=245760Kb used=189432Kb
```

Fix:

```bash
# BAD: default (may be too small for large apps)
# GOOD: increase Code Cache at startup
-XX:ReservedCodeCacheSize=512m
-XX:+UseCodeCacheFlushing  # enables LRU eviction
```

Prevention:
Profile Code Cache usage in staging before production, and set
`ReservedCodeCacheSize` appropriately for your framework's proxy generation volume.

---

**JIT Deoptimization Storm**

Symptom:
`-XX:+PrintDeoptimization` logs flood with deoptimization events. CPU spikes
on CompilerThreads. Throughput drops 50% then recovers after 10–30 seconds.

Root Cause:
A new class loaded at runtime violated a previous type assumption. All methods
that speculatively inlined the old assumption are deoptimized simultaneously.

Diagnostic Command / Tool:

```bash
java -XX:+PrintDeoptimization -XX:+PrintCompilation MyApp 2>&1 \
  | grep -i "deoptimiz"
# Shows: deoptimized method, reason, type (e.g., "not_entrant")
```

Fix:
Avoid loading new class implementations (plugins, hot-reload) under production
load. If required, batch the loading and allow recompilation to settle.

Prevention:
Keep the set of loaded classes stable under steady-state load.

---

**Warm-up Blindness in Performance Tests**

Symptom:
Benchmark shows Java is 10× slower than C++. But only the first 5 seconds
are being measured — before JIT has compiled the hot paths.

Root Cause:
Missing JIT warm-up phase in the benchmark design.

Diagnostic Command / Tool:

```bash
# Use JMH (Java Microbenchmark Harness) which handles warm-up automatically
# Or observe JIT activity during test:
-XX:+PrintCompilation 2>&1 | grep -v "^$" | wc -l
# Count compilation events — test should run no compilations after warm-up
```

Fix:

```java
// BAD: measure from cold start
long t = System.nanoTime(); hotMethod(); // still interpreted!

// GOOD with JMH:
@Warmup(iterations = 5)
@Measurement(iterations = 10)
@State(Scope.Benchmark)
public class MyBenchmark {
    @Benchmark
    public long measure() { return hotMethod(); }
}
```

Prevention:
Always use JMH or equivalent harness for Java micro-benchmarks. Never
benchmark without explicit warm-up iterations.

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**

- `JVM` — JIT is a subsystem of the JVM; understanding the JVM's execution model is required
- `Bytecode` — JIT compiles bytecode to native code; must understand what bytecode is
- `Class Loader` — Classes must be loaded before JIT can profile and compile them

**Builds On This (learn these next):**

- `C1 / C2 Compiler` — the two specific JIT compiler tiers and their trade-offs
- `Tiered Compilation` — the strategy of using C1 for fast compile, C2 for peak optimization
- `Method Inlining` — the single most impactful JIT optimization; enabled by JIT
- `Deoptimization` — JIT's mechanism for reverting speculative assumptions
- `OSR (On-Stack Replacement)` — JIT's ability to compile and swap in code for a running loop

**Alternatives / Comparisons:**

- `AOT (Ahead-of-Time Compilation)` — compiles before running; no warm-up but loses runtime profile data
- `GraalVM` — alternative JIT/AOT implementation with superior optimization pipeline

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ WHAT IT IS   │ Runtime bytecode-to-native compiler        │
├──────────────┼───────────────────────────────────────────┤
│ PROBLEM IT   │ Interpreted bytecode is 10–100× slower     │
│ SOLVES       │ than native machine code                   │
├──────────────┼───────────────────────────────────────────┤
│ KEY INSIGHT  │ Compiles with runtime profile data —       │
│              │ impossible for static compilers            │
├──────────────┼───────────────────────────────────────────┤
│ USE WHEN     │ Any long-running Java server application   │
├──────────────┼───────────────────────────────────────────┤
│ AVOID WHEN   │ Serverless cold-start sensitive workloads  │
│              │ (use GraalVM Native Image instead)         │
├──────────────┼───────────────────────────────────────────┤
│ TRADE-OFF    │ Peak throughput vs warm-up latency         │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "JIT wins by watching before it compiles"  │
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ C1/C2 Compiler → Tiered Compilation        │
│              │ → Method Inlining → Deoptimization         │
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** A JIT-compiled method for a polymorphic call site was optimised
assuming only `ArrayList` was ever passed. Halfway through a production
deployment, a new library starts passing `LinkedList` to the same method.
Trace exactly what happens: which JVM mechanism fires, what performance
profile you'd observe in metrics, and how long recovery takes.

**Q2.** GraalVM's JIT compiler consistently outperforms HotSpot's C2 on
numeric-heavy benchmarks, yet most Java shops still use HotSpot. If JIT
performance is a first-principles optimization problem, what constraints
prevent every engineering team from simply switching to GraalVM, and under
what specific conditions does the switch become the clearly correct decision?
