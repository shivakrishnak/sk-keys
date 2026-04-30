---
layout: default
title: "Bean Lifecycle"
parent: "Spring Core"
nav_order: 376
permalink: /spring/bean-lifecycle/
number: "376"
category: Spring Core
difficulty: ★★★
depends_on: Bean, ApplicationContext, BeanPostProcessor, @PostConstruct
used_by: BeanPostProcessor, SmartLifecycle, DisposableBean, @PreDestroy
tags: #java, #spring, #springboot, #internals, #advanced, #deep-dive
---

# 376 — Bean Lifecycle

`#java` `#spring` `#springboot` `#internals` `#advanced` `#deep-dive`

⚡ TL;DR — The complete ordered sequence of phases Spring executes from bean instantiation through dependency injection, initialisation callbacks, AOP proxy creation, and finally destruction.

| #376 | category: Spring Core
|:---|:---|:---|
| **Depends on:** | Bean, ApplicationContext, BeanPostProcessor, @PostConstruct | |
| **Used by:** | BeanPostProcessor, SmartLifecycle, DisposableBean, @PreDestroy | |

---

### 📘 Textbook Definition

The **Spring Bean Lifecycle** is the ordered sequence of operations the container performs for every singleton bean from creation to destruction. It proceeds through: **instantiation** (constructor), **dependency injection** (field, setter, constructor), **Aware callbacks** (`setBeanName`, `setApplicationContext`), **pre-init BeanPostProcessor** processing, **initialisation callbacks** (`@PostConstruct`, `InitializingBean.afterPropertiesSet()`, custom `init-method`), **post-init BeanPostProcessor** processing (where AOP proxies are created by `AbstractAutoProxyCreator`), **bean in use**, and **destruction** (`@PreDestroy`, `DisposableBean.destroy()`, custom `destroy-method`). Each phase is an extension point for customising or instrumenting beans.

---

### 🟢 Simple Definition (Easy)

Every Spring bean goes through a birth-to-death journey: Spring creates it, fills in its dependencies, calls your setup methods, wraps it in proxies, puts it to work, then calls your cleanup methods on shutdown.

---

### 🔵 Simple Definition (Elaborated)

The lifecycle exists because constructors alone aren't enough for complex initialisation. A connection pool must open connections *after* the database URL is injected — not before. A Kafka consumer must start listening *after* all authentication beans are ready. Spring's `@PostConstruct` runs after all injection completes (safe). `@PreDestroy` runs before the context closes (cleanup guaranteed). The lifecycle's most powerful feature: `BeanPostProcessor.postProcessAfterInitialization()` fires after `@PostConstruct`, and this is exactly where Spring creates the CGLIB proxy for `@Transactional` methods — that's how AOP works without any manual proxy setup.

---

### 🔩 First Principles Explanation

**Problem — initialisation order dependencies:**

```java
// UNSAFE: constructor fires before injection
@Service
class DataProcessor {
  @Value("${batch.size}")
  private int batchSize; // NOT set during constructor

  public DataProcessor() {
    processBatch(batchSize); // batchSize = 0!
  }
}
```

A constructor cannot safely use injected values — injection happens *after* the constructor returns. `@PostConstruct` solves this: it fires after all injection completes.

**BeanPostProcessor — the AOP proxy integration point:**

After `@PostConstruct` completes, `BeanPostProcessor.postProcessAfterInitialization()` fires. This is where `AbstractAutoProxyCreator` examines the bean for `@Transactional`, `@Async`, `@Cacheable`, `@Secured` — and if found, creates a CGLIB subclass proxy that wraps every method call with the appropriate advice. The proxy replaces the original bean in the container. All callers get the proxy, not the original.

---

### ❓ Why Does This Exist (Why Before What)

**WITHOUT lifecycle callbacks:**

```
WITHOUT lifecycle phases:

  No @PostConstruct:
    Init code in constructor — but @Value/@Autowired
    not yet set → NPE or invalid state at runtime

  No @PreDestroy:
    Connection pools not closed → connection leak
    Kafka consumers stop mid-message → lost messages
    Temp files never deleted → disk fills up

  No BeanPostProcessor post-init:
    @Transactional is an annotation only — no proxy
    @Async does not spawn threads
    @Cacheable does not cache
    Spring Security cannot intercept methods
```

**WITH lifecycle hooks:**

```
→ @PostConstruct: safely use all injected values
→ @PreDestroy: guaranteed cleanup on graceful shutdown
→ BPP postProcessAfterInit: AOP proxies created here
  → all features that depend on method-level interception
→ SmartLifecycle: ordered start/stop (Kafka consumer
  starts AFTER auth service is fully ready)
→ DisposableBean: cleanup even if @PreDestroy missed
```

---

### 🧠 Mental Model / Analogy

> The lifecycle is like a **surgeon's hospital shift**. First: arrive and credential (constructor + Aware callbacks). Then: briefing and equipment (dependency injection). Confirm readiness: open sterile field (@PostConstruct). Get your enhanced gear (BPP wraps you in special tools — AOP proxy). Perform operations (bean in use). End of shift: complete post-op notes and sterilise (@PreDestroy). Leave without cleanup and the next shift inherits chaos — like a bean that leaks resources.

"Credentialing" = constructor + Aware callbacks
"Briefing and equipment" = dependency injection
"Opening sterile field" = @PostConstruct — all deps available
"Enhanced gear applied" = BPP.postProcessAfterInit (AOP proxy)
"Post-op cleanup" = @PreDestroy / DisposableBean

---

### ⚙️ How It Works (Mechanism)

**Complete lifecycle — every step:**

```
┌─────────────────────────────────────────────────────┐
│  SPRING BEAN LIFECYCLE (singleton)                  │
├─────────────────────────────────────────────────────┤
│  1. Instantiate (invoke constructor)                │
│  2. Inject: @Autowired, @Value, constructor params  │
│  3. setBeanName()  — BeanNameAware                  │
│  4. setBeanFactory() — BeanFactoryAware             │
│  5. setApplicationContext() — AppContextAware       │
│  6. BPP.postProcessBeforeInitialization()           │
│     (CommonAnnotationBPP processes @PostConstruct)  │
│  7. @PostConstruct methods                          │
│  8. InitializingBean.afterPropertiesSet()           │
│  9. Custom @Bean(initMethod = "init")               │
│  10. BPP.postProcessAfterInitialization()           │
│      ← AOP PROXY CREATED HERE                      │
│         AbstractAutoProxyCreator detects            │
│         @Transactional / @Async / @Cacheable        │
│         → creates CGLIB proxy → replaces bean       │
│  11. Bean stored in context (proxy if applicable)   │
│  ─────────────────────────────────────────          │
│  SHUTDOWN (context.close() or JVM shutdown hook)   │
│  12. @PreDestroy methods                            │
│  13. DisposableBean.destroy()                       │
│  14. Custom @Bean(destroyMethod = "cleanup")        │
└─────────────────────────────────────────────────────┘
```

**Declaring init / destroy — three options:**

```java
// Option 1: JSR-250 annotations (preferred — no Spring dep)
@PostConstruct public void init()     { openConnections(); }
@PreDestroy    public void cleanup()  { closeConnections(); }

// Option 2: Spring interfaces
class Pool implements InitializingBean, DisposableBean {
  public void afterPropertiesSet() { openConnections(); }
  public void destroy()           { closeConnections(); }
}

// Option 3: @Bean factory method attributes
@Bean(initMethod = "start", destroyMethod = "close")
public ScheduledExecutorService executor() {
  return Executors.newScheduledThreadPool(4);
}
```

---

### 🔄 How It Connects (Mini-Map)

```
ApplicationContext.refresh() triggers startup
        ↓
  Instantiate + inject all singleton beans
        ↓
  BEAN LIFECYCLE HOOKS  ← you are here
  BPP.beforeInit → @PostConstruct → BPP.afterInit
        ↓
  BPP.postProcessAfterInitialization
  AbstractAutoProxyCreator checks @Transactional etc.
        ↓
  AOP PROXY (CGLIB) created and stored in context
        ↓
  Application in service
        ↓
  Shutdown → @PreDestroy → DisposableBean.destroy()
```

---

### 💻 Code Example

**Example 1 — @PostConstruct for safe post-injection init:**

```java
@Component
public class CacheWarmer {
  private final ProductRepository repo;
  private final CacheManager cacheManager;

  public CacheWarmer(ProductRepository repo,
                     CacheManager cacheManager) {
    this.repo         = repo;
    this.cacheManager = cacheManager;
    // DO NOT warm cache here — proxy not yet applied
  }

  @PostConstruct  // All beans ready, proxies in place
  public void warmCache() {
    repo.findTopSellers(100)
        .forEach(p -> cacheManager
            .getCache("products")
            .put(p.getId(), p));
  }

  @PreDestroy
  public void flushCache() {
    cacheManager.getCache("products").clear();
  }
}
```

**Example 2 — SmartLifecycle for ordered start/stop:**

```java
@Component
public class KafkaConsumerBean implements SmartLifecycle {
  private boolean running = false;

  @Override
  public void start() {
    consumer.subscribe(topics);
    this.running = true;
  }

  @Override
  public void stop() {
    consumer.wakeup();  // unblocks poll()
    this.running = false;
  }

  @Override public boolean isRunning() { return running; }
  @Override public int getPhase() { return Integer.MAX_VALUE; }
  // MAX_VALUE = last to start, first to stop on shutdown
}
```

**Example 3 — AOP proxy creation verified:**

```java
@Service
@Transactional
public class OrderService {

  @PostConstruct
  public void onInit() {
    // At @PostConstruct: BPP.postProcessAfter not yet run
    // THIS = real OrderService, NOT yet a proxy
    log.info(this.getClass().getName());
    // → com.example.OrderService (no CGLIB suffix)
  }
}

// After context refresh — proxy confirmed:
OrderService proxy = ctx.getBean(OrderService.class);
proxy.getClass().getName();
// → com.example.OrderService$$SpringCGLIB$$0
AopUtils.isAopProxy(proxy); // true
AopUtils.getTargetClass(proxy); // OrderService.class
```

---

### 🔁 Flow / Lifecycle

```
ApplicationContext.refresh()
        ↓
Step 1: new OrderService()         ← constructor
        ↓
Step 2: @Autowired deps injected   ← injection
        ↓
Step 3: setBeanName("orderSvc")    ← BeanNameAware
        ↓
Step 4: setApplicationContext(ctx) ← AppContextAware
        ↓
Step 5: BPP.postProcessBefore()    ← @PostConstruct detected
        ↓
Step 6: orderService.init()        ← @PostConstruct
        ↓
Step 7: BPP.postProcessAfter()
        AbstractAutoProxyCreator sees @Transactional
        → creates CGLIB proxy wrapping orderService
        ↓
Context stores: proxy (not original)
════════════════════════
App handles requests via proxy
════════════════════════
JVM shutdown signal
        ↓
Step 8: orderService.shutdown()   ← @PreDestroy
Step 9: disposable.destroy()      ← DisposableBean
Context closed
```

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| @PostConstruct is called before dependencies are injected | @PostConstruct runs AFTER all injection completes — that is specifically why it exists |
| AOP proxies are created during @PostConstruct | Proxies are created AFTER @PostConstruct — in BPP.postProcessAfterInitialization(). Self-calls inside @PostConstruct bypass the proxy |
| @PreDestroy is always called on shutdown | @PreDestroy is called on graceful shutdown (context.close()). A hard `kill -9` skips it entirely |
| Prototype beans have @PreDestroy called | Spring NEVER calls @PreDestroy on prototype beans — you must manage prototype cleanup manually |
| You must use InitializingBean or DisposableBean | @PostConstruct and @PreDestroy (JSR-250) are preferred — no Spring dependency in your class |

---

### 🔥 Pitfalls in Production

**1. Self-invocation bypassing AOP proxy in @PostConstruct**

```java
@Service
@Transactional
public class MigrationService {
  @PostConstruct
  public void migrate() {
    this.runMigration(); // calls REAL object, not proxy
    // @Transactional has NO effect — no transaction!
  }
  public void runMigration() {
    repo.deleteAll(); // runs without transaction
  }
}
// Fix: use ApplicationRunner — runs after context is ready
@Component
class MigrationRunner implements ApplicationRunner {
  @Autowired MigrationService svc;
  @Override
  public void run(ApplicationArguments a) {
    svc.runMigration(); // called via proxy → transactional
  }
}
```

**2. Long @PostConstruct blocking Kubernetes readiness**

```java
// BAD: 30-second init blocks context refresh
// → Kubernetes sees NotReady → kills pod → restart loop
@PostConstruct
public void init() {
  loadAllProductsIntoCache(); // 500K records, 30s

}

// GOOD: async warm-up after full startup
@EventListener(ApplicationReadyEvent.class)
@Async
public void warmCacheAsync() {
  loadAllProductsIntoCache(); // non-blocking
}
// App ready immediately → Kubernetes marks Ready probe OK
```

**3. Prototype @PreDestroy never called — resource leak**

```java
// BAD: @PreDestroy on prototype is never invoked
@Scope("prototype")
@Component
class TempProcessor {
  @PreDestroy
  void cleanup() { tempDir.delete(); } // NEVER CALLED!
}

// GOOD: explicit lifecycle management
@Service
class Orchestrator {
  @Autowired ObjectProvider<TempProcessor> provider;

  public void process() {
    TempProcessor p = provider.getObject();
    try { p.run(); }
    finally { p.cleanup(); } // explicit
  }
}
```

---

### 🔗 Related Keywords

- `Bean` — the subject of the lifecycle; every singleton bean passes through these phases
- `ApplicationContext` — orchestrates the full lifecycle at startup and shutdown
- `BeanPostProcessor` — fires at pre-init and post-init phases; creates AOP proxies
- `@Transactional` — applied via CGLIB proxy created in postProcessAfterInitialization
- `SmartLifecycle` — ordered start/stop across beans (Kafka, schedulers)
- `@PostConstruct` — JSR-250 post-injection init annotation; preferred over InitializingBean

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ KEY IDEA     │ new → inject → @PostConstruct →           │
│              │ BPP proxy → use → @PreDestroy → done      │
├──────────────┼───────────────────────────────────────────┤
│ USE WHEN     │ @PostConstruct: resource init after inj;  │
│              │ @PreDestroy: cleanup on shutdown          │
├──────────────┼───────────────────────────────────────────┤
│ AVOID WHEN   │ Long sync work in @PostConstruct (blocks  │
│              │ startup); @PreDestroy on prototype beans  │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "Injection first, then init —             │
│              │  the proxy wraps after both."             │
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ BeanPostProcessor (110) → Spring AOP →    │
│              │ @Transactional (127)                      │
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** A `BeanPostProcessor` implementation scans for a custom `@Encrypt` annotation and wraps qualifying beans in a CGLIB proxy. If the `BeanPostProcessor` itself has an `@Autowired` dependency on a `@Service` bean, Spring's BeanPostProcessorChecker fires a warning. Explain exactly why this is a problem — which `@Service` bean in the application will be created *without* the `@Encrypt` proxy — and describe the correct design for a `BeanPostProcessor` that needs collaborating beans without causing this ordering issue.

**Q2.** Spring's `AbstractAutoProxyCreator` stores the CGLIB proxy in the singleton registry. When you call `ctx.getBean(OrderService.class)`, you get the proxy. But when `OrderService.methodA()` calls `this.methodB()` internally — both methods are `@Transactional` with different propagation settings — the inner call bypasses the proxy entirely. Explain why this occurs at the bytecode level, what the two standard solutions are (`AopContext.currentProxy()` and self-injection), and why self-injection is generally the cleaner approach for Spring Boot applications.

