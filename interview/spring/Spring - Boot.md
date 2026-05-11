---
layout: default
title: "Spring - Boot"
parent: "Spring"
grand_parent: "Interview Mastery"
nav_order: 2
permalink: /interview/spring/boot/
topic: Spring
subtopic: Boot
keywords:
  - Auto-Configuration
  - Starters and Dependencies
  - Properties and Profiles
  - Actuator
  - Embedded Server
difficulty_range: easy to medium
status: in-progress
version: 3
---

**Keywords covered in this file:**

- [Auto-Configuration](#auto-configuration)
- [Starters and Dependencies](#starters-and-dependencies)
- [Properties and Profiles](#properties-and-profiles)
- [Actuator](#actuator)
- [Embedded Server](#embedded-server)

# Auto-Configuration

**TL;DR** - Spring Boot auto-configuration automatically creates beans based on classpath contents, existing beans, and properties - eliminating hundreds of lines of manual @Bean configuration while remaining fully overridable.
---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
Configuring a Spring web application with JPA, security, and caching requires 200+ lines of XML or Java config: DataSource, EntityManagerFactory, TransactionManager, DispatcherServlet, security filter chain, cache managers. Every project repeats this boilerplate.

**THE BREAKING POINT:**
A new microservice requires 3 days of configuration before writing a single line of business logic. Configuration errors cause cryptic startup failures. Teams copy-paste config between projects, propagating outdated settings.

**THE INVENTION MOMENT:**
"This is exactly why Spring Boot auto-configuration was created."
---

### 📘 Textbook Definition

[TODO: 2-4 sentences. Formal. Technically precise.]
---

### ⏱️ Understand It in 30 Seconds

**One line:**
[TODO: 15 words max. Zero jargon.]

**One analogy:**
> [TODO: 2-3 sentence real-world analogy.]

**One insight:**
[TODO: What separates knowing the name from understanding it.]
---

### 🔩 First Principles Explanation

**CORE INVARIANTS:**
1. [TODO: Always true about this concept]
2. [TODO: Always true about this concept]
3. [TODO: Always true about this concept]

**DERIVED DESIGN:**
[TODO: How the invariants force the design.]

**THE TRADE-OFFS:**
**Gain:** [TODO]
**Cost:** [TODO]

**ESSENTIAL vs ACCIDENTAL COMPLEXITY:**
**Essential:** [TODO]
**Accidental:** [TODO]
---

### 🧠 Mental Model / Analogy

> [TODO: Primary analogy in blockquote.]

- "[TODO: Analogy element]" -> [technical element]
- "[TODO: Analogy element]" -> [technical element]
- "[TODO: Analogy element]" -> [technical element]

Where this analogy breaks down: [TODO: 1 sentence.]
---

### 📶 Gradual Depth - Five Levels

**Level 1 - What it is (anyone can understand):**
Spring Boot looks at what's on your classpath and automatically configures everything. Add `spring-boot-starter-web` -> you get an embedded Tomcat, a DispatcherServlet, and JSON serialization. Zero config needed.

**Level 2 - How to use it (junior developer):**

```java
// This is ALL you need for a web app with JPA:
@SpringBootApplication
public class App {
    public static void main(String[] args) {
        SpringApplication.run(App.class, args);
    }
}
// spring-boot-starter-web -> Tomcat + Jackson
// spring-boot-starter-data-jpa -> DataSource +
//   EntityManager + TransactionManager
// All configured automatically!
```

**Level 3 - How it works (mid-level engineer):**

Auto-configuration is conditional:

```java
// Example: DataSource auto-configuration
@AutoConfiguration
@ConditionalOnClass(DataSource.class)
@ConditionalOnMissingBean(DataSource.class)
public class DataSourceAutoConfiguration {
    @Bean
    @ConditionalOnProperty(
        prefix = "spring.datasource",
        name = "url")
    public DataSource dataSource(
            DataSourceProperties props) {
        return props.initializeDataSourceBuilder()
            .build();
    }
}
```

Key conditions:

- `@ConditionalOnClass` - class exists on classpath
- `@ConditionalOnMissingBean` - no user-defined bean of this type
- `@ConditionalOnProperty` - property is set
- `@ConditionalOnWebApplication` - web environment detected

**Override rule:** If you define your own `@Bean DataSource`, auto-config backs off (`@ConditionalOnMissingBean`).

**Level 4 - Mastery (senior/staff+ engineer):**

**How auto-configuration classes are discovered:**

```
META-INF/spring/
  org.springframework.boot.autoconfigure.
  AutoConfiguration.imports
```

This file lists all auto-configuration classes. Spring Boot loads them, evaluates their conditions, and registers only those that match.

**Debugging auto-configuration:**

```properties
# application.properties
debug=true
# Prints ConditionEvaluationReport at startup:
# Positive matches (applied)
# Negative matches (skipped, with reason)
```

**Ordering:**

```java
@AutoConfiguration(
    before = SecurityAutoConfiguration.class,
    after = DataSourceAutoConfiguration.class)
```


**Level 5 - Distinguished (expert thinking):**
[TODO: Cross-domain pattern recognition. Expert heuristics.
 What would you change if redesigning today?
 How does this compose at extreme scale?]
---

### How It Works (Mechanism)

[TODO: Internal mechanics. Data flow. Key steps.
 4-8 sentences covering implementation details.]
---

### 🔄 Complete Picture - End-to-End Flow

**NORMAL FLOW:**
[TODO] -> [TODO] -> [THIS CONCEPT <- YOU ARE HERE]
       -> [TODO]

**FAILURE PATH:**
[TODO: cascade -> observable symptom]

**WHAT CHANGES AT SCALE:**
[TODO: 2-3 sentences on behaviour at 10x/100x/1000x load.]
---

### 💻 Code Example

**Overriding auto-configuration:**

```java
// Auto-config creates HikariDataSource
// To customize: just set properties
// spring.datasource.url=jdbc:postgresql://...
// spring.datasource.hikari.maximum-pool-size=20

// To fully replace: define your own bean
@Configuration
public class CustomDataSourceConfig {
    @Bean
    public DataSource dataSource() {
        // Auto-config backs off!
        return new CustomDataSource();
    }
}
```
---

### 📌 Quick Reference Card

**WHAT IT IS:** [TODO]
**PROBLEM IT SOLVES:** [TODO]
**KEY INSIGHT:** [TODO]
**USE WHEN:** [TODO]
**AVOID WHEN:** [TODO]
**ANTI-PATTERN:** [TODO]
**TRADE-OFF:** [TODO]
**ONE-LINER:** [TODO]
**KEY NUMBERS:** [TODO: 2-3 critical thresholds/defaults/limits]

**If you remember only 3 things:**

1. Auto-config uses `@ConditionalOn*` to decide what to configure
2. Your `@Bean` definitions always win (auto-config backs off via `@ConditionalOnMissingBean`)
3. `debug=true` shows exactly what was auto-configured and why

**Interview one-liner:**
"Auto-configuration conditionally creates beans based on classpath, properties, and existing beans, always backing off when user-defined beans exist, debuggable with `debug=true`."
---

### ✅ Mastery Checklist

**You've mastered this when you can:**
1. **EXPLAIN:** [TODO: Teach to a junior in 2 min without notes]
2. **DEBUG:** [TODO: Diagnose a specific failure from symptoms]
3. **DECIDE:** [TODO: Choose this vs alternative under pressure]
4. **BUILD:** [TODO: Implement/configure in production context]
5. **EXTEND:** [TODO: Apply principle to a different domain]---

### 💡 The Surprising Truth

[TODO: 2-4 sentences. One counterintuitive fact.
 Specific. Makes this concept permanently memorable.]
---

### ⚖️ Comparison Table

[TODO: Include if 2+ named alternatives exist for Auto-Configuration. Otherwise remove this section.]
---

### ⚠️ Common Misconceptions

| # | Misconception | Reality |
|---|---------------|---------|
| 1 | [TODO] | [TODO] |
| 2 | [TODO] | [TODO] |
| 3 | [TODO] | [TODO] |
| 4 | [TODO] | [TODO] |
---

### 🚨 Failure Modes and Diagnosis

**Failure Mode 1: [TODO]**
**Symptom:** [TODO]
**Root Cause:** [TODO]
**Diagnostic:**
```
[TODO: real diagnostic command]
```
**Fix:** [TODO: BAD then GOOD]
**Prevention:** [TODO]

**Failure Mode 2: [TODO]**
**Symptom:** [TODO]
**Root Cause:** [TODO]
**Diagnostic:**
```
[TODO: real diagnostic command]
```
**Fix:** [TODO: BAD then GOOD]
**Prevention:** [TODO]

**Failure Mode 3: [TODO]**
**Symptom:** [TODO]
**Root Cause:** [TODO]
**Diagnostic:**
```
[TODO: real diagnostic command]
```
**Fix:** [TODO: BAD then GOOD]
**Prevention:** [TODO]
---

### 🎯 Interview Deep-Dive

**Q1: How does @SpringBootApplication work?**

_Why they ask:_ Tests understanding of the bootstrap.

_Strong answer:_

`@SpringBootApplication` is a meta-annotation combining:

1. `@SpringBootConfiguration` (= `@Configuration`): This class is a config source
2. `@EnableAutoConfiguration`: Load and apply auto-configuration classes
3. `@ComponentScan`: Scan this package and sub-packages for @Component classes

```java
// Equivalent to:
@Configuration
@EnableAutoConfiguration
@ComponentScan(basePackages = "com.myapp")
public class App {}
```

`@EnableAutoConfiguration` triggers:

- Loading `AutoConfiguration.imports` file
- Evaluating all `@ConditionalOn*` annotations
- Registering beans for matching auto-configs

Component scan default: the package of the `@SpringBootApplication` class and all sub-packages. This is why the main class should be in the root package.

---

**Q2: How do you exclude an auto-configuration?**

_Why they ask:_ Tests practical configuration knowledge.

_Strong answer:_

Three ways:

```java
// 1. In annotation
@SpringBootApplication(
    exclude = SecurityAutoConfiguration.class)

// 2. In properties
spring.autoconfigure.exclude=\
  org.springframework.boot.autoconfigure\
  .security.servlet.SecurityAutoConfiguration

// 3. Custom condition (advanced)
@Configuration
@ConditionalOnProperty(
    name = "security.enabled",
    havingValue = "true",
    matchIfMissing = false)
public class SecurityConfig { }
```

Common exclusions:

- `DataSourceAutoConfiguration` (don't want auto DB)
- `SecurityAutoConfiguration` (during development)
- `ErrorMvcAutoConfiguration` (custom error handling)
---

### 🔗 Related Keywords

**Prerequisites (understand these first):**
- [TODO] - [why needed]
- [TODO] - [why needed]

**Builds on this (learn these next):**
- [TODO] - [what it adds]
- [TODO] - [what it adds]

**Alternatives / Comparisons:**
- [TODO] - [when to prefer it]
- [TODO] - [when to prefer it]


---

---

# Properties and Profiles

**TL;DR** - Spring Boot externalizes configuration through properties/YAML files with environment-specific profiles, allowing the same code to run differently across dev/staging/prod without recompilation.
---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
Database URLs, API keys, and feature flags hardcoded in source code. Deploying to production requires code changes and recompilation. Secrets leak into version control.
---

### 📘 Textbook Definition

[TODO: 2-4 sentences. Formal. Technically precise.]
---

### ⏱️ Understand It in 30 Seconds

**One line:**
[TODO: 15 words max. Zero jargon.]

**One analogy:**
> [TODO: 2-3 sentence real-world analogy.]

**One insight:**
[TODO: What separates knowing the name from understanding it.]
---

### 🔩 First Principles Explanation

**CORE INVARIANTS:**
1. [TODO: Always true about this concept]
2. [TODO: Always true about this concept]
3. [TODO: Always true about this concept]

**DERIVED DESIGN:**
[TODO: How the invariants force the design.]

**THE TRADE-OFFS:**
**Gain:** [TODO]
**Cost:** [TODO]

**ESSENTIAL vs ACCIDENTAL COMPLEXITY:**
**Essential:** [TODO]
**Accidental:** [TODO]
---

### 🧠 Mental Model / Analogy

> [TODO: Primary analogy in blockquote.]

- "[TODO: Analogy element]" -> [technical element]
- "[TODO: Analogy element]" -> [technical element]
- "[TODO: Analogy element]" -> [technical element]

Where this analogy breaks down: [TODO: 1 sentence.]
---

### 📶 Gradual Depth - Five Levels

**Level 1 - What it is (anyone can understand):**
Configuration values live outside your code in properties files. Different environments (dev, prod) use different files automatically.

**Level 2 - How to use it (junior developer):**

```yaml
# application.yml (default)
server:
  port: 8080
spring:
  datasource:
    url: jdbc:h2:mem:testdb

# application-prod.yml (activated by profile)
spring:
  datasource:
    url: jdbc:postgresql://prod-db:5432/app
```

```java
@Value("${server.port}")
private int port;

// Or type-safe binding (preferred):
@ConfigurationProperties(prefix = "app")
public record AppConfig(
    String name,
    int maxRetries,
    Duration timeout) {}
```

**Level 3 - How it works (mid-level engineer):**

**Property source order (highest priority wins):**

1. Command-line args (`--server.port=9090`)
2. JNDI attributes
3. System properties (`-Dserver.port=9090`)
4. Environment variables (`SERVER_PORT=9090`)
5. `application-{profile}.yml`
6. `application.yml`
7. `@PropertySource` annotations
8. Default values (`@Value("${x:default}")`)

**Profiles:**

```bash
# Activate via:
java -jar app.jar --spring.profiles.active=prod
# Or env var:
SPRING_PROFILES_ACTIVE=prod
```

**Level 4 - Mastery (senior/staff+ engineer):**

**@ConfigurationProperties validation:**

```java
@ConfigurationProperties(prefix = "app.db")
@Validated
public class DbProps {
    @NotBlank private String url;
    @Min(1) @Max(100) private int poolSize;
    @DurationUnit(ChronoUnit.SECONDS)
    private Duration timeout = Duration.ofSeconds(30);
}
// Fails at startup if validation fails!
```

**Relaxed binding:** `app.max-retries`, `APP_MAX_RETRIES`, `app.maxRetries` all bind to `maxRetries` field.

**Profile-specific beans:**

```java
@Configuration
@Profile("dev")
public class DevConfig {
    @Bean public DataSource mockDataSource() {}
}
```


**Level 5 - Distinguished (expert thinking):**
[TODO: Cross-domain pattern recognition. Expert heuristics.
 What would you change if redesigning today?
 How does this compose at extreme scale?]
---

### How It Works (Mechanism)

[TODO: Internal mechanics. Data flow. Key steps.
 4-8 sentences covering implementation details.]
---

### 🔄 Complete Picture - End-to-End Flow

**NORMAL FLOW:**
[TODO] -> [TODO] -> [THIS CONCEPT <- YOU ARE HERE]
       -> [TODO]

**FAILURE PATH:**
[TODO: cascade -> observable symptom]

**WHAT CHANGES AT SCALE:**
[TODO: 2-3 sentences on behaviour at 10x/100x/1000x load.]
---

### 📌 Quick Reference Card

**WHAT IT IS:** [TODO]
**PROBLEM IT SOLVES:** [TODO]
**KEY INSIGHT:** [TODO]
**USE WHEN:** [TODO]
**AVOID WHEN:** [TODO]
**ANTI-PATTERN:** [TODO]
**TRADE-OFF:** [TODO]
**ONE-LINER:** [TODO]
**KEY NUMBERS:** [TODO: 2-3 critical thresholds/defaults/limits]

**If you remember only 3 things:**

1. Property precedence: CLI > env vars > profile-specific > application.yml
2. Use `@ConfigurationProperties` for type-safe, validated binding
3. Profiles switch environment configs: `spring.profiles.active=prod`
---

### ✅ Mastery Checklist

**You've mastered this when you can:**
1. **EXPLAIN:** [TODO: Teach to a junior in 2 min without notes]
2. **DEBUG:** [TODO: Diagnose a specific failure from symptoms]
3. **DECIDE:** [TODO: Choose this vs alternative under pressure]
4. **BUILD:** [TODO: Implement/configure in production context]
5. **EXTEND:** [TODO: Apply principle to a different domain]---

### 💡 The Surprising Truth

[TODO: 2-4 sentences. One counterintuitive fact.
 Specific. Makes this concept permanently memorable.]
---

### ⚖️ Comparison Table

[TODO: Include if 2+ named alternatives exist for Properties and Profiles. Otherwise remove this section.]
---

### ⚠️ Common Misconceptions

| # | Misconception | Reality |
|---|---------------|---------|
| 1 | [TODO] | [TODO] |
| 2 | [TODO] | [TODO] |
| 3 | [TODO] | [TODO] |
| 4 | [TODO] | [TODO] |
---

### 🚨 Failure Modes and Diagnosis

**Failure Mode 1: [TODO]**
**Symptom:** [TODO]
**Root Cause:** [TODO]
**Diagnostic:**
```
[TODO: real diagnostic command]
```
**Fix:** [TODO: BAD then GOOD]
**Prevention:** [TODO]

**Failure Mode 2: [TODO]**
**Symptom:** [TODO]
**Root Cause:** [TODO]
**Diagnostic:**
```
[TODO: real diagnostic command]
```
**Fix:** [TODO: BAD then GOOD]
**Prevention:** [TODO]

**Failure Mode 3: [TODO]**
**Symptom:** [TODO]
**Root Cause:** [TODO]
**Diagnostic:**
```
[TODO: real diagnostic command]
```
**Fix:** [TODO: BAD then GOOD]
**Prevention:** [TODO]
---

### 🎯 Interview Deep-Dive

**Q1: How do you handle secrets in Spring Boot?**

_Why they ask:_ Tests security awareness.

_Strong answer:_

Never commit secrets to properties files. Options:

1. **Environment variables:** `SPRING_DATASOURCE_PASSWORD=secret`
2. **Spring Cloud Config Server:** Centralized, encrypted config
3. **Vault integration:** `spring-cloud-vault` fetches secrets at startup
4. **Kubernetes secrets:** Mounted as env vars or files
5. **AWS Secrets Manager / Azure Key Vault:** Cloud-native secret stores

```yaml
# Reference env var in properties:
spring:
  datasource:
    password: ${DB_PASSWORD}
```

For local development: use `.env` files (gitignored) or Spring Cloud Config with dev profile.
---

### 🔗 Related Keywords

**Prerequisites (understand these first):**
- [TODO] - [why needed]
- [TODO] - [why needed]

**Builds on this (learn these next):**
- [TODO] - [what it adds]
- [TODO] - [what it adds]

**Alternatives / Comparisons:**
- [TODO] - [when to prefer it]
- [TODO] - [when to prefer it]


---

---

# Actuator

**TL;DR** - Spring Boot Actuator exposes production-ready endpoints for health checks, metrics, environment inspection, and operational diagnostics without writing any custom code.
---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
Operations team asks: "Is the service healthy? How many requests/second? What's the memory usage? What configuration is active?" Without Actuator, you write custom health endpoints, metrics collection, and diagnostic tools for every service.
---

### 📘 Textbook Definition

[TODO: 2-4 sentences. Formal. Technically precise.]
---

### ⏱️ Understand It in 30 Seconds

**One line:**
[TODO: 15 words max. Zero jargon.]

**One analogy:**
> [TODO: 2-3 sentence real-world analogy.]

**One insight:**
[TODO: What separates knowing the name from understanding it.]
---

### 🔩 First Principles Explanation

**CORE INVARIANTS:**
1. [TODO: Always true about this concept]
2. [TODO: Always true about this concept]
3. [TODO: Always true about this concept]

**DERIVED DESIGN:**
[TODO: How the invariants force the design.]

**THE TRADE-OFFS:**
**Gain:** [TODO]
**Cost:** [TODO]

**ESSENTIAL vs ACCIDENTAL COMPLEXITY:**
**Essential:** [TODO]
**Accidental:** [TODO]
---

### 🧠 Mental Model / Analogy

> [TODO: Primary analogy in blockquote.]

- "[TODO: Analogy element]" -> [technical element]
- "[TODO: Analogy element]" -> [technical element]
- "[TODO: Analogy element]" -> [technical element]

Where this analogy breaks down: [TODO: 1 sentence.]
---

### 📶 Gradual Depth - Five Levels

**Level 1 - What it is (anyone can understand):**
Add one dependency and get dozens of operational endpoints: health check, metrics, environment info, thread dump, heap dump - all built in.

**Level 2 - How to use it (junior developer):**

```xml
<dependency>
    <groupId>org.springframework.boot</groupId>
    <artifactId>
        spring-boot-starter-actuator</artifactId>
</dependency>
```

```yaml
management:
  endpoints:
    web:
      exposure:
        include: health, info, metrics, env
  endpoint:
    health:
      show-details: always
```

Key endpoints:

- `/actuator/health` - liveness/readiness
- `/actuator/metrics` - application metrics
- `/actuator/env` - configuration properties
- `/actuator/info` - build info, git info
- `/actuator/threaddump` - thread state

**Level 3 - How it works (mid-level engineer):**

**Custom health indicators:**

```java
@Component
public class DatabaseHealthIndicator
        implements HealthIndicator {
    public Health health() {
        if (db.isConnected())
            return Health.up()
                .withDetail("latency", "2ms")
                .build();
        return Health.down()
            .withDetail("error", "timeout")
            .build();
    }
}
```

**Kubernetes probes:**

```yaml
management:
  endpoint:
    health:
      probes:
        enabled: true
# Exposes:
# /actuator/health/liveness
# /actuator/health/readiness
```

**Level 4 - Mastery (senior/staff+ engineer):**

**Metrics with Micrometer:**

```java
@Service
public class OrderService {
    private final Counter orderCounter;
    private final Timer orderTimer;

    public OrderService(MeterRegistry reg) {
        this.orderCounter = reg.counter(
            "orders.created");
        this.orderTimer = reg.timer(
            "orders.processing.time");
    }

    public Order create(OrderReq req) {
        return orderTimer.record(() -> {
            Order o = process(req);
            orderCounter.increment();
            return o;
        });
    }
}
```

**Security:** Never expose all endpoints publicly:

```yaml
management:
  server:
    port: 8081 # separate port
  endpoints:
    web:
      exposure:
        include: health, info
        # Only expose safe endpoints publicly
```


**Level 5 - Distinguished (expert thinking):**
[TODO: Cross-domain pattern recognition. Expert heuristics.
 What would you change if redesigning today?
 How does this compose at extreme scale?]
---

### How It Works (Mechanism)

[TODO: Internal mechanics. Data flow. Key steps.
 4-8 sentences covering implementation details.]
---

### 🔄 Complete Picture - End-to-End Flow

**NORMAL FLOW:**
[TODO] -> [TODO] -> [THIS CONCEPT <- YOU ARE HERE]
       -> [TODO]

**FAILURE PATH:**
[TODO: cascade -> observable symptom]

**WHAT CHANGES AT SCALE:**
[TODO: 2-3 sentences on behaviour at 10x/100x/1000x load.]
---

### 📌 Quick Reference Card

**WHAT IT IS:** [TODO]
**PROBLEM IT SOLVES:** [TODO]
**KEY INSIGHT:** [TODO]
**USE WHEN:** [TODO]
**AVOID WHEN:** [TODO]
**ANTI-PATTERN:** [TODO]
**TRADE-OFF:** [TODO]
**ONE-LINER:** [TODO]
**KEY NUMBERS:** [TODO: 2-3 critical thresholds/defaults/limits]

**If you remember only 3 things:**

1. `/actuator/health` for Kubernetes probes (liveness + readiness)
2. Micrometer + `/actuator/metrics` for Prometheus/Grafana integration
3. Secure actuator endpoints - never expose env/heapdump publicly
---

### ✅ Mastery Checklist

**You've mastered this when you can:**
1. **EXPLAIN:** [TODO: Teach to a junior in 2 min without notes]
2. **DEBUG:** [TODO: Diagnose a specific failure from symptoms]
3. **DECIDE:** [TODO: Choose this vs alternative under pressure]
4. **BUILD:** [TODO: Implement/configure in production context]
5. **EXTEND:** [TODO: Apply principle to a different domain]---

### 💡 The Surprising Truth

[TODO: 2-4 sentences. One counterintuitive fact.
 Specific. Makes this concept permanently memorable.]
---

### ⚖️ Comparison Table

[TODO: Include if 2+ named alternatives exist for Actuator. Otherwise remove this section.]
---

### ⚠️ Common Misconceptions

| # | Misconception | Reality |
|---|---------------|---------|
| 1 | [TODO] | [TODO] |
| 2 | [TODO] | [TODO] |
| 3 | [TODO] | [TODO] |
| 4 | [TODO] | [TODO] |
---

### 🚨 Failure Modes and Diagnosis

**Failure Mode 1: [TODO]**
**Symptom:** [TODO]
**Root Cause:** [TODO]
**Diagnostic:**
```
[TODO: real diagnostic command]
```
**Fix:** [TODO: BAD then GOOD]
**Prevention:** [TODO]

**Failure Mode 2: [TODO]**
**Symptom:** [TODO]
**Root Cause:** [TODO]
**Diagnostic:**
```
[TODO: real diagnostic command]
```
**Fix:** [TODO: BAD then GOOD]
**Prevention:** [TODO]

**Failure Mode 3: [TODO]**
**Symptom:** [TODO]
**Root Cause:** [TODO]
**Diagnostic:**
```
[TODO: real diagnostic command]
```
**Fix:** [TODO: BAD then GOOD]
**Prevention:** [TODO]
---

### 🎯 Interview Deep-Dive

**Q1: How do you implement custom health checks for Kubernetes?**

_Why they ask:_ Tests production deployment knowledge.

_Strong answer:_

```java
// Readiness: can this instance serve traffic?
@Component
public class ReadinessCheck
        implements HealthIndicator {
    public Health health() {
        if (!cache.isWarmedUp())
            return Health.down().build();
        if (!db.connectionPoolHealthy())
            return Health.down().build();
        return Health.up().build();
    }
}
```

Kubernetes deployment:

```yaml
livenessProbe:
  httpGet:
    path: /actuator/health/liveness
    port: 8080
  initialDelaySeconds: 30
readinessProbe:
  httpGet:
    path: /actuator/health/readiness
    port: 8080
  initialDelaySeconds: 10
```

Liveness = "is the JVM stuck?" (restart if failing)
Readiness = "can it handle traffic?" (remove from LB if failing)
---

### 🔗 Related Keywords

**Prerequisites (understand these first):**
- [TODO] - [why needed]
- [TODO] - [why needed]

**Builds on this (learn these next):**
- [TODO] - [what it adds]
- [TODO] - [what it adds]

**Alternatives / Comparisons:**
- [TODO] - [when to prefer it]
- [TODO] - [when to prefer it]


---

---

# Embedded Server

**TL;DR** - Spring Boot embeds the web server (Tomcat, Jetty, or Netty) inside the application JAR, eliminating external server deployment and enabling self-contained executable applications.
---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
Traditional Java web apps are packaged as WAR files and deployed to external Tomcat/WebLogic/JBoss servers. DevOps must manage server installations, version compatibility, shared classpaths, and deployment scripts across environments.
---

### 📘 Textbook Definition

[TODO: 2-4 sentences. Formal. Technically precise.]
---

### ⏱️ Understand It in 30 Seconds

**One line:**
[TODO: 15 words max. Zero jargon.]

**One analogy:**
> [TODO: 2-3 sentence real-world analogy.]

**One insight:**
[TODO: What separates knowing the name from understanding it.]
---

### 🔩 First Principles Explanation

**CORE INVARIANTS:**
1. [TODO: Always true about this concept]
2. [TODO: Always true about this concept]
3. [TODO: Always true about this concept]

**DERIVED DESIGN:**
[TODO: How the invariants force the design.]

**THE TRADE-OFFS:**
**Gain:** [TODO]
**Cost:** [TODO]

**ESSENTIAL vs ACCIDENTAL COMPLEXITY:**
**Essential:** [TODO]
**Accidental:** [TODO]
---

### 🧠 Mental Model / Analogy

> [TODO: Primary analogy in blockquote.]

- "[TODO: Analogy element]" -> [technical element]
- "[TODO: Analogy element]" -> [technical element]
- "[TODO: Analogy element]" -> [technical element]

Where this analogy breaks down: [TODO: 1 sentence.]
---

### 📶 Gradual Depth - Five Levels

**Level 1 - What it is (anyone can understand):**
Your application IS the server. `java -jar app.jar` starts everything - no separate Tomcat installation needed.

**Level 2 - How to use it (junior developer):**

```yaml
server:
  port: 8080
  tomcat:
    threads:
      max: 200
      min-spare: 10
    connection-timeout: 5s
    max-connections: 10000
```

**Level 3 - How it works (mid-level engineer):**

Embedded server options:

| Server   | Default For                 | Style                        | Best For         |
| -------- | --------------------------- | ---------------------------- | ---------------- |
| Tomcat   | spring-boot-starter-web     | Servlet (thread-per-request) | Most apps        |
| Jetty    | (swap Tomcat)               | Servlet                      | Low memory       |
| Undertow | (swap Tomcat)               | Servlet                      | High performance |
| Netty    | spring-boot-starter-webflux | Non-blocking (reactive)      | High concurrency |

Swap Tomcat for Undertow:

```xml
<dependency>
    <groupId>org.springframework.boot</groupId>
    <artifactId>spring-boot-starter-web</artifactId>
    <exclusions>
        <exclusion>
            <groupId>org.springframework.boot</groupId>
            <artifactId>
                spring-boot-starter-tomcat</artifactId>
        </exclusion>
    </exclusions>
</dependency>
<dependency>
    <groupId>org.springframework.boot</groupId>
    <artifactId>
        spring-boot-starter-undertow</artifactId>
</dependency>
```

**Level 4 - Mastery (senior/staff+ engineer):**

**Tomcat tuning for production:**

```yaml
server:
  tomcat:
    threads:
      max: 200 # platform threads (pre VT)
    accept-count: 100 # queue when threads full
    max-connections: 8192
    connection-timeout: 20s
    keep-alive-timeout: 60s
```

**Virtual threads (Spring Boot 3.2+):**

```yaml
spring:
  threads:
    virtual:
      enabled: true
# Tomcat uses virtual thread per request
# No thread pool sizing needed!
```

**Graceful shutdown:**

```yaml
server:
  shutdown: graceful
spring:
  lifecycle:
    timeout-per-shutdown-phase: 30s
# Stops accepting new connections
# Waits for in-flight requests to complete
# Times out after 30s
```


**Level 5 - Distinguished (expert thinking):**
[TODO: Cross-domain pattern recognition. Expert heuristics.
 What would you change if redesigning today?
 How does this compose at extreme scale?]
---

### How It Works (Mechanism)

[TODO: Internal mechanics. Data flow. Key steps.
 4-8 sentences covering implementation details.]
---

### 🔄 Complete Picture - End-to-End Flow

**NORMAL FLOW:**
[TODO] -> [TODO] -> [THIS CONCEPT <- YOU ARE HERE]
       -> [TODO]

**FAILURE PATH:**
[TODO: cascade -> observable symptom]

**WHAT CHANGES AT SCALE:**
[TODO: 2-3 sentences on behaviour at 10x/100x/1000x load.]
---

### 📌 Quick Reference Card

**WHAT IT IS:** [TODO]
**PROBLEM IT SOLVES:** [TODO]
**KEY INSIGHT:** [TODO]
**USE WHEN:** [TODO]
**AVOID WHEN:** [TODO]
**ANTI-PATTERN:** [TODO]
**TRADE-OFF:** [TODO]
**ONE-LINER:** [TODO]
**KEY NUMBERS:** [TODO: 2-3 critical thresholds/defaults/limits]

**If you remember only 3 things:**

1. Default: embedded Tomcat with 200 threads, configurable via properties
2. `spring.threads.virtual.enabled=true` (Boot 3.2+) for virtual threads
3. `server.shutdown=graceful` for zero-downtime deployments
---

### ✅ Mastery Checklist

**You've mastered this when you can:**
1. **EXPLAIN:** [TODO: Teach to a junior in 2 min without notes]
2. **DEBUG:** [TODO: Diagnose a specific failure from symptoms]
3. **DECIDE:** [TODO: Choose this vs alternative under pressure]
4. **BUILD:** [TODO: Implement/configure in production context]
5. **EXTEND:** [TODO: Apply principle to a different domain]---

### 💡 The Surprising Truth

[TODO: 2-4 sentences. One counterintuitive fact.
 Specific. Makes this concept permanently memorable.]
---

### ⚖️ Comparison Table

[TODO: Include if 2+ named alternatives exist for Embedded Server. Otherwise remove this section.]
---

### ⚠️ Common Misconceptions

| # | Misconception | Reality |
|---|---------------|---------|
| 1 | [TODO] | [TODO] |
| 2 | [TODO] | [TODO] |
| 3 | [TODO] | [TODO] |
| 4 | [TODO] | [TODO] |
---

### 🚨 Failure Modes and Diagnosis

**Failure Mode 1: [TODO]**
**Symptom:** [TODO]
**Root Cause:** [TODO]
**Diagnostic:**
```
[TODO: real diagnostic command]
```
**Fix:** [TODO: BAD then GOOD]
**Prevention:** [TODO]

**Failure Mode 2: [TODO]**
**Symptom:** [TODO]
**Root Cause:** [TODO]
**Diagnostic:**
```
[TODO: real diagnostic command]
```
**Fix:** [TODO: BAD then GOOD]
**Prevention:** [TODO]

**Failure Mode 3: [TODO]**
**Symptom:** [TODO]
**Root Cause:** [TODO]
**Diagnostic:**
```
[TODO: real diagnostic command]
```
**Fix:** [TODO: BAD then GOOD]
**Prevention:** [TODO]
---

### 🎯 Interview Deep-Dive

**Q1: How would you tune Tomcat for a high-traffic API?**

_Why they ask:_ Tests production performance knowledge.

_Strong answer:_

For an API handling 5000 req/sec with 50ms avg latency:

Thread calculation: `5000 req/sec * 0.05 sec/req = 250 concurrent threads needed`

```yaml
server:
  tomcat:
    threads:
      max: 300 # 250 + headroom
      min-spare: 50 # pre-warmed
    accept-count: 200 # queue before reject
    max-connections: 10000
  compression:
    enabled: true
    min-response-size: 1024
```

With virtual threads (Java 21 + Boot 3.2):

```yaml
spring.threads.virtual.enabled: true
# No thread pool sizing needed
# But add Semaphore for DB connection limiting
```

Also consider: connection pooling (HikariCP sizing), response compression, keep-alive tuning, and HTTP/2 (`server.http2.enabled=true`).
---

### 🔗 Related Keywords

**Prerequisites (understand these first):**
- [TODO] - [why needed]
- [TODO] - [why needed]

**Builds on this (learn these next):**
- [TODO] - [what it adds]
- [TODO] - [what it adds]

**Alternatives / Comparisons:**
- [TODO] - [when to prefer it]
- [TODO] - [when to prefer it]
