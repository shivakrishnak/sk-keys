---
layout: default
title: "ApplicationContext"
parent: "Spring Framework"
nav_order: 105
permalink: /spring/applicationcontext/
---
# 105 — ApplicationContext

`#spring` `#springboot` `#internals` `#foundational`

⚡ TL;DR — ApplicationContext is Spring's full-featured IoC container — it manages beans, resolves dependencies, fires events, handles AOP, and provides environment abstraction all in one.

| #105 | Category: Spring & Spring Boot | Difficulty: ★★☆ |
|:---|:---|:---|
| **Depends on:** | BeanFactory, IoC, DI | |
| **Used by:** | Spring Boot, Spring MVC, AOP, @Configuration | |

---

### 📘 Textbook Definition

`ApplicationContext` is the central interface in Spring's IoC implementation. It extends `BeanFactory` and adds enterprise features including event publication, internationalization (i18n), resource loading, transparent AOP integration, and environment/profile abstraction. It is the primary entry point to Spring's container in production applications.

---

### 🟢 Simple Definition (Easy)

ApplicationContext is the Spring container — the box that holds all your application's objects (beans), wires them together, and manages their life from startup to shutdown.

---

### 🔵 Simple Definition (Elaborated)

When your Spring application starts, an `ApplicationContext` is created. It scans your code for `@Component`, `@Service`, `@Repository`, and `@Configuration` classes; creates objects (beans) for each; injects their dependencies; applies AOP proxies; and makes them available for use. It also handles events (`ApplicationEvent`), environment properties (`@Value`, `@Profile`), and resource loading (files, classpath, URLs). In Spring Boot, `SpringApplication.run()` creates and returns an `ApplicationContext` automatically.

---

### 🔩 First Principles Explanation

**Why is BeanFactory not enough?**

`BeanFactory` is the minimal IoC container — it just creates beans on demand. But enterprise applications need more:

```
BeanFactory (minimal)         ApplicationContext (enterprise)
─────────────────────         ──────────────────────────────
Bean creation               + Event publishing/listening
Bean lookup                 + Environment/profiles
Dependency injection        + i18n / MessageSource
                            + Resource loading
                            + Eager initialization
                            + AOP integration
                            + @PostConstruct support
```

`ApplicationContext` wraps `BeanFactory` and adds all the above.

**Eager vs. Lazy initialization:**

BeanFactory creates beans lazily (on first `getBean()` call). ApplicationContext creates all singleton beans eagerly at startup, surfacing all misconfiguration errors immediately rather than at runtime.

---

### ❓ Why Does This Exist (Why Before What)

Before Spring, managing an enterprise application's objects meant complex factories, service locators, and manual wiring — thousands of lines of boilerplate. ApplicationContext provides a unified, configuration-driven object lifecycle manager that eliminates all of this. It's the single "table of truth" for what exists in your application.

---

### 🧠 Mental Model / Analogy

> Think of ApplicationContext as the **city government** of your application. All citizens (beans) are registered with city hall (context). The government knows who needs what services (dependencies), provides utilities (events, messaging, resources), and handles birth (instantiation) and death certificates (destruction). No citizen manages themselves — the government coordinates everything.

---

### ⚙️ How It Works (Mechanism)

```
ApplicationContext.refresh() sequence:
────────────────────────────────────────
1. prepareRefresh()         — set startDate, active flag
2. obtainFreshBeanFactory() — create/reload BeanFactory, load BeanDefinitions
3. prepareBeanFactory()     — configure ClassLoader, BeanPostProcessors
4. postProcessBeanFactory() — hook for subclasses
5. invokeBeanFactoryPostProcessors() — run BeanFactoryPostProcessors (@PropertySource etc.)
6. registerBeanPostProcessors()      — register BeanPostProcessors (AOP, @Autowired etc.)
7. initMessageSource()      — i18n support
8. initApplicationEventMulticaster() — event system
9. onRefresh()              — hook for subclasses
10. registerListeners()     — wire ApplicationListeners
11. finishBeanFactoryInitialization() — instantiate ALL singleton beans
12. finishRefresh()         — publish ContextRefreshedEvent
```

---

### 🔄 How It Connects (Mini-Map)

```
          [ApplicationContext]
                 |
    ┌────────────┼────────────┐
    ↓            ↓             ↓
[BeanFactory] [Events]  [Environment]
    ↓            ↓             ↓
[Beans/DI] [Listeners] [Profiles/@Value]

Common implementations:
  AnnotationConfigApplicationContext  ← Java config / annotations
  AnnotationConfigWebApplicationContext ← Web apps
  ClassPathXmlApplicationContext      ← XML config (legacy)
  GenericWebApplicationContext        ← Spring Boot default
```

---

### 💻 Code Example

```java
// ── Standalone (non-Boot) application ────────────────────────────────────────
@Configuration
@ComponentScan("com.example")
public class AppConfig { }

public class Main {
    public static void main(String[] args) {
        // Create and refresh the ApplicationContext
        ApplicationContext ctx = new AnnotationConfigApplicationContext(AppConfig.class);

        // Get a bean
        UserService userService = ctx.getBean(UserService.class);
        userService.doWork();

        // Inspect beans
        System.out.println("All beans: " + Arrays.toString(ctx.getBeanDefinitionNames()));

        // Access environment
        Environment env = ctx.getEnvironment();
        System.out.println("Profile: " + Arrays.toString(env.getActiveProfiles()));

        // Publish a custom event
        ctx.publishEvent(new UserRegisteredEvent("alice"));

        // Close context (triggers @PreDestroy)
        ((ConfigurableApplicationContext) ctx).close();
    }
}

// ── Spring Boot (context created automatically) ───────────────────────────────
@SpringBootApplication
public class MyApp {
    public static void main(String[] args) {
        ApplicationContext ctx = SpringApplication.run(MyApp.class, args);
        // ctx is a GenericWebApplicationContext (or GenericApplicationContext if non-web)
    }
}

// ── Listening to context events ───────────────────────────────────────────────
@Component
public class StartupListener implements ApplicationListener<ContextRefreshedEvent> {
    @Override
    public void onApplicationEvent(ContextRefreshedEvent event) {
        System.out.println("Application fully started: " + event.getTimestamp());
    }
}
```

---

### 🔁 Flow / Lifecycle

```
1. ApplicationContext created (new / SpringApplication.run)
       ↓
2. refresh() called
       ↓
3. BeanDefinitions loaded (scan @Component, process @Configuration)
       ↓
4. BeanFactoryPostProcessors run (e.g., PropertySourcesPlaceholderConfigurer)
       ↓
5. BeanPostProcessors registered
       ↓
6. All singleton beans eagerly instantiated + dependencies injected
       ↓
7. BeanPostProcessors run (AOP proxies created, @Autowired validated)
       ↓
8. @PostConstruct methods called
       ↓
9. ContextRefreshedEvent published — app is LIVE
       ↓
10. On shutdown: ContextClosedEvent → @PreDestroy → beans destroyed
```

---

### ⚠️ Common Misconceptions

| ❌ Wrong Belief | ✅ Correct Reality |
|---|---|
| ApplicationContext = BeanFactory | ApplicationContext *extends* BeanFactory with many enterprise features |
| There's always one ApplicationContext | Spring MVC has parent (root) + child (web) contexts; Boot usually has one |
| `getBean()` is the right way to get beans | Use `@Autowired` / DI; `getBean()` is only for bootstrap / integration code |
| ApplicationContext is lazy like BeanFactory | ApplicationContext eagerly initializes ALL singletons at startup |
| Closing context is unnecessary | Always close in standalone apps: triggers `@PreDestroy` and cleanup |

---

### 🔥 Pitfalls in Production

**Pitfall 1: Using ApplicationContext as a service locator**
```java
// Bad: ApplicationContext as service locator — breaks DI benefits
@Autowired ApplicationContext ctx;
UserService us = ctx.getBean(UserService.class); // anti-pattern

// Good: declare the direct dependency
@Autowired UserService userService;
```

**Pitfall 2: Multiple context refresh causing duplicate initialization**
```java
// In tests: if you don't cache the context, Spring creates a new one per test class
// Fix: use @DirtiesContext carefully; Spring Test caches contexts by default
```

**Pitfall 3: Forgetting to close standalone contexts**
```java
// Fix: use try-with-resources
try (ConfigurableApplicationContext ctx =
        new AnnotationConfigApplicationContext(AppConfig.class)) {
    ctx.getBean(MyService.class).run();
} // auto-closes: @PreDestroy methods invoked
```

---

### 🔗 Related Keywords

- **[IoC (Inversion of Control)](./103 — IoC (Inversion of Control).md)** — the principle ApplicationContext implements
- **[BeanFactory](./106 — BeanFactory.md)** — the interface ApplicationContext extends
- **[Bean Lifecycle](./108 — Bean Lifecycle.md)** — the lifecycle ApplicationContext manages
- **[BeanPostProcessor](./110 — BeanPostProcessor.md)** — hooks ApplicationContext provides for bean customization
- **[Spring Boot Startup Lifecycle](./135 — Spring Boot Startup Lifecycle.md)** — how Boot bootstraps the ApplicationContext

---

### 📌 Quick Reference Card

```
+------------------------------------------------------------------+
| KEY IDEA    | Full-featured IoC container — manages all beans    |
+------------------------------------------------------------------+
| USE WHEN    | Always — it IS the Spring container                 |
+------------------------------------------------------------------+
| MAIN IMPL   | AnnotationConfigApplicationContext (non-web)        |
|             | SpringApplication.run() result (Spring Boot)        |
+------------------------------------------------------------------+
| ONE-LINER   | "The Spring container that knows everything"        |
+------------------------------------------------------------------+
| NEXT EXPLORE| BeanFactory → Bean Lifecycle → BeanPostProcessor    |
+------------------------------------------------------------------+
```

---

### 🧠 Think About This Before We Continue

**Q1.** What is the difference between `ApplicationContext.refresh()` and `ApplicationContext.start()`? When would you call each?

**Q2.** In a Spring MVC app (non-Boot), there are typically *two* ApplicationContexts — the root context and the web (DispatcherServlet) context. What beans live in each? Why?

**Q3.** If `ApplicationContext` eagerly initializes all singletons at startup, what happens when a bean's required dependency is missing? At what point does the error surface — startup or first use?
