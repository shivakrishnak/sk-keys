---
layout: default
title: "Transitive Dependencies"
parent: "Maven & Build Tools (Java)"
nav_order: 1074
permalink: /maven-build/transitive-dependencies/
number: "1074"
category: Maven & Build Tools (Java)
difficulty: ★★☆
depends_on: Maven Dependencies, Dependency Scope (compile, test, provided, runtime), pom.xml
used_by: Dependency Exclusion, Dependency Convergence, Maven BOM (Bill of Materials)
related: Dependency Exclusion, Dependency Convergence, Maven BOM (Bill of Materials)
tags:
  - maven
  - build-tools
  - java
  - intermediate
  - dependencies
---

# 1074 — Transitive Dependencies

⚡ TL;DR — Transitive dependencies are the dependencies of your dependencies — Maven resolves them automatically, but they can introduce version conflicts, unexpected libraries, and security vulnerabilities that you didn't explicitly choose.

| #1074           | Category: Maven & Build Tools (Java)                                        | Difficulty: ★★☆ |
| :-------------- | :-------------------------------------------------------------------------- | :-------------- |
| **Depends on:** | Maven Dependencies, Dependency Scope, pom.xml                               |                 |
| **Used by:**    | Dependency Exclusion, Dependency Convergence, Maven BOM (Bill of Materials) |                 |
| **Related:**    | Dependency Exclusion, Dependency Convergence, Maven BOM (Bill of Materials) |                 |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
Without transitive resolution, when you declare `spring-boot-starter-web` as a dependency, you'd also have to manually declare spring-webmvc, spring-context, spring-core, spring-beans, spring-aop, spring-expression, tomcat-embed-core, jackson-databind, jackson-core, jackson-annotations, slf4j-api, logback-classic... and then each of those dependencies' dependencies in turn. A single `spring-boot-starter-web` declaration would balloon to 50+ explicit declarations.

**THE BREAKING POINT:**
This is the JAR hell problem at scale. Manually managing 200-1000 transitive JARs is error-prone: one missed dependency causes a runtime `ClassNotFoundException`; one wrong version causes a `NoSuchMethodError`. And every time you upgrade a library, you'd have to re-audit and update all its transitives manually.

**THE INVENTION MOMENT:**
Maven's transitive dependency resolution was created to automate the dependency graph. Declare only what your code directly uses; Maven follows the dependency chain and resolves everything transitively. This is the core of Maven's value proposition: package once with declared dependencies, and any consumer automatically gets what they need.

---

### 📘 Textbook Definition

**Transitive dependencies** are artifacts that are not directly declared by a project but are required by the project's direct dependencies (or their dependencies, recursively). Maven performs a depth-first traversal of the dependency graph: for each declared dependency, Maven downloads its POM, reads its `<dependencies>`, and recursively resolves those. The resulting DAG may contain the same artifact at multiple versions (from different dependency paths); Maven applies its conflict resolution strategy (nearest-wins: the version closest to the root of the dependency tree is selected; equal-depth: first-declared wins) to produce a single resolved version for each artifact. Transitive dependencies with `test` or `provided` scope in their originating POM are NOT propagated.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
Your library depends on other libraries, which depend on other libraries — Maven automatically discovers and includes the entire chain.

**One analogy:**

> Transitive dependencies are like inheriting family friends. You invite Alice to your party (direct dependency). Alice is always with Bob (Alice's direct dependency → your transitive). Bob can't go anywhere without Carol (Carol becomes another transitive). You invited one person; three showed up. You didn't choose Bob and Carol, but here they are — with all their own opinions about how things should work.

**One insight:**
The real danger of transitive dependencies isn't the extra JARs — it's the version conflicts. When your project pulls in 500 transitive JARs and two different paths require different versions of Guava, Maven silently picks one. The chosen version may be incompatible with the code that requested the other version, causing runtime failures that have no obvious connection to the code you actually changed.

---

### 🔩 First Principles Explanation

**CORE INVARIANTS:**

1. Every artifact published to Maven Central includes a POM describing its own `<dependencies>`.
2. Maven recursively follows these POM chains to build the complete dependency graph.
3. Only `compile` and `runtime`-scoped transitive dependencies propagate; `test` and `provided` do not.

**HOW TRANSITIVE RESOLUTION WORKS:**

```
Your pom.xml declares:
  → spring-context:6.1.2 (compile)

Maven reads spring-context's pom.xml → finds:
  → spring-core:6.1.2 (compile)      ← now resolved transitively
  → spring-expression:6.1.2 (compile)← now resolved transitively
  → spring-aop:6.1.2 (compile)       ← now resolved transitively

Maven reads spring-core's pom.xml → finds:
  → spring-jcl:6.1.2 (compile)       ← now resolved at depth 3

Final classpath includes ALL of:
spring-context, spring-core, spring-expression, spring-aop, spring-jcl
(plus all of their transitives recursively)
```

**VERSION CONFLICT RESOLUTION (nearest-wins):**

```
Your project (depth 0)
├── Library A (depth 1) → guava 31.1.1 (depth 2)
└── Library B (depth 1) → guava 32.0.0 (depth 2)

CONFLICT: guava 31.1.1 vs 32.0.0

RESOLUTION: same depth (2), first-declared wins
Library A declared first → guava 31.1.1 selected

Library B was compiled against guava 32.0.0
At runtime: NoSuchMethodError if B uses a 32.0.0-only method
```

**SCOPE PROPAGATION RULES:**

| Library A scope | Library B scope in A | Effective scope in your project |
| --------------- | -------------------- | ------------------------------- |
| compile         | compile              | compile                         |
| compile         | runtime              | runtime                         |
| compile         | provided             | **NOT propagated**              |
| compile         | test                 | **NOT propagated**              |
| runtime         | compile              | runtime                         |
| provided        | compile              | **NOT propagated**              |

**THE TRADE-OFFS:**

**Gain:** Automatic dependency management; zero manual JAR tracking; ecosystem of libraries works together by declaring their own requirements.

**Cost:** Large transitive graphs are hard to audit; version conflicts are silently resolved; vulnerabilities in transitive deps (like Log4Shell) affect your project even though you never chose them; binary size grows unpredictably.

---

### 🧪 Thought Experiment

**SETUP:**
In December 2021, a critical vulnerability (Log4Shell, CVE-2021-44228) was discovered in `log4j-core`. Millions of Java applications were affected. Most developers had never heard of log4j-core — it was a transitive dependency.

**THE TRANSITIVE CHAIN:**

```
Developer's pom.xml:
  spring-boot-starter-web (directly declared)

Transitive chain:
  spring-boot-starter-web
  → spring-boot-starter-logging
    → logback-classic
      → slf4j-api
        (at this point, many apps also had log4j bound via other paths)

Other common path:
  elasticsearch-client or kafka-clients
  → log4j-core ← THE VULNERABLE LIBRARY
    (nobody declared this; it arrived transitively)
```

**THE INSIGHT:**
The developer never wrote `<dependency>log4j-core</dependency>`. It arrived 3-4 hops into the transitive graph. The impact: every application that had log4j-core anywhere in its transitive graph was potentially vulnerable — regardless of whether the developer knew it was there. This is why `mvn dependency:tree` and OWASP Dependency Check exist.

---

### 🧠 Mental Model / Analogy

> Transitive dependencies are like biological food chains. You eat fish (direct dependency). The fish ate algae (transitive dep). The algae absorbed heavy metals from the water (another transitive dep). You didn't eat the heavy metals — but they're in your system because of the chain. You inherit both the benefits and risks of everything in the chain, even though you only chose the fish.

- "You eat fish" → declare a direct dependency
- "Fish ate algae" → fish's transitive dep
- "Heavy metals in algae" → vulnerability/conflict in transitive dep
- "You inherit heavy metals" → your project is affected by transitive dep issues
- "Food chain audit" → `mvn dependency:tree` + OWASP Dependency Check

**Where this analogy breaks down:** In a food chain, you can't remove one link; in Maven, you can exclude specific transitive dependencies you don't want.

---

### 📶 Gradual Depth — Four Levels

**Level 1 — What it is (anyone can understand):**
When you depend on Library A, and Library A depends on Library B, Maven automatically includes Library B in your project too. You didn't ask for Library B, but you need it because Library A needs it. These automatically included libraries are called transitive dependencies.

**Level 2 — How to use it (junior developer):**
Run `mvn dependency:tree` to see all transitive dependencies. You'll usually see 30–100x more JARs than you explicitly declared. If you see a library you don't want (e.g., `commons-logging` which conflicts with slf4j), you can exclude it: add `<exclusions>` to the declaration of the dependency that brings it in.

**Level 3 — How it works (mid-level engineer):**
Maven performs a DFS traversal of the POM dependency graph. When the same artifact appears at multiple versions (conflict), Maven applies nearest-wins: lowest depth wins, then first-declared. You can force a version by declaring it directly in your POM's `<dependencies>` (depth 1 always beats transitive depth 2+). `<dependencyManagement>` lets you govern versions without adding the dependency itself — it acts as a version override instruction. Use `mvn dependency:tree -Dverbose` to see "omitted for conflict" lines showing what was chosen vs. rejected.

**Level 4 — Why it was designed this way (senior/staff):**
Maven's nearest-wins conflict resolution is a deterministic algorithm with a known bias: it prefers versions declared closer to the project root, regardless of which version is newer or more compatible. This was a deliberate choice: "newest wins" produces non-deterministic results when different orderings of dependencies produce different selections. The cost is that older versions can silently win over newer ones. Modern enterprise builds use BOMs (Bill of Materials) to take explicit control of the entire transitive version graph, eliminating reliance on nearest-wins for critical library versions.

---

### ⚙️ How It Works (Mechanism)

```
┌──────────────────────────────────────────────────────┐
│         Transitive Dependency Graph (DFS)            │
├──────────────────────────────────────────────────────┤
│                                                      │
│  Your Project                                        │
│  ├── spring-context 6.1.2 (direct, compile)         │
│  │   ├── spring-core 6.1.2 (transitive, compile)    │
│  │   │   └── spring-jcl 6.1.2 (transitive, depth 3) │
│  │   ├── spring-aop 6.1.2 (transitive, compile)     │
│  │   └── spring-beans 6.1.2 (transitive, compile)   │
│  │                                                   │
│  └── jackson-databind 2.16.0 (direct, compile)      │
│      ├── jackson-core 2.16.0 (transitive, compile)  │
│      └── jackson-annotations 2.16.0 (transitive)    │
│                                                      │
│  spring-core appears TWICE:                          │
│  - from spring-context (depth 2): 6.1.2             │
│  - (if another dep also needs it: conflict check)   │
│                                                      │
│  Resolution:                                         │
│  mvn dependency:tree -Dverbose shows:               │
│  [INFO] [compile] spring-core:6.1.2                 │
│  [INFO]    [compile] spring-core:6.0.0 (omitted for │
│             conflict with 6.1.2)                    │
└──────────────────────────────────────────────────────┘
```

---

### 🔄 The Complete Picture — End-to-End Flow

**NORMAL FLOW:**

```
mvn package
  → Dependency resolution phase
      → Your pom.xml: 5 declared deps  ← YOU ARE HERE
      → Maven resolves transitives recursively
      → 5 declared → 127 resolved (including transitives)
      → Conflict resolution: nearest-wins applied
      → Scope propagation: test/provided not propagated
      → Classpaths populated
  → Compile phase (all compile-scope deps available)
  → Test phase (all scopes available)
  → Package phase: target/app.jar includes compile+runtime
```

**FAILURE PATH:**

```
Transitive version conflict not caught:
  → Library A compiled against guava 32 (uses new method)
  → guava 31 selected (nearest-wins from Library B)
  → BUILD SUCCESS (compile passes — guava is on classpath)
  → RUNTIME FAILURE: NoSuchMethodError at guava method
  → Fix: mvn dependency:tree → pin guava 32 explicitly
```

**WHAT CHANGES AT SCALE:**
Enterprise applications with 1000+ transitive dependencies use Maven BOMs to govern versions centrally. Security teams run automated SCA tools on every build to detect known CVEs in the transitive graph. Nexus/Artifactory can be configured to block artifacts with known critical vulnerabilities from being downloaded.

---

### 💻 Code Example

**Example 1 — Inspecting the dependency tree:**

```bash
# Show full transitive tree (can be hundreds of lines)
mvn dependency:tree

# Show tree with conflict resolution (verbose)
mvn dependency:tree -Dverbose

# Filter to one specific artifact across all paths
mvn dependency:tree -Dincludes=com.google.guava:guava

# Show only test scope transitives
mvn dependency:tree -Dscope=test

# Output tree to a file
mvn dependency:tree -DoutputFile=deps.txt
```

**Example 2 — Detecting and auditing:**

```bash
# Find unused declared deps + used undeclared deps
mvn dependency:analyze

# Security scan: find CVEs in all transitive deps
# (requires owasp-dependency-check-maven plugin configured)
mvn org.owasp:dependency-check-maven:check

# Resolve all deps (fail fast if any can't be resolved)
mvn dependency:resolve
```

**Example 3 — Forcing a transitive version:**

```xml
<dependencies>
  <!-- Force guava version even though we don't use it directly -->
  <!-- Our explicit declaration (depth 1) beats transitive ones -->
  <dependency>
    <groupId>com.google.guava</groupId>
    <artifactId>guava</artifactId>
    <version>32.1.3-jre</version>
    <!-- No scope → compile (default) -->
    <!-- Add this comment to explain the override: -->
    <!-- Forced: transitives from library-a and library-b
         require conflicting versions; 32.1.3 is compatible -->
  </dependency>

  <dependency>
    <groupId>com.example</groupId>
    <artifactId>library-a</artifactId>
    <version>1.0.0</version>
  </dependency>
</dependencies>
```

---

### ⚖️ Comparison Table

| Strategy                    | Mechanism                           | Best For                                      |
| --------------------------- | ----------------------------------- | --------------------------------------------- |
| Nearest-wins (default)      | Maven auto-selects by tree depth    | Simple projects with few conflicts            |
| Direct declaration override | Add dep at depth 1 to force version | Fixing a specific conflict                    |
| `<dependencyManagement>`    | Govern version without importing    | Multi-module version alignment                |
| BOM import                  | Import entire curated version set   | Framework-wide version alignment (Spring BOM) |
| Exclusion                   | Remove specific transitive dep      | Removing an unwanted/conflicting transitive   |

---

### ⚠️ Common Misconceptions

| Misconception                                                         | Reality                                                                                                  |
| --------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------- |
| Maven picks the newest version in a conflict                          | Maven uses nearest-wins — the version closest to the project root wins, regardless of version number     |
| `test` scoped deps of my deps appear transitively                     | `test` and `provided` scoped transitives are NOT propagated — they stop at the declaring project         |
| Transitive deps are safe because they were published to Maven Central | Central doesn't vet for security; transitive deps regularly contain CVEs (Log4Shell, Spring4Shell, etc.) |
| `mvn dependency:analyze` finds all transitive issues                  | It only finds unused/undeclared compile-time issues; it doesn't detect runtime-only transitive conflicts |

---

### 🚨 Failure Modes & Diagnosis

**`NoSuchMethodError` on library method you didn't change**

**Root Cause:** Transitive version conflict — wrong version of a library was selected by nearest-wins.

**Diagnosis:**

```bash
mvn dependency:tree -Dverbose -Dincludes=<affected-groupId>:<artifactId>
# Find the "(omitted for conflict with X.Y.Z)" line
# The omitted version is what the failing library needs
```

**Fix:** Explicitly declare the correct version in `<dependencies>` (or use `<dependencyManagement>`).

---

**Security scanner reports CVE in a library you never heard of**

**Root Cause:** Library is a transitive dependency you didn't declare.

**Diagnosis:**

```bash
mvn dependency:tree -Dincludes=<vulnerable-groupId>:<artifactId>
# Trace which direct dependency introduced it
```

**Fix:** Update the direct dependency that brings in the vulnerable transitive, or override the transitive version in `<dependencyManagement>`.

---

### 🔗 Related Keywords

**Prerequisites:** `Maven Dependencies`, `Dependency Scope`, `pom.xml`

**Builds On This:** `Dependency Exclusion`, `Dependency Convergence`, `Maven BOM (Bill of Materials)`

**Related Patterns:** `Dependency Exclusion`, `Dependency Convergence`, `Maven BOM (Bill of Materials)`

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ VIEW TREE  │ mvn dependency:tree (-Dverbose for details) │
├────────────┼──────────────────────────────────────────── │
│ CONFLICT   │ nearest-wins (lowest depth, first-declared)  │
├────────────┼──────────────────────────────────────────── │
│ FORCE VER  │ declare directly in <dependencies> (depth 1) │
├────────────┼──────────────────────────────────────────── │
│ AUDIT      │ mvn dependency:analyze                      │
├────────────┼──────────────────────────────────────────── │
│ NOT PROP.  │ test + provided scope NOT propagated        │
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** You run `mvn dependency:tree -Dverbose` and see this line:
`[INFO] com.google.guava:guava:jar:31.0.1-jre:compile (omitted for conflict with 32.0.0-jre)`
What does this tell you, and which version of guava is actually on the classpath?

**Q2.** Log4Shell (CVE-2021-44228) affected applications that had `log4j-core` as a transitive dependency. Describe the steps you would take to: (1) determine if your project is affected; (2) remediate the vulnerability without removing the direct dependency that pulls in log4j-core.
