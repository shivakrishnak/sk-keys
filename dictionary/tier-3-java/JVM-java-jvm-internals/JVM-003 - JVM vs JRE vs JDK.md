---
id: JVM-003
title: JVM vs JRE vs JDK
category: Java & JVM Internals
tier: tier-3-java
folder: JVM-java-jvm-internals
difficulty: ★☆☆
depends_on: JVM-001
used_by: JVM-004, JVM-005
related: JVM-006, JVM-007, JVM-047
tags:
  - jvm
  - java
  - foundational
  - internals
status: complete
version: 1
layout: default
parent: "Java & JVM Internals"
grand_parent: "Technical Dictionary"
nav_order: 3
permalink: /jvm/jvm-vs-jre-vs-jdk/
---

# JVM-003 - JVM vs JRE vs JDK

**⚡ TL;DR** - JVM runs bytecode; JRE = JVM + class libraries; JDK = JRE + compiler + dev tools. Development needs JDK; production can run with just JRE (or JDK).

| Field | Value |
|---|---|
| **Depends on** | [[JVM-001 - What Is the JVM - A Mental Model]] |
| **Used by** | [[JVM-004 - How Java Code Runs - Bytecode to Execution]], [[JVM-005 - The JVM Ecosystem Map]] |
| **Related** | [[JVM-006 - JRE]], [[JVM-007 - JDK]], [[JVM-047 - AOT Compilation]] |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
Java's three-component architecture confuses every new developer. Teams deploy the wrong artifact to production - running a full JDK with compiler tooling on a production server when only the runtime is needed, adding unnecessary attack surface and disk footprint. Conversely, developers who install only the JRE find they cannot compile code and wonder why `javac` is missing.

**THE BREAKING POINT:**
As Java matured, the runtime and the development toolchain diverged in purpose. End users running applets or desktop applications needed only the runtime. Developers needed compilers, debuggers, and profilers. Server operators needed a middle ground. Three distinct packages emerged from one confusing name: "Java."

**THE INVENTION MOMENT:**
Sun formalised the JVM/JRE/JDK hierarchy in Java 1.1 (1997). The JRE became the minimal runtime for end users. The JDK became the development superset. This separation allowed lighter distribution for non-developers while keeping the full toolchain available for engineers.

**EVOLUTION:**
- Java 9 (2017): JDK modularised via JPMS. JRE as a separate distribution was eliminated. The JDK became the recommended distribution for both development and production.
- Java 11+: Oracle stopped providing standalone JRE downloads. Users build custom runtimes using `jlink`.
- GraalVM Native Image: eliminates the JRE entirely at runtime - produces a self-contained native binary with no JVM required on the target machine.

---

### 📘 Textbook Definition

The **Java Development Kit (JDK)** is the full development environment containing: the Java compiler (`javac`), the Java runtime (`java`), standard class libraries, development tools (`jshell`, `jdeps`, `jlink`, `jcmd`, `jmap`, `jstack`), and documentation. The **Java Runtime Environment (JRE)** is a subset containing only what is needed to run compiled Java applications: the JVM and the standard class libraries. The **Java Virtual Machine (JVM)** is the execution engine at the core - the component that loads, verifies, and executes bytecode. JDK ⊃ JRE ⊃ JVM. Since Java 9, the JRE as a standalone distribution has been deprecated; the JDK is the standard distribution.

---

### ⏱️ Understand It in 30 Seconds

**One line:** JDK is for developers; JVM is the execution engine inside everything.

> Like a car workshop: the JVM is the engine (runs the car). The JRE is a complete car (engine + body + wheels). The JDK is the workshop (car + all the tools to build and maintain cars).

**One insight:** Since Java 9, the distinction matters less in practice - the JDK is shipped as a single unit. The real modern decision is: "Full JDK, `jlink` custom runtime, or GraalVM Native Image?" The JRE vs JDK debate is historical context, not a current operational choice.

---

### 🔩 First Principles Explanation

**CORE INVARIANTS:**
1. Running a Java program requires: bytecode interpreter/executor + standard libraries
2. Building a Java program additionally requires: compiler, linker/packager, debug tools
3. Ship the minimum surface area needed for each role

**DERIVED DESIGN:**
From invariant 1: the JVM alone is not enough to run a Java program - `java.lang.String`, `java.util.List`, and all standard library classes must be present. The JRE packages JVM + standard library.
From invariant 2: developers additionally need `javac`, `jar`, `jdeps`, etc. The JDK adds these atop the JRE.
From invariant 3: production servers historically installed JRE (smaller, fewer attack vectors).

**THE TRADE-OFFS:**
**Gain (JRE-only production):** Smaller footprint, fewer installed tools that could be misused
**Cost (JRE-only production):** Cannot run `jmap`, `jstack`, `jcmd` - common production diagnostic tools that require JDK
**Gain (JDK production):** Full diagnostic tooling available; simpler "one thing to install"
**Cost (JDK production):** Compiler and build tools on production host increases attack surface marginally

**ESSENTIAL vs ACCIDENTAL COMPLEXITY:**
**Essential:** Any runtime must package both an execution engine and the standard library it depends on. This is irreducible.
**Accidental:** Shipping the full compiler toolchain to production machines is accidental complexity. `jlink` custom runtimes address this by packaging exactly the modules needed and nothing else.

---

### 🧪 Thought Experiment

**SETUP:** You deploy a Spring Boot `.jar` to production. The server has only a JVM binary with no class libraries. No `java.lang`, no `java.util`, no `java.io`.

**WHAT HAPPENS WITHOUT JRE (JVM only):**
The JVM starts. It loads your application's bytecode. The first `new String()` call triggers loading of `java.lang.String`. The class loader searches the classpath - but `rt.jar` (or the module system) is absent. `ClassNotFoundException: java.lang.String`. The JVM crashes before your first line of application code runs.

**WHAT HAPPENS WITH JRE (JVM + class libraries):**
The JVM starts. All standard library classes are available. Your application loads and runs normally.

**THE INSIGHT:**
The JVM cannot run any realistic Java program alone. The standard library is a required runtime dependency, not an optional feature. The JRE packages this dependency. Modern JDK distributions include it all; the conceptual separation matters for understanding what the minimum runtime requirements are.

---

### 🧠 Mental Model / Analogy

> Think of the JDK as a professional kitchen. The JVM is the stove (execution unit). The JRE is the stove plus all standard utensils and pantry staples (you can cook a meal). The JDK is the full professional kitchen with stove, pantry, plus all chef's knives, blowtorch, immersion circulator, and culinary textbooks (you can cook anything and teach others).

Element mapping:
- Stove = JVM execution engine
- Pantry staples and utensils = Java standard library (`java.lang`, `java.util`, etc.)
- Chef's tools = `javac`, `jshell`, `jlink`, `jmap`, `jstack`
- JRE = stove + pantry
- JDK = entire professional kitchen

Where this analogy breaks down: in a real kitchen, adding tools does not add security risk. In a server environment, installing the JDK compiler on a production host is a minor but real attack surface increase that the JRE-only model was designed to prevent.

---

### 📶 Gradual Depth - Four Levels

**Level 1 - What it is (anyone can understand):**
If you want to run a Java program, you need the Java Runtime Environment (JRE). If you want to write and compile Java programs, you need the Java Development Kit (JDK). The JDK includes everything in the JRE plus extra tools for developers.

**Level 2 - How to use it (junior developer):**
Install the JDK on your development machine - this gives you `javac` (compiler), `java` (runtime), and tools like `jshell`. For production servers, the JDK is also fine since Java 9 eliminated the standalone JRE. Check your Java version: `java -version` and `javac -version` - both should match. Mismatches indicate split installations and cause `UnsupportedClassVersionError`.

**Level 3 - How it works (mid-level engineer):**
The JDK contains: `bin/` (executables: `javac`, `java`, `jshell`, `jdeps`, `jlink`, `jcmd`, `jmap`, `jstack`, `jstat`), `lib/` (class libraries as modules in `jmods/`), `conf/` (security policy, logging config), and `include/` (JNI headers). The JVM lives inside `bin/java` and is loaded when you run `java`. The compiler (`javac`) reads `.java` source and writes `.class` bytecode. Since Java 9, the standard library is split into named modules (e.g., `java.base`, `java.sql`, `java.xml`) stored in `jmods/`. `jlink` composes a custom runtime from selected modules.

**Level 4 - Why it was designed this way (senior/staff):**
The JDK/JRE split predates security awareness of reducing attack surface. Its original rationale was distribution size: JRE was a 25MB download on dial-up connections, while JDK was 60MB. Size mattered when bandwidth was scarce. As bandwidth improved and security became paramount, the split became more of a security partition than a size optimisation. Java 9's JPMS modularisation made a more principled separation possible: `jlink` can produce a minimal runtime of exactly the modules your application uses, smaller and more secure than any historical JRE. This is the modern answer to the JRE/JDK question.

**Expert Thinking Cues:**
- `java -version` shows runtime; `javac -version` shows compiler - both should match in CI
- `jlink --list-modules` reveals what modules a custom runtime contains
- When optimising Docker image size, think `jlink` custom runtime, not "install JRE not JDK"

---

### ⚙️ How It Works (Mechanism)

**JDK directory structure (Java 17+):**
```
$JAVA_HOME/
  bin/
    java          <- JVM launcher
    javac         <- Java compiler
    jshell        <- Interactive REPL
    jlink         <- Custom runtime builder
    jdeps         <- Dependency analyser
    jcmd          <- JVM diagnostic tool
    jmap          <- Heap analysis
    jstack        <- Thread dump
    jstat         <- GC/performance stats
  lib/
    modules       <- Compiled module images
    src.zip       <- Standard library source
  conf/
    security/     <- Security policies
    logging.properties
  jmods/
    java.base.jmod
    java.sql.jmod
    ...
  include/        <- JNI C headers
  legal/          <- Licenses
```

**How `java` uses the JDK components:**
1. `java -jar app.jar` launches the JVM via the `java` launcher binary
2. JVM locates and loads `java.base` module (bootstrap classes)
3. Class loader resolves application classes
4. Execution engine (JIT + interpreter) executes bytecode
5. Diagnostic tools (`jcmd`, `jmap`) attach to the running JVM via the JVM attach mechanism

---

### 🔄 The Complete Picture - End-to-End Flow

**NORMAL FLOW:**
```
  Developer machine (JDK)
       |
  javac Hello.java   <- compiler from JDK
       |
  Hello.class        <- platform-neutral
       |
  jar -cf app.jar Hello.class
       |                <- YOU ARE HERE
  Production server (JDK or jlink runtime)
       |
  java -jar app.jar
       |
  JVM loads + executes Hello.class
```

**FAILURE PATH:**
- Developer installs only JRE: `javac: command not found` - need JDK for compilation
- Version mismatch: compile with Java 21 JDK, run on Java 17 JVM: `UnsupportedClassVersionError`
- Missing module: using `java.sql` but custom `jlink` runtime did not include it: `Module not found`

**WHAT CHANGES AT SCALE:**
Modern Dockerised deployments use `jlink` to create minimal custom runtimes inside containers:
```bash
# Build custom runtime with only needed modules
jlink --add-modules java.base,java.net.http \
      --output custom-jre/
# Docker final image: copy custom-jre/ + app.jar
# No full JDK required - image can be 60-80MB smaller
```

---

### 💻 Code Example

**BAD - installing full JDK unnecessarily in production Docker image:**
```dockerfile
# Uses full JDK (400MB+) in production
FROM eclipse-temurin:21-jdk
COPY app.jar /app/app.jar
ENTRYPOINT ["java", "-jar", "/app/app.jar"]
```

**GOOD - multi-stage: JDK for build, jlink runtime for production:**
```dockerfile
# Stage 1: build with full JDK
FROM eclipse-temurin:21-jdk AS builder
COPY . /src
WORKDIR /src
RUN javac -d out src/Main.java

# Stage 2: custom minimal runtime
FROM eclipse-temurin:21-jdk AS jlink-builder
RUN jlink \
  --add-modules java.base,java.net.http,java.logging \
  --strip-debug \
  --no-man-pages \
  --compress 2 \
  --output /custom-jre

# Stage 3: final minimal image
FROM debian:bookworm-slim
COPY --from=jlink-builder /custom-jre /custom-jre
COPY --from=builder /src/out /app
ENTRYPOINT ["/custom-jre/bin/java", "-cp", "/app", "Main"]
```

**How to test / verify correctness:**
```bash
# Verify custom runtime contains expected modules
/custom-jre/bin/java --list-modules
# Verify compiler is NOT present in production image
docker run --rm my-prod-image which javac  # should return empty
# Verify runtime version
/custom-jre/bin/java -version
```

---

### ⚖️ Comparison Table

| Aspect | JVM only | JRE (pre-Java 9) | JDK | jlink custom runtime |
|---|---|---|---|---|
| Can run Java programs | No (missing stdlib) | Yes | Yes | Yes (selected modules) |
| Can compile Java | No | No | Yes | No |
| Diagnostic tools | No | No | Yes | Subset (add manually) |
| Footprint | Smallest | ~50MB | ~200MB | 30-80MB (configurable) |
| Security surface | Minimal | Low | Moderate | Minimal |
| Recommended for | Not standalone | Legacy | Dev + Production | Optimised production |

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| "Production should always use JRE not JDK" | Since Java 9, standalone JRE is not distributed. JDK is the standard for both dev and prod. Use `jlink` for minimised runtimes. |
| "JVM and JRE are the same thing" | JVM is only the execution engine. JRE = JVM + standard class libraries. You cannot run `new String()` without the JRE's class libraries. |
| "Installing JDK gives two Java installs" | JDK contains the JRE (and JVM) inside it. One install, three conceptual layers. |
| "jlink is only for advanced users" | `jlink` is the modern replacement for JRE-only deployments and is standard practice in Docker/containerised environments. |
| "All JDKs are equal" | OpenJDK, Oracle JDK, Amazon Corretto, Eclipse Temurin, and GraalVM differ in bundled GC algorithms, JIT optimisations, and included tools. |

---

### 🚨 Failure Modes & Diagnosis

**Failure Mode 1: UnsupportedClassVersionError from JDK/JRE mismatch**
**Symptom:** `java.lang.UnsupportedClassVersionError: Unsupported major.minor version`
**Root Cause:** Application compiled with newer JDK than the runtime JVM
**Diagnostic:**
```bash
javap -verbose MyClass.class | grep "major version"
java -version
# major version 65 = Java 21; 61 = Java 17; 55 = Java 11
```
**Fix:** Align JDK compile target with runtime JVM version
BAD: compile with default `javac` (picks up JDK 21), run with JVM 17
GOOD: `javac --release 17 ...` or upgrade runtime JVM to Java 21
**Prevention:** Pin `sourceCompatibility` and `targetCompatibility` in Gradle/Maven; use same JDK version in CI and production

**Failure Mode 2: Missing diagnostic tools in minimal runtime**
**Symptom:** `jmap: No such file` or `jcmd: not found` when debugging production
**Root Cause:** Production image uses `jlink` custom runtime without diagnostic tools
**Diagnostic:**
```bash
ls /custom-jre/bin/   # check what binaries exist
```
**Fix:**
Add diagnostic tool modules to `jlink` build:
```bash
jlink --add-modules java.base,...,jdk.management,jdk.attach \
      --output /custom-jre
```
Or maintain separate diagnostic-enabled runtime for troubleshooting
**Prevention:** Include `jdk.management` and `jdk.attach` in all `jlink` production runtimes

**Failure Mode 3: Module not found in custom jlink runtime**
**Symptom:** `java.lang.module.FindException: Module java.sql not found`
**Root Cause:** Application uses JDBC but `java.sql` module was excluded from `jlink` output
**Diagnostic:**
```bash
/custom-jre/bin/java --list-modules | grep sql
# If empty, java.sql was not included
jdeps --print-module-deps myapp.jar
# Lists all required modules
```
**Fix:**
Re-run `jlink` with the correct module list; use `jdeps` first to enumerate all required modules
**Prevention:** Always run `jdeps --print-module-deps app.jar` before `jlink`; include output in CI

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**
- [[JVM-001 - What Is the JVM - A Mental Model]] - The JVM concept

**Builds On This (learn these next):**
- [[JVM-004 - How Java Code Runs - Bytecode to Execution]] - What the JVM actually does
- [[JVM-047 - AOT Compilation]] - Alternative to JRE: GraalVM Native Image (no JVM at runtime)

**Alternatives / Comparisons:**
- [[JVM-006 - JRE]] - JRE deep dive
- [[JVM-007 - JDK]] - JDK deep dive

---

### 📌 Quick Reference Card

```
+--------------------------------------------------+
| WHAT IT IS    | Three nested Java components:     |
|               | JVM inside JRE inside JDK         |
+--------------------------------------------------+
| PROBLEM       | Confusion about what to install   |
|               | for dev vs production             |
+--------------------------------------------------+
| KEY INSIGHT   | JDK = compiler + JRE;             |
|               | use jlink for minimal production  |
+--------------------------------------------------+
| USE WHEN      | Dev: JDK always.                  |
|               | Prod: JDK or jlink custom runtime |
+--------------------------------------------------+
| AVOID WHEN    | "Install JRE only on prod" is     |
|               | obsolete advice since Java 9      |
+--------------------------------------------------+
| TRADE-OFF     | JDK footprint vs diagnostic       |
|               | tool availability                 |
+--------------------------------------------------+
| ONE-LINER     | javac (JDK) -> .class -> java (JRE)|
+--------------------------------------------------+
| NEXT EXPLORE  | JVM-004 execution mechanics,      |
|               | JVM-047 jlink/native image        |
+--------------------------------------------------+
```

**If you remember only 3 things:**
1. JDK contains JRE contains JVM - nested subsets
2. Since Java 9, standalone JRE is gone - use JDK or jlink custom runtime
3. `jlink` creates minimal, module-specific runtimes for production Docker images

**Interview one-liner:** "JVM executes bytecode; JRE = JVM + standard library; JDK = JRE + compiler + dev tools. Since Java 9, the JDK is the standard for all environments."

---

### 💎 Transferable Wisdom

**Reusable Engineering Principle:** Separate runtime from development toolchain. Ship to production only what is needed to run, not what is needed to build. Build tools add attack surface, disk footprint, and cognitive overhead in production environments.

**Where else this pattern appears:**
- Node.js: `devDependencies` vs `dependencies` in `package.json` - test frameworks stay off production
- Docker: multi-stage builds compile in `FROM node:20` but run in `FROM node:20-alpine` (smaller runtime)
- Python: `pip install -r requirements.txt` vs `requirements-dev.txt` - test tools excluded from production images

---

### 💡 The Surprising Truth

Since Java 11, Oracle no longer provides a standalone JRE download. The canonical guidance is: use the JDK everywhere, or use `jlink` to create a purpose-built runtime. This means that for the first time in Java's history, the "smallest Java runtime" is not a pre-built artifact from Oracle - it is something you build yourself with `jlink`. A `jlink`-built runtime for a simple HTTP service can be as small as 30MB, smaller than any historical JRE. The JRE/JDK distinction has been replaced by a build-time decision about which modules to include - a more precise and more powerful model.

---

### 🧠 Think About This Before We Continue

**Q1 (System Interaction):** A security scanner reports that your production Docker image contains `javac` - the Java compiler. You are running a `FROM eclipse-temurin:21-jdk` base image. Why is the compiler present, and what is the exact change needed to remove it without breaking the application?
*Hint:* Investigate the multi-stage Docker build pattern and the `jlink` tool documented in this entry and [[JVM-007 - JDK]].

**Q2 (Scale):** You have 500 microservices each packaged as Docker images. Each uses `FROM eclipse-temurin:21-jdk` (300MB JDK layer). If you switch to `jlink` minimal runtimes of 50MB each, what is the infrastructure saving, and what new risk do you introduce that a single shared JDK base image did not have?
*Hint:* Think about security patches. When a JVM vulnerability is disclosed, how does the patch propagation differ between a shared base image and 500 custom `jlink` runtimes?

**Q3 (Design Trade-off):** GraalVM Native Image eliminates the JRE entirely at runtime - the native binary contains everything it needs. Under what specific production scenario does this approach become worse than a traditional JDK deployment, despite the footprint and startup advantages?
*Hint:* Consider the JIT compilation warm-up curve in [[JVM-041 - JIT Compiler]] and what happens to throughput of a long-running, CPU-intensive server after 30 minutes of operation.
