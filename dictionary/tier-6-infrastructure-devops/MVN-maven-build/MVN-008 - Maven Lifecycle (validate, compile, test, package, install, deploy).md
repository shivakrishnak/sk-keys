---
version: 2
layout: default
title: "Maven Lifecycle (validate, compile, test, package, install, deploy)"
parent: "Maven & Build Tools"
grand_parent: "Technical Dictionary"
nav_order: 8
permalink: /maven-build/maven-lifecycle/
id: MVN-008
category: Maven & Build Tools (Java)
difficulty: ★★☆
depends_on: Maven Overview, pom.xml, Maven Plugins
used_by: Maven Goals, Maven Phases, Maven Profiles, Build Performance Optimization
related: Maven Goals, Maven Phases, Maven Plugins
tags:
  - maven
  - build-tools
  - java
  - intermediate
  - build
---

# MVN-008 - Maven Lifecycle (validate, compile, test, package, install, deploy)

⚡ TL;DR - Maven's build lifecycle is an ordered sequence of phases (validate → compile → test → package → install → deploy) that every build follows automatically - run any phase and all prior phases execute first.

| #1068           | Category: Maven & Build Tools (Java)                      | Difficulty: ★★☆ |
| :-------------- | :-------------------------------------------------------- | :-------------- |
| **Depends on:** | Maven Overview, pom.xml, Maven Plugins                    |                 |
| **Used by:**    | Maven Goals, Maven Phases, Build Performance Optimization |                 |
| **Related:**    | Maven Goals, Maven Phases, Maven Plugins                  |                 |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
With Ant, every project had to manually chain build steps: "first run compile, then run test, then run package." Developers would skip steps (run `package` without `test`), produce broken artifacts, forget to validate the project structure before compiling, or deploy untested code. Every project had its own opinion about which steps happened in which order.

**THE BREAKING POINT:**
Without a standard execution order, "mvn package" means different things in different projects. Some run tests; some don't. Some validate inputs; some skip it. The build becomes a black box that only the original author understands. Importantly, it becomes easy to accidentally skip critical steps like testing.

**THE INVENTION MOMENT:**
Maven's build lifecycle was invented to make the order of build operations a convention, not a choice. When you run `mvn package`, you always get: validate → initialize → generate-sources → compile → test → package. No steps can be skipped unless explicitly opted out. This is why the Maven lifecycle exists.

---

### 📘 Textbook Definition

The **Maven Build Lifecycle** is a well-defined sequence of named phases that describe the stages of a project's build and deployment process. Maven defines three built-in lifecycles: (1) **default** (handles project deployment: validate through deploy); (2) **clean** (handles project cleaning: pre-clean, clean, post-clean); (3) **site** (handles site documentation generation). The default lifecycle's principal phases - validate, compile, test, package, verify, install, deploy - are executed in strict sequential order. When a user invokes a phase, Maven automatically executes all preceding phases in the same lifecycle. Phases themselves perform no work directly; they are execution checkpoints to which plugin goals are bound.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
Run any Maven phase and everything before it runs automatically - the lifecycle is a guaranteed build sequence.

**One analogy:**

> Maven's lifecycle is like a car production line. To reach the "paint" station, the car must have already passed through "frame assembly," "engine install," and "wiring." You can't run "paint" on a car that hasn't been assembled. Maven ensures the same: you can't package uncompiled code.

**One insight:**
The lifecycle's value is in what it prevents, not just what it does. You cannot deploy unpackaged code, package untested code (without explicit override), or compile without first validating the project structure. The lifecycle encodes correctness constraints as execution order.

---

### 🔩 First Principles Explanation

**CORE INVARIANTS:**

1. Phases execute in a fixed, immutable order within each lifecycle.
2. Running phase N automatically triggers phases 1 through N−1.
3. Phases are empty by default - work is performed by plugin goals bound to phases.

**THE THREE LIFECYCLES:**

```
┌─────────────────────────────────────────────────────┐
│ CLEAN LIFECYCLE                                     │
│  pre-clean → clean → post-clean                     │
├─────────────────────────────────────────────────────┤
│ DEFAULT LIFECYCLE (principal phases)                │
│  validate                                           │
│  initialize                                         │
│  generate-sources                                   │
│  process-sources                                    │
│  generate-resources                                 │
│  process-resources                                  │
│  compile                          ← javac           │
│  process-classes                                    │
│  generate-test-sources                              │
│  process-test-sources                               │
│  generate-test-resources                            │
│  process-test-resources                             │
│  test-compile                     ← javac (tests)   │
│  process-test-classes                               │
│  test                             ← surefire        │
│  prepare-package                                    │
│  package                          ← jar/war plugin  │
│  pre-integration-test                               │
│  integration-test                                   │
│  post-integration-test                              │
│  verify                           ← checksum etc    │
│  install                          ← local .m2       │
│  deploy                           ← remote repo     │
├─────────────────────────────────────────────────────┤
│ SITE LIFECYCLE                                      │
│  pre-site → site → post-site → site-deploy          │
└─────────────────────────────────────────────────────┘
```

**DERIVED DESIGN:**
Phases are bound to plugin goals by Maven's default bindings for each packaging type (`jar`, `war`, `pom`). For `jar` packaging:

- `compile` → `maven-compiler-plugin:compile`
- `test` → `maven-surefire-plugin:test`
- `package` → `maven-jar-plugin:jar`
- `install` → `maven-install-plugin:install`
- `deploy` → `maven-deploy-plugin:deploy`

**THE TRADE-OFFS:**

**Gain:** Guaranteed execution order; impossible to deploy without testing (unless overridden); standardised build sequence understood by every Maven user.

**Cost:** The lifecycle is fixed - you cannot reorder phases. Adding custom steps requires binding a plugin goal to one of the existing phase slots, which can feel awkward if the phase name doesn't exactly match the step's purpose.

---

### 🧪 Thought Experiment

**SETUP:**
A developer wants to deploy a new version of their service. They've made changes and just want to "ship it fast."

**WHAT HAPPENS WITHOUT A FIXED LIFECYCLE:**
The developer calls the deploy step directly, skipping tests. The untested code reaches production. A NullPointerException introduced in the last commit crashes 10% of user requests. The fix takes 2 hours to deploy.

**WHAT HAPPENS WITH MAVEN'S LIFECYCLE:**
The developer runs `mvn deploy`. Maven automatically runs: validate → compile → test → package → verify → install → deploy. The test phase catches the NullPointerException. The build fails. The developer fixes it locally before it reaches production. Total time: 10 minutes.

**THE INSIGHT:**
The lifecycle's sequential constraint is a safety mechanism. Its value is precisely that you cannot skip prior phases without explicit intent (`-DskipTests` requires a conscious decision). Accidental omissions are prevented by design.

---

### 🧠 Mental Model / Analogy

> Maven's lifecycle is like a rocket launch checklist. Every stage must complete before the next begins: fuelling → systems check → launch sequence → orbit insertion. You cannot skip "systems check" just because you're in a hurry - the rocket will fail.

- "Fuelling" → `validate` + `compile`: project is structurally sound, code compiles
- "Systems check" → `test`: all tests pass before proceeding
- "Rocket assembly complete" → `package`: deployable artifact created
- "Launchpad transfer" → `install`: artifact available to other local projects
- "Launch" → `deploy`: artifact pushed to remote repository

**Where this analogy breaks down:** A rocket launch is truly linear; Maven allows running `mvn clean deploy -DskipTests` to explicitly skip tests - unlike a real rocket, you can override the lifecycle if you deliberately accept the risk.

---

### 📶 Gradual Depth - Four Levels

**Level 1 - What it is (anyone can understand):**
Maven has a fixed sequence of build steps. When you ask for step 5, steps 1–4 run automatically. This means your code is always compiled before it's tested, and always tested before it's packaged.

**Level 2 - How to use it (junior developer):**
The six commands you'll use most: `mvn validate` (check pom.xml), `mvn compile` (compile source), `mvn test` (run tests), `mvn package` (create JAR/WAR), `mvn install` (copy to local `.m2`), `mvn deploy` (push to remote repo). Each one runs all prior phases first. Combine with `clean`: `mvn clean package` erases `target/` then packages.

**Level 3 - How it works (mid-level engineer):**
Phases are named checkpoints. All actual work is done by plugin goals bound to phases. The binding is packaging-type-dependent: a `jar` project binds different goals than a `pom` project (which is an aggregator - no jar plugin). You can bind custom plugin goals to any phase in `pom.xml`, including `generate-sources` for code generation or `pre-integration-test` for starting a database before integration tests.

**Level 4 - Why it was designed this way (senior/staff):**
The separation of lifecycle phases from plugin goals was a key design decision. Phases provide a stable extension point: if you need to run a code generator before compilation, you bind it to `generate-sources` - the phase name is stable even if the plugin changes. This made Maven's lifecycle an extension contract, not an implementation detail. The cost of this design: lifecycle phases have fixed, opinionated names that don't map cleanly to every build scenario (hence why Gradle abandoned the concept in favour of a task graph).

---

### ⚙️ How It Works (Mechanism)

```
┌─────────────────────────────────────────────────────┐
│    mvn package - what actually happens              │
├─────────────────────────────────────────────────────┤
│                                                     │
│  Phase: validate                                    │
│    └─ (no default binding for jar packaging)        │
│                                                     │
│  Phase: compile                                     │
│    └─ maven-compiler-plugin:compile                 │
│       → reads src/main/java/**/*.java               │
│       → javac with Java version from pom.xml        │
│       → outputs .class files to target/classes/     │
│                                                     │
│  Phase: test-compile                                │
│    └─ maven-compiler-plugin:testCompile             │
│       → reads src/test/java/**/*.java               │
│       → outputs to target/test-classes/             │
│                                                     │
│  Phase: test                                        │
│    └─ maven-surefire-plugin:test                    │
│       → discovers *Test.java, *Tests.java           │
│       → runs in forked JVM                         │
│       → writes reports to target/surefire-reports/  │
│       → fails build on test failure                 │
│                                                     │
│  Phase: package                                     │
│    └─ maven-jar-plugin:jar                          │
│       → bundles target/classes/ + META-INF/         │
│       → outputs target/my-app-1.0.jar               │
└─────────────────────────────────────────────────────┘
```

---

### 🔄 The Complete Picture - End-to-End Flow

**NORMAL FLOW:**

```
Developer: mvn deploy
  → validate (project structure OK)
  → compile (sources → .class)
  → test (unit tests pass)         ← YOU ARE HERE (tests gate deploy)
  → package (JAR created)
  → verify (integration checks)
  → install (copied to ~/.m2)
  → deploy (uploaded to Nexus)
  → Build SUCCESS
```

**FAILURE PATH:**

```
test phase: surefire reports failures
  → "BUILD FAILURE" - Tests run: 120, Failures: 2, Errors: 1
  → lifecycle stops immediately
  → package/install/deploy phases NEVER run
  → artifact NOT deployed
  → Fix tests → re-run mvn deploy
```

**WHAT CHANGES AT SCALE:**
In multi-module projects, the lifecycle runs once per module in dependency order. With `-T 4`, independent modules' lifecycles execute in parallel. The `deploy` phase pushes to a Nexus/Artifactory repository rather than Maven Central, making artifacts available to other teams immediately.

---

### 💻 Code Example

**Example 1 - Common lifecycle commands:**

```bash
# Run all phases up to and including 'compile'
mvn compile

# Run all phases up to and including 'test'
mvn test

# Create JAR (validate + compile + test + package)
mvn package

# Install to local .m2 (all phases through install)
mvn install

# Full build: clean first, then deploy to remote repository
mvn clean deploy

# Skip test EXECUTION (tests still compile)
mvn package -DskipTests

# Skip test compilation AND execution (dangerous)
mvn package -Dmaven.test.skip=true

# Run only from a specific phase (advanced - rare use)
# Note: Maven always starts from the beginning of the lifecycle
```

**Example 2 - Binding a custom goal to a lifecycle phase:**

```xml
<build>
  <plugins>
    <!-- Run integration tests in the integration-test phase -->
    <plugin>
      <groupId>org.apache.maven.plugins</groupId>
      <artifactId>maven-failsafe-plugin</artifactId>
      <executions>
        <execution>
          <goals>
            <!-- bound to: integration-test + verify phases -->
            <goal>integration-test</goal>
            <goal>verify</goal>
          </goals>
        </execution>
      </executions>
    </plugin>
  </plugins>
</build>
```

---

### ⚖️ Comparison Table

| Phase    | What Runs                    | Output            | Common Failure     |
| -------- | ---------------------------- | ----------------- | ------------------ |
| validate | POM structure check          | Nothing (or fail) | Invalid pom.xml    |
| compile  | `javac` on src/main/java     | target/classes/   | Compilation error  |
| test     | Surefire runs \*Test classes | test reports      | Test failure       |
| package  | jar/war plugin               | target/\*.jar     | Missing Main-Class |
| install  | Copy to ~/.m2                | Local repo entry  | Disk full          |
| deploy   | Upload to remote repo        | Remote repo entry | Auth failure       |

**How to choose which phase to run:** Use `package` for local development and CI validation. Use `install` when other local modules depend on this one. Use `deploy` only from CI pipelines (never from developer machines for release artifacts).

---

### ⚠️ Common Misconceptions

| Misconception                            | Reality                                                                                                                                   |
| ---------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------- |
| `mvn deploy` pushes to production        | `deploy` pushes the artifact to a Maven repository (Nexus/Artifactory), not to a production server                                        |
| You can run phases out of order          | Maven always executes phases in order from the beginning of the lifecycle                                                                 |
| `clean` is part of the default lifecycle | `clean` is a separate lifecycle; `mvn clean package` runs two lifecycles in sequence                                                      |
| Skipping tests is always safe            | `-DskipTests` skips execution only; `-Dmaven.test.skip=true` also skips compilation - the latter can hide compilation errors in test code |

---

### 🚨 Failure Modes & Diagnosis

**Build fails at `test` phase silently**

**Root Cause:** Tests fail but output is verbose and scrolls past; only the summary matters.

**Fix:**

```bash
# Show test output inline
mvn test -Dsurefire.useFile=false

# Run a single test class
mvn test -Dtest=MyServiceTest

# Show full stack traces
mvn test -e
```

---

**`deploy` phase fails with "401 Unauthorized"**

**Root Cause:** Maven's `settings.xml` doesn't have credentials for the remote repository.

**Fix:** Add `<server>` entry to `~/.m2/settings.xml` matching the `<id>` of the repository in `pom.xml`.

---

### 🔗 Related Keywords

**Prerequisites:** `Maven Overview`, `pom.xml`, `Maven Plugins`

**Builds On This:** `Maven Goals`, `Maven Phases`, `Build Performance Optimization`

**Related Patterns:** `Maven Goals`, `Maven Phases`, `Maven Plugins`

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ KEY PHASES    │ validate → compile → test → package      │
│               │ → install → deploy                       │
├───────────────┼──────────────────────────────────────────│
│ FAST BUILD    │ mvn package -DskipTests                  │
├───────────────┼──────────────────────────────────────────│
│ CLEAN BUILD   │ mvn clean package                        │
├───────────────┼──────────────────────────────────────────│
│ FULL CI BUILD │ mvn clean deploy                         │
├───────────────┼──────────────────────────────────────────│
│ DEBUG         │ mvn -e (show exception) / -X (debug)     │
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** A developer runs `mvn package` and the tests fail. They then run `mvn package -DskipTests` and it succeeds. They ship this artifact to production. What risk did they accept, and under what circumstances is `-DskipTests` actually legitimate to use?

**Q2.** You need a code generator to run before compilation to produce Java sources from a schema file. Which lifecycle phase should you bind the generator to, and why? What would break if you bound it to the `compile` phase instead?
