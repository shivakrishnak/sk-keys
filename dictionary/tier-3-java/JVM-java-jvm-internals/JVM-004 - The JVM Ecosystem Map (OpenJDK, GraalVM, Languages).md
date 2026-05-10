---
id: JVM-008
title: "The JVM Ecosystem Map (OpenJDK, GraalVM, Languages)"
category: Java & JVM Internals
tier: tier-3-java
folder: JVM-java-jvm-internals
difficulty: ★☆☆
depends_on: JVM-001, JVM-002, JVM-003
used_by:
related: JVM-051, JVM-052, JVM-053
tags:
  - jvm
  - java
  - foundational
  - architecture
status: complete
version: 2
layout: default
parent: "Java & JVM Internals"
grand_parent: "Technical Dictionary"
nav_order: 4
permalink: /jvm/the-jvm-ecosystem-map/
---

# JVM-004 - The JVM Ecosystem Map (OpenJDK, GraalVM, Languages)

**⚡ TL;DR** - The JVM ecosystem spans multiple JDK distributions, GC-variant runtimes, polyglot VMs, and 30+ JVM-targeting languages - all sharing one bytecode standard.

| Field | Value |
|---|---|
| **Depends on** | [[JVM-001 - What Is the JVM - A Mental Model]], [[JVM-002 - Why the JVM Was Invented]], [[JVM-003 - JVM vs JRE vs JDK]] |
| **Used by** | (none - survey entry) |
| **Related** | [[JVM-051 - AOT Compilation]], [[JVM-052 - GraalVM]], [[JVM-053 - Native Image]] |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
A developer joins a Java project and sees: `temurin-21`, `corretto-17`, `graalvm-21`, a Kotlin service, and a Scala analytics job all coexisting. Without a map, they cannot answer: are these the same JVM? Are they compatible? Which should we use for new services? When a CVE is published against "the JDK," which distributions are affected?

**THE BREAKING POINT:**
As the JVM ecosystem fragmented post-Oracle/Sun acquisition in 2010, many competing distributions, languages, and toolchains emerged. Teams make uninformed decisions: using an end-of-life Oracle JDK without realising free OpenJDK alternatives exist, running Kotlin without understanding it targets the same JVM, or choosing GraalVM without knowing it requires a separate compatibility matrix.

**THE INVENTION MOMENT:**
The JVM Specification as a public standard is the root of the ecosystem. Once Sun published the specification, any organisation could build a compliant JVM. OpenJDK became the open-source reference implementation. Distributions (Temurin, Corretto, Zulu) are built from OpenJDK source with vendor additions. GraalVM extends HotSpot with a new JIT and polyglot engine.

**EVOLUTION:**
- 1995: Sun JDK - single vendor, proprietary
- 2006: OpenJDK announced - open-source reference implementation
- 2010: Oracle acquires Sun; Oracle JDK vs OpenJDK split begins
- 2017: AdoptOpenJDK (now Eclipse Temurin) provides free binaries
- 2018: GraalVM 1.0 released - polyglot + Native Image
- 2021: Oracle JDK free again for production use (NFTC license)
- 2024: Major distributions: OpenJDK, Temurin, Corretto, Zulu, GraalVM, Liberica, Microsoft Build

---

### 📘 Textbook Definition

The **JVM ecosystem** consists of four concentric rings: (1) **The Specification**: the JVM Specification and Java SE Specification define bytecode format and API contracts that all conforming implementations must satisfy. (2) **Runtimes**: JVM implementations that execute bytecode - HotSpot (in OpenJDK), Eclipse OpenJ9, GraalVM's JVMCI-extended HotSpot, and others. (3) **Distributions**: pre-built, tested JDK binaries from different vendors (Eclipse Temurin, Amazon Corretto, Azul Zulu, Microsoft Build of OpenJDK, GraalVM CE) that build from OpenJDK source. (4) **Languages**: programming languages that compile to JVM bytecode - Kotlin, Scala, Clojure, Groovy, JRuby, Jython, and others - all running on any conforming JVM without modification.

---

### ⏱️ Understand It in 30 Seconds

**One line:** The JVM ecosystem is one bytecode standard, many implementations, and dozens of languages all interoperating.

> Like the internet's TCP/IP: one protocol specification, thousands of hardware vendors implementing it (all compatible), and unlimited application protocols running on top (HTTP, SMTP, WebSocket).

**One insight:** All major JVM distributions (Temurin, Corretto, Zulu, GraalVM) are functionally equivalent for most applications - they run the same bytecode and pass the same TCK (Technology Compatibility Kit) tests. Choosing between them is a support, licensing, and specific-feature decision, not a compatibility decision.

---

### 🔩 First Principles Explanation

**CORE INVARIANTS:**
1. The JVM Specification is the source of truth - not any implementation
2. Any TCK-compliant JVM is a valid runtime for any valid bytecode
3. JVM languages must compile to valid bytecode - they need not resemble Java
4. Distributions add vendor-specific support and tooling but must not break compatibility

**DERIVED DESIGN:**
From invariant 1: when Oracle changes the JVM Specification (via JSRs/JEPs), all distributions must eventually conform.
From invariant 2: Kotlin `.class` files run on any JVM - Kotlin does not require a special runtime.
From invariant 3: Scala's functional features (case classes, pattern matching) are implemented by the Scala compiler emitting bytecode patterns - the JVM knows nothing about them.

**THE TRADE-OFFS:**
**Gain:** Ecosystem diversity (multiple vendors, multiple languages, tooling breadth)
**Cost:** Decision fatigue (which distribution? which language?); TCK gaps (some vendors lag behind specification updates)

**ESSENTIAL vs ACCIDENTAL COMPLEXITY:**
**Essential:** Multiple distributions naturally arise from an open specification. This is a feature, not a problem.
**Accidental:** Vendor licensing confusion (Oracle JDK free vs paid history) added accidental complexity. OpenJDK and Temurin eliminate this confusion.

---

### 🧪 Thought Experiment

**SETUP:** You are the CTO of a startup. You have Java services (Spring Boot), a Kotlin API gateway, a Scala analytics pipeline, and you are evaluating GraalVM Native Image for serverless functions. All run in Kubernetes.

**WHAT HAPPENS WITHOUT UNDERSTANDING THE ECOSYSTEM MAP:**
You install three different JDKs without realising they are the same OpenJDK source. Your Kotlin team asks "which JVM should we use?" and nobody knows. A security vulnerability is announced for `log4j` - your team patches Java services but does not check the Kotlin or Scala services (they are also JVM-based and also affected). You evaluate GraalVM Native Image for Spring Boot and hit reflection limitations nobody warned you about.

**WHAT HAPPENS WITH THE MAP:**
You standardise on Temurin 21 LTS for all services. Your Kotlin, Scala, and Java code all run on the same JVM version. When the `log4j` CVE lands, you patch the JVM version fleet-wide. For GraalVM Native Image evaluation, you know it has closed-world assumption limitations and test your Spring Boot reflection usage against it first.

**THE INSIGHT:**
The ecosystem map reveals what is shared (bytecode format, JVM runtime, tooling, monitoring) and what is distinct (language syntax, standard library, compilation model). This shared foundation is why JVM languages interoperate: a Kotlin class can extend a Java class; a Scala actor can call a Java API; a Groovy script can import Kotlin code.

---

### 🧠 Mental Model / Analogy

> Think of the JVM ecosystem as a city built on a shared infrastructure grid. The JVM Specification is the building code that every structure must follow. OpenJDK is the reference building. The distributions (Temurin, Corretto, Zulu) are different construction companies using the same building code - you get the same structure, different service contracts. Languages (Kotlin, Scala, Clojure) are architectural styles - different facades and floor plans - but all connected to the same water, electricity, and sewage infrastructure (the JVM runtime services).

Element mapping:
- Building code = JVM Specification
- Reference building = OpenJDK HotSpot
- Construction companies = distribution vendors (Adoptium, Amazon, Azul)
- Architectural styles = programming languages (Kotlin, Scala, Clojure)
- Infrastructure grid = JVM runtime services (GC, JIT, class loading, monitoring)

Where this analogy breaks down: in a city, different buildings are isolated. On the JVM, code from different languages (Java + Kotlin + Scala) can be mixed in the same JVM process and even the same class hierarchy - a Kotlin data class can extend a Java abstract class.

---

### 📶 Gradual Depth - Four Levels

**Level 1 - What it is (anyone can understand):**
"Java" is not one thing - it is a family. OpenJDK is the open-source core. Companies like Amazon, Red Hat, and Azul take OpenJDK and release their own builds with support contracts. Programming languages like Kotlin and Scala compile to the same format Java uses, so they can run on any Java virtual machine. GraalVM is an enhanced JVM that can also compile Java to a standalone native program.

**Level 2 - How to use it (junior developer):**
For most developers: install Eclipse Temurin (from adoptium.net) - it is the community-recommended OpenJDK distribution, free for production, with LTS versions. Use Java 21 LTS or Java 17 LTS. If you need native compilation, use GraalVM CE. If you are in an AWS environment, Amazon Corretto is pre-installed and supported. Manage JDK versions with `sdkman` (Linux/macOS) or `scoop`/`jabba` (Windows). Never mix multiple JDK installations for one application - it causes confusing errors.

**Level 3 - How it works (mid-level engineer):**
All distributions are built from the OpenJDK source tree. Each vendor applies their own patches (GC configuration, performance tuning, security backports) and builds for their supported platforms. The TCK (Technology Compatibility Kit) test suite validates compliance. For enterprise support, vendors provide multi-year patch commitments beyond OpenJDK's 6-month release cycle. GraalVM extends HotSpot with JVMCI (JVM Compiler Interface) to replace the C2 JIT with the Graal compiler, and adds the Truffle framework for polyglot language implementations (JavaScript, Python, Ruby on the JVM).

**Level 4 - Why it was designed this way (senior/staff):**
The multi-distribution ecosystem is a consequence of OpenJDK's open governance model. The JCP (Java Community Process) standardises APIs via JSRs; JEPs (JDK Enhancement Proposals) govern OpenJDK development. Any vendor can fork OpenJDK, apply patches, and release - as long as they pass the TCK they may call their product "Java." This created healthy competition: Azul's Zing introduced C4 (Continuously Concurrent Compacting Collector) with sub-millisecond GC pauses years before ZGC appeared in OpenJDK. IBM's OpenJ9 introduced ahead-of-time class data sharing (now replicated in OpenJDK as AppCDS). Amazon's Corretto contributed performance fixes specific to AWS instance types. The ecosystem produces innovation that feeds back into OpenJDK.

**Expert Thinking Cues:**
- When choosing a JDK for production: "Is there a support SLA?" OpenJDK community support is 6 months per release; Temurin LTS has 8-10 years
- When a JVM vulnerability is disclosed, check if it affects all distributions (usually yes) or vendor-specific patches
- GraalVM CE vs GraalVM EE: CE is free; EE includes enterprise GC (G1GC improvements), Native Image PGO, and multi-layer compilation caching

---

### ⚙️ How It Works (Mechanism)

**Distribution Relationship:**
```
  JVM Specification (Oracle/JCP)
          |
    OpenJDK source (open-source)
          |
  +-------+--------+----------+
  |       |        |          |
Temurin Corretto  Zulu   GraalVM CE
(Adoptium)(Amazon)(Azul) (Oracle)
          |
  [Vendor-specific patches]
  [TCK validation]
  [Platform builds: linux/arm64, etc.]
```

**JVM Language Compilation:**
```
  Kotlin source  ->  [kotlinc]  ->  .class bytecode
  Scala source   ->  [scalac]   ->  .class bytecode
  Clojure source ->  [lein]     ->  .class bytecode
  Java source    ->  [javac]    ->  .class bytecode
                            |
                     Any JVM runtime
```

**GraalVM Extended Architecture:**
```
  OpenJDK HotSpot (base)
       |
  JVMCI interface
       |
  Graal JIT compiler (replaces C2)
       |
  Truffle framework
       |
  Language implementations:
    GraalJS (JavaScript)
    GraalPy (Python)
    TruffleRuby
    FastR (R)
```

---

### 🔄 The Complete Picture - End-to-End Flow

**NORMAL FLOW:**
```
  Choose distribution     <- YOU ARE HERE
       |
  Install JDK (e.g. Temurin 21)
       |
  Write code in Java/Kotlin/Scala
       |
  Compile to .class bytecode
       |
  Deploy to any compatible JVM
  (same or different distribution)
       |
  JVM executes bytecode
```

**FAILURE PATH:**
- Version incompatibility: `.class` compiled for Java 21 run on Java 17 JVM: `UnsupportedClassVersionError`
- TCK non-compliance: rare edge case; most major distributions pass TCK
- GraalVM Native Image closed-world failure: reflection-heavy frameworks (Spring without native support) may fail at image build time

**WHAT CHANGES AT SCALE:**
At scale, fleet standardisation matters more than distribution choice. Mixing Temurin 21 with Corretto 17 with Oracle JDK 11 in the same fleet creates three separate monitoring profiles, three patch schedules, and three sets of GC tuning parameters. Standardise on one distribution and one LTS version across the fleet.

---

### 💻 Code Example

**Checking your JDK distribution and version:**
```bash
# Identify distribution
java -XshowSettings:all 2>&1 | grep "java.vendor"
# e.g.: java.vendor = Eclipse Adoptium

# Check Java version
java -version
# e.g.: openjdk version "21.0.3" 2024-04-16 LTS

# Check what modules are available
java --list-modules | wc -l
# Typically 70+ modules for full JDK

# Verify TCK info (GraalVM example)
java -XshowSettings:all 2>&1 | grep "java.vm.name"
# e.g.: java.vm.name = Oracle GraalVM 21+35.1
```

**Installing and switching with SDKMAN:**
```bash
# Install SDKMAN
curl -s "https://get.sdkman.io" | bash

# List available JDK distributions
sdk list java

# Install Temurin 21
sdk install java 21.0.3-tem

# Install GraalVM CE 21
sdk install java 21.0.3-graalce

# Switch between versions
sdk use java 21.0.3-tem
sdk use java 21.0.3-graalce
```

**How to test / verify correctness:**
```bash
# Verify the JVM you are running
java -XshowSettings:all -version 2>&1

# Verify bytecode compatibility
javap -verbose MyClass.class | grep "major version"
# major version 65 = Java 21; 61 = Java 17

# Check GraalVM Native Image compilation
native-image --version
native-image -jar app.jar  # if using GraalVM
```

---

### ⚖️ Comparison Table

| Distribution | Vendor | License | LTS Support | Special Features |
|---|---|---|---|---|
| Eclipse Temurin | Adoptium (Eclipse) | Free (GPLv2) | 8-10 years | Community-standard, widest platform support |
| Amazon Corretto | Amazon | Free (GPLv2) | 8+ years | AWS-optimised patches, Lambda-tuned |
| Azul Zulu | Azul | Free + paid | 8+ years | Zulu Prime: C4 GC, sub-ms pauses |
| GraalVM CE | Oracle | Free (GPLv2) | Per release | Native Image, Truffle polyglot, Graal JIT |
| Microsoft Build | Microsoft | Free (GPLv2) | 8+ years | Azure-optimised, Windows ARM64 support |
| Oracle JDK | Oracle | Free (NFTC) | Per release | Includes GraalVM tech, official Oracle support |

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| "Oracle JDK is better than OpenJDK" | Since Java 11, Oracle JDK and OpenJDK are functionally equivalent. Oracle JDK adds support contract and some commercial features (Flight Recorder was open-sourced in Java 11). |
| "GraalVM is a different JVM" | GraalVM is OpenJDK with additional components. For most JVM workloads, GraalVM behaves identically to Temurin. It adds the Native Image tool and Truffle framework on top. |
| "Kotlin requires a Kotlin runtime" | Kotlin compiles to standard JVM bytecode. The only Kotlin-specific runtime dependency is `kotlin-stdlib.jar` - a regular `.jar` with utility classes, not a separate JVM. |
| "All JVM languages are slow to compile" | Kotlin compilation is comparable to Java. Scala compilation is slower by design (complex type system). Clojure compiles to bytecode at runtime (REPL-first). |
| "Upgrading JVM version is risky" | Major JVM versions maintain strong backward compatibility. Upgrading from Java 17 to 21 rarely breaks applications. The JDK migration guide documents all incompatibilities. |

---

### 🚨 Failure Modes & Diagnosis

**Failure Mode 1: Mixed JDK distributions in fleet**
**Symptom:** GC logs show different pause patterns on seemingly identical pods; monitoring dashboards have inconsistent JVM metrics
**Root Cause:** Pods running different JDK distributions with different GC defaults
**Diagnostic:**
```bash
# Check all pods in fleet
kubectl get pods -o jsonpath='{range .items[*]}{.metadata.name}{"\t"}{.spec.containers[*].image}{"\n"}{end}'
# Look for multiple java base images
jcmd <pid> VM.version  # on each pod
```
**Fix:** Standardise all services to one base Docker image with pinned JDK version
**Prevention:** Enforce base image in CI; use `FROM eclipse-temurin:21-jre-jammy` as the only allowed base

**Failure Mode 2: GraalVM Native Image reflection failure**
**Symptom:** Application works with standard JVM but `native-image` build fails or produces binary that crashes at runtime
**Root Cause:** GraalVM Native Image requires all reflection, JNI, and dynamic class loading to be declared at build time (closed-world assumption)
**Diagnostic:**
```bash
native-image --no-fallback -jar app.jar 2>&1 | \
  grep "ReflectionConfigurationFiles"
# Or run with:
native-image -jar app.jar -H:+ReportExceptionStackTraces
```
**Fix:** Generate reflection configuration using the tracing agent:
```bash
java -agentlib:native-image-agent=config-output-dir=native-config \
     -jar app.jar
# Then: native-image --no-fallback \
#   -H:ReflectionConfigurationFiles=native-config/reflect-config.json \
#   -jar app.jar
```
**Prevention:** Use GraalVM-compatible frameworks (Micronaut, Quarkus) that generate native config at build time

**Failure Mode 3: License violation with Oracle JDK**
**Symptom:** Legal team flags Oracle JDK use in production after Oracle changed NFTC terms
**Root Cause:** Confusion between Oracle JDK license history; Oracle JDK was paid in Java 11-16 timeframe
**Diagnostic:** Check `java -version` output for "Oracle" vs "OpenJDK" in the vendor string
**Fix:** Migrate to Temurin or Corretto - drop-in replacements
**Prevention:** Use Temurin or Corretto as default; document JDK distribution choice in architecture decisions

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**
- [[JVM-001 - What Is the JVM - A Mental Model]]
- [[JVM-002 - Why the JVM Was Invented]]
- [[JVM-003 - JVM vs JRE vs JDK]]

**Builds On This (learn these next):**
- [[JVM-052 - GraalVM]] - GraalVM deep dive
- [[JVM-053 - Native Image]] - Native compilation path
- [[JVM-051 - AOT Compilation]] - Ahead-of-time compilation concepts

**Alternatives / Comparisons:**
- CLR (.NET runtime) ecosystem - Microsoft's equivalent multi-language managed runtime

---

### 📌 Quick Reference Card

```
+--------------------------------------------------+
| WHAT IT IS    | Map of JVM distributions,        |
|               | languages, and extended VMs       |
+--------------------------------------------------+
| PROBLEM       | Distribution confusion;           |
|               | wrong runtime for the job         |
+--------------------------------------------------+
| KEY INSIGHT   | All distributions share one       |
|               | bytecode standard; pick by        |
|               | support needs, not compatibility  |
+--------------------------------------------------+
| USE WHEN      | Choosing a JDK; onboarding to     |
|               | a polyglot JVM project            |
+--------------------------------------------------+
| AVOID WHEN    | (Survey entry - always relevant)  |
+--------------------------------------------------+
| TRADE-OFF     | Ecosystem diversity vs            |
|               | standardisation overhead          |
+--------------------------------------------------+
| ONE-LINER     | Temurin for apps; GraalVM for     |
|               | native or polyglot; Corretto AWS  |
+--------------------------------------------------+
| NEXT EXPLORE  | JVM-052 GraalVM,                 |
|               | JVM-053 Native Image              |
+--------------------------------------------------+
```

**If you remember only 3 things:**
1. All major distributions build from OpenJDK - they are TCK-compatible
2. GraalVM = OpenJDK + Graal JIT + Native Image + Truffle polyglot
3. Temurin (Eclipse Adoptium) is the community-default free LTS JDK

**Interview one-liner:** "The JVM ecosystem has one bytecode standard with many distributions (Temurin, Corretto, Zulu, GraalVM) and languages (Kotlin, Scala, Clojure) all running on any conforming JVM."

---

### 💎 Transferable Wisdom

**Reusable Engineering Principle:** An open specification with multiple implementations creates a healthy ecosystem of competing vendors, but requires explicit fleet standardisation policy to avoid operational fragmentation.

**Where else this pattern appears:**
- Linux distributions: one kernel, many distros (Ubuntu, RHEL, Alpine) - standardise on one per environment
- Kubernetes: one API specification, multiple distributions (k3s, EKS, GKE, AKS) - standardise for operator familiarity
- SQL: one ANSI standard, many databases (Postgres, MySQL, Oracle) - choose by feature, not compatibility

---

### 💡 The Surprising Truth

Kotlin, Scala, and Clojure were not designed as Java replacements - they were designed as JVM languages. Their authors specifically chose to compile to JVM bytecode rather than building new runtimes, because the JVM's GC, JIT, monitoring ecosystem, and multi-decade library ecosystem were worth more than any performance difference from a custom runtime. This decision means a Kotlin coroutine and a Java thread can share the same heap, the same JFR profiler, and the same GC tuning. Languages built on the JVM inherit 30 years of JVM performance research without writing a single line of garbage collector code. The JVM became the industry's most battle-tested runtime layer not by designing for it, but because the open specification made it the obvious foundation for any new language targeting the server.

---

### 🧠 Think About This Before We Continue

**Q1 (System Interaction):** Your monolith contains Java, Kotlin, and Scala code. All three compile to bytecode and run in the same JVM process. A Kotlin coroutine dispatches to a Scala Future which calls a Java CompletableFuture. They all share one JVM thread pool. What single JVM subsystem is responsible for all three, and what happens when one blocks the shared pool?
*Hint:* Look at [[JVM-008 - How Java Code Runs]] and the thread management sections; then explore virtual threads in Java 21 as a potential solution to the blocking concern.

**Q2 (Scale):** You have 200 microservices standardised on Temurin 21 LTS. A critical JVM security patch is released. How does your patch propagation work, and what is the exact rebuild/redeploy sequence required for all 200 services?
*Hint:* Consider Docker image layering and base image pinning. When the base image `eclipse-temurin:21-jre` is updated, what is the minimum CI/CD change required per service?

**Q3 (Design Trade-off):** GraalVM Native Image produces a self-contained binary with no JVM dependency on the target machine. A traditional JVM application depends on the JVM being installed. From a security patching perspective, which model is harder to maintain at scale and why?
*Hint:* When a JVM vulnerability is patched, consider how the patch reaches running applications in each model (shared JVM binary vs statically-linked native binary per service).
