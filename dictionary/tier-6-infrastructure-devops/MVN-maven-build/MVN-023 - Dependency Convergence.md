---
version: 1
layout: default
title: "Dependency Convergence"
parent: "Maven & Build Tools"
grand_parent: "Technical Dictionary"
nav_order: 23
permalink: /maven-build/dependency-convergence/
id: MVN-017
category: Maven & Build Tools (Java)
difficulty: ★★★
depends_on: Transitive Dependencies, Dependency Exclusion, Maven Dependencies
used_by: Maven BOM (Bill of Materials), Maven Enforcer Plugin, Build Performance Optimization
related: Maven BOM (Bill of Materials), Dependency Exclusion, Transitive Dependencies
tags:
  - maven
  - build-tools
  - dependencies
  - java
  - deep-dive
---

# MVN-019 - Dependency Convergence

⚡ TL;DR - Dependency convergence means all transitive paths to the same artifact resolve to exactly the same version, eliminating version conflicts that cause runtime `NoSuchMethodError`, `ClassNotFoundException`, or subtle behavioural bugs.

| #1076           | Category: Maven & Build Tools (Java)                                                 | Difficulty: ★★★ |
| :-------------- | :----------------------------------------------------------------------------------- | :-------------- |
| **Depends on:** | Transitive Dependencies, Dependency Exclusion, Maven Dependencies                    |                 |
| **Used by:**    | Maven BOM (Bill of Materials), Maven Enforcer Plugin, Build Performance Optimization |                 |
| **Related:**    | Maven BOM (Bill of Materials), Dependency Exclusion, Transitive Dependencies         |                 |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
Your project depends on Library A (which requires Guava 30) and Library B (which requires Guava 28). Maven's nearest-wins strategy picks Guava 28 (declared first in dependency tree). Library A was compiled against Guava 30 and calls a method added in version 29. At runtime: `NoSuchMethodError: com.google.common.collect.ImmutableList.copyOf(...)`. The build succeeds; the application crashes in production.

**THE BREAKING POINT:**
Large Java projects can have hundreds of transitive dependencies, with the same artifact appearing at many different versions across different dependency paths. Without a mechanism to detect and enforce version alignment, builds silently carry these time-bombs.

**THE INVENTION MOMENT:**
The Maven Enforcer Plugin's `dependencyConvergence` rule fails the build if any artifact appears at more than one version in the dependency tree. This turns a silent runtime problem into a loud, early build failure - catching conflicts before code is shipped.

---

### 📘 Textbook Definition

**Dependency convergence** is the property of a Maven build where every transitive path to the same artifact (identified by groupId:artifactId) resolves to identical versions. When convergence is violated - two or more paths require different versions of the same artifact - Maven applies its nearest-wins resolution strategy, which silently selects one version and may break code compiled against the other. The Maven Enforcer Plugin can enforce convergence as a build rule, failing fast when conflicts are detected, and allowing developers to explicitly resolve them via dependency management overrides or exclusions.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
Ensure every library in your project tree agrees on exactly one version of each shared artifact - no silent version conflicts.

**One analogy:**

> Two flight crew members with different checklists for the same aircraft model. One says the fuel gauge is calibrated one way; the other says another way. Which one does the plane use at takeoff? Dependency convergence ensures everyone uses the same checklist - the same version - so there's no ambiguity.

**One insight:**
Maven's nearest-wins resolution is a tie-breaker, not a safety net. It never fails; it just silently picks a version. Convergence enforcement turns silent selection into explicit validation.

---

### 🔩 First Principles Explanation

**HOW MAVEN RESOLVES VERSION CONFLICTS:**

When the same artifact appears at multiple versions in the dependency graph, Maven uses **nearest-wins**: the version closest to your project root in the dependency tree wins.

```
Your project
├── Library A → Guava 30       (depth 1)
│   └── Guava 30               (depth 2 - selected!)
└── Library B → Spring → Guava 28  (depth 3 - loses)
```

**THE CONVERGENCE VIOLATION:**

```
Your project
├── Library A v1.0  →  commons-lang3:3.12
└── Library B v2.0  →  commons-lang3:3.9
```

Maven picks `3.12` (nearest wins, if A is declared first). Library B was compiled against `3.9`. If `3.9` removed or changed a method present in `3.12`, problems appear at runtime - not at compile time.

**ENFORCING CONVERGENCE:**

```xml
<!-- Enforcer plugin: fail build on version conflicts -->
<plugin>
  <groupId>org.apache.maven.plugins</groupId>
  <artifactId>maven-enforcer-plugin</artifactId>
  <executions>
    <execution>
      <id>enforce</id>
      <goals><goal>enforce</goal></goals>
      <configuration>
        <rules>
          <dependencyConvergence/>
        </rules>
      </configuration>
    </execution>
  </executions>
</plugin>
```

**RESOLUTION STRATEGIES:**

1. **Dependency management override** (preferred): declare the winning version in `<dependencyManagement>` explicitly
2. **Exclusion**: exclude the conflicting transitive dependency from a specific path
3. **BOM import**: import a BOM that aligns all versions for a framework stack

**THE TRADE-OFFS:**
**Gain:** Runtime errors caught at build time; explicit, documented version decisions; reproducible builds; team visibility into dependency conflicts.
**Cost:** Adds build-time overhead (full tree traversal); may require significant work to resolve existing violations in a legacy project; version pinning in `<dependencyManagement>` adds maintenance overhead as libraries evolve.

---

### 🧪 Thought Experiment

**SETUP:**
You add Spring Boot to an existing project that already uses Hibernate ORM 5.6 directly. Spring Boot 3.x manages Hibernate 6.x. Both paths pull in `byte-buddy` at different versions. Maven picks one. The enforcer fires.

**HOW DO YOU RESOLVE:**
Option 1 (override): add `<dependencyManagement>` pinning `byte-buddy` to the version compatible with both.
Option 2 (align): migrate your direct Hibernate dependency to match Spring Boot's managed version, so your `<dependencyManagement>` is empty for these.
Option 3 (exclude): exclude `byte-buddy` from your direct Hibernate dependency and let Spring Boot's version win.

**THE LESSON:**
Convergence violations are information: they tell you two dependencies disagree on a shared library. The fix requires understanding _why_ they disagree - often, upgrading your direct dependency resolves it naturally.

---

### 🧠 Mental Model / Analogy

> Dependency convergence is like establishing a single canonical API spec across a distributed team. Without a canonical spec, Team A builds against v2.1 and Team B builds against v1.9. The integration fails at runtime. The convergence rule is like requiring everyone to declare which spec version they need - and failing the sprint review if there's a conflict.

---

### 📶 Gradual Depth - Four Levels

**Level 1:** The same library appears twice in your project at different versions. That's a conflict. Convergence means there's only one version.

**Level 2:** Maven's `mvn dependency:tree` shows all transitive dependencies and their resolved versions. The enforcer's `dependencyConvergence` rule fails the build if any artifact has more than one version across paths.

**Level 3:** Resolution: use `<dependencyManagement>` to pin the winning version for the whole project. BOMs are collections of such pins - importing a BOM (e.g., `spring-boot-dependencies`) instantly aligns dozens of library versions.

**Level 4:** In multi-module projects, the root `pom.xml` `<dependencyManagement>` section governs all modules. But if module A imports BOM X and module B imports BOM Y, and both BOMs declare different versions of the same artifact, convergence violations reappear. Solution: import BOMs in the root POM; use `<dependencyManagement>` overrides only there.

---

### ⚙️ How It Works (Mechanism)

```
mvn dependency:tree -Dverbose
[INFO] com.example:my-app:jar:1.0
[INFO] +- com.libraryA:libraryA:jar:1.0:compile
[INFO] |  \- com.google.guava:guava:jar:30.0-jre:compile
[INFO] \- com.libraryB:libraryB:jar:2.0:compile
[INFO]    \- com.google.guava:guava:jar:28.0-jre:compile (omitted for conflict with 30.0-jre)

# Enforcer output:
[ERROR] Failed to execute goal org.apache.maven.plugins:maven-enforcer-plugin:...
Rule 0: org.apache.maven.plugins.enforcer.DependencyConvergence failed with message:
  Dependency convergence error for com.google.guava:guava:30.0-jre paths to dependency are:
  +-com.example:my-app:1.0
    +-com.libraryA:libraryA:1.0
      +-com.google.guava:guava:30.0-jre
  and
  +-com.example:my-app:1.0
    +-com.libraryB:libraryB:2.0
      +-com.google.guava:guava:28.0-jre
```

---

### 💻 Code Example

**Fix via `<dependencyManagement>`:**

```xml
<dependencyManagement>
  <dependencies>
    <!-- Pin the winning Guava version for the entire project -->
    <dependency>
      <groupId>com.google.guava</groupId>
      <artifactId>guava</artifactId>
      <version>30.0-jre</version>  <!-- both libraries will get this -->
    </dependency>
  </dependencies>
</dependencyManagement>

<build>
  <plugins>
    <plugin>
      <groupId>org.apache.maven.plugins</groupId>
      <artifactId>maven-enforcer-plugin</artifactId>
      <version>3.4.1</version>
      <executions>
        <execution>
          <id>enforce-convergence</id>
          <goals><goal>enforce</goal></goals>
          <configuration>
            <rules>
              <dependencyConvergence/>
            </rules>
          </configuration>
        </execution>
      </executions>
    </plugin>
  </plugins>
</build>
```

---

### ⚖️ Comparison Table

| Approach                         | Visibility | Auto-Resolves   | Explicit              | Recommended           |
| -------------------------------- | ---------- | --------------- | --------------------- | --------------------- |
| Maven nearest-wins (default)     | Low        | Yes (silently)  | No                    | No (silent)           |
| `dependencyConvergence` enforcer | High       | No (fails)      | Yes (you fix)         | Yes                   |
| BOM import                       | Medium     | Yes (by design) | Yes (BOM is explicit) | Yes (for frameworks)  |
| Manual `<dependencyManagement>`  | High       | Yes (pin wins)  | Yes                   | Yes (for custom pins) |

---

### ⚠️ Common Misconceptions

| Misconception                            | Reality                                                                                        |
| ---------------------------------------- | ---------------------------------------------------------------------------------------------- |
| Maven always picks the newest version    | Maven picks the _nearest_ (fewest hops from root), not the newest                              |
| Convergence is enforced by default       | It requires explicit Maven Enforcer Plugin configuration                                       |
| Excluding a dependency fixes convergence | Exclusion removes a path; the other path's version may still be wrong                          |
| BOMs guarantee convergence               | BOMs align versions within a framework stack; external libs outside the BOM can still conflict |

---

### 🚨 Failure Modes & Diagnosis

**`NoSuchMethodError` at runtime after build passes**

**Symptom:** Build succeeds, tests pass, but production throws `NoSuchMethodError` or `ClassNotFoundException`.

**Root Cause:** Two versions of same artifact; wrong version was selected at runtime; enforcer not enabled.

**Diagnosis:**

```bash
mvn dependency:tree -Dverbose | grep "(omitted for conflict"
```

**Fix:** Enable enforcer `dependencyConvergence` + pin winning version in `<dependencyManagement>`.

---

### 🔗 Related Keywords

**Prerequisites:** `Transitive Dependencies`, `Dependency Exclusion`, `Maven Dependencies`

**Builds On This:** `Maven BOM (Bill of Materials)`, `Maven Enforcer Plugin`

**Related Patterns:** `Maven BOM (Bill of Materials)`, `Dependency Exclusion`, `Transitive Dependencies`

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ WHAT IT IS   │ All paths to same artifact use same ver. │
├──────────────┼───────────────────────────────────────────┤
│ MAVEN DEFAULT│ nearest-wins (silent - no convergence)   │
├──────────────┼───────────────────────────────────────────┤
│ ENFORCE IT   │ maven-enforcer-plugin dependencyConvergence│
├──────────────┼───────────────────────────────────────────┤
│ DIAGNOSE     │ mvn dependency:tree -Dverbose             │
├──────────────┼───────────────────────────────────────────┤
│ FIX          │ <dependencyManagement> pin + BOM import   │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "One version per artifact, enforced"     │
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** Your enforcer reports a conflict: `jackson-databind:2.14` vs `jackson-databind:2.13`. Library A needs `2.14` (uses a new API); Library B needs `2.13` (works with both). Which version do you pin in `<dependencyManagement>`, and why? What would happen if you pinned `2.13` instead?

**Q2.** You import `spring-boot-dependencies` BOM. The BOM manages `jackson-databind:2.14`. You also have a direct dependency on a legacy library that pulled in `jackson-databind:2.12` transitively. Does importing the BOM resolve the convergence violation? Explain the mechanism.
