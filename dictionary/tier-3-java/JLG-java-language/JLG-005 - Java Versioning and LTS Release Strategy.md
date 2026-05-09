---
id: JLG-005
title: Java Versioning and LTS Release Strategy
category: Java Language
tier: tier-3-java
folder: JLG-java-language
difficulty: ★☆☆
depends_on: JLG-001
used_by: JLG-041
related: JLG-002, JLG-043, JLG-049
tags:
  - java
  - foundational
  - bestpractice
  - production
status: complete
version: 1
layout: default
parent: "Java Language"
grand_parent: "Technical Dictionary"
nav_order: 5
permalink: /jlg/java-versioning-and-lts-release-strategy/
---

# JLG-005 - Java Versioning and LTS Release Strategy

⚡ TL;DR - Since Java 9, Java releases every 6 months; LTS versions (8, 11, 17, 21, 25) receive multi-year security patches and are the only versions safe for production enterprise use.

| Field          | Value                                                                                                                                                               |
| -------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Depends on** | [[JLG-001 - What Is Java - History and Philosophy]]                                                                                                                 |
| **Used by**    | [[JLG-041 - Java Version Migration Strategy (8 to 17 to 21)]]                                                                                                       |
| **Related**    | [[JLG-002 - The Java Ecosystem Map (SE, EE, ME, Android)]], [[JLG-043 - Java Modularity Strategy (JPMS)]], [[JLG-049 - Java Language Design History and Rationale]] |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**

Before Java 9, Java releases were infrequent and enormous. Java 5 took 2 years, Java 6 took 3 years, Java 7 took 5 years, Java 8 took 2 years. Developers waited years for language improvements. Features were bundled, delayed by unfinished components, and shipped in massive breaking batches. The Java 8 → Java 9 gap took 3.5 years partly because the module system (Project Jigsaw) delayed the entire release.

**THE BREAKING POINT:**

Java 9's delay to September 2017 (originally targeted 2016) from a single unfinished feature (JPMS) demonstrated that the "big bang" release model was unsustainable. Oracle had spent years engineering JVM improvements that could not ship because one feature was blocking the release. The community was frustrated; developers could not plan around an unpredictable release cadence.

**THE INVENTION MOMENT:**

Oracle adopted a **time-based 6-month release cadence** starting with Java 9 (September 2017), inspired by the Ubuntu LTS model. Features that are ready ship; features that aren't defer to the next release. No feature can block the release. Every March and September, a new Java version ships. This transformed Java from a language with years-long waits to a language with continuous incremental improvement.

**EVOLUTION:**

- **Java 8 (2014):** Last "big bang" release. LTS. Lambdas, streams, Optional - most significant Java release since Java 1.0
- **Java 9 (Sept 2017):** First time-based release. Module system (JPMS). Also last release where Oracle JDK was free for commercial use
- **Java 11 (Sept 2018):** First LTS in new cadence. Oracle JDK commercial licence required; OpenJDK free alternative
- **Java 17 (Sept 2021):** LTS. Sealed classes, pattern matching, records GA. Free Oracle JDK reinstated (NFTC licence)
- **Java 21 (Sept 2023):** LTS. Virtual threads GA, structured concurrency, pattern matching for switch GA, sequenced collections
- **Java 25 (Sept 2025):** Upcoming LTS. Project Valhalla value types expected

---

### 📘 Textbook Definition

**Java's release strategy** consists of two release types:

**Feature releases** (non-LTS): Shipped every 6 months (March and September). Supported for 6 months only (until the next release). Contains features in various states - GA (generally available), Preview (requires `--enable-preview` flag), and Incubator (via `jdk.incubator.*` modules). Not suitable for production enterprise use.

**LTS releases (Long-Term Support):** Every 4th major release receives multi-year maintenance. Oracle provides 8+ years of commercial support; vendors (Red Hat, Amazon, Azul, SAP) provide LTS for their OpenJDK distributions. LTS releases contain only GA features - no previews or incubators in production code.

**Current LTS versions:** Java 8 (EOL Sept 2030 for most vendors), Java 11 (EOL Sept 2026), Java 17 (EOL Sept 2029), Java 21 (EOL Sept 2031).

---

### ⏱️ Understand It in 30 Seconds

**One line:** Java ships every 6 months; LTS versions (8, 11, 17, 21, 25) are the only versions for production; non-LTS versions expire in 6 months.

> Java releases are like a train service: a new train departs every 6 months (feature releases). Most passengers use the express trains (LTS) that run for years and are maintained reliably. Short-distance commuters can ride the local trains (non-LTS) but they stop running after 6 months and there's no guarantee they'll be maintained.

**One insight:** The 6-month cadence means you can try features in Preview across 2-3 releases before they are finalised as GA. Pattern matching took 3 preview cycles (Java 14-16) before GA in Java 16. This preview process is how Java prevents permanent API mistakes.

---

### 🔩 First Principles Explanation

**CORE INVARIANTS:**

1. Every Java release is strictly forward-compatible with the previous release (code compiled on Java N runs on Java N+1)
2. Preview features require `--enable-preview` flag; they are explicitly not stable API contracts
3. LTS versions receive security patches for years; non-LTS versions receive only 6 months of critical fixes
4. The `--release N` flag pins bytecode to a specific class format version, preventing newer APIs from being used
5. OpenJDK and Oracle JDK are now functionally identical for most users; Oracle JDK adds extra telemetry and some support tooling

**DERIVED DESIGN:**

From invariant 1 → upgrading Java is generally safe (forward compatibility). The risk is not that old code breaks; the risk is deprecated APIs becoming removed, or `sun.*` / `com.sun.*` internal APIs breaking.
From invariant 3 → using Java 16 in production (a non-LTS version) means your runtime will receive no security patches after 6 months. Production systems must use LTS.
From invariant 4 → `mvn compiler plugin <release>17</release>` ensures code compiled on Java 21 JDK will run on Java 17 JRE without using Java 18-21 APIs.

**THE TRADE-OFFS:**

**Gain:** Continuous incremental improvement; no multi-year waits; preview process prevents permanent API mistakes; 6-month feedback cycle for experimental features.

**Cost:** Organizations must decide "which LTS to track" rather than just "upgrade when new Java ships." Non-LTS versions require 6-monthly upgrades (teams that track non-LTS face upgrade treadmill). Preview features in non-LTS code must be removed or promoted before that version expires.

**ESSENTIAL vs ACCIDENTAL COMPLEXITY:**

**Essential:** Long support periods for production systems are genuinely required. Banks cannot upgrade their JVM every 6 months. LTS addresses this real constraint.

**Accidental:** The preview feature mechanism adds complexity for library authors who must decide whether to support preview APIs in their libraries. Most library authors avoid preview APIs until GA.

---

### 🧪 Thought Experiment

**SETUP:** It is 2017. Oracle must decide: release Java 9 now (with JPMS), or delay 6 more months to polish one more feature. They've already delayed 18 months for JPMS.

**WITHOUT 6-month cadence (old model):**

Delay to polish: 6-month delay becomes 12 months because the next feature isn't ready either. The community waits. JVM engineers working on completed improvements (GC algorithms, JIT improvements) cannot ship their work. The frustration compounds. Java 11 doesn't ship until 2020.

**WITH 6-month cadence (new model):**

Ship what's ready. JPMS ships incomplete with known limitations. Developers use it experimentally. Feedback in Java 10-11 reveals the real-world problems. Java 11 addresses the most critical JPMS gaps with information from 6 months of production use. The improvements are better because they are informed by real usage, not guesses.

**THE INSIGHT:**

The preview feature mechanism (ship as preview, get feedback, finalise in 2-3 releases) is the core innovation of the 6-month cadence. It transforms language design from "design in the dark, ship once" to "design, experiment, refine, finalise" - a feedback loop that Java never had in its first 20 years.

---

### 🧠 Mental Model / Analogy

> Java releases are like software product version management with a rolling support window. LTS versions are "stable releases" in the Ubuntu model - 5-year support, conservative changes, production-ready. Non-LTS versions are "interim releases" - 6-month support, experimental features, cutting-edge but ephemeral. Most servers run Ubuntu LTS; enthusiasts run interim releases for new features. Most enterprises run Java LTS; individual developers experiment with non-LTS.

**Element mapping:**

- Ubuntu LTS (18.04, 20.04, 22.04) → Java LTS (11, 17, 21)
- Ubuntu interim (21.10, 22.10) → Java non-LTS (14, 15, 16, 18, 19, 20, 22, 23, 24)
- 5-year Ubuntu LTS support → 8-year Oracle Java LTS support
- Ubuntu update-manager → Maven `compiler.source/target/release`

Where this analogy breaks down: Ubuntu interim releases are still production-supported for their 9-month window; Java non-LTS receives minimal support and is explicitly not recommended for production by most enterprise vendors.

---

### 📶 Gradual Depth - Four Levels

**Level 1 - What it is (anyone can understand):**
Java releases a new version every 6 months. Most companies only use the "LTS" (Long-Term Support) versions - Java 8, 11, 17, and 21 - because these get security updates for years. The other versions are for testing new features and expire after 6 months.

**Level 2 - How to use it (junior developer):**
Set your JDK to the latest LTS (Java 21 as of 2024). In Maven: `<java.version>21</java.version>` and Spring Boot's parent POM propagates this correctly. In Gradle: `java { toolchains { languageVersion = JavaLanguageVersion.of(21) } }`. Use `--release 17` (not `--source`/`--target`) to pin bytecode to Java 17 if deploying to a Java 17 JRE.

**Level 3 - How it works (mid-level engineer):**
Each Java version increments the class file format major version (Java 8 = 52, Java 17 = 61, Java 21 = 65). The `--release N` flag (introduced Java 9) compiles bytecode targeting class version N AND restricts which Java SE APIs can be used to those available in Java N. This is safer than `--source N --target N` which allowed using newer APIs in old-targeted code, causing `NoSuchMethodError` at runtime. Preview features are flagged with `ACC_MODULE`/`ACC_PREVIEW` in bytecode; the JVM refuses to run them without `--enable-preview`.

**Level 4 - Why it was designed this way (senior/staff):**
The 4-release LTS cycle (Java 17, 21, 25, 29...) was a deliberate balance between two constituencies: individual developers who wanted faster innovation, and enterprise users who needed multi-year stability. The 4-release cycle means LTS is updated every 2 years (at the 6-month cadence, release 1, 2, 3, 4 → LTS at release 4). This is roughly equivalent to Ubuntu LTS's 2-year cycle. The OpenJDK governance structure (JCP, JEP process) ensures that Oracle cannot unilaterally change the LTS cadence; it requires JCP Executive Committee consensus. This governance structure was a deliberate protection against Oracle repeating the Java EE slow-walking that led to the Jakarta EE transfer.

**Expert Thinking Cues:**

- `--release` flag vs `--source`/`--target`: always prefer `--release`; it prevents "compiles but fails at runtime" errors from using APIs not available in the target JRE
- Oracle JDK vs OpenJDK: functionally identical since Java 11; choose by vendor support commitment (Temurin, Corretto, Zulu all provide free LTS)
- Preview features: enabled per-project with `--enable-preview`; every .class file using preview is marked; running requires `--enable-preview` on JVM too

---

### ⚙️ How It Works (Mechanism)

```
Java Release Timeline (6-month cadence):

Mar 2022: Java 18 (non-LTS, expires Sep 2022)
Sep 2022: Java 19 (non-LTS, expires Mar 2023)
Mar 2023: Java 20 (non-LTS, expires Sep 2023)
Sep 2023: Java 21 (LTS ← 8yr support window)
Mar 2024: Java 22 (non-LTS, expires Sep 2024)
Sep 2024: Java 23 (non-LTS, expires Mar 2025)
Mar 2025: Java 24 (non-LTS, expires Sep 2025)
Sep 2025: Java 25 (LTS ← next LTS target)

Feature lifecycle:
Preview (N)   → Preview (N+1)   → GA (N+2)
  [--enable-preview]              [standard]
```

---

### 🔄 The Complete Picture - End-to-End Flow

**NORMAL FLOW - deciding which Java version to use:**

```
[Project starts or version review needed]
     |
     ├─ Is this production? → YES
     |    ← YOU ARE HERE
     |
     ├─ Use LTS only: Java 8, 11, 17, or 21
     |
     ├─ Which LTS?
     |    ├─ Java 8: only if legacy Spring/EE
     |    ├─ Java 11: EOL Sept 2026, plan migration
     |    ├─ Java 17: stable, widely supported
     |    └─ Java 21: latest LTS, virtual threads
     |
     ├─ Set in build tool:
     |    └─ maven: <release>21</release>
     |    └─ gradle: JavaLanguageVersion.of(21)
     |
[CI pins JDK version via .java-version or toolchain]
[Deploy JRE matches compile --release version]
```

**FAILURE PATH:**

- Deploying code compiled with `--release 21` to a Java 17 JRE → `UnsupportedClassVersionError` at startup
- Using a preview feature in production code without `--enable-preview` on the deployed JVM → `ClassFormatError`
- Running Java 16 (non-LTS) in production past its 6-month support window → unpatched CVEs

**WHAT CHANGES AT SCALE:**

Large organisations with 100+ services cannot upgrade all services to every new LTS simultaneously. Standard practice: pin all services to LTS N; create a migration lane for LTS N+1; give teams 12-18 months to migrate before N becomes EOL.

---

### 💻 Code Example

**Pinning Java version in Maven correctly:**

```xml
<!-- BAD: --source/--target permits using APIs
     from newer Java despite target version -->
<plugin>
  <artifactId>maven-compiler-plugin</artifactId>
  <configuration>
    <source>17</source>
    <target>17</target>
    <!-- Bug: can still use Java 21 APIs!
         Causes NoSuchMethodError at runtime
         on Java 17 JRE -->
  </configuration>
</plugin>

<!-- GOOD: --release restricts to Java 17 API
     surface AND targets Java 17 class format -->
<properties>
  <java.version>21</java.version>
  <maven.compiler.release>21</maven.compiler.release>
</properties>
```

**Gradle toolchain (modern approach):**

```groovy
// GOOD: Gradle toolchain auto-downloads JDK
java {
    toolchain {
        languageVersion =
            JavaLanguageVersion.of(21)
        vendor =
            JvmVendorSpec.ADOPTIUM
    }
}
// Gradle downloads Temurin JDK 21 if not present
// Reproducible builds across machines
```

**Using a preview feature safely:**

```java
// Preview features require explicit opt-in
// In Maven: <compilerArgs>--enable-preview</compilerArgs>
// In JVM: java --enable-preview -jar app.jar

// Java 21 preview: unnamed patterns in switch
Object obj = getShape();
switch (obj) {
    case Integer i when i > 0 ->
        System.out.println("Positive: " + i);
    case String s ->
        System.out.println("String: " + s);
    default ->
        System.out.println("Other");
}
```

---

### ⚖️ Comparison Table

| Java Version | Release  | Type          | Status (2025)           | Key Features                                                    |
| ------------ | -------- | ------------- | ----------------------- | --------------------------------------------------------------- |
| Java 8       | Mar 2014 | LTS           | EOL 2030 (most vendors) | Lambdas, streams, Optional, Date/Time                           |
| Java 11      | Sep 2018 | LTS           | EOL Sep 2026            | HTTP client, var in lambdas, JEP 320 (remove EE modules)        |
| Java 17      | Sep 2021 | LTS           | EOL Sep 2029            | Sealed classes, records GA, pattern matching switch preview     |
| Java 21      | Sep 2023 | LTS           | EOL Sep 2031            | Virtual threads GA, structured concurrency, pattern matching GA |
| Java 25      | Sep 2025 | LTS (planned) | Future                  | Project Valhalla value types expected                           |
| Java 22-24   | 2024     | Non-LTS       | Expired / Expiring      | Unnamed patterns, stream gatherers, FFM API GA                  |

---

### ⚠️ Common Misconceptions

| Misconception                                                  | Reality                                                                                                                                                                                                                 |
| -------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| "We should upgrade to every new Java version to get features"  | Non-LTS versions expire in 6 months with no security patches. Only upgrade to LTS in production.                                                                                                                        |
| "Oracle JDK is better than OpenJDK"                            | Since Java 11, Oracle JDK and OpenJDK are functionally identical for most users. Oracle JDK adds commercial support. Temurin (Adoptium) is Oracle JDK-equivalent and free.                                              |
| "`--source`/`--target` pins the Java API surface"              | No. Only `--release` pins the API surface. `--source 17 --target 17` can still use Java 21 APIs in source code, causing `NoSuchMethodError` at runtime on Java 17.                                                      |
| "Preview features are safe to use in production"               | Preview features are explicitly not finalized API. They change or are removed between releases. Running them requires `--enable-preview` on the JVM, which is not supported by most production deployment policies.     |
| "Java 8 will be supported forever so we don't need to upgrade" | Oracle's free (NFTC) support for Java 8 ended in December 2020. Most vendors (Temurin, Corretto) provide paid-only security updates after 2026. Security vulnerabilities in Java 8 will stop being patched on schedule. |

---

### 🚨 Failure Modes & Diagnosis

**Mode 1: Non-LTS version used in production past EOL**

**Symptom:** Security scan reports CVE in Java 16 runtime; vendor patches available only for Java 17+.

**Root Cause:** Team upgraded to Java 16 (non-LTS) for a specific feature; 6-month support window expired; no patches available.

**Diagnostic:**

```bash
# Check current Java version
java -version
# Check EOL date at adoptium.net
# For non-LTS: EOL is 6 months from release
# Java 16 released Mar 2021, EOL Sep 2021
```

**Fix:** Upgrade to Java 17 LTS immediately. Audit for Java 16-specific APIs used (`jdk.incubator.*` modules from Java 16 may not exist in 17).

**Prevention:** Never use non-LTS in production. Pin LTS in company standards. Add Java version check to CI: fail builds targeting non-LTS versions.

---

**Mode 2: `--source`/`--target` mismatch causes NoSuchMethodError**

**Symptom:** Application compiles successfully on developer's Java 21 JDK; fails at runtime on Java 17 JRE with `NoSuchMethodError: String.stripIndent()`.

**Root Cause:** Build uses `--source 17 --target 17` but developer's code calls `String.stripIndent()` (added in Java 15). The `--target` flag sets class file format version but does NOT restrict which Java APIs can be called.

**Diagnostic:**

```bash
# Check class file version
javap -verbose MyClass.class | grep "major version"
# major version: 61 = Java 17 (correct)
# But the code still calls Java 21 APIs

# Recompile with --release to catch the error:
javac --release 17 MyClass.java
# Error: cannot find symbol: method stripIndent()
```

**Fix:** Replace `--source`/`--target` with `--release` in all build configurations.

**Prevention:** Add `maven-enforcer-plugin` rule requiring `<release>` instead of `<source>`/`<target>`. Catch in code review.

---

**Mode 3: Java version mismatch between build and runtime (Security)**

**Symptom:** Application compiled with Java 21 (`class version 65`) deployed to Java 11 JRE; fails at startup. Attacker exploits the deployment confusion to delay security patches.

**Root Cause:** Build pipeline compiles with latest Java; deployment target is pinned to older JRE. The mismatch is undetected until production startup. Security patches for the newer Java are available but never applied because the deployed JRE is older.

**Diagnostic:**

```bash
# Check compiled version
unzip -p app.jar BOOT-INF/classes/com/example/App.class \
  | head -c 8 | xxd | grep "0041\|003d\|0034"
# 0x003d = 61 (Java 17), 0x0041 = 65 (Java 21)

# Check deployed JRE version
java -version 2>&1 | head -1
```

**Fix:** Add a CI gate that checks deployed JRE version matches compiled `--release` version. Pin both compile and runtime Java versions in Kubernetes deployments via container image.

**Prevention:** Use Gradle Java Toolchains in CI - toolchain declaration ensures build and test use the same JDK version. Pin base Docker image: `FROM eclipse-temurin:21-jre`.

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**

- [[JLG-001 - What Is Java - History and Philosophy]] - Java's history and design

**Builds On This (learn these next):**

- [[JLG-041 - Java Version Migration Strategy (8 to 17 to 21)]] - how to execute the upgrade
- [[JLG-043 - Java Modularity Strategy (JPMS)]] - JPMS introduced in Java 9

**Alternatives / Comparisons:**

- Python release strategy - Python 2→3 chose breaking compatibility; Java chose backwards compatibility; contrasting approaches
- .NET release cadence - Microsoft's aligned release cadence (similar 6-month rhythm, LTS every other release)

---

### 📌 Quick Reference Card

```
+----------------------------------------------------------+
| WHAT IT IS    | Java's 6-month release cadence with LTS  |
|               | at every 4th release (Java 21, 25, ...)  |
| PROBLEM       | Unpredictable release schedule blocked    |
|               | features for years (Java 8→9: 3.5 years) |
| KEY INSIGHT   | Production must use LTS only; non-LTS    |
|               | expires in 6 months with no security fix |
| USE WHEN      | Selecting Java version for new project,  |
|               | planning migration from old LTS          |
| AVOID WHEN    | N/A - foundational knowledge for all     |
|               | Java developers                          |
| TRADE-OFF     | Faster innovation (6-month cadence) vs   |
|               | upgrade overhead for LTS-only shops      |
| ONE-LINER     | Use LTS only in production; preview      |
|               | features experimental only; --release    |
|               | not --source/--target                    |
| NEXT EXPLORE  | JLG-041 (Migration Strategy),            |
|               | JLG-043 (JPMS from Java 9)               |
+----------------------------------------------------------+
```

**If you remember only 3 things:**

1. Production must use LTS only: Java 8, 11, 17, 21, 25 - non-LTS versions expire in 6 months with no security patches
2. Use `--release N` not `--source N --target N` - only `--release` restricts the API surface to prevent `NoSuchMethodError` at runtime
3. Oracle JDK and Adoptium Temurin are functionally equivalent since Java 11 - choose Temurin (free) or Corretto (AWS) for production

**Interview one-liner:** "Since Java 9, Java ships every 6 months; every 4th release is LTS (8, 11, 17, 21, 25) with multi-year security support; production systems must use LTS only; `--release` pins both bytecode format and API surface; Oracle JDK and OpenJDK distributions like Temurin are functionally identical since Java 11."

---

### 💎 Transferable Wisdom

**Reusable Engineering Principle:** _Predictable release cadences with explicit support windows reduce ecosystem anxiety and enable long-term planning._ When release schedules are unpredictable (old Java), ecosystem participants cannot plan. When release schedules are predictable (Ubuntu LTS, modern Java), infrastructure teams can create migration lanes, library authors can target specific versions, and enterprises can commit multi-year support budgets.

**Where else this pattern appears:**

- **Ubuntu LTS model** - 2-year LTS cycle with 5-year support; non-LTS interim releases for enthusiasts; same economic rationale as Java LTS
- **Spring Framework releases** - Spring Boot LTS releases align with Java LTS; Spring 3.x targets Java 17+; organizations upgrade Spring when they upgrade Java
- **Node.js LTS** - even-numbered Node.js versions are LTS (16, 18, 20, 22); odd-numbered (17, 19, 21) are non-LTS; identical model to Java

---

### 💡 The Surprising Truth

The 6-month Java release cadence was not adopted because Oracle decided it was technically superior - it was adopted because Oracle was facing an existential threat to Java's reputation. By 2016, Go had been released (2009), Kotlin had been announced (2011), and the Java community's frustration with 3.5-year release gaps was vocal and public. The JVM language ecosystem (Kotlin, Scala, Groovy) was growing because developers could get features in those languages that were stuck in Java's slow release process. Oracle's adoption of the 6-month cadence was a competitive defensive move. The preview feature mechanism - which allows Oracle to ship experimental features without permanent API commitments - was explicitly designed to let Oracle compete with Kotlin's rapid feature delivery without risking permanent mistakes in Java's backwards-compatible API surface.

---

### 🧠 Think About This Before We Continue

**Question 1 (C - Design Trade-off):** Java's backwards compatibility guarantee means code compiled on Java 5 runs on Java 21. This enables 30-year codebases but also means Java cannot remove deprecated APIs (they stay forever). Python made the opposite choice with Python 2→3. Describe the industry impact of each choice: what did Python gain and lose with breaking compatibility, and what did Java gain and lose by maintaining it forever?

_Hint:_ Python 2 reached EOL January 2020 - 11 years after Python 3 was released. The migration took a decade. Many Python 2 libraries were never ported. Java's backwards compatibility means Java 8 code still runs in 2025, but also means `Date`, `Calendar`, and `Vector` (all deprecated for 20+ years) still exist in the API.

**Question 2 (A - System Interaction):** A company upgrades from Java 11 to Java 21. The Spring Boot application uses `sun.misc.Unsafe` for a low-latency serialisation library. Java 21 has `--illegal-access=deny` as default (this was the default since Java 17). Describe the specific runtime errors that will appear, the JVM flags available to temporarily allow the access, and the correct long-term fix.

_Hint:_ `sun.misc.Unsafe` is in the `jdk.internal.misc` module in Java 9+. Access from the unnamed module requires `--add-opens java.base/sun.misc=ALL-UNNAMED`. The long-term fix is Project Panama's Foreign Memory API (`java.lang.foreign.MemorySegment`) which provides safe unsafe memory access.

**Question 3 (B - Scale):** A large organisation has 400 microservices spread across Java 8 (150 services), Java 11 (200 services), and Java 17 (50 services). Java 11 EOL is September 2026. Describe the migration strategy: how to prioritise the 200 Java 11 services, how to handle services with framework dependencies (Spring Boot 2 only supports Java 17 via complex workarounds), and how to manage the CI/CD pipeline during a multi-version transition period.

_Hint:_ Spring Boot 2 reaches EOL November 2024. Spring Boot 3 requires Java 17 minimum. The Java 11 → 17 migration and Spring Boot 2 → 3 migration must happen together for Spring Boot services. Services using other frameworks (plain Servlets, custom stacks) can upgrade Java version independently of framework version.
