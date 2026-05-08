---
layout: default
title: "Maven Dependencies"
parent: "Maven & Build Tools"
grand_parent: "Technical Dictionary"
nav_order: 12
permalink: /maven-build/maven-dependencies/
id: MVN-012
category: Maven & Build Tools (Java)
difficulty: ★☆☆
depends_on: Maven Overview, pom.xml
used_by: Dependency Scope (compile, test, provided, runtime), Transitive Dependencies, Dependency Exclusion, Dependency Convergence, Maven BOM (Bill of Materials)
related: Dependency Scope (compile, test, provided, runtime), Transitive Dependencies, Maven Repository (local, central, remote)
tags:
  - maven
  - build-tools
  - java
  - foundational
  - dependencies
---

# MVN-012 - Maven Dependencies

⚡ TL;DR - Maven dependencies are external libraries your project declares it needs; Maven automatically downloads them, resolves their transitive dependencies, and adds them to the correct classpath for compilation and runtime.

| #1072           | Category: Maven & Build Tools (Java)                                                               | Difficulty: ★☆☆ |
| :-------------- | :------------------------------------------------------------------------------------------------- | :-------------- |
| **Depends on:** | Maven Overview, pom.xml                                                                            |                 |
| **Used by:**    | Dependency Scope, Transitive Dependencies, Dependency Exclusion, Dependency Convergence, Maven BOM |                 |
| **Related:**    | Dependency Scope, Transitive Dependencies, Maven Repository                                        |                 |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
Before automated dependency management, Java developers downloaded JAR files manually from project websites. Each JAR was committed to source control (or stored on a shared drive). When a library was upgraded, every project that used it needed manual JAR replacement. When Library A required Library B, developers had to read the documentation to discover this and download B separately. Classpath management was an error-prone, time-consuming ritual.

**THE BREAKING POINT:**
A typical enterprise Java project depends on 20–50 direct libraries, each of which may depend on 5–20 others. Managing 200–1000 JAR files by hand is impractical. Worse: two dependencies might require different, incompatible versions of the same library. Without automated resolution, this "JAR hell" problem had no systematic solution.

**THE INVENTION MOMENT:**
Maven's dependency management system was created to solve JAR hell: declare what you need (not how to get it), and Maven figures out the rest - downloading, caching, and managing the full transitive dependency graph automatically. This is why Maven's dependency model exists.

---

### 📘 Textbook Definition

A **Maven dependency** is a reference declared in `pom.xml` to an external artifact (JAR, WAR, POM) that the current project requires. Each dependency is identified by its Maven coordinates (groupId, artifactId, version) and an optional scope that controls when the dependency is on the classpath (compile, test, runtime, provided, system, import). Maven performs transitive dependency resolution: if project A depends on library B, which depends on library C, Maven automatically includes C without requiring an explicit declaration. Dependencies are resolved from Maven repositories (local cache first, then remote repositories), and version conflicts in the transitive graph are resolved using Maven's nearest-wins strategy.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
Declare what your project needs and Maven automatically downloads it, including everything that it needs.

**One analogy:**

> Maven dependencies are like a grocery delivery order. You write a list of what you need: "milk, eggs, flour." The delivery service (Maven) figures out that flour comes in a bag that requires a shelf, eggs come in a carton - all the "dependencies of your ingredients" are handled automatically. You don't go to the store; the ingredients arrive at your door.

**One insight:**
The transitive resolution is both Maven's greatest strength (you don't have to know your library's internal dependencies) and its greatest source of problems (you inherit version conflicts from libraries you've never heard of). Understanding transitive resolution is the key to mastering Maven dependency management.

---

### 🔩 First Principles Explanation

**CORE INVARIANTS:**

1. Every dependency is uniquely identified by groupId:artifactId:version (GAV coordinates).
2. Maven resolves the full transitive dependency graph - all deps of deps, recursively.
3. Version conflicts (same artifact, different versions) are resolved by nearest-wins: the version closest to the root of the dependency tree wins.

**DEPENDENCY DECLARATION:**

```xml
<dependencies>

  <!-- Direct dependency: available at compile + runtime -->
  <dependency>
    <groupId>org.springframework</groupId>
    <artifactId>spring-context</artifactId>
    <version>6.1.2</version>
    <!-- scope defaults to 'compile' if omitted -->
  </dependency>

  <!-- Test-only dependency: not in production classpath -->
  <dependency>
    <groupId>org.junit.jupiter</groupId>
    <artifactId>junit-jupiter</artifactId>
    <version>5.10.1</version>
    <scope>test</scope>
  </dependency>

  <!-- Provided by the runtime container (Servlet API): -->
  <!-- compile-time only, not bundled in final artifact -->
  <dependency>
    <groupId>jakarta.servlet</groupId>
    <artifactId>jakarta.servlet-api</artifactId>
    <version>6.0.0</version>
    <scope>provided</scope>
  </dependency>

</dependencies>
```

**TRANSITIVE RESOLUTION EXAMPLE:**

```
Your project depends on spring-context 6.1.2
  spring-context depends on spring-core 6.1.2
  spring-context depends on spring-aop 6.1.2
  spring-core depends on spring-jcl 6.1.2

Maven adds to classpath: spring-context, spring-core, spring-aop, spring-jcl
You only declared spring-context.
```

**NEAREST-WINS CONFLICT RESOLUTION:**

```
Your project
├── Library A → guava 32.0
└── Library B → guava 31.0

Maven's dependency tree:
Your project (depth 0)
  Library A (depth 1) → guava 32.0 (depth 2)
  Library B (depth 1) → guava 31.0 (depth 2)

SAME depth → FIRST-DECLARED wins → guava 32.0 selected
(Library A declared first in pom.xml → its version wins)
```

**THE TRADE-OFFS:**

**Gain:** Automatic dependency resolution; no manual JAR management; reproducible builds across machines; transitive dependencies handled transparently.

**Cost:** Transitive resolution can introduce unexpected dependencies; nearest-wins can silently select a version that breaks a library; fat dependency trees are hard to audit.

---

### 🧪 Thought Experiment

**SETUP:**
Your project declares one dependency: `spring-boot-starter-web`. You run `mvn dependency:tree`.

**WHAT YOU DECLARED:**
1 dependency.

**WHAT MAVEN RESOLVED (approximately):**

```
spring-boot-starter-web (your declaration)
├── spring-boot-starter (transitively resolved)
│   ├── spring-boot
│   ├── spring-boot-autoconfigure
│   └── spring-boot-starter-logging
│       ├── logback-classic
│       └── slf4j-api
├── spring-webmvc
│   ├── spring-context
│   ├── spring-core
│   └── spring-beans
├── tomcat-embed-core
└── jackson-databind
    ├── jackson-core
    └── jackson-annotations
... (30+ total artifacts)
```

**THE INSIGHT:**
One `<dependency>` declaration resolves to 30+ JARs on the classpath. Maven's transitive resolution is powerful, but it means your application contains code you didn't explicitly choose. This is why dependency auditing tools (OWASP Dependency Check, `mvn dependency:analyze`) are important.

---

### 🧠 Mental Model / Analogy

> Maven dependencies are like hiring a contractor. You hire the plumber (direct dependency). The plumber brings their own tools and materials (transitive dependencies). You don't need to know what wrench they use - you just need the pipes installed. But if the plumber brings a faulty tool (vulnerable transitive dependency), it affects your project even though you didn't choose it.

- "Hiring the plumber" → declaring a direct dependency in `<dependencies>`
- "Plumber's tools and materials" → transitive dependencies (deps of your dep)
- "Plumber costs" → dependency scope: when is it available?
- "Faulty tool you didn't choose" → vulnerable or conflicting transitive dependency
- "Deciding which version of the plumber" → dependency version management (BOM, `<dependencyManagement>`)

**Where this analogy breaks down:** A real contractor's tools don't conflict with each other; Maven transitive dependencies can and do conflict on version numbers.

---

### 📶 Gradual Depth - Four Levels

**Level 1 - What it is (anyone can understand):**
Maven dependencies are libraries your project needs. You list them in `pom.xml`, Maven downloads them automatically, and they're available when your code compiles and runs.

**Level 2 - How to use it (junior developer):**
Add a `<dependency>` block with `groupId`, `artifactId`, and `version`. Find the coordinates on [mvnrepository.com](https://mvnrepository.com). Use `<scope>test</scope>` for test-only deps. Run `mvn dependency:tree` to see all resolved dependencies including transitive ones. Run `mvn clean install` after adding dependencies so your IDE picks them up.

**Level 3 - How it works (mid-level engineer):**
Maven builds a Directed Acyclic Graph (DAG) of all dependencies and their transitive dependencies. When the same artifact appears at multiple versions (a conflict), the version closest to the root of the tree wins (nearest-wins). If two paths have equal depth, the first-declared wins. To force a specific version regardless of position, declare it directly in your POM's `<dependencies>` (it becomes depth-1, beating all transitive versions). Use `<dependencyManagement>` to govern versions without importing dependencies.

**Level 4 - Why it was designed this way (senior/staff):**
Nearest-wins was chosen over "highest version wins" for a reason: "highest version wins" is non-deterministic across different orderings of declarations and can cause unexpected upgrades. Nearest-wins is deterministic: the project owner's explicit declaration always beats transitive versions. The trade-off: you may unknowingly downgrade a transitive dependency if you declare an older version of something that two different libraries require at different versions. Modern Maven best practice uses `<dependencyManagement>` or BOMs to govern the transitive graph explicitly rather than relying on nearest-wins.

---

### ⚙️ How It Works (Mechanism)

```
┌──────────────────────────────────────────────────────┐
│         Dependency Resolution Process                │
├──────────────────────────────────────────────────────┤
│                                                      │
│  1. Read pom.xml <dependencies>                      │
│       │                                              │
│  2. For each dependency:                             │
│     a. Look up in local ~/.m2/repository             │
│     b. If absent: download from remote repo          │
│     c. Download artifact's POM file                  │
│     d. Read POM's <dependencies> (transitives)       │
│     e. Recursively resolve transitives               │
│       │                                              │
│  3. Build full dependency DAG                        │
│       │                                              │
│  4. Detect version conflicts:                        │
│     - Same groupId:artifactId, different versions    │
│     - Apply nearest-wins: lower depth wins           │
│     - Equal depth: first-declared wins               │
│       │                                              │
│  5. Apply scope rules:                               │
│     - compile: compile + test + runtime classpaths   │
│     - test: test classpath only                      │
│     - provided: compile only (not bundled)           │
│     - runtime: runtime + test, not compile           │
│       │                                              │
│  6. Produce three classpaths:                        │
│     - compile classpath (for javac)                  │
│     - test classpath (for surefire)                  │
│     - runtime classpath (for execution)              │
└──────────────────────────────────────────────────────┘
```

---

### 🔄 The Complete Picture - End-to-End Flow

**NORMAL FLOW:**

```
Developer adds <dependency> to pom.xml  ← YOU ARE HERE
  → Maven resolves GAV coordinates
  → Check local ~/.m2/repository
  → Download from Maven Central if absent
  → Resolve all transitive deps recursively
  → Detect and resolve version conflicts (nearest-wins)
  → Add to appropriate classpaths
  → mvn compile succeeds with new library available
```

**FAILURE PATH:**

```
Dependency not found in any repository
  → BUILD FAILURE: "Could not resolve artifact"
  → Check groupId/artifactId/version spelling
  → Check repository configuration
  → Use mvn dependency:resolve to debug resolution
```

**WHAT CHANGES AT SCALE:**
Large enterprise applications have 500-1000+ transitive dependencies. Version conflicts are common and require explicit `<dependencyManagement>` or BOM imports. OWASP Dependency Check and other SCA tools scan this graph for known CVEs. CI pipelines use Nexus/Artifactory as a proxy so all developers share a local cache, avoiding redundant downloads.

---

### 💻 Code Example

**Example 1 - Common dependency declarations:**

```xml
<dependencies>

  <!-- Compile dependency: available everywhere -->
  <dependency>
    <groupId>com.google.guava</groupId>
    <artifactId>guava</artifactId>
    <version>32.1.3-jre</version>
  </dependency>

  <!-- Test-only: not in final JAR/WAR -->
  <dependency>
    <groupId>org.assertj</groupId>
    <artifactId>assertj-core</artifactId>
    <version>3.24.2</version>
    <scope>test</scope>
  </dependency>

  <!-- Provided by container: compile-time only -->
  <dependency>
    <groupId>jakarta.servlet</groupId>
    <artifactId>jakarta.servlet-api</artifactId>
    <version>6.0.0</version>
    <scope>provided</scope>
  </dependency>

  <!-- Runtime driver: not needed for compilation -->
  <dependency>
    <groupId>org.postgresql</groupId>
    <artifactId>postgresql</artifactId>
    <version>42.7.1</version>
    <scope>runtime</scope>
  </dependency>

</dependencies>
```

**Example 2 - Diagnosing the dependency tree:**

```bash
# Show full dependency tree
mvn dependency:tree

# Show verbose tree with version conflict resolution
mvn dependency:tree -Dverbose

# Filter to a specific artifact
mvn dependency:tree -Dincludes=com.google.guava:guava

# Find unused declared / undeclared used dependencies
mvn dependency:analyze
```

**Example 3 - Forcing a version (overriding nearest-wins):**

```xml
<dependencies>
  <!-- Force guava to 32.1.3 regardless of what transitives want -->
  <dependency>
    <groupId>com.google.guava</groupId>
    <artifactId>guava</artifactId>
    <version>32.1.3-jre</version>
  </dependency>

  <!-- These also pull in guava, but our declaration (depth 1)
       beats their transitive versions (depth 2+) -->
  <dependency>
    <groupId>com.example</groupId>
    <artifactId>library-a</artifactId>
    <version>1.0.0</version>
  </dependency>
</dependencies>
```

---

### ⚖️ Comparison Table

| Dependency Type            | Scope             | Compile? | Runtime? | Test? | Bundled in JAR? |
| -------------------------- | ----------------- | -------- | -------- | ----- | --------------- |
| Regular library            | compile (default) | ✓        | ✓        | ✓     | ✓               |
| Test library               | test              | ✗        | ✗        | ✓     | ✗               |
| Container-provided         | provided          | ✓        | ✗        | ✓     | ✗               |
| Runtime-only (JDBC driver) | runtime           | ✗        | ✓        | ✓     | ✓               |
| System classpath           | system            | ✓        | ✓        | ✓     | ✗ (avoid)       |

---

### ⚠️ Common Misconceptions

| Misconception                                           | Reality                                                                                                                 |
| ------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------- |
| All declared dependencies are included in the final JAR | Only `compile` and `runtime` scope deps are bundled; `test` and `provided` are excluded                                 |
| The highest version of a conflicting dep always wins    | Nearest-wins: the version closest to the root of the dependency tree wins, regardless of version number                 |
| Transitive dependencies are fully trustworthy           | Transitive deps can introduce vulnerabilities (Log4Shell was a transitive dep); always audit with `mvn dependency:tree` |
| Adding a dependency is always safe                      | Every new dependency adds transitive deps, potential version conflicts, and security exposure surface area              |

---

### 🚨 Failure Modes & Diagnosis

**`NoSuchMethodError` or `ClassNotFoundException` at runtime**

**Root Cause:** A transitive dependency was resolved to a version missing a method that another library expects.

**Diagnosis:**

```bash
mvn dependency:tree -Dverbose -Dincludes=com.example:problematic-lib
# Look for "omitted for conflict with X.Y.Z" entries
```

**Fix:** Explicitly declare the correct version in `<dependencies>` or use `<dependencyManagement>` to pin it.

---

**"Unused declared dependency" warning from `dependency:analyze`**

**Root Cause:** A dependency declared in `<dependencies>` has no direct usage detected at compile time (only used reflectively or transitively).

**Fix:** Either remove the dependency if genuinely unused, or add `<!-- Used at runtime -->` comment and suppress the warning in plugin configuration.

---

### 🔗 Related Keywords

**Prerequisites:** `Maven Overview`, `pom.xml`

**Builds On This:** `Dependency Scope`, `Transitive Dependencies`, `Dependency Exclusion`, `Dependency Convergence`, `Maven BOM`

**Related Patterns:** `Dependency Scope`, `Transitive Dependencies`, `Maven Repository`

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ DECLARE  │ <dependency> with groupId:artifactId:version  │
├──────────┼──────────────────────────────────────────────  │
│ SCOPES   │ compile (default), test, provided, runtime    │
├──────────┼──────────────────────────────────────────────  │
│ CONFLICT │ nearest-wins (closest to root of tree)        │
├──────────┼──────────────────────────────────────────────  │
│ DIAGNOSE │ mvn dependency:tree -Dverbose                 │
├──────────┼──────────────────────────────────────────────  │
│ AUDIT    │ mvn dependency:analyze                        │
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** Your project declares dependency A (which requires guava 31.0) and dependency B (which requires guava 32.0). After running `mvn dependency:tree`, you see guava 31.0 was selected. Why? How would you force guava 32.0 to be used for both?

**Q2.** What is the difference between a `provided` scope and a `runtime` scope dependency? Give a concrete example of a dependency that should use each scope, and explain what happens if you accidentally use the wrong scope.
