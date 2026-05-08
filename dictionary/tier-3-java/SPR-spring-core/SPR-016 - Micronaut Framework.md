---
layout: default
title: "Micronaut Framework"
parent: "Spring Core"
grand_parent: "Technical Dictionary"
nav_order: 16
permalink: /spring/micronaut-framework/
id: SPR-016
category: Spring Core
difficulty: ★★★
depends_on: Spring Boot, Dependency Injection, AOT (Ahead-of-Time Compilation)
used_by: Microservices, Containers, Cloud - AWS
related: Quarkus Framework, Spring Boot, GraalVM Native Image
tags:
  - java
  - jvm
  - microservices
  - advanced
  - performance
---

# SPR-016 - Micronaut Framework

⚡ TL;DR - Micronaut is a JVM framework that resolves dependency injection at compile time instead of runtime, delivering sub-second startup and minimal memory footprint.

| Field | Value |
|---|---|
| **Depends on** | Spring Boot, Dependency Injection, AOT (Ahead-of-Time Compilation) |
| **Used by** | Microservices, Containers, Cloud - AWS |
| **Related** | Quarkus Framework, Spring Boot, GraalVM Native Image |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:** Spring Boot scans the classpath, loads every `@Component`, resolves all dependencies via reflection, builds proxy classes via CGLIB, and processes `@Configuration` classes - all at startup time. A moderately complex microservice takes 8–15 seconds to start and consumes 200–400 MB RAM before serving a single request. In a Kubernetes cluster that auto-scales under load, a 12-second cold start means your scaling event finishes after the traffic spike has passed.

**THE BREAKING POINT:** Three trends made Spring Boot's runtime DI model painful: (1) **Serverless** - Lambda functions are invoked in under 100 ms; a 12 s cold start makes Spring unusable. (2) **Containers** - 200 MB baseline RAM means fewer pods per node; cost scales linearly with RAM. (3) **GraalVM Native** - native compilation requires closed-world assumption; Spring's reflection-heavy DI is incompatible with native images without heroic configuration.

**THE INVENTION MOMENT:** In 2018, Object Computing Inc. released **Micronaut**, designed from scratch with one constraint: *no reflection at runtime for the DI framework itself*. All bean wiring, AOP proxies, and configuration binding are computed by annotation processors during `javac` - before the JVM ever starts. The result: startup in ~100 ms, 40–80 MB RSS, and first-class GraalVM compatibility.

---

### 📘 Textbook Definition

**Micronaut** is a modern, JVM-based, full-stack framework for building modular, easily testable microservice and serverless applications. Its defining characteristic is **compile-time dependency injection**: Micronaut's annotation processor (`micronaut-inject-java`) scans `@Singleton`, `@Inject`, `@Value`, and all AOP annotations during compilation and generates Java source files (not bytecode manipulation at runtime) that perform all wiring. The result is a framework with Spring-like productivity and near-native performance characteristics. Micronaut supports Java, Kotlin, and Groovy; integrates with GraalVM natively; and provides first-class HTTP server and client components built on Netty.

---

### ⏱️ Understand It in 30 Seconds

**One line:** A JVM framework that does all the DI work at compile time so the JVM has nothing to figure out at startup.

> "Micronaut is a meal-prep kitchen: all the chopping, measuring, and prep work (DI resolution) happens the night before (compile time), so when service starts (dinner time), it just plates and serves - instantly."

**One insight:** The performance gain is not about doing less work - it's about doing the same work earlier. Annotation processing is already a compile step; Micronaut simply moves DI resolution into that step.

---

### 🔩 First Principles Explanation

**CORE INVARIANTS:**
1. Dependency graphs are static - they do not change between `javac` and `java`. Computing them at runtime is wasteful by definition.
2. Reflection is the runtime equivalent of not planning ahead - it works but pays a per-call cost.
3. A framework cannot use features unavailable to native images without sacrificing native compatibility.
4. Testing should not require a running application context to be fast and deterministic.

**DERIVED DESIGN:**
- `micronaut-inject-java` annotation processor runs during `javac` and generates `$Definition` and `$DefinitionReference` classes.
- Generated classes implement `BeanDefinition<T>` - they contain the exact constructor/field injection calls as compiled Java, with no reflection.
- `ApplicationContext.start()` calls `loadContextConfiguration()`, which instantiates the generated definitions directly.
- AOP interception is generated as subclass proxies at compile time, not via CGLIB at runtime.

**THE TRADE-OFFS:**

**Gain:** ~100 ms startup; 40–80 MB RSS; native-image compatible without extra config; faster test context startup (50–200 ms vs 5–15 s).

**Cost:** Incremental compile required when adding beans - cannot add a new `@Singleton` to a running JDK process via hot reload; a full recompile is needed. Less dynamic than Spring - runtime-conditional beans are harder to express.

---

### 🧪 Thought Experiment

**SETUP:** You deploy a microservice to AWS Lambda. It processes user profile requests. You have two options: Spring Boot (SB) or Micronaut (MN).

**WHAT HAPPENS WITHOUT MICRONAUT (Spring Boot on Lambda):** First invocation triggers a cold start. Spring Boot scans 300 classpath entries, creates 120 beans, fires 8 application events, and connects to the database - 9 seconds. Lambda's 10 s timeout barely allows the first request. AWS pre-provisioned concurrency costs 10× normal to hide the cold starts. Monthly bill is $4,000.

**WHAT HAPPENS WITH MICRONAUT:** The Lambda is packaged with a GraalVM native binary. No JVM warm-up. All beans were resolved at compile time and baked into the binary. Cold start: 80 ms. AWS pre-provisioned concurrency: not needed. Monthly bill: $400.

**THE INSIGHT:** For workloads where startup frequency is high (serverless, scale-to-zero, frequent deployments), framework startup time directly translates to cost and responsiveness. Micronaut's compile-time DI makes this workload class viable for JVM-based teams.

---

### 🧠 Mental Model / Analogy

> "Micronaut is an IKEA flat-pack where every part is pre-labelled, pre-drilled, and pre-measured at the factory. Spring Boot is building the same furniture from raw timber - it cuts, measures, and drills at assembly time (runtime). Both produce the same table; Micronaut's takes 5 minutes to assemble; Spring Boot's takes an hour."

- **Factory pre-drilling = annotation processor** - all holes (injection points) made during build.
- **Pre-labelled parts = generated `$Definition` classes** - exact wiring code, no guessing.
- **Assembly time = JVM startup** - Micronaut just screws parts together; Spring still cuts lumber.
- **Same final table = functionally equivalent application** - same endpoints, same business logic.
- **Custom modifications (new holes) = adding new beans** - requires going back to the factory (recompile).

Where this analogy breaks down: IKEA furniture is truly static once built; Micronaut still allows runtime configuration overrides via `@Requires` conditions and environment properties.

---

### 📶 Gradual Depth - Four Levels

**Level 1 - What it is (anyone can understand):**
Micronaut is a framework for building Java microservices that starts in under a second and uses very little memory. It achieves this by doing all the setup work during the build rather than when the app starts.

**Level 2 - How to use it (junior developer):**
Create a project at `launch.micronaut.io`. Annotate services with `@Singleton`. Use `@Inject` for dependencies. Use `@Controller("/users")` for HTTP handlers. Run `./gradlew run` for dev or `./gradlew nativeCompile` for a native binary. Testing uses `@MicronautTest` which starts an embedded server in ~200 ms.

**Level 3 - How it works (mid-level engineer):**
During `javac`, the `micronaut-inject-java` annotation processor processes every `@Singleton`, `@Controller`, `@Client`, `@Value`, `@ConfigurationProperties`, and AOP annotation. For each annotated class `Foo`, it generates `FooDefinition.java` containing `getConstructor()`, `inject()`, and `getBeanDefinitionType()` methods with direct constructor calls - no `Class.forName()`, no `Method.invoke()`. At startup, `DefaultApplicationContext` scans the classpath for all classes named `*$DefinitionReference` (generated), instantiates them via the generated classes, and wires the graph in milliseconds.

**Level 4 - Why it was designed this way (senior/staff):**
The generated-code approach mirrors what a developer would write by hand if they didn't have a DI framework - direct constructor calls, no reflection, no proxies via bytecode manipulation. This has three architectural consequences: (1) **GraalVM compatibility** - `native-image` requires knowing all reflection calls at build time; generated Java code has none. (2) **Deterministic startup** - no classpath scanning race conditions; the generated code is deterministic and can be audited. (3) **AOT-first test performance** - `@MicronautTest` starts the real application context in 50–200 ms because there is no reflection scan to perform. The trade-off accepted is reduced dynamic extensibility - Spring's `BeanFactoryPostProcessor` and `SmartInstantiationAwareBeanPostProcessor` allow third-party libraries to modify beans at runtime; Micronaut has no equivalent runtime hook because the bean graph is already fixed.

---

### ⚙️ How It Works (Mechanism)

```
BUILD TIME (javac + annotation processor)
──────────────────────────────────────────────────────
 Source: UserService.java                 Annotation
 @Singleton                               Processor
 class UserService {                  ──────────────►
   @Inject UserRepository repo;           Generates:
 }                                    UserServiceDefinition.java
                                          ┌──────────────────────┐
                                          │ getConstructor() {   │
                                          │  return new          │
                                          │   Constructor<>(     │
                                          │    UserRepository.class│
                                          │   );                 │
                                          │ }                    │
                                          └──────────────────────┘
RUNTIME (java -jar app.jar)
──────────────────────────────────────────────────────
 ApplicationContext.start()
   │
   ├─► Scan classpath for *$DefinitionReference classes
   ├─► No reflection - all wiring via generated code
   ├─► Instantiate beans in dependency order
   └─► Netty HTTP server starts on port 8080
       Total: ~80–120 ms
```

**Annotation-driven AOP at compile time:**
```
@Singleton
@Transactional          ← triggers proxy generation
class OrderService { }

Generated:
OrderService$Intercepted extends OrderService {
  @Override
  public Order create(Cart cart) {
    txInterceptor.intercept(ctx, () -> super.create(cart));
  }
}
```

---

### 🔄 The Complete Picture - End-to-End Flow

**NORMAL FLOW:**
```
gradle build
  │
  ├─► javac + micronaut-inject-java annotation processor
  ├─► Generated: *Definition.class, *DefinitionReference.class
  │
java -jar app.jar
  │
  ├─► ApplicationContext.start()                 ← YOU ARE HERE
  │     ├─► Load all DefinitionReference classes (fast index)
  │     ├─► Resolve bean graph (precomputed)
  │     ├─► Instantiate singletons in order
  │     └─► Register Netty HTTP routes from @Controller classes
  │
  ├─► HTTP server listening: ~80 ms from JVM start
  └─► First request served
```

**FAILURE PATH:**
- Missing `@Inject` annotation → `NoSuchBeanException` at startup (caught early, not at first use).
- Circular dependency → compilation error from annotation processor (caught at build time).
- Invalid `@ConfigurationProperties` binding → startup failure with clear property path error.

**WHAT CHANGES AT SCALE:**
- Native image builds take 2–5 minutes (`native-compile`) but produce a binary that starts in 50 ms.
- GraalVM reflection configuration (`reflect-config.json`) still needed for third-party libraries that use reflection (e.g., Jackson, database drivers).
- Kubernetes pod scaling with Micronaut native is near-instant; Kubernetes `readinessProbe` can use a 1 s `initialDelaySeconds` instead of Spring's 30 s.

---

### 💻 Code Example

**BAD - Spring Boot style (works but heavy for serverless/containers):**
```java
// ~9 s startup, ~250 MB RAM for similar app
@SpringBootApplication
public class UserApp {
    public static void main(String[] args) {
        SpringApplication.run(UserApp.class, args);
    }
}

@Service
public class UserService {
    @Autowired
    private UserRepository repo;  // reflection at runtime

    public User findById(Long id) {
        return repo.findById(id).orElseThrow();
    }
}
```

**GOOD - Micronaut compile-time DI, native-image ready:**
```java
// build.gradle
plugins {
    id("io.micronaut.application") version "4.3.5"
    id("io.micronaut.aot") version "4.3.5"
}

micronaut {
    runtime("netty")
    testRuntime("junit5")
    processing {
        incremental(true)
        annotations("com.example.*")
    }
}

dependencies {
    annotationProcessor("io.micronaut:micronaut-inject-java")
    implementation("io.micronaut:micronaut-http-server-netty")
    implementation("io.micronaut.data:micronaut-data-jdbc")
    runtimeOnly("io.micronaut.sql:micronaut-jdbc-hikari")
    testImplementation("io.micronaut.test:micronaut-test-junit5")
}
```
```java
// Controller - no reflection, wired at compile time
@Controller("/users")
public class UserController {

    private final UserService userService;

    // Constructor injection - generated by annotation processor
    public UserController(UserService userService) {
        this.userService = userService;
    }

    @Get("/{id}")
    public HttpResponse<UserDto> getUser(Long id) {
        return userService.findById(id)
            .map(HttpResponse::ok)
            .orElse(HttpResponse.notFound());
    }
}

@Singleton
public class UserService {

    private final UserRepository repo;

    public UserService(UserRepository repo) {
        this.repo = repo;
    }

    public Optional<UserDto> findById(Long id) {
        return repo.findById(id).map(UserDto::from);
    }
}
```
```java
// Test - full context in ~150ms
@MicronautTest
class UserControllerTest {

    @Inject
    HttpClient client;

    @Test
    void getUser_returnsUser() {
        HttpResponse<UserDto> resp = client.toBlocking()
            .exchange(HttpRequest.GET("/users/1"), UserDto.class);

        assertThat(resp.status()).isEqualTo(HttpStatus.OK);
        assertThat(resp.body().id()).isEqualTo(1L);
    }
}
```
```yaml
# application.yml - typed, validated at compile time
micronaut:
  application:
    name: user-service
  server:
    port: 8080
datasources:
  default:
    url: ${JDBC_URL:`jdbc:h2:mem:user-db`}
    driver-class-name: org.h2.Driver
    username: ${DB_USER:sa}
    password: ${DB_PASS:}
```

---

### ⚖️ Comparison Table

| Feature | Micronaut | Spring Boot | Quarkus | Helidon |
|---|---|---|---|---|
| **DI resolution** | Compile time | Runtime (reflection) | Compile time (Jandex) | Runtime |
| **Startup time (JVM)** | ~100 ms | ~5–15 s | ~200 ms | ~500 ms |
| **Startup time (native)** | ~50 ms | ~200 ms (AOT) | ~20 ms | ~20 ms |
| **RSS memory (JVM)** | ~60 MB | ~200–400 MB | ~100 MB | ~150 MB |
| **GraalVM native** | First-class | Supported (Spring AOT) | First-class | First-class |
| **Ecosystem maturity** | Growing | Very mature | Growing | Smaller |
| **Learning curve** | Medium | Low (vast docs) | Medium | High |
| **Hot reload** | Via `mn:run` | DevTools | Quarkus Dev Mode | Manual |
| **Best for** | Serverless, containers | Enterprise, large teams | Kubernetes-native | Helidon MP users |

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| "Micronaut doesn't support Spring annotations" | `micronaut-spring` compatibility layer translates some Spring annotations, but it is not a drop-in Spring replacement. Core Micronaut uses its own `@Singleton`, `@Inject`, `@Controller`. |
| "Compile-time DI means no dynamic beans" | Micronaut supports `@Requires` conditions (evaluated at context startup based on environment/config), `@Secondary`, and `@Replaces` for dynamic substitution. True runtime dynamic bean registration is not supported. |
| "Micronaut native images need no extra config" | Libraries using reflection (Jackson, Hibernate, some JDBC drivers) still require `reflect-config.json`. Micronaut generates most of it automatically via `micronaut-graal` - but edge cases remain. |
| "Faster startup means faster throughput" | Startup time and request throughput are independent. JVM JIT still warms up over the first few thousand requests. For max throughput, JVM mode (with JIT) beats native images at steady state. |
| "Micronaut is a Spring killer" | Both serve different use cases. Micronaut excels at containers, serverless, and latency-sensitive services. Spring Boot excels at enterprise apps with rich ecosystem and large existing codebases. |

---

### 🚨 Failure Modes & Diagnosis

**Mode 1 - Bean wiring error only visible at runtime despite compile-time DI**

**Symptom:** Application compiles successfully but throws `NoSuchBeanException` on startup for `UserRepository`.

**Root Cause:** `UserRepository` uses a third-party library that relies on runtime classpath scanning (e.g., MyBatis mapper scanner). Micronaut's annotation processor cannot see these beans at compile time - they are only registered when the library's own runtime initializer runs, but after Micronaut's bean graph is already constructed.

**Diagnostic:**
```bash
# Run with bean debug logging
java -Dmicronaut.bootstrap.context=true \
     -Dmicronaut.beanIntrospection.logger=DEBUG \
     -jar app.jar 2>&1 | grep -E 'NoSuch|not found'

# List all registered bean definitions
curl -s http://localhost:8080/beans | jq '.beans[].type'
```

**Fix:**
```java
// Register the third-party bean manually via a @Factory
@Factory
public class MyBatisConfig {

    @Singleton
    @Requires(classes = UserMapper.class)
    public UserRepository userRepository(SqlSession session) {
        return session.getMapper(UserRepository.class);
    }
}
```

**Prevention:** For third-party libraries, check for Micronaut-specific modules at `micronaut.io/modules` before using raw library adapters.

---

**Mode 2 - Native image crashes with reflection error**

**Symptom:** App runs perfectly in JVM mode. Native image build succeeds. At runtime, `com.fasterxml.jackson.databind.exc.InvalidDefinitionException: No serializer found`.

**Root Cause:** Jackson uses reflection to discover bean properties. GraalVM's native image has a closed-world assumption - reflection on classes not declared in `reflect-config.json` fails at runtime.

**Diagnostic:**
```bash
# Run native image with tracing agent to discover reflection needs
java -agentlib:native-image-agent=config-output-dir=\
src/main/resources/META-INF/native-image \
-jar app.jar
# Exercise all code paths via tests
# Agent generates reflect-config.json, resource-config.json
```

**Fix:**
```json
// src/main/resources/META-INF/native-image/reflect-config.json
[
  {
    "name": "com.example.UserDto",
    "allDeclaredConstructors": true,
    "allDeclaredFields": true,
    "allDeclaredMethods": true
  }
]
```
Or use Micronaut's `@Introspected` annotation which generates reflection-free introspection:
```java
@Introspected   // generates BeanIntrospection at compile time
public record UserDto(Long id, String name, String email) {}
```

**Prevention:** Use Micronaut Serde (`micronaut-serde-jackson`) instead of raw Jackson - it generates serializers at compile time and needs zero `reflect-config`.

---

**Mode 3 - AOP not applied (aspect advice silently skipped)**

**Symptom:** `@Transactional` annotated method runs without a transaction. Database writes are not rolled back on exception.

**Root Cause:** The bean was instantiated directly with `new UserService()` instead of being injected via the Micronaut context. Compile-time AOP generates a `UserService$Intercepted` proxy subclass - direct instantiation bypasses the proxy entirely.

**Diagnostic:**
```bash
# Verify the injected type is the proxy subclass
curl -s http://localhost:8080/beans \
  | jq '.beans[] | select(.type | contains("UserService"))
    | .type'
# Should show: com.example.UserService$Intercepted
# If shows: com.example.UserService - proxy is not being used
```

**Fix:**
```java
// BAD - direct instantiation bypasses AOP proxy
UserService svc = new UserService(repo);

// GOOD - always inject via context
@Inject
UserService svc;  // receives UserService$Intercepted proxy
```

**Prevention:** ArchUnit rule: ban `new` instantiation of `@Singleton`-annotated classes inside service code.

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**
- Dependency Injection - the core pattern Micronaut reimplements at compile time
- AOT (Ahead-of-Time Compilation) - the compile-time technique enabling Micronaut's performance
- Spring Boot - the framework Micronaut was designed as an alternative to

**Builds On This (learn these next):**
- GraalVM Native Image - the native compilation target that makes Micronaut's advantages most dramatic
- Micronaut vs Spring Boot - detailed comparison of trade-offs and migration considerations
- Quarkus Framework - alternative compile-time DI framework with a different extension model

**Alternatives / Comparisons:**
- Quarkus Framework - Red Hat's equivalent; different extension API; stronger Kubernetes-native story
- Spring Boot - the incumbent; richer ecosystem; now offers Spring AOT for similar native-image support
- Helidon - Oracle's lightweight framework; MP spec compatible; less traction

---

### 📌 Quick Reference Card

```
╔══════════════════════════════════════════════════╗
║  WHAT IT IS      Compile-time DI JVM framework   ║
║  PROBLEM         JVM frameworks too slow to start║
║  KEY INSIGHT     Move DI work from run to build  ║
║  USE WHEN        Serverless, containers, scale-0 ║
║  AVOID WHEN      Large dynamic Spring ecosystems ║
║  TRADE-OFF       Startup speed vs DI dynamism    ║
║  ONE-LINER       "Spring-like API, native speed" ║
║  NEXT EXPLORE    GraalVM Native Image, Quarkus   ║
╚══════════════════════════════════════════════════╝
```

---

### 🧠 Think About This Before We Continue

1. **(B - Scale)** In a Lambda function that receives 100,000 invocations per day with a 5-minute idle window, estimate the total cold-start latency overhead for Spring Boot (9 s cold start) vs Micronaut native (80 ms) over one month. At what request frequency does the difference become negligible, and why?

2. **(E - First Principles)** Micronaut's compile-time DI means it cannot support a library that registers beans dynamically based on data read from a database at startup. Design a pattern that achieves runtime-configurable bean selection within Micronaut's compile-time model without breaking GraalVM compatibility.

3. **(C - Design Trade-off)** Spring Boot's runtime reflection model enables powerful features like `BeanFactoryPostProcessor` used by libraries such as Spring Security for runtime bean mutation. Which class of features in modern enterprise applications becomes genuinely harder to implement in Micronaut due to the absence of runtime bean graph modification, and how would you architect around this limitation?
