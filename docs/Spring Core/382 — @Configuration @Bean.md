---
layout: default
title: "@Configuration / @Bean"
parent: "Spring Core"
nav_order: 382
permalink: /spring/configuration-bean/
number: "382"
category: Spring Core
difficulty: ★★☆
depends_on: "Bean, ApplicationContext, BeanFactoryPostProcessor"
used_by: "@Qualifier / @Primary, Auto-Configuration, Bean Lifecycle"
tags: #intermediate, #spring, #architecture, #foundational
---

# 382 — @Configuration / @Bean

`#intermediate` `#spring` `#architecture` `#foundational`

⚡ TL;DR — `@Configuration` marks a class as a Spring configuration source; `@Bean` marks a method within it as a factory for a managed bean. Together they replace XML bean definitions with type-safe Java code.

| #382            | Category: Spring Core                                     | Difficulty: ★★☆ |
| :-------------- | :-------------------------------------------------------- | :-------------- |
| **Depends on:** | Bean, ApplicationContext, BeanFactoryPostProcessor        |                 |
| **Used by:**    | @Qualifier / @Primary, Auto-Configuration, Bean Lifecycle |                 |

---

### 📘 Textbook Definition

`@Configuration` is a class-level annotation that declares the annotated class as a source of bean definitions for the Spring IoC container. It is processed by `ConfigurationClassPostProcessor` (a `BeanDefinitionRegistryPostProcessor`) during the pre-instantiation phase. A `@Configuration` class is itself registered as a bean and is CGLIB-subclassed by Spring to intercept `@Bean` method calls. `@Bean` is a method-level annotation placed inside a `@Configuration` (or `@Component`) class to declare that the method's return value is a bean to be managed by the container. The method name becomes the default bean name; it can be overridden with `@Bean(name = "customName")`. Spring calls `@Bean` methods at most once per scope (singleton: once; prototype: per request) by intercepting calls through the CGLIB proxy on `@Configuration` classes — this is "full mode." When `@Bean` methods appear in `@Component` classes ("lite mode"), CGLIB interception is absent and method calls produce new instances every time. `@Configuration` classes can import other configurations (`@Import`), trigger component scanning (`@ComponentScan`), and load property files (`@PropertySource`).

---

### 🟢 Simple Definition (Easy)

`@Configuration` is a class that contains Spring bean recipes. `@Bean` is one recipe — a method that creates and returns a bean. Spring calls these methods once and manages what they return.

---

### 🔵 Simple Definition (Elaborated)

Before Java-based configuration, Spring beans were declared in XML files. `@Configuration` and `@Bean` replace XML with type-safe Java. A `@Configuration` class is where you write code that builds objects with full control — you can pass constructor arguments, call setters, conditionally create different implementations, and chain beans together. Spring treats the class itself as a bean and CGLIB-proxies it so that calling one `@Bean` method from another returns the same cached singleton instance instead of creating a new one. This is the key difference from a plain `@Component` with `@Bean` methods (lite mode) — without CGLIB proxying, internal `@Bean` method calls create new instances and bypass the container.

---

### 🔩 First Principles Explanation

**Full mode (@Configuration) vs lite mode (@Component + @Bean):**

```java
// ─── FULL MODE: @Configuration ─────────────────────────────────
// CGLIB-proxied: all @Bean method calls go through the container
@Configuration
class FullModeConfig {

    @Bean
    ConnectionPool pool() {
        return new ConnectionPool(10);
    }

    @Bean
    UserRepository userRepo() {
        // Calls pool() — but this call is intercepted by CGLIB proxy
        // Spring returns the SAME singleton ConnectionPool, not a new one
        return new UserRepository(pool()); // ← same instance as pool() above
    }

    @Bean
    OrderRepository orderRepo() {
        return new OrderRepository(pool()); // ← same instance again (singleton)
    }
}
// Result: pool() created ONCE, shared by both repositories

// ─── LITE MODE: @Component + @Bean ────────────────────────────
// No CGLIB proxy: @Bean method calls are plain Java method calls
@Component
class LiteModeConfig {

    @Bean
    ConnectionPool pool() {
        return new ConnectionPool(10); // called each time method is invoked
    }

    @Bean
    UserRepository userRepo() {
        return new UserRepository(pool()); // NEW ConnectionPool — not singleton!
    }

    @Bean
    OrderRepository orderRepo() {
        return new OrderRepository(pool()); // ANOTHER new ConnectionPool!
    }
}
// Result: pool() called 2 times → 3 total ConnectionPool instances (BUG!)
```

**Common @Configuration capabilities:**

```java
@Configuration
@PropertySource("classpath:application.properties") // load property file
@ComponentScan("com.example.services")              // scan for @Components
@Import(SecurityConfig.class)                       // import another @Configuration
public class AppConfig {

    @Value("${db.url}")
    private String dbUrl;

    @Bean
    @Profile("production")          // only register in 'production' profile
    DataSource productionDataSource() {
        HikariConfig cfg = new HikariConfig();
        cfg.setJdbcUrl(dbUrl);
        return new HikariDataSource(cfg);
    }

    @Bean
    @Profile("test")                // register only in 'test' profile
    DataSource embeddedDataSource() {
        return new EmbeddedDatabaseBuilder()
            .setType(EmbeddedDatabaseType.H2)
            .build();
    }

    @Bean
    @ConditionalOnProperty(name = "audit.enabled", havingValue = "true")
    AuditService auditService() {
        return new AuditService();
    }

    // @Bean with explicit init and destroy methods
    @Bean(initMethod = "connect", destroyMethod = "disconnect")
    MessageBrokerClient messageBroker() {
        return new MessageBrokerClient(brokerUrl());
    }
}
```

**Injecting dependencies into @Bean methods:**

```java
@Configuration
class ServiceConfig {

    // Spring injects other beans as method parameters — no @Autowired needed
    @Bean
    OrderService orderService(OrderRepository repo,
                               PaymentGateway gateway,
                               @Qualifier("auditLogger") Logger logger) {
        return new OrderService(repo, gateway, logger);
    }

    // Cross-configuration dependency — parameter resolved from full context
    @Bean
    InvoiceService invoiceService(OrderService orderService) {
        return new InvoiceService(orderService);
    }
}
```

---

### ❓ Why Does This Exist (Why Before What)

WITHOUT `@Configuration` / `@Bean`:

What breaks without it:

1. Bean declarations require XML — no compile-time type safety, no IDE autocompletion on class names.
2. Complex bean construction (conditional logic, computed arguments, multi-step setup) is impossible in XML.
3. Tests cannot easily override individual beans without XML manipulation or subclassing.
4. Third-party library integration (libraries that do not use Spring annotations) requires XML to register as beans.

WITH `@Configuration` / `@Bean`:
→ Full Java type safety — typos in class names are compile errors, not runtime failures.
→ Full Java expressiveness — loops, conditionals, factory methods, and builders for complex bean construction.
→ `@Profile`, `@Conditional`, and `@ConditionalOnProperty` enable environment-specific bean registration in code.
→ Any third-party class can be registered as a bean via `@Bean` without modifying the class.

---

### 🧠 Mental Model / Analogy

> Think of `@Configuration` as a factory blueprint and `@Bean` methods as the individual assembly instructions. The CGLIB proxy on `@Configuration` is like a shared-parts warehouse: when two assembly lines (two `@Bean` methods) both call for "engine block" (`pool()`), the warehouse checks its shelf first — if the engine is already built (singleton cached), it hands out the same one instead of building a new engine from scratch. Without the warehouse (`@Component` lite mode), each assembly line builds its own engine from scratch.

"`@Configuration` class" = the factory blueprint
"`@Bean` method" = individual assembly instructions for one component
"CGLIB proxy" = the shared-parts warehouse (prevents duplicate construction)
"Singleton cached instance" = a component already built and shelved
"`@Component` lite mode" = assembly lines without shared warehouse (each builds its own)

---

### ⚙️ How It Works (Mechanism)

**CGLIB proxying of @Configuration classes:**

```
At startup, ConfigurationClassPostProcessor detects @Configuration classes.
It registers a CGLIB subclass of the @Configuration class as the bean:

  Original:   AppConfig (your class)
  CGLIB proxy: AppConfig$$EnhancerBySpringCGLIB$$abc123
                 → overrides ALL @Bean methods
                 → before each @Bean method runs:
                   1. Is this scope singleton?
                   2. Is the bean already in singletonObjects cache?
                   3. YES → return cached instance (skip method body)
                      NO  → call original method body, cache result

Effect: pool() in @Configuration is called AT MOST ONCE for singletons,
        no matter how many @Bean methods call pool().
```

**@Bean method parameter resolution:**

```
@Bean
OrderService orderService(OrderRepository repo, PaymentGateway gateway) {
    ...
}

Spring resolves parameters:
  1. For each parameter type (OrderRepository, PaymentGateway):
     → Search ApplicationContext by type
     → Apply @Qualifier / @Primary resolution if multiple
     → Inject the resolved bean as the argument
  2. Call the @Bean method with injected arguments
  3. Register return value as bean "orderService"
```

---

### 🔄 How It Connects (Mini-Map)

```
BeanFactoryPostProcessor
(ConfigurationClassPostProcessor processes @Configuration at startup)
        │
        ▼
@Configuration  ◄──── (you are here, part 1)
(container of @Bean declarations; CGLIB-proxied)
        │
        ▼
@Bean  ◄──── (you are here, part 2)
(factory method for a single bean)
        │
        ├──── bean registered in ApplicationContext
        │
        ├──── @Profile / @Conditional → conditional registration
        │
        └──── @Import → compose multiple @Configuration classes
                │
                ▼
        Auto-Configuration
        (Spring Boot's @EnableAutoConfiguration uses @Configuration + @Conditional)
```

---

### 💻 Code Example

**Production-grade multi-datasource configuration:**

```java
@Configuration
@EnableTransactionManagement
public class PersistenceConfig {

    @Bean
    @Primary
    @ConfigurationProperties("spring.datasource.primary")
    DataSource primaryDataSource() {
        return DataSourceBuilder.create().build();
    }

    @Bean
    @ConfigurationProperties("spring.datasource.reporting")
    DataSource reportingDataSource() {
        return DataSourceBuilder.create().build();
    }

    @Bean
    @Primary
    LocalContainerEntityManagerFactoryBean entityManagerFactory(
            DataSource primaryDataSource,               // @Primary injected
            JpaVendorAdapter jpaVendorAdapter) {
        LocalContainerEntityManagerFactoryBean emf =
            new LocalContainerEntityManagerFactoryBean();
        emf.setDataSource(primaryDataSource);
        emf.setJpaVendorAdapter(jpaVendorAdapter);
        emf.setPackagesToScan("com.example.domain");
        return emf;
    }

    @Bean
    @Primary
    PlatformTransactionManager transactionManager(
            EntityManagerFactory entityManagerFactory) {
        return new JpaTransactionManager(entityManagerFactory);
    }

    @Bean
    @ConditionalOnProperty(name = "app.audit.enabled", havingValue = "true")
    AuditingEntityListener auditingEntityListener() {
        return new AuditingEntityListener();
    }
}
```

---

### ⚠️ Common Misconceptions

| Misconception                                      | Reality                                                                                                                                                                                                                                                                                     |
| -------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `@Bean` can only be used inside `@Configuration`   | `@Bean` can appear in `@Component`, `@Service`, and other stereotype-annotated classes (lite mode). The difference is that lite-mode `@Bean` methods are NOT CGLIB-intercepted, so calling one `@Bean` method from another creates new instances rather than returning the cached singleton |
| `@Configuration` inherits component-scan behaviour | `@Configuration` does NOT automatically scan for `@Component` classes. You must add `@ComponentScan` to the `@Configuration` class or a parent configuration class. `@SpringBootApplication` bundles `@Configuration` + `@ComponentScan` + `@EnableAutoConfiguration`                       |
| `@Bean` method visibility must be public           | `@Bean` methods can be package-private or protected (but not private or final). Private methods cannot be overridden by the CGLIB subclass and will not be intercepted — treat private `@Bean` methods as lite-mode                                                                         |
| A `@Configuration` class is not itself a bean      | `@Configuration` classes ARE registered as singleton beans in the container. This is why they can receive `@Autowired` dependencies and be injected into other beans. `@Configuration` implies `@Component`                                                                                 |

---

### 🔥 Pitfalls in Production

**Using `@Bean` in a `@Component` class (lite mode) and calling `@Bean` methods internally:**

```java
// BAD: @Component (lite mode) — no CGLIB interception
@Component
class DataConfig {
    @Bean
    ConnectionPool pool() { return new ConnectionPool(5); }

    @Bean
    RepoA repoA() { return new RepoA(pool()); } // NEW pool instance

    @Bean
    RepoB repoB() { return new RepoB(pool()); } // ANOTHER new pool instance
}
// Two separate pools → two connection pools → too many connections

// GOOD: use @Configuration for full mode
@Configuration
class DataConfig {
    @Bean
    ConnectionPool pool() { return new ConnectionPool(5); } // one instance

    @Bean
    RepoA repoA() { return new RepoA(pool()); } // same pool

    @Bean
    RepoB repoB() { return new RepoB(pool()); } // same pool
}
```

---

**Making a `@Bean` method `final` — disables CGLIB override:**

```java
// BAD: final method cannot be overridden by CGLIB subclass
@Configuration
class AppConfig {
    @Bean
    public final DataSource dataSource() { ... } // CGLIB cannot override final!
    // Spring logs a warning and falls back to lite mode for this method
    // → singleton guarantee broken — new instance created each call
}
// GOOD: @Bean methods must NOT be final
```

---

### 🔗 Related Keywords

- `Bean` — the object produced and managed as a result of a `@Bean` method
- `BeanFactoryPostProcessor` — specifically `ConfigurationClassPostProcessor` which processes `@Configuration`
- `CGLIB Proxy` — the mechanism used to subclass `@Configuration` classes for singleton enforcement
- `@ComponentScan` — used alongside `@Configuration` to enable classpath scanning
- `Auto-Configuration` — Spring Boot's mechanism uses `@Configuration` + `@Conditional` annotations
- `@Qualifier / @Primary` — used to disambiguate when `@Bean` methods produce multiple beans of the same type

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ @Configuration │ Full mode: CGLIB-proxied class          │
│                │ Singleton @Bean methods called once      │
├───────────────┼───────────────────────────────────────────┤
│ @Bean          │ Factory method — return value = bean     │
│                │ Method name = default bean name          │
├───────────────┼───────────────────────────────────────────┤
│ LITE MODE      │ @Bean in @Component — no CGLIB proxy     │
│ CAVEAT         │ Internal @Bean calls create new instances│
├───────────────┼───────────────────────────────────────────┤
│ BEST PRACTICE  │ Inject deps as method parameters         │
│                │ Don't call @Bean methods directly        │
├───────────────┼───────────────────────────────────────────┤
│ ONE-LINER      │ "@Configuration = factory blueprint;     │
│                │  @Bean = one assembly instruction;        │
│                │  CGLIB = shared-parts warehouse."        │
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** `@Configuration` classes are CGLIB-subclassed so that `@Bean` methods are intercepted. However, `@SpringBootTest` with `@MockBean` replaces a bean in the application context. Describe what happens at the CGLIB level when a `@MockBean` replaces a singleton that other `@Bean` methods depend on: does the CGLIB proxy return the mock or the original? How does Spring Boot ensure the mock is used when other beans call the `@Bean` method that was mocked? And what is the consequence of calling a `@Bean` factory method that returns a mock via CGLIB interception?

**Q2.** `@Configuration` supports `proxyBeanMethods = false` (introduced in Spring 5.2) which disables CGLIB subclassing for performance. This means `@Bean` methods become lite-mode: each call creates a new instance. Describe the specific use cases where `proxyBeanMethods = false` is safe (beans don't call each other's `@Bean` methods internally) vs. dangerous (singleton sharing via internal method calls). How does Spring Boot's own auto-configuration use `proxyBeanMethods = false` extensively, and what is the startup performance benefit of disabling CGLIB subclassing?
