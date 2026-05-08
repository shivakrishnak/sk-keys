---
layout: default
title: "Gradle Incremental Build"
parent: "Maven & Build Tools (Java)"
grand_parent: "Technical Dictionary"
nav_order: 27
permalink: /maven-build/gradle-incremental-build/
id: MVN-027
category: Maven & Build Tools (Java)
difficulty: ★★★
depends_on: Gradle Tasks, Gradle Build Script
used_by: Gradle Build Cache, Build Performance Optimization
related: Gradle Build Cache, Gradle Tasks, Build Performance Optimization
tags:
  - gradle
  - build-tools
  - incremental-build
  - performance
  - java
  - deep-dive
---

# MVN-027 — Gradle Incremental Build

⚡ TL;DR — Gradle's incremental build skips tasks whose declared inputs and outputs haven't changed since the last run, marking them UP-TO-DATE. Combined with incremental compilation (only recompile changed Java files), this dramatically reduces local development build times.

| #1087           | Category: Maven & Build Tools (Java)                             | Difficulty: ★★★ |
| :-------------- | :--------------------------------------------------------------- | :-------------- |
| **Depends on:** | Gradle Tasks, Gradle Build Script                                |                 |
| **Used by:**    | Gradle Build Cache, Build Performance Optimization               |                 |
| **Related:**    | Gradle Build Cache, Gradle Tasks, Build Performance Optimization |                 |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
You change one line in one Java file. You run `mvn package`. Maven compiles all 500 source files in the project, runs all 300 unit tests, re-packages the JAR. 90 seconds for a 1-line change.

**THE BREAKING POINT:**
Developer feedback loops are the most important factor in productivity. A 90-second build for a one-line change is not a workflow — it's an interruption. Multiply by 50 developers making 30 changes per day = thousands of developer-hours lost to redundant compilation.

**THE INVENTION MOMENT:**
Gradle tracks which source files changed, which class files they affect, and which tasks depend on affected outputs. Tasks that process only unchanged inputs are marked UP-TO-DATE and execute in nanoseconds. Tasks that process changed inputs re-run only for those changes (incremental task action). For the 1-line change: compile one file (200ms), run affected tests only, skip packaging if class files are unchanged.

---

### 📘 Textbook Definition

**Gradle incremental build** is a build optimisation where Gradle skips executing tasks whose declared inputs and outputs are identical to their state at the end of the last execution. Gradle persists input/output fingerprints (content hashes, not just timestamps) in a `.gradle/` directory. When a task is requested, Gradle compares current input fingerprints to stored fingerprints: if unchanged, the task is marked `UP-TO-DATE` and skipped. Beyond task-level skipping, **incremental task actions** (implemented via `InputChanges` API) allow a task to process only the files that changed — not all inputs. The Java plugin's `compileJava` task supports incremental compilation: only recompiling source files whose bytecode dependencies changed.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
Gradle remembers the state of every task's inputs/outputs; if nothing changed, the task is skipped instantly.

**One analogy:**

> A smart résumé checker that remembers what it reviewed last time. If no new jobs were posted and your résumé didn't change, it skips the review. Only new applications trigger new work.

**One insight:**
Incremental build is not about timestamps — it's about content fingerprints (SHA hashes). Touching a file without changing its content does not trigger a re-run. This is more robust and accurate than Make-style timestamp comparisons.

---

### 🔩 First Principles Explanation

**HOW UP-TO-DATE CHECKING WORKS:**

```
Previous execution:
  inputs: {src/Foo.java: SHA-256-abc, config.yml: SHA-256-xyz}
  outputs: {build/classes/Foo.class: SHA-256-def}
  stored in: .gradle/7.6/executionHistory.bin

Current execution request for 'compileJava':
  current inputs: {src/Foo.java: SHA-256-abc, config.yml: SHA-256-xyz}
  comparison: UNCHANGED → task is UP-TO-DATE → SKIP
```

**INCREMENTAL TASK ACTION (InputChanges API):**

```kotlin
abstract class ProcessTemplates : DefaultTask() {
    @get:InputFiles
    abstract val templateFiles: ConfigurableFileCollection

    @get:OutputDirectory
    abstract val outputDir: DirectoryProperty

    @TaskAction
    fun processTemplates(inputChanges: InputChanges) {
        if (inputChanges.isIncremental) {
            // Only process changed files
            inputChanges.getFileChanges(templateFiles).forEach { change ->
                when (change.changeType) {
                    ChangeType.ADDED, ChangeType.MODIFIED -> processFile(change.file)
                    ChangeType.REMOVED -> removeOutput(change.file)
                }
            }
        } else {
            // Full rebuild (e.g., first run, or output was deleted)
            templateFiles.forEach { processFile(it) }
        }
    }
}
```

**JAVA INCREMENTAL COMPILATION:**

```
Only Foo.java changed:
  1. Compile Foo.java → Foo.class
  2. Analyse: which classes depend on Foo? (classpath analysis)
  3. Only recompile those dependent classes
  4. All unaffected .java files: skipped
```

**THE TRADE-OFFS:**
**Gain:** Dramatically faster local builds after initial; no-op builds (nothing changed) complete in seconds; incremental task actions reduce per-file processing overhead.
**Cost:** `.gradle/` metadata must be preserved between builds (deleting it = cold rebuild); incorrect input/output declarations cause false UP-TO-DATE (stale outputs); configuration cache must also be valid for full skipping benefit; first build (cold) is no faster than Maven.

---

### 🧪 Thought Experiment

**SETUP:**
Your `generateDocs` task has:

- Input: all `*.java` files in `src/main/java`
- Output: `build/docs/` directory

You change one `.java` file. The task re-runs and regenerates ALL docs (not just the changed one's doc).

**WITH INCREMENTAL TASK ACTIONS:**

```kotlin
@TaskAction
fun generate(inputChanges: InputChanges) {
    inputChanges.getFileChanges(sourceFiles).forEach { change ->
        if (change.changeType != ChangeType.REMOVED) {
            generateDocFor(change.file)  // only regenerate this file's doc
        }
    }
}
```

**THE LESSON:**
Task-level incremental (UP-TO-DATE) coarsely skips the whole task. `InputChanges` finely processes only changed files within a single task execution. Both are valuable at different granularities.

---

### 🧠 Mental Model / Analogy

> Incremental build is like a smart to-do list app that tracks what was completed and what changed since last sync. If your task is "review these 100 documents," and you reviewed all of them yesterday and none changed today — your list says "all done, nothing new." You spend zero time reviewing. Only added or modified documents go on today's list.

---

### 📶 Gradual Depth — Four Levels

**Level 1:** Gradle skips tasks when nothing changed. `UP-TO-DATE` means "I checked — inputs same as last time, outputs still valid — no work needed."

**Level 2:** Gradle stores content fingerprints (not timestamps) of inputs and outputs. Even if you `touch` a file without changing content, Gradle won't re-run the task. `./gradlew build` after no changes completes in under 1 second for a large project.

**Level 3:** `InputChanges` API enables sub-task incremental work: only process files that were added/modified/removed since last run. The Java `compileJava` task uses this — only files whose class dependencies changed are recompiled.

**Level 4:** Interaction with build cache: incremental build checks local state; build cache extends this to shared state. If task was run by CI yesterday with the same inputs (same SHA), developer can restore outputs from cache without re-running at all. Combined: incremental build (local skip) + build cache (remote restore) = near-zero rebuild time for unchanged work.

---

### ⚙️ How It Works (Mechanism)

```bash
# Run build and observe UP-TO-DATE markers
./gradlew build

# Output:
# > Task :compileJava UP-TO-DATE
# > Task :processResources UP-TO-DATE
# > Task :classes UP-TO-DATE
# > Task :jar UP-TO-DATE
# > Task :assemble UP-TO-DATE

# Force all tasks to re-run (ignore incremental state)
./gradlew build --rerun-tasks

# See why a task was not UP-TO-DATE (input that changed)
./gradlew compileJava --info 2>&1 | grep -E "(UP-TO-DATE|not up-to-date|Input property)"

# Clean removes outputs (forces full rebuild next run)
./gradlew clean build  # equivalent to mvn clean install
```

---

### 💻 Code Example

**Demonstrating UP-TO-DATE in a multi-module project:**

```bash
# Initial build: everything compiles and tests run
$ ./gradlew build
> Task :domain:compileJava
> Task :domain:test
> Task :api:compileJava
> Task :api:test
> Task :web:compileJava
> Task :web:test
BUILD SUCCESSFUL in 45s

# No changes: run again
$ ./gradlew build
> Task :domain:compileJava UP-TO-DATE
> Task :domain:test UP-TO-DATE
> Task :api:compileJava UP-TO-DATE
> Task :api:test UP-TO-DATE
> Task :web:compileJava UP-TO-DATE
> Task :web:test UP-TO-DATE
BUILD SUCCESSFUL in 0.8s   ← 45x faster

# Change one file in domain:
$ echo "// change" >> domain/src/main/java/Foo.java
$ ./gradlew build
> Task :domain:compileJava        ← recompiled (input changed)
> Task :domain:test               ← re-run (compiled output changed)
> Task :api:compileJava           ← re-run (depends on domain classes)
> Task :api:test UP-TO-DATE       ← tests not affected
> Task :web:compileJava UP-TO-DATE
> Task :web:test UP-TO-DATE
BUILD SUCCESSFUL in 8s     ← only affected tasks ran
```

---

### ⚖️ Comparison Table

| Mechanism               | Scope                       | How                               | Benefit                           |
| ----------------------- | --------------------------- | --------------------------------- | --------------------------------- |
| Task UP-TO-DATE         | Whole task                  | Input/output fingerprints         | Skip entire task                  |
| Incremental task action | Per-file within task        | `InputChanges` API                | Process only changed files        |
| Incremental compilation | Per Java class              | Classpath dependency analysis     | Recompile only affected classes   |
| Build cache             | Cross-build / cross-machine | Input fingerprint → cached output | Restore from cache (no execution) |

---

### ⚠️ Common Misconceptions

| Misconception                             | Reality                                                                                  |
| ----------------------------------------- | ---------------------------------------------------------------------------------------- |
| `./gradlew clean build` is safer          | `clean` destroys incremental state — only use when debugging; slow it down unnecessarily |
| UP-TO-DATE means "no bugs"                | It means inputs/outputs match last run; a bug won't affect UP-TO-DATE checking           |
| Incremental build only helps locally      | With build cache, it benefits CI too (restoring outputs from previous runs)              |
| Touching a file always triggers recompile | Only changing _content_ triggers recompile; Gradle uses content hashes, not timestamps   |

---

### 🚨 Failure Modes & Diagnosis

**Build produces stale output after source change**

**Root Cause:** Input file (e.g., schema, template) not declared as a task input — Gradle doesn't know to re-run.

**Diagnosis:**

```bash
./gradlew taskName --info | grep "Task ':taskName' is not up-to-date"
```

**Fix:** Add `inputs.file(...)` or `inputs.files(...)` for all files the task reads.

---

**Incremental compilation misses a change (wrong class file)**

**Root Cause:** Annotation processor output or a generated source file changed but wasn't tracked.

**Fix:** Declare generated source directories as `inputs`; ensure `compileJava.options.incremental = true` (enabled by default in modern Gradle).

---

### 🔗 Related Keywords

**Prerequisites:** `Gradle Tasks`, `Gradle Build Script`

**Builds On This:** `Gradle Build Cache`, `Build Performance Optimization`

**Related Patterns:** `Gradle Build Cache`, `Gradle Tasks`, `Build Performance Optimization`

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ UP-TO-DATE   │ Task skipped: inputs+outputs unchanged    │
├──────────────┼───────────────────────────────────────────┤
│ HOW TRACKED  │ Content fingerprints (SHA), not timestamps│
├──────────────┼───────────────────────────────────────────┤
│ FORCE RERUN  │ --rerun-tasks                             │
├──────────────┼───────────────────────────────────────────┤
│ INPUT API    │ inputs.file/files/dir/property(...)       │
├──────────────┼───────────────────────────────────────────┤
│ INCREMENTAL  │ InputChanges → only process changed files │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "Skip unchanged; rerun only what changed" │
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** You have a custom Gradle task that reads from a database to generate a configuration file. How would you model this in Gradle's incremental build system? What challenges arise from non-file inputs, and what workarounds exist?

**Q2.** A colleague runs `./gradlew clean build` every time "just to be safe." Explain what `clean` actually does to Gradle's incremental state, and when (if ever) it is genuinely necessary versus unnecessary overhead.
