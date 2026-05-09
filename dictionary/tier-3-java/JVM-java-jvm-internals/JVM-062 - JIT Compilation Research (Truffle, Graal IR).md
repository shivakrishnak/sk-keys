---
id: JVM-062
title: "JIT Compilation Research (Truffle, Graal IR)"
category: Java & JVM Internals
tier: tier-3-java
folder: JVM-java-jvm-internals
difficulty: ★★★
depends_on: JVM-041, JVM-042, JVM-043
used_by:
related: JVM-044, JVM-045, JVM-046, JVM-048
tags:
  - jvm
  - java
  - jit
  - internals
  - advanced
status: complete
version: 1
layout: default
parent: "Java & JVM Internals"
grand_parent: "Technical Dictionary"
nav_order: 62
permalink: /jvm/jit-compilation-research-truffle-graal-ir/
---

# JVM-062 - JIT Compilation Research (Truffle, Graal IR)

**⚡ TL;DR** - Graal IR (sea-of-nodes graph) and the Truffle AST interpreter framework represent the current state of JIT research: one delivers better JVM code quality, the other enables any language to run at near-Java speed on the JVM.

| Field | Value |
|---|---|
| **Depends on** | [[JVM-041 - JIT Compiler]], [[JVM-042 - C1 and C2 Compiler]], [[JVM-043 - Tiered Compilation]] |
| **Used by** | (none - research entry) |
| **Related** | [[JVM-044 - Method Inlining]], [[JVM-045 - Deoptimization]], [[JVM-046 - OSR (On-Stack Replacement)]], [[JVM-048 - GraalVM]] |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
HotSpot's C2 compiler (written in C++) is one of the most complex components of the JVM. Making improvements to it requires deep C++ expertise and intimate knowledge of C2's internal IR. New optimisations take months to implement. The compiler is a bottleneck for JVM performance improvements.

**THE BREAKING POINT:**
In 2012, researchers at Oracle Labs asked: what if the JIT compiler itself was written in Java? A Java JIT compiler could be maintained more easily, tested with standard Java tools, and improved by Java developers rather than only systems programmers. This question led to the Graal compiler project.

**THE INVENTION MOMENT:**
Graal IR introduced a "sea-of-nodes" intermediate representation (IR) where control flow and data flow are unified in a single graph, rather than being separate structures as in C2. This unified representation enables more powerful optimisations - particularly conditional eliminations and combined control+data optimisations - that are architecturally difficult in C2's separate SSA + CFG design.

**EVOLUTION:**
- 2012: Graal project starts at Oracle Labs (Java-written JIT)
- 2014: Truffle framework published (language-agnostic AST interpreter)
- 2016: GraalVM concept: one VM, many languages
- 2019: GraalVM CE 19.0 released (open source)
- 2020: JVMCI (JVM Compiler Interface) shipped in OpenJDK - enables Graal as JIT
- 2021: Graal JIT included in OpenJDK experimental (`-XX:+UseJVMCICompiler`)
- 2022: Project Mandrel - GraalVM Native Image without full GraalVM
- 2023: Oracle GraalVM free for production (GFTC licence)

---

### 📘 Textbook Definition

**Graal IR** is the intermediate representation used by the Graal JIT compiler. It uses a sea-of-nodes (or "click nodes") graph structure where both data dependencies and control dependencies are represented as edges in a single directed graph. This enables unified optimisation passes over both control and data flow. **The Truffle framework** is a Java API for building language interpreters (ASTs) that, when executed on GraalVM, are automatically partially evaluated and JIT-compiled by the Graal compiler - enabling interpreted languages to achieve near-native performance without writing a custom compiler. **JVMCI (JVM Compiler Interface)** is the JDK API that allows plugging an external JIT compiler (such as Graal) into HotSpot, replacing C2 for tier-4 (optimised) compilations.

---

### ⏱️ Understand It in 30 Seconds

**One line:** Graal rewrites the JIT in Java for better optimisations; Truffle makes any language fast on the JVM via partial evaluation.

> Like replacing a car's engine with a more powerful one built using modern tools: the chassis (JVM) stays the same, but the engine (JIT compiler) is rebuilt in a more maintainable material (Java instead of C++) with a better internal design (sea-of-nodes IR) and can now power different vehicle types (languages via Truffle).

**One insight:** Truffle's core insight is that a language interpreter, when written as a Java AST and run on GraalVM, can be "partially evaluated" - the interpreter overhead is compiled away, and only the interpreted program's code remains in the compiled output. This makes interpreter overhead nearly zero.

---

### 🔩 First Principles Explanation

**CORE INVARIANTS:**
1. A JIT compiler is just software; it can be written in any language
2. Partial evaluation: given a program and some of its inputs, produce a specialised residual program that runs faster for those inputs
3. An AST interpreter is a program; Truffle partially evaluates it to produce code for the interpreted program
4. Sea-of-nodes IR enables optimisation passes that see both data and control flow simultaneously

**DERIVED DESIGN:**
From invariant 1: writing the JIT in Java enables testing with JUnit, profiling with JFR, and maintenance by Java developers. JVMCI is the hook that plugs this Java JIT into HotSpot.
From invariant 2+3: Truffle's partial evaluation means writing a correct (but slow) language interpreter is sufficient. GraalVM then makes it fast automatically, without requiring the language designer to write machine code generation.
From invariant 4: sea-of-nodes allows an optimisation like "constant folding" to eliminate a branch even when the branch condition depends on a value that flows through multiple intermediate nodes.

**THE TRADE-OFFS:**
**Gain:** Better optimised code quality (Graal often generates faster code than C2 for certain patterns); language portability (Truffle languages run on JVM, LLVM, native); Java JIT maintainability
**Cost:** Graal JIT startup cost (Graal itself is JIT-compiled - bootstrapping overhead); Truffle language startup cost (AST specialisation takes time); Graal compilation is slower than C2 for same compilation unit

**ESSENTIAL vs ACCIDENTAL COMPLEXITY:**
**Essential:** Building an optimising compiler is inherently complex - sea-of-nodes IR consolidates this complexity into one structure rather than two (SSA + CFG).
**Accidental:** The bootstrapping problem (a Java JIT compiler that needs to be JIT-compiled before it can JIT-compile your code) adds startup latency. This is an implementation constraint, not an inherent necessity of a Java-written JIT.

---

### 🧪 Thought Experiment

**SETUP:** You want to add a new programming language to the JVM ecosystem. Your language is "SimpleLang" - it has variables, loops, function calls, and arithmetic.

**WITHOUT TRUFFLE:**
You write a SimpleLang compiler that emits JVM bytecode. This takes 6+ months: parsing, AST → bytecode lowering, type inference, stack frame management. Your compiler must handle every JVM bytecode constraint. To get good performance, you need to implement your own inliner, loop unrolling, and escape analysis - all targeting bytecode, before HotSpot even sees it. Then HotSpot still JIT-compiles your bytecode. Total: you write two compilers (source→bytecode, bytecode→native via HotSpot).

**WITH TRUFFLE:**
You write a SimpleLang AST interpreter in Java using the Truffle framework. Total implementation: 3,000 lines of Java covering lexer, parser, and AST evaluator. You annotate nodes with Truffle's `@Specialization` annotations to handle common cases (e.g., integer add vs float add). GraalVM's Truffle layer partially evaluates your interpreter on the fly. Result: SimpleLang programs run at 80-90% of Java speed without writing a single line of machine code generation.

**THE INSIGHT:**
Truffle shifts the compiler work from "language designer must write a compiler" to "JVM does the compilation by partially evaluating the interpreter." Language designers write interpreters (easy); JVM engineers write the partial evaluator once (hard). This unlocks a Cambrian explosion of JVM-hosted languages.

---

### 🧠 Mental Model / Analogy

> Think of Truffle partial evaluation as translation by specialisation. A universal translator (Truffle interpreter framework) can translate any language - but doing so in real time is slow. Now, if you know one specific language in advance, you produce a specialised translator that only handles that language, eliminating all the "switch to detect language type" overhead. GraalVM produces this specialised translator (compiled code) from the universal one (AST interpreter) by freezing the language-specific structure in place.

Element mapping:
- Universal translator = Truffle AST interpreter framework
- Specific language = SimpleLang interpreter nodes
- Specialised translator = GraalVM-compiled native code for SimpleLang
- Partial evaluation = the process of freezing language-specific parts

Where this analogy breaks down: the "specialised translator" (compiled native code) needs to be re-produced for each program being run, not just once per language. Truffle compiles per-function call-site specialisations, not one binary per language.

---

### 📶 Gradual Depth - Four Levels

**Level 1 - What it is (anyone can understand):**
Graal is a new JIT compiler for the JVM, written in Java instead of C++. It produces the same kind of fast machine code as the old compiler but is easier to improve. Truffle is a toolkit that lets someone build a new programming language and have it run fast on the JVM without writing a traditional compiler.

**Level 2 - How to use it (junior developer):**
To use Graal as the JIT compiler:
```bash
# OpenJDK 21+ (experimental)
java -XX:+UnlockExperimentalVMOptions \
     -XX:+UseJVMCICompiler \
     -jar app.jar

# Or: use GraalVM JDK (Graal is default JIT)
sdk install java 21.0.2-graal
java -jar app.jar
```
For Truffle languages: GraalVM ships with JavaScript (GraalJS), Python (GraalPy), Ruby (TruffleRuby), LLVM bitcode interpreter, and WebAssembly interpreter out of the box.

**Level 3 - How it works (mid-level engineer):**
The Graal compiler implements the JVM Compiler Interface (JVMCI). When HotSpot decides to tier-4 compile a method, instead of calling C2, it calls Graal via JVMCI. Graal receives bytecode, constructs a Graal IR graph, runs optimization phases (inlining, constant folding, loop transformations, escape analysis), and emits machine code back to HotSpot. Truffle works differently: a Truffle interpreter is an AST interpreter written using Truffle's node types. When a Truffle node becomes hot, GraalVM's partial evaluator "peeks inside" the interpreter, inlines all the interpreter dispatch logic, and compiles the residual AST-execution code directly. After several specialisation cycles, the compiled code has no interpreter overhead.

**Level 4 - Why it was designed this way (senior/staff):**
Sea-of-nodes IR (Graal's design) differs from traditional CFG+SSA (C2's design) in a fundamental way: in sea-of-nodes, there is no explicit control flow graph. Instead, control dependencies (what must execute before what) are represented as special edges in the same graph as data dependencies. This means an optimisation pass sees both "this value depends on this computation" and "this computation must occur before that one" in a single traversal. The key benefit: "floating" nodes that are not pinned to a specific position in the control flow can be freely moved by the optimiser to the most beneficial position. C2 maintains separate IR structures and must coordinate between them for cross-cutting optimisations - an architectural reason why some optimisations that are natural in sea-of-nodes are difficult in C2.

**Expert Thinking Cues:**
- Use `-Dgraal.ShowConfiguration=info` to see Graal's active optimisations
- Use `-Dpolyglot.log.level=INFO` for Truffle language startup information
- GraalVM Native Image uses Graal as its AOT compiler - same IR, different application

---

### ⚙️ How It Works (Mechanism)

**Graal IR (Sea-of-Nodes):**
```
Traditional IR (C2 style):
  CFG: blocks + control flow edges
  SSA: values + data flow edges (separate)
  Optimisation must correlate both structures

Graal Sea-of-Nodes:
  Single graph: all nodes
  Data edges: value produced -> value consumed
  Control edges: must-execute-before dependency
  Floating nodes: no control anchor (free to move)
  Fixed nodes: anchored to control point

Benefits:
  - Value numbering trivial (same node = same value)
  - Floating nodes optimised to ideal position
  - Combined control+data optimisations natural
```

**JVMCI - Graal as Hot Spot JIT:**
```
  Method becomes hot (CompileThreshold)
       |
  HotSpot: "compile this method"
       |
  JVMCI check: UseJVMCICompiler?
  YES -> call Graal (via JVMCI)
  NO  -> call C2 (classic path)
       |
  Graal: bytecode -> Graal IR graph
       |
  Graal: optimization phases
  (inlining, EA, constant folding...)
       |
  Graal: Graal IR -> machine code
       |
  Machine code returned to HotSpot
  and installed in Code Cache
```

**Truffle Partial Evaluation:**
```
  Truffle AST interpreter defined in Java
       |
  Program runs (interpreted initially)
       |
  Hot method detected
       |
  GraalVM: partial evaluation starts
  - Inline all Truffle dispatch nodes
  - Specialise for observed types
  - Fold interpreter framework overhead
       |
  Residual compiled code: only the
  program-specific execution remains
  (no interpreter dispatch overhead)
       |
  Compiled code installed
  (runs at near-native speed)
```

---

### 🔄 The Complete Picture - End-to-End Flow

**GRAAL JIT COMPILATION FLOW:**
```
  Java source                   <- YOU ARE HERE
       |
  javac -> bytecode
       |
  HotSpot interprets (tier 0-3)
       |
  Method hits compile threshold
       |
  JVMCI: dispatch to Graal compiler
       |
  Graal: bytecode -> Graal IR
       |
  Graal: run optimization phases
  (inlining, loop opts, EA,
   conditional elimination, etc.)
       |
  Graal: Graal IR -> LIR ->
  machine code (via HotSpot backend)
       |
  Machine code: installed in Code Cache
       |
  Future calls: execute native code
```

**FAILURE PATH:**
- Graal compilation time too high: `jvmci.CompilerThreads` limit hit; long compile queue; tier-4 compilations delayed
- Graal crashes or produces wrong code: deoptimisation triggered; method falls back to interpreter; bug report to GraalVM project
- Truffle AST specialisation divergence: too many type specialisations invalidated; re-compilation storm; similar to megamorphic call site problem in HotSpot

**WHAT CHANGES AT SCALE:**
At fleet scale, Graal compilation time is the bottleneck: Graal compiles more aggressively than C2, which means longer cold start. Profile-Guided Optimization (PGO) for Native Image requires a training run first - impractical for all services. Ahead-of-Time class data sharing (AppCDS + Graal) helps but requires per-app image creation.

---

### 💻 Code Example

**BAD - dynamic dispatch defeating Graal inlining:**
```java
// PROBLEM: megamorphic interface call
// Graal sees 10+ implementations of Processor
// Cannot inline - must emit call via vtable
interface Processor {
    void process(byte[] data);
}

// Many implementations registered dynamically
List<Processor> processors = loadAllProcessors();
for (Processor p : processors) {
    p.process(data);  // megamorphic - Graal cannot
}                     // inline; becomes indirect call
```

**GOOD - monomorphic/bimorphic call sites:**
```java
// GOOD: sealed interface -> Graal knows all subtypes
// Can inline all cases and eliminate dispatch
sealed interface Processor
    permits FastProcessor, SlowProcessor {}

// Graal inlines BOTH cases and eliminates dispatch
// for known-monomorphic call sites
void process(Processor p, byte[] data) {
    // JIT sees closed type set -> inlines both arms
    p.process(data);
}
```

**Using Graal as JIT (GraalVM JDK):**
```bash
# Verify Graal is active:
java -XX:+UnlockExperimentalVMOptions \
     -XX:+UseJVMCICompiler \
     -Dgraal.ShowConfiguration=info \
     -jar app.jar 2>&1 | head -5
# Output: Graal.ShowConfiguration: Graal Enterprise...

# Measure compilation time:
java -XX:+UnlockExperimentalVMOptions \
     -XX:+UseJVMCICompiler \
     -Dgraal.PrintCompilation=true \
     -jar app.jar 2>&1 | grep "compile"
```

**Truffle language node example:**
```java
import com.oracle.truffle.api.nodes.*;
import com.oracle.truffle.api.dsl.*;

// Add node that specialises on int then falls back
@NodeChildren({
    @NodeChild("left"),
    @NodeChild("right")
})
abstract class AddNode extends Node {
    abstract Object execute(Object left, Object right);

    // Fast path: both int
    @Specialization
    int add(int left, int right) {
        return left + right;
    }

    // Slow path: generic
    @Specialization
    Object add(Object left, Object right) {
        // ... generic number addition
        return ((Number) left).doubleValue()
             + ((Number) right).doubleValue();
    }
}
// Truffle generates a state machine between
// specialisations; Graal compiles the hot path only
```

**How to test / verify correctness:**
```bash
# Compare Graal vs C2 performance:
java -XX:+UseJVMCICompiler -jar benchmark.jar
java -XX:-UseJVMCICompiler -jar benchmark.jar
# Compare: throughput, startup time, p99 latency

# Verify Graal compilation of specific method:
java -XX:+UnlockDiagnosticVMOptions \
     -XX:+UseJVMCICompiler \
     -Dgraal.Dump=:1 \
     -jar app.jar
# Generates .bgv files viewable in Ideal Graph Visualizer
```

---

### ⚖️ Comparison Table

| Dimension | HotSpot C2 | Graal JIT | Truffle |
|---|---|---|---|
| Language | C++ | Java | Java (framework) |
| IR | SSA + CFG (separate) | Sea-of-nodes (unified) | AST specialisations |
| Target | Java bytecode | Java bytecode | Any language AST |
| Peak performance | Excellent | Slightly better for some patterns | Near-C2 for hot code |
| Compilation speed | Fast | Slower (more aggressive) | Slow initial |
| Startup | Good | Cold start overhead | Slow (specialisation) |
| Optimisation quality | Very good | Better for some patterns | Depends on specialisation |

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| "Graal always generates faster code than C2" | Graal generates better code for some patterns (more aggressive inlining, better escape analysis). C2 is faster for other patterns (warm-up speed, simple loops). Benchmarking is required. |
| "Truffle languages run at full Java speed" | Truffle languages run at 60-90% of equivalent Java speed for typical workloads. Object model overhead, boxing, and garbage generation from dynamic typing still apply. |
| "JVMCI replaces the JVM" | JVMCI is just the compilation hook. HotSpot still provides GC, class loading, bytecode interpretation, and runtime services. Only the tier-4 JIT is replaced. |
| "Graal IR is more complex than C2" | Graal IR is arguably simpler: one graph instead of two separate structures. The simplicity enables the compiler to be written in Java and maintained by Java engineers. |
| "Native Image uses the same JIT as Graal JIT" | Native Image uses Graal as an AOT compiler (compile once at build time). The runtime has no JIT. The Graal IR and optimisations are shared, but the compilation model is fundamentally different. |

---

### 🚨 Failure Modes & Diagnosis

**Failure Mode 1: Graal deoptimisation storm**
**Symptom:** Application running on GraalVM JIT shows intermittent performance drops; GraalVM logs show repeated `deopt` events for same method
**Root Cause:** Graal speculative optimisation violated (e.g., type assumption disproved); method deoptimised and re-compiled repeatedly
**Diagnostic:**
```bash
java -XX:+UseJVMCICompiler \
     -Dgraal.TraceDeoptimization=true \
     -jar app.jar 2>&1 | grep "deoptimize"
# Look for: repeated deoptimisation of same method
```
**Fix:** Identify method with repeated deopt; check if polymorphic call site or volatile type assumption; add type hints or refactor to monomorphic
**Prevention:** JFR compilation events + deoptimisation events; alert on high deopt rate per method

**Failure Mode 2: Truffle AST specialisation explosion**
**Symptom:** TruffleRuby/GraalPy program shows good initial performance, then degrades; memory usage grows from AST specialisation nodes
**Root Cause:** Dynamic language creates too many distinct types at a call site; Truffle creates one specialisation per type; compilation threshold for "megamorphic" fallback exceeded
**Diagnostic:**
```bash
# Enable Truffle diagnostic output
java -Dpolyglot.engine.TraceCompilation=true \
     -Dpolyglot.engine.TraceDeopt=true \
     script.rb 2>&1 | grep "Truffle"
# Look for: "INVALIDATED" with reasons
```
**Fix:** Reduce dynamic type diversity at hot call sites; use explicit type annotations in dynamic language code
**Prevention:** Profile dynamic language code for call-site type diversity before production deployment

**Failure Mode 3: Graal cold start latency**
**Symptom:** Service using GraalVM JIT (not Native Image) has longer cold start than HotSpot; first-minute latency is higher
**Root Cause:** Graal compiler is itself JIT-compiled during startup; Graal's more aggressive compilation takes longer per method; Net latency: Graal > C2 for first 30-60 seconds
**Diagnostic:**
```bash
# Compare startup time:
time java -XX:+UseJVMCICompiler -jar app.jar &
time java -jar app.jar  # default JIT
# Measure time until first request handles < 100ms
```
**Fix:** For latency-critical services: use GraalVM Native Image (no JIT, instant start); for throughput services: the startup cost amortises and Graal peak throughput wins
**Prevention:** Choose JIT vs Native Image based on workload: long-running = JIT Graal; serverless/FaaS = Native Image

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**
- [[JVM-041 - JIT Compiler]] - How JIT compilation works fundamentally
- [[JVM-042 - C1 and C2 Compiler]] - The compilers Graal replaces/improves upon
- [[JVM-043 - Tiered Compilation]] - How Graal fits into the compilation tiers

**Builds On This (learn these next):**
- (none - this is a frontier research entry)

**Alternatives / Comparisons:**
- [[JVM-044 - Method Inlining]] - Key optimisation in both C2 and Graal
- [[JVM-045 - Deoptimization]] - Required by both speculative JITs
- [[JVM-048 - GraalVM]] - Full GraalVM ecosystem including Native Image

---

### 📌 Quick Reference Card

```
+--------------------------------------------------+
| WHAT IT IS    | Graal: Java-written JIT with     |
|               | sea-of-nodes IR. Truffle: any-   |
|               | language AST -> compiled via PE  |
+--------------------------------------------------+
| PROBLEM       | C2 hard to improve; new languages|
|               | need a full compiler to run fast |
+--------------------------------------------------+
| KEY INSIGHT   | Partial evaluation: interpreter+ |
|               | program = compiled program        |
+--------------------------------------------------+
| USE WHEN      | Long-running services needing    |
|               | peak throughput; polyglot needs  |
+--------------------------------------------------+
| AVOID WHEN    | Latency-critical cold-start;     |
|               | use Native Image instead         |
+--------------------------------------------------+
| TRADE-OFF     | Better peak perf vs slower JIT  |
|               | compilation + startup overhead   |
+--------------------------------------------------+
| ONE-LINER     | -XX:+UseJVMCICompiler for Graal; |
|               | Truffle via GraalVM SDK install  |
+--------------------------------------------------+
| NEXT EXPLORE  | JVM-048 GraalVM overview,       |
|               | JVM-045 Deoptimization           |
+--------------------------------------------------+
```

**If you remember only 3 things:**
1. Graal IR uses sea-of-nodes: unified control+data graph enabling optimisations that are hard in C2's separate SSA+CFG
2. Truffle partial evaluation: write a language interpreter in Java; GraalVM compiles away the interpreter overhead, leaving only program code
3. JVMCI is the plug-in API: Graal replaces only C2 (tier-4 compilation); HotSpot handles everything else

**Interview one-liner:** "Graal is a Java-written JIT using sea-of-nodes IR that replaces C2 via JVMCI; Truffle uses partial evaluation to make any language interpreter run at near-native speed by compiling away interpreter dispatch overhead on GraalVM."

---

### 💎 Transferable Wisdom

**Reusable Engineering Principle:** Partial evaluation is the universal bridge between "easy to write" (interpreters) and "fast to execute" (compiled code). Wherever an interpreter has a fixed program structure (the language's runtime) and a variable program (the user's code), partial evaluation can specialise the interpreter for the specific program and compile away the interpreter overhead.

**Where else this pattern appears:**
- Database query plans: a query optimizer partially evaluates generic scan operators against a specific query's predicates, producing a specialised execution plan
- Template metaprogramming (C++): computation fixed at compile time is "partially evaluated" away; only runtime-variable computation remains
- JIT for regex engines: a regex pattern is "partially evaluated" against itself to produce specialised matching code, faster than generic NFA traversal

---

### 💡 The Surprising Truth

The Graal compiler is not only used as a JIT for the JVM - it is also used as an AOT compiler for GraalVM Native Image. The same Java codebase implements two fundamentally different compilation models: one that compiles methods one at a time during runtime (JIT), and one that compiles the entire application's reachable code before execution starts (AOT). This dual use is possible because Graal IR and its optimisation phases are agnostic to when compilation happens. The same pass that inlines a virtual call during JIT compilation inlines it during AOT compilation. This makes Graal arguably the most versatile compiler in production use today: it is simultaneously a production JIT compiler, a research platform, an AOT compiler, and through Truffle, a substrate for over a dozen production languages. No other compiler in active production use spans this range.

---

### 🧠 Think About This Before We Continue

**Q1 (First Principles):** Truffle partial evaluation "inlines the interpreter" to eliminate dispatch overhead. But an AST interpreter for a dynamic language like Ruby must check types at every node (is this an int? a string?). After partial evaluation, where do these type checks go, and how does Truffle ensure they don't eliminate the performance benefit?
*Hint:* Research Truffle's `@Specialization` mechanism and "node rewriting" - how individual AST nodes maintain per-call-site type specialisations and what happens when a type assumption is violated.

**Q2 (Scale):** You want to run JavaScript (via GraalJS) in a multi-tenant environment where 1,000 concurrent users each run isolated scripts. Truffle compiles hot code per-polyglot-context. What happens to memory and CPU if all 1,000 contexts independently JIT-compile the same hot functions?
*Hint:* Research GraalVM's "context pre-initialisation" and "code sharing across contexts" features in the Truffle API - and think about what "isolated compilation" means for shared compilation overhead.

**Q3 (Design Trade-off):** Sea-of-nodes IR makes Graal more powerful than C2 for some optimisations but also makes it harder to debug. A compiler engineer finds a bug: a method's sea-of-nodes graph produces wrong machine code. How does a developer introspect a sea-of-nodes graph compared to a traditional CFG+SSA graph, and what tooling does GraalVM provide for this?
*Hint:* Research IGV (Ideal Graph Visualizer), `-Dgraal.Dump=:2`, and `.bgv` files - and consider why visualising a unified control+data graph is harder than visualising separate control and data structures.
