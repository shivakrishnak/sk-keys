---
layout: default
title: "Maven Goals"
parent: "Maven & Build Tools (Java)"
nav_order: 9
permalink: /maven-build/maven-goals/
id: MVN-009
category: Maven & Build Tools (Java)
difficulty: ★★☆
depends_on: Maven Overview, pom.xml, Maven Lifecycle (validate, compile, test, package, install, deploy)
used_by: Maven Phases, Maven Plugins, Build Performance Optimization
related: Maven Phases, Maven Plugins, Maven Lifecycle (validate, compile, test, package, install, deploy)
tags:
  - maven
  - build-tools
  - java
  - intermediate
  - build
---

# MVN-009 — Maven Goals

⚡ TL;DR — A Maven goal is a specific unit of work performed by a plugin (e.g., `compiler:compile`, `surefire:test`); it is the actual executable action behind every Maven build phase.

| #1069           | Category: Maven & Build Tools (Java)                        | Difficulty: ★★☆ |
| :-------------- | :---------------------------------------------------------- | :-------------- |
| **Depends on:** | Maven Overview, pom.xml, Maven Lifecycle                    |                 |
| **Used by:**    | Maven Phases, Maven Plugins, Build Performance Optimization |                 |
| **Related:**    | Maven Phases, Maven Plugins, Maven Lifecycle                |                 |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
The Maven lifecycle defines phases like `compile` and `test`, but phases themselves do nothing — they're just named milestones. Without goals, running `mvn compile` would be a no-op: the `compile` phase would be reached, and nothing would happen because there's nothing bound to it.

**THE BREAKING POINT:**
Build tools need to balance two concerns: (1) a fixed, predictable execution order (the lifecycle) and (2) pluggable, replaceable work units that perform actual tasks (the goals). Conflating these would mean you couldn't swap the compiler plugin without changing the lifecycle, or add code generation without modifying the phase definitions.

**THE INVENTION MOMENT:**
Maven separates the lifecycle (the ordered phases) from goals (the actual work). Goals are provided by plugins and bound to phases. This separation allows the lifecycle to be stable and universal while the implementation of each step is pluggable. This is why Maven goals exist as a distinct concept from phases.

---

### 📘 Textbook Definition

A **Maven goal** is a specific task or unit of work provided by a Maven plugin, identified by the notation `plugin-prefix:goal-name` (e.g., `compiler:compile`, `surefire:test`, `jar:jar`). Goals are the atomic executable units in Maven's build model. A goal can be bound to a lifecycle phase (so it executes automatically when that phase is reached) or executed directly via the command line (e.g., `mvn dependency:tree`). Each plugin exposes one or more goals; each goal performs a single, focused task. When multiple goals are bound to the same lifecycle phase, they execute in the order their plugins are declared in the POM.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
A goal is what actually runs when Maven builds — it's the specific action a plugin performs at a given phase.

**One analogy:**

> Maven phases are like chapter headings in a textbook ("Chapter 3: Testing"). Maven goals are the actual content of each chapter. The chapter heading tells you where you are in the sequence; the content is what you actually learn. Without content (goals), chapters are just empty titles.

**One insight:**
The key distinction: `mvn compile` executes the `compile` phase (which triggers the `compiler:compile` goal bound to it). `mvn compiler:compile` executes the goal directly, bypassing the lifecycle entirely. Understanding this distinction explains why some goals (like `dependency:tree` or `help:effective-pom`) run without triggering compilation.

---

### 🔩 First Principles Explanation

**CORE INVARIANTS:**

1. Every goal belongs to exactly one plugin.
2. A goal can be bound to a lifecycle phase (lifecycle-bound goal) or run standalone (direct goal invocation).
3. Goals bound to the same phase execute in POM declaration order.

**GOAL SYNTAX:**

```
mvn [phase]            → runs lifecycle up to and including phase
mvn [plugin]:[goal]    → runs a specific goal directly (no lifecycle)
mvn [phase] [plugin]:[goal]  → runs lifecycle to phase, then goal
```

**DEFAULT BINDINGS (jar packaging):**

| Phase          | Bound Goal             | Plugin                |
| -------------- | ---------------------- | --------------------- |
| `compile`      | `compiler:compile`     | maven-compiler-plugin |
| `test-compile` | `compiler:testCompile` | maven-compiler-plugin |
| `test`         | `surefire:test`        | maven-surefire-plugin |
| `package`      | `jar:jar`              | maven-jar-plugin      |
| `install`      | `install:install`      | maven-install-plugin  |
| `deploy`       | `deploy:deploy`        | maven-deploy-plugin   |

**STANDALONE GOALS (no lifecycle binding needed):**

```bash
mvn dependency:tree          # show dependency tree
mvn dependency:analyze       # find unused/undeclared deps
mvn help:effective-pom       # show merged effective POM
mvn versions:display-dependency-updates   # check for newer versions
mvn sonar:sonar              # run SonarQube analysis
```

**THE TRADE-OFFS:**

**Gain:** Pluggable build actions; any plugin can be added without changing the lifecycle; goals can be run standalone for ad-hoc operations.

**Cost:** The two-level model (lifecycle + goals) is more complex than a simple task list; newcomers often confuse phases with goals.

---

### 🧪 Thought Experiment

**SETUP:**
You want to run only the static analysis plugin (Checkstyle) without compiling or testing your project — you just want to check code style on the existing sources.

**WHAT HAPPENS IF GOALS DIDN'T EXIST (phases only):**
You'd have to run `mvn verify` or another phase that triggers Checkstyle, which also triggers compilation and testing. A 30-second style check becomes a 5-minute full build.

**WHAT HAPPENS WITH DIRECT GOAL INVOCATION:**

```bash
mvn checkstyle:check
```

This runs Checkstyle's `check` goal directly, without triggering any lifecycle phase. It scans sources, reports violations, and exits in seconds — no compilation, no testing.

**THE INSIGHT:**
Direct goal invocation transforms plugins from "lifecycle participants" into "command-line tools." Any plugin goal can be run standalone, making Maven a general-purpose project toolbox, not just a build pipeline.

---

### 🧠 Mental Model / Analogy

> Maven goals are like individual power tools in a workshop. The lifecycle is the assembly process ("step 1: cut, step 2: sand, step 3: paint"). Goals are the specific tools used at each step (circular saw, orbital sander, paint sprayer). You can also pick up any tool and use it directly — run the circular saw without doing the full assembly process.

- "Assembly step" → lifecycle phase (compile, test, package)
- "Power tool" → plugin goal (compiler:compile, surefire:test, jar:jar)
- "Using a tool outside the assembly process" → direct goal invocation (`mvn dependency:tree`)
- "Workshop toolbox" → Maven plugin ecosystem

**Where this analogy breaks down:** Power tools don't have a "default binding" to assembly steps; Maven goals do — the compiler plugin is automatically bound to the `compile` phase without any configuration.

---

### 📶 Gradual Depth — Four Levels

**Level 1 — What it is (anyone can understand):**
A Maven goal is a specific task a plugin can perform, like "compile Java code" or "run unit tests." Goals are what actually do the work when you run a Maven command.

**Level 2 — How to use it (junior developer):**
Run a goal directly with `mvn plugin:goal` (e.g., `mvn dependency:tree`). Or let the lifecycle trigger goals automatically — running `mvn test` automatically triggers `compiler:compile` and `surefire:test` because they're bound to the `compile` and `test` phases respectively. To see all goals a plugin provides: `mvn help:describe -Dplugin=compiler`.

**Level 3 — How it works (mid-level engineer):**
When Maven executes a lifecycle phase, it collects all goals bound to that phase (from default bindings + plugin declarations in `pom.xml`) and runs them in order. For direct goal invocation (`mvn dependency:tree`), Maven loads the plugin, instantiates the Mojo (Maven plain Old Java Object — the class implementing the goal), injects parameters from `pom.xml` and command line, and executes the goal's `execute()` method. No lifecycle is triggered.

**Level 4 — Why it was designed this way (senior/staff):**
The Mojo pattern (each goal is a Java class implementing `Mojo.execute()`) makes Maven's plugin API a first-class extension point. Any team can write a Maven plugin (a JAR with annotated Mojo classes) and distribute it via Maven Central. The lifecycle-binding mechanism means plugin authors can declare default phase bindings in the plugin's own POM (via `@Mojo(defaultPhase = LifecyclePhase.COMPILE)`), so consumers don't need to configure bindings unless they want to change them.

---

### ⚙️ How It Works (Mechanism)

```
┌──────────────────────────────────────────────────────┐
│   How a goal executes                                │
├──────────────────────────────────────────────────────┤
│                                                      │
│  mvn compiler:compile                                │
│       │                                              │
│       ▼                                              │
│  Maven downloads maven-compiler-plugin from repo     │
│       │                                              │
│       ▼                                              │
│  Locates Mojo class: CompilerMojo.java               │
│       │                                              │
│       ▼                                              │
│  Injects parameters:                                 │
│    source dir = ${project.build.sourceDirectory}     │
│    Java release = ${maven.compiler.release}          │
│    classpath = resolved dependency JARs              │
│       │                                              │
│       ▼                                              │
│  Calls CompilerMojo.execute()                        │
│    → invokes javax.tools.JavaCompiler                │
│    → writes .class files to target/classes/          │
│       │                                              │
│       ▼                                              │
│  Reports success (0 errors) or failure               │
└──────────────────────────────────────────────────────┘
```

**Goal execution order when multiple goals bound to same phase:**

```xml
<!-- Both goals run at 'generate-sources' phase -->
<plugins>
  <!-- Plugin A declared first → its goal runs first -->
  <plugin>
    <groupId>com.example</groupId>
    <artifactId>plugin-a</artifactId>
    <executions>
      <execution>
        <phase>generate-sources</phase>
        <goals><goal>generate</goal></goals>
      </execution>
    </executions>
  </plugin>

  <!-- Plugin B declared second → runs after plugin A -->
  <plugin>
    <groupId>com.example</groupId>
    <artifactId>plugin-b</artifactId>
    <executions>
      <execution>
        <phase>generate-sources</phase>
        <goals><goal>generate</goal></goals>
      </execution>
    </executions>
  </plugin>
</plugins>
```

---

### 🔄 The Complete Picture — End-to-End Flow

**NORMAL FLOW:**

```
mvn package
  → phase: validate (no default goals for jar)
  → phase: compile
      → GOAL: compiler:compile ← YOU ARE HERE
         → javac reads src/main/java/
         → writes target/classes/
  → phase: test-compile
      → GOAL: compiler:testCompile
  → phase: test
      → GOAL: surefire:test
  → phase: package
      → GOAL: jar:jar
  → target/my-app.jar ✓
```

**FAILURE PATH:**

```
GOAL: compiler:compile fails (compilation error)
  → Maven reports error with file + line number
  → lifecycle stops — test/package goals NEVER run
  → developer fixes source → re-runs mvn package
```

**WHAT CHANGES AT SCALE:**
In large multi-module builds, each module's goals execute in isolation. Goals like `sonar:sonar` aggregate results across all modules when run from the root. Remote build caches (Gradle Enterprise / Develocity for Maven) can skip goals whose inputs haven't changed.

---

### 💻 Code Example

**Example 1 — Useful standalone goals:**

```bash
# Show all transitive dependencies as a tree
mvn dependency:tree

# Verbose tree showing version conflict resolution
mvn dependency:tree -Dverbose

# Find unused declared deps / undeclared used deps
mvn dependency:analyze

# Show what the effective POM looks like (all inheritance merged)
mvn help:effective-pom

# Describe all goals of the compiler plugin
mvn help:describe -Dplugin=compiler -Ddetail

# Check for newer dependency versions
mvn versions:display-dependency-updates

# Check for newer plugin versions
mvn versions:display-plugin-updates
```

**Example 2 — Binding a goal to a custom phase in pom.xml:**

```xml
<build>
  <plugins>
    <plugin>
      <groupId>org.apache.maven.plugins</groupId>
      <artifactId>maven-antrun-plugin</artifactId>
      <executions>
        <execution>
          <id>print-build-info</id>
          <!-- bind to validate phase -->
          <phase>validate</phase>
          <goals>
            <!-- the goal to run: antrun:run -->
            <goal>run</goal>
          </goals>
          <configuration>
            <target>
              <echo>Building ${project.artifactId}
                     version ${project.version}</echo>
            </target>
          </configuration>
        </execution>
      </executions>
    </plugin>
  </plugins>
</build>
```

---

### ⚖️ Comparison Table

| Invocation             | What Runs                                         | Lifecycle Triggered? | Use Case              |
| ---------------------- | ------------------------------------------------- | -------------------- | --------------------- |
| `mvn compile`          | All phases up to `compile`, including bound goals | Yes                  | Normal compilation    |
| `mvn compiler:compile` | Only the `compiler:compile` goal                  | No                   | Ad-hoc compilation    |
| `mvn dependency:tree`  | Only the `dependency:tree` goal                   | No                   | Dependency inspection |
| `mvn clean package`    | `clean` lifecycle + `default` up to `package`     | Yes (both)           | Clean build           |
| `mvn -pl module test`  | `test` phase for one module only                  | Yes (single module)  | Module-scoped test    |

**How to choose:** Use lifecycle phase invocation (`mvn package`) for normal builds. Use direct goal invocation (`mvn dependency:tree`) for inspection, analysis, and reporting tasks that should not trigger a full build.

---

### ⚠️ Common Misconceptions

| Misconception                                           | Reality                                                                                                                |
| ------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------- |
| `mvn compile` runs the `compiler:compile` goal directly | It runs the lifecycle up to the `compile` phase, which triggers the bound goal — subtle but different                  |
| Goals always require a lifecycle phase                  | Many goals (like `dependency:tree`, `help:effective-pom`) are designed for standalone invocation with no phase binding |
| You can only run one goal at a time                     | You can run multiple: `mvn clean compiler:compile dependency:tree`                                                     |
| All phases have a goal bound by default                 | Many intermediate phases (`generate-sources`, `process-resources`) have no default bindings unless you add plugins     |

---

### 🚨 Failure Modes & Diagnosis

**Goal fails with "No plugin found for prefix"**

**Root Cause:** Maven can't resolve the plugin by its short prefix (e.g., `mvn versions:...` but the plugin isn't in the default group IDs).

**Fix:** Use the full plugin coordinates: `mvn org.codehaus.mojo:versions-maven-plugin:display-dependency-updates`, or add the plugin's groupId to `~/.m2/settings.xml` plugin groups.

---

**Two goals bound to the same phase conflict (both write to the same directory)**

**Root Cause:** Plugin declaration order determines execution order; earlier plugin overwrites later plugin's output.

**Fix:** Reorder plugin declarations, or configure each to write to distinct output directories.

---

### 🔗 Related Keywords

**Prerequisites:** `Maven Overview`, `pom.xml`, `Maven Lifecycle`

**Builds On This:** `Maven Phases`, `Maven Plugins`, `Build Performance Optimization`

**Related Patterns:** `Maven Phases`, `Maven Plugins`, `Maven Lifecycle`

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ SYNTAX      │ mvn plugin-prefix:goal-name               │
├─────────────┼──────────────────────────────────────────  │
│ LIFECYCLE   │ mvn compile → triggers compiler:compile   │
├─────────────┼──────────────────────────────────────────  │
│ STANDALONE  │ mvn dependency:tree (no lifecycle)        │
├─────────────┼──────────────────────────────────────────  │
│ DESCRIBE    │ mvn help:describe -Dplugin=compiler       │
├─────────────┼──────────────────────────────────────────  │
│ ORDER       │ goals bound to same phase: POM order      │
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** What is the difference between running `mvn test` and `mvn surefire:test`? In what scenario would you use one over the other?

**Q2.** You add a code-generation plugin to your `pom.xml` bound to the `generate-sources` phase. A colleague adds another code-generation plugin also bound to `generate-sources`. Plugin B depends on the output of Plugin A. How does Maven determine execution order, and what can you do to guarantee Plugin A runs first?
