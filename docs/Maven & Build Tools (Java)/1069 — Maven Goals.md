---
layout: default
title: "Maven Goals"
parent: "Maven & Build Tools (Java)"
nav_order: 1069
permalink: /maven-build/maven-goals/
number: "1069"
category: Maven & Build Tools (Java)
difficulty: ★★☆
depends_on: "Maven Lifecycle, Maven Plugins"
used_by: "Maven Phases, CI-CD pipelines"
tags: #maven, #goals, #plugins, #build, #tasks
---

# 1069 — Maven Goals

`#maven` `#goals` `#plugins` `#build` `#tasks`

⚡ TL;DR — A **Maven goal** is a specific task executed by a plugin — the atomic unit of work in Maven. `compiler:compile`, `surefire:test`, `jar:jar`, `spring-boot:run` are goals. Goals can be bound to lifecycle phases (so `mvn package` automatically triggers them) or invoked directly (`mvn dependency:tree`). Each plugin provides one or more goals; understanding goals explains what Maven actually does when you run a lifecycle phase.

| #1069           | Category: Maven & Build Tools (Java) | Difficulty: ★★☆ |
| :-------------- | :----------------------------------- | :-------------- |
| **Depends on:** | Maven Lifecycle, Maven Plugins       |                 |
| **Used by:**    | Maven Phases, CI-CD pipelines        |                 |

---

### 📘 Textbook Definition

**Maven goal**: the finest unit of work in Maven's build system. Goals are provided by **plugins** (Maven plugins are JARs containing Mojo classes — Maven plain Old Java Objects). Each Mojo implements one goal. A goal is referenced as `pluginPrefix:goalName` (e.g., `compiler:compile`) or fully qualified as `groupId:artifactId:version:goalName` (e.g., `org.apache.maven.plugins:maven-compiler-plugin:3.12.0:compile`). Goals have two modes: (1) **bound to a lifecycle phase** — automatically executed when that phase is reached; (2) **invoked directly** — `mvn pluginPrefix:goalName` executes the goal without running lifecycle phases. Goals can be bound to phases in the POM `<build><plugins><executions>` section. Multiple goals from different plugins can be bound to the same phase — they execute in the order they appear in the POM. Plugin prefixes are configured in `plugin.xml` inside the plugin JAR or inferred from the artifactId (`maven-XXX-plugin` → prefix `XXX`, `XXX-maven-plugin` → prefix `XXX`).

---

### 🟢 Simple Definition (Easy)

If Maven lifecycle phases are "departments" (compile, test, package), then goals are the "workers" who actually do the work. `mvn package` visits the compile department → the `compiler:compile` worker compiles code. Then visits the test department → the `surefire:test` worker runs tests. Then visits the package department → the `jar:jar` worker creates the JAR. Goals are the actual executable tasks; phases are just the schedule.

---

### 🔵 Simple Definition (Elaborated)

Goals vs phases: **phases** define WHEN something happens in the build order; **goals** define WHAT actually happens. An empty lifecycle phase (no goals bound) does nothing. The `compile` phase only compiles code because `maven-compiler-plugin:compile` is bound to it.

Direct goal invocation: some goals are useful outside the lifecycle. `mvn dependency:tree` shows the dependency tree — you don't want or need to run compile, test, and package just to see dependencies. Direct invocation runs the goal without triggering any lifecycle phase. `mvn spring-boot:run` starts the Spring Boot app without packaging it into a JAR first.

Plugin prefixes: `mvn compiler:compile` works because Maven knows that `compiler` is the prefix for `maven-compiler-plugin`. This mapping comes from the plugin's metadata. You can always use the full form: `mvn org.apache.maven.plugins:maven-compiler-plugin:3.12.0:compile`.

---

### 🔩 First Principles Explanation

```
GOAL FORMAT:

  Short form: compiler:compile
              ────────┬──────── ─────┬────
              plugin prefix    goal name

  Full form: org.apache.maven.plugins:maven-compiler-plugin:3.12.0:compile

  Plugin prefix resolution:
  compiler → maven-compiler-plugin (convention: maven-XXX-plugin → prefix XXX)
  spring-boot → spring-boot-maven-plugin
  dependency → maven-dependency-plugin
  surefire → maven-surefire-plugin
  jar → maven-jar-plugin

GOALS BOUND BY DEFAULT (jar packaging):

  Phase                Goal
  ─────────────────────────────────────────────────────────────────────
  process-resources    resources:resources
  compile              compiler:compile
  process-test-resources resources:testResources
  test-compile         compiler:testCompile
  test                 surefire:test
  package              jar:jar
  install              install:install
  deploy               deploy:deploy

  Additional (spring-boot-maven-plugin):
  package              spring-boot:repackage  (runs after jar:jar)

USEFUL GOALS TO INVOKE DIRECTLY:

  mvn dependency:tree              ← print full dependency tree (with versions)
  mvn dependency:analyze           ← find unused/undeclared dependencies
  mvn dependency:resolve           ← download all dependencies
  mvn dependency:purge-local-repository ← delete cached deps + re-download

  mvn help:effective-pom           ← show fully resolved POM (with inheritance)
  mvn help:effective-settings      ← show resolved Maven settings
  mvn help:describe -Dplugin=compiler ← describe plugin + all its goals
  mvn help:active-profiles         ← show active profiles

  mvn versions:display-dependency-updates  ← show available version updates
  mvn versions:set -DnewVersion=2.0.0      ← update project version

  mvn spring-boot:run              ← run Spring Boot app without packaging
  mvn spring-boot:build-image      ← build OCI image with Cloud Native Buildpacks

  mvn compiler:compile             ← compile only (without full lifecycle)
  mvn compiler:testCompile         ← compile tests only

  mvn surefire:test                ← run tests (without compile phase; .class must exist)
  mvn failsafe:integration-test    ← run integration tests only

  mvn clean:clean                  ← delete target/

MULTIPLE GOALS IN ONE INVOCATION:

  mvn clean:clean compiler:compile surefire:test
  ← runs exactly these three goals in order; no lifecycle

  mvn clean package
  ← clean lifecycle (clean:clean) + default lifecycle up to package
  ← NOT the same as: mvn clean:clean package (which would fail: no lifecycle phase "package")

CUSTOM GOAL BINDING IN pom.xml:

  <build>
    <plugins>
      <plugin>
        <groupId>org.apache.maven.plugins</groupId>
        <artifactId>maven-antrun-plugin</artifactId>
        <executions>
          <execution>
            <id>print-build-info</id>
            <phase>compile</phase>       ← bind to compile phase
            <goals>
              <goal>run</goal>           ← antrun:run goal
            </goals>
            <configuration>
              <target>
                <echo>Compiling ${project.artifactId} ${project.version}</echo>
              </target>
            </configuration>
          </execution>
        </executions>
      </plugin>
    </plugins>
  </build>

MOJO (Maven Plain Old Java Object):

  A Mojo is a Java class that implements one Maven goal

  @Mojo(name = "compile", defaultPhase = LifecyclePhase.COMPILE)
  public class CompilerMojo extends AbstractMojo {
      @Parameter(defaultValue = "${project}")
      private MavenProject project;

      public void execute() throws MojoExecutionException {
          // compile source files
      }
  }

  Maven downloads the plugin JAR, instantiates the Mojo, runs execute()
```

---

### ❓ Why Does This Exist (Why Before What)

Goals separate the WHAT (compile code, run tests, create JAR) from the WHEN (which lifecycle phase). This separation enables: (1) running tasks outside the lifecycle for utility/debugging (`dependency:tree`); (2) binding the same goal to different phases in different contexts; (3) multiple goals bound to the same phase (jar:jar + spring-boot:repackage both in `package`); (4) third-party plugins hooking into any lifecycle phase without Maven core changes. The plugin model makes Maven extensible: any tool (Checkstyle, SpotBugs, Docker buildpack, Terraform) can provide Maven goals and integrate with the standard lifecycle.

---

### 🧠 Mental Model / Analogy

> **Goals are like individual recipes in a cookbook; lifecycle phases are the meal plan**: "Wednesday dinner" (the `package` phase) specifies WHEN to cook. The "roast chicken recipe" (the `jar:jar` goal) specifies WHAT to cook. You can follow Wednesday's meal plan (run the lifecycle) and the cookbook tells you which recipe to execute. Or you can flip straight to the roast chicken recipe and make it anytime (`mvn jar:jar`). The cookbook (plugin) can be used standalone or integrated into the meal plan (lifecycle binding).

---

### 🔄 How It Connects (Mini-Map)

```
Plugin provides goals; goals do the actual work
        │
        ▼
Maven Goals ◄── (you are here)
(specific tasks; bound to phases or invoked directly)
        │
        ├── Maven Plugins: provide the goal implementations (Mojo classes)
        ├── Maven Phases: goals are bound to phases to integrate with lifecycle
        ├── Maven Lifecycle: running a phase triggers all bound goals
        └── pom.xml: <executions> section binds additional goals to phases
```

---

### 💻 Code Example

```bash
# Explore what goals are available for a plugin
mvn help:describe -Dplugin=compiler -Ddetail

# Describe a specific goal
mvn help:describe -Dplugin=compiler -Dmojo=compile -Ddetail

# Common direct goal invocations:

# Check for dependency updates:
mvn versions:display-dependency-updates

# Find unused dependencies:
mvn dependency:analyze

# Show what files would be in the final JAR:
mvn dependency:build-classpath -DincludeScope=runtime

# Run app without packaging (dev):
mvn spring-boot:run

# Build Docker image with Buildpacks (no Dockerfile needed):
mvn spring-boot:build-image -Dspring-boot.build-image.imageName=myorg/myapp:latest
```

---

### ⚠️ Common Misconceptions

| Misconception                                                                    | Reality                                                                                                                                                                                                                                                                                                                                                 |
| -------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `mvn compiler:compile` and `mvn compile` do the same thing                       | `mvn compile` runs the lifecycle UP TO compile (including validate, initialize, generate-sources, process-resources). `mvn compiler:compile` runs ONLY the compiler plugin's compile goal, skipping all preceding lifecycle phases. If resources haven't been processed yet, `compiler:compile` may work but the build won't have up-to-date resources. |
| A goal can only be bound to one lifecycle phase                                  | A goal can be bound to any lifecycle phase — even multiple times in different `<execution>` blocks with different `<id>` values. A single goal can be configured to run multiple times in the same build (e.g., compile with different configurations).                                                                                                 |
| Plugin goals run in alphabetical order when multiple are bound to the same phase | Goals bound to the same phase run in the order they appear in the POM's `<plugins>` list. Within a plugin, `<executions>` run in declaration order. Spring Boot's `repackage` goal runs after `jar:jar` because the spring-boot-maven-plugin appears after the jar plugin in the effective POM.                                                         |

---

### 🔗 Related Keywords

- `Maven Plugins` — JARs that contain goal implementations (Mojos)
- `Maven Phases` — the lifecycle slots that goals are bound to
- `Maven Lifecycle` — the ordered sequence of phases
- `pom.xml` — where additional goal-to-phase bindings are configured
- `Maven Overview` — the overall build system that executes goals

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ GOAL FORMAT: pluginPrefix:goalName                      │
│   compiler:compile  | surefire:test  | jar:jar          │
│   dependency:tree   | spring-boot:run                   │
│                                                         │
│ INVOKE DIRECTLY (no lifecycle):                         │
│   mvn dependency:tree    → dep tree                     │
│   mvn help:effective-pom → resolved POM                 │
│   mvn spring-boot:run    → run app                      │
│   mvn versions:display-dependency-updates               │
│                                                         │
│ GOALS vs PHASES:                                        │
│   Phase = WHEN (lifecycle slot)                         │
│   Goal  = WHAT (actual task implementation)             │
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** `mvn dependency:analyze` identifies "used but undeclared" and "declared but unused" dependencies. A dependency is "used but undeclared" when your code imports a class from a transitive dependency (a dependency of your dependency) rather than declaring it directly. This works at runtime but breaks if the transitive dependency's version changes or is removed. Why is this a build fragility? How do you enforce that all used dependencies are explicitly declared? What is the "dependency management" strategy for a team to prevent this drift over time?

**Q2.** The `maven-failsafe-plugin` runs integration tests (by convention, `*IT.java` files) in `integration-test` and `post-integration-test` phases, while `maven-surefire-plugin` runs unit tests (`*Test.java`) in the `test` phase. The key difference: Failsafe is designed to NOT fail the build immediately if tests fail — it continues to `post-integration-test` (to shut down any started servers/containers) THEN fails in `verify`. Surefire fails immediately. Why is this design difference important? What real problem does it prevent?
