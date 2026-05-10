---
id: JLG-039
title: Java Module System (JPMS, Java 9+)
category: Java Language
tier: tier-3-java
folder: JLG-java-language
difficulty: ★★☆
depends_on: JLG-075, JLG-021, JLG-001
used_by: JLG-012, JLG-014
related: JLG-031, JLG-065, JLG-042
tags:
  - java
  - internals
  - advanced
  - intermediate
  - build
status: complete
version: 3
layout: default
parent: "Java Language"
grand_parent: "Technical Dictionary"
nav_order: 40
permalink: /java-language/java-module-system-jpms/
---

# JLG-040 - JAVA MODULE SYSTEM (JPMS, JAVA 9+)

⚡ **TL;DR** - JPMS (Project Jigsaw) divides Java code into named
modules with explicit `requires` and `exports` declarations,
enforcing encapsulation at the package level at compile time and
runtime.

---

| Field      | Value                                              |
|------------|----------------------------------------------------|
| Depends on | JLG-075 Java Modularity Strategy, JLG-021 Java Access Modifiers, JLG-001 Java EE Overview |
| Used by    | JLG-012 Class File Format, JLG-014 Hidden Classes |
| Related    | JLG-031 Reflection, JLG-065 Annotation Processing, JLG-042 JLS |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
Java's classpath model has no encapsulation beyond what `public`,
`protected`, `package-private` provides at the class level.
Any code on the classpath can access any public API of any library -
even APIs explicitly marked as internal. JDK internal APIs like
`sun.misc.Unsafe` are used widely by third-party libraries despite
Oracle repeatedly warning they are implementation details.

**THE BREAKING POINT:**
Oracle needs to restructure the JDK internals for long-term
maintainability but cannot because millions of production classpaths
depend on internal JDK packages. Every JDK refactoring breaks
library compatibility. The ecosystem is frozen by accidental
coupling to implementation details.

**THE INVENTION MOMENT:**
Project Jigsaw (Mark Reinhold) modularised the JDK itself in Java 9
(JEP 261). `module-info.java` files declare what a module exports
and what it requires. The JVM enforces these boundaries at class
loading time - packages not exported are inaccessible even via
reflection (unless opened with `--add-opens`).

**EVOLUTION:**
- **Java 9:** JPMS GA (JEP 261). JDK itself split into ~100 modules
- **Java 16:** `--illegal-access=deny` default (blocks `--add-opens`
  bypasses); most reflective access now requires explicit opens
- **Java 17+:** Strong encapsulation enforced; many legacy `--add-opens`
  workarounds stopped working without explicit module flags

---

### 📘 Textbook Definition

**Java Platform Module System (JPMS)** is a module system
introduced in Java 9 (JEP 261). A *module* is a named, self-
describing collection of packages. Each module has a
`module-info.java` descriptor at its root:

```java
module com.example.app {
    requires java.sql;            // depends on java.sql module
    requires transitive java.logging; // transitive: re-exports to dependents
    exports com.example.api;      // public API: accessible to all
    exports com.example.internal to com.example.tests; // qualified: test only
    opens com.example.model;      // allows deep reflection
    uses com.example.api.Service; // SPI consumer
    provides com.example.api.Service with com.example.impl.ServiceImpl; // SPI
}
```

**Accessibility levels (Java 9+):**
1. `public` to `exports` = accessible by dependent modules
2. `public` in non-exported package = module-private (inaccessible)
3. `opens` = accessible via reflection even if not exported

---

### ⏱️ Understand It in 30 Seconds

**One line:** `module-info.java` declares what your code needs
(`requires`) and what it exposes (`exports`) - the JVM enforces
this contract.

**One analogy:**
> Before modules: a city with no trespassing laws - anyone can walk
> into any building. JPMS: each building (module) has a locked
> entrance. Only registered guests (`requires`) gain entry, and only
> through the designated lobby (`exports`). Staff areas (non-exported
> packages) remain inaccessible even to registered guests.

**One insight:** `public` is no longer the maximum access level.
A class can be `public` but in a non-exported package - making it
accessible within the module but inaccessible to all others.

---

### 🔩 First Principles Explanation

**CORE INVARIANTS:**

1. Every module has a unique name (e.g., `java.base`, `com.example.app`).
2. `requires X` creates a compile-time and runtime dependency on module X.
3. `exports P` makes package `P` accessible to all dependent modules.
4. `exports P to M` makes package `P` accessible only to module `M`.
5. Classes in non-exported packages: inaccessible from outside the
   module regardless of their access modifier.
6. `opens P` allows reflective access to package `P` (for frameworks
   like Spring, Hibernate that use reflection).
7. All code on the classpath (unnamed module) can read all exported
   packages of all modules.

**DERIVED DESIGN:**
The module layer sits between the classpath resolver and the class
loader. At startup, the JVM builds a *module graph* from all
`module-info.class` files, resolves `requires` edges, and installs
access checks enforced at class loading.

**THE TRADE-OFFS:**

**Gain:** Strong encapsulation; reliable component boundaries; JDK
modularity (smaller runtime images via `jlink`); improved security.

**Cost:** Migration complexity for existing classpaths; framework
reflection (Spring, Hibernate) requires `opens`; `--add-opens` is
a temporary escape hatch, not a solution.

**ESSENTIAL vs ACCIDENTAL COMPLEXITY:**

**Essential:** Enforcing encapsulation at the module level is
fundamentally different from class-level access control. Some
complexity is inherent.

**Accidental:** The migration from classpath to module path is
painful for existing codebases. The unnamed module concept exists
to ease migration but adds conceptual overhead.

---

### 🧪 Thought Experiment

**SETUP:** Two libraries `lib-api` and `lib-impl` where `lib-impl`
contains implementation classes that should never be used directly.

**WITHOUT JPMS:**
```
lib-api.jar: com.example.api.Service (public)
lib-impl.jar: com.example.impl.FastService (public, internal)

User code: new com.example.impl.FastService() // works! Unintended coupling
```

**WITH JPMS:**
```
module lib-api {
    exports com.example.api; // ONLY the API package
}
module lib-impl {
    requires lib-api;
    exports com.example.impl to lib-api; // ONLY to lib-api internally
    provides com.example.api.Service with com.example.impl.FastService;
}
// User code: new com.example.impl.FastService()
// -> InaccessibleObjectException at compile time AND runtime
```

**THE INSIGHT:** JPMS makes "internal" actually mean internal,
without relying on convention or code review.

---

### 🧠 Mental Model / Analogy

> A module is a sealed shipping container. Its manifest (`module-info`)
> lists what can be loaded/unloaded (`exports`), what it needs from
> other containers (`requires`), and what customs can inspect
> (`opens`). The port authority (JVM) enforces the manifest. No
> unauthorised cargo leaves or enters.

**Element mapping:**
- Container = module
- Container manifest = `module-info.java`
- Loading dock (public entry) = `exports`
- Required supplies = `requires`
- Customs inspection allowed = `opens`
- Port authority = JVM module system (readability + accessibility checks)

Where this analogy breaks down: modules can form a graph, not just
a ship manifest. Module graph resolution is more complex than one
container's rules.

---

### 📶 Gradual Depth - Four Levels

**Level 1 - What it is (anyone can understand):**
A way to say "my code needs X and exposes Y" - so the JVM prevents
anyone from using parts of your code you didn't intend to share.

**Level 2 - How to use it (junior developer):**
```java
// module-info.java at src/main root
module com.example.myapp {
    requires java.net.http;    // use Java HTTP client
    requires com.example.lib;  // use a library module
    exports com.example.api;   // my public API
    // com.example.internal: NOT exported = module-private
}
```

**Level 3 - How it works (mid-level engineer):**
The JVM reads all `module-info.class` files at startup to build a
module graph. For each `requires` edge, it verifies the named module
exists on the module path. Readability is transitive via `requires transitive`.
Accessibility check: `class.forName("X")` throws `InaccessibleObjectException`
if X is in a non-exported, non-opened package.

**Level 4 - Why it was designed this way (senior/staff):**
Mark Reinhold's original motivation: modularise the JDK to enable
custom runtime images (`jlink`) that include only the JDK modules
a specific application needs - reducing JRE size from ~200MB to
<50MB for many applications. The Jigsaw design chose a readability
graph (not just accessibility) to enable lazy link-time graph
analysis, supporting `jlink`'s trimming.

**Expert Thinking Cues:**
- `module-path` vs `classpath`: module path requires `module-info`.
  Classpath is the "unnamed module" - reads all other modules' exports.
- `--add-modules`, `--add-opens`, `--add-exports`: escape hatches
  for migration; should not be in final builds.
- `jlink`: creates minimal runtime images. `jdeps` analyses classpath
  jars for JPMS compatibility.
- `ServiceLoader`: JPMS's module-aware SPI mechanism (uses `provides`/`uses`).

---

### ⚙️ How It Works (Mechanism)

**Module resolution at JVM startup:**
```
java --module-path mods -m com.example.app/com.example.Main

1. Read module-info.class from mods/com.example.app
2. Build initial module graph: {com.example.app}
3. For each requires X: add X to graph, transitively resolve
4. Verify no missing modules (all requires satisfied)
5. Verify no split packages (same package in two modules - illegal)
6. Install readability: A reads B means A can see B's exports
7. Accessibility: enforced at Class.forName / field access time
```

**Split package detection:**
```
ERROR: two modules both contain com.example.shared
com.module.a       com.module.b
-> JVM refuses to start: split package not allowed
```

---

### 🔄 The Complete Picture - End-to-End Flow

**NORMAL FLOW:**
```
Compile: javac --module-path libs -d out src/module-info.java src/**/*.java
       |
  Compiler reads requires -> resolves module graph
  Compiler enforces exports (compile-time access check)
       |
Runtime: java --module-path libs:out -m myapp/com.example.Main
       |    <- YOU ARE HERE
  JVM resolves module graph
  Installs readability + accessibility checks
  Main class loaded -> application starts
```

**FAILURE PATH:**
```
java.lang.module.FindException: Module X not found
-> X is on classpath (jar) not module path (missing module-info)
-> Fix: move X to module path or use --add-modules X
```

**WHAT CHANGES AT SCALE:**
- Large codebases: mapping existing packages to modules requires
  dependency analysis (jdeps). Split packages must be resolved.
- Frameworks: Spring 6 is JPMS-aware. Earlier Spring requires
  `--add-opens` for reflection to work.

---

### 💻 Code Example

**BAD - ClassPath project using JDK internal API:**
```java
// BAD: sun.misc.Unsafe is a JDK internal -> breaks in Java 17+
import sun.misc.Unsafe;
// InaccessibleObjectException in Java 17 without --add-opens
```

**GOOD - module-info.java for a library:**
```java
// good: module-info.java
module com.example.lib {
    requires java.base;         // implicitly required; explicit is fine
    requires java.logging;

    exports com.example.lib.api;           // public API
    // com.example.lib.internal: not exported = private to module

    opens com.example.lib.model;           // allow Jackson/Hibernate reflection
}
```

**GOOD - SPI with modules:**
```java
// In API module: service interface declaration
module com.payment.api {
    exports com.payment.api;
    uses com.payment.api.PaymentProcessor; // declare SPI consumer
}

// In implementation module:
module com.payment.stripe {
    requires com.payment.api;
    provides com.payment.api.PaymentProcessor
        with com.payment.stripe.StripeProcessor;
}

// At runtime:
ServiceLoader<PaymentProcessor> loader =
    ServiceLoader.load(PaymentProcessor.class);
loader.findFirst().ifPresent(p -> p.process(order));
```

**How to verify:**
```bash
# Resolve modules and check for missing/split packages
jdeps --module-path libs --check com.example.app

# Build module-aware image (only modules needed):
jlink --module-path mods:$JAVA_HOME/jmods \
      --add-modules com.example.app \
      --output custom-runtime

# Test: custom-runtime is self-contained
custom-runtime/bin/java -m com.example.app/com.example.Main
```

---

### ⚖️ Comparison Table

| Feature | Classpath | JPMS (module path) | OSGi |
|---------|-----------|-------------------|------|
| Encapsulation | Class-level only | Package-level, module-enforced | Bundle-level, enforced |
| Circular dependencies | Allowed | Not allowed | Allowed |
| Split packages | Allowed | Forbidden | Allowed |
| Runtime images | Full JRE required | `jlink` custom images | Not applicable |
| Reflection | Always allowed | Requires `opens` | Bundle-controlled |
| Migration effort | None | Medium-High | Very High |
| Framework support | Universal | Java 11+ | Specialised |

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| "JPMS replaces OSGi" | JPMS is a platform-level module system; OSGi is a runtime component system with dynamic loading/unloading. They serve different needs and can coexist. |
| "All jars on the module path become modules" | Only jars with `module-info.class` are named modules. Jars without it are automatic modules (named by jar file name) or go on the classpath (unnamed module). |
| "`public` access works the same in modules as before" | NO. `public` in a non-exported package is module-private. External code cannot access it even via reflection without `opens`. |
| "I have to modularise my code to use Java 9+" | You can stay on the classpath forever. JPMS is opt-in for application code. Only the JDK is fully modularised. |
| "`--add-opens` can be permanent in production" | It's a workaround for migration. As of Java 17, many `--add-opens` for JDK internals generate warnings or are restricted. |

---

### 🚨 Failure Modes & Diagnosis

**Failure Mode 1: InaccessibleObjectException from Spring/Hibernate reflection**

**Symptom:** `java.lang.reflect.InaccessibleObjectException: Unable to make
field private final...` at application startup.

**Root Cause:** Framework uses reflection to access non-exported,
non-opened JDK internal packages.

**Diagnostic:**
```bash
java --list-modules 2>&1 | grep java
# Find which module owns the inaccessible package
```

**Fix:**
```bash
# Temporary migration fix:
java --add-opens java.base/java.lang=ALL-UNNAMED \
     --add-opens java.base/java.util=ALL-UNNAMED \
     -jar app.jar
# Permanent fix: upgrade to Spring 6 / Hibernate 6 (JPMS-aware)
```

---

**Failure Mode 2: Split package error at startup**

**Symptom:** `java.lang.module.FindException: Two of the modules
... contain package ...`

**Root Cause:** Two jars on the module path both contain the same
Java package. JPMS forbids this.

**Fix:** Move one of the jars to the classpath (unnamed module does
not enforce split package rules) or resolve the duplication.

---

**Failure Mode 3: ServiceLoader finds no implementations**

**Symptom:** `ServiceLoader.load(Service.class)` returns empty.

**Root Cause:** Implementation module missing `provides` declaration
in `module-info`.

**Fix:**
```java
// Add to implementation module's module-info.java:
provides com.example.api.Service with com.example.impl.ServiceImpl;
```

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**
- [[JLG-021 - Java Access Modifiers]] - the access model JPMS extends
- [[JLG-075 - Java Modularity Strategy]] - high-level strategy context

**Builds On This (learn these next):**
- [[JLG-012 - Class File Format (javap)]] - module-info.class format
- [[JLG-014 - Hidden Classes (Java 15+)]] - JVM internal class
  isolation that builds on module concepts

**Alternatives / Comparisons:**
- OSGi bundles - dynamic loading, more powerful but heavier
- Classpath with package conventions - no enforcement

---

### 📌 Quick Reference Card

```
+--------------------------------------------------+
| WHAT IT IS   | Named module system enforcing pkg  |
|              | encapsulation at JVM level         |
+--------------+------------------------------------+
| PROBLEM      | Public APIs accessible to anyone;  |
|              | JDK internals used by 3rd parties  |
+--------------+------------------------------------+
| KEY INSIGHT  | public in non-exported pkg =       |
|              | module-private despite being public|
+--------------+------------------------------------+
| USE WHEN     | Library development, JDK migration,|
|              | custom runtime images (jlink)      |
+--------------+------------------------------------+
| AVOID WHEN   | Small apps, prototype code;        |
|              | migration cost outweighs benefit   |
+--------------+------------------------------------+
| TRADE-OFF    | Strong encapsulation / migration   |
|              | pain; framework reflection needs   |
|              | explicit opens                    |
+--------------+------------------------------------+
| ONE-LINER    | module X { requires Y; exports P; }|
|              | in module-info.java at src root    |
+--------------+------------------------------------+
| NEXT EXPLORE | JLG-012 Class File Format,         |
|              | jlink custom runtime images        |
+--------------------------------------------------+
```

**If you remember only 3 things:**
1. `public` inside a non-exported package = module-private. Exported
   packages only are accessible outside the module.
2. `opens P` allows reflection on package P - required for
   Spring/Hibernate to function on Java 9+ without `--add-opens`.
3. `jlink` creates minimal custom JRE images using modules - reduces
   Docker image size dramatically.

**Interview one-liner:** "JPMS (Java 9) adds module-level
encapsulation: `module-info.java` declares `requires` dependencies
and `exports` the packages that are publicly accessible; the JVM
enforces this, making `public` inside a non-exported package
effectively module-private."

---

### 💎 Transferable Wisdom

**Reusable Engineering Principle:** Encapsulation enforced by tooling
is more reliable than encapsulation enforced by convention. Internal
APIs cannot remain truly internal if the platform allows unrestricted
access and teams are under time pressure.

**Where else this pattern appears:**
- **npm `exports` field:** Node.js `package.json` `exports` field
  restricts which sub-paths of a package are importable - the same
  "explicitly declare public surface" principle.
- **Rust visibility (`pub(crate)`, `pub(super)`):** Rust's module
  system uses explicit visibility modifiers that enforce encapsulation
  at the language level, similar to JPMS.
- **Go package visibility (unexported identifiers):** Go enforces
  that identifiers starting with lowercase are package-private.
  Simple but the same concept - explicit public surface declaration.

---

### 💡 The Surprising Truth

Java 9's module system introduced the concept of the "unnamed module"
to maintain backward compatibility with the classpath. All code on
the classpath is treated as one big unnamed module that can read
all named modules' exported packages. This means that most existing
Java applications in production today are running in the unnamed
module - they use Java 9+ JVMs but gain zero JPMS encapsulation
benefits. The module system is opt-in and most production codebases
chose not to opt in, making JPMS's strongest guarantee invisible
to the majority of Java developers despite being available for
over 8 years since Java 9.

---

### 🧠 Think About This Before We Continue

**Question 1 (System Interaction):** A Spring Boot 3 application
uses JPMS with a fully modularised `module-info.java`. Spring uses
reflection to inject dependencies into `private` fields. What
specific JPMS declaration does Spring 6 require in the application's
`module-info`, and what would happen if it was omitted?

*Hint:* Study `opens com.example.domain to spring.core` and how
Spring 6 uses `MethodHandles.privateLookupIn()` with module opens
to avoid the deprecated `--add-opens` workaround.

---

**Question 2 (Design Trade-off):** Your team creates a library
that is used both by modular (Java 9+) and non-modular (classpath)
consumers. Your library has internal implementation classes you
want to hide in the modular case. Design the `module-info.java` and
multi-release jar strategy that enforces encapsulation for modular
consumers while remaining fully accessible for classpath consumers.

*Hint:* Research Multi-Release JARs (`META-INF/versions/9/`) and
how the module-info.class at `META-INF/versions/9/module-info.class`
applies only when the jar is loaded as a named module.

---

**Question 3 (Root Cause):** After upgrading from Java 11 to Java 21,
a production service fails to start with `InaccessibleObjectException`
in 5 different frameworks simultaneously. The service worked on
Java 11: `--add-opens java.base/java.lang=ALL-UNNAMED` was in the
startup script. What changed between Java 11 and 21 regarding
`--add-opens` semantics, and why did the same flag stop working?

*Hint:* Investigate Java 17's strong encapsulation enforcement that
made several previously open internal packages strongly encapsulated.
The `--add-opens` flag still works for SOME packages but specific
JDK-internal packages became permanently closed in Java 17+.

