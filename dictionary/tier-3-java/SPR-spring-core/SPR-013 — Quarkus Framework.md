---
layout: default
title: "Quarkus Framework"
parent: "Spring Core"
nav_order: 13
permalink: /spring/quarkus-framework/
number: "SPR-013"
category: Spring Core
difficulty: ★★★
depends_on: Spring Boot, Dependency Injection, GraalVM Native Image
used_by: Microservices, Containers, Cloud — AWS
related: Micronaut Framework, Spring Boot, GraalVM
tags:
  - java
  - jvm
  - microservices
  - advanced
  - performance
---

# SPR-013 — Quarkus Framework

⚡ TL;DR — Quarkus is a Kubernetes-native Java framework that moves as much work as possible to build time, delivering native-image-first, sub-50ms startup for cloud-native workloads.

| Field | Value |
|---|---|
| **Depends on** | Spring Boot, Dependency Injection, GraalVM Native Image |
| **Used by** | Microservices, Containers, Cloud — AWS |
| **Related** | Micronaut Framework, Spring Boot, GraalVM |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:** The Java ecosystem has powerful standards (CDI, MicroProfile, JAX-RS) but every implementation (WildFly, TomEE, Liberty) was designed for long-lived application servers. Startup times of 30–60 s, 400–600 MB RAM, and no native-image support made Java a second-class citizen on Kubernetes and serverless platforms — where container density and cold-start speed are billable.

**THE BREAKING POINT:** GraalVM native-image became viable in 2019 but required a closed-world assumption incompatible with Java EE's runtime reflection, dynamic class loading, and CDI's bytecode manipulation at startup. The existing frameworks could not be made native-compatible without a fundamental redesign.

**THE INVENTION MOMENT:** In 2019, Red Hat released **Quarkus** — "Supersonic Subatomic Java." Its core insight: use existing MicroProfile and CDI standards (which developers already know) but implement them using **build-time augmentation** instead of runtime scanning. The `quarkus-build` step processes all annotations, generates bytecode, pre-computes metadata, and produces a either a fast-start JVM JAR or a GraalVM native binary. The tagline captures the ambition: supersonic startup (native binary), subatomic footprint (minimal RSS).

---

### 📘 Textbook Definition

**Quarkus** is a full-stack, Kubernetes-native Java framework built on top of Eclipse MicroProfile, CDI (Contexts and Dependency Injection), JAX-RS, Hibernate, and Vert.x. Its distinguishing feature is **build-time augmentation**: a multi-step bytecode-processing pipeline that runs during `quarkus build`, performing class scanning, dependency injection wiring, configuration binding, and REST endpoint registration — all before any JVM process starts. Quarkus produces deployable artifacts in two modes: a **JVM mode** fast-JAR (startup ~300 ms) and a **native mode** GraalVM binary (startup ~20 ms, ~15 MB RSS). It includes **Dev Services** (automatic Testcontainers for development), **Continuous Testing**, and a first-class **Dev UI** for productivity.

---

### ⏱️ Understand It in 30 Seconds

**One line:** A standards-based Java framework that compiles your application's wiring into the binary, not the startup sequence.

> "Quarkus is a prefabricated house: the walls, plumbing, and wiring are assembled at the factory (build-time augmentation), so on-site construction (JVM startup) is just placing the house on its foundation — seconds, not months."

**One insight:** Quarkus reuses existing Java EE standards (`@ApplicationScoped`, `@Path`, `@Inject`) — so a Java EE developer can read Quarkus code immediately. The innovation is entirely in how those standards are *implemented*, not in replacing them with new APIs.

---

### 🔩 First Principles Explanation

**CORE INVARIANTS:**
1. Standards-compliant code (CDI, JAX-RS) should not require a heavyweight runtime to execute.
2. The class scanning, proxy generation, and injection graph computation done at server startup can be done at build time — the result is the same.
3. GraalVM native-image requires knowing all code paths at build time; the framework must make the same guarantee.
4. Developer experience must not be sacrificed for performance — fast dev cycles are non-negotiable.

**DERIVED DESIGN:**
- **Augmentation pipeline:** `DeploymentProcessor` chain runs during `quarkus build`; each processor handles one concern (CDI, REST, config).
- **Fast-start JVM JAR:** produces a single mutable JAR with pre-generated index (Jandex), pre-computed DI wiring, and optimised classpath.
- **Native binary:** runs the augmented code through `native-image`, producing a platform-specific executable with ~20 ms startup.
- **Dev mode (`quarkus dev`):** watches source files, hot-reloads on change in <100 ms, starts Dev Services automatically.

**THE TRADE-OFFS:**

**Gain:** ~20 ms native startup, ~15 MB RSS native, standards compliance (CDI/MicroProfile), unmatched Dev mode experience, native-first GraalVM integration.

**Cost:** Native image build takes 3–8 minutes; some CDI features (producer methods for dynamic beans) have restrictions; extension authoring is complex; smaller ecosystem than Spring Boot.

---

### 🧪 Thought Experiment

**SETUP:** You build an order processing service that must handle peak holiday traffic (1,000 events/s) and idle at near-zero during off-peak. You deploy it as a Kubernetes Deployment with HPA (Horizontal Pod Autoscaler), min replicas = 0.

**WHAT HAPPENS WITHOUT QUARKUS (Spring Boot JVM):** A scale-from-0 event starts 10 pods. Each takes 12 s to reach readiness. HPA triggered 30 s before peak. You miss the first 15 s of peak traffic. Engineers configure min replicas = 3 to avoid cold starts — costing $800/month in idle compute.

**WHAT HAPPENS WITH QUARKUS NATIVE:** Scale-from-0 event starts 10 pods. Each reaches readiness in 300 ms (native). Zero traffic missed. Min replicas = 0 is viable. Idle cost: $0. RSS per pod: 20 MB vs 250 MB. Node density: 12× higher — same hardware runs 12× more pods.

**THE INSIGHT:** Quarkus native makes "scale to zero" a practical operational choice, not a theoretical one. The economic model of cloud computing is fundamentally different when your service starts in 20 ms vs 12 s.

---

### 🧠 Mental Model / Analogy

> "Quarkus's build-time augmentation is a GPS turn-by-turn route calculated before you get in the car (compile time), not one calculated while you drive (runtime). Spring Boot calculates the route as you drive — more flexible but slower to start moving."

- **Route calculation = DI resolution, class scanning, proxy generation** — framework startup work.
- **Pre-calculated route = augmented bytecode / native binary** — all decisions made, baked in.
- **Driving = handling HTTP requests** — happens at identical speed once started.
- **Road closures (new beans) = requires recalculation (rebuild)** — cost of the pre-calculation model.
- **GPS updates = Dev mode hot reload** — Quarkus recalculates just the changed segment in <100 ms.

Where this analogy breaks down: a GPS can recalculate in real-time for unexpected events; Quarkus cannot add new beans to a running native binary — a full rebuild is required.

---

### 📶 Gradual Depth — Four Levels

**Level 1 — What it is (anyone can understand):**
Quarkus is a Java framework that makes Java applications start in under a second and use very little memory. It does this by doing all the setup work during the build, and it can even compile your Java code into a native binary that starts as fast as a Go or Rust program.

**Level 2 — How to use it (junior developer):**
Create a project at `code.quarkus.io`. Annotate services with `@ApplicationScoped`. Use `@Inject` for dependencies. Use `@Path("/users")` and `@GET` for REST endpoints. Run `./mvnw quarkus:dev` for dev mode with live reload. Build native with `./mvnw package -Pnative`. Use `@QuarkusTest` for fast integration tests.

**Level 3 — How it works (mid-level engineer):**
The `quarkus build` Maven/Gradle goal triggers the **augmentation phase** — a multi-step pipeline of `BuildStep`-annotated processor methods. Key processors: `ArcAnnotationProcessor` (CDI wiring), `ResteasyReactiveProcessor` (JAX-RS routes), `HibernateOrmProcessor` (entity scanning). Each processor produces `BuildItem` records consumed by downstream processors. The final output is either: (a) a `fast-jar` with a pre-computed `quarkus-application.dat` (serialised startup state) for JVM mode, or (b) GraalVM `native-image` input for native mode. The `ApplicationClassLoader` in JVM mode deserialises the startup state rather than re-scanning — achieving ~300 ms startup.

**Level 4 — Why it was designed this way (senior/staff):**
Quarkus's `BuildStep` pipeline is itself a reactive, DAG-based build system — processors declare their inputs (`@Consume`) and outputs (`@Produce`) as `BuildItem` types, and Quarkus schedules them in dependency order. This design enables incremental augmentation: only changed processors re-run on hot reload. The CDI implementation (`ArC`) was written from scratch to avoid Weld/OpenWeaver's runtime bytecode manipulation — instead, ArC generates `InjectableBean` implementations as Java source during augmentation. The choice to use CDI/MicroProfile standards rather than invent new APIs (like Micronaut did) was a deliberate bet that the existing Java EE developer population would adopt Quarkus faster if they could reuse existing knowledge. This bet paid off — Quarkus's adoption in Red Hat/JBoss shops was rapid precisely because `@Inject`, `@Path`, and `@Transactional` worked as expected.

---

### ⚙️ How It Works (Mechanism)

```
BUILD-TIME AUGMENTATION PIPELINE
────────────────────────────────────────────────────────────
quarkus build
  │
  ├─► 1. Jandex indexing (scan all classes → bytecode index)
  │
  ├─► 2. CDI ARC processor
  │     ├─ Scan @ApplicationScoped, @Singleton, @Inject
  │     ├─ Generate InjectableBean<UserService>.java
  │     └─ Generate InterceptorInvoker for @Transactional
  │
  ├─► 3. RESTEasy Reactive processor
  │     ├─ Scan @Path, @GET, @POST
  │     ├─ Generate RouteBuilders
  │     └─ Register with Vert.x router
  │
  ├─► 4. Configuration processor
  │     ├─ Validate all @ConfigProperty references
  │     └─ Generate typed config classes
  │
  ├─► 5. Produce deployment artifact
  │     ├─ JVM mode: fast-jar + quarkus-application.dat
  │     └─ Native mode: → native-image compiler (3–8 min)
  │
RUNTIME
  java -jar target/quarkus-app/quarkus-run.jar
  │
  └─► Deserialise quarkus-application.dat
      ├─ No class scanning
      ├─ No proxy generation
      └─► Ready: ~300ms (JVM) / ~20ms (native)
```

**Dev Services — automatic infrastructure for development:**
```
quarkus:dev detects dependency on quarkus-jdbc-postgresql
  │
  ├─► No DB configured in application.properties
  ├─► Starts Testcontainers PostgreSQL automatically
  ├─► Injects JDBC URL into running application
  └─► Stops container on quarkus:dev exit
```

---

### 🔄 The Complete Picture — End-to-End Flow

**NORMAL FLOW (Development → Production):**
```
Developer writes UserService.java
  │
  ├─► quarkus:dev starts
  │     ├─► Augmentation: 2 s (first time)
  │     ├─► Dev Services: PostgreSQL started
  │     ├─► JVM started: 300 ms
  │     └─► Dev UI available at localhost:8080/q/dev
  │
Developer edits UserController.java
  │
  ├─► File watcher detects change             ← YOU ARE HERE
  ├─► Incremental augmentation: ~80 ms
  └─► Application reloaded: total ~100 ms

Production build:
  │
  ├─► ./mvnw package -Pnative
  ├─► native-image runs: 4 min
  ├─► Output: target/user-service-runner (22 MB)
  └─► docker build → 35 MB container image
```

**FAILURE PATH:**
- Native build fails with `ReflectionException` → class needs `@RegisterForReflection`.
- Dev Services cannot pull Docker image → dev mode falls back to config-specified datasource.
- CDI ambiguous dependency (`@Inject FooService` with 2 beans) → augmentation error with class name and injection point (caught at build time, not runtime).

**WHAT CHANGES AT SCALE:**
- Native build time (4–8 min) becomes a CI bottleneck at 50+ services. Solution: dedicated native build agents with 16+ CPU cores.
- `@ConfigProperty` injection is validated at build time — misconfigured deployments fail the build, not the pod startup. This is a **shift-left** of configuration errors.
- Multi-stage Docker builds with `FROM quay.io/quarkus/ubi-quarkus-native-image` reduce native build infrastructure to standard CI runners.

---

### 💻 Code Example

**BAD — traditional Spring Boot REST (works but starts in 12 s, uses 250 MB):**
```java
@RestController
@RequestMapping("/orders")
public class OrderController {
    @Autowired
    private OrderService service;   // runtime reflection

    @PostMapping
    public ResponseEntity<Order> create(
            @RequestBody CreateOrderRequest req) {
        return ResponseEntity.ok(service.create(req));
    }
}
```

**GOOD — Quarkus native-ready REST with CDI:**
```xml
<!-- pom.xml -->
<properties>
    <quarkus.platform.version>3.9.2</quarkus.platform.version>
    <quarkus.native.enabled>false</quarkus.native.enabled>
</properties>
<dependencies>
    <dependency>
        <groupId>io.quarkus</groupId>
        <artifactId>quarkus-rest</artifactId>
    </dependency>
    <dependency>
        <groupId>io.quarkus</groupId>
        <artifactId>quarkus-rest-jackson</artifactId>
    </dependency>
    <dependency>
        <groupId>io.quarkus</groupId>
        <artifactId>quarkus-hibernate-orm-panache</artifactId>
    </dependency>
    <dependency>
        <groupId>io.quarkus</groupId>
        <artifactId>quarkus-jdbc-postgresql</artifactId>
    </dependency>
    <dependency>
        <groupId>io.quarkus</groupId>
        <artifactId>quarkus-smallrye-openapi</artifactId>
    </dependency>
</dependencies>
<profiles>
    <profile>
        <id>native</id>
        <properties>
            <quarkus.native.enabled>true</quarkus.native.enabled>
        </properties>
    </profile>
</profiles>
```
```java
// Entity — Panache Active Record pattern
@Entity
@Table(name = "orders")
public class Order extends PanacheEntity {

    @Column(nullable = false)
    public String customerId;

    @Column(nullable = false)
    @Enumerated(EnumType.STRING)
    public OrderStatus status;

    public static List<Order> findByCustomer(String customerId) {
        return list("customerId", customerId);
    }
}

// CDI service — compile-time wiring, no reflection
@ApplicationScoped
@Transactional
public class OrderService {

    public Order create(CreateOrderRequest req) {
        Order order = new Order();
        order.customerId = req.customerId();
        order.status = OrderStatus.PENDING;
        order.persist();
        return order;
    }

    @Transactional(Transactional.TxType.SUPPORTS)
    public List<Order> getByCustomer(String customerId) {
        return Order.findByCustomer(customerId);
    }
}

// JAX-RS resource — augmented at build time
@Path("/orders")
@Produces(MediaType.APPLICATION_JSON)
@Consumes(MediaType.APPLICATION_JSON)
public class OrderResource {

    @Inject
    OrderService orderService;        // wired at build time

    @POST
    public Response create(CreateOrderRequest req) {
        Order order = orderService.create(req);
        return Response.created(
            URI.create("/orders/" + order.id)).entity(order).build();
    }

    @GET
    @Path("/customer/{customerId}")
    public List<Order> getByCustomer(
            @PathParam("customerId") String customerId) {
        return orderService.getByCustomer(customerId);
    }
}
```
```java
// Integration test — full app context in ~300ms
@QuarkusTest
class OrderResourceTest {

    @Test
    void createOrder_returns201() {
        given()
            .contentType(ContentType.JSON)
            .body("""
                {"customerId": "cust-123"}
                """)
        .when()
            .post("/orders")
        .then()
            .statusCode(201)
            .header("Location", containsString("/orders/"));
    }
}
```
```properties
# application.properties
quarkus.datasource.db-kind=postgresql
quarkus.datasource.username=${DB_USER:quarkus}
quarkus.datasource.password=${DB_PASS:quarkus}
quarkus.datasource.jdbc.url=${JDBC_URL:\
  jdbc:postgresql://localhost:5432/orders}
quarkus.hibernate-orm.database.generation=update

# Dev Services auto-configure in dev/test when JDBC_URL absent
%dev.quarkus.datasource.devservices.enabled=true
%test.quarkus.datasource.devservices.enabled=true
```

---

### ⚖️ Comparison Table

| Feature | Quarkus | Spring Boot 3 | Micronaut 4 |
|---|---|---|---|
| **DI standard** | CDI (ArC) | Spring DI | Custom (compile-time) |
| **REST standard** | JAX-RS / MicroProfile | Spring MVC / WebFlux | Micronaut HTTP |
| **Startup (JVM)** | ~300 ms | ~3–15 s | ~100 ms |
| **Startup (native)** | ~20 ms | ~200 ms | ~60 ms |
| **Memory (native)** | ~15 MB | ~50 MB | ~25 MB |
| **Dev mode** | quarkus:dev (live reload) | DevTools (restart) | mn:run (live reload) |
| **Dev Services** | First-class (auto-containers) | Manual Testcontainers | Manual Testcontainers |
| **Native maturity** | Excellent (native-first) | Good (AOT retrofit) | Very good |
| **MicroProfile** | Full compliance | No | Partial |
| **Kubernetes native** | Operator, Helm, Kube manifests | Via Spring Cloud K8s | Via micronaut-k8s |
| **Extension system** | Rich (500+ extensions) | Rich (500+ starters) | Moderate (80+ modules) |
| **Reactive** | Mutiny + Vert.x | Reactor (WebFlux) | Reactor / Coroutines |
| **Red Hat support** | Enterprise subscription | Pivotal/VMware | OCI / community |

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| "Quarkus only works with GraalVM native" | Quarkus's JVM mode (fast-jar) starts in ~300 ms without native-image. Native is optional and provides additional startup/memory gains. Most teams run JVM mode in dev/staging. |
| "CDI in Quarkus is full WildFly CDI" | Quarkus uses ArC — a CDI subset that excludes dynamic features like `CDI.current().select()` at runtime with no type information. Some advanced CDI patterns need refactoring. |
| "Dev Services use real cloud resources" | Dev Services use Testcontainers on the local Docker daemon — PostgreSQL, Redis, Kafka start as local containers. No cloud account, no cost. They stop when `quarkus:dev` exits. |
| "Quarkus extensions are optional extras" | Extensions are how Quarkus augments third-party libraries. Using `quarkus-hibernate-orm` instead of raw Hibernate is required for build-time augmentation to work — raw Hibernate has no Quarkus BuildSteps. |
| "Native image has identical throughput to JVM" | Native image lacks JIT compilation. At startup and under light load it is faster. Under sustained load, a warmed JVM (with JIT) typically achieves 10–30% higher throughput. Use JVM mode for throughput-sensitive batch; native for cold-start-sensitive Lambda/containers. |

---

### 🚨 Failure Modes & Diagnosis

**Mode 1 — Native image build fails with missing reflection config**

**Symptom:** `./mvnw package -Pnative` fails with `ClassNotFoundException: com.example.dto.UserDto` during `native-image` run, or runs but throws `IllegalReflectiveAccessException` at runtime.

**Root Cause:** `UserDto` is accessed via Jackson serialisation at runtime. GraalVM's native-image cannot include reflectively-accessed classes without explicit declaration. Quarkus auto-generates most configs, but DTO classes without Quarkus annotations require explicit registration.

**Diagnostic:**
```bash
# Run native agent to discover all reflection needs during tests
./mvnw test \
  -Dquarkus.native.agent-library-path=\
    ${GRAALVM_HOME}/lib/svm/bin/native-image-agent \
  -Dquarkus.native.config-output-dir=\
    src/main/resources/META-INF/native-image

# Check augmentation output for generated reflect-config
find target -name "reflect-config.json" -exec cat {} \;
```

**Fix:**
```java
// Option 1: Annotate DTO for Quarkus build-time introspection
@RegisterForReflection       // generates reflect-config entry
public class UserDto {
    public Long id;
    public String name;
}

// Option 2: Use @RegisterForReflection on package level
@RegisterForReflection(targets = {
    UserDto.class,
    PagedResponse.class
})
public class ReflectionConfig {}
```

**Prevention:** Use `quarkus-rest-jackson` with `@JsonProperty` annotations — Quarkus serialises these at build time using Jackson metadata, requiring no runtime reflection. Prefer records with `@Serdeable` for zero-reflection serialisation.

---

**Mode 2 — Dev Services conflict with existing local infrastructure**

**Symptom:** `quarkus:dev` fails to start with "Could not create container: port 5432 already in use." Developer already has PostgreSQL running locally.

**Root Cause:** Dev Services default to fixed ports (5432 for PostgreSQL). The developer's local instance occupies the port. Dev Services cannot start a second instance.

**Diagnostic:**
```bash
# Find which process owns port 5432
netstat -ano | findstr :5432
# or on Unix
lsof -i :5432

# Check Dev Services configuration
./mvnw quarkus:dev -Dquarkus.log.level=DEBUG \
  2>&1 | grep -i "devservices\|container\|port"
```

**Fix:**
```properties
# Option 1: Disable Dev Services and use local DB
%dev.quarkus.datasource.devservices.enabled=false
%dev.quarkus.datasource.jdbc.url=\
  jdbc:postgresql://localhost:5432/orders_dev

# Option 2: Use a random port for Dev Services container
%dev.quarkus.datasource.devservices.port=0
```

**Prevention:** In team environments, document which profiles use Dev Services vs local infra. Use `.env` files with `quarkus.datasource.devservices.enabled=false` for developers with local stacks.

---

**Mode 3 — CDI ambiguous dependency crash at augmentation**

**Symptom:** `quarkus build` fails: `AmbiguousResolutionException: Ambiguous dependencies for type OrderRepository. Beans: [OrderRepositoryImpl, MockOrderRepository]`.

**Root Cause:** Two CDI beans implement `OrderRepository`. Quarkus ArC cannot resolve which to inject without a qualifier. Unlike Spring (which fails at runtime), Quarkus fails this at build time — which is the correct behaviour but surprises developers used to Spring's runtime error.

**Diagnostic:**
```bash
# Build output includes the exact injection point and candidates
./mvnw package 2>&1 \
  | grep -A 20 "AmbiguousResolution"
# Shows: class, injection point, candidate bean list
```

**Fix:**
```java
// BAD — two beans, no qualifier
@ApplicationScoped
public class OrderRepositoryImpl implements OrderRepository {}

@ApplicationScoped
public class MockOrderRepository implements OrderRepository {}

// GOOD — use @Default and @Alternative with @Priority
@ApplicationScoped
@Default
public class OrderRepositoryImpl implements OrderRepository {}

@ApplicationScoped
@Alternative
@Priority(1)              // higher priority activates alternative
@IfBuildProfile("test")  // only active in test profile
public class MockOrderRepository implements OrderRepository {}
```

**Prevention:** Validate ambiguity locally with `quarkus build` before pushing to CI. Use `@IfBuildProfile`, `@UnlessBuildProfile`, and `@IfBuildProperty` to make environment-specific beans explicit.

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**
- GraalVM Native Image — the native compilation target that Quarkus is optimised for
- Dependency Injection — CDI (the standard Quarkus implements) is a DI spec
- Spring Boot — the incumbent framework Quarkus is positioned against

**Builds On This (learn these next):**
- Micronaut Framework — alternative compile-time DI framework; compare extension model and standards support
- Micronaut vs Spring Boot — framework trade-off analysis applicable to Quarkus selection as well
- Containers — Quarkus native images produce the smallest container images possible for Java

**Alternatives / Comparisons:**
- Micronaut Framework — non-standards-based compile-time DI; faster startup; smaller footprint
- Spring Boot — richer ecosystem; slower startup; Spring AOT closing the native-image gap
- Helidon — Oracle's MicroProfile-compliant framework; MP2 and MP4 support; smaller community

---

### 📌 Quick Reference Card

```
╔══════════════════════════════════════════════════╗
║  WHAT IT IS      Build-time augmented Java FW    ║
║  PROBLEM         JVM too slow for cloud-native   ║
║  KEY INSIGHT     Pre-compute everything buildable║
║  USE WHEN        K8s scale-to-zero, Lambda, IoT  ║
║  AVOID WHEN      Heavy CDI producer patterns     ║
║  TRADE-OFF       Build time (4min) vs run speed  ║
║  ONE-LINER       "Supersonic Subatomic Java"     ║
║  NEXT EXPLORE    GraalVM Native Image, Micronaut ║
╚══════════════════════════════════════════════════╝
```

---

### 🧠 Think About This Before We Continue

1. **(C — Design Trade-off)** Quarkus shifts errors from runtime to build time (e.g., CDI ambiguity, missing `@RegisterForReflection`). List three specific failure scenarios that Spring Boot would discover at runtime but Quarkus catches at build time. For each, explain whether the earlier detection is always beneficial, or if there are cases where runtime flexibility is worth the later detection.

2. **(B — Scale)** Your team has 60 microservices. Native image builds take 5 minutes each. CI pipeline runs on 20 parallel agents. You push a cross-cutting library change that triggers rebuilds of all 60 services. Calculate the total CI agent-minutes consumed, the wall-clock time to complete all builds, and propose a caching or build strategy that reduces this to under 15 minutes wall-clock time.

3. **(A — System Interaction)** Quarkus Dev Services automatically starts a PostgreSQL container for development. Describe the full sequence of events from `quarkus:dev` startup to a developer executing a `SELECT` query — including which Quarkus components detect the missing config, which Testcontainers API is invoked, how the JDBC URL is injected, and how Dev Services cleans up on shutdown.
