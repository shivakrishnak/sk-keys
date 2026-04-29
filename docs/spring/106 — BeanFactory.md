---
layout: default
title: "BeanFactory"
parent: "Spring Framework"
nav_order: 106
permalink: /spring/beanfactory/
---

`#spring` `#internals` `#foundational`

⚡ TL;DR — BeanFactory is Spring's root IoC container interface — the minimal core that creates beans on demand; ApplicationContext extends it with enterprise features.

---

## 📘 Textbook Definition

`BeanFactory` is the root interface of Spring's IoC container hierarchy. It provides the foundational contract for object configuration, creation, and dependency injection. It follows a lazy initialization strategy — beans are instantiated only when first requested via `getBean()`.

---

## 🟢 Simple Definition (Easy)

BeanFactory is the simplest possible version of Spring's container. It's a factory that knows how to create and configure objects (beans). Think of it as the stripped-down core that ApplicationContext builds on top of.

---

## 🔵 Simple Definition (Elaborated)

BeanFactory reads configuration metadata (XML, annotations, Java config), maintains a registry of bean definitions, and creates beans lazily when requested. It handles basic dependency injection, but none of the advanced features: no events, no AOP support, no `@PostConstruct`, no environment/profile abstraction. These extras are in `ApplicationContext`. In modern Spring (especially Spring Boot), you almost always work with `ApplicationContext` — but knowing `BeanFactory` helps you understand what's really happening under the hood.

---

## 🔩 First Principles Explanation

**BeanFactory is the core contract:**

```java
public interface BeanFactory {
    Object getBean(String name);
    <T> T getBean(Class<T> requiredType);
    boolean containsBean(String name);
    boolean isSingleton(String name);
    boolean isPrototype(String name);
    Class<?> getType(String name);
    // ... few more
}
```

The key implementation: `DefaultListableBeanFactory` — the actual engine that stores `BeanDefinition` objects, resolves dependencies, and instantiates beans.

**Lazy vs. Eager:**

```
BeanFactory (Lazy)               ApplicationContext (Eager)
──────────────────               ─────────────────────────
Bean created: first getBean()    Bean created: at refresh() startup
Error surfaced: at runtime       Error surfaced: at startup
Memory: lower until first use    Memory: all singletons loaded upfront
```

---

## ❓ Why Does This Exist (Why Before What)

BeanFactory exists as the minimal interface so that alternative IoC containers, test utilities, and framework internals can operate with the minimal contract without pulling in all the enterprise features of ApplicationContext. It's the lean core of the IoC engine.

---

## 🧠 Mental Model / Analogy

> BeanFactory is like a **bare-bones recipe book** — it knows how to cook every dish (create every bean) but only when you explicitly ask for a dish. ApplicationContext is the full restaurant — it has the recipe book, plus staff (event system), a menu board (environment/properties), a dining room (web support), and everything else.

---

## ⚙️ How It Works (Mechanism)

```
BeanDefinition Registry (DefaultListableBeanFactory)
         ↓
  registerBeanDefinition("userService", bd)
         ↓
  getBean("userService") called for the first time
         ↓
  BeanDefinition inspected: class, scope, constructor args
         ↓
  Bean instantiated via reflection or constructor
         ↓
  Dependencies injected (other beans looked up recursively)
         ↓
  Bean stored in singleton cache (if scope=singleton)
         ↓
  Bean returned to caller
```

---

## 🔄 How It Connects (Mini-Map)

```
[BeanFactory] ← root interface
      ↓ extended by
[ListableBeanFactory]   [HierarchicalBeanFactory]
      ↓ extended by
[ApplicationContext] ← adds events, i18n, AOP, profiles
      ↓ implemented by
[AnnotationConfigApplicationContext]
[ClassPathXmlApplicationContext]
[GenericWebApplicationContext]
```

---

## 💻 Code Example

```java
// Low-level BeanFactory usage (rare in practice, useful for understanding)
DefaultListableBeanFactory factory = new DefaultListableBeanFactory();

// Register a bean definition programmatically
BeanDefinitionBuilder builder = BeanDefinitionBuilder
    .genericBeanDefinition(UserService.class)
    .addConstructorArgReference("userRepository"); // inject by name
factory.registerBeanDefinition("userService", builder.getBeanDefinition());

// Get bean lazily — only now is UserService instantiated
UserService service = factory.getBean("userService", UserService.class);

// ── In practice, use ApplicationContext ──────────────────────────────────────
// ApplicationContext wraps DefaultListableBeanFactory internally
ApplicationContext ctx = new AnnotationConfigApplicationContext(AppConfig.class);
// ctx.getBeanFactory() returns the underlying DefaultListableBeanFactory
ConfigurableListableBeanFactory underlying = ctx.getBeanFactory();
```

---

## ⚠️ Common Misconceptions

| ❌ Wrong Belief | ✅ Correct Reality |
|---|---|
| ApplicationContext IS BeanFactory | ApplicationContext *extends* BeanFactory; they're in a hierarchy |
| Should use BeanFactory in modern apps | Always use ApplicationContext; BeanFactory is for internals/testing |
| BeanFactory supports AOP | BeanFactory alone doesn't; AOP requires BeanPostProcessors in ApplicationContext |
| BeanFactory is faster at runtime | Only startup differs (lazy vs eager); runtime performance is identical |

---

## 🔥 Pitfalls in Production

**Pitfall 1: Using BeanFactory directly in production**
```java
// Bad: misses @PostConstruct, AOP proxies, events
BeanFactory bf = new DefaultListableBeanFactory();

// Good: use ApplicationContext
ApplicationContext ctx = new AnnotationConfigApplicationContext(AppConfig.class);
```

**Pitfall 2: Lazy init hiding misconfiguration**
> BeanFactory's lazy init means a missing bean dependency only fails when that code path is executed at runtime. ApplicationContext reveals these at startup. Prefer ApplicationContext for early error detection.

---

## 🔗 Related Keywords

- **[ApplicationContext](./105 — ApplicationContext.md)** — extends BeanFactory with enterprise features
- **[Bean](./107 — Bean.md)** — objects created by BeanFactory
- **[IoC (Inversion of Control)](./103 — IoC (Inversion of Control).md)** — the principle BeanFactory implements
- **[BeanFactoryPostProcessor](./111 — BeanFactoryPostProcessor.md)** — hook to modify BeanFactory before bean creation

---

## 📌 Quick Reference Card

```
+------------------------------------------------------------------+
| KEY IDEA    | Minimal IoC interface — lazy bean creation          |
+------------------------------------------------------------------+
| USE WHEN    | Framework internals, tests needing minimal container |
+------------------------------------------------------------------+
| USE IN PROD | ApplicationContext instead (extends BeanFactory)    |
+------------------------------------------------------------------+
| ONE-LINER   | "The raw engine; ApplicationContext is the full car"|
+------------------------------------------------------------------+
| NEXT EXPLORE| ApplicationContext → BeanDefinition → Bean Lifecycle|
+------------------------------------------------------------------+
```

---

## 🧠 Think About This Before We Continue

**Q1.** `BeanFactory` is lazy; `ApplicationContext` is eager. Give a real-world scenario where each behavior is preferable.

**Q2.** `DefaultListableBeanFactory` is the main implementation of BeanFactory — it also implements `BeanDefinitionRegistry`. Why is this dual role important for Spring's startup process?

**Q3.** If `ApplicationContext` extends `BeanFactory`, is an `ApplicationContext` usable anywhere a `BeanFactory` is expected? What design pattern does this represent?

