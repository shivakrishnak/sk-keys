---
id: CSF-004
title: How Code Becomes Execution - Big Picture
category: CS Fundamentals - Paradigms
tier: tier-1-foundations
folder: CSF-cs-fundamentals
difficulty: ★☆☆
depends_on:
used_by:
related:
tags:
  - csf
  - foundational
  - mental-model
status: draft
version: 2
layout: default
parent: "CS Fundamentals - Paradigms"
grand_parent: "Technical Dictionary"
nav_order: 4
permalink: /csf/how-code-becomes-execution-big-picture/
---

# CSF-004 - How Code Becomes Execution - Big Picture

⚡ TL;DR - Source code travels through lexing, parsing, semantic analysis, code generation, linking, loading, and finally execution on real hardware.

| CSF-004         | Category: CS Fundamentals - Paradigms | Difficulty: ★☆☆ |
| :-------------- | :------------------------------------ | :-------------- |
| **Depends on:** | CSF-001, CSF-003                      |                 |
| **Used by:**    | CSF-014, CSF-058, CSF-062             |                 |
| **Related:**    | CSF-014, CSF-058, CSF-062, CSF-005    |                 |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
Without understanding how code becomes execution, error messages
are oracles rather than diagnostics. A `NullPointerException` at
runtime, a linker error at build time, a type error at compile
time — these all look like "the computer is broken" rather than
"I violated a contract at a specific phase of execution."

**THE BREAKING POINT:**
Developers who can't reason about the pipeline write code that
works in dev but fails in prod due to loading order, that passes
tests but fails at JIT warmup, or that produces subtle security
vulnerabilities because they misunderstood when validation happens.

**THE INVENTION MOMENT:**
The compilation pipeline was formalised in the 1950s–1970s,
culminating in Aho, Lam, Sethi, and Ullman's _Compilers: Principles,
Techniques, and Tools_ (the "Dragon Book"). This gave the field a
standard vocabulary: lexer, parser, AST, semantic analyser, IR,
optimiser, code generator, linker, loader.

**EVOLUTION:**
Modern languages add layers: JIT compilation after loading (JVM,
V8), AOT compilation at deploy time (GraalVM, Dart), and
interpreters that skip machine code entirely (CPython). The
pipeline grew richer without changing its fundamental structure.

---

### 📘 Textbook Definition

Code execution is a multi-phase pipeline that transforms human-
readable source text into sequences of processor instructions. The
pipeline includes: lexical analysis (tokenisation), parsing (AST
construction), semantic analysis (type checking, name resolution),
optimisation, code generation, linking (combining object files),
loading (placing code and data in memory), and execution (CPU
fetching, decoding, and executing instructions).

---

### ⏱️ Understand It in 30 Seconds

**One line:**
Your source code is a recipe; the compiler/interpreter is the kitchen; machine instructions are the meal.

**One analogy:**

> Publishing a book follows a similar pipeline: manuscript (source)
> → copyediting (lexing/parsing errors) → proofreading (semantic
> analysis) → typesetting (code generation) → printing (assembly)
> → shipping (linking/loading) → reading (execution).
> Each phase can catch different types of errors.

**One insight:**
Where in the pipeline an error is caught determines its cost.
Compile-time errors are cheap (caught before deployment). Runtime
errors are expensive (caught in production). Type systems and
static analysis move errors earlier in the pipeline.

---

### 🔩 First Principles Explanation

**CORE INVARIANTS:**

1. CPUs execute binary instructions, not source code.
2. Every high-level language feature must map to machine instructions.
3. Different phases catch different error classes.
4. Earlier detection is always cheaper than later detection.
5. The pipeline is a series of transformations; each stage has a well-defined input and output.

**DERIVED DESIGN:**
The pipeline stages each handle a distinct concern:

- **Lexer** → character stream → token stream (catches illegal characters)
- **Parser** → token stream → AST (catches syntax errors)
- **Semantic analyser** → AST → typed AST (catches type errors, undeclared variables)
- **Optimiser** → IR → optimised IR (inlining, dead code elimination)
- **Code generator** → IR → machine code / bytecode
- **Linker** → object files → executable (resolves external references)
- **Loader** → executable → running process (loads into memory)
- **Runtime** → manages GC, JIT, threads during execution

**THE TRADE-OFFS:**
**Gain:** Each stage separation enables specialisation — the same
front-end (parser) can feed multiple back-ends (x86, ARM, WASM).
**Cost:** Multi-stage compilation has overhead; interpreted languages
skip some stages for faster startup but lose optimisation opportunities.

**ESSENTIAL vs ACCIDENTAL COMPLEXITY:**
**Essential:** You cannot execute source text — it must be transformed.
**Accidental:** Slow compilation (C++ template instantiation), complex
linking errors, and cryptic JVM class-loading errors are accidents
of specific design choices.

---

### 🧪 Thought Experiment

**SETUP:**
You write `int x = "hello"` in Java. Nothing runs yet.

**WHAT HAPPENS AT EACH STAGE:**

- Lexer: tokenises correctly (`int`, `x`, `=`, `"hello"`, `;`)
- Parser: parses correctly (it's a valid assignment expression syntactically)
- Semantic analyser: **STOPS HERE** — String is not assignable to int

You get a compile-time error. No executable was produced. No code ran.

**WHAT HAPPENS IN A DYNAMICALLY TYPED LANGUAGE:**
In Python: `x = "hello"; x + 1` — the first line succeeds (Python assigns any type to any name). The second line raises `TypeError` at _runtime_ — after execution begins.

**THE INSIGHT:**
The difference between Java and Python here is not about what's
possible — it's about _when_ the error is caught. Static typing
moves type errors from runtime to compile time. This is a pipeline
decision, not a language quality decision.

---

### 🧠 Mental Model / Analogy

> The pipeline is an assembly line with quality gates. Raw
> material (source) enters. At each station, a different
> inspector (lexer, parser, type checker) checks for a different
> class of defect. Products that pass all gates get shipped to
> the production line (CPU). Products that fail at an early gate
> are cheap to fix — products that fail after shipping (runtime)
> are expensive.

**Element mapping:**

- Raw material → source code text
- Lexer gate → checks character-level validity (legal tokens)
- Parser gate → checks grammatical structure (well-formed syntax)
- Type checker gate → checks semantic contracts (types match)
- Optimiser → improves the product without changing its function
- Linker/Loader → integrates components and deploys to factory floor
- CPU execution → the actual production run

Where this analogy breaks down: JIT compilation re-optimises the
"product" _during_ the production run, which has no factory analogy.

---

### 📶 Gradual Depth - Four Levels

**Level 1 - What it is (anyone can understand):**
When you write code and press run, a lot happens before the computer
actually does your instructions. The computer reads your text,
checks it for mistakes, translates it to its own language, and then
follows it step by step.

**Level 2 - How to use it (junior developer):**
Knowing the pipeline explains error messages. "Syntax error" =
parser failure. "Cannot find symbol" = semantic analysis failure.
"UnsatisfiedLinkError" = linker/loader failure at runtime.
"NullPointerException" = runtime execution failure. Each category
points to a different root cause.

**Level 3 - How it works (mid-level engineer):**
JVM runs bytecode, not your Java source. `.class` files are
compiled bytecode. The JIT compiler re-compiles hot bytecode to
native machine code at runtime. This two-phase compilation
explains JVM warmup: initial runs are slower (interpreted bytecode),
later runs are faster (JIT-compiled native code).

**Level 4 - Why it was designed this way (senior/staff):**
The IR (intermediate representation) is the key abstraction.
LLVM's IR allows Clang (C), Rust, Swift, and Kotlin Native to
share the same optimiser and backend. This is why Rust gets
world-class performance — it reuses decades of LLVM optimisation
research. Understanding IR enables you to understand why
cross-language performance characteristics differ so dramatically.

**Expert Thinking Cues:**

- Performance debugging: which phase is the bottleneck?
- Security analysis: which phase validates inputs? What happens at execution?
- JVM startup time: JIT warmup vs AOT compilation trade-offs

---

### ⚙️ How It Works (Mechanism)

Phase-by-phase:

**1. Lexical Analysis (Lexer)**
Input: character stream. Output: token stream.
`int x = 42;` → `[INT, IDENTIFIER(x), ASSIGN, NUMBER(42), SEMICOLON]`

**2. Parsing**
Input: token stream. Output: Abstract Syntax Tree.
Checks grammatical structure. `int x = 42;` becomes an assignment
node with left=variable declaration, right=integer literal.

**3. Semantic Analysis**
Input: AST. Output: annotated AST (with types, resolved names).
Checks types, resolves variable references, checks scope rules.

**4. Optimisation (IR level)**
Dead code elimination, constant folding, function inlining.
`x = 2 + 2` → `x = 4` at compile time.

**5. Code Generation**
IR → target bytecode or machine code.

**6. Linking**
Combines object files and resolves external references.
`printf` in your C code → resolved to libc's implementation.

**7. Loading**
OS loads executable into memory, resolves dynamic libraries.

**8. Runtime Execution**
CPU fetch-decode-execute loop. JVM/V8 may JIT compile hot paths.

---

### 🔄 The Complete Picture - End-to-End Flow

**NORMAL FLOW:**

```
source.java
    ↓ [Lexer]
tokens
    ↓ [Parser]
AST
    ↓ [Semantic Analyser]
Typed AST
    ↓ [IR Generator]
Bytecode (.class)    ← YOU ARE HERE
    ↓ [Linker]
JAR / executable
    ↓ [JVM Loader]
Loaded classes in heap
    ↓ [JIT Compiler (C1/C2)]
Native machine code for hot methods
    ↓ [CPU]
Actual execution
```

**FAILURE PATH:**
Build failure (compile-time) → fast, cheap, dev-only.
Link failure (link-time) → fast, pre-deployment.
Load failure (load-time) → caught at startup.
Runtime exception → caught during execution, potentially in prod.

**WHAT CHANGES AT SCALE:**
JIT warmup becomes measurable. Cold starts matter for serverless.
AOT (GraalVM native-image) eliminates warmup at cost of peak
performance. Large codebases suffer from long compilation times.

---

### ⚖️ Comparison Table

| Execution Model    | Compilation     | Startup       | Peak Perf         | Examples                 |
| ------------------ | --------------- | ------------- | ----------------- | ------------------------ |
| Compiled (AOT)     | Before run      | Fast          | Highest           | C, C++, Rust, Go         |
| JVM Bytecode + JIT | Before + during | Slow (warmup) | Very high         | Java, Kotlin, Scala      |
| Interpreted        | None / per-line | Instant       | Low               | CPython, Ruby            |
| Transpiled         | Before run      | Fast          | Depends on target | TypeScript→JS, Kotlin→JS |
| JIT-only           | During run      | Moderate      | High              | JavaScript (V8), LuaJIT  |
| AOT from JVM       | At build time   | Fast          | High              | GraalVM Native Image     |

---

### ⚠️ Common Misconceptions

| Misconception                               | Reality                                                                                       |
| ------------------------------------------- | --------------------------------------------------------------------------------------------- |
| "Compiled languages are always faster"      | JVM JIT-compiled Java often matches or beats C++ for long-running processes                   |
| "Interpreted languages have no compilation" | CPython compiles to bytecode (.pyc files); it just doesn't produce native machine code        |
| "The compiler checks everything"            | Compilers check what the language's type system models; runtime errors are outside that scope |
| "Linking is automatic"                      | Dynamic linking requires all dependencies present at runtime; missing DLLs break production   |
| "JIT makes startup instant"                 | JIT introduces warmup; cold-start latency is real and important for serverless                |

---

### 🚨 Failure Modes & Diagnosis

**Mode 1: JVM Warmup Blindness**
**Symptom:** Benchmarks show Java is slow; same benchmark in
continuous load shows it's fast.
**Root Cause:** Measuring JIT warmup as steady-state performance.
**Diagnostic:**

```bash
# Use JMH for proper JVM benchmarking (includes warmup iterations)
java -jar benchmarks.jar -wi 5 -i 10  # 5 warmup, 10 measured
```

**Fix:** Use JMH or similar for JVM benchmarks. Exclude warmup iterations.

**Mode 2: Dynamic Library Missing in Production**
**Symptom:** Works in dev, `UnsatisfiedLinkError` or `cannot find shared library` in prod.
**Root Cause:** Runtime dynamic linking assumes libraries present; dev machine has them, prod doesn't.
**Diagnostic:**

```bash
# Linux: list dynamic dependencies
ldd /path/to/binary
# Check if all libraries resolve
```

**Fix:** Include all native libraries in deployment artifacts. Use static linking for critical dependencies.

**Mode 3: Runtime Type Error in Dynamic Language**
**Symptom:** Python/JavaScript code fails at runtime on an unexpected data type.
**Root Cause:** Dynamic language defers type checking to runtime.
**Fix:** Use mypy (Python) or TypeScript for static type checking before runtime.

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**

- [[CSF-001 - What Is Computer Science - A Map]]
- [[CSF-003 - The History of Programming Languages]]

**Builds On This (learn these next):**

- [[CSF-014 - Compiled vs Interpreted Languages]]
- [[CSF-058 - JIT vs AOT Compilation Deep Dive]]
- [[CSF-062 - Language Runtime Internals]]

**Alternatives / Comparisons:**

- LLVM architecture (specific implementation of this pipeline)
- JVM bytecode specification (JVM-specific execution model)

---

### 📌 Quick Reference Card

```
┌─────────────────────────────────────────────────────┐
│ WHAT IT IS      Pipeline: source → tokens → AST →    │
│                 IR → bytecode → native code → CPU  │
│ PROBLEM         Error messages look arbitrary without  │
│ IT SOLVES       knowing which phase produced them     │
│ KEY INSIGHT     Earlier detection is cheaper — move   │
│                 errors from runtime to compile time   │
│ USE WHEN        Debugging errors, optimising build,   │
│                 choosing language execution model     │
│ AVOID WHEN      Over-engineering for imaginary        │
│                 compile-time guarantees              │
│ TRADE-OFF       Compile-time safety vs startup speed  │
│ ONE-LINER       Source code → phases of transformation│
│                 → CPU instructions                   │
│ NEXT EXPLORE    CSF-014, CSF-058, JVM-001, JVM-004    │
└─────────────────────────────────────────────────────┘
```

**If you remember only 3 things:**

1. Code travels through multiple phases before execution; each phase catches different errors.
2. Earlier in the pipeline = cheaper error detection.
3. JIT compilation happens _during_ execution — explaining warmup, startup, and peak performance.

**Interview one-liner:**
"Code becomes execution through phases: lexing, parsing, semantic analysis, IR generation, linking, loading, and runtime execution — each phase catches different error classes and offers different optimisation opportunities."

---

### 💎 Transferable Wisdom

**Reusable Engineering Principle:**
Every system that processes input has a pipeline. Structuring
validation, transformation, and execution as separate phases makes
errors diagnosable and enables optimisation at each stage.

**Where else this pattern appears:**

- **CI/CD pipelines** — lint/test/build/deploy stages catch different error classes
- **HTTP request processing** — authentication, authorisation, rate-limiting, routing, handler
- **Database query processing** — parse, optimise, execute (same three-phase structure as a compiler)

---

### 💡 The Surprising Truth

Java is often considered a "slow" language, but on the TechEmpower
benchmarks for plaintext HTTP responses, Java (with JIT warmup)
outperforms Rust on some scenarios — not because Java's runtime
is faster, but because HotSpot's C2 JIT compiler can observe
actual runtime data that static compilers can't: what branches are
actually taken, what types actually appear. This is the surprising
power of JIT: it knows more about your workload than your source
code does.

---

### 🧠 Think About This Before We Continue

**Q1 (System Interaction):** GraalVM Native Image compiles Java
to a native binary (AOT compilation). It starts instantly and
uses less memory than JVM. But it has a cold performance ceiling
that JVM+JIT can exceed. For what types of workloads does each
model win, and why?

_Hint:_ Think about serverless functions (cold starts matter) vs
long-running services (JIT warmup amortises over millions of requests).

**Q2 (Root Cause):** A production Java application slows down after
restarting but recovers performance after 5–10 minutes. What is
happening, and how would you diagnose it?

_Hint:_ Look up JVM JIT tiered compilation and what `-XX:+PrintCompilation`
shows. What does the warmup period correspond to in the pipeline?

**Q3 (Design Trade-off):** Rust compiles much slower than Go.
Go compiles much faster than C++. Yet Go is simpler than Rust,
and Rust is safer than C++. What does compilation speed reveal
about the design priorities of each language?

_Hint:_ Research what Rust's borrow checker and monomorphisation
cost in compile time, and what Go's design explicitly trades away
to achieve fast compilation.
