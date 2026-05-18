---
version: 1
layout: default
title: "Auto-Configuration"
parent: "Spring Core"
grand_parent: "Technical Mastery"
nav_order: 70
permalink: /technical-mastery/spring/auto-configuration/
id: SPR-088
category: Spring Core
difficulty: ★★★
depends_on: ApplicationContext, Bean, BeanFactoryPostProcessor, "@Configuration"
used_by: Spring Boot Starter, Spring Boot Actuator, Spring Data JPA
related: "@Conditional, @EnableAutoConfiguration, spring.factories"
tags:
  - spring
  - springboot
  - internals
  - deep-dive
---

⚡ TL;DR - Spring Boot's auto-configuration scans the classpath and conditionally wires beans for you based on what's present, so you get a working `DataSource` or `WebMvcConfigurer` without writing a single `@Bean` definition.

| #401            | Category: Spring Core                                              | Difficulty: ★★★ |
| :-------------- | :----------------------------------------------------------------- | :-------------- |
| **Depends on:** | ApplicationContext, Bean, BeanFactoryPostProcessor, @Configuration |                 |
| **Used by:**    | Spring Boot Starter, Spring Boot Actuator, Spring Data JPA         |                 |
| **Related:**    | @Conditional, @EnableAutoConfiguration, spring.factories           |                 |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
Pre-Spring Boot, adding a database to a Spring application required: declaring a `DataSource` bean, configuring a `JdbcTemplate` bean, configuring an `EntityManagerFactory` bean, a `TransactionManager` bean, setting up Hibernate properties, registering a `PlatformTransactionManager`. That's 6–10 `@Bean` methods of boilerplate XML or Java config - identical across every application. Every developer writes the same wiring code. Typos cause runtime failures. New team members spend days understanding configuration scaffolding before writing any business logic.

**THE BREAKING POINT:**
At scale across hundreds of microservices, this boilerplate is multiplied. When a new version of Hibernate changes a property name, every service must be updated manually. When a new security best practice requires an additional filter, it's manually added to every application.

**THE INVENTION MOMENT:**
"This is exactly why auto-configuration was created."

---

### 📘 Textbook Definition

**Auto-configuration** is Spring Boot's mechanism for automatically configuring the Spring ApplicationContext based on the libraries (JARs) present on the classpath and the properties supplied in `application.properties`. Auto-configuration classes are annotated with `@Configuration` and `@Conditional*` annotations that evaluate at context startup - if the condition is satisfied (e.g., "DataSource class is on the classpath AND no DataSource bean is already defined"), the configuration class is applied and its beans are registered. Auto-configuration classes are discovered via `META-INF/spring/org.springframework.boot.autoconfigure.AutoConfiguration.imports` (Spring Boot 2.7+) or `META-INF/spring.factories` (earlier versions). The feature is enabled by `@EnableAutoConfiguration` which is included in `@SpringBootApplication`.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
Spring Boot looks at what's on your classpath and configures it for you - unless you've already configured it yourself.

**One analogy:**

> Auto-configuration is like a smart hotel room that detects what you've brought with you. If you brought a laptop, it turns on the WiFi. If you brought running shoes, it leaves a city map. If you already have your own towels, it doesn't provide theirs. It sets up sensible defaults for what's present and backs off when you've customized something.

**One insight:**
The core principle is "back off when the user has configured it manually." The `@ConditionalOnMissingBean` annotation means "apply this auto-config only if the user hasn't already defined one." This makes auto-configuration additive and safe to override.

---

### 🔩 First Principles Explanation

**CORE INVARIANTS:**

1. Auto-configuration applies only when its conditions are satisfied - specifically, `@ConditionalOnClass` (class is on classpath) and `@ConditionalOnMissingBean` (no user-defined bean of this type exists).
2. Auto-configuration always backs off when the user explicitly defines a bean - user-defined beans take precedence.
3. Auto-configuration is applied after the application's own `@Configuration` classes, ensuring user beans are registered first.

**DERIVED DESIGN:**
The design follows the Open/Closed Principle: the framework is open for extension (you can add custom beans) and closed for modification (you don't need to change framework code to override defaults).

Consider `DataSourceAutoConfiguration`. It's `@ConditionalOnClass(DataSource.class)` - applied only if HikariCP (or another JDBC driver) is on the classpath. It's `@ConditionalOnMissingBean(DataSource.class)` - applied only if you haven't defined your own `DataSource`. So: add `spring-boot-starter-data-jpa` to your pom, set `spring.datasource.url`, and you get a fully configured HikariCP connection pool automatically. Define your own `@Bean DataSource` in a `@Configuration` class, and the auto-configuration steps aside.

**THE TRADE-OFFS:**

**Gain:** Zero-boilerplate setup for common use cases; consistent configuration across all Spring Boot apps; centrally maintained by the Spring team (updated when best practices change).

**Cost:** Magic - when things go wrong, the failure is in auto-configuration code you didn't write, which is hard to debug without understanding the mechanism. Over-reliance on auto-config can obscure what beans are actually in the context. Testing can be complicated by unexpected auto-configured beans.

---

### 🧪 Thought Experiment

**SETUP:**
You add `spring-boot-starter-security` to your `pom.xml`. You run your app. All your endpoints now require Basic Auth. You never wrote a security configuration. How?

**TRACE THE MECHANISM:**

1. `spring-boot-starter-security` brings `spring-security-web` and `spring-security-config` onto the classpath.
2. At context startup, Spring scans `AutoConfiguration.imports`.
3. `SecurityAutoConfiguration` is evaluated: `@ConditionalOnClass(AuthenticationManager.class)` - passes (spring-security-web is on classpath).
4. `SpringBootWebSecurityConfiguration` is evaluated: `@ConditionalOnDefaultWebSecurity @ConditionalOnMissingBean(WebSecurityConfigurerAdapter.class)` - passes (you haven't written any security config).
5. A default `SecurityFilterChain` is registered that requires HTTP Basic on all paths.
6. Result: your app is now secured without a line of security code.

**THE INSIGHT:**
The behavior you didn't write is the auto-configuration kicking in. When you define your own `@Configuration class SecurityConfig extends WebSecurityConfigurerAdapter`, `@ConditionalOnMissingBean` trips, the default chain is NOT registered, and your config takes over completely.

---

### 🧠 Mental Model / Analogy

> Think of auto-configuration as a smart assistant who sets up your office before you arrive. They check what equipment you've requested (dependencies on classpath) and set up the defaults. If you've already arranged your desk a specific way (defined your own beans), they leave it alone. If you haven't touched something, they configure it sensibly. The rulebook they follow is the `@Conditional` annotations.

- "Checking what equipment you've requested" → `@ConditionalOnClass` checking classpath
- "Seeing you've already arranged your desk" → `@ConditionalOnMissingBean` finding your bean
- "Leaving it alone" → auto-config backs off
- "Setting up defaults" → auto-config registers its beans
- "The rulebook" → `@Conditional` annotations on each auto-config class

Where this analogy breaks down: unlike a one-time office setup, conditions are evaluated dynamically at each application startup - so changing a dependency or property changes what's auto-configured.

---

### 📶 Gradual Depth - Four Levels

**Level 1 - What it is (anyone can understand):**
When you add a library to a Spring Boot project (like a database driver), Spring Boot automatically sets up everything needed to use it - connection pool, templates, repositories - without you writing configuration code. You just add the dependency and set a URL.

**Level 2 - How to use it (junior developer):**
Auto-configuration is invisible when it works. To understand what's been auto-configured, run your app with `--debug` flag: it prints a "CONDITIONS EVALUATION REPORT" listing which auto-configurations matched and which were skipped and why. To override an auto-configured bean, simply declare your own `@Bean` of the same type in a `@Configuration` class. To disable a specific auto-configuration: `@SpringBootApplication(exclude = {DataSourceAutoConfiguration.class})`.

**Level 3 - How it works (mid-level engineer):**
`@SpringBootApplication` includes `@EnableAutoConfiguration` which imports `AutoConfigurationImportSelector`. This selector reads `META-INF/spring/org.springframework.boot.autoconfigure.AutoConfiguration.imports` (a list of 150+ auto-configuration class names). Spring registers all of them as candidate `@Configuration` classes. During context refresh, `@Conditional` annotations are evaluated: `@ConditionalOnClass` checks `ClassLoader.loadClass()`, `@ConditionalOnMissingBean` checks the `BeanDefinitionRegistry`. Auto-configuration classes are `@AutoConfigureAfter` and `@AutoConfigureBefore` ordered relative to each other to ensure correct initialization sequence.

**Level 4 - Why it was designed this way (senior/staff):**
Auto-configuration was designed with the explicit "convention over configuration" philosophy from Ruby on Rails, applied to the JVM ecosystem. The key insight was that 80% of applications use the same configuration for a given library - so codifying that in auto-config and overriding it for the remaining 20% is more efficient than requiring everyone to write it. The `@ConditionalOnMissingBean` safety valve was crucial: it means adding a dependency to a Spring Boot project can never silently override your explicit configuration - your beans always win. The transition from `spring.factories` to `AutoConfiguration.imports` in Spring Boot 2.7/3.0 improved startup time by separating auto-configuration from other factory lookups.

---

### ⚙️ How It Works (Mechanism)

```
┌─────────────────────────────────────────────────────────┐
│ AUTO-CONFIGURATION RESOLUTION AT STARTUP                │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  @SpringBootApplication                                 │
│    → @EnableAutoConfiguration                           │
│      → AutoConfigurationImportSelector                  │
│        → reads AutoConfiguration.imports               │
│          → 140+ auto-config class names loaded          │
│                                                         │
│  For each AutoConfiguration class:                      │
│    1. @ConditionalOnClass: is HikariCP on classpath?    │
│       NO  → skip DataSourceAutoConfiguration            │
│       YES → evaluate next condition                     │
│                                                         │
│    2. @ConditionalOnMissingBean: user DataSource exists?│
│       YES → skip (user-defined bean wins)               │
│       NO  → register HikariDataSource bean              │
│                                                         │
│    3. @ConditionalOnProperty: spring.datasource.url set?│
│       NO  → skip connection pool creation               │
│       YES → create HikariDataSource from properties     │
│                                                         │
│  Result: ApplicationContext has DataSource bean         │
│          without a single line of user config           │
└─────────────────────────────────────────────────────────┘
```

---

### 💻 Code Example

**Example 1 - What auto-configuration looks like (Spring's source):**

```java
// This is what DataSourceAutoConfiguration looks like internally
// You don't write this - Spring Boot provides it

@AutoConfiguration(before = SqlInitializationAutoConfiguration.class)
@ConditionalOnClass({ DataSource.class, EmbeddedDatabaseType.class })
@ConditionalOnMissingBean(type = "io.r2dbc.spi.ConnectionFactory")
@EnableConfigurationProperties(DataSourceProperties.class)
@Import(DataSourcePoolMetadataProvidersConfiguration.class)
public class DataSourceAutoConfiguration {

    @Configuration(proxyBeanMethods = false)
    @ConditionalOnEmbeddedDatabase
    static class EmbeddedDatabaseConfiguration {
        // in-memory DB setup for H2/Derby
    }

    @Configuration(proxyBeanMethods = false)
    @ConditionalOnMissingBean({ DataSource.class,
        XADataSource.class })
    @Import({ DataSourceConfiguration.Hikari.class,
              DataSourceConfiguration.Tomcat.class })
    static class PooledDataSourceConfiguration {
        // HikariCP pool setup from spring.datasource.*
    }
}
```

**Example 2 - Overriding auto-configuration with your own bean:**

```java
// BAD: modifying application.properties while also
// relying on auto-config DataSource for different DB
// - creates confusion about which DataSource wins

// GOOD: override with explicit @Bean - auto-config backs off
@Configuration
public class DataSourceConfig {

    @Bean // your DataSource → DataSourceAutoConfiguration skipped
    public DataSource dataSource(
            @Value("${db.url}") String url,
            @Value("${db.user}") String user) {
        HikariConfig config = new HikariConfig();
        config.setJdbcUrl(url);
        config.setUsername(user);
        config.setMaximumPoolSize(20); // override default 10
        return new HikariDataSource(config);
    }
}
```

**Example 3 - Disabling and debugging auto-configuration:**

```java
// Disable specific auto-config (e.g., in tests without DB)
@SpringBootApplication(exclude = {
    DataSourceAutoConfiguration.class,
    HibernateJpaAutoConfiguration.class
})
public class MyApplication {
    public static void main(String[] args) {
        SpringApplication.run(MyApplication.class, args);
    }
}
```

```bash
# See the full CONDITIONS EVALUATION REPORT at startup
java -jar myapp.jar --debug 2>&1 | grep -A3 "DataSource"

# Or via Spring Boot Actuator
curl http://localhost:8080/actuator/conditions
```

---

### ⚖️ Comparison Table

| Approach                 | Config Lines   | Flexibility         | Debuggability           | Best For                |
| ------------------------ | -------------- | ------------------- | ----------------------- | ----------------------- |
| **Auto-Configuration**   | 0–3 properties | Override with @Bean | Hard without debug mode | Standard use cases      |
| Manual @Configuration    | 20–50+ lines   | Full control        | Easy to trace           | Custom/complex setup    |
| XML Configuration        | 30–100+ lines  | Full control        | Verbose                 | Legacy systems          |
| @Import specific configs | 5–15 lines     | Selective           | Moderate                | Partial auto-config use |

How to choose: Use auto-configuration (the default) for standard patterns. Switch to explicit `@Bean` definitions when you need non-default behavior. Use `exclude` to disable auto-configuration for test slices or when you have conflicting beans.

---

### ⚠️ Common Misconceptions

| Misconception                                                         | Reality                                                                                                                                                          |
| --------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Auto-configuration reads my `@Configuration` classes and adds to them | Auto-config is in separate JARs; it adds beans to the SAME context; conditions check the unified bean registry                                                   |
| You need to understand auto-configuration to use Spring Boot          | For basic use: no. For debugging production issues or writing starters: yes, deeply                                                                              |
| `spring.factories` is still used in Spring Boot 3                     | Auto-configuration discovery moved to `AutoConfiguration.imports` in Spring Boot 2.7 / 3.0; `spring.factories` is still supported but deprecated for auto-config |
| Auto-configuration adds every possible bean                           | Only conditions that evaluate to true result in beans; unused auto-configs are skipped and have zero runtime cost                                                |
| Excluding an auto-config with `exclude` removes the dependency        | It only prevents the auto-configuration class from running; the dependency JAR is still on the classpath                                                         |

---

### 🚨 Failure Modes & Diagnosis

**1. Unexpected Bean in Context (Auto-config Conflict)**

**Symptom:** `NoUniqueBeanDefinitionException: expected single matching bean but found 2`; or unexpected behavior from an auto-configured bean you didn't know existed.

**Root Cause:** An auto-configuration class registered a bean that conflicts with your manually defined bean, or two auto-configurations each registered the same bean type.

**Diagnostic:**

```bash
# Run with --debug to see what auto-config was applied
java -jar myapp.jar --debug | grep "DataSource"

# Via Actuator (runtime)
curl http://localhost:8080/actuator/conditions | \
  python -m json.tool | grep -A5 "DataSource"

# Print all beans in context
curl http://localhost:8080/actuator/beans | \
  python -m json.tool | grep dataSource
```

**Fix:**

```java
// Exclude the conflicting auto-configuration
@SpringBootApplication(exclude = {
    DataSourceAutoConfiguration.class
})

// OR: add your own @Primary bean to win the disambiguation
@Bean @Primary
public DataSource primaryDataSource() { ... }
```

**Prevention:** Run `--debug` startup in a staging environment after adding new dependencies to see what gets auto-configured.

---

**2. Auto-Configuration Not Applying (Missing Condition)**

**Symptom:** Expected bean (e.g., `JdbcTemplate`) is missing; `NoSuchBeanDefinitionException` despite having the dependency on classpath.

**Root Cause:** One of the `@Conditional` conditions failed - usually the required class isn't on classpath (dependency not included), a required property is missing, or you accidentally defined a bean that triggered `@ConditionalOnMissingBean`.

**Diagnostic:**

```bash
# Check NEGATIVE MATCHES in the conditions report
java -jar myapp.jar --debug 2>&1 | \
  grep -A10 "JdbcTemplateAutoConfiguration"

# Output shows which @Conditional failed and why
```

**Fix:**

```xml
<!-- Missing dependency for JdbcTemplate auto-config -->
<dependency>
    <groupId>org.springframework.boot</groupId>
    <artifactId>spring-boot-starter-jdbc</artifactId>
</dependency>
```

**Prevention:** Always check the conditions report when an expected bean is missing; it directly shows which condition failed.

---

**3. Custom Starter Auto-Configuration Not Loading**

**Symptom:** Writing a custom Spring Boot starter; your auto-configuration class exists but its beans are never registered.

**Root Cause:** Auto-configuration class is not listed in `META-INF/spring/org.springframework.boot.autoconfigure.AutoConfiguration.imports` (Spring Boot 3) or `spring.factories` (Spring Boot 2).

**Diagnostic:**

```bash
# Check that the imports file exists in your JAR
jar tf mylib.jar | grep "AutoConfiguration.imports"

# Verify the content
jar xf mylib.jar META-INF/spring/
cat META-INF/spring/\
  org.springframework.boot.autoconfigure.AutoConfiguration.imports
```

**Fix:**

```
# src/main/resources/META-INF/spring/
# org.springframework.boot.autoconfigure.AutoConfiguration.

com.mycompany.MyLibraryAutoConfiguration
```

**Prevention:** When writing custom starters, always verify the imports file is packaged in the JAR and contains your auto-configuration class FQCN.

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**

- `ApplicationContext` - auto-configuration populates the ApplicationContext; understand the container before understanding what fills it
- `Bean` - auto-configuration registers beans; understand bean lifecycle first
- `@Configuration` - auto-configuration classes are `@Configuration` classes with conditions; understand the base pattern first

**Builds On This (learn these next):**

- `Spring Boot Actuator` - uses auto-configuration to expose management endpoints; `@ConditionalOnWebApplication` is a key condition here
- `Spring Boot Startup Lifecycle` - auto-configuration fires during context refresh; understanding startup phases contextualizes when conditions are evaluated
- `Lazy vs Eager Loading` - auto-configured beans follow the same lazy/eager rules as user beans

**Alternatives / Comparisons:**

- `@Import` - manually import specific `@Configuration` classes; more explicit but requires knowledge of class names
- `@ComponentScan` - discovers beans by classpath scanning; does not evaluate conditions; complementary to auto-configuration
- `@Profile` - environment-specific bean activation; coarser-grained than `@Conditional` conditions

---

### 📌 Quick Reference Card

```
┌─────────────────────────────────────────────────────────┐
│ WHAT IT IS   │ Spring Boot conditionally registers beans│
│              │ based on classpath and properties        │
├──────────────┼──────────────────────────────────────────┤
│ PROBLEM IT   │ Boilerplate config code duplicated across│
│ SOLVES       │ every application for common libraries   │
├──────────────┼──────────────────────────────────────────┤
│ KEY INSIGHT  │ @ConditionalOnMissingBean: your beans win│
│              │ - auto-config always backs off           │
├──────────────┼──────────────────────────────────────────┤
│ HOW TO DEBUG │ Start with --debug; check                │
│              │ /actuator/conditions                     │
├──────────────┼──────────────────────────────────────────┤
│ HOW TO       │ Define @Bean of same type (backs off)    │
│ OVERRIDE     │ OR exclude = {SomeAutoConfiguration.class│
├──────────────┼──────────────────────────────────────────┤
│ TRADE-OFF    │ Zero boilerplate vs. "magic" failures    │
│              │ that require knowing internals to debug  │
├──────────────┼──────────────────────────────────────────┤
│ ONE-LINER    │ "It sets up your libraries for you -     │
│              │  and steps aside when you say otherwise" │
├──────────────┼──────────────────────────────────────────┤
│ NEXT EXPLORE │ Spring Boot Actuator →                   │
│              │ Spring Boot Startup Lifecycle            │
└─────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** (TYPE E - Architectural) You're building a Spring Boot starter library that other teams' services will include. The starter needs to provide a `RateLimiter` bean, but only if the user hasn't defined their own, and only if a specific property `mycompany.rate-limiter.enabled=true` is set. Write the exact annotations needed on your auto-configuration class to achieve this. What happens if the user sets the property to true AND defines their own `@Bean RateLimiter`?

**Q2.** (TYPE D - Debugging) A developer adds `spring-boot-starter-security` to an existing Spring Boot service. Suddenly all integration tests fail with 401 Unauthorized. The developer has no `SecurityConfig` class. Trace exactly why this happened using your knowledge of auto-configuration and `@ConditionalOnMissingBean`. What is the minimum code change to restore the tests, and what does that change cause the `@Conditional` to evaluate?
