---
layout: default
title: "Gradle Build Script"
parent: "Maven & Build Tools (Java)"
grand_parent: "Technical Dictionary"
nav_order: 25
permalink: /maven-build/gradle-build-script/
id: MVN-025
category: Maven & Build Tools (Java)
difficulty: ★★★
depends_on: Gradle vs Maven, Gradle Tasks
used_by: Gradle Tasks, Gradle Incremental Build, Gradle Convention Plugins
related: Gradle Tasks, Gradle Incremental Build, Gradle Convention Plugins
tags:
  - gradle
  - build-tools
  - build-script
  - kotlin-dsl
  - java
  - deep-dive
---

# MVN-025 — Gradle Build Script

⚡ TL;DR — A Gradle build script (`build.gradle.kts` in Kotlin DSL or `build.gradle` in Groovy DSL) defines plugins, dependencies, tasks, and configuration for a project using a programmatic API — it's both build configuration and executable code in one file.

| #1085           | Category: Maven & Build Tools (Java)                              | Difficulty: ★★★ |
| :-------------- | :---------------------------------------------------------------- | :-------------- |
| **Depends on:** | Gradle vs Maven, Gradle Tasks                                     |                 |
| **Used by:**    | Gradle Tasks, Gradle Incremental Build, Gradle Convention Plugins |                 |
| **Related:**    | Gradle Tasks, Gradle Incremental Build, Gradle Convention Plugins |                 |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
Build logic must live in XML (Maven) or a separate shell script. Complex build steps — code generation, signing, custom packaging, conditional compilation — require writing a full Maven plugin (a separate Maven project with Java classes). Every custom build requirement becomes disproportionately heavy.

**THE BREAKING POINT:**
Real-world build requirements are never purely declarative: "compile these files with this processor, but only if this environment variable is set; generate this protobuf schema; copy these resources to a special location; sign the JAR with this key on release only." Maven's XML cannot express this without plugin authorship. Shell scripts are fragile and not portable.

**THE INVENTION MOMENT:**
Gradle build scripts are code: they can contain `if` statements, loops, function calls, and any JVM library — while also providing a clean DSL for the common declarative cases (plugins, dependencies, repositories). One file handles both declarative config and custom build logic.

---

### 📘 Textbook Definition

A **Gradle build script** is a file (`build.gradle` in Groovy DSL, or `build.gradle.kts` in Kotlin DSL) that configures a Gradle project. It uses Gradle's API to: apply plugins (`plugins { }` block), declare dependencies (`dependencies { }` block), configure compilation, testing, packaging, and publication, and define or customise tasks. The script is executed by Gradle during the configuration phase, building a task graph that is then executed. Kotlin DSL (`build.gradle.kts`) is the modern standard, offering static type checking, IDE auto-complete, and compile-time error detection not available in Groovy DSL.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
`build.gradle.kts` is your project's build definition: plugins, dependencies, and tasks — in typed, IDE-friendly Kotlin code.

**One analogy:**

> A Maven `pom.xml` is a form you fill in with fixed fields. A Gradle build script is a recipe you write in a real programming language — you can add conditionals, loops, and custom logic, but you still follow cooking conventions (prepare, cook, plate).

**One insight:**
The `plugins { }` block is declarative and evaluated first; everything else is configuration code. Understanding the three Gradle build phases — initialisation, configuration, execution — is the key to writing correct Gradle scripts.

---

### 🔩 First Principles Explanation

**GRADLE BUILD PHASES:**

```
Phase 1: INITIALIZATION
  - Reads settings.gradle.kts
  - Determines which projects exist in the build
  - Creates Project objects for each

Phase 2: CONFIGURATION
  - Executes build.gradle.kts for each project
  - Configures plugins, dependencies, tasks
  - Builds the task dependency graph
  - ALL build script code runs here (even if task won't execute)

Phase 3: EXECUTION
  - Runs only the tasks requested (and their dependencies)
  - Task actions execute in dependency order
```

**COMMON MISTAKE: Code in configuration phase, not execution phase:**

```kotlin
// WRONG: This print runs EVERY time — during configuration, not just when 'build' runs
tasks.named("build") {
    println("Building...")  // configuration phase — runs even for 'gradle tasks'
}

// CORRECT: Use doLast to run code in the execution phase
tasks.named("build") {
    doLast {
        println("Build complete!")  // execution phase — only when task runs
    }
}
```

**SCRIPT STRUCTURE:**

```kotlin
// build.gradle.kts — Kotlin DSL

// 1. PLUGINS BLOCK (evaluated first, special semantics)
plugins {
    id("java")                          // standard Java plugin
    id("org.springframework.boot") version "3.2.0"
    id("io.spring.dependency-management") version "1.1.4"
}

// 2. PROJECT METADATA
group = "com.example"
version = "1.0.0"
description = "My Spring Boot service"

// 3. JAVA TOOLCHAIN (replaces manual source/target)
java {
    toolchain {
        languageVersion = JavaLanguageVersion.of(17)
    }
}

// 4. REPOSITORIES
repositories {
    mavenCentral()
    maven { url = uri("https://nexus.mycompany.com/repository/maven-public/") }
}

// 5. DEPENDENCIES
dependencies {
    // Configurations map to Maven scopes:
    implementation("org.springframework.boot:spring-boot-starter-web")      // compile + runtime (not test)
    runtimeOnly("org.postgresql:postgresql")                                 // runtime only
    compileOnly("org.projectlombok:lombok")                                  // compile only (like Maven 'provided')
    annotationProcessor("org.projectlombok:lombok")
    testImplementation("org.springframework.boot:spring-boot-starter-test")
    testRuntimeOnly("org.junit.platform:junit-platform-launcher")
}

// 6. TASK CONFIGURATION
tasks.withType<Test> {
    useJUnitPlatform()
    maxHeapSize = "2g"
}

tasks.named<Jar>("jar") {
    archiveClassifier = "plain"  // Spring Boot plugin creates fat jar; this avoids conflict
}

// 7. CUSTOM TASK
tasks.register("printVersion") {
    group = "help"
    description = "Prints the project version"
    doLast {
        println("Version: ${project.version}")
    }
}
```

**THE TRADE-OFFS:**
**Gain:** Full Kotlin type safety; IDE auto-complete; can express any build logic; composable with `buildSrc` or convention plugins; readable for developers who know Kotlin.
**Cost:** Configuration phase runs all code eagerly (if poorly written, can be slow); Groovy DSL tempts dynamic typing anti-patterns; build scripts require Kotlin/Groovy knowledge; debugging required when build script has bugs.

---

### 🧪 Thought Experiment

**SETUP:**
You need to generate a `version.txt` file containing the current build version during every build, to be included in the JAR's `META-INF/`. In Maven, this requires writing a plugin or using a complex `maven-resources-plugin` filter. In Gradle:

```kotlin
val writeVersion = tasks.register("writeVersion") {
    val outDir = layout.buildDirectory.dir("generated/resources")
    outputs.dir(outDir)
    inputs.property("version", project.version)

    doLast {
        outDir.get().asFile.mkdirs()
        outDir.get().file("META-INF/version.txt").asFile
            .writeText(project.version.toString())
    }
}

sourceSets.main {
    resources.srcDir(writeVersion.map { it.outputs.files })
}
```

**THE LESSON:**
Custom build logic that would require a new Maven plugin is 10 lines in a Gradle build script — directly in `build.gradle.kts`, no separate project required.

---

### 🧠 Mental Model / Analogy

> A Gradle build script is like a `Makefile` with a clean API and a type system. The `plugins { }` block declares which tools are available. The `dependencies { }` block declares what materials are needed. The `tasks { }` block defines the steps. Everything outside a `doLast`/`doFirst` block is configuration code (the plan); everything inside is execution code (the work).

---

### 📶 Gradual Depth — Four Levels

**Level 1:** `build.gradle.kts` is a Kotlin file. The `plugins { }` block adds capabilities (Java, Spring Boot). The `dependencies { }` block lists libraries. `./gradlew build` runs the build.

**Level 2:** Gradle's `dependencies` configurations map to lifecycle: `implementation` (compile + runtime), `testImplementation` (tests only), `runtimeOnly` (JARs in classpath, not compile). `repositories` lists where to find JARs.

**Level 3:** Kotlin DSL vs Groovy DSL: `build.gradle.kts` has static type checking and IDE auto-complete; `build.gradle` (Groovy) is dynamically typed. Prefer Kotlin DSL for new projects. Configuration phase vs execution phase: code not inside `doLast` runs during configuration — keep it lightweight.

**Level 4:** `buildSrc` folder: a special Gradle project whose code is available in all build scripts. Use it for shared build logic, custom task classes, and type-safe version catalogs. Convention plugins (inside `buildSrc` or a separate `build-conventions` module): reusable, shareable Gradle plugin applied to all subprojects — the Gradle equivalent of a parent POM.

---

### ⚙️ How It Works (Mechanism)

```bash
# Key Gradle commands corresponding to build script elements:
./gradlew dependencies            # show dependency graph for all configurations
./gradlew dependencies --configuration implementation  # specific configuration
./gradlew properties              # dump all project properties
./gradlew tasks                   # list all available tasks
./gradlew tasks --all             # including task dependencies
./gradlew build --scan            # generate build scan at scans.gradle.com
./gradlew help --task compileJava # describe a specific task's inputs/outputs
```

---

### 💻 Code Example

**`settings.gradle.kts` — multi-project root:**

```kotlin
rootProject.name = "my-enterprise-app"

include(
    "domain",
    "api",
    "web",
    "infra"
)

// Version catalog (modern dependency management)
dependencyResolutionManagement {
    repositories {
        mavenCentral()
    }
    versionCatalogs {
        create("libs") {
            version("spring-boot", "3.2.0")
            library("spring-boot-web", "org.springframework.boot", "spring-boot-starter-web")
                .versionRef("spring-boot")
        }
    }
}
```

**`build.gradle.kts` — Groovy to Kotlin DSL translation:**

```groovy
// GROOVY (old):
dependencies {
    implementation 'org.springframework.boot:spring-boot-starter-web:3.2.0'
}
tasks.named('test') {
    useJUnitPlatform()
}
```

```kotlin
// KOTLIN DSL (modern):
dependencies {
    implementation("org.springframework.boot:spring-boot-starter-web:3.2.0")
}
tasks.named<Test>("test") {
    useJUnitPlatform()
}
```

---

### ⚖️ Comparison Table

| Element            | Maven equivalent          | Gradle (Kotlin DSL)                    |
| ------------------ | ------------------------- | -------------------------------------- |
| Build definition   | `pom.xml`                 | `build.gradle.kts`                     |
| Plugin application | `<plugin>` in `<build>`   | `plugins { id(...) }`                  |
| Dependency         | `<dependency>`            | `dependencies { implementation(...) }` |
| compile scope      | `<scope>compile</scope>`  | `implementation(...)`                  |
| test scope         | `<scope>test</scope>`     | `testImplementation(...)`              |
| provided scope     | `<scope>provided</scope>` | `compileOnly(...)`                     |
| runtime scope      | `<scope>runtime</scope>`  | `runtimeOnly(...)`                     |
| Property           | `<properties>`            | `ext { }` or Kotlin val                |
| Custom goal        | New plugin project        | `tasks.register("name") { }`           |

---

### ⚠️ Common Misconceptions

| Misconception                                                    | Reality                                                                                        |
| ---------------------------------------------------------------- | ---------------------------------------------------------------------------------------------- |
| Code in `tasks.named("build") { }` runs only when that task runs | Code outside `doLast`/`doFirst` runs during configuration phase — always                       |
| Groovy DSL and Kotlin DSL are equivalent                         | Kotlin DSL has static typing + IDE auto-complete; Groovy is dynamic                            |
| `implementation` = Maven `compile`                               | Similar, but Gradle `implementation` hides transitive deps from consumers (`api` exposes them) |
| `build.gradle.kts` is just config (not code)                     | It is compiled Kotlin code — bugs and logic errors are possible                                |

---

### 🚨 Failure Modes & Diagnosis

**Configuration cache miss: build script runs slowly every time**

**Root Cause:** Build script contains I/O operations or uses non-cacheable APIs at configuration time.

**Diagnosis:**

```bash
./gradlew build --configuration-cache
# Reports: "X problems found reusing configuration cache"
```

**Fix:** Move I/O and task-specific logic inside `doLast { }` actions.

---

**`Could not resolve` dependency at configuration time**

**Root Cause:** Accessing `configurations.runtimeClasspath.files` at configuration time forces dependency resolution too early.

**Fix:** Use `configurations.runtimeClasspath` lazily, or only access files inside a task action.

---

### 🔗 Related Keywords

**Prerequisites:** `Gradle vs Maven`, `Gradle Tasks`

**Builds On This:** `Gradle Tasks`, `Gradle Incremental Build`, `Gradle Convention Plugins`

**Related Patterns:** `Gradle Tasks`, `Gradle Incremental Build`, `Gradle Convention Plugins`

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ FILE         │ build.gradle.kts (Kotlin) or .groovy      │
├──────────────┼───────────────────────────────────────────┤
│ BLOCKS       │ plugins | repositories | dependencies |   │
│              │ java | tasks                              │
├──────────────┼───────────────────────────────────────────┤
│ CONFIG PHASE │ All script code (even uneeded tasks)      │
├──────────────┼───────────────────────────────────────────┤
│ EXEC PHASE   │ Only doLast/doFirst inside tasks          │
├──────────────┼───────────────────────────────────────────┤
│ SCOPE MAP    │ implementation=compile, runtimeOnly=runtime│
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "Typed code that describes the build"     │
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** In a Gradle build script, you write `println("Configuring project")` directly inside the `plugins { }` block, and also inside a `doLast { }` action in a custom task. During `./gradlew tasks` (which doesn't execute any task), which print statement runs? Why?

**Q2.** You have a multi-project Gradle build with 20 subprojects. Every subproject needs the same `plugins`, `repositories`, and base `dependencies` configuration. Instead of copying this into 20 `build.gradle.kts` files, what Gradle mechanism would you use to share it, and how does it compare to Maven's parent POM approach?
