---
id: SPR-064
title: Spring Framework Internals Deep Dive
category: Spring Core
tier: tier-3-java
folder: SPR-spring-core
difficulty: ★★★
depends_on: SPR-019, SPR-020, SPR-021, SPR-022, SPR-024, SPR-026, SPR-027
used_by:
related: SPR-067, SPR-065, SPR-071
tags:
  - spring
  - java
  - advanced
  - deep-dive
  - internals
  - first-principles
status: complete
version: 1
layout: default
parent: "Spring Core"
grand_parent: "Technical Dictionary"
nav_order: 64
permalink: /spr/spring-framework-internals-deep-dive/
---

# SPR-064 - Spring Framework Internals Deep Dive

⚡ TL;DR - The Spring IoC container is a two-phase lifecycle: BeanDefinition registration (what to build) followed by bean instantiation (build it), with two extension point phases between them.

| Field          | Value                                                                                                                                                                                                                                                 |
| -------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Depends on** | [[SPR-019 - IoC (Inversion of Control)]], [[SPR-020 - DI (Dependency Injection)]], [[SPR-021 - ApplicationContext]], [[SPR-022 - BeanFactory]], [[SPR-024 - Bean Lifecycle]], [[SPR-026 - BeanPostProcessor]], [[SPR-027 - BeanFactoryPostProcessor]] |
| **Used by**    | -                                                                                                                                                                                                                                                     |
| **Related**    | [[SPR-067 - Spring Specification and Extension Points]], [[SPR-065 - Spring Reactive Model (Project Reactor Internals)]], [[SPR-071 - Spring Context Refresh (AbstractApplicationContext)]]                                                           |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**

You configure a Spring application and it "just works." Then it doesn't. `BeanCreationException` on startup. `NoSuchBeanDefinitionException` at runtime. `@Transactional` not working on a `@Service` method. `@Autowired` injecting the wrong implementation. Without understanding Spring's internal machinery, these failures are indistinguishable from magic going wrong - you cannot reason about the cause.

**THE BREAKING POINT:**

Advanced Spring usage - custom auto-configuration, `BeanPostProcessor` implementations, AOP advice, `@Configuration` class processing - requires understanding the container internals. Debugging production issues (`@Transactional` self-invocation, prototype beans in singletons, circular dependencies) requires the same knowledge.

**THE INVENTION MOMENT:**

Spring's container design is not accidental - it is a carefully layered architecture with two distinct lifecycle phases and two symmetric extension point pairs (`BeanFactoryPostProcessor` / `BeanPostProcessor`). Understanding the design makes the entire Spring ecosystem readable.

**EVOLUTION:**

- **2003:** `BeanFactory` + XML `BeanDefinitionReader` - the minimal container
- **2005:** `ApplicationContext` adds events, resource loading, MessageSource
- **2006:** `BeanFactoryPostProcessor` formalised; component scan introduced
- **2010:** `@Configuration` class processing via `ConfigurationClassPostProcessor`
- **2022:** Spring 6.0 AOT - `BeanDefinition` graph pre-computed at build time

---

### 📘 Textbook Definition

The **Spring IoC container** is implemented as a two-phase process. **Phase 1 (definition):** `BeanDefinition` objects are registered in a `BeanDefinitionRegistry` by `BeanDefinitionReader` (XML), `ClassPathBeanDefinitionScanner` (component scan), or `@Configuration` class processing. `BeanFactoryPostProcessor` beans then mutate definitions before any instantiation. **Phase 2 (instantiation):** Beans are created in dependency order; `BeanPostProcessor` implementations intercept each bean after construction and after dependency injection - this is where AOP proxies are created, `@PostConstruct` is called, and `@Autowired` is resolved.

---

### ⏱️ Understand It in 30 Seconds

**One line:** Spring builds a blueprint of every bean (Phase 1), then constructs them using the blueprint while allowing hooks before and after each construction (Phase 2).

> Spring's container is a construction project: Phase 1 is the architect drawing blueprints (BeanDefinitions). Phase 2 is the construction crew building from the blueprints (instantiation). `BeanFactoryPostProcessor` is the city planner who can modify blueprints before construction. `BeanPostProcessor` is the building inspector who checks and modifies each building after it is built.

**One insight:** If you understand that `BeanFactoryPostProcessor` operates on _definitions_ and `BeanPostProcessor` operates on _instances_, 80% of Spring's "magic" becomes predictable.

---

### 🔩 First Principles Explanation

**CORE INVARIANTS:**

1. A `BeanDefinition` is a metadata description of a bean, not the bean itself
2. `BeanDefinition` objects exist before any application bean is instantiated
3. `BeanFactoryPostProcessor` can modify definitions; it cannot create application beans (only infrastructure)
4. `BeanPostProcessor` wraps instances; the returned object replaces the original bean in the registry
5. Beans are instantiated in topological dependency order (dependencies before dependents)

**DERIVED DESIGN:**

From invariant 1+2 → auto-configuration (detecting classpath libraries) operates in Phase 1 - it registers `BeanDefinition` objects for discovered capabilities before any bean exists.
From invariant 3 → property placeholder resolution (`${server.port}`) is a `BeanFactoryPostProcessor` that mutates definition property values.
From invariant 4 → AOP proxy creation is a `BeanPostProcessor` (`AbstractAutoProxyCreator`) - it replaces the target bean with a proxy.
From invariant 5 → circular dependencies between constructor-injected singleton beans are impossible (Phase 2 cannot start a bean whose dependency chain hasn't completed).

**THE TRADE-OFFS:**

**Gain:** Extreme extensibility - any Spring feature can be implemented as a `BeanFactoryPostProcessor` or `BeanPostProcessor` without modifying core classes.

**Cost:** Two-phase processing adds startup overhead; deep extension chains are hard to debug; order-sensitive (poorly ordered processors cause subtle bugs).

**ESSENTIAL vs ACCIDENTAL COMPLEXITY:**

**Essential:** A container that can be extended with new capabilities (AOP, transactions, metrics) without modifying core code requires extension points at both the definition and instance levels.

**Accidental:** The naming (`BeanFactoryPostProcessor` vs `BeanPostProcessor`) is confusingly similar; the key is "Factory" = definitions, no prefix = instances.

---

### 🧪 Thought Experiment

**SETUP:** You add `@Transactional` to a `@Service` method. How does Spring make that method transactional without modifying your class?

**Step 1 - Phase 1 (definition):**
`ClassPathBeanDefinitionScanner` finds `OrderService` class. Registers `BeanDefinition` with `class = OrderService.class`, `scope = singleton`.

**Step 2 - Phase 1 (BeanFactoryPostProcessor):**
`ConfigurationClassPostProcessor` processes `@Configuration` classes. `AutoProxyCreator` bean definition registered.

**Step 3 - Phase 2 (instantiation):**
`OrderService` instance created. `BeanPostProcessor` phase runs. `AbstractAutoProxyCreator` (the AOP proxy creator) calls `getAdvicesAndAdvisorsForBean(OrderService.class)`. `TransactionInterceptor` is found as applicable advice (because `@Transactional` is present). `AbstractAutoProxyCreator.createProxy()` wraps `OrderService` with a CGLIB subclass proxy. The proxy (not the original) is stored in the singleton registry.

**Step 4 - Injection:**
When `PaymentController` receives its `OrderService` dependency, it gets the CGLIB proxy. Every `@Transactional` method call goes through `TransactionInterceptor` first.

**THE INSIGHT:**

Every Spring feature that modifies bean behaviour without touching the bean class follows this exact pattern - it is always a `BeanPostProcessor` creating a proxy or wrapper.

---

### 🧠 Mental Model / Analogy

> Spring's two-phase container is like publishing a recipe book (Phase 1) and then cooking every recipe (Phase 2). `BeanFactoryPostProcessor` is an editor who can update the recipes before cooking starts. `BeanPostProcessor` is a chef's assistant who can garnish or modify each dish after it comes off the stove (but before it is served). The book (BeanDefinitions) and the dishes (bean instances) are completely separate artifacts.

**Element mapping:**

- Recipe book → `BeanDefinitionRegistry`
- Individual recipe → `BeanDefinition`
- Recipe editor → `BeanFactoryPostProcessor`
- Cooking a recipe → bean instantiation
- Chef's assistant (garnishing) → `BeanPostProcessor`
- Garnished dish → AOP proxy / wrapped bean
- Serving the dish → bean available for injection

Where this analogy breaks down: unlike recipes, `BeanDefinition` objects can reference other `BeanDefinition` objects (dependencies), creating a graph that must be resolved in topological order before cooking can begin.

---

### 📶 Gradual Depth - Four Levels

**Level 1 - What it is (anyone can understand):**
Spring reads all your class annotations, figures out what objects are needed and in what order, creates them, and then wraps special ones (like `@Transactional`) in interceptors. It happens at startup so by the time your code runs, everything is already set up and connected.

**Level 2 - How to use it (junior developer):**
You mostly interact with the output of this process, not the internals. But knowing that `@Transactional` requires a proxy helps you understand why calling a `@Transactional` method from within the same class doesn't start a transaction - you're calling the original object, not the proxy. Understanding `BeanPostProcessor` helps you write custom bean transformations.

**Level 3 - How it works (mid-level engineer):**
`AbstractApplicationContext.refresh()` orchestrates everything. `invokeBeanFactoryPostProcessors()` runs all `BeanFactoryPostProcessor` beans in priority order. `registerBeanPostProcessors()` registers all `BeanPostProcessor` beans into the factory. `finishBeanFactoryInitialization()` instantiates all remaining singletons, calling `getBean()` for each. `getBean()` triggers `createBean()` → `doCreateBean()` → `instantiateBean()` (constructor) → `populateBean()` (injection) → `initializeBean()` (post-processors, `@PostConstruct`).

**Level 4 - Why it was designed this way (senior/staff):**
The two-phase design solves the _bootstrap problem_: if `BeanPostProcessor` beans (like the AOP proxy creator) were themselves processed by other `BeanPostProcessor` beans, you'd need an infinite regress. Spring avoids this by instantiating and registering all `BeanPostProcessor` beans _before_ processing non-infrastructure beans. This is why Spring logs a warning when a non-`BeanPostProcessor` bean is created early during `registerBeanPostProcessors()` - it means that bean won't be processed by all post-processors, which can cause subtle `@Transactional` or AOP failures.

**Expert Thinking Cues:**

- `Ordered` and `PriorityOrdered` control `BeanFactoryPostProcessor` and `BeanPostProcessor` execution order
- `InstantiationAwareBeanPostProcessor` can short-circuit bean creation entirely (used by Mockito's `@MockBean`)
- `SmartInstantiationAwareBeanPostProcessor.getEarlyBeanReference()` resolves circular dependencies by exposing a partially-initialised proxy

---

### ⚙️ How It Works (Mechanism)

`AbstractApplicationContext.refresh()` call sequence:

```
1. prepareRefresh()
   └─ Set start time, active flag, validate required properties

2. obtainFreshBeanFactory()
   └─ Create DefaultListableBeanFactory
   └─ Load BeanDefinitions (XML / component scan / @Config)

3. prepareBeanFactory(beanFactory)
   └─ Register built-in beans (environment, etc.)

4. postProcessBeanFactory(beanFactory)
   └─ Subclass hook (e.g., web app adds web-specific scopes)

5. invokeBeanFactoryPostProcessors(beanFactory)
   └─ Run BeanDefinitionRegistryPostProcessor first
       (ConfigurationClassPostProcessor reads @Configuration)
   └─ Run BeanFactoryPostProcessor
       (PropertySourcesPlaceholderConfigurer resolves ${...})

6. registerBeanPostProcessors(beanFactory)
   └─ Instantiate all BeanPostProcessor beans
   └─ Register in order (PriorityOrdered, Ordered, rest)

7. initMessageSource()
8. initApplicationEventMulticaster()

9. onRefresh()  [web: start embedded server]

10. registerListeners()

11. finishBeanFactoryInitialization(beanFactory)
    └─ Instantiate all non-lazy singleton beans
    └─ For each bean: createBean()
       ├─ instantiateBean() [constructor]
       ├─ populateBean() [@Autowired, @Value injection]
       └─ initializeBean()
          ├─ applyBeanPostProcessorsBeforeInit()
          ├─ invokeInitMethods() [@PostConstruct, afterPropertiesSet()]
          └─ applyBeanPostProcessorsAfterInit()
             └─ AbstractAutoProxyCreator wraps with proxy

12. finishRefresh()
    └─ Publish ContextRefreshedEvent
    └─ Start SmartLifecycle beans
```

---

### 🔄 The Complete Picture - End-to-End Flow

**NORMAL FLOW:**

```
[SpringApplication.run()]
     |
     ├─ Phase 1: BeanDefinition registration
     |    ├─ Component scan → 200 BeanDefinitions
     |    └─ @Configuration classes processed
     |          ← YOU ARE HERE (after definitions built)
     |
     ├─ BeanFactoryPostProcessor phase
     |    ├─ ${placeholders} resolved
     |    └─ @Conditional evaluations finalised
     |
     ├─ BeanPostProcessor registration
     |    └─ AutoProxyCreator, @Autowired processor, etc.
     |
     ├─ Phase 2: Singleton instantiation
     |    ├─ Each bean: construct → inject → post-process
     |    └─ @Transactional beans → CGLIB proxy created
     |
[Application ready]
```

**FAILURE PATH:**

- `BeanDefinitionOverrideException` → two beans with same name in Phase 1
- `UnsatisfiedDependencyException` → missing dependency detected in Phase 2 (injection)
- `BeanCurrentlyInCreationException` → circular constructor dependency in Phase 2
- `NoUniqueBeanDefinitionException` → multiple matching beans, no `@Primary`

**WHAT CHANGES AT SCALE:**

Spring Boot 3.x AOT shifts Phase 1 to build time. The `BeanDefinition` graph is serialised to Java source files (`BeanFactory.java`) generated by `spring-aot-maven-plugin`. At runtime, Phase 2 starts immediately from the pre-built graph - startup time reduced by 30-70%.

---

### 💻 Code Example

**Implementing a custom `BeanPostProcessor`:**

```java
// Wraps every @Monitored service with timing metrics
@Component
public class MonitoringBeanPostProcessor
        implements BeanPostProcessor {

    private final MeterRegistry registry;

    public MonitoringBeanPostProcessor(
            MeterRegistry registry) {
        this.registry = registry;
    }

    @Override
    public Object postProcessAfterInitialization(
            Object bean, String beanName) {
        // Check if bean class has @Monitored
        if (bean.getClass()
                .isAnnotationPresent(Monitored.class)) {
            // Wrap with timing proxy
            return Proxy.newProxyInstance(
                bean.getClass().getClassLoader(),
                bean.getClass().getInterfaces(),
                (proxy, method, args) -> {
                    return Timer.builder(
                            "service." + beanName)
                        .register(registry)
                        .record(() -> method.invoke(
                            bean, args));
                });
        }
        return bean; // no wrapping
    }
}
```

**Implementing a custom `BeanFactoryPostProcessor`:**

```java
// Adds a BeanDefinition programmatically
@Component
public class DynamicBeanRegistrar
        implements BeanDefinitionRegistryPostProcessor {

    @Override
    public void postProcessBeanDefinitionRegistry(
            BeanDefinitionRegistry registry) {
        // Register a bean definition at startup
        // (before any beans are created)
        GenericBeanDefinition def =
            new GenericBeanDefinition();
        def.setBeanClass(DynamicService.class);
        def.setScope("singleton");
        registry.registerBeanDefinition(
            "dynamicService", def);
    }

    @Override
    public void postProcessBeanFactory(
            ConfigurableListableBeanFactory bf) {
        // Optional: mutate existing definitions
    }
}
```

---

### ⚖️ Comparison Table

| Extension Point                       | Phase                        | Input                             | Can Create Beans?  | Common Uses                                 |
| ------------------------------------- | ---------------------------- | --------------------------------- | ------------------ | ------------------------------------------- |
| `BeanDefinitionRegistryPostProcessor` | 1                            | `BeanDefinitionRegistry`          | Yes (via registry) | Auto-configuration, dynamic registration    |
| `BeanFactoryPostProcessor`            | 1                            | `ConfigurableListableBeanFactory` | Via factory        | Placeholder resolution, definition mutation |
| `InstantiationAwareBeanPostProcessor` | 2 (pre-instantiation)        | Class, bean name                  | Replaces bean      | `@MockBean`, custom instantiation           |
| `BeanPostProcessor.beforeInit`        | 2 (post-construct, pre-init) | Bean instance                     | Wraps instance     | Custom validation, early wiring             |
| `BeanPostProcessor.afterInit`         | 2 (post-init)                | Bean instance                     | Wraps instance     | AOP proxies, metrics, `@Async` proxy        |

---

### ⚠️ Common Misconceptions

| Misconception                                            | Reality                                                                                                                                                                                            |
| -------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| "`@Transactional` wraps the class at compile time"       | `@Transactional` is applied at runtime via a `BeanPostProcessor` that creates a proxy. Nothing in the compiled class changes.                                                                      |
| "Spring reads annotations at every method call"          | Annotations are read once in Phase 2 (startup) to build metadata. At runtime, the proxy - not annotation reading - provides the behaviour.                                                         |
| "`BeanFactoryPostProcessor` can modify bean instances"   | No - beans don't exist yet in Phase 1. It can only modify `BeanDefinition` objects.                                                                                                                |
| "Component scan runs before `@Configuration` processing" | Both are handled by `BeanFactoryPostProcessor` implementations; `ConfigurationClassPostProcessor` processes `@Configuration` classes which may trigger additional component scans.                 |
| "A `BeanPostProcessor` returning null removes the bean"  | Returning null from `postProcessBeforeInitialization` or `postProcessAfterInitialization` causes a `NullPointerException` during injection. Return the original bean if no modification is needed. |

---

### 🚨 Failure Modes & Diagnosis

**Mode 1: `@Transactional` has no effect (self-invocation)**

**Symptom:** Calling `this.transactionalMethod()` from within the same class does not start a transaction.

**Root Cause:** The call bypasses the CGLIB proxy. The proxy only intercepts external calls - internal calls use `this` (the real object), not the proxy reference.

**Diagnostic:**

```java
// Log to verify: is the injected bean a proxy?
@Autowired OrderService orderService;

@Test
void isProxy() {
    System.out.println(AopUtils.isAopProxy(
        orderService)); // true if proxied
    System.out.println(orderService.getClass()
        .getName()); // ends in $$SpringCGLIB$$0 if proxied
}
```

**Fix:** Inject `self` reference: `@Autowired @Lazy private OrderService self;` and call `self.transactionalMethod()`. Or restructure to avoid internal transactional calls.

**Prevention:** Code review rule: `@Transactional` method calls from within the same class are architecture violations.

---

**Mode 2: Bean created before all BeanPostProcessors registered**

**Symptom:** Spring logs: `Bean 'X' of type Y is not eligible for getting processed by all BeanPostProcessor interfaces.` Bean `X` is not transactional / not proxied.

**Root Cause:** Bean `X` depends on a `BeanPostProcessor` (or is depended on by one), forcing it to be created early during `registerBeanPostProcessors()`.

**Diagnostic:**

```bash
java -jar app.jar --debug 2>&1 | grep \
  "not eligible for getting processed"
# Shows which bean and which post-processor was missed
```

**Fix:** Remove the dependency that causes early creation. Mark the dependency `@Lazy` to defer creation. Use `ApplicationContext.getBean()` lazily instead of `@Autowired`.

**Prevention:** Never `@Autowired` infrastructure beans from domain beans at construction time.

---

**Mode 3: Malicious `BeanFactoryPostProcessor` manipulates bean definitions (Security failure mode)**

**Symptom:** A third-party library's `BeanFactoryPostProcessor` replaces a `SecurityFilterChain` bean definition with its own.

**Root Cause:** `BeanDefinitionOverrideException` is disabled (`spring.main.allow-bean-definition-overriding=true`); library silently replaces security beans.

**Diagnostic:**

```bash
# Enable bean override logging
logging.level.org.springframework.beans.factory
  .support.DefaultListableBeanFactory=DEBUG
# Look for "Overriding bean definition for bean 'X'"
```

**Fix:** Never set `allow-bean-definition-overriding=true` in production without auditing which beans are overridden. Use `@Order` and `@ConditionalOnMissingBean` to control override precedence safely.

**Prevention:** Add a startup test asserting that `SecurityFilterChain` bean is your expected class, not overridden.

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**

- [[SPR-019 - IoC (Inversion of Control)]] - the principle the container implements
- [[SPR-021 - ApplicationContext]] - the container being described
- [[SPR-026 - BeanPostProcessor]] - the Phase 2 extension point
- [[SPR-027 - BeanFactoryPostProcessor]] - the Phase 1 extension point

**Builds On This (learn these next):**

- [[SPR-067 - Spring Specification and Extension Points]] - applying this knowledge to write extensions
- [[SPR-071 - Spring Context Refresh (AbstractApplicationContext)]] - the `refresh()` call in detail
- [[SPR-073 - Spring Boot AOT Compilation]] - shifting Phase 1 to build time

**Alternatives / Comparisons:**

- Micronaut AOT (compile-time DI) - eliminates Phase 1 entirely; DI graph pre-built
- Guice (Google) - simpler DI container without the two-phase design
- CDI (Jakarta EE) - specification-based container with similar Phase 1/2 distinction

---

### 📌 Quick Reference Card

```
+----------------------------------------------------------+
| WHAT IT IS    | Spring IoC two-phase container internals  |
| PROBLEM       | Debugging "magic" failures without knowing|
|               | how the container actually works          |
| KEY INSIGHT   | Phase 1 = BeanDefinitions; Phase 2 =      |
|               | instances; extension points at both phases|
| USE WHEN      | Debugging AOP, transactions, circular deps;|
|               | writing custom BeanPostProcessors         |
| AVOID WHEN    | You need this knowledge to use Spring     |
|               | correctly at all - no avoidance           |
| TRADE-OFF     | Runtime flexibility vs startup complexity |
| ONE-LINER     | BeanFactoryPostProcessor: definitions;    |
|               | BeanPostProcessor: instances              |
| NEXT EXPLORE  | SPR-067 (Extension Points), SPR-071       |
|               | (Context Refresh)                         |
+----------------------------------------------------------+
```

**If you remember only 3 things:**

1. Phase 1 builds `BeanDefinition` blueprints; Phase 2 constructs beans from them - these are completely separate
2. `@Transactional` works via a `BeanPostProcessor` proxy - self-invocation bypasses the proxy
3. `BeanFactoryPostProcessor` operates on definitions; `BeanPostProcessor` operates on instances

**Interview one-liner:** "Spring's container has two phases: definition registration (Phase 1, where `BeanFactoryPostProcessor` can mutate blueprints) and bean instantiation (Phase 2, where `BeanPostProcessor` wraps instances - enabling AOP, transactions, and all proxy-based features)."

---

### 💎 Transferable Wisdom

**Reusable Engineering Principle:** _Separate the plan from the execution._ Building a metadata description of what to create (Phase 1) before creating it (Phase 2) enables validation, transformation, and extension at the metadata level - without touching the construction process. This pattern appears in any system where declarative configuration drives imperative execution.

**Where else this pattern appears:**

- **Kubernetes** - `PodSpec` (metadata/definition) → `kubelet` creates containers (execution); `MutatingWebhookConfiguration` modifies specs before creation (the `BeanFactoryPostProcessor` equivalent)
- **Webpack** - module graph analysis (Phase 1) → code generation (Phase 2); loaders transform modules at the metadata phase
- **SQL execution** - query parsing/planning (Phase 1) → execution (Phase 2); `EXPLAIN` shows the plan without executing

---

### 💡 The Surprising Truth

`AbstractApplicationContext.refresh()` - the single method that boots an entire Spring application - is 150 lines of code. It calls 12 methods in a defined sequence. Every Spring feature you use (auto-configuration, AOP, events, web server startup) is implemented as a call to one of these 12 methods or as a hook registered within them. The entire Spring Framework is, in a sense, 150 lines of orchestration code plus thousands of plugins. If you read and understand those 150 lines, you understand the architecture of the entire framework - which is exactly why Rod Johnson's _Expert One-on-One Spring_ spends a chapter on them.

---

### 🧠 Think About This Before We Continue

**Question 1 (D - Root Cause):** A team reports that `@Async` annotations on service methods have no effect - methods execute synchronously despite the annotation. They confirmed `@EnableAsync` is present. What is the most likely root cause related to the two-phase container lifecycle, and how would you diagnose it?

_Hint:_ The `AsyncAnnotationBeanPostProcessor` responsible for `@Async` proxy creation must be registered _before_ the annotated beans are instantiated. Think about what could cause it to be registered late or missed entirely.

**Question 2 (A - System Interaction):** Spring resolves circular dependencies between singleton beans using a _three-level cache_ in `DefaultSingletonBeanRegistry`. Constructor injection circular dependencies cannot be resolved, but field/setter injection circular dependencies can. Describe the three-cache mechanism and explain why it works for field injection but not constructor injection.

_Hint:_ The three caches are: `singletonObjects` (complete), `earlySingletonObjects` (partially initialised), and `singletonFactories` (object factories). Constructor injection requires the dependency to be fully complete before the bean can be constructed.

**Question 3 (E - First Principles):** Spring Boot 3.x AOT shifts `BeanDefinition` registration from startup to build time. What categories of `BeanFactoryPostProcessor` behaviour _cannot_ be shifted to build time, and why does this mean AOT cannot handle all Spring applications without additional configuration?

_Hint:_ Consider `@ConditionalOnProperty` (requires runtime property values), dynamic database schema detection, and any `BeanFactoryPostProcessor` that reads from external systems (databases, HTTP endpoints) at startup.
