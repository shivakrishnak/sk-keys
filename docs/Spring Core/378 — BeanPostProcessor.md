---
layout: default
title: "BeanPostProcessor"
parent: "Spring Core"
nav_order: 378
permalink: /spring/beanpostprocessor/
number: "378"
category: Spring Core
difficulty: ★★★
depends_on: Bean Lifecycle, Bean, ApplicationContext
used_by: AOP, @Transactional, @Autowired, Bean Lifecycle
tags: #advanced, #spring, #internals, #deep-dive
---

# 378 — BeanPostProcessor

`#advanced` `#spring` `#internals` `#deep-dive`

⚡ TL;DR — A **BeanPostProcessor** is a Spring extension point that intercepts every bean after instantiation — allowing you to inspect, wrap, or replace it before and after its initialisation method runs. AOP proxy creation is implemented as a BeanPostProcessor.

| #378            | Category: Spring Core                           | Difficulty: ★★★ |
| :-------------- | :---------------------------------------------- | :-------------- |
| **Depends on:** | Bean Lifecycle, Bean, ApplicationContext        |                 |
| **Used by:**    | AOP, @Transactional, @Autowired, Bean Lifecycle |                 |

---

### 📘 Textbook Definition

A **BeanPostProcessor** is a Spring container extension point that operates on _bean instances_ after they are created. It defines two callback methods: `postProcessBeforeInitialization(Object bean, String beanName)` — called after dependency injection but before the init method (`@PostConstruct` / `InitializingBean.afterPropertiesSet()`), and `postProcessAfterInitialization(Object bean, String beanName)` — called after the init method. Any registered `BeanPostProcessor` is called for every bean in the container. BeanPostProcessors can return the original bean, a modified bean, or a completely different object (typically an AOP proxy). The entire `@Autowired` processing, `@PostConstruct` / `@PreDestroy` processing, and AOP proxy creation in Spring are all implemented as `BeanPostProcessor` implementations: `AutowiredAnnotationBeanPostProcessor`, `CommonAnnotationBeanPostProcessor`, and `AnnotationAwareAspectJAutoProxyCreator` respectively. BeanPostProcessors are distinct from `BeanFactoryPostProcessor` (which operates on bean _definitions_, not instances).

---

### 🟢 Simple Definition (Easy)

A BeanPostProcessor is a plugin you write that Spring calls on every bean it creates, letting you inspect or modify beans right after they are built — before and after their setup methods run.

---

### 🔵 Simple Definition (Elaborated)

Imagine Spring creates 300 beans at startup. For each one, before it is handed to the application, Spring runs every registered BeanPostProcessor against it. The processor receives the bean instance and its name and can: do nothing and return it unchanged, add behaviour (wrap it in a proxy that adds logging), or replace it entirely with a different object. This is the mechanism Spring itself uses internally for almost everything important: `@Autowired` injection, `@PostConstruct` callback processing, AOP proxy creation for `@Transactional`, and validation annotations. You can write your own BeanPostProcessor to implement cross-cutting concerns without modifying any bean class — for example, automatically adding metrics to all services that implement a certain interface.

---

### 🔩 First Principles Explanation

**The interface:**

```java
public interface BeanPostProcessor {
    // Called AFTER injection, BEFORE init method (@PostConstruct)
    @Nullable
    default Object postProcessBeforeInitialization(Object bean, String beanName)
            throws BeansException {
        return bean; // return the bean unchanged (default)
    }

    // Called AFTER init method — AOP proxy creation happens here
    @Nullable
    default Object postProcessAfterInitialization(Object bean, String beanName)
            throws BeansException {
        return bean; // return the bean (or a proxy)
    }
}
```

**The full lifecycle showing exactly where BeanPostProcessor fits:**

```
 construct → inject deps → Aware callbacks
      ↓
 [ ALL BPPs ] postProcessBeforeInitialization()
      ↓
 @PostConstruct / afterPropertiesSet()  ← init method
      ↓
 [ ALL BPPs ] postProcessAfterInitialization()  ← proxy created here
      ↓
 Bean is READY (may be the proxy, not the original object)
```

**Spring's built-in BeanPostProcessors — what they do:**

```
AutowiredAnnotationBeanPostProcessor
  → Processes @Autowired, @Value, @Inject annotations
  → Called in postProcessBeforeInitialization
  → Injects dependencies into @Autowired fields

CommonAnnotationBeanPostProcessor
  → Processes @PostConstruct, @PreDestroy, @Resource
  → Calls @PostConstruct methods in postProcessBeforeInitialization
  → Registers @PreDestroy for later execution

AnnotationAwareAspectJAutoProxyCreator  ← the most important one
  → Processes @Transactional, @Cacheable, @Async, @Aspect
  → Called in postProcessAfterInitialization
  → Wraps bean in CGLIB or JDK proxy if any advice applies
  → Returns the PROXY — the original bean is stored inside it
```

---

### ❓ Why Does This Exist (Why Before What)

WITHOUT BeanPostProcessor:

What breaks without it:

1. No way to apply cross-cutting behaviour to beans without modifying each bean class.
2. `@Autowired`, `@PostConstruct`, `@PreDestroy` would have to be hardcoded into the container — no pluggability.
3. AOP proxy creation would require compile-time weaving or special inheritance — no runtime proxy transparency.
4. Framework extensions (Hibernate validation, Spring Security method security) could not hook into the bean lifecycle.

WITH BeanPostProcessor:
→ All annotation processing is delegated to pluggable processors — Spring's own code uses the same extension point you use.
→ AOP proxies are created transparently at the right lifecycle phase (after init, before ready).
→ Third-party frameworks can register BeanPostProcessors to instrument beans without Spring code changes.
→ The factory is open for extension, closed for modification.

---

### 🧠 Mental Model / Analogy

> Think of an assembly line quality-control checkpoint. Each product (bean) rolls off the manufacturing line. Before it is packaged (before init), quality control inspectors (BeanPostProcessors) check it and can add features or corrections. After final assembly (after init), a second set of inspectors can wrap it in protective packaging (AOP proxy) before shipping it to customers (the application). Every single product goes through every checkpoint — no bean escapes BeanPostProcessor processing.

"Quality-control checkpoint before packaging" = `postProcessBeforeInitialization`
"Second inspector wrapping in packaging" = `postProcessAfterInitialization` (AOP proxy)
"Protective packaging" = the AOP proxy that wraps the real bean
"Every product goes through every checkpoint" = all registered BPPs run for every bean

---

### ⚙️ How It Works (Mechanism)

**How Spring manages BeanPostProcessor ordering:**

```
BeanPostProcessors implement PriorityOrdered or Ordered or neither:
  PriorityOrdered BPPs  → registered and run first
    (AutowiredAnnotationBPP, CommonAnnotationBPP)
  Ordered BPPs          → registered and run second
  Unordered BPPs        → registered and run last
    (custom BPPs without Ordered)

Critical invariant:
  BeanPostProcessors are instantiated BEFORE regular beans.
  This means: beans that BeanPostProcessors depend on are
  instantiated early — BEFORE @Transactional wrapping.
  A bean used by a BPP will NOT have its AOP proxy created
  in time → beans like this should not use @Transactional.
```

**What happens when `postProcessAfterInitialization` returns a proxy:**

```
Before BPP.postProcessAfterInitialization:
  ApplicationContext registry: "orderService" → OrderService@123 (raw bean)

BPP (AnnotationAwareAspectJAutoProxyCreator) runs:
  OrderService has @Transactional methods?  YES
  → Create CGLIB subclass proxy wrapping OrderService@123
  → Proxy intercepts method calls, applies TransactionInterceptor
  → Return proxy OrderServiceProxy@456

After BPP.postProcessAfterInitialization:
  ApplicationContext registry: "orderService" → OrderServiceProxy@456 (proxy)
  OrderService@123 is stored INSIDE the proxy, not in the context

When code injects OrderService:
  Gets OrderServiceProxy@456 — proxy is transparent (same interface)
  Calls proxy.createOrder() → TransactionInterceptor begins transaction
                            → delegates to OrderService@123.createOrder()
                            → TransactionInterceptor commits/rolls back
```

---

### 🔄 How It Connects (Mini-Map)

```
Bean Lifecycle (phases 4 and 6)
        │
        ▼
BeanPostProcessor  ◄──── (you are here)
(instance-level hooks: before and after init)
        │
        ├──── postProcessBeforeInit ──► @Autowired injection
        │                               @PostConstruct processing
        │
        └──── postProcessAfterInit  ──► AOP Proxy creation
                                        (@Transactional, @Cacheable, @Async)
                                                │
                                                ▼
                                        CGLIB Proxy / JDK Dynamic Proxy
                                        (the proxy returned to application)
        │
        ▼
BeanFactoryPostProcessor
(different hook — operates on BeanDefinitions, not instances)
```

---

### 💻 Code Example

**Example 1 — Custom BeanPostProcessor that logs all bean types:**

```java
@Component
public class BeanAuditPostProcessor implements BeanPostProcessor {

    private static final Logger log = LoggerFactory.getLogger(BeanAuditPostProcessor.class);

    @Override
    public Object postProcessBeforeInitialization(Object bean, String beanName)
            throws BeansException {
        log.debug("BEFORE INIT: bean '{}' of type {}", beanName, bean.getClass().getSimpleName());
        return bean; // return unchanged
    }

    @Override
    public Object postProcessAfterInitialization(Object bean, String beanName)
            throws BeansException {
        log.debug("AFTER INIT: bean '{}' final type {} (may be proxy)",
                beanName, bean.getClass().getSimpleName());
        return bean; // return unchanged
    }
}
```

**Example 2 — BeanPostProcessor that wraps services with timing metrics:**

```java
@Component
public class TimingProxyPostProcessor implements BeanPostProcessor {

    @Override
    public Object postProcessAfterInitialization(Object bean, String beanName)
            throws BeansException {
        // Only wrap beans that implement our Monitored marker interface
        if (!(bean instanceof Monitored)) {
            return bean; // pass through unchanged
        }

        return Proxy.newProxyInstance(
            bean.getClass().getClassLoader(),
            bean.getClass().getInterfaces(),
            (proxy, method, args) -> {
                long start = System.nanoTime();
                try {
                    return method.invoke(bean, args);
                } finally {
                    long elapsed = System.nanoTime() - start;
                    Metrics.timer("service." + beanName + "." + method.getName())
                           .record(elapsed, TimeUnit.NANOSECONDS);
                }
            }
        );
    }
}
```

**Example 3 — InstantiationAwareBeanPostProcessor (advanced — intercepts before construction):**

```java
@Component
public class ConditionalBeanPostProcessor
        implements InstantiationAwareBeanPostProcessor {

    @Override
    public Object postProcessBeforeInstantiation(Class<?> beanClass, String beanName)
            throws BeansException {
        // Return non-null to short-circuit default instantiation
        // (WARNING: skips DI, @PostConstruct, etc. — advanced use only)
        if (beanClass.isAnnotationPresent(MockInTests.class) && isTestContext()) {
            return Mockito.mock(beanClass); // replace real bean with mock
        }
        return null; // proceed with normal instantiation
    }
}
```

---

### 🔁 Flow / Lifecycle

**BeanPostProcessor registration and execution flow:**

```
APPLICATION CONTEXT REFRESH
           │
           ▼
  1. Register BeanPostProcessors FIRST
     (PriorityOrdered → Ordered → rest)
           │
           ▼
  2. For each regular bean:
     a. Instantiate (constructor)
     b. Inject dependencies
     c. Run Aware callbacks
           │
           ▼
  3. For each registered BPP in order:
     → BPP.postProcessBeforeInitialization(bean, name)
           │
           ▼
  4. Run init method (@PostConstruct / afterPropertiesSet)
           │
           ▼
  5. For each registered BPP in order:
     → BPP.postProcessAfterInitialization(bean, name)
     ← returns: original bean OR proxy
           │
           ▼
  6. Store result in ApplicationContext
     (may be proxy, not original bean)
```

---

### ⚠️ Common Misconceptions

| Misconception                                                                  | Reality                                                                                                                                                                                                                                                                               |
| ------------------------------------------------------------------------------ | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| BeanPostProcessor only runs on custom beans                                    | BPPs run on EVERY bean in the context — including Spring's own infrastructure beans (unless specifically excluded). This is why the order of BPP registration matters                                                                                                                 |
| BeanPostProcessor and BeanFactoryPostProcessor are the same thing              | BeanPostProcessor runs on bean INSTANCES after creation (phases 4 and 6 of lifecycle). BeanFactoryPostProcessor runs on bean DEFINITIONS before any beans are created — completely different phase and purpose                                                                        |
| If a BeanPostProcessor replaces a bean with a proxy, the original bean is gone | The original bean instance is NOT discarded — it is stored inside the proxy as the "target." The proxy delegates all method calls to it. AOP advice wraps around the target, it does not replace it                                                                                   |
| You can safely inject regular beans into a BeanPostProcessor                   | BeanPostProcessors are instantiated very early, before the main bean lifecycle. Beans they depend on skip the normal proxy-creation phase, so injected beans may not have `@Transactional` or other AOP advice applied. Use `@Lazy` injection or `ObjectProvider` to defer resolution |

---

### 🔥 Pitfalls in Production

**BeanPostProcessor that depends on a `@Transactional` bean — proxy not applied**

```java
// BAD: BPP injects a regular service bean
@Component
class SecurityBeanPostProcessor implements BeanPostProcessor {
    @Autowired
    AuditService auditService; // instantiated early, BEFORE AnnotationAwareAspectJAutoProxyCreator
    // auditService will NOT have @Transactional proxy applied!
    // Spring logs a warning: "AuditService is not eligible for proxy creation"

    @Override
    public Object postProcessAfterInitialization(Object bean, String beanName) {
        auditService.logBeanCreation(beanName); // runs without transaction
        return bean;
    }
}

// GOOD: use @Lazy or ObjectProvider to defer auditService resolution
@Component
class SecurityBeanPostProcessor implements BeanPostProcessor {
    @Autowired
    ObjectProvider<AuditService> auditServiceProvider; // deferred resolution

    @Override
    public Object postProcessAfterInitialization(Object bean, String beanName) {
        auditServiceProvider.ifAvailable(svc -> svc.logBeanCreation(beanName));
        return bean;
    }
}
```

---

### 🔗 Related Keywords

- `Bean Lifecycle` — defines the phases where BeanPostProcessor callbacks are invoked (phases 4 and 6)
- `BeanFactoryPostProcessor` — sibling concept; operates on bean definitions before instance creation
- `AOP (Aspect-Oriented Programming)` — implemented via BeanPostProcessor; proxies created in `postProcessAfterInitialization`
- `CGLIB Proxy` — the proxy type used by `AnnotationAwareAspectJAutoProxyCreator` for class-based proxying
- `@Autowired` — processed by `AutowiredAnnotationBeanPostProcessor` in `postProcessBeforeInitialization`
- `@PostConstruct` — processed by `CommonAnnotationBeanPostProcessor` in `postProcessBeforeInitialization`

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ INTERFACE    │ postProcessBeforeInitialization()         │
│              │ postProcessAfterInitialization()          │
├──────────────┼───────────────────────────────────────────┤
│ TIMING       │ Before: after inject, before @PostConstruct│
│              │ After:  after @PostConstruct — AOP proxy  │
├──────────────┼───────────────────────────────────────────┤
│ BUILT-IN BPPs│ AutowiredAnnotationBPP → @Autowired       │
│              │ CommonAnnotationBPP    → @PostConstruct   │
│              │ AspectJAutoProxyCreator→ AOP proxies      │
├──────────────┼───────────────────────────────────────────┤
│ KEY RISK     │ BPP dependencies instantiated early —     │
│              │ their @Transactional proxy not applied    │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "BeanPostProcessor = QC inspector:        │
│              │ every bean passes through every inspector  │
│              │ before going to production."              │
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** You write a `BeanPostProcessor` that returns a JDK dynamic proxy from `postProcessAfterInitialization` for all beans implementing `Service`. Later, another `@Aspect` in the application also wants to apply advice to those same beans. Explain the interaction: what does `AnnotationAwareAspectJAutoProxyCreator` see when it processes a bean that your BPP already replaced with a JDK proxy? Will the Aspect's advice be applied to the original bean or the JDK proxy? Does the order of BPP registration matter? And what is the risk of double-proxying?

**Q2.** `SmartInstantiationAwareBeanPostProcessor.predictBeanType()` is called by Spring to resolve circular dependency candidate types before full instantiation. Explain the specific circular dependency scenario where this method is critical: if Bean A (a singleton) depends on Bean B (which has `@Transactional`), and Bean B depends on Bean A, describe the exact order of events Spring uses to resolve this circular dependency using the "early exposure" mechanism (`ObjectFactory` in the `singletonFactories` map), explain why this early-exposed reference is the RAW bean (not the proxy), and identify the risk this creates for the `@Transactional` proxy on Bean B when it is injected into Bean A.
