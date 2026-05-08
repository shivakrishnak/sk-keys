---
layout: default
title: "Maven Wrapper (mvnw)"
parent: "Maven & Build Tools (Java)"
grand_parent: "Technical Dictionary"
nav_order: 23
permalink: /maven-build/maven-wrapper-mvnw/
id: MVN-023
category: Maven & Build Tools (Java)
difficulty: ★★☆
depends_on: Maven Overview, Maven Lifecycle, pom.xml
used_by: Build Reproducibility, Build Performance Optimization, CI-CD
related: Gradle vs Maven, Build Reproducibility, Maven Profiles
tags:
  - maven
  - build-tools
  - wrapper
  - mvnw
  - java
  - intermediate
---

# MVN-023 - Maven Wrapper (mvnw)

⚡ TL;DR - The Maven Wrapper (`mvnw` / `mvnw.cmd`) is a shell script committed to your repository that auto-downloads the specific Maven version required by your project - eliminating "works on my machine" Maven version mismatches without requiring Maven to be pre-installed.

| #1083           | Category: Maven & Build Tools (Java)                         | Difficulty: ★★☆ |
| :-------------- | :----------------------------------------------------------- | :-------------- |
| **Depends on:** | Maven Overview, Maven Lifecycle, pom.xml                     |                 |
| **Used by:**    | Build Reproducibility, Build Performance Optimization, CI-CD |                 |
| **Related:**    | Gradle vs Maven, Build Reproducibility, Maven Profiles       |                 |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
Developer A has Maven 3.6.3 installed. Developer B has Maven 3.9.5. The CI server has Maven 3.8.1. A new Maven version changes default plugin behaviour - builds produce different results across environments. "But it works on my machine!" is now a Maven version problem.

**THE BREAKING POINT:**
As teams grow and CI infrastructure diversifies, keeping Maven versions synchronised across all environments (developer machines, Docker images, CI agents, cloud build services) requires manual coordination. A Maven update on one machine silently diverges from others.

**THE INVENTION MOMENT:**
Borrowed from Gradle (which introduced the wrapper concept), the Maven Wrapper checks in a version-pinned Maven download script with your project. Any build environment runs `./mvnw` (or `mvnw.cmd` on Windows) instead of `mvn` - the script downloads and uses the exact Maven version specified in `.mvn/wrapper/maven-wrapper.properties`, cached locally after first download.

---

### 📘 Textbook Definition

The **Maven Wrapper** is a set of project-level scripts (`mvnw` on Unix, `mvnw.cmd` on Windows) and a properties file (`.mvn/wrapper/maven-wrapper.properties`) committed to the project repository. When invoked, the wrapper checks whether the specified Maven version is present in the user's local cache (typically `~/.m2/wrapper/dists/`). If not, it downloads the specified Maven distribution from the configured URL, installs it into the cache, and delegates the build command to that exact Maven version. This ensures the entire team - including CI - uses the identical Maven version without requiring system-level Maven installation.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
`mvnw` = Maven version pinned in your repo; auto-downloaded on first use; same version everywhere.

**One analogy:**

> A self-serve coffee machine that always uses the exact same brand, grind, and roast specified on a label attached to the machine - regardless of what coffees are stocked in the kitchen. Everyone brews the same coffee.

**One insight:**
Committing `mvnw` shifts Maven version management from system administration to source control - the project defines its own build toolchain, not the environment.

---

### 🔩 First Principles Explanation

**FILE STRUCTURE:**

```
my-project/
  .mvn/
    wrapper/
      maven-wrapper.properties       ← pinned Maven version + download URL
      maven-wrapper.jar              ← bootstrap downloader (in older setups)
  mvnw                               ← Unix shell script
  mvnw.cmd                           ← Windows batch script
  pom.xml
```

**`maven-wrapper.properties` content:**

```properties
# The exact Maven version to use
distributionUrl=https://repo.maven.apache.org/maven2/org/apache/maven/apache-maven/3.9.5/apache-maven-3.9.5-bin.zip

# Cache location (default: ~/.m2/wrapper/dists/)
# wrapperUrl=https://repo.maven.apache.org/maven2/org/apache/maven/wrapper/maven-wrapper/3.2.0/maven-wrapper-3.2.0.jar
```

**EXECUTION FLOW:**

```
Developer runs: ./mvnw clean install
       │
       ▼
mvnw script reads .mvn/wrapper/maven-wrapper.properties
       │
       ▼
Is apache-maven-3.9.5 in ~/.m2/wrapper/dists/?
   YES → use it
   NO  → download from distributionUrl, extract, cache
       │
       ▼
Execute: ~/.m2/wrapper/dists/apache-maven-3.9.5/bin/mvn clean install
```

**THE TRADE-OFFS:**
**Gain:** Reproducible Maven version across all environments; no system-level Maven installation required; version upgrades are a `git commit` (PR-reviewable); CI setup simplifies (just run `./mvnw`).
**Cost:** Small network overhead on first use per machine; wrapper scripts must be kept up to date when Maven version is bumped; in air-gapped environments, `distributionUrl` must point to an internal mirror; `mvnw` file must have execute permission set (`chmod +x mvnw`) on Unix-based CI agents.

---

### 🧪 Thought Experiment

**SETUP:**
Your project's `maven-wrapper.properties` pins `apache-maven:3.8.7`. A security vulnerability is discovered in Maven 3.8.7. Your security team requires upgrading to 3.9.5 within 48 hours.

**WITH WRAPPER:**

1. Update `distributionUrl` in `maven-wrapper.properties` to 3.9.5
2. Run `./mvnw --version` locally to verify
3. Open a PR with the single-line change
4. PR merged → CI automatically uses 3.9.5; all developers get 3.9.5 on next pull

**WITHOUT WRAPPER:**

1. Email all developers to upgrade Maven
2. Update CI agent configuration (requires infra ticket)
3. Update Docker build image (requires image rebuild + push)
4. Verify each environment has upgraded correctly
5. Lag time: days to weeks

**THE LESSON:**
The wrapper converts Maven version management from an ops/manual coordination problem into a developer workflow (commit + PR) problem.

---

### 🧠 Mental Model / Analogy

> `mvnw` is to Maven what `nvm use` (with a `.nvmrc` file) is to Node.js, or what `rbenv` is to Ruby. The toolchain version is declared in the project, auto-provisioned on demand, and reproducible everywhere without manual intervention.

---

### 📶 Gradual Depth - Four Levels

**Level 1:** Instead of typing `mvn clean install`, type `./mvnw clean install`. The script downloads Maven if needed and runs the build with the pinned version.

**Level 2:** `maven-wrapper.properties` specifies the Maven download URL. The wrapper caches Maven in `~/.m2/wrapper/dists/`. Commands after `./mvnw` are passed directly to that Maven version.

**Level 3:** In CI (GitHub Actions, Jenkins, etc.): use `./mvnw` instead of `mvn` - no need to configure a specific Maven version in the CI tool's settings. In Docker builds: `COPY . /build && RUN ./mvnw clean package` - the wrapper handles Maven download.

**Level 4:** Corporate environments: change `distributionUrl` to point to your internal Nexus Maven distribution mirror. For security: `mvnw` supports `distributionSha256Sum` in properties to verify the downloaded Maven distribution's checksum before trusting it - preventing supply chain tampering.

---

### ⚙️ How It Works (Mechanism)

```bash
# Add Maven Wrapper to an existing project
mvn wrapper:wrapper                              # uses current installed Maven version
mvn wrapper:wrapper -Dmaven=3.9.5               # pin specific version

# Verify which Maven version the wrapper will use
./mvnw --version

# Clear wrapper cache (forces re-download)
rm -rf ~/.m2/wrapper/dists/

# Make mvnw executable (Unix - required after git clone on some systems)
chmod +x mvnw

# Use wrapper in CI (GitHub Actions example)
# (No special Maven installation step needed)
- run: ./mvnw clean package -DskipTests
```

---

### 💻 Code Example

**`maven-wrapper.properties` with internal mirror (corporate setup):**

```properties
# Internal Nexus mirror for air-gapped environment
distributionUrl=https://nexus.mycompany.com/repository/maven-distributions/\
  org/apache/maven/apache-maven/3.9.5/apache-maven-3.9.5-bin.zip

# Checksum verification (security best practice)
distributionSha256Sum=4810523ba025104106567d8a15a8aa19db35068c8c8be19e30b219a1d7e83bcab

# Wrapper distribution source
wrapperUrl=https://nexus.mycompany.com/repository/maven-distributions/\
  org/apache/maven/wrapper/maven-wrapper/3.2.0/maven-wrapper-3.2.0.jar
```

**`.gitignore` for wrapper cache:**

```gitignore
# Don't commit downloaded Maven distributions
.mvn/wrapper/maven-wrapper.jar  # In modern Maven wrapper this is not needed (pure shell bootstrap)
```

**GitHub Actions workflow using wrapper:**

```yaml
jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-java@v4
        with:
          java-version: "17"
          distribution: "temurin"
          # NO maven-version: needed - wrapper handles it
      - name: Build with Maven Wrapper
        run: ./mvnw clean verify
```

---

### ⚖️ Comparison Table

| Approach               | Version Pinned  | Works Without Maven Installed | In Version Control    | Upgrade Path       |
| ---------------------- | --------------- | ----------------------------- | --------------------- | ------------------ |
| System `mvn`           | No              | No                            | No                    | Manual per machine |
| `MAVEN_HOME` env var   | Partial         | No                            | No                    | Manual CI config   |
| Maven Wrapper (`mvnw`) | Yes             | Yes                           | Yes                   | Single file commit |
| Docker base image      | Yes (via image) | Yes (in container)            | Indirect (Dockerfile) | Image rebuild      |

---

### ⚠️ Common Misconceptions

| Misconception                         | Reality                                                                         |
| ------------------------------------- | ------------------------------------------------------------------------------- |
| `mvnw` requires Maven to be installed | It requires Java only; Maven is downloaded by the wrapper                       |
| The wrapper is the same as `mvn`      | `./mvnw` delegates to a pinned version; system `mvn` uses whatever is installed |
| Wrapper JAR must be committed         | Modern wrapper uses a pure shell bootstrap - the JAR may not be needed          |
| Wrapper only works on Unix            | `mvnw.cmd` works on Windows; PowerShell can also run the wrapper                |

---

### 🚨 Failure Modes & Diagnosis

**`mvnw: Permission denied` on Linux/macOS CI**

**Root Cause:** `mvnw` file has no execute permission after `git clone`.

**Fix:**

```bash
chmod +x mvnw
# Or in CI pipeline:
git update-index --chmod=+x mvnw  # set in git index (persists in repo)
git commit -m "fix: set mvnw execute permission"
```

---

**Wrapper downloads from internet on air-gapped CI**

**Root Cause:** `distributionUrl` points to `repo.maven.apache.org` which CI agents can't reach.

**Fix:** Update `distributionUrl` in `maven-wrapper.properties` to internal Nexus/Artifactory mirror URL.

---

### 🔗 Related Keywords

**Prerequisites:** `Maven Overview`, `Maven Lifecycle`, `pom.xml`

**Builds On This:** `Build Reproducibility`, `Build Performance Optimization`

**Related Patterns:** `Gradle vs Maven`, `Build Reproducibility`, `Maven Profiles`

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ SCRIPTS      │ mvnw (Unix), mvnw.cmd (Windows)           │
├──────────────┼───────────────────────────────────────────┤
│ CONFIG       │ .mvn/wrapper/maven-wrapper.properties     │
├──────────────┼───────────────────────────────────────────┤
│ CACHE        │ ~/.m2/wrapper/dists/                      │
├──────────────┼───────────────────────────────────────────┤
│ GENERATE     │ mvn wrapper:wrapper -Dmaven=3.9.5         │
├──────────────┼───────────────────────────────────────────┤
│ COMMIT?      │ Yes - mvnw, mvnw.cmd, .mvn/ all committed │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "Pin Maven version in version control"    │
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** A new developer clones your repo and tries to build with `./mvnw clean install`. Their machine has no Maven installed. They are behind a corporate firewall with no direct internet access. The `distributionUrl` in `maven-wrapper.properties` still points to `repo.maven.apache.org`. What will happen, and what changes are needed to make this work?

**Q2.** You want to add SNAPSHOT checksum verification to prevent supply-chain attacks on the Maven distribution download. Which property in `maven-wrapper.properties` supports this, and what value would you set?
