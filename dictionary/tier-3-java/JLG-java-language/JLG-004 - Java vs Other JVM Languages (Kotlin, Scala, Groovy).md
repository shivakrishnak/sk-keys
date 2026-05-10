---
id: JLG-004
title: "Java vs Other JVM Languages (Kotlin, Scala, Groovy)"
category: Java Language
tier: tier-3-java
folder: JLG-java-language
difficulty: ★☆☆
depends_on: JLG-001, JLG-002, JLG-003
used_by: JLG-077, JLG-084
related: JLG-075, JLG-081, JLG-083
tags:
  - java
  - foundational
  - tradeoff
  - mental-model
status: complete
version: 2
layout: default
parent: "Java Language"
grand_parent: "Technical Dictionary"
nav_order: 4
permalink: /jlg/java-vs-other-jvm-languages-kotlin-scala-groovy/
---

# JLG-004 - Java vs Other JVM Languages (Kotlin, Scala, Groovy)

⚡ TL;DR - The JVM ecosystem has four primary languages - Java, Kotlin, Scala, and Groovy - each with different design goals; the right choice depends on the domain, not preference.

| Field          | Value                                                                                                                                                     |
| -------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Depends on** | [[JLG-001 - What Is Java - History and Philosophy]], [[JLG-002 - The Java Ecosystem Map (SE, EE, ME, Android)]], [[JLG-003 - Why Java Is Still Dominant]] |
| **Used by**    | [[JLG-077 - Java in Polyglot Architecture]], [[JLG-084 - Java Ecosystem Selection Framework]]                                                             |
| **Related**    | [[JLG-075 - Java Modularity Strategy (JPMS)]], [[JLG-081 - Java Language Design History and Rationale]], [[JLG-083 - Language Feature Trade-off Framing]] |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**

An Android team debates whether to use Kotlin or Java for a new app. A data engineering team debates Scala vs Java for a new Spark pipeline. A DevOps team debates Groovy vs Kotlin for Gradle build scripts. Each team has opinions but no framework for making the decision systematically.

**THE BREAKING POINT:**

The JVM ecosystem has multiple production-grade languages. Choosing "the best JVM language" without understanding their design goals leads to mismatches: using Scala's complexity for a simple CRUD app; using Java's verbosity for a functional data pipeline; using Groovy's dynamic typing where compile-time safety is critical.

**THE INVENTION MOMENT:**

Each non-Java JVM language was born from a specific dissatisfaction with Java at a point in time. Groovy (2004) added scripting/dynamic features Java lacked. Scala (2004) brought Haskell-style type theory and functional programming. Kotlin (2011) addressed Java's null-safety and verbosity problems without abandoning OOP. Understanding the problem each language solved reveals where it is still the best choice.

**EVOLUTION:**

- **2004:** Groovy 1.0 - dynamic JVM scripting language; later powers Gradle and Grails
- **2004:** Scala 0.1 - functional+OOP hybrid with advanced type system
- **2011:** Kotlin 1.0 announced by JetBrains (released 2016) - null-safe, concise Java alternative
- **2017:** Google endorses Kotlin as first-class Android language
- **2019:** Kotlin Multiplatform (KMP) - Kotlin compiles to JVM, WASM, JS, native
- **2022:** Kotlin 1.7 - K2 compiler preview (2× faster compilation)
- **2023:** Kotlin Multiplatform Mobile (KMM) reaches stable; Groovy 4 adds Java-compatible syntax

---

### 📘 Textbook Definition

**JVM languages** are programming languages that compile to JVM bytecode and interoperate with Java classes and libraries. The primary alternatives to Java on the JVM are:

- **Kotlin** (JetBrains, 2016): statically typed, null-safe, concise Java-compatible language; first-class Android support; Kotlin Coroutines for async; KMP for multiplatform
- **Scala** (EPFL, 2004): statically typed, functional+OOP hybrid; advanced type system (implicits, type classes); primary language for Apache Spark; Akka ecosystem
- **Groovy** (ASF, 2004): optionally typed (static or dynamic), JVM scripting language; powers Gradle DSL; easy Java interop; used in Jenkins pipelines

All three compile to the same JVM bytecode and can import/extend Java classes. Java can import Kotlin/Scala/Groovy classes with some limitations.

---

### ⏱️ Understand It in 30 Seconds

**One line:** Kotlin replaces Java for new code; Scala dominates functional/data-engineering; Groovy powers build scripts and test DSLs - each owns a distinct niche.

> JVM languages are like specialist tools in a workshop: Java is the standard drill (reliable, familiar, everyone has one). Kotlin is the upgraded cordless drill (more ergonomic, same holes). Scala is the precision CNC machine (extraordinary capabilities, steep learning curve). Groovy is the flexible hand tool (good for quick work, not for structural components).

**One insight:** The best JVM language choice is often determined not by language features but by the framework's primary language: Spark pipelines → Scala; Spring Boot backends → Java or Kotlin; Gradle build scripts → Groovy or Kotlin DSL; Android apps → Kotlin.

---

### 🔩 First Principles Explanation

**CORE INVARIANTS:**

1. All JVM languages share the same runtime: JVM performance tuning, GC configuration, and monitoring apply equally
2. Interoperability is bidirectional but asymmetric: calling Java from Kotlin is seamless; calling Kotlin from Java requires awareness of nullability annotations and extension functions
3. Team productivity on language X is proportional to team experience with X, not language X's intrinsic quality
4. Language choice is sticky: rewriting 500K lines of Scala to Java is as costly as rewriting to any other language
5. Framework ecosystem matters more than language: Spring Boot is Java/Kotlin-first; Spark is Scala-first; no JVM language gives access to a framework designed for another

**DERIVED DESIGN:**

From invariant 1 → JVM language choice does not affect production monitoring, GC tuning, JFR profiling, or heap analysis. These skills transfer fully.
From invariant 3 → a team of expert Java developers will outperform Kotlin on day 1; after 6 months of Kotlin practice, they will likely prefer Kotlin for new code.
From invariant 5 → for Spark, Scala is not a preference; it is required for full API access (Scala Dataset API is richer than Java API; Python API has overhead).

**THE TRADE-OFFS:**

**Kotlin vs Java:**
Kotlin gain: null safety, data classes, coroutines, extension functions, sealed classes (nicer syntax), less boilerplate.
Kotlin cost: slower compilation than Java (K2 compiler closing this gap), additional framework for coroutines, team must learn Kotlin idioms.

**Scala vs Java:**
Scala gain: type system expressiveness, functional programming, pattern matching (since Scala 2), Akka ecosystem.
Scala cost: compile times 3-5× Java; steep learning curve (implicits, category theory); binary incompatibility between Scala 2.12/2.13/3 versions.

**Groovy vs Java:**
Groovy gain: scripting speed, DSL power (Gradle, Jenkinsfile), optional typing, runtime metaprogramming.
Groovy cost: dynamic typing → runtime errors instead of compile-time errors; slower than Kotlin for Gradle scripts (Kotlin DSL now preferred for new Gradle scripts).

**ESSENTIAL vs ACCIDENTAL COMPLEXITY:**

**Essential:** Null safety (Kotlin's primary innovation over Java) is an essential improvement; null-pointer exceptions are the most common production exception in Java.

**Accidental:** Scala's implicit conversions are extremely powerful but create invisible code paths that are hard to debug. The implicits mechanism solves real type-system problems but introduces accidental complexity through abuse.

---

### 🧪 Thought Experiment

**SETUP:** A JetBrains engineer in 2010 is frustrated writing Java for IntelliJ IDEA. Null checks litter the code. Data classes require 100 lines of boilerplate for 5 fields. Anonymous inner classes are verbose even for simple callbacks. Java 8 is 4 years away.

**WITHOUT Kotlin (Java only):**

```java
// BAD: Java 6 era - verbose, null-unsafe
public class User {
    private final String name;
    private final String email;
    // constructor, getters, equals,
    // hashCode, toString = 80 lines
}
// NullPointerException possible at every
// method call on User fields
```

**WITH Kotlin:**

```kotlin
// GOOD: Kotlin - concise, null-safe
data class User(
    val name: String,       // non-null
    val email: String?      // nullable
)
// Compiler-enforced null safety
// equals/hashCode/toString auto-generated
// copy() for immutable modification
```

**THE INSIGHT:**

Kotlin did not invent null safety or data classes. It packaged improvements that the Java community had been requesting for a decade into a production-ready, Java-compatible language. The insight is that JVM language innovation is incremental, not revolutionary - and the right language is the one that solves your specific friction points within your domain.

---

### 🧠 Mental Model / Analogy

> JVM languages are like dialects of the same spoken language. Standard American English (Java) is universally understood. British English (Kotlin) uses slightly different vocabulary and idioms; understanding is nearly perfect either way. Academic English (Scala) is precise and expressive for scholarly work but impractical for casual conversation. Street slang (Groovy) is quick and expressive for informal communication but inappropriate for legal documents.

**Element mapping:**

- Standard American English → Java (standard, universal, no surprises)
- British English → Kotlin (nearly identical, different idioms, widely understood)
- Academic English → Scala (precise, complex, restricted audience)
- Street slang → Groovy (informal, quick, context-specific)
- JVM bytecode → the underlying brain process that understands all dialects

Where this analogy breaks down: unlike dialects, Scala's type system gives it genuine capabilities that Java cannot express, not just stylistic differences.

---

### 📶 Gradual Depth - Four Levels

**Level 1 - What it is (anyone can understand):**
Java has several cousin languages that run on the same JVM. Kotlin is like a modernised Java - same ideas but shorter, safer. Scala is like Java with a PhD - very powerful but complex. Groovy is like Java's laid-back sibling - great for scripting and configuration, less strict.

**Level 2 - How to use it (junior developer):**
For a new Android app: use Kotlin (Google endorsement, better null safety, less boilerplate). For a new Spring Boot backend: either Java or Kotlin (Spring supports both equally well since Spring 5). For Gradle build scripts: Kotlin DSL (better IDE support than Groovy DSL). For a data pipeline on Apache Spark: Scala (richest Dataset API; most Spark examples in Scala).

**Level 3 - How it works (mid-level engineer):**
Kotlin compiles to JVM bytecode via `kotlinc`; Kotlin standard library (`kotlin-stdlib`) adds ~1.6MB to the classpath. Kotlin Coroutines (`kotlinx-coroutines-core`) add structured concurrency: `suspend fun`, `CoroutineScope`, `Flow`. Scala uses `scalac`; Scala 2 and Scala 3 (Dotty) have incompatible bytecode for macros; Scala's SBT build tool is slower than Maven/Gradle. Groovy can be compiled statically (`@CompileStatic`) or dynamically (default); dynamic mode enables runtime metaprogramming (AST transformations, meta-object protocol) that powers Gradle's `task { }` blocks.

**Level 4 - Why it was designed this way (senior/staff):**
Kotlin's design philosophy is explicit and documented: make Java developers productive in Kotlin with a gentle learning curve. JetBrains had a commercial incentive (IntelliJ IDEA) to make Kotlin IDE support excellent - which is why Kotlin's IDE experience is superior to Scala's. Scala's design philosophy (Martin Odersky) is academic: make the type system expressive enough to encode entire program logics in types. This produces exceptional code when used by type-system experts; it produces unmaintainable code when used by average developers who don't understand the implications of their implicit conversions. The Scala community's long debate over whether implicits should be rebranded "given/using" in Scala 3 reflects this tension.

**Expert Thinking Cues:**

- Kotlin Coroutines vs Java Virtual Threads: coroutines are library-level structured concurrency; virtual threads are JVM-level scheduling. Both solve I/O concurrency. Key difference: coroutines propagate context explicitly; virtual threads use thread-local variables
- Scala's `implicit` feature was renamed to `given`/`using` in Scala 3 - the rename was specifically to reduce accidental use
- Groovy's `@CompileStatic` annotation makes it perform like Java; without it, Groovy uses dynamic dispatch (invokedynamic)

---

### ⚙️ How It Works (Mechanism)

```
JVM Language Compilation Pipeline:

Kotlin (.kt)    Scala (.scala)    Groovy (.groovy)
     |                |                 |
  kotlinc          scalac            groovyc
     |                |                 |
     └────────────────┴─────────────────┘
                      |
              JVM Bytecode (.class)
                      |
            [JVM - HotSpot / GraalVM]
                      |
              Native machine code
                      |
              Production execution
              (same GC, JFR, JMX as Java)
```

---

### 🔄 The Complete Picture - End-to-End Flow

**NORMAL FLOW - choosing between Java and Kotlin for Spring Boot:**

```
[New microservice project starts]
     |
     ├─ Use case: REST API + JPA + Spring Boot
     |    ← YOU ARE HERE (language selection)
     |
     ├─ Option A: Java
     |    ├─ All Spring Boot docs in Java
     |    ├─ All team members know Java
     |    └─ Safe, zero learning curve
     |
     ├─ Option B: Kotlin
     |    ├─ Spring Boot 5 has first-class Kotlin support
     |    ├─ Null safety removes NPE risk
     |    ├─ Data classes replace POJOs
     |    └─ Requires team Kotlin familiarisation
     |
[Decision factors: team expertise, NPE pain,
 maintenance horizon, onboarding cost]
```

**FAILURE PATH:**

- Choosing Scala for a simple CRUD service → 3-5× compile time, hiring difficulty, complexity premium for no benefit
- Choosing Groovy (dynamic) for business-critical logic → runtime ClassCastExceptions replace compile-time errors
- Mixing Kotlin and Java in same module with complex generics → null-safety annotations may not propagate correctly across language boundary

**WHAT CHANGES AT SCALE:**

Large Scala codebases have compilation time problems: a 1M-line Scala codebase can take 20-40 minutes to compile incrementally. This drove LinkedIn, Twitter, and Foursquare to reduce Scala usage. The Scala 3 compiler is faster but migration from Scala 2 requires code changes.

---

### 💻 Code Example

**Same task in four JVM languages:**

```java
// Java 21 - concise with records
record Order(
    String id,
    BigDecimal amount,
    List<String> items
) {}

List<Order> bigOrders = orders.stream()
    .filter(o -> o.amount()
        .compareTo(BigDecimal.valueOf(100)) > 0)
    .collect(Collectors.toList());
```

```kotlin
// Kotlin - null-safe, extension functions
data class Order(
    val id: String,
    val amount: BigDecimal,
    val items: List<String>
)

val bigOrders = orders.filter {
    it.amount > BigDecimal(100)
}
```

```scala
// Scala 3 - functional, case class
case class Order(
  id: String,
  amount: BigDecimal,
  items: List[String]
)

val bigOrders = orders
  .filter(_.amount > BigDecimal(100))
```

```groovy
// Groovy - concise scripting
def bigOrders = orders.findAll {
    it.amount > 100
}
```

---

### ⚖️ Comparison Table

| Feature          | Java                      | Kotlin                  | Scala              | Groovy          |
| ---------------- | ------------------------- | ----------------------- | ------------------ | --------------- |
| Null safety      | No (Optional workaround)  | Yes (compiler-enforced) | Option[T]          | No              |
| Data classes     | Records (Java 16+)        | `data class`            | `case class`       | Dynamic         |
| Async model      | Virtual threads (Java 21) | Coroutines + VT         | Akka / ZIO         | GPars           |
| Type system      | Strong, simple            | Strong, pragmatic       | Strong, advanced   | Optional typing |
| Compilation      | Fast                      | Medium (K2: fast)       | Slow (incremental) | Fast            |
| Spring support   | Full                      | Full                    | Limited            | Limited         |
| Android          | Legacy (Kotlin preferred) | First-class             | No                 | No              |
| Big data (Spark) | Supported                 | Supported               | First-class        | No              |
| Build scripts    | Ant/Maven/Gradle          | Kotlin DSL              | SBT                | Groovy DSL      |
| Best domain      | Enterprise, anything      | Android, Spring         | Data, functional   | Gradle, Jenkins |

---

### ⚠️ Common Misconceptions

| Misconception                                           | Reality                                                                                                                                                                                    |
| ------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| "Kotlin will replace Java"                              | Kotlin and Java coexist on the JVM. Spring Boot supports both; most large codebases mix them. New code trends to Kotlin; old code stays Java.                                              |
| "Scala is better for everything functional"             | Scala's advanced type system is powerful for library authors. For application code, Java Streams + lambdas + records achieve most functional patterns without Scala's complexity overhead. |
| "Groovy is just for scripts"                            | Groovy powers Gradle (the most popular Java build tool), Grails, and Jenkins Pipelines. It is production-grade for DSLs and dynamic configuration.                                         |
| "Performance differs across JVM languages"              | All compile to JVM bytecode. Runtime performance is nearly identical for equivalent code. Differences come from library choices (Akka vs virtual threads) not language.                    |
| "Kotlin Coroutines make Java Virtual Threads redundant" | They solve the same I/O concurrency problem differently. Virtual threads (Java 21) are JVM-native; coroutines are a library model. Both can coexist; Spring Boot 3 supports both.          |

---

### 🚨 Failure Modes & Diagnosis

**Mode 1: Kotlin-Java interop null safety gap causes NPE**

**Symptom:** Kotlin code calls a Java library method; gets `NullPointerException` at runtime despite Kotlin's null-safety checks.

**Root Cause:** Java methods without `@NotNull`/`@Nullable` annotations return "platform types" in Kotlin (type `T!`). Kotlin treats them as non-null without a compiler guarantee. If the Java method returns `null`, Kotlin code throws NPE at the assignment point.

**Diagnostic:**

```kotlin
// BAD: Java method without annotation
// returns platform type - NPE possible
val result: String = javaLibrary.getValue()
// ← NPE if getValue() returns null

// GOOD: explicit nullable handling
val result: String? = javaLibrary.getValue()
val safe = result ?: "default"
```

**Fix:** Always use `?` for return types from unannotated Java methods. Add `@NotNull`/`@Nullable` to Java APIs where possible.

**Prevention:** Enable Kotlin strict mode (`-Xjsr305=strict`); use IntelliJ's "Infer Annotations" to add nullability annotations to Java APIs.

---

**Mode 2: Scala binary incompatibility breaks dependency resolution**

**Symptom:** `sbt compile` fails with `evicted: org.typelevel:cats-core_2.13 ... incompatible cross version`.

**Root Cause:** Scala libraries encode Scala version in artifact name (`cats-core_2.12`, `cats-core_2.13`, `cats-core_3`). All Scala libraries in a project must match the same Scala binary version.

**Diagnostic:**

```bash
# In sbt
sbt "evicted"  # shows all version conflicts
# Find the library requiring wrong Scala version:
sbt "dependencyTree" | grep "_2.12"
```

**Fix:** Align all Scala dependencies to same cross-version. Check library support matrix before adding any Scala library.

**Prevention:** Define Scala version once in `build.sbt`: `scalaVersion := "2.13.12"`. Use `%%` instead of `%` for Scala artifact resolution: `"org.typelevel" %% "cats-core" % "2.10.0"`.

---

**Mode 3: Groovy dynamic typing allows injection through script execution (Security)**

**Symptom:** Application executes Groovy scripts provided by users (scripting engine); malicious script calls `Runtime.exec("rm -rf /")`.

**Root Cause:** Groovy's `GroovyShell.evaluate()` and `ScriptEngine` execute arbitrary Groovy code with full JVM access unless a security sandbox is applied.

**Diagnostic:**

```groovy
// DANGEROUS: user-provided script
def shell = new GroovyShell()
shell.evaluate(userProvidedScript)
// userProvidedScript can call ANY Java API
```

**Fix:** Use `SecureASTCustomizer` to restrict allowed AST nodes; run scripts in a `SecurityManager` context (deprecated Java 17+; use OSGi or dedicated subprocess instead).

**Prevention:** Never execute user-provided Groovy/scripts in the application JVM. Use a subprocess with minimal permissions or a dedicated sandboxed runtime. Prefer a limited expression language (SpEL with property-only access) over full Groovy for user-configurable rules.

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**

- [[JLG-001 - What Is Java - History and Philosophy]] - the Java platform origin
- [[JLG-002 - The Java Ecosystem Map (SE, EE, ME, Android)]] - platform editions

**Builds On This (learn these next):**

- [[JLG-077 - Java in Polyglot Architecture]] - mixing JVM languages in one system
- [[JLG-084 - Java Ecosystem Selection Framework]] - systematic language selection

**Alternatives / Comparisons:**

- Go - not JVM-based; better for infrastructure tools and simpler concurrency models
- Python - different runtime entirely; preferred for data science and scripting
- .NET / C# - Microsoft ecosystem alternative with similar managed runtime characteristics

---

### 📌 Quick Reference Card

```
+----------------------------------------------------------+
| WHAT IT IS    | Four primary JVM languages: Java, Kotlin,|
|               | Scala, Groovy - each with distinct goals |
| PROBLEM       | Choosing the wrong JVM language creates  |
|               | complexity premium without benefit       |
| KEY INSIGHT   | Domain determines language: Android=Kotlin|
|               | Spark=Scala; build scripts=Groovy DSL    |
| USE WHEN      | Evaluating language for new project,     |
|               | justifying JVM language choice           |
| AVOID WHEN    | Choosing purely on language ergonomics - |
|               | framework ecosystem governs              |
| TRADE-OFF     | Kotlin: null-safety + conciseness vs     |
|               | team ramp-up; Scala: power vs complexity |
| ONE-LINER     | All compile to same bytecode; domain and |
|               | framework determine the right choice     |
| NEXT EXPLORE  | JLG-077 (Polyglot),                      |
|               | JLG-084 (Selection Framework)            |
+----------------------------------------------------------+
```

**If you remember only 3 things:**

1. All JVM languages produce the same bytecode - performance, GC tuning, and monitoring are identical at runtime
2. Kotlin is the go-to Java successor for new Android and Spring Boot code; it solves null safety and verbosity without Scala's complexity
3. The framework chooses the language: Spark → Scala; Gradle build scripts → Kotlin DSL; Android → Kotlin; Spring Boot → Java or Kotlin

**Interview one-liner:** "The four main JVM languages - Java, Kotlin, Scala, Groovy - compile to the same bytecode and share the JVM runtime; Kotlin improves null safety and conciseness over Java; Scala adds advanced functional type theory; Groovy enables DSLs; the choice is governed by domain and framework, not subjective preference."

---

### 💎 Transferable Wisdom

**Reusable Engineering Principle:** _The right tool for a domain is determined by the domain's ecosystem, not the tool's intrinsic features._ Scala is technically more expressive than Java for functional programming - but in a Spring Boot microservice, Scala's expressiveness adds zero value while its compilation cost and hiring difficulty add real costs. The principle: choose the language that is native to your framework's ecosystem.

**Where else this pattern appears:**

- **SQL dialects** - PostgreSQL extensions (JSONB, CTE) are more expressive than standard SQL; but if the ORM's query language is JPQL (Java Persistence Query Language), the extension expressiveness is irrelevant
- **Shell scripting (bash vs Python vs Ruby)** - Python is more expressive than bash; but for a one-line `cron` task that pipes `grep` and `awk`, bash is the right tool
- **CSS preprocessors (Sass vs PostCSS)** - Sass has more features; PostCSS is native to the CSS ecosystem; the build toolchain determines the choice

---

### 💡 The Surprising Truth

Scala's biggest technical success is also the cause of its declining adoption: Apache Spark. Spark 1.0 was written in Scala and offered a Scala API far richer than the Java API. This drove the entire big data engineering community to Scala, building a generation of Scala expertise. But Spark 2.0's Python (PySpark) API reached feature parity, and Python's enormous data science community moved to PySpark. The result: Scala's primary commercial driver (Spark) is now primarily used via Python. Scala retains dominance in the most performance-sensitive Spark jobs and in library authorship, but the mass-market Spark developer is now a Python developer. Scala "won" Spark technically but lost it commercially to Python's network effects.

---

### 🧠 Think About This Before We Continue

**Question 1 (C - Design Trade-off):** Kotlin was designed for 100% Java interoperability - you can call any Java method from Kotlin and extend any Java class. This is Kotlin's primary adoption advantage. But this interoperability requires Kotlin to adopt Java's platform types (non-null-annotated Java methods return `T!` in Kotlin). Describe the fundamental tension between "full Java interoperability" and "true null safety" - can both coexist?

_Hint:_ True null safety requires that every value's nullability is known at compile time. Java's lack of nullability annotations means this is impossible for Java interop boundaries. Research how Kotlin's `@NotNull`/`@Nullable` annotation processing and platform types resolve this tension in practice.

**Question 2 (B - Scale):** A company has a 1.5M-line Scala 2.12 codebase. Scala 3 (Dotty) has been stable for 2 years with significant improvements. Most of the team's 30 engineers are Scala experts. Describe the migration risk assessment: what are the binary compatibility concerns, macro migration challenges, implicit→given/using migration scope, and build time implications of migrating from Scala 2.12 to Scala 3?

_Hint:_ Scala 2 macros do not compile under Scala 3 (different macro system). All macro-using libraries (shapeless, circe) need Scala 3 ports. Scala 2.13 is an intermediate step. The Scala 3 migration guide and `scala-migrate` tool are starting points.

**Question 3 (D - Root Cause):** A Kotlin coroutine-based service has been running well for 6 months. After a dependency upgrade (Spring Boot 2.7 → 3.1), coroutine-based tests start hanging indefinitely in the CI pipeline but pass locally. Root cause analysis: what interaction between Spring's test `ApplicationContext` lifecycle, Kotlin Coroutine's test dispatcher, and Spring Boot 3's virtual thread integration might cause this, and what diagnostic steps would you take?

_Hint:_ Spring Boot 3 enables virtual threads by default. Kotlin's `runBlocking` in tests may interact poorly with virtual thread schedulers. Research `Dispatchers.Unconfined` vs `Dispatchers.IO` in test contexts, and Spring's `@TestConfiguration` for coroutine dispatcher overrides.
