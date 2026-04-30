---
layout: default
title: "Bean Lifecycle"
parent: "Spring & Spring Boot"
nav_order: 144
permalink: /spring/bean-lifecycle/
number: "144"
category: Spring & Spring Boot
difficulty: ★★★
depends_on: Bean, ApplicationContext, BeanPostProcessor, @PostConstruct
used_by: BeanPostProcessor, SmartLifecycle, DisposableBean, @PreDestroy
tags: #java, #spring, #springboot, #internals, #advanced, #deep-dive
---

# 144 — Bean Lifecycle

`#java` `#spring` `#springboot` `#internals` `#advanced` `#deep-dive`

⚡ TL;DR — The complete sequence of phases Spring executes from bean instantiation through dependency injection, initialisation callbacks, use, and destruction — with multiple extension points at each phase.

| #144 | Category: Spring & Spring Boot | Difficulty: ★★★ |
|:---|:---|:---|
| **Depends on:** | Bean, ApplicationContext, BeanPostProcessor, @PostConstruct | |
| **Used by:** | BeanPostProcessor, SmartLifecycle, DisposableBean, @PreDestroy | |

---

### 📘 Textbook Definition

The **Spring Bean Lifecycle** is the ordered sequence of operations the Spring container performs for every singleton bean from creation to destruction. The lifecycle passes through: **instantiation** (constructor call), **dependency injection** (property/constructor injection), **Aware interface callbacks** (`setBeanName`, `setApplicationContext`), **pre-init BeanPostProcessor** processing, **initialisation callbacks** (`@PostConstruct`, `InitializingBean.afterPropertiesSet()`, custom `init-method`), **post-init BeanPostProcessor** processing (where AOP proxies are created), **bean in use**, and finally **destruction callbacks** (`@PreDestroy`, `DisposableBean.destroy()`, custom `destroy-method`). Each phase provides extension points for customising bean behaviour.

---

### 🟢 Simple Definition (Easy)

Every Spring bean goes through a birth-to-death journey: Spring creates it, fills in its dependencies, calls setup methods, puts it to work, then calls cleanup methods when the app shuts down.

---

### 🔵 Simple Definition (Elaborated)

The lifecycle matters because setting up a bean often requires more than just running its constructor. A database connection pool needs to create connections after all config is injected. A message consumer needs to start listening after the broker URL is set. A thread pool needs to shut down gracefully. Spring provides @PostConstruct for post-injection setup and @PreDestroy for cleanup. BeanPostProcessors intercept every bean at two points — before and after initialisation — and are how Spring implements @Transactional, @Async, caching, and security: by wrapping beans in proxies *after* they're initialised.

---

### 🔩 First Principles Explanation

**Problem — initialisation order dependencies:**

Object construction can only set primitive values and wire references. But many resources require:

1. All properties injected (database URL, pool size)
2. Then open connections
3. All beans ready
4. Then start processing

A constructor cannot guarantee dependencies are available — they're injected after construction. So "open the connection pool" cannot go in the constructor safely:

```java
// UNSAFE: constructor fires before injection
@Service
class DataProcessor {
  @Value("${batch.size}")
  private int batchSize; // NOT yet set during constructor

  public DataProcessor() {
    processBatch(batchSize); // batchSize is 0!
  }
}
```

**The lifecycle phases solve this by providing ordered hooks:**

```
Constructor → @Value/@Autowired injected → @PostConstruct
             ↑ constructor runs here      ↑ safe to use here
```

**BeanPostProcessor — the powerful extensibility hook:**

The lifecycle's post-init phase is where Spring's most important features live. After a bean's `@PostConstruct` runs, `BeanPostProcessor.postProcessAfterInitialization()` fires. This is where `AbstractAutoProxyCreator` (the AOP proxy creator) examines the bean, detects `@Transactional` / `@Async` / `@Cacheable`, creates a CGLIB proxy wrapping the original bean, and registers the proxy in the container instead of the original.

---

### ❓ Why Does This Exist (Why Before What)

**WITHOUT lifecycle callbacks:**

```
WITHOUT lifecycle phases:

  No @PostConstruct:
    Cannot safely initialise resources after injection
    Must put init code in constructor, but
    properties aren't injected yet → NPE / invalid state

  No @PreDestroy:
    Connection pools leak on shutdown
    Message consumers stop without ACKing in-flight msgs
    File handles remain open → data corruption risk

  No BeanPostProcessor:
    @Transactional is dead annotation — no proxy created
    @Async doesn't start thread pools
    @Cacheable doesn't intercept methods
    Spring Security has no method-security proxy

  No Aware interfaces:
    Beans can't access container (beanName, context)
    without tightly coupling to Spring
```

**WITH lifecycle callbacks:**

```
→ @PostConstruct: init after all props injected (safe)
→ @PreDestroy: clean shutdown of resources
→ BeanPostProcessor: AOP proxy creation → all of
  @Transactional, @Async, @Cacheable, @Secured work
→ SmartLifecycle: start/stop integrations in order
  (e.g. Kafka consumer starts AFTER auth service)
→ DisposableBean: guaranteed cleanup even on exceptions
```

---

### 🧠 Mental Model / Analogy

> The bean lifecycle is like a **surgeon's shift at a hospital**. First, the surgeon arrives and is credentialed (constructor + Aware callbacks). Then they receive their briefing and equipment (dependency injection). They confirm readiness and open their sterile field (BeanPostProcessor before-init + @PostConstruct). They then perform operations (bean in use). When the shift ends, they complete post-op notes and sterilise instruments (@PreDestroy). If they leave without cleanup, the next shift inherits chaos — just like a bean that doesn't clean up its resources.

"Surgeon arriving and credentialing" = constructor + Aware callbacks
"Receiving briefing and equipment" = dependency injection
"Confirming readiness" = @PostConstruct (safe to use all injected values)
"Performing operations" = bean in active use
"End-of-shift cleanup" = @PreDestroy / DisposableBean

---

### ⚙️ How It Works (Mechanism)

**Complete lifecycle sequence:**

```
┌─────────────────────────────────────────────────────┐
│  SPRING BEAN LIFECYCLE (singleton)                  │
├─────────────────────────────────────────────────────┤
│  1.  Instantiate (invoke constructor)               │
│  2.  Inject dependencies                            │
│      (@Autowired, @Value, constructor params)       │
│  3.  setBeanName() — BeanNameAware                  │
│  4.  setBeanFactory() — BeanFactoryAware            │
│  5.  setApplicationContext() — AppContextAware      │
│  6.  BPP.postProcessBeforeInitialization()          │
│      (pre-init custom processing)                   │
│  7.  @PostConstruct methods                         │
│  8.  InitializingBean.afterPropertiesSet()          │
│  9.  Custom @Bean(initMethod = "init")              │
│  10. BPP.postProcessAfterInitialization()           │
│      ← AOP PROXY CREATED HERE (if @Transactional   │
│         @Async, @Cacheable, @Secured detected)      │
│  11. Bean is ready — stored in context              │
│  ──────────────────────────────────────────         │
│  SHUTDOWN triggered (context.close() / JVM hook)   │
│  12. @PreDestroy methods                            │
│  13. DisposableBean.destroy()                       │
│  14. Custom @Bean(destroyMethod = "cleanup")        │
└─────────────────────────────────────────────────────┘
```

**Three ways to declare init/destroy:**

```java
@Component
public class ConnectionPool implements
    InitializingBean, DisposableBean {

  @PostConstruct  // JSR-250 — preferred (no Spring dep)
  public void init() {
    openConnections(); // runs after all injection done
  }

  @Override
  public void afterPropertiesSet() { // Spring-specific
    // redundant with @PostConstruct — pick one
  }

  @PreDestroy     // preferred
  public void shutdown() {
    closeConnections();
  }

  @Override
  public void destroy() { // Spring-specific
    // redundant with @PreDestroy — pick one
  }
}

// @Bean factory method approach
@Bean(initMethod = "start", destroyMethod = "close")
public ScheduledExecutorService scheduler() {
  return Executors.newScheduledThreadPool(4);
}
```

---

### 🔄 How It Connects (Mini-Map)

```
ApplicationContext.refresh() triggers lifecycle
        ↓
  1. Instantiation + injection
  2. Aware interface callbacks
  3. BEAN LIFECYCLE HOOKS  ← you are here
     BPS.beforeInit → @PostConstruct → BPP.afterInit
        ↓
  BPP.postProcessAfterInitialization
  (AbstractAutoProxyCreator runs here)
        ↓
  AOP PROXY created (CGLIB/JDK)
  BEAN stored in container
        ↓
  Used by application
        ↓
  Shutdown: @PreDestroy → DisposableBean
        ↓
  Context closed
```

---

### 💻 Code Example

**Example 1 — Correct use of @PostConstruct for resource init:**

```java
@Component
public class CacheWarmer {
  private final ProductRepository repo;
  private final CacheManager cacheManager;

  // Injected via constructor — guaranteed present
  public CacheWarmer(ProductRepository repo,
                     CacheManager cacheManager) {
    this.repo         = repo;
    this.cacheManager = cacheManager;
    // DO NOT warm cache here — proxy not yet applied
    // repo may not be fully initialised
  }

  @PostConstruct  // All beans ready, proxy applied — safe
  public void warmCache() {
    log.info("Warming product cache on startup");
    repo.findTopSellers(100)
        .forEach(p -> cacheManager.getCache("products")
                                  .put(p.getId(), p));
  }

  @PreDestroy
  public void flushCache() {
    log.info("Flushing cache on shutdown");
    cacheManager.getCache("products").clear();
  }
}
```

**Example 2 — SmartLifecycle for ordered start/stop:**

```java
// Control start/stop ORDER across beans
@Component
public class KafkaConsumerBean implements SmartLifecycle {
  private boolean running = false;

  @Override
  public void start() {
    // Called by Spring after ALL beans initialised
    // Use getPhase() to order relative to other Lifecycles
    consumer.subscribe(topics);
    this.running = true;
  }

  @Override
  public void stop() {
    // Graceful stop: finish in-flight messages
    consumer.wakeup();
    this.running = false;
  }

  @Override
  public boolean isRunning() { return running; }

  @Override
  public int getPhase() { return Integer.MAX_VALUE; }
  // MAX_VALUE = last to start, first to stop
}
```

**Example 3 — Detecting AOP proxy creation in lifecycle:**

```java
@Service
public class OrderService {
  @PostConstruct
  public void checkProxyStatus() {
    // At @PostConstruct: bean is NOT yet proxied
    // (BPP.postProcessAfterInit hasn't run yet)
    boolean proxied = AopUtils.isAopProxy(this);
    // proxied = false here!
  }
}

// After postProcessAfterInitialization:
// The bean stored in container IS a proxy:
OrderService proxy = ctx.getBean(OrderService.class);
AopUtils.isAopProxy(proxy); // true — proxy wraps original
```

---

### 🔁 Flow / Lifecycle

```
ApplicationContext.refresh()
        ↓
Step 1: new OrderService()          ← constructor
        ↓
Step 2: @Autowired dependencies set ← injection
        ↓
Step 3: setBeanName("orderService") ← BeanNameAware
        ↓
Step 4: setApplicationContext(ctx)  ← AppContextAware
        ↓
Step 5: BPP.postProcessBefore()     ← @CommonAnnotation
        checks for @PostConstruct
        ↓
Step 6: orderService.init()         ← @PostConstruct
        ↓
Step 7: BPP.postProcessAfter()      ← AbstractAutoProxy
        detects @Transactional → creates CGLIB proxy
        ↓
Created: proxy stored in context (replaces original)
════════════════════════════════════
Step 8: App runs / handles requests
════════════════════════════════════
JVM shutdown signal received
        ↓
Step 9: orderService.shutdown()     ← @PreDestroy
        ↓
Step 10: disposableBean.destroy()   ← DisposableBean
        ↓
Context closed
```

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| @PostConstruct is called before dependencies are injected | @PostConstruct runs AFTER all injection is complete — it is specifically designed for post-injection initialisation |
| You must use @PostConstruct — constructor is not enough | For stateless beans, constructor is fine. @PostConstruct is needed when initialisation requires injected dependencies |
| AOP proxies are created during @PostConstruct | Proxies are created AFTER @PostConstruct — in BPP.postProcessAfterInitialization(). Self-calls in @PostConstruct bypass the proxy |
| @PreDestroy is always called | @PreDestroy is called only on graceful shutdown (context.close()). Hard JVM kill (kill -9) skips it. Use JVM shutdown hooks for critical cleanup |
| Prototype beans follow the same lifecycle | Spring manages prototype bean creation and initialisation but NOT destruction. @PreDestroy on prototype beans is NEVER called |

---

### 🔥 Pitfalls in Production

**1. Self-invocation bypassing AOP proxy in @PostConstruct**

```java
@Service
@Transactional  // applied at class level
public class DataMigrationService {
  @PostConstruct
  public void migrate() {
    // BAD: this internal call bypasses the proxy
    // @Transactional has NO effect here during init
    this.runMigration(); // calls the REAL object, not proxy
  }

  public void runMigration() {
    // Expects to run in a transaction — won't!
    repo.deleteAll(); // executes without transaction
  }
}

// GOOD: publish an event or use ApplicationRunner
@Component
public class DataMigrationRunner implements ApplicationRunner {
  @Autowired DataMigrationService service;

  @Override
  public void run(ApplicationArguments args) {
    service.runMigration(); // called via proxy → transactional
  }
}
```

**2. Long-running @PostConstruct blocking startup**

```java
// BAD: slow init in @PostConstruct blocks context refresh
// and all health checks until complete
@PostConstruct
public void init() {
  // Takes 30 seconds — blocks the whole context
  loadAllProductsIntoCache(); // 500K products from DB
}
// Health check returns UP only after 30s
// Kubernetes marks pod NotReady → restarts it

// GOOD: warm cache asynchronously after startup
@EventListener(ApplicationReadyEvent.class)
@Async
public void warmCacheAsync() {
  loadAllProductsIntoCache(); // post-startup async
}
// App ready immediately → Kubernetes marks Ready
```

**3. Prototype bean @PreDestroy never called**

```java
// BAD: expecting @PreDestroy cleanup for prototype beans
@Component
@Scope("prototype")
public class TempFileProcessor {
  @PreDestroy
  public void cleanupTempFiles() {
    // NEVER CALLED for prototype scope!
    tempDir.delete(); // leaked temp files in production
  }
}

// GOOD: manage prototype lifecycle explicitly
@Service
public class ProcessingOrchestrator {
  @Autowired
  private ObjectProvider<TempFileProcessor> processorProvider;

  public void process() {
    TempFileProcessor p = processorProvider.getObject();
    try {
      p.process();
    } finally {
      p.cleanupTempFiles(); // explicit cleanup
    }
  }
}
```

---

### 🔗 Related Keywords

- `Bean` — the subject of the lifecycle; every managed bean passes through these phases
- `ApplicationContext` — orchestrates the entire lifecycle sequence at startup and shutdown
- `BeanPostProcessor` — intercepts beans at pre-init and post-init phases (AOP proxy creation)
- `@Transactional` — applied via AOP proxy created in postProcessAfterInitialization
- `SmartLifecycle` — extends lifecycle with ordered start/stop control (for Kafka, schedulers)
- `@PostConstruct` — JSR-250 annotation for post-injection initialisation; preferred over InitializingBean

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ KEY IDEA     │ Ordered phases: new → inject → @PostCons  │
│              │ → BPP proxy → use → @PreDestroy → destroy │
├──────────────┼───────────────────────────────────────────┤
│ USE WHEN     │ Resource init after injection (@PostCons); │
│              │ cleanup on shutdown (@PreDestroy)          │
├──────────────┼───────────────────────────────────────────┤
│ AVOID WHEN   │ Long sync work in @PostConstruct (blocks  │
│              │ startup); relying on @PreDestroy for proto │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "Injection first, then init —             │
│              │  the proxy wraps after both."             │
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ BeanPostProcessor → AOP Proxy → Spring AOP│
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** A `BeanPostProcessor` implementation scans for `@Encrypt` annotations on service methods and wraps qualifying beans in a CGLIB proxy that encrypts return values. Write out the exact ordering problem that occurs if the `BeanPostProcessor` itself has an `@Autowired` dependency on a `@Service` bean — explain what Spring's "BeanPostProcessorChecker" warning means, why the targeted `@Service` bean could be created without the `@Encrypt` proxy applied, and what the correct solution is to avoid this ordering race.

**Q2.** Spring's `AbstractAutoProxyCreator` creates CGLIB proxies in `postProcessAfterInitialization`. This means the bean stored in the context is a **subclass proxy**, not the original class. Trace what happens when code calls `ctx.getBean(OrderService.class)` — explain whether it gets the proxy or original, what `AopUtils.getTargetClass(proxy)` does, and describe the specific serialisation scenario where CGLIB proxy classes cause `ClassCastException` or failed deserialization in a distributed cache.

