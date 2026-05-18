---
id: JLG-002
title: "The Java Ecosystem Map (SE, EE, ME, Android)"
category: Java Language
tier: tier-3-java
folder: JLG-java-language
difficulty: ★☆☆
depends_on: JLG-001
used_by: JLG-003, JLG-004, JLG-084
related: JLG-005, JLG-075, SPR-002
tags:
  - java
  - foundational
  - mental-model
  - architecture
status: complete
version: 2
layout: default
parent: "Java Language"
grand_parent: "Technical Mastery"
nav_order: 2
permalink: /technical-mastery/jlg/the-java-ecosystem-map-se-ee-me-android/
---

⚡ TL;DR - The Java platform splits into four editions - SE (standard library), EE/Jakarta (enterprise services), ME (embedded), and Android (mobile) - each targeting a distinct deployment context with different APIs.

| Field          | Value                                                                                                                                                         |
| -------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Depends on** | [[JLG-001 - What Is Java - History and Philosophy]]                                                                                                           |
| **Used by**    | [[JLG-003 - Why Java Is Still Dominant]], [[JLG-004 - Java vs Other JVM Languages (Kotlin, Scala, Groovy)]], [[JLG-084 - Java Ecosystem Selection Framework]] |
| **Related**    | [[JLG-005 - Java Versioning and LTS Release Strategy]], [[JLG-075 - Java Modularity Strategy (JPMS)]], [[SPR-002 - The Spring Ecosystem Map]]                 |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**

A Java developer in 1998 needs to write a web application. Which APIs do they use? Are `Servlet` and `JDBC` part of the JDK? What about XML parsing? Message queues? Transaction management? Without an organised platform map, every project team must discover which APIs exist, where they live, and which JVM ships them.

**THE BREAKING POINT:**

Sun Microsystems' Java success created a proliferation problem: thousands of Java APIs developed by Sun, IBM, BEA, Oracle, and the open-source community, with no clear taxonomy. Developers did not know if an API was "standard," "enterprise," or "vendor-specific." The platform needed a formal map.

**THE INVENTION MOMENT:**

Sun formalised the Java editions in 1998-1999, creating explicit tiers: Java 2 Standard Edition (J2SE), Java 2 Enterprise Edition (J2EE), and Java 2 Micro Edition (J2ME). Each edition defined a specific API surface for a specific deployment context. The structure was not purely technical - it was a product and licensing structure that enabled Sun to charge for enterprise server licences.

**EVOLUTION:**

- **1998:** J2SE 1.2, J2EE 1.2, J2ME 1.0 - the three editions formalised
- **2006:** Java SE 6, Java EE 5 - naming simplified (dropped "2")
- **2007:** Android 1.0 - Java language + custom Dalvik VM (later ART), no J2ME
- **2010:** Oracle acquires Sun; stewardship of Java platform changes
- **2017:** Java SE 9 module system (JPMS) - modularises Java SE itself
- **2017:** Java EE transferred to Eclipse Foundation; renamed **Jakarta EE**
- **2019:** Jakarta EE 8 - first release under new governance
- **2022:** Jakarta EE 10 - modern APIs; `javax.*` namespace → `jakarta.*`
- **2023:** GraalVM SDK - a new platform component for polyglot and native

---

### 📘 Textbook Definition

The **Java platform** is organised into four primary editions:

- **Java SE (Standard Edition):** The core language and foundational class libraries (`java.lang`, `java.util`, `java.io`, `java.net`, `java.nio`, `java.time`, `java.util.stream`). All Java development builds on SE.
- **Jakarta EE (formerly Java EE / J2EE):** Specifications for enterprise services built on top of Java SE - Servlets, CDI, JPA, JMS, EJB, JAX-RS, Bean Validation. Implemented by application servers (WildFly, Payara, GlassFish) and lightweight runtimes (Spring, Quarkus).
- **Java ME (Micro Edition):** A subset of Java SE with APIs for constrained devices (smart cards, IoT microcontrollers). Largely superseded by Android for mobile and modern IoT frameworks.
- **Android:** Java language (plus Kotlin) with Android SDK APIs (`android.*`), backed by the ART runtime (not HotSpot JVM).

---

### ⏱️ Understand It in 30 Seconds

**One line:** Java SE is the foundation; Jakarta EE adds enterprise services on top; Android uses the Java language with its own runtime; ME targets constrained devices.

> The Java ecosystem is like a city zoning map. Java SE is the city infrastructure - roads, electricity, water (the JVM and core libraries). Jakarta EE is the commercial district - banks, government offices, enterprise services. Android is the suburbs with its own transit system (ART runtime). Java ME is the rural area with minimal services for resource-constrained environments.

**One insight:** "Java EE" and "Spring" are complementary, not competitors. Spring implements Jakarta EE specifications (JPA, Servlets, CDI-like patterns) and adds its own layer. Knowing the edition map helps you understand which Spring features are standard specs versus Spring-specific innovations.

---

### 🔩 First Principles Explanation

**CORE INVARIANTS:**

1. Java SE is the universal foundation - every Java edition builds on SE
2. Jakarta EE is a specification, not an implementation - the APIs define contracts; application servers implement them
3. Android uses Java language syntax and Java SE core classes but its runtime (ART) is not a JVM
4. ME and SE are separate download packages - ME does not include SE; SE does not include ME
5. JPMS (Java 9+) modularises Java SE itself into named modules, enabling smaller runtime images

**DERIVED DESIGN:**

From invariant 1 → any Jakarta EE code also has full access to Java SE APIs.
From invariant 2 → Spring Boot + Hibernate is a valid Jakarta EE implementation without a traditional application server. The specification's value is in the API contract, not in the server.
From invariant 3 → Android developers use Java syntax and many `java.util.*` APIs, but Android-specific APIs (`android.app.Activity`) have no equivalent in Java SE. This is why Android code cannot run on a server JVM.

**THE TRADE-OFFS:**

**Gain:** Clear API taxonomy; specifications enable multiple competing implementations; SE baseline ensures portability.

**Cost:** Jakarta EE specifications lag behind the industry (2-3 year cycle); the `javax` → `jakarta` namespace migration in Jakarta EE 9 broke every existing application; Android's divergence from standard JVM creates fragmentation.

**ESSENTIAL vs ACCIDENTAL COMPLEXITY:**

**Essential:** Enterprise software genuinely requires transaction management, connection pooling, message queues, and security - these belong in a separate tier from the standard library.

**Accidental:** The `javax` → `jakarta` namespace rename (Java EE → Jakarta EE) was a governance decision that caused a massive industry-wide migration effort with no functional benefit to developers.

---

### 🧪 Thought Experiment

**SETUP:** You are building three applications: (A) a REST API for an e-commerce platform, (B) a fitness tracking app for iPhone and Android, (C) firmware for an industrial sensor with 512KB RAM.

**WITHOUT the edition map:**

You don't know which APIs are available. For the Android app, you try to use `java.awt.Graphics` for UI - compile error. For the firmware, you try to load Hibernate - OutOfMemoryError at startup. For the REST API, you're unsure whether to use Java SE's built-in `com.sun.httpserver.HttpServer` or a Jakarta EE container. Hours lost to discovery.

**WITH the edition map:**

- Application A → Java SE + Jakarta EE (Servlet/JAX-RS); deploy to Spring Boot embedded Tomcat
- Application B → Android SDK (Java/Kotlin); no Swing/AWT; use Android lifecycle APIs
- Application C → Java ME or C (512KB too small even for ME); consider MicroProfile for IoT with sufficient RAM

**THE INSIGHT:**

The edition map is a prerequisite for selecting the correct API set. Developers without this map waste hours attempting to use APIs from the wrong edition.

---

### 🧠 Mental Model / Analogy

> The Java ecosystem editions are like professional certifications layered on a common education foundation. Java SE is the undergraduate degree (everyone needs it). Jakarta EE is the MBA (enterprise business skills built on the degree). Android is a trade school certificate (uses the same foundational skills but specialises in mobile, with its own unique practicum). Java ME is the specialised vocational training for working in constrained environments.

**Element mapping:**

- Undergraduate degree (core knowledge) → Java SE standard library
- MBA programs → Jakarta EE application server implementations
- Trade school for mobile → Android SDK + ART
- Specialised constrained environment training → Java ME profile
- Common academic prerequisites → JVM bytecode spec (shared foundation)

Where this analogy breaks down: unlike academic degrees, you don't need Jakarta EE to use Java SE. They are additive, not sequential. Spring Boot uses Java SE directly without requiring a Jakarta EE application server.

---

### 📶 Gradual Depth - Four Levels

**Level 1 - What it is (anyone can understand):**
Java comes in different flavours for different uses. The standard version (Java SE) is for desktop and server programs. The enterprise version (Jakarta EE) adds extra tools for large business systems. Android uses Java syntax for phones. And there's a tiny version (Java ME) for very small devices.

**Level 2 - How to use it (junior developer):**
When someone says "Java developer," they typically mean Java SE + some Jakarta EE specs (via Spring Boot or Quarkus). Download JDK (Java SE). Use Maven/Gradle. Spring Boot includes embedded Tomcat (Servlet spec) and Hibernate (JPA spec) - you get enterprise features without installing a full application server.

**Level 3 - How it works (mid-level engineer):**
Java SE ships as `java.base`, `java.sql`, `java.net`, `java.logging` modules (Java 9+ JPMS). Jakarta EE adds `jakarta.servlet`, `jakarta.persistence`, `jakarta.ws.rs` - these are specifications with multiple implementations. Hibernate implements JPA. Tomcat/Undertow implement Servlet. RESTEasy/Jersey implement JAX-RS. Spring Boot pulls these implementations together via auto-configuration. When you add `spring-boot-starter-web`, you get Tomcat (Servlet) + Spring MVC (uses Servlet) + Jackson (JSON) automatically.

**Level 4 - Why it was designed this way (senior/staff):**
The specification-over-implementation approach of Jakarta EE was designed to prevent vendor lock-in after the J2EE era of vendor-proprietary extensions. By standardising API contracts (JPA, Servlets), the specification forces implementations to be interchangeable. In practice, Hibernate-specific features (`@Formula`, `@NaturalId`) are used everywhere, reintroducing lock-in - but at the ORM layer, not the application server layer. The governance transfer from Oracle to Eclipse Foundation (2017) was driven by Oracle's slow-walking the specification process; the Eclipse Foundation's open, community-driven model has accelerated Jakarta EE releases significantly.

**Expert Thinking Cues:**

- `javax.*` = Java EE (Oracle); `jakarta.*` = Jakarta EE (Eclipse) - version determines which namespace
- Spring 6 / Spring Boot 3 requires Jakarta EE 9+ (`jakarta.*` namespace) - this broke all legacy Spring 5 apps
- MicroProfile is a community initiative extending Jakarta EE with cloud-native specs (Health, Metrics, OpenAPI) - used by Quarkus, Helidon, OpenLiberty

---

### ⚙️ How It Works (Mechanism)

```
Java Platform Editions Map:

Java SE (Foundation)
├── java.lang (Object, String, Thread...)
├── java.util (Collections, streams...)
├── java.io / java.nio (File, channels...)
├── java.net (sockets, HTTP client...)
└── java.time (LocalDate, ZonedDateTime...)

Jakarta EE (Built on SE)
├── jakarta.servlet (HTTP request/response)
├── jakarta.persistence (JPA - ORM)
├── jakarta.transaction (JTA - transactions)
├── jakarta.ws.rs (JAX-RS - REST APIs)
├── jakarta.ejb (EJB - legacy enterprise)
├── jakarta.inject (CDI - dependency injection)
└── jakarta.validation (Bean validation)

Android SDK (Java language, own runtime)
├── android.app (Activity, Fragment...)
├── android.view (UI components)
├── android.os (Looper, Handler...)
└── java.* (subset of SE core)

Java ME (Subset of SE, constrained)
├── CLDC (Connected Limited Device Config)
└── CDC (Connected Device Config)
```

---

### 🔄 The Complete Picture - End-to-End Flow

**NORMAL FLOW - Spring Boot REST API:**

```
[Developer creates Spring Boot project]
     |
     ├─ build.gradle: spring-boot-starter-web
     |    ← YOU ARE HERE (edition selection)
     |
     ├─ spring-boot-starter-web includes:
     |    ├─ Spring MVC (uses jakarta.servlet)
     |    ├─ Tomcat (implements jakarta.servlet)
     |    └─ Jackson (JSON serialization)
     |
     ├─ All built on Java SE (JDK 21)
     |
[Application serves HTTP requests via Tomcat Servlet API]
```

**FAILURE PATH:**

- Using `javax.servlet.*` with Spring Boot 3 → `ClassNotFoundException` (Spring Boot 3 requires `jakarta.servlet.*`)
- Importing `android.widget.TextView` in a Java SE project → compile error (Android SDK not on classpath)
- Loading full Hibernate ORM on Java ME → `OutOfMemoryError` (ME heap too small)

**WHAT CHANGES AT SCALE:**

Microservices architectures use only Java SE + a small subset of Jakarta EE APIs (Servlets/JAX-RS). Full Jakarta EE application servers (WildFly, Payara) are increasingly rare in new projects. Spring Boot (embedded server, selected specs) is the dominant enterprise Java deployment model.

---

### 💻 Code Example

**Jakarta EE JAX-RS endpoint (spec code):**

```java
// Standard Jakarta EE - works on any JAX-RS impl
// (Jersey, RESTEasy, CXF, Spring MVC)
import jakarta.ws.rs.GET;
import jakarta.ws.rs.Path;
import jakarta.ws.rs.PathParam;
import jakarta.ws.rs.Produces;
import jakarta.ws.rs.core.MediaType;

@Path("/users")
public class UserResource {
    @GET
    @Path("/{id}")
    @Produces(MediaType.APPLICATION_JSON)
    public User getUser(@PathParam("id") Long id) {
        return userRepository.findById(id);
    }
}
```

**Spring MVC equivalent (Spring-specific but uses SE):**

```java
// Spring MVC - Spring-specific annotations
// but deploys via Jakarta Servlet spec
import org.springframework.web.bind.annotation.*;

@RestController
@RequestMapping("/users")
public class UserController {
    @GetMapping("/{id}")
    public User getUser(@PathVariable Long id) {
        return userRepository.findById(id)
            .orElseThrow();
    }
}
```

**Detecting which edition APIs are available:**

```java
// Check if running on full JDK vs JRE subset
boolean hasJaxRs;
try {
    Class.forName(
        "jakarta.ws.rs.core.Application");
    hasJaxRs = true;
} catch (ClassNotFoundException e) {
    hasJaxRs = false;
}
System.out.println("Jakarta EE: " + hasJaxRs);
```

---

### ⚖️ Comparison Table

| Edition     | Target                   | API Set                       | Runtime                 | Common Use                         |
| ----------- | ------------------------ | ----------------------------- | ----------------------- | ---------------------------------- |
| Java SE     | Desktop, server, tooling | Core JDK (`java.*`)           | HotSpot/OpenJ9/GraalVM  | Spring Boot, CLI tools, batch      |
| Jakarta EE  | Enterprise server        | SE + enterprise (`jakarta.*`) | App servers or embedded | Legacy enterprise, Quarkus         |
| Android     | Mobile                   | Java language + `android.*`   | ART (not JVM)           | Android apps                       |
| Java ME     | Embedded/IoT             | Subset of SE                  | KVM or custom           | Smart cards, industrial IoT        |
| GraalVM SDK | Polyglot, native         | SE + GraalVM APIs             | GraalVM                 | Native images, embedding Python/JS |

---

### ⚠️ Common Misconceptions

| Misconception                                    | Reality                                                                                                                                                                 |
| ------------------------------------------------ | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| "Spring Boot is a Jakarta EE implementation"     | Spring Boot uses some Jakarta EE specs (Servlet, JPA, Validation) but adds Spring-specific APIs. It is not a Jakarta EE certified runtime.                              |
| "Android is Java"                                | Android uses Java language syntax and some `java.*` classes, but runs on ART (not a JVM). APIs differ completely: no `javax.swing`, no Jakarta EE, no `java.awt`.       |
| "Jakarta EE requires a heavy application server" | Modern Jakarta EE runs on lightweight embedded runtimes (Quarkus, Helidon, OpenLiberty). Spring Boot effectively implements many EE specs without a traditional server. |
| "`javax.*` and `jakarta.*` are the same"         | `javax.*` is Oracle's namespace (Java EE, used in Spring 5 and below). `jakarta.*` is Eclipse's namespace (Jakarta EE 9+, required by Spring 6+). Not interchangeable.  |
| "Java ME is still relevant for IoT"              | Java ME is largely superseded. Modern IoT uses MicroProfile (for capable devices) or C/Rust (for constrained devices). Java ME smart card profiles remain active.       |

---

### 🚨 Failure Modes & Diagnosis

**Mode 1: `javax` vs `jakarta` namespace confusion after Spring Boot 3 migration**

**Symptom:** After upgrading from Spring Boot 2 to Spring Boot 3, compilation fails with `cannot find symbol: class HttpServletRequest` or `package javax.servlet does not exist`.

**Root Cause:** Spring Boot 3 requires Jakarta EE 9+ which uses `jakarta.servlet.*`. All imports of `javax.servlet.*` must be changed to `jakarta.servlet.*`.

**Diagnostic:**

```bash
# Find all javax.* imports that need migration
grep -r "import javax\." src/ --include="*.java" \
  | grep -v "javax.crypto\|javax.net\|javax.xml"
  # Note: javax.crypto, javax.net are Java SE
  # (stay as javax); only Jakarta EE specs moved
```

**Fix:** Run OpenRewrite migration recipe: `org.openrewrite.java.migrate.jakarta.JavaxMigrationToJakarta` to auto-migrate all imports.

**Prevention:** Pin Spring Boot version in parent POM; upgrade in a dedicated sprint with full regression testing.

---

**Mode 2: Android code attempted on server JVM**

**Symptom:** A developer copies Android utility class to a backend service; compilation fails: `cannot find symbol: class Context`.

**Root Cause:** `android.content.Context` is an Android SDK class; it does not exist in Java SE or Jakarta EE classpaths.

**Diagnostic:**

```bash
# List all android.* imports
grep -r "import android\." src/ --include="*.java"
# All should be removed from non-Android code
```

**Fix:** Extract the logic from the Android utility class and rewrite using Java SE / Jakarta EE equivalents. Android utility code cannot be shared with server-side Java as-is.

**Prevention:** Code module structure: `core-logic` module (Java SE only), `android-module` (Android SDK), `server-module` (Spring Boot). Never let `android.*` imports into non-Android modules.

---

**Mode 3: Outdated Jakarta EE spec exposes known vulnerability (Security)**

**Symptom:** Security scan flags `CVE-2021-44228` (Log4Shell) - application uses Log4j 2.x via a Jakarta EE component.

**Root Cause:** Application server bundles an old version of Log4j; Jakarta EE spec does not mandate logging framework version; vendor-bundled version is outdated.

**Diagnostic:**

```bash
# Find all log4j jars in application server
find /opt/wildfly -name "log4j*.jar"
find ~/.m2 -name "log4j*.jar" | grep "2\.[0-9]"
# Check for versions < 2.17.1
```

**Fix:** Upgrade Log4j to 2.17.1+. Set system property: `-Dlog4j2.formatMsgNoLookups=true` as immediate mitigation.

**Prevention:** Add dependency vulnerability scanning (Snyk, OWASP Dependency-Check) to CI pipeline for all Jakarta EE and Spring Boot projects.

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**

- [[JLG-001 - What Is Java - History and Philosophy]] - the Java platform origin

**Builds On This (learn these next):**

- [[JLG-003 - Why Java Is Still Dominant]] - why the ecosystem remains relevant
- [[JLG-075 - Java Modularity Strategy (JPMS)]] - Java SE modularisation
- [[SPR-002 - The Spring Ecosystem Map]] - the Spring portfolio built on this platform

**Alternatives / Comparisons:**

- [[JLG-004 - Java vs Other JVM Languages (Kotlin, Scala, Groovy)]] - other languages on the JVM platform
- .NET Core / CLR - Microsoft's competing managed runtime platform
- Node.js - JavaScript runtime as an alternative to Java EE for web backends

---

### 📌 Quick Reference Card

```
+----------------------------------------------------------
| WHAT IT IS    | Java's four-edition platform taxonomy:
  |
|               | SE, Jakarta EE, Android, ME
  |
| PROBLEM       | API proliferation confusion - which
  |
|               | APIs are available in which context
  |
| KEY INSIGHT   | SE is the foundation; EE is enterprise
  |
|               | specs on top; Android = own runtime
  |
| USE WHEN      | Selecting APIs, diagnosing class-not-
  |
|               | found, migrating between Java versions
  |
| AVOID WHEN    | N/A - foundational knowledge, always
  |
|               | relevant
  |
| TRADE-OFF     | Specification layer adds portability but
  |
|               | delays adoption of new features
  |
| ONE-LINER     | SE=core; jakarta=enterprise specs;
  |
|               | Android=own runtime; ME=tiny devices
  |
| NEXT EXPLORE  | JLG-003 (Why Java Dominates),
  |
|               | JLG-075 (JPMS Modularity)
  |
+----------------------------------------------------------
```

**If you remember only 3 things:**

1. Java SE is the foundation every Java edition builds on - core JDK, JVM, standard library
2. Jakarta EE is a _specification_ (not an implementation) - Spring Boot, Quarkus, and WildFly all implement parts of it
3. Android uses Java language syntax but its own runtime (ART) - `android.*` APIs never work on server JVMs

**Interview one-liner:** "The Java platform has four editions: Java SE (core JDK and standard library), Jakarta EE (enterprise API specifications for servers), Android (Java language on ART runtime for mobile), and Java ME (constrained device subset); modern enterprise development uses Java SE plus selected Jakarta EE specs implemented via Spring Boot or Quarkus."

---

### 💎 Transferable Wisdom

**Reusable Engineering Principle:** _Separate specification from implementation to enable multiple competing implementations of the same API contract._ The value of specifications is that they allow vendor competition (multiple JPA implementations, multiple Servlet containers) while preserving application portability. This pattern appears wherever an industry wants standards without monopoly.

**Where else this pattern appears:**

- **SQL standard** - ISO SQL specifies the language; PostgreSQL, MySQL, Oracle implement it; application code is theoretically portable (within standard SQL)
- **OpenAPI specification** - API contracts defined in YAML; code generators, gateways, and validators implement them
- **Kubernetes CRI (Container Runtime Interface)** - specification for how Kubernetes calls container runtimes; Docker, containerd, cri-o all implement it

---

### 💡 The Surprising Truth

Java EE (now Jakarta EE) was originally created partly as a business strategy, not just a technical one. Sun Microsystems saw that IBM, BEA, and Oracle were making billions selling enterprise application servers (WebSphere, WebLogic, BEA WebLogic). By creating the Java EE specification, Sun established itself as the standards authority - companies had to implement Sun's specs to call their server "Java EE certified." This gave Sun enormous influence over the enterprise market without needing to sell servers itself. When Oracle acquired Sun for $7.4 billion in 2010, the Java EE specification became one of the primary strategic assets in the deal. The subsequent slow-walking of Java EE development by Oracle was widely attributed to Oracle's preference for customers to buy commercial Oracle application server licences rather than competing open-source implementations.

---

### 🧠 Think About This Before We Continue

**Question 1 (C - Design Trade-off):** Jakarta EE separates specification from implementation, allowing Hibernate (JPA), Tomcat (Servlet), and Jersey (JAX-RS) to coexist. However, real applications use Hibernate-specific annotations (not in the JPA spec) for performance. Does the specification abstraction provide genuine portability in practice, or is it theoretical?

_Hint:_ Count how many JPA-standard annotations vs Hibernate-specific annotations a typical Spring Boot application uses. Consider what "porting" to EclipseLink would cost.

**Question 2 (A - System Interaction):** A Spring Boot 2 application is being migrated to Spring Boot 3. The codebase has 200 classes with `javax.servlet.*`, `javax.persistence.*`, and `javax.validation.*` imports. The migration must not break the build. Describe the migration strategy, including which `javax.*` packages become `jakarta.*` and which remain `javax.*`.

_Hint:_ Java SE's own APIs (`javax.crypto`, `javax.net.ssl`, `javax.xml.crypto`) were NOT renamed to `jakarta.*` - they are in Java SE, not Jakarta EE. Only the Jakarta EE specs (servlet, persistence, validation, inject, ws.rs) moved to `jakarta.*`.

**Question 3 (E - First Principles):** Android's ART runtime is not a JVM, yet Android developers write Java code. From first principles, explain why ART-compiled Android apps cannot run on a desktop JVM, and why most pure Java SE library code (like Gson, Retrofit) CAN be used on Android despite the different runtime.

_Hint:_ The compilation target is different (ART uses dex bytecode, not JVM bytecode). Pure Java SE code that uses only `java.lang`, `java.util` APIs is available on Android because Google re-implemented those packages for the Android runtime. Libraries that use `javax.swing` or JVM-specific APIs will fail.
