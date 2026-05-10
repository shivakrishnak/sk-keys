---
id: SPR-002
title: The Spring Ecosystem Map
category: Spring Core
tier: tier-3-java
folder: SPR-spring-core
difficulty: ★☆☆
depends_on: SPR-001
used_by: SPR-003, SPR-004, SPR-005
related: SPR-051, SPR-067, SPR-030
tags:
  - spring
  - java
  - foundational
  - mental-model
  - architecture
status: complete
version: 2
layout: default
parent: "Spring Core"
grand_parent: "Technical Dictionary"
nav_order: 2
permalink: /spr/the-spring-ecosystem-map/
---

# SPR-002 - The Spring Ecosystem Map

⚡ TL;DR - The Spring ecosystem is a family of projects sharing the IoC container core, each solving a different domain from web to batch to cloud to AI.

| Field          | Value                                                                                                                                                                   |
| -------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Depends on** | [[SPR-001 - What Is Spring - History and Philosophy]]                                                                                                                   |
| **Used by**    | [[SPR-003 - Why Spring Boot Changed Java Development]], [[SPR-004 - Spring vs Jakarta EE vs Micronaut vs Quarkus]], [[SPR-005 - Spring in Production - What to Expect]] |
| **Related**    | [[SPR-051 - Spring Cloud Overview]], [[SPR-067 - Auto-Configuration]], [[SPR-030 - Spring Security]]                                                                    |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**

A developer joining a Spring project faces an alphabet soup: Spring Boot, Spring MVC, Spring Data, Spring Security, Spring Cloud, Spring Batch, Spring Integration, Spring WebFlux, Spring AMQP, Spring Kafka. Without a map, they either assume these are separate unrelated products or assume Spring Boot contains everything. Both assumptions lead to choosing the wrong tool or re-implementing what Spring already provides.

**THE BREAKING POINT:**

The Spring portfolio grew organically from 2003 to today. Each project solved a real need but was named independently. "Spring Cloud" sounds nothing like "Spring Batch" yet both live under the same parent. Without an explicit mental map, the ecosystem appears chaotic.

**THE INVENTION MOMENT:**

The ecosystem is not chaos - it is layered. There is one core (the IoC container in Spring Framework), one opinionated assembler (Spring Boot), and then domain-specific projects that each wrap a third-party integration point. Understanding the layer structure makes the whole map readable.

**EVOLUTION:**

The ecosystem expanded in predictable waves: web (MVC), data access (Spring Data), security (Spring Security), batch processing (Spring Batch), reactive (WebFlux, Project Reactor), cloud-native (Spring Cloud), native images (Spring Native / GraalVM), and most recently AI/LLM integration (Spring AI, introduced 2024).

---

### 📘 Textbook Definition

The **Spring Ecosystem** is the collection of open-source Java projects maintained under the Spring umbrella at [spring.io](https://spring.io/projects). All projects are built on or integrate with **Spring Framework** (the IoC container core). **Spring Boot** is the assembly layer that auto-configures and connects them. Each portfolio project addresses a specific integration domain: data access, security, messaging, batch processing, distributed systems, or cloud infrastructure.

---

### ⏱️ Understand It in 30 Seconds

**One line:** Spring Framework is the engine; Spring Boot is the car; the other projects are interchangeable parts for specific roads.

> The Spring ecosystem is a LEGO system: every brick uses the same stud interface (the IoC container). Spring Boot is the base plate. Spring Data, Security, Cloud, and Batch are specialist bricks that snap on without modification.

**One insight:** You never use "Spring" - you always use a specific combination of Spring projects. Knowing which brick does what is the whole skill.

---

### 🔩 First Principles Explanation

**CORE INVARIANTS:**

1. Every Spring project integrates via the IoC container (beans, lifecycle, events)
2. Spring Boot auto-configures any Spring project that is on the classpath
3. Each project is independently versioned and can be used without others
4. Integration with third-party libraries is handled by "starter" dependencies
5. All projects follow the same configuration property namespace pattern (`spring.datasource.*`, `spring.security.*`)

**DERIVED DESIGN:**

From invariants 1 + 2 → dropping a starter JAR on the classpath is sufficient to activate a full subsystem.
From invariant 3 → you can use Spring Data without Spring Security; you can use Spring Batch without Spring Cloud.
From invariant 5 → `application.yml` is the single configuration surface for the entire ecosystem.

**THE TRADE-OFFS:**

**Gain:** Consistent programming model, shared lifecycle, unified configuration, coordinated version management via Spring Boot BOM (Bill of Materials).

**Cost:** The BOM constrains version choices; upgrading Spring Boot can force major upgrades across all dependent projects simultaneously.

**ESSENTIAL vs ACCIDENTAL COMPLEXITY:**

**Essential:** Managing a dozen integration domains (databases, queues, REST, security, batch) is inherently complex. The ecosystem complexity mirrors real enterprise complexity.

**Accidental:** Historical naming inconsistencies (why is it "Spring Batch" but "Spring Data JPA" not "Spring JPA"?) add cognitive overhead without technical necessity.

---

### 🧪 Thought Experiment

**SETUP:** Your application needs REST APIs, a database, authentication, scheduled jobs, and an event queue.

**WHAT HAPPENS WITHOUT the ecosystem map:**

You research each need independently: pick a REST framework, pick an ORM, pick an auth library, pick a scheduler, pick a messaging client. Each has its own configuration model, lifecycle, and connection pooling strategy. You write integration glue code for each. Total: ~500 lines of infrastructure before any business logic.

**WHAT HAPPENS WITH the ecosystem map:**

You add five starter dependencies. Spring Boot auto-configures a `DispatcherServlet` (MVC), `DataSource` (Data JPA), `SecurityFilterChain` (Security), `@Scheduled` executor (Boot), and `RabbitTemplate` or `KafkaTemplate` (AMQP/Kafka). Total infrastructure code: ~50 lines of `application.yml` properties.

**THE INSIGHT:**

The ecosystem map is a _pre-computed set of integration decisions_. Every starter encodes the community's best-practice wiring for that domain, saving each project from rediscovering it.

---

### 🧠 Mental Model / Analogy

> The Spring ecosystem is a city's utility infrastructure. Spring Framework is the underground pipe network (the shared container). Spring Boot is the city planning office that connects utilities to each building automatically. Spring Data, Security, Cloud, and Batch are specialised utility companies (water, electricity, gas, telecoms) that each plug into the same underground network.

**Element mapping:**

- Underground pipe network → Spring Framework IoC container
- City planning office → Spring Boot auto-configuration
- Water utility → Spring Data (database access)
- Electricity utility → Spring Security (authentication/authorisation)
- Telecom utility → Spring Cloud (distributed systems / service mesh)
- Industrial power plant → Spring Batch (bulk data processing)

Where this analogy breaks down: unlike utilities, Spring projects can be combined freely in one application - you can have Spring Data AND Spring Batch AND Spring Cloud all active simultaneously.

---

### 📶 Gradual Depth - Four Levels

**Level 1 - What it is (anyone can understand):**
Spring is not one thing - it is a family of tools. The main tool (Spring Framework) holds everything together. Spring Boot makes starting a project easy. The rest of the family handles specific jobs: database access, security, cloud services, batch jobs.

**Level 2 - How to use it (junior developer):**
Go to [start.spring.io](https://start.spring.io), pick the capabilities you need (Web, JPA, Security, etc.), and download. Each checkbox adds a "starter" that Spring Boot auto-configures. You get a working skeleton in seconds with all the selected Spring projects wired together.

**Level 3 - How it works (mid-level engineer):**
Each Spring project ships a `spring.factories` (pre-Boot 3) or `AutoConfiguration.imports` (Boot 3+) file listing `@AutoConfiguration` classes. When Spring Boot scans the classpath at startup, it finds these files and conditionally applies the configuration based on what jars are present and what properties are set. This is the auto-configuration engine.

**Level 4 - Why it was designed this way (senior/staff):**
The BOM (Bill of Materials) model, where Spring Boot declares compatible versions for all ecosystem projects, was a deliberate choice to eliminate "dependency hell". Before the BOM, developers manually resolved version conflicts between Spring Framework, Hibernate, Jackson, and Tomcat. The BOM encodes the Spring team's integration-tested version matrix as a single parent POM dependency. The trade-off: the BOM creates a "blessing radius" - you can only easily use BOM-managed versions.

**Expert Thinking Cues:**

- `spring-boot-dependencies` BOM is the single source of truth for all Spring ecosystem versions
- `@ConditionalOnClass`, `@ConditionalOnMissingBean`, and `@ConditionalOnProperty` are the three core auto-configuration conditions
- Each Spring project has its own release cadence; the BOM absorbs coordination overhead

---

### ⚙️ How It Works (Mechanism)

The ecosystem integration mechanism:

1. Developer adds `spring-boot-starter-data-jpa` to `pom.xml` or `build.gradle`
2. The starter pulls in Spring Data JPA, Hibernate, Spring JDBC, HikariCP, and the Spring Boot auto-config module
3. At startup, `AutoConfigurationImportSelector` scans `META-INF/spring/org.springframework.boot.autoconfigure.AutoConfiguration.imports`
4. It finds `DataSourceAutoConfiguration`, `JpaRepositoriesAutoConfiguration`, `HibernateJpaAutoConfiguration`
5. Each `@AutoConfiguration` class checks conditions: `@ConditionalOnClass(DataSource.class)`, `@ConditionalOnMissingBean(DataSource.class)`
6. If conditions pass, the auto-configuration registers beans (`DataSource`, `EntityManagerFactory`, `JpaTransactionManager`)
7. The developer's `@Repository` interfaces are detected and proxy implementations generated by Spring Data

---

### 🔄 The Complete Picture - End-to-End Flow

**NORMAL FLOW:**

```
[pom.xml / build.gradle]
     |
     ├─ spring-boot-starter-web
     |    └─ Spring MVC + Tomcat + Jackson
     |          ← YOU ARE HERE (dependency selection)
     ├─ spring-boot-starter-data-jpa
     |    └─ Spring Data + Hibernate + HikariCP
     |
     ├─ spring-boot-starter-security
     |    └─ Spring Security + Filter chain
     |
[Spring Boot startup]
     |
     ├─ Auto-configuration fires per starter
     ├─ Beans registered: DataSource, EntityManager,
     |   SecurityFilterChain, DispatcherServlet
     |
[Application running]
     ├─ HTTP request → Security filter → MVC controller
     ├─ Controller → Service → Repository (JPA)
     └─ Response returned
```

**FAILURE PATH:**

- Auto-configuration condition not met → starter silently inactive; no bean registered → `NoSuchBeanDefinitionException` at first use
- BOM version conflict overridden manually → runtime `ClassNotFoundException` or `NoSuchMethodError`
- Two starters register conflicting beans → `BeanDefinitionOverrideException`

**WHAT CHANGES AT SCALE:**

Large teams use Spring Boot's auto-configuration exclusion (`spring.autoconfigure.exclude`) and custom `@Configuration` classes to override defaults. Platform teams publish internal starters that encode company-specific defaults (custom `DataSource`, tracing, audit logging) using the same auto-configuration mechanism.

---

### 💻 Code Example

**BAD - manually wiring what starters provide:**

```java
// Manually constructing what spring-boot-starter-data-jpa
// would auto-configure
@Configuration
public class ManualJpaConfig {
    @Bean
    public DataSource dataSource() {
        HikariConfig cfg = new HikariConfig();
        cfg.setJdbcUrl("jdbc:postgresql://...");
        // 15 more lines of boilerplate...
        return new HikariDataSource(cfg);
    }
    // + EntityManagerFactory, TransactionManager...
}
```

**GOOD - let the starter and auto-configuration do the work:**

```yaml
# application.yml - the only config needed
spring:
  datasource:
    url: jdbc:postgresql://localhost:5432/mydb
    username: app
    password: secret
  jpa:
    hibernate:
      ddl-auto: validate
```

```java
// pom.xml addition only:
// <dependency>
//   <groupId>org.springframework.boot</groupId>
//   <artifactId>spring-boot-starter-data-jpa</artifactId>
// </dependency>

@Repository
public interface OrderRepository
        extends JpaRepository<Order, Long> {
    List<Order> findByCustomerId(Long customerId);
}
```

**How to test / verify correctness:**

```java
// Verify auto-configuration applied correctly
@SpringBootTest
class EcosystemWiringTest {
    @Autowired ApplicationContext ctx;

    @Test
    void dataSourceBeanPresent() {
        assertThat(ctx.getBean(DataSource.class))
            .isInstanceOf(HikariDataSource.class);
    }
}
```

---

### ⚖️ Comparison Table

| Spring Project    | Domain                          | Typical Starter                        |
| ----------------- | ------------------------------- | -------------------------------------- |
| Spring Framework  | IoC container, AOP, MVC core    | (always present)                       |
| Spring Boot       | Auto-configuration, packaging   | `spring-boot-starter`                  |
| Spring Data JPA   | Relational DB via JPA/Hibernate | `spring-boot-starter-data-jpa`         |
| Spring Data Redis | Redis cache/store access        | `spring-boot-starter-data-redis`       |
| Spring Security   | AuthN/AuthZ, OAuth2             | `spring-boot-starter-security`         |
| Spring MVC        | REST and web layer              | `spring-boot-starter-web`              |
| Spring WebFlux    | Reactive web layer              | `spring-boot-starter-webflux`          |
| Spring Batch      | Bulk data processing            | `spring-boot-starter-batch`            |
| Spring Cloud      | Distributed systems patterns    | platform-specific starters             |
| Spring AMQP       | RabbitMQ integration            | `spring-boot-starter-amqp`             |
| Spring Kafka      | Apache Kafka integration        | `spring-kafka`                         |
| Spring AI         | LLM / AI model integration      | `spring-ai-openai-spring-boot-starter` |

---

### ⚠️ Common Misconceptions

| Misconception                           | Reality                                                                                                                                                                          |
| --------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| "Spring Boot contains everything"       | Spring Boot is the assembler. The actual functionality lives in Spring Framework, Spring Data, Spring Security, etc. Boot just auto-wires them.                                  |
| "I need Spring Cloud for microservices" | Spring Cloud adds distributed systems _patterns_ (service discovery, circuit breaking, config server). A microservice with a REST API and database only needs Boot + MVC + Data. |
| "Spring Data replaces Hibernate"        | Spring Data is a repository abstraction _layer on top of_ Hibernate (or other ORMs). Hibernate still does the SQL.                                                               |
| "One Spring version for everything"     | Each Spring project has its own version. Spring Boot's BOM aligns them. Overriding a single version without checking compatibility is dangerous.                                 |
| "Spring AI is experimental"             | Spring AI reached GA (1.0) in 2024 and is production-supported with adapters for OpenAI, Azure OpenAI, Anthropic, Ollama, and vector stores.                                     |

---

### 🚨 Failure Modes & Diagnosis

**Mode 1: Auto-configuration silently inactive**

**Symptom:** Expected bean (e.g., `DataSource`) is missing; `NoSuchBeanDefinitionException` at runtime.

**Root Cause:** Starter JAR not on classpath, or auto-configuration condition not met (e.g., no `spring.datasource.url` property set).

**Diagnostic:**

```bash
# List all auto-configuration conditions evaluated at startup
java -jar app.jar --debug 2>&1 | grep "Did not match"
# Or via Actuator:
curl http://localhost:8080/actuator/conditions | jq .
```

**Fix:** Add the missing starter dependency or set the required property.

**Prevention:** Use `@SpringBootTest` slices (`@DataJpaTest`, `@WebMvcTest`) to verify each layer independently.

---

**Mode 2: Dependency version conflict**

**Symptom:** `NoSuchMethodError` or `ClassNotFoundException` at runtime despite successful compilation.

**Root Cause:** A transitive dependency was overridden to a version incompatible with the Spring Boot BOM.

**Diagnostic:**

```bash
# Maven: show effective dependency tree
mvn dependency:tree -Dverbose | grep "conflict"
# Gradle:
./gradlew dependencies --configuration runtimeClasspath
```

**Fix:** Remove the manual version override and let the Spring Boot BOM manage the version.

**Prevention:** Never override BOM-managed versions without checking the Spring Boot release notes.

---

**Mode 3: Starter pulls in unwanted auto-configuration (Security failure mode)**

**Symptom:** Adding `spring-boot-starter-security` causes all endpoints to return HTTP 401 unexpectedly.

**Root Cause:** Spring Security auto-configuration secures all endpoints by default - intentional secure-by-default behaviour.

**Diagnostic:**

```bash
logging.level.org.springframework.security=DEBUG
# Look for filter chain matches and access denied reasons
```

**Fix:**

```java
@Bean
public SecurityFilterChain filterChain(HttpSecurity http)
        throws Exception {
    http.authorizeHttpRequests(auth -> auth
        .requestMatchers("/public/**").permitAll()
        .anyRequest().authenticated());
    return http.build();
}
```

**Prevention:** Always explicitly define a `SecurityFilterChain` bean when adding the security starter.

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**

- [[SPR-001 - What Is Spring - History and Philosophy]] - the foundation the ecosystem builds on
- [[SPR-006 - IoC (Inversion of Control)]] - the shared container concept
- [[SPR-067 - Auto-Configuration]] - the mechanism connecting ecosystem projects

**Builds On This (learn these next):**

- [[SPR-003 - Why Spring Boot Changed Java Development]] - how Boot unified the ecosystem
- [[SPR-051 - Spring Cloud Overview]] - the distributed systems layer
- [[SPR-071 - Spring Data JPA]] - the data access layer

**Alternatives / Comparisons:**

- [[SPR-004 - Spring vs Jakarta EE vs Micronaut vs Quarkus]] - competing ecosystems
- Micronaut Framework (SPR-057) - compile-time DI with a similar module structure
- Quarkus Framework (SPR-059) - Kubernetes-native alternative ecosystem

---

### 📌 Quick Reference Card

```
+----------------------------------------------------------+
| WHAT IT IS    | Family of Spring projects on shared IoC   |
| PROBLEM       | Navigating 20+ projects without a map      |
| KEY INSIGHT   | Framework=engine; Boot=assembler; rest=parts|
| USE WHEN      | Selecting which Spring projects to include |
| AVOID WHEN    | -                                          |
| TRADE-OFF     | BOM consistency vs version flexibility     |
| ONE-LINER     | start.spring.io = the ecosystem menu       |
| NEXT EXPLORE  | SPR-003 (Boot), SPR-067 (Auto-Config)      |
+----------------------------------------------------------+
```

**If you remember only 3 things:**

1. Spring Framework is the shared IoC container core - all projects integrate through it
2. Spring Boot auto-configures whatever Spring projects are on the classpath
3. The BOM (Bill of Materials) manages all version compatibility - never override it casually

**Interview one-liner:** "The Spring ecosystem is a family of projects sharing a common IoC container core, each addressing a specific integration domain, coordinated via Spring Boot auto-configuration and a version BOM."

---

### 💎 Transferable Wisdom

**Reusable Engineering Principle:** Large ecosystems stay manageable through _layered abstraction_: a shared kernel (IoC), a configuration layer (Boot), and domain-specific modules. This is the same pattern as the Linux kernel + systemd + userland applications.

**Where else this pattern appears:**

- **AWS SDK** - a shared `SdkClient` kernel, service-specific clients (S3Client, DynamoDbClient), and a Regions/Credentials configuration layer
- **npm ecosystem** - Node.js core + Express/Koa as assemblers + domain packages (Mongoose, Passport, Bull)
- **Eclipse plugin ecosystem** - OSGi container as the shared kernel; each plugin contributes extension points consumed by others

---

### 💡 The Surprising Truth

The [start.spring.io](https://start.spring.io) project initialiser processes over **1 million project generation requests per month**. It is the single most-used onboarding tool in the Java ecosystem. More significantly, it acts as an implicit standard: the dependency combinations it offers define what the community considers "blessed" combinations. A technology that is not offered as a starter on start.spring.io is effectively invisible to most new Spring developers - making inclusion there a significant competitive advantage for any Java library.

---

### 🧠 Think About This Before We Continue

**Question 1 (A - System Interaction):** When Spring Boot auto-configures a `DataSource` and an `EntityManagerFactory`, they must start and stop in a specific order. What mechanism ensures the connection pool is ready before the JPA layer tries to use it?

_Hint:_ Look at `@DependsOn` and `SmartLifecycle` ordering in [[SPR-069 - Spring Boot Startup Lifecycle]] and compare with how Spring Batch depends on a `DataSource`.

**Question 2 (B - Scale):** A large monolith imports 30 Spring starter dependencies. How does this affect startup time, memory footprint, and how might you measure the contribution of each starter?

_Hint:_ Use Spring Boot Actuator's `/actuator/startup` endpoint (Spring Boot 2.4+) and compare startup snapshots with and without specific starters.

**Question 3 (F - Comparison):** Micronaut and Quarkus also offer an ecosystem of modules with a similar starter/auto-configuration concept. What is the fundamental technical difference in _how_ their module activation works compared to Spring Boot's runtime classpath scanning approach?

_Hint:_ Compare Spring Boot's `@ConditionalOnClass` (evaluated at JVM startup) with Micronaut's compile-time bean factory generation in [[SPR-058 - Micronaut vs Spring Boot]].
