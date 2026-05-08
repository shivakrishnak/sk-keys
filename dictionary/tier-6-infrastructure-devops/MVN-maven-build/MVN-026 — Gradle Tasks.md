---
layout: default
title: "Gradle Tasks"
parent: "Maven & Build Tools (Java)"
nav_order: 26
permalink: /maven-build/gradle-tasks/
id: MVN-026
category: Maven & Build Tools (Java)
difficulty: ★★★
depends_on: Gradle Build Script, Gradle vs Maven
used_by: Gradle Incremental Build, Gradle Build Cache, Gradle Convention Plugins
related: Gradle Incremental Build, Gradle Build Cache, Gradle Build Script
tags:
  - gradle
  - build-tools
  - tasks
  - java
  - deep-dive
---

# MVN-026 — Gradle Tasks

⚡ TL;DR — A Gradle task is an atomic unit of build work (compile, test, copy, sign) with declared inputs and outputs. Tasks form a DAG; Gradle runs only what's needed in dependency order — and skips tasks whose inputs haven't changed (incremental build).

| #1086           | Category: Maven & Build Tools (Java)                                    | Difficulty: ★★★ |
| :-------------- | :---------------------------------------------------------------------- | :-------------- |
| **Depends on:** | Gradle Build Script, Gradle vs Maven                                    |                 |
| **Used by:**    | Gradle Incremental Build, Gradle Build Cache, Gradle Convention Plugins |                 |
| **Related:**    | Gradle Incremental Build, Gradle Build Cache, Gradle Build Script       |                 |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
Build systems that run steps unconditionally — every step, every time — regardless of whether inputs changed. In Maven, running `mvn package` always compiles every file, even if only one file changed. Custom build steps are expressed as shell commands in CI scripts, not as typed, trackable build primitives.

**THE BREAKING POINT:**
As projects grow, the gap between "amount of work that actually needs doing" and "work the build system does" widens. A 10-second local compilation cycle becomes 5 minutes because the build tool can't reason about what changed.

**THE INVENTION MOMENT:**
Gradle models build work as tasks — typed objects with explicit `inputs` and `outputs`. Gradle tracks what changed. If inputs and outputs are unchanged since the last run, the task is `UP-TO-DATE` and skipped entirely. This granular, tracked model enables incremental builds and build caching.

---

### 📘 Textbook Definition

A **Gradle task** is an object representing a unit of build work, defined by: an optional type (extending `DefaultTask` or a built-in type), a set of declared inputs (files, directories, properties), a set of declared outputs (files, directories), and one or more actions (`doFirst`/`doLast` closures). Built-in plugins provide standard tasks (`compileJava`, `test`, `jar`). Tasks declare dependencies via `dependsOn`, `mustRunAfter`, `finalizedBy`, and `shouldRunAfter`. Gradle builds a Directed Acyclic Graph (DAG) of all tasks to execute, runs tasks in topological order respecting declared dependencies, and skips tasks whose inputs and outputs are unchanged (`UP-TO-DATE`) or whose outputs can be restored from the build cache (`FROM-CACHE`).

---

### ⏱️ Understand It in 30 Seconds

**One line:**
Tasks are the atoms of Gradle builds — each has declared inputs/outputs so Gradle can skip work that hasn't changed.

**One analogy:**

> Tasks are like Make targets, but smarter: Gradle computes the full dependency tree automatically, checks timestamps and checksums for you, and can restore outputs from a cache — not just skip based on file modification times.

**One insight:**
Declaring inputs and outputs correctly is the contract: if you declare them precisely, Gradle gives you incremental builds and cache hits for free. Lying to Gradle (undeclared inputs) gives false UP-TO-DATE and produces stale outputs — the worst kind of build bug.

---

### 🔩 First Principles Explanation

**TASK STATES:**

```
Task execution states:
  (no label)     → task ran (full execution)
  UP-TO-DATE     → inputs/outputs unchanged since last execution; skipped
  FROM-CACHE     → outputs restored from build cache; skipped
  SKIPPED        → task was explicitly skipped (e.g., predicate false, --exclude-task)
  NO-SOURCE      → task has no source files to process (e.g., no test files found)
```

**TASK DEPENDENCY GRAPH:**

```
build
 └── check
 │    └── test
 │         └── compileTestJava
 │              └── compileJava
 │                   └── processResources
 └── assemble
      └── jar
           └── classes
                ├── compileJava
                └── processResources
```

**BUILT-IN TASK TYPES:**

```kotlin
// Copy task
tasks.register<Copy>("copyConfigs") {
    from("src/main/config")
    into(layout.buildDirectory.dir("config"))
    include("*.yml")
}

// Exec task
tasks.register<Exec>("generateProto") {
    commandLine("protoc", "--java_out=build/generated", "src/proto/*.proto")
}

// Zip task
tasks.register<Zip>("packageDocs") {
    from("docs")
    archiveFileName.set("docs.zip")
    destinationDirectory.set(layout.buildDirectory.dir("dist"))
}
```

**THE TRADE-OFFS:**
**Gain:** UP-TO-DATE checking eliminates redundant work; build cache allows sharing task outputs across machines; task types provide reusable, typed build primitives; task graph enables parallel execution.
**Cost:** Correct input/output declaration requires discipline; incorrect declarations cause stale build outputs (harder to diagnose than a slow build); complex task graphs in large projects can slow configuration phase.

---

### 🧪 Thought Experiment

**SETUP:**
You have a custom `generateCode` task that reads a schema file and produces Java source files. You run it, Gradle marks it UP-TO-DATE. You change the schema file. Gradle still marks it UP-TO-DATE. Your generated code is wrong.

**ROOT CAUSE:**
You forgot to declare the schema file as an `inputs.file(...)`. Gradle doesn't know the schema file is an input, so it never re-runs the task when it changes.

**FIX:**

```kotlin
tasks.register("generateCode") {
    inputs.file("src/schema/model.json")      // declare: re-run if this changes
    outputs.dir(layout.buildDirectory.dir("generated"))
    doLast {
        // code generation logic
    }
}
```

**THE LESSON:**
UP-TO-DATE is only safe when all inputs and outputs are declared. Undeclared inputs = silent stale outputs.

---

### 🧠 Mental Model / Analogy

> Each Gradle task is a pure function with declared inputs and outputs — like a memoised function that caches its return value by input hash. If the inputs hash hasn't changed, return the cached output immediately. If inputs changed, re-execute and update the cache. The build graph is the function call graph of your build.

---

### 📶 Gradual Depth — Four Levels

**Level 1:** `./gradlew build` runs several tasks in order: compile, test, package. UP-TO-DATE next to a task name means it was skipped (nothing changed).

**Level 2:** Tasks have `dependsOn` links forming a DAG. Each task has `inputs` (source files, properties) and `outputs` (class files, JARs). If inputs and outputs are unchanged, the task is UP-TO-DATE.

**Level 3:** Custom tasks: use `tasks.register<Copy>(...)`, `tasks.register<Exec>(...)`, or `tasks.register("name") { doLast { ... } }`. Task ordering: `dependsOn` (must run first), `mustRunAfter` (order if both requested), `finalizedBy` (always run after, like a cleanup), `shouldRunAfter` (order hint, not enforced).

**Level 4:** Task inputs/outputs API: `inputs.files(...)`, `inputs.dir(...)`, `inputs.property(...)` for inputs; `outputs.file(...)`, `outputs.dir(...)` for outputs. Lazy configuration: `tasks.named(...)` (configure only if task is in graph) vs `tasks.getByName(...)` (always configures — avoid). Provider API (`layout.buildDirectory.file(...)`) for lazy evaluation. Task configuration avoidance for faster configuration phase.

---

### ⚙️ How It Works (Mechanism)

```bash
# List all tasks (and their group/description)
./gradlew tasks
./gradlew tasks --all

# Run a specific task
./gradlew compileJava

# Run task in specific subproject
./gradlew :web:test

# See task dependency graph
./gradlew :build --dry-run     # shows tasks that would run, in order

# Force re-run (ignore UP-TO-DATE)
./gradlew build --rerun-tasks

# Exclude a task from execution
./gradlew build -x test

# Parallel execution (if tasks are independent)
./gradlew build --parallel
```

---

### 💻 Code Example

**Complete custom task with correct input/output declaration:**

```kotlin
// build.gradle.kts

// Task type approach (reusable across subprojects)
abstract class GenerateVersionTask : DefaultTask() {
    @get:Input
    abstract val version: Property<String>

    @get:OutputFile
    abstract val outputFile: RegularFileProperty

    @TaskAction
    fun generate() {
        outputFile.get().asFile.writeText("version=${version.get()}")
    }
}

// Register the task
val generateVersion = tasks.register<GenerateVersionTask>("generateVersion") {
    version.set(project.version.toString())
    outputFile.set(layout.buildDirectory.file("generated/version.properties"))
}

// Wire task output into processResources input (lazy, correct)
tasks.named<ProcessResources>("processResources") {
    from(generateVersion.map { it.outputFile })
    into("META-INF")
}

// Lifecycle extension: custom task runs as part of 'check'
tasks.named("check") {
    dependsOn("customLintTask")
}

// Ordering: signJar must run after jar, but only if both requested
tasks.named("signJar") {
    mustRunAfter("jar")
}
```

---

### ⚖️ Comparison Table

| Relationship             | Maven equivalent            | Gradle (Kotlin DSL)                 |
| ------------------------ | --------------------------- | ----------------------------------- |
| Task runs before another | Plugin phase ordering       | `dependsOn("otherTask")`            |
| Task always runs after   | `verify` phase / post goals | `mustRunAfter("...")`               |
| Cleanup after task       | N/A                         | `finalizedBy("cleanupTask")`        |
| Skip task                | `-DskipTests`               | `-x taskName` or `onlyIf { false }` |
| List tasks               | `mvn help:describe`         | `./gradlew tasks`                   |

---

### ⚠️ Common Misconceptions

| Misconception                         | Reality                                                                             |
| ------------------------------------- | ----------------------------------------------------------------------------------- |
| `dependsOn` ensures ordering          | It ensures execution — if A `dependsOn` B, B runs first AND always when A runs      |
| `mustRunAfter` ensures B runs         | Only controls order IF both A and B are already in the graph                        |
| UP-TO-DATE means "correct output"     | Only if inputs/outputs are declared correctly; undeclared inputs → false UP-TO-DATE |
| `tasks.getByName(...)` is always fine | Eagerly configures the task; use `tasks.named(...)` for lazy configuration          |

---

### 🚨 Failure Modes & Diagnosis

**Task always runs (never UP-TO-DATE)**

**Root Cause:** Output directory not declared, or output changes between runs (e.g., timestamp embedded in output).

**Diagnosis:**

```bash
./gradlew taskName --info 2>&1 | grep -A3 "Input property"
# Shows what changed since last run
```

**Fix:** Declare outputs precisely; avoid writing non-deterministic content (timestamps) to output files.

---

**Task `UP-TO-DATE` but output is stale**

**Root Cause:** An input file is not declared via `inputs.file(...)` — Gradle doesn't know to re-run.

**Fix:** Add `inputs.file(...)` or `inputs.files(...)` for all files the task reads.

---

### 🔗 Related Keywords

**Prerequisites:** `Gradle Build Script`, `Gradle vs Maven`

**Builds On This:** `Gradle Incremental Build`, `Gradle Build Cache`, `Gradle Convention Plugins`

**Related Patterns:** `Gradle Incremental Build`, `Gradle Build Cache`, `Gradle Build Script`

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ REGISTER     │ tasks.register<Type>("name") { ... }      │
├──────────────┼───────────────────────────────────────────┤
│ STATES       │ (ran) | UP-TO-DATE | FROM-CACHE | SKIPPED │
├──────────────┼───────────────────────────────────────────┤
│ INPUTS       │ inputs.file/files/dir/property(...)       │
├──────────────┼───────────────────────────────────────────┤
│ OUTPUTS      │ outputs.file/dir/...)                     │
├──────────────┼───────────────────────────────────────────┤
│ ORDERING     │ dependsOn | mustRunAfter | finalizedBy    │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "Input+output declared → incremental free"│
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** You register a Gradle task that reads a file `config/app.yml` and writes to `build/output/app-processed.yml`. You run the build; it succeeds. You edit `config/app.yml`. You run again — task is UP-TO-DATE. What is missing, and how do you fix it?

**Q2.** What is the difference between `dependsOn` and `mustRunAfter` in terms of when each dependency type matters? Give a concrete example where `mustRunAfter` is the correct choice and `dependsOn` would be wrong.
