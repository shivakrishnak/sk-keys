---
layout: default
title: "Maven Lifecycle (validate, compile, test, package, install, deploy)"
parent: "Maven & Build Tools (Java)"
nav_order: 1068
permalink: /maven-build/maven-lifecycle/
number: "1068"
category: Maven & Build Tools (Java)
difficulty: ★★☆
depends_on: "Maven Overview, pom.xml"
used_by: "Maven Goals, Maven Plugins, Maven Phases, CI-CD pipelines"
tags: #maven, #lifecycle, #build-phases, #compile, #test, #package, #deploy
---

# 1068 — Maven Lifecycle (validate, compile, test, package, install, deploy)

`#maven` `#lifecycle` `#build-phases` `#compile` `#test` `#package` `#deploy`

⚡ TL;DR — Maven defines three built-in lifecycles: **default** (build), **clean**, and **site**. The default lifecycle has 23 ordered phases; the key ones are: `validate → compile → test → package → verify → install → deploy`. Running any phase executes ALL preceding phases. Plugins bind goals to phases: `maven-compiler-plugin:compile` binds to `compile`; `maven-surefire-plugin:test` binds to `test`. Understanding the lifecycle explains why `mvn package` also runs tests (because `test` precedes `package`).

| #1068           | Category: Maven & Build Tools (Java)                      | Difficulty: ★★☆ |
| :-------------- | :-------------------------------------------------------- | :-------------- |
| **Depends on:** | Maven Overview, pom.xml                                   |                 |
| **Used by:**    | Maven Goals, Maven Plugins, Maven Phases, CI-CD pipelines |                 |

---

### 📘 Textbook Definition

**Maven Build Lifecycle**: a well-defined sequence of phases that describes the process of building and distributing an artifact. Maven has three built-in lifecycles: (1) **default** (handles project build and deployment — 23 phases), (2) **clean** (handles project cleaning — 3 phases: pre-clean, clean, post-clean), (3) **site** (handles creation of the project's documentation — 4 phases). A **phase** is a step in the lifecycle; it has no inherent behavior of its own — it becomes meaningful when **plugin goals** are bound to it. Built-in plugin bindings (for `jar` packaging): `process-resources` → `maven-resources-plugin:resources`; `compile` → `maven-compiler-plugin:compile`; `test` → `maven-surefire-plugin:test`; `package` → `maven-jar-plugin:jar`; `install` → `maven-install-plugin:install`; `deploy` → `maven-deploy-plugin:deploy`. Key rule: **invoking a phase invokes all preceding phases in sequence**. `mvn package` = validate + initialize + generate-sources + process-sources + generate-resources + process-resources + compile + process-classes + generate-test-sources + process-test-sources + generate-test-resources + process-test-resources + test-compile + process-test-classes + test + prepare-package + package.

---

### 🟢 Simple Definition (Easy)

Maven's default lifecycle is a conveyor belt: `validate → compile → test → package → install → deploy`. Each step builds on the previous. Running `mvn package` starts the conveyor belt and runs EVERY step up to `package` (including compile and test). You can't skip steps (unless you use flags like `-DskipTests`). This is intentional: you shouldn't be able to deploy without first compiling and testing.

---

### 🔵 Simple Definition (Elaborated)

The lifecycle is Maven's answer to "what does building a project mean?" It defines a universal contract:

- **validate**: is the POM valid? Are all required info present?
- **compile**: compile `src/main/java` → `target/classes`
- **test**: compile `src/test/java` + run tests with Surefire
- **package**: bundle `target/classes` into `target/myapp.jar`
- **verify**: run integration tests, quality checks (Checkstyle, SpotBugs)
- **install**: copy JAR to `~/.m2/repository` (available to other local projects)
- **deploy**: upload JAR + POM to remote repository (Nexus/Artifactory) for team sharing

The real power: plugins can ADD goals to any phase. The `spring-boot-maven-plugin` adds its `repackage` goal to the `package` phase — after `maven-jar-plugin:jar` runs, Spring Boot's plugin creates a fat JAR with all dependencies included. No configuration needed by the developer — it just hooks into the existing lifecycle.

---

### 🔩 First Principles Explanation

```
DEFAULT LIFECYCLE (23 phases, in order):

  1.  validate                ← validate project is correct
  2.  initialize              ← set properties, create dirs
  3.  generate-sources        ← annotation processors, code generators
  4.  process-sources         ← filter/process source files
  5.  generate-resources      ← generate resources
  6.  process-resources       ← copy/filter resources to target/classes
  7.  compile          ★      ← compile src/main/java → target/classes
  8.  process-classes         ← post-process .class files (bytecode enhancement)
  9.  generate-test-sources   ← generate test source code
  10. process-test-sources    ← filter test sources
  11. generate-test-resources ← generate test resources
  12. process-test-resources  ← copy test resources to target/test-classes
  13. test-compile            ← compile src/test/java → target/test-classes
  14. process-test-classes    ← post-process test .class files
  15. test             ★      ← run unit tests (Surefire plugin)
  16. prepare-package         ← prepare for packaging (pre-processing)
  17. package          ★      ← create JAR/WAR → target/myapp.jar
  18. pre-integration-test    ← start servers, set up test environment
  19. integration-test        ← run integration tests (Failsafe plugin)
  20. post-integration-test   ← shut down servers
  21. verify           ★      ← run checks (Checkstyle, SpotBugs, coverage)
  22. install          ★      ← install to ~/.m2/repository
  23. deploy           ★      ← upload to remote repository

  ★ = phases developers commonly invoke directly

CLEAN LIFECYCLE:
  pre-clean → clean → post-clean

  mvn clean: runs pre-clean + clean (deletes target/ directory)

  Combined: mvn clean package
  → runs clean lifecycle: delete target/
  → then runs default lifecycle up to package
  → ensures no stale .class files from previous build

SITE LIFECYCLE:
  pre-site → site → post-site → site-deploy

  mvn site: generates HTML project documentation
  (dependency reports, test reports, Javadoc, etc.)

PLUGIN GOAL BINDINGS (default for jar packaging):

  Phase                   Default bound goal
  ─────────────────────────────────────────────────────────
  process-resources    → maven-resources-plugin:resources
  compile              → maven-compiler-plugin:compile
  process-test-resources → maven-resources-plugin:testResources
  test-compile         → maven-compiler-plugin:testCompile
  test                 → maven-surefire-plugin:test
  package              → maven-jar-plugin:jar
  install              → maven-install-plugin:install
  deploy               → maven-deploy-plugin:deploy

  + spring-boot-maven-plugin adds:
  package              → spring-boot-maven-plugin:repackage
  (runs AFTER maven-jar-plugin:jar creates the thin JAR;
   replaces it with a fat JAR containing all dependencies)

INVOKING PHASES:

  # Single lifecycle phase (runs everything up to that phase):
  mvn compile          ← runs: validate → ... → compile
  mvn test             ← runs: validate → ... → compile → test-compile → test
  mvn package          ← runs: validate → ... → test → package
  mvn verify           ← runs: validate → ... → package → integration-test → verify
  mvn install          ← runs: validate → ... → verify → install
  mvn deploy           ← runs: validate → ... → install → deploy

  # Two lifecycle phases (combined):
  mvn clean package    ← clean lifecycle: clean target/ + default lifecycle: → package

  # Directly invoke a plugin goal (bypasses lifecycle):
  mvn dependency:tree  ← directly runs dependency plugin's 'tree' goal
  mvn spring-boot:run  ← directly runs spring-boot plugin's 'run' goal
  mvn compiler:compile ← directly runs compiler plugin's 'compile' goal

  # Plugin goal vs lifecycle phase:
  # Phase: mvn package → triggers the phase (all preceding phases + bound goals)
  # Goal: mvn jar:jar  → directly runs maven-jar-plugin:jar (skips other phases)
  #                       (may fail if .class files not already compiled)

PHASE SKIPPING (common CI patterns):

  mvn package -DskipTests         ← compile tests but don't run them
  mvn package -Dmaven.test.skip=true  ← don't even compile tests
  mvn deploy -DskipTests          ← full build+deploy without running tests
  mvn package -Dcheckstyle.skip=true  ← skip checkstyle

  WARNING: Skipping tests in CI defeats the purpose of CI.
  Use -DskipTests only for: build performance tests, emergency hotfix
  Never skip tests in the main branch CI pipeline.
```

---

### ❓ Why Does This Exist (Why Before What)

Before Maven, each project had its own Ant build script with arbitrary task names and ordering. One project: `ant compile-java test-code build-jar`. Another: `ant javac run-junit package`. No standard. Maven's lifecycle standardizes the what and when of building: every Maven project compiles in the `compile` phase, tests in `test`, and packages in `package`. This means: CI systems can run `mvn package` on ANY Maven project. IDEs can detect phases. Reports (test results, coverage) are always in known locations. Plugin authors know which phase to bind to. The lifecycle is the common language of the Maven ecosystem.

---

### 🧠 Mental Model / Analogy

> **The Maven lifecycle is like an assembly line quality checkpoint**: a car must pass inspection at each station before moving to the next. You can't paint the car (package) before welding the frame (compile) or running safety checks (test). Running `mvn package` is like saying "take this car to the packaging station" — the conveyor belt automatically runs every prior station first. Maven won't let you skip quality control (test) to get to packaging faster, just as a car factory won't let you skip safety testing to ship a car faster (well, unless you explicitly use `-DskipTests`).

---

### 🔄 How It Connects (Mini-Map)

```
Maven executes build actions in a defined order
        │
        ▼
Maven Lifecycle ◄── (you are here)
(ordered phases; each phase triggers all prior phases)
        │
        ├── Maven Phases: each step in the lifecycle
        ├── Maven Goals: plugin actions bound to phases
        ├── Maven Plugins: provide the goals that implement phases
        ├── pom.xml: plugins bound to phases are configured here
        └── CI-CD: CI runs mvn clean package or mvn verify
```

---

### 💻 Code Example

```xml
<!-- Bind a custom goal to an existing phase in pom.xml -->
<build>
  <plugins>
    <!-- Run OWASP dependency vulnerability check during verify phase -->
    <plugin>
      <groupId>org.owasp</groupId>
      <artifactId>dependency-check-maven</artifactId>
      <version>9.0.4</version>
      <executions>
        <execution>
          <goals>
            <goal>check</goal>    <!-- goal to run -->
          </goals>
          <phase>verify</phase>   <!-- bind to verify phase -->
          <!-- now: mvn verify → runs check + fails if HIGH severity CVEs found -->
        </execution>
      </executions>
      <configuration>
        <failBuildOnCVSS>7</failBuildOnCVSS>  <!-- fail on CVSS score >= 7 -->
      </configuration>
    </plugin>

    <!-- JaCoCo coverage: instrument during test, report during verify -->
    <plugin>
      <groupId>org.jacoco</groupId>
      <artifactId>jacoco-maven-plugin</artifactId>
      <version>0.8.11</version>
      <executions>
        <execution>
          <id>prepare-agent</id>
          <goals><goal>prepare-agent</goal></goals>
          <!-- default phase: initialize -->
        </execution>
        <execution>
          <id>report</id>
          <phase>verify</phase>
          <goals><goal>report</goal></goals>
        </execution>
        <execution>
          <id>check</id>
          <phase>verify</phase>
          <goals><goal>check</goal></goals>
          <configuration>
            <rules>
              <rule>
                <limits>
                  <limit>
                    <counter>LINE</counter>
                    <value>COVEREDRATIO</value>
                    <minimum>0.80</minimum>  <!-- fail if <80% line coverage -->
                  </limit>
                </limits>
              </rule>
            </rules>
          </configuration>
        </execution>
      </executions>
    </plugin>
  </plugins>
</build>
```

---

### ⚠️ Common Misconceptions

| Misconception                                       | Reality                                                                                                                                                                                                                                                                                          |
| --------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| Phases do something by themselves                   | Phases have no inherent behavior — they're just ordered slots. Behavior comes from plugin goals bound to phases. An empty phase does nothing. The `compile` phase only compiles code because `maven-compiler-plugin:compile` is bound to it by default (for `jar` packaging).                    |
| `mvn install` is needed to use a dependency locally | Only if your project is a library that OTHER local projects depend on. For a standalone application, `mvn package` is sufficient. `mvn install` puts the JAR in `~/.m2` so other Maven projects on the same machine can depend on it.                                                            |
| `mvn clean` runs before every build                 | No — `mvn clean` is a separate invocation. `mvn package` does NOT automatically clean. This means stale `.class` files from deleted source files can remain in `target/`. In CI, always use `mvn clean package`. Locally, `mvn package` is faster (incremental) but may have stale class issues. |

---

### 🔗 Related Keywords

- `Maven Phases` — the individual steps within the lifecycle
- `Maven Goals` — plugin actions bound to phases
- `Maven Plugins` — provide the goals that implement lifecycle phases
- `pom.xml` — where plugin-to-phase bindings are configured
- `Maven Overview` — the overall Maven tool that executes the lifecycle

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ DEFAULT LIFECYCLE KEY PHASES:                           │
│ validate → compile → test → package → verify → install → deploy │
│                                                         │
│ COMMANDS:                                               │
│   mvn clean package    → clean + build + test + jar    │
│   mvn clean verify     → + integration tests + checks  │
│   mvn clean install    → + install to ~/.m2            │
│   mvn clean deploy     → + upload to Nexus/Artifactory │
│   mvn package -DskipTests → skip test execution        │
│                                                         │
│ LIFECYCLE ORDER:                                        │
│   validate < compile < test < package < verify < install < deploy │
│   Running any phase executes ALL preceding phases       │
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** The `verify` phase runs integration tests (via `maven-failsafe-plugin`) and quality checks (Checkstyle, SpotBugs, JaCoCo coverage thresholds). In practice, `mvn verify` can take 20+ minutes for a large project. CI pipelines often run `mvn package -DskipTests` for a fast feedback loop, then `mvn verify` for full validation in a separate CI stage. Design a multi-stage CI pipeline that: (a) fails fast on compile errors (2 min), (b) runs unit tests in parallel (5 min), (c) runs integration tests with Testcontainers (10 min), (d) checks coverage and security. How do you structure this with Maven and GitHub Actions parallel jobs?

**Q2.** Maven Wrapper (`mvnw`) is a shell script (committed to the repo) that downloads and uses a specific Maven version, ensuring all developers and CI systems use the same Maven version. Compare: project using `mvnw` vs relying on the system-installed `mvn`. What problems does Maven Wrapper solve? How is it similar to the concept of lockfiles in npm (`package-lock.json`) and how does it differ? When would you NOT use Maven Wrapper?
