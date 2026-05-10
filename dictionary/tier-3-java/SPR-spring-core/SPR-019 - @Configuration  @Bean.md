---
version: 2
layout: default
title: "@Configuration  @Bean"
parent: "Spring Core"
grand_parent: "Technical Dictionary"
nav_order: 19
permalink: /spring/configuration-bean/
id: SPR-006
category: Spring Core
difficulty: ★★☆
depends_on: IoC, DI, ApplicationContext, Bean, BeanFactory
used_by: Spring Configuration Classes, @SpringBootApplication, Auto-Configuration
related: "@Component, @ComponentScan, @Import, @Conditional, BeanDefinition"
tags:
  - spring
  - springboot
  - intermediate
  - pattern
  - bestpractice
---

# SPR-019 - @Configuration  @Bean

⚡ TL;DR - @Configuration marks a class as a source of bean definitions; @Bean marks a method whose return value is registered as a Spring bean - together they replace XML bean definitions with type-safe Java configuration.

| #382            | Category: Spring Core                                                    | Difficulty: ★★☆ |
| :-------------- | :----------------------------------------------------------------------- | :-------------- |
| **Depends on:** | IoC, DI, ApplicationContext, Bean, BeanFactory                           |                 |
| **Used by:**    | Spring Configuration Classes, @SpringBootApplication, Auto-Configuration |                 |
| **Related:**    | @Component, @ComponentScan, @Import, @Conditional, BeanDefinition        |                 |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
Pre-Spring 3.0, the only way to define beans was XML: `<bean id="dataSource" class="org.apache.commons.dbcp.BasicDataSource">` with `<property>` sub-elements for each configuration value. Constructing a bean that required another bean meant writing `<ref bean="..." />`. Conditional bean registration required XML namespace hacks or custom `BeanFactoryPostProcessor` code. The configuration was separate from the code, un-navigable by IDEs, unchecked at compile time, and verbose.

**THE BREAKING POINT:**
XML configuration has no compile-time safety. Typos in class names (`class="com.example.DataSoruce"`) become runtime failures. Renaming a class doesn't update the XML. The IDE cannot navigate from an XML bean reference to the class definition. Generic type information is unavailable. Constructor injection requires knowing argument order. Building conditional logic ("register this bean only if this property is set") requires writing raw Java code within XML, which is worse than either.

**THE INVENTION MOMENT:**
"This is exactly why @Configuration and @Bean were created."

---

### 📘 Textbook Definition

**@Configuration** is a Spring annotation (`org.springframework.context.annotation.Configuration`) that marks a class as a CGLIB-enhanced configuration class. The class serves as a source of bean definitions: Spring reads its `@Bean` methods to create `BeanDefinition` objects. The CGLIB enhancement ensures that `@Bean` method calls between configuration methods return the same singleton bean (inter-bean method calls are intercepted). **@Bean** is placed on methods within a `@Configuration` class (or a `@Component` class for lite mode) to declare that the method's return value should be registered in the Spring container. The method name becomes the bean name by default. Method parameters are auto-wired from the container. `@Bean` supports `name`, `initMethod`, `destroyMethod`, `autowireCandidate`, and `@Scope` attributes.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
@Configuration is "this class is a Spring config file in Java"; @Bean is "this method creates a bean."

**One analogy:**

> @Configuration is like a cookbook (@Bean methods are recipes). The `applicationContext` is the restaurant kitchen - it reads the cookbook, executes each recipe, stores the results (beans), and serves them on demand. Inter-method calls in the cookbook don't re-cook the dish - they fetch the already-cooked version (CGLIB interception).

**One insight:**
The CGLIB proxy on `@Configuration` classes is what makes `@Bean` methods singletons by default. Without the proxy, every direct Java call to `beanMethod()` would create a new instance. With the proxy, Spring intercepts the call and returns the cached singleton. This is the critical difference between `@Configuration` (full mode, CGLIB-proxied) and `@Component` with `@Bean` (lite mode, no proxy).

---

### 🔩 First Principles Explanation

**CORE INVARIANTS:**

1. `@Configuration` classes are CGLIB-proxied at startup - `@Bean` method calls within the class return the singleton from the context, not new instances.
2. `@Bean` methods are factory methods - the container calls them once (for singletons), caches the result, and injects it wherever needed.
3. Method parameters in `@Bean` methods are automatically resolved from the container (equivalent to `@Autowired`).
4. In lite mode (`@Bean` on a plain `@Component`), no CGLIB proxy - inter-bean method calls create new instances. This is a subtle and common bug.

**DERIVED DESIGN:**
`@Configuration` + `@Bean` produces the same `BeanDefinition` objects that XML produced, but via Java reflection instead of XML parsing. The ApplicationContext processes both identically - the difference is purely at the definition-reading phase.

**THE TRADE-OFFS:**

**Gain:** Type safety (compiler checks class names and return types). IDE navigation (Ctrl+Click works). Conditional logic in plain Java (`if/else`, `instanceof`). Generics preserved. Refactoring-safe.

**Cost:** CGLIB overhead (small - one proxy class per `@Configuration`). CGLIB restrictions: `@Configuration` classes must be non-final (CGLIB can't subclass final classes). `@Bean` methods must not be `final` or `private` (CGLIB can't override them).

---

### 🧪 Thought Experiment

**SETUP:**
A `DataSource` bean depends on a `DataSourceProperties` bean. Both are defined in the same configuration class.

**WITHOUT CGLIB (conceptual, if @Configuration were not proxied):**

```java
@Configuration
public class DbConfig {
    @Bean public DataSourceProperties props() {
        return new DataSourceProperties();  // NEW INSTANCE
    }
    @Bean public DataSource dataSource() {
        return new DataSource(props());  // calls props() → ANOTHER NEW INSTANCE
    }
    @Bean public DataSourceValidator validator() {
        return new DataSourceValidator(props());  // THIRD NEW INSTANCE of props!
    }
}
```

Three calls to `props()` → three `DataSourceProperties` objects. Each consumer gets a _different_ instance. Mutations on one don't affect others. Catastrophic if properties are shared state.

**WITH CGLIB (actual @Configuration behavior):**

```java
// Spring intercepts all @Bean method calls within the class
dbConfig.props()     // 1st call → creates and caches
dbConfig.dataSource() → calls dbConfig.props() → returns CACHED instance
dbConfig.validator()  → calls dbConfig.props() → returns CACHED instance
// All three share the SAME DataSourceProperties instance
```

**THE INSIGHT:**
`@Configuration`'s CGLIB proxy solves the "singleton guarantee" problem for inter-bean dependencies declared in the same config class. Without it, dependency sharing would require passing beans as method parameters instead of calling other methods - syntactically verbose and easy to get wrong.

---

### 🧠 Mental Model / Analogy

> `@Configuration` is a Java class wearing a Spring "factory manager" uniform. The CGLIB proxy is the manager's rulebook: "When anyone asks for a widget from room 3, check the warehouse first - if it's already made, deliver that. Don't manufacture a new one each time." `@Bean` methods are the manufacturing instructions. The manager (CGLIB proxy) ensures that each product is made once and reused.

- "Factory manager uniform" → CGLIB proxy
- "Check the warehouse" → singleton cache in ApplicationContext
- "Manufacturing instructions" → `@Bean` method body
- "Anyone asks for a widget" → any direct call to a `@Bean` method within the config class

**Where this analogy breaks down:** The proxy only intercepts calls _within_ the same `@Configuration` class. External classes calling `dataSourceConfig.dataSource()` directly bypass the proxy (though this is considered an anti-pattern - never call `@Bean` methods directly from outside the config class).

---

### 📶 Gradual Depth - Four Levels

**Level 1 - What it is (anyone can understand):**
@Configuration turns a Java class into a "settings file" for your application. @Bean on a method means "run this method and register the result as a reusable object in Spring." Every other class can then ask Spring for that object.

**Level 2 - How to use it (junior developer):**
Create a class annotated with `@Configuration`. Add `@Bean` methods returning the objects you want to be beans. Use method parameters for dependencies (Spring auto-wires them). Set `@Scope` for non-singleton beans. Use `@Conditional` or `if/else` logic for conditional registration. Don't make the class final or its @Bean methods private/final.

**Level 3 - How it works (mid-level engineer):**
At startup, `ConfigurationClassPostProcessor` (a `BeanFactoryPostProcessor`) scans for `@Configuration` classes via `ConfigurationClassParser`. For each `@Bean` method found, it creates a `ConfigurationClassBeanDefinitionReader` that registers a `BeanDefinition` with the factory method reference stored. The `@Configuration` class itself is replaced with a CGLIB subclass via `ConfigurationClassEnhancer`. When the container calls the `@Bean` method, the CGLIB intercept (`BeanMethodInterceptor`) first checks the singleton cache - returning the cached bean if it exists, calling the real method only for the first request.

**Level 4 - Why it was designed this way (senior/staff):**
The CGLIB enhancement was a deliberate trade-off to give developers the "singleton-by-default" mental model without requiring them to understand the container's singleton cache. The alternative (always passing beans as method parameters) is more explicit but more verbose. Spring Boot's auto-configuration uses `@Configuration` + `@ConditionalOnMissingBean` extensively - each starter defines a configuration class that registers beans only if the user hasn't already defined one, creating the "opinionated defaults that yield to user configuration" model. This pattern would be impossible without the conditional, programmatic nature of Java configuration.

---

### ⚙️ How It Works (Mechanism)

**Processing sequence:**

```
Application startup:
    ↓
ConfigurationClassPostProcessor.postProcessBeanFactory()
    ↓
ConfigurationClassParser.parse():
  Finds @Configuration classes
  For each @Bean method:
    → Creates MethodMetadata
    → Registers ConfigurationClassBeanDefinition
    ↓
ConfigurationClassEnhancer.enhance(@Configuration class):
  → Creates CGLIB subclass
  → Adds BeanMethodInterceptor to intercept @Bean calls
    ↓
Bean creation phase:
  Container calls @Bean method via CGLIB proxy
  BeanMethodInterceptor.intercept():
    Is bean already in singleton cache?
      YES → return cached instance
      NO  → call original method, cache result, return it
```

**CGLIB interception (pseudo-code):**

```java
// What CGLIB adds to your @Configuration class:
@Override
public DataSource dataSource() {
    // Intercept the call
    String beanName = "dataSource";
    if (beanFactory.containsSingleton(beanName)) {
        return beanFactory.getSingleton(beanName);  // cached!
    }
    // Otherwise call original factory method
    DataSource result = super.dataSource();
    beanFactory.registerSingleton(beanName, result);
    return result;
}
```

---

### 🔄 The Complete Picture - End-to-End Flow

**NORMAL FLOW:**

```
@SpringBootApplication
    ↓
@EnableAutoConfiguration activates AutoConfigurationImportSelector
    ↓
User's @Configuration classes found by @ComponentScan
    ↓
ConfigurationClassPostProcessor parses all @Configuration classes
    ↓
@Bean methods registered as BeanDefinitions
    ↓ ← YOU ARE HERE
CGLIB enhancement applied to @Configuration classes
    ↓
Bean creation: @Bean methods called (once per singleton)
    ↓
CGLIB proxy ensures inter-method calls return cached singletons
    ↓
ApplicationContext fully initialized
```

**CONDITIONAL CONFIGURATION:**

```java
@Configuration
public class CacheConfig {

    @Bean
    @ConditionalOnProperty(name = "cache.enabled", havingValue = "true")
    public CacheManager redisCacheManager(RedisConnectionFactory factory) {
        return RedisCacheManager.create(factory);
    }

    @Bean
    @ConditionalOnMissingBean(CacheManager.class)
    public CacheManager noOpCacheManager() {
        return new NoOpCacheManager();
    }
}
```

**WHAT CHANGES AT SCALE:**
Startup time scales with the number of `@Configuration` classes and `@Bean` methods - each requires CGLIB processing and reflection. Spring Boot's auto-configuration defers bean creation where possible (`@Lazy`). Spring 6 and GraalVM AOT processing moves `@Configuration` processing to build time, eliminating runtime CGLIB costs entirely in native executables.

---

### 💻 Code Example

**Example 1 - Basic @Configuration with @Bean:**

```java
@Configuration
public class AppConfig {

    @Bean  // bean name: "dataSource"
    public DataSource dataSource(
            @Value("${db.url}") String url,
            @Value("${db.username}") String username,
            @Value("${db.password}") String password) {
        HikariDataSource ds = new HikariDataSource();
        ds.setJdbcUrl(url);
        ds.setUsername(username);
        ds.setPassword(password);
        return ds;
    }

    @Bean  // bean name: "jdbcTemplate"
    public JdbcTemplate jdbcTemplate(DataSource dataSource) {
        // Spring injects the DataSource bean above
        return new JdbcTemplate(dataSource);
    }
}
```

**Example 2 - Inter-bean dependency using method call (CGLIB in action):**

```java
@Configuration
public class ServiceConfig {

    @Bean
    public UserRepository userRepository(DataSource dataSource) {
        return new JpaUserRepository(dataSource);
    }

    @Bean
    public UserService userService() {
        // Calling userRepository() here goes through CGLIB proxy
        // → returns the SAME singleton cached earlier
        return new UserService(userRepository(null));
        // Note: prefer parameter injection (cleaner):
    }

    // PREFERRED: use parameter injection
    @Bean
    public UserService userService(UserRepository userRepository) {
        return new UserService(userRepository);
    }
}
```

**Example 3 - Conditional registration:**

```java
@Configuration
public class MessagingConfig {

    @Bean
    @ConditionalOnProperty("messaging.kafka.bootstrap-servers")
    public KafkaProducer<?, ?> kafkaProducer(KafkaProperties props) {
        return new KafkaProducer<>(props.buildProducerProperties());
    }

    @Bean
    @ConditionalOnMissingBean(KafkaProducer.class)
    public InMemoryMessageQueue fallbackQueue() {
        return new InMemoryMessageQueue();
    }
}
```

**Example 4 - Prototype-scoped bean:**

```java
@Configuration
public class ProcessorConfig {

    @Bean
    @Scope("prototype")  // new instance per request
    public ReportProcessor reportProcessor() {
        return new ReportProcessor();  // stateful - not safe to share
    }
}
```

---

### ⚖️ Comparison Table

| Approach                 | Type Safety | IDE Navigation    | Conditional Logic | Verbosity | Mode            |
| ------------------------ | ----------- | ----------------- | ----------------- | --------- | --------------- |
| XML `<bean>`             | None        | Limited (plugins) | Verbose           | High      | Pre-Spring 3.0  |
| `@Configuration`+`@Bean` | Full        | Full (Ctrl+Click) | Plain Java        | Low       | Full (CGLIB)    |
| `@Component` + auto-scan | Full        | Full              | Via @Conditional  | Zero      | Auto            |
| `@Component` + `@Bean`   | Full        | Full              | Plain Java        | Low       | Lite (no CGLIB) |

**Lite mode vs Full mode:**

- **Full:** `@Configuration` class - CGLIB proxy - inter-bean calls return cached singletons
- **Lite:** `@Component` with `@Bean` methods - no CGLIB - inter-bean calls create new instances

---

### ⚠️ Common Misconceptions

| Misconception                                                   | Reality                                                                                                                                                                           |
| --------------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| @Bean methods can be final or private                           | Cannot - CGLIB cannot override final/private methods. Startup will fail or lite mode will be silently used.                                                                       |
| @Configuration must extend some base class                      | No - it's a plain Java class annotated with @Configuration. CGLIB subclassing happens behind the scenes.                                                                          |
| @Bean methods must return the declared type                     | @Bean methods can return supertypes or even Object, but returning the concrete type allows Spring to apply type-based features correctly.                                         |
| @Component with @Bean is identical to @Configuration with @Bean | Critical difference: @Component with @Bean (lite mode) has NO CGLIB proxy. Inter-@Bean method calls create new instances in lite mode, potentially breaking singleton guarantees. |

---

### 🚨 Failure Modes & Diagnosis

**@Configuration class is final → CGLIB cannot proxy it**

**Symptom:**
`BeanCreationException: Could not generate CGLIB subclass of class ... final class`

**Root Cause:**
CGLIB creates a subclass of the `@Configuration` class at runtime. Java's `final` modifier prevents subclassing.

**Fix:**

```java
// BAD:
@Configuration
public final class AppConfig { ... }  // CGLIB fails

// GOOD:
@Configuration
public class AppConfig { ... }  // CGLIB can subclass
```

---

**Lite mode singleton violation (@Component + @Bean)**

**Symptom:**
Two beans that are supposed to share a `DataSourceProperties` instance have different instances - configuration mutations in one don't affect the other.

**Root Cause:**
`@Bean` methods on a `@Component` class are in lite mode - no CGLIB proxy. Direct method calls create new instances.

**Diagnostic Command / Tool:**

```java
// Check if your config class is CGLIB-enhanced:
System.out.println(dataSourceConfig.getClass().getName());
// Full mode: "...$$EnhancerBySpringCGLIB$$..."
// Lite mode: "...DataSourceConfig"
```

**Fix:**

```java
// Change @Component to @Configuration
@Configuration  // was @Component - now CGLIB proxied
public class DataSourceConfig { ... }
```

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**

- `IoC` - @Configuration is the Java-code expression of IoC container configuration
- `Bean` - @Bean methods produce the beans that the container manages
- `BeanFactory` - @Bean method results are stored in the BeanFactory

**Builds On This (learn these next):**

- `@Qualifier / @Primary` - how @Bean-defined beans are disambiguated at injection points
- `Circular Dependency` - what happens when @Bean method A calls @Bean method B which calls A
- `Auto-Configuration` - Spring Boot's @Configuration + @Conditional at industrial scale

**Alternatives / Comparisons:**

- `@Component` - stereotype-annotation-driven bean registration (no factory method, no lite mode)
- XML `<bean>` - the predecessor; identical semantics, no type safety

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ WHAT IT IS   │ @Configuration: Java config class.        │
│              │ @Bean: factory method that produces a bean │
├──────────────┼───────────────────────────────────────────┤
│ PROBLEM IT   │ XML configuration: not type-safe, not IDE- │
│ SOLVES       │ navigable, verbose, unchecked at compile  │
├──────────────┼───────────────────────────────────────────┤
│ KEY INSIGHT  │ @Configuration adds CGLIB proxy so that   │
│              │ inter-@Bean method calls return the cached│
│              │ singleton, not a new instance             │
├──────────────┼───────────────────────────────────────────┤
│ USE WHEN     │ Third-party classes that can't be annotated│
│              │ with @Component; conditional bean creation;│
│              │ complex wiring logic                      │
├──────────────┼───────────────────────────────────────────┤
│ AVOID WHEN   │ Avoid @Configuration on final classes;     │
│              │ avoid @Bean on private/final methods      │
├──────────────┼───────────────────────────────────────────┤
│ TRADE-OFF    │ Full type-safety and flexibility vs CGLIB │
│              │ overhead and non-final class requirement  │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "@Configuration is the Java cookbook;      │
│              │  @Bean is a recipe."                      │
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ Circular Dependency → CGLIB Proxy → AOP   │
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** Spring Boot's auto-configuration uses `@Configuration` + `@ConditionalOnMissingBean` extensively. The `@ConditionalOnMissingBean` condition is evaluated during `ConfigurationClassPostProcessor` - at bean definition time, before beans are actually created. This means the condition checks if a `BeanDefinition` is registered, not if a bean instance exists. What are the implications when a user's `@Bean` is defined in a `@Configuration` class that is processed AFTER the auto-configuration class? Would the auto-configured bean be created even though the user defined one?

**Q2.** `@Bean` methods can call each other directly within a `@Configuration` class, relying on CGLIB to return the singleton. But `@Bean` methods can also declare their dependencies as parameters. In what scenarios should you prefer method parameters over inter-method calls, even in a `@Configuration` class?
