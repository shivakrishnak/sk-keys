---
layout: default
title: "Bean Lifecycle"
parent: "Spring Core"
nav_order: 376
permalink: /spring/bean-lifecycle/
number: "376"
category: Spring Core
difficulty: ★★☆
depends_on: Bean, ApplicationContext, BeanPostProcessor, DI (Dependency Injection)
used_by: BeanPostProcessor, BeanFactoryPostProcessor, @Transactional, AOP
tags: #intermediate, #spring, #internals, #deep-dive
---

# 376 — Bean Lifecycle

`#intermediate` `#spring` `#internals` `#deep-dive`

⚡ TL;DR — The Bean Lifecycle is the sequence of phases a Spring bean passes through — from instantiation and dependency injection, through initialisation callbacks, to active use and final destruction.

| #376            | Category: Spring Core                                                  | Difficulty: ★★☆ |
| :-------------- | :--------------------------------------------------------------------- | :-------------- |
| **Depends on:** | Bean, ApplicationContext, BeanPostProcessor, DI (Dependency Injection) |                 |
| **Used by:**    | BeanPostProcessor, BeanFactoryPostProcessor, @Transactional, AOP       |                 |

---

### 📘 Textbook Definition

The **Bean Lifecycle** in Spring is the ordered sequence of phases that every bean passes through from the moment the container creates it to the moment the container destroys it. The sequence is: (1) _instantiation_ — the bean class is instantiated via its constructor; (2) _property population_ — dependencies are injected via constructor, setter, or field; (3) _BeanNameAware / BeanFactoryAware / ApplicationContextAware_ callbacks; (4) `BeanPostProcessor.postProcessBeforeInitialization()`; (5) `@PostConstruct` / `InitializingBean.afterPropertiesSet()` / custom `init-method`; (6) `BeanPostProcessor.postProcessAfterInitialization()` — where AOP proxies are created; (7) bean is ready for use; (8) `@PreDestroy` / `DisposableBean.destroy()` / custom `destroy-method` — on container shutdown. Understanding this lifecycle is essential for writing `BeanPostProcessor` extensions, debugging AOP proxy creation, and managing resources correctly.

---

### 🟢 Simple Definition (Easy)

The bean lifecycle is the set of steps Spring follows from "create this object" to "destroy this object" — you can plug in your own code at several of these steps.

---

### 🔵 Simple Definition (Elaborated)

When Spring starts, it does not just call `new MyService()` and move on. It follows a precise pipeline: create the object, inject its dependencies, call any setup methods you declared (`@PostConstruct`), then wrap it in a proxy if needed (for `@Transactional` or `@Cacheable`). From that point the bean is "live" and handles requests. On shutdown, Spring calls your cleanup method (`@PreDestroy`) before destroying the bean. The reason this matters in practice: `@PostConstruct` lets you run setup code after all dependencies are injected (safe place to call injected dependencies), `@PreDestroy` lets you release resources (close connections, shut down thread pools), and knowing when the AOP proxy is created (after `@PostConstruct`) explains why calling `this.transactionalMethod()` from within a bean bypasses the transaction.

---

### 🔩 First Principles Explanation

**The complete lifecycle, phase by phase:**

```
Phase 1: Instantiation
  Spring calls the constructor (chosen by DI rules).
  Dependencies are not yet available.
  Do NOT access injected dependencies here.

Phase 2: Dependency Injection (Property Population)
  Constructor injection: happens in Phase 1.
  Setter / field injection: happens here, after construction.

Phase 3: Aware Interface Callbacks
  BeanNameAware.setBeanName(name)
  BeanFactoryAware.setBeanFactory(factory)
  ApplicationContextAware.setApplicationContext(ctx)
  Use these to give a bean access to container metadata.

Phase 4: BeanPostProcessor.postProcessBeforeInitialization()
  All registered BeanPostProcessors run BEFORE the init method.
  Example: @PostConstruct processing by
    CommonAnnotationBeanPostProcessor.

Phase 5: Initialisation
  @PostConstruct method  (preferred modern approach)
  InitializingBean.afterPropertiesSet()  (Spring interface)
  init-method in @Bean(initMethod="init")  (XML/config)
  At this point, all dependencies are injected and verified.
  SAFE to call injected services here.

Phase 6: BeanPostProcessor.postProcessAfterInitialization()
  AOP proxy is created HERE by AnnotationAwareAspectJAutoProxyCreator.
  @Transactional, @Cacheable, @Async wrappers are applied here.
  The object in the application context AFTER this step is the PROXY,
  not the original bean instance.

Phase 7: Bean is Ready (Active)
  Bean handles application requests for the duration of its scope.

Phase 8: Destruction (on context close / @PreDestroy)
  @PreDestroy method  (preferred)
  DisposableBean.destroy()  (Spring interface)
  destroy-method in @Bean(destroyMethod="close")
  NOTE: prototype beans do NOT receive destruction callbacks.
```

**Why `@PostConstruct` is the right place for initialisation code:**

```java
@Service
class CacheWarmer {
    private final ProductRepository repo; // injected dependency

    CacheWarmer(ProductRepository repo) {
        this.repo = repo;
        // DO NOT call repo here — Phase 1, repo not yet injected via field/setter
        // (For constructor injection it IS available here, but @PostConstruct
        //  is still preferred for clarity and interface parity)
    }

    @PostConstruct  // Phase 5 — all deps injected, safe to use them
    void warmCache() {
        repo.findTopProducts().forEach(cache::put); // safe
        log.info("Cache warmed with {} products", cache.size());
    }

    @PreDestroy     // Phase 8 — cleanup before bean destroyed
    void clearCache() {
        cache.clear();
    }
}
```

---

### ❓ Why Does This Exist (Why Before What)

WITHOUT Bean Lifecycle:

What breaks without it:

1. No safe point to run initialisation code after all dependencies are injected — `@PostConstruct` does not exist.
2. No hook to release resources (connections, threads) on shutdown — resource leaks on application stop.
3. No mechanism for AOP proxy creation after initialisation — `@Transactional` cannot wrap the real bean.
4. No way for beans to receive their Spring-assigned name or the containing context reference — prevents self-registration patterns.

WITH Bean Lifecycle:
→ `@PostConstruct` provides a guaranteed safe initialisation point: all dependencies are set, all proxy wrappers not yet applied.
→ `@PreDestroy` enables clean shutdown: thread pools, connections, and caches are released properly.
→ `BeanPostProcessor` hooks enable AOP proxy creation, annotation processing, and framework-level bean transformation.
→ Lifecycle events (`ApplicationReadyEvent`, `ContextClosedEvent`) allow services to react to container state changes.

---

### 🧠 Mental Model / Analogy

> Think of hiring and onboarding a new employee. The lifecycle mirrors the process: recruitment (instantiation), orientation and providing equipment (dependency injection), introduction to the team (Aware callbacks), HR check-in before first day (BeanPostProcessor before init), first day training (PostConstruct), passing them through the building's badge system (BeanPostProcessor after init — proxy wrapping), working life (active ready state), and finally an exit interview and return of equipment (PreDestroy). You cannot do first-day training before they have their equipment — similarly, `@PostConstruct` is guaranteed to run after all dependencies are available.

"Providing equipment (laptop, badge)" = dependency injection
"First-day training" = @PostConstruct initialisation
"Badge system wrapping access" = AOP proxy created in postProcessAfterInitialization
"Exit interview and equipment return" = @PreDestroy cleanup

---

### ⚙️ How It Works (Mechanism)

**The full lifecycle as a diagram:**

```
┌──────────────────────────────────────────────┐
│  Spring Bean Lifecycle                       │
│                                              │
│  1. constructor()           ← instantiate   │
│           ↓                                  │
│  2. setter injection        ← wire deps     │
│           ↓                                  │
│  3. *Aware callbacks        ← meta access   │
│           ↓                                  │
│  4. BPP.postProcessBefore() ← pre-init hook │
│           ↓                                  │
│  5. @PostConstruct / init() ← user init     │
│           ↓                                  │
│  6. BPP.postProcessAfter()  ← AOP proxy ✦  │
│           ↓                                  │
│  7. [ BEAN IS READY / IN USE ]              │
│           ↓                                  │
│  8. @PreDestroy / destroy() ← user cleanup  │
│           ↓                                  │
│  9. GC                      ← gone          │
│                                              │
│  ✦ The proxy replaces the bean in context   │
└──────────────────────────────────────────────┘
```

**The self-invocation trap — why internal `@Transactional` calls fail:**

```java
@Service
class OrderService {
    // In the ApplicationContext, this reference points to the AOP PROXY,
    // not the raw OrderService instance.

    public void placeOrder(Order order) {
        // 'this' refers to the RAW bean — bypasses the proxy!
        this.processPayment(order); // @Transactional on processPayment IGNORED
    }

    @Transactional  // only works when called through the proxy
    public void processPayment(Order order) { ... }
}
// Fix: inject self, or extract processPayment to a separate bean
```

---

### 🔄 How It Connects (Mini-Map)

```
Bean (object registered with the container)
        │
        ▼
Bean Lifecycle  ◄──── (you are here)
        │
        ├──────────────────────────────────────────┐
        ▼                                          ▼
BeanPostProcessor                       BeanFactoryPostProcessor
(phases 4 and 6 — instance hooks)       (pre-lifecycle — definition hooks)
        │                                          │
        ▼                                          ▼
AOP Proxy creation                      @ConfigurationProperties binding
(@Transactional, @Cacheable, @Async)    (property injection into beans)
        │
        ▼
@PostConstruct / @PreDestroy
(user lifecycle callbacks)
```

---

### 💻 Code Example

**Example 1 — All lifecycle hooks in one class:**

```java
@Component("orderProcessor")
class OrderProcessor implements BeanNameAware,
                                InitializingBean,
                                DisposableBean {
    private final OrderRepository repo;
    private String beanName;

    // Phase 1+2: constructor injection
    OrderProcessor(OrderRepository repo) { this.repo = repo; }

    // Phase 3: Aware callback
    @Override
    public void setBeanName(String name) { this.beanName = name; }

    // Phase 5a: @PostConstruct (processed by CommonAnnotationBPP)
    @PostConstruct
    void postConstruct() {
        log.info("[{}] @PostConstruct — all deps injected", beanName);
    }

    // Phase 5b: InitializingBean (runs after @PostConstruct)
    @Override
    public void afterPropertiesSet() {
        log.info("[{}] afterPropertiesSet", beanName);
    }

    // Phase 8a: @PreDestroy
    @PreDestroy
    void preDestroy() {
        log.info("[{}] @PreDestroy — preparing for shutdown", beanName);
    }

    // Phase 8b: DisposableBean.destroy (runs after @PreDestroy)
    @Override
    public void destroy() {
        log.info("[{}] destroy()", beanName);
    }
}
// Log output at startup: @PostConstruct → afterPropertiesSet
// Log output at shutdown: @PreDestroy → destroy()
```

**Example 2 — Resource management via @PostConstruct / @PreDestroy:**

```java
@Component
class ManagedScheduler {
    private ScheduledExecutorService executor;

    @PostConstruct
    void start() {
        executor = Executors.newScheduledThreadPool(4);
        executor.scheduleAtFixedRate(this::checkHealth, 0, 30, SECONDS);
        log.info("Health checker started");
    }

    @PreDestroy
    void stop() {
        executor.shutdown();
        try {
            if (!executor.awaitTermination(10, SECONDS))
                executor.shutdownNow();
        } catch (InterruptedException e) {
            executor.shutdownNow();
            Thread.currentThread().interrupt();
        }
        log.info("Health checker stopped");
    }
}
```

---

### ⚠️ Common Misconceptions

| Misconception                                                                      | Reality                                                                                                                                                                                              |
| ---------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `@PostConstruct` runs before dependency injection                                  | `@PostConstruct` runs AFTER all dependencies are injected — that is its guarantee and purpose. The constructor runs at Phase 1; `@PostConstruct` at Phase 5                                          |
| AOP proxy is applied before `@PostConstruct`                                       | AOP proxies are created by `BeanPostProcessor.postProcessAfterInitialization()` — Phase 6, AFTER `@PostConstruct`. This means `this` inside `@PostConstruct` is always the raw bean, never the proxy |
| Prototype beans have the same lifecycle as singleton beans                         | Prototype beans receive Phases 1–6 (instantiation through post-processing) but NOT Phase 8 (destruction). Spring does not track prototype instances; `@PreDestroy` is never called for them          |
| `InitializingBean.afterPropertiesSet()` and `@PostConstruct` run in the same phase | Both run in Phase 5, but `@PostConstruct` runs first (processed by `CommonAnnotationBeanPostProcessor` in Phase 4/5), then `afterPropertiesSet()` runs                                               |

---

### 🔥 Pitfalls in Production

**Calling `@Transactional` method via `this` — transaction silently skipped**

```java
// BAD: self-invocation bypasses the AOP proxy
@Service
class InvoiceService {
    public void generateMonthlyInvoices() {
        for (Account acc : accounts) {
            this.generateInvoice(acc); // 'this' = raw bean, not proxy
        }                             // @Transactional IGNORED!
    }

    @Transactional
    public void generateInvoice(Account acc) {
        // No transaction wrapping — DB operations not atomic
    }
}

// GOOD option A: inject self via @Autowired (Spring injects the proxy)
@Autowired @Lazy InvoiceService self;
self.generateInvoice(acc); // uses proxy — @Transactional works

// GOOD option B: extract to a separate @Transactional bean
@Service
class InvoiceGenerator {
    @Transactional
    public void generateInvoice(Account acc) { ... }
}
```

---

**@PreDestroy not called for prototype beans — resource leak**

```java
// BAD: expecting @PreDestroy on a prototype bean
@Component
@Scope("prototype")
class ExpensiveResource {
    private Connection conn;

    @PostConstruct void open()  { conn = db.acquire(); }
    @PreDestroy    void close() { conn.close(); } // NEVER called by Spring!
}
// Connections leak — Spring creates prototype beans on demand
// but does NOT track them for destruction

// GOOD: manage prototype resource lifecycle explicitly
// Use a try-with-resources pattern, or use @Scope("singleton")
// for shared resources, or implement DisposableBean and call
// ctx.close() on the specific prototype instance manually
```

---

### 🔗 Related Keywords

- `Bean` — the object whose lifecycle this describes
- `BeanPostProcessor` — the extension point at phases 4 and 6 of the lifecycle
- `BeanFactoryPostProcessor` — runs before any beans are instantiated; modifies bean definitions
- `@PostConstruct` — the preferred initialisation callback (Phase 5)
- `@PreDestroy` — the preferred cleanup callback (Phase 8)
- `ApplicationContext` — the container that drives the lifecycle sequence
- `AOP (Aspect-Oriented Programming)` — proxies created at Phase 6; explains self-invocation limitation
- `Bean Scope` — determines how many times the lifecycle runs (once for singleton; per-use for prototype)

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ PHASES       │ construct → inject → Aware → BPP.before  │
│              │ → PostConstruct → BPP.after(proxy) → USE │
│              │ → PreDestroy → destroy                   │
├──────────────┼───────────────────────────────────────────┤
│ SAFE INIT    │ @PostConstruct: all deps present,         │
│              │ called before AOP proxy is applied        │
├──────────────┼───────────────────────────────────────────┤
│ PROXY TRAP   │ AOP proxy created AFTER @PostConstruct    │
│              │ → 'this.method()' bypasses transactions   │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "Bean lifecycle = hire → onboard →        │
│              │ badge-activate → work → exit interview."  │
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ BeanPostProcessor → BeanFactoryPostProc →│
│              │ AOP → @Transactional → CGLIB Proxy        │
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** A bean implements `ApplicationContextAware` and stores a reference to the `ApplicationContext` in a static field during Phase 3 of the lifecycle. Another bean, created earlier in the same context refresh, tries to call `AppContextHolder.getContext().getBean(SomeService.class)` during its own `@PostConstruct`. Describe the exact ordering problem this creates, explain whether the static reference is guaranteed to be set when the second bean's `@PostConstruct` runs, and identify a safer alternative to the `ApplicationContextAware` static holder pattern for this use case.

**Q2.** Spring's `SmartLifecycle` interface extends `Lifecycle` and adds `getPhase()` and `isAutoStartup()` methods. Multiple `SmartLifecycle` beans can be started and stopped in phase order. Describe a concrete production scenario where ordering the startup and shutdown of `SmartLifecycle` beans is critical (e.g., a Kafka consumer starting before a database connection pool is ready would fail), explain how Spring determines startup vs shutdown order from the `getPhase()` return value, and identify the relationship between `SmartLifecycle` phases and the `ApplicationReadyEvent` timing.
