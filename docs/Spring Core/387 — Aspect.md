---
layout: default
title: "Aspect"
parent: "Spring Core"
nav_order: 387
permalink: /spring/aspect/
number: "387"
category: Spring Core
difficulty: ★★☆
depends_on: "AOP (Aspect-Oriented Programming), Advice, Pointcut, BeanPostProcessor"
used_by: "Advice, Pointcut, JoinPoint, Weaving, @Transactional"
tags: #intermediate, #spring, #architecture, #pattern
---

# 387 — Aspect

`#intermediate` `#spring` `#architecture` `#pattern`

⚡ TL;DR — An **Aspect** is the modular unit of cross-cutting concern in AOP — a class annotated with `@Aspect` that bundles one or more **Pointcut** definitions (where to apply) and **Advice** methods (what to do) into a single, reusable module.

| #387            | Category: Spring Core                                                  | Difficulty: ★★☆ |
| :-------------- | :--------------------------------------------------------------------- | :-------------- |
| **Depends on:** | AOP (Aspect-Oriented Programming), Advice, Pointcut, BeanPostProcessor |                 |
| **Used by:**    | Advice, Pointcut, JoinPoint, Weaving, @Transactional                   |                 |

---

### 📘 Textbook Definition

In Spring AOP, an **Aspect** is a class annotated with `@Aspect` that encapsulates a cross-cutting concern by combining Pointcut expressions (specifying which join points to intercept) with Advice methods (specifying what code to execute at those join points). An Aspect is also a Spring `@Component` (or registered as a bean via `@Bean`) so that it is detected and activated by `AnnotationAwareAspectJAutoProxyCreator`. Each Aspect can define multiple `@Pointcut` methods (reusable expression definitions) and multiple Advice methods (`@Before`, `@After`, `@Around`, `@AfterReturning`, `@AfterThrowing`), each referencing one or more Pointcuts. Spring AOP Aspects are singletons by default — one shared instance handles all intercepted method calls. Ordering between Aspects is controlled via `@Order(n)` on the Aspect class or by implementing `org.springframework.core.Ordered`. The `@Aspect` annotation alone does NOT register the class as a Spring bean — `@Component` (or equivalent) is needed alongside it.

---

### 🟢 Simple Definition (Easy)

An Aspect is a class that says "for all methods matching this pattern, run this code before/after/around the call." It is the container for a cross-cutting concern.

---

### 🔵 Simple Definition (Elaborated)

An Aspect is where you define a cross-cutting concern as a reusable module. Instead of putting security checks, logging statements, or transaction management into every service method, you define them once in an Aspect class. The Aspect contains two things: a Pointcut (which methods to intercept, specified as an expression), and Advice (the code to run at those methods — before the method, after it returns, around the whole call, etc.). Spring detects all `@Aspect` beans at startup and weaves their Advice into the corresponding beans via proxies. One Aspect class can handle multiple concerns or one focused concern across many methods.

---

### 🔩 First Principles Explanation

**Structure of a complete Spring Aspect:**

```java
@Aspect              // marks this class as an AOP Aspect
@Component           // makes it a Spring bean (required!)
@Order(10)           // controls order among multiple Aspects (lower = outermost)
public class AuditAspect {

    // ─── POINTCUT DEFINITIONS ────────────────────────────────────
    // Named pointcuts: reusable expressions referenced by advice methods

    // Matches: execution of any public method in any @Service bean
    @Pointcut("within(@org.springframework.stereotype.Service *)")
    public void serviceBean() {}

    // Matches: methods annotated with @Audited (custom annotation)
    @Pointcut("@annotation(com.example.Audited)")
    public void auditedOperation() {}

    // Composed pointcut: service bean AND audited
    @Pointcut("serviceBean() && auditedOperation()")
    public void auditedServiceOperation() {}


    // ─── ADVICE METHODS ──────────────────────────────────────────

    // @Before: runs before the matched method executes
    @Before("auditedServiceOperation()")
    public void beforeAuditedOp(JoinPoint jp) {
        String operation = jp.getSignature().toShortString();
        String user = SecurityContext.currentUser();
        auditLog.recordEntry(user, operation, jp.getArgs());
    }

    // @AfterReturning: runs after normal return
    @AfterReturning(pointcut = "auditedServiceOperation()", returning = "result")
    public void afterSuccess(JoinPoint jp, Object result) {
        auditLog.recordSuccess(jp.getSignature().getName(), result);
    }

    // @AfterThrowing: runs after exception
    @AfterThrowing(pointcut = "auditedServiceOperation()", throwing = "ex")
    public void afterFailure(JoinPoint jp, Exception ex) {
        auditLog.recordFailure(jp.getSignature().getName(), ex.getMessage());
    }

    // @Around: full control — wraps the method call
    @Around("serviceBean()")
    public Object measurePerformance(ProceedingJoinPoint pjp) throws Throwable {
        long start = System.nanoTime();
        try {
            return pjp.proceed(); // call the actual method
        } finally {
            long ms = (System.nanoTime() - start) / 1_000_000;
            metrics.recordLatency(pjp.getSignature().getName(), ms);
        }
    }
}
```

**Key rules for Aspect classes:**

```
Rule 1: @Aspect alone does NOT make a Spring bean.
  @Aspect + @Component → detected by component scan
  @Aspect + explicit @Bean registration in @Configuration → also works
  @Aspect without @Component → NOT activated by Spring (silent miss!)

Rule 2: Aspect methods must return correct types.
  @Before, @After, @AfterReturning, @AfterThrowing → return void
  @Around → must return Object (the return value of pjp.proceed())

Rule 3: Aspects are singletons (default).
  → stateful Aspects cause race conditions under concurrent requests
  → keep Aspects stateless: no instance fields that change per-invocation

Rule 4: @Around must call pjp.proceed() or the method is never executed.
  Missing pjp.proceed() → the real method is silently skipped
```

---

### ❓ Why Does This Exist (Why Before What)

WITHOUT Aspect as a modular unit:

What breaks without it:

1. Cross-cutting concerns have no cohesive home — logging code is scattered across every class.
2. Multiple concerns that apply to the same methods (transaction + security + logging) cannot be composed and ordered.
3. Adding a new concern requires modifying every class it applies to.
4. Testing cross-cutting behaviour requires setting up full application context.

WITH Aspect:
→ Each concern is in one class — easy to find, modify, disable, or test in isolation.
→ Multiple Aspects compose naturally via the `@Order` interceptor chain.
→ Aspects can be enabled/disabled by `@Profile` without changing any business code.
→ Aspects are testable independently — invoke advice methods directly in unit tests.

---

### 🧠 Mental Model / Analogy

> Think of an Aspect as a policy document for a hotel chain. The policy document says: "For all customer-facing operations (Pointcut: all public methods in @Service classes), the following procedures apply: greet the customer before service (Before advice), log the completed service (AfterReturning advice), and escalate complaints (AfterThrowing advice)." All hotel branches (beans) follow this policy without needing to know its details. The policy is written once, applied everywhere it matches. Multiple policy documents can exist for different concerns (safety, billing, hospitality), each with its own procedures and priority order.

"Policy document" = the @Aspect class
"For all customer-facing operations" = the @Pointcut expression
"Greet before service" = @Before advice
"Log completed service" = @AfterReturning advice
"Escalate complaints" = @AfterThrowing advice
"Multiple policy documents with priority order" = multiple @Aspect classes with @Order

---

### ⚙️ How It Works (Mechanism)

**How Spring discovers and activates Aspects:**

```
At startup (@EnableAspectJAutoProxy is active):
  1. AnnotationAwareAspectJAutoProxyCreator (BeanPostProcessor) is registered
  2. Spring creates all @Component + @Aspect beans
  3. AAPC scans all beans for @Aspect annotation
  4. For each @Aspect bean:
     → Parses @Pointcut methods → builds pointcut expressions
     → Parses @Before/@After/@Around methods → builds Advisors
     → Each Advisor = one Pointcut + one Advice
  5. For each regular bean (postProcessAfterInitialization):
     → Test each Advisor's Pointcut against the bean's methods
     → If any match → create proxy with matching Advisors as MethodInterceptors
     → If none match → return bean unchanged

@Order on Aspect classes:
  Lower @Order value = outer position in the interceptor chain
  Outer = first to enter Before advice, last to leave After advice
  Example: @Order(1) SecurityAspect wraps @Order(2) TransactionAspect:
    SecurityAspect.before → TransactionAspect.before → method()
    → TransactionAspect.after → SecurityAspect.after
```

---

### 🔄 How It Connects (Mini-Map)

```
AOP (Aspect-Oriented Programming)
(the paradigm)
        │
        ▼
Aspect  ◄──── (you are here)
(the module: @Aspect class combining Pointcut + Advice)
        │
        ├──── contains ──────────► Pointcut  (where: execution expression)
        │
        ├──── contains ──────────► Advice    (what: @Before, @Around, etc.)
        │                               │
        │                               ▼
        │                          JoinPoint (specific matched call)
        │
        └──── activated by ──────► AnnotationAwareAspectJAutoProxyCreator
                                   (BeanPostProcessor that creates proxies)
                │
                ▼
           Weaving (applying Aspect to target beans via proxy)
```

---

### 💻 Code Example

**Production-ready security Aspect:**

```java
@Aspect
@Component
@Order(1)  // Security runs first (outermost)
public class SecurityAspect {

    @Autowired
    private SecurityService securityService;

    // All methods in controllers
    @Pointcut("within(@org.springframework.web.bind.annotation.RestController *)")
    private void restController() {}

    // Methods annotated with @RequiresRole
    @Pointcut("@annotation(requiresRole)")
    private void requiresRole(RequiresRole requiresRole) {}

    // Check role before method execution
    @Before("restController() && requiresRole(requiresRole)")
    public void checkRole(JoinPoint jp, RequiresRole requiresRole) {
        String requiredRole = requiresRole.value();
        if (!securityService.currentUserHasRole(requiredRole)) {
            throw new AccessDeniedException(
                "Role required: " + requiredRole
                + ", current user: " + securityService.currentUsername()
            );
        }
    }
}

// Custom annotation used in Pointcut
@Target(ElementType.METHOD)
@Retention(RetentionPolicy.RUNTIME)
public @interface RequiresRole {
    String value();
}

// Usage in controller
@RestController
class OrderController {
    @GetMapping("/admin/orders")
    @RequiresRole("ADMIN")  // SecurityAspect activates for this method
    List<Order> getAllOrders() { ... }
}
```

---

### ⚠️ Common Misconceptions

| Misconception                                                         | Reality                                                                                                                                                                                                             |
| --------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | --- | ----------------------------------------------------------------------------- |
| `@Aspect` alone makes the class an active Spring Aspect               | `@Aspect` marks the class as an Aspect but does NOT register it as a Spring bean. Without `@Component` (or explicit bean registration), Spring will not discover or activate the Aspect — it silently does nothing  |
| Stateful fields in an Aspect are safe because Aspects are singletons  | Singleton Aspects are shared across all threads. Mutable instance fields cause race conditions. Aspects must be stateless, or use thread-local storage for per-request state                                        |
| `@Around` advice is required to call `pjp.proceed()`                  | While best practice, there is no compile-time enforcement. Forgetting `pjp.proceed()` in `@Around` silently skips the real method and returns null — a severe bug that produces incorrect results with no exception |
| Multiple `@Pointcut` expressions in one `@Aspect` are evaluated as OR | Multiple `@Pointcut` methods are independent definitions. Combining them uses explicit operators: `&&` (AND), `                                                                                                     |     | `(OR),`!` (NOT). By default they are independent; you compose them explicitly |

---

### 🔥 Pitfalls in Production

**Forgetting `pjp.proceed()` in @Around — method silently not executed**

```java
// BAD: forgot to call pjp.proceed()
@Around("execution(* com.example.service.*.*(..))")
public Object aroundAdvice(ProceedingJoinPoint pjp) throws Throwable {
    log.info("Before: {}", pjp.getSignature().getName());
    // return pjp.proceed(); ← MISSING!
    return null; // ALL service methods now return null — no business logic runs
}

// GOOD: always call pjp.proceed()
@Around("execution(* com.example.service.*.*(..))")
public Object aroundAdvice(ProceedingJoinPoint pjp) throws Throwable {
    log.info("Before: {}", pjp.getSignature().getName());
    Object result = pjp.proceed(); // call the real method
    log.info("After: {}", pjp.getSignature().getName());
    return result; // return the real result
}
```

---

**@Aspect without @Component — Aspect silently not applied**

```java
// BAD: @Aspect without @Component — not a Spring bean, never activated
@Aspect // not a Spring bean!
public class LoggingAspect {
    @Before("execution(* com.example.*.*(..))")
    public void logEntry(JoinPoint jp) { ... }
}
// No error, no warning — all methods just run without logging

// GOOD: add @Component (or register as @Bean)
@Aspect
@Component // now it is a Spring bean AND an active Aspect
public class LoggingAspect { ... }
```

---

### 🔗 Related Keywords

- `AOP (Aspect-Oriented Programming)` — the paradigm that Aspect implements
- `Advice` — the code unit within an Aspect (`@Before`, `@After`, `@Around`, etc.)
- `Pointcut` — the expression within an Aspect that specifies which methods to intercept
- `JoinPoint` — the specific method execution instance passed to Advice methods
- `Weaving` — the process of applying the Aspect to target beans via proxy
- `BeanPostProcessor` — `AnnotationAwareAspectJAutoProxyCreator` scans for `@Aspect` beans and creates proxies

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ STRUCTURE    │ @Aspect + @Component                      │
│              │ @Pointcut methods → expressions           │
│              │ @Before/@After/@Around advice methods     │
├──────────────┼───────────────────────────────────────────┤
│ SINGLETON    │ Default scope — must be STATELESS         │
│              │ Mutable fields → race conditions          │
├──────────────┼───────────────────────────────────────────┤
│ ORDERING     │ @Order(n): lower n = outermost in chain   │
├──────────────┼───────────────────────────────────────────┤
│ @AROUND RULE │ MUST call pjp.proceed() or real method    │
│              │ is silently skipped                       │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "Aspect = policy document: defines what   │
│              │  to do and where, applied to all          │
│              │  matching beans via proxy."               │
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** An application has two Aspects: `SecurityAspect (@Order(1))` and `TransactionAspect (@Order(2))`. Both apply `@Around` advice to the same service method. The security check throws `AccessDeniedException` before calling `pjp.proceed()`. Trace the exact execution: does `TransactionAspect`'s `@Around` advice ever execute? Is any part of `TransactionAspect`'s cleanup (transaction rollback) invoked? Now reverse the order — `TransactionAspect (@Order(1))` begins a transaction, then `SecurityAspect (@Order(2))` throws. Explain why the transaction rollback behaviour differs between the two ordering scenarios.

**Q2.** Spring AOP Aspects are Spring beans and therefore subject to the full bean lifecycle. If an `@Aspect` bean itself has a `@Transactional` method, and another Aspect applies `@Around` advice to ALL service beans (including the Aspect bean), describe the recursive wrapping situation: does the Aspect bean get proxied? Can an Aspect have advice applied to it by another Aspect? What prevents an infinite recursion where the Aspect proxy intercepts calls to the Aspect proxy's own advice methods?
