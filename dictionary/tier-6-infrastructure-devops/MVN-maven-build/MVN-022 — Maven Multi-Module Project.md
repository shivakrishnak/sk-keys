---
layout: default
title: "Maven Multi-Module Project"
parent: "Maven & Build Tools (Java)"
grand_parent: "Technical Dictionary"
nav_order: 22
permalink: /maven-build/maven-multi-module-project/
id: MVN-022
category: Maven & Build Tools (Java)
difficulty: ★★★
depends_on: pom.xml, Maven Lifecycle, Maven BOM (Bill of Materials), Maven Profiles
used_by: Maven Release Plugin, Build Performance Optimization, Dependency Convergence
related: Maven BOM (Bill of Materials), Maven Profiles, Build Performance Optimization
tags:
  - maven
  - build-tools
  - multi-module
  - java
  - deep-dive
---

# MVN-022 — Maven Multi-Module Project

⚡ TL;DR — A Maven multi-module project groups related submodules under a single root POM (`<packaging>pom</packaging>`), enabling unified dependency management, single-command builds, ordered module compilation, and shared configuration — essential for large Java codebases split into coherent layers.

| #1082           | Category: Maven & Build Tools (Java)                                          | Difficulty: ★★★ |
| :-------------- | :---------------------------------------------------------------------------- | :-------------- |
| **Depends on:** | pom.xml, Maven Lifecycle, Maven BOM (Bill of Materials), Maven Profiles       |                 |
| **Used by:**    | Maven Release Plugin, Build Performance Optimization, Dependency Convergence  |                 |
| **Related:**    | Maven BOM (Bill of Materials), Maven Profiles, Build Performance Optimization |                 |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
Your application has a `domain` layer, an `api` layer, and a `web` layer. Three separate Maven projects. To build and test the full application, you must manually build each project in the right order, manage version alignment between them, and run three separate `mvn install` commands. A shared utility change requires touching three projects. Refactoring across layers is painful.

**THE BREAKING POINT:**
As Java projects grow — microservices sharing common contracts, monorepos with multiple services, layered enterprise apps — the coordination cost of independent Maven projects scales linearly. One logical application becomes ten separate build operations with brittle version glue between them.

**THE INVENTION MOMENT:**
The Maven multi-module structure: one root POM declares `<modules>` listing sub-projects. A single `mvn build` from the root builds all modules in dependency order, with shared `<dependencyManagement>` and `<pluginManagement>` in the root POM applying across all modules automatically.

---

### 📘 Textbook Definition

A **Maven multi-module project** consists of a root (aggregator) POM with `<packaging>pom</packaging>` that declares child modules via `<modules>`. Each child module has its own `pom.xml` that may declare the root as `<parent>`. The root POM serves two roles: **aggregator** (lists modules to build in one command) and **parent** (provides shared `<dependencyManagement>`, `<pluginManagement>`, and `<properties>` to all children via inheritance). Maven resolves the module build order using the dependency graph: a module that depends on another module is built after it, regardless of declaration order.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
One root POM orchestrates building multiple submodules in dependency order with shared configuration.

**One analogy:**

> A software monorepo with a build system that knows how to build each component in the right order and apply the same build rules across all components from a single root configuration — like Gradle's root `settings.gradle` but for Maven.

**One insight:**
The aggregator role (what to build) and the parent role (what config to inherit) are separate concerns. The root POM typically fills both roles, but they can be split into separate POMs for more flexibility.

---

### 🔩 First Principles Explanation

**STRUCTURE:**

```
my-project/                          ← root aggregator POM
  pom.xml                            ← <packaging>pom</packaging>
  domain/
    pom.xml                          ← <parent> points to root
    src/main/java/...
  api/
    pom.xml                          ← depends on domain module
    src/main/java/...
  web/
    pom.xml                          ← depends on api module
    src/main/java/...
  infra/
    pom.xml                          ← shared infrastructure
    src/main/java/...
```

**ROOT POM ROLES:**

```xml
<project>
  <groupId>com.example</groupId>
  <artifactId>my-project</artifactId>
  <version>1.0.0-SNAPSHOT</version>
  <packaging>pom</packaging>          <!-- aggregator: must be pom -->

  <!-- Aggregator role: which modules to build -->
  <modules>
    <module>domain</module>
    <module>api</module>
    <module>web</module>
    <module>infra</module>
  </modules>

  <!-- Parent role: shared dependency versions -->
  <dependencyManagement>
    <dependencies>
      <dependency>
        <groupId>org.springframework.boot</groupId>
        <artifactId>spring-boot-dependencies</artifactId>
        <version>3.2.0</version>
        <type>pom</type>
        <scope>import</scope>
      </dependency>
    </dependencies>
  </dependencyManagement>

  <!-- Shared plugin config for all modules -->
  <build>
    <pluginManagement>
      <plugins>
        <plugin>
          <groupId>org.apache.maven.plugins</groupId>
          <artifactId>maven-compiler-plugin</artifactId>
          <version>3.12.0</version>
          <configuration>
            <source>17</source>
            <target>17</target>
          </configuration>
        </plugin>
      </plugins>
    </pluginManagement>
  </build>
</project>
```

**CHILD MODULE POM:**

```xml
<project>
  <parent>
    <groupId>com.example</groupId>
    <artifactId>my-project</artifactId>
    <version>1.0.0-SNAPSHOT</version>
    <relativePath>../pom.xml</relativePath>  <!-- explicit is safer -->
  </parent>

  <artifactId>api</artifactId>       <!-- groupId + version inherited from parent -->

  <dependencies>
    <!-- Cross-module dependency: api depends on domain -->
    <dependency>
      <groupId>com.example</groupId>
      <artifactId>domain</artifactId>
      <version>${project.version}</version>   <!-- inherit version from parent -->
    </dependency>
  </dependencies>
</project>
```

**BUILD ORDER RESOLUTION:**
Maven analyses the dependency graph (`api → domain`, `web → api → domain`) and builds in topological order: `domain` → `api` → `web`. Module declaration order in `<modules>` does not control build order — dependency relationships do.

**THE TRADE-OFFS:**
**Gain:** Single `mvn install` from root builds everything in order; shared config eliminates duplication; inter-module changes (e.g., interface contract in `domain`) are validated immediately; reactor build can skip unchanged modules (with Incremental Build support).
**Cost:** Root POM becomes a critical shared file with merge contention; partial builds (building one module) require understanding of module dependencies; large multi-module projects can have long clean build times; version management (bumping all modules simultaneously) requires discipline or tooling.

---

### 🧪 Thought Experiment

**SETUP:**
You have a 50-module Maven project. A developer changes only `infra` module's logging utility. The full build takes 20 minutes. Running `mvn install` from root rebuilds all 50 modules.

**APPROACHES:**

1. Build only the changed module: `cd infra && mvn install` — but downstream modules aren't retested
2. Use `--also-make-dependents` (`-amd`): `mvn install -pl infra -amd` — builds `infra` + all modules that depend on it
3. Use Maven's incremental build (experimental): only rebuild modules with changed sources

**THE LESSON:**
`-pl` (project list) and `-am`/`-amd` reactor flags are the key to efficient partial builds in large multi-module projects.

---

### 🧠 Mental Model / Analogy

> A multi-module Maven project is like a factory assembly line. The root POM is the factory manager who knows all the stations (modules) and the order work flows between them. Raw materials (no-dep modules) are processed first; each subsequent station adds value using the output of the previous one. The manager issues one work order (`mvn install`) and each station starts as soon as its inputs are ready.

---

### 📶 Gradual Depth — Four Levels

**Level 1:** You split your big project into folders (`domain/`, `api/`, `web/`). Each has its own `pom.xml`. The root `pom.xml` lists all folders as `<modules>`. Run `mvn install` in the root — all modules build in order.

**Level 2:** The root POM is both an aggregator (lists modules) and a parent (provides shared config). Child POMs declare `<parent>` to inherit `<dependencyManagement>`, `<pluginManagement>`, and `<properties>`.

**Level 3:** Maven's reactor is the engine that resolves build order from inter-module `<dependency>` declarations. `mvn install -pl api -am` builds only `api` and its prerequisites. `mvn install -pl api -amd` builds `api` and everything that depends on it.

**Level 4:** Separate aggregator and parent POM pattern: a root `aggregator` POM lists modules (aggregator role); a separate `parent` POM defines shared config (parent role). Modules inherit from `parent` but aren't direct children of `aggregator`. This allows modules to opt in/out of the parent hierarchy independently. Common in large enterprises where the same parent POM is shared across different aggregator projects.

---

### ⚙️ How It Works (Mechanism)

```bash
# Build all modules in correct order from root
mvn clean install

# Build specific module and its dependencies
mvn install -pl web -am

# Build module and everything that depends on it (downstream)
mvn install -pl domain -amd

# Skip a specific module
mvn install -pl '!infra'

# Resume from a specific module after a failure
mvn install --resume-from api

# List modules in build order
mvn validate --also-make -Dverbose
```

---

### 💻 Code Example

**`-pl` / `-am` / `-amd` flags in practice:**

```bash
# Project structure:
# root → domain → api → web
#                     → mobile-api

# Build only domain:
mvn install -pl domain

# Build api and all its prerequisites (domain):
mvn install -pl api -am

# Build domain AND everything that uses it (api, web, mobile-api):
mvn install -pl domain -amd

# Build api and web together, with prerequisites:
mvn install -pl api,web -am

# Run tests only for web module
mvn test -pl web

# Skip tests for everything except web
mvn install -DskipTests -pl '!web' && mvn test -pl web
```

---

### ⚖️ Comparison Table

| Build Target           | Command                            | Scope                                       |
| ---------------------- | ---------------------------------- | ------------------------------------------- |
| All modules            | `mvn install` (from root)          | Everything in order                         |
| One module only        | `mvn install -pl module`           | That module only (may fail if deps missing) |
| Module + prerequisites | `mvn install -pl module -am`       | Module + upstream                           |
| Module + dependents    | `mvn install -pl module -amd`      | Module + downstream                         |
| Resume after failure   | `mvn install --resume-from module` | From that module forward                    |

---

### ⚠️ Common Misconceptions

| Misconception                                    | Reality                                                                           |
| ------------------------------------------------ | --------------------------------------------------------------------------------- |
| Module order in `<modules>` controls build order | Dependency graph controls order; `<modules>` listing order is a hint only         |
| The parent POM must be the aggregator            | They can be separate POMs; parent and aggregator roles are independent            |
| `${project.version}` works for inter-module deps | It works at build time (same session); not after `install` if versions differ     |
| Building one module from root is always safe     | If downstream modules cached stale versions, `-amd` may be needed for consistency |

---

### 🚨 Failure Modes & Diagnosis

**"Could not find artifact" for a sibling module**

**Root Cause:** Running `mvn install` only in a child module (`cd api && mvn install`) without building `domain` first. `domain` isn't in local `.m2`.

**Fix:**

```bash
# From root, build api and all its prerequisites
cd ..  # back to root
mvn install -pl api -am
```

---

**Root POM `<version>` doesn't match child `<parent>` version**

**Root Cause:** Root POM version was bumped but child POM's `<parent><version>` wasn't updated.

**Fix:** Use `mvn versions:update-child-modules` to align all child `<parent>` versions with root.

---

### 🔗 Related Keywords

**Prerequisites:** `pom.xml`, `Maven Lifecycle`, `Maven BOM (Bill of Materials)`, `Maven Profiles`

**Builds On This:** `Maven Release Plugin`, `Build Performance Optimization`

**Related Patterns:** `Maven BOM (Bill of Materials)`, `Maven Profiles`, `Build Performance Optimization`

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ ROOT POM     │ <packaging>pom</packaging> + <modules>    │
├──────────────┼───────────────────────────────────────────┤
│ CHILD POM    │ Declares <parent> to inherit config       │
├──────────────┼───────────────────────────────────────────┤
│ BUILD ORDER  │ Dependency graph (not <modules> order)    │
├──────────────┼───────────────────────────────────────────┤
│ -pl          │ Project list (selective build)            │
├──────────────┼───────────────────────────────────────────┤
│ -am / -amd   │ Also Make (upstream) / Dependents (down)  │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "One root, many modules, ordered build"   │
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** You have a 10-module Maven project where `module-A` depends on `module-B`. You run `mvn install -pl module-A`. Does Maven automatically build `module-B` first? What flag do you add to make it do so?

**Q2.** Your root POM contains `<dependencyManagement>` with a Spring Boot BOM import. A child module declares `spring-boot-starter-web` without a version. Explain how Maven resolves the version from the root POM's `<dependencyManagement>` when building only that child module with `-pl`.
