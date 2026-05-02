---
layout: default
title: "Maven Dependencies"
parent: "Maven & Build Tools (Java)"
nav_order: 1072
permalink: /maven-build/maven-dependencies/
number: "1072"
category: Maven & Build Tools (Java)
difficulty: ★☆☆
depends_on: "pom.xml, Maven Overview"
used_by: "Dependency Scope, Transitive Dependencies, Dependency Exclusion"
tags: #maven, #dependencies, #classpath, #jar, #dependency-resolution
---

# 1072 — Maven Dependencies

`#maven` `#dependencies` `#classpath` `#jar` `#dependency-resolution`

⚡ TL;DR — **Maven dependencies** are the external libraries your project needs, declared in `pom.xml`'s `<dependencies>` section using `groupId:artifactId:version`. Maven downloads them from Maven Central (or a configured private repo), caches them in `~/.m2/repository`, and adds them to the appropriate classpath (compile, test, runtime). Maven also resolves **transitive dependencies** — the dependencies of your dependencies — automatically.

| #1072 | Category: Maven & Build Tools (Java) | Difficulty: ★☆☆ |
|:---|:---|:---|
| **Depends on:** | pom.xml, Maven Overview | |
| **Used by:** | Dependency Scope, Transitive Dependencies, Dependency Exclusion | |

---

### 📘 Textbook Definition

**Maven dependencies**: external artifacts (JARs) required by a project, declared in `pom.xml`'s `<dependencies>` section. Each dependency is identified by Maven coordinates (`groupId`, `artifactId`, `version`) plus an optional `scope` (compile, test, provided, runtime, system, import) and `classifier`. Maven's dependency resolution: (1) reads `pom.xml`; (2) checks local repository (`~/.m2/repository`) for each dependency; (3) downloads missing artifacts from remote repositories (Maven Central by default, plus any configured in `pom.xml` or `settings.xml`); (4) resolves transitive dependencies (reads the `.pom` files of direct dependencies to find their dependencies, recursively); (5) applies dependency mediation (nearest-definition-wins rule for version conflicts); (6) builds the effective classpath per scope. The dependency mechanism eliminates manual JAR management: declaring 5 direct dependencies may pull in 80+ transitive dependencies, all version-compatible and available on the classpath without manual intervention.

---

### 🟢 Simple Definition (Easy)

Instead of downloading `spring-web.jar`, `jackson.jar`, `slf4j.jar`, and 50 more JARs by hand, you declare what you need in `pom.xml`. Maven figures out what each library needs (transitively) and downloads everything automatically. Dependencies are cached in `~/.m2/repository` — you only download each version once. Different types of dependencies go on different classpaths: test libraries only for tests, server-provided libraries not bundled in your JAR.

---

### 🔵 Simple Definition (Elaborated)

Dependencies have a lifecycle in the build:
1. **Declared**: you write `<dependency>spring-boot-starter-web:3.2.0</dependency>`
2. **Resolved**: Maven reads the POM of `spring-boot-starter-web` to find its dependencies (Spring Web, Spring WebMVC, Tomcat, Jackson...) — recursively
3. **Downloaded**: Maven downloads any JARs not in `~/.m2/repository`
4. **Scoped**: Maven puts JARs on the right classpath based on `<scope>`:
   - `compile` (default): compile classpath + runtime classpath + test classpath
   - `test`: test compile + test runtime only (NOT in the final JAR)
   - `provided`: compile only (server provides at runtime: Servlet API, Lombok)
   - `runtime`: runtime + test only (not needed for compile: JDBC driver)

**Dependency conflicts**: two dependencies need different versions of the same library (both need `jackson-databind` but different versions). Maven's nearest-definition rule: whichever version is declared closer to the root of the dependency tree wins. The `<dependencyManagement>` section lets you override this by explicitly declaring the version you want.

---

### 🔩 First Principles Explanation

```xml
<!-- DEPENDENCY DECLARATION EXAMPLES -->

<dependencies>
  <!-- ══════════════════════════════════
       COMPILE SCOPE (default)
       On: compile + runtime + test classpaths
       Included in: JAR/WAR
       ══════════════════════════════════ -->
  <dependency>
    <groupId>org.springframework.boot</groupId>
    <artifactId>spring-boot-starter-web</artifactId>
    <version>3.2.0</version>
    <!-- scope: compile (default; don't need to specify) -->
  </dependency>
  
  <!-- ══════════════════════════════════
       TEST SCOPE
       On: test compile + test runtime classpaths only
       NOT included in production JAR/WAR
       ══════════════════════════════════ -->
  <dependency>
    <groupId>org.springframework.boot</groupId>
    <artifactId>spring-boot-starter-test</artifactId>
    <version>3.2.0</version>
    <scope>test</scope>
  </dependency>
  
  <dependency>
    <groupId>org.testcontainers</groupId>
    <artifactId>postgresql</artifactId>
    <version>1.19.3</version>
    <scope>test</scope>
  </dependency>
  
  <!-- ══════════════════════════════════
       PROVIDED SCOPE
       On: compile classpath only
       NOT included in JAR (container provides it at runtime)
       ══════════════════════════════════ -->
  <dependency>
    <groupId>jakarta.servlet</groupId>
    <artifactId>jakarta.servlet-api</artifactId>
    <version>6.0.0</version>
    <scope>provided</scope>
    <!-- Tomcat/Jetty provides servlet-api at runtime; 
         if included in WAR → classpath conflict -->
  </dependency>
  
  <!-- Lombok: annotation processor; not needed at runtime -->
  <dependency>
    <groupId>org.projectlombok</groupId>
    <artifactId>lombok</artifactId>
    <version>1.18.30</version>
    <scope>provided</scope>
    <!-- Lombok generates code at compile time; not in final JAR -->
  </dependency>
  
  <!-- ══════════════════════════════════
       RUNTIME SCOPE
       On: runtime + test classpaths only
       NOT on compile classpath (code doesn't import from it)
       Included in: final JAR/WAR
       ══════════════════════════════════ -->
  <dependency>
    <groupId>org.postgresql</groupId>
    <artifactId>postgresql</artifactId>
    <version>42.7.0</version>
    <scope>runtime</scope>
    <!-- Code uses javax.sql.DataSource (compile scope) not PostgreSQL classes directly -->
    <!-- PostgreSQL driver loads via JDBC ServiceLoader at runtime -->
  </dependency>
  
  <!-- ══════════════════════════════════
       CLASSIFIER (optional)
       Distinguish multiple artifacts from same GAV
       ══════════════════════════════════ -->
  <dependency>
    <groupId>com.example</groupId>
    <artifactId>my-service</artifactId>
    <version>1.0.0</version>
    <classifier>tests</classifier>   <!-- use the -tests.jar (test classes JAR) -->
    <scope>test</scope>
  </dependency>

  <!-- ══════════════════════════════════
       OPTIONAL (informational only)
       Marks a dependency as optional: consumers don't get it transitively
       ══════════════════════════════════ -->
  <dependency>
    <groupId>com.fasterxml.jackson.core</groupId>
    <artifactId>jackson-databind</artifactId>
    <version>2.16.0</version>
    <optional>true</optional>
    <!-- If YOUR library uses Jackson but doesn't require it
         (e.g., optional JSON serialization), mark optional.
         Consumers must declare jackson-databind themselves to use it. -->
  </dependency>
</dependencies>
```

```
DEPENDENCY RESOLUTION PROCESS:

  1. Read direct dependencies from pom.xml
  2. For each direct dependency, read its .pom file from the registry
  3. Add its dependencies to the dependency tree (transitively)
  4. Apply scope rules:
     compile dep's transitive compile → compile ✓
     compile dep's transitive provided → excluded ✗
     compile dep's transitive test → excluded ✗
     compile dep's transitive runtime → runtime ✓
  5. Version conflict resolution (nearest-definition wins):
     
     YOUR PROJECT
     ├── dep-A:1.0 → requires jackson:2.12
     └── dep-B:2.0 → requires jackson:2.15
     
     Both at the same depth → first one declared wins → jackson:2.12
     (can cause problems if dep-B uses 2.15 features)
     
     Fix: declare jackson:2.15 directly in YOUR pom.xml (closer = wins)
     <dependency>
       <groupId>com.fasterxml.jackson.core</groupId>
       <artifactId>jackson-databind</artifactId>
       <version>2.15.0</version>
     </dependency>

SCOPE CLASSPATH MATRIX:

  Scope       Compile  Runtime  Test
  ─────────────────────────────────────
  compile     ✓        ✓        ✓     (default)
  provided    ✓        ✗        ✓     (server-provided)
  runtime     ✗        ✓        ✓     (JDBC drivers)
  test        ✗        ✗        ✓     (JUnit, Mockito)
  system      ✓        ✓        ✓     (local JAR; avoid)
```

---

### ❓ Why Does This Exist (Why Before What)

Before Maven's dependency system, Java developers manually downloaded JARs, tracked their versions, managed their transitive requirements, and configured IDE classpaths. Adding Spring to a project meant manually downloading Spring + all its dependencies (dozens of JARs) and knowing which versions were compatible. Maven's dependency system automates this: the `.pom` file published with each artifact declares its dependencies, enabling Maven to build the full dependency graph automatically. This is the foundation of the Java ecosystem's modularity — libraries can depend on other libraries, and consumers get everything they need automatically.

---

### 🧠 Mental Model / Analogy

> **Maven dependencies are like a restaurant's supply chain**: you (the project) declare your menu (direct dependencies: "I need chicken and vegetables"). The chicken supplier (Spring Boot) has its own suppliers (Tomcat, Jackson, SLF4J). Maven is your procurement manager who builds the full supply chain automatically — you just say "chicken" and the procurement manager figures out that chicken needs: poultry farm → cold chain → distribution → your restaurant. The local warehouse (`~/.m2`) caches everything so you don't re-order the same items every day.

---

### 🔄 How It Connects (Mini-Map)

```
Project needs external libraries to compile and run
        │
        ▼
Maven Dependencies ◄── (you are here)
(declared in pom.xml; resolved from Maven Central; cached in ~/.m2)
        │
        ├── pom.xml: <dependencies> section declares them
        ├── Dependency Scope: controls which classpath they appear on
        ├── Transitive Dependencies: automatically resolved by Maven
        └── Dependency Exclusion: remove unwanted transitive dependencies
```

---

### 💻 Code Example

```bash
# Show full dependency tree (versions, scopes, transitive):
mvn dependency:tree

# Show dependency tree for a specific scope:
mvn dependency:tree -Dscope=compile

# Find which dependency brings in a specific artifact:
mvn dependency:tree -Dincludes=com.fasterxml.jackson.core:jackson-databind

# Analyze used/unused dependencies:
mvn dependency:analyze

# Download all dependencies (pre-cache for offline/CI):
mvn dependency:resolve

# Build effective classpath string:
mvn dependency:build-classpath

# Clean local cache for a specific artifact (force re-download):
mvn dependency:purge-local-repository -DincludeArtifactIds=spring-web
```

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| `provided` scope means Maven won't download it | Maven DOES download `provided` dependencies (to put on the compile classpath). `provided` just means: don't bundle it in the WAR/JAR, because the runtime container (Tomcat, WildFly) will provide it. The dependency IS downloaded; it just doesn't ship in your artifact. |
| Test-scope dependencies are not on the classpath when running the app | Correct — `test` scope dependencies are ONLY on the classpath during `mvn test` and `mvn verify`. They're not available in the packaged JAR or when running with `mvn spring-boot:run` (which uses runtime scope). If you accidentally put a needed class in test scope, the app will fail with `ClassNotFoundException` at runtime. |
| Adding a dependency always increases JAR size | Only `compile` and `runtime` scope dependencies are included in the final JAR/WAR. `test` and `provided` scope dependencies do NOT increase the final artifact size. Spring Boot's fat JAR includes `compile` + `runtime` scope dependencies. |

---

### 🔗 Related Keywords

- `pom.xml` — where dependencies are declared in `<dependencies>`
- `Dependency Scope` — controls which classpath (compile/test/runtime) the dep appears on
- `Transitive Dependencies` — Maven resolves these automatically from dependency POMs
- `Dependency Exclusion` — remove unwanted transitive dependencies
- `Maven Overview` — the tool that resolves and caches dependencies

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ DECLARATION: <groupId> + <artifactId> + <version>       │
│ CACHE: ~/.m2/repository (download once, reuse)          │
│                                                          │
│ SCOPES:                                                  │
│   compile  → compile + runtime + test (default)         │
│   test     → test compile + test runtime only           │
│   provided → compile only (container provides runtime)  │
│   runtime  → runtime + test only (JDBC drivers)         │
│                                                          │
│ COMMANDS:                                               │
│   mvn dependency:tree    → full dependency tree         │
│   mvn dependency:analyze → find unused/undeclared       │
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** Maven's dependency resolution uses "nearest-definition wins" for version conflicts. This means if two transitive dependencies require different versions, the one declared closer to the root of YOUR project's dependency tree wins — without any warning. You might unknowingly end up with jackson:2.12 (required by dep-A) when dep-B needs 2.15 and crashes at runtime with `NoSuchMethodError`. How do you detect these version conflicts before they cause production issues? What role does `mvn dependency:analyze` vs `mvn dependency:tree` play? How does the `maven-enforcer-plugin` with `DependencyConvergence` rule solve this?

**Q2.** The Maven local repository (`~/.m2/repository`) is a local file system cache. In CI/CD with ephemeral build agents (new Docker container per build), `~/.m2` is empty on each run — Maven downloads everything from Maven Central every build. With a large project and 100 builds/day, this is: (a) slow (every build downloads 500MB), (b) expensive (bandwidth + Maven Central load), (c) fragile (build fails if Maven Central is down). Design a caching strategy using: GitHub Actions cache, Nexus/Artifactory proxy, or ECR/S3 for the Maven repository. What are the cache invalidation challenges? How do SNAPSHOT dependencies complicate this?
