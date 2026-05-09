---
version: 1
layout: default
title: "Maven Enforcer Plugin"
parent: "Maven & Build Tools"
grand_parent: "Technical Dictionary"
nav_order: 32
permalink: /maven-build/maven-enforcer-plugin/
id: MVN-032
category: Maven & Build Tools (Java)
difficulty: ★★★
depends_on: Maven Plugins, Dependency Convergence, Maven Multi-Module Project, SNAPSHOT vs RELEASE
used_by: Build Reproducibility, OWASP Dependency Check, Build Performance Optimization
related: Dependency Convergence, SNAPSHOT vs RELEASE, Build Reproducibility
tags:
  - maven
  - build-tools
  - enforcer
  - quality
  - java
  - deep-dive
---

# MVN-032 - Maven Enforcer Plugin

⚡ TL;DR - The Maven Enforcer Plugin defines build quality gates as rules in `pom.xml`: minimum JDK version, no SNAPSHOT dependencies in releases, dependency convergence, banned dependencies, required OS. Rules fail the build fast before bad artifacts are produced or deployed.

| #1092           | Category: Maven & Build Tools (Java)                                                   | Difficulty: ★★★ |
| :-------------- | :------------------------------------------------------------------------------------- | :-------------- |
| **Depends on:** | Maven Plugins, Dependency Convergence, Maven Multi-Module Project, SNAPSHOT vs RELEASE |                 |
| **Used by:**    | Build Reproducibility, OWASP Dependency Check, Build Performance Optimization          |                 |
| **Related:**    | Dependency Convergence, SNAPSHOT vs RELEASE, Build Reproducibility                     |                 |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
A developer with Java 8 builds a project that requires Java 17 - the build compiles with degraded bytecode but fails at runtime on the server. A SNAPSHOT dependency slips into a release artifact. A banned transitive dependency (GPL licence) appears in your commercial project. These violations are discovered in production, not in the build pipeline.

**THE BREAKING POINT:**
Build quality gates scattered across wikis, code review checklists, and institutional knowledge are unenforced. The build system itself should enforce the rules - not humans manually checking.

**THE INVENTION MOMENT:**
The Maven Enforcer Plugin provides a `enforce` goal with a library of built-in rules and an extension point for custom rules. Configured in `pom.xml`, rules run during the `validate` or `verify` phase - before compilation, packaging, or deployment - failing the build immediately on violation.

---

### 📘 Textbook Definition

The **Maven Enforcer Plugin** (`maven-enforcer-plugin`) is a Maven plugin that runs configurable validation rules during the build lifecycle. Built-in rules cover: environment constraints (`requireJavaVersion`, `requireMavenVersion`, `requireOS`), dependency constraints (`dependencyConvergence`, `bannedDependencies`, `requireReleaseDeps`, `requireUpperBoundDeps`), project constraints (`requireProperty`, `requireFiles`), and custom rule support via the `EnforceRule` interface. The plugin binds to the `validate` phase by default (earliest in the lifecycle), ensuring violations are caught before any compilation or test execution. Multiple `<execution>` blocks can enforce different rules at different lifecycle phases.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
Enforcer Plugin = build-time assertions: configure your non-negotiable rules in `pom.xml` and fail fast if violated.

**One analogy:**

> Airport security gates: you can't board the plane (deploy the artifact) without passing each check. Enforcer rules are the gates - they run automatically on every build, every developer, every CI run, without any manual intervention.

**One insight:**
The Enforcer Plugin shifts quality checks left - from production discovery to build time. Rules documented in `pom.xml` are visible, version-controlled, and automated - infinitely more reliable than documentation or code review.

---

### 🔩 First Principles Explanation

**PLUGIN STRUCTURE:**

```xml
<plugin>
  <groupId>org.apache.maven.plugins</groupId>
  <artifactId>maven-enforcer-plugin</artifactId>
  <version>3.4.1</version>
  <executions>
    <execution>
      <id>enforce-rules</id>
      <phase>validate</phase>  <!-- run first, before compile -->
      <goals><goal>enforce</goal></goals>
      <configuration>
        <rules>
          <!-- rules go here -->
        </rules>
        <fail>true</fail>  <!-- fail build on violation (default) -->
      </configuration>
    </execution>
  </executions>
</plugin>
```

**BUILT-IN RULES OVERVIEW:**

```xml
<!-- Minimum Java version -->
<requireJavaVersion>
  <version>[17,)</version>  <!-- at least Java 17 -->
</requireJavaVersion>

<!-- Minimum Maven version -->
<requireMavenVersion>
  <version>[3.9,)</version>
</requireMavenVersion>

<!-- All dep paths resolve to same version -->
<dependencyConvergence/>

<!-- No SNAPSHOT dependencies in release builds -->
<requireReleaseDeps>
  <failWhenParentIsSnapshot>true</failWhenParentIsSnapshot>
</requireReleaseDeps>

<!-- Ban specific dependencies (security, licence, legacy) -->
<bannedDependencies>
  <excludes>
    <exclude>commons-logging:commons-logging</exclude>
    <exclude>log4j:log4j:*:*:compile</exclude>  <!-- groupId:artifactId:version:type:scope -->
  </excludes>
  <message>Use SLF4J and Logback instead of commons-logging or log4j</message>
</bannedDependencies>

<!-- Require newer transitive version (upper bounds) -->
<requireUpperBoundDeps/>

<!-- Require a property to be set -->
<requireProperty>
  <property>env</property>
  <message>Please pass -Denv=dev|ci|prod</message>
</requireProperty>

<!-- Require files to exist -->
<requireFilesExist>
  <files>
    <file>${project.basedir}/src/main/resources/application.yml</file>
  </files>
</requireFilesExist>
```

**THE TRADE-OFFS:**
**Gain:** Automated, version-controlled quality gates; fail fast (before compilation); consistent enforcement across all developers and CI; custom rules enable organisation-specific policies; violations produce actionable error messages.
**Cost:** Some rules (like `dependencyConvergence`) are expensive to evaluate on large dependency trees; rule maintenance required as project evolves; too many strict rules create "enforcer fatigue" if violations are common and expected; needs explicit configuration per project (no global Maven configuration).

---

### 🧪 Thought Experiment

**SETUP:**
Your organisation banned `commons-logging` 2 years ago (standardised on SLF4J). The `bannedDependencies` rule enforces this. A new team member adds a Spring MVC dependency that transitively pulls in `commons-logging` via a legacy Spring module. The build fails with:

```
[ERROR] Rule 0: org.apache.maven.plugins.enforcer.BannedDependencies failed
Dependency commons-logging:commons-logging:1.2 found (excluded: commons-logging:commons-logging)
```

**APPROACHES:**

1. Exclude `commons-logging` from the Spring MVC transitive chain
2. Check if a newer Spring version eliminated the dependency
3. Temporarily whitelist it with `<allowed>commons-logging:commons-logging:1.2</allowed>` (short-term)

**THE LESSON:**
Enforcer violations from transitive dependencies are common. The fix is usually an exclusion or an upgrade of the direct dependency that pulled in the banned artifact. The rule message ("Use SLF4J...") guides the developer to the right solution.

---

### 🧠 Mental Model / Analogy

> The Maven Enforcer Plugin is like a compiler for your build policy. Just as a compiler rejects syntactically incorrect code, the Enforcer rejects builds that violate your architectural, security, or quality policies. The policies are first-class build configuration - not documentation.

---

### 📶 Gradual Depth - Four Levels

**Level 1:** The Enforcer Plugin lets you add rules to your build that fail it if violated. Example: "This project requires Java 17 or higher - fail if built with Java 11."

**Level 2:** Rules bind to the `validate` phase (first in lifecycle). Common rules: `requireJavaVersion`, `dependencyConvergence`, `bannedDependencies`, `requireReleaseDeps`. Multiple `<execution>` blocks can run different rules at different phases.

**Level 3:** `dependencyConvergence` vs `requireUpperBoundDeps`: convergence fails if any artifact appears at multiple versions; upper bounds fails if a selected version is lower than any requested version (a more nuanced subset of convergence). Both are important for safe dependency management.

**Level 4:** Custom rules: implement `EnforceRule` interface, package as a Maven plugin JAR, add as a plugin dependency. Custom rules can enforce: license policies (parsing LICENCE headers), architectural patterns (no `*.xml` in `src/main/java`), team-specific naming conventions, security constraints (no `System.exit` calls detected via static analysis). Combine with `requirePlugin` to ensure consistent plugin versions across teams.

---

### ⚙️ How It Works (Mechanism)

```bash
# Run enforcer rules manually (without full build)
mvn enforcer:enforce

# Display dependency tree to understand violation context
mvn dependency:tree -Dverbose | grep "commons-logging"

# Run specific rule check
mvn enforcer:enforce -Drules=dependencyConvergence

# Skip enforcer (useful for debugging build issues)
mvn package -Denforcer.skip=true
# or
mvn package -Dmaven.enforcer.skip=true
```

---

### 💻 Code Example

**Complete enterprise enforcer configuration:**

```xml
<plugin>
  <groupId>org.apache.maven.plugins</groupId>
  <artifactId>maven-enforcer-plugin</artifactId>
  <version>3.4.1</version>
  <executions>

    <!-- Phase 1: Environment checks (validate) -->
    <execution>
      <id>enforce-environment</id>
      <phase>validate</phase>
      <goals><goal>enforce</goal></goals>
      <configuration>
        <rules>
          <requireJavaVersion>
            <version>[17,21]</version>
            <message>This project requires Java 17-21. Set JAVA_HOME appropriately.</message>
          </requireJavaVersion>
          <requireMavenVersion>
            <version>[3.9,)</version>
            <message>Maven 3.9+ required. Use mvnw instead of system mvn.</message>
          </requireMavenVersion>
        </rules>
      </configuration>
    </execution>

    <!-- Phase 2: Dependency checks (verify - after tests) -->
    <execution>
      <id>enforce-dependencies</id>
      <phase>verify</phase>
      <goals><goal>enforce</goal></goals>
      <configuration>
        <rules>
          <!-- All transitive deps must resolve to single versions -->
          <dependencyConvergence/>

          <!-- No SNAPSHOT dependencies (enforce for release builds) -->
          <requireReleaseDeps>
            <onlyWhenRelease>true</onlyWhenRelease>  <!-- only enforced for non-SNAPSHOT projects -->
            <message>No SNAPSHOT dependencies allowed in release builds!</message>
          </requireReleaseDeps>

          <!-- Ban forbidden dependencies -->
          <bannedDependencies>
            <excludes>
              <!-- Legacy logging (use SLF4J) -->
              <exclude>commons-logging:commons-logging</exclude>
              <exclude>log4j:log4j</exclude>
              <!-- Vulnerable transitive (example) -->
              <exclude>org.springframework:spring-core:[,5.3.0)</exclude>
            </excludes>
            <searchTransitive>true</searchTransitive>
          </bannedDependencies>

        </rules>
      </configuration>
    </execution>

  </executions>
</plugin>
```

---

### ⚖️ Comparison Table

| Rule                    | What It Checks                   | Severity Scenario                   |
| ----------------------- | -------------------------------- | ----------------------------------- |
| `requireJavaVersion`    | JDK version used for build       | Wrong JDK → wrong bytecode          |
| `dependencyConvergence` | All artifacts at single version  | `NoSuchMethodError` at runtime      |
| `requireReleaseDeps`    | No SNAPSHOT in release artifact  | Non-reproducible release            |
| `bannedDependencies`    | Specific forbidden artifacts     | Security, licence, or legacy policy |
| `requireUpperBoundDeps` | Resolved version ≥ all requested | Undeclared API incompatibility      |
| `requireMavenVersion`   | Maven version used               | Build tool version drift            |

---

### ⚠️ Common Misconceptions

| Misconception                                 | Reality                                                                                |
| --------------------------------------------- | -------------------------------------------------------------------------------------- |
| Enforcer only checks your direct dependencies | `searchTransitive=true` (default for banned) checks the full dependency tree           |
| `requireReleaseDeps` blocks all SNAPSHOT deps | `<onlyWhenRelease>true</onlyWhenRelease>` restricts to release-versioned projects only |
| Enforcer rules slow builds significantly      | Environment rules are fast; `dependencyConvergence` is slower for large trees          |
| Skipping enforcer in CI is acceptable         | `-Denforcer.skip=true` should be a developer escape hatch only, never a CI default     |

---

### 🚨 Failure Modes & Diagnosis

**`dependencyConvergence` fails but fixing it is unclear**

**Diagnosis:**

```bash
# See the full conflict paths
mvn enforcer:enforce
# The error output shows BOTH paths causing the conflict

# Also useful:
mvn dependency:tree -Dverbose | grep "(conflict with"
```

**Fix:** Add `<dependencyManagement>` entry to pin the winning version.

---

**`requireReleaseDeps` fires unexpectedly**

**Root Cause:** Parent POM version or imported BOM is still SNAPSHOT.

**Fix:** Check `<parent><version>` and all BOM imports in `<dependencyManagement>` for `-SNAPSHOT` versions.

---

### 🔗 Related Keywords

**Prerequisites:** `Maven Plugins`, `Dependency Convergence`, `Maven Multi-Module Project`, `SNAPSHOT vs RELEASE`

**Builds On This:** `Build Reproducibility`, `OWASP Dependency Check`

**Related Patterns:** `Dependency Convergence`, `SNAPSHOT vs RELEASE`, `Build Reproducibility`

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ PLUGIN       │ maven-enforcer-plugin                     │
├──────────────┼───────────────────────────────────────────┤
│ PHASE        │ validate (before compile, by default)     │
├──────────────┼───────────────────────────────────────────┤
│ KEY RULES    │ requireJavaVersion, dependencyConvergence │
│              │ bannedDependencies, requireReleaseDeps    │
├──────────────┼───────────────────────────────────────────┤
│ RUN ALONE    │ mvn enforcer:enforce                      │
├──────────────┼───────────────────────────────────────────┤
│ SKIP         │ -Denforcer.skip=true (dev only!)          │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "Build-time assertions for project rules" │
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** You want to enforce that no module in your 15-module Maven project directly depends on `com.example:legacy-module` (a library being phased out). However, `legacy-module` may still appear as a transitive dependency through third-party libs. How would you configure `bannedDependencies` to ban only _direct_ dependencies on it while allowing transitive presence?

**Q2.** Your team uses `dependencyConvergence` and it fires constantly due to conflicts introduced by Spring Boot's BOM and your custom libraries. A colleague suggests disabling `dependencyConvergence` to "reduce noise." What is the risk of doing so, and what is the correct long-term solution for managing a project where multiple BOMs introduce competing versions?
