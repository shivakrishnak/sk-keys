---
layout: default
title: "Maven BOM (Bill of Materials)"
parent: "Maven & Build Tools"
grand_parent: "Technical Dictionary"
nav_order: 17
permalink: /maven-build/maven-bom-bill-of-materials/
id: MVN-017
category: Maven & Build Tools (Java)
difficulty: ★★★
depends_on: Dependency Convergence, Maven Dependencies, pom.xml, Maven Multi-Module Project
used_by: Spring Core, Maven Release Plugin, Build Performance Optimization
related: Dependency Convergence, Transitive Dependencies, Maven Profiles
tags:
  - maven
  - build-tools
  - dependencies
  - bom
  - java
  - deep-dive
---

# MVN-017 - Maven BOM (Bill of Materials)

⚡ TL;DR - A BOM is a special POM with `<packaging>pom</packaging>` that contains only `<dependencyManagement>` entries. Importing a BOM into your project pins compatible versions for an entire ecosystem (e.g., Spring Boot) in one line - no per-library version juggling required.

| #1077           | Category: Maven & Build Tools (Java)                                            | Difficulty: ★★★ |
| :-------------- | :------------------------------------------------------------------------------ | :-------------- |
| **Depends on:** | Dependency Convergence, Maven Dependencies, pom.xml, Maven Multi-Module Project |                 |
| **Used by:**    | Spring Core, Maven Release Plugin, Build Performance Optimization               |                 |
| **Related:**    | Dependency Convergence, Transitive Dependencies, Maven Profiles                 |                 |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
You add Spring Boot to your project and manually specify `spring-core:6.1.0`, `spring-web:6.1.0`, `spring-context:6.1.0`, `jackson-databind:2.16.1`, `micrometer-core:1.12.0` … and 50 more compatible library versions. A typo - `spring-core:6.0.0` while everything else is `6.1.0` - causes a runtime failure. You spend hours debugging a version mismatch.

**THE BREAKING POINT:**
Modern Java frameworks involve dozens of co-versioned artifacts. Tracking which version of each library is compatible with which version of the framework is a full-time job - and it changes with every framework release.

**THE INVENTION MOMENT:**
BOM (Bill of Materials) packages a curated, tested set of `<dependencyManagement>` entries into a single importable POM. One import line replaces 50 manual version declarations - and the framework team guarantees the versions are compatible with each other.

---

### 📘 Textbook Definition

A **Maven BOM (Bill of Materials)** is a POM file with `<packaging>pom</packaging>` containing a `<dependencyManagement>` section that defines recommended versions for a set of related artifacts. Consumers import the BOM using `<scope>import</scope>` inside their own `<dependencyManagement>` block. The effect: every artifact listed in the BOM is version-pinned in the consumer's project - without requiring explicit `<version>` in individual `<dependency>` declarations. BOMs are the primary mechanism used by frameworks like Spring Boot, Quarkus, and Micronaut to guarantee version compatibility across their ecosystem.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
Import a BOM = instantly pin dozens of curated, compatible library versions from a framework's tested release.

**One analogy:**

> Ordering a pre-configured tech stack from a menu versus choosing every component individually. The BOM is the combo meal: someone else verified all the parts work together - you just order the meal number.

**One insight:**
BOMs do not add dependencies to your project. They only set _default versions_ for dependencies you choose to add. You still opt in to each dependency - but the version is already chosen for you.

---

### 🔩 First Principles Explanation

**HOW A BOM IS STRUCTURED:**

```xml
<!-- spring-boot-dependencies BOM (simplified) -->
<project>
  <groupId>org.springframework.boot</groupId>
  <artifactId>spring-boot-dependencies</artifactId>
  <version>3.2.0</version>
  <packaging>pom</packaging>

  <dependencyManagement>
    <dependencies>
      <dependency>
        <groupId>org.springframework</groupId>
        <artifactId>spring-core</artifactId>
        <version>6.1.1</version>
      </dependency>
      <dependency>
        <groupId>com.fasterxml.jackson.core</groupId>
        <artifactId>jackson-databind</artifactId>
        <version>2.16.1</version>
      </dependency>
      <!-- ~300 more pinned entries... -->
    </dependencies>
  </dependencyManagement>
</project>
```

**HOW CONSUMERS IMPORT IT:**

```xml
<dependencyManagement>
  <dependencies>
    <!-- BOM import: pulls in all pinned versions -->
    <dependency>
      <groupId>org.springframework.boot</groupId>
      <artifactId>spring-boot-dependencies</artifactId>
      <version>3.2.0</version>
      <type>pom</type>
      <scope>import</scope>
    </dependency>
  </dependencies>
</dependencyManagement>

<!-- Now declare dependencies WITHOUT version: BOM provides it -->
<dependencies>
  <dependency>
    <groupId>org.springframework</groupId>
    <artifactId>spring-core</artifactId>
    <!-- no <version> needed - BOM pins 6.1.1 -->
  </dependency>
</dependencies>
```

**OVERRIDE MECHANISM:**
Entries in your local `<dependencyManagement>` take precedence over BOM entries. You can override a specific BOM-pinned version:

```xml
<dependencyManagement>
  <dependencies>
    <!-- BOM first -->
    <dependency>
      <groupId>org.springframework.boot</groupId>
      <artifactId>spring-boot-dependencies</artifactId>
      <version>3.2.0</version>
      <type>pom</type>
      <scope>import</scope>
    </dependency>
    <!-- Override a specific version from the BOM -->
    <dependency>
      <groupId>com.fasterxml.jackson.core</groupId>
      <artifactId>jackson-databind</artifactId>
      <version>2.15.0</version>  <!-- overrides BOM's 2.16.1 -->
    </dependency>
  </dependencies>
</dependencyManagement>
```

**THE TRADE-OFFS:**
**Gain:** Eliminates per-dependency version management for entire ecosystems; guarantees tested compatibility; dramatically simplifies upgrades (change one BOM version, 300+ libs follow); enables convergence enforcement by aligning transitive versions.
**Cost:** BOM versioning lag - the BOM may pin older versions of libs you need newer; override discipline required to avoid hidden divergence; implicit version sourcing can confuse new developers unfamiliar with BOM pattern; multiple conflicting BOMs require careful ordering.

---

### 🧪 Thought Experiment

**SETUP:**
You import both `spring-boot-dependencies:3.2.0` and `quarkus-bom:3.5.0`. Both BOMs contain `io.netty:netty-all` but at different versions. Maven resolves `<dependencyManagement>` in declaration order - the first BOM's version wins for `netty-all`.

**QUESTIONS:**

1. Which version of Netty does your Quarkus code get?
2. How can you explicitly pin the Quarkus-compatible version after both BOMs are imported?
3. What happens if Quarkus and Spring Boot share a web server and they use incompatible Netty versions?

**THE LESSON:**
Multiple BOMs in the same project create their own convergence challenge. Import order matters, and explicit `<dependencyManagement>` overrides after the BOM imports are the safety valve.

---

### 🧠 Mental Model / Analogy

> A BOM is like a compatibility matrix published by a car manufacturer: "Engine model X is certified to work with transmission Y, suspension Z, and ECU firmware version 4.1.2. Use the parts list - don't mix and match randomly." Your job isn't to know which version of each part is compatible; your job is to choose the right manufacturer version (BOM version) and trust the matrix.

---

### 📶 Gradual Depth - Four Levels

**Level 1:** A BOM is a file from a framework team that says "these library versions all work together." You import it to avoid version errors.

**Level 2:** The BOM is a `<packaging>pom</packaging>` POM with only `<dependencyManagement>`. Importing it with `<scope>import</scope>` copies its `<dependencyManagement>` entries into yours. You can then declare dependencies without `<version>`.

**Level 3:** Your own `<dependencyManagement>` takes precedence over imported BOM entries (first-declaration wins for multiple imports). Spring Boot's Maven plugin parent POM uses `spring-boot-dependencies` BOM implicitly - you don't need to import it separately when using the parent.

**Level 4:** Creating your own internal BOM for an enterprise multi-module project: define a `<packaging>pom</packaging>` POM containing `<dependencyManagement>` for all internal and third-party libraries, then have all project modules import it. Combine with the Maven Enforcer Plugin's `dependencyConvergence` rule and CI validation to maintain alignment across 100+ modules.

---

### ⚙️ How It Works (Mechanism)

**Maven resolution sequence:**

1. Collect `<dependencyManagement>` entries from:
   - Current POM
   - Imported BOMs (in declaration order)
   - Parent POM chain
2. When resolving a `<dependency>` with no `<version>`, look up in the merged `<dependencyManagement>`
3. First match wins
4. If no match: Maven requires a version to be declared or inherited - build fails

**Spring Boot parent vs. BOM import:**

```xml
<!-- Option A: parent (includes BOM + plugin config) -->
<parent>
  <groupId>org.springframework.boot</groupId>
  <artifactId>spring-boot-starter-parent</artifactId>
  <version>3.2.0</version>
</parent>

<!-- Option B: BOM-only (use when you have your own parent POM) -->
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
```

---

### 💻 Code Example

**Complete multi-ecosystem project POM:**

```xml
<project>
  <groupId>com.example</groupId>
  <artifactId>my-app</artifactId>
  <version>1.0.0</version>
  <packaging>jar</packaging>

  <dependencyManagement>
    <dependencies>
      <!-- Spring Boot ecosystem BOM -->
      <dependency>
        <groupId>org.springframework.boot</groupId>
        <artifactId>spring-boot-dependencies</artifactId>
        <version>3.2.0</version>
        <type>pom</type>
        <scope>import</scope>
      </dependency>
      <!-- Testcontainers BOM -->
      <dependency>
        <groupId>org.testcontainers</groupId>
        <artifactId>testcontainers-bom</artifactId>
        <version>1.19.3</version>
        <type>pom</type>
        <scope>import</scope>
      </dependency>
      <!-- Override: use older Logback for compliance -->
      <dependency>
        <groupId>ch.qos.logback</groupId>
        <artifactId>logback-classic</artifactId>
        <version>1.4.11</version>
      </dependency>
    </dependencies>
  </dependencyManagement>

  <dependencies>
    <!-- No versions needed for Spring or Testcontainers artifacts -->
    <dependency>
      <groupId>org.springframework.boot</groupId>
      <artifactId>spring-boot-starter-web</artifactId>
    </dependency>
    <dependency>
      <groupId>org.testcontainers</groupId>
      <artifactId>postgresql</artifactId>
      <scope>test</scope>
    </dependency>
  </dependencies>
</project>
```

---

### ⚖️ Comparison Table

| Approach                   | Who Picks Versions          | Version Conflicts | Upgrade Path           |
| -------------------------- | --------------------------- | ----------------- | ---------------------- |
| Manual `<version>` per dep | Developer                   | High risk         | Per-dependency edits   |
| Parent POM inheritance     | Parent POM author           | Medium            | Change parent version  |
| BOM import                 | BOM author (framework team) | Low               | Change one BOM version |
| Internal enterprise BOM    | Platform team               | Low               | Platform team controls |

---

### ⚠️ Common Misconceptions

| Misconception                           | Reality                                                                                                      |
| --------------------------------------- | ------------------------------------------------------------------------------------------------------------ |
| BOM automatically adds dependencies     | BOM only pins versions; you must explicitly declare `<dependency>`                                           |
| First BOM import always wins            | First _`<dependencyManagement>` entry_ for an artifact wins; explicit entries before BOM import override BOM |
| Spring Boot parent IS the BOM           | Spring Boot parent includes the BOM + plugin management; you can use just the BOM without the parent         |
| BOM version locks child module versions | BOM only affects artifacts in the BOM's list; custom internal libs need separate management                  |

---

### 🚨 Failure Modes & Diagnosis

**Missing `<type>pom</type>` or `<scope>import</scope>`**

**Symptom:** BOM import appears in `pom.xml` but dependencies still require explicit versions.

**Root Cause:** The import only works with both `<type>pom</type>` AND `<scope>import</scope>` present.

**Fix:**

```xml
<dependency>
  <type>pom</type>        <!-- REQUIRED -->
  <scope>import</scope>   <!-- REQUIRED -->
</dependency>
```

---

### 🔗 Related Keywords

**Prerequisites:** `Dependency Convergence`, `Maven Dependencies`, `pom.xml`

**Builds On This:** `Maven Multi-Module Project`, `Maven Release Plugin`

**Related Patterns:** `Dependency Convergence`, `Transitive Dependencies`, `Maven Profiles`

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ WHAT IT IS   │ POM that pins compatible lib versions     │
├──────────────┼───────────────────────────────────────────┤
│ IMPORT SYNTAX│ <type>pom</type><scope>import</scope>     │
├──────────────┼───────────────────────────────────────────┤
│ EFFECT       │ Copies <dependencyManagement> into yours  │
├──────────────┼───────────────────────────────────────────┤
│ OVERRIDE     │ Declare entry before/after BOM (order!)   │
├──────────────┼───────────────────────────────────────────┤
│ NO PARENT?   │ Use spring-boot-dependencies BOM directly │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "Curated version set - import, don't pin" │
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** Your project imports `spring-boot-dependencies:3.2.0`. You also have a direct `<dependency>` on `commons-lang3` without a version. The Spring BOM pins `commons-lang3:3.12.0`. A colleague adds a second BOM that pins `commons-lang3:3.11.0`. Which version wins, and what controls the outcome?

**Q2.** Your enterprise has 30 microservices. Each uses Spring Boot but at slightly different patch versions (3.2.0, 3.2.1, 3.2.2). What would be the benefit and the cost of maintaining a single internal enterprise BOM that all 30 services import for third-party library versions?
