---
layout: default
title: "Bean Lifecycle"
parent: "Spring Core"
nav_order: 24
permalink: /spring/bean-lifecycle/
id: SPR-024
category: Spring Core
difficulty: ★★☆
depends_on: Bean, BeanFactory, ApplicationContext, DI
used_by: BeanPostProcessor, BeanFactoryPostProcessor, AOP, Spring Security
related: BeanPostProcessor, InitializingBean, DisposableBean, SmartLifecycle
tags:
  - spring
  - springboot
  - internals
  - intermediate
  - architecture
---

# SPR-024 — Bean Lifecycle

⚡ TL;DR — Bean Lifecycle is the precise sequence of events from bean definition to destruction that Spring orchestrates, giving you hooks to run code at each stage.

| #376            | Category: Spring Core                                               | Difficulty: ★★☆ |
| :-------------- | :------------------------------------------------------------------ | :-------------- |
| **Depends on:** | Bean, BeanFactory, ApplicationContext, DI                           |                 |
| **Used by:**    | BeanPostProcessor, BeanFactoryPostProcessor, AOP, Spring Security   |                 |
| **Related:**    | BeanPostProcessor, InitializingBean, DisposableBean, SmartLifecycle |                 |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
A `DatabaseConnectionPool` bean needs to open connections after Spring injects the `DataSource` configuration, and close those connections cleanly when the application shuts down. Without lifecycle hooks, you either run setup code in the constructor (before `DataSource` is injected — it's null) or call `init()` manually after Spring starts (requiring coordination you can't guarantee). On shutdown, the JVM exits without closing connections, leaving the database with orphaned sessions. This repeats for every resource that needs orderly initialization and cleanup.

**THE BREAKING POINT:**
Infrastructure beans need post-construction initialization that runs _after_ all dependencies are injected. Constructors can't do this — dependencies are null at construction time for field-injected beans. Shutdown hooks need to know about application-managed resources. Without a formal lifecycle, every team invents their own convention, startup order becomes fragile, and resource leaks on shutdown are common.

**THE INVENTION MOMENT:**
"This is exactly why the Spring Bean Lifecycle was formalized."

---

### 📘 Textbook Definition

The **Spring Bean Lifecycle** is the complete sequence of phases a bean passes through from definition registration to destruction. It comprises: BeanDefinition registration, `BeanFactoryPostProcessor` processing (modifying definitions), bean instantiation, dependency injection, `BeanPostProcessor` before-initialization processing, initialization callbacks (`@PostConstruct`, `InitializingBean.afterPropertiesSet()`, custom init method), `BeanPostProcessor` after-initialization processing (when AOP proxies are created), normal usage, and finally destruction callbacks (`@PreDestroy`, `DisposableBean.destroy()`, custom destroy method) triggered by context close.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
Bean Lifecycle is Spring's birth-to-death choreography for every object it manages.

**One analogy:**

> A bean's lifecycle is like an employee's journey at a company: hired (instantiated), given their tools and desk (dependencies injected), trained (init callbacks), productive for years (normal usage), and eventually given an offboarding checklist to complete before leaving (destroy callbacks). Spring is the HR department managing every stage.

**One insight:**
The lifecycle exists to solve a sequencing problem: dependencies must be fully injected before initialization code runs, and initialization must complete before the bean is handed to callers. The `BeanPostProcessor` hooks at before/after initialization are how all of Spring's AOP, transaction management, caching, and security annotations get applied — they intercept every bean during this phase.

---

### 🔩 First Principles Explanation

**CORE INVARIANTS:**

1. Initialization callbacks run _after_ all dependencies are injected — never before.
2. Destruction callbacks run during an orderly shutdown — not on garbage collection (singletons are never GC'd while the context is alive).
3. `BeanPostProcessor` runs around every initialization — this is how cross-cutting concerns (AOP) are applied without changing the bean itself.

**DERIVED DESIGN:**
The lifecycle has two non-obvious phases that most developers miss:

**Phase between injection and init:** `BeanPostProcessor.postProcessBeforeInitialization()` runs here. This is where `@PostConstruct` is processed by `CommonAnnotationBeanPostProcessor`.

**Phase after init:** `BeanPostProcessor.postProcessAfterInitialization()` runs here. This is where Spring replaces the raw bean with an AOP proxy (e.g., for `@Transactional`). The proxy is what gets stored in the singleton cache — not the original object.

This ordering explains why `@Transactional` works: Spring waits until the bean is fully initialized before wrapping it in a proxy, ensuring the proxy wraps a fully functional object.

**THE TRADE-OFFS:**

**Gain:** Guaranteed sequencing of setup and teardown. All Spring features (AOP, transactions, security) are applied uniformly via lifecycle hooks.

**Cost:** The lifecycle is complex — missing a detail (like the proxy replacement in `postProcessAfterInitialization`) causes subtle bugs like self-invocation bypass. The `Aware` interfaces (`ApplicationContextAware`, `BeanNameAware`) add coupling to Spring's internals.

---

### 🧪 Thought Experiment

**SETUP:**
A `CacheManager` bean needs to pre-warm a local cache by reading from the database. The database URL is injected via `@Value`. The cache must be warm before the application starts serving traffic.

**WHAT HAPPENS WITHOUT lifecycle hooks:**
Approach 1 — In the constructor: `@Value` hasn't been processed yet. `dbUrl` is null. `NullPointerException` in constructor. Application fails to start.
Approach 2 — In a `@Bean` method body: works for `@Bean` factory methods, but `@Value` fields aren't available in factory methods without an extra parameter.
Approach 3 — Manual `cacheManager.warmUp()` in `main()`: fragile — you must know to call it, and it runs before Spring has fully started other beans.

**WHAT HAPPENS WITH `@PostConstruct`:**

1. Spring injects `@Value("${db.url}") String dbUrl` into the field.
2. Spring calls `warmUpCache()` annotated with `@PostConstruct`.
3. `dbUrl` is fully resolved. Query runs. Cache is warm.
4. Spring proceeds to mark the bean as ready.
5. First HTTP request hits a warm cache — no cold-start latency.

**THE INSIGHT:**
`@PostConstruct` is the correct place for any initialization that depends on injected values. It runs after injection, before the bean is used — exactly the window needed.

---

### 🧠 Mental Model / Analogy

> A bean's lifecycle is an assembly line. The chassis (instance) starts bare, then station by station: the engine (dependencies) is installed, then safety systems (AOP proxy) are added, then a quality check (init callbacks) runs. Only after passing all stations does the car (bean) roll off the line ready for customers. On end-of-life, the car goes through a disposal process (destroy callbacks) before being recycled.

- "Bare chassis enters the line" → bean instantiation
- "Parts installed" → dependency injection
- "Safety system added" → BeanPostProcessor wrapping (AOP)
- "Quality check" → @PostConstruct / afterPropertiesSet()
- "Car ready for customers" → bean stored in singleton cache, available for injection
- "Disposal process" → @PreDestroy / destroy()

**Where this analogy breaks down:** Unlike an assembly line, Spring's lifecycle has bidirectional communication — beans can query the container during init (via `Aware` interfaces), and containers can query beans (via `SmartLifecycle.isRunning()`).

---

### 📶 Gradual Depth — Four Levels

**Level 1 — What it is (anyone can understand):**
Spring manages every bean's life. It creates beans, sets them up, lets them work, and cleans them up when the app stops. You can plug code into the "setup" and "cleanup" stages using `@PostConstruct` and `@PreDestroy`.

**Level 2 — How to use it (junior developer):**
Use `@PostConstruct` on a method that needs to run after injection (cache warming, validation, connection setup). Use `@PreDestroy` on a method that runs on shutdown (closing connections, flushing buffers). Both annotations are from `jakarta.annotation` — no Spring import needed, making your beans portable.

**Level 3 — How it works (mid-level engineer):**
The lifecycle is orchestrated in `AbstractAutowireCapableBeanFactory.doCreateBean()`. After `populateBean()` (injection), it calls `initializeBean()` which runs: (1) `Aware` interface callbacks, (2) `BeanPostProcessor.postProcessBeforeInitialization()` — where `@PostConstruct` is processed, (3) `afterPropertiesSet()` / custom init method, (4) `BeanPostProcessor.postProcessAfterInitialization()` — where AOP proxies are created. The result of step 4 (potentially a proxy) is stored in the singleton cache.

**Level 4 — Why it was designed this way (senior/staff):**
The two-phase BeanPostProcessor hooks (before and after init) solve a fundamental ordering problem: AOP proxies must wrap a _fully initialized_ bean. If the proxy were created before init, the init callbacks would run on the proxy, not the real object — which would break for constructors, reflection-based injection, and `Aware` callbacks. The post-init hook guarantees the proxy wraps a fully ready bean. This is also why `@Async` beans can cause circular dependency issues: the proxy is created after init, but another bean may have cached a reference to the pre-proxy instance during init.

---

### ⚙️ How It Works (Mechanism)

**Complete Bean Lifecycle Sequence:**

```
┌──────────────────────────────────────────────────────────┐
│         PHASE 1: DEFINITION (before instantiation)      │
├──────────────────────────────────────────────────────────┤
│ 1. BeanDefinition registered (component scan / @Bean)   │
│ 2. BeanFactoryPostProcessor.postProcessBeanFactory()    │
│    - PropertySourcesPlaceholderConfigurer resolves       │
│      ${placeholders} in bean definitions                 │
│    - @ConfigurationClassPostProcessor processes          │
│      @Configuration classes                             │
└──────────────────────────────────────────────────────────┘
                          ↓
┌──────────────────────────────────────────────────────────┐
│         PHASE 2: INSTANTIATION & INJECTION               │
├──────────────────────────────────────────────────────────┤
│ 3. Bean instantiated (constructor called)               │
│ 4. BeanNameAware.setBeanName() [if implemented]         │
│ 5. BeanFactoryAware.setBeanFactory() [if implemented]   │
│ 6. ApplicationContextAware.setApplicationContext()      │
│ 7. Dependencies injected (@Autowired fields/setters)    │
└──────────────────────────────────────────────────────────┘
                          ↓
┌──────────────────────────────────────────────────────────┐
│         PHASE 3: INITIALIZATION                          │
├──────────────────────────────────────────────────────────┤
│ 8. BeanPostProcessor.postProcessBeforeInitialization()  │
│    - @PostConstruct methods run here                    │
│    - (via CommonAnnotationBeanPostProcessor)             │
│ 9. InitializingBean.afterPropertiesSet() [if impl]      │
│ 10. Custom init-method [if declared]                    │
│ 11. BeanPostProcessor.postProcessAfterInitialization()  │
│     - AOP proxy created here (replaces raw bean)        │
│     - @Transactional, @Async proxies wrapped here       │
└──────────────────────────────────────────────────────────┘
                          ↓
┌──────────────────────────────────────────────────────────┐
│         PHASE 4: USE                                     │
├──────────────────────────────────────────────────────────┤
│ 12. Bean stored in singleton cache                      │
│ 13. Injected into dependent beans                       │
│ 14. Application serves requests                         │
└──────────────────────────────────────────────────────────┘
                          ↓
┌──────────────────────────────────────────────────────────┐
│         PHASE 5: DESTRUCTION                             │
├──────────────────────────────────────────────────────────┤
│ 15. context.close() or JVM shutdown hook triggered      │
│ 16. @PreDestroy methods called                          │
│     (via DestructionAwareBeanPostProcessor)              │
│ 17. DisposableBean.destroy() [if implemented]           │
│ 18. Custom destroy-method [if declared]                 │
└──────────────────────────────────────────────────────────┘
```

---

### 🔄 The Complete Picture — End-to-End Flow

**NORMAL FLOW:**

```
@SpringBootApplication
    ↓
Component scan → BeanDefinitions registered
    ↓
BeanFactoryPostProcessors run (resolve properties)
    ↓
BeanPostProcessors registered
    ↓
Singleton beans instantiated → injected → initialized
   ← YOU ARE HERE (each bean goes through full lifecycle)
    ↓
AOP proxies replace raw beans in cache
    ↓
ApplicationReadyEvent fired → app serves traffic
    ↓
[shutdown]
    ↓
@PreDestroy callbacks → DisposableBean.destroy()
    ↓
Context closed, JVM exits
```

**FAILURE PATH:**

```
@PostConstruct method throws exception
    ↓
BeanCreationException wraps the exception
    ↓
initializeBean() fails → doCreateBean() fails
    ↓
preInstantiateSingletons() aborts
    ↓
ApplicationContext.refresh() throws
    ↓
Application fails to start
```

**WHAT CHANGES AT SCALE:**
With hundreds of beans, the cumulative time of all `@PostConstruct` methods determines startup time. One slow `@PostConstruct` (20s database migration) blocks the entire startup sequence, as `preInstantiateSingletons()` is synchronous. Use `ApplicationReadyEvent` for non-critical initialization to parallelize startup.

---

### 💻 Code Example

**Example 1 — @PostConstruct and @PreDestroy:**

```java
@Component
public class ReportCache {
    private final ReportRepository repo;
    private Map<String, Report> cache;

    public ReportCache(ReportRepository repo) {
        this.repo = repo;
    }

    @PostConstruct  // runs AFTER injection, BEFORE bean is used
    public void warmUp() {
        // repo is injected here — safe to use
        cache = repo.findAllActive()
            .stream()
            .collect(Collectors.toMap(Report::getId, r -> r));
        log.info("Cache warmed: {} reports", cache.size());
    }

    @PreDestroy     // runs during context close
    public void flushPendingWrites() {
        repo.saveAll(cache.values());
        log.info("Cache flushed to database");
    }
}
```

**Example 2 — Initialization order: wrong vs right:**

```java
// BAD: field injection + constructor init
@Component
public class ServiceConfig {
    @Autowired
    private ConfigRepository repo;  // null during construction!

    public ServiceConfig() {
        String config = repo.find("key");  // NullPointerException
    }
}

// GOOD: @PostConstruct for post-injection init
@Component
public class ServiceConfig {
    private final ConfigRepository repo;
    private String config;

    public ServiceConfig(ConfigRepository repo) {
        this.repo = repo;  // injected; not null
    }

    @PostConstruct
    public void loadConfig() {
        config = repo.find("key");  // repo is available
    }
}
```

**Example 3 — SmartLifecycle for ordered startup/shutdown:**

```java
@Component
public class KafkaConsumerManager implements SmartLifecycle {
    private volatile boolean running = false;

    @Override
    public void start() {
        // Called after ALL beans are initialized
        startConsumers();
        running = true;
    }

    @Override
    public void stop() {
        stopConsumers();
        running = false;
    }

    @Override
    public boolean isRunning() {
        return running;
    }

    @Override
    public int getPhase() {
        return 100;  // higher = starts later, stops first
    }
}
```

---

### ⚖️ Comparison Table

| Hook                                    | When It Runs                  | Interface Required | Spring Dependency |
| --------------------------------------- | ----------------------------- | ------------------ | ----------------- |
| `@PostConstruct`                        | After injection, before use   | No                 | JSR-250 only      |
| `InitializingBean.afterPropertiesSet()` | Same as @PostConstruct        | Spring interface   | Yes               |
| Custom `init-method`                    | Same as @PostConstruct        | No                 | Config only       |
| `@PreDestroy`                           | Context close, before destroy | No                 | JSR-250 only      |
| `DisposableBean.destroy()`              | Same as @PreDestroy           | Spring interface   | Yes               |
| `SmartLifecycle.start()/stop()`         | After/before all beans ready  | Spring interface   | Yes               |

**How to choose:** Prefer `@PostConstruct` and `@PreDestroy` for most cases — no Spring interface coupling. Use `SmartLifecycle` for ordered startup (e.g., start consuming Kafka only after all services are ready).

---

### ⚠️ Common Misconceptions

| Misconception                                            | Reality                                                                                                                                                             |
| -------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| @PostConstruct runs at bean creation (in constructor)    | It runs after construction AND after injection. The constructor runs first, then injection, then @PostConstruct.                                                    |
| @PreDestroy is called when the bean is garbage collected | @PreDestroy is called during context.close(), not on GC. Singleton beans are never GC'd while the context is alive.                                                 |
| BeanPostProcessor hooks are only for Spring internal use | They are the primary extension point for all frameworks built on Spring. Your own BeanPostProcessors are valid and powerful.                                        |
| The AOP proxy is created during bean instantiation       | The AOP proxy is created by BeanPostProcessor.postProcessAfterInitialization() — AFTER initialization. The singleton cache stores the proxy, not the original bean. |
| Prototype beans have a full lifecycle                    | Prototype beans are created and injected, but Spring does NOT call @PreDestroy on them — the caller is responsible for cleanup.                                     |

---

### 🚨 Failure Modes & Diagnosis

**@PostConstruct fails silently in tests**

**Symptom:**
`@PostConstruct` method throws an exception in tests, but no failure is observed. Or conversely, `@PostConstruct` validation fails to run in a `@WebMvcTest` slice.

**Root Cause:**
Test slices (`@WebMvcTest`, `@DataJpaTest`) only load specific bean slices. Beans not included in the slice don't have their lifecycle run. `@PostConstruct` methods on beans outside the slice are not called.

**Diagnostic Command / Tool:**

```bash
# Check which beans are loaded in a test
@SpringBootTest
class LifecycleDebugTest {
    @Autowired ApplicationContext ctx;

    @Test
    void printBeans() {
        Arrays.stream(ctx.getBeanDefinitionNames())
              .sorted()
              .forEach(System.out::println);
    }
}
```

**Fix:**
Use `@SpringBootTest` for tests that need the full lifecycle. Use `@ContextConfiguration(classes = SpecificConfig.class)` for narrower lifecycle tests.

**Prevention:** Be explicit about which beans need full lifecycle in tests vs. which can be mocked.

---

**Prototype bean @PreDestroy not called**

**Symptom:**
`@PreDestroy` on a prototype-scoped bean never executes. Resources (file handles, connections) are leaked.

**Root Cause:**
Spring intentionally does not call `@PreDestroy` on prototype beans. The container hands off the prototype and forgets about it — lifecycle management becomes the caller's responsibility.

**Diagnostic Command / Tool:**

```java
// Verify scope at runtime
ConfigurableListableBeanFactory factory =
    (ConfigurableListableBeanFactory) context.getAutowireCapableBeanFactory();
BeanDefinition def = factory.getBeanDefinition("myPrototypeBean");
System.out.println("Scope: " + def.getScope()); // "prototype"
```

**Fix:**

```java
// Implement DisposableBean and call explicitly, or use try-with-resources pattern
// OR: switch to singleton scope with thread-safe state management
// OR: use @Scope(proxyMode = TARGET_CLASS) for request-scoped beans
//     where Spring manages lifecycle via the proxy
```

**Prevention:** Avoid `@PreDestroy` on prototype beans — it will never run. Use explicit lifecycle management or switch to a scoped proxy.

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**

- `Bean` — the object going through the lifecycle
- `BeanFactory` — the container orchestrating the lifecycle
- `ApplicationContext` — the full context that triggers the lifecycle phases
- `DI (Dependency Injection)` — injection happens mid-lifecycle, between instantiation and init

**Builds On This (learn these next):**

- `BeanPostProcessor` — the hook that runs around init phases; how AOP works
- `BeanFactoryPostProcessor` — the hook that modifies bean definitions before instantiation
- `AOP` — implemented by wrapping beans with proxies during postProcessAfterInitialization

**Alternatives / Comparisons:**

- `@Lazy` — defers the entire lifecycle to first use, not to startup
- `SmartLifecycle` — an extended lifecycle interface for beans that need ordered start/stop

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ WHAT IT IS   │ The ordered sequence: define → create →   │
│              │ inject → init → use → destroy             │
├──────────────┼───────────────────────────────────────────┤
│ PROBLEM IT   │ No guaranteed order for setup/teardown    │
│ SOLVES       │ relative to dependency injection          │
├──────────────┼───────────────────────────────────────────┤
│ KEY INSIGHT  │ AOP proxies are created AFTER init        │
│              │ (@postProcessAfterInit) — the proxy, not  │
│              │ the bean, lives in the singleton cache     │
├──────────────┼───────────────────────────────────────────┤
│ USE WHEN     │ Post-injection resource setup:            │
│              │ @PostConstruct; shutdown cleanup: @PreDestroy│
├──────────────┼───────────────────────────────────────────┤
│ AVOID WHEN   │ Never put init logic in constructors when │
│              │ using field/setter injection              │
├──────────────┼───────────────────────────────────────────┤
│ TRADE-OFF    │ Guaranteed ordering vs lifecycle complexity│
│              │ (easy to get phase wrong)                 │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "Create → inject → init → use → destroy   │
│              │  — in that exact order, guaranteed."      │
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ BeanPostProcessor → AOP → @Transactional  │
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** `@PostConstruct` on a `@Transactional`-annotated service runs before the AOP proxy is created (AOP proxy is created in `postProcessAfterInitialization`, which runs AFTER `@PostConstruct`). So if `@PostConstruct` calls a `@Transactional` method on `this`, is there a transaction? Trace the exact lifecycle state at that moment and explain the consequence.

**Q2.** Spring calls `@PreDestroy` in reverse-dependency order during shutdown: beans that depend on others are destroyed first. But if your `@PreDestroy` method itself uses another bean that has already been destroyed, what happens? How does Spring attempt to prevent this, and where does that protection break down?
