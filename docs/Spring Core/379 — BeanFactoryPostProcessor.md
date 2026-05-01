---
layout: default
title: "BeanFactoryPostProcessor"
parent: "Spring Core"
nav_order: 379
permalink: /spring/beanfactorypostprocessor/
number: "379"
category: Spring Core
difficulty: ★★★
depends_on: Bean Lifecycle, BeanPostProcessor, ApplicationContext, BeanFactory
used_by: Auto-Configuration, @ConfigurationProperties, Bean Lifecycle
tags: #advanced, #spring, #internals, #deep-dive
---

# 379 — BeanFactoryPostProcessor

`#advanced` `#spring` `#internals` `#deep-dive`

⚡ TL;DR — A **BeanFactoryPostProcessor** intercepts bean _definitions_ (the metadata blueprints) before any beans are instantiated, allowing you to modify, add, or remove bean definitions at container startup. `PropertySourcesPlaceholderConfigurer` — the processor that resolves `${property.name}` — is a BeanFactoryPostProcessor.

| #379            | Category: Spring Core                                              | Difficulty: ★★★ |
| :-------------- | :----------------------------------------------------------------- | :-------------- |
| **Depends on:** | Bean Lifecycle, BeanPostProcessor, ApplicationContext, BeanFactory |                 |
| **Used by:**    | Auto-Configuration, @ConfigurationProperties, Bean Lifecycle       |                 |

---

### 📘 Textbook Definition

A **BeanFactoryPostProcessor** is a Spring container extension point that operates on the `BeanFactory` _after_ all bean definitions have been loaded but _before_ any bean instances are created. Its single method, `postProcessBeanFactory(ConfigurableListableBeanFactory beanFactory)`, receives the full bean factory, giving access to all registered `BeanDefinition` objects. A `BeanFactoryPostProcessor` can read, modify, or add bean definitions — changing scope, adding property values, setting constructor arguments, or registering entirely new bean definitions. The canonical Spring implementation is `PropertySourcesPlaceholderConfigurer`, which resolves `${...}` property placeholders in bean definitions before beans are instantiated. `BeanDefinitionRegistryPostProcessor` (a sub-interface) additionally allows registering new `BeanDefinition` objects — `ConfigurationClassPostProcessor`, which processes all `@Configuration`, `@ComponentScan`, `@Bean`, and `@Import` annotations, is a `BeanDefinitionRegistryPostProcessor`. BeanFactoryPostProcessor is distinct from `BeanPostProcessor` (which operates on instances after creation).

---

### 🟢 Simple Definition (Easy)

A BeanFactoryPostProcessor runs before Spring creates any beans and lets you change the recipes (definitions) used to create beans — for example, filling in property values from config files.

---

### 🔵 Simple Definition (Elaborated)

Spring's startup has two phases: first, it reads and compiles all the instructions (bean definitions) for how to create each bean. Second, it creates the actual bean instances. A BeanFactoryPostProcessor runs between these two phases — after all definitions are loaded, before any beans exist. At this point you have access to every blueprint, and you can change them. The most common real-world use is `PropertySourcesPlaceholderConfigurer`: it scans every bean definition looking for `${db.url}` placeholders and replaces them with real values from `application.properties` before any database bean is created. Spring Boot's auto-configuration heavily uses `BeanDefinitionRegistryPostProcessor` (a sub-interface) to conditionally register bean definitions based on classpath detection.

---

### 🔩 First Principles Explanation

**The interface and its position in the startup sequence:**

```java
@FunctionalInterface
public interface BeanFactoryPostProcessor {
    // Called AFTER all BeanDefinitions are loaded,
    // BEFORE any bean instances are created
    void postProcessBeanFactory(ConfigurableListableBeanFactory beanFactory)
            throws BeansException;
}

// Sub-interface: allows registering NEW BeanDefinitions
public interface BeanDefinitionRegistryPostProcessor
        extends BeanFactoryPostProcessor {
    // Called BEFORE postProcessBeanFactory
    void postProcessBeanDefinitionRegistry(BeanDefinitionRegistry registry)
            throws BeansException;
}
```

**The full startup sequence showing where BFPP fits:**

```
APPLICATION CONTEXT REFRESH
           │
   1. Load all BeanDefinitions
      (component scan, @Configuration classes, XML)
           │
   2. Run BeanDefinitionRegistryPostProcessors  ← sub-interface
      (ConfigurationClassPostProcessor runs here:
       processes @Configuration, @Bean, @ComponentScan, @Import)
           │
   3. Run BeanFactoryPostProcessors  ← standard interface
      (PropertySourcesPlaceholderConfigurer: resolves ${...})
           │
   4. Register BeanPostProcessors
           │
   5. Instantiate beans (singleton beans, unless lazy)
      (BeanPostProcessors run during this phase)
           │
   6. Context is READY
```

**What a BeanFactoryPostProcessor can do:**

```java
// Access any registered BeanDefinition
BeanDefinition bd = beanFactory.getBeanDefinition("orderService");

// Read metadata
String className  = bd.getBeanClassName();
String scope      = bd.getScope();
boolean lazy      = bd.isLazyInit();

// Modify metadata BEFORE instantiation
bd.setScope("prototype");           // change scope
bd.setLazyInit(true);               // make lazy
bd.getPropertyValues().add("timeout", 30); // add property value
bd.getConstructorArgumentValues()
  .addIndexedArgumentValue(0, "value"); // change constructor arg
```

**The most important built-in BeanFactoryPostProcessors:**

```
ConfigurationClassPostProcessor (BeanDefinitionRegistryPostProcessor)
  → Processes ALL @Configuration classes
  → Discovers @Bean methods, registers their BeanDefinitions
  → Processes @ComponentScan — triggers classpath scanning
  → Processes @Import — registers imported BeanDefinitions
  → Processes @PropertySource — adds property files to Environment
  ★ This is the most important BFPP — without it, none of
    @Configuration, @Bean, or @ComponentScan would work.

PropertySourcesPlaceholderConfigurer (BeanFactoryPostProcessor)
  → Scans all BeanDefinitions for ${property.placeholder} strings
  → Resolves them from Environment (application.properties, env vars)
  → Replaces placeholders with actual values in BeanDefinitions
  → Must be registered as a STATIC @Bean to work in @Configuration
    (it runs before @Configuration is fully processed)
```

---

### ❓ Why Does This Exist (Why Before What)

WITHOUT BeanFactoryPostProcessor:

What breaks without it:

1. `@Configuration` and `@ComponentScan` processing would need to be hardcoded in the container — no extensibility.
2. Property placeholder resolution (`${db.url}`) would not exist — bean definitions could not reference external configuration.
3. Spring Boot's conditional auto-configuration (`@ConditionalOnClass`, `@ConditionalOnProperty`) could not dynamically register beans at startup.
4. Framework integrations (Hibernate validator, Spring Data repository generation) could not register their own bean definitions.

WITH BeanFactoryPostProcessor:
→ `ConfigurationClassPostProcessor` drives all modern annotation-based configuration.
→ `PropertySourcesPlaceholderConfigurer` externalisesall configuration — no hardcoded values in bean definitions.
→ Spring Boot auto-configuration conditionally populates the container based on environment inspection.
→ The factory is open for extension at the definition level, not just the instance level.

---

### 🧠 Mental Model / Analogy

> Think of a construction project. BeanDefinitions are the architect's blueprints. BeanFactoryPostProcessors are the planning committee reviewers who examine all blueprints before construction begins — they can annotate blueprints with amendments, reject some designs, or add new buildings. Only after all reviews are complete does construction (bean instantiation) begin. BeanPostProcessors are the on-site quality inspectors who check each building as it is constructed. The reviewers (BFPP) work before a single brick is laid; the inspectors (BPP) work during construction.

"Architect's blueprints" = BeanDefinitions
"Planning committee review" = BeanFactoryPostProcessor
"Adding amendments to blueprints" = modifying BeanDefinition properties
"On-site construction inspectors" = BeanPostProcessors
"Construction phase" = bean instantiation

---

### ⚙️ How It Works (Mechanism)

**ConfigurationClassPostProcessor — the heart of Spring Boot startup:**

```
@SpringBootApplication
  = @EnableAutoConfiguration
  + @ComponentScan
  + @SpringBootConfiguration (@Configuration)

At startup, ConfigurationClassPostProcessor:
  1. Finds this @Configuration class (it's a BeanDefinition already)
  2. Parses it: discovers @ComponentScan("com.example")
  3. Scans classpath for @Component/@Service/@Repository/@Controller
  4. Registers each found class as a BeanDefinition
  5. Parses each @Configuration class found in the scan
  6. Discovers @Bean methods → registers as BeanDefinitions
  7. Processes @Import (imports more configuration)
  8. Processes @EnableAutoConfiguration
     → reads META-INF/spring/auto-configuration.imports
     → conditionally registers auto-configuration BeanDefinitions

Result: before any beans are created, ALL BeanDefinitions are ready
```

**PropertySourcesPlaceholderConfigurer — how ${} resolution works:**

```java
// Bean definition (what you write)
@Bean
DataSource dataSource(
    @Value("${db.url}") String url,        // placeholder in definition
    @Value("${db.password}") String pass    // placeholder in definition
) { ... }

// BFPP action:
// Scans all BeanDefinitions for "${...}" patterns
// Looks up "db.url" in Environment (application.properties → env var → system prop)
// Replaces "${db.url}" with "jdbc:postgresql://localhost:5432/mydb"
// Replaces "${db.password}" with "secret"
// THEN: bean instantiation happens with already-resolved values

// CRITICAL: must be @Bean as static in @Configuration
@Configuration
class DataConfig {
    @Bean
    public static PropertySourcesPlaceholderConfigurer propertyConfigurer() {
        return new PropertySourcesPlaceholderConfigurer();
        // STATIC because it must run before @Configuration is processed
        // Non-static would cause a circular dependency with @Configuration
    }
}
```

---

### 🔄 How It Connects (Mini-Map)

```
BeanDefinitions (blueprints for all beans)
        │
        ▼
BeanFactoryPostProcessor  ◄──── (you are here)
(modifies definitions BEFORE instantiation)
        │
        ├──── BeanDefinitionRegistryPostProcessor
        │     (ConfigurationClassPostProcessor)
        │     → @Configuration / @Bean / @ComponentScan / @Import
        │
        ├──── PropertySourcesPlaceholderConfigurer
        │     → ${property.placeholder} resolution
        │
        ▼
Bean Instantiation
        │
        ▼
BeanPostProcessor
(modifies INSTANCES during/after creation)
```

---

### 💻 Code Example

**Example 1 — Custom BFPP that enforces bean naming conventions:**

```java
@Component
public class NamingConventionBFPP implements BeanFactoryPostProcessor {

    @Override
    public void postProcessBeanFactory(ConfigurableListableBeanFactory bf)
            throws BeansException {
        for (String beanName : bf.getBeanDefinitionNames()) {
            BeanDefinition bd = bf.getBeanDefinition(beanName);
            String className = bd.getBeanClassName();
            if (className == null) continue;

            // Enforce: all @Service beans must end in "Service"
            if (bd.hasAttribute("serviceComponent") &&
                !className.endsWith("Service")) {
                throw new BeanDefinitionParsingException(
                    new Problem("Service beans must have class names ending in 'Service'",
                                new Location(new ClassPathResource(className))));
            }
        }
    }
}
```

**Example 2 — BeanDefinitionRegistryPostProcessor that dynamically registers beans:**

```java
@Component
public class PluginRegistryPostProcessor
        implements BeanDefinitionRegistryPostProcessor {

    @Override
    public void postProcessBeanDefinitionRegistry(BeanDefinitionRegistry registry)
            throws BeansException {
        // Discover all Plugin implementations on the classpath
        ServiceLoader.load(Plugin.class).forEach(plugin -> {
            String beanName = "plugin-" + plugin.getName();
            BeanDefinition bd = BeanDefinitionBuilder
                .genericBeanDefinition(plugin.getClass())
                .setScope(BeanDefinition.SCOPE_SINGLETON)
                .getBeanDefinition();
            registry.registerBeanDefinition(beanName, bd);
            log.info("Registered plugin bean: {}", beanName);
        });
    }

    @Override
    public void postProcessBeanFactory(ConfigurableListableBeanFactory beanFactory)
            throws BeansException {
        // No further modification needed
    }
}
```

---

### ⚠️ Common Misconceptions

| Misconception                                                                                               | Reality                                                                                                                                                                                                                                                                             |
| ----------------------------------------------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| BeanFactoryPostProcessor and BeanPostProcessor do the same thing                                            | They operate at completely different phases: BFPP operates on bean DEFINITIONS before any beans are instantiated; BPP operates on bean INSTANCES after creation. BFPP changes blueprints; BPP changes buildings                                                                     |
| You can access bean instances inside a BeanFactoryPostProcessor                                             | You must NOT call `beanFactory.getBean()` inside a BFPP — this triggers early instantiation of beans before the full lifecycle is set up, leading to beans without BPP processing (no AOP proxies, no `@Autowired` injection)                                                       |
| `PropertySourcesPlaceholderConfigurer` is auto-registered                                                   | In Spring Boot, `@Value` and `${...}` resolution work because Spring Boot auto-configures `PropertySourcesPlaceholderConfigurer`. In plain Spring MVC or `@Configuration`, you must register it explicitly as a `static @Bean`                                                      |
| `BeanDefinitionRegistryPostProcessor.postProcessBeanDefinitionRegistry` runs after `postProcessBeanFactory` | It runs BEFORE: first all `postProcessBeanDefinitionRegistry` methods run (so all BeanDefinitions are fully registered), then all `postProcessBeanFactory` methods run. `ConfigurationClassPostProcessor` is a prime example — it must register beans before the factory-level pass |

---

### 🔥 Pitfalls in Production

**Calling `beanFactory.getBean()` inside a BFPP — bypasses AOP proxying**

```java
// BAD: getting a bean instance inside a BFPP
@Component
public class EagerBFPP implements BeanFactoryPostProcessor {
    @Override
    public void postProcessBeanFactory(ConfigurableListableBeanFactory bf) {
        OrderService svc = bf.getBean(OrderService.class); // WRONG
        // OrderService is instantiated NOW — before BeanPostProcessors run
        // → @Transactional AOP proxy NOT applied
        // → @Autowired dependencies may not be injected
        // Spring logs: "Bean 'orderService' is not eligible for getting
        //               processed by all BeanPostProcessors"
    }
}

// GOOD: modify BeanDefinitions only — never instantiate beans inside BFPP
@Override
public void postProcessBeanFactory(ConfigurableListableBeanFactory bf) {
    BeanDefinition bd = bf.getBeanDefinition("orderService");
    bd.getPropertyValues().add("timeout", 30); // safe — modifies definition only
}
```

---

**Non-static `PropertySourcesPlaceholderConfigurer` in a `@Configuration` class**

```java
// BAD: non-static @Bean — BFPP may not run early enough
@Configuration
class AppConfig {
    @Bean  // not static — Spring tries to create AppConfig first
    PropertySourcesPlaceholderConfigurer cfg() {
        // AppConfig needs @Value resolution → BFPP needed →
        // BFPP needs AppConfig bean → circular bootstrap issue
        return new PropertySourcesPlaceholderConfigurer();
    }

    @Value("${app.name}") // may not be resolved — BFPP too late
    String appName;
}

// GOOD: static @Bean ensures BFPP instantiated before @Configuration bean
@Configuration
class AppConfig {
    @Bean
    public static PropertySourcesPlaceholderConfigurer cfg() {
        return new PropertySourcesPlaceholderConfigurer();
    }
}
```

---

### 🔗 Related Keywords

- `BeanPostProcessor` — sibling; operates on bean instances (phases 4 and 6) vs. definitions (pre-instantiation)
- `BeanFactory` — the container whose `BeanFactory.postProcessBeanFactory()` is the callback parameter
- `Bean Lifecycle` — BFPP runs between definition loading (phase 0) and bean instantiation (phase 1)
- `@Configuration / @Bean` — processed by `ConfigurationClassPostProcessor` (a `BeanDefinitionRegistryPostProcessor`)
- `Auto-Configuration` — Spring Boot's `AutoConfigurationImportSelector` uses BFPP-driven import to register beans
- `@Value / @ConfigurationProperties` — placeholder resolution via `PropertySourcesPlaceholderConfigurer`

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ TIMING       │ After all definitions loaded              │
│              │ BEFORE any bean instances created         │
├──────────────┼───────────────────────────────────────────┤
│ KEY BUILT-IN │ ConfigurationClassPostProcessor           │
│ EXAMPLES     │   → processes @Configuration/@Bean/@Scan  │
│              │ PropertySourcesPlaceholderConfigurer      │
│              │   → resolves ${property.placeholder}      │
├──────────────┼───────────────────────────────────────────┤
│ DANGER       │ NEVER call beanFactory.getBean() inside  │
│              │ BFPP — causes early unproxied bean creation│
├──────────────┼───────────────────────────────────────────┤
│ STATIC RULE  │ BFPP @Bean methods must be STATIC in     │
│              │ @Configuration to avoid bootstrap issues  │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "BFPP = planning committee: amends        │
│              │  blueprints before construction begins."  │
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** `ConfigurationClassPostProcessor` is a `BeanDefinitionRegistryPostProcessor`. It processes `@ComponentScan` and discovers all `@Component`-annotated classes, registering them as `BeanDefinitions`. If a scanned class is itself a `@Configuration` class with a `@Bean` method that returns a `DataSource`, trace the exact sequence of events: when does Spring discover the nested `@Configuration`? When is the `@Bean` method's `BeanDefinition` registered? Can a `@Bean` method in a scanned `@Configuration` class have a `@Conditional` annotation, and if so, when is that condition evaluated — during the BFPP phase or during instantiation?

**Q2.** Spring Boot's `@ConditionalOnMissingBean` annotation is evaluated by `OnMissingBeanCondition`, which is invoked during `ConfigurationClassPostProcessor`'s processing phase. This evaluation depends on what `BeanDefinitions` have already been registered at the time of evaluation. Explain why the ORDER in which `@Configuration` classes are processed matters for `@ConditionalOnMissingBean` correctness, describe how Spring Boot controls this ordering (via `@AutoConfigureAfter`, `@AutoConfigureBefore`, `AutoConfigurationSorter`), and explain the edge case where a user's own `@Bean` definition for a type might appear AFTER the auto-configuration processes — causing the condition to evaluate incorrectly.
