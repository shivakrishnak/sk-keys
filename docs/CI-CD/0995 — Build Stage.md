---
layout: default
title: "Build Stage"
parent: "CI/CD"
nav_order: 995
permalink: /ci-cd/build-stage/
number: "0995"
category: CI/CD
difficulty: ★☆☆
depends_on: Pipeline, Version Control, Maven Overview
used_by: Test Stage, Artifact, Artifact Registry
related: Test Stage, Artifact, Pipeline as Code
tags:
  - cicd
  - build
  - devops
  - foundational
---

# 0995 — Build Stage

⚡ TL;DR — The build stage compiles source code and packages it into a deployable artifact, verifying the code is syntactically correct and all dependencies are resolved before any test runs.

| #0995 | Category: CI/CD | Difficulty: ★☆☆ |
|:---|:---|:---|
| **Depends on:** | Pipeline, Version Control, Maven Overview | |
| **Used by:** | Test Stage, Artifact, Artifact Registry | |
| **Related:** | Test Stage, Artifact, Pipeline as Code | |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
A developer commits code with an import error on line 47 — a class that was deleted yesterday. Without an automated build stage, the test suite starts executing, imports fail at runtime, and the test runner reports cryptic `ClassNotFoundException` errors. The developer loses 5 minutes before realising it's not a test failure but a compilation failure. Worse, if the tests are written in a dynamically-typed language, the error might only surface when that code path is executed — potentially in production.

**THE BREAKING POINT:**
Compilation errors and missing dependencies are the cheapest possible failures to catch — they require no test execution, just a compiler. Not catching them immediately means wasting time on test infrastructure for fundamentally broken code.

**THE INVENTION MOMENT:**
This is exactly why the build stage exists: before testing anything, verify the code can be compiled and all dependencies resolved — turning a 30-second compiler check into a hard gate that prevents broken code from advancing.

---

### 📘 Textbook Definition

The **build stage** is the first stage in a CI/CD pipeline. It compiles source code into executable or deployable form, resolves and validates all declared dependencies, runs static code analysis and linting, and produces an artifact (JAR, Docker image, executable binary). The build stage is a prerequisite for all subsequent stages — a failing build prevents tests from running. It catches syntax errors, missing dependencies, and compile-time type errors at the lowest cost point in the pipeline.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
Turn raw source code into a runnable package and fail immediately if it can't be done.

**One analogy:**
> The build stage is like proving all your ingredients exist before you start cooking. Before preheating the oven, you check that eggs, flour, and butter are in the kitchen. If the butter is missing, there's no point starting — the recipe can't complete. Building verifies your code's "ingredients" (dependencies, syntax) are all present.

**One insight:**
The build stage is the first gate in the fail-fast strategy. Its goal is not to verify behaviour — that's for tests. Its goal is to verify that the code is *compilable and complete*. A fast build (under 3 minutes) saves the slower downstream stages from running on fundamentally broken input.

---

### 🔩 First Principles Explanation

**CORE INVARIANTS:**
1. Build must be reproducible: same source + same dependency versions = same artifact, always.
2. Build runs in a clean, isolated environment — no reliance on local developer tools.
3. Build produces a single, versioned artifact that all downstream stages use.

**DERIVED DESIGN:**
Reproducibility requires pinning dependency versions (lockfiles, `pom.xml` explicit versions). Isolation requires containerised build environments. Single-artifact requires building once and passing the artifact to subsequent stages via a registry or artifact store — never rebuilding for each environment.

Build caching (Maven's `.m2` folder, npm's `node_modules`) is keyed on the dependency manifest's hash. If `pom.xml` hasn't changed, downloading 200 Maven dependencies again is wasted time — the cache provides a 10x speedup.

**THE TRADE-OFFS:**
**Gain:** Compile errors caught in 2–3 minutes, before slow tests run. Immutable, traceable artifact produced once.
**Cost:** Build environment must be maintained. Slow builds without caching become a team-wide bottleneck.

---

### 🧪 Thought Experiment

**SETUP:**
Developer Alice pushes a commit that accidentally introduces a circular dependency between two modules. The project has 400 unit tests.

**WHAT HAPPENS WITHOUT A BUILD STAGE:**
The pipeline goes straight to running 400 unit tests. After 8 minutes, 400 tests fail with `ClassCircularityError`. The failure report shows 400 red tests. Alice must look through all of them to understand that the root cause is not a logic error but a structural dependency problem.

**WHAT HAPPENS WITH A BUILD STAGE:**
The build stage runs `mvn compile`. After 45 seconds, it fails: `circular dependency detected between module-a and module-b`. The pipeline stops. The 400 unit tests never run. Alice sees a single, clear error in 45 seconds, not 400 confusing errors in 8 minutes.

**THE INSIGHT:**
One class of failures (structural/compilation) should be separated from another class (behavioural/test). The build stage is this separation — it handles class 1 so that the test stage handles only class 2.

---

### 🧠 Mental Model / Analogy

> The build stage is like a factory's incoming materials inspection. Before widgets go to the assembly floor, an inspector verifies that all parts are correct and present. Defective blanks are rejected immediately — before any assembly work is done on them. The assembly floor (test stage) only sees pre-verified materials.

- "Parts arriving at the factory" → source code committed to the repo
- "Materials inspector" → compiler / build tool
- "Defective blank rejected" → compilation failure — pipeline stopped
- "Verified materials passed to assembly" → artifact passed to test stage
- "Assembly floor" → test stage

Where this analogy breaks down: unlike physical parts, the same source code always compiles to the same binary — there's no natural variability. The analogy's strength is in the sequencing logic, not the randomness of defects.

---

### 📶 Gradual Depth — Four Levels

**Level 1 — What it is (anyone can understand):**
The build stage takes the raw code files developers wrote and turns them into a program the computer can run. If the code has mistakes that prevent it from being turned into a program (like using a function that doesn't exist), the build stage fails immediately and nothing else runs.

**Level 2 — How to use it (junior developer):**
In your pipeline YAML, the build stage runs the project's build command: `mvn compile` or `mvn package` for Java, `npm run build` for JavaScript, `go build` for Go. It should also run linting (`mvn checkstyle:check`, `eslint`). The stage produces an artifact (JAR, Docker image) stored for later stages. Cache your dependency directory — `~/.m2`, `node_modules` — keyed on the lock file hash.

**Level 3 — How it works (mid-level engineer):**
The build tool resolves the dependency graph, downloads missing artifacts from the configured repositories (Maven Central, npm registry), compiles source files in dependency order, and links them into the final artifact. Docker builds add a layer: each `RUN` instruction in the `Dockerfile` is a layer cached independently. Multi-stage Docker builds separate the build environment (JDK + Maven) from the runtime image (JRE only), producing a minimal production image.

**Level 4 — Why it was designed this way (senior/staff):**
Build reproducibility is harder than it looks. Maven's `SNAPSHOT` dependencies, npm's `^` version ranges, and OS-level library versions all introduce non-determinism. Google's Bazel and Facebook's Buck solve this with hermetic builds — every input is explicitly declared with a hash, and the build output is a pure function of the inputs. This enables distributed build caching across hundreds of machines. For most teams, strict lockfiles (`package-lock.json`, `maven-enforcer` with no `SNAPSHOT` in release builds) provide sufficient reproducibility.

---

### ⚙️ How It Works (Mechanism)

```
┌─────────────────────────────────────────────┐
│           BUILD STAGE EXECUTION             │
├─────────────────────────────────────────────┤
│  Input: source code at commit SHA           │
│         ↓                                   │
│  1. Clean environment provisioned           │
│     (Docker image: openjdk:21-slim)         │
│         ↓                                   │
│  2. Dependency resolution                   │
│     - Check cache (key: hash of pom.xml)    │
│     - Cache miss: download from Maven Central│
│     - Cache hit: use local (~/.m2)          │
│         ↓                                   │
│  3. Compile source files                    │
│     mvn compile                             │
│     - Errors: FAIL → pipeline stopped       │
│         ↓ PASS                              │
│  4. Lint / style check                      │
│     mvn checkstyle:check                    │
│         ↓ PASS                              │
│  5. Package artifact                        │
│     mvn package -DskipTests                 │
│     Output: target/myapp-1.0.jar            │
│         ↓                                   │
│  6. Build Docker image                      │
│     docker build -t myapp:sha-abc123 .      │
│     docker push myapp:sha-abc123            │
│         ↓                                   │
│  Output: image in registry, tagged SHA      │
│  → Passed to Test Stage                     │
└─────────────────────────────────────────────┘
```

**Dependency caching:** Without caching, a Maven project with 50 dependencies takes 3–5 minutes to resolve and download them. With a restore from cache (keyed on `pom.xml` SHA256), this becomes 15 seconds. Caches are per-branch but can fall back to the default branch's cache.

**Multi-stage Docker builds** separate concerns:
```dockerfile
# Stage 1: build environment (large image, JDK + Maven)
FROM maven:3.9-eclipse-temurin-21 AS builder
WORKDIR /app
COPY pom.xml .
RUN mvn dependency:go-offline  # cache deps as a layer
COPY src ./src
RUN mvn package -DskipTests

# Stage 2: runtime image (small, JRE only)
FROM eclipse-temurin:21-jre-alpine
COPY --from=builder /app/target/myapp.jar /app.jar
ENTRYPOINT ["java", "-jar", "/app.jar"]
```
The final image contains only the JRE and the JAR — no Maven, no source code. Typical size: 120 MB vs 600 MB for a full JDK image.

---

### 🔄 The Complete Picture — End-to-End Flow

**NORMAL FLOW:**
```
Commit pushed → CI triggered
  → Clean container: openjdk:21 image
  → Restore dependency cache (pom.xml hash)
  → mvn compile → SUCCESS (47 seconds)
  → mvn checkstyle:check → PASS
  → mvn package → JAR produced
  → docker build → image: myapp:sha-a3f8c [← YOU ARE HERE]
  → docker push → image in registry
  → Test stage picks up image from registry
```

**FAILURE PATH:**
```
mvn compile fails: SymbolNotFound: class PaymentService
  → Pipeline stops immediately
  → Test stage, integration stage: not triggered
  → PR shows ✗ at Build stage
  → Developer sees: "cannot find symbol: PaymentService"
  → Fix: add missing import → push → build reruns
```

**WHAT CHANGES AT SCALE:**
In monorepos with 100+ modules, rebuilding everything for a single file change is wasteful. Bazel and Nx implement dependency-graph analysis — only modules that transitively depend on the changed file are rebuilt. This reduces a 20-minute full build to a 90-second incremental build. The tradeoff: a more complex build configuration that must accurately model all module dependencies.

---

### 💻 Code Example

**Example 1 — Maven build stage in GitHub Actions with caching:**
```yaml
build:
  runs-on: ubuntu-latest
  steps:
    - uses: actions/checkout@v4

    - uses: actions/setup-java@v4
      with:
        java-version: '21'
        distribution: 'temurin'
        cache: maven   # caches ~/.m2 automatically

    - name: Compile and package
      # -DskipTests: tests run in a separate stage
      run: mvn --batch-mode package -DskipTests

    - name: Upload artifact
      uses: actions/upload-artifact@v4
      with:
        name: app-jar
        path: target/*.jar
        retention-days: 1  # only needed for this pipeline run
```

**Example 2 — Docker build with layer caching:**
```yaml
    - name: Set up Docker Buildx
      uses: docker/setup-buildx-action@v3

    - name: Build and push Docker image
      uses: docker/build-push-action@v5
      with:
        push: true
        tags: myorg/myapp:${{ github.sha }}
        cache-from: type=gha  # GitHub Actions cache
        cache-to: type=gha,mode=max
```

---

### ⚖️ Comparison Table

| Build Tool | Language | Caching | Incremental | Best For |
|---|---|---|---|---|
| **Maven** | Java | Local `~/.m2` | Module-level | Java enterprise projects |
| Gradle | Java/Kotlin | File-level cache | Task-level | Android, multi-module Java |
| npm/webpack | JavaScript | `node_modules` | None (default) | Node.js / frontend |
| Bazel | Any | Distributed, hermetic | File-level | Monorepos at scale |
| Docker | Any | Layer cache | Layer-level | Container-based deployments |

How to choose: Use the ecosystem's standard tool (Maven for Java, npm for Node). Layer Docker on top for containerised deployments. Only invest in Bazel when monorepo build times exceed 10 minutes despite all other optimisations.

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| The build stage should run all tests | The build stage compiles and packages. Tests are a separate stage. Running tests in the build stage mixes two concerns and prevents parallelism |
| A fast build means a good build | Speed matters, but build reproducibility matters more. A build that takes 5 minutes and always produces the same artifact is safer than a 30-second build with undeclared dependencies |
| Build failures mean test failures | Build failures (compilation, missing dependencies) are structurally different from test failures. A build failure means nothing works; a test failure means something specific doesn't work as expected |
| You should always run a clean build in CI | Clean builds eliminate cache pollution but are 10x slower. Use dependency caching with good cache key strategy (lock file hash) to get clean semantics with near-cache speed |

---

### 🚨 Failure Modes & Diagnosis

**1. Non-Reproducible Build — Different Output Each Run**

**Symptom:** Same commit produces different artifacts on different runs. Tests pass on one run, fail on the next with no code change.

**Root Cause:** `SNAPSHOT` Maven version, npm `^` range, or timestamp embedded in artifact causes non-determinism.

**Diagnostic:**
```bash
# Check for SNAPSHOT dependencies
mvn dependency:tree | grep SNAPSHOT
# Check npm for version ranges vs exact
cat package-lock.json | grep '"version"' | head -20
# Compare artifact checksums across two builds:
sha256sum target/myapp-*.jar
```

**Fix:** Replace `SNAPSHOT` with explicit release versions in production builds. Use `package-lock.json` and `npm ci` instead of `npm install`.

**Prevention:** Add `maven-enforcer-plugin` to fail the build if any `SNAPSHOT` dependency is found in a release context.

---

**2. Build Cache Poisoning**

**Symptom:** After changing `pom.xml`, the build still fetches the old dependency version — because a corrupted cache entry wasn't invalidated.

**Root Cause:** Cache key doesn't accurately reflect all inputs. A manual cache upload with wrong key contaminates the cache for subsequent runs.

**Diagnostic:**
```bash
# GitHub Actions: check cache hits in build logs
# Look for "Cache restored from key: ..."
# Then verify the actual key matched
grep "Cache restored" .github/workflows/action-output.log
```

**Fix:** Use precise cache keys. For Maven: `${{ hashFiles('**/pom.xml') }}`. Include OS and Java version in the key if they affect the artifact.

**Prevention:** Never manually upload to the build cache. Let the CI system manage it. Periodically run with `--no-cache` to verify fresh builds still work.

---

**3. Build Succeeds But Image Is Oversized**

**Symptom:** Docker image is 1.2 GB. Deployment to new nodes takes 8 minutes just for image pull.

**Root Cause:** Build tools, source code, and test dependencies are all baked into the production image. No multi-stage build.

**Diagnostic:**
```bash
# Inspect layers and their sizes
docker history myapp:latest
docker image inspect myapp:latest \
  --format='{{.Size}}' | numfmt --to=iec
```

**Fix:** Implement multi-stage Dockerfile — build in a full JDK image, copy only the JAR to a JRE-only runtime image.

**Prevention:** Set a maximum allowed image size in the pipeline. Fail the build if the image exceeds (e.g.) 200 MB.

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**
- `Pipeline` — the build stage is the first stage inside a pipeline; understanding pipeline structure is necessary
- `Version Control` — the build stage is triggered by commits and checks out code at a specific commit SHA
- `Maven Overview` — for Java projects, Maven is the primary build tool used in the build stage

**Builds On This (learn these next):**
- `Test Stage` — the next pipeline stage that receives the artifact produced by the build stage
- `Artifact` — the output of a successful build stage: the JAR, Docker image, or binary
- `Artifact Registry` — where the build stage pushes its output for use by downstream stages and environments

**Alternatives / Comparisons:**
- `Gradle Build Script` — an alternative to Maven for Java build automation with more flexible DSL
- `Pipeline as Code` — the practice of defining the build stage (and all others) as version-controlled YAML

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ WHAT IT IS   │ First pipeline stage: compile, package,   │
│              │ produce immutable versioned artifact       │
├──────────────┼───────────────────────────────────────────┤
│ PROBLEM IT   │ Compilation errors and missing            │
│ SOLVES       │ dependencies discovered late in tests     │
├──────────────┼───────────────────────────────────────────┤
│ KEY INSIGHT  │ Build once, deploy everywhere — the same  │
│              │ artifact tests and production must share  │
├──────────────┼───────────────────────────────────────────┤
│ USE WHEN     │ Always — every pipeline needs a build     │
│              │ stage as its first gate                   │
├──────────────┼───────────────────────────────────────────┤
│ AVOID WHEN   │ N/A — interpreted languages still need    │
│              │ lint + dependency resolution              │
├──────────────┼───────────────────────────────────────────┤
│ TRADE-OFF    │ Reproducibility + isolation vs            │
│              │ infrastructure cost and cache management  │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "Check all ingredients exist before       │
│              │  starting to cook"                        │
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ Test Stage → Artifact → Artifact Registry │
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** A team's Java build stage takes 18 minutes on CI. Locally, the same `mvn package` completes in 2 minutes. List the five most likely causes of this 9x slowdown in order of likelihood, and describe the diagnostic command to confirm each one. Then design a caching strategy that would bring CI build time under 4 minutes.

**Q2.** Your team uses multi-stage Docker builds. The build stage produces a 95 MB image (JRE + JAR). Three months later, the same build produces a 340 MB image with no obvious source change. Trace the possible causes — from Dockerfile changes to dependency additions to base image updates — and describe the systematic investigation process you'd follow to pinpoint the exact cause.

