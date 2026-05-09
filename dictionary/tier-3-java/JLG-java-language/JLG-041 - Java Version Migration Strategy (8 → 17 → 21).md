---
id: JLG-041
title: Java Version Migration Strategy (8 to 17 to 21)
category: Java Language
tier: tier-3-java
folder: JLG-java-language
difficulty: ★★★
depends_on: JLG-005, JLG-043
related: JLG-002, JLG-046, JLG-049
tags:
  - java
  - advanced
  - production
  - bestpractice
status: complete
version: 1
layout: default
parent: "Java Language"
grand_parent: "Technical Dictionary"
nav_order: 41
permalink: /jlg/java-version-migration-strategy-8-17-21/
---

# JLG-041 - Java Version Migration Strategy (8 to 17 to 21)

⚡ TL;DR - Migrating from Java 8 to Java 17 or 21 requires addressing strong encapsulation of internal APIs, the module system's classpath changes, and the javax-to-jakarta namespace rename in Spring Boot 3.

| Field          | Value                                                                                                                                                                     |
| -------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Depends on** | [[JLG-005 - Java Versioning and LTS Release Strategy]], [[JLG-043 - Java Modularity Strategy (JPMS)]]                                                                     |
| **Used by**    | -                                                                                                                                                                         |
| **Related**    | [[JLG-002 - The Java Ecosystem Map (SE, EE, ME, Android)]], [[JLG-046 - Java Language Specification Deep Dive]], [[JLG-049 - Java Language Design History and Rationale]] |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**

A Java 8 production service has been running reliably for 6 years. The team wants to upgrade to Java 21 for virtual threads. They run `java -jar app.jar` on Java 21 and get: `InaccessibleObjectException: Unable to make field accessible`. Three separate libraries use reflection to access private JDK internals. The migration that seemed trivial becomes a multi-month investigation.

**THE BREAKING POINT:**

Java 9 introduced **strong encapsulation**: JDK internal APIs (`sun.*`, `com.sun.*`, `jdk.internal.*`) that were accessible via reflection in Java 8 are now module-encapsulated. Hundreds of popular libraries (Hibernate, Spring, Jackson, Netty) used these internal APIs for performance-critical operations. Upgrading past Java 8 without understanding strong encapsulation produces a cascade of `InaccessibleObjectException` errors.

**THE INVENTION MOMENT:**

The Java team designed a migration path: Java 9-15 allowed `--illegal-access=permit` to temporarily restore Java 8 reflection behaviour. Java 16 changed the default to `--illegal-access=deny`. Java 17 removed `--illegal-access` entirely. This staged approach gave the ecosystem 8 years (2017-2025) to migrate away from internal API usage - but many codebases are only starting this migration now.

**EVOLUTION:**

- **Java 9 (2017):** JPMS introduced; `--illegal-access=permit` default (illegal access logged but allowed)
- **Java 16 (2021):** `--illegal-access=deny` becomes default; reflection access to JDK internals requires explicit `--add-opens`
- **Java 17 (2021):** `--illegal-access` flag removed entirely; `--add-opens` is the only workaround
- **Java 21 (2023):** Stricter sequenced collection API changes; virtual threads change thread-local assumptions
- **Spring Boot 3 (2022):** Requires Java 17 minimum + Jakarta EE 9 (`jakarta.*` namespace)
- **OpenRewrite (2022+):** Automated migration tool for `javax.*` to `jakarta.*`, Java API changes

---

### 📘 Textbook Definition

**Java version migration** is the process of updating a Java application's runtime from one major Java version to a newer one, addressing breaking changes introduced by:

1. **Strong encapsulation (Java 9+):** JDK internal APIs (`sun.misc.Unsafe`, `sun.reflect.*`, `com.sun.*`) are no longer accessible via reflection without explicit `--add-opens` JVM arguments
2. **Removed APIs:** APIs deprecated in Java 8 and removed in later versions (`sun.misc.BASE64Encoder`, `com.sun.image.codec.jpeg.*`)
3. **Module system (JPMS):** Split packages, classpath vs module path, unnamed module restrictions
4. **Jakarta EE namespace:** `javax.*` package renamed to `jakarta.*` in Jakarta EE 9 (required by Spring Boot 3)
5. **Behavioural changes:** GC default changes, thread scheduling changes, serialisation filter defaults

---

### ⏱️ Understand It in 30 Seconds

**One line:** Migrating from Java 8 to 17/21 requires fixing reflection access to JDK internals, removing removed APIs, and (for Spring Boot 3) renaming all `javax.*` imports to `jakarta.*`.

> Java version migration is like renovating a house built to 1970s building codes for 2024 occupancy. The house (application) still stands (compiles), but the wiring (internal API access), plumbing (reflection), and materials (removed APIs) no longer meet code. You can get temporary permits (`--add-opens`) for some non-compliant wiring, but eventually the whole house must be brought up to modern code.

**One insight:** The migration is not linear. Java 8 to Java 17 has more breaking changes than Java 17 to Java 21. The biggest jump is Java 8 to Java 9 (JPMS + strong encapsulation). After Java 9, each subsequent upgrade is incremental.

---

### 🔩 First Principles Explanation

**CORE INVARIANTS:**

1. Strong encapsulation is permanent - `--illegal-access` is gone; `--add-opens` is a temporary workaround, not a solution
2. The module system does not require migration - code that uses the classpath (unnamed module) continues to work in Java 21
3. API removals are permanent - removed APIs cannot be restored with JVM flags
4. Framework upgrades and Java upgrades are coupled - Spring Boot 3 requires Java 17; if you upgrade Spring Boot 3, you must upgrade Java simultaneously
5. Incremental version-by-version migration is lower risk than skipping multiple versions

**DERIVED DESIGN:**

From invariant 1 → every `--add-opens` in a JVM startup script is a technical debt marker indicating a library that must be updated.
From invariant 2 → you do not need to adopt JPMS for your own code to migrate to Java 17/21. The unnamed module (classpath) continues to work.
From invariant 4 → the correct migration order is: (1) upgrade to Spring Boot 3 and Java 17 together; (2) then upgrade to Java 21 separately. Do not decouple these when Spring Boot is involved.

**THE TRADE-OFFS:**

**Gain:** Virtual threads (Java 21); sealed classes; records; pattern matching; better GC (ZGC, Shenandoah); security patches; modern API access (HTTP/2 client, text blocks, var).

**Cost:** Migration effort (typically 1-4 weeks per service depending on library debt); breaking change analysis for each library; potential `--add-opens` flags while waiting for library updates; `javax` to `jakarta` rename across large codebases.

**ESSENTIAL vs ACCIDENTAL COMPLEXITY:**

**Essential:** Strong encapsulation is genuinely an improvement - JDK internal API usage in libraries was a maintenance and security burden on the JDK team.

**Accidental:** The `javax` to `jakarta` namespace rename was a governance necessity (Oracle retained the `javax` trademark) but created enormous accidental migration complexity for no functional benefit.

---

### 🧪 Thought Experiment

**SETUP:** A Spring Boot 2.7 application using Hibernate 5 and Jackson 2.13 runs on Java 11. The team attempts to upgrade to Java 17.

**WITHOUT migration planning:**

Run `java 17 -jar app.jar`. Hibernate's `EnhancerImpl` throws `InaccessibleObjectException` trying to enhance entities via reflection. Add `--add-opens java.base/java.lang=ALL-UNNAMED`. Application starts. 2 weeks later in production: `NoSuchMethodError: sun.reflect.ReflectionFactory`. Jackson's internal class generation path fails. Add another `--add-opens`. Now Spring's `ReflectionUtils` fails. The application accumulates 15 `--add-opens` flags. None of these flags are documented; they are discovered through error messages.

**WITH migration planning:**

1. Run `jdeps --jdk-internals app.jar` to discover all JDK internal usages upfront
2. Map each usage to its library: Hibernate 5 → upgrade to Hibernate 6; Jackson 2.13 → 2.15+ (no internal API usage)
3. Upgrade libraries BEFORE upgrading Java; confirm zero internal API usage
4. Upgrade Java with zero `--add-opens` flags needed

**THE INSIGHT:**

Migration planning converts a reactive "discover failures in production" process into a proactive "fix before migration" process. The key tool is `jdeps`, not trial-and-error.

---

### 🧠 Mental Model / Analogy

> Java version migration is like upgrading a city's electrical grid from 110V (Java 8) to 230V (Java 17). The appliances (libraries) that used direct wiring to the internal grid (JDK internals) must be replaced or rewired. The buildings (applications) that used standard sockets (public Java APIs) need only a socket adapter (recompile). The grid standards (JVM spec) changed for good reasons; the appliances that worked around the grid are the problem.

**Element mapping:**

- Electrical grid standard → JVM encapsulation rules
- Appliances using direct wiring → libraries accessing `sun.*` / `com.sun.*`
- Standard socket appliances → libraries using only `java.*` public APIs
- Temporary adapter → `--add-opens` JVM flags
- Rewiring → library upgrade to version using public API

Where this analogy breaks down: unlike electrical appliances, library maintainers can release updated versions compatible with Java 17 - you are not permanently stuck with the non-compliant version.

---

### 📶 Gradual Depth - Four Levels

**Level 1 - What it is (anyone can understand):**
Moving from an old Java version (like Java 8) to a new one (like Java 21) isn't just changing a number. Java tightened its security rules over the years - some tricks that libraries used to do internally no longer work. Upgrading means fixing these library issues and sometimes renaming your imports (from `javax.` to `jakarta.`).

**Level 2 - How to use it (junior developer):**
Migration checklist: (1) Run `jdeps --jdk-internals` to find internal API usage; (2) Upgrade problematic libraries to versions supporting Java 17; (3) If using Spring Boot, upgrade to Spring Boot 3 (requires Java 17 + `jakarta.*` namespace); (4) Run with `--add-opens` as temporary workarounds for slow-to-update libraries; (5) Verify in staging with full test suite; (6) Remove all `--add-opens` once libraries are updated.

**Level 3 - How it works (mid-level engineer):**
Java 9's JPMS introduced modules with `exports` declarations. Packages not exported are inaccessible. JDK internal packages (`jdk.internal.*`, `sun.*`, `com.sun.*`) are never exported. Pre-Java 9, `setAccessible(true)` on any field/method worked regardless of visibility. Java 9-15 allowed `--illegal-access=permit` to restore this. Java 16+ treats all such access as `InaccessibleObjectException` unless `--add-opens MODULE/PACKAGE=TARGET_MODULE` explicitly opens the package. `--add-opens java.base/java.lang=ALL-UNNAMED` opens `java.lang` (from `java.base` module) to the unnamed module (classpath code). Every `--add-opens` is a module system bypass that should be a temporary workaround.

**Level 4 - Why it was designed this way (senior/staff):**
The strong encapsulation decision was controversial because it broke working code. The JDK team's justification: JDK internal APIs have never been supported; they change with every release; any code using them is technically broken already. The staged approach (`--illegal-access=warn` to `deny` over 8 years) was a recognition that the practical reality (libraries widely using internal APIs) required a grace period. The decision to make `--add-opens` a JVM-flag (not a code annotation) was deliberate: it keeps the bypass at the deployment layer, visible to operations teams, not buried in code.

**Expert Thinking Cues:**

- `jdeps` is the canonical tool for migration analysis; always run it before attempting a Java version upgrade
- `--add-opens` vs `--add-exports`: `--add-exports` makes a package accessible for compilation; `--add-opens` makes it accessible for reflection at runtime
- The Module system (JPMS) for application modules is optional; you only need `module-info.java` if you want to publish a named module

---

### ⚙️ How It Works (Mechanism)

```
Java 8 to Java 17 Migration Checklist:

[Step 1: Analysis]
  jdeps --jdk-internals app.jar
  jdeps --jdk-internals lib/*.jar
       |
       ├─ sun.misc.Unsafe → ProjectLombok,
       |                     ByteBuddy, Netty
       ├─ sun.reflect.*  → Hibernate ORM 5
       └─ com.sun.xml.*  → JAXB (removed Java 11)

[Step 2: Library Upgrades]
  Hibernate 5 → 6 (uses public ByteBuddy API)
  JAXB → add dependency (removed from JDK)
  Lombok → 1.18.26+ (Java 17 compatible)

[Step 3: API Removals (Java 11+)]
  RMI activation → add jakarta.activation
  CORBA → remove or use standalone
  Applet API → remove (no replacement)

[Step 4: javax to jakarta (Spring Boot 3)]
  Run OpenRewrite recipe:
  JavaxMigrationToJakarta

[Step 5: Verify with --add-opens]
  Add temporary --add-opens for any
  remaining library violations

[Step 6: Clean up]
  Remove --add-opens as libraries update
```

---

### 🔄 The Complete Picture - End-to-End Flow

**NORMAL FLOW:**

```
[Current: Spring Boot 2.7, Java 11]
     |
     ├─ Step 1: Analysis
     |    jdeps --jdk-internals *.jar
     |    ← YOU ARE HERE
     |
     ├─ Step 2: Library upgrades
     |    Spring Boot 2.7 → 3.x
     |    Hibernate 5 → 6
     |    Jackson 2.13 → 2.15
     |
     ├─ Step 3: javax to jakarta rename
     |    OpenRewrite: JavaxMigration
     |    Spring 5.x → 6.x
     |
     ├─ Step 4: Java 11 → 17 upgrade
     |    Update Docker base image
     |    Update CI JDK
     |    Fix remaining --add-opens
     |
     ├─ Step 5: Test suite validation
     |    Full regression + integration
     |
     └─ Step 6: Java 17 → 21 (optional)
          Virtual threads adoption
          Pattern matching refactoring
```

**FAILURE PATH:**

- Upgrading Spring Boot 3 without Java 17 → Spring Boot 3 requires Java 17 minimum; compile error
- Upgrading Java 17 without library analysis → `InaccessibleObjectException` at runtime (not compile time)
- Skipping `javax` to `jakarta` rename → `ClassNotFoundException: javax.servlet.http.HttpServletRequest`

**WHAT CHANGES AT SCALE:**

A large organisation with 400 services cannot migrate all at once. Strategy: (1) Create a migration playbook with service-specific steps; (2) Migrate pilot services first to discover common issues; (3) Use a shared migration task force to batch-apply OpenRewrite recipes across repositories; (4) Track progress with a Java version dashboard; (5) Set EOL deadline for Java 11 (September 2026) as forcing function.

**CONCURRENCY & DISTRIBUTED IMPLICATIONS:**

Java 21 virtual threads change thread-local variable semantics. Code using `ThreadLocal` for request context (e.g., MDC in logging, request ID propagation) must be audited. Virtual threads can be created by the thousands per second; `ThreadLocal` state is inherited by each virtual thread which can create unexpected state isolation issues. Solution: use `ScopedValue` (Java 21+ incubator) for request-scoped context instead of `ThreadLocal`.

---

### 💻 Code Example

**Step 1: Discovery - find internal API usage:**

```bash
# Scan application and all dependencies
jdeps --jdk-internals \
      --class-path 'lib/*' \
      app.jar

# Expected output:
# app.jar -> JDK removed internal API
# com.example.LegacyEncoder
#   -> sun.misc.BASE64Encoder JDK internal API
#
# Hibernate.jar -> JDK removed internal API
# org.hibernate.internal.util.ReflectHelper
#   -> sun.reflect.ReflectionFactory JDK internal
```

**Step 2: javax to jakarta migration with OpenRewrite:**

```xml
<!-- pom.xml: add OpenRewrite plugin -->
<plugin>
  <groupId>org.openrewrite.maven</groupId>
  <artifactId>rewrite-maven-plugin</artifactId>
  <version>5.35.0</version>
  <configuration>
    <activeRecipes>
      <recipe>
        org.openrewrite.java.migrate.jakarta
        .JavaxMigrationToJakarta
      </recipe>
    </activeRecipes>
  </configuration>
  <dependencies>
    <dependency>
      <groupId>org.openrewrite.recipe</groupId>
      <artifactId>rewrite-migrate-java</artifactId>
      <version>2.19.0</version>
    </dependency>
  </dependencies>
</plugin>
```

```bash
# Run migration (modifies source files)
mvn rewrite:run
# Before (Java EE):
# import javax.servlet.http.HttpServletRequest;
# After (Jakarta EE):
# import jakarta.servlet.http.HttpServletRequest;
```

**Step 3: Temporary --add-opens while libraries update:**

```bash
# BAD: Permanent --add-opens in production
# (technical debt that will never be paid)
java \
  --add-opens java.base/java.lang=ALL-UNNAMED \
  --add-opens java.base/java.util=ALL-UNNAMED \
  -jar app.jar

# GOOD: Tracked --add-opens with ticket ref
# JIRA-1234: Remove after Hibernate 5 -> 6
export JVM_OPTS=\
"--add-opens java.base/java.lang=ALL-UNNAMED"
java $JVM_OPTS -jar app.jar
```

---

### ⚖️ Comparison Table

| Migration Path        | Difficulty | Key Changes                                         | Time Estimate         |
| --------------------- | ---------- | --------------------------------------------------- | --------------------- |
| Java 8 to 11          | Medium     | Remove EE modules; `--illegal-access=warn`          | 1-2 weeks per service |
| Java 11 to 17         | Hard       | `--illegal-access` removed; library upgrades        | 2-4 weeks per service |
| Java 17 to 21         | Easy       | Virtual thread adoption; mostly additive            | 1-3 days per service  |
| Java 8 to 21 (direct) | Very Hard  | All of the above at once; highest risk              | 4-8 weeks per service |
| Spring Boot 2 to 3    | Hard       | Java 17 minimum; javax to jakarta; Hibernate 5 to 6 | 2-4 weeks per service |

---

### ⚠️ Common Misconceptions

| Misconception                                | Reality                                                                                                                                                        |
| -------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| "Adding `--add-opens` fixes the migration"   | `--add-opens` is a temporary workaround. The underlying library must be upgraded to remove internal API usage.                                                 |
| "Java 9 module system must be adopted"       | No. Classpath (unnamed module) continues to work in Java 21 without `module-info.java`. JPMS adoption is optional.                                             |
| "Java 8 code just runs on Java 17 unchanged" | Code using only public Java SE APIs often works. Code using `sun.*`, `com.sun.*`, or removed APIs fails at runtime - not compile time.                         |
| "javax to jakarta is a JVM change"           | It is a Jakarta EE governance change (Oracle retained the `javax` trademark). The JVM is unaffected.                                                           |
| "Virtual threads replace thread pools"       | Virtual threads replace blocking thread pools for I/O. `CompletableFuture`, executors, and reactive patterns remain valid for CPU-bound and non-blocking work. |

---

### 🚨 Failure Modes & Diagnosis

**Mode 1: InaccessibleObjectException during migration**

**Symptom:** After upgrading to Java 17: `java.lang.reflect.InaccessibleObjectException: Unable to make field accessible: module java.base does not open java.io to unnamed module`

**Root Cause:** A library uses reflection to access private JDK fields that are now encapsulated by the module system.

**Diagnostic:**

```bash
# Identify internal API usage before migration
jdeps --jdk-internals app.jar
# Stack trace reveals the library class
# Check if newer version exists without
# internal API usage:
mvn dependency:tree | grep kryo
```

**Fix:** Upgrade the library to a Java 17-compatible version. If unavailable, add `--add-opens` temporarily and track as debt.

**Prevention:** Run `jdeps --jdk-internals` before migration. Map every internal API usage to a library version that removes it. Upgrade libraries before upgrading Java.

---

**Mode 2: ClassNotFoundException on javax.\* after Spring Boot 3**

**Symptom:** After upgrading to Spring Boot 3, startup fails: `java.lang.ClassNotFoundException: javax.servlet.http.HttpServletRequest`

**Root Cause:** Custom code still imports `javax.servlet.*`. Spring Boot 3 requires `jakarta.servlet.*`.

**Diagnostic:**

```bash
# Find all javax.* imports requiring migration
grep -r "import javax\." src/ --include="*.java" \
  | grep -v \
    "javax.crypto\|javax.net\|javax.xml.crypto"
# Note: these Java SE javax.* do NOT need renaming
```

**Fix:** Run OpenRewrite `JavaxMigrationToJakarta` recipe. Keep `javax.crypto`, `javax.net.ssl`, `javax.xml.*` as Java SE (not Jakarta EE) packages.

**Prevention:** Add OpenRewrite check to CI; report any Jakarta EE `javax.` imports in the codebase.

---

**Mode 3: Thread-local state corruption with virtual threads (Security)**

**Symptom:** After enabling virtual threads in Java 21, request-scoped security context leaks between requests under high load.

**Root Cause:** `SecurityContextHolder` uses `ThreadLocal`. Under virtual thread scheduling, unexpected carrier thread sharing may cause context leakage if `ThreadLocal` propagation assumptions break.

**Diagnostic:**

```java
// Check SecurityContextHolder strategy
String strategy =
    SecurityContextHolder
        .getContextHolderStrategy()
        .getClass().getName();
// Test: verify no context sharing under load
// using request ID tracking in logs
```

**Fix:** Use `SecurityContextHolder.MODE_INHERITABLETHREADLOCAL` and test under load. Use Spring Security 6's built-in virtual thread support. Prefer `ScopedValue` for request context.

**Prevention:** Audit all `ThreadLocal` usage before enabling virtual threads. Document each as "VT-safe" or "needs review."

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**

- [[JLG-005 - Java Versioning and LTS Release Strategy]] - which versions exist and their lifecycle
- [[JLG-043 - Java Modularity Strategy (JPMS)]] - the module system driving encapsulation changes

**Builds On This (learn these next):**

- [[JLG-046 - Java Language Specification Deep Dive]] - understanding the JVM spec changes
- [[JLG-044 - Java Performance Profiling at Scale]] - profiling after migration

**Alternatives / Comparisons:**

- GraalVM Native Image migration - avoids JVM cold start but has its own reflection constraints
- Python 2 to 3 migration - comparable ecosystem-wide migration that chose breaking compatibility

---

### 📌 Quick Reference Card

```
+----------------------------------------------------------+
| WHAT IT IS    | Strategy for migrating Java 8 codebases  |
|               | to Java 17 and 21 safely                 |
| PROBLEM       | Strong encapsulation, removed APIs, and  |
|               | javax to jakarta break applications      |
| KEY INSIGHT   | Fix libraries BEFORE upgrading Java;     |
|               | jdeps reveals all internal API usages    |
| USE WHEN      | Upgrading any service from Java 8/11 to  |
|               | Java 17/21; Spring Boot 2 to 3           |
| AVOID WHEN    | N/A - migration is mandatory before Java |
|               | 11 EOL (Sept 2026)                       |
| TRADE-OFF     | Migration effort (weeks) vs staying on   |
|               | EOL runtime with unpatched CVEs          |
| ONE-LINER     | Run jdeps first; upgrade libraries; then |
|               | Java; then javax-to-jakarta; then Java 21|
| NEXT EXPLORE  | JLG-046 (JLS Deep Dive),                 |
|               | JLG-043 (JPMS details)                   |
+----------------------------------------------------------+
```

**If you remember only 3 things:**

1. Run `jdeps --jdk-internals` before every Java version upgrade - it reveals all library internal API usage to fix proactively
2. `--add-opens` is temporary technical debt, not a migration solution; each flag must be tracked and removed when the library is upgraded
3. Spring Boot 3 upgrade and Java 17 upgrade must happen together; the `javax.*` to `jakarta.*` rename is part of that migration

**Interview one-liner:** "The Java 8-to-17 migration requires addressing strong encapsulation (libraries using `sun.*` internal APIs must be upgraded or patched with `--add-opens`), removed APIs (JAXB, CORBA), and for Spring Boot 3 the `javax.*`-to-`jakarta.*` namespace rename; the key tool is `jdeps --jdk-internals` for proactive discovery before runtime failures appear."

---

### 💎 Transferable Wisdom

**Reusable Engineering Principle:** _Discover migration blockers proactively with static analysis before attempting the migration, not reactively from runtime errors._ The `jdeps` tool is the static analysis tool for Java migrations. Equivalent tools exist for every migration: `2to3` for Python, `eslint --fix` for JavaScript upgrades, breaking change scanners for API migrations. The principle: never attempt a major version migration without first running the available static analysis tools.

**Where else this pattern appears:**

- **Database schema migrations** - use `flyway info` to see pending migrations before applying; never run `flyway migrate` blind
- **API gateway upgrades** - use contract testing (Pact) to verify all consumer contracts before upgrading; discover breakage proactively
- **npm major version upgrades** - use `npx npm-check-updates` to audit dependency updates before running `npm install`

---

### 💡 The Surprising Truth

The `javax` to `jakarta` namespace rename - which caused a massive industry-wide migration effort - happened because Oracle retained the trademark to the `javax` namespace when donating Java EE to the Eclipse Foundation. Oracle declined to grant the Eclipse Foundation permission to use the `javax.*` package namespace for new APIs. The Eclipse Foundation had to rename everything to `jakarta.*` starting with Jakarta EE 9. There was no technical motivation - the move was purely a trademark licensing dispute. This means every `javax.servlet.http.HttpServletRequest` to `jakarta.servlet.http.HttpServletRequest` rename in millions of Java files globally, representing hundreds of thousands of person-hours of migration work, was caused by a trademark dispute, not any improvement to the software.

---

### 🧠 Think About This Before We Continue

**Question 1 (A - System Interaction):** A microservice uses Netty 4.1 for HTTP/2 handling. Netty 4.1 uses `sun.nio.ch` and `sun.misc.Unsafe` for direct memory access. Java 17 blocks this access. The Netty 5.0 upgrade has breaking API changes in Netty's own API. Describe the migration path: what are the options for handling the Netty 4 to 5 API change, and how would you test the low-level network behaviour to ensure correctness after the upgrade?

_Hint:_ For Java 17 compatibility with Netty 4.1, `--add-opens java.base/sun.nio.ch=ALL-UNNAMED` is the temporary fix. Consider whether to upgrade Netty 4 to 5 (API changes) or switch to Java's built-in `java.net.http.HttpClient` (no external dependency).

**Question 2 (B - Scale):** A company has 200 Spring Boot 2.7 services on Java 11. Java 11 EOL is September 2026. Spring Boot 2 EOL is November 2024. Each service takes 2 weeks to migrate (Spring Boot 3 + Java 17 + javax-to-jakarta). With 50 engineers spending 50% capacity on migrations, calculate total person-weeks, calendar time, and the optimal migration sequence ordering (which services migrate first, which last).

_Hint:_ 200 services x 2 weeks = 400 person-weeks. 50 engineers x 50% = 25 engineer-weeks/calendar-week. 400/25 = 16 calendar weeks. Simple CRUD services migrate first to build the playbook; services with complex library debt migrate later when the patterns are established.

**Question 3 (D - Root Cause):** After a Java 11-to-17 migration, a service that previously handled 10,000 req/s now handles only 6,000 req/s. GC logs look normal. Profiler shows increased time in `java.lang.reflect.Method.invoke()`. What change between Java 11 and Java 17 could increase reflection overhead by this magnitude, and how would you diagnose and fix it?

_Hint:_ Java 17's strong encapsulation can cause previously-cached reflection paths to become `InaccessibleObjectException` which are caught and retried via slower uncached paths. Frameworks that cached field accessors may fall back to uncached reflection on every call. Check if the framework has a Java 17-optimised version using method handles instead of reflection.
