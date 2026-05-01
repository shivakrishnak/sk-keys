---
layout: default
title: "CGLIB Proxy"
parent: "Spring Core"
nav_order: 384
permalink: /spring/cglib-proxy/
number: "384"
category: Spring Core
difficulty: ★★★
depends_on: "Bean Lifecycle, AOP (Aspect-Oriented Programming), BeanPostProcessor, @Configuration / @Bean"
used_by: "AOP (Aspect-Oriented Programming), @Transactional, Circular Dependency, Bean Scope"
tags: #advanced, #spring, #internals, #jvm, #deep-dive
---

# 384 — CGLIB Proxy

`#advanced` `#spring` `#internals` `#jvm` `#deep-dive`

⚡ TL;DR — A **CGLIB proxy** is a runtime-generated subclass of a target class that intercepts method calls to apply Spring's AOP advice (`@Transactional`, `@Cacheable`, `@Async`). It is used when the target class does not implement an interface.

| #384            | Category: Spring Core                                                                        | Difficulty: ★★★ |
| :-------------- | :------------------------------------------------------------------------------------------- | :-------------- |
| **Depends on:** | Bean Lifecycle, AOP (Aspect-Oriented Programming), BeanPostProcessor, @Configuration / @Bean |                 |
| **Used by:**    | AOP (Aspect-Oriented Programming), @Transactional, Circular Dependency, Bean Scope           |                 |

---

### 📘 Textbook Definition

**CGLIB** (Code Generation Library) is a bytecode manipulation library that generates subclasses of Java classes at runtime by extending them and overriding their methods. In Spring, CGLIB proxies are created by `AnnotationAwareAspectJAutoProxyCreator` (a `BeanPostProcessor`) during `postProcessAfterInitialization` for beans that (a) have AOP advice applied (`@Transactional`, `@Cacheable`, `@Async`, or `@Aspect` pointcuts) and (b) do not implement any interface (making JDK dynamic proxying inapplicable). The CGLIB subclass overrides every non-final, non-private method to route calls through a `MethodInterceptor` chain, where Spring's AOP advice logic (e.g., `TransactionInterceptor`) is applied before and after delegation to the real target object. `@Configuration` classes are also CGLIB-proxied to enforce singleton semantics for `@Bean` method calls. Limitations: CGLIB cannot proxy `final` classes or `final`/`private` methods; it requires that the target class has a no-arg constructor accessible to the subclass (or uses `objenesis` to bypass this requirement in modern Spring).

---

### 🟢 Simple Definition (Easy)

CGLIB Proxy is a Spring-generated subclass of your class that intercepts every method call, applies cross-cutting logic (like starting a transaction), then calls your real code.

---

### 🔵 Simple Definition (Elaborated)

Spring adds behaviour to your beans — transactions, caching, async execution — without you writing that code in every class. The mechanism is a proxy: Spring generates a new class at runtime that extends your class, overrides all your public methods, and wraps each call with the extra behaviour. When `@Transactional void save(Order o)` is called through the proxy, the proxy's override starts a transaction, calls the real `save()` in the original class, then commits or rolls back. The original object is untouched. CGLIB does this at the bytecode level by subclassing — it works even if your class does not implement an interface (unlike JDK dynamic proxies which require interfaces). The trade-off is that `final` classes and methods cannot be subclassed and therefore cannot be CGLIB-proxied.

---

### 🔩 First Principles Explanation

**How CGLIB generates a proxy subclass:**

```java
// Your real class
@Service
class OrderService {
    @Transactional
    public void placeOrder(Order order) {
        // ... save to database
    }

    public Order findOrder(Long id) {
        // ... query database
    }
}

// What CGLIB generates at runtime (conceptual equivalent in Java):
class OrderService$$EnhancerBySpringCGLIB$$abc123 extends OrderService {

    private final OrderService target;         // wrapped original bean
    private final List<MethodInterceptor> interceptors; // advice chain

    @Override
    public void placeOrder(Order order) {
        // Call advice chain (TransactionInterceptor is here)
        MethodInvocation invocation = new ReflectiveMethodInvocation(
            target, placeOrderMethod, new Object[]{order}, interceptors);
        invocation.proceed();
        // TransactionInterceptor:
        //   BEGIN TRANSACTION
        //   → target.placeOrder(order)  ← real method
        //   COMMIT / ROLLBACK
    }

    @Override
    public Order findOrder(Long id) {
        // No interceptors for this method → direct delegation
        return target.findOrder(id);
    }

    // final methods and private methods: NOT overridden → not interceptable
}

// In the ApplicationContext:
//   "orderService" → OrderService$$EnhancerBySpring...@456 (the proxy)
//   The real OrderService@123 is inside the proxy as 'target'
```

**CGLIB on @Configuration classes — singleton enforcement:**

```java
// Your @Configuration
@Configuration
class AppConfig {
    @Bean ConnectionPool pool() { return new ConnectionPool(10); }
    @Bean RepoA repoA()        { return new RepoA(pool()); } // calls pool()
    @Bean RepoB repoB()        { return new RepoB(pool()); } // calls pool()
}

// CGLIB-generated subclass ensures pool() returns cached singleton:
class AppConfig$$EnhancerByCGLIB extends AppConfig {
    @Override
    ConnectionPool pool() {
        // Check container: "pool" bean already exists?
        if (beanFactory.containsBean("pool")) {
            return (ConnectionPool) beanFactory.getBean("pool"); // cached!
        }
        return super.pool(); // create once, cache it
    }
}
// Result: pool() called multiple times → same instance returned
```

**CGLIB limitations:**

```java
// LIMITATION 1: final class — cannot be subclassed
@Service
final class FinalService {
    @Transactional
    public void save() { ... }
}
// Spring throws: Cannot subclass final class FinalService
// Fix: remove final, or use an interface + JDK proxy

// LIMITATION 2: final method — cannot be overridden
@Service
class PartialService {
    @Transactional
    public final void save() { ... } // final method — CGLIB cannot intercept!
    // @Transactional has NO effect on final methods
    // Spring logs a warning; method runs WITHOUT transaction
}

// LIMITATION 3: private method — not visible to subclass
@Service
class ServiceWithPrivate {
    @Transactional
    private void internalSave() { ... } // CGLIB cannot override private
    // @Transactional IGNORED — private methods are not intercepted
}
```

---

### ❓ Why Does This Exist (Why Before What)

WITHOUT CGLIB Proxy:

What breaks without it:

1. `@Transactional` on a class that does not implement an interface cannot be enforced — no proxy mechanism.
2. `@Configuration` bean singleton semantics cannot be enforced — calling `@Bean` methods repeatedly creates multiple instances.
3. AOP advice cannot be applied to legacy classes that do not implement interfaces.
4. `@Cacheable`, `@Async`, `@Retryable` cannot be applied to non-interface classes.

WITH CGLIB Proxy:
→ AOP works on any non-final class, regardless of interfaces.
→ `@Configuration` singleton enforcement is transparent — developers don't see the CGLIB detail.
→ Spring can instrument third-party classes (JPA entities, library classes) that don't implement Spring interfaces.
→ Combined with JDK dynamic proxy (for interface-based beans), Spring covers all proxy use cases.

---

### 🧠 Mental Model / Analogy

> Think of CGLIB as a stunt double system for Java classes. A stunt double is hired to stand in for the real actor in dangerous scenes — they look identical, handle the risky part, then hand off to the real actor for the dialogue. The stunt double is literally a physical copy of the actor's appearance (CGLIB generates a bytecode subclass). When AOP advice is needed (the "dangerous scene"), the stunt double (proxy) takes the call, applies the advice (transaction, cache, security check), then delegates to the real actor (original bean) for the actual business logic. Audiences (application code) see the stunt double — they don't know the real actor is backstage.

"Stunt double standing in for the real actor" = CGLIB proxy subclass
"Dangerous scene handling" = AOP advice (transaction, cache, security)
"Handing off to the real actor for dialogue" = calling `target.method()` on the original bean
"Physically identical appearance" = CGLIB generates a class that extends the original
"Actor who can't do stunts" = `final` class — cannot be subclassed by CGLIB

---

### ⚙️ How It Works (Mechanism)

**How Spring decides CGLIB vs JDK dynamic proxy:**

```
AnnotationAwareAspectJAutoProxyCreator.postProcessAfterInitialization(bean):
  1. Does this bean need proxying? (has applicable advice?)
     NO → return bean unchanged
     YES → continue

  2. Does bean implement at least one interface (non-Spring internal)?
     YES → use JDK Dynamic Proxy (creates interface-based proxy)
     NO  → use CGLIB (creates class-based subclass proxy)

  3. Is targetClass forced? (proxyTargetClass = true)
     YES → always use CGLIB, even if interfaces exist

@EnableAspectJAutoProxy(proxyTargetClass = true)
// Forces CGLIB for ALL beans, even interface-based ones
// Spring Boot default: proxyTargetClass = true since Spring Boot 2.x
```

**CGLIB class generation using ASM:**

```
At runtime, CGLIB uses ASM (low-level bytecode manipulation):
  1. Read bytecode of OrderService.class
  2. Generate new class name: OrderService$$EnhancerBySpring...
  3. For each non-final, non-private method:
     → Generate override that calls MethodInterceptor chain
  4. Load generated class into the JVM (ClassLoader)
  5. Instantiate via Objenesis (no-arg constructor not needed)
  6. Store instance in ApplicationContext as "orderService"

Performance note:
  → Class generation happens ONCE per class at startup
  → Runtime overhead: one extra method dispatch per proxied call
  → Not a significant production concern for typical applications
```

---

### 🔄 How It Connects (Mini-Map)

```
BeanPostProcessor (phase 6: postProcessAfterInitialization)
        │
        ▼
AnnotationAwareAspectJAutoProxyCreator
(decides whether to proxy and which proxy type)
        │
        ├──── no interfaces ──────────► CGLIB Proxy  ◄──── (you are here)
        │                               (subclass-based, intercepts non-final methods)
        │
        └──── has interfaces ─────────► JDK Dynamic Proxy
                                        (interface-based, requires interface)
        │
        ▼
AOP Advice Chain (MethodInterceptor chain)
  TransactionInterceptor → CacheInterceptor → AsyncExecutionInterceptor
        │
        ▼
target.method() ← the real bean method is called here
```

---

### 💻 Code Example

**Verifying that the ApplicationContext holds the proxy, not the original bean:**

```java
@SpringBootApplication
class VerifyProxyApp implements CommandLineRunner {

    @Autowired ApplicationContext ctx;

    @Override
    public void run(String... args) {
        Object service = ctx.getBean("orderService");

        // The bean in context is the CGLIB proxy, not the original class
        System.out.println(service.getClass().getName());
        // Output: com.example.OrderService$$EnhancerBySpringCGLIB$$abc123def

        // Check if it is a Spring proxy
        System.out.println(AopUtils.isAopProxy(service));       // true
        System.out.println(AopUtils.isCglibProxy(service));     // true
        System.out.println(AopUtils.isJdkDynamicProxy(service));// false

        // Unwrap to get the original target
        OrderService target = (OrderService) ((Advised) service).getTargetSource()
                                                                 .getTarget();
        System.out.println(target.getClass().getName());
        // Output: com.example.OrderService (the real bean)
    }
}
```

**Why `@Transactional` fails on `final` methods — and the fix:**

```java
// BAD: final method — CGLIB cannot intercept, @Transactional silently skipped
@Service
class LegacyService {
    @Transactional
    public final void updateInventory(Item item) {
        // NO TRANSACTION — this method is never called through the proxy
        repo.save(item);
    }
}

// GOOD option A: remove final
@Service
class LegacyService {
    @Transactional
    public void updateInventory(Item item) { repo.save(item); }
}

// GOOD option B: extract to interface + JDK proxy
interface InventoryService {
    void updateInventory(Item item);
}
@Service
class LegacyService implements InventoryService {
    @Transactional
    public void updateInventory(Item item) { repo.save(item); }
}
// JDK proxy can intercept interface methods even if the class has final methods
// (provided the intercepted method is declared in the interface)
```

---

### ⚠️ Common Misconceptions

| Misconception                                                 | Reality                                                                                                                                                                                                        |
| ------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| CGLIB proxy and the original bean are the same object         | They are different objects. The CGLIB proxy is a subclass instance. The original bean is stored inside the proxy's `targetSource`. The ApplicationContext holds the proxy; the proxy delegates to the original |
| `@Transactional` on a private method creates a transaction    | Private methods cannot be overridden by CGLIB. Spring cannot intercept them. `@Transactional` on private methods is silently ignored — no transaction is started                                               |
| CGLIB proxy is slower than JDK dynamic proxy                  | Modern benchmarks show negligible difference for typical application method calls. CGLIB subclass dispatch is comparable to JDK interface dispatch. The class generation cost is paid once at startup          |
| Spring always uses JDK dynamic proxy when an interface exists | Spring Boot 2.x+ sets `proxyTargetClass = true` by default, meaning Spring uses CGLIB even when interfaces are present — unless explicitly changed                                                             |

---

### 🔥 Pitfalls in Production

**Kotlin data classes and `final` by default — all methods are final, all AOP silently fails**

```kotlin
// BAD: Kotlin classes are final by default — CGLIB cannot subclass
@Service
class OrderService {  // implicitly final in Kotlin!
    @Transactional
    fun placeOrder(order: Order) { ... } // @Transactional IGNORED
}

// FIX: Use kotlin-spring plugin (open plugin) or annotate explicitly
// In build.gradle.kts:
plugins {
    kotlin("plugin.spring") version "1.9.0" // opens Spring-annotated classes
}

// Or manually:
@Service
open class OrderService {
    @Transactional
    open fun placeOrder(order: Order) { ... } // open = not final → CGLIB works
}
```

---

**Casting proxy to concrete class causes ClassCastException when proxyTargetClass = false:**

```java
// In a configuration with proxyTargetClass = false (JDK proxy mode)
OrderService svc = ctx.getBean("orderService");
// svc is actually a JDK proxy implementing the interface — not OrderService
OrderServiceImpl impl = (OrderServiceImpl) svc; // ClassCastException!

// GOOD: always reference by interface type
OrderService svc = ctx.getBean(OrderService.class); // by interface — safe
// Or use proxyTargetClass = true (default in Spring Boot) to get CGLIB
// where casting to concrete class works
```

---

### 🔗 Related Keywords

- `JDK Dynamic Proxy` — the alternative proxy mechanism; requires interfaces, generates interface-based proxy
- `AOP (Aspect-Oriented Programming)` — the paradigm that requires proxy generation; CGLIB is the implementation
- `BeanPostProcessor` — `AnnotationAwareAspectJAutoProxyCreator` creates CGLIB proxies in Phase 6
- `@Configuration / @Bean` — CGLIB proxies `@Configuration` classes to enforce singleton `@Bean` semantics
- `Circular Dependency` — CGLIB proxy creation timing (phase 6) is why early references in circular deps miss the proxy
- `Weaving` — the act of applying AOP advice; CGLIB implements runtime weaving via subclass proxy

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ MECHANISM    │ Subclass generated at runtime via ASM     │
│              │ Overrides non-final, non-private methods  │
├──────────────┼───────────────────────────────────────────┤
│ USED WHEN    │ Bean has no interface, or                 │
│              │ proxyTargetClass=true (Spring Boot default)│
├──────────────┼───────────────────────────────────────────┤
│ LIMITATIONS  │ Cannot proxy: final classes, final/private│
│              │ methods → @Transactional silently skipped │
├──────────────┼───────────────────────────────────────────┤
│ @CONFIG USE  │ CGLIB ensures @Bean method singleton      │
│              │ semantics inside @Configuration classes   │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "CGLIB = stunt double that handles the    │
│              │  risky advice, then calls the real actor."│
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** Spring Boot's default `proxyTargetClass = true` means all beans are CGLIB-proxied even when they implement interfaces. This was changed from the original Spring default (`proxyTargetClass = false`, JDK proxy). Explain the specific Spring Boot use case that motivated this change: why does Spring Boot's auto-configuration for `@Transactional` and `@Cacheable` work better with CGLIB proxies? Describe the `ClassCastException` scenario that occurs with JDK proxies when `@Autowired` expects the concrete class type rather than the interface type. And explain why `@SpringBootTest` with `@MockBean` may behave differently depending on whether CGLIB or JDK proxy is used.

**Q2.** CGLIB uses `Objenesis` to instantiate proxy subclasses without calling a constructor. Before `Objenesis` was integrated, all CGLIB-proxied classes required a no-arg constructor. Explain why requiring a no-arg constructor was problematic for classes using constructor injection (which ideally have no no-arg constructor). Describe how `Objenesis` bypasses constructor invocation at the JVM level (via `sun.misc.Unsafe` or `ReflectionFactory`), and identify the risk: if a proxy subclass is created without calling the constructor, what state is the proxy's own fields in? Why does this not matter for Spring's AOP proxy use case?
