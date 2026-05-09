---
id: CSF-037
title: Modules and Packages
category: CS Fundamentals - Paradigms
tier: tier-1-foundations
folder: CSF-cs-fundamentals
difficulty: ★★☆
depends_on:
used_by:
related:
tags:
  - csf
  - intermediate
  - pattern
status: draft
version: 1
layout: default
parent: "CS Fundamentals - Paradigms"
grand_parent: "Technical Dictionary"
nav_order: 37
permalink: /csf/modules-and-packages/
---

# CSF-037 - Modules and Packages

⚡ TL;DR - Modules and packages are the unit of code organisation at the file/directory level: they control what is visible, what is importable, and what are the build and deployment units.

| CSF-037         | Category: CS Fundamentals - Paradigms | Difficulty: ★☆☆ |
| :-------------- | :------------------------------------ | :-------------- |
| **Depends on:** | CSF-006, CSF-021, CSF-011             |                 |
| **Used by:**    | CSF-065, CSF-066                      |                 |
| **Related:**    | CSF-011, CSF-065, CSF-066             |                 |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
Without modules, all code lives in a single namespace. Every
function name must be globally unique. A `sort()` in one library
clashes with `sort()` in another. As codebases grow, names must
be mangled: `user_sort`, `order_sort`, `inventory_sort`. In C,
this is still partially true: the linker merges all functions
into a single namespace.

**THE BREAKING POINT:**
Early JavaScript had no module system. Every `<script>` tag
shared the global `window` namespace. Libraries polluted
globals. Version conflicts caused silent overrides. The
Callback Hell era also produced Namespace Hell: every team
prefixed everything with their company name to avoid clashes.

**THE INVENTION MOMENT:**
MLs (1973) and Modula-2 (1977) formalised the module as a unit
of encapsulation and namespace management. A module explicitly
exports its public API and hides its implementation. Callers
can only access what's exported. Java packages, Python modules,
Node.js CommonJS/ESModules, and Rust crates all follow this model.

**EVOLUTION:**
Modules evolved from compilation units (reducing build times)
to namespace managers to distribution units (npm packages,
Maven artifacts). The Java Module System (JPMS, Java 9) added
strong encapsulation at the JVM level: a module can declare
which packages it exports to which other modules, enabling
true encapsulation across JAR boundaries.

---

### 📘 Textbook Definition

A **module** is a unit of code organisation that encapsulates
related declarations and controls visibility through explicit
exports. A **package** is a namespace grouping of related
classes/modules, usually corresponding to a directory structure.
Together, modules and packages provide: (1) namespace management
(avoid name clashes); (2) encapsulation (hide implementation);
(3) dependency declaration (explicit imports); (4) compilation
and deployment units.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
Modules group related code, control what's visible, and prevent name clashes across a large codebase.

**One analogy:**

> A module is like a department in a company. Each department
> has an internal phone book (private members) and a public
> reception number (exported API). Other departments call the
> reception — they can't call internal extensions directly.
> The company directory (package) lists all departments.

**One insight:**
Every public API in a module is a contract that other code
depends on. Every private/internal API is an implementation
detail you can change freely. The smaller your public API,
the more freedom you have to refactor.

---

### 🔩 First Principles Explanation

**CORE INVARIANTS:**

1. A module has an explicit boundary: what's inside vs what's visible outside.
2. Imports make dependencies explicit and auditable.
3. Cyclic dependencies between modules are a design smell.
4. Public API = contract; private = implementation detail (free to change).
5. One module per coherent concept; one concept per module (SRP at module level).

**DERIVED DESIGN:**

- **Java package**: namespace grouping; `public` = visible outside, no `public` = package-private
- **Java JPMS module** (Java 9): explicit `exports` in `module-info.java`
- **Python module**: `.py` file; `__all__` controls what `from x import *` exports
- **Node.js CommonJS**: `module.exports = { ... }` explicit export
- **ES Modules**: `export` keyword; `import { x } from './y'`
- **Rust crate/module**: `pub` keyword; `mod` blocks; `use` for imports

**THE TRADE-OFFS:**
**Gain:** Encapsulation, refactor freedom, explicit dependencies.
**Cost:** Indirection overhead; module boundaries require discipline;
circular dependency errors when modules are too tightly coupled.

**ESSENTIAL vs ACCIDENTAL COMPLEXITY:**
**Essential:** Large codebases require organisation; namespaces prevent collisions.
**Accidental:** Circular dependencies, "utils" catch-all modules, over-fragmentation.

---

### 🧪 Thought Experiment

**SETUP:**
You build a system with three teams: User, Order, Inventory.
No module boundaries. All code in one namespace.

**WHAT BREAKS:**

- `User.Service` and `Order.Service` conflict — everyone adds prefixes
- Team A changes `validate()` helper — Team B's code breaks silently
- Circular calls: User calls Order calls User — dependency cycle, impossible to test in isolation
- Adding a new feature requires searching all code for side effects

**WITH MODULES:**

- Each team owns their module; exports only their public API
- `UserModule.validate()` and `OrderModule.validate()` are separate
- Circular dependencies caught at compile/import time
- Each team can refactor internals without breaking others

**THE INSIGHT:**
Module boundaries are team boundaries encoded in code. Conway's
Law says teams build systems that mirror their communication
structure. Modules make that structure explicit and enforceable.

---

### 🧠 Mental Model / Analogy

> A module is an iceberg. The exported API is the visible part
> above water — everything else uses this. The implementation
> is the 90% below the surface: other modules can't see it,
> can't depend on it, and can't break when you change it.

**Element mapping:**

- Iceberg above water = exported public API
- Iceberg below water = private implementation
- Ocean = the rest of the codebase (can only see above water)
- Ship navigation = your code navigating by module APIs

Where this analogy breaks down: reflection in Java can access
private members, partially bypassing module visibility
(mitigated by JPMS strong encapsulation).

---

### 📶 Gradual Depth - Four Levels

**Level 1 - What it is (anyone can understand):**
Modules are folders for code. They group related things,
give them a name, and decide which parts other code can see.
Like a book chapter: you see the chapter title and contents,
but not the author's private notes.

**Level 2 - How to use it (junior developer):**
Organise Java code by feature, not by layer: `com.app.user`
(User + UserRepository + UserService) not `com.app.repository`
(all repositories together). Keep internal helpers
package-private (no `public`). Only make public what is
genuinely needed by other packages.

**Level 3 - How it works (mid-level engineer):**
Java JPMS (`module-info.java`) adds a second layer of
encapsulation beyond `public/private`. `exports com.app.user`
makes the package available to other modules. `exports com.app.user
to com.app.order` restricts it to a specific module. The JVM
enforces this at class loading time — unlike jar-level `public`
which is accessible to anyone with the jar on the classpath.

**Level 4 - Why it was designed this way (senior/staff):**
The `module-info.java` approach was driven by the JDK's own
modularisation (Project Jigsaw): the JDK itself was split into
~90 modules. This enables minimal JVM packaging (custom runtimes
with only required modules), reduces attack surface (internal
JDK APIs no longer accessible), and makes dependency graphs
machine-readable for tooling.

**Expert Thinking Cues:**

- When reviewing a package: are all its classes cohesive (same concept)?
- When seeing `public` on a class: does external code actually need this?
- When a module has a dependency cycle: which abstraction is missing?

---

### ⚙️ How It Works (Mechanism)

**Java module-info.java:**

```java
module com.app.user {
    requires com.app.common;       // dependency
    exports com.app.user.api;      // public API
    // com.app.user.internal is NOT exported = private
}
```

**ES Module (browser/Node.js):**

```javascript
// user.js
export class User { ... } // public
function validateInternal() { ... } // private (not exported)

// order.js
import { User } from './user.js'; // explicit dependency
```

**Python:**

```python
# user/__init__.py
from .user import User  # exported
# user/_internal.py - convention-only private
```

---

### 🔄 The Complete Picture - End-to-End Flow

**NORMAL FLOW:**

```
order.Service imports user.API  ← YOU ARE HERE
  |-> compiler checks: does user module export user.API?
  |-> yes: import allowed
  |-> no: compile error (JPMS) or runtime error (classic Java)
order.Service calls user.UserRepository directly
  |-> user.UserRepository is not exported
  |-> JPMS: InaccessibleObjectException
  |-> classic Java: works (bad! encapsulation violated)
```

**FAILURE PATH:**

- Circular dependency: A imports B imports A — build failure or runtime error
- Missing module declaration: `requires` not declared — ClassNotFoundException at runtime
- Over-broad exports: everything public, nothing truly encapsulated

---

### ⚖️ Comparison Table

| System                | Encapsulation Level                   | Circular Dep Detection | Explicit Dependency?       |
| --------------------- | ------------------------------------- | ---------------------- | -------------------------- |
| Java packages (pre-9) | Weak (public = accessible everywhere) | No                     | No                         |
| Java JPMS (9+)        | Strong (exports explicit)             | At build time          | Yes (`requires`)           |
| Node.js CommonJS      | Medium (exports object)               | No (runtime)           | Yes (`require`)            |
| ES Modules            | Medium (export keyword)               | Build tools            | Yes (`import`)             |
| Rust crates           | Strong (pub/pub(crate))               | Build time             | Yes (`use`/`extern crate`) |
| Python                | Weak (convention-based `_`)           | No                     | Yes (`import`)             |

---

### ⚠️ Common Misconceptions

| Misconception                                  | Reality                                                                                              |
| ---------------------------------------------- | ---------------------------------------------------------------------------------------------------- |
| "`public` in Java means visible to everyone"   | Public + no JPMS = visible to any class; public + JPMS = only visible to modules that `requires` you |
| "Packages and modules are the same"            | Packages are namespace groups; modules (JPMS) are explicit dependency+export declarations            |
| "The `utils` package is fine"                  | Utils is a junk drawer; everything in it lacks a home because it's not part of a coherent concept    |
| "More packages = better organisation"          | Over-fragmentation creates too many indirections; group by feature, not by type                      |
| "Circular dependencies only matter at runtime" | They indicate a design flaw: two things that are too tightly coupled to be separated                 |

---

### 🚨 Failure Modes & Diagnosis

**Mode 1: Circular Module Dependency**
**Symptom:** Build fails with "circular dependency" or `ClassCircularityError` at runtime.
**Root Cause:** Module A depends on Module B which depends on A.
**Diagnostic:**

```bash
# Maven dependency tree
mvn dependency:tree
# Check for cycles in a Java project
jdeps --module-path . --check <module>
```

**Fix:** Extract a third module C containing the shared abstraction.

**Mode 2: Unintended Internal API Exposure**
**Symptom:** External team calls your internal class; refactoring breaks them.
**Root Cause:** Internal classes are `public` without module restrictions.
**Fix:** Use Java JPMS with explicit `exports`; use `exports ... to` for single-consumer APIs.

**Mode 3: Missing `requires` (JPMS)**
**Symptom:** `module not found` or `package not visible` at compile time.
**Root Cause:** `module-info.java` missing `requires` declaration.
**Fix:** Add `requires <module.name>` to `module-info.java`.

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**

- [[CSF-006 - Imperative Programming]]
- [[CSF-011 - Encapsulation and Information Hiding]]

**Builds On This (learn these next):**

- [[CSF-065 - Dependency Hell and Package Management]]
- [[CSF-066 - Polyglot Architecture Strategy]]

**Alternatives / Comparisons:**

- Microservices (modules at service level)
- Monorepos (many modules in one repo)

---

### 📌 Quick Reference Card

```
┌─────────────────────────────────────────────────────┐
│ WHAT IT IS      Units of code organisation with       │
│                 namespaces and explicit exports       │
│ PROBLEM         Name clashes, leaked internals,        │
│ IT SOLVES       implicit dependencies                 │
│ KEY INSIGHT     Public API = contract; private =       │
│                 free-to-change implementation        │
│ USE WHEN        Any codebase with >1 team or >1 concern│
│ AVOID WHEN      "utils" catch-all packages;            │
│                 circular dependencies                │
│ TRADE-OFF       Encapsulation vs accessibility         │
│ ONE-LINER       Modules are team boundaries encoded    │
│                 in code                              │
│ NEXT EXPLORE    CSF-065, JPMS, ESModules              │
└─────────────────────────────────────────────────────┘
```

**If you remember only 3 things:**

1. Modules group related code and expose only what callers need; everything else is private.
2. Public API = contract (can't change freely); private/internal = implementation detail (change at will).
3. Circular module dependencies signal a missing abstraction, not just a code quality issue.

**Interview one-liner:**
"Modules group related code behind an explicit public API, preventing name clashes, hiding implementation details, and making dependencies explicit — they encode team and concept boundaries in code structure."

---

### 💎 Transferable Wisdom

**Reusable Engineering Principle:**
Minimise your public API. Every exported symbol is a promise
you must keep. Every unexported symbol is an implementation
detail you can change freely. The smaller the public surface,
the greater the refactor freedom.

**Where else this pattern appears:**

- **HTTP API design** — public endpoints are contracts; internal service calls are implementation
- **Database views** — views expose selected data; underlying tables are implementation
- **AWS IAM policies** — policy exports define what external services can call

---

### 💡 The Surprising Truth

Java's `public` modifier, before Java 9, provided no encapsulation
between JARs. Any class with `public` in any JAR was accessible
by any other code on the classpath — including JDK internal APIs
like `sun.misc.Unsafe`. This is why Java 9's JPMS was so
controversial: it broke thousands of libraries that relied on
internal JDK APIs. The lesson: encapsulation without enforcement
is documentation, not architecture. Real encapsulation requires
a runtime mechanism that enforces the boundary.

---

### 🧠 Think About This Before We Continue

**Q1 (System Interaction):** Java's `module-info.java` allows
`opens com.app.internal to framework.module` which allows
reflection into a package that is not exported. Spring and
Hibernate both require `opens` to work. What does this reveal
about the tension between strong encapsulation and framework
conventions?

_Hint:_ Research why Spring Boot requires `--add-opens` flags
or `opens` in module-info. What Spring features depend on reflection?

**Q2 (Scale):** A monorepo has 500 modules with explicit
dependency declarations. The dependency graph can be analysed
to understand coupling. How would you identify which modules
are "too central" (depended on by many others), and why is
this important for deployment and testing strategy?

_Hint:_ Research graph centrality measures (in-degree, betweenness
centrality) applied to module dependency graphs. Tools like
Structure101 or JDepend visualise this.

**Q3 (Design Trade-off):** Node.js originally used CommonJS
(`require`/`module.exports`) but ES Modules (`import`/`export`)
is now standard. They cannot directly mix. What architectural
problem does this dual-module-system create for a large
Node.js project?

_Hint:_ Research the CommonJS/ESM interoperability problem in
Node.js, why `import` is asynchronous while `require` is
synchronous, and what `.mjs` files are.
