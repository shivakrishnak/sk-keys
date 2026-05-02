---
layout: default
title: "Transitive Dependencies"
parent: "Maven & Build Tools (Java)"
nav_order: 1074
permalink: /maven-build/transitive-dependencies/
number: "1074"
category: Maven & Build Tools (Java)
difficulty: ★★☆
depends_on: "Maven Dependencies, Dependency Scope"
used_by: "Dependency Exclusion, pom.xml"
tags: #maven, #transitive-dependencies, #dependency-mediation, #classpath, #version-conflict
---

# 1074 — Transitive Dependencies

`#maven` `#transitive-dependencies` `#dependency-mediation` `#classpath` `#version-conflict`

⚡ TL;DR — **Transitive dependencies** are the dependencies of your dependencies — pulled in automatically by Maven. You declare Spring Boot; Maven also pulls in Tomcat, Jackson, SLF4J, and 50+ more. Convenient, but creates risks: version conflicts (two deps need different versions of the same library), unexpected classpath bloat, and security vulnerabilities in libraries you didn't know you had. Tools: `mvn dependency:tree` to see them all; `<exclusions>` to remove unwanted ones; `<dependencyManagement>` to override versions.

| #1074 | Category: Maven & Build Tools (Java) | Difficulty: ★★☆ |
|:---|:---|:---|
| **Depends on:** | Maven Dependencies, Dependency Scope | |
| **Used by:** | Dependency Exclusion, pom.xml | |

---

### 📘 Textbook Definition

**Transitive dependencies**: dependencies that your direct dependencies themselves depend on, resolved automatically by Maven. When you declare a dependency, Maven reads that dependency's POM file to find its dependencies, then reads those POMs, recursively building a **dependency tree**. Example: declaring `spring-boot-starter-web:3.2.0` (1 dependency) results in Maven resolving ~70 transitive dependencies (Tomcat, Jackson, Spring Framework modules, SLF4J, Logback, etc.). **Dependency mediation**: when the same artifact appears multiple times in the tree at different versions, Maven applies the "nearest-definition" rule — the version declared closest to the root of the dependency tree (fewest hops) wins. Ties (same depth): first-declared wins. **Scope propagation**: `compile`-scope deps propagate transitively as `compile`; `runtime`-scope deps propagate as `runtime`; `test` and `provided` deps do NOT propagate transitively. **Optional dependencies**: a library can mark a dependency as `<optional>true</optional>` — consumers do not inherit it transitively (they must declare it themselves if needed). **Dependency tree inspection**: `mvn dependency:tree` shows the full tree; `mvn dependency:analyze` finds undeclared/unused dependencies.

---

### 🟢 Simple Definition (Easy)

You add Spring Boot to your project. Spring Boot needs Tomcat, Tomcat needs some logging library, that logging library needs something else. Without transitive dependencies, you'd have to manually find and add every library in the chain. Maven reads the "what I need" list of each library recursively and adds everything automatically. The downside: you might end up with 100+ JARs on your classpath, including some you didn't know about and some with security vulnerabilities.

---

### 🔵 Simple Definition (Elaborated)

Transitive dependencies are both Maven's superpower and its primary source of problems:

**Superpower**: declare `spring-boot-starter-data-jpa` → Maven pulls in Hibernate, Spring Data JPA, JDBC, Spring ORM, Bean Validation, and all their dependencies. You get a working JPA stack with one `<dependency>` declaration.

**Problems**:
1. **Version conflicts**: dep-A needs `jackson:2.12`; dep-B needs `jackson:2.15`. Maven picks one (nearest wins). Wrong choice → `NoSuchMethodError` at runtime.
2. **Security vulnerabilities**: you depend on library A; A depends on B (old version with CVE). Security scanners find vulnerabilities in B — but you didn't explicitly add B.
3. **Classpath pollution**: a 5-line utility library brings in 50 transitive deps you don't need.
4. **Undeclared direct usage**: your code imports classes from a transitive dep (not declared directly). If that transitive dep is removed/updated → compile error.

---

### 🔩 First Principles Explanation

```
DEPENDENCY TREE VISUALIZATION:

  mvn dependency:tree output for a Spring Boot project:
  
  com.example:my-service:jar:1.0.0
  ├── org.springframework.boot:spring-boot-starter-web:jar:3.2.0:compile
  │   ├── org.springframework.boot:spring-boot-starter:jar:3.2.0:compile
  │   │   ├── org.springframework.boot:spring-boot:jar:3.2.0:compile
  │   │   ├── org.springframework.boot:spring-boot-autoconfigure:jar:3.2.0:compile
  │   │   └── org.springframework.boot:spring-boot-starter-logging:jar:3.2.0:compile
  │   │       ├── ch.qos.logback:logback-classic:jar:1.4.11:compile
  │   │       │   ├── ch.qos.logback:logback-core:jar:1.4.11:compile
  │   │       │   └── org.slf4j:slf4j-api:jar:2.0.7:compile
  │   │       └── ...
  │   ├── org.springframework.boot:spring-boot-starter-tomcat:jar:3.2.0:compile
  │   │   ├── org.apache.tomcat.embed:tomcat-embed-core:jar:10.1.16:compile
  │   │   └── ...
  │   ├── com.fasterxml.jackson.core:jackson-databind:jar:2.15.3:compile
  │   │   ├── com.fasterxml.jackson.core:jackson-annotations:jar:2.15.3:compile
  │   │   └── com.fasterxml.jackson.core:jackson-core:jar:2.15.3:compile
  │   └── ...
  └── org.springframework.data:spring-data-jpa:jar:3.2.0:compile
      ├── org.hibernate.orm:hibernate-core:jar:6.4.0.Final:compile
      │   └── ... (many more)
      └── ...

DEPENDENCY MEDIATION (version conflict resolution):

  Scenario:
  YOUR PROJECT (root)
  ├── dep-A:1.0 → depends on jackson-databind:2.12.0
  └── dep-B:1.0 → depends on jackson-databind:2.15.0
  
  Both at depth 2 (same distance from root) → FIRST DECLARED WINS
  If dep-A declared before dep-B → jackson-databind:2.12.0 chosen
  
  dep-B was compiled against 2.15.0 features → runtime NoSuchMethodError!
  
  FIX 1: Declare the version you need directly (depth 1 wins):
  YOUR PROJECT (root)
  ├── jackson-databind:2.15.0  ← declared directly! depth=1
  ├── dep-A:1.0 → jackson:2.12 ← depth 2, loses to your direct declaration
  └── dep-B:1.0 → jackson:2.15 ← depth 2, same version → OK
  
  FIX 2: Use <dependencyManagement> to pin the version (even without declaring the dep directly):
  <dependencyManagement>
    <dependencies>
      <dependency>
        <groupId>com.fasterxml.jackson.core</groupId>
        <artifactId>jackson-databind</artifactId>
        <version>2.15.0</version>
      </dependency>
    </dependencies>
  </dependencyManagement>
  
  dependencyManagement version → always wins (regardless of depth in tree)
  → preferred approach: explicit, doesn't pollute direct dependencies

SCOPE PROPAGATION RULES:

  Your dependency X has scope A. X depends on Y with scope B.
  What scope does Y appear in YOUR project?
  
  B (X→Y scope)  A (your scope of X)  →  Your scope of Y
  ─────────────────────────────────────────────────────────
  compile         compile              →  compile
  compile         test                 →  test
  compile         runtime              →  runtime
  compile         provided             →  provided
  runtime         compile              →  runtime
  runtime         test                 →  test
  test            ANY                  →  NOT propagated (test never transitive)
  provided        ANY                  →  NOT propagated (provided never transitive)
  
  CRITICAL: provided and test are "dead ends" in the dependency tree.
  If spring-boot-starter-web has test-scope dep on H2 → you do NOT get H2.
  Each project must declare its own test dependencies.

OPTIONAL DEPENDENCIES:

  Library B marks dep on Jackson as optional:
  <dependency>
    <groupId>com.fasterxml.jackson.core</groupId>
    <artifactId>jackson-databind</artifactId>
    <optional>true</optional>
  </dependency>
  
  Meaning: "If you use B's Jackson integration, you must declare Jackson yourself."
  Common in: Spring Boot autoconfigure (optional features), utility libraries.
  
  If YOUR code uses B's Jackson support → declare jackson-databind yourself.
  If not → don't declare it; you don't get it (optional = not transitive).

DETECTING UNDECLARED DIRECT USAGE:

  mvn dependency:analyze → output:
  
  [WARNING] Used undeclared dependencies:
    com.fasterxml.jackson.core:jackson-databind:jar:2.15.3:compile
  ← Your code imports Jackson, but you didn't declare it in pom.xml!
  ← You're relying on it as a transitive dep of spring-boot-starter-web
  ← If spring-boot changes its Jackson dep → your code breaks
  
  FIX: Declare jackson-databind directly in your pom.xml
  
  [WARNING] Unused declared dependencies:
    org.apache.commons:commons-lang3:jar:3.13.0:compile
  ← You declared it but your code doesn't import from it
  ← May indicate a leftover dependency (remove to reduce attack surface)

ENFORCING DEPENDENCY CONVERGENCE (no silent version mismatches):

  <!-- maven-enforcer-plugin: fail build if conflicting versions exist -->
  <plugin>
    <groupId>org.apache.maven.plugins</groupId>
    <artifactId>maven-enforcer-plugin</artifactId>
    <executions>
      <execution>
        <id>enforce-convergence</id>
        <goals><goal>enforce</goal></goals>
        <configuration>
          <rules>
            <dependencyConvergence/>  ← fail if any dep has multiple versions in tree
          </rules>
        </configuration>
      </execution>
    </executions>
  </plugin>
  
  With this: if dep-A and dep-B require different Jackson versions → BUILD FAILS
  You MUST resolve the conflict explicitly → prevents silent version mismatch
```

---

### ❓ Why Does This Exist (Why Before What)

Transitive dependency resolution is the mechanism that makes the Java library ecosystem composable. Without it, every library would either: (1) bundle all its dependencies (fat JARs) — causing version conflicts when two fat JARs include the same library; or (2) require consumers to manually declare all transitive requirements. Maven's automatic resolution, combined with `.pom` files published alongside JARs, is what enables the Maven Central ecosystem to work: 500K+ artifacts, each declaring their own dependencies, all composable. The dependency tree resolves everything automatically.

---

### 🧠 Mental Model / Analogy

> **Transitive dependencies are like subcontractors bringing their own tools and those subcontractors having their own subcontractors**: you hire "Spring Boot Construction" (direct dep), who arrives with "Tomcat HVAC" (transitive), "Jackson Electrical" (transitive), and "Logback Plumbing" (transitive). Jackson Electrical has a subcontractor "Core Wiring" (transitive of transitive). You didn't hire them, but they show up because Spring Boot needs them. If both Spring Boot Construction and "Hibernate Foundations" need "Jackson Electrical" at different versions, you have two electricians with different toolkits showing up — Maven picks one (nearest-definition wins), potentially causing issues if the wrong version shows up for the other contractor.

---

### 🔄 How It Connects (Mini-Map)

```
Declaring a dependency automatically brings in its dependencies
        │
        ▼
Transitive Dependencies ◄── (you are here)
(automatically resolved; version mediation applied)
        │
        ├── Maven Dependencies: transitive deps are resolved from their POMs
        ├── Dependency Scope: controls what propagates transitively
        ├── Dependency Exclusion: remove specific transitive dependencies
        └── pom.xml: <dependencyManagement> overrides transitive versions
```

---

### 💻 Code Example

```bash
# See the full dependency tree:
mvn dependency:tree

# Find who brings in a specific library (security audit):
mvn dependency:tree -Dincludes=org.apache.commons:commons-text

# Show only compile-scope dependencies:
mvn dependency:tree -Dscope=compile

# Find and analyze dependency conflicts:
mvn dependency:analyze -Dverbose

# Resolve all dependencies and show their paths:
mvn dependency:resolve

# Show dependencies with their checksums (for security verification):
mvn dependency:resolve -Dclassifier=sha1
```

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| Maven always picks the newest version in a conflict | Maven picks the NEAREST (fewest tree hops from root), not the newest. The closest declaration to your root POM wins. This is often not the newest version. Explicitly declare the version in `<dependencyManagement>` to override this behavior with the version you actually want. |
| You don't need to declare transitive dependencies you use directly | If your code imports classes from a transitive dependency, you SHOULD declare it directly. If the library that brought it in transitively upgrades and removes or changes that dep, your code breaks. Rule: if you import it in your code, declare it in your POM. `mvn dependency:analyze` catches "used undeclared dependencies." |
| `<exclusions>` permanently removes a transitive dependency | `<exclusions>` removes the exclusion only for dependencies pulled through THAT specific parent dependency. If the same artifact is pulled in transitively through a different path, it still appears. `<dependencyManagement>` with the desired version is more reliable for version control across all paths. |

---

### 🔗 Related Keywords

- `Maven Dependencies` — the direct dependencies that have transitive deps
- `Dependency Scope` — controls which scoped deps propagate transitively
- `Dependency Exclusion` — explicitly removes specific transitive dependencies
- `pom.xml` — `<dependencyManagement>` overrides transitive dependency versions
- `Maven Overview` — Maven's resolver walks the dependency tree

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ COMMANDS:                                               │
│   mvn dependency:tree             → see full tree      │
│   mvn dependency:analyze          → find issues        │
│   mvn dependency:tree -Dincludes=groupId:artifactId    │
│                                                         │
│ VERSION CONFLICTS → nearest-definition wins            │
│ FIX: declare version in <dependencyManagement>         │
│                                                         │
│ NOT TRANSITIVE: test scope, provided scope, optional   │
│ ENFORCE CONVERGENCE: maven-enforcer DependencyConvergence│
│                                                         │
│ RULE: if you import it in code → declare it directly   │
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** The Log4Shell vulnerability (CVE-2021-44228, CVSS 10.0) affected `log4j-core:2.x`. Many organizations discovered they were vulnerable because `log4j-core` was a transitive dependency they didn't know they had — brought in by frameworks like Spring, Elasticsearch, or dozens of other libraries. After disclosure, the challenge was: find every place we use log4j-core across all projects. How does `mvn dependency:tree -Dincludes=org.apache.logging.log4j:log4j-core` help? What organizational practices (SBOM — Software Bill of Materials, Dependabot, Snyk) would have detected this before the emergency? How does dependency convergence enforcement help prevent similar incidents?

**Q2.** In a microservices architecture with 50 services sharing a parent POM, the parent manages 200+ dependency versions via `<dependencyManagement>`. Upgrading the parent to update a dependency version means ALL 50 services get the update on their next build. This is convenient for security patches but risky for compatibility (a single parent upgrade might break 10 services). Compare: (a) shared parent POM with centralized dependency management, vs (b) each service managing its own versions with Dependabot PRs, vs (c) a published internal BOM artifact with semantic versioning. What's the right granularity for shared dependency management?
