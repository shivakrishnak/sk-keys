---
id: CSF-052
title: Modules and Packages
category: CS Fundamentals - Paradigms
tier: tier-1-foundations
folder: CSF-cs-fundamentals
difficulty: ★★☆
depends_on: CSF-013, CSF-015
used_by: JLG-005, MVN-001, NPM-001
related: CSF-013, JLG-005, MVN-001
tags: [modules, packages, namespaces, encapsulation, jpms]
status: complete
version: 4
layout: default
parent: "CS Fundamentals - Paradigms"
grand_parent: "Technical Mastery"
nav_order: 52
permalink: /technical-mastery/csf/modules-and-packages/
---

⚡ TL;DR - A package groups related classes under a namespace
(prevents name collisions). A module groups packages with
an explicit dependency graph and access control (Java 9+
JPMS). Packages = compile-time namespace. Modules = runtime
boundary with declared exports and requires.

| #052 | Category: CS Fundamentals - Paradigms | Difficulty: ★★☆ |
|:---|:---|:---|
| **Depends on:** | CSF-013 (OOP), CSF-015 (Encapsulation) | |
| **Used by:** | JLG-005 (Java Package System), MVN-001 (Build Modules), NPM-001 (Node Packages) | |
| **Related:** | CSF-013 (OOP), JLG-005 (Java Packages), MVN-001 (Maven) | |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**

A Java project with 500 classes all in one flat namespace.
Two developers independently create a `Utils` class. Both
compile fine. At runtime, the JVM loads one and ignores
the other - which one is non-deterministic (depends on
classpath ordering). Any class can access any other class's
internal state (all classes see each other). A bug in
`InternalParserHelper` is directly accessed from production
code in a completely unrelated module, creating an invisible
coupling. When `InternalParserHelper` is refactored (its
intended purpose: an implementation detail), all the code
that depended on it directly breaks. The "internal" is
just a naming convention - nothing enforces it.

**THE BREAKING POINT:**

As codebases grow to tens of thousands of classes (Spring
Framework: ~20,000 classes), flat namespaces cause:
(1) Name collision: commons-collections and another library
    both define `AbstractMap` - classloader picks one.
(2) Unintended coupling: internal classes accessed from
    external code, making refactoring impossible.
(3) No encapsulation at the library level: `public` means
    accessible to the ENTIRE JVM, including code the library
    author never intended to support.
Java 9's JPMS (Java Platform Module System) added module-level
encapsulation to address this.

**THE INVENTION MOMENT:**

Packages (Java 1.0) solved naming: `com.example.utils.StringUtils`
vs `org.apache.commons.utils.StringUtils` are different despite
same simple name. The namespace prevents collision.
JPMS (Java 9, Project Jigsaw) added module-level visibility:
a module declares which packages it EXPORTS (visible outside)
and which it REQUIRES (dependencies). Internal packages
(not exported) are inaccessible even if the classes are `public`.
`public` within a module is no longer global - it's module-internal.
This is the missing encapsulation layer between "class-level
private" (too narrow) and "JAR-level public" (too broad).

---

### 📘 Textbook Definition

**Package:** A named grouping of related classes and interfaces
in a hierarchical namespace. In Java: declared with `package
com.example.service;` at the top of each source file.
Provides namespace isolation (same simple class name in
different packages = different classes). Controls access:
package-private (no modifier) = visible only within the package.

**Module (JPMS, Java 9+):** A named group of related packages
with a `module-info.java` file declaring:
- `requires ModuleName;` - runtime dependency on another module
- `exports com.example.api;` - makes this package accessible to other modules
- `opens com.example.model;` - allows deep reflection (for frameworks)

**Module System Goals:**
1. Strong encapsulation: un-exported packages are inaccessible
   even via reflection (by default)
2. Reliable configuration: dependency graph is known at startup
3. Scalable Java platform: JDK itself was modularized (20+ modules)

---

### ⏱️ Understand It in 30 Seconds

**One line:**
Package = namespace (groups classes, prevents name collision).
Module = deployment unit with declared exports and dependencies
(enforces what's public at the library level).

**One analogy:**

> Package: rooms in an apartment building. Each room (package)
> has a number (name). "Kitchen" on floor 2 and "kitchen"
> on floor 5 are different rooms (different packages despite
> same local name). You can walk between rooms if the doors
> are unlocked (package-private = room-private; public = unlocked).

> Module: the apartment BUILDING itself. The building controls
> which doors are even accessible to the public. Internal
> service corridors (un-exported packages) are inaccessible
> from outside the building regardless of whether individual
> doors are unlocked (public) within the corridor.

**One insight:**

Before JPMS: a library can have a class marked `public`
in an "internal" package (`sun.misc.Unsafe`, `com.sun.net.httpserver.*`).
Any other code can use it. Library authors cannot prevent it.
JDK authors cannot remove `sun.misc.Unsafe` because too many
applications depend on it. JPMS: the `java.base` module
does not export `sun.misc`. External code cannot access it
even though the class is technically `public`. The module
system enforces the "this is internal" contract that was
previously just a naming convention.

---

### 🔩 First Principles Explanation

**PACKAGE STRUCTURE AND NAMING:**

```
┌──────────────────────────────────────────────────────┐
│ Package naming convention: reverse domain name       │
│   com.example.service          -> service layer      │
│   com.example.service.impl     -> implementations    │
│   com.example.repository       -> data access        │
│   com.example.model            -> domain objects     │
│   com.example.api              -> public API         │
│   com.example.internal         -> internal (by convention)│
│                                                      │
│ Java package-private (no modifier):                  │
│   class Foo {}  // Only visible in same package      │
│   Only com.example.service classes can use Foo       │
│                                                      │
│ Java public:                                         │
│   public class Bar {}  // Before JPMS: entire JVM   │
│                        // After JPMS: depends on     │
│                        // module's exports           │
└──────────────────────────────────────────────────────┘
```

**JPMS MODULE DECLARATION:**

```java
// module-info.java (in root of source directory)
module com.example.payment {
    // Dependencies (compile + runtime):
    requires java.base;         // implicit always
    requires java.sql;          // JDBC
    requires com.example.model; // our own module

    // What we expose to other modules:
    exports com.example.payment.api;
    // com.example.payment.internal is NOT exported
    // -> external code cannot access it (enforced by JVM)

    // Allow reflection for frameworks (Spring, Hibernate):
    opens com.example.payment.model to spring.core, hibernate.core;
    // 'opens' without 'to': any module can reflect
}
```

---

### 🧪 Thought Experiment

**THE CLASSPATH HELL PROBLEM:**

Before JPMS: two JARs both contain `com.google.common.collect.ImmutableList`.
The JVM classpath loads JARs in order. The first `ImmutableList`
found on the classpath is the one loaded. If JAR A depends
on Guava 20 and JAR B depends on Guava 30, only one version
loads. If JAR B uses a method from Guava 30 that didn't
exist in Guava 20, a `NoSuchMethodError` occurs at runtime
(not compile time). "Works on my machine" = Guava 30 comes
first. Fails in production = Guava 20 comes first.

This is "JAR hell" or "dependency hell." JPMS does not
fully solve this (one version of a module per module name
is still the rule), but it makes the dependency graph
explicit and catches missing dependencies at startup (not
at runtime when a missing class is first accessed).

---

### 🎯 Mental Model / Analogy

**LAYERED SECURITY MODEL:**

Access control in Java with JPMS = four concentric zones:

```
┌─────────────────────────────────────────────┐
│ Module boundary (module exports control)     │
│  ┌──────────────────────────────────────┐   │
│  │ Package boundary (package-private)   │   │
│  │  ┌───────────────────────────────┐   │   │
│  │  │ Class boundary (protected)   │   │   │
│  │  │  ┌────────────────────────┐  │   │   │
│  │  │  │ Method body (private)  │  │   │   │
│  │  │  └────────────────────────┘  │   │   │
│  │  └───────────────────────────────┘   │   │
│  └──────────────────────────────────────┘   │
└─────────────────────────────────────────────┘
```

Each layer adds a boundary. JPMS adds the outermost boundary
that was missing: "even if a class is `public`, if its
package is not exported, external modules cannot see it."

**MEMORY HOOK:**

"Package = namespace + package-private access.
Module = module-info.java + requires/exports.
exports = visible to other modules.
opens = reflection allowed (for Spring/Hibernate).
requires = compile and runtime dependency declared.
Before JPMS: public = global. After JPMS: public + exported = external.
JAR hell: solved partially (explicit dependency graph).
Spring Boot: --add-opens flags for deep reflection in modular JVM."

---

### 📊 Gradual Depth - Five Levels

**Level 1 - Child:**
Your city has neighborhoods (packages). Each neighborhood
has a name. Two people named "John" in different neighborhoods
are different people. You can visit any neighborhood, but
some buildings (modules) have security guards who only
let you into specific floors (exported packages).

**Level 2 - Student:**
```java
// package declaration in each file
package com.example.service;

// import class from another package
import com.example.model.User;
import java.util.List; // java.base module, always available
```

**Level 3 - Professional:**
Packages map directly to directory structure. `com.example.service`
= `src/main/java/com/example/service/`. Package-private classes
(no modifier) cannot be used outside their package - a useful
encapsulation tool even without JPMS. A `ServiceHelper`
that is package-private cannot be misused by code in other packages.

**Level 4 - Senior Engineer:**
JPMS migration challenges:
- Many libraries use deep reflection (`getDeclaredField`, `setAccessible`)
  to access private fields (Hibernate, Jackson, Spring). JPMS blocks
  this by default. Fix: `opens com.example.model to hibernate.core;`
  or JVM flags `--add-opens java.base/java.lang=ALL-UNNAMED`.
- Split packages: the same package in two different JARs.
  JPMS forbids this (a package can only belong to one module).
  Many legacy codebases and frameworks have split packages -
  a major JPMS adoption barrier.

**Level 5 - Expert:**
Unnamed module: all JARs on the classpath (not module-path)
are part of the "unnamed module." The unnamed module can
access ALL packages from named modules (it's a compatibility
layer for legacy code). Named modules cannot require the
unnamed module. This asymmetry is the backward-compatibility
mechanism: old JAR-based code still works on Java 9+
(unnamed module). New JPMS modules can be added to the
module-path; they cannot access unnamed module's internals.
Migration path: classpath (unnamed) -> automatic module
(on module-path, implicit module-info inferred from JAR name) ->
full module (explicit module-info.java).

---

### ⚙️ How It Works (Formal Basis)

**MODULE RESOLUTION AT JVM STARTUP:**

```
┌──────────────────────────────────────────────────────┐
│ JVM startup with JPMS:                               │
│ 1. Read root module(s) from module-path              │
│ 2. Resolve requires graph (BFS traversal)            │
│    - Missing required module -> startup error        │
│    - Circular requires -> startup error              │
│ 3. Check exports/opens against requires              │
│    - Package access violations detected at startup   │
│    - NOT at first use (unlike classpath JAR hell)    │
│ 4. Build module graph (DAG)                          │
│ 5. Start application                                 │
│                                                      │
│ Benefit: "module not found" at startup vs            │
│ "NoClassDefFoundError" at runtime (hours into load   │
│ test when a specific code path is first hit).        │
└──────────────────────────────────────────────────────┘
```

---

### 💻 Code Example

**Example 1 - Wrong vs Right: Missing Package Encapsulation**

```java
// BAD: internal class is public -> anyone can use it
package com.example.payment.internal;

public class PaymentGatewayConnector {
    // Implementation detail - should not be used outside payment module
    public Response connect(String endpoint, Credentials creds) { ... }
}

// External code (different JAR) couples to internal:
import com.example.payment.internal.PaymentGatewayConnector;
// Now the payment team cannot refactor PaymentGatewayConnector
// without breaking external callers. Coupling is invisible.

// GOOD option 1: package-private (no modifier)
package com.example.payment.internal;

// No 'public' keyword - only classes in the same package can use this
class PaymentGatewayConnector {
    Response connect(String endpoint, Credentials creds) { ... }
}
// External code: compilation error (class not visible). Coupling prevented.

// GOOD option 2: JPMS module with unexported package
// module-info.java:
// module com.example.payment {
//     requires java.net.http;
//     exports com.example.payment.api;       // public API only
//     // com.example.payment.internal NOT listed -> not accessible
// }
// External code: InaccessibleObjectException at runtime
// or compilation error with --module-source-path
```

**Example 2 - JPMS module-info.java for a Service Module**

```java
// File: src/main/java/module-info.java
module com.example.orderservice {
    // Compile and runtime dependencies
    requires java.base;           // always implicit
    requires java.sql;            // JDBC for database access
    requires com.fasterxml.jackson.core;   // JSON serialization
    requires spring.context;      // Spring DI
    requires com.example.model;   // shared domain model module

    // Export only the public API package
    exports com.example.orderservice.api;
    // Unexported packages (internal implementation):
    //   com.example.orderservice.repository
    //   com.example.orderservice.service
    //   com.example.orderservice.config

    // Allow Spring to inject into private fields via reflection
    opens com.example.orderservice.api to spring.core;
    opens com.example.orderservice.service to spring.context;
}
// Note: most Spring Boot apps still run on the classpath
// (unnamed module mode) to avoid --add-opens complexity.
// JPMS is more common in library development than application development.
```

---

### ⚖️ Comparison Table

| Feature | Packages (Java 1.0) | Modules (JPMS, Java 9+) | npm packages (Node.js) |
|---|---|---|---|
| Unit | Classes grouped by package | Packages grouped by module | Files in node_modules |
| Encapsulation | package-private + public | exports control public API | module.exports |
| Dependency declaration | Implicit (classpath) | `requires` in module-info | `package.json` dependencies |
| Conflict resolution | Classpath order (fragile) | One module per name (explicit) | Nested node_modules (version isolation) |
| Runtime enforcement | None (all JARs accessible) | JVM enforces exports | Import fails if not exported |

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| "Packages are the same as modules" | Packages are namespaces (prevent name collision, provide package-private access). Modules (JPMS) are deployment units with explicit dependency graphs and export control. A module contains multiple packages. A package is NOT a module. Java had packages since 1.0; modules since Java 9. Many projects use packages without modules (running on the classpath). |
| "JPMS is required for all Java 9+ code" | JPMS is optional. Java 9+ can run entirely without module declarations (all code goes on the classpath as the "unnamed module"). JPMS is beneficial for library authors (enforce public API), the JDK itself, and applications that want explicit dependency management. Most Spring Boot applications still run without `module-info.java`. Spring Boot 3 runs on Java 17+ but defaults to classpath mode. |
| "Making a class `public` makes it accessible to everyone with JPMS" | With JPMS: `public` means accessible within the module (or to other modules IF the package is exported). A `public class` in a non-exported package is accessible within the module but NOT to other modules. JPMS broke the prior meaning of `public` (global). `public` + `exported package` = accessible externally. `public` + non-exported package = module-internal only. |
| "Packages prevent circular dependencies" | Packages do NOT prevent circular dependencies. Two packages in the same codebase can import from each other freely (cyclic package dependencies are a code smell but compile and run fine). JPMS modules prevent circular dependencies between MODULES (circular `requires` is a startup error). Maven/Gradle enforce no circular dependencies at the artifact level. Circular PACKAGE dependencies must be caught by code quality tools (ArchUnit, JDepend, SonarQube). |

---

### 🚨 Failure Modes & Diagnosis

**Failure Mode 1: InaccessibleObjectException (Spring + JPMS)**

**Symptom:** Spring Boot fails to start with:
`java.lang.reflect.InaccessibleObjectException: Unable to make
field private final ... accessible: module java.base does not
"opens java.lang" to unnamed module`

**Root Cause:** Spring uses reflection to inject into private
fields or access private constructors. On Java 9+ with stricter
module defaults, some reflective access is blocked.

**Diagnosis:** Check the full stack trace for the class
and module that is "closed."

**Fix (temporary):** Add JVM argument:
`--add-opens java.base/java.lang=ALL-UNNAMED`

**Fix (proper):** If the class is yours: add `opens` in
`module-info.java`. If it's a library: upgrade to a
JPMS-compatible version of the library.

---

**Security Note:**

Before JPMS, `setAccessible(true)` via reflection could bypass
all Java access controls (`private`, `protected`) at runtime.
Malicious code or vulnerable libraries could access private
credentials stored in fields of other classes. JPMS restricts
this: `opens` is required for deep reflection, and `opens`
can be scoped to specific modules (`opens to com.trusted.module`).
An un-opened package cannot be reflected into from external
modules, even with `setAccessible(true)`. This closes a
significant security gap: library code cannot snoop into
application internals, and application code cannot access
JDK internals that are not exported. The `--add-opens` JVM
flags are effectively "security configuration" for reflection
access.

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**
- `OOP` (CSF-013) - packages organize OOP classes
- `Encapsulation` (CSF-015) - modules extend encapsulation
  to the library/deployment level

**Builds On This (learn these next):**
- `Java Language: Package System` (JLG-005) - Java-specific
  package conventions, import statements, wildcard imports
- `Maven and Build Tools` (MVN-001) - Maven modules and
  multi-module projects align with JPMS concepts

---

### 📌 Quick Reference Card

```
┌────────────────────────────────────────────────────────┐
│ PACKAGE      │ Namespace + package-private access      │
│              │ `package com.example.service;`          │
│              │ Directory = package path                │
├──────────────┼─────────────────────────────────────────┤
│ MODULE       │ module-info.java in source root         │
│              │ requires = dependency                   │
│              │ exports = external visibility           │
│              │ opens = reflection allowed              │
├──────────────┼─────────────────────────────────────────┤
│ ACCESS RULES │ No export + public = module-internal    │
│              │ Exported + public = global access       │
│              │ package-private = package only          │
├──────────────┼─────────────────────────────────────────┤
│ SPRING BOOT  │ Most apps: classpath (unnamed module)   │
│              │ JPMS common for libraries, not apps     │
│              │ --add-opens for legacy reflection       │
├──────────────┼─────────────────────────────────────────┤
│ FAILURE      │ InaccessibleObjectException: add opens  │
│              │ Classpath: classpath order matters      │
├──────────────┼─────────────────────────────────────────┤
│ NEXT EXPLORE │ JLG-005 (Java Packages), MVN-001 (Maven)│
└────────────────────────────────────────────────────────┘
```

**If you remember only 3 things:**

1. Package = namespace (prevents name collision) + package-private
   access (classes without access modifier visible only in
   the same package). Packages map to directory structure.
   Use package-private classes for internal implementation
   details that should not be used outside the package.
2. JPMS module (Java 9+) = `module-info.java` with `requires`
   (dependencies), `exports` (visible packages), `opens`
   (reflection access). A `public` class in a non-exported
   package is NOT accessible outside the module. Modules
   enforce the "internal" contract that packages previously
   expressed only by naming convention.
3. Most Spring Boot applications still run in classpath mode
   (unnamed module), not JPMS module mode. JPMS is most
   beneficial for library authors and the JDK itself. When
   you see `InaccessibleObjectException` at startup, the
   JVM is enforcing JPMS access control for reflection.
   Fix with `--add-opens` (JVM argument) or `opens` in
   module-info if it's your module.

**Interview one-liner:**
"Packages group classes under a namespace and provide package-private
access control. JPMS modules (Java 9+) group packages with
declared `requires` dependencies and `exports` visibility;
unexported `public` classes are module-internal only.
Package = namespace. Module = deployment unit with enforced API boundary."

---

### 💎 Transferable Wisdom

**Reusable Engineering Principle:**
The package/module system is an implementation of the
"information hiding" principle at different granularity levels.
`private` hides from other classes. Package-private hides
from other packages. Module unexported hides from other
modules. Each boundary is a contract: "the implementation
behind this boundary can change without breaking callers."
The absence of a module boundary (pre-JPMS) is why JDK
internal APIs (`sun.misc.Unsafe`) became load-bearing
dependencies in major frameworks: they were accessible,
they worked, and now they cannot be removed. Module systems
(JPMS, npm, Go modules, Python wheels) are all attempts
to enforce the boundary between public API and private
implementation at the deployment unit level.

**Where else this pattern appears:**

- **Go packages and modules** - Go has packages (directory-based,
  lowercase function names = package-private, uppercase =
  exported). Go modules (`go.mod`) declare the module name
  and dependency versions. All exported names (uppercase)
  from a package are accessible to other packages in the
  same module. Cross-module: same rules (exported = visible).
  Go enforces no circular imports between packages (unlike Java).
  Circular imports = compile error in Go. This makes Go's
  package structure inherently DAG-shaped (no cycles).
- **Python packages and `__all__`** - Python packages =
  directories with `__init__.py`. Names starting with `_`
  are "private by convention" (not enforced). `__all__` in
  `__init__.py` declares what `from package import *` exports.
  Without `__all__`: everything is importable (no module-level
  enforcement). Python's packaging (pip, PyPI) = distribution
  units (analogous to JARs). PEP 517/518 (pyproject.toml)
  are the Python equivalent of Maven pom.xml.
- **microservice boundary as module boundary** - A microservice's
  API (REST, gRPC) is the "exports" of the service module.
  Internal implementation (database schema, internal services,
  data structures) is unexported. Other services must use
  the public API. This is why internal database schemas
  are never shared between microservices: sharing the schema
  is like using a non-exported internal class - it creates
  an invisible coupling that makes independent deployment impossible.

---

### 💡 The Surprising Truth

Java's module system (JPMS) was delayed multiple times
and was the most controversial feature in Java history.
Project Jigsaw (JPMS's development name) was originally
planned for Java 7 (2011), then Java 8 (2014), then Java 9
(finally released 2017). The 6-year delay was caused primarily
by ONE issue: OSGi. The enterprise Java ecosystem had built
an existing module system (OSGi - Open Service Gateway Initiative,
used by Eclipse, Apache Felix, Spring Dynamic Modules)
that solved many of the same problems. IBM, Red Hat, and
others argued that JPMS was incompatible with OSGi and
would fragment the ecosystem. The Expert Group vote was
unprecedented: 13 votes for (Oracle + most votes), 4 against
(IBM, Red Hat, Twitter, Intel) - the largest opposition
in a Java JSR vote. Despite the controversy, JPMS shipped
with Java 9. Today: most enterprise applications ignore
JPMS and run in classpath mode. OSGi is still used in
Eclipse plugins. JPMS found its sweet spot in modularizing
the JDK itself (achieving smaller runtime footprints for
container deployments via `jlink`) rather than replacing
OSGi or becoming universal in application development.

---

### ✅ Mastery Checklist

**You've mastered this when you can:**

1. **[IDENTIFY]** In a Spring Boot project, list which classes
   should be package-private vs public. Create a package
   structure for a `payment` module with separate API,
   service, repository, and model packages. Make internal
   classes package-private.

2. **[MODULE]** Create a `module-info.java` for a Java library
   that: exports the `api` package, keeps the `impl` package
   internal, opens the `model` package to Hibernate, and
   requires `java.sql`.

3. **[DIAGNOSE]** Given a Spring Boot application that throws
   `InaccessibleObjectException` when starting on Java 17,
   diagnose which module is blocking reflection and provide
   the correct `--add-opens` JVM argument.

4. **[EXPLAIN]** Explain why OSGi (existing before JPMS)
   solves different problems than JPMS for enterprise applications.
   When would you use JPMS vs OSGi vs neither?

5. **[DESIGN]** Design the package structure for a multi-module
   Maven project with: a shared domain model, a REST API
   module, a persistence module, and a messaging module.
   Define which packages are internal vs exported between modules.

---

### 🧠 Think About This Before We Continue

**Q1.** A Maven project has module A and module B. Module A
has class `com.example.a.InternalHelper` (package-private).
Module B wants to use `InternalHelper`. What are the options,
and which is architecturally correct?

*Hint:
Options:
1. Make `InternalHelper` public: wrong. Now it's a public API.
   Other modules can also use it. You've promoted an internal
   detail to a public API.
2. Move `InternalHelper` to a shared module C and import C
   from both A and B: correct IF the helper is genuinely shared.
   Reflect: why does B need A's internal helper? Is this
   a sign that A and B should be merged? Or that the helper
   belongs in a shared module?
3. Duplicate the helper in B: wrong. Code duplication.
4. Make `InternalHelper` package-private in a shared package
   that both A and B are in: violates the package structure
   (A and B are separate modules with different package roots).
   Not possible with JPMS modules (different module = different
   package namespace).
5. Refactor B to not need A's internals: usually the correct
   answer. If B needs A's internal helper, the dependency
   is coupling B to A's implementation details. Provide
   a public API in A that exposes the needed functionality
   without exposing the internal class.*

**Q2.** What is the difference between `exports` and `opens`
in a JPMS `module-info.java`? When do you need each?

*Hint:
`exports com.example.api`:
- Makes all public types in `com.example.api` accessible
  to code in other modules at compile time AND runtime.
- Compile-time: other modules can import the types.
- Runtime: code can use the types directly.
- Does NOT allow reflective access to private members.

`opens com.example.model`:
- Allows any module to use DEEP REFLECTION on `com.example.model`
  at runtime. Specifically: `getDeclaredFields()`, `setAccessible(true)`,
  `getDeclaredConstructors()`.
- Does NOT grant compile-time access (types are not importable).
- Required for: Hibernate (accesses private entity fields),
  Jackson (accesses private record components or private fields),
  Spring (accesses @Autowired private fields or @Value fields).

You need `exports` for code that other modules call directly
(public API). You need `opens` for code that frameworks
access via reflection (domain models, Spring beans, Jackson DTOs).
You can have `opens ... to <module>` (scoped) or `opens ...`
(all modules). Scoped is better security.
Both `exports` and `opens` can apply to the same package.*

---

### 🎯 Interview Deep-Dive

**Q1: "What is the Java module system (JPMS) and why was it introduced?"**

*Why they ask:* Tests Java 9+ knowledge. Senior Java developers
should know JPMS even if they don't use it daily.

*Strong answer includes:*
- Introduced in Java 9 as Project Jigsaw. Adds a module layer
  above packages.
- Problems it solves: (1) No way to enforce internal API
  boundaries (`public` was global). (2) Classpath fragility
  (JAR hell: missing JARs discovered at runtime, split packages).
  (3) JDK could not be made smaller (entire JDK always loaded).
- How: `module-info.java` declares `requires` (dependencies)
  and `exports` (visible packages). Un-exported packages
  are inaccessible to other modules even if classes are `public`.
- JDK modularization: JDK is split into 20+ modules
  (`java.base`, `java.sql`, `java.desktop`, etc.). `jlink`
  creates custom runtimes with only needed modules (useful
  for containers: smaller images).
- Adoption: most Spring Boot apps still run in classpath
  (unnamed module) mode. JPMS is more used in library
  development and JDK itself.

**Q2: "When would you use package-private access in Java?"**

*Why they ask:* Tests whether the developer uses all
available encapsulation tools, not just public/private.

*Strong answer includes:*
- Package-private (no access modifier): class/method/field
  is accessible only within the same package.
- Use cases: internal helper classes that implement details
  of the public API (e.g., a `PaymentProcessor` class that
  implements complex logic but should not be used directly).
  These are `class PaymentProcessor {}` (package-private),
  used only by the `public class PaymentService {}` in the
  same package.
- The pattern: one or few public classes that form the API,
  many package-private classes that implement details.
  Prevents "accidental coupling": external code cannot
  depend on internal classes (compiler enforces it).
- Alternative to JPMS for teams that don't adopt JPMS:
  package-private + naming convention (`internal` in package
  name) is practical encapsulation without JPMS overhead.
