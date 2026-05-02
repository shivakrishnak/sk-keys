---
layout: default
title: "GraalVM"
parent: "Java & JVM Internals"
nav_order: 304
permalink: /java/graalvm/
number: "0304"
category: Java & JVM Internals
difficulty: ★★★
depends_on: JIT Compiler, AOT (Ahead-of-Time Compilation), JVM
used_by: Native Image, Tiered Compilation
related: Native Image, AOT (Ahead-of-Time Compilation), JIT Compiler
tags:
  - java
  - jvm
  - internals
  - performance
  - graalvm
  - deep-dive
---

# 304 — GraalVM

⚡ TL;DR — GraalVM is a high-performance JDK that replaces HotSpot's C2 JIT compiler with one written in Java, and adds the ability to compile Java to standalone native binaries.

┌─────────────────────────────────────────────────────────────────────────────────┐
│ #304 │ Category: Java & JVM Internals │ Difficulty: ★★★ │
├──────────────┼──────────────────────────────────────┼──────────────────────────┤
│ Depends on: │ JIT Compiler, AOT, JVM │ │
│ Used by: │ Native Image, Tiered Compilation │ │
│ Related: │ Native Image, AOT Compilation, │ │
│ │ JIT Compiler │ │
└─────────────────────────────────────────────────────────────────────────────────┘

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
HotSpot's C2 JIT compiler is written in C++ and is notoriously difficult to
maintain and extend. Adding new optimizations requires deep C++ expertise and
understanding of a complex, poorly-documented "sea of nodes" IR. Meanwhile,
languages like Truffle-based interpreters (Ruby, Python, R on JVM) needed a
JIT compiler — but writing a separate JIT for each was infeasible. The Java
ecosystem had two siloed execution models: interpreted (slow, immediate) and
JIT (fast, warm-up required) — with no bridge.

**THE BREAKING POINT:**
The Oracle Labs research team wanted to create a universal JIT infrastructure
that could: (1) JIT-compile Java better than C2, (2) JIT-compile other languages
using a framework, (3) produce native binaries from Java. All three in one codebase.
The blocker: JIT compilers must be written in C++ (for performance). Or... must they?

**THE INVENTION MOMENT:**
This is exactly why **GraalVM** was created: write the JIT compiler in Java,
use the JVM's self-referential ability (the JIT itself runs on a JIT), and build
a platform where one compiler serves Java, JavaScript, Python, Ruby, R, and WASM —
plus produces native binaries. "One VM to rule them all."

---

### 📘 Textbook Definition

GraalVM is a high-performance polyglot JDK developed by Oracle Labs that provides
multiple execution modes: the Graal JIT compiler (a Java-written replacement for
HotSpot's C2), GraalVM Native Image (AOT compilation to standalone native binaries),
and the Truffle framework (a guest-language framework that lets language implementors
build high-performance interpreters that GraalVM JIT-compiles automatically).
GraalVM Community Edition is open-source (GPLv2); GraalVM Enterprise adds
additional optimizations and support. Starting with Java 21, key GraalVM
technologies are being upstreamed into OpenJDK.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
GraalVM is a JDK that replaces the JIT compiler with a better one and adds the ability to make native binaries.

**One analogy:**

> Think of the traditional JVM as a dedicated car factory that only makes sedans.
> GraalVM is a universal manufacturing platform: it makes sedans (Java), sports
> cars (JavaScript), trucks (Python), and can even ship pre-assembled cars (native
> binaries) directly instead of requiring customers to assemble them.

**One insight:**
The radical idea of GraalVM is that the JIT compiler itself is Java code, running
on a JVM, being optimized by a JIT. This "meta-circular" design means improvements
to the JIT improve themselves — and the same compiler can be pointed at any
language that provides an IR (Intermediate Representation) in Graal's format.

---

### 🔩 First Principles Explanation

**CORE INVARIANTS:**

1. A JIT compiler transforms an IR into optimized native code.
2. The choice of implementation language for the JIT affects maintainability, not capability.
3. Any language can be JIT-compiled if it can be represented as a standard IR.
4. Native code generation is a transformation — it doesn't require a JVM at runtime.

**DERIVED DESIGN:**
From invariant 1 and 2: write the JIT in Java. This gives you the full Java
ecosystem (IDEs, debuggers, profilers, unit testing) for JIT development.

From invariant 3: create a standard guest-language IR (Truffle AST nodes).
Any language that implements Truffle nodes gets JIT compilation "for free."
GraalVM compiles the Truffle interpreter itself — since the interpreter is
just Java, the JIT optimizes through it (partial evaluation), eliminating
interpretation overhead.

From invariant 4: run the same Graal compiler at build time instead of runtime —
with the output being a standalone binary. This is Native Image.

**THE TRADE-OFFS:**

- Gain: JIT compiler written in Java → maintainable, testable, extensible.
- Gain: Single compiler infrastructure for multiple languages.
- Gain: AOT native binaries with excellent startup times.
- Cost: "Meta-circular" JIT bootstrapping is complex (Graal compiles the JVM
  that runs Graal).
- Cost: Native Image requires closed-world assumption.
- Cost: Enterprise edition optimizations require license fee.

---

### 🧪 Thought Experiment

**SETUP:**
You have a monolithic Java application that calls into a Python ML library for inference.
Traditional approach: Java → HTTP call → Python process → HTTP response.
Latency: 10ms + HTTP overhead + Python startup.

**WHAT HAPPENS WITH GRAALVM POLYGLOT:**
Using GraalVM's Polyglot API, Java calls Python directly in the same JVM process:

```java
try (Context ctx = Context.create("python")) {
    Value result = ctx.eval("python", "import sklearn; ...");
}
```

The Python code runs under GraalVM's Truffle interpreter, JIT-compiled alongside
the Java code. No HTTP overhead. No process boundary. Latency: 10μs.

**WHAT HAPPENS WITH NATIVE IMAGE:**
The same application compiled to a native binary: 50ms startup, runs on bare metal
without JRE installed. Memory footprint: 30MB vs 500MB for JVM-based.

**THE INSIGHT:**
GraalVM unifies three traditionally separate concerns: JIT performance, polyglot
interop, and native deployment. Each was previously solved by different tools;
GraalVM provides one platform for all three.

---

### 🧠 Mental Model / Analogy

> GraalVM is like a universal adapter. JVM is region-specific: it handles Java.
> GraalVM is like a world adapter that also works as a power converter: it
> handles Java natively, adapts any other language through an adapter (Truffle),
> and can also power the device directly from a stable DC source (native binary —
> no AC conversion needed).

- "Region-specific plug" → standard JVM (Java only)
- "Universal adapter" → GraalVM polyglot (Java + Python + JS + Ruby + R)
- "Power converter" → Truffle (transforms any language to optimizable IR)
- "DC power source directly" → Native Image (no runtime conversion needed)

**Where this analogy breaks down:** A universal adapter accepts any plug passively.
GraalVM's Truffle requires active language implementation work — language authors
must implement their language as a Truffle AST interpreter. The platform doesn't
magically support arbitrary languages.

---

### 📶 Gradual Depth — Four Levels

**Level 1 — What it is (anyone can understand):**
GraalVM is a version of Java that runs faster, can run multiple programming
languages in the same program, and can package Java programs as standalone
executables that don't need Java installed.

**Level 2 — How to use it (junior developer):**
Download GraalVM CE from graalvm.org (or use SDKMAN: `sdk install java 21-graal`).
Use exactly like standard JDK — it's a drop-in replacement. For Native Image:
install Native Image component with `gu install native-image`, then run
`native-image -jar app.jar`. For Spring Boot Native: use `spring-boot-starter-aot`.

**Level 3 — How it works (mid-level engineer):**
GraalVM's JIT (Graal compiler) uses a different IR than HotSpot's C2: Graal
uses a custom graph-based IR with explicit data flow and control flow edges.
It applies a set of "phases" (optimization passes) that are Java classes —
debuggable, testable, extensible. Truffle AST interpreters gain JIT compilation
via "partial evaluation": Graal treats the interpreter as a specializer, unfolds
it for a specific program, and optimizes the result. Native Image runs the Graal
compiler at build time, baking the output into a GCC-linked binary with
embedded GC (Serial GC by default) and initial heap snapshot.

**Level 4 — Why it was designed this way (senior/staff):**
The meta-circular compiler design (JIT in Java, running on JVM, compiled by
the same JIT) creates a bootstrapping challenge similar to compiler self-hosting.
GraalVM solves this with a two-stage build: compile Graal with javac first,
run on HotSpot with C2 to bootstrap, then (optionally) compile Graal with
Graal for maximum performance. This "compiler compiler" design philosophy means
improvements to Graal's core optimization engine benefit all languages using
it simultaneously — a virtuous cycle. The Oracle Labs research that led to
GraalVM (2013–2018) also produced academic contributions on partial evaluation
and self-optimizing AST interpreters that influenced language VM design broadly.

---

### ⚙️ How It Works (Mechanism)

```
┌──────────────────────────────────────────────────────────┐
│              GRAALVM COMPONENTS                          │
├──────────────────────────────────────────────────────────┤
│                                                          │
│  ┌──────────────────┐   ┌─────────────────────────┐     │
│  │ Graal JIT        │   │ Native Image (AOT)       │     │
│  │ (replaces C2)    │   │ Build-time compilation   │     │
│  │ Written in Java  │   │ Standalone native binary │     │
│  │ Better IR        │   │ Closed-world assumption  │     │
│  └──────────────────┘   └─────────────────────────┘     │
│           ↑                         ↑                   │
│   ┌───────────────────────────────────────────┐         │
│   │ Graal Compiler API                         │         │
│   │ Graph-based IR, Optimization Phases        │         │
│   └───────────────────────────────────────────┘         │
│           ↑                                             │
│   ┌───────────────────────────────────────────┐         │
│   │ Truffle Framework                          │         │
│   │ Guest language AST nodes                  │         │
│   │ Partial evaluation → JIT compilation      │         │
│   │ (JavaScript, Python, Ruby, R, WASM, etc.) │         │
│   └───────────────────────────────────────────┘         │
└──────────────────────────────────────────────────────────┘
```

**GraalVM JIT vs HotSpot C2:**

- Graal is written in Java vs C2's C++ — same conceptual output, better engineering
- Graal JIT throughput: comparable to C2 or better on many benchmarks
- Escape analysis in Graal is more aggressive than C2 in several cases
- Graal supports "inlining through interfaces" better than C2 in some scenarios

---

### 🔄 The Complete Picture — End-to-End Flow

```
┌──────────────────────────────────────────────────────────┐
│       GRAALVM EXECUTION PATH OPTIONS                     │
├──────────────────────────────────────────────────────────┤
│  Java source code .java                                  │
│           ↓ javac                                        │
│  .class bytecode                                         │
│           ↓                                              │
│  OPTION A: Graal JIT mode                               │
│    JVM start → ClassLoader → Tiered:                    │
│    [Interpreter] → [C1] → [Graal JIT] ← YOU ARE HERE   │
│    Better optimization than C2 for some workloads       │
│           ↓                                              │
│  OPTION B: Native Image AOT mode                        │
│    Build: native-image analysis → Graal compile →       │
│    native binary ← YOU ARE HERE (build time)            │
│    Run: binary starts in 50ms (no JVM)                  │
│           ↓                                              │
│  OPTION C: Polyglot mode                                │
│    Java + Truffle language in same JVM                  │
│    Graal JIT optimizes across language boundaries       │
└──────────────────────────────────────────────────────────┘
```

**FAILURE PATH:**
Native Image build fails due to unreachable configuration → missing reflection
config → application fails at runtime with `ClassNotFoundException`.
JIT mode: if Graal JIT encounters an optimization bug → falls back to C2
(in some configurations) or throws `BailoutException` → method runs unoptimized.

**WHAT CHANGES AT SCALE:**
At scale, GraalVM JIT's escape analysis is more aggressive — it can allocate
more objects on the stack (no GC pressure), reducing GC pause frequency.
For memory-constrained environments (containers), Native Image's lower footprint
allows 3–4× higher pod density compared to JVM-based deployments.

---

### 💻 Code Example

```java
// Example 1 — GraalVM as drop-in JDK replacement
// Install: sdk install java 21.0.2-graal
// Use: java -jar app.jar  (same command)
// Or force Graal JIT (vs HotSpot C2):
// java -XX:+UseJVMCICompiler -jar app.jar
// JVMCI = JVM Compiler Interface (how Graal plugs in)
```

```java
// Example 2 — Polyglot API (Java + JS in same process)
import org.graalvm.polyglot.*;

public class PolyglotExample {
    public static void main(String[] args) {
        // Run JavaScript in-process, no overhead
        try (Context context = Context.create()) {
            Value result = context.eval(
                "js",
                "1 + 2" // any JS code
            );
            System.out.println(result.asInt()); // 3
        }

        // Call Python for ML inference (with GraalPy)
        try (Context ctx = Context.newBuilder("python")
                .allowAllAccess(true).build()) {
            ctx.eval("python",
                "import numpy as np; " +
                "result = np.sum([1,2,3])"
            );
        }
    }
}
```

```java
// Example 3 — Native Image with Spring Boot 3
// pom.xml:
// <parent>
//   <groupId>org.springframework.boot</groupId>
//   <artifactId>spring-boot-starter-parent</artifactId>
//   <version>3.2.0</version>
// </parent>
// <dependency>spring-boot-starter-web</dependency>

// Profile in pom.xml:
// <profiles>
//   <profile>
//     <id>native</id>
//     <build>
//       <plugins>
//         <plugin>
//           <groupId>org.graalvm.buildtools</groupId>
//           <artifactId>
//             native-maven-plugin
//           </artifactId>
//         </plugin>
//       </plugins>
//     </build>
//   </profile>
// </profiles>

// Build: ./mvnw -Pnative native:compile
// Run:   ./target/myapp    (no JVM needed)
// Start: ~80ms  vs ~3s with JVM
```

---

### ⚖️ Comparison Table

| Feature             | HotSpot (OpenJDK)       | GraalVM CE             | GraalVM EE                |
| ------------------- | ----------------------- | ---------------------- | ------------------------- |
| **JIT Compiler**    | C2 (C++)                | Graal (Java)           | Graal (Java, enhanced)    |
| **Native Image**    | No                      | Yes                    | Yes (faster build)        |
| **Polyglot**        | No                      | Yes (Truffle)          | Yes (Truffle + optimized) |
| **JIT Performance** | Excellent               | Comparable/better      | Better than CE            |
| **License**         | GPLv2                   | GPLv2                  | Commercial                |
| **Support**         | Community / vendors     | Community              | Oracle                    |
| **Best For**        | Production Java servers | Native image, polyglot | Enterprise AOT            |

**How to choose:** GraalVM CE is free and suitable for most use cases.
Use GraalVM EE when AOT build time matters at scale, or when enterprise
support is required. Use HotSpot for maximum JVM compatibility and tooling.

---

### ⚠️ Common Misconceptions

| Misconception                                      | Reality                                                                                                          |
| -------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------- |
| GraalVM is a completely different JVM              | GraalVM is a JDK built on OpenJDK with the JIT compiler replaced; it passes the Java TCK                         |
| GraalVM Native Image supports all Java features    | Native Image requires closed-world analysis; reflection, dynamic proxies, and serialization need configuration   |
| GraalVM Polyglot is zero-overhead                  | There is a small startup overhead per language context; in-context execution can be near-zero overhead after JIT |
| GraalVM EE is significantly faster than CE for JIT | Performance differences are modest for JIT; EE's advantages are primarily in build tooling and support           |
| GraalVM is only useful for microservices           | GraalVM JIT is valuable for any Java application; polyglot is valuable for data science workflows                |

---

### 🚨 Failure Modes & Diagnosis

**Native Image Build Failure — Missing Classes**

Symptom:
`native-image` build fails with `Error: Build image failed` or
`ClassInitializationError` during analysis phase.

Root Cause:
A class referenced via reflection or Class.forName is not reachable
statically.

Diagnostic Command / Tool:

```bash
native-image --verbose -jar app.jar 2>&1 | grep "Missing"
# Or use the diagnostic report:
native-image -H:+ReportExceptionStackTraces -jar app.jar
```

Fix:
Run tracing agent and add generated config:

```bash
java -agentlib:native-image-agent=config-output-dir=./config \
  -jar app.jar
native-image -H:ConfigurationFileDirectories=./config -jar app.jar
```

---

**JIT Bailout (Graal Fails to Compile Method)**

Symptom:
Method logs `Could not compile [method]: ...` or `BailoutException`. Method
runs at interpreter speed.

Root Cause:
Graal's compiler encountered unsupported bytecode pattern or an internal
assertion failure.

Diagnostic Command / Tool:

```bash
java -XX:+UseJVMCICompiler \
  -Dgraal.CompilationFailureAction=Diagnose \
  -jar app.jar 2>&1 | grep "BailoutException"
```

Fix:
Update GraalVM to latest version. If reproducible, exclude method:
`-Dgraal.CompileOnly=-com.example.Foo.problematic`

Prevention:
Stay current with GraalVM patch releases.

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**

- `JIT Compiler` — GraalVM's primary JIT replaces C2; must understand JIT basics
- `AOT (Ahead-of-Time Compilation)` — Native Image is GraalVM's AOT implementation
- `JVM` — GraalVM is built on OpenJDK; JVM architecture knowledge is prerequisite

**Builds On This (learn these next):**

- `Native Image` — the GraalVM product specifically for AOT native binary compilation
- `Tiered Compilation` — GraalVM participates in JVM's tiered compilation when in JIT mode

**Alternatives / Comparisons:**

- `JIT Compiler (HotSpot C2)` — the JIT that GraalVM replaces; C++ vs Java trade-offs
- `AOT (Ahead-of-Time Compilation)` — the broader concept; GraalVM Native Image is one implementation

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ WHAT IT IS   │ Polyglot JDK with Java-written JIT + AOT  │
├──────────────┼───────────────────────────────────────────┤
│ PROBLEM IT   │ C2 JIT is hard to extend; Java lacks AOT; │
│ SOLVES       │ polyglot interop is expensive             │
├──────────────┼───────────────────────────────────────────┤
│ KEY INSIGHT  │ Writing the JIT in Java makes it          │
│              │ self-improving and extensible — the same  │
│              │ compiler serves JIT, AOT, and polyglot    │
├──────────────┼───────────────────────────────────────────┤
│ USE WHEN     │ Native Image for serverless; Graal JIT for │
│              │ better JIT performance; Truffle for        │
│              │ polyglot Java applications                │
├──────────────┼───────────────────────────────────────────┤
│ AVOID WHEN   │ Heavyweight reflection frameworks without  │
│              │ AOT support (older Spring, Struts, etc.)  │
├──────────────┼───────────────────────────────────────────┤
│ TRADE-OFF    │ Platform capability vs compatibility       │
│              │ complexity (closed-world for Native Image) │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "One compiler to compile the compiler"     │
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ Native Image → AOT → Tiered Compilation    │
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** GraalVM's Truffle framework enables "partial evaluation" — the JIT treats
an interpreter as a specializer and unfolds it for a specific program input,
eliminating interpretation overhead. Concretely: a Python interpreter written
in Truffle runs Python code. Graal JIT-compiles the execution of that interpreter
interpreting that specific Python program. Does the resulting native code look
more like compiled Python or compiled Java? Trace through what happens at the
JIT level when the same Python function is called 10,000 times.

**Q2.** GraalVM CE is open-source under GPLv2, while GraalVM EE is commercial.
The JIT performance difference between CE and EE is modest for throughput.
Yet many organizations pay for EE. From a total-cost-of-ownership perspective,
what is the exact category of value that EE provides that CE cannot, and under
what engineering maturity profile does EE's cost become clearly worth it?
