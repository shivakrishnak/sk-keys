---
layout: default
title: "Compiled vs Interpreted Languages"
parent: "CS Fundamentals — Paradigms"
nav_order: 12
permalink: /cs-fundamentals/compiled-vs-interpreted-languages/
number: "12"
category: CS Fundamentals — Paradigms
difficulty: ★☆☆
depends_on: Imperative Programming, Procedural Programming
used_by: Type Systems (Static vs Dynamic), JVM (Java Virtual Machine), Bytecode, Metaprogramming
tags: #foundational, #internals, #pattern, #jvm
---

# 12 — Compiled vs Interpreted Languages

`#foundational` `#internals` `#pattern` `#jvm`

⚡ TL;DR — Compiled languages translate source code to machine code before execution; interpreted languages execute source code line-by-line at runtime via an interpreter.

| #12             | Category: CS Fundamentals — Paradigms                                                   | Difficulty: ★☆☆ |
| :-------------- | :-------------------------------------------------------------------------------------- | :-------------- |
| **Depends on:** | Imperative Programming, Procedural Programming                                          |                 |
| **Used by:**    | Type Systems (Static vs Dynamic), JVM (Java Virtual Machine), Bytecode, Metaprogramming |                 |

---

### 📘 Textbook Definition

A **compiled language** is one whose source code is translated by a _compiler_ into target machine code (or intermediate bytecode) before execution. The resulting binary can be executed directly by the CPU or a virtual machine without further translation. An **interpreted language** is one whose source code is executed by an _interpreter_ at runtime, translating and executing each statement on the fly. Many modern languages use a hybrid approach: compile to bytecode (an intermediate representation), then interpret or JIT-compile that bytecode at runtime (Java, Python, JavaScript V8). The distinction affects startup time, execution speed, portability, and development cycle.

---

### 🟢 Simple Definition (Easy)

A compiled language is like translating a book into another language before the reader gets it. An interpreted language is like having a live translator read the book aloud, sentence by sentence, as you listen.

---

### 🔵 Simple Definition (Elaborated)

When you write C code and run `gcc myprogram.c -o myprogram`, the compiler reads your entire source code, analyses it, and produces an executable binary that the CPU runs directly. The original source code is no longer needed at runtime. Python works differently: when you run `python script.py`, the interpreter reads your source, converts it to bytecode, and executes it statement by statement — the interpreter is always present during execution. Java takes a middle path: `javac` compiles Java source to `.class` bytecode files, and then the JVM interprets (or JIT-compiles) that bytecode at runtime. This middle path gives Java the "write once, run anywhere" portability of an interpreted language with performance approaching native compilation.

---

### 🔩 First Principles Explanation

**The problem: source code is written for humans; CPUs execute binary instructions.**

A CPU understands only machine code — specific binary opcodes for its instruction set architecture (x86, ARM). Your Java or Python source code is written for human comprehension. Something must bridge the gap.

**Two strategies:**

**Strategy 1 — Compile ahead of time (AOT):**

```
  Source.c  ──► Compiler (gcc) ──► myprogram.exe
                                         │
                              CPU executes directly
                              at full native speed
                              no compiler at runtime
```

**Strategy 2 — Interpret at runtime:**

```
  Script.py  ──► Python Interpreter ──► results
                       │
               reads source line by line
               translates + executes on the fly
               interpreter always needed at runtime
```

**Strategy 3 — Hybrid: compile to bytecode, then interpret/JIT:**

```
  Source.java  ──► javac ──► .class (bytecode)
                                  │
                             JVM at runtime:
                         interpret bytecode OR
                         JIT-compile hot paths
                         to native machine code
```

**The trade-offs:**

- AOT compilation: fast execution, no startup overhead, platform-specific binary.
- Pure interpretation: portable, easy to debug, slow execution (10-100× slower).
- Bytecode + JIT: portable bytecode, near-native performance after warmup.

---

### ❓ Why Does This Exist (Why Before What)

WITHOUT compilation (pure interpretation of complex programs):

```
Interpreter executing Python CPython on a busy server:
- Each arithmetic operation: parse bytecode → dispatch → execute
- A tight loop of 10M iterations: ~50× slower than compiled C
- No CPU branch prediction optimisation
- JIT warmup provides no benefit in short-lived scripts
```

What breaks without compilation:

1. CPU-intensive algorithms (image processing, cryptography) are impractically slow in pure interpreters.
2. Type errors in rarely-executed code paths are never caught until that path runs in production.
3. Deployment requires the interpreter version to be installed on every target machine.

WITHOUT interpretation:

```
C binary compiled for x86-64 Linux:
- Does not run on ARM Mac without recompilation
- Compiled with DEBUG symbols vs RELEASE changes behaviour
- Crash is a segfault with no line number — harder to diagnose
```

What breaks without interpretation:

1. Platform portability requires recompilation for every target OS/CPU.
2. Development cycle: change code → compile (minutes for large projects) → run → debug.
3. No runtime introspection or dynamic code loading.

WITH bytecode + JIT (Java model):
→ Compile once → run on any JVM regardless of OS/CPU (portability).
→ JIT detects hot paths and compiles them to native machine code (performance).
→ Stack traces point to source file and line number (debuggability).
→ Startup pays a warmup cost; long-running servers reach near-native speed.

---

### 🧠 Mental Model / Analogy

> Think of two ways to read a foreign novel. Option A: hire a translator who produces a complete translated edition before you start reading. You read at full speed; the translator is never present again. Option B: hire a live interpreter who sits next to you and translates every sentence as you read. You always need them present; the process is slower but you can ask questions (debug) mid-read. Option C: the interpreter pre-translates common paragraphs they know you'll read often (JIT) — so frequently visited passages flow at near-full speed.

"Translator producing complete edition" = ahead-of-time compiler
"Reading the translation at full speed" = executing native machine code
"Live interpreter translating sentence-by-sentence" = interpreter at runtime
"Pre-translating common paragraphs" = JIT compilation of hot paths
"The translated edition" = compiled binary / bytecode

---

### ⚙️ How It Works (Mechanism)

**Full Compilation (C/C++/Rust/Go):**

```
┌───────────────────────────────────────────────────┐
│           Ahead-of-Time Compilation               │
│                                                   │
│  Source.c ──► Lexer ──► Parser ──► AST            │
│                                    │              │
│                              Type Check           │
│                                    │              │
│                              Optimiser            │
│                                    │              │
│                          Code Generator           │
│                                    │              │
│                          myprogram (ELF/PE)        │
│                          CPU executes directly    │
└───────────────────────────────────────────────────┘
```

**Java Hybrid (Bytecode + JIT):**

```
┌───────────────────────────────────────────────────┐
│            Java Execution Model                   │
│                                                   │
│  Source.java ──► javac ──► MyClass.class          │
│                             (bytecode)            │
│                                │                  │
│                           JVM loads               │
│                                │                  │
│                    ┌───────────┴──────────┐       │
│                    ▼                      ▼       │
│            Interpreter                JIT         │
│           (cold paths)            (hot paths)     │
│           (bytecode exec)     (native machine     │
│                                   code cache)     │
└───────────────────────────────────────────────────┘
```

**Python (bytecode interpreted):**

```
Source.py ──► CPython ──► .pyc (bytecode)
                              │
                     CPython interpreter
                     (eval loop — no JIT
                      in standard CPython)
```

**Key Performance Difference:**

| Approach                  | Startup       | Throughput               | Portability              |
| ------------------------- | ------------- | ------------------------ | ------------------------ |
| AOT (C/Rust/Go)           | Instant       | Fastest                  | Platform-specific binary |
| JIT (Java/JVM)            | Slow (warmup) | Near-native after warmup | Any JVM                  |
| Interpreted (Python/Ruby) | Fast          | 10-100× slower than C    | Any interpreter install  |

---

### 🔄 How It Connects (Mini-Map)

```
Source Code (human-readable)
        │
        ├──────────────────────────────────┐
        ▼                                  ▼
Compiler (AOT)                      Interpreter
(gcc, rustc, go build)             (python, ruby)
        │                                  │
        ▼                                  ▼
Native Binary ──────────► JVM Bytecode ──► JIT
(x86/ARM)                 (.class files)  (native)
        │                                  │
        └──────────────┬───────────────────┘
                       ▼
               CPU Execution
(you are here → Compiled vs Interpreted)
```

---

### 💻 Code Example

**Example 1 — C: compiled, runs natively:**

```bash
# Compile source to native binary
gcc -O2 hello.c -o hello

# Run — no compiler/interpreter present
./hello        # direct CPU execution
# → Hello, World!

# Platform-specific: hello binary works only on this OS/arch
file hello     # → ELF 64-bit LSB executable, x86-64
```

**Example 2 — Python: compiled to bytecode, then interpreted:**

```bash
# Run Python — interpreter translates+executes
python3 hello.py

# Python auto-generates bytecode cache
ls __pycache__/
# → hello.cpython-311.pyc  (cached bytecode)

# The .pyc is loaded on next run (skips re-parsing)
# but is still interpreted, not natively executed
```

**Example 3 — Java: compile to bytecode, JVM runs it anywhere:**

```bash
# Compile to platform-independent bytecode
javac Hello.java    # → Hello.class

# Inspect bytecode
javap -c Hello.class
# → 0: getstatic #2  // Field java/lang/System.out
#    3: ldc #3        // String "Hello, World!"
#    5: invokevirtual #4  // Method println

# Run on JVM (any platform)
java Hello          # → Hello, World!

# Same Hello.class runs on Linux, macOS, Windows
```

**Example 4 — JIT warmup effect:**

```java
// JVM cold: first 10,000 iterations interpreted
// JVM warm: JIT compiles the hot loop to native code
// Performance measurement changes significantly between
// the first and the 100,000th invocation

// Use JMH (Java Microbenchmark Harness) to account for warmup:
@Benchmark
@Warmup(iterations = 5)
@Measurement(iterations = 10)
public int squareLoop() {
    int sum = 0;
    for (int i = 0; i < 10_000; i++) sum += i * i;
    return sum;
}
```

---

### ⚠️ Common Misconceptions

| Misconception                                             | Reality                                                                                                                                                      |
| --------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| Java is an interpreted language                           | Java compiles to bytecode; the JVM JIT-compiles hot paths to native machine code — modern Java performance is close to C for long-running workloads          |
| Compiled languages are always faster                      | Go and Rust are compiled and fast; JVM-based code with JIT often outperforms Go for long-running server workloads due to runtime profile-guided optimisation |
| Python is purely interpreted                              | CPython compiles source to `.pyc` bytecode; the bytecode is then interpreted. PyPy uses JIT compilation and is significantly faster                          |
| Compiled binaries are always smaller                      | Go produces large static binaries; JVM languages ship a small `.jar` but require a separate JVM install                                                      |
| Source code is always needed to run interpreted languages | Python `.pyc` bytecode files can be deployed without source; the interpreter runs the bytecode directly                                                      |

---

### 🔥 Pitfalls in Production

**JVM warmup causing latency spikes on cold start**

```java
// BAD: deploy new instance and immediately route full traffic
// First 30 seconds: JIT hasn't compiled hot paths
// → latency 3-10× higher than steady state
// → health check passes but real users see slow responses

// GOOD: use warmup strategies
// 1. Canary deployment: route 1% traffic to new instance first
// 2. JVM warmup flags: -XX:+TieredCompilation (default in Java 8+)
// 3. Spring Boot: configure warmup endpoint that exercises hot paths
// 4. GraalVM native image: AOT-compile to avoid warmup entirely
```

---

**Python GIL limiting multi-core utilisation**

```python
# BAD: assume Python threads use multiple CPU cores
import threading

def cpu_work():
    for _ in range(10_000_000):
        pass  # CPU-bound

# Two threads — still run on ONE core due to GIL
t1 = threading.Thread(target=cpu_work)
t2 = threading.Thread(target=cpu_work)
t1.start(); t2.start()
# Wall time ≈ same as single-threaded — GIL prevents parallel execution

# GOOD: use multiprocessing for CPU-bound parallelism
from multiprocessing import Process
```

The GIL is a CPython interpreter design choice, not a language limitation.

---

**Deploying the wrong bytecode version**

```bash
# BAD: compile with Java 21, deploy on Java 11 JVM
javac --release 21 Service.java
java -version  # → openjdk version "11.0.x"
java Service   # → UnsupportedClassVersionError: 65.0 (Java 21)
               # service crashes at startup

# GOOD: always specify --release target for deployment JVM
javac --release 11 Service.java  # bytecode compatible with Java 11+
```

---

### 🔗 Related Keywords

- `JVM (Java Virtual Machine)` — the runtime that interprets and JIT-compiles Java bytecode
- `Bytecode` — the intermediate representation that compiled Java, Python, and .NET produce
- `JIT Compiler` — the component that compiles hot bytecode to native machine code at runtime
- `Type Systems (Static vs Dynamic)` — compiled languages tend to be statically typed; interpreted languages tend to be dynamically typed (though not always)
- `Metaprogramming` — interpreted languages enable richer runtime metaprogramming due to constant access to the interpreter
- `GraalVM` — ahead-of-time compiler for JVM languages that produces native binaries, eliminating warmup
- `Python GIL` — the Global Interpreter Lock: a CPython implementation detail affecting multi-threaded CPU parallelism

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ KEY IDEA     │ Compiled: translate before run (faster).  │
│              │ Interpreted: translate while running.     │
│              │ JIT: both — bytecode + hot-path native    │
├──────────────┼───────────────────────────────────────────┤
│ USE WHEN     │ Compiled (AOT): max perf, systems code    │
│              │ JIT (JVM): portable + near-native perf    │
│              │ Interpreted: scripting, fast dev cycle    │
├──────────────┼───────────────────────────────────────────┤
│ AVOID WHEN   │ Pure interpretation for CPU-bound work    │
│              │ AOT for polyglot/multi-platform deploys   │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "Compiled is the finished bridge; JIT     │
│              │ paves the road as you drive; interpreted  │
│              │ builds each plank as you step."           │
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ JVM → Bytecode → JIT Compiler → GraalVM   │
│              │ → Python GIL → AOT vs JIT trade-offs      │
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** A Java service deployed as a GraalVM native image has a 10ms cold start time and a throughput of 80,000 requests per second from the first request. The same service on a traditional JVM starts in 3 seconds and reaches 120,000 requests per second after 2 minutes of warmup. In a Kubernetes environment that scales instances up and down frequently with requests arriving immediately on pod startup, which deployment model wins on P99 latency, and what architectural pattern compensates for the JVM's warmup period in this scenario?

**Q2.** CPython's GIL prevents true parallel execution of Python threads for CPU-bound work. The `multiprocessing` module bypasses this by using separate processes. Describe exactly what the GIL protects in CPython's interpreter internals, why simply removing it would break existing C extension modules, and why Python 3.13's experimental free-threaded mode (PEP 703) still requires performance trade-offs even without the GIL.
