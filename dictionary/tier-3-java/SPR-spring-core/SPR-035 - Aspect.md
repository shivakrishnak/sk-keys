---
layout: default
title: "Aspect"
parent: "Spring Core"
grand_parent: "Technical Dictionary"
nav_order: 35
permalink: /spring/aspect/
id: SPR-035
category: Spring Core
difficulty: ★★☆
depends_on: AOP, CGLIB Proxy, JDK Dynamic Proxy, Bean
used_by: "@Transactional, @Cacheable, @Async, Spring Security, Custom AOP"
related: Advice, Pointcut, JoinPoint, Weaving, "@Aspect"
tags:
  - spring
  - springboot
  - intermediate
  - pattern
  - bestpractice
---

# SPR-035 - Aspect

⚡ TL;DR - An Aspect is the AOP module that groups a Pointcut (which methods to intercept) with Advice (what code to run) - it's the complete unit of a cross-cutting concern, marked with `@Aspect` in Spring.

| #387            | Category: Spring Core                                           | Difficulty: ★★☆ |
| :-------------- | :-------------------------------------------------------------- | :-------------- |
| **Depends on:** | AOP, CGLIB Proxy, JDK Dynamic Proxy, Bean                       |                 |
| **Used by:**    | @Transactional, @Cacheable, @Async, Spring Security, Custom AOP |                 |
| **Related:**    | Advice, Pointcut, JoinPoint, Weaving, @Aspect                   |                 |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
Logging, security, caching, and transaction logic are scattered across 200 service methods. Each concern is duplicated and interleaved with business logic. When the security policy changes, you hunt through 200 files. You can't unit test the security check in isolation - it's embedded in each method.

**THE INVENTION MOMENT:**
"An Aspect is the unit of modularity for AOP - the way a class is the unit of modularity for OOP."

---

### 📘 Textbook Definition

An **Aspect** in Spring AOP is a Java class annotated with `@Aspect` (and typically `@Component`) that encapsulates a cross-cutting concern. It contains one or more **Pointcut** declarations (`@Pointcut` methods) that define _which_ method executions to intercept, and one or more **Advice** methods (`@Before`, `@After`, `@Around`, `@AfterReturning`, `@AfterThrowing`) that define _what_ to do at those join points. Spring's `AnnotationAwareAspectJAutoProxyCreator` discovers `@Aspect` beans and registers them as `Advisor` objects, which are applied to matching beans via proxy generation. An Aspect class itself is NOT proxied - only the beans it targets are proxied.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
An Aspect = "WHERE to intercept" (Pointcut) + "WHAT to do there" (Advice), packaged as a class.

**One analogy:**

> An Aspect is a policy manual for a department. The policy says: "For all customer-facing transactions over $10,000 (the Pointcut), a supervisor must review them before processing (the Advice)." The policy is a separate document from the transaction procedures. Cashiers follow the transaction procedures; the supervisor review happens automatically when the threshold is met.

**One insight:**
The Aspect is the atomic unit of AOP concern. Just as a Java class is the unit of OOP modularity (encapsulating state + behavior), the Aspect is the unit of AOP modularity (encapsulating pointcut + advice). An Aspect can contain multiple pointcuts and multiple advice methods, all related to one cross-cutting concern.

---

### 🔩 First Principles Explanation

**CORE INVARIANTS:**

1. `@Aspect` marks a class as an aspect definition - Spring does NOT create a proxy of the aspect class itself.
2. An Aspect class must also be a Spring bean (`@Component` or registered via `@Bean`) for Spring AOP to discover it.
3. One Aspect class can contain multiple `@Pointcut` methods and multiple advice methods.
4. An Aspect should represent ONE concern - mixing logging and security in one Aspect violates the Single Responsibility Principle.
5. Aspect ordering (when multiple aspects apply to the same join point) is controlled via `@Order` or implementing `Ordered`.

**ASPECT ANATOMY:**

```
@Aspect
@Component
public class TransactionAspect {

    // Pointcut: WHERE to intercept
    @Pointcut("execution(* com.example.service.*.*(..))")
    public void allServiceMethods() {}

    // Advice: WHAT to do
    @Around("allServiceMethods()")
    public Object manageTransaction(ProceedingJoinPoint pjp) throws Throwable { ... }

    @AfterThrowing(
        pointcut = "allServiceMethods()",
        throwing = "ex"
    )
    public void onError(JoinPoint jp, Exception ex) { ... }
}
```

**THE TRADE-OFFS:**

**Gain:** Cross-cutting concern is encapsulated, testable, and reusable.
**Cost:** Invisible at call sites - you must check aspects to understand full method behavior. Stack traces include proxy frames. Self-invocation bypasses aspects.

---

### 🧪 Thought Experiment

**SETUP:**
You have a `PerformanceAspect` that logs method execution times. Six months later you realize it's logging too much. Without AOP, you'd edit 50 methods. With AOP, you edit one class.

**ONE CHANGE, ZERO SERVICE EDITS:**

```java
@Aspect @Component
public class PerformanceAspect {
    // BEFORE: log everything over 100ms
    // AFTER: change threshold to 500ms - one line change
    @Around("execution(* com.example.service.*.*(..))")
    public Object logSlowCalls(ProceedingJoinPoint pjp) throws Throwable {
        long start = System.nanoTime();
        Object result = pjp.proceed();
        long ms = (System.nanoTime() - start) / 1_000_000;
        if (ms > 500) {  // was 100 - changed in ONE place
            log.warn("SLOW: {} took {}ms", pjp.getSignature(), ms);
        }
        return result;
    }
}
```

**THE INSIGHT:**
The Aspect is a deployment unit for a cross-cutting concern. You can add, remove, modify, or disable a concern by changing one class. The 50 service classes are untouched.

---

### 🧠 Mental Model / Analogy

> An Aspect is like a filter on a camera lens. The camera body (business logic) takes photos (executes methods). The filter (aspect) snaps onto the lens and applies its effect (cross-cutting concern) to every photo taken through that lens. Different filters for different effects: polarizing filter (logging), UV filter (security check), ND filter (rate limiting). Each filter is a distinct, removable unit. The camera body knows nothing about which filters are attached.

- "Camera body" → service class with business logic
- "Filter on lens" → Aspect applied to the bean
- "Snapping on the lens" → Spring AOP proxying the bean
- "Effect on every photo" → advice running on every matching method
- "Removable" → removing `@Component` from the Aspect class disables it

---

### 📶 Gradual Depth - Four Levels

**Level 1 - What it is (anyone can understand):**
An Aspect is a class that says "whenever any method in the service package is called, also run this code." It's how Spring adds transaction management, security checks, and logging to your code without touching your code.

**Level 2 - How to use it (junior developer):**

1. Create a class annotated `@Aspect @Component`.
2. Add `@Pointcut` methods with expressions defining which methods to target.
3. Add `@Before`, `@After`, `@Around`, `@AfterReturning`, or `@AfterThrowing` methods referencing the pointcut.
4. Keep one Aspect per concern. Control ordering with `@Order`.
5. Annotate `@EnableAspectJAutoProxy` on your config (Spring Boot does this automatically).

**Level 3 - How it works (mid-level engineer):**
Spring's `BeanDefinitionRegistryPostProcessor` and `AnnotationAwareAspectJAutoProxyCreator` discover `@Aspect` beans. `ReflectiveAspectJAdvisorFactory.getAdvisors()` inspects the class for `@Pointcut` and advice annotations, building `InstantiationModelAwarePointcutAdvisorImpl` objects - each wrapping a `PointcutExpression` and an `AbstractAspectJAdvice`. These advisors are checked against each bean: `AopUtils.findAdvisorsThatCanApply()` runs the pointcut matcher. Matching beans are wrapped in proxies with the advisor chain ordered by `@Order`.

**Level 4 - Why it was designed this way (senior/staff):**
The `@Aspect` annotation is from AspectJ - Spring borrowed it rather than inventing a new annotation. This was a deliberate choice: developers familiar with AspectJ can apply their knowledge to Spring AOP without learning new syntax. The semantic difference (Spring AOP = proxy-based; AspectJ = bytecode weaving) is intentionally hidden - the same annotation syntax works for both, with the mode configurable. This "same language, different backend" design lets applications start with Spring AOP (simpler) and migrate to AspectJ (more powerful) by changing configuration, not code. `@Order` on aspects respects the Decorator pattern's ordered wrapping semantics - the highest precedence aspect's advice wraps the outermost layer, analogous to the outermost decorator in a Decorator chain.

---

### ⚙️ How It Works (Mechanism)

**Discovery and application:**

```
AnnotationAwareAspectJAutoProxyCreator.postProcessAfterInitialization():
  ↓
findEligibleAdvisors(beanClass):
  ↓
  For each @Aspect bean in context:
    ReflectiveAspectJAdvisorFactory.getAdvisors():
      For each advice method (@Before, @Around, etc.):
        Build InstantiationModelAwarePointcutAdvisorImpl
        (wraps: AspectJExpressionPointcut + advice method)
  ↓
  Filter: AopUtils.findAdvisorsThatCanApply(advisors, beanClass)
    → AspectJExpressionPointcut.matches(beanClass)?
  ↓
Matching advisors found → createProxy(bean, advisors)
  ↓
singletonObjects[beanName] = proxy
```

**Multiple aspects on one method (ordering):**

```java
@Aspect @Component @Order(1)  // outermost wrapper
public class SecurityAspect {
    @Before("execution(* com.example.service.*.*(..))")
    public void checkSecurity(JoinPoint jp) { /* check */ }
}

@Aspect @Component @Order(2)  // middle wrapper
public class TransactionAspect {
    @Around("execution(* com.example.service.*.*(..))")
    public Object manageTransaction(ProceedingJoinPoint pjp) { /* tx */ }
}

@Aspect @Component @Order(3)  // innermost wrapper (closest to method)
public class LoggingAspect {
    @Around("execution(* com.example.service.*.*(..))")
    public Object log(ProceedingJoinPoint pjp) { /* log */ }
}

// Call chain:
// SecurityAspect.before → TransactionAspect.around-before
//   → LoggingAspect.around-before → real method
//   → LoggingAspect.around-after → TransactionAspect.around-after
//   → (SecurityAspect has only @Before, no after)
```

---

### 🔄 The Complete Picture - End-to-End Flow

**NORMAL FLOW:**

```
@Aspect beans discovered at startup
    ↓
UserService bean created
    ↓
AnnotationAwareAspectJAutoProxyCreator checks: any aspects match?
    YES ← YOU ARE HERE (Aspect applied to UserService)
    ↓
Proxy wrapping UserService with [SecurityAspect, LoggingAspect]
    ↓
userService.save(user) called:
  [1] SecurityAspect @Before → checkSecurity()
  [2] LoggingAspect @Around before → log start
  [3] target.save(user) - real method
  [4] LoggingAspect @Around after → log duration
  [5] (no SecurityAspect @After)
    ↓
return result
```

---

### 💻 Code Example

**Example 1 - Complete Aspect with multiple advice types:**

```java
@Aspect
@Component
@Order(10)
public class ServiceAuditAspect {

    private static final Logger log = LoggerFactory.getLogger(ServiceAuditAspect.class);

    // Reusable pointcut
    @Pointcut("execution(public * com.example.service.*.*(..))")
    public void publicServiceMethod() {}

    // Before: log method entry
    @Before("publicServiceMethod()")
    public void logEntry(JoinPoint jp) {
        log.debug("Entering: {}", jp.getSignature().toShortString());
    }

    // AfterReturning: log successful return
    @AfterReturning(pointcut = "publicServiceMethod()", returning = "result")
    public void logSuccess(JoinPoint jp, Object result) {
        log.debug("Returned from {}: {}", jp.getSignature().toShortString(), result);
    }

    // AfterThrowing: log exceptions
    @AfterThrowing(pointcut = "publicServiceMethod()", throwing = "ex")
    public void logError(JoinPoint jp, Exception ex) {
        log.error("Exception in {}: {}", jp.getSignature().toShortString(), ex.getMessage());
    }
}
```

**Example 2 - Around advice for retry logic:**

```java
@Aspect
@Component
public class RetryAspect {

    @Around("@annotation(com.example.annotation.Retryable)")
    public Object retry(ProceedingJoinPoint pjp) throws Throwable {
        Retryable annotation = AnnotationUtils.findAnnotation(
            ((MethodSignature) pjp.getSignature()).getMethod(),
            Retryable.class
        );
        int maxAttempts = annotation.maxAttempts();

        Throwable lastException = null;
        for (int attempt = 1; attempt <= maxAttempts; attempt++) {
            try {
                return pjp.proceed();
            } catch (TransientDataAccessException e) {
                lastException = e;
                log.warn("Attempt {}/{} failed", attempt, maxAttempts);
                if (attempt < maxAttempts) Thread.sleep(100L * attempt);
            }
        }
        throw lastException;
    }
}
```

---

### ⚖️ Comparison Table

| Concern                | Aspect Name         | Pointcut Target        | Advice Type |
| ---------------------- | ------------------- | ---------------------- | ----------- |
| Transaction management | `TransactionAspect` | @Transactional methods | @Around     |
| Method logging         | `LoggingAspect`     | all service methods    | @Around     |
| Security check         | `SecurityAspect`    | secured methods        | @Before     |
| Caching                | `CachingAspect`     | @Cacheable methods     | @Around     |
| Retry                  | `RetryAspect`       | @Retryable methods     | @Around     |

**One Aspect per concern.** Don't mix logging and security in one `@Aspect` class - SRP applies to aspects too.

---

### ⚠️ Common Misconceptions

| Misconception                                        | Reality                                                                                                                                                  |
| ---------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------- |
| The @Aspect class itself is proxied by Spring        | No - Spring proxies the TARGET beans that the aspect applies to. The @Aspect class is a regular bean.                                                    |
| @Aspect without @Component is discovered             | No - the @Aspect class must be a Spring bean. @Aspect alone marks it as an aspect definition, but Spring AOP only applies aspects that are Spring beans. |
| Removing @Aspect disables the aspect                 | You also need to remove @Component (or remove the bean registration). @Aspect without @Component creates a broken half-configured state.                 |
| Multiple aspects on one method always cause overhead | The overhead is proportional to the number of aspects × number of calls. For typical services, this is nanoseconds per call - negligible vs I/O.         |

---

### 🚨 Failure Modes & Diagnosis

**Aspect not applying (missing @Component)**

**Symptom:**
Your `@Aspect` class code never runs despite correct pointcut.

**Root Cause:**
`@Aspect` marks the class as an aspect _definition_, but Spring AOP only discovers aspects that are Spring beans. Without `@Component` (or `@Bean` registration), the class is not in the application context.

**Fix:**

```java
@Aspect
@Component  // REQUIRED for Spring AOP discovery
public class LoggingAspect { ... }
```

---

**Aspect applying to itself (infinite loop)**

**Symptom:** (Rare) `StackOverflowError` involving the aspect class in the stack trace.

**Root Cause:** The aspect's pointcut accidentally matches a method on the aspect class itself.

**Fix:**

```java
// BAD: matches all beans including the aspect
@Pointcut("execution(* *.*(..))")
// GOOD: scope to specific packages, excluding the aspect package
@Pointcut("execution(* com.example.service..*(..))")
```

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**

- `AOP` - Aspect is the fundamental unit of AOP
- `CGLIB Proxy / JDK Dynamic Proxy` - the mechanisms that implement Aspect interception

**Builds On This (learn these next):**

- `Advice` - the action part of an Aspect (@Before, @After, @Around)
- `Pointcut` - the matching expression that selects join points
- `JoinPoint` - the specific execution context available within advice

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ WHAT IT IS   │ An AOP module: Pointcut (WHERE) +         │
│              │ Advice (WHAT) for one cross-cutting concern│
├──────────────┼───────────────────────────────────────────┤
│ ANNOTATIONS  │ @Aspect @Component (both required)        │
│              │ @Pointcut, @Before, @After, @Around       │
├──────────────┼───────────────────────────────────────────┤
│ KEY INSIGHT  │ One aspect per concern (SRP). @Aspect is  │
│              │ NOT proxied - its targets are proxied     │
├──────────────┼───────────────────────────────────────────┤
│ ORDERING     │ @Order(N) - lower N = outermost wrapper   │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "The complete policy document for a       │
│              │  cross-cutting concern."                  │
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ Advice → Pointcut → JoinPoint → Weaving   │
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** Spring AOP does not proxy `@Aspect` classes - they're plain beans. But what if an `@Aspect` class has a method annotated with `@Transactional`? Does that `@Transactional` work? Trace what would have to happen for a Spring bean that is also an `@Aspect` to have its own methods transactionally wrapped.

**Q2.** When two aspects apply to the same join point and both use `@Around`, each calls `pjp.proceed()` to invoke the next item in the chain. If the inner aspect's `@Around` advice throws an exception, does the outer aspect's `@Around` advice handle it? Trace the exception propagation through a two-@Around-advice chain.
