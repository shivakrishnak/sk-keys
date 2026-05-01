---
layout: default
title: "BeanFactory"
parent: "Spring Core"
nav_order: 374
permalink: /spring/bean-factory/
number: "374"
category: Spring Core
difficulty: ★★☆
depends_on: IoC (Inversion of Control), DI (Dependency Injection), Bean
used_by: ApplicationContext, Spring Core Internals
tags: #intermediate, #spring, #internals, #deep-dive
---

# 374 — BeanFactory

`#intermediate` `#spring` `#internals` `#deep-dive`

⚡ TL;DR — `BeanFactory` is the root interface of Spring's IoC container, providing basic bean instantiation and retrieval with lazy initialisation — `ApplicationContext` extends it with enterprise features needed in production.

| #374            | Category: Spring Core                                       | Difficulty: ★★☆ |
| :-------------- | :---------------------------------------------------------- | :-------------- |
| **Depends on:** | IoC (Inversion of Control), DI (Dependency Injection), Bean |                 |
| **Used by:**    | ApplicationContext, Spring Core Internals                   |                 |

---

### 📘 Textbook Definition

`BeanFactory` is the root interface in Spring's bean container hierarchy, defining the contract for an IoC container that manages bean definitions and produces bean instances. It provides core operations: `getBean(name)`, `getBean(type)`, `containsBean(name)`, `isSingleton(name)`, `isPrototype(name)`, and `getType(name)`. The primary implementation is `DefaultListableBeanFactory`, which implements both `BeanFactory` and `BeanDefinitionRegistry`. Unlike `ApplicationContext`, `BeanFactory` initialises beans lazily (on first `getBean()` call), does NOT automatically detect and register `BeanPostProcessor` or `BeanFactoryPostProcessor` implementations, does NOT publish application events, and does NOT integrate with Spring's `Environment` abstraction. It is rarely used directly in application code; its importance is as the underlying implementation that `ApplicationContext` delegates to.

---

### 🟢 Simple Definition (Easy)

`BeanFactory` is the most basic Spring container — it knows how to create beans and give them to you when asked, but it doesn't automatically wire everything up the way `ApplicationContext` does.

---

### 🔵 Simple Definition (Elaborated)

Think of `BeanFactory` as the engine inside Spring's container. It holds all the bean definitions (descriptions of how to create each bean), creates beans on demand, and injects their declared dependencies. `ApplicationContext` is built on top of `BeanFactory` and adds the full suite of Spring features: auto-registration of post-processors, event publication, property resolution, and AOP. In application development you almost always work with `ApplicationContext` (or Spring Boot's auto-configured version of it). `BeanFactory` knowledge matters when: debugging Spring internals, writing framework-level code (like custom Spring extensions), or understanding why certain features (like `@Autowired`) require an `ApplicationContext` rather than a raw `BeanFactory`.

---

### 🔩 First Principles Explanation

**What BeanFactory does — and what it deliberately omits:**

```java
// BeanFactory in its minimal form:
DefaultListableBeanFactory factory = new DefaultListableBeanFactory();

// Manually register a bean definition
factory.registerBeanDefinition("orderService",
    BeanDefinitionBuilder
        .rootBeanDefinition(OrderService.class)
        .addConstructorArgReference("paymentGateway")
        .getBeanDefinition()
);

factory.registerBeanDefinition("paymentGateway",
    BeanDefinitionBuilder
        .rootBeanDefinition(StripeGateway.class)
        .getBeanDefinition()
);

// Bean is NOT yet created — lazy
OrderService svc = factory.getBean(OrderService.class); // created NOW

// IMPORTANT: @Autowired does NOT work without manually adding the processor:
factory.addBeanPostProcessor(
    new AutowiredAnnotationBeanPostProcessor() // must be added manually!
);
// ApplicationContext does this automatically; BeanFactory does NOT
```

**The lazy vs eager distinction:**

```
BeanFactory behaviour:
  startup:    parse bean definitions only — zero beans instantiated
  getBean():  instantiate bean + its dependency graph on first call
  → startup is fast; misconfiguration discovered only at first use

ApplicationContext behaviour:
  startup:    instantiate ALL singleton beans during refresh()
  → startup is slower; misconfiguration discovered immediately
  → appropriate for production: fail fast, not fail later
```

**DefaultListableBeanFactory — the real workhorse:**

```
BeanFactory (interface)
    └─ HierarchicalBeanFactory (interface)
          └─ ConfigurableBeanFactory (interface)
                └─ ConfigurableListableBeanFactory (interface)
                      └─ DefaultListableBeanFactory (class) ← the real impl
                            ↑
                   ApplicationContext delegates to this
```

`ApplicationContext` implementations hold a `DefaultListableBeanFactory` internally and delegate all bean operations to it while adding the enterprise feature layer on top.

---

### ❓ Why Does This Exist (Why Before What)

WITHOUT BeanFactory (no separation of container contract from implementation):

What breaks without it:

1. No stable API for IoC containers — different Spring modules could not rely on a common interface.
2. Custom bean containers (test doubles, embedded containers, Spring extensions) have no base contract to implement.
3. The `ApplicationContext` implementation would be a monolith — no separation between core container and enterprise features.

WITH BeanFactory:
→ Clear separation of concerns: `BeanFactory` = core container contract; `ApplicationContext` = enterprise enrichment.
→ Lightweight containers (resource-constrained environments, unit tests) can use `DefaultListableBeanFactory` without the overhead of a full `ApplicationContext`.
→ Spring framework internals use `ConfigurableListableBeanFactory` directly for fine-grained container manipulation (e.g., in `BeanFactoryPostProcessor`).

---

### 🧠 Mental Model / Analogy

> Think of `BeanFactory` as a kitchen pantry with a recipe book. The pantry has all the ingredients (bean definitions) and a recipe book (bean metadata). When you ask for a dish (getBean), the pantry prepares it for you. `ApplicationContext` is the full restaurant: it has the pantry, plus trained waitstaff (BeanPostProcessors), an announcement system (events), a calendar (lifecycle callbacks), and menus pre-printed at startup (eager singleton initialisation). The pantry is always there inside the restaurant — the restaurant is just a much richer environment built around it.

"Pantry with recipe book" = BeanFactory (definitions + lazy creation)
"Preparing a dish on request" = lazy bean instantiation
"Full restaurant with all staff" = ApplicationContext
"Trained waitstaff" = auto-registered BeanPostProcessors
"Pre-printed menus (eager init)" = singleton beans created at context refresh

---

### ⚙️ How It Works (Mechanism)

**BeanFactory getBean() flow:**

```
┌──────────────────────────────────────────────┐
│  BeanFactory.getBean(OrderService.class)     │
│                                              │
│  1. Look up BeanDefinition for OrderService  │
│  2. Check if singleton instance exists       │
│     → YES: return cached instance            │
│     → NO: proceed to create                 │
│  3. Resolve dependencies (DI):               │
│     find PaymentGateway bean definition      │
│     recursively create PaymentGateway        │
│  4. Instantiate: call constructor with deps  │
│  5. Apply BeanPostProcessor (if registered)  │
│  6. Store singleton in singleton cache       │
│  7. Return instance                          │
└──────────────────────────────────────────────┘
```

**BeanDefinition — what BeanFactory stores:**

```java
// BeanDefinition holds the blueprint for creating a bean:
BeanDefinition def = new RootBeanDefinition(OrderService.class);
def.setScope(BeanDefinition.SCOPE_SINGLETON);  // or "prototype"
def.setLazyInit(false);
def.setConstructorArgumentValues(...);
def.setPropertyValues(...);
def.setInitMethodName("init");    // @PostConstruct equivalent
def.setDestroyMethodName("close");// @PreDestroy equivalent

// ApplicationContext wraps this in a richer BeanDefinitionHolder
// and processes it through BeanFactoryPostProcessors before use
```

---

### 🔄 How It Connects (Mini-Map)

```
BeanFactory (interface)  ◄──── (you are here)
        │  ← extended by →
        ▼
ApplicationContext
(adds events, post-processors, properties, AOP)
        │  ← delegates bean ops back to →
        ▼
DefaultListableBeanFactory
(the real impl: BeanFactory + BeanDefinitionRegistry)
        │
        ├──────────────────────────────────┐
        ▼                                  ▼
BeanFactoryPostProcessor          BeanPostProcessor
(modifies definitions pre-init)   (modifies instances post-init)
```

---

### 💻 Code Example

**Example 1 — Using BeanFactory directly (framework / test use):**

```java
// Create a standalone BeanFactory (no ApplicationContext overhead)
DefaultListableBeanFactory factory = new DefaultListableBeanFactory();

// Load bean definitions from XML
XmlBeanDefinitionReader reader =
    new XmlBeanDefinitionReader(factory);
reader.loadBeanDefinitions("classpath:beans.xml");

// Manually register BeanPostProcessors (ApplicationContext does this auto)
factory.addBeanPostProcessor(
    new AutowiredAnnotationBeanPostProcessor());

// Beans are NOT yet created — only definitions loaded
OrderService svc = factory.getBean(OrderService.class);
// Created on first getBean() call — lazy
```

**Example 2 — Accessing BeanFactory inside a BeanFactoryPostProcessor:**

```java
// BeanFactoryPostProcessor receives ConfigurableListableBeanFactory
// (the BeanFactory interface with modification capabilities)
@Component
class DatabaseUrlOverridePostProcessor
    implements BeanFactoryPostProcessor {

    @Override
    public void postProcessBeanFactory(
            ConfigurableListableBeanFactory beanFactory) {

        // Access and modify bean definitions BEFORE beans are instantiated
        BeanDefinition ds =
            beanFactory.getBeanDefinition("dataSource");
        MutablePropertyValues props = ds.getPropertyValues();
        props.addPropertyValue("url", System.getenv("DATABASE_URL"));
        // The DataSource bean will be created with the overridden URL
    }
}
```

---

### ⚠️ Common Misconceptions

| Misconception                                          | Reality                                                                                                                                                                                                                               |
| ------------------------------------------------------ | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `BeanFactory` is deprecated and should never be used   | `BeanFactory` is the core interface; `ApplicationContext` extends it. The interface is actively used by all Spring internals. What is discouraged is using `BeanFactory` directly in application code instead of `ApplicationContext` |
| `BeanFactory` performs eager initialisation by default | `BeanFactory` (via `DefaultListableBeanFactory`) is lazy: beans are created on first `getBean()`. `ApplicationContext` overrides this by calling `preInstantiateSingletons()` during `refresh()` to eagerly init all singletons       |
| `@Autowired` works with a raw `BeanFactory`            | `@Autowired` is processed by `AutowiredAnnotationBeanPostProcessor`. With a raw `BeanFactory`, this processor must be manually registered. `ApplicationContext` registers it automatically                                            |
| `BeanFactory` and `FactoryBean` are related concepts   | They are distinct: `BeanFactory` is the IoC container interface. `FactoryBean` is a special bean type that produces other beans (a factory managed by the container). The names are unfortunately similar                             |

---

### 🔥 Pitfalls in Production

**Using raw BeanFactory without registering BeanPostProcessors — silent injection failure**

```java
// BAD: raw factory without BeanPostProcessor registration
DefaultListableBeanFactory factory = new DefaultListableBeanFactory();
factory.registerBeanDefinition("orderService", def);
OrderService svc = factory.getBean(OrderService.class);
// svc.paymentGateway is NULL — @Autowired was never processed
// No error thrown — silent failure

// GOOD: either use ApplicationContext, OR register the processor manually
factory.addBeanPostProcessor(new AutowiredAnnotationBeanPostProcessor());
// Only use raw BeanFactory when ApplicationContext overhead is genuinely unacceptable
// (e.g., extremely resource-constrained embedded systems, custom test scenarios)
```

---

**Mutating BeanFactory post-initialisation — race conditions in lazy resolution**

```java
// BAD: registering new bean definitions after context has started
// (bypasses post-processing and can cause inconsistent state)
@Component
class DynamicBeanRegistrar implements CommandLineRunner {
    @Autowired
    ConfigurableListableBeanFactory factory;

    public void run(String... args) {
        factory.registerBeanDefinition("dynamicService", def);
        // AOP proxies will NOT be created for this bean
        // @Transactional will NOT work on dynamicService
    }
}

// GOOD: use ApplicationContext's registerBean() or prototype scope
// for runtime bean creation; or use FactoryBean for dynamic instances
```

---

### 🔗 Related Keywords

- `ApplicationContext` — extends `BeanFactory` with enterprise features; the container you use in practice
- `Bean` — the objects whose lifecycle `BeanFactory` manages
- `Bean Lifecycle` — the phases a bean goes through inside the `BeanFactory`
- `BeanFactoryPostProcessor` — receives the `ConfigurableListableBeanFactory` to modify bean definitions
- `BeanPostProcessor` — processes bean instances after they are created by the `BeanFactory`
- `IoC (Inversion of Control)` — the principle that `BeanFactory` implements
- `FactoryBean` — a special Spring interface; a bean that is itself a factory for other objects

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ KEY IDEA     │ Root IoC container interface: getBean,    │
│              │ lazy init, no auto post-processor wiring  │
├──────────────┼───────────────────────────────────────────┤
│ VS CONTEXT   │ BeanFactory: lazy, minimal, no auto-reg   │
│              │ ApplicationContext: eager, full-featured  │
├──────────────┼───────────────────────────────────────────┤
│ REAL IMPL    │ DefaultListableBeanFactory — used          │
│              │ internally by all ApplicationContexts     │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "BeanFactory is the engine; Application-  │
│              │ Context is the finished car."             │
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ ApplicationContext → Bean Lifecycle →     │
│              │ BeanPostProcessor → BeanFactoryPostProc.  │
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** A performance engineer measures Spring Boot application startup time and finds that `finishBeanFactoryInitialization()` — the step where all singletons are eagerly instantiated — accounts for 80% of startup time. They propose replacing `ApplicationContext` with a raw `DefaultListableBeanFactory` to get lazy initialisation, claiming it will reduce startup from 30 seconds to 2 seconds. Identify at least four Spring features that silently stop working with a raw `BeanFactory`, explain the runtime consequences of each failure, and propose an alternative approach that achieves fast startup without sacrificing these features.

**Q2.** `FactoryBean<T>` is a Spring interface where implementing it makes the bean itself act as a factory: `getBean("myFactory")` returns the object produced by `FactoryBean.getObject()`, and `getBean("&myFactory")` returns the `FactoryBean` instance itself. Explain when you would choose `FactoryBean` over a `@Bean` factory method in a `@Configuration` class, describe the `&` prefix convention and which Spring internals use it, and identify a specific scenario from the Spring ecosystem (e.g., `SqlSessionFactoryBean`, `ProxyFactoryBean`) where `FactoryBean` solves a problem that `@Bean` methods cannot.
