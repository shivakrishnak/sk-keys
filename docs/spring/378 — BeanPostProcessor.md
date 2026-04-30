---
layout: default
title: "BeanPostProcessor"
parent: "Spring & Spring Boot"
nav_order: 110
permalink: /spring/bean-post-processor/
number: "110"
category: Spring & Spring Boot
difficulty: ★★★
depends_on: Bean Lifecycle, ApplicationContext, AOP Proxy, CGLIB
used_by: Spring AOP, @Transactional, @Async, @Cacheable, Spring Security
tags: #java, #spring, #internals, #advanced, #deep-dive
---

# 110 — BeanPostProcessor

`#java` `#spring` `#internals` `#advanced` `#deep-dive`

⚡ TL;DR — A Spring extension interface that intercepts every bean at two points in its lifecycle — before and after initialisation — enabling annotation processing, proxying, and instrumentation.

| #110 | Category: Spring & Spring Boot | Difficulty: ★★★ |
|:---|:---|:---|
| **Depends on:** | Bean Lifecycle, ApplicationContext, AOP Proxy, CGLIB | |
| **Used by:** | Spring AOP, @Transactional, @Async, @Cacheable, Spring Security | |

---

### 📘 Textbook Definition

`BeanPostProcessor` is a Spring extension interface with two callback methods: `postProcessBeforeInitialization(bean, beanName)` — called after dependency injection but before `@PostConstruct` / `afterPropertiesSet()` — and `postProcessAfterInitialization(bean, beanName)` — called after all initialisation callbacks complete. Implementations can inspect, modify, or replace (wrap in a proxy) any bean. `BeanPostProcessor` beans are created before all other beans, in a special early phase of the ApplicationContext startup. Spring's most critical features — `@Transactional`, `@Async`, `@Cacheable`, `@Scheduled`, Spring Security method security — all work via `BeanPostProcessor` implementations that create CGLIB or JDK proxies in `postProcessAfterInitialization`.

---

### 🟢 Simple Definition (Easy)

A BeanPostProcessor is a "before and after" hook that fires for every bean Spring creates. Before: inspect or modify it. After: wrap it in a proxy. This is how Spring wires in transactions, caching, and security without you writing any proxy code.

---

### 🔵 Simple Definition (Elaborated)

Think of `BeanPostProcessor` as Spring's plugin mechanism for the bean lifecycle. Every time Spring creates a bean — any bean in your application — it runs every registered `BeanPostProcessor` against it. If the processor detects its annotation (e.g. `@Transactional`), it replaces the original bean with a CGLIB proxy. The proxy intercepts every method call, applies the cross-cutting behaviour (open a transaction, check security, hit cache), and delegates to the original bean. None of this requires any changes in your application code — the processor wires it all behind the scenes.

---

### 🔩 First Principles Explanation

**The problem — cross-cutting concerns require boilerplate:**

Without AOP or proxying, every service method that needs a transaction must manually:

```java
// Manual transaction management — repeated everywhere
public Receipt chargeCustomer(Order order) {
  TransactionStatus tx = tm.getTransaction(new DefaultTransactionDef());
  try {
    Receipt r = gateway.charge(order);
    auditRepo.save(new AuditEntry(order, r));
    tm.commit(tx);
    return r;
  } catch (Exception e) {
    tm.rollback(tx);
    throw e;
  }
}
```

Multiply by 50 service methods. Now add security checks, caching, retry logic, metrics recording. The business logic drowns in boilerplate.

**BeanPostProcessor solves this by intercepting at creation time:**

```
┌────────────────────────────────────────────────────────┐
│  BPP EXECUTION MODEL (postProcessAfterInitialization)  │
│                                                        │
│  For each bean in the context:                         │
│    inspect bean for @Transactional annotation          │
│    if found:                                           │
│      create CGLIB subclass proxy                       │
│      proxy intercepts ALL method calls                 │
│      proxy opens/commits/rolls back transactions       │
│      proxy delegates to original bean                  │
│    replace bean in context with proxy                  │
│    return proxy                                        │
│                                                        │
│  Application code calls proxy → gets transaction       │
│  Application code has zero transaction boilerplate     │
└────────────────────────────────────────────────────────┘
```

---

### ❓ Why Does This Exist (Why Before What)

**WITHOUT BeanPostProcessor:**

```
Without BPP extension point:

  @Transactional is just metadata — nothing acts on it
  @Cacheable is just metadata — no caching happens
  @Async is just metadata — no thread pool used
  Spring Security @Secured — no security check applied

  Every cross-cutting concern must be implemented
  manually in every class that needs it:
  → Transaction: 30 lines of boilerplate per method
  → Security: manual SecurityContextHolder checks
  → Caching: manual Map.computeIfAbsent calls

  No way to instrument beans post-creation
  without changing the bean's source code
```

**WITH BeanPostProcessor:**

```
→ @Transactional: add annotation, get transactions
→ @Cacheable: add annotation, get caching
→ @Async: add annotation, get async execution
→ @Secured: add annotation, get security checks

Spring's built-in BPPs:
  AutowiredAnnotationBPP → processes @Autowired
  CommonAnnotationBPP    → processes @PostConstruct
  AbstractAutoProxyCreator → creates AOP proxies
  ScheduledAnnotationBPP → registers @Scheduled tasks
  PersistenceAnnotationBPP → injects @PersistenceContext
```

---

### 🧠 Mental Model / Analogy

> A `BeanPostProcessor` is like a **customs inspection checkpoint** that every person (bean) must pass through when arriving in a country. Before inspection: you verify the person's identity (pre-init customisation). After inspection: you stamp their passport and optionally give them a special jacket (proxy) that lets them transact in the country's economy (transaction management), access restricted areas (security), or move through fast lanes (caching). The person never knows they're wearing a special jacket — but the country's systems do.

"Person arriving" = bean being created
"Before inspection" = postProcessBeforeInitialization
"After inspection" = postProcessAfterInitialization
"Special jacket" = AOP proxy created by BPP
"Country's systems recognising the jacket" = proxy intercepting method calls

---

### ⚙️ How It Works (Mechanism)

**The interface:**

```java
public interface BeanPostProcessor {
  // Called BEFORE init callbacks (@PostConstruct, afterPropertiesSet)
  // Return: modified bean or null (= use original)
  default Object postProcessBeforeInitialization(
      Object bean, String beanName) {
    return bean; // default: pass through unchanged
  }

  // Called AFTER all init callbacks complete
  // Return: modified bean — THIS is where proxies are created
  default Object postProcessAfterInitialization(
      Object bean, String beanName) {
    return bean; // default: pass through unchanged
  }
}
```

**BPP creation order — the special early phase:**

```
┌─────────────────────────────────────────────────────┐
│  BPP INSTANTIATION ORDER (startup)                  │
│                                                     │
│  1. BeanFactoryPostProcessors run first             │
│     (modify bean DEFINITIONS, not instances)        │
│                                                     │
│  2. BeanPostProcessors instantiated NEXT            │
│     (before any regular beans)                      │
│     Reason: BPPs must exist BEFORE beans are created│
│     so they can intercept creation                  │
│                                                     │
│  3. All other singleton beans created               │
│     Each passes through ALL registered BPPs         │
│                                                     │
│  Consequence: beans required by a BPP are created   │
│  EARLY, outside normal BPP processing → may miss   │
│  annotations like @Transactional (BPP ordering bug) │
└─────────────────────────────────────────────────────┘
```

**Writing a custom BeanPostProcessor:**

```java
@Component
public class LoggingBeanPostProcessor
    implements BeanPostProcessor {

  @Override
  public Object postProcessBeforeInitialization(
      Object bean, String name) {
    if (bean.getClass().isAnnotationPresent(Audit.class)) {
      log.debug("Initialising audited bean: {}", name);
    }
    return bean; // unchanged
  }

  @Override
  public Object postProcessAfterInitialization(
      Object bean, String name) {
    if (bean.getClass().isAnnotationPresent(Audit.class)) {
      // Return a proxy that logs every method call
      return Proxy.newProxyInstance(
          bean.getClass().getClassLoader(),
          bean.getClass().getInterfaces(),
          (proxy, method, args) -> {
            log.info("Calling {}.{}", name, method.getName());
            return method.invoke(bean, args);
          });
    }
    return bean;
  }
}
```

---

### 🔄 How It Connects (Mini-Map)

```
Bean created (constructor + injection)
        ↓
  BPP.postProcessBeforeInitialization
  (CommonAnnotationBPP → @PostConstruct prep)
        ↓
  @PostConstruct / afterPropertiesSet()
        ↓
  BPP.postProcessAfterInitialization  ← you are here
  (AbstractAutoProxyCreator runs here)
        ↓
  AOP PROXY created if @Transactional/@Async/@Cacheable
        ↓
  Proxy replaces original in context
        ↓
  Used by: @Transactional (127), @Async,
           @Cacheable, Spring Security
```

---

### 💻 Code Example

**Example 1 — Spring's AbstractAutoProxyCreator in action:**

```java
// Your service
@Service
@Transactional  // detected by AbstractAutoProxyCreator BPP
public class OrderService {
  public Order place(OrderRequest req) {
    // business logic
    return orderRepo.save(Order.from(req));
  }
}

// After BPP processing — what's actually in the context:
OrderService bean = ctx.getBean(OrderService.class);
bean.getClass().getName();
// → "com.example.OrderService$$SpringCGLIB$$0" (proxy!)

// Proxy intercepts place() call:
// 1. Opens transaction
// 2. Calls original OrderService.place(req)
// 3. Commits on success / rolls back on exception
```

**Example 2 — BPP ordering problem (classic pitfall):**

```java
@Component
public class MyBeanPostProcessor implements BeanPostProcessor {
  @Autowired
  AuditService auditService; // regular @Service bean

  // PROBLEM: auditService is created EARLY to satisfy
  // BPP creation → auditService created before
  // AbstractAutoProxyCreator runs → auditService has
  // NO @Transactional proxy!
}
// Spring logs: BeanPostProcessorChecker WARNING
// "AuditService is not eligible for getting processed
//  by all BeanPostProcessors"

// FIX: BPP should not @Autowired regular beans directly
// Use ApplicationContext.getBean() lazily if needed:
@Override
public Object postProcessAfterInitialization(
    Object bean, String name) {
  AuditService svc = beanFactory.getBean(AuditService.class);
  // resolved lazily — fully proxied at this point
}
```

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| BeanPostProcessor runs once at startup | It runs for every singleton bean created — once per bean during context initialisation |
| You can use @Transactional on a BeanPostProcessor | BPPs are created before the AOP infrastructure that implements @Transactional. The annotation is present but the proxy may not be applied |
| BPP only runs for beans with certain annotations | BPP fires for ALL beans — it is up to the implementation to check the bean type/annotations and decide whether to act |
| Returning null from a BPP method is safe | Returning null from postProcessBeforeInitialization is treated as null in the chain — the next BPP receives null. Always return the bean (or your replacement) |

---

### 🔥 Pitfalls in Production

**1. BPP dependency on regular bean — proxy not applied**

```java
// BAD: CachingBPP depends on MetricsService
// → MetricsService created before AOP proxies → no @Transactional
@Component
public class CachingBPP implements BeanPostProcessor {
  @Autowired MetricsService metrics; // created too early!
}

// GOOD: retrieve lazily from BeanFactory after startup
@Component
public class CachingBPP
    implements BeanPostProcessor, BeanFactoryAware {
  private BeanFactory beanFactory;

  @Override
  public void setBeanFactory(BeanFactory bf) {
    this.beanFactory = bf;
  }

  @Override
  public Object postProcessAfterInitialization(
      Object bean, String name) {
    // Lazy get — MetricsService fully proxied by now
    MetricsService m = beanFactory.getBean(MetricsService.class);
    // ...
    return bean;
  }
}
```

**2. Returning wrong type from BPP breaks injection**

```java
// BAD: wrapping changes the interface, breaks @Autowired
@Override
public Object postProcessAfterInitialization(
    Object bean, String name) {
  if (bean instanceof UserService) {
    // Returns Object proxy without UserService interface
    return Proxy.newProxyInstance(
        bean.getClass().getClassLoader(),
        new Class[]{},  // empty interfaces! breaks injection
        handler);
  }
  return bean;
}
// @Autowired UserService — NoSuchBeanDefinitionException

// GOOD: preserve the interfaces
return Proxy.newProxyInstance(
    bean.getClass().getClassLoader(),
    bean.getClass().getInterfaces(), // preserve all
    handler);
```

---

### 🔗 Related Keywords

- `Bean Lifecycle` — BPP fires at steps 6 and 10 of the lifecycle (before and after init callbacks)
- `Spring AOP` — implemented via AbstractAutoProxyCreator, a BeanPostProcessor subclass
- `@Transactional` — enabled by AnnotationTransactionAttributeSource + BPP proxy creation
- `CGLIB Proxy` — the proxy type created by BPP for class-based (non-interface) beans
- `BeanFactoryPostProcessor` — sibling that modifies bean DEFINITIONS before beans are created
- `ApplicationContext` — auto-discovers and registers BPPs from the context

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ KEY IDEA     │ Intercepts every bean before/after init;  │
│              │ can replace bean with proxy — all AOP uses │
│              │ this mechanism                            │
├──────────────┼───────────────────────────────────────────┤
│ USE WHEN     │ Applying cross-cutting behaviour via      │
│              │ annotation scanning; custom proxying      │
├──────────────┼───────────────────────────────────────────┤
│ AVOID WHEN   │ Injecting regular beans into BPP — BPP-  │
│              │ dependent beans won't be fully proxied    │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "BPP is the assembly line inspector —     │
│              │  every bean passes through its hands."    │
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ BeanFactoryPostProcessor (111) →          │
│              │ Spring AOP (118) → @Transactional (127)   │
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** `AbstractAutoProxyCreator` uses a `Map<Object, Boolean>` called `advisedBeans` to track which beans have been processed to avoid double-proxying. If a `BeanPostProcessor` chains with `AbstractAutoProxyCreator` — that is, your custom BPP also wraps beans in a proxy — explain the specific scenario where two layers of CGLIB proxies are created, whether Spring detects and prevents this, and what `AopProxyUtils.ultimateTargetClass()` returns in each case.

**Q2.** Spring Boot Actuator's `/actuator/beans` endpoint lists all beans in the ApplicationContext with their types. When a `@Transactional` bean is listed, it shows the CGLIB proxy class, not the original. Write the exact code you would use in a diagnostic `BeanPostProcessor` to record the mapping of original class → proxy class for all proxied beans at startup, and explain why comparing `bean.getClass()` against `AopUtils.getTargetClass(bean)` is the reliable detection method rather than instanceof checks.

