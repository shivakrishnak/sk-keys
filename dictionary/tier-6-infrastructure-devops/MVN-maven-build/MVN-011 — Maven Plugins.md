---
layout: default
title: "Maven Plugins"
parent: "Maven & Build Tools (Java)"
grand_parent: "Technical Dictionary"
nav_order: 11
permalink: /maven-build/maven-plugins/
id: MVN-011
category: Maven & Build Tools (Java)
difficulty: ★★☆
depends_on: Maven Overview, pom.xml, Maven Lifecycle (validate, compile, test, package, install, deploy), Maven Goals, Maven Phases
used_by: Maven Profiles, Maven Multi-Module Project, Build Performance Optimization
related: Maven Goals, Maven Phases, Maven BOM (Bill of Materials)
tags:
  - maven
  - build-tools
  - java
  - intermediate
  - build
---

# MVN-011 — Maven Plugins

⚡ TL;DR — Maven plugins are JAR packages that provide the executable goals behind every Maven build operation — without plugins, Maven's lifecycle is a skeleton with no muscle; plugins are what actually compile, test, and package your code.

| #1071           | Category: Maven & Build Tools (Java)                                       | Difficulty: ★★☆ |
| :-------------- | :------------------------------------------------------------------------- | :-------------- |
| **Depends on:** | Maven Overview, pom.xml, Maven Lifecycle, Maven Goals, Maven Phases        |                 |
| **Used by:**    | Maven Profiles, Maven Multi-Module Project, Build Performance Optimization |                 |
| **Related:**    | Maven Goals, Maven Phases, Maven BOM (Bill of Materials)                   |                 |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
Maven defines what to do (compile, test, package) but not how to do it. Without a plugin system, Maven would need to hard-code every possible build operation — including operations that don't exist yet (Protobuf generation, container image building, coverage reporting). Hard-coding everything means Maven Core changes for every new build requirement — an unmaintainable monolith.

**THE BREAKING POINT:**
Build needs vary wildly: some projects generate code, others build Docker images, others run Sonar analysis or sign artifacts. No single tool can hard-code all of these. And as technologies evolve, new operations are needed. The build tool must be extensible.

**THE INVENTION MOMENT:**
Maven's plugin architecture separates the framework (lifecycle, dependency resolution) from the work (compilation, testing, packaging). Any team can write a Maven plugin, package it as a JAR, and publish it to Maven Central. Maven downloads and executes it as part of the build. This is why the plugin system was created: to make Maven infinitely extensible without modifying Maven Core.

---

### 📘 Textbook Definition

A **Maven plugin** is a JAR artifact containing one or more Mojos (Maven plain Old Java Objects), each implementing a specific build goal. Plugins are distributed like any other Maven artifact (identified by groupId, artifactId, version), resolved from Maven repositories, and executed by Maven at runtime. Plugins are categorized as: (1) **build plugins** — executed during the build lifecycle; (2) **reporting plugins** — executed during site generation. Maven provides a set of core plugins (compiler, surefire, jar, install, deploy) with default lifecycle bindings; additional plugins are declared in the `<build><plugins>` section of `pom.xml` and can be bound to any lifecycle phase. Plugin configuration is passed via `<configuration>` blocks in the POM.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
Plugins are the engines that power Maven — they contain the code that actually compiles, tests, packages, and deploys your project.

**One analogy:**

> Maven Core is the electrical grid; plugins are the appliances. The grid delivers power (lifecycle orchestration, dependency resolution) to every socket. But to get work done — cook, heat, light — you plug in appliances (plugins). The grid doesn't cook your food; the microwave does. Maven doesn't compile your code; the compiler plugin does.

**One insight:**
Even Maven's built-in operations (compile, test, package) are implemented as plugins. There is no special "Maven compiler" baked into Maven Core — `maven-compiler-plugin` is just a plugin that ships with Maven and is bound to the `compile` phase by default. Everything is a plugin: the built-ins are just pre-configured ones.

---

### 🔩 First Principles Explanation

**CORE INVARIANTS:**

1. Every goal in Maven is provided by a plugin — there are no built-in goals in Maven Core.
2. A plugin is identified by GAV coordinates (groupId:artifactId:version), just like a dependency.
3. Plugin configuration in `pom.xml` is type-safe — parameters match fields in the Mojo class.

**ESSENTIAL BUILT-IN PLUGINS:**

| Plugin    | Artifact ID            | Key Goal                 | Default Phase            |
| --------- | ---------------------- | ------------------------ | ------------------------ |
| Compiler  | maven-compiler-plugin  | compile, testCompile     | compile, test-compile    |
| Surefire  | maven-surefire-plugin  | test                     | test                     |
| Failsafe  | maven-failsafe-plugin  | integration-test, verify | integration-test, verify |
| JAR       | maven-jar-plugin       | jar                      | package                  |
| WAR       | maven-war-plugin       | war                      | package                  |
| Install   | maven-install-plugin   | install                  | install                  |
| Deploy    | maven-deploy-plugin    | deploy                   | deploy                   |
| Clean     | maven-clean-plugin     | clean                    | clean                    |
| Resources | maven-resources-plugin | resources                | process-resources        |
| Shade     | maven-shade-plugin     | shade                    | package                  |

**WRITING A PLUGIN (simplified):**

```java
@Mojo(name = "greet", defaultPhase = LifecyclePhase.VALIDATE)
public class GreetMojo extends AbstractMojo {

    @Parameter(property = "greeting", defaultValue = "Hello")
    private String greeting;

    @Override
    public void execute() throws MojoExecutionException {
        getLog().info(greeting + " from custom plugin!");
    }
}
```

**THE TRADE-OFFS:**

**Gain:** Maven is infinitely extensible; the entire Java/JVM ecosystem's build toolchain is available as plugins.

**Cost:** Plugin version management is manual (unless using a parent BOM); plugin compatibility issues can be hard to debug; XML configuration is verbose compared to Gradle's Kotlin DSL for plugins.

---

### 🧪 Thought Experiment

**SETUP:**
Your company builds gRPC services. Every `.proto` file must be compiled to Java before `javac` can compile the service code.

**WITHOUT A PLUGIN SYSTEM:**
You'd have to run `protoc` manually before running Maven, creating a two-step build process. CI pipelines break because they only know to run `mvn package`. New developers don't know about the manual `protoc` step.

**WITH THE PROTOBUF MAVEN PLUGIN:**

```xml
<plugin>
  <groupId>io.grpc</groupId>
  <artifactId>protoc-gen-grpc-java</artifactId>
  <version>1.58.0</version>
  <!-- bound to generate-sources phase -->
</plugin>
```

Now `mvn package` automatically: generates Java from `.proto` → compiles Java → tests → packages. One command. Zero manual steps. CI and developers use the same process.

**THE INSIGHT:**
Maven's plugin system turns the build tool into a platform. The `.proto` → Java step is just another plugin bound to a phase. Any tool that can be wrapped in a Java Mojo can be part of the Maven lifecycle.

---

### 🧠 Mental Model / Analogy

> Maven plugins are like smartphone apps. The phone (Maven Core) provides the platform: lifecycle management, dependency resolution, file system access, execution model. Apps (plugins) provide the actual functionality: the phone doesn't take photos — the camera app does. You download new apps to get new capabilities. The phone doesn't change; your capabilities expand.

- "Phone OS" → Maven Core
- "App Store" → Maven Central
- "App" → Maven plugin
- "App feature" → plugin goal
- "App settings" → plugin `<configuration>` in pom.xml
- "Default apps installed" → core plugins (compiler, surefire, jar)

**Where this analogy breaks down:** Smartphone apps run independently; Maven plugins execute within the Maven build lifecycle's strict phase sequence and share the same JVM as Maven Core.

---

### 📶 Gradual Depth — Four Levels

**Level 1 — What it is (anyone can understand):**
A Maven plugin is an add-on that teaches Maven how to do new things. The compiler plugin teaches Maven how to compile Java. The surefire plugin teaches Maven how to run tests. You add new plugins to add new build capabilities.

**Level 2 — How to use it (junior developer):**
Add plugins in the `<build><plugins>` section of `pom.xml`. Configure them with `<configuration>` blocks. Set the Java version for the compiler plugin: `<configuration><release>17</release></configuration>`. For plugins not bound to any lifecycle phase by default (e.g., `versions-maven-plugin`), run their goals directly: `mvn versions:display-dependency-updates`.

**Level 3 — How it works (mid-level engineer):**
Maven resolves plugin artifacts the same way it resolves dependencies: by GAV coordinates, from configured repositories. Each plugin's Mojo classes are loaded into a separate ClassRealm (isolated classloader) to prevent plugin dependencies from polluting the build classpath. Parameter injection happens via reflection: Maven reads the Mojo's `@Parameter` annotations and maps POM configuration + system properties to Mojo fields before calling `execute()`.

**Level 4 — Why it was designed this way (senior/staff):**
The ClassRealm isolation for plugin classloading was a hard-won design decision in Maven 3. Maven 2 had plugin classloader leakage — plugins could accidentally use each other's dependencies, causing subtle compatibility bugs. Maven 3's classworld isolation ensures each plugin runs against its own declared dependencies, making plugin behaviour reproducible regardless of what other plugins are present. The trade-off: plugin startup time increases slightly; shared classes (like the Maven API itself) must be loaded in a parent classloader visible to all plugins.

---

### ⚙️ How It Works (Mechanism)

```
┌──────────────────────────────────────────────────────┐
│           Plugin Resolution & Execution              │
├──────────────────────────────────────────────────────┤
│                                                      │
│  pom.xml declares plugin (groupId:artifactId:version)│
│       │                                              │
│       ▼                                              │
│  Maven checks local .m2 cache                        │
│  → download from remote repo if absent               │
│       │                                              │
│       ▼                                              │
│  Plugin loaded into isolated ClassRealm              │
│  (plugin deps isolated from project deps)            │
│       │                                              │
│       ▼                                              │
│  Maven reads plugin.xml (goal → Mojo class mapping)  │
│       │                                              │
│       ▼                                              │
│  For each execution in lifecycle:                    │
│    1. Instantiate Mojo class                         │
│    2. Inject @Parameter fields from:                 │
│       - pom.xml <configuration>                      │
│       - System properties (-Dproperty=value)         │
│       - ${project.*} expressions                     │
│    3. Call Mojo.execute()                            │
│    4. Report success or throw MojoExecutionException │
└──────────────────────────────────────────────────────┘
```

---

### 🔄 The Complete Picture — End-to-End Flow

**NORMAL FLOW (standard jar build):**

```
mvn package
  → compile phase
      → PLUGIN: maven-compiler-plugin ← YOU ARE HERE
         config: <release>17</release>
         → invokes javac → target/classes/
  → test phase
      → PLUGIN: maven-surefire-plugin
         config: <forkCount>1</forkCount>
         → discovers *Test.java → runs → reports
  → package phase
      → PLUGIN: maven-jar-plugin
         config: <archive><manifest>...</manifest></archive>
         → bundles .class + resources → target/app.jar
  → Build SUCCESS
```

**FAILURE PATH:**

```
PLUGIN: maven-compiler-plugin throws MojoExecutionException
  → "Compilation failure: cannot find symbol"
  → Maven prints plugin + goal + error
  → Lifecycle stops immediately
  → Run with -e for full stack trace
```

**WHAT CHANGES AT SCALE:**
In CI environments, plugin JARs are cached in the Maven local repository (often in a Docker layer or CI cache). Without caching, downloading all plugins adds minutes to every build. Plugin versions should be pinned in `<pluginManagement>` to ensure reproducibility across developer machines and CI.

---

### 💻 Code Example

**Example 1 — Configuring the compiler plugin:**

```xml
<build>
  <plugins>
    <plugin>
      <groupId>org.apache.maven.plugins</groupId>
      <artifactId>maven-compiler-plugin</artifactId>
      <version>3.11.0</version>
      <configuration>
        <!-- Use <release> (not <source>/<target>) for modern Java -->
        <release>17</release>
        <!-- Enable preview features (Java 21+ pattern matching, etc.) -->
        <!-- <compilerArgs><arg>--enable-preview</arg></compilerArgs> -->
      </configuration>
    </plugin>
  </plugins>
</build>
```

**Example 2 — Shade plugin for fat JARs:**

```xml
<plugin>
  <groupId>org.apache.maven.plugins</groupId>
  <artifactId>maven-shade-plugin</artifactId>
  <version>3.5.1</version>
  <executions>
    <execution>
      <phase>package</phase>
      <goals><goal>shade</goal></goals>
      <configuration>
        <!-- Set main class in MANIFEST.MF -->
        <transformers>
          <transformer implementation=
"org.apache.maven.plugins.shade.resource.ManifestResourceTransformer">
            <mainClass>com.example.Main</mainClass>
          </transformer>
        </transformers>
      </configuration>
    </execution>
  </executions>
</plugin>
```

**Example 3 — Locking plugin versions in pluginManagement:**

```xml
<!-- In parent pom.xml: governance without activation -->
<build>
  <pluginManagement>
    <plugins>
      <plugin>
        <groupId>org.apache.maven.plugins</groupId>
        <artifactId>maven-compiler-plugin</artifactId>
        <version>3.11.0</version>
      </plugin>
      <plugin>
        <groupId>org.apache.maven.plugins</groupId>
        <artifactId>maven-surefire-plugin</artifactId>
        <version>3.2.2</version>
      </plugin>
    </plugins>
  </pluginManagement>
</build>
```

---

### ⚖️ Comparison Table

| Plugin                | Purpose                     | Phase                    | Notable Config                |
| --------------------- | --------------------------- | ------------------------ | ----------------------------- |
| maven-compiler-plugin | Compile Java sources        | compile, test-compile    | `<release>17</release>`       |
| maven-surefire-plugin | Unit tests                  | test                     | `<forkCount>`, `<parallel>`   |
| maven-failsafe-plugin | Integration tests           | integration-test, verify | Guaranteed teardown           |
| maven-jar-plugin      | Create executable JAR       | package                  | `<mainClass>` in MANIFEST     |
| maven-shade-plugin    | Fat/uber JAR                | package                  | Merges all deps into one JAR  |
| maven-assembly-plugin | Custom distribution archive | package                  | Custom file sets              |
| maven-enforcer-plugin | Enforce build rules         | validate / verify        | Java version, dep convergence |
| maven-release-plugin  | Automate releases           | N/A (direct invocation)  | Version bumping, tagging      |

---

### ⚠️ Common Misconceptions

| Misconception                              | Reality                                                                                                                                 |
| ------------------------------------------ | --------------------------------------------------------------------------------------------------------------------------------------- |
| Maven Core compiles Java                   | `maven-compiler-plugin` compiles Java — Maven Core only orchestrates the lifecycle                                                      |
| Plugin deps end up in your app's classpath | Plugin dependencies are loaded in an isolated ClassRealm; they never appear on the project's compile/runtime classpath                  |
| You must always specify plugin version     | Maven will use a default version from its internal metadata, but this is non-reproducible — always pin versions in `<pluginManagement>` |
| `<pluginManagement>` activates plugins     | It only governs versions; the plugin must also be declared in `<plugins>` to actually run                                               |

---

### 🚨 Failure Modes & Diagnosis

**"Plugin ... not found" or version resolution failure**

**Root Cause:** Plugin not in configured plugin repository, or version doesn't exist.

**Fix:** Check `settings.xml` for plugin repositories; verify version in Maven Central; use `-U` to force update.

---

**Plugin fails with ClassNotFoundException at runtime**

**Root Cause:** Plugin's dependency version conflicts with another plugin's dependency (ClassRealm isolation failure, very rare in Maven 3).

**Fix:** Use `mvn -X` to see ClassRealm loading; check plugin's declared dependencies vs. what's actually available.

---

**Surefire fails with "Could not find forked JVM"**

**Root Cause:** Surefire forks a JVM for test execution; if the JDK is not correctly configured, the fork fails.

**Fix:** Ensure `JAVA_HOME` is set; check `<jvm>` configuration in surefire plugin; use `<forkCount>0</forkCount>` to run in-process (disables isolation but avoids fork issues).

---

### 🔗 Related Keywords

**Prerequisites:** `Maven Overview`, `pom.xml`, `Maven Lifecycle`, `Maven Goals`, `Maven Phases`

**Builds On This:** `Maven Profiles`, `Maven Multi-Module Project`, `Build Performance Optimization`

**Related Patterns:** `Maven Goals`, `Maven Phases`, `Maven BOM (Bill of Materials)`

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ CORE PLUGINS │ compiler, surefire, jar, install, deploy  │
├──────────────┼──────────────────────────────────────────  │
│ FAT JAR      │ maven-shade-plugin                        │
├──────────────┼──────────────────────────────────────────  │
│ INTEGRATION  │ maven-failsafe-plugin                     │
├──────────────┼──────────────────────────────────────────  │
│ GOVERNANCE   │ <pluginManagement> in parent POM          │
├──────────────┼──────────────────────────────────────────  │
│ DESCRIBE     │ mvn help:describe -Dplugin=compiler       │
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** What is the difference between declaring a plugin in `<plugins>` vs `<pluginManagement>`? In a parent POM, how would you use both together to let child modules inherit version governance while activating a plugin only in specific children?

**Q2.** You need integration tests that start a Docker container (PostgreSQL), run against it, and always stop it — even if tests fail. Which Maven plugin and which lifecycle phases would you use, and why does using `maven-failsafe-plugin` give you different teardown guarantees than `maven-surefire-plugin`?
