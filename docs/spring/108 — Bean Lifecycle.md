---
layout: default
title: "Bean Lifecycle"
parent: "Spring Framework"
nav_order: 108
permalink: /spring/bean-lifecycle/
number: "108"
category: Spring & Spring Boot
difficulty: ★★☆
depends_on: Bean, IoC, ApplicationContext
used_by: BeanPostProcessor, @PostConstruct, @PreDestroy
tags: #spring, #internals, #intermediate
---

# 108 — Bean Lifecycle

`#spring` `#internals` `#intermediate`

⚡ TL;DR — A Spring Bean's lifecycle spans instantiation → dependency injection → initialization callbacks → active use → destruction callbacks — all orchestrated by the container.

| #108 | Category: Spring & Spring Boot | Difficulty: ★★☆ |
|:---|:---|:---|
| **Depends on:** | Bean, IoC, ApplicationContext | |
| **Used by:** | BeanPostProcessor, @PostConstruct, @PreDestroy | |

---

### 📘 Textbook Definition

The Spring Bean Lifecycle is the sequence of phases a bean passes through from the moment the IoC container creates it to the moment it is destroyed. It encompasses instantiation, dependency injection, BeanPostProcessor processing, initialization callbacks (`@PostConstruct`, `InitializingBean`, `init-method`), active service, and destruction callbacks (`@PreDestroy`, `DisposableBean`, `destroy-method`).

---

### 🟢 Simple Definition (Easy)

Just like a living thing is born, grows up, does work, and eventually dies, a Spring bean is created by Spring, has its setup run, does its job, and gets cleaned up when the app shuts down. You can hook into the "born" and "dying" moments with `@PostConstruct` and `@PreDestroy`.

---

### 🔵 Simple Definition (Elaborated)

The bean lifecycle gives you well-defined hook points: after a bean is fully constructed and its dependencies are injected, `@PostConstruct` runs your setup code (opening DB connections, warming caches). When the app shuts down, `@PreDestroy` runs your teardown code (releasing resources, flushing data). BeanPostProcessors run before and after these hooks to apply framework-level transformations like AOP proxying.

---

### 🔩 First Principles Explanation

**Why hooks are necessary:**
A bean often can't do its full initialization in the constructor because not all dependencies are available yet. By the time `@PostConstruct` runs, every dependency has been injected and validated.
**The complete sequence:**
```
1.  Instantiation        — constructor called
2.  Dependency Injection — @Autowired fields/setters populated
3.  BeanNameAware        — setBeanName(name) called if implemented
4.  BeanFactoryAware     — setBeanFactory(bf) called if implemented
5.  ApplicationContextAware — setApplicationContext(ctx) if implemented
6.  BeanPostProcessor    — postProcessBeforeInitialization()
7.  @PostConstruct       — your initialization code
8.  InitializingBean     — afterPropertiesSet() if implemented
9.  init-method          — custom init method if configured
10. BeanPostProcessor    — postProcessAfterInitialization() (AOP proxies here!)
11. BEAN IS READY — live in application
         ... (app runs) ...
12. @PreDestroy          — your cleanup code
13. DisposableBean       — destroy() if implemented
14. destroy-method       — custom destroy method if configured
```

---

### ❓ Why Does This Exist (Why Before What)

Resources like database connections, file handles, and thread pools must be opened after configuration is available and closed before the JVM exits. The lifecycle gives clean, framework-provided hook points for this — without requiring the bean to manage its own construction or thread join.

---

### 🧠 Mental Model / Analogy

> Think of a bean's lifecycle like an **employee's journey at a company**: hired (instantiate), background check (dependency injection), onboarding training (`@PostConstruct`), productive work (active use), exit interview (`@PreDestroy`), access revoked (destroyed). HR (the container) handles all administrative steps.

---

### ⚙️ How It Works (Mechanism)

BeanPostProcessors run **twice** — before and after initialization callbacks. This is how AOP proxies are created: `AbstractAutoProxyCreator` (a BeanPostProcessor) wraps the bean in a proxy *after* `@PostConstruct` runs, so the proxy is the final object returned to callers.
```
Constructor
    ↓
@Autowired injection
    ↓
BPP.postProcessBeforeInitialization()
    ↓
@PostConstruct
    ↓
BPP.postProcessAfterInitialization() ← AOP PROXY CREATED HERE
    ↓
Bean returned to callers (may be a proxy, not the original object)
```

---

### 🔄 How It Connects (Mini-Map)
```
[Bean Lifecycle]
      ↓ depends on
[BeanPostProcessor] → processes bean before/after init
[ApplicationContext] → orchestrates full lifecycle
[AOP] → proxy applied in postProcessAfterInitialization()
[Bean Scope] → prototype beans: no destroy callbacks called by container
```

---

### 💻 Code Example
```java
@Service
public class DatabaseConnectionService implements InitializingBean, DisposableBean {
    @Value("\")
    private int poolSize;
    private Connection[] pool;
    // ── Option 1: @PostConstruct (PREFERRED) ─────────────────────────────────
    @PostConstruct
    public void init() {
        System.out.println("@PostConstruct — opening " + poolSize + " connections");
        pool = new Connection[poolSize];
        // open connections...
    }
    // ── Option 2: InitializingBean (framework coupling — avoid) ──────────────
    @Override
    public void afterPropertiesSet() {
        System.out.println("afterPropertiesSet — also called after @PostConstruct");
    }
    // ── Option 3: @PreDestroy (PREFERRED) ────────────────────────────────────
    @PreDestroy
    public void cleanup() {
        System.out.println("@PreDestroy — closing all connections");
        // close connections...
    }
    // ── Option 4: DisposableBean (framework coupling — avoid) ────────────────
    @Override
    public void destroy() {
        System.out.println("destroy() — also called after @PreDestroy");
    }
}
// ── @Bean with init/destroy method names ─────────────────────────────────────
@Configuration
public class CacheConfig {
    @Bean(initMethod = "start", destroyMethod = "stop")
    public CacheManager cacheManager() {
        return new HazelcastCacheManager();
    }
}
```

---

### ⚠️ Common Misconceptions

| ❌ Wrong Belief | ✅ Correct Reality |
|---|---|
| Constructor = @PostConstruct | Constructor runs before DI; @PostConstruct runs after all injection complete |
| @PreDestroy always runs | @PreDestroy only runs for singleton beans; prototype beans are not destroyed by container |
| initMethod and @PostConstruct conflict | They both run — @PostConstruct first, then InitializingBean, then init-method |
| AOP proxy wraps bean before @PostConstruct | The proxy is applied AFTER @PostConstruct (in postProcessAfterInitialization) |

---

### 🔥 Pitfalls in Production

**Pitfall 1: Using constructor for post-injection logic**
```java
// Bad: dependencies not injected yet in constructor
@Service
public class CacheService {
    @Autowired private RedisTemplate redis;
    public CacheService() {
        redis.expire("key", 100, TimeUnit.SECONDS); // NullPointerException! redis=null
    }
}
// Fix: use @PostConstruct
@PostConstruct public void init() { redis.expire("key", 100, TimeUnit.SECONDS); }
```
**Pitfall 2: Prototype beans never get @PreDestroy called**
```java
@Bean @Scope("prototype") public HeavyResource resource() { return new HeavyResource(); }
// Container creates it but NEVER calls @PreDestroy — you must close it manually
```

---

### 🔗 Related Keywords

- **[BeanPostProcessor](./110 — BeanPostProcessor.md)** — applies transformations around init callbacks
- **[BeanFactoryPostProcessor](./111 — BeanFactoryPostProcessor.md)** — modifies bean definitions before instantiation
- **[Bean Scope](./109 — Bean Scope.md)** — affects which lifecycle phases apply
- **[AOP](./118 — AOP (Aspect-Oriented Programming).md)** — proxy applied in postProcessAfterInitialization

---

### 📌 Quick Reference Card
```
+------------------------------------------------------------------+
| KEY IDEA    | Instantiate → Inject → Init → Active → Destroy      |
+------------------------------------------------------------------+
| INIT HOOK   | @PostConstruct (preferred), InitializingBean         |
+------------------------------------------------------------------+
| DESTROY HOOK| @PreDestroy (preferred), DisposableBean              |
+------------------------------------------------------------------+
| AOP PROXY   | Applied in postProcessAfterInitialization()          |
+------------------------------------------------------------------+
| ONE-LINER   | "Hook into born and dying moments of a bean"         |
+------------------------------------------------------------------+
```

---

### 🧠 Think About This Before We Continue

**Q1.** You inject a `@Transactional` service into your bean. Is the injected dependency the original object or an AOP proxy? At what lifecycle phase does the proxy get created?
**Q2.** If `@PostConstruct` throws an exception, what happens to the application startup? What about if `@PreDestroy` throws?
**Q3.** You have a prototype-scoped bean that holds an open file handle. How do you ensure the file is properly closed without the container calling `@PreDestroy`?
