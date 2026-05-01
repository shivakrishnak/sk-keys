---
layout: default
title: "AOP (Aspect-Oriented Programming)"
parent: "Spring Core"
nav_order: 386
permalink: /spring/aop/
number: "386"
category: Spring Core
difficulty: ★★☆
depends_on: "Bean Lifecycle, BeanPostProcessor, CGLIB Proxy, JDK Dynamic Proxy"
used_by: "Aspect, Advice, Pointcut, JoinPoint, Weaving, @Transactional"
tags: #intermediate, #spring, #architecture, #pattern, #deep-dive
---

# 386 — AOP (Aspect-Oriented Programming)

`#intermediate` `#spring` `#architecture` `#pattern` `#deep-dive`

⚡ TL;DR — **AOP** is a programming paradigm that separates cross-cutting concerns (logging, transactions, security, caching) from business logic by defining them in modular units called **Aspects** that are woven into the code at defined join points.

| #386            | Category: Spring Core                                             | Difficulty: ★★☆ |
| :-------------- | :---------------------------------------------------------------- | :-------------- |
| **Depends on:** | Bean Lifecycle, BeanPostProcessor, CGLIB Proxy, JDK Dynamic Proxy |                 |
| **Used by:**    | Aspect, Advice, Pointcut, JoinPoint, Weaving, @Transactional      |                 |

---

### 📘 Textbook Definition

**Aspect-Oriented Programming (AOP)** is a programming paradigm that addresses _cross-cutting concerns_ — behaviours that span multiple modules (logging, security, transaction management, caching, auditing) and cannot be cleanly modularised in OOP. AOP enables these concerns to be defined in a separate, modular unit called an **Aspect**, which specifies _what_ to do (**Advice**), _where_ to apply it (**Pointcut**), and the specific execution point it applies to (**JoinPoint**). Spring AOP is a proxy-based, runtime implementation of AOP that uses CGLIB or JDK dynamic proxies. It supports only **method execution** join points (unlike full AspectJ, which supports field access, constructor calls, and static initializers). Spring AOP is activated via `@EnableAspectJAutoProxy` and uses AspectJ annotation syntax (`@Aspect`, `@Before`, `@After`, `@Around`, `@AfterReturning`, `@AfterThrowing`). Advice is applied by building a chain of `MethodInterceptor` objects that wrap the target method call.

---

### 🟢 Simple Definition (Easy)

AOP lets you add behaviour (logging, security, transactions) to many methods at once without modifying each method — you describe the behaviour once in an Aspect and Spring applies it everywhere it matches.

---

### 🔵 Simple Definition (Elaborated)

Without AOP, every method that needs transaction management must explicitly start and commit transactions, every service call that needs security checks must explicitly check permissions, and every operation that needs logging must have log statements. This is code duplication — the same boilerplate repeated everywhere. AOP extracts this repeated code into a separate class (an Aspect) and attaches it to matching methods automatically. `@Transactional` is the most common example: Spring's `TransactionInterceptor` is an Aspect whose Advice starts transactions and whose Pointcut matches all `@Transactional` methods. You never write transaction boilerplate — it is woven in by Spring at runtime through proxy generation.

---

### 🔩 First Principles Explanation

**The cross-cutting concern problem:**

```java
// WITHOUT AOP: cross-cutting code duplicated everywhere
class OrderService {
    void placeOrder(Order o) {
        log.info("ENTER placeOrder");          // logging
        checkPermission("PLACE_ORDER");         // security
        Transaction tx = txManager.begin();    // transaction
        try {
            orderRepo.save(o);                  // business logic
            tx.commit();
        } catch (Exception e) {
            tx.rollback();
            throw e;
        }
        log.info("EXIT placeOrder");
    }
}

class ProductService {
    void createProduct(Product p) {
        log.info("ENTER createProduct");        // same logging
        checkPermission("CREATE_PRODUCT");      // same security
        Transaction tx = txManager.begin();    // same transaction
        try {
            productRepo.save(p);
            tx.commit();
        } catch (Exception e) { tx.rollback(); throw e; }
        log.info("EXIT createProduct");
    }
}

// WITH AOP: cross-cutting code defined ONCE in Aspects
class OrderService {
    void placeOrder(Order o) {
        orderRepo.save(o); // ONLY business logic — everything else is in Aspects
    }
}
// @Transactional Aspect handles transactions
// LoggingAspect handles entry/exit logging
// SecurityAspect handles permission checks
```

**The five AOP concepts — how they fit together:**

```
┌─────────────────────────────────────────────────────────┐
│  Concept     │  Definition                              │
│─────────────────────────────────────────────────────────│
│  JoinPoint   │  A point in execution that can have      │
│              │  advice applied (e.g., method execution) │
│              │                                          │
│  Pointcut    │  A predicate that matches a set of       │
│              │  JoinPoints (e.g., all @Transactional    │
│              │  methods in com.example.service.*)       │
│              │                                          │
│  Advice      │  What code to execute at matched         │
│              │  JoinPoints (Before, After, Around)      │
│              │                                          │
│  Aspect      │  A module combining Pointcut + Advice    │
│              │  (@Aspect class with @Pointcut and       │
│              │  @Before/@Around/@After methods)         │
│              │                                          │
│  Weaving     │  The process of applying Aspects to      │
│              │  targets (Spring: runtime via proxy)     │
└─────────────────────────────────────────────────────────┘
```

**Spring AOP execution model:**

```
Client call: orderService.placeOrder(order)
    ↓
CGLIB/JDK proxy intercepts the call
    ↓
MethodInterceptor chain:
  1. SecurityInterceptor.invoke()    → check @PreAuthorize
  2. TransactionInterceptor.invoke() → BEGIN TRANSACTION
  3. CachingInterceptor.invoke()     → check cache miss
     ↓
  4. target.placeOrder(order)        ← actual method
     ↓
  3. CachingInterceptor.invoke()     → populate cache
  2. TransactionInterceptor.invoke() → COMMIT
  1. SecurityInterceptor.invoke()    → (post-processing)
    ↓
Return result to client
```

---

### ❓ Why Does This Exist (Why Before What)

WITHOUT AOP:

What breaks without it:

1. Security checks, logging, and transaction management are scattered across every method in the codebase.
2. Adding a new cross-cutting concern requires modifying hundreds of methods — high risk, high effort.
3. Removing or changing a cross-cutting concern is error-prone — must find and update every occurrence.
4. Business logic is obscured by infrastructure code — poor readability and maintainability.

WITH AOP:
→ Each cross-cutting concern is in one place — change `@Transactional` behaviour by changing one interceptor.
→ Adding audit logging to all `@Service` methods requires one Aspect, zero changes to service code.
→ Business logic in service methods is clean — no transaction, security, or logging boilerplate.
→ `@Transactional`, `@Cacheable`, `@PreAuthorize`, `@Async`, `@Retryable` — all standard Spring features implemented as AOP Aspects.

---

### 🧠 Mental Model / Analogy

> Think of AOP as a hotel's automated building management system. Every room (method) has the same standard procedures applied when a guest enters or leaves — heating adjusted, lights switched, minibar restocked. None of this is programmed into each individual room; the building management system (AOP Aspect) defines the policy (Advice) and applies it to all rooms matching a pattern (Pointcut: "all rooms on floors 3–10"). Guests (callers) see only their room; the building's cross-cutting management is transparent. Adding a new standard procedure (e.g., air freshener on checkout) means updating one system policy, not visiting 300 rooms individually.

"Building management system" = the Aspect
"Policy applied when guest enters" = Before advice
"Policy applied when guest leaves" = After advice
"All rooms on floors 3–10" = Pointcut (method matching expression)
"A specific room and moment of entry" = JoinPoint
"Applying policies to rooms automatically" = Weaving

---

### ⚙️ How It Works (Mechanism)

**How @EnableAspectJAutoProxy activates Spring AOP:**

```java
@SpringBootApplication  // includes @EnableAspectJAutoProxy(proxyTargetClass = true)
class App { ... }

// Enables: AnnotationAwareAspectJAutoProxyCreator (a BeanPostProcessor)
// This BPP:
//   1. Scans all @Aspect beans to collect Advisors (Pointcut + Advice pairs)
//   2. For each bean being created (postProcessAfterInitialization):
//      a. Check if any Advisor's Pointcut matches this bean's methods
//      b. If YES → create CGLIB or JDK proxy with MethodInterceptor chain
//      c. If NO  → return bean unchanged
```

**Complete AOP example — method timing aspect:**

```java
@Aspect
@Component
public class PerformanceAspect {

    // Pointcut: any method in any class in com.example.service package
    @Pointcut("execution(* com.example.service.*.*(..))")
    private void serviceLayer() {}

    // Around advice: runs instead of the method, with before and after hooks
    @Around("serviceLayer()")
    public Object measureTime(ProceedingJoinPoint pjp) throws Throwable {
        long start = System.nanoTime();
        String method = pjp.getSignature().toShortString();
        try {
            Object result = pjp.proceed(); // call the real method
            return result;
        } finally {
            long elapsed = (System.nanoTime() - start) / 1_000_000;
            log.info("[PERF] {} completed in {}ms", method, elapsed);
        }
    }
}

// No changes to any service class — timing applied to ALL service methods
```

---

### 🔄 How It Connects (Mini-Map)

```
AOP (Aspect-Oriented Programming)  ◄──── (you are here)
(paradigm: separate cross-cutting concerns)
        │
        ├──── Aspect    (the module: class with @Aspect)
        ├──── Advice    (what: @Before, @After, @Around, etc.)
        ├──── Pointcut  (where: execution expressions)
        ├──── JoinPoint (specific execution point matched)
        └──── Weaving   (process of applying aspects)
                │
                ▼
        Spring AOP runtime
        (proxy-based, method execution only)
                │
                ├──── CGLIB Proxy   (class-based, no interface needed)
                └──── JDK Dynamic Proxy (interface-based)
                │
                ▼
        Built-in Spring AOP features:
        @Transactional, @Cacheable, @Async, @PreAuthorize, @Retryable
```

---

### 💻 Code Example

**Complete Aspect with multiple advice types:**

```java
@Aspect
@Component
@Order(1) // run this aspect before others (lower = higher priority)
public class AuditAspect {

    // Pointcut 1: methods annotated with @Audited (custom annotation)
    @Pointcut("@annotation(com.example.Audited)")
    private void auditedMethod() {}

    // Pointcut 2: all public methods in *Service classes
    @Pointcut("execution(public * com.example..*Service.*(..))")
    private void publicServiceMethod() {}

    // Runs BEFORE the method — captures input
    @Before("auditedMethod()")
    public void logMethodEntry(JoinPoint jp) {
        String method = jp.getSignature().toShortString();
        Object[] args = jp.getArgs();
        auditLog.record("ENTER " + method, args);
    }

    // Runs AFTER method returns normally — captures output
    @AfterReturning(pointcut = "publicServiceMethod()", returning = "result")
    public void logSuccess(JoinPoint jp, Object result) {
        auditLog.recordSuccess(jp.getSignature().getName(), result);
    }

    // Runs if method throws — captures exception
    @AfterThrowing(pointcut = "publicServiceMethod()", throwing = "ex")
    public void logFailure(JoinPoint jp, Exception ex) {
        auditLog.recordFailure(jp.getSignature().getName(), ex.getMessage());
        // NOTE: does NOT suppress the exception — it still propagates
    }

    // @After: runs after method regardless of outcome (like finally)
    @After("auditedMethod()")
    public void logExit(JoinPoint jp) {
        auditLog.recordExit(jp.getSignature().toShortString());
    }
}
```

---

### ⚠️ Common Misconceptions

| Misconception                                             | Reality                                                                                                                                                                                                                       |
| --------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Spring AOP applies advice to all method calls on a bean   | Spring AOP only intercepts calls that go through the proxy. Calls from within the bean (`this.method()`) bypass the proxy and receive no advice. This is the famous "self-invocation problem"                                 |
| AOP works on field access and constructor calls in Spring | Spring AOP supports ONLY method execution join points. Field access, constructor execution, and static initializers require full AspectJ (compile-time or load-time weaving)                                                  |
| `@AfterThrowing` suppresses the exception                 | `@AfterThrowing` advice runs when an exception is thrown but does NOT suppress it — the exception still propagates to the caller. Use `@Around` with a try-catch to suppress exceptions                                       |
| `@Aspect` beans are singleton by default                  | Yes, `@Aspect` classes are Spring beans with default singleton scope. This means any mutable state in an Aspect is shared across all method invocations — stateful Aspects cause race conditions. Aspects should be stateless |

---

### 🔥 Pitfalls in Production

**Self-invocation bypasses the proxy — @Transactional and @Cacheable silently skipped**

```java
@Service
class OrderService {
    // Called from OUTSIDE — goes through proxy — @Transactional WORKS
    public void processAllOrders(List<Order> orders) {
        orders.forEach(this::processOrder); // calls this.processOrder()
    }

    @Transactional // This annotation has NO EFFECT when called via 'this'
    public void processOrder(Order order) {
        // 'this' = raw bean, not proxy
        // No transaction — DB changes not wrapped
        orderRepo.save(order);
    }
}

// Fix: inject self and use the injected reference (which is the proxy)
@Service
class OrderService {
    @Autowired @Lazy
    private OrderService self; // Spring injects the PROXY

    public void processAllOrders(List<Order> orders) {
        orders.forEach(self::processOrder); // goes through proxy — works!
    }

    @Transactional
    public void processOrder(Order order) { ... }
}
```

---

### 🔗 Related Keywords

- `Aspect` — the module that combines Pointcut and Advice definitions
- `Advice` — the code that runs at a matched JoinPoint (Before, After, Around)
- `Pointcut` — the predicate expression that identifies which JoinPoints to match
- `JoinPoint` — the specific method execution instance that advice targets
- `Weaving` — the process of applying Aspects; Spring AOP uses runtime proxy-based weaving
- `CGLIB Proxy` — the proxy type used by Spring AOP for class-based beans
- `@Transactional` — the most common real-world use of Spring AOP

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ PARADIGM     │ Separate cross-cutting concerns           │
│              │ from business logic via Aspects           │
├──────────────┼───────────────────────────────────────────┤
│ SPRING SCOPE │ Method execution only (no field/constructor│
│              │ Full AspectJ needed for those)            │
├──────────────┼───────────────────────────────────────────┤
│ ADVICE TYPES │ @Before, @After, @Around                  │
│              │ @AfterReturning, @AfterThrowing           │
├──────────────┼───────────────────────────────────────────┤
│ SELF-INVOKE  │ this.method() bypasses proxy → no advice  │
│              │ Fix: inject self or extract to new bean   │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "AOP = hotel building management:         │
│              │  define room policies once, apply         │
│              │  transparently to all matching rooms."    │
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** Multiple Aspects can apply to the same method. Spring AOP uses the `@Order` annotation (or `Ordered` interface) on `@Aspect` classes to control the interceptor chain order. Describe the execution model: if `SecurityAspect` (order=1) and `TransactionAspect` (order=2) both apply `@Around` advice to the same method, what is the exact execution sequence? Draw the call stack. Now describe what happens if `SecurityAspect` throws an exception — does `TransactionAspect`'s advice run? Does the transaction get rolled back? And what if `TransactionAspect` runs first and `SecurityAspect` is inner — does the security exception trigger a transaction rollback?

**Q2.** Spring AOP is a "proxy-based" AOP, meaning it can only intercept method calls made through the proxy. Full AspectJ (available via `@EnableLoadTimeWeaving` or compile-time weaving) can intercept field access, constructor calls, and `this()` invocations. Describe two concrete Spring application scenarios where proxy-based AOP is insufficient and requires full AspectJ: one involving `this`-invocation inside the same bean (already mentioned), and one involving a non-Spring-managed object (e.g., a JPA entity or a `new`-created object) that needs `@Configurable` injection. Explain the load-time weaving mechanism that makes `@Configurable` work.
