---
id: SPR-004
title: "Spring vs Jakarta EE vs Micronaut vs Quarkus"
category: Spring Core
tier: tier-3-java
folder: SPR-spring-core
difficulty: ★☆☆
depends_on: SPR-001, SPR-002, SPR-003
used_by:
related: SPR-016, SPR-017, SPR-018
tags:
  - spring
  - java
  - foundational
  - tradeoff
  - architecture
status: complete
version: 2
layout: default
parent: "Spring Core"
grand_parent: "Technical Dictionary"
nav_order: 4
permalink: /spr/spring-vs-jakarta-ee-vs-micronaut-vs-quarkus/
---

# SPR-004 - Spring vs Jakarta EE vs Micronaut vs Quarkus

⚡ TL;DR - Spring dominates in ecosystem breadth; Jakarta EE provides vendor-neutral standards; Micronaut and Quarkus win on startup time and memory via compile-time DI.

| Field          | Value                                                                                                                                                 |
| -------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Depends on** | [[SPR-001 - What Is Spring - History and Philosophy]], [[SPR-002 - The Spring Ecosystem Map]], [[SPR-003 - Why Spring Boot Changed Java Development]] |
| **Used by**    | -                                                                                                                                                     |
| **Related**    | [[SPR-016 - Micronaut Framework]], [[SPR-017 - Micronaut vs Spring Boot]], [[SPR-018 - Quarkus Framework]]                                            |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**

When starting a new Java backend project, the framework choice feels overwhelming. Spring is the market leader but is labelled "heavyweight." Jakarta EE is the official standard but feels fragmented. Micronaut and Quarkus are fast but newer. Without a structured comparison, teams default to familiarity rather than making an informed trade-off for their specific constraints.

**THE BREAKING POINT:**

The rise of containerised microservices (2015-2020) exposed Spring's JVM startup time (2-10 seconds) and memory footprint (200-400 MB) as genuine costs when orchestrating hundreds of service instances. Kubernetes kills and restarts containers frequently - a slow-starting container becomes a reliability problem, not just an inconvenience.

**THE INVENTION MOMENT:**

Micronaut (2018, OCI) and Quarkus (2019, Red Hat) were created specifically to address the startup time and memory footprint problem by shifting IoC from runtime reflection to compile-time annotation processing. This is not a small optimisation - it is a fundamentally different architecture.

**EVOLUTION:**

- **2003-2014:** Spring dominates; Jakarta EE (then Java EE) is the official standard; both use runtime reflection
- **2018:** Micronaut introduces compile-time DI - proves the alternative is viable
- **2019:** Quarkus launches with Kubernetes-native focus and GraalVM native image as first-class target
- **2022:** Spring 6 / Boot 3 responds with AOT compilation and GraalVM native support
- **2024:** All four frameworks support native compilation; difference narrows but compile-time-first still leads

---

### 📘 Textbook Definition

The four major Java application frameworks differ primarily in their **dependency injection model**, **startup performance**, and **ecosystem alignment**:

- **Spring (+ Boot):** Runtime reflection-based IoC; largest ecosystem; most mature production tooling
- **Jakarta EE:** Specification-based standard (CDI, JAX-RS, JPA); multiple vendor implementations (WildFly, Payara, Open Liberty, TomEE)
- **Micronaut:** Compile-time annotation processing for DI; no reflection at runtime; AOT-native by design
- **Quarkus:** Compile-time DI (based on ArC, a CDI subset); Kubernetes-native; GraalVM native image as first-class target; Vert.x-backed reactive model

---

### ⏱️ Understand It in 30 Seconds

**One line:** Choose Spring for ecosystem depth, Jakarta EE for vendor standards, Micronaut/Quarkus for cold-start performance.

> These frameworks are like four car models: Spring is the SUV with every feature; Jakarta EE is the government-standard fleet vehicle; Micronaut and Quarkus are sports cars optimised for zero-to-sixty - but with a smaller boot.

**One insight:** The compile-time vs runtime DI distinction is not academic - it determines whether your service can start in 50ms (native) or 3 seconds (JVM reflection), which matters in autoscaling Kubernetes environments.

---

### 🔩 First Principles Explanation

**CORE INVARIANTS:**

1. All four provide a DI container - the question is _when_ the container is built (compile vs runtime)
2. Runtime reflection DI (Spring, Jakarta EE) can inspect arbitrary code without build tooling changes
3. Compile-time DI (Micronaut, Quarkus, Spring AOT) requires annotation processing at build time
4. Ecosystem breadth is a function of community size and years of library support
5. Native compilation (GraalVM) eliminates JVM warm-up but limits runtime dynamism

**DERIVED DESIGN:**

Runtime reflection → large ecosystem, flexible at cost of startup time and memory.
Compile-time DI → fast starts, low memory, but less runtime flexibility (dynamic class loading, reflection APIs are restricted).
Vendor standard (Jakarta EE) → portability across implementations, but specification lag behind market.

**THE TRADE-OFFS:**

**Gain (Spring):** Largest ecosystem, most Stack Overflow answers, most talent, best Spring Cloud integration.

**Gain (Micronaut/Quarkus):** 50-200ms startup (native), 50-100MB memory (native), no reflection vulnerabilities.

**Cost (Spring JVM):** 2-10s cold start, 200-400MB baseline heap, reflection makes serialisation gadget attacks feasible.

**Cost (compile-time):** Dynamic proxies, runtime code generation, and reflection-based libraries (some ORMs, some serialisers) require workarounds or are unsupported.

**ESSENTIAL vs ACCIDENTAL COMPLEXITY:**

**Essential:** Choosing a DI mechanism has genuine trade-offs in startup, memory, ecosystem, and dynamism.

**Accidental:** The frameworks have converged significantly. Spring Boot 3 + GraalVM native now delivers startup times within 3-5x of Quarkus native; the gap is narrowing with each release.

---

### 🧪 Thought Experiment

**SETUP:** You run a Kubernetes cluster with 50 microservices. Each service is replicated and experiences periodic pod restarts due to node scaling and deployments.

**WHAT HAPPENS with Spring JVM:**

Each new pod takes 5-8 seconds to start and accept traffic. During a rolling deployment of 10 services, Kubernetes must wait for each pod to become healthy before proceeding. A 10-service rolling update takes 1-2 minutes. Load spikes trigger autoscaling, but new pods do not serve traffic for 5-8 seconds, leaving the cluster momentarily undersupplied.

**WHAT HAPPENS with Quarkus/Micronaut native:**

Each pod starts in 50-100ms. Rolling deployments complete in seconds. Autoscaling responds within the same Kubernetes scheduling cycle. Memory per pod is 80MB instead of 350MB, enabling denser packing - effectively 4x more pods per node for the same cost.

**THE INSIGHT:**

For long-running, stable services with rich ecosystem needs, Spring JVM is optimal. For high-churn, autoscaling-intensive, memory-constrained Kubernetes workloads, compile-time native frameworks are not premature optimisation - they are the correct engineering choice.

---

### 🧠 Mental Model / Analogy

> Choosing between these frameworks is like choosing between an interpreted scripting language and a compiled language for a specific task. The interpreted language (Spring/runtime reflection) starts coding immediately and has the most libraries. The compiled language (Micronaut/Quarkus) requires a build step but runs faster with less memory. Neither is universally "better" - context decides.

**Element mapping:**

- Interpreted scripting language → Spring + runtime reflection
- Compiler → annotation processor (Micronaut APT, Quarkus Jandex)
- Runtime → JVM + application startup
- Library ecosystem → Spring ecosystem vs Micronaut ecosystem
- Static typing benefit → compile-time DI validation

Where this analogy breaks down: Spring Boot 3's AOT mode blurs the line by adding a compile-time phase while keeping the full runtime ecosystem.

---

### 📶 Gradual Depth - Four Levels

**Level 1 - What it is (anyone can understand):**
These are four different brands of Java backend framework. Spring is the most popular. Jakarta EE is the official standard. Micronaut and Quarkus start up faster. If you are just starting Java, use Spring - the most learning resources exist for it.

**Level 2 - How to use it (junior developer):**
Spring Boot: `@SpringBootApplication` + starters. Jakarta EE: no Spring; use `@Inject`, JAX-RS `@Path`, `@Stateless` EJBs, deploy to WildFly or Open Liberty. Micronaut: identical annotations to Spring but no `ApplicationContext` startup scan; use `mn` CLI. Quarkus: `quarkus create app` + Panache for JPA; reactive with Mutiny.

**Level 3 - How it works (mid-level engineer):**
Spring: `ClassPathBeanDefinitionScanner` + `BeanPostProcessor` at runtime. Micronaut: `BeanDefinitionProcessor` runs at build time via Java APT; generates `BeanDefinitionClass` source files compiled into the JAR. Quarkus: Jandex indexes annotations at build time; ArC CDI container built from the index; Vert.x event loop for reactive. Jakarta EE: CDI container provided by the application server; beans discovered via `beans.xml` marker.

**Level 4 - Why it was designed this way (senior/staff):**
Micronaut's compile-time DI was a deliberate response to the Lambda cold-start problem. Serverless functions could not tolerate Spring's startup time. Quarkus was designed for OpenShift/Kubernetes at Red Hat's scale, where memory density directly determines cluster cost. Spring's response (AOT + Native) is architecturally additive - they preserved 100% runtime compatibility while adding the compile-time path, a significantly harder engineering problem.

**Expert Thinking Cues:**

- Micronaut's compile-time DI means DI errors surface at build time, not runtime - faster feedback
- Quarkus dev mode (`quarkus dev`) provides hot reload that Micronaut matches but Spring DevTools does differently
- Spring's `@Lazy` beans are incompatible with GraalVM native image without explicit hints

---

### ⚙️ How It Works (Mechanism)

**Runtime DI (Spring):**

```
[JAR on classpath] → startup → ClassPathScanner
→ reads annotations via reflection
→ builds BeanDefinition graph → instantiates beans
Duration: 2-10 seconds; memory: 200-400MB
```

**Compile-time DI (Micronaut):**

```
[Source code] → javac + APT processor
→ generates BeanDefinition*.class files
→ JAR contains pre-built DI metadata
→ startup reads metadata (no reflection scan)
Duration: 50-200ms JVM, 20-50ms native
```

**Compile-time DI (Quarkus):**

```
[Source code] → Quarkus build → Jandex index
→ ArC CDI generates proxy/binding code
→ Augmented JAR built
→ startup bootstraps from augmented metadata
Duration: 50-300ms JVM, 10-50ms native
```

---

### 🔄 The Complete Picture - End-to-End Flow

**NORMAL FLOW:**

```
[Framework Selection Decision]
     |
     ├─ Is startup time < 500ms required?
     |    ├─ YES → Quarkus / Micronaut (native or JVM)
     |    └─ NO → Continue
     |         ← YOU ARE HERE (typical case)
     ├─ Is vendor-neutral spec compliance required?
     |    ├─ YES → Jakarta EE
     |    └─ NO → Continue
     |
     ├─ Need Spring Cloud / Spring Data / Spring AI?
     |    ├─ YES → Spring Boot
     |    └─ NO → Evaluate Micronaut or Quarkus
     |
[Framework chosen → use start.spring.io /
 quarkus.io/start / micronaut.io/launch]
```

**FAILURE PATH:**

- Choosing Spring for a Lambda/FaaS use case → cold start timeout (Lambda default: 15s)
- Choosing Quarkus for a legacy library that uses heavy reflection → native image compatibility failures
- Choosing Jakarta EE without a vetted app server → vendor fragmentation; different behaviours per server

**WHAT CHANGES AT SCALE:**

At Google/Netflix scale, the framework choice is less important than the operational model. Both Spring and Quarkus are run at massive scale in production. The decision shifts from "which framework" to "what are our container density and deployment latency SLOs."

---

### 💻 Code Example

**Same REST endpoint + JPA repository in all four frameworks:**

**Spring Boot:**

```java
@RestController
public class ProductController {
    private final ProductRepository repo;

    public ProductController(ProductRepository repo) {
        this.repo = repo;
    }

    @GetMapping("/products/{id}")
    public Product getProduct(@PathVariable Long id) {
        return repo.findById(id).orElseThrow();
    }
}
// ProductRepository extends JpaRepository<Product, Long>
```

**Micronaut:**

```java
@Controller("/products")
public class ProductController {
    private final ProductRepository repo;

    public ProductController(ProductRepository repo) {
        this.repo = repo;
    }

    @Get("/{id}")
    public Product getProduct(Long id) {
        return repo.findById(id).orElseThrow();
    }
}
// ProductRepository extends CrudRepository<Product, Long>
```

**Quarkus (Panache):**

```java
@Path("/products")
public class ProductResource {

    @GET
    @Path("/{id}")
    public Product getProduct(Long id) {
        return Product.findById(id); // Active Record pattern
    }
}
// Product extends PanacheEntity
```

**Jakarta EE (JAX-RS + CDI):**

```java
@Path("/products")
@ApplicationScoped
public class ProductResource {
    @Inject ProductService service;

    @GET
    @Path("/{id}")
    @Produces(MediaType.APPLICATION_JSON)
    public Response getProduct(@PathParam("id") Long id) {
        return Response.ok(service.find(id)).build();
    }
}
```

---

### ⚖️ Comparison Table

| Dimension            | Spring Boot               | Jakarta EE            | Micronaut                | Quarkus             |
| -------------------- | ------------------------- | --------------------- | ------------------------ | ------------------- |
| DI model             | Runtime reflection        | Runtime (CDI)         | Compile-time             | Compile-time        |
| JVM startup          | 2-10s                     | 10-60s (server)       | 200-500ms                | 100-300ms           |
| Native startup       | 100-300ms                 | Limited               | 20-100ms                 | 10-50ms             |
| JVM memory           | 200-400MB                 | 200-500MB             | 50-150MB                 | 50-150MB            |
| Ecosystem            | Largest                   | Broad (vendor)        | Growing                  | Growing             |
| Cloud vendor support | AWS, GCP, Azure           | Varies                | AWS Lambda optimised     | Red Hat / OpenShift |
| Learning resources   | Most                      | Moderate              | Growing                  | Growing             |
| Reactive model       | Project Reactor / WebFlux | RxJava / MicroProfile | Project Reactor / RxJava | Mutiny / Vert.x     |
| GraalVM native       | Boot 3 (supported)        | Limited               | First-class              | First-class         |

---

### ⚠️ Common Misconceptions

| Misconception                                     | Reality                                                                                                                                                                                |
| ------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| "Spring is too slow for Kubernetes"               | Spring Boot 3 with GraalVM native starts in 100-300ms - comparable to Quarkus. JVM Spring is slow for serverless/Lambda; for long-running containers, startup time is a one-time cost. |
| "Jakarta EE is dead"                              | Jakarta EE 11 (2024) is actively developed. It is the foundation for Quarkus (CDI spec), and major vendors (IBM, Red Hat, Eclipse) continue investing.                                 |
| "Micronaut and Quarkus are the same"              | Different underlying reactive models (Reactor vs Mutiny/Vert.x), different compile tools (APT vs Jandex), different CDI compliance (full vs subset).                                   |
| "Compile-time DI has no trade-offs"               | Dynamic class loading, runtime-generated proxies, and libraries that use reflection internally require explicit GraalVM `reflect-config.json` hints - adding build complexity.         |
| "Choose Quarkus/Micronaut for better performance" | They win on _cold-start_ performance. Throughput and latency of a running JVM Spring app are comparable to a running Quarkus JVM app.                                                  |

---

### 🚨 Failure Modes & Diagnosis

**Mode 1: GraalVM native compilation fails**

**Symptom:** `mvn -Pnative package` fails with `ClassNotFoundException` or missing reflection entries.

**Root Cause:** A library uses reflection or runtime class generation that GraalVM's static analysis cannot discover.

**Diagnostic:**

```bash
# Run in tracing agent mode to auto-discover
java -agentlib:native-image-agent=\
  config-output-dir=src/main/resources/META-INF/native-image \
  -jar app.jar
# Then rebuild with native profile
```

**Fix:** Add generated `reflect-config.json` / `resource-config.json` to the native image configuration.

**Prevention:** Use GraalVM-tested Spring Boot starters; check [reachability metadata repository](https://github.com/oracle/graalvm-reachability-metadata) before adding libraries.

---

**Mode 2: Jakarta EE deployment behaves differently across servers**

**Symptom:** Application works on WildFly; fails on TomEE with `CDIException`.

**Root Cause:** CDI spec has optional features; vendor implementations differ in strictness and extensions.

**Diagnostic:**

```bash
# Check beans.xml discovery mode
cat src/main/webapp/WEB-INF/beans.xml
# annotated = explicit; all = implicit
```

**Fix:** Use `bean-discovery-mode="annotated"` for maximum portability; annotate all CDI beans explicitly.

**Prevention:** Test against multiple Jakarta EE runtimes in CI if portability is a requirement.

---

**Mode 3: Dependency injection security misconfiguration (Security failure mode)**

**Symptom:** A `@RequestScoped` bean in Jakarta EE (or `@Scope("request")` in Spring) is accidentally shared between requests due to scope proxy misconfiguration.

**Root Cause:** Singleton bean holds a direct reference to a narrower-scoped bean without a proxy.

**Diagnostic:**

```bash
# Spring: check bean scope proxy mode
@Scope(value = "request",
       proxyMode = ScopedProxyMode.TARGET_CLASS)
```

**Fix:** Always use `ScopedProxyMode.TARGET_CLASS` for request/session-scoped beans injected into singletons.

**Prevention:** Write multi-threaded integration tests that send concurrent requests and assert request isolation.

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**

- [[SPR-001 - What Is Spring - History and Philosophy]] - the history context for this comparison
- [[SPR-002 - The Spring Ecosystem Map]] - what Spring's ecosystem provides
- [[SPR-019 - IoC (Inversion of Control)]] - the shared concept all four implement differently

**Builds On This (learn these next):**

- [[SPR-016 - Micronaut Framework]] - Micronaut in depth
- [[SPR-017 - Micronaut vs Spring Boot]] - detailed head-to-head
- [[SPR-018 - Quarkus Framework]] - Quarkus in depth

**Alternatives / Comparisons:**

- [[SPR-066 - Spring Native and GraalVM Integration]] - Spring's response to compile-time frameworks
- [[SPR-073 - Spring Boot AOT Compilation]] - AOT in Spring Boot 3
- Vert.x (not in SPR - see DST category) - fully reactive, non-framework toolkit

---

### 📌 Quick Reference Card

```
+----------------------------------------------------------+
| WHAT IT IS    | Decision framework for Java backend choice|
| PROBLEM       | Cold start, memory, ecosystem trade-offs  |
| KEY INSIGHT   | Runtime vs compile-time DI is the axis     |
| USE WHEN      | Starting a new Java backend service       |
| AVOID WHEN    | Mid-project framework switches (high cost) |
| TRADE-OFF     | Ecosystem (Spring) vs cold-start perf      |
|               | (Micronaut/Quarkus)                        |
| ONE-LINER     | Spring=ecosystem, EE=standards,            |
|               | Micronaut/Quarkus=startup                  |
| NEXT EXPLORE  | SPR-016 (Micronaut), SPR-018 (Quarkus)     |
+----------------------------------------------------------+
```

**If you remember only 3 things:**

1. Spring wins on ecosystem breadth and talent pool; Micronaut/Quarkus win on cold-start and memory
2. The fundamental difference is compile-time (Micronaut, Quarkus) vs runtime (Spring, Jakarta EE) DI
3. Spring Boot 3 + GraalVM native closes much of the gap; evaluate your actual SLOs before deciding

**Interview one-liner:** "Spring dominates in ecosystem depth; Micronaut and Quarkus offer compile-time DI for sub-second cold starts; Jakarta EE provides vendor-neutral standards - the choice depends on startup SLO, ecosystem needs, and team expertise."

---

### 💎 Transferable Wisdom

**Reusable Engineering Principle:** _Shift left on cost_ - moving expensive operations from runtime to compile time (DI graph building, annotation scanning, proxy generation) improves production performance at the cost of build complexity. This is the same principle behind ahead-of-time compilation, link-time optimisation, and query plan caching.

**Where else this pattern appears:**

- **TypeScript / Webpack** - type checking and tree-shaking at build time eliminates runtime type errors and dead code
- **GraphQL persisted queries** - query parsing and validation shifted from runtime to build/registration time
- **Database prepared statements** - query compilation at preparation time, not execution time

---

### 💡 The Surprising Truth

Quarkus was not built by a startup trying to disrupt Spring - it was built by Red Hat engineers who maintain the WildFly application server and contributed to Hibernate. They had direct access to the runtime bottlenecks in enterprise Java and used that knowledge to design a system that eliminates them at build time. The irony: the framework that most directly challenges Spring was built by the same community that spent 15 years maintaining the enterprise Java standards that Spring originally challenged. The problem space had come full circle.

---

### 🧠 Think About This Before We Continue

**Question 1 (C - Design Trade-off):** Both Spring Boot 3 (with GraalVM native) and Quarkus support sub-200ms cold starts. Given this convergence, what factors beyond startup time should drive the framework choice in 2025 and beyond?

_Hint:_ Consider developer ecosystem (libraries, training, hiring), operational tooling (Actuator vs Quarkus health), Spring Cloud integration depth, and the cost of migrating existing Spring codebases.

**Question 2 (B - Scale):** At what scale does the per-pod memory saving of Micronaut/Quarkus (e.g., 80MB vs 350MB per pod) translate into meaningful infrastructure cost savings, and when does it become negligible compared to other cost drivers?

_Hint:_ Calculate the cost delta for 10 pods vs 1,000 pods on AWS EC2 or EKS node pricing. Consider that memory savings may allow denser packing, reducing node count.

**Question 3 (E - First Principles):** Jakarta EE's CDI specification defines a portable component model that Quarkus implements (as a subset). If Quarkus uses a CDI subset rather than the full spec, in what ways could this break theoretical Jakarta EE portability, and why did the Quarkus team accept this trade-off?

_Hint:_ Look at which CDI features Quarkus's ArC container omits (e.g., `@Decorator`, certain interceptor chains) and how this affects the compile-time feasibility of the container.
