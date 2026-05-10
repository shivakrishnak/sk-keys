---
version: 2
layout: default
title: "Java 8 to Java 17 Migration Guide"
parent: "Java Language"
grand_parent: "Technical Dictionary"
nav_order: 61
permalink: /java/java-8-to-java-17-migration/
id: JLG-015
category: Java & JVM Internals
difficulty: ★★★
depends_on: Java Language, JVM, Modules (JPMS)
used_by: CI-CD, Java Performance Tuning
related: Java 17 Features, Modules (JPMS), LTS Release Cycle
tags:
  - java
  - jvm
  - advanced
  - build
---

# JLG-061 - Java 8 to Java 17 Migration Guide

⚡ **TL;DR -** Migrating from Java 8 to Java 17 is a phased exercise in removing illegal reflective access, handling removed APIs, and adopting the module system - rewarded with significantly better performance and modern language features.

| | |
|---|---|
| **Depends on** | Java Language, JVM, Modules (JPMS) |
| **Used by** | CI-CD, Java Performance Tuning |
| **Related** | Java 17 Features, Modules (JPMS), LTS Release Cycle |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:** Most enterprise Java codebases were written for Java 8 (2014 LTS). They rely on Sun/com internal APIs accessed via reflection, bundled Java EE modules (JAXB, JAX-WS), and behaviours that later Java versions actively forbid. Running such a codebase on Java 17 without migration work produces a torrent of `InaccessibleObjectException` errors, broken third-party libraries, and broken builds.

**THE BREAKING POINT:** Java 9 introduced the module system (JPMS) and *strong encapsulation*. From Java 16 onwards, `--illegal-access=deny` is the default. Any library or application using `setAccessible(true)` on JDK-internal classes breaks silently on Java 16 and fatally on Java 17. The ecosystem has had years to adapt - but codebases frozen at Java 8 have not.

**THE INVENTION MOMENT:** A structured migration path exists. It is not a single leap but a series of checkpoints: compile under 11 LTS, fix warnings under 11, upgrade to 17 LTS, fix errors. Each step is independently shippable, testable, and reversible.

---

### 📘 Textbook Definition

**Java 8 to Java 17 migration** is the process of updating a Java application from the Java SE 8 platform to Java SE 17 LTS. It involves: updating the build tool compiler target, resolving removed and encapsulated APIs, addressing module system incompatibilities, upgrading third-party library versions, enabling and validating LTS-specific GC improvements, and adopting new language features (records, sealed classes, text blocks, switch expressions, pattern matching). Java 17 is a Long-Term Support release with free Oracle builds available and vendor support until at least 2029.

---

### ⏱️ Understand It in 30 Seconds

**One line:** Java 8 to 17 migration means fixing encapsulation violations, replacing removed APIs, and optionally adopting new features - done in two LTS hops.

> Moving from Java 8 to Java 17 is like renovating a house built in 2014: the structure is sound, but the wiring, pipes, and fixtures need updating before you can pass modern inspection.

**One insight:** You do not have to adopt the module system (JPMS) to compile on Java 17. You can stay on the classpath and use `--add-opens` flags as temporary shims while migrating library by library.

---

### 🔩 First Principles Explanation

**CORE INVARIANTS:**
1. Java maintains backward compatibility for public APIs; it breaks *internal* API access (e.g., `sun.misc.*`, `com.sun.*`).
2. Modules enforce strong encapsulation at runtime; the classpath is an unnamed module with looser rules.
3. A library compiled for Java 8 runs on Java 17 as long as it does not touch encapsulated internals.
4. Build tools must be updated independently of application source: Maven 3.8+, Gradle 7+.
5. LTS-to-LTS migration (8 → 11 → 17) is safer than a single large hop.

**DERIVED DESIGN:**
- **Phase 1 (compile):** Bump compiler to `--release 11`, fix API deprecation warnings.
- **Phase 2 (runtime):** Add `--add-opens` flags for remaining reflective access violations; verify with integration tests.
- **Phase 3 (libraries):** Upgrade Lombok, Spring Boot, Jackson, Hibernate to Java-17-certified versions.
- **Phase 4 (language):** Optionally replace boilerplate with records, text blocks, switch expressions.

**THE TRADE-OFFS:**
**Gain:** G1 GC improvements, ZGC availability, new language features, security patches, vendor support, 10–25% throughput gain from JIT improvements (Java 11–17).
**Cost:** Migration effort (days to weeks), required library upgrades, potential `--add-opens` flags that reveal architectural debt.

---

### 🧪 Thought Experiment

**SETUP:** Your team has a Spring Boot 2.3 / Java 8 application using Lombok, Jackson, and a proprietary PDF library that calls `sun.font.FontDesignMetrics` via reflection.

**WHAT HAPPENS WITHOUT MIGRATION PLANNING:** You set `java.version = 17` in your CI pipeline. The build fails with 40 Lombok annotation errors (Lombok 1.18.8 does not support Java 17). The runtime fails with `InaccessibleObjectException` on the PDF library. Spring Boot 2.3 is EOL and has no Java 17 patches. Three weeks of emergency firefighting ensue.

**WHAT HAPPENS WITH MIGRATION PLANNING:** You audit with `jdeprscan`, run `--illegal-access=warn` on Java 11 to enumerate reflective access violations, upgrade Lombok and Spring Boot first, and add targeted `--add-opens` flags for the PDF library until a new version ships. Each step is a separate PR, tested independently.

**THE INSIGHT:** Treat library upgrades and JDK upgrades as separate workstreams. Upgrade libraries first on Java 8, verify, then bump the JDK. Never change both simultaneously.

---

### 🧠 Mental Model / Analogy

> Migrating from Java 8 to Java 17 is like upgrading a city's building codes. Most buildings (libraries) need only minor changes to pass inspection. A few violate new safety rules (internal API access) and must be renovated. A handful are condemned and need complete replacement (removed APIs, EOL libraries).

- **Building codes** → Java module system / strong encapsulation rules
- **Structural changes** → removed APIs (JAXB, RMI Activation, Security Manager)
- **Minor violations** → illegal reflective access (fixed with `--add-opens`)
- **Condemned buildings** → libraries with no Java 17 release (must replace)
- **Renovation budget** → `--add-opens` and `--add-modules` flags (temporary exemptions)

Where this analogy breaks down: unlike buildings, library upgrades can introduce breaking API changes independent of the JDK version - you must test both axes.

---

### 📶 Gradual Depth - Four Levels

**Level 1 - What it is (anyone can understand):**
Java 17 is a newer, better version of Java with improved speed, security, and features. Getting your old Java 8 code to run on Java 17 requires fixing a few things that have changed - mainly, some internal shortcuts the old code was using that are no longer allowed.

**Level 2 - How to use it (junior developer):**
Set your Maven/Gradle compiler to `--release 11`. Run your test suite. Look for `InaccessibleObjectException` and `WARNING: An illegal reflective access` messages. Add `--add-opens` for any violations temporarily. Upgrade your major library versions (Spring Boot 3.x, Lombok 1.18.30+, Hibernate 6.x). Then bump to `--release 17` and test again.

**Level 3 - How it works (mid-level engineer):**
Java 9 introduced the JPMS, splitting the JDK into named modules with explicit package exports. The unnamed classpath module can access exported packages but not encapsulated ones. `--add-opens module/package=ALL-UNNAMED` opens a specific package for reflective access. `--add-modules` restores removed Java EE modules (e.g., `java.xml.bind` for JAXB). Java 11 removed the Java EE modules entirely - you must add `jakarta.xml.bind-api` as a Maven dependency instead.

**Level 4 - Why it was designed this way (senior/staff):**
Strong encapsulation is the JDK team's mechanism for evolving internal APIs without backward-compatibility guarantees. Prior to Java 9, libraries like Spring, Hibernate, and Guava routinely accessed `sun.misc.Unsafe`, `sun.reflect.ReflectionFactory`, and `com.sun.xml.internal.*` - APIs that were never meant to be public. This made JDK evolution impossible without breaking half the ecosystem. The module system provides the language-enforced boundary that lets the JDK team remove, refactor, and optimise internal classes. The migration pain is the cost of years of implicit API boundary violations being made explicit.

---

### ⚙️ How It Works (Mechanism)

```
  Java 8 Classpath (unnamed module)
  ─────────────────────────────────
  All JDK internals accessible via
  reflection (setAccessible = true)

  Java 9-15: --illegal-access=permit
  ─────────────────────────────────
  Reflective access logs WARNING
  App still runs, but warns

  Java 16: --illegal-access=warn (default)
  ─────────────────────────────────
  Strong encapsulation ON
  setAccessible throws
  InaccessibleObjectException

  Java 17: --illegal-access=deny (default)
  ─────────────────────────────────
  All internal access denied
  --add-opens required explicitly
  ─────────────────────────────────
  Module boundaries enforced by JVM
```

---

### 🔄 The Complete Picture - End-to-End Flow

**NORMAL FLOW:**
```
  STEP 1: Audit & Prepare (Java 8)
    jdeprscan --release 11 myapp.jar
    Add dependency-check plugin to Maven
    │
    ▼
  STEP 2: Compile under Java 11 LTS     ← YOU ARE HERE
    Set --release 11 in pom.xml
    Fix compiler deprecation warnings
    │
    ▼
  STEP 3: Runtime test on Java 11
    Run with --illegal-access=warn
    Collect all WARNING lines
    Add --add-opens for each
    │
    ▼
  STEP 4: Upgrade libraries
    Spring Boot → 3.x (Jakarta EE 10)
    Lombok      → 1.18.30+
    Hibernate   → 6.x
    Jackson     → 2.15+
    │
    ▼
  STEP 5: Bump to Java 17
    Change CI java-version to 17
    Replace JAXB dependency with
    jakarta.xml.bind-api
    │
    ▼
  STEP 6: Adopt new features (optional)
    Replace POJOs with Records
    Replace instanceof-cast with
    pattern matching
    Adopt text blocks for SQL/JSON
```

**FAILURE PATH:**
- Library with no Java 17 artifact → fork, patch, or replace.
- `--add-opens` not inherited by subprocess / agent → pass via `JAVA_TOOL_OPTIONS`.
- Annotation processor (Lombok) incompatibility → pin exact Lombok version; check matrix.

**WHAT CHANGES AT SCALE:**
In a microservices fleet, upgrade services leaf-first (services with fewest dependencies). Share a common parent POM with Java 17 compiler settings. Gate the upgrade behind a feature flag in CI so teams can opt-in incrementally.

---

### 💻 Code Example

```xml
<!-- BAD - Java 8 Maven setup, no module awareness -->
<properties>
  <maven.compiler.source>1.8</maven.compiler.source>
  <maven.compiler.target>1.8</maven.compiler.target>
</properties>
```

```xml
<!-- GOOD - Java 17 Maven setup with release flag -->
<properties>
  <java.version>17</java.version>
  <maven.compiler.release>17</maven.compiler.release>
</properties>

<dependencies>
  <!-- Replace removed java.xml.bind module -->
  <dependency>
    <groupId>jakarta.xml.bind</groupId>
    <artifactId>jakarta.xml.bind-api</artifactId>
    <version>4.0.0</version>
  </dependency>
  <dependency>
    <groupId>com.sun.xml.bind</groupId>
    <artifactId>jaxb-impl</artifactId>
    <version>4.0.3</version>
    <scope>runtime</scope>
  </dependency>
</dependencies>
```

```bash
# Add to JVM launch args for reflective access
# until libraries ship Java 17 patches
--add-opens java.base/java.lang=ALL-UNNAMED
--add-opens java.base/java.util=ALL-UNNAMED
--add-opens java.base/java.lang.reflect=ALL-UNNAMED

# Spring Boot Gradle example - pass via bootRun
tasks.named("bootRun") {
    jvmArgs(
      "--add-opens",
      "java.base/java.lang=ALL-UNNAMED"
    )
}
```

```java
// BAD - Java 8 instanceof with cast
if (shape instanceof Circle) {
    Circle c = (Circle) shape;
    return Math.PI * c.radius() * c.radius();
}

// GOOD - Java 17 pattern matching
if (shape instanceof Circle c) {
    return Math.PI * c.radius() * c.radius();
}

// BAD - Java 8 verbose data class
public class Point {
    private final int x;
    private final int y;
    public Point(int x, int y) {
        this.x = x; this.y = y;
    }
    // + getters, equals, hashCode, toString...
}

// GOOD - Java 17 Record
public record Point(int x, int y) {}
```

---

### ⚖️ Comparison Table

| Concern | Java 8 | Java 11 LTS | Java 17 LTS |
|---|---|---|---|
| Internal API access | Allowed silently | Warning via `--illegal-access=warn` | Denied by default |
| JAXB / JAX-WS | Bundled in JDK | Removed - add as dependency | Removed |
| GC default | Parallel GC | G1 GC | G1 GC (ZGC opt-in) |
| Language features | Lambdas, Streams | `var`, HTTP client | Records, Sealed, PM |
| String performance | String.intern() | Compact Strings (Latin-1) | Same + improvements |
| Docker container awareness | No | Yes (`-XX:UseContainerSupport`) | Yes (improved) |
| Oracle LTS support | EOL 2030 (extended) | EOL 2026 | EOL 2029+ |

---

### 🔁 Flow / Lifecycle

```
Phase 1: AUDIT
  jdeprscan, jdeps --jdk-internals
  Identify: removed APIs, internal deps
      │
      ▼
Phase 2: LIBRARY UPGRADE (on Java 8)
  Spring Boot, Lombok, Hibernate
  Hibernate 6 = Jakarta namespace
      │
      ▼
Phase 3: COMPILE ON JAVA 11
  --release 11, fix warnings
  Run full test suite
      │
      ▼
Phase 4: RUNTIME ON JAVA 11
  --illegal-access=warn
  Collect & add --add-opens flags
      │
      ▼
Phase 5: JUMP TO JAVA 17
  --release 17, fix new errors
  Replace JAXB/JAX-WS with deps
      │
      ▼
Phase 6: CLEANUP (optional)
  Remove --add-opens as libs update
  Adopt records, text blocks, PM
```

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| "Java is backward compatible, so 8 code runs on 17 unchanged" | Public API code runs unchanged. Code using internal (`sun.*`, `com.sun.*`) APIs or depending on removed modules breaks. |
| "I need to adopt the module system (JPMS) to use Java 17" | No. Your application can stay on the classpath (unnamed module) indefinitely. JPMS is opt-in. |
| "`--add-opens` is permanent" | It is a *temporary shim*. It re-opens encapsulated packages at runtime; it should be removed once libraries ship Java 17 native fixes. |
| "Upgrading to Java 17 requires upgrading all microservices simultaneously" | Services only need to agree on their own runtime. Internal calls via HTTP/gRPC are Java-version-agnostic. Upgrade service by service. |
| "Spring Boot 2.x works on Java 17" | Spring Boot 2.7 runs on Java 17 with workarounds, but Spring Boot 3.x is required for proper Jakarta EE 10 / Java 17 support. Use 3.x. |

---

### 🚨 Failure Modes & Diagnosis

**Mode 1: `InaccessibleObjectException` at runtime**
**Symptom:** `java.lang.reflect.InaccessibleObjectException: Unable to make ... accessible` - service starts then crashes, or test fails.
**Root Cause:** Library (Hibernate, Lombok, ASM-based proxies) calls `setAccessible(true)` on a JDK-internal class that Java 17 now encapsulates.
**Diagnostic:**
```bash
# Run with Java 11 first to see full warning list
java --illegal-access=warn -jar myapp.jar 2>&1 \
  | grep "WARNING: An illegal reflective access"

# On Java 17, get exact exception
java -jar myapp.jar 2>&1 \
  | grep "InaccessibleObjectException" -A5
```
**Fix:**
```bash
# Temporary: add --add-opens to JVM args
--add-opens java.base/java.lang=ALL-UNNAMED
# Permanent: upgrade the offending library
```
**Prevention:** Run `jdeps --jdk-internals myapp.jar` as part of your CI pipeline. Block PRs that add new internal-API usages.

**Mode 2: `ClassNotFoundException` for JAXB / JAX-WS classes**
**Symptom:** Application starts but fails on first XML marshalling call with `ClassNotFoundException: javax.xml.bind.JAXBContext`.
**Root Cause:** Java EE modules (`java.xml.bind`, `java.activation`) were removed in Java 11. Code still references `javax.xml.bind.*`.
**Diagnostic:**
```bash
jdeps --multi-release 11 \
  --module-path . myapp.jar \
  | grep "javax.xml.bind"
# Shows which classes depend on removed module
```
**Fix:** Add the standalone JAXB dependency:
```xml
<dependency>
  <groupId>jakarta.xml.bind</groupId>
  <artifactId>jakarta.xml.bind-api</artifactId>
  <version>4.0.0</version>
</dependency>
```
**Prevention:** Run `jdeprscan --release 11 myapp.jar` in CI to catch usages of removed APIs before they reach production.

**Mode 3: Spring Boot `BeanCreationException` from Jakarta namespace conflict**
**Symptom:** Spring 3.x application fails to start: `ClassNotFoundException: javax.persistence.Entity` or `javax.servlet.Servlet`.
**Root Cause:** Spring Boot 3.x moved from `javax.*` to `jakarta.*` namespace (Jakarta EE 10). Old Hibernate / Servlet API jars still export `javax.*`.
**Diagnostic:**
```bash
mvn dependency:tree | grep "javax\|jakarta"
# Check for old javax.persistence, javax.servlet
./gradlew dependencies | grep "javax.persistence"
```
**Fix:** Upgrade Hibernate to 6.x, replace `javax.servlet:javax.servlet-api` with `jakarta.servlet:jakarta.servlet-api:6.0.0`. Find-and-replace all `import javax.persistence` to `import jakarta.persistence` in source code.
**Prevention:** Add a Maven Enforcer rule that bans `javax.persistence` and `javax.servlet` artifacts after migration.

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**
- Java Language - understanding what changed in each version
- JVM - runtime architecture that enforces module boundaries
- Modules (JPMS) - the Java Platform Module System introduced in Java 9

**Builds On This (learn these next):**
- Java 17 Features (Records, Sealed, Pattern Matching) - the payoff of migration
- Java Performance Tuning - exploiting G1/ZGC improvements available post-migration
- CI-CD - automating migration validation gates in pipelines

**Alternatives / Comparisons:**
- Kotlin migration - alternative to Java 17 adoption for modern language features
- GraalVM Native Image - requires module-aware code; migration is a prerequisite
- Jakarta EE 10 - the server-side framework migration that accompanies Spring Boot 3.x

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────┐
│ WHAT IT IS    Upgrade path from Java 8 to 17 LTS │
│ PROBLEM SOLVED Encapsulation violations, OOM APIs│
│ KEY INSIGHT   Stay classpath; JPMS is opt-in     │
│ USE WHEN      LTS EOL approaching; security push │
│ AVOID WHEN    - (not avoidable; plan it properly)│
│ TRADE-OFF     Migration effort vs 10yr support   │
│ ONE-LINER     8→11→17 in phases, libs first      │
│ NEXT EXPLORE  Java 17 Features, GC Tuning        │
└──────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

1. **(A - System Interaction)** Your service uses Java serialization (`ObjectInputStream`) to deserialize objects from a message queue. Java 17's strong encapsulation changes how the serialization mechanism accesses private fields. What specific `--add-opens` flags would be required, and what long-term alternative removes this dependency entirely?

2. **(B - Scale)** You are migrating 40 microservices from Java 8 to Java 17. Each service has a different Spring Boot version. What ordering strategy minimises risk - and why should library upgrades and JDK version bumps be separate PRs rather than combined?

3. **(F - Comparison)** The `--add-opens` flag and the `--module-path` with an `opens` directive in `module-info.java` both allow reflective access. What is the architectural difference between the two approaches, and which is appropriate for production versus migration phases?
