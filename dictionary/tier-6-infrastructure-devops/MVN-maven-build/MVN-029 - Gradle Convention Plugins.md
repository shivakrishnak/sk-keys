---
layout: default
title: "Gradle Convention Plugins"
parent: "Maven & Build Tools (Java)"
grand_parent: "Technical Dictionary"
nav_order: 29
permalink: /maven-build/gradle-convention-plugins/
id: MVN-029
category: Maven & Build Tools (Java)
difficulty: ★★★
depends_on: Gradle Build Script, Gradle Tasks, Maven Multi-Module Project
used_by: Build Performance Optimization, Build Reproducibility, Gradle Incremental Build
related: Gradle Build Script, Gradle Tasks, Maven Multi-Module Project
tags:
  - gradle
  - build-tools
  - convention-plugins
  - buildSrc
  - java
  - deep-dive
---

# MVN-029 - Gradle Convention Plugins

⚡ TL;DR - Convention plugins are reusable Gradle plugins (written in `buildSrc/` or a standalone build-conventions module) that apply shared build standards to multiple subprojects - the Gradle equivalent of Maven's parent POM, but with full programming-language power.

| #1089           | Category: Maven & Build Tools (Java)                                            | Difficulty: ★★★ |
| :-------------- | :------------------------------------------------------------------------------ | :-------------- |
| **Depends on:** | Gradle Build Script, Gradle Tasks, Maven Multi-Module Project                   |                 |
| **Used by:**    | Build Performance Optimization, Build Reproducibility, Gradle Incremental Build |                 |
| **Related:**    | Gradle Build Script, Gradle Tasks, Maven Multi-Module Project                   |                 |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
A 20-subproject Gradle build. Every `build.gradle.kts` starts with the same 60 lines: same plugins, same repositories, same compiler settings, same test framework config, same code style plugin. A team decides to enforce a new lint rule. They update 20 files. Two are missed. Inconsistency creeps in.

**THE BREAKING POINT:**
Copy-pasted build script fragments across subprojects violate DRY. Changes require touching every subproject. Refactoring (e.g., upgrading from Java 17 to Java 21 across all modules) becomes a mechanical but error-prone multi-file operation.

**THE INVENTION MOMENT:**
Convention plugins: a custom Gradle plugin that applies a _convention_ - a set of build rules that reflect how all your projects should be built. Apply `my-company.java-conventions` to a subproject and it gets: correct JDK version, test framework, code coverage, lint, standard repos - in one line. Change the convention; all subprojects update automatically on next build.

---

### 📘 Textbook Definition

**Gradle convention plugins** are lightweight Gradle plugins, written in the `buildSrc/` directory or in a dedicated composite build (e.g., `build-logic/`), that encapsulate and enforce build conventions across a multi-project build. They are applied to subprojects using `plugins { id("...") }` syntax. Each convention plugin is a `Plugin<Project>` implementation (or a precompiled script plugin - a `.gradle.kts` file in `buildSrc/src/main/kotlin/`) that applies base plugins, configures repositories, defines dependency constraints, sets compiler options, and configures testing. Convention plugins replace duplicated `build.gradle.kts` boilerplate with a single, version-controlled, testable build convention.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
Convention plugins package repeated build config into an apply-one-liner - the Gradle equivalent of a shared parent POM, with code.

**One analogy:**

> A company employee handbook embedded into HR software. Every new hire applies the same handbook (`my-company.java-conventions`); the rules are enforced automatically, not copy-pasted. Update the handbook - all employees follow the new rules on the next login.

**One insight:**
Convention plugins enable the same "convention over configuration" that Maven's parent POM provides - but because they're code (Kotlin), they can express any logic: conditional configuration, cross-cutting concerns, computed properties.

---

### 🔩 First Principles Explanation

**`buildSrc/` MECHANICS:**
`buildSrc/` is a special Gradle project directory that is:

1. Automatically detected and compiled before the main build
2. Its compiled code is available on the classpath of all build scripts in the main build
3. Changes to `buildSrc/` invalidate all build script caches (configuration cache)

**PRECOMPILED SCRIPT PLUGIN (simplest form):**

```
buildSrc/
  src/main/kotlin/
    my-company.java-conventions.gradle.kts   ← the convention plugin
  build.gradle.kts                           ← buildSrc's own build file
```

`my-company.java-conventions.gradle.kts`:

```kotlin
// This file IS the convention plugin - applied like: plugins { id("my-company.java-conventions") }

plugins {
    id("java-library")
    id("jacoco")
    id("checkstyle")
}

java {
    toolchain {
        languageVersion = JavaLanguageVersion.of(17)
    }
}

repositories {
    mavenCentral()
    maven { url = uri("https://nexus.mycompany.com/repository/maven-public/") }
}

dependencies {
    testImplementation("org.junit.jupiter:junit-jupiter:5.10.1")
    testRuntimeOnly("org.junit.platform:junit-platform-launcher")
}

tasks.withType<Test> {
    useJUnitPlatform()
    maxHeapSize = "2g"
}

jacoco {
    toolVersion = "0.8.11"
}

tasks.named<JacocoReport>("jacocoTestReport") {
    reports {
        xml.required = true
        html.required = true
    }
}

checkstyle {
    toolVersion = "10.12.5"
    configFile = rootProject.file("config/checkstyle/checkstyle.xml")
}
```

**SUBPROJECT `build.gradle.kts`:**

```kotlin
// Before: 60 lines of boilerplate
// After: ONE LINE
plugins {
    id("my-company.java-conventions")
}

// Only project-specific config remains:
dependencies {
    implementation(project(":shared-domain"))
    implementation("org.springframework.boot:spring-boot-starter-web")
}
```

**`buildSrc/build.gradle.kts`:**

```kotlin
plugins {
    `kotlin-dsl`   // enables .gradle.kts precompiled script plugins
}

repositories {
    gradlePluginPortal()  // so buildSrc can use Gradle plugins
    mavenCentral()
}
```

**THE TRADE-OFFS:**
**Gain:** DRY build configuration; single point of change; testable build logic; IDE auto-complete in convention plugin scripts; conventions are version-controlled and code-reviewed.
**Cost:** `buildSrc/` changes invalidate ALL configuration caches (build-logic composite build avoids this); adds a `buildSrc/` project build overhead; developers must know where conventions live; too much logic in one convention plugin reduces flexibility.

---

### 🧪 Thought Experiment

**SETUP:**
Your `my-company.java-conventions` plugin configures `checkstyle`. Module `legacy-service` has 200 existing checkstyle violations and can't be fixed in the current sprint. You can't exempt it from conventions entirely - it still needs the JDK and test framework config.

**APPROACHES:**

1. Split convention: `my-company.java-base` (JDK, test, repos) + `my-company.java-quality` (checkstyle, coverage). `legacy-service` applies `java-base` only.
2. Add a configurable property to the convention: `checkstyleEnabled = false` in `legacy-service/build.gradle.kts`
3. Add `legacy-service` to a suppression list in the convention plugin

**THE LESSON:**
Convention plugins should be composable and optionally configurable. A monolithic convention that can't be partially opted-out from becomes a migration blocker. Design conventions as small, focused, additive plugins.

---

### 🧠 Mental Model / Analogy

> Convention plugins are like linting rules in a shared ESLint config (`eslint-config-company`). Every JavaScript project in your org extends the shared config; the rules are centralised and version-controlled. Individual projects can override specific rules as needed, but the base standard applies everywhere automatically.

---

### 📶 Gradual Depth - Four Levels

**Level 1:** Instead of copying the same 60 lines into every `build.gradle.kts`, you create a convention plugin. Each module applies it in one line and inherits all the shared config.

**Level 2:** Convention plugins live in `buildSrc/src/main/kotlin/` as `.gradle.kts` files. They're precompiled by Gradle and available by filename (without extension) as plugin IDs. `buildSrc/` is compiled before the main build.

**Level 3:** Multiple convention plugins can be defined and applied in combination: `my-company.java-conventions` for Java base; `my-company.spring-conventions` for Spring-specific config; `my-company.publishing-conventions` for release setup. Subprojects apply only the plugins they need.

**Level 4:** Composite build alternative to `buildSrc/`: create a separate `build-logic/` Gradle project, included in `settings.gradle.kts` via `includeBuild("build-logic")`. Advantage: `build-logic/` changes don't invalidate all configuration caches (unlike `buildSrc/`); can be versioned and published as a standalone plugin for cross-project sharing.

---

### ⚙️ How It Works (Mechanism)

```bash
# buildSrc is auto-compiled - no explicit command needed
# But you can test convention plugins directly:
cd buildSrc && ./gradlew test

# View effective build configuration after convention plugin applied:
./gradlew :module:dependencies
./gradlew :module:properties | grep toolchain

# List all plugins applied to a subproject:
./gradlew :module:buildEnvironment
```

---

### 💻 Code Example

**Complete `buildSrc/` structure for a Spring Boot microservices monorepo:**

```
buildSrc/
  build.gradle.kts
  src/main/kotlin/
    my-company.java-base.gradle.kts        ← JDK, test, repos
    my-company.spring-service.gradle.kts   ← Spring Boot config
    my-company.publishing.gradle.kts       ← release + publish config
```

`my-company.spring-service.gradle.kts`:

```kotlin
plugins {
    id("my-company.java-base")             // apply base convention
    id("org.springframework.boot")
    id("io.spring.dependency-management")
}

val springBootVersion: String by extra("3.2.0")

springBoot {
    mainClass = "com.mycompany.${project.name}.ApplicationKt"
}

dependencies {
    implementation("org.springframework.boot:spring-boot-starter-actuator")
    implementation("org.springframework.boot:spring-boot-starter-web")
    testImplementation("org.springframework.boot:spring-boot-starter-test")
}

tasks.named<BootJar>("bootJar") {
    archiveClassifier = ""
}
tasks.named<Jar>("jar") {
    archiveClassifier = "plain"
}
```

Subproject `user-service/build.gradle.kts`:

```kotlin
plugins {
    id("my-company.spring-service")  // one line → full Spring Boot setup
}

dependencies {
    implementation(project(":shared-domain"))
    implementation("org.springframework.boot:spring-boot-starter-data-jpa")
    runtimeOnly("org.postgresql:postgresql")
}
```

---

### ⚖️ Comparison Table

| Mechanism                  | Maven equivalent                       | Convention plugin                      |
| -------------------------- | -------------------------------------- | -------------------------------------- |
| Shared dependency versions | `<dependencyManagement>` in parent POM | `dependencies { constraints { ... } }` |
| Shared plugin config       | `<pluginManagement>` in parent POM     | Convention plugin body                 |
| Per-module apply           | `<parent>` in child POM                | `plugins { id("...") }`                |
| Conditional config         | `<profiles>`                           | Kotlin `if` / project properties       |
| Testable                   | No (POM is data)                       | Yes (buildSrc is compiled Kotlin)      |

---

### ⚠️ Common Misconceptions

| Misconception                                           | Reality                                                                           |
| ------------------------------------------------------- | --------------------------------------------------------------------------------- |
| `buildSrc` is for custom tasks only                     | It's for any reusable build logic: tasks, plugins, convention plugins, utilities  |
| Convention plugins replace `plugins { }` in subprojects | They _are applied_ via `plugins { }` - they apply _other_ plugins internally      |
| `buildSrc` changes are cheap                            | Any change in `buildSrc/` invalidates all configuration caches for the main build |
| Convention plugins must be all-or-nothing               | They should be small and composable - each one does one thing                     |

---

### 🚨 Failure Modes & Diagnosis

**`Plugin [id: 'my-company.java-conventions'] was not found`**

**Root Cause:** `buildSrc/build.gradle.kts` doesn't have `kotlin-dsl` plugin applied, so `.gradle.kts` files aren't compiled as precompiled script plugins.

**Fix:**

```kotlin
// buildSrc/build.gradle.kts
plugins {
    `kotlin-dsl`  // REQUIRED for precompiled script plugins
}
```

---

**Convention plugin change invalidates entire configuration cache**

**Root Cause:** `buildSrc/` changes always invalidate the cache.

**Fix:** Migrate `buildSrc/` to a composite build (`build-logic/`) to scope cache invalidation.

---

### 🔗 Related Keywords

**Prerequisites:** `Gradle Build Script`, `Gradle Tasks`, `Maven Multi-Module Project`

**Builds On This:** `Build Performance Optimization`, `Build Reproducibility`

**Related Patterns:** `Gradle Build Script`, `Gradle Tasks`, `Maven Multi-Module Project`

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ LOCATION     │ buildSrc/src/main/kotlin/*.gradle.kts     │
├──────────────┼───────────────────────────────────────────┤
│ APPLY        │ plugins { id("my-company.conventions") }  │
├──────────────┼───────────────────────────────────────────┤
│ PREREQUISITE │ buildSrc/build.gradle.kts: kotlin-dsl     │
├──────────────┼───────────────────────────────────────────┤
│ MAVEN EQUIV  │ Parent POM (but with full code power)     │
├──────────────┼───────────────────────────────────────────┤
│ ADVANCED     │ Composite build (build-logic/) avoids     │
│              │ full cache invalidation on changes        │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "Reusable build conventions as code"      │
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** Your team has 30 Gradle subprojects. You need to enforce that every subproject must generate a JaCoCo code coverage report and fail the build if coverage drops below 80%. Where would you put this logic, and what are the advantages of using a convention plugin versus configuring it in the root `build.gradle.kts` using `subprojects { }` or `allprojects { }` blocks?

**Q2.** Compare the Maven parent POM approach to Gradle convention plugins for managing shared build configuration across 20+ microservices. What can convention plugins do that parent POMs cannot? What does a Maven parent POM do that a convention plugin cannot (or requires more effort to replicate)?
