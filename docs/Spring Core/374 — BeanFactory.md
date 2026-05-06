---
layout: default
title: "BeanFactory"
parent: "Spring Core"
nav_order: 374
permalink: /spring/beanfactory/
number: "0374"
category: Spring Core
difficulty: ★★☆
depends_on: IoC, DI, Bean
used_by: ApplicationContext, Bean Lifecycle, BeanPostProcessor
related: ApplicationContext, DefaultListableBeanFactory, ListableBeanFactory
tags:
  - spring
  - internals
  - intermediate
  - architecture
---

# 374 — BeanFactory

⚡ TL;DR — BeanFactory is Spring's foundational container interface: it creates beans on demand, resolves dependencies, and is the root of the entire Spring container hierarchy.

| #374            | Category: Spring Core                                               | Difficulty: ★★☆ |
| :-------------- | :------------------------------------------------------------------ | :-------------- |
| **Depends on:** | IoC, DI, Bean                                                       |                 |
| **Used by:**    | ApplicationContext, Bean Lifecycle, BeanPostProcessor               |                 |
| **Related:**    | ApplicationContext, DefaultListableBeanFactory, ListableBeanFactory |                 |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
Before Spring, J2EE applications used heavyweight EJB containers that required deployment descriptors, specific class hierarchies, and deployment to an application server just to test a single business class. Getting an object required navigating JNDI lookups, which required a running server. Developers ran integration tests against live servers, cycles were slow, and the cognitive overhead of EJB configuration was immense.

**THE BREAKING POINT:**
Lightweight applications and unit tests had no path to a managed object container. Developers either accepted the EJB overhead or wrote their own manual wiring code. There was no middle ground: a programmable, lightweight container that could be embedded in tests, CLI tools, and batch jobs without a full application server.

**THE INVENTION MOMENT:**
"This is exactly why BeanFactory was created."

---

### 📘 Textbook Definition

**BeanFactory** is the root interface of Spring's IoC container hierarchy, defined in `org.springframework.beans.factory`. It provides the contract for accessing and managing beans: `getBean(String name)`, `getBean(Class<T> type)`, `containsBean(String name)`, `isSingleton(String name)`, and `getType(String name)`. `BeanFactory` implementations are responsible for creating beans, resolving dependencies, and managing the singleton cache. The most commonly used implementation is `DefaultListableBeanFactory`, which also implements `BeanDefinitionRegistry` for bean registration. `ApplicationContext` extends `BeanFactory` (via `HierarchicalBeanFactory` and `ListableBeanFactory`) and adds enterprise features on top.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
BeanFactory is the minimal Spring contract: give me an object by name or type, create it if needed.

**One analogy:**

> BeanFactory is like a vending machine. You push a button (request a bean by name or type), and the machine dispenses the item (creates or retrieves the object). The machine knows what it contains (bean definitions) and fulfills requests. ApplicationContext is a vending machine with a loyalty program, music, and event notifications — more features, same core dispensing mechanism.

**One insight:**
BeanFactory distinguishes between _bean definitions_ (recipes) and _bean instances_ (cooked dishes). Storing a definition is cheap; creating an instance may be expensive. For singletons, the instance is created once and cached. For prototypes, each `getBean()` call creates a new instance. This recipe-vs-instance separation is the core design that makes Spring flexible.

---

### 🔩 First Principles Explanation

**CORE INVARIANTS:**

1. BeanFactory stores _bean definitions_ (metadata) not _bean instances_ — instances are created lazily or eagerly based on scope.
2. Singletons are cached after first creation; every `getBean()` for the same singleton returns the same object.
3. The factory is responsible for dependency resolution: if Bean A needs Bean B, the factory creates B before completing A.

**DERIVED DESIGN:**
The factory pattern fits naturally: a factory knows how to build objects from a recipe. BeanFactory's recipe is `BeanDefinition` — it stores the class, scope, constructor arguments, property values, and initialization method names. When `getBean()` is called, the factory reads the definition and produces the instance.

The hierarchy (`HierarchicalBeanFactory`) allows parent-child context relationships: a child factory can look up beans from its parent, enabling modular architectures where common beans live in a parent context and module-specific beans live in child contexts.

**THE TRADE-OFFS:**

**Gain:** Minimal API, no dependency on enterprise features. Can be used in constrained environments (embedded, CLI, batch). Easy to test implementations.

**Cost:** No event system, no AOP auto-proxy, no i18n, no environment abstraction. Beans declared in a `BeanFactory` do not receive `@Autowired` processing unless `AutowiredAnnotationBeanPostProcessor` is explicitly registered. BeanFactory does not auto-register `BeanPostProcessors` — you must do it manually.

---

### 🧪 Thought Experiment

**SETUP:**
You need a `BeanFactory` in a unit test to verify that a specific configuration class correctly wires two beans together. You don't want to start a full Spring Boot context (takes 5 seconds), you just need the factory.

**WHAT HAPPENS WITHOUT BeanFactory abstraction:**
You'd need to run a full `@SpringBootTest` with the Tomcat server, all auto-configurations, and all beans loading. A test that should take 50ms takes 5 seconds. Your CI pipeline runs 200 such tests — that's 1,000 seconds of pure container startup.

**WHAT HAPPENS WITH BeanFactory (minimal context):**

```java
AnnotationConfigApplicationContext ctx =
    new AnnotationConfigApplicationContext(MyConfig.class);
MyService service = ctx.getBean(MyService.class);
// Only beans in MyConfig are loaded — milliseconds, not seconds
```

You get exactly the beans from `MyConfig`, nothing else. No Tomcat, no auto-configuration, no 30 other Spring Boot modules.

**THE INSIGHT:**
The BeanFactory abstraction enables contextual isolation: you can test exactly the slice of beans you care about without the entire application. This is why Spring tests with `@ContextConfiguration` are far faster than `@SpringBootTest`.

---

### 🧠 Mental Model / Analogy

> BeanFactory is a recipe book + kitchen. The recipe book (BeanDefinitionRegistry) contains instructions for every dish (bean class, dependencies, scope). The kitchen (factory methods) executes those instructions on demand. Ordering the same dish twice gives you either the same plate (singleton) or a freshly cooked plate (prototype), depending on the recipe.

- "Recipe book" → `BeanDefinitionRegistry` / stored `BeanDefinition` objects
- "Recipe entry" → `BeanDefinition` (class, scope, constructor args, init method)
- "Kitchen executing a recipe" → `BeanFactory.getBean()` → instantiation + DI
- "Singleton cache" → plate delivered once, then kept under the heat lamp for reuse
- "Prototype scope" → cook a fresh plate every time it's ordered

**Where this analogy breaks down:** Unlike a kitchen, BeanFactory can create beans that have other beans as ingredients — and it resolves those ingredients recursively, potentially creating a chain of 20 objects to satisfy one `getBean()` call.

---

### 📶 Gradual Depth — Four Levels

**Level 1 — What it is (anyone can understand):**
BeanFactory is the basic Spring container. You register your classes with it and ask for them by name or type. It creates them (resolving their dependencies) and remembers them for next time if they're singletons.

**Level 2 — How to use it (junior developer):**
You rarely use `BeanFactory` directly in Spring Boot — `ApplicationContext` (which extends `BeanFactory`) is always available. When writing tests that need only a subset of beans, use `AnnotationConfigApplicationContext` instead of `@SpringBootTest`. For programmatic bean lookup, inject `BeanFactory` and call `getBean(MyService.class)` — though constructor injection is always preferred.

**Level 3 — How it works (mid-level engineer):**
`DefaultListableBeanFactory` is Spring's primary implementation. It stores `BeanDefinition` objects in a `ConcurrentHashMap<String, BeanDefinition>`. On `getBean()`, it resolves the definition, checks the singleton cache (`singletonObjects` map), and instantiates via `BeanDefinitionValueResolver` if not cached. Constructor arguments are resolved recursively. After construction, `BeanPostProcessor` chain runs (if registered). For singletons, the result is added to `singletonObjects`.

**Level 4 — Why it was designed this way (senior/staff):**
BeanFactory was designed as an interface rather than an abstract class to allow multiple implementations — XML-based, annotation-based, programmatic. The extension interfaces (`ListableBeanFactory`, `HierarchicalBeanFactory`, `AutowireCapableBeanFactory`) follow the Interface Segregation Principle: callers that only need to list beans don't need to see the autowiring API. This design predates Java 8 default methods, which is why there are so many granular interfaces rather than one fat interface with default implementations.

---

### ⚙️ How It Works (Mechanism)

**BeanFactory Interface Hierarchy:**

```
┌──────────────────────────────────────────────────┐
│  BeanFactory                                     │
│  getBean(), containsBean(), isSingleton()...     │
└────────────────────┬─────────────────────────────┘
                     │
         ┌───────────┼────────────┐
         ↓           ↓            ↓
ListableBeanFactory  HierarchicalBeanFactory
(list beans by type) (parent-child contexts)
         │           │
         └─────┬─────┘
               ↓
   AutowireCapableBeanFactory
   (createBean, autowire, applyBeanPostProcessors)
               │
               ↓
   ConfigurableListableBeanFactory
   (freeze config, preInstantiate singletons)
               │
               ↓
   DefaultListableBeanFactory  ← concrete implementation
```

**getBean() Flow:**

```
getBean("userService")
    ↓
Check singletonObjects cache — if found: return it
    ↓
Not cached → get BeanDefinition for "userService"
    ↓
Resolve constructor params (recurse for each dependency)
    ↓
Instantiate via reflection: constructor.newInstance(args)
    ↓
Apply BeanPostProcessors (if registered):
  - AutowiredAnnotationBeanPostProcessor (@Autowired fields)
  - CommonAnnotationBeanPostProcessor (@PostConstruct)
    ↓
Add to singletonObjects cache
    ↓
Return instance
```

**BeanDefinition:**

```java
// What BeanFactory stores per bean
BeanDefinition {
    beanClassName: "com.example.UserService"
    scope: "singleton"  // or "prototype"
    constructorArgumentValues: [UserRepository.class]
    propertyValues: []
    initMethodName: "init"  // @PostConstruct equiv
    destroyMethodName: "destroy"
    lazyInit: false
    primary: false
}
```

---

### 🔄 The Complete Picture — End-to-End Flow

**NORMAL FLOW:**

```
BeanDefinitions registered (via XML, annotations, @Bean)
    ↓
ApplicationContext.refresh() called
    ↓
BeanFactoryPostProcessors run (modify definitions)
    ↓
BeanPostProcessors registered
    ↓
DefaultListableBeanFactory.preInstantiateSingletons()
   ← YOU ARE HERE (BeanFactory creates all singletons)
    ↓
Each singleton resolved, created, post-processed, cached
    ↓
Beans available for injection and direct lookup
```

**FAILURE PATH:**

```
BeanFactory cannot resolve a dependency
    ↓
NoSuchBeanDefinitionException or circular dep error
    ↓
preInstantiateSingletons() aborts
    ↓
ApplicationContext.refresh() throws
    ↓
Application exits
```

**WHAT CHANGES AT SCALE:**
The singleton cache (`singletonObjects` as `ConcurrentHashMap`) is read-only after startup — zero contention at scale. The bottleneck is _startup time_ during `preInstantiateSingletons()`, not runtime `getBean()` calls. At 1,000+ beans, startup dominates; the cache lookup is O(1) for billions of requests.

---

### 💻 Code Example

**Example 1 — Using BeanFactory in isolation (test/CLI scenario):**

```java
// Lightweight context — no auto-configuration
AnnotationConfigApplicationContext ctx =
    new AnnotationConfigApplicationContext();

// Register only the beans we need
ctx.register(UserServiceConfig.class);
ctx.refresh();

// Retrieve beans
UserService userService = ctx.getBean(UserService.class);
userService.findById(1L);

ctx.close();  // triggers @PreDestroy
```

**Example 2 — Programmatic BeanFactory access (avoid in production):**

```java
@Component
public class PluginRegistry {

    private final BeanFactory beanFactory;

    public PluginRegistry(BeanFactory beanFactory) {
        this.beanFactory = beanFactory;
    }

    // Use only when bean type is dynamic (runtime strategy selection)
    public Plugin getPlugin(String pluginName) {
        // Service Locator pattern — use only when DI is impossible
        return beanFactory.getBean(pluginName, Plugin.class);
    }
}
```

**Example 3 — BeanDefinition programmatic registration:**

```java
@Configuration
public class DynamicBeanConfig
        implements BeanDefinitionRegistryPostProcessor {

    @Override
    public void postProcessBeanDefinitionRegistry(
            BeanDefinitionRegistry registry) {

        // Register a bean at configuration time
        RootBeanDefinition def = new RootBeanDefinition(
            FeatureService.class);
        def.setScope(BeanDefinition.SCOPE_SINGLETON);
        registry.registerBeanDefinition("featureService", def);
    }

    @Override
    public void postProcessBeanFactory(
            ConfigurableListableBeanFactory beanFactory) {
        // Post-process existing definitions if needed
    }
}
```

---

### ⚖️ Comparison Table

| Container           | Lazy Init             | Events | AOP Auto-proxy | BeanPostProcessor Auto-reg | Use Case             |
| ------------------- | --------------------- | ------ | -------------- | -------------------------- | -------------------- |
| **BeanFactory**     | Yes (always lazy)     | No     | No             | No                         | Constrained/embedded |
| ApplicationContext  | No (eager by default) | Yes    | Yes            | Yes                        | Production apps      |
| ListableBeanFactory | Yes                   | No     | No             | No                         | Testing slices       |

**How to choose:** Use `ApplicationContext` for all production applications — the richer features are worth the startup cost. Use `BeanFactory` directly only in resource-constrained environments (IoT, Android, embedded) where the enterprise features of `ApplicationContext` are not available.

---

### ⚠️ Common Misconceptions

| Misconception                                          | Reality                                                                                                                                                                      |
| ------------------------------------------------------ | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| BeanFactory and ApplicationContext are interchangeable | ApplicationContext has 10+ additional capabilities. Injecting BeanFactory gives a read-only reference; ApplicationContext gives access to events, environment, and more.     |
| BeanFactory is deprecated                              | BeanFactory is alive and is the root interface. ApplicationContext _extends_ it — it's not a replacement, it's a superset.                                                   |
| BeanFactory is lazy by default                         | DefaultListableBeanFactory doesn't call preInstantiateSingletons until refresh() completes. ApplicationContext calls it during refresh, making singletons eager by default.  |
| Direct BeanFactory usage is always an anti-pattern     | It's acceptable for dynamic plugin systems, test utilities, and programmatic bean registration. The anti-pattern is using getBean() _instead of_ DI for normal dependencies. |

---

### 🚨 Failure Modes & Diagnosis

**BeanCurrentlyInCreationException**

**Symptom:**
`BeanCurrentlyInCreationException: Error creating bean with name 'A': Requested bean is currently in creation`

**Root Cause:**
Constructor-injection circular dependency. Bean A's constructor requires Bean B, and B's constructor requires A. BeanFactory cannot complete either construction.

**Diagnostic Command / Tool:**

```bash
# Spring prints a clear cycle in the error:
# "The dependencies of some of the beans in the application context
#  form a cycle: A -> B -> A"
# Check startup logs for this pattern
grep "The dependencies.*form a cycle" app.log
```

**Fix:**

```java
// BAD: constructor circular dependency
@Component class A {
    A(B b) { ... }
}
@Component class B {
    B(A a) { ... }
}

// OPTION 1: Break the cycle with @Lazy
@Component class A {
    A(@Lazy B b) { ... }  // B injected as proxy, resolved on first use
}

// OPTION 2: Redesign — extract shared functionality to a new C
@Component class C { /* shared logic */ }
@Component class A { A(C c) { ... } }
@Component class B { B(C c) { ... } }
```

**Prevention:** Circular dependencies are a design smell. Two classes that depend on each other often share a responsibility that belongs in a third class.

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**

- `IoC (Inversion of Control)` — BeanFactory is the concrete implementation of IoC in Spring
- `Bean` — the objects BeanFactory creates and manages
- `DI (Dependency Injection)` — BeanFactory implements DI by resolving and injecting constructor/field dependencies

**Builds On This (learn these next):**

- `ApplicationContext` — the full-featured container extending BeanFactory
- `BeanDefinition` — the recipe BeanFactory uses to create beans
- `BeanPostProcessor` — the extension mechanism that runs after bean creation
- `BeanFactoryPostProcessor` — the extension mechanism that modifies bean definitions before creation

**Alternatives / Comparisons:**

- `ApplicationContext` — the superset; use this in all production code
- `CDI (Contexts and Dependency Injection)` — the Java EE/Jakarta EE alternative to Spring's BeanFactory

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ WHAT IT IS   │ Spring's root container interface —       │
│              │ creates, caches, and resolves beans       │
├──────────────┼───────────────────────────────────────────┤
│ PROBLEM IT   │ Heavyweight EJB containers with no        │
│ SOLVES       │ lightweight embedded alternative          │
├──────────────┼───────────────────────────────────────────┤
│ KEY INSIGHT  │ Stores definitions (cheap) separately     │
│              │ from instances (expensive) — singleton    │
│              │ cache makes repeated lookups free         │
├──────────────┼───────────────────────────────────────────┤
│ USE WHEN     │ Constrained environments, test slices,    │
│              │ dynamic plugin registration               │
├──────────────┼───────────────────────────────────────────┤
│ AVOID WHEN   │ Production Spring Boot apps — use         │
│              │ ApplicationContext instead                │
├──────────────┼───────────────────────────────────────────┤
│ TRADE-OFF    │ Lightweight + flexible vs no events,      │
│              │ AOP, or i18n support                      │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "The recipe book and kitchen — minus      │
│              │ the dining room."                         │
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ ApplicationContext → Bean Lifecycle →     │
│              │ BeanPostProcessor                         │
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** `BeanFactory` uses a singleton cache: every `getBean()` call for a singleton returns the same instance. But what happens when two threads call `getBean()` simultaneously for a bean that hasn't been created yet? Trace the exact synchronization mechanism Spring uses to prevent duplicate creation, and explain why the three-level cache (singletonObjects, earlySingletonObjects, singletonFactories) is necessary rather than a simple synchronized block.

**Q2.** Spring's parent-child `BeanFactory` hierarchy lets child contexts look up beans from parent contexts, but not the reverse. What problem does this directional lookup solve, and when would you actually use parent-child contexts in production? What breaks if you try to inject a child-context bean into a parent-context bean?
