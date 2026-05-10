---
id: JLG-053
title: Java Modularity Strategy (JPMS)
category: Java Language
tier: tier-3-java
folder: JLG-java-language
difficulty: ★★★
depends_on: JLG-001, JLG-041
used_by: JLG-074
related: JLG-078, JLG-076, JLG-081
tags:
  - java
  - advanced
  - architecture
  - internals
status: complete
version: 3
layout: default
parent: "Java Language"
grand_parent: "Technical Dictionary"
nav_order: 75
permalink: /jlg/java-modularity-strategy-jpms/
---

# JLG-075 - Java Modularity Strategy (JPMS)

⚡ TL;DR - The Java Platform Module System (JPMS) adds compile-time and runtime enforcement of package boundaries via `module-info.java`, replacing the classpath's flat visibility with explicit `requires` and `exports` declarations.

| Field | Value |
|---|---|
| **Depends on** | [[JLG-001 - What Is Java - History and Philosophy]], [[JLG-041 - Java Version Migration Strategy (8 to 17 to 21)]] |
| **Used by** | [[JLG-074 - Java API Design at Scale]] |
| **Related** | [[JLG-078 - Java Language Specification Deep Dive]], [[JLG-076 - Java Performance Profiling at Scale]], [[JLG-081 - Java Language Design History and Rationale]] |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**

In Java 8 and below, all code on the classpath could access all other code on the classpath. A private field in `sun.misc.Unsafe` was accessible via reflection from any library. A class in `com.google.guava.internal` was accessible from application code despite the package name suggesting it was internal. There were no technical boundaries - only naming conventions that could be ignored.

**THE BREAKING POINT:**

The JDK itself could not safely evolve because external code depended on its internal implementation details. `sun.misc.Unsafe` was used by thousands of libraries. If the JDK team changed internal classes, the ecosystem broke. The classpath JAR hell problem was also acute: two libraries each requiring different versions of the same dependency would conflict silently.

**THE INVENTION MOMENT:**

Project Jigsaw (Mark Reinhold, 2008-2017) designed the **Java Platform Module System** as a named module graph with explicit dependency declarations. A module's `module-info.java` declares what it requires, what it exports, and what it opens for reflection. The JVM enforces these at both compile time and runtime. JDK internal packages are no longer exported.

**EVOLUTION:**

- **2008:** Project Jigsaw starts; original goal was modularity for the JDK itself
- **2017:** Java 9 - JPMS ships; JDK itself modularised into 70+ named modules
- **2017:** `--illegal-access=permit` added as migration escape hatch
- **2021:** Java 16 - `--illegal-access=deny` becomes default
- **2021:** Java 17 - `--illegal-access` removed; strong encapsulation final
- **2023:** Java 21 - module system stable; adoption remains optional for application code

---

### 📘 Textbook Definition

The **Java Platform Module System (JPMS)** is a named module graph system introduced in Java 9 (JEP 261) providing:

- **Strong encapsulation:** packages are inaccessible unless explicitly exported
- **Explicit dependencies:** modules declare what they require at compile time
- **Reliable configuration:** the module system validates the dependency graph at startup, failing fast on missing dependencies
- **Scalable platform:** the JDK is divided into named modules enabling small runtime images via `jlink`

A module is defined by a `module-info.java` at the root of the module's source tree. The unnamed module (the classpath) continues to work as before.

---

### ⏱️ Understand It in 30 Seconds

**One line:** JPMS adds a `module-info.java` declaring what your module requires and exports, enforced by the JVM at compile time and runtime.

> JPMS is like adding customs and border control to Java packages. Before JPMS, all packages lived in the same country (classpath) with no borders. JPMS adds passports (`requires`), border control (`exports`), and visa requirements (`opens`). The JDK is now a gated community that only lets approved visitors in.

**One insight:** JPMS adoption is entirely optional for application code. If you never create a `module-info.java`, your code runs in the unnamed module on the classpath - exactly as it did in Java 8. JPMS is not required for Java 17/21 migration.

---

### 🔩 First Principles Explanation

**CORE INVARIANTS:**

1. A named module is defined by `module-info.java`; code without one lives in the unnamed module
2. Exported packages are accessible by other modules; unexported packages are inaccessible even within the same JAR
3. `requires` declarations are checked at compile time and at JVM startup
4. `opens` declarations enable reflective access (required for frameworks using reflection)
5. Split packages (same package in multiple modules) are not permitted in the named module graph

**DERIVED DESIGN:**

From invariant 2 → library authors can have `com.example.api` (exported, public) and `com.example.internal` (unexported, private). Consumers cannot access internal packages.
From invariant 4 → Spring, Hibernate, and Jackson need `opens` declarations because they use reflection to access entity fields.
From invariant 5 → split packages are the most common migration blocker; many legacy codebases have the same package in multiple JARs.

**THE TRADE-OFFS:**

**Gain:** Compile-time enforcement of API surface area; smaller runtime images via `jlink`; earlier detection of missing dependencies (fail at startup, not at runtime).

**Cost:** Migration complexity (split packages, missing `opens`, framework reflection); most frameworks require extensive `opens` declarations; adoption effort for existing codebases rarely justified unless building a platform.

**ESSENTIAL vs ACCIDENTAL COMPLEXITY:**

**Essential:** The JDK modularisation (70+ JDK modules) was essential for JDK maintainability. Without it, the JDK could not evolve its internals.

**Accidental:** Application-level JPMS adoption is mostly accidental complexity for typical enterprise applications. The benefits can be achieved by other means (package naming, code reviews, `revapi`).

---

### 🧪 Thought Experiment

**SETUP:** You are the JDK team in 2010. Hibernate uses `sun.misc.Unsafe` to access entity fields directly. 200,000 projects depend on Hibernate. You need to refactor `sun.misc.Unsafe` to enable a new GC algorithm.

**WHAT HAPPENS WITHOUT JPMS:**

You cannot rename or change `sun.misc.Unsafe` because 200,000 projects will break. The JDK is held hostage by its own internal API. Every potential JVM improvement is blocked by library code that uses internal APIs.

**WHAT HAPPENS WITH JPMS:**

You make `sun.misc.Unsafe` unexported from `java.base`. All modules that need it must explicitly `--add-opens java.base/sun.misc=ALL-UNNAMED`. This appears in JVM startup flags - visible and auditable. You refactor the internals, adding a supported replacement (`java.lang.foreign.MemorySegment`). Libraries migrate. Old `--add-opens` flags are removed as libraries update.

**THE INSIGHT:**

JPMS's primary value was enabling the JDK to evolve. The module system was designed for the JDK first, and for application code second.

---

### 🧠 Mental Model / Analogy

> JPMS is like a university campus access control system. The classpath (pre-JPMS) is an open campus - all buildings accessible to everyone. JPMS adds key card access: each building (module) has a directory of who is allowed in (`exports`), who can use reflection to look inside (`opens`), and which buildings it needs access to (`requires`). The administration building (JDK internals) is restricted to authorised personnel only.

**Element mapping:**
- University campus → JVM classpath
- Building → Java module
- Key card access list → `exports` declarations
- Reflection permission → `opens` declarations
- Building dependency → `requires` declaration
- Restricted administration building → JDK internal packages

Where this analogy breaks down: unlike campus buildings, JPMS modules have transitive dependency chains (`requires transitive`) that automatically grant access through the module graph.

---

### 📶 Gradual Depth - Four Levels

**Level 1 - What it is (anyone can understand):**
Java 9 added a system where you tell Java exactly which parts of your code are accessible to other code, and which libraries your code needs. Before this, everything was visible to everything. Now you can say "only export the public API, keep internals hidden."

**Level 2 - How to use it (junior developer):**
Create `src/main/java/module-info.java`:
```java
module com.example.myapp {
    requires spring.context;
    exports com.example.myapp.api;
    opens com.example.myapp.entity
        to org.hibernate.orm;
}
```
Compile with `javac --module-source-path src`. Run with `java --module-path mods -m com.example.myapp/com.example.Main`.

**Level 3 - How it works (mid-level engineer):**
The module system adds a layer on top of the classloader hierarchy. Named modules are loaded from the module path (`--module-path`). The unnamed module is loaded from the classpath. Named modules cannot read the unnamed module by default. The module graph is validated at JVM startup: all `requires` must be satisfiable; no split packages; no cycles. `exports X to Y` is qualified export - only module Y can access package X. `opens X` allows deep reflection (required for most Java frameworks).

**Level 4 - Why it was designed this way (senior/staff):**
The separation of `exports` (compile-time and runtime read access) from `opens` (reflective access) was deliberate. Frameworks like Spring, Hibernate, and Jackson need to set private fields without requiring those fields to be in the public API. If `exports` implied reflective access, it would force library authors to export internal packages to enable framework reflection. The separate `opens` mechanism allows an internal package to be reflectively accessible without being part of the public API surface.

**Expert Thinking Cues:**
- `jlink` is the primary motivator for JPMS in embedded and native contexts: create a minimal JRE containing only required modules (~20MB vs 200MB full JDK)
- Automatic modules: placing a non-modular JAR on the module path creates an automatic module named after the JAR filename; its entire content is exported and opened
- Named modules cannot read the unnamed module; this is the most common source of confusion in JPMS migration

---

### ⚙️ How It Works (Mechanism)

```
JPMS Module Resolution at JVM Startup:

module-info.java declarations:
  module com.example.app {
    requires com.example.core;
    requires spring.context;
    exports com.example.app.api;
    opens com.example.app.entity
      to org.hibernate.orm;
  }

JVM module graph validation:
  1. Find all named modules on module path
  2. Resolve requires graph recursively
  3. Check no split packages exist
  4. Check no missing requires
  5. Fail fast if validation fails
  6. Start application

Runtime access control:
  - Named module A reads named module B
    only if B exports the accessed package
  - Reflection access needs opens
  - Violation: InaccessibleObjectException
  - Override: --add-opens (JVM flag)
```

---

### 🔄 The Complete Picture - End-to-End Flow

**NORMAL FLOW:**

```
[Developer adds module-info.java]
     |
     ├─ Declare module name
     |    ← YOU ARE HERE
     ├─ Add requires for dependencies
     ├─ Add exports for public API packages
     ├─ Add opens for framework reflection
     |
[Compile with javac --module-path]
     |
     ├─ Compiler validates requires
     ├─ Compiler enforces exports
     |
[JVM startup with --module-path]
     |
     ├─ Module graph resolved
     ├─ Split packages checked
     ├─ Missing modules: fail fast
     |
[Runtime access control enforced]
     └─ InaccessibleObjectException if
          opens declaration missing
```

**FAILURE PATH:**

- Split package across two JARs → `FindException: Two different modules read package X`
- Missing `opens` for framework reflection → `InaccessibleObjectException`
- Missing `requires` → `FindException: module X not found`

**WHAT CHANGES AT SCALE:**

At large scale, JPMS's primary value shifts to `jlink` for minimal runtime images. A Spring Boot application modularised with JPMS and packaged with `jlink` produces a self-contained runtime (application + minimal JRE) of ~50-100MB rather than requiring a full JDK installation.

---

### 💻 Code Example

**module-info.java - complete example:**

```java
// BAD: no module-info.java
// Everything on classpath accessible to
// everything - no enforced API boundaries

// GOOD: module-info.java with clear boundaries
module com.example.payments {
    // External dependencies
    requires java.sql;
    requires com.fasterxml.jackson.databind;

    // Public API - exported to all
    exports com.example.payments.api;
    exports com.example.payments.model;

    // Internal packages - NOT exported:
    // com.example.payments.internal
    // com.example.payments.service

    // Reflection access for Hibernate
    opens com.example.payments.model
        to org.hibernate.orm;

    // Reflection access for Jackson
    opens com.example.payments.api
        to com.fasterxml.jackson.databind;
}
```

**Building a minimal JRE with jlink:**

```bash
# List required modules for your application:
jdeps --module-path mods \
      --print-module-deps target/my-app.jar
# Output: java.base,java.sql,java.logging

# Build minimal JRE (~25MB vs 200MB full JDK):
jlink \
  --module-path $JAVA_HOME/jmods:mods \
  --add-modules com.example.app,java.sql \
  --output custom-runtime

# Run with custom runtime (no JDK required):
./custom-runtime/bin/java \
  -m com.example.app/com.example.app.Main
```

**How to test / verify module structure:**

```bash
# Verify module structure of a JAR:
java --describe-module java.base
# Lists all exported and opened packages

# Check for split packages before migration:
jdeps --class-path 'lib/*' \
      --check com.example.mymodule
```

---

### ⚖️ Comparison Table

| Feature | Classpath (pre-Java 9) | JPMS Named Module | OSGi |
|---|---|---|---|
| Package visibility | All public classes accessible | Only exported packages | Bundle-level control |
| Dependency declaration | None (implicit) | `requires` (explicit) | `Import-Package` |
| Reflection access | All via setAccessible | Only `opens` packages | Bundle-level |
| Version conflict detection | Silent (last-one-wins) | Fail-fast at startup | Full version resolution |
| Adoption complexity | Zero | High | Very high |
| JRE minimisation | No | Yes (jlink) | No |

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| "JPMS is required for Java 17/21" | No. JPMS is optional. Classpath-based code works unchanged on Java 21. The unnamed module is fully supported. |
| "JPMS solves JAR version conflicts" | JPMS detects split packages but does NOT resolve version conflicts between different versions of the same library. |
| "Spring Boot apps must be modularised" | Spring Boot works perfectly without `module-info.java`. Spring Boot 3 runs on Java 21 classpath. |
| "JPMS replaces OSGi" | JPMS provides static module graph resolution. OSGi provides dynamic module loading and service registry. For dynamic plugins, OSGi is still needed. |
| "Unnamed module and named modules freely interact" | Named modules cannot read the unnamed module by default. The unnamed module CAN access exported packages of named modules. |

---

### 🚨 Failure Modes & Diagnosis

**Mode 1: Split package error blocks modularisation**

**Symptom:** `java.lang.module.FindException: Module X contains package com.example.util, module Y also contains package com.example.util`

**Root Cause:** Two JARs share the same Java package. JPMS forbids split packages in the named module graph.

**Diagnostic:**
```bash
# Find split packages across JARs:
jdeps --class-path 'lib/*' \
      --multi-release 21 \
      --check com.example.mymodule
# Lists all package splits detected
```

**Fix:** Refactor packages to eliminate splits. If third-party libraries cause the split, keep those JARs on classpath (not module path) until the libraries are fixed.

**Prevention:** Check for split packages before migrating to JPMS. Run `jdeps --check` in CI when modularising.

---

**Mode 2: Missing `opens` causes framework reflection failure**

**Symptom:** Hibernate fails with `InaccessibleObjectException: module com.example.app does not open com.example.app.entity to org.hibernate.orm`

**Root Cause:** `module-info.java` does not have `opens com.example.app.entity to org.hibernate.orm`. Hibernate needs reflective access to set entity fields.

**Diagnostic:**
```bash
# Temporarily add --add-opens to identify all
# missing opens declarations:
java \
  --add-opens com.example.app/com.example.entity\
=org.hibernate.orm \
  -m com.example.app/com.example.Main
# If startup succeeds, add to module-info.java
```

**Fix:** Add `opens com.example.app.entity to org.hibernate.orm;` to `module-info.java`.

**Prevention:** When first creating `module-info.java`, run full test suite to discover all missing `opens` before deploying.

---

**Mode 3: Automatic module naming collision (Security/Stability)**

**Symptom:** Two JARs on the module path derive to the same module name. JVM startup fails with ambiguous module name.

**Root Cause:** Automatic module name is derived from JAR filename. Different versions of the same library on the module path create a name collision.

**Diagnostic:**
```bash
# Check automatic module names:
jar --describe-module --file=guava-31.0.1.jar
# No module descriptor found; uses jar name

# Trace module resolution:
java --show-module-resolution \
     --module-path mods -m myapp
```

**Fix:** Use only one version of each dependency. Prefer libraries that ship with `module-info.java` over automatic modules.

**Prevention:** Library authors: include `Automatic-Module-Name` in `MANIFEST.MF` for stable module naming independent of JAR filename.

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**
- [[JLG-001 - What Is Java - History and Philosophy]] - the classpath model this replaces
- [[JLG-041 - Java Version Migration Strategy (8 to 17 to 21)]] - strong encapsulation migration context

**Builds On This (learn these next):**
- [[JLG-074 - Java API Design at Scale]] - using JPMS to enforce API boundaries
- [[JLG-078 - Java Language Specification Deep Dive]] - the JVM spec defining module behaviour

**Alternatives / Comparisons:**
- OSGi - mature dynamic module system; supports version resolution and runtime loading
- Maven/Gradle multi-module - build-time separation without runtime enforcement

---

### 📌 Quick Reference Card

```
+----------------------------------------------------------+
| WHAT IT IS    | Java 9+ named module system with         |
|               | requires, exports, opens declarations    |
| PROBLEM       | Classpath gives no API boundary control; |
|               | JDK internals exposed to all libraries  |
| KEY INSIGHT   | JPMS is optional for app code; required  |
|               | for jlink minimal JRE creation           |
| USE WHEN      | Building libraries/platforms; creating   |
|               | minimal JRE with jlink; enforcing API   |
| AVOID WHEN    | Standard Spring Boot apps where classpath|
|               | works fine with no migration effort     |
| TRADE-OFF     | Strong API boundaries + jlink vs high    |
|               | migration complexity + framework opens  |
| ONE-LINER     | module-info.java declares requires and   |
|               | exports; JVM enforces at startup         |
| NEXT EXPLORE  | JLG-074 (API Design),                   |
|               | JLG-078 (JLS Deep Dive)                 |
+----------------------------------------------------------+
```

**If you remember only 3 things:**
1. JPMS is optional for application code - the unnamed module (classpath) still works on Java 21
2. `exports` controls compile/read access; `opens` is needed separately for reflective access by Spring/Hibernate/Jackson
3. `jlink` is JPMS's biggest practical payoff - creates a minimal custom JRE containing only your application's required modules

**Interview one-liner:** "JPMS (Java Platform Module System, Java 9+) adds a `module-info.java` descriptor declaring `requires` (dependencies), `exports` (public API packages), and `opens` (reflective access); it enforces strong encapsulation at compile time and runtime, enables `jlink` minimal JRE creation, and is optional for application code - the unnamed module continues to work on the classpath."

---

### 💎 Transferable Wisdom

**Reusable Engineering Principle:** *Explicit declarations of dependencies and visibility, enforced at system startup, catch configuration errors early rather than late.* JPMS validates the entire module graph at JVM startup - a missing dependency fails immediately, not when the first request tries to use it. This fail-fast principle is more reliable than classpath's implicit resolution.

**Where else this pattern appears:**
- **Docker multi-stage builds** - explicitly list only the components needed in the final image; reduced attack surface and size; same principle as `jlink`
- **TypeScript `export` declarations** - explicit exports from modules; non-exported types are inaccessible; same API boundary principle as JPMS `exports`
- **Kubernetes RBAC** - explicit `ClusterRole` declarations list exactly which API groups and verbs are permitted; deny-by-default same as JPMS unexported packages

---

### 💡 The Surprising Truth

Project Jigsaw (which became JPMS) was started in 2008 but only shipped in Java 9 in 2017 - a 9-year development cycle for a single feature. The feature was so controversial that it delayed the entire Java 9 release by 18 months. The core controversy: OSGi, already used by Eclipse IDE and many enterprise applications, provided dynamic modular Java. IBM (a Java Steering Committee member and major OSGi user) argued that JPMS should be OSGi-compatible. JetBrains argued for rejecting JPMS in favour of evolving OSGi. The final JPMS design was a compromise that satisfied neither camp: it provides static module graph resolution (unlike OSGi's dynamic loading) and is incompatible with OSGi's versioning model. The 9-year delay was not technical - it was a governance and ecosystem politics problem, demonstrating that standardisation in large ecosystems is more political than technical.

---

### 🧠 Think About This Before We Continue

**Question 1 (C - Design Trade-off):** JPMS's `opens` mechanism requires a module to explicitly grant reflective access to specific other modules. A Spring Boot application using JPMS must grant Hibernate access to entity packages, Spring access to configuration packages, Jackson access to DTO packages. As framework dependencies grow, the `opens` list grows. Describe the fundamental tension between strong encapsulation (JPMS's goal) and the reflection-heavy framework ecosystem, and whether this tension can be resolved.

*Hint:* Java 9's `opens ... to ALL-UNNAMED` is the escape hatch that bypasses the tension by granting reflective access to all unnamed module code. Research whether Spring Boot's JPMS support guide recommends this approach or specific per-framework `opens` declarations.

**Question 2 (B - Scale):** A company builds a Java library used by 300 external customers. The library is a single JAR with 50 packages: 10 are public API, 40 are internal implementation. Without JPMS, customers access internal packages via reflection, creating support nightmares when internals change. Design the JPMS migration strategy: module name, exports, opens, and backwards compatibility for customers currently depending on internal packages.

*Hint:* Customers using the public API will not break. Customers using internal packages will break - JPMS is the mechanism to force them to stop. Consider what `--add-opens` flags customers can use as a temporary workaround while migrating their code.

**Question 3 (D - Root Cause):** After adding `module-info.java` to a Spring Boot application and running tests, the test suite fails with `InaccessibleObjectException` in 80 places. The application itself starts fine. Root cause analysis: why do tests specifically fail while the application works, and what difference between test execution and application execution in the module system context causes this?

*Hint:* Maven Surefire and Gradle Test tasks run tests in a different classloader context. Test frameworks (JUnit 5, Mockito) use reflection extensively. The `opens` in `module-info.java` may not grant access to the test module (which has no `module-info`). Research `--add-opens` in Maven Surefire `argLine` and why test frameworks need special JPMS handling.
