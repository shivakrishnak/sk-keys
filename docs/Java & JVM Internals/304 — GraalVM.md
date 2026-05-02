---
layout: default
title: "GraalVM"
parent: "Java & JVM Internals"
nav_order: 304
permalink: /java/graalvm/
number: "0304"
category: Java & JVM Internals
difficulty: ★★★
depends_on:
  - JIT Compiler
  - AOT (Ahead-of-Time Compilation)
  - JVM
  - Bytecode
  - C1 / C2 Compiler
used_by:
  - Native Image
related:
  - Native Image
  - AOT (Ahead-of-Time Compilation)
  - JIT Compiler
  - C1 / C2 Compiler
tags:
  - jvm
  - graalvm
  - performance
  - java-internals
  - deep-dive
---

# 0304 — GraalVM

⚡ TL;DR — GraalVM is a high-performance JDK that replaces HotSpot's C2 compiler with a Java-written Graal JIT, adds AOT native image compilation, and enables polyglot execution of multiple languages on a single runtime.

| #0304 | Category: Java & JVM Internals | Difficulty: ★★★ |
|:---|:---|:---|
| **Depends on:** | JIT Compiler, AOT (Ahead-of-Time Compilation), JVM, Bytecode, C1 / C2 Compiler | |
| **Used by:** | Native Image | |
| **Related:** | Native Image, AOT Compilation, JIT Compiler, C1 / C2 Compiler | |

### 🔥 The Problem This Solves

WORLD WITHOUT IT:
HotSpot JVM's C2 compiler is written in C++ and is extremely difficult to extend, debug, or analyze. Adding new JIT optimizations requires deep C++ expertise, full knowledge of HotSpot internals, and months of work per optimization. The research community and cloud providers wanted better JIT performance (especially for long-running cloud services), polyglot language support, and the ability to compile Java to native executables — but C2's architecture made all of this prohibitively hard.

THE BREAKING POINT:
Oracle's JVM team wanted to add escape analysis improvements, vector API support, and memory access intrinsics to C2. Each change required weeks of work from rare C++ JVM experts. Meanwhile, GraalVM research (started by Thomas Würthinger at Oracle Labs, Zurich) demonstrated that a JIT compiler written in Java could be optimized by itself — using speculative optimizations that a JIT uniquely enables for its own compilation. This "JIT compiling the JIT" concept was uniquely powerful.

THE INVENTION MOMENT:
This is exactly why **GraalVM** was created — to build a new generation JIT compiler in Java (using the JVMCI interface), enabling faster iteration on compiler optimizations, native image compilation, polyglot language support, and ultimately better performance than C2 for many workloads.

### 📘 Textbook Definition

**GraalVM** is an Oracle-developed, high-performance JDK distribution and compiler project with three main components: (1) the **Graal JIT compiler** — a Java-written JIT that replaces C2 as the Tier 4 optimizer, accessible via the JVMCI (JVM Compiler Interface — JEP 243), delivering equal or better peak throughput than C2 for many workloads; (2) **Native Image** — an AOT compilation toolchain using Graal as the backend, producing self-contained native binaries with sub-100ms startup; (3) **Truffle** — a language implementation framework that allows any language (Python, Ruby, R, WebAssembly, LLVM-IR) to be implemented as an interpreter that GraalVM then JIT-optimizes transparently through partial evaluation.

### ⏱️ Understand It in 30 Seconds

**One line:**
GraalVM is a next-generation JDK where the JIT compiler is written in Java — so it can compile itself and be extended by any Java developer.

**One analogy:**
> Imagine a programming language where the compiler is written in the same language it compiles. This allows the compiler to improve itself (bootstrapping). GraalVM does this for Java JIT: the Graal compiler is Java code, compiled by Graal itself, making Graal faster the better Java code it produces — a virtuous cycle impossible for C2.

**One insight:**
The deepest insight about GraalVM is that writing the JIT in Java enables *partial evaluation*: GraalVM can JIT-compile Truffle language interpreters into near-native code by treating the interpreter as a *specialization problem*. When a Python loop runs in GraalVM's CPython interpreter, GraalVM partially evaluates the Python byte­code against the interpreter source code — effectively inlining away the entire interpreter dispatch loop and producing native code equivalent to hand-written C. This is called the *First Futamura Projection*, and it is what makes Truffle languages competitive with native implementations.

### 🔩 First Principles Explanation

CORE INVARIANTS:
1. A JIT compiler written in a high-level language (Java) is easier to extend than one written in C++.
2. A JIT that is itself JIT-compiled has an unusual advantage: the compiler can optimize itself using the same runtime profiling it provides to other code.
3. A universal intermediate representation (IR) can bridge multiple source languages to a single optimizer/code generator.

DERIVED DESIGN:
GraalVM's architecture has three layers:

**Layer 1 — Graal JIT (JVMCI-based):**
The Graal compiler implements the JVMCI interface (Java VM Compiler Interface), an API that allows plugging a custom JIT compiler into the JVM. Graal's IR is a Sea of Nodes graph (same conceptual IR as C2, but implemented in Java). Graal adds new optimizations C2 lacks: more aggressive speculative inlining, better partial escape analysis, and iterative loop optimization.

**Layer 2 — SubstrateVM (for Native Image):**
A minimal Java runtime (GC, thread management, signal handling) implemented in Java using Graal's AOT compilation. SubstrateVM provides exactly the runtime services needed at native image runtime without a full JVM.

**Layer 3 — Truffle:**
An AST-interpreting framework where each language (Python, Ruby, JS) writes their interpreter as a Java Truffle AST. GraalVM's partial evaluator "specializes" this interpreter to the specific program being run, using the real-time profile of which AST nodes are hot. The result: a Truffle language interpreter achieves performance within 2–3x of hand-optimized native code — sometimes faster for specific workloads.

```
┌──────────────────────────────────────────────────┐
│           GraalVM Architecture                   │
│                                                  │
│  Java/Kotlin/Scala source                        │
│         ↓                                        │
│  javac → bytecode                                │
│         ↓ (on JVM)                               │
│  [JVMCI] → [Graal JIT] → native code            │
│                  ↑                               │
│         Same Graal compiles itself               │
│                                                  │
│  Python/Ruby/JS source                           │
│         ↓                                        │
│  [Truffle interpreter] → AST                     │
│                  ↓                               │
│  [Graal partial evaluator] → native code         │
│                                                  │
│  Any of the above → [Native Image] → binary      │
└──────────────────────────────────────────────────┘
```

THE TRADE-OFFS:
Gain: Better JIT performance in certain scenarios; native image support; polyglot languages with near-native performance; extensible in Java.
Cost: Graal JIT compilation itself takes more CPU/memory than C2 for equivalent methods; startup time for Graal JIT mode is slightly higher than HotSpot default; Native Image has dynamic Java feature restrictions; Truffle language startup is slower than their native counterparts.

### 🧪 Thought Experiment

SETUP:
Two JVMs process a machine learning workload: 10 million matrix multiplications, each using a 100x100 double array.

HOTSPOT C2:
C2 compiles the inner loop efficiently but uses a conservative alias analysis. The loop body: 2–3 SIMD vector instructions per iteration, handles possible overlap assumptions.

GRAAL JIT:
Graal's more aggressive alias analysis determines the arrays cannot overlap (more precise points-to). Generates wider SIMD instructions (512-bit AVX-512 vs C2's 256-bit AVX2). Result: 40% more throughput for this specific workload.

SAME WORKLOAD IN TRUFFLE PYTHON:
Without GraalVM: CPython interprets Python code at ~1000 ns/matrix multiplication.
With GraalVM's Truffle: GraalVM partially evaluates the numpy-like Python operations, generating similar SIMD code to the Java version. Result: ~20 ns/matrix multiplication — 50x faster than CPython for this hot loop.

THE INSIGHT:
GraalVM's value is not uniform — it shines in specific scenarios (numeric computation, polyglot workloads) and may not improve (or may slightly regress) simpler CRUD-style Java workloads where C2 is already near-optimal.

### 🧠 Mental Model / Analogy

> GraalVM is like a universal translator that speaks all programming languages and is itself written in a language it can translate — allowing it to improve its own translation speed. The three parts: a better English-to-machine-code translator (Graal JIT replacing C2), the ability to pre-translate books before publishing (Native Image), and universal language support that translates any language to the same high-quality machine translation engine (Truffle).

"Better English-to-machine-code" → Graal JIT compiler.
"Pre-translate books" → AOT Native Image.
"Universal language support" → Truffle framework.
"Written in a language it can translate" → Graal JIT compiles itself.

Where this analogy breaks down: Unlike a universal translator, GraalVM's polyglot support is not seamless — there is interop overhead when crossing language boundaries (Java↔Python objects), and not all Java libraries are accessible from Truffle languages without interop layer work.

### 📶 Gradual Depth — Four Levels

**Level 1 — What it is (anyone can understand):**
GraalVM is a supercharged version of Java that also runs other programming languages, compiles Java to native executables, and has a better-performing internal optimizer. Think of it as the next-generation JVM that does everything the standard JVM does, plus more.

**Level 2 — How to use it (junior developer):**
Download GraalVM JDK from `graalvm.io` or via SDKMAN (`sdk install java 21.0.2-graal`). For most Java apps, just replacing the JDK with GraalVM works — the Graal JIT runs transparently. For native image, use `native-image` command. For polyglot: use GraalVM SDK's `org.graalvm.polyglot.Context` API to run Python/JS/Ruby code from Java.

**Level 3 — How it works (mid-level engineer):**
The Graal JIT is activated via Java's JVMCI (JVM Compiler Interface) by passing `-XX:+UseJVMCICompiler` to the JVM. JVMCI allows replacing the C2 Tier 4 compiler with a custom implementation. Graal's IR is a subgraph of `Node` objects in Java — each `Node` represents an operation or value. The compiler runs optimization `Phase` objects over the graph: inlining, escape analysis, loop transformations, etc. Because Graal is Java code, adding a new optimization phase is writing a Java class that transforms the graph.

**Level 4 — Why it was designed this way (senior/staff):**
The JVMCI interface is the architectural lynchpin — it allowed Graal to be developed *outside* the JVM codebase (in a separate GitHub repository `oracle/graal`) while still plugging into the JVM. This separation enabled Oracle Labs to iterate on compiler research independently from HotSpot maintenance. The same Graal codebase serves three roles: JIT (via JVMCI), AOT backend (for native-image), and Truffle partial evaluator. This sharing is architecturally significant: improvements to Graal's optimizer benefit all three use cases simultaneously. The open-source licensing of GraalVM Community Edition while maintaining GraalVM Enterprise Edition (with additional optimizations) creates an interesting ecosystem dynamic where community users benefit from research advances, while enterprise features fund continued development.

### ⚙️ How It Works (Mechanism)

**Graal JIT Activation:**
```bash
# Enable Graal as Tier 4 JIT compiler:
java -XX:+UnlockExperimentalVMOptions \
     -XX:+UseJVMCICompiler \
     -jar myapp.jar
# Or: use GraalVM JDK directly (Graal is default JIT)
```

**Graal Compiler Phase Pipeline:**
```
[Bytecode → StructuredGraph (Sea-of-Nodes IR)]
    ↓
[Phase: CanonicalizerPhase (constant folding, strength reduction)]
    ↓
[Phase: InliningPhase (profile-guided, speculative)]
    ↓
[Phase: PartialEscapeAnalysis (scalar replacement)]
    ↓
[Phase: LoopTransformations (unrolling, vectorization)]
    ↓
[Phase: LowTier (machine-specific lowering)]
    ↓
[Phase: RegisterAllocation (linear scan)]
    ↓
[Native code in code cache]
```

**Truffle Partial Evaluation:**
```java
// A simple Truffle language interpreter node:
@NodeInfo(language = "SimpleCalc")
public class AddNode extends CalcNode {
    @Child CalcNode left;
    @Child CalcNode right;

    @Override
    @Specialization  // Truffle auto-specializes for types
    protected long add(long l, long r) { return l + r; }
}
// Graal's PE sees: left=always long, right=always long
// Specializes: removes all dispatch, inlines add directly
// Result: AddNode PE'd to 1 assembly instruction
```

**Polyglot API:**
```java
try (Context ctx = Context.create()) {
    ctx.eval("python", "print('Hello from Python')");
    Value pyResult = ctx.eval("python",
        "import math; math.sqrt(42.0)");
    double result = pyResult.asDouble(); // 6.48...
}
// Python code JIT-compiled by Graal via Truffle
```

### 🔄 The Complete Picture — End-to-End Flow

JIT MODE:
```
[Java source] → [javac] → [bytecode]
    → [JVM starts with -XX:+UseJVMCICompiler]
    → [HotSpot interpreter + C1 (Tiers 0-3)]
    → [Hot method → JVMCI handoff to Graal]  ← YOU ARE HERE
    → [Graal JIT: parse → optimize → emit]
    → [Better native code than C2 in some cases]
```

NATIVE IMAGE MODE:
```
[bytecode + libraries]
    → [native-image builds with Graal AOT backend]
    → [Points-to analysis]    ← YOU ARE HERE (build time)
    → [Whole-program Graal compilation]
    → [SubstrateVM linking]
    → [Native binary: ./myapp]
```

FAILURE PATH:
```
[Graal JIT runs out of time/memory for complex method]
    → [Falls back to C1 compiled code]
    → [Logs: "graal compilation failed, falling back"]
[Native image: missing reflection config]
    → [Runtime ClassNotFoundException]
    → [Fix: native-image-agent]
```

WHAT CHANGES AT SCALE:
GraalVM JIT mode uses more memory per compilation than C2 (more optimization phases, Java heap for compiler state). At scale on memory-constrained containers, this can cause GraalVM compilation threads to pressure the heap. On large instances (16+ cores), Graal's compilation thread count scales better than C2, giving higher aggregate JIT throughput.

### 💻 Code Example

Example 1 — Enabling Graal JIT in HotSpot JVM:
```bash
# Works with standard JDK 17+:
java -XX:+UnlockExperimentalVMOptions \
     -XX:+UseJVMCICompiler \
     -XX:+EagerJVMCI \
     -Djvmci.Compiler=graal \
     -jar myapp.jar

# Check Graal is active:
java -XX:+UseJVMCICompiler -version
# Output: GraalVM CE ...
```

Example 2 — Simple polyglot: calling Python from Java:
```java
import org.graalvm.polyglot.*;

public class PolyglotExample {
    public static void main(String[] args) {
        try (Context ctx = Context.newBuilder()
                .allowAllAccess(true).build()) {

            // Execute Python code:
            ctx.eval("python", 
                "import numpy as np; arr = np.array([1,2,3])");

            // Call Python function from Java:
            Value fn = ctx.eval("python", 
                "(lambda x: x * x)");
            System.out.println(fn.execute(7).asInt()); // 49
        }
    }
}
```

Example 3 — Checking if Graal JIT is compiling a method:
```bash
# With GraalVM JDK, print compilation info:
java -Dgraal.PrintCompilation=true \
     -XX:+UseJVMCICompiler \
     -jar myapp.jar 2>&1 | grep "HotSpotCompilation"

# Output:
# HotSpotCompilation[id=42, method=com.example.Hot.process,
# osr_bci=-1, level=4, ...]
```

Example 4 — Benchmarking Graal vs C2:
```bash
# Run the same JMH benchmark with C2 and Graal:
java -jar benchmarks.jar -f 2 -wi 5 -i 10 \
     -jvmArgs "-XX:-UseJVMCICompiler" \
     MatrixMultiplyBenchmark

java -jar benchmarks.jar -f 2 -wi 5 -i 10 \
     -jvmArgs "-XX:+UseJVMCICompiler" \
     MatrixMultiplyBenchmark

# Compare results for numeric compute vs CRUD workloads
```

### ⚖️ Comparison Table

| Component | What It Does | When to Use |
|---|---|---|
| **Graal JIT** | Replaces C2 for Tier 4 compilation | Numeric compute, long-running services needing max throughput |
| **Native Image** | AOT compilation to native binary | Serverless, CLIs, cold-start-critical services |
| **Truffle** | Polyglot language runtime | Embedding Python/JS/Ruby in Java services |
| **SubstrateVM** | Minimal Java runtime for native image | Automatically used with Native Image |
| **HotSpot + C2** | Default JIT | General-purpose Java services, maximum compatibility |
| **GraalVM Community** | Free tier: Graal JIT + Native Image | Open-source projects, general adoption |
| **GraalVM Enterprise** | All above + advanced GC + PGO + profiling | Mission-critical, highest performance |

How to choose: Start with GraalVM JDK as a drop-in JDK replacement — it is backward-compatible. Add native image only when startup or memory is a constraint. Truffle when you need polyglot.

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| GraalVM is always faster than HotSpot | Graal JIT is better for numeric/compute workloads; for typical CRUD services, the performance difference is small (±5%). Some workloads are slightly slower due to Graal's higher compilation CPU cost |
| GraalVM is only for native image | GraalVM's most impactful feature for most services is the Graal JIT compiler in JVM mode, not native image |
| GraalVM replaces the JVM | GraalVM includes a JVM (it is a JDK, not a replacement). In JIT mode, it runs on the HotSpot JVM with Graal as the JIT compiler. Native Image builds don't need the JVM at runtime, but still need it at build time |
| Truffle languages are Java | Truffle languages (Python, Ruby) run on GraalVM but are separate implementations. GraalPython is not CPython + Java bindings — it is a Python implementation built using Truffle |
| GraalVM CE and EE have the same performance | GraalVM Enterprise includes additional advanced optimizations (more aggressive inlining, improved GC, PGO) that measurably exceed GraalVM CE for throughput-intensive workloads |
| GraalVM is production-ready for all use cases | GraalVM is production-ready as a JDK for Java. Native Image has framework constraints (Spring Boot 3+ is well-supported, many older libraries are not). Truffle languages are production-ready for specific high-value use cases |

### 🚨 Failure Modes & Diagnosis

**Graal JIT Uses Too Much CPU During Compilation**

Symptom:
Application under load shows spikes in CPU. Profiling identifies `JVMCI compiler thread` as the consumer. Memory pressure increases.

Root Cause:
Graal compiler itself runs on the Java heap. Compilation of complex methods can consume significant heap and CPU, sometimes more than C2 for equivalent methods.

Diagnostic Command / Tool:
```bash
# Check JIT compilation overhead with JFR:
jcmd <pid> JFR.start name=graal_jit duration=60s \
  filename=graal.jfr

# In JMC: JVM Internals → Compilations
# Compare: Graal compilation time vs HotSpot

# Switch back to C2 if Graal compilation is too expensive:
java -XX:-UseJVMCICompiler ...
```

Fix:
For CPU-constrained containers, C2 may be preferable to Graal JIT. For throughput-focused large instances, Graal's CPU spend pays off with better native code.

Prevention:
Benchmark both Graal and C2 under production-realistic load before committing to Graal JIT for a service.

---

**Native Image: Missing Class in Closed-World Analysis**

Symptom:
`native-image` build success. Runtime: `com.example.PluginLoader: class not found`.

Root Cause:
`PluginLoader` uses reflection to load classes by name at runtime. The class names are strings — the static analysis cannot determine which classes will be loaded.

Diagnostic Command / Tool:
```bash
# Run with agent to capture missing reflection:
java -agentlib:native-image-agent=\
  config-output-dir=src/main/resources/META-INF/native-image/ \
  -jar myapp.jar
# Run all tests + integration tests under agent
```

Fix:
Add generated config files to the build. For dynamic plugin loading: use GraalVM's resource configuration or embed a list of allowed plugin class names in the config.

Prevention:
Include `native-image-agent` execution in CI as part of the build pipeline.

---

**Truffle Language Context Memory Leak**

Symptom:
Polyglot application's heap grows without bound. JVM metrics show Context objects accumulating.

Root Cause:
`Context` objects must be explicitly closed. If Java code creates a new `Context` per request without `try-with-resources`, each Context leaks Truffle language state.

Diagnostic Command / Tool:
```bash
jmap -histo:live <pid> | grep Context
# Shows com.oracle.truffle.api.*Context count growing
```

Fix:
```java
// BAD: Context never closed
Value result = Context.create().eval("python", code);

// GOOD: Always use try-with-resources
try (Context ctx = Context.create()) {
    Value result = ctx.eval("python", code);
    // use result...
}  // context closed, resources freed
```

Prevention:
Code review: all `Context.create()` calls must be in `try-with-resources`. Add Checkstyle rule.

### 🔗 Related Keywords

**Prerequisites (understand these first):**
- `JIT Compiler` — GraalVM's core value proposition is a better JIT; full JIT understanding is prerequisite
- `AOT (Ahead-of-Time Compilation)` — GraalVM Native Image is an AOT implementation; understanding AOT concepts is necessary
- `C1 / C2 Compiler` — Graal JIT replaces C2; understanding what C2 does clarifies what Graal improves

**Builds On This (learn these next):**
- `Native Image` — the primary production use case for GraalVM; the next entry covers it in depth

**Alternatives / Comparisons:**
- `C1 / C2 Compiler` — HotSpot's default JIT; the established alternative with broader framework support
- `AOT (Ahead-of-Time Compilation)` — GraalVM Native Image IS an AOT implementation; the two entries are complementary

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ WHAT IT IS   │ JDK with Java-written JIT (Graal),        │
│              │ native image AOT, and polyglot runtime    │
├──────────────┼───────────────────────────────────────────┤
│ PROBLEM IT   │ C2 is hard to extend; JVM bad for cold-   │
│ SOLVES       │ start; polyglot languages need fast rntm  │
├──────────────┼───────────────────────────────────────────┤
│ KEY INSIGHT  │ Writing the JIT in Java means it can be   │
│              │ compiled by itself — improving the JIT    │
│              │ improves its own performance (bootstrap)  │
├──────────────┼───────────────────────────────────────────┤
│ USE WHEN     │ Numeric-heavy Java; serverless; embedding │
│              │ Python/JS/Ruby in Java services           │
├──────────────┼───────────────────────────────────────────┤
│ AVOID WHEN   │ Libraries incompatible with native image; │
│              │ teams unfamiliar with closed-world model  │
├──────────────┼───────────────────────────────────────────┤
│ TRADE-OFF    │ Better optimizations vs more compiler CPU │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "A compiler that improves itself because  │
│              │  it's written in the language it compiles"│
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ Native Image → Truffle → Spring Native    │
└──────────────────────────────────────────────────────────┘
```

---
### 🧠 Think About This Before We Continue

**Q1.** GraalVM's Truffle framework achieves near-native performance for language interpreters through partial evaluation — treating the interpreter as a specialization problem. A bank runs both Java and Python code in the same JVM via GraalVM's polyglot Context API. A Python risk model and a Java pricing engine need to share large arrays without copying. Describe the exact interop mechanism GraalVM uses for zero-copy array sharing between Java and Python code, and what guarantees (and limits) exist around GC interaction with objects that are shared across language contexts.

**Q2.** Oracle maintains both GraalVM Community Edition (free, open-source) and GraalVM Enterprise Edition (commercial). CE uses Serial GC as the default native image GC; EE includes G1GC for native image. Design a production decision framework — as a CTO making a buy/build decision for a serverless-heavy Java microservices fleet — that evaluates the ROI of GraalVM EE vs GraalVM CE, considering compilation time, throughput, pause latencies, licensing cost, and operational overhead. What workload characteristics would definitively tip the decision toward EE?

