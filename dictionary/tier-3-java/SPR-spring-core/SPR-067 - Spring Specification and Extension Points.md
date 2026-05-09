---
id: SPR-067
title: Spring Specification and Extension Points
category: Spring Core
tier: tier-3-java
folder: SPR-spring-core
difficulty: ★★★
depends_on: SPR-019, SPR-020, SPR-024, SPR-026, SPR-027, SPR-064
used_by:
related: SPR-066, SPR-044, SPR-068
tags:
  - spring
  - java
  - advanced
  - deep-dive
  - internals
  - pattern
status: complete
version: 1
layout: default
parent: "Spring Core"
grand_parent: "Technical Dictionary"
nav_order: 67
permalink: /spr/spring-specification-and-extension-points/
---

# SPR-067 - Spring Specification and Extension Points

⚡ TL;DR - Spring provides a layered extension API: `BeanDefinitionRegistryPostProcessor` for adding beans, `BeanPostProcessor` for wrapping them, `SmartLifecycle` for controlling start/stop order, and `@EnableXxx` for packaging reusable capabilities.

| Field          | Value                                                                                                                                                                                                                                        |
| -------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Depends on** | [[SPR-019 - IoC (Inversion of Control)]], [[SPR-020 - DI (Dependency Injection)]], [[SPR-024 - Bean Lifecycle]], [[SPR-026 - BeanPostProcessor]], [[SPR-027 - BeanFactoryPostProcessor]], [[SPR-064 - Spring Framework Internals Deep Dive]] |
| **Used by**    | -                                                                                                                                                                                                                                            |
| **Related**    | [[SPR-066 - Spring Native and GraalVM Integration]], [[SPR-044 - Spring Boot Auto-configuration Deep Dive]], [[SPR-068 - IoC-First Thinking]]                                                                                                |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**

You want to add cross-cutting behaviour to a Spring application - audit logging on every repository save, custom metrics on every `@Service` method, or loading additional `BeanDefinition` objects from a database schema. Without formal extension points, you have three bad options: copy-paste the behaviour into every bean (violation of DRY), fork the Spring Framework (impossible), or use AOP without understanding the underlying contract (fragile).

**THE BREAKING POINT:**

Framework adoption in enterprises requires customisation. Spring is used in everything from small REST APIs to enterprise integration platforms. Every Spring feature (transactions, security, data, caching) is itself implemented as an extension - `@Transactional` is a `BeanPostProcessor`, auto-configuration is a `BeanDefinitionRegistryPostProcessor`, Spring Security's `SecurityFilterChain` is a `SmartLifecycle`. If the extension API is not formal and stable, every release breaks every customisation.

**THE INVENTION MOMENT:**

Spring's extension point hierarchy was established in Spring 1.x and formalised in Spring 2.0. The key insight: every Spring feature can be implemented as a first-class citizen using the same API available to application developers. The framework does not use private APIs.

**EVOLUTION:**

- **2004:** `BeanPostProcessor`, `BeanFactoryPostProcessor` in Spring 1.0
- **2007:** `BeanDefinitionRegistryPostProcessor` in Spring 2.5 - enables programmatic bean registration
- **2011:** `@Enable*` pattern emerges (Spring 3.1) - `@EnableTransactionManagement`, `@EnableWebMvc`, `@EnableScheduling`
- **2014:** `ImportBeanDefinitionRegistrar` + `@Import` becomes the standard `@Enable*` implementation mechanism
- **2022:** `BeanRegistrationAotProcessor` added (Spring 6.0) - AOT-compatible extension point for native image

---

### 📘 Textbook Definition

Spring's **extension points** are defined interfaces that the framework calls at specific lifecycle phases, allowing application code (or library code) to participate in container initialization without modifying Spring itself. The hierarchy is: (1) `BeanDefinitionRegistryPostProcessor` / `BeanFactoryPostProcessor` operate on the _definition graph_ before instantiation; (2) `BeanPostProcessor` (and its subinterfaces) wraps _instances_ after construction; (3) `SmartLifecycle` controls _start/stop ordering_ after context refresh; (4) `ApplicationListener` / `ApplicationEventPublisher` provides _event-driven_ decoupling; (5) `@Import` + `ImportBeanDefinitionRegistrar` enables _annotation-driven_ activation of extension bundles (`@Enable*` pattern).

---

### ⏱️ Understand It in 30 Seconds

**One line:** Spring's extension points let you insert code at every phase of bean creation without touching the framework - definitions, instances, lifecycle, and events.

> Spring's extension points are like electrical sockets in a house. The house (Spring container) is built with standard sockets at specific locations (definition phase, instance phase, lifecycle phase). You plug in devices (your extension code) at the socket that matches what you need to do. `BeanPostProcessor` is the socket nearest the light switch (after beans are built). `BeanFactoryPostProcessor` is the socket in the blueprint room (before beans are built). `SmartLifecycle` is the master power switch order.

**One insight:** Every Spring feature you use is implemented using these same extension points. Understanding them lets you read Spring's own source code as clearly as documentation.

---

### 🔩 First Principles Explanation

**CORE INVARIANTS:**

1. Extension code must not depend on application beans that haven't been created yet
2. Extension points are ordered - `PriorityOrdered` < `Ordered` < unordered
3. `BeanPostProcessor` implementations must be registered before the beans they process are instantiated
4. The `@Enable*` pattern = `@Import(ConfigClass.class)` + configuration class that registers infrastructure beans
5. Extension points are symmetric: same contract for framework code and application code

**DERIVED DESIGN:**

From invariant 1 → `BeanPostProcessor` beans must not depend on application service beans (Spring warns about this with "not eligible" log messages).
From invariant 2 → `PriorityOrdered` is for framework-internal processors that must run first (e.g., `ConfigurationClassPostProcessor`). Use `Ordered` for library processors. Leave unordered for application processors.
From invariant 4 → `@EnableTransactionManagement` is `@Import(TransactionManagementConfigurationSelector.class)` which registers `InfrastructureAdvisorAutoProxyCreator` (a `BeanPostProcessor`) for `@Transactional` proxying.

**THE TRADE-OFFS:**

**Gain:** Formal, stable API for extending the framework; all Spring features use the same API; extension code is independently testable; AOT-compatible extension points exist for native image.

**Cost:** Extension points are order-sensitive and phase-sensitive; incorrect ordering causes subtle bugs; over-using extension points for business logic (instead of using them for infrastructure concerns) creates hard-to-debug startup overhead.

**ESSENTIAL vs ACCIDENTAL COMPLEXITY:**

**Essential:** A framework that supports cross-cutting concerns (AOP, transactions, security) without modifying user code requires formal hooks into bean lifecycle - this complexity is inherent.

**Accidental:** Spring's naming (`BeanDefinitionRegistryPostProcessor` vs `BeanFactoryPostProcessor`) is verbose. The mental model is simple: registry = add beans, factory = mutate beans.

---

### 🧪 Thought Experiment

**SETUP:** You want to add `@AuditLog` annotation support to all Spring services. When a method annotated with `@AuditLog` is called, an audit entry should be written.

**WITHOUT extension points:**

Option A: Write an AspectJ aspect using raw `@AspectJ` configuration without Spring integration - works but is not integrated with Spring's transaction lifecycle.
Option B: Add audit calls to every service method manually - violates DRY.
Option C: Use Spring AOP but configure it in every application module separately.

**WITH extension points:**

1. Declare `@AuditLog` annotation.
2. Write an `Advisor` (advice + pointcut for `@AuditLog`).
3. Write a `BeanPostProcessor` that detects any bean with `@AuditLog` methods and wraps it with the advisor.
4. Package as `@EnableAuditLog` = `@Import(AuditLogConfiguration.class)` which registers the `BeanPostProcessor`.
5. Any application that adds `@EnableAuditLog` to `@Configuration` gets audit logging on all `@AuditLog` methods - zero boilerplate per service.

**THE INSIGHT:**

The `@Enable*` pattern is the standard packaging mechanism for any reusable Spring extension. `@EnableTransactionManagement`, `@EnableCaching`, `@EnableScheduling`, `@EnableWebMvc` are all the same pattern.

---

### 🧠 Mental Model / Analogy

> Spring's extension points are like the operating system's plugin architecture. The OS (Spring container) defines standard interfaces (system calls = extension point interfaces). Applications (libraries, frameworks) register plugins that the OS calls at the right moment. The OS never needs to know the plugin's details - it just calls the interface. Spring Security is a plugin (SecurityFilterChain). Spring Data is a plugin (RepositoryFactoryBeanPostProcessor). Your `@EnableAuditLog` is a plugin. All equal-citizens.

**Element mapping:**

- Operating system → Spring container
- System call interface → extension point interface (`BeanPostProcessor`, etc.)
- OS loading plugins at boot → extension point registration in `refresh()`
- Plugin hooks → `postProcessBeforeInitialization()`, `postProcessBeanDefinitionRegistry()`
- Plugin ordering → `PriorityOrdered` / `Ordered`
- Plugin package → `@Enable*` + `@Import`

Where this analogy breaks down: OS plugins are loaded dynamically; Spring extension points are resolved at startup from the application's classpath and registered into a fixed ordering - there is no hot-reload of extension points at runtime.

---

### 📶 Gradual Depth - Four Levels

**Level 1 - What it is (anyone can understand):**
Spring has defined "hook points" where you can insert your own code. When Spring is building your application's objects, it calls your hook at the right time - before an object is created, after, when the app starts, when it stops. This is how Spring features like transactions and security work, and you can use the same hooks.

**Level 2 - How to use it (junior developer):**
Implement `BeanPostProcessor` and annotate with `@Component` to process all beans after creation. Implement `SmartLifecycle` to execute code at startup/shutdown with a controlled order. Use `ApplicationEventPublisher.publishEvent()` and `@EventListener` for loose coupling. Use `@Enable*` annotations provided by libraries (e.g., `@EnableAsync`) to activate infrastructure without XML.

**Level 3 - How it works (mid-level engineer):**
`ConfigurationClassPostProcessor` (a `BeanDefinitionRegistryPostProcessor`) is the first processor Spring runs. It scans for `@Configuration` classes, processes `@Bean`, `@ComponentScan`, `@Import`, and `@EnableXxx`. `@EnableXxx` annotations typically use `@Import(ConfigClass.class)` which registers infrastructure `BeanPostProcessor` beans. These processors are then instantiated early (during `registerBeanPostProcessors()`) so they are in place before any application bean is created. The `SmartLifecycle` beans are started after all singletons are initialised, in ascending `getPhase()` order.

**Level 4 - Why it was designed this way (senior/staff):**
The `@Enable*` + `@Import` mechanism was introduced in Spring 3.1 to replace XML namespace handlers (`<tx:annotation-driven/>`). The design goal was to enable modular, composable feature activation using Java annotations. The key constraint: `@Enable*` must be self-contained - it should not require any additional configuration to work. This drove the pattern of using `ImportSelector` (for conditional imports based on `@Enable*` annotation attributes) and `ImportBeanDefinitionRegistrar` (for programmatic bean registration from annotation metadata). Spring Boot's auto-configuration extends this pattern: instead of requiring `@EnableAutoConfiguration` on specific beans, it uses `spring.factories` / `imports` files to discover `@Configuration` classes automatically.

**Expert Thinking Cues:**

- `DeferredImportSelector` is the `@Enable*` variant that runs _after_ all regular configuration is processed - used by Spring Boot auto-configuration to allow user config to override auto-config
- `@ConditionalOnMissingBean` works because auto-configuration uses `DeferredImportSelector` - user `@Configuration` runs first, `@ConditionalOnMissingBean` fires after and sees user beans
- `SmartLifecycle.isRunning()` must accurately reflect state; Spring uses it for graceful shutdown ordering

---

### ⚙️ How It Works (Mechanism)

```
Extension Point Hierarchy:

Phase 1 (Definition):
  BeanDefinitionRegistryPostProcessor
    └─ postProcessBeanDefinitionRegistry()
       [Add/remove BeanDefinitions]
       Example: ConfigurationClassPostProcessor
                (processes @Configuration)

  BeanFactoryPostProcessor
    └─ postProcessBeanFactory()
       [Mutate existing BeanDefinitions]
       Example: PropertySourcesPlaceholderConfigurer
                (resolves ${...} placeholders)

Phase 2 (Instance):
  InstantiationAwareBeanPostProcessor
    ├─ postProcessBeforeInstantiation()
    |  [Can short-circuit instantiation]
    └─ postProcessAfterInstantiation()
       [Post-construction hook]

  BeanPostProcessor
    ├─ postProcessBeforeInitialization()
    |  [Before @PostConstruct, afterPropertiesSet]
    └─ postProcessAfterInitialization()
       [After init - where proxies are created]
       Example: AbstractAutoProxyCreator
                (creates @Transactional proxies)

Lifecycle Phase (Post-refresh):
  SmartLifecycle
    ├─ start()  [ascending phase order]
    └─ stop()   [descending phase order]
    Example: KafkaListenerEndpointRegistry,
             EmbeddedWebServer

Events:
  ApplicationListener<E>  or  @EventListener
    └─ onApplicationEvent(E event)
    Example: @EventListener(ContextRefreshedEvent)
```

---

### 🔄 The Complete Picture - End-to-End Flow

**NORMAL FLOW - `@EnableAuditLog` activation:**

```
[@EnableAuditLog on @Configuration class]
     |
     ├─ @Import(AuditLogConfiguration.class)
     |    └─ ConfigurationClassPostProcessor
     |         registers AuditLogBeanPostProcessor
     |           ← YOU ARE HERE (Phase 1)
     |
     ├─ registerBeanPostProcessors()
     |    └─ AuditLogBeanPostProcessor instantiated
     |       and registered
     |
     ├─ finishBeanFactoryInitialization()
     |    └─ For each @Service bean:
     |         AuditLogBPP.postProcessAfterInit()
     |         └─ Wraps @AuditLog methods with proxy
     |
[Application ready: @AuditLog methods are proxied]
```

**FAILURE PATH:**

- `BeanPostProcessor` depends on `@Service` bean → "not eligible" warning → `@Service` not proxied by that `BPP`
- `@EventListener` method throws → `ApplicationEventMulticaster` catches; `SimpleApplicationEventMulticaster` re-throws by default
- `SmartLifecycle.start()` blocks indefinitely → context refresh hangs; `Spring.setDefaultTimeout()` in tests

**WHAT CHANGES AT SCALE:**

In large applications with 50+ extension-point beans, startup time increases linearly. Profile with Spring Boot actuator's startup endpoint (`/actuator/startup`) to find slow `BeanPostProcessor` or `SmartLifecycle` implementations.

---

### 💻 Code Example

**`@Enable*` pattern - complete implementation:**

```java
// 1. The activation annotation
@Target(ElementType.TYPE)
@Retention(RetentionPolicy.RUNTIME)
@Documented
@Import(AuditLogConfiguration.class)
public @interface EnableAuditLog {
    String applicationName() default "app";
}

// 2. The infrastructure configuration
// (imported via @EnableAuditLog)
@Configuration
public class AuditLogConfiguration {

    @Bean
    public AuditLogBeanPostProcessor
            auditLogBeanPostProcessor(
            AuditLogRepository repository) {
        return new AuditLogBeanPostProcessor(
            repository);
    }
}

// 3. The BeanPostProcessor
public class AuditLogBeanPostProcessor
        implements BeanPostProcessor {

    private final AuditLogRepository repository;

    @Override
    public Object postProcessAfterInitialization(
            Object bean, String beanName) {
        boolean hasAuditLog =
            Arrays.stream(
                    bean.getClass().getMethods())
                .anyMatch(m -> m.isAnnotationPresent(
                    AuditLog.class));
        if (!hasAuditLog) return bean;
        return Proxy.newProxyInstance(
            bean.getClass().getClassLoader(),
            bean.getClass().getInterfaces(),
            (proxy, method, args) -> {
                Object result = method.invoke(
                    bean, args);
                if (method.isAnnotationPresent(
                        AuditLog.class)) {
                    repository.log(
                        method.getName(), args);
                }
                return result;
            });
    }
}
```

**`ImportBeanDefinitionRegistrar` for dynamic registration:**

```java
public class ConditionalMetricRegistrar
        implements ImportBeanDefinitionRegistrar {

    @Override
    public void registerBeanDefinitions(
            AnnotationMetadata importingClassMetadata,
            BeanDefinitionRegistry registry) {
        // Read annotation attributes
        Map<String, Object> attrs =
            importingClassMetadata
                .getAnnotationAttributes(
                    EnableMetrics.class.getName());
        boolean enabled =
            (Boolean) attrs.get("enabled");

        if (enabled) {
            RootBeanDefinition def =
                new RootBeanDefinition(
                    MetricsBeanPostProcessor.class);
            registry.registerBeanDefinition(
                "metricsBpp", def);
        }
    }
}
```

---

### ⚖️ Comparison Table

| Extension Point                       | Phase               | When to Use                                                                      |
| ------------------------------------- | ------------------- | -------------------------------------------------------------------------------- |
| `BeanDefinitionRegistryPostProcessor` | 1 - Definition      | Adding new `BeanDefinition` objects from external sources                        |
| `BeanFactoryPostProcessor`            | 1 - Definition      | Mutating existing definitions (property values, scope)                           |
| `InstantiationAwareBeanPostProcessor` | 2 - Pre-instance    | Replacing instantiation logic (Mockito `@MockBean`)                              |
| `BeanPostProcessor`                   | 2 - Post-instance   | Wrapping beans with proxies (AOP, metrics, audit)                                |
| `SmartLifecycle`                      | 3 - Post-refresh    | Ordered start/stop (servers, consumers, schedulers)                              |
| `ApplicationListener`                 | Event-driven        | Reacting to application events (startup, shutdown, custom)                       |
| `ImportBeanDefinitionRegistrar`       | 1 - via `@Import`   | `@Enable*` pattern: register beans from annotation metadata                      |
| `DeferredImportSelector`              | 1 - last in Phase 1 | Auto-configuration (runs after user config, enables `@ConditionalOnMissingBean`) |

---

### ⚠️ Common Misconceptions

| Misconception                                    | Reality                                                                                                                                                                                                                         |
| ------------------------------------------------ | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| "`@Enable*` is just a shortcut for `@Import`"    | `@Enable*` packages a complete feature. The `@Import` inside it may include `BeanPostProcessor`, `Advisor`, configuration conditions, and `ImportSelector` - a full capability bundle.                                          |
| "Any bean can be a `BeanPostProcessor`"          | `BeanPostProcessor` beans must not depend on `@Service` beans. If they do, those service beans are created early before all processors are registered - and will not be processed by later `BeanPostProcessor` implementations. |
| "`@EventListener` is synchronous"                | By default, yes - `SimpleApplicationEventMulticaster` calls listeners synchronously. Use `@Async` on the listener method for asynchronous dispatch.                                                                             |
| "`SmartLifecycle` start order is alphabetical"   | `SmartLifecycle` start order is controlled by `getPhase()` return value. Lower phase = earlier start. Default phase is `Integer.MAX_VALUE` (starts last).                                                                       |
| "You need `@Order` on `BeanPostProcessor` beans" | `@Order` does not affect `BeanPostProcessor` ordering. They must implement `Ordered` or `PriorityOrdered` interface. `@Order` only affects `@EventListener` ordering.                                                           |

---

### 🚨 Failure Modes & Diagnosis

**Mode 1: BeanPostProcessor misses beans due to early creation**

**Symptom:** `@Transactional` on certain beans has no effect. Spring logs: `Bean 'X' of type Y is not eligible for getting processed by all BeanPostProcessor interfaces.`

**Root Cause:** Bean `X` was created during `registerBeanPostProcessors()` phase (because a `BeanPostProcessor` depends on `X`). It was created before all `BeanPostProcessor` implementations were registered, so some processors were not applied.

**Diagnostic:**

```bash
java -jar app.jar \
  --logging.level.org.springframework.context
    .support.PostProcessorRegistrationDelegate=DEBUG
# Log shows which beans created early
# and which processors missed them
```

**Fix:** Remove the dependency causing early creation. Mark it `@Lazy`. Or extract the common dependency to a separate, infrastructure-only bean.

**Prevention:** Architectural rule: `BeanPostProcessor` implementations must only depend on other infrastructure beans (`DataSource`, `Environment`) - never on application service beans.

---

**Mode 2: `SmartLifecycle.stop()` hangs on shutdown**

**Symptom:** Application shutdown hangs indefinitely; Kubernetes sends `SIGKILL` after grace period; in-flight requests are lost.

**Root Cause:** `SmartLifecycle.stop()` implementation has an infinite wait, deadlocked callback, or missing `callback.run()` call in the `stop(Runnable callback)` overload.

**Diagnostic:**

```bash
# Thread dump during shutdown
kill -3 <pid>  # on Linux
# Look for threads stuck in SmartLifecycle.stop()
# Check the lifecycle bean implementation
# for missing callback.run()
```

**Fix:**

```java
@Override
public void stop(Runnable callback) {
    // Must always call callback, even on error
    try {
        doStop();
    } finally {
        callback.run();  // REQUIRED - signals done
    }
}
```

**Prevention:** Always implement `stop(Runnable callback)` rather than `stop()` for `SmartLifecycle`. Add `spring.lifecycle.timeout-per-shutdown-phase=30s` as a hard upper bound.

---

**Mode 3: `@EventListener` in security context exposes sensitive data (Security failure mode)**

**Symptom:** An `@EventListener(UserDeletedEvent.class)` sends a notification email with user PII. A malicious bean publishes a `UserDeletedEvent` with fabricated user data, causing notification emails to be sent to wrong addresses.

**Root Cause:** `ApplicationEvent` objects are arbitrary POJOs. Without source validation, any bean can publish any event with any payload.

**Diagnostic:**

```java
// Review: who publishes UserDeletedEvent?
// Are event sources validated?
@EventListener
public void onUserDeleted(UserDeletedEvent event) {
    // Is event.getSource() trusted?
    // Is event.getUser() from a trusted source?
}
```

**Fix:** Validate event source. Enrich events from authoritative data source on receipt, not from event payload:

```java
@EventListener
public void onUserDeleted(
        UserDeletedEvent event) {
    // Fetch from DB, not from event payload
    User user = userRepository
        .findById(event.getUserId())
        .orElseThrow();
    // user is authoritative - event.getUserId()
    // is just an ID, not sensitive data
    notificationService.sendDeletion(user.email());
}
```

**Prevention:** Events should carry minimal data (IDs, not full objects). Listeners should re-fetch from authoritative source.

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**

- [[SPR-026 - BeanPostProcessor]] - the most commonly used extension point
- [[SPR-027 - BeanFactoryPostProcessor]] - the definition-phase extension point
- [[SPR-064 - Spring Framework Internals Deep Dive]] - the container lifecycle these points plug into

**Builds On This (learn these next):**

- [[SPR-044 - Spring Boot Auto-configuration Deep Dive]] - auto-configuration uses `DeferredImportSelector` + `@Conditional`
- [[SPR-066 - Spring Native and GraalVM Integration]] - `BeanRegistrationAotProcessor` for native-compatible extensions
- [[SPR-068 - IoC-First Thinking]] - how to design systems that use extension points correctly

**Alternatives / Comparisons:**

- CDI extension API (Jakarta EE) - `javax.enterprise.inject.spi.Extension` provides equivalent lifecycle hooks
- Guice `Module` - simpler but less expressive; no post-processing concept
- Micronaut `BeanCreatedEventListener` - compile-time equivalent of `BeanPostProcessor`

---

### 📌 Quick Reference Card

```
+----------------------------------------------------------+
| WHAT IT IS    | Formal API for plugging into Spring's    |
|               | bean lifecycle at 5 distinct phases      |
| PROBLEM       | Adding cross-cutting infrastructure      |
|               | without modifying framework or beans     |
| KEY INSIGHT   | Every Spring feature is an extension;    |
|               | application code uses the same hooks     |
| USE WHEN      | Writing shared library features; adding  |
|               | cross-cutting infrastructure; @Enable*   |
| AVOID WHEN    | Business logic - use services/events     |
|               | instead of BeanPostProcessors            |
| TRADE-OFF     | Flexibility vs ordering complexity       |
| ONE-LINER     | BFPostProcessor: defs; BPostProcessor:   |
|               | instances; SmartLifecycle: start/stop    |
| NEXT EXPLORE  | SPR-044 (Auto-configuration),            |
|               | SPR-068 (IoC-First Thinking)             |
+----------------------------------------------------------+
```

**If you remember only 3 things:**

1. `BeanFactoryPostProcessor` = mutate definitions; `BeanPostProcessor` = wrap instances - these are the two core extension phases
2. The `@Enable*` pattern = `@Import` + infrastructure `@Configuration` class - the standard way to package reusable Spring extensions
3. `BeanPostProcessor` beans must not depend on application service beans - doing so causes "not eligible" skipping of that service

**Interview one-liner:** "Spring's extension points form a hierarchy: `BeanDefinitionRegistryPostProcessor` adds beans (Phase 1), `BeanPostProcessor` wraps them (Phase 2), and `SmartLifecycle` controls start/stop order - all Spring features (AOP, transactions, security) are implemented using these same public APIs."

---

### 💎 Transferable Wisdom

**Reusable Engineering Principle:** _A framework that uses its own public API for all built-in features is self-documenting and fully extensible._ When the framework authors cannot use private shortcuts not available to application developers, they are forced to design a clean, sufficient extension API. The constraint produces quality.

**Where else this pattern appears:**

- **Webpack plugin API** - all built-in Webpack features (chunk splitting, minification) are Webpack plugins; application plugins use the identical hook-based API
- **VS Code extensions** - VS Code's core features (IntelliSense, debugger) are extensions; your extension uses the same `vscode.Extension` API
- **Kubernetes controllers** - all Kubernetes built-in resources (Deployments, Services) are managed by controllers using the Kubernetes controller-runtime API - the same API available for custom operators

---

### 💡 The Surprising Truth

Spring's `BeanPostProcessor` interface was originally designed in 2003 for one specific purpose: AOP proxy creation. Rod Johnson wanted AOP to be a first-class citizen without baking proxy creation into the core container. By making proxy creation a `BeanPostProcessor` - a publicly documented interface - he inadvertently created the most used and most powerful extension point in the Spring ecosystem. Spring Security's filter chain registration, Spring Data's repository proxy creation, Spring Cache's `@Cacheable` proxying, and Spring Async's `@Async` proxy - all are `BeanPostProcessor` implementations that followed the same pattern invented for AOP 20 years ago. The single architectural decision to make AOP an extension rather than a built-in feature produced the extensibility that made the entire Spring ecosystem possible.

---

### 🧠 Think About This Before We Continue

**Question 1 (A - System Interaction):** You are writing a library that provides `@RateLimit` annotation support. When placed on a Spring `@Service` method, calls to that method should be rate-limited using a Redis token bucket. Describe the complete implementation using Spring extension points: which interface to implement, how to activate it via `@EnableRateLimit`, and how the proxy wraps the rate limit check around the method call.

_Hint:_ Consider `BeanPostProcessor` that creates a JDK proxy for each bean with `@RateLimit` methods, `ImportBeanDefinitionRegistrar` to register the post-processor, and `@EnableRateLimit` as `@Import(RateLimitConfiguration.class)`.

**Question 2 (C - Design Trade-off):** Spring Boot auto-configuration uses `DeferredImportSelector` to ensure auto-configuration runs _after_ user configuration, enabling `@ConditionalOnMissingBean` to check for user-provided beans before registering auto-configured ones. A library author uses a regular `ImportSelector` (not deferred). What breaks, and why?

_Hint:_ Regular `ImportSelector` runs during `ConfigurationClassPostProcessor`'s first pass, at the same time as user `@Configuration` classes. The processing order between user config and the library's config becomes undefined. `@ConditionalOnMissingBean` may fire before the user's bean is registered.

**Question 3 (E - First Principles):** The `SmartLifecycle` contract includes both `start()` and `stop(Runnable callback)`. Why is the `stop(Runnable)` overload needed in addition to `stop()`? Describe a real scenario where the distinction matters for correctness during application shutdown.

_Hint:_ `stop()` is synchronous. `stop(Runnable callback)` supports _asynchronous_ shutdown - the bean may need to finish in-flight requests before signalling completion. The container waits for `callback.run()` before proceeding to the next lifecycle phase. What happens to in-flight Kafka messages if `callback.run()` is called before the consumer finishes committing offsets?
