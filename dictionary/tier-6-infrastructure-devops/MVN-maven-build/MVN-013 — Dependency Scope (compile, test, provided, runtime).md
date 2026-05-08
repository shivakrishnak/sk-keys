---
layout: default
title: "Dependency Scope (compile, test, provided, runtime)"
parent: "Maven & Build Tools (Java)"
grand_parent: "Technical Dictionary"
nav_order: 13
permalink: /maven-build/dependency-scope/
id: MVN-013
category: Maven & Build Tools (Java)
difficulty: ★★☆
depends_on: Maven Dependencies, pom.xml, Maven Overview
used_by: Transitive Dependencies, Dependency Exclusion, Dependency Convergence
related: Transitive Dependencies, Maven Dependencies, Maven Repository (local, central, remote)
tags:
  - maven
  - build-tools
  - java
  - intermediate
  - dependencies
---

# MVN-013 — Dependency Scope (compile, test, provided, runtime)

⚡ TL;DR — Dependency scope controls exactly when a library is available (compile time, test time, runtime) and whether it ends up bundled in your final artifact — getting scope wrong produces either a bloated JAR or a runtime `ClassNotFoundException`.

| #1073           | Category: Maven & Build Tools (Java)                                  | Difficulty: ★★☆ |
| :-------------- | :-------------------------------------------------------------------- | :-------------- |
| **Depends on:** | Maven Dependencies, pom.xml, Maven Overview                           |                 |
| **Used by:**    | Transitive Dependencies, Dependency Exclusion, Dependency Convergence |                 |
| **Related:**    | Transitive Dependencies, Maven Dependencies, Maven Repository         |                 |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
Without dependency scopes, every library you declare would be on every classpath and bundled into every artifact. Your test libraries (JUnit, Mockito, AssertJ) would ship to production in your JAR/WAR. The Servlet API — which the application server already provides — would be bundled twice, causing class conflicts at runtime. Your final artifact would be bloated with development-only code.

**THE BREAKING POINT:**
Different libraries are needed at different points in the build. JUnit is needed only to compile and run tests — not in production. The Servlet API is needed to compile your code but must NOT be bundled (the app server provides it). PostgreSQL JDBC driver needs to be on the runtime classpath but doesn't affect compilation (your code uses `java.sql.DataSource`, not postgres-specific classes).

**THE INVENTION MOMENT:**
Dependency scope was introduced to give developers precise control over when a dependency is on the classpath and whether it's included in the final artifact. This is why dependency scope exists: to keep production artifacts clean and avoid class conflicts from bundled-vs-provided libraries.

---

### 📘 Textbook Definition

**Dependency scope** in Maven controls the visibility of a dependency on different classpaths during the build process and whether it is transitively propagated to downstream projects. Maven defines six scopes: (1) **compile** (default) — available on all classpaths; propagated transitively; bundled in final artifact; (2) **test** — available only during test compilation and execution; not propagated; not bundled; (3) **provided** — available for compilation and test execution; NOT bundled (expected to be provided by the runtime environment); NOT propagated; (4) **runtime** — NOT on compile classpath; available for test and runtime; bundled; (5) **system** — like `provided` but requires a local filesystem path; deprecated/avoid; (6) **import** — only valid in `<dependencyManagement>` for importing a BOM's dependency definitions.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
Scope tells Maven when a library is needed and whether to include it in the deployable artifact.

**One analogy:**

> Scope is like dress code for libraries. `compile` = formal wear (everywhere, always). `test` = gym clothes (only in the testing room, left at the gym). `provided` = uniform (wear it in the office to compile, but the company provides the actual uniform — don't bring your own to production). `runtime` = safety boots (not needed to design the building, but required when you're actually on-site running it).

**One insight:**
The `provided` scope is the most misunderstood. It means: "I need this to compile, but the runtime environment (Tomcat, JBoss, Lambda) will have it — don't include it in my artifact." Forgetting `provided` for the Servlet API in a WAR causes a `ClassCastException` at runtime because two versions of the same class exist: yours (bundled) and the container's (injected).

---

### 🔩 First Principles Explanation

**CORE INVARIANTS:**

1. Maven maintains three distinct classpaths: compile, test, and runtime.
2. Scope determines which classpaths include the dependency.
3. Scope affects transitive propagation: downstream projects inherit `compile`-scoped deps; they don't inherit `test` or `provided`.

**SCOPE CLASSPATH MATRIX:**

```
┌────────────┬─────────┬───────────────┬─────────┬──────────────┐
│ Scope      │ Compile │ Test Compile  │ Runtime │ Bundled?     │
│            │ Class   │ + Execution   │ Class   │ In Artifact? │
├────────────┼─────────┼───────────────┼─────────┼──────────────┤
│ compile    │   ✓     │      ✓        │   ✓     │     ✓        │
│ test       │   ✗     │      ✓        │   ✗     │     ✗        │
│ provided   │   ✓     │      ✓        │   ✗     │     ✗        │
│ runtime    │   ✗     │      ✓        │   ✓     │     ✓        │
│ system     │   ✓     │      ✓        │   ✗     │     ✗        │
└────────────┴─────────┴───────────────┴─────────┴──────────────┘
```

**TRANSITIVE SCOPE PROPAGATION:**

When project A depends on project B (which has its own dependencies), B's `compile`-scoped deps propagate to A as `compile`. B's `provided` and `test`-scoped deps do NOT propagate — they're private to B's build.

**CONCRETE USE CASES:**

```xml
<!-- COMPILE (default): production library, always needed -->
<dependency>
  <groupId>org.springframework.boot</groupId>
  <artifactId>spring-boot-starter-web</artifactId>
  <version>3.2.0</version>
  <!-- scope: compile (default) — bundled in final JAR -->
</dependency>

<!-- TEST: only needed to write and run tests -->
<dependency>
  <groupId>org.junit.jupiter</groupId>
  <artifactId>junit-jupiter</artifactId>
  <version>5.10.1</version>
  <scope>test</scope>  <!-- NOT in production artifact -->
</dependency>

<!-- PROVIDED: compile + test only; container provides at runtime -->
<dependency>
  <groupId>jakarta.servlet</groupId>
  <artifactId>jakarta.servlet-api</artifactId>
  <version>6.0.0</version>
  <scope>provided</scope>  <!-- Tomcat provides this at runtime -->
</dependency>

<!-- RUNTIME: driver not needed to compile, but needed to run -->
<dependency>
  <groupId>org.postgresql</groupId>
  <artifactId>postgresql</artifactId>
  <version>42.7.1</version>
  <scope>runtime</scope>  <!-- Code uses java.sql.*, not pg-specific -->
</dependency>
```

**THE TRADE-OFFS:**

**Gain:** Lean production artifacts; no class conflicts from bundled-vs-provided libraries; clear separation of concerns between compile-time, test-time, and runtime.

**Cost:** Scoping errors are often invisible at compile time but fail loudly at runtime; `provided` scope requires knowing what the deployment target provides.

---

### 🧪 Thought Experiment

**SETUP:**
You're building a WAR file for deployment on Tomcat. You declare the Servlet API as `compile` scope instead of `provided`.

**WHAT HAPPENS WITH WRONG SCOPE (compile):**
Your WAR file now contains `jakarta.servlet.HttpServlet` from your `jakarta.servlet-api` JAR. Tomcat also loads `jakarta.servlet.HttpServlet` from its own lib directory. When your servlet class is loaded, Java sees two different `HttpServlet` classes from two different ClassLoaders. Spring tries to cast between them: `ClassCastException: jakarta.servlet.HttpServlet cannot be cast to jakarta.servlet.HttpServlet`. The application fails to start.

**WHAT HAPPENS WITH CORRECT SCOPE (provided):**
Your WAR doesn't contain the Servlet API JAR. Tomcat provides the one and only `HttpServlet` class. No conflict. Application starts correctly.

**THE INSIGHT:**
`provided` scope is a contract with the deployment environment. When you use `provided`, you're saying "I trust the runtime to supply this." Breaking that contract by bundling what the container provides causes class identity conflicts that are uniquely confusing to debug.

---

### 🧠 Mental Model / Analogy

> Dependency scope is like packing for a trip. `compile` = pack it in your suitcase, use it everywhere. `test` = bring practice gear to the rehearsal room but leave it at the hotel — don't take it on stage. `provided` = wear the theatre costume during rehearsals, but don't bring your own to the venue — they have the official one. `runtime` = the props department handles it during the actual show; you don't need it in rehearsal.

- "Pack it everywhere" → compile scope
- "Rehearsal room only" → test scope
- "Theatre provides the official costume" → provided scope
- "Props department during the show" → runtime scope

**Where this analogy breaks down:** In Maven, `provided` deps are still available during test execution (unlike the analogy where you'd never have the official costume in rehearsal). This is intentional: tests need to simulate the runtime environment.

---

### 📶 Gradual Depth — Four Levels

**Level 1 — What it is (anyone can understand):**
Scope tells Maven when a library should be available. Test libraries like JUnit should only be available during testing (scope: test). Application server libraries like the Servlet API are available for coding but shouldn't be bundled into your app (scope: provided). Everything else is the default (scope: compile).

**Level 2 — How to use it (junior developer):**
Use `scope: test` for JUnit, Mockito, AssertJ. Use `scope: provided` for Servlet API, JSP API, EJB API (anything your application server provides). Use `scope: runtime` for JDBC drivers (you code against `java.sql.*` interfaces, not the driver directly). Omit scope for everything else (default is compile). After changing scopes, re-run `mvn clean package` and check the artifact size.

**Level 3 — How it works (mid-level engineer):**
When Maven assembles classpaths, it evaluates each dependency's scope to determine inclusion. For a WAR file, the `maven-war-plugin` includes `compile` and `runtime` dependencies in `WEB-INF/lib/`, explicitly excluding `provided` and `test`. Transitive scope combinations are resolved according to a scope mediation table: a `compile` dep of a `runtime` dep becomes `runtime` in your project. Understanding scope mediation explains why `mvn dependency:analyze` sometimes reports "used undeclared" dependencies — you're using a transitive `compile` dep of a `runtime`-scoped dep.

**Level 4 — Why it was designed this way (senior/staff):**
The `provided` scope was introduced specifically for J2EE/Jakarta EE development patterns where the application server is a first-class part of the runtime environment and provides specific API implementations. The design decision to keep `provided` off the runtime classpath (while keeping it on the compile classpath) mirrors the actual deployment topology. The `runtime` scope was added to enable the JDBC driver pattern: code compiles against `java.sql.*` (interface), the actual driver class is loaded by `Class.forName()` at runtime — the driver is needed only when the code runs, not when it compiles.

---

### ⚙️ How It Works (Mechanism)

```
┌────────────────────────────────────────────────────────┐
│         How Maven builds classpaths per scope          │
├────────────────────────────────────────────────────────┤
│                                                        │
│  COMPILE CLASSPATH (used by javac):                    │
│    include: compile-scoped + provided-scoped deps       │
│    exclude: test-scoped + runtime-scoped deps           │
│                                                        │
│  TEST CLASSPATH (used by surefire):                    │
│    include: ALL scopes (compile + test + provided +    │
│             runtime)                                   │
│                                                        │
│  RUNTIME CLASSPATH (used when running the app):        │
│    include: compile-scoped + runtime-scoped deps        │
│    exclude: test-scoped + provided-scoped deps          │
│                                                        │
│  WAR/JAR CONTENTS:                                     │
│    include: compile-scoped + runtime-scoped deps        │
│    exclude: test-scoped + provided-scoped deps          │
│                                                        │
└────────────────────────────────────────────────────────┘
```

**Transitive scope mediation table:**

When project A → B (scope X) → C (scope Y), C appears in A's classpath with this effective scope:

| A→B scope | B→C scope | Effective scope of C in A |
| --------- | --------- | ------------------------- |
| compile   | compile   | compile                   |
| compile   | runtime   | runtime                   |
| compile   | provided  | NOT propagated            |
| compile   | test      | NOT propagated            |
| provided  | compile   | provided                  |
| runtime   | compile   | runtime                   |

---

### 🔄 The Complete Picture — End-to-End Flow

**NORMAL FLOW (Spring Boot WAR on Tomcat):**

```
pom.xml declares:
  spring-boot-starter-web (compile)  ← YOU ARE HERE
  jakarta.servlet-api (provided)
  postgresql (runtime)
  junit-jupiter (test)

mvn package produces target/my-app.war containing:
  WEB-INF/lib/spring-boot-starter-web.jar ✓ (compile)
  WEB-INF/lib/postgresql.jar ✓ (runtime)
  [jakarta.servlet-api.jar ABSENT] ✓ (provided — Tomcat supplies)
  [junit-jupiter.jar ABSENT] ✓ (test — development only)

Tomcat deploys WAR:
  Loads WEB-INF/lib/ → runtime classpath
  Provides jakarta.servlet-api from its own lib/
  No class conflicts → application starts cleanly
```

**FAILURE PATH:**

```
jakarta.servlet-api declared as compile (wrong scope)
  → bundled in WEB-INF/lib/
  → Tomcat also provides servlet-api from its own classpath
  → ClassCastException: two versions of HttpServlet
  → Application fails to start
```

**WHAT CHANGES AT SCALE:**
In microservices deployed as fat JARs (Spring Boot executable JAR), all dependencies use compile/runtime scope since there's no application server. The `provided` scope is relevant primarily for WAR deployments and Lambda functions (where the Lambda runtime provides specific AWS SDK classes).

---

### 💻 Code Example

**Example 1 — Correct scope assignment for common libraries:**

```xml
<dependencies>

  <!-- Spring Boot web: needs everywhere → compile (default) -->
  <dependency>
    <groupId>org.springframework.boot</groupId>
    <artifactId>spring-boot-starter-web</artifactId>
    <version>3.2.0</version>
  </dependency>

  <!-- Test libraries: test scope -->
  <dependency>
    <groupId>org.junit.jupiter</groupId>
    <artifactId>junit-jupiter</artifactId>
    <version>5.10.1</version>
    <scope>test</scope>
  </dependency>
  <dependency>
    <groupId>org.mockito</groupId>
    <artifactId>mockito-core</artifactId>
    <version>5.8.0</version>
    <scope>test</scope>
  </dependency>

  <!-- App server provides: provided scope -->
  <dependency>
    <groupId>jakarta.servlet</groupId>
    <artifactId>jakarta.servlet-api</artifactId>
    <version>6.0.0</version>
    <scope>provided</scope>
  </dependency>

  <!-- JDBC driver: runtime scope -->
  <!-- Code uses java.sql.*, not org.postgresql.* directly -->
  <dependency>
    <groupId>org.postgresql</groupId>
    <artifactId>postgresql</artifactId>
    <version>42.7.1</version>
    <scope>runtime</scope>
  </dependency>

</dependencies>
```

**Example 2 — Verify what ends up in the WAR:**

```bash
# List contents of the WAR's WEB-INF/lib/
unzip -l target/my-app.war | grep WEB-INF/lib/

# postgresql.jar should be present (runtime)
# jakarta.servlet-api.jar should be ABSENT (provided)
# junit-jupiter.jar should be ABSENT (test)
```

---

### ⚖️ Comparison Table

| Scope    | Typical Libraries        | Bundled? | Transitive? | Key Question                    |
| -------- | ------------------------ | -------- | ----------- | ------------------------------- |
| compile  | Spring, Jackson, Guava   | ✓        | ✓           | "My app needs this to run"      |
| test     | JUnit, Mockito, AssertJ  | ✗        | ✗           | "I only need this to test"      |
| provided | Servlet API, EJB API     | ✗        | ✗           | "Container provides this"       |
| runtime  | JDBC drivers, SLF4J impl | ✓        | ✓           | "Loaded dynamically at runtime" |

---

### ⚠️ Common Misconceptions

| Misconception                                              | Reality                                                                                                                         |
| ---------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------- |
| `provided` means the library is not available during tests | `provided` deps ARE on the test classpath — tests can compile and run code that uses them                                       |
| `runtime` deps can't be used in source code                | They can, but compile will fail — this enforces the pattern of coding to interfaces (`java.sql.DataSource`) not implementations |
| Default scope is `runtime`                                 | Default scope is `compile` — the most permissive option                                                                         |
| `test` scope dependencies are still in the final WAR       | `test` scope deps are never in the final artifact — they're development-only                                                    |

---

### 🚨 Failure Modes & Diagnosis

**`ClassNotFoundException` for a class you're sure exists**

**Root Cause:** Dependency has `runtime` or `test` scope but your code tries to use it at compile time.

**Fix:** Change scope to `compile`, or (better) verify your code is using an abstraction interface rather than the concrete implementation class.

---

**`ClassCastException: X cannot be cast to X` (same class, different cast)**

**Root Cause:** Servlet API (or similar) was bundled (wrong `compile` scope) AND provided by the container — two different ClassLoader instances loaded the same class.

**Fix:** Change the conflicting dependency's scope to `provided`.

---

### 🔗 Related Keywords

**Prerequisites:** `Maven Dependencies`, `pom.xml`, `Maven Overview`

**Builds On This:** `Transitive Dependencies`, `Dependency Exclusion`, `Dependency Convergence`

**Related Patterns:** `Transitive Dependencies`, `Maven Dependencies`, `Maven Repository`

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ compile  │ Always available; bundled (default scope)     │
│ test     │ Test-only; NOT bundled                        │
│ provided │ Compile+test; NOT bundled (container has it)  │
│ runtime  │ Runtime+test; NOT on compile path; bundled    │
├──────────┼──────────────────────────────────────────────  │
│ RULE     │ Servlet API → provided                       │
│ RULE     │ JUnit/Mockito → test                         │
│ RULE     │ JDBC Driver → runtime                        │
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** You're building a Spring Boot application deployed as a fat JAR (not a WAR). Does the `provided` scope for the Servlet API still make sense? What scope should the Servlet API have in a Spring Boot executable JAR project, and why does Spring Boot's starter parent handle this automatically?

**Q2.** Library A (compile scope) depends on Library C (runtime scope). When your project declares Library A, what scope does Library C appear as in your transitive dependency graph? Now what if Library A depended on Library C with `provided` scope — would C appear in your project at all?
