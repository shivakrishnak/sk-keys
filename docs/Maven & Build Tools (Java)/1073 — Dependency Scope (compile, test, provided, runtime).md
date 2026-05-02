---
layout: default
title: "Dependency Scope (compile, test, provided, runtime)"
parent: "Maven & Build Tools (Java)"
nav_order: 1073
permalink: /maven-build/dependency-scope/
number: "1073"
category: Maven & Build Tools (Java)
difficulty: ★★☆
depends_on: "Maven Dependencies, pom.xml"
used_on: "Transitive Dependencies, Maven Lifecycle"
tags: #maven, #dependency-scope, #classpath, #compile-scope, #test-scope, #provided-scope
---

# 1073 — Dependency Scope (compile, test, provided, runtime)

`#maven` `#dependency-scope` `#classpath` `#compile-scope` `#test-scope` `#provided-scope`

⚡ TL;DR — **Dependency scope** controls when a dependency is available on the classpath and whether it's included in the final artifact. The four main scopes: `compile` (everywhere; default), `test` (tests only; not in JAR), `provided` (compile time; not bundled; server provides), `runtime` (runtime/tests; not compile; e.g., JDBC drivers). Correct scoping prevents classpath pollution, reduces JAR size, and avoids runtime conflicts.

| #1073           | Category: Maven & Build Tools (Java)     | Difficulty: ★★☆ |
| :-------------- | :--------------------------------------- | :-------------- |
| **Depends on:** | Maven Dependencies, pom.xml              |                 |
| **Used by:**    | Transitive Dependencies, Maven Lifecycle |                 |

---

### 📘 Textbook Definition

**Dependency scope** in Maven: a declaration on each `<dependency>` that controls three things: (1) **classpath availability** — which classpath(s) the dependency appears on (compile, runtime, test); (2) **transitivity** — whether the dependency is passed to consumers of your artifact; (3) **packaging inclusion** — whether the JAR is bundled in the final artifact (WAR/fat JAR). Available scopes: **compile** (default — available on compile, runtime, and test classpath; included in final artifact; transitive); **test** (available only on test classpath; NOT included; NOT transitive); **provided** (available on compile and test classpath; NOT included in final artifact; NOT transitive — container provides it); **runtime** (available on runtime and test classpath, NOT compile classpath; included in final artifact; transitive); **system** (like `provided` but references a specific filesystem path; avoid — breaks portability); **import** (used only in `<dependencyManagement>` to import a BOM). Scope affects the classpaths used for: `javac` (compile classpath), the JVM when running tests (test classpath), and the JVM when running the packaged application (runtime classpath).

---

### 🟢 Simple Definition (Easy)

Scope answers: "where is this library needed?"

- `compile` (default): everywhere — compile, test, and when running
- `test`: only when testing — JUnit, Mockito, Testcontainers
- `provided`: compile only — Servlet API (Tomcat provides it; don't bundle it)
- `runtime`: only when running — PostgreSQL driver (your code uses `java.sql.*`, not PostgreSQL classes directly)

Wrong scope → wrong behavior: using `provided` for something that isn't provided at runtime → `ClassNotFoundException`. Using `compile` for a test library → it ships in your production JAR unnecessarily.

---

### 🔵 Simple Definition (Elaborated)

Understanding scope requires understanding the three separate classpaths Maven manages:

1. **Compile classpath** (`javac`): what's available when compiling `src/main/java`. You reference class names from this.
2. **Runtime classpath** (running the app / running the JAR): what's available when the JVM actually runs. Includes everything needed at runtime.
3. **Test classpath**: runtime classpath + test-specific extras (JUnit, Mockito, Testcontainers).

Scope matrix:

- `compile`: all three classpaths ✓
- `provided`: compile + test ✓, runtime ✗ (provided externally)
- `runtime`: runtime + test ✓, compile ✗ (not needed for compilation)
- `test`: test ✓ only

**Transitivity** is the other dimension: if your library has a `compile` scope dependency on Jackson, your consumers automatically get Jackson (transitive). If your library has a `test` scope dependency on JUnit, your consumers do NOT get JUnit — test dependencies are never transitive.

---

### 🔩 First Principles Explanation

```
SCOPE EFFECT ON CLASSPATHS:

  Scope       Compile  Runtime  Test  Transitive  In Final JAR
  ─────────────────────────────────────────────────────────────
  compile     ✓        ✓        ✓     YES         YES
  provided    ✓        ✗        ✓     NO          NO
  runtime     ✗        ✓        ✓     YES         YES
  test        ✗        ✗        ✓     NO          NO
  system      ✓        ✓        ✓     YES         NO (filesystem ref)

  Notes:
  - "In Final JAR": means in Spring Boot fat JAR / WAR lib/
  - compile-scope deps of your deps → compile scope for you (transitive)
  - runtime-scope deps of your deps → runtime scope for you (transitive)
  - provided-scope deps of your deps → NOT transitive (you must declare if needed)
  - test-scope deps of your deps → NOT transitive (never)

SCOPE EXAMPLES WITH RATIONALE:

  1. SPRING BOOT STARTER WEB → compile (default)
  <dependency>
    <groupId>org.springframework.boot</groupId>
    <artifactId>spring-boot-starter-web</artifactId>
    <!-- no scope = compile -->
  </dependency>
  WHY: Your code IMPORTS Spring classes (@RestController, @GetMapping).
       The JVM needs Spring at runtime to run.
       Tests need Spring for @SpringBootTest.
       → compile scope (everywhere)

  2. JUNIT 5 / MOCKITO → test
  <dependency>
    <groupId>org.junit.jupiter</groupId>
    <artifactId>junit-jupiter</artifactId>
    <scope>test</scope>
  </dependency>
  WHY: Test code imports @Test, @Mock. Production code never imports JUnit.
       The production JAR should NOT contain JUnit (waste of space, wrong).
       → test scope (test only; not in JAR)

  3. SERVLET API → provided
  <dependency>
    <groupId>jakarta.servlet</groupId>
    <artifactId>jakarta.servlet-api</artifactId>
    <scope>provided</scope>
  </dependency>
  WHY: Your code compiles against HttpServletRequest (needs compile classpath).
       BUT: Tomcat/WildFly bundles its own servlet-api.
       If you also bundle it in your WAR → classloader conflict.
       → provided scope (compile; not in WAR)

  4. LOMBOK → provided
  <dependency>
    <groupId>org.projectlombok</groupId>
    <artifactId>lombok</artifactId>
    <scope>provided</scope>
  </dependency>
  WHY: Lombok is an annotation processor — it generates code at compile time.
       No Lombok classes are referenced at runtime (the generated code is plain Java).
       → provided scope (used during compilation; not at runtime)

  NOTE: Lombok annotations (@Data, @Builder) are available at compile time because
  Lombok is on the compile classpath. At runtime, only the GENERATED code runs.

  5. POSTGRESQL DRIVER → runtime
  <dependency>
    <groupId>org.postgresql</groupId>
    <artifactId>postgresql</artifactId>
    <scope>runtime</scope>
  </dependency>
  WHY: Your code uses javax.sql.DataSource and java.sql.* (from JDK — always available).
       You NEVER import org.postgresql.* in your code (you use the JDBC interface).
       The PostgreSQL driver registers itself via ServiceLoader at runtime.
       If you put it on compile classpath by accident, nothing breaks, but it's bad practice
       — it tempts developers to directly import PostgreSQL classes (coupling to implementation).
       → runtime scope (runtime only; not compile)

  6. SLF4J API → compile; SLF4J IMPLEMENTATION → runtime
  <!-- API: your code imports Logger, LoggerFactory -->
  <dependency>
    <groupId>org.slf4j</groupId>
    <artifactId>slf4j-api</artifactId>
    <!-- compile scope: you import from it -->
  </dependency>
  <!-- Implementation: loaded at runtime via ServiceLoader -->
  <dependency>
    <groupId>ch.qos.logback</groupId>
    <artifactId>logback-classic</artifactId>
    <scope>runtime</scope>  <!-- or omit and let Spring Boot manage it -->
  </dependency>
  WHY: Classic API/SPI pattern: compile against the interface (SLF4J API),
       provide the implementation at runtime (Logback).
       Prevents code from depending on a specific logging implementation.

SCOPE TRANSITIVITY DETAILS:

  When YOUR project (A) depends on library B with scope X,
  and B depends on library C with scope Y:

  B's scope for C:   compile  test  provided  runtime
  Your A's scope X:
  ────────────────────────────────────────────────────
  compile            compile  -     -         runtime
  provided           provided -     -         provided
  runtime            runtime  -     -         runtime
  test               test     -     -         test

  KEY RULE: provided and test dependencies are NEVER transitive.
  If B uses Lombok (provided), A does NOT get Lombok transitively.
  A must declare Lombok itself if it uses it.

COMMON SCOPE MISTAKES:

  ❌ JUnit in compile scope: ships in production JAR; waste of space + wrong
  ❌ Servlet API in compile scope: bundled in WAR → classloader conflict with Tomcat
  ❌ PostgreSQL driver in compile scope: couples code to specific DB (temptation to import)
  ❌ Test-only library in compile scope: available in production classpath (security concern)
  ❌ lombok in compile scope (without provided): not harmful but imprecise
```

---

### ❓ Why Does This Exist (Why Before What)

Different build phases need different sets of libraries. Compilation needs APIs; runtime needs implementations; testing needs mocking frameworks and test data builders that shouldn't ship to production. Without scope, every library would be on every classpath and bundled in every artifact: JUnit in your production JAR, servlet-api causing classloader conflicts in Tomcat, unused test libraries increasing attack surface. Scope is the mechanism for applying the principle of least privilege to the build: each library is available ONLY where it's needed.

---

### 🧠 Mental Model / Analogy

> **Dependency scope is like access cards in a building**: `compile` = master key (access everywhere — construction site, offices, server room). `test` = temporary contractor badge (access during testing/construction only; expired when building opens). `provided` = borrowed equipment (you use the forklift during construction; when done, you return it — the building's own forklift handles operations). `runtime` = night security badge (not needed during business hours/construction; only at night/runtime). Wrong badge in wrong place = either security breach (test library in production) or doors that won't open (`ClassNotFoundException`).

---

### 🔄 How It Connects (Mini-Map)

```
Each dependency has rules about where it's available
        │
        ▼
Dependency Scope ◄── (you are here)
(compile / test / provided / runtime controls classpath placement)
        │
        ├── Maven Dependencies: scope is an attribute on each dependency
        ├── Transitive Dependencies: scope affects what propagates to consumers
        ├── Maven Lifecycle: different phases use different classpaths
        └── pom.xml: <scope> element in each <dependency>
```

---

### 💻 Code Example

```xml
<dependencies>
  <!-- Spring Boot Web: compile (default) - code imports Spring classes -->
  <dependency>
    <groupId>org.springframework.boot</groupId>
    <artifactId>spring-boot-starter-web</artifactId>
  </dependency>

  <!-- Test framework: test scope only -->
  <dependency>
    <groupId>org.springframework.boot</groupId>
    <artifactId>spring-boot-starter-test</artifactId>
    <scope>test</scope>
  </dependency>

  <!-- Lombok: annotation processor; code generated at compile; not needed at runtime -->
  <dependency>
    <groupId>org.projectlombok</groupId>
    <artifactId>lombok</artifactId>
    <scope>provided</scope>
  </dependency>

  <!-- PostgreSQL driver: JDBC interface used at compile; driver loaded at runtime -->
  <dependency>
    <groupId>org.postgresql</groupId>
    <artifactId>postgresql</artifactId>
    <scope>runtime</scope>
  </dependency>

  <!-- H2 in-memory DB for tests: test scope -->
  <dependency>
    <groupId>com.h2database</groupId>
    <artifactId>h2</artifactId>
    <scope>test</scope>
  </dependency>
</dependencies>
```

---

### ⚠️ Common Misconceptions

| Misconception                                              | Reality                                                                                                                                                                                                                                                                                                                                  |
| ---------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `provided` scope prevents Maven from downloading the JAR   | Maven downloads `provided` scope JARs into `~/.m2` and puts them on the compile classpath. `provided` means "don't bundle in the final artifact" — it does NOT mean "don't download." The compilation still needs the JAR to resolve types.                                                                                              |
| `runtime` scope dependencies can't be used at compile time | Correct — `runtime` scope specifically removes the dependency from the compile classpath. This is intentional: if your code compiles without it, it shouldn't need it on the compile classpath. Using `runtime` for a JDBC driver enforces that your code only uses the standard `java.sql` API, not vendor-specific PostgreSQL classes. |
| Scope is only about the final JAR size                     | Scope affects three things: classpath availability (compile vs runtime), artifact inclusion (in JAR or not), and transitivity (whether consumers inherit this dependency). Getting the scope wrong can cause `ClassNotFoundException`, class conflicts, or expose test libraries to production code — not just JAR size issues.          |

---

### 🔗 Related Keywords

- `Maven Dependencies` — scope is an attribute on each declared dependency
- `Transitive Dependencies` — scope rules control what propagates transitively
- `pom.xml` — `<scope>` element in `<dependency>` declarations
- `Maven Lifecycle` — different phases use different classpaths based on scope
- `Dependency Exclusion` — remove unwanted transitive dependencies regardless of scope

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ SCOPE        COMPILE  RUNTIME  TEST  IN JAR  TRANSITIVE │
│ compile✓     ✓        ✓        ✓     YES     YES        │
│ provided     ✓        ✗        ✓     NO      NO         │
│ runtime      ✗        ✓        ✓     YES     YES        │
│ test         ✗        ✗        ✓     NO      NO         │
├──────────────────────────────────────────────────────────┤
│ USE CASES:                                              │
│ provided → Lombok, Servlet API (container provides)    │
│ runtime  → JDBC drivers, SLF4J implementations         │
│ test     → JUnit, Mockito, Testcontainers, H2          │
│ compile  → Spring, Jackson, your business libraries    │
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** The SLF4J pattern (API in compile scope, implementation in runtime scope) is the textbook example of the Dependency Inversion Principle applied to build management. Your code depends on the `slf4j-api` abstraction; the `logback-classic` implementation is swappable at deployment time (runtime scope). How does this pattern apply to other Java abstractions? Consider: `javax.sql.DataSource` (API) vs `postgresql` driver (runtime), `jakarta.persistence` (API) vs `hibernate-core` (runtime). What are the limits of this pattern — when DOES your code need to directly depend on an implementation?

**Q2.** The `provided` scope is commonly used in WAR deployments (classic app server: Tomcat, WildFly). But in Spring Boot fat JAR deployments (embedded Tomcat), you do NOT use `provided` for Tomcat — Spring Boot embeds Tomcat and it's part of the fat JAR. The `spring-boot-starter-tomcat` is `compile` scope by default. When deploying a Spring Boot app to an external Tomcat (WAR file), you must switch `spring-boot-starter-tomcat` to `provided`. How does the Maven profile system handle this dual-deployment requirement (fat JAR for containers, WAR for app servers) from the same `pom.xml`?
