---
layout: default
title: "CGLIB Proxy"
parent: "Spring Core"
nav_order: 384
permalink: /spring/cglib-proxy/
number: "384"
category: Spring Core
difficulty: ★★★
depends_on: "AOP, Bean Lifecycle, BeanPostProcessor, Bytecode, Inheritance"
used_by: "@Transactional, @Async, @Cacheable, Spring AOP, @Configuration"
tags: #java, #spring, #internals, #advanced, #deep-dive, #performance
---

# 384 — CGLIB Proxy

`#java` `#spring` `#internals` `#advanced` `#deep-dive` `#performance`

⚡ TL;DR — A runtime-generated subclass proxy that intercepts method calls by extending the target class via bytecode generation — Spring's default proxy mechanism for classes without interfaces.

| #384 | category: Spring Core
|:---|:---|:---|
| **Depends on:** | AOP, Bean Lifecycle, BeanPostProcessor, Bytecode, Inheritance | |
| **Used by:** | @Transactional, @Async, @Cacheable, Spring AOP, @Configuration | |

---

### 📘 Textbook Definition

**CGLIB (Code Generation Library) Proxy** is a bytecode manipulation library that generates a subclass of a target class at runtime. Spring uses CGLIB to create AOP proxies for beans that do not implement interfaces (or when `@EnableAspectJAutoProxy(proxyTargetClass = true)` is set). The generated subclass overrides all non-`final`, non-`private` methods, inserting interceptor chains before and after each. CGLIB is bundled into `spring-core` since Spring 3.2. CGLIB proxies carry notable constraints: the proxied class must not be `final`, advised methods must not be `final`, and the class must have a no-argument constructor accessible to the proxy generator (or use objenesis to bypass this).

---

### 🟢 Simple Definition (Easy)

A CGLIB proxy is a child class that Spring generates automatically at runtime. It looks exactly like your class but intercepts every method call to apply cross-cutting concerns like transactions and caching — before passing the call through to your real code.

---

### 🔵 Simple Definition (Elaborated)

When you add `@Transactional` to a service class, Spring doesn't change your source code. Instead, at startup, it generates a new subclass of your service class using CGLIB. This subclass overrides all your methods: when code calls `orderService.place(order)`, it silently goes through the generated subclass first, which opens a transaction, calls your real `place(order)` method, then commits or rolls back. Your application code sees only the interface — it doesn't know a subclass is involved. This is different from JDK dynamic proxies, which require an interface — CGLIB works on any class.

---

### 🔩 First Principles Explanation

**The problem — adding behaviour without modifying source:**

Cross-cutting concerns (transactions, security checks, caching, audit logging) need to wrap every relevant method. Without a proxy mechanism:

```java
// Manual approach — boilerplate in every method
public Order place(OrderRequest req) {
  TransactionStatus tx = tm.getTransaction(...);
  try {
    securityCheck(); // every method needs this
    Order o = doPlace(req);
    tm.commit(tx);
    return o;
  } catch (Exception e) {
    tm.rollback(tx);
    throw e;
  }
}
```

**The CGLIB solution — generate a subclass at runtime:**

```
Your class:          CGLIB generates at runtime:
──────────────────   ──────────────────────────────────
OrderService         OrderService$$SpringCGLIB$$0
  place(req)   →       override place(req) {
               →         interceptorChain.invoke(
               →           "place", args,
               →           target::place); }
               →       override cancel(id) {
               →         interceptorChain.invoke(...)
               →       }
```

**CGLIB bytecode generation process:**

```
┌─────────────────────────────────────────────────────┐
│  CGLIB PROXY CREATION (in BPP.postProcessAfterInit) │
│                                                     │
│  1. AbstractAutoProxyCreator examines bean          │
│  2. Checks for applicable advisors (@Transactional, │
│     @Aspect, etc.)                                  │
│  3. Decides: JDK proxy (has interface) or CGLIB     │
│     @EnableAspectJAutoProxy(proxyTargetClass=true)  │
│     → always CGLIB                                  │
│  4. CGLIB generates OrderService$$SpringCGLIB$$0    │
│     (written to off-heap or memory in JDK17+)       │
│  5. Proxy registered in ApplicationContext          │
│  6. All injections now receive the proxy            │
└─────────────────────────────────────────────────────┘
```

---

### ❓ Why Does This Exist (Why Before What)

**WITHOUT proxy mechanism:**

```
Without CGLIB (or any proxy):

  @Transactional is a marker only:
    No code wraps method calls → no transaction opened
    → Data corruption: multiple ops without atomicity

  AOP impossible for concrete classes:
    JDK dynamic proxies require interfaces
    → Most Spring service classes have no interface
    → AOP would be unusable for 80% of real beans

  Bytecode modification at compile time:
    AspectJ compile-time weaving requires build tooling
    → Every project needs AspectJ compiler integration
    → No runtime adaptability
```

**WITH CGLIB proxy:**

```
→ @Transactional, @Async, @Cacheable work on ANY class
→ No interface required
→ Zero source code changes needed
→ Runtime flexibility: add/remove aspects dynamically
→ @Configuration CGLIB proxy ensures singleton @Bean
→ Works with Spring Boot auto-configuration out-of-box
```

---

### 🧠 Mental Model / Analogy

> A CGLIB proxy is like a **celebrity body double** who intercepts all public appearances. The body double wears the same costume, has the same name, and looks identical. Before every appearance, the body double checks security clearance (security advice), walks the red carpet procedure (before-advice), then calls the real celebrity for the main event. After the event, the body double handles the press (after-advice). Audience members see only "the celebrity" — they don't know they're interacting with the body double most of the time.

"Body double identical appearance" = proxy class extends real class
"Intercepting all appearances" = overriding all public methods
"Security check before event" = @Secured / @PreAuthorize advice
"Main event delegated to real celebrity" = method invocation on target
"After-event press handling" = @AfterReturning / commit transaction

---

### ⚙️ How It Works (Mechanism)

**CGLIB proxy structure:**

```java
// Generated at runtime — conceptual equivalen:
class OrderService$$SpringCGLIB$$0 extends OrderService {
  private MethodInterceptor[] interceptors;
  private OrderService target;

  @Override
  public Order place(OrderRequest req) {
    // Interceptor chain: security → retry → transaction
    return interceptors[i].intercept(
        this, placeMethod, new Object[]{req}, proxy);
  }
}

// The interceptor for @Transactional:
class TransactionInterceptor implements MethodInterceptor {
  public Object invoke(MethodInvocation inv) throws Throwable {
    TransactionStatus tx = tm.getTransaction(txAttr);
    try {
      Object result = inv.proceed(); // calls real method
      tm.commit(tx);
      return result;
    } catch (Throwable ex) {
      tm.rollback(tx);
      throw ex;
    }
  }
}
```

**CGLIB vs JDK Dynamic Proxy selection:**

```
CGLIB PROXY used when:
  → Bean class does NOT implement target interface
  → @EnableAspectJAutoProxy(proxyTargetClass = true)
  → @SpringBootApplication (Spring Boot default)
  → @Configuration classes (always CGLIB-enhanced)

JDK DYNAMIC PROXY used when:
  → Bean implements at least one interface
  → proxyTargetClass = false (Spring default pre-Boot)
  → Injection point uses the interface type
```

**Constraints — what CGLIB cannot proxy:**

```java
// FAILS: final class cannot be subclassed
@Service
public final class OrderService { // Cannot proxy!
  @Transactional
  public Order place(OrderRequest req) {...}
}

// FAILS: final method cannot be overridden
@Service
public class OrderService {
  @Transactional
  public final Order place(OrderRequest req) {...} // No proxy!
}

// FAILS: private method (not eligible for interception)
@Service
public class OrderService {
  @Transactional
  private Order internalPlace(OrderRequest req) {...} // Ignored
}
```

---

### 🔄 How It Connects (Mini-Map)

```
BeanPostProcessor.postProcessAfterInitialization
        ↓
  AbstractAutoProxyCreator detects @Transactional/@Async
        ↓
  CGLIB PROXY (116)  ← you are here
  (bytecode-generated subclass wrapping the target)
        ↓
  Proxy stored in ApplicationContext (replaces original)
        ↓
  All injection points receive the proxy
  Proxy intercepts all public methods
        ↓
  Interceptor chain applied:
  @Transactional (127) — transaction management
  @Async — executor submission
  @Cacheable — cache lookup/store
  @Secured — security check
```

---

### 💻 Code Example

**Example 1 — Detecting CGLIB proxy at runtime:**

```java
@SpringBootTest
class ProxyDetectionTest {
  @Autowired OrderService orderService;

  @Test
  void shouldBeCglibProxy() {
    // Class name shows CGLIB-generated subclass
    String className = orderService.getClass().getName();
    assertThat(className).contains("$$SpringCGLIB$$");

    // Is it a proxy?
    assertThat(AopUtils.isAopProxy(orderService)).isTrue();
    assertThat(AopUtils.isCglibProxy(orderService)).isTrue();

    // Get the real class (not the proxy class)
    assertThat(AopUtils.getTargetClass(orderService))
        .isEqualTo(OrderService.class);
  }
}
```

**Example 2 — Self-invocation bypassing the proxy:**

```java
@Service
public class OrderService {
  @Transactional
  public void processAll(List<OrderRequest> requests) {
    for (OrderRequest req : requests) {
      this.place(req); // BYPASSES PROXY! 'this' = real object
      // @Transactional on place() has NO EFFECT here
      // All inserts execute in processAll's transaction
    }
  }

  @Transactional(propagation = REQUIRES_NEW)
  public Order place(OrderRequest req) {
    return orderRepo.save(Order.from(req));
    // REQUIRES_NEW never fires — proxy not involved
  }
}

// FIX: self-inject via @Autowired and call through proxy
@Service
public class OrderService {
  @Autowired @Lazy
  private OrderService self; // injects the proxy

  public void processAll(List<OrderRequest> requests) {
    requests.forEach(req -> self.place(req)); // via proxy!
  }
}
```

**Example 3 — Profiling CGLIB proxy creation overhead:**

```bash
# Startup: check how many CGLIB proxies are created
# Enable spring.jmx.enabled and use jconsole
# Or use Spring Boot Actuator:
curl http://localhost:8080/actuator/beans | \
  jq '.contexts[].beans | to_entries[] |
      select(.value.type | contains("CGLIB"))' | wc -l
# Typical Spring Boot app: 20-60 CGLIB proxies
# Each takes ~1-3ms to generate → adds 50-180ms startup
```

---

### 🔁 Flow / Lifecycle

```
1. Bean created (constructor called)
        ↓
2. Dependencies injected
        ↓
3. @PostConstruct called
        ↓
4. BPP.postProcessAfterInitialization
   AbstractAutoProxyCreator checks: needs proxy?
        ↓
5. If yes: CGLIB.Enhancer generates subclass
   Class: OrderService$$SpringCGLIB$$0
        ↓
6. Proxy configured with interceptor chain
        ↓
7. Proxy registered in context (replaces original)
        ↓
8. All @Autowired points receive proxy
        ↓
Method call: orderService.place(req)
  → Interceptor chain fires
  → Before advice (security, transaction begin)
  → Delegate to real OrderService.place(req)
  → After advice (commit/rollback, cache store)
```

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| CGLIB modifies your compiled class files | CGLIB generates a NEW subclass at runtime — your compiled .class files are never modified |
| CGLIB proxy wraps private methods | CGLIB generates a subclass, which can only override non-private, non-static, non-final methods. Private methods are never intercepted |
| All Spring beans are CGLIB proxied | Only beans with applicable AOP advice (@Transactional, @Async, etc.) receive a proxy. Plain @Service with no AOP annotations gets NO proxy |
| CGLIB requires a no-arg constructor | Since Spring 4 + Objenesis, CGLIB no longer requires a default constructor for proxy generation. Objenesis bypasses the constructor entirely |
| CGLIB proxies are slow | CGLIB generates bytecode compiled to machine code by JIT — long-lived proxy instances have negligible overhead. Cost is one-time at startup |

---

### 🔥 Pitfalls in Production

**1. @Transactional not working on final class/method**

```java
// BAD: @Transactional silently ignored on final method
@Service
public class PaymentService {
  @Transactional
  public final Receipt charge(PaymentRequest req) {
    // Final method cannot be overridden by CGLIB
    // @Transactional has NO effect — no exception warning!
    return repo.save(Receipt.from(req));
    // Runs WITHOUT a transaction → data integrity risk
  }
}
// FIX: remove final from methods that use AOP annotations
```

**2. Serialisation of CGLIB proxy classes**

```java
// BAD: trying to cache/serialise CGLIB proxy to Redis
@Service
class SessionCache {
  public void cacheUser(User user) {
    // User is NOT a proxy, this is fine
    redisTemplate.opsForValue().set("user:" + user.getId(),
        user);
  }

  // BAD: caching the service bean itself (which is a proxy)
  redisTemplate.opsForValue().set("svc", orderService);
  // Throws NotSerializableException:
  // OrderService$$SpringCGLIB$$0 is not serializable

  // FIX: never cache beans — cache their data/return values
}
```

---

### 🔗 Related Keywords

- `JDK Dynamic Proxy` — the alternative proxy mechanism for interface-based beans
- `Spring AOP` — uses CGLIB (or JDK) proxies to implement aspect advice
- `BeanPostProcessor` — the phase where CGLIB proxies are created (postProcessAfterInit)
- `@Transactional` — the most commonly encountered use of CGLIB proxies
- `Bean Lifecycle` — proxy creation happens at step 10 of the lifecycle
- `@Configuration` — always CGLIB-enhanced (even without AOP) to ensure singleton @Bean calls

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ KEY IDEA     │ Runtime bytecode subclass that intercepts │
│              │ method calls to apply AOP advice           │
├──────────────┼───────────────────────────────────────────┤
│ USE WHEN     │ Applied automatically by Spring when any  │
│              │ AOP annotation is detected on a bean      │
├──────────────┼───────────────────────────────────────────┤
│ AVOID WHEN   │ Never make adviced methods or classes     │
│              │ final — proxy cannot override them        │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "A body double who handles all public     │
│              │  appearances on your behalf."             │
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ JDK Dynamic Proxy (117) → Spring AOP (118)│
│              │ → @Transactional (127)                    │
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** Spring Boot uses CGLIB for all AOP proxies by default (`proxyTargetClass = true` is the default since Spring Boot 1.x). A grpc service class implements a `BindableService` interface and is also annotated `@Transactional`. Explain whether Spring will use JDK proxy or CGLIB proxy in this case, what the runtime class hierarchy looks like for the proxy, how `instanceof BindableService` behaves on the proxy, and why gRPC's framework code that calls `getClass()` to inspect the service type would fail on the proxy and what the fix is.

**Q2.** CGLIB bypasses the normal constructor when creating proxies (via Objenesis). This means the proxy's superclass (your real bean class) constructor does NOT run when the proxy is created. Explain what consequence this has for beans that have constructor argument validation (`Objects.requireNonNull`), what the proxy's field state is after Objenesis construction, and describe the exact scenario where a unit test creates a bean directly with `new OrderService(null)` to test null handling — and why this test would have DIFFERENT behaviour than the same validation in a Spring context.

