---
version: 2
layout: default
title: "Maven Phases"
parent: "Maven & Build Tools"
grand_parent: "Technical Dictionary"
nav_order: 10
permalink: /maven-build/maven-phases/
id: MVN-010
category: Maven & Build Tools (Java)
difficulty: ★★☆
depends_on: Maven Overview, pom.xml, Maven Lifecycle (validate, compile, test, package, install, deploy), Maven Goals
used_by: Maven Plugins, Build Performance Optimization, Maven Profiles
related: Maven Goals, Maven Lifecycle (validate, compile, test, package, install, deploy), Maven Plugins
tags:
  - maven
  - build-tools
  - java
  - intermediate
  - build
---

# MVN-010 - Maven Phases

⚡ TL;DR - A Maven phase is a named step in the build lifecycle (like `compile`, `test`, `package`); phases define the sequence, while goals do the actual work - understanding which is which is key to controlling Maven builds.

| #1070           | Category: Maven & Build Tools (Java)                          | Difficulty: ★★☆ |
| :-------------- | :------------------------------------------------------------ | :-------------- |
| **Depends on:** | Maven Overview, pom.xml, Maven Lifecycle, Maven Goals         |                 |
| **Used by:**    | Maven Plugins, Build Performance Optimization, Maven Profiles |                 |
| **Related:**    | Maven Goals, Maven Lifecycle, Maven Plugins                   |                 |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
Goals provide execution units; lifecycles provide overall sequencing. But without named phases as extension points, you'd have no way to insert custom steps into the build at the right moment. "Run my code generator before compilation" - where exactly? "Spin up a database before integration tests" - when? Without named phases, there's no standardised answer.

**THE BREAKING POINT:**
Build tool users need to plug in at precise points in the build sequence - before compilation, after testing, before deployment. Without named extension points, every plugin would need to hardcode its position, creating fragile ordering dependencies and making it impossible to reason about what runs when.

**THE INVENTION MOMENT:**
Maven phases are named anchors in the lifecycle sequence. They serve as universal extension points: any plugin can bind its goal to `generate-sources`, `pre-integration-test`, or `verify` by name. The name is stable even if the plugin changes. This is why Maven phases exist as a distinct concept: they are the "where" of build extensibility.

---

### 📘 Textbook Definition

A **Maven phase** is a named stage in one of Maven's three built-in build lifecycles (default, clean, site). Phases are ordered checkpoints that collectively form the lifecycle sequence. Individually, phases perform no work; they are defined as ordered named milestones to which plugin goals can be bound. When Maven is asked to execute a phase, it executes all phases that precede it in the same lifecycle, then the target phase itself, triggering any goals bound to each phase in order. The default lifecycle contains 23 phases; the key ones developers interact with are: validate, initialize, generate-sources, process-sources, generate-resources, process-resources, compile, process-classes, generate-test-sources, process-test-sources, generate-test-resources, process-test-resources, test-compile, process-test-classes, test, prepare-package, package, pre-integration-test, integration-test, post-integration-test, verify, install, deploy.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
A phase is a checkpoint in the build sequence - the "when," not the "what."

**One analogy:**

> Maven phases are like train stations on a fixed route. The lifecycle is the rail line from "validate" station to "deploy" station. Trains (goals) are assigned to specific stations. When you ask Maven to go to the "package" station, the train stops at every station along the way, picking up and dropping off work (goals) as it goes.

**One insight:**
The named-phase model is what makes Maven extensible without being chaotic. Plugin authors know exactly which phase to bind to: need to run before compilation? → `generate-sources`. Need to run integration tests? → `integration-test`. The vocabulary of phases is shared across the entire Maven ecosystem.

---

### 🔩 First Principles Explanation

**CORE INVARIANTS:**

1. Phases within a lifecycle are totally ordered (phase 1 always before phase 2, always before phase 3...).
2. Phases are execution containers, not executors - they contain zero or more bound goals.
3. Phases exist in three separate lifecycles; running a phase in one does not trigger phases in another.

**ALL DEFAULT LIFECYCLE PHASES IN ORDER:**

```
 1. validate
 2. initialize
 3. generate-sources     ← bind code generators here
 4. process-sources
 5. generate-resources
 6. process-resources
 7. compile              ← javac runs here (default binding)
 8. process-classes
 9. generate-test-sources
10. process-test-sources
11. generate-test-resources
12. process-test-resources
13. test-compile
14. process-test-classes
15. test                 ← surefire runs here (default binding)
16. prepare-package
17. package              ← jar/war plugin runs here
18. pre-integration-test ← start test containers here
19. integration-test     ← failsafe runs here
20. post-integration-test← stop test containers here
21. verify               ← enforce quality gates
22. install              ← copy to local .m2
23. deploy               ← push to remote repository
```

**PRACTICAL PHASE SELECTION:**

Most developers only use 6-8 phases in practice. The others exist as extension points for advanced scenarios (code generation, integration testing, coverage enforcement).

**THE TRADE-OFFS:**

**Gain:** Universal vocabulary for build extensibility; any plugin author can express "run before X" or "run after Y" without knowing what other plugins exist.

**Cost:** 23 phases is too many for most projects - most are empty. The phase names are sometimes confusing (`prepare-package` vs `package`). The lifecycle is rigid: you cannot add a new phase between `test` and `package` without changing Maven itself.

---

### 🧪 Thought Experiment

**SETUP:**
You want to: (1) generate Java source files from a Protobuf schema before compilation; (2) start a Docker database before integration tests; (3) stop the Docker database after integration tests.

**WHICH PHASES TO USE:**
Without named phases, you'd have to hack around the lifecycle or use a complex configuration.

**WITH NAMED PHASES:**

```
(1) Bind protobuf-maven-plugin to 'generate-sources'
    → runs before compile, generated sources are on classpath
(2) Bind docker-maven-plugin:start to 'pre-integration-test'
    → database is running before failsafe integration tests
(3) Bind docker-maven-plugin:stop to 'post-integration-test'
    → database stops even if tests fail
```

**THE INSIGHT:**
Named phases are a contract between Maven and the ecosystem: "if you need to run before compilation, bind to `generate-sources`; I guarantee it runs before `compile`." Every plugin respects this contract, and every build is predictable because of it.

---

### 🧠 Mental Model / Analogy

> Maven phases are like chapters in a story that must be told in order. The chapters are named ("The Setup", "The Confrontation", "The Resolution"), and authors (plugin developers) contribute content to specific chapters. You can't read "The Resolution" without reading "The Setup" first - Maven enforces this.

- "Chapter" → lifecycle phase (compile, test, package)
- "Story must be told in order" → phases always execute sequentially
- "Author contributes to a chapter" → plugin goal bound to a phase
- "Can't skip chapters" → Maven always runs all prior phases

**Where this analogy breaks down:** You can skip test execution with `-DskipTests`, but you cannot remove the `test` phase itself from the sequence - it will just have no goals bound to it when skipping is active.

---

### 📶 Gradual Depth - Four Levels

**Level 1 - What it is (anyone can understand):**
A Maven phase is a step in the build process. When you run `mvn package`, Maven runs all steps leading up to "package" - compile, test, etc. - in order. You can't run package without compile running first.

**Level 2 - How to use it (junior developer):**
The phases you'll use most: `compile` (just compile), `test` (compile + test), `package` (compile + test + create JAR), `install` (everything + put JAR in local repo), `deploy` (everything + push to remote). Combine with `clean` for a fresh build: `mvn clean package`.

**Level 3 - How it works (mid-level engineer):**
The 23 phases of the default lifecycle exist so plugins can bind at precise points. Most are empty by default. Key extension phases: `generate-sources` (code generation before compilation), `pre-integration-test` / `post-integration-test` (start/stop external resources), `verify` (enforce quality gates). The clean lifecycle is separate: `clean` deletes `target/`; `pre-clean` and `post-clean` are hooks before and after.

**Level 4 - Why it was designed this way (senior/staff):**
The large number of phases (23 in the default lifecycle) was a deliberate design choice to provide fine-grained extension points without requiring plugins to know about each other. The `pre-integration-test`/`integration-test`/`post-integration-test` triplet was specifically designed to allow setup → test → teardown patterns that are guaranteed to execute in order even on failure (with the right plugin configuration). The limitation: new phases cannot be added without changing Maven core, which is why the lifecycle has remained largely static since Maven 2.

---

### ⚙️ How It Works (Mechanism)

```
┌──────────────────────────────────────────────────────┐
│  Phase execution - how Maven processes each phase    │
├──────────────────────────────────────────────────────┤
│                                                      │
│  Maven walks the lifecycle from phase 1 onwards:    │
│                                                      │
│  For each phase up to and including target phase:   │
│    1. Collect all goals bound to this phase          │
│       (default bindings + pom.xml declarations)      │
│    2. Order goals by POM declaration order           │
│    3. Execute each goal in order                     │
│    4. If any goal fails → STOP, report failure       │
│    5. If all goals succeed → proceed to next phase   │
│                                                      │
│  After target phase reached and completed:           │
│    Build SUCCESS                                     │
│                                                      │
└──────────────────────────────────────────────────────┘
```

**Phase-goal binding in pom.xml:**

```xml
<build>
  <plugins>
    <!-- Start DB before integration tests -->
    <plugin>
      <groupId>io.fabric8</groupId>
      <artifactId>docker-maven-plugin</artifactId>
      <executions>
        <execution>
          <id>start-postgres</id>
          <phase>pre-integration-test</phase>
          <goals><goal>start</goal></goals>
        </execution>
        <execution>
          <id>stop-postgres</id>
          <phase>post-integration-test</phase>
          <goals><goal>stop</goal></goals>
        </execution>
      </executions>
    </plugin>

    <!-- Run integration tests -->
    <plugin>
      <groupId>org.apache.maven.plugins</groupId>
      <artifactId>maven-failsafe-plugin</artifactId>
      <executions>
        <execution>
          <goals>
            <goal>integration-test</goal>  <!-- → integration-test phase -->
            <goal>verify</goal>            <!-- → verify phase -->
          </goals>
        </execution>
      </executions>
    </plugin>
  </plugins>
</build>
```

---

### 🔄 The Complete Picture - End-to-End Flow

**NORMAL FLOW (integration test scenario):**

```
mvn verify
  → validate (POM OK)
  → compile (sources compiled)
  → test (unit tests pass)
  → package (JAR created)
  → pre-integration-test  ← YOU ARE HERE
      → docker:start (PostgreSQL started on port 5432)
  → integration-test
      → failsafe:integration-test (ITs run against live DB)
  → post-integration-test
      → docker:stop (PostgreSQL stopped)
  → verify
      → failsafe:verify (check IT results, fail if any failed)
  → Build SUCCESS
```

**FAILURE PATH:**

```
integration-test phase: IT fails
  → post-integration-test STILL runs (docker:stop runs)
  → verify phase: failsafe:verify detects IT failure
  → BUILD FAILURE reported at verify phase
  → Database is always stopped (no leaked containers)
```

**WHAT CHANGES AT SCALE:**
In CI pipelines, the full lifecycle (`mvn verify`) runs on every PR. Heavy integration tests are often split to a separate CI job that runs `mvn -Pintegration-test verify` to avoid slowing the main build pipeline.

---

### ⚖️ Comparison Table

| Phase                   | Purpose                | Default Goal Bound   | When to Add Custom Goals                   |
| ----------------------- | ---------------------- | -------------------- | ------------------------------------------ |
| `generate-sources`      | Source code generation | None                 | Code generators (protobuf, jOOQ, OpenAPI)  |
| `compile`               | Compile main sources   | compiler:compile     | Never (override plugin config instead)     |
| `test-compile`          | Compile test sources   | compiler:testCompile | Test code generators                       |
| `test`                  | Unit test execution    | surefire:test        | Coverage tools (JaCoCo)                    |
| `pre-integration-test`  | Pre-IT setup           | None                 | Start Docker, mock servers                 |
| `integration-test`      | IT execution           | None                 | failsafe:integration-test                  |
| `post-integration-test` | Post-IT teardown       | None                 | Stop Docker, cleanup                       |
| `verify`                | Quality gates          | None                 | Coverage thresholds, failsafe result check |

**How to choose:** Bind setup/teardown operations to `pre-`/`post-` phases that surround the main execution phase. Use `verify` for quality gate enforcement (coverage minimums, static analysis failures).

---

### ⚠️ Common Misconceptions

| Misconception                                         | Reality                                                                                              |
| ----------------------------------------------------- | ---------------------------------------------------------------------------------------------------- |
| Phases and goals are the same thing                   | Phases are ordered checkpoints; goals are executable tasks bound to phases - fundamentally different |
| `clean` is a phase of the default lifecycle           | `clean` is its own lifecycle; `mvn clean package` runs two separate lifecycles in sequence           |
| Skipping a phase means skipping all subsequent phases | `-DskipTests` skips test execution but the `test` phase still executes - it's just empty             |
| All 23 phases are useful                              | Most projects only interact with 6-8; the others are extension points for advanced scenarios         |

---

### 🚨 Failure Modes & Diagnosis

**Custom goal runs at wrong point in build**

**Root Cause:** Goal bound to wrong phase - runs too late (after compilation) when it should run in `generate-sources`.

**Fix:** Check current phase binding: `mvn help:describe -Dplugin=myplugin -Dgoal=mygoal`. Change `<phase>` in pom.xml. Validate with `mvn -X` to see phase execution debug output.

---

**Integration tests fail but cleanup doesn't run**

**Root Cause:** Using `maven-surefire-plugin` for integration tests (bound to `test` phase) instead of `maven-failsafe-plugin`; when tests fail, lifecycle stops before `post-integration-test`.

**Fix:** Use `maven-failsafe-plugin` - its `integration-test` goal always runs (even on failure) and `verify` is where failures are reported, ensuring `post-integration-test` always executes.

---

### 🔗 Related Keywords

**Prerequisites:** `Maven Overview`, `pom.xml`, `Maven Lifecycle`, `Maven Goals`

**Builds On This:** `Maven Plugins`, `Build Performance Optimization`, `Maven Profiles`

**Related Patterns:** `Maven Goals`, `Maven Lifecycle`, `Maven Plugins`

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ MOST USED │ validate, compile, test, package,            │
│           │ install, deploy                              │
├───────────┼──────────────────────────────────────────────│
│ CODE GEN  │ bind to generate-sources                     │
├───────────┼──────────────────────────────────────────────│
│ IT TESTS  │ pre-IT → integration-test → post-IT → verify │
├───────────┼──────────────────────────────────────────────│
│ DEBUG     │ mvn -X (show phase/goal execution order)     │
├───────────┼──────────────────────────────────────────────│
│ DESCRIBE  │ mvn help:describe -Dplugin=X -Dgoal=Y        │
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** You need to generate Java source code from an OpenAPI spec before `javac` compiles the project. Which phase should you bind the generator to, and why would binding it to the `compile` phase be a problem?

**Q2.** Your integration tests start a Docker container in `pre-integration-test`, run tests in `integration-test`, and stop the container in `post-integration-test`. An IT fails. Will the `post-integration-test` phase (container stop) still run? What would happen if you had used the `maven-surefire-plugin` instead of `maven-failsafe-plugin` for the integration tests?
