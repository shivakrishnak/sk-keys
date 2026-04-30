---
layout: default
title: "Auto-Configuration"
parent: "Spring & Spring Boot"
nav_order: 133
permalink: /spring/auto-configuration/
number: "133"
category: Spring & Spring Boot
difficulty: ★★★
depends_on: "@Configuration, @Conditional, BeanFactoryPostProcessor, ApplicationContext"
used_by: "Spring Boot Startup, HikariCP, JPA, Security, Actuator, MVC"
tags: #java, #spring, #springboot, #advanced, #internals, #deep-dive
---

# 133 — Auto-Configuration

`#java` `#spring` `#springboot` `#advanced` `#internals` `#deep-dive`

⚡ TL;DR — Spring Boot's mechanism for automatically configuring beans based on classpath presence, existing beans, and properties — eliminating boilerplate setup for common libraries.

| #133 | Category: Spring & Spring Boot | Difficulty: ★★★ |
|:---|:---|:---|
| **Depends on:** | @Configuration, @Conditional, BeanFactoryPostProcessor, ApplicationContext | |
| **Used by:** | Spring Boot Startup, HikariCP, JPA, Security, Actuator, MVC | |

---

### 📘 Textbook Definition

**Auto-Configuration** is Spring Boot's mechanism for registering `@Configuration` classes conditionally based on the state of the classpath, existing beans, and environment properties. It is driven by `AutoConfigurationImportSelector`, which reads candidate class names from `META-INF/spring/org.springframework.boot.autoconfigure.AutoConfiguration.imports` (Spring Boot 2.7+) and applies `@Conditional` annotations to each — `@ConditionalOnClass`, `@ConditionalOnMissingBean`, `@ConditionalOnProperty`, etc. Auto-configurations fire after user-defined beans are registered, ensuring user configurations always take precedence (`@ConditionalOnMissingBean`). Spring Boot ships ~150 auto-configurations covering databases, web, security, messaging, observability, and more.

---

### 🟢 Simple Definition (Easy)

Auto-Configuration is Spring Boot's "smart default" system. Add `spring-boot-starter-data-jpa` to your classpath and Spring Boot automatically sets up a DataSource, EntityManagerFactory, and TransactionManager — without you writing any configuration code.

---

### 🔵 Simple Definition (Elaborated)

Before Spring Boot, every Spring application needed explicit `@Configuration` classes to set up a DataSource, JPA, transactions, web MVC, and security. Spring Boot maps "library on classpath" to "default configuration for that library." When it detects `spring-jdbc.jar`, it registers `DataSourceAutoConfiguration`. When it detects `spring-security.jar`, it registers `SecurityAutoConfiguration`. Each auto-configuration uses `@Conditional` annotations to activate only when its conditions are met — and backs off when you've already defined your own version of that bean.

---

### 🔩 First Principles Explanation

**The repetition problem Auto-Configuration solves:**

Every Spring MVC application needed the same boilerplate:

```java
// Boilerplate 1: DispatcherServlet setup
// Boilerplate 2: Jackson ObjectMapper configuration
// Boilerplate 3: HikariCP DataSource
// Boilerplate 4: EntityManagerFactory
// Boilerplate 5: JpaTransactionManager
// Boilerplate 6: Error handling
// Boilerplate 7: Content negotiation
// ... × every new project
```

**How Auto-Configuration works — three-phase mechanism:**

```
┌─────────────────────────────────────────────────────┐
│  AUTO-CONFIGURATION MECHANISM                       │
│                                                     │
│  Phase 1: DISCOVERY                                 │
│  @SpringBootApplication triggers                    │
│  @EnableAutoConfiguration                           │
│  → AutoConfigurationImportSelector reads:           │
│    META-INF/spring/                                 │
│    ...AutoConfiguration.imports                     │
│  → ~150 candidate class names loaded               │
│                                                     │
│  Phase 2: FILTERING (BeanFactoryPostProcessor)      │
│  ConfigurationClassPostProcessor evaluates each:    │
│  @ConditionalOnClass: HikariDataSource on classpath?│
│  @ConditionalOnMissingBean: DataSource already?     │
│  @ConditionalOnProperty: spring.datasource.url set? │
│  → Failing conditions: skip this auto-config        │
│                                                     │
│  Phase 3: REGISTRATION                              │
│  Passing auto-configs: their @Bean methods register │
│  beans → normal lifecycle (injection, BPP, etc.)   │
└─────────────────────────────────────────────────────┘
```

---

### ❓ Why Does This Exist (Why Before What)

**WITHOUT Auto-Configuration:**

```
Every Spring project needs:

  DataSource setup:    ~20 lines @Configuration
  JPA setup:           ~30 lines EntityManagerFactory
  Transaction setup:   ~15 lines TransactionManager
  MVC setup:           ~25 lines DispatcherServlet config
  Jackson setup:       ~10 lines ObjectMapper config
  Error handling:      ~20 lines ErrorController

  Total: ~120 lines of config per project
  × 50 microservices = 6,000 lines of identical config

  Change Jackson date format: edit 50 configs
  Upgrade Hibernate: test 50 custom configs
```

**WITH Auto-Configuration:**

```
→ spring.datasource.url=... → DataSource configured
→ spring-boot-starter-data-jpa → JPA fully configured
→ spring-boot-starter-web → MVC + Jackson configured
→ Override: define your own @Bean → auto-config backs off
→ Debug: --debug flag prints ConditionEvaluationReport
→ ~0 lines of config for standard setups
→ Change defaults: override in application.properties
```

---

### 🧠 Mental Model / Analogy

> Auto-Configuration is like a **smart hotel room** that configures itself based on its guest profile. The room system detects you booked the "Business Suite" (spring-boot-starter-web) and automatically sets the room temperature to 22°C (MVC defaults), turns on the desk lamp (Jackson), and pre-stocks the fridge with water (embedded Tomcat). If you call reception and say "I prefer 18°C" (define your own bean), the room honours your preference instead. If you bring your own coffee machine (Jetty on classpath), the in-room machine backs off.

"Room auto-configuring on arrival" = condition-based bean registration
"Guest profile = starter" = classpath detection (@ConditionalOnClass)
"Calling reception with preference" = defining your own @Bean
"Room honours your preference" = @ConditionalOnMissingBean backs off
"Bringing your own coffee machine" = overriding default infrastructure

---

### ⚙️ How It Works (Mechanism)

**Writing a custom Auto-Configuration (library authors):**

```java
// 1. Create the auto-configuration class
@AutoConfiguration
@ConditionalOnClass(AwsS3Client.class)     // only if SDK present
@ConditionalOnMissingBean(S3FileStorage.class) // user hasn't defined one
@EnableConfigurationProperties(S3Properties.class)
public class S3AutoConfiguration {

  @Bean
  @ConditionalOnProperty("cloud.aws.s3.bucket")
  S3FileStorage s3FileStorage(S3Properties props,
                              AwsS3Client client) {
    return new S3FileStorage(client, props.getBucket());
  }

  @Bean
  @ConditionalOnMissingBean(AwsS3Client.class)
  AwsS3Client awsS3Client(AwsProperties aws) {
    return AwsS3Client.builder()
        .region(aws.getRegion())
        .build();
  }
}

// 2. Register it
// File: META-INF/spring/
//   org.springframework.boot.autoconfigure.AutoConfiguration.imports
// Content:
//   com.example.S3AutoConfiguration
```

**Debugging auto-configuration decisions:**

```bash
# Run with --debug to print ConditionEvaluationReport
java -jar app.jar --debug

# Output shows:
# POSITIVE MATCHES (conditions passed → beans registered):
#   DataSourceAutoConfiguration:
#     - @ConditionalOnClass found: HikariDataSource ✅
#     - @ConditionalOnMissingBean: DataSource not found ✅
#     → beans: dataSource, hikariConfig registered

# NEGATIVE MATCHES (conditions failed → beans skipped):
#   MongoAutoConfiguration:
#     - @ConditionalOnClass: MongoClient NOT on classpath ❌
#     → entire auto-config skipped

# EXCLUSIONS (explicitly excluded):
#   SecurityAutoConfiguration:
#     - Excluded via @SpringBootApplication(exclude=...) ❌
```

**Controlling auto-configuration:**

```java
// Exclude specific auto-config
@SpringBootApplication(exclude = {
    SecurityAutoConfiguration.class,
    DataSourceAutoConfiguration.class
})

// Via properties:
// spring.autoconfigure.exclude=
//   org.springframework.boot.autoconfigure.security.SecurityAutoConfiguration

// Override individual auto-configured beans:
@Bean  // this back-pressures the auto-configured DataSource
DataSource myCustomDataSource() {
  // Your custom DataSource — auto-config sees it via
  // @ConditionalOnMissingBean and skips its DataSource
  return customDataSource;
}
```

---

### 🔄 How It Connects (Mini-Map)

```
Spring Boot classpath: spring-boot-starter-data-jpa
        ↓
  @SpringBootApplication
  → @EnableAutoConfiguration
  → AutoConfigurationImportSelector
  → reads AutoConfiguration.imports (~150 candidates)
        ↓
  AUTO-CONFIGURATION (133)  ← you are here
  ConfigurationClassPostProcessor evaluates @Conditional
        ↓
  Passes → beans registered:
  HikariCP (132) via DataSourceAutoConfiguration
  JPA via JpaAutoConfiguration
  MVC via WebMvcAutoConfiguration
  Actuator (134) via ActuatorAutoConfiguration
        ↓
  Your own @Configuration classes always take priority
  (registered first → @ConditionalOnMissingBean = false)
```

---

### 💻 Code Example

**Example 1 — How DataSourceAutoConfiguration works:**

```java
// Simplified from Spring Boot source:
@AutoConfiguration
@ConditionalOnClass({ DataSource.class, EmbeddedDatabase.class })
@ConditionalOnMissingBean(type = {
    "io.r2dbc.spi.ConnectionFactory" })
@EnableConfigurationProperties(DataSourceProperties.class)
@Import({ DataSourcePoolMetadataProvidersConfiguration.class,
          DataSourceCheckpointRestoreConfiguration.class })
public class DataSourceAutoConfiguration {

  @Configuration(proxyBeanMethods = false)
  @Conditional(PooledDataSourceCondition.class)
  @ConditionalOnMissingBean({ DataSource.class,
                              XADataSource.class })
  @Import({ DataSourceConfiguration.Hikari.class,
            DataSourceConfiguration.Tomcat.class,
            DataSourceConfiguration.Dbcp2.class,
            DataSourceConfiguration.OracleUcp.class,
            DataSourceConfiguration.Generic.class })
  protected static class PooledDataSourceConfiguration { }
}
// Condition: if spring-jdbc on classpath AND
//            spring.datasource.url set AND
//            NO DataSource bean already defined:
// → registers HikariCP-backed DataSource
```

**Example 2 — Conditional annotations reference:**

```java
@ConditionalOnClass(HikariDataSource.class)
// Registers only if HikariCP is on the classpath

@ConditionalOnMissingClass("com.zaxxer.hikari.HikariDataSource")
// Registers only if HikariCP is NOT on classpath

@ConditionalOnBean(DataSource.class)
// Registers only if a DataSource bean already exists

@ConditionalOnMissingBean(DataSource.class)
// Registers only if NO DataSource bean is defined

@ConditionalOnProperty(
    prefix = "spring.datasource",
    name = "url",
    matchIfMissing = false)
// Registers only if spring.datasource.url is set

@ConditionalOnWebApplication(type = SERVLET)
// Registers only for servlet-based web applications

@ConditionalOnExpression("${features.new-algo:false}")
// Registers if SpEL expression evaluates to true
```

---

### 🔁 Flow / Lifecycle

```
1. SpringApplication.run() starts
2. ApplicationContext created (AnnotationConfigServletWebServerAppContext)
3. @SpringBootApplication scanned
   → @EnableAutoConfiguration triggers AutoConfigurationImportSelector
4. ~150 auto-config class names loaded from classpath
5. ConfigurationClassPostProcessor (BFPP) runs:
   Each auto-config class evaluated for @Conditional
   → ~100 fail (@ConditionalOnClass not on classpath)
   → ~50 pass and are registered as @Configuration sources
6. User @Configuration classes registered first (priority)
7. Auto-configuration @Bean methods processed
   @ConditionalOnMissingBean: skip if user already defined
8. All beans instantiated (normal lifecycle)
9. ApplicationReadyEvent published
```

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| Auto-Configuration replaces all Spring configuration | Auto-Configuration provides defaults. User-defined @Configuration always takes precedence — @ConditionalOnMissingBean ensures auto-config backs off |
| Auto-Configuration runs before user beans are registered | User @Configuration classes are processed first, then auto-configurations. This ordering guarantees auto-config sees user beans before deciding whether to register defaults |
| All 150 auto-configurations load at every startup | Only auto-configurations whose @ConditionalOnClass conditions pass (their library is on the classpath) are evaluated. Most are discarded at the class-loading stage |
| You need @EnableAutoConfiguration annotation explicitly | @SpringBootApplication is a composite of @Configuration + @ComponentScan + @EnableAutoConfiguration — you never need to add @EnableAutoConfiguration separately |

---

### 🔥 Pitfalls in Production

**1. Unexpected auto-configuration activating on classpath change**

```java
// BAD: test dependency leaking into production classpath
// pom.xml accidentally has scope=compile for H2:
<dependency>
  <groupId>com.h2database</groupId>
  <artifactId>h2</artifactId>
  <!-- Missing: <scope>test</scope> -->
</dependency>
// → DataSourceAutoConfiguration detects H2 on classpath
// → Configures in-memory H2 database INSTEAD of PostgreSQL
// → App starts with empty H2 in production
// FIX: always use <scope>test</scope> for test DBs

// Diagnose: run with --debug, check POSITIVE MATCHES
```

**2. Custom @Bean not preventing auto-config due to wrong type**

```java
// BAD: defining a different type doesn't satisfy @ConditionalOnMissingBean
@Bean
HikariDataSource mySpecialDataSource() { ... }
// DataSourceAutoConfiguration checks for type DataSource (the interface)
// HikariDataSource IS-A DataSource → usually works
// BUT if @ConditionalOnMissingBean targets a specific implementation type:
// → auto-config may STILL register its own DataSource (secondary!)
// → TWO DataSource beans → NoUniqueBeanDefinitionException!

// GOOD: check what type the @ConditionalOnMissingBean checks
// and match it exactly. Or use @Bean @Primary for clarity
```

---

### 🔗 Related Keywords

- `@Conditional` — the annotation family powering auto-configuration decisions
- `@Configuration / @Bean` — the Java class format each auto-configuration uses
- `BeanFactoryPostProcessor` — auto-configuration evaluated by ConfigurationClassPostProcessor
- `Spring Boot Startup Lifecycle` — auto-configuration fires during refresh phase
- `@ConditionalOnMissingBean` — the key annotation ensuring user config takes priority
- `Spring Boot Actuator` — auto-configured by ActuatorAutoConfiguration when on classpath

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ KEY IDEA     │ Conditionally register @Configuration     │
│              │ classes based on classpath, beans, props; │
│              │ user beans always win via OnMissingBean   │
├──────────────┼───────────────────────────────────────────┤
│ USE WHEN     │ Add starter → get working defaults;       │
│              │ override by defining your own @Bean       │
├──────────────┼───────────────────────────────────────────┤
│ AVOID WHEN   │ Don't fight auto-config — exclude it or   │
│              │ override the specific @Bean you want      │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "Smart hotel room: configures itself for  │
│              │  you, steps aside when you prefer custom."│
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ Spring Boot Actuator (134) →              │
│              │ Spring Boot Startup Lifecycle (135)       │
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** Spring Boot 2.7 changed auto-configuration registration from `META-INF/spring.factories` (a static `EnableAutoConfiguration=...` list) to `META-INF/spring/org.springframework.boot.autoconfigure.AutoConfiguration.imports` (one class per line). Explain why this change was made — what problem with the old `spring.factories` approach caused ordering and class-loading issues — and describe the specific backwards-compatibility challenge for library authors who need to support both Spring Boot 2.x and 3.x simultaneously.

**Q2.** `@ConditionalOnMissingBean` checks whether a bean of the specified type exists in the `ApplicationContext` — but at the time auto-configuration is evaluated, not all user beans may have been registered yet. Explain how Spring Boot guarantees that user-defined beans always win over auto-configured ones — specifically how `ImportAutoConfigurationImportSelector` ordering and `@AutoConfigureAfter`/`@AutoConfigureBefore` annotations enforce the correct evaluation sequence — and describe the failure mode when two auto-configurations have a `@ConditionalOnMissingBean` dependency cycle.

