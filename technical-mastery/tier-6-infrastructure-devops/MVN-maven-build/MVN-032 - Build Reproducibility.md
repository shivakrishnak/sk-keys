---
version: 1
layout: default
title: "Build Reproducibility"
parent: "Maven & Build Tools"
grand_parent: "Technical Mastery"
nav_order: 32
permalink: /technical-mastery/maven-build/build-reproducibility/
id: MVN-036
category: Maven & Build Tools (Java)
difficulty: ★★★
depends_on: SNAPSHOT vs RELEASE, Gradle Build Cache, Maven Wrapper (mvnw)
used_by: Maven Release Plugin, OWASP Dependency Check, Build Performance Optimization
related: SNAPSHOT vs RELEASE, Gradle Build Cache, Maven Release Plugin
tags:
  - build-tools
  - reproducibility
  - security
  - java
  - deep-dive
---

⚡ TL;DR - A reproducible build produces byte-for-byte identical output from identical inputs, regardless of when or where it runs. This enables independent verification of published artifacts, eliminates "works on my machine" mysteries, and is a critical defence against supply-chain attacks.

| #1090           | Category: Maven & Build Tools (Java)                                         | Difficulty: ★★★ |
| :-------------- | :--------------------------------------------------------------------------- | :-------------- |
| **Depends on:** | SNAPSHOT vs RELEASE, Gradle Build Cache, Maven Wrapper (mvnw)                |                 |
| **Used by:**    | Maven Release Plugin, OWASP Dependency Check, Build Performance Optimization |                 |
| **Related:**    | SNAPSHOT vs RELEASE, Gradle Build Cache, Maven Release Plugin                |                 |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
You publish `my-library-1.0.0.jar`. A security researcher downloads it six months later, rebuilds from the same tag, and gets a different JAR. Are there differences because of legitimate toolchain changes - or because the build was compromised? You can't tell. The JAR in production cannot be independently verified.

**THE BREAKING POINT:**
Supply chain attacks (SolarWinds, XZ Utils, log4shell exploitation) demonstrate that build pipelines are high-value targets. If your build is non-reproducible, attackers can inject malicious code into your build output without changing your source code - and you have no way to detect it.

**THE INVENTION MOMENT:**
Reproducible builds movement (reproducible-builds.org) established practices to make build outputs deterministic: fixed timestamps, sorted file entries, stable classpath ordering, hermetic toolchains. The Java ecosystem adopted these via the Maven Reproducible Build plugin and Gradle's built-in reproducibility support.

---

### 📘 Textbook Definition

**Build reproducibility** is the property of a build system where the same source code, built with the same toolchain and inputs, always produces byte-for-byte identical output artifacts. Sources of non-reproducibility include: file system ordering (non-deterministic directory traversal), embedded timestamps (current date/time in JAR manifest or class files), non-deterministic hashing (HashMap iteration order in older JDK), system-specific paths, and random seeds. Achieving reproducibility requires: (1) a fixed, pinned toolchain; (2) deterministic ordering of all inputs; (3) removal or normalisation of timestamps; (4) hermetic builds (isolation from system environment); (5) locked dependency versions (no SNAPSHOTs).

---

### ⏱️ Understand It in 30 Seconds

**One line:**
Reproducible build: same source + same tools = same output, always - verifiable by anyone, anywhere.

**One analogy:**

> A notarised document. The same text, signed by the same notary, on the same date, produces a document with the same content. If anyone claims the content changed, you can verify against the notarised original. A non-reproducible build is like a document that looks slightly different every time it's printed - you can never be sure the printed copy matches the original.

**One insight:**
Non-reproducibility isn't just a security issue - it's also the root cause of "works on CI but not locally" bugs. A reproducible build is also a more debuggable build.

---

### 🔩 First Principles Explanation

**COMMON SOURCES OF NON-REPRODUCIBILITY:**

```
1. TIMESTAMPS embedded in artifacts:
   - JAR MANIFEST.MF: "Build-Time: 2024-12-01 14:30:00"
   - Class file last-modified timestamps in ZIP entries
   - javadoc HTML files with generation date

2. FILE SYSTEM ORDERING:
   - readdir() returns files in arbitrary order on Linux
   - Two builds on different filesystems → different JAR
     entry order

3. TOOLCHAIN VARIATION:
   - Different JDK versions produce different bytecode
   - Different Maven/Gradle versions use different defaults

4. NON-DETERMINISTIC MAP ITERATION:
   - HashMap iteration order changed in JDK 9+
   - If serialisation iterates a HashMap, output varies

5. SNAPSHOT DEPENDENCIES:
   - Dependency version resolves to different artifact
     each run
   - "same" inputs produce different classpath

6. SYSTEM-SPECIFIC VALUES:
   - Absolute paths embedded in output
   - Username or hostname in generated artifacts
   - Locale/timezone affecting date formatting
```

**FIXES:**

| Problem                | Fix                                                                                                              |
| ---------------------- | ---------------------------------------------------------------------------------------------------------------- |
| Timestamps in JAR      | `project.reproducibleFileOrder=true` + `preserveFileTimestamps=false` in Gradle; Maven Reproducible Build plugin |
| File ordering          | Sort file collections before processing; use deterministic collections                                           |
| Toolchain variation    | Maven Wrapper / Gradle Wrapper + Java toolchain pinning                                                          |
| SNAPSHOT deps          | Pin all dependencies to RELEASE versions for release builds                                                      |
| Non-deterministic maps | Use `LinkedHashMap`, `TreeMap` for anything serialised                                                           |

**THE TRADE-OFFS:**

**Gain:** Independent verification of published artifacts; supply-chain attack detection; no more "works on my machine"; build cache effectiveness increases (deterministic = better cache hit rate); legal compliance (some regulatory frameworks require reproducible builds).

**Cost:** Requires disciplined toolchain pinning; some frameworks/tools embed non-deterministic data by default (must be configured to remove it); not all Maven plugins support reproducible builds; achieving full reproducibility may require patching upstream dependencies.

---

### 🧪 Thought Experiment

**SETUP:**
You build `my-app-1.0.0.jar` and release it. A month later, a security researcher independently rebuilds from tag `v1.0.0` with the same `JAVA_HOME` and Maven version. They compute `sha256` of both JARs:

```
Published JAR: sha256 = abc123...
Rebuilt JAR:   sha256 = def456...   ← DIFFERENT
```

**INVESTIGATION:**

1. Diff the ZIP entries - JAR entry ordering differs (filesystem traversal order different on researcher's machine)
2. A MANIFEST.MF entry: `Build-Time: ...` timestamp differs
3. One class file has an annotation processor that embedded the build host name

**REMEDIATION:**

1. Enable `preserveFileTimestamps = false` in Gradle Jar task
2. Remove `Build-Time` from MANIFEST.MF
3. Fix annotation processor to not embed non-deterministic data

**THE LESSON:**
Non-reproducibility requires investigation - each source must be identified and fixed. Tools like `diffoscope` (diff two binary files intelligently) help locate discrepancies.

---

### 🧠 Mental Model / Analogy

> Reproducible builds are the same concept as pure functions in functional programming: a pure function always returns the same output for the same inputs, with no side effects. A reproducible build is a "pure build" - same inputs (source + tools + config), same outputs, no environmental side effects leaking in.

---

### 📶 Gradual Depth - Four Levels

**Level 1:** A reproducible build always produces the same JAR for the same source code. Timestamps in JARs and random file ordering are the main problems to fix.

**Level 2:** Maven: enable the `artifact:check` goal with `maven-artifact-plugin` or use `spring-boot-maven-plugin`'s `reproducible` property. Gradle: `tasks.withType<AbstractArchiveTask> { isPreserveFileTimestamps = false; isReproducibleFileOrder = true }`.

**Level 3:** Full reproducibility requires: pinned JDK (toolchain), pinned build tool (wrapper), pinned all dependency versions (no SNAPSHOTs), deterministic file ordering, no timestamps, no system-specific values. Hermetic builds (containers) provide full isolation.

**Level 4:** Reproducible Builds project (`reproducible-builds.org`) provides `diffoscope` for binary diff analysis, a certification database for known-reproducible Maven Central artifacts, and tooling for verification workflows. GitHub Actions and Jenkins can be configured to independently rebuild and compare checksums as part of a security pipeline.

---

### ⚙️ How It Works (Mechanism)

```bash
# Maven: verify reproducibility (rebuild and compare)
mvn clean package
cp target/my-app.jar /tmp/my-app-build1.jar
mvn clean package
sha256sum target/my-app.jar /tmp/my-app-build1.jar
# Should be identical

# Gradle: enable reproducible archives globally
# In build.gradle.kts:
tasks.withType<AbstractArchiveTask>().configureEach {
    isPreserveFileTimestamps = false
    isReproducibleFileOrder = true
}

# Verify JAR entries:
jar tf build/libs/my-app.jar | sort
# sorted = reproducible entry order
unzip -p build/libs/my-app.jar META-INF/MANIFEST.MF
# check for timestamps
```

---

### 💻 Code Example

**Gradle: make all archive tasks reproducible:**

```kotlin
// build.gradle.kts (or in convention plugin)

tasks.withType<AbstractArchiveTask>().configureEach {
    isPreserveFileTimestamps = false
    // no timestamps in ZIP entries
    isReproducibleFileOrder = true     // deterministic entry order
}

tasks.named<Jar>("jar") {
    manifest {
        // REMOVE non-deterministic values:
        // attributes("Build-Time" to System.currentTimeMillis())  ←
        // BAD
        // KEEP only deterministic values:
        attributes(
            "Implementation-Version" to project.version,
            "Implementation-Title" to project.name
        )
    }
}
```

**Maven: maven-artifact-plugin for reproducibility check:**

```xml
<plugin>
  <groupId>org.apache.maven.plugins</groupId>
  <artifactId>maven-artifact-plugin</artifactId>
  <version>3.5.0</version>
  <executions>
    <execution>
      <goals>
        <!-- Record build info for reproducibility check -->
        <goal>buildinfo</goal>
        <!-- Check that rebuild matches recorded buildinfo -->
        <!-- <goal>check-buildinfo</goal> -->
      </goals>
    </execution>
  </executions>
</plugin>

<!-- Also required: remove MANIFEST timestamps -->
<plugin>
  <groupId>org.apache.maven.plugins</groupId>
  <artifactId>maven-jar-plugin</artifactId>
  <configuration>
    <archive>
      <manifest>
        <addDefaultImplementationEntries>false</addDefaultImplementationEntries>
      </manifest>
      <!-- no custom timestamp entries -->
    </archive>
  </configuration>
</plugin>
```

---

### ⚖️ Comparison Table

| Reproducibility Factor | Non-Reproducible Default | Reproducible Fix               |
| ---------------------- | ------------------------ | ------------------------------ |
| JAR entry timestamps   | Set to build time        | `preserveFileTimestamps=false` |
| JAR entry order        | Filesystem order         | `reproducibleFileOrder=true`   |
| MANIFEST.MF Build-Time | Current timestamp        | Remove or use version          |
| Dependency versions    | SNAPSHOT (mutable)       | RELEASE (immutable)            |
| JDK version            | Whatever's installed     | Toolchain pinning              |
| Build tool version     | Whatever's installed     | Maven/Gradle Wrapper           |

---

### ⚠️ Common Misconceptions

| Misconception                              | Reality                                                                       |
| ------------------------------------------ | ----------------------------------------------------------------------------- |
| Reproducibility is only a security concern | Also improves build cache efficiency and debugging                            |
| Same SHA = no bug injected                 | It proves output matches a previous build; still need to audit the original   |
| Java bytecode is always deterministic      | Annotation processors and code generators can embed non-deterministic content |
| Reproducibility requires Gradle            | Maven supports it with maven-artifact-plugin and proper plugin config         |

---

### 🚨 Failure Modes & Diagnosis

**Two builds of the same commit produce different JARs**

**Diagnosis:**

```bash
# Intelligent binary diff:
diffoscope target/my-app-build1.jar target/my-app-build2.jar
# Shows exactly what changed: file entries, timestamps, bytecode
# differences
```

**Common findings:**

- `META-INF/MANIFEST.MF` timestamp
- `META-INF/maven/*/pom.properties` with build timestamp
- Annotation processor output with non-deterministic ordering

---

### 🔗 Related Keywords

**Prerequisites:** `SNAPSHOT vs RELEASE`, `Gradle Build Cache`, `Maven Wrapper (mvnw)`

**Builds On This:** `Maven Release Plugin`, `OWASP Dependency Check`

**Related Patterns:** `SNAPSHOT vs RELEASE`, `Gradle Build Cache`, `Maven Release Plugin`

---

### 📌 Quick Reference Card

```
┌─────────────────────────────────────────────────────────┐
│ GOAL         │ Same inputs → identical bytes, always    │
├──────────────┼──────────────────────────────────────────┤
│ FIX GRADLE   │ preserveFileTimestamps=false +           │
│              │ reproducibleFileOrder=true               │
├──────────────┼──────────────────────────────────────────┤
│ FIX MAVEN    │ maven-artifact-plugin buildinfo goal     │
├──────────────┼──────────────────────────────────────────┤
│ DIAGNOSE     │ diffoscope jar1.jar jar2.jar             │
├──────────────┼──────────────────────────────────────────┤
│ KEY RULES    │ No SNAPSHOTs, no timestamps, pin toolchai│
├──────────────┼──────────────────────────────────────────┤
│ ONE-LINER    │ "Pure build: same in → same out, always" │
└─────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** Your team has achieved reproducible builds for the `compile` and `test` phases. But the final `jar` still varies between builds because a custom Gradle task reads from a properties file that includes the machine hostname. How would you fix this without removing the hostname information entirely (it's needed for diagnostics)?

**Q2.** An open-source library claims to be "reproducibly built." A security researcher independently rebuilds it and gets the same SHA-256 checksum as the published artifact. Does this mean the library is safe from supply chain attack? What does reproducibility prove, and what does it not prove?
