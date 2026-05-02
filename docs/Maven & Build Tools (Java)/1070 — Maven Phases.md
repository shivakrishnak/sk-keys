---
layout: default
title: "Maven Phases"
parent: "Maven & Build Tools (Java)"
nav_order: 1070
permalink: /maven-build/maven-phases/
number: "1070"
category: Maven & Build Tools (Java)
difficulty: ★★☆
depends_on: "Maven Lifecycle, Maven Goals"
used_by: "Maven Plugins, pom.xml, CI-CD pipelines"
tags: #maven, #phases, #lifecycle, #build-stages, #ordered-execution
---

# 1070 — Maven Phases

`#maven` `#phases` `#lifecycle` `#build-stages` `#ordered-execution`

⚡ TL;DR — **Maven phases** are the individual ordered steps within a lifecycle. The default lifecycle has 23 phases; the most important: `validate`, `compile`, `test`, `package`, `verify`, `install`, `deploy`. Phases themselves do nothing — they're hooks where plugin goals are bound. Running a phase executes all goals bound to all preceding phases in order. Phases answer the question "WHEN in the build sequence should this happen?"

| #1070           | Category: Maven & Build Tools (Java)    | Difficulty: ★★☆ |
| :-------------- | :-------------------------------------- | :-------------- |
| **Depends on:** | Maven Lifecycle, Maven Goals            |                 |
| **Used by:**    | Maven Plugins, pom.xml, CI-CD pipelines |                 |

---

### 📘 Textbook Definition

**Maven phase**: a named step in a Maven build lifecycle, representing a stage in the project's build process. Phases are ordered and sequential within a lifecycle — invoking any phase automatically invokes all preceding phases. Phases have no inherent behavior: they function as ordered slots to which plugin goals bind. Built-in bindings are provided for standard packaging types (`jar`, `war`, `pom`); additional bindings can be declared in the POM. The default lifecycle's 23 phases, in order: `validate`, `initialize`, `generate-sources`, `process-sources`, `generate-resources`, `process-resources`, `compile`, `process-classes`, `generate-test-sources`, `process-test-sources`, `generate-test-resources`, `process-test-resources`, `test-compile`, `process-test-classes`, `test`, `prepare-package`, `package`, `pre-integration-test`, `integration-test`, `post-integration-test`, `verify`, `install`, `deploy`. Phases between the "main" phases (e.g., `prepare-package` between `test` and `package`) exist as extension points — plugin authors can bind goals there without disrupting the primary flow. The `clean` lifecycle has 3 phases: `pre-clean`, `clean`, `post-clean`. The `site` lifecycle has 4: `pre-site`, `site`, `post-site`, `site-deploy`.

---

### 🟢 Simple Definition (Easy)

Think of phases as a numbered checklist: 1-validate, 2-compile, 7-test, 10-package, etc. When you say "run step 10 (package)," Maven automatically runs steps 1 through 10 in order. You can't package without compiling first. You can't compile without validating first. Phases ensure the right things happen in the right order, every time.

---

### 🔵 Simple Definition (Elaborated)

Phases vs goals: phases are the "when" (ordered position in the build), goals are the "what" (the actual task). A phase is meaningless without goals bound to it. The `process-classes` phase (phase 8) exists but has no default goals bound — it's available for plugins that need to manipulate bytecode after compilation (e.g., AspectJ weaving, JPA entity enhancement). The phase exists to reserve a position in the build order; plugins use it when needed.

The `pre-integration-test` / `integration-test` / `post-integration-test` trio is designed for: start test infrastructure (DB, server) → run integration tests → shut down infrastructure. The failsafe plugin runs tests in `integration-test` and ALWAYS runs the post-integration-test phase (to shut down) even if tests fail, then reports failure in `verify`. This prevents leaked resources (running containers/servers) even when tests fail.

---

### 🔩 First Principles Explanation

```
DEFAULT LIFECYCLE: 23 PHASES WITH PURPOSE

  Phase                    Purpose / What binds here
  ──────────────────────────────────────────────────────────────────────
  1.  validate             Check POM is valid; all info available
      ↓
  2.  initialize           Set properties; create directories
      ↓
  3.  generate-sources     Generate source code (JAXB, Thrift, Protobuf,
                           annotation processing initial pass)
      ↓
  4.  process-sources      Filter/process source files
      ↓
  5.  generate-resources   Generate resource files
      ↓
  6.  process-resources ★  Copy + filter src/main/resources → target/classes
                           (maven-resources-plugin:resources)
      ↓
  7.  compile ★            Compile src/main/java → target/classes
                           (maven-compiler-plugin:compile)
      ↓
  8.  process-classes      Post-process .class files (AspectJ, JPA enhancement,
                           bytecode instrumentation)
      ↓
  9.  generate-test-sources Generate test source code
      ↓
  10. process-test-sources  Filter/process test source files
      ↓
  11. generate-test-resources Generate test resources
      ↓
  12. process-test-resources Copy src/test/resources → target/test-classes
                             (maven-resources-plugin:testResources)
      ↓
  13. test-compile ★        Compile src/test/java → target/test-classes
                            (maven-compiler-plugin:testCompile)
      ↓
  14. process-test-classes  Post-process test .class files
      ↓
  15. test ★               Run unit tests; fail immediately on failure
                           (maven-surefire-plugin:test)
      ↓
  16. prepare-package       Pre-packaging steps (e.g., shade plugin preparation)
      ↓
  17. package ★            Create distributable format (JAR/WAR/EAR)
                           (maven-jar-plugin:jar)
                           (spring-boot-maven-plugin:repackage runs here too)
      ↓
  18. pre-integration-test  Start test infrastructure (DBs, app servers,
                            Testcontainers, WireMock)
      ↓
  19. integration-test ★    Run integration tests
                            (maven-failsafe-plugin:integration-test)
      ↓
  20. post-integration-test Shut down test infrastructure (ALWAYS runs,
                            even if integration tests fail)
      ↓
  21. verify ★             Check quality gates: coverage thresholds,
                           code style, security scans, integration test results
                           (failsafe:verify, jacoco:check, checkstyle:check)
      ↓
  22. install ★            Install to ~/.m2/repository
                           (maven-install-plugin:install)
      ↓
  23. deploy ★             Upload to remote repo (Nexus/Artifactory)
                           (maven-deploy-plugin:deploy)

  ★ = phases where meaningful work happens by default

PHASES WITH NO DEFAULT BINDINGS (extension points):

  initialize        → set custom properties
  generate-sources  → code generators (JAXB, OpenAPI, Protobuf)
  process-classes   → bytecode weaving (AspectJ)
  prepare-package   → pre-packaging manipulation
  pre-integration-test → start infrastructure
  post-integration-test → stop infrastructure

  These exist because plugin authors needed a standard slot BEFORE or AFTER
  the main phases without disrupting the build order.

PRACTICAL PHASE SELECTION:

  LOCAL DEVELOPMENT:
  mvn compile          ← just check it compiles (fastest)
  mvn test             ← compile + unit tests
  mvn package          ← compile + test + JAR (most common local build)

  CI PIPELINE:
  mvn clean verify     ← full: unit tests + integration tests + quality gates
  mvn clean package -DskipTests ← fast build without tests (emergency)

  PUBLISHING:
  mvn clean deploy     ← full build + upload to artifact repo

  BETWEEN BUILDS:
  mvn clean            ← delete target/ (no lifecycle phase skipping occurs)

  CUSTOM PHASE IN pom.xml:
  <!-- Bind Checkstyle to validate phase (fail early on style violations): -->
  <execution>
    <phase>validate</phase>
    <goals><goal>check</goal></goals>
  </execution>
  <!-- vs binding to verify (after tests, before install): -->
  <execution>
    <phase>verify</phase>
    <goals><goal>check</goal></goals>
  </execution>
  <!-- Trade-off: validate = fast fail but before compile;
                  verify = full picture but runs longer -->
```

---

### ❓ Why Does This Exist (Why Before What)

The 23-phase design accommodates the full diversity of Java project needs: simple JARs need only a handful of phases; complex projects with code generation, bytecode weaving, multiple test types, and deployment need all of them. The phases between the "main" phases are extension points — they let plugin authors insert behavior in the right place without disrupting the sequence. Without this fine granularity, plugin ordering would be non-deterministic or require complex configuration to specify "run after compile but before test."

---

### 🧠 Mental Model / Analogy

> **Phases are like railway stations on a fixed route**: the train (build) always stops at each station in order. Passengers (plugin goals) board at specific stations. The `compile` station has the "compiler" passenger who does their job (compiles code) and stays on. The `test` station has the "tester" passenger. At `package`, the "packager" creates the JAR. You can board the train at any station (invoke any phase), and the train will stop at every station before it in sequence. Some stations are empty (no passengers = no plugin bound) — the train still stops there briefly (the phase is visited) but nothing happens.

---

### 🔄 How It Connects (Mini-Map)

```
Lifecycle defines the order; phases are the individual steps
        │
        ▼
Maven Phases ◄── (you are here)
(ordered slots; goals bind here; running a phase runs all prior phases)
        │
        ├── Maven Lifecycle: the lifecycle contains the ordered phases
        ├── Maven Goals: goals bind to phases to do actual work
        ├── Maven Plugins: provide goals that bind to phases
        └── pom.xml: <execution><phase> configures additional bindings
```

---

### 💻 Code Example

```xml
<!-- Using phases strategically in a CI-optimized pom.xml -->
<build>
  <plugins>
    <!-- Checkstyle: bind to validate for fast fail on style violations -->
    <plugin>
      <groupId>org.apache.maven.plugins</groupId>
      <artifactId>maven-checkstyle-plugin</artifactId>
      <version>3.3.0</version>
      <executions>
        <execution>
          <id>validate-style</id>
          <phase>validate</phase>
          <goals><goal>check</goal></goals>
        </execution>
      </executions>
    </plugin>

    <!-- Failsafe: run integration tests in integration-test phase -->
    <!-- Stops infrastructure in post-integration-test EVEN IF tests fail -->
    <plugin>
      <groupId>org.apache.maven.plugins</groupId>
      <artifactId>maven-failsafe-plugin</artifactId>
      <executions>
        <execution>
          <goals>
            <goal>integration-test</goal>   <!-- phase: integration-test -->
            <goal>verify</goal>             <!-- phase: verify (report failures) -->
          </goals>
        </execution>
      </executions>
    </plugin>

    <!-- Spring Boot: bind start/stop to pre/post-integration-test phases -->
    <plugin>
      <groupId>org.springframework.boot</groupId>
      <artifactId>spring-boot-maven-plugin</artifactId>
      <executions>
        <execution>
          <id>pre-integration-test</id>
          <goals><goal>start</goal></goals>    <!-- start app server -->
        </execution>
        <execution>
          <id>post-integration-test</id>
          <goals><goal>stop</goal></goals>     <!-- stop app server -->
        </execution>
      </executions>
    </plugin>
  </plugins>
</build>
```

---

### ⚠️ Common Misconceptions

| Misconception                                               | Reality                                                                                                                                                                                                                                                                                                                                         |
| ----------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Phases are the same as goals                                | Phases are ordering slots in a lifecycle; goals are the tasks that do work. A phase can have zero, one, or multiple goals bound to it. The same goal can be bound to different phases in different executions.                                                                                                                                  |
| You can invoke multiple phases independently in one command | `mvn compile test` does NOT run compile then test independently. Maven processes them as: run lifecycle up to `compile`, then run lifecycle up to `test`. Since `test` includes `compile`, the result is just running up to `test`. `mvn compile test` = `mvn test`. To run specific goals independently: `mvn compiler:compile surefire:test`. |
| The 23 phases all run for every project                     | Only phases with bound goals "do" anything. Most projects only see meaningful work in ~8 phases. The others are visited (phase is evaluated) but pass through instantly because no goals are bound.                                                                                                                                             |

---

### 🔗 Related Keywords

- `Maven Lifecycle` — the three lifecycles (default, clean, site) containing phases
- `Maven Goals` — the tasks that bind to phases and do actual work
- `Maven Plugins` — provide the goals that bind to phases
- `pom.xml` — configures additional goal-to-phase bindings via `<execution>`
- `Maven Lifecycle` — running a phase invokes all preceding phases

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ KEY PHASES (default lifecycle):                         │
│ validate → compile → test → package                     │
│         → verify → install → deploy                     │
│                                                         │
│ FOR CI: mvn clean verify (unit + integration + quality) │
│ FOR DEV: mvn clean package (compile + unit tests + jar) │
│ FOR PUBLISH: mvn clean deploy                           │
│                                                         │
│ EXTENSION POINTS (empty by default, plugins hook here): │
│ generate-sources | process-classes | prepare-package    │
│ pre-integration-test | post-integration-test            │
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** The `process-classes` phase (after `compile`) exists for bytecode weaving — tools like AspectJ and Hibernate's JPA bytecode enhancer modify `.class` files in-place after the Java compiler runs. This is how compile-time AOP works (vs load-time weaving with a Java agent). Compare: compile-time weaving (AspectJ plugin binding to `process-classes`) vs load-time weaving (JVM agent via `-javaagent:aspectjweaver.jar`). What are the build-time vs runtime trade-offs? What debugging challenges arise with each?

**Q2.** Large Maven multi-module projects can have slow builds because Maven processes modules sequentially by default. `mvn -T 4 clean package` enables 4-thread parallel builds for independent modules. However, Maven's sequential lifecycle phases within a single module cannot be parallelized (compile must complete before test). Gradle's task graph (vs Maven's linear phase model) enables more fine-grained parallelism. What are the specific scenarios where Maven's lifecycle model is a build performance bottleneck, and how do tools like Gradle's build cache and configuration cache specifically address these?
