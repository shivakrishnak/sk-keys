---
layout: default
title: "BeanFactory"
parent: "Spring Core"
nav_order: 374
permalink: /spring/bean-factory/
number: "374"
category: Spring Core
difficulty: ★☆☆
depends_on: IoC, Bean, Dependency Injection
used_by: ApplicationContext, BeanPostProcessor, Lazy Beans, Spring Internals
tags: #java, #spring, #foundational, #internals
---

# 374 — BeanFactory

`#java` `#spring` `#foundational` `#internals`

⚡ TL;DR — Spring's minimal, lazy-initialising IoC container interface — the root abstraction that ApplicationContext extends with enterprise features.

| #374 | category: Spring Core
|:---|:---|:---|
| **Depends on:** | IoC, Bean, Dependency Injection | |
| **Used by:** | ApplicationContext, BeanPostProcessor, Lazy Beans, Spring Internals | |

---

### 📘 Textbook Definition

`BeanFactory` is the root interface of Spring's IoC container hierarchy. It defines the fundamental contract for a bean container: `getBean(name)`, `containsBean(name)`, `isSingleton(name)`, `getType(name)`, and related methods. `BeanFactory` implements lazy initialisation — beans are created only when first requested via `getBean()`, not eagerly at startup. It does not provide event publication, AOP auto-application, environment abstraction, internationalisation, or automatic `BeanPostProcessor` registration. `ApplicationContext` extends `BeanFactory` and adds all these enterprise features. `BeanFactory` is primarily relevant as the root API type and for understanding Spring internals; production applications always use `ApplicationContext`.

---

### 🟢 Simple Definition (Easy)

`BeanFactory` is Spring's basic "bean dispenser" — ask it for a bean by name or type and it creates and returns one. ApplicationContext is the full-featured version you actually use in production.

---

### 🔵 Simple Definition (Elaborated)

BeanFactory is the minimal foundation of Spring's container. It can create beans, inject dependencies, and return them on demand. But it does nothing automatically — no eager startup, no AOP proxies, no event system. You'd only write code that depends on `BeanFactory` directly if you're building a lightweight embedded container or working deep in Spring's plumbing. In practice, every Spring application uses `ApplicationContext`, which implements `BeanFactory` and adds all the features a real application needs. Understanding `BeanFactory` helps understand the core contract that all Spring containers share.

---

### 🔩 First Principles Explanation

**The minimal contract — what every container must do:**

`BeanFactory` defines the irreducible minimum a Spring container must provide:

```java
// Core BeanFactory API
public interface BeanFactory {
  Object getBean(String name);
  <T> T getBean(String name, Class<T> requiredType);
  <T> T getBean(Class<T> requiredType);
  boolean containsBean(String name);
  boolean isSingleton(String name);
  boolean isPrototype(String name);
  Class<?> getType(String name);
}
```

**The lazy-init difference:**

```
┌───────────────────────────────────────────────┐
│  BeanFactory (lazy)                           │
│                                               │
│  Startup: only reads configuration            │
│  First getBean("userService"):                │
│    → creates UserService                      │
│    → injects UserRepository                  │
│    → returns the bean                         │
│  Startup is fast; first request is slow       │
│                                               │
│  ApplicationContext (eager)                   │
│                                               │
│  Startup: creates ALL singleton beans         │
│  First getBean("userService"):                │
│    → returns already-created bean (fast)      │
│  Startup is slower; requests are always fast  │
└───────────────────────────────────────────────┘
```

**Why BeanFactory exists as a separate interface:**

It allows Spring-integrated frameworks (e.g. test frameworks, lightweight containers) to depend only on the minimal contract without requiring full ApplicationContext. Spring's `ListableBeanFactory`, `HierarchicalBeanFactory`, and `ConfigurableListableBeanFactory` all extend `BeanFactory` with progressively more capability.

---

### ❓ Why Does This Exist (Why Before What)

**WITHOUT a BeanFactory abstraction:**

```
Without BeanFactory as a root interface:

  Code that only needs to look up beans
  must depend on the full ApplicationContext
  → heavyweight dependency for lightweight use

  Test frameworks can't use minimal containers
  → must spin up full context for any bean access

  Spring's own internals (BeanPostProcessor,
  FactoryBean, etc.) would need to import
  ApplicationContext → circular dependency
```

**WITH BeanFactory:**

```
→ Clean separation: minimal contract at root
  → progressive enhancement upward
→ Test / embedded containers can use just BeanFactory
→ Spring's internal wiring uses BeanFactory APIs
  without depending on ApplicationContext features
→ External code checks: instanceof BeanFactory
  → works for all container implementations
```

---

### 🧠 Mental Model / Analogy

> `BeanFactory` is like a **basic vending machine** — insert a name, receive a product. It dispenses items on demand, one at a time, only when you ask. `ApplicationContext` is the full **supermarket** — everything is stocked and ready before you arrive, there are announcements on the intercom (events), loyalty programmes (profiles), and a bakery section that wraps your purchases (AOP proxies).

"Basic vending machine" = BeanFactory — minimal, on-demand
"Products dispensed on request" = lazy bean creation
"Full supermarket" = ApplicationContext — stocked, featured
"Items ready before you arrive" = eager singleton initialisation
"Intercom announcements" = ApplicationEventPublisher

---

### ⚙️ How It Works (Mechanism)

**BeanFactory hierarchy:**

```
BeanFactory
  └── ListableBeanFactory
        (enumerate all beans by type/name)
  └── HierarchicalBeanFactory
        (parent-child container chains)
  └── ConfigurableListableBeanFactory
        (used internally by Spring for full config)
        └── DefaultListableBeanFactory
              (concrete implementation used internally)

ApplicationContext
  └── extends BeanFactory (via all above)
  └── adds: events, i18n, env, eager init, BPPs
```

**Direct usage (rare — mainly for lightweight scenarios):**

```java
// Only for embedded / test lightweight scenarios
DefaultListableBeanFactory factory =
    new DefaultListableBeanFactory();
BeanDefinitionReader reader =
    new XmlBeanDefinitionReader(factory);
reader.loadBeanDefinitions(new ClassPathResource("beans.xml"));

// Beans created lazily on first access
UserService svc = factory.getBean(UserService.class);
// Note: @Transactional does NOT work here — no BPPs run
```

**FactoryBean — BeanFactory's factory hook:**

```java
// A special bean that creates OTHER beans
@Component
public class ConnectionFactoryBean
    implements FactoryBean<Connection> {

  @Override
  public Connection getObject() throws Exception {
    return DriverManager.getConnection(url);
  }

  @Override
  public Class<?> getObjectType() {
    return Connection.class;
  }

  @Override
  public boolean isSingleton() { return true; }
}
// ctx.getBean("connectionFactoryBean") → Connection object
// ctx.getBean("&connectionFactoryBean") → the FactoryBean itself
```

---

### 🔄 How It Connects (Mini-Map)

```
IoC Principle (103)
        ↓
  BEANFACTORY (106)  ← you are here
  (root container interface — minimal contract)
        ↓
  Extended by:
  ApplicationContext (105)
  (adds events, profiles, AOP, eager init)
        ↓
  Implemented internally by:
  DefaultListableBeanFactory
  (does the actual bean creation work)
        ↓
  Special subtypes:
  FactoryBean → creates complex beans
  ObjectFactory → deferred bean resolution
```

---

### 💻 Code Example

**Example 1 — BeanFactory vs ApplicationContext behaviour:**

```java
// ApplicationContext: eager init catches errors at startup
@SpringBootApplication
public class App {
  // BAD bean — circular dep or missing required dep
  @Bean OrderService orderService(PaymentGateway gw) {
    return new OrderService(gw); // gw missing → FAIL at start
  }
  // → Startup fails fast; no requests ever served
}

// BeanFactory lazy: error surfaces at first getBean() call
DefaultListableBeanFactory factory = new DefaultListableBeanFactory();
// ... register bean definitions
// No error yet — beans not created
factory.getBean(OrderService.class); // ERROR here, at runtime
// Dangerous: app appears to start successfully
```

**Example 2 — Accessing the FactoryBean vs its product:**

```java
@Component
public class MyFactoryBean implements FactoryBean<MyService> {
  @Override
  public MyService getObject() {
    return new MyService(complexConfig);
  }
  @Override
  public Class<?> getObjectType() { return MyService.class; }
}

// Normal access: gets the product (MyService)
MyService svc = ctx.getBean("myFactoryBean", MyService.class);

// Ampersand prefix: gets the FactoryBean itself
MyFactoryBean fb = ctx.getBean("&myFactoryBean");
```

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| BeanFactory is the container you interact with in Spring Boot | ApplicationContext is always used in production. BeanFactory is the interface, not the runtime object you work with |
| BeanFactory and ApplicationContext initialise beans the same way | BeanFactory is lazy (first getBean()); ApplicationContext is eager (all singletons at startup) |
| FactoryBean is the same as BeanFactory | FactoryBean is a special bean that CREATES other beans. BeanFactory is the container interface |
| BeanFactory runs BeanPostProcessors automatically | BeanFactory does NOT auto-discover or run BeanPostProcessors — you must register them manually |

---

### 🔥 Pitfalls in Production

**1. Using BeanFactory directly — missing AOP proxy application**

```java
// BAD: getting BeanFactory from ApplicationContext
// and using it directly bypasses BPP processing
BeanFactory bf = (BeanFactory) ctx;
UserService svc = bf.getBean(UserService.class);
// @Transactional WORKS here — bean was already
// created by ApplicationContext with proxy applied

// But if using standalone BeanFactory:
DefaultListableBeanFactory bf = new DefaultListableBeanFactory();
// register beans manually... BPPs never auto-run
// @Transactional does NOTHING — no proxy created
// Dangerous in integration test setups
```

**2. Confusing FactoryBean's & prefix in bean names**

```java
// Attempting to inject a FactoryBean by type
@Autowired MyService service;         // gets the PRODUCT
@Autowired MyFactoryBean factory;     // gets the FactoryBean

// getBean() with & prefix — only works with string name
ctx.getBean("&myFactoryBean");        // the FactoryBean
ctx.getBean(MyFactoryBean.class);     // also the FactoryBean
ctx.getBean("myFactoryBean");         // the PRODUCT (MyService)
// Most developers trip on this in integration tests
```

---

### 🔗 Related Keywords

- `ApplicationContext` — extends BeanFactory with all enterprise features; use this in production
- `Bean` — the objects BeanFactory creates and manages
- `IoC` — the principle BeanFactory implements at the most basic level
- `FactoryBean` — a special BeanFactory-aware bean that delegates bean creation to custom logic
- `DefaultListableBeanFactory` — the concrete implementation used internally by ApplicationContext
- `BeanPostProcessor` — must be registered manually with BeanFactory; ApplicationContext auto-discovers them

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ KEY IDEA     │ Root container interface — minimal,       │
│              │ lazy-init; ApplicationContext adds all    │
│              │ enterprise features on top               │
├──────────────┼───────────────────────────────────────────┤
│ USE WHEN     │ Writing Spring-compatible framework code  │
│              │ that needs only basic bean lookup         │
├──────────────┼───────────────────────────────────────────┤
│ AVOID WHEN   │ Application code: always use             │
│              │ ApplicationContext, never raw BeanFactory │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "BeanFactory is the key;                  │
│              │  ApplicationContext is the full keyring." │
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ ApplicationContext (105) → Bean (107) →   │
│              │ Bean Lifecycle (108)                      │
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** `DefaultListableBeanFactory` is used *inside* ApplicationContext as the actual bean registry. When you call `ctx.getBean(UserService.class)`, trace the exact call chain from ApplicationContext down to DefaultListableBeanFactory — explaining what each layer adds — and describe the specific data structure DefaultListableBeanFactory uses to store beans by type vs by name, and why type-based lookup (by Class) is more expensive than name-based lookup.

**Q2.** Spring's `FactoryBean` pattern predates `@Bean` factory methods. Explain the specific use case where `FactoryBean` is still preferable over a `@Bean` method in 2026 — specifically, what `FactoryBean.isSingleton()` returning `false` enables that a `@Bean` method cannot replicate, and how Spring's `@Scope` annotations on `@Bean` methods partially close this gap but still fall short in one key scenario.

