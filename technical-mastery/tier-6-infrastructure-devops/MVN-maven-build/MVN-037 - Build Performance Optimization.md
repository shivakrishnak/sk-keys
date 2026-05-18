---
version: 1
layout: default
title: "Build Performance Optimization"
parent: "Maven & Build Tools"
grand_parent: "Technical Mastery"
nav_order: 37
permalink: /technical-mastery/maven-build/build-performance-optimization/
id: MVN-039
category: Maven & Build Tools (Java)
difficulty: ★★★
depends_on: Gradle Incremental Build, Gradle Build Cache, Maven Multi-Module Project, Maven Wrapper (mvnw)
used_by: []
related: Gradle Incremental Build, Gradle Build Cache, Maven Multi-Module Project
tags:
  - maven
  - gradle
  - build-tools
  - performance
  - optimization
  - java
  - deep-dive
---

⚡ TL;DR - Build performance optimisation reduces the time between a code change and a verified build through four levers: parallel execution, incremental builds, caching (local and remote), and hermetic toolchain pinning - applied across both Maven and Gradle, and across local development and CI environments.

| #1095           | Category: Maven & Build Tools (Java)                                                           | Difficulty: ★★★ |
| :-------------- | :--------------------------------------------------------------------------------------------- | :-------------- |
| **Depends on:** | Gradle Incremental Build, Gradle Build Cache, Maven Multi-Module Project, Maven Wrapper (mvnw) |                 |
| **Related:**    | Gradle Incremental Build, Gradle Build Cache, Maven Multi-Module Project                       |                 |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
A 50-module Java monorepo. Developer changes one file. Full build: 20 minutes. CI build: 30 minutes (cold container). 50 developers × 20 builds per day × 20 minutes = 333 developer-hours lost daily to waiting for builds. Teams stop writing tests because the feedback loop is too slow. Code quality degrades.

**THE BREAKING POINT:**
Build time is a developer experience multiplier. A 10-second feedback loop enables fearless refactoring; a 20-minute loop forces cognitive batching and discourages iteration. Google's Blaze (open-sourced as Bazel), the Facebook Buck, and Gradle's build cache all emerged from the recognition that build speed is an engineering productivity problem at scale.

**THE INVENTION MOMENT:**
No single technique transforms build performance - it requires applying a cascade of optimisations: parallel module builds, incremental compilation (recompile only changed files), output caching (skip tasks whose outputs are stored), and reducing configuration overhead.

---

### 📘 Textbook Definition

**Build performance optimisation** is the systematic application of techniques to reduce build execution time and resource consumption. Key techniques include: (1) **parallel execution** - running independent tasks or modules simultaneously; (2) **incremental compilation** - recompiling only source files whose dependencies changed; (3) **build caching** - storing and retrieving task outputs by input fingerprint; (4) **toolchain pinning** - eliminating JDK/tool download overhead; (5) **configuration optimisation** - reducing the Gradle configuration phase cost; (6) **CI cache strategies** - persisting `.gradle/`, `.m2/`, and build outputs across pipeline runs. The techniques are complementary and compound: each reduces a different component of total build time.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
Don't redo what hasn't changed; do what can be done in parallel; reuse what others have already built.

**One analogy:**

> Assembling IKEA furniture. Slow approach: one person, sequential steps, rebuilding a step if a screw was dropped. Fast approach: two people working on independent sections in parallel, reusing subassemblies that are already complete, sharing a finished section that a neighbour assembled identically. Same result, fraction of the time.

**One insight:**
The biggest wins are usually ordering-dependent: (1) enable parallelism first (biggest impact on large multi-module builds); (2) then incremental builds (biggest impact on iterative development); (3) then remote build cache (biggest impact on CI cold builds). Start with the highest-impact technique for your specific bottleneck.

---

### 🔩 First Principles Explanation

**THE FOUR LEVERS:**

**LEVER 1: PARALLEL EXECUTION**

```
Sequential (default Maven):
module-A [===20s===] → module-B [===20s===] → module-C
  [===20s===]  = 60s

Parallel (Maven -T 3 / Gradle --parallel):
module-A [===20s===]
module-B [===20s===]  (all run simultaneously if no
  dependency between them)
module-C [===20s===]
                                                           
```

**LEVER 2: INCREMENTAL BUILD**

```
Before incremental: 50 source files changed → compile 500
  files (all)
After incremental:  50 source files changed → compile 50 +
  affected = 60–80 files
Benefit: proportional to percentage unchanged
```

**LEVER 3: BUILD CACHE**

```
CI Build 1: compileJava → 30s → store output in cache
  (key: SHA of inputs)
CI Build 2 (same inputs):  → lookup cache → restore output
  = 0.5s
Developer (same inputs): → lookup remote cache → restore
  = 1–2s download
```

**LEVER 4: CONFIGURATION / TOOLCHAIN**

```
Gradle configuration cache: skip recomputing task graph =
  -5s per build
JDK toolchain: auto-provision correct JDK = consistent
  builds, no JAVA_HOME issues
Wrapper: no Maven/Gradle download on CI = -30s first run
```

**MAVEN-SPECIFIC OPTIMISATIONS:**

```bash
# Parallel module builds (N threads, or C = CPU cores)
mvn clean install -T 4    # 4 threads
mvn clean install -T 2C   # 2 × CPU core count

# Skip javadoc (slow) except on release
mvn install -Dmaven.javadoc.skip=true

# Skip tests (use carefully)
mvn install -DskipTests  # skip test execution (still compiles)
mvn install -Dmaven.test.skip=true  # skip compile AND execution

# Offline mode: no network calls
mvn install -o  # all deps must be in local .m2

# Build only changed modules (with Git)
mvn install -pl $(git diff --name-only HEAD~1 | grep pom.xml | sed 's|/pom.xml||') -am

# Multi-threaded surefire (parallel test execution within module)
<configuration>
  <parallel>methods</parallel>
  <threadCount>4</threadCount>
</configuration>
```

**GRADLE-SPECIFIC OPTIMISATIONS:**

```bash
# Parallel project execution
./gradlew build --parallel

# Build cache (local + remote)
./gradlew build --build-cache

# Configuration cache (reuse task graph)
./gradlew build --configuration-cache

# Worker daemon (JVM reuse between builds)
org.gradle.daemon=true  # in gradle.properties

# JVM memory for build daemon
org.gradle.jvmargs=-Xmx4g -XX:MaxMetaspaceSize=512m
```

**THE TRADE-OFFS:**

**Parallel execution cost:** Thread-safety of Maven plugins; module-level test result isolation; increased memory usage (N parallel JVMs).

**Incremental build cost:** Initial build slightly slower (fingerprinting); incorrect input declarations → stale outputs.

**Build cache cost:** Infrastructure (remote cache server); cache key correctness; non-deterministic tasks produce cache misses.

**Configuration cache cost:** Not all plugins support it (compatibility list); first run slightly slower (cache population).

---

### 🧪 Thought Experiment

**SETUP:**
A large Spring Boot microservices monorepo has 20 modules. Full CI build: 45 minutes. Most developers change only 1–3 modules per PR.

**OPTIMISATION SEQUENCE:**

1. Enable `--parallel` in Gradle → independent modules build simultaneously → 20 min (-55%)
2. Enable `--build-cache` with remote cache → most modules get FROM-CACHE → 5 min (-75%)
3. Enable `--configuration-cache` → task graph reuse → 3 min (-33%)
4. Split large test suites: unit tests fast path, integration tests separate job → 1.5 min for PR gate

**TOTAL REDUCTION:** 45 min → 1.5 min for the fast PR gate. Integration test job: 8 min (runs in parallel).

**THE LESSON:**
Build performance is a compound problem. No single fix gives 97% reduction. The techniques compose: each tackles a different bottleneck. Profile first (`--scan`, `--info`) to identify where time is actually spent before optimising.

---

### 🧠 Mental Model / Analogy

> Build optimisation is like optimising a restaurant kitchen. (1) Parallel execution = multiple chefs working simultaneously on different dishes. (2) Incremental build = only recook dishes that changed (not the entire menu every service). (3) Build cache = dishes prepared in advance and stored; retrieved instead of cooked from scratch. (4) Configuration = the kitchen setup time before service starts - minimise it. All four reduce total service time; each addresses a different bottleneck.

---

### 📶 Gradual Depth - Four Levels

**Level 1:** Build slow? First try: enable parallel builds (`-T 2C` for Maven, `--parallel` for Gradle) and skip tests when not needed (`-DskipTests`).

**Level 2:** Enable Gradle's incremental build and build cache. In Maven, use `mvn -pl module -am` to build only what changed. Cache your `.m2/` and `.gradle/` directories between CI runs.

**Level 3:** Profile the build: `./gradlew build --scan` (Gradle) generates a detailed build analysis online. In Maven, use `-Dverbose` and `mvn help:effective-pom` to find slow plugins. Identify the top 3 slowest tasks and target them specifically.

**Level 4:** Hermeticity: build in isolated containers with pinned JDK (toolchain), pinned build tool (wrapper), pinned all dependencies (no SNAPSHOTs). Combine with Bazel or Gradle for remote build execution (distribute build tasks across a build farm). Measure `P95` build time (95th percentile), not average - tail latency determines developer experience.

---

### ⚙️ How It Works (Mechanism)

```bash
# MAVEN PERFORMANCE FLAGS REFERENCE:
mvn install \
  -T 2C \                    # 2x CPU cores parallel
  -DskipTests \              # skip test execution
  -Dmaven.javadoc.skip=true\ # skip slow javadoc generation
  -o \                       # offline (no network, all deps cached)
  -pl :changed-module -am    # only changed module + its deps

# GRADLE PERFORMANCE FLAGS:
./gradlew build \
  --parallel \               # parallel project execution
  --build-cache \            # enable build cache
  --configuration-cache \    # reuse task graph
  --no-daemon \
  # CI: disable daemon (containers exit after build)
  -x test                    # exclude test task

# GRADLE gradle.properties (persistent optimisations):
org.gradle.daemon=true
org.gradle.parallel=true
org.gradle.caching=true
org.gradle.jvmargs=-Xmx4g -XX:+HeapDumpOnOutOfMemoryError
org.gradle.configuration-cache=true

# CI CACHE: preserve these directories between runs
# GitHub Actions:
- uses: actions/cache@v4
  with:
    path: |
      ~/.gradle/caches
      ~/.gradle/wrapper
      ~/.m2/repository
    key: ${{ runner.os }}-gradle-${{ hashFiles('**/*.gradle.kts') }}
```

---

### 💻 Code Example

**`gradle.properties` for a high-performance Gradle build:**

```properties
# Core performance settings
org.gradle.daemon=true
org.gradle.parallel=true
org.gradle.caching=true
org.gradle.configuration-cache=true
org.gradle.configuration-cache.problems=warn
# warn instead of fail during migration

# JVM tuning: build daemon heap
org.gradle.jvmargs=-Xmx4g -Xms512m -XX:+HeapDumpOnOutOfMemoryError -XX:HeapDumpPath=/tmp/gradle-heap-dump

# Worker daemon JVM args (task execution)
org.gradle.workers.max=4
```

**GitHub Actions optimised workflow:**

```yaml
name: Build
on: [push, pull_request]
jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - uses: actions/setup-java@v4
        with:
          java-version: "17"
          distribution: "temurin"

      - name: Cache Gradle
        uses: actions/cache@v4
        with:
          path: |
            ~/.gradle/caches
            ~/.gradle/wrapper
          key: gradle-${{ hashFiles('**/*.gradle.kts',
              '**/gradle-wrapper.properties') }}
          restore-keys: gradle-

      - name: Build and test
        run: ./gradlew build --build-cache --configuration-cache --parallel
        env:
          GRADLE_BUILD_ACTION_CACHE_DEBUG_ENABLED: true
```

---

### ⚖️ Comparison Table

| Technique               | Maven              | Gradle                   | Impact Area                      |
| ----------------------- | ------------------ | ------------------------ | -------------------------------- |
| Parallel module builds  | `-T 4` / `-T 2C`   | `--parallel`             | Multi-module CI builds           |
| Skip tests              | `-DskipTests`      | `-x test`                | Fast iteration / deployment      |
| Incremental compilation | Limited (surefire) | Built-in                 | Single-module dev loop           |
| Local build cache       | No                 | `--build-cache`          | CI cold starts                   |
| Remote build cache      | No                 | Gradle Enterprise        | Team-wide cache sharing          |
| Config cache            | No                 | `--configuration-cache`  | Repeated builds                  |
| Offline mode            | `-o`               | `--offline`              | Air-gapped / network-free builds |
| Partial builds          | `-pl module -am`   | `./gradlew :module:task` | Changed-only rebuilds            |

---

### ⚠️ Common Misconceptions

| Misconception                          | Reality                                                                      |
| -------------------------------------- | ---------------------------------------------------------------------------- |
| `mvn clean install` is always correct  | `clean` destroys incremental state - only use when debugging, not by default |
| Parallel builds are always faster      | Memory-bound builds may be slower with parallelism (GC pressure, OOM)        |
| Build cache requires Gradle Enterprise | Local build cache is free; only remote build cache needs infrastructure      |
| Build time = compilation time          | Test execution, plugin execution, and I/O often dominate over compilation    |

---

### 🚨 Failure Modes & Diagnosis

**Parallel builds produce non-deterministic failures**

**Root Cause:** Modules write to shared output directories; test suites share state (static fields, temp files).

**Fix:** Isolate module outputs; use unique temp file prefixes; enable `fork=true` in surefire.

---

**CI build ignores local build cache from developer**

**Root Cause:** No shared remote build cache configured; CI environment different from dev (different OS, JDK vendor) → different cache keys.

**Fix:** Configure a remote build cache server; pin OS and JDK vendor in toolchain for consistent keys.

---

### 🔗 Related Keywords

**Prerequisites:** `Gradle Incremental Build`, `Gradle Build Cache`, `Maven Multi-Module Project`, `Maven Wrapper (mvnw)`

**Builds On This:** (end of category - culminates all previous Maven & Build Tools concepts)

**Related Patterns:** `Gradle Incremental Build`, `Gradle Build Cache`, `Maven Multi-Module Project`

---

### 📌 Quick Reference Card

```
┌─────────────────────────────────────────────────────────┐
│ LEVER 1      │ Parallel: -T 2C (Maven) / --parallel (G) │
├──────────────┼──────────────────────────────────────────┤
│ LEVER 2      │ Incremental: built-in Gradle; limited MVP│
├──────────────┼──────────────────────────────────────────┤
│ LEVER 3      │ Cache: --build-cache (Gradle); cache .m2 │
├──────────────┼──────────────────────────────────────────┤
│ LEVER 4      │ Config: --configuration-cache (Gradle)   │
├──────────────┼──────────────────────────────────────────┤
│ PROFILE      │ ./gradlew build --scan → build analysis  │
├──────────────┼──────────────────────────────────────────┤
│ ONE-LINER    │ "Skip unchanged, run parallel, cache all"│
└─────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** Your Maven build's slowest step is Surefire test execution taking 15 minutes for 2,000 unit tests. Compilation is already parallel and takes only 2 minutes. What specific Maven (or CI) techniques would you apply to reduce test execution time, and what are the correctness trade-offs of each?

**Q2.** You've enabled Gradle's remote build cache on your CI server. After 2 weeks, you measure that the cache hit rate for `compileJava` is only 12% (88% misses). What are the three most likely causes of low cache hit rates for the `compileJava` task, and how would you diagnose which cause is responsible?
