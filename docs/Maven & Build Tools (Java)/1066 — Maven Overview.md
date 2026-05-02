---
layout: default
title: "Maven Overview"
parent: "Maven & Build Tools (Java)"
nav_order: 1066
permalink: /maven-build/maven-overview/
number: "1066"
category: Maven & Build Tools (Java)
difficulty: ★☆☆
depends_on: "JDK, Java Language"
used_by: "pom.xml, Maven Lifecycle, Maven Dependencies, CI-CD pipelines"
tags: #maven, #build-tools, #java, #dependency-management, #project-management
---

# 1066 — Maven Overview

`#maven` `#build-tools` `#java` `#dependency-management` `#project-management`

⚡ TL;DR — **Apache Maven** is the dominant build and dependency management tool for Java projects. It defines a standard project structure, a lifecycle (compile → test → package → deploy), and declarative dependency management via `pom.xml`. Maven resolves dependencies from Maven Central (or private Nexus/Artifactory), downloads them to `~/.m2/repository`, and wires them into the build classpath automatically. Contrast with Gradle (Groovy/Kotlin DSL, more flexible but complex).

| #1066           | Category: Maven & Build Tools (Java)                          | Difficulty: ★☆☆ |
| :-------------- | :------------------------------------------------------------ | :-------------- |
| **Depends on:** | JDK, Java Language                                            |                 |
| **Used by:**    | pom.xml, Maven Lifecycle, Maven Dependencies, CI-CD pipelines |                 |

---

### 📘 Textbook Definition

**Apache Maven**: an open-source build automation and project management tool for Java (and JVM) projects, maintained by the Apache Software Foundation. Core concepts: (1) **Project Object Model (POM)**: the `pom.xml` file declares project metadata, dependencies, plugins, and build configuration; (2) **Convention over Configuration**: Maven defines a standard directory layout (`src/main/java`, `src/test/java`, `target/`) — projects following conventions require minimal configuration; (3) **Build Lifecycle**: ordered phases (validate → compile → test → package → verify → install → deploy) — executing a phase runs all preceding phases; (4) **Dependency Management**: Maven resolves transitive dependencies from configured repositories (Maven Central by default), downloads to local repository (`~/.m2/repository`), and makes them available on the compile/runtime/test classpath; (5) **Plugin architecture**: all build actions (compile, test, package) are performed by plugins bound to lifecycle phases. Maven coordinates (`groupId:artifactId:version`, or GAV) uniquely identify every artifact. Maven is the standard for enterprise Java: Spring Boot, Jakarta EE, and most Java libraries publish to Maven Central.

---

### 🟢 Simple Definition (Easy)

Before Maven: manually download every `.jar` (Spring, Hibernate, Jackson), add them to your project, figure out their transitive dependencies, do it again for each new machine. Maven: you declare `<dependency>spring-boot:3.1.0</dependency>` in `pom.xml`. Maven downloads it + all its dependencies. `mvn package` compiles + tests + creates a JAR. Standard directory structure means everyone knows where `src` is. No more "it works on my machine" for builds.

---

### 🔵 Simple Definition (Elaborated)

Maven solves three problems:

1. **Dependency hell**: manually managing 50 JAR files, their transitive dependencies, and version conflicts. Maven: declare direct dependencies → Maven resolves the full dependency tree automatically.
2. **Build inconsistency**: each developer had a different build script. Maven: standard lifecycle → `mvn package` means the same thing everywhere.
3. **Project structure chaos**: every project had different layouts. Maven: convention → `src/main/java` for source, `src/test/java` for tests, `target/` for output. IDE support, plugins, and CI systems all know this layout.

Maven vs Gradle: Maven is XML-based (verbose but explicit), lifecycle-driven, and rigid but predictable. Gradle is Groovy/Kotlin DSL (concise), task-graph-based, and flexible but has steeper learning curve. Gradle is faster for large multi-module projects (incremental builds, build cache). Maven dominates in enterprise Java; Gradle dominates in Android.

---

### 🔩 First Principles Explanation

```
MAVEN STANDARD DIRECTORY LAYOUT:

  myproject/
  ├── pom.xml                    ← project descriptor
  ├── src/
  │   ├── main/
  │   │   ├── java/              ← application source code
  │   │   │   └── com/example/App.java
  │   │   └── resources/         ← application resources (properties, XMLs)
  │   │       └── application.properties
  │   └── test/
  │       ├── java/              ← test source code
  │       │   └── com/example/AppTest.java
  │       └── resources/         ← test resources
  └── target/                    ← all generated output (add to .gitignore)
      ├── classes/               ← compiled .class files
      ├── test-classes/          ← compiled test .class files
      ├── surefire-reports/      ← test results
      ├── myproject-1.0.0.jar    ← packaged artifact
      └── myproject-1.0.0.jar.original

MAVEN COORDINATES (GAV):

  groupId:artifactId:version
  org.springframework.boot:spring-boot-starter-web:3.1.0
  ├── groupId:    org.springframework.boot  (organization/group)
  ├── artifactId: spring-boot-starter-web   (project/module name)
  └── version:    3.1.0                     (version)

  + optional:
  ├── packaging: jar | war | pom | ear (default: jar)
  └── classifier: sources | javadoc | tests (optional label)

  Stored in local repo: ~/.m2/repository/org/springframework/boot/
                                       spring-boot-starter-web/3.1.0/
                                       spring-boot-starter-web-3.1.0.jar
                                       spring-boot-starter-web-3.1.0.pom

MAVEN ARCHITECTURE:

  pom.xml → Maven → Plugin execution

  Maven resolves plugins (also from Maven Central):
  - maven-compiler-plugin: compiles Java source
  - maven-surefire-plugin: runs JUnit/TestNG tests
  - maven-jar-plugin: packages .class files into JAR
  - maven-install-plugin: installs to ~/.m2
  - maven-deploy-plugin: deploys to remote repository
  - spring-boot-maven-plugin: creates executable fat JAR

  Each plugin has goals; goals are bound to lifecycle phases

COMMON COMMANDS:

  mvn validate         ← check project is correct; all info available
  mvn compile          ← compile src/main/java → target/classes
  mvn test             ← compile + run tests (src/test/java)
  mvn package          ← compile + test + package → target/*.jar
  mvn verify           ← package + integration tests + quality checks
  mvn install          ← verify + install to ~/.m2/repository
  mvn deploy           ← install + upload to remote repository
  mvn clean            ← delete target/ directory
  mvn clean package    ← clean then package (most common in CI)
  mvn clean package -DskipTests  ← skip tests (faster CI)
  mvn dependency:tree  ← show full dependency tree
  mvn dependency:resolve ← download all dependencies
  mvn versions:display-dependency-updates  ← show available updates

MULTI-MODULE PROJECTS:

  parent/
  ├── pom.xml              ← parent POM: manages versions + common config
  ├── api/
  │   └── pom.xml          ← child module
  ├── service/
  │   └── pom.xml          ← child module (depends on api)
  └── web/
      └── pom.xml          ← child module (depends on service)

  mvn clean package from parent: builds all modules in dependency order
```

---

### ❓ Why Does This Exist (Why Before What)

Before Maven (pre-2004), Java build tools were Ant (imperative XML scripts — you wrote every build step manually, no dependency management) or manual. Maven introduced declarative build description: describe WHAT your project is, not HOW to build it. The conventions (standard directories, lifecycle) enabled the ecosystem: IDEs like IntelliJ IDEA auto-detect Maven projects, CI tools know how to run `mvn package`, and plugins are reusable across all Maven projects without project-specific configuration.

---

### 🧠 Mental Model / Analogy

> **Maven is like a franchise franchise system for Java builds**: every McDonald's (Maven project) has the same kitchen layout (directory structure), the same menu items made the same way (lifecycle phases), and sources ingredients from the same supplier network (Maven Central). You don't need to explain to a new employee where the fryer is — convention means they already know. The franchise owner (Maven) coordinates suppliers (dependency management) and ensures every location (machine) produces consistent results.

---

### 🔄 How It Connects (Mini-Map)

```
Need to build Java projects consistently with managed dependencies
        │
        ▼
Maven Overview ◄── (you are here)
(build + dependency management tool)
        │
        ├── pom.xml: the project descriptor Maven reads
        ├── Maven Lifecycle: the ordered build phases Maven executes
        ├── Maven Plugins: how Maven performs each build step
        ├── Maven Dependencies: how Maven resolves and downloads JARs
        └── CI-CD Pipeline: CI runs mvn clean package to build/test
```

---

### 💻 Code Example

```xml
<!-- Minimal Spring Boot Maven project pom.xml -->
<?xml version="1.0" encoding="UTF-8"?>
<project xmlns="http://maven.apache.org/POM/4.0.0"
         xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
         xsi:schemaLocation="http://maven.apache.org/POM/4.0.0
         https://maven.apache.org/xsd/maven-4.0.0.xsd">
    <modelVersion>4.0.0</modelVersion>

    <!-- Inherit Spring Boot defaults -->
    <parent>
        <groupId>org.springframework.boot</groupId>
        <artifactId>spring-boot-starter-parent</artifactId>
        <version>3.2.0</version>
    </parent>

    <!-- Project coordinates (GAV) -->
    <groupId>com.example</groupId>
    <artifactId>my-api</artifactId>
    <version>1.0.0-SNAPSHOT</version>
    <packaging>jar</packaging>

    <properties>
        <java.version>17</java.version>
    </properties>

    <dependencies>
        <dependency>
            <groupId>org.springframework.boot</groupId>
            <artifactId>spring-boot-starter-web</artifactId>
        </dependency>
        <dependency>
            <groupId>org.springframework.boot</groupId>
            <artifactId>spring-boot-starter-test</artifactId>
            <scope>test</scope>
        </dependency>
    </dependencies>

    <build>
        <plugins>
            <plugin>
                <groupId>org.springframework.boot</groupId>
                <artifactId>spring-boot-maven-plugin</artifactId>
            </plugin>
        </plugins>
    </build>
</project>
```

---

### ⚠️ Common Misconceptions

| Misconception                               | Reality                                                                                                                                                                                                                                                                   |
| ------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Maven downloads dependencies on every build | Maven downloads each dependency version ONCE to `~/.m2/repository` (the local cache). Subsequent builds use the local cache — no network required. Only new or updated dependencies require a download. In CI, the `.m2` directory is typically cached between runs.      |
| `mvn package` runs all tests                | Yes — `package` phase includes the `test` phase. To skip tests: `mvn package -DskipTests`. To compile tests but not run: `mvn package -Dmaven.test.skip=false -DskipTests=true`.                                                                                          |
| Maven is being replaced by Gradle           | Both coexist. Maven is still the majority in enterprise Java (Spring ecosystem, Jakarta EE). Gradle dominates Android and Kotlin projects. Many shops use Maven for backend Java and Gradle for Android/Kotlin. Migration is possible but non-trivial for large projects. |

---

### 🔗 Related Keywords

- `pom.xml` — the Maven project descriptor that Maven reads
- `Maven Lifecycle` — the ordered phases Maven executes
- `Maven Dependencies` — how Maven resolves and caches JARs
- `Maven Plugins` — how Maven performs each build action
- `JDK` — Maven requires a JDK to compile Java source

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ COORDINATES: groupId:artifactId:version (GAV)           │
│ LOCAL CACHE: ~/.m2/repository                           │
│ COMMANDS:                                               │
│   mvn clean package      → full build + test           │
│   mvn clean package -DskipTests → build only           │
│   mvn dependency:tree    → show dep tree               │
│   mvn install            → build + add to local cache  │
├──────────────────────────────────────────────────────────┤
│ STANDARD DIRS:                                          │
│   src/main/java      → source code                     │
│   src/test/java      → tests                           │
│   src/main/resources → config files                    │
│   target/            → all output (gitignore this)     │
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** Maven SNAPSHOT versions (e.g., `1.0.0-SNAPSHOT`) are special: they're not immutable — the same `1.0.0-SNAPSHOT` can be re-deployed with different content. Maven re-downloads SNAPSHOTs periodically (daily by default) even if cached. In a microservices environment where Team A's service depends on Team B's `api:1.0.0-SNAPSHOT`, what problems can SNAPSHOTs cause in CI? When should you use SNAPSHOT vs a release version? How do SNAPSHOTs interact with reproducible builds?

**Q2.** `mvn install` installs to the local `~/.m2/repository`. In a multi-developer team, each developer has their own local repo. When multiple CI agents build in parallel, they each have a local repo too (or share one). What problems arise with shared Maven local repos in CI (concurrent writes, partial downloads, corrupted cache)? How do enterprise CI systems (GitHub Actions cache, Artifactory, Nexus) solve this?
