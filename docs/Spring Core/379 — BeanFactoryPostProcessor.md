---
layout: default
title: "BeanFactoryPostProcessor"
parent: "Spring Core"
nav_order: 379
permalink: /spring/beanfactorypostprocessor/
number: "379"
category: Spring Core
difficulty: ★★☆
depends_on: BeanFactory, ApplicationContext, Bean Lifecycle, @Configuration
used_by: PropertySourcesPlaceholderConfigurer, @Value, Auto-Configuration, Conditional Beans
tags: #java, #spring, #springboot, #intermediate, #internals
---

# 379 — BeanFactoryPostProcessor

`#java` `#spring` `#springboot` `#intermediate` `#internals`

⚡ TL;DR — A Spring extension that intercepts bean definitions (metadata) before any beans are instantiated — enabling property resolution, conditional registration, and definition modification.

| #379 | category: Spring Core
|:---|:---|:---|
| **Depends on:** | BeanFactory, ApplicationContext, Bean Lifecycle, @Configuration | |
| **Used by:** | PropertySourcesPlaceholderConfigurer, @Value, Auto-Configuration, Conditional Beans | |

---

### 📘 Textbook Definition

`BeanFactoryPostProcessor` (BFPP) is a Spring extension interface invoked after all bean definitions have been parsed and registered but before any bean instances are created. It receives a `ConfigurableListableBeanFactory` and can read or modify `BeanDefinition` objects — changing scope, adding property values, overriding class names, or removing definitions entirely. The most important built-in BFPP is `PropertySourcesPlaceholderConfigurer`, which resolves `${property.key}` placeholders in `@Value` annotations and XML configuration. `BeanDefinitionRegistryPostProcessor` (a subinterface) can additionally register new `BeanDefinition`s dynamically.

---

### 🟢 Simple Definition (Easy)

A `BeanFactoryPostProcessor` runs before Spring creates any beans. It reads or rewrites the "blueprints" (bean definitions) — for example, filling in property placeholders like `${server.port}` before any objects are built.

---

### 🔵 Simple Definition (Elaborated)

Before Spring instantiates a single bean, it first builds a complete map of all bean definitions — the metadata describing every class to instantiate, its scope, constructor arguments, and property values. `BeanFactoryPostProcessor` intercepts at this definition-metadata stage. The most visible use is property resolution: `@Value("${spring.datasource.url}")` is just a placeholder string in the bean definition until `PropertySourcesPlaceholderConfigurer` resolves it by reading `application.properties` or environment variables. Spring Boot's auto-configuration conditions (`@ConditionalOnClass`, `@ConditionalOnProperty`) are evaluated by `ConfigurationClassPostProcessor`, a `BeanDefinitionRegistryPostProcessor`, before any beans are created.

---

### 🔩 First Principles Explanation

**Two distinct pre-instantiation phases:**

```
┌─────────────────────────────────────────────────────┐
│  STARTUP PHASES                                     │
│                                                     │
│  Phase 1: DEFINITION PHASE                          │
│  ApplicationContext reads @Configuration classes,  │
│  classpath scan, XML → builds BeanDefinition map   │
│  (metadata only — no objects created yet)           │
│                                                     │
│  ↓ BFPP runs HERE ↓                                │
│  BeanFactoryPostProcessor invoked:                  │
│  - Reads/modifies BeanDefinitions                  │
│  - Resolves ${placeholders} in definitions          │
│  - Registers/removes bean definitions              │
│  - Evaluates @Conditional conditions                │
│                                                     │
│  Phase 2: INSTANTIATION PHASE                       │
│  All singleton beans created in dependency order    │
│  BeanPostProcessors intercept (see entry 110)       │
└─────────────────────────────────────────────────────┘
```

**Why definition modification must happen before creation:**

`@Value("${db.url}")` is stored as a literal string `"${db.url}"` in the bean definition. When the `DataSource` bean is created, Spring reads this literal and initialises the dataSource with `"${db.url}"` — obviously wrong. `PropertySourcesPlaceholderConfigurer` (a BFPP) resolves all `${...}` strings to their real values *before* any beans are created, so the DataSource constructor receives the real URL.

---

### ❓ Why Does This Exist (Why Before What)

**WITHOUT BeanFactoryPostProcessor:**

```
Without BFPP:

  @Value("${server.port}") → literal string "${server.port}"
    never resolved → injected as the placeholder string itself
    → application.properties has no effect on @Value fields

  @ConditionalOnClass impossible:
    Conditions must be evaluated BEFORE beans are created
    → can't decide "create DataSourceAutoConfiguration?"
    at instantiation time — too late

  Dynamic bean registration impossible:
    Can't register a BeanDefinition based on external
    config (API key present? register this gateway bean)
    without BeanDefinitionRegistryPostProcessor
```

**WITH BeanFactoryPostProcessor:**

```
→ @Value("${db.url}") resolved to real URL before bean creation
→ @ConditionalOnProperty evaluated at definition phase
  → beans conditionally registered or skipped
→ PropertyOverrideConfigurer overrides any bean property
  from external config file (legacy use case)
→ Spring Boot's ConfigurationClassPostProcessor processes
  @Import, @Bean, @ComponentScan at definition time
```

---

### 🧠 Mental Model / Analogy

> A `BeanFactoryPostProcessor` is like a **building inspector who reviews blueprints before construction begins**. They can mark required corrections: fill in missing measurements (property resolution), approve or reject designs based on building codes (conditional evaluation), or add new rooms to the blueprint (dynamic bean registration). Once construction starts (bean instantiation), the blueprints are fixed. The inspector works only on paper, not on actual buildings — this is the key distinction from `BeanPostProcessor`, who works on finished structures.

"Blueprints" = BeanDefinitions (metadata)
"Inspector reviewing before construction" = BFPP runs before instantiation
"Filling in missing measurements" = resolving ${placeholder} values
"Approving/rejecting designs" = @Conditional evaluation
"Adding new rooms to blueprint" = BeanDefinitionRegistryPostProcessor
"Construction starts" = bean instantiation phase

---

### ⚙️ How It Works (Mechanism)

**The interface:**

```java
@FunctionalInterface
public interface BeanFactoryPostProcessor {
  void postProcessBeanFactory(
      ConfigurableListableBeanFactory beanFactory)
      throws BeansException;
}
```

**What you can do with the BeanFactory at this phase:**

```java
@Component
public class MyBFPP implements BeanFactoryPostProcessor {

  @Override
  public void postProcessBeanFactory(
      ConfigurableListableBeanFactory bf) {

    // Read all bean definitions
    String[] names = bf.getBeanDefinitionNames();

    // Modify a specific bean's definition
    BeanDefinition def = bf.getBeanDefinition("dataSource");
    def.getPropertyValues().add(
        "connectionTimeout", "5000");

    // Change scope of a bean programmatically
    BeanDefinition svcDef = bf.getBeanDefinition("orderSvc");
    svcDef.setScope(BeanDefinition.SCOPE_PROTOTYPE);
  }
}
```

**BeanDefinitionRegistryPostProcessor (subinterface):**

```java
@Component
public class DynamicBeanRegistrar
    implements BeanDefinitionRegistryPostProcessor {

  @Override
  public void postProcessBeanDefinitionRegistry(
      BeanDefinitionRegistry registry) {
    // Register a new bean definition dynamically
    // (conditioned on runtime config)
    if (System.getenv("STRIPE_KEY") != null) {
      registry.registerBeanDefinition("paymentGateway",
          BeanDefinitionBuilder
              .genericBeanDefinition(StripeGateway.class)
              .getBeanDefinition());
    }
  }

  @Override
  public void postProcessBeanFactory(
      ConfigurableListableBeanFactory bf) {
    // optional additional modification
  }
}
```

---

### 🔄 How It Connects (Mini-Map)

```
ApplicationContext parses @Configuration / scan
        ↓
  BeanDefinition registry built (all metadata)
        ↓
  BFPP runs  ← you are here
  (modifies BeanDefinitions before instantiation)
        ↓
  Key built-in BFPPs:
  ConfigurationClassPostProcessor
    (processes @Bean, @Import, @Conditional)
  PropertySourcesPlaceholderConfigurer
    (resolves ${} in @Value and XML)
        ↓
  Bean instantiation begins
  (BeanPostProcessor intercepts per-bean)
        ↓
  ApplicationContext fully started
```

---

### 💻 Code Example

**Example 1 — PropertySourcesPlaceholderConfigurer (how @Value works):**

```java
// Defined automatically by Spring Boot
@Bean
public static PropertySourcesPlaceholderConfigurer pspc() {
  return new PropertySourcesPlaceholderConfigurer();
  // Runs as BFPP at startup; resolves all ${...} in defs
}

// application.properties:
// db.url=jdbc:postgresql://prod-db:5432/app
// db.pool.size=20

@Service
public class DatabaseService {
  @Value("${db.url}")        // stored as literal in BeanDef
  private String dbUrl;      // resolved by PSPC before creation

  @Value("${db.pool.size}")
  private int poolSize;
}
// Without PSPC BFPP: dbUrl = "${db.url}" (unresolved!)
// With PSPC BFPP:    dbUrl = "jdbc:postgresql://prod-db..."
```

**Example 2 — ConfigurationClassPostProcessor processing @Conditional:**

```java
// Auto-configuration processed by ConfigurationClassBPP
@Configuration
@ConditionalOnClass(DataSource.class)      // evaluates here
@ConditionalOnProperty("spring.datasource.url") // evaluates here
public class DataSourceAutoConfiguration {
  @Bean
  DataSource dataSource(DataSourceProperties p) {
    return DataSourceBuilder.create()
        .url(p.getUrl()).build();
  }
}
// If spring-jdbc not on classpath → bean NOT registered
// Evaluated at BFPP phase, before any beans created
```

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| BFPP and BeanPostProcessor run at the same time | BFPP runs on bean DEFINITIONS before instantiation; BPP runs on bean INSTANCES after creation. They operate on different subjects at different times |
| @Value resolution is built into @Value annotation processing | @Value placeholders are resolved by PropertySourcesPlaceholderConfigurer (a BFPP) before beans are created, not at injection time |
| You should always inject beans into a BFPP | BFPPs should NOT have injected dependencies — they run so early that the injection infrastructure may not be ready. Use static factory methods where possible |
| BFPP can create new bean instances | BFPP operates on BeanDefinitions (metadata), not instances. Creating bean instances at BFPP phase can cause initialization issues |

---

### 🔥 Pitfalls in Production

**1. BFPP with @Autowired dependencies — premature creation**

```java
// BAD: BFPP with @Autowired forces bean creation too early
@Component
public class MyBFPP implements BeanFactoryPostProcessor {
  @Autowired
  ConfigProperties config; // Forces ConfigProperties to be
  // instantiated BEFORE BFPP processing completes
  // → ConfigProperties may not have ${} values resolved yet!
}

// GOOD: implement as a static @Bean with no dependencies,
// or use BeanDefinitionRegistryPostProcessor pattern
@Bean
public static MyBFPP myBfpp() {
  return new MyBFPP(); // static — no injection
}
```

**2. Forgetting `static` on BFPP @Bean method**

```java
// BAD: non-static @Bean method for BFPP
@Configuration
class AppConfig {
  @Bean
  public BeanFactoryPostProcessor myBFPP() {
    // Non-static: requires AppConfig instance to be created first
    // AppConfig bean processed normally → too late for BFPP!
    return bf -> { /* ... */ };
  }
}
// Spring may log WARNING: "non-static @Bean may cause issues
// with post-processing of the configuration class"

// GOOD: always declare BFPP @Bean methods as static
@Configuration
class AppConfig {
  @Bean
  public static BeanFactoryPostProcessor myBFPP() {
    return bf -> { /* ... */ };
  }
}
```

---

### 🔗 Related Keywords

- `BeanPostProcessor` — intercepts bean INSTANCES post-creation; BFPP intercepts bean DEFINITIONS pre-creation
- `ApplicationContext` — orchestrates BFPP invocation at startup before bean instantiation
- `@Value` — relies on PropertySourcesPlaceholderConfigurer (a BFPP) for ${} resolution
- `Auto-Configuration` — Spring Boot's conditional auto-config is processed by ConfigurationClassPostProcessor
- `BeanDefinition` — the metadata object BFPP reads and modifies (scope, class, properties)
- `@Conditional` — evaluated during BFPP phase to include/exclude bean definitions

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ KEY IDEA     │ Runs on bean DEFINITIONS before any bean  │
│              │ is created — resolves properties,         │
│              │ evaluates conditions, registers defs      │
├──────────────┼───────────────────────────────────────────┤
│ USE WHEN     │ Dynamic bean registration; property       │
│              │ placeholder resolution; condition testing  │
├──────────────┼───────────────────────────────────────────┤
│ AVOID WHEN   │ Never @Autowired into BFPP — mark @Bean   │
│              │ methods static to avoid ordering issues   │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "BPP works on buildings;                  │
│              │  BFPP works on blueprints."               │
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ @Autowired (112) → Circular Dependency    │
│              │ (115) → Auto-Configuration (133)          │
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** Spring Boot's `ConfigurationClassPostProcessor` is a `BeanDefinitionRegistryPostProcessor` that processes all `@Configuration` classes, evaluates `@Conditional` annotations, and registers bean definitions. It runs in a fixed order relative to other BFPPs. Explain what happens if you write a custom `BeanFactoryPostProcessor` that modifies a bean definition that `ConfigurationClassPostProcessor` hasn't yet processed — specifically, what ordering guarantee does `Ordered` or `PriorityOrdered` provide — and describe how `PropertySourcesPlaceholderConfigurer.setOrder(Ordered.HIGHEST_PRECEDENCE)` affects the processing chain.

**Q2.** `@Value` injection resolves `${property.key}` strings at bean creation time via BFPP. But `@ConfigurationProperties` (used by Spring Boot for type-safe configuration binding) uses a completely different mechanism — it does NOT use `PropertySourcesPlaceholderConfigurer`. Explain how `@ConfigurationProperties` binding works instead, what `ConfigurationPropertiesBindingPostProcessor` is, and describe the specific scenario where `@Value` and `@ConfigurationProperties` behave differently when a property is missing from the configuration.

