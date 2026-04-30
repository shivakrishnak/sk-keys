---
layout: default
title: "Aspect"
parent: "Spring Core"
nav_order: 387
permalink: /spring/aspect/
number: "387"
category: Spring Core
difficulty: ★★☆
depends_on: "AOP, Spring AOP, @Aspect, Pointcut, Advice"
used_by: "Advice, Pointcut, @Transactional internals, Custom cross-cutting"
tags: #java, #spring, #intermediate, #pattern, #architecture
---

# 387 — Aspect

`#java` `#spring` `#intermediate` `#pattern` `#architecture`

⚡ TL;DR — The AOP module that encapsulates a cross-cutting concern by combining pointcuts (where to intercept) with advice (what to do) in a single annotated class.

| #387 | category: Spring Core
|:---|:---|:---|
| **Depends on:** | AOP, Spring AOP, @Aspect, Pointcut, Advice | |
| **Used by:** | Advice, Pointcut, @Transactional internals, Custom cross-cutting | |

---

### 📘 Textbook Definition

An **Aspect** is the unit of modularisation in AOP — it is the class that contains one or more pointcut expressions and the advice methods that execute at those points. In Spring, aspects are declared using the `@Aspect` annotation (from AspectJ) combined with `@Component` to make the class a managed bean. An aspect class must not itself be advised by another AOP proxy (it cannot be `@Transactional` without special care) and must be a concrete class — not abstract, not an interface. `AbstractAutoProxyCreator`, triggered during `BeanPostProcessor` processing, scans all `@Aspect` beans and uses their pointcuts and advice to build the interceptor chain applied to target beans.

---

### 🟢 Simple Definition (Easy)

An Aspect is the "cross-cutting module" in AOP. You write one class that says "whenever any service method is called, do this before and this after." That class is an aspect.

---

### 🔵 Simple Definition (Elaborated)

An aspect is a Java class annotated `@Aspect` that bundles two things: a pointcut (which methods to intercept, expressed as an AspectJ expression) and advice (what code to run before, after, or around those methods). When Spring starts, it scans all `@Aspect` beans, builds a mapping of "which beans need which aspects applied," and creates proxies for those beans. The aspect's advice code runs transparently whenever a matched method is called — your service classes never reference the aspect directly.

---

### 🔩 First Principles Explanation

**Aspect = pointcut + advice combined:**

Without the aspect abstraction, you'd need a separate mechanism to express "where" and another to express "what." The aspect is the container that binds them:

```
ASPECT
  ├── POINTCUT: "execution(* com.example.service.*.*(..))"
  │   (WHAT to match: all service layer methods)
  │
  └── ADVICE: @Before / @After / @Around
      (WHAT to do when a matched method runs)
```

**@Aspect is discovery metadata, not behaviour:**

`@Aspect` alone doesn't create a bean. You need `@Component` (or a `@Bean` factory method). `@Aspect` tells `AbstractAutoProxyCreator` to scan this class for pointcut/advice definitions. Without `@Component`, the aspect is never detected.

```java
@Aspect            // tells Spring AOP: "scan this class"
@Component         // tells container: "create this as a bean"
public class AuditAspect {
  // pointcuts + advice methods here
}
```

---

### ❓ Why Does This Exist (Why Before What)

**WITHOUT the Aspect abstraction:**

```
Without a dedicated aspect class:

  Cross-cutting logic embedded in services:
    Every service that needs auditing must call
    auditLog.log(...) manually → scattered, forgettable

  No single point of change:
    "Change audit format" → edit every service
    "Disable audit in tests" → edit every service

  No reuse:
    Same retry logic copied into 20 DAO methods
    Bug in retry logic → 20 fixes needed
```

**WITH Aspect:**

```
→ All audit logic in ONE class: AuditAspect
→ All retry logic in ONE class: RetryAspect
→ Change audit format: edit AuditAspect only
→ Disable in tests: remove @Component or use @Profile
→ Add concerns to existing code: zero modification
→ Open/Closed Principle: open for extension (new aspect),
  closed for modification (existing code unchanged)
```

---

### 🧠 Mental Model / Analogy

> An Aspect is like a **building inspector's remit document**. The remit specifies WHICH buildings to inspect (pointcut: "all buildings over 5 floors in Zone A") and WHAT the inspector does on each visit (advice: "check fire escape clearance before occupancy approval"). The buildings themselves don't need to know they're being inspected — the inspector's remit is defined separately and applied by the inspection authority (Spring container) when buildings (beans) are commissioned.

"Inspector's remit document" = Aspect class
"WHICH buildings to inspect" = Pointcut expression
"WHAT the inspector checks" = Advice method
"Buildings don't know they're inspected" = services unmodified
"Inspection authority applying the remit" = Spring AOP proxy creation

---

### ⚙️ How It Works (Mechanism)

**Complete aspect class structure:**

```java
@Aspect
@Component
@Order(1)  // optional: controls relative order vs other aspects
public class SecurityAspect {

  // ── Named pointcut (reusable reference) ──────────────────
  @Pointcut("execution(* com.example.api..*.*(..))")
  public void apiLayer() {}  // empty body — just a name

  @Pointcut("@annotation(com.example.Secured)")
  public void securedAnnotation() {}

  // ── Combined pointcut ─────────────────────────────────────
  @Pointcut("apiLayer() && securedAnnotation()")
  public void securedApiCall() {}

  // ── Advice using named pointcut ───────────────────────────
  @Before("securedApiCall()")
  public void checkAccess(JoinPoint jp) {
    String role = ((Secured)
        jp.getTarget().getClass()
          .getDeclaredMethod(
              jp.getSignature().getName())
          .getAnnotation(Secured.class)
    ).value();
    SecurityContext.requireRole(role);
  }

  // ── Around advice with full control ──────────────────────
  @Around("securedApiCall()")
  public Object secureExecution(
      ProceedingJoinPoint pjp) throws Throwable {
    checkAccess(pjp);
    try {
      return pjp.proceed();
    } catch (AccessDeniedException e) {
      log.warn("Access denied: {}", pjp.getSignature());
      throw e;
    }
  }
}
```

**Aspect detection sequence:**

```
┌─────────────────────────────────────────────────────┐
│  HOW SPRING DETECTS AND APPLIES ASPECTS             │
│                                                     │
│  1. @Aspect + @Component beans registered in ctx    │
│  2. AnnotationAwareAspectJAutoProxyCreator (a BPP)  │
│     scans all @Aspect beans                         │
│  3. For each non-aspect bean at BPP.afterInit:      │
│     check if any @Aspect pointcut matches this bean │
│  4. If match found:                                 │
│     create CGLIB/JDK proxy with interceptor chain   │
│     advice methods → interceptors in chain          │
└─────────────────────────────────────────────────────┘
```

---

### 🔄 How It Connects (Mini-Map)

```
Cross-cutting concern identified
        ↓
  ASPECT (119)  ← you are here
  (@Aspect class: bundles pointcut + advice)
        ↓
  Contains:
  Pointcut (121) → "match these method executions"
  Advice (120)   → @Before / @After / @Around code
  JoinPoint (122)→ runtime context passed to advice
        ↓
  Detected by: AnnotationAwareAspectJAutoProxyCreator
  Applied by: CGLIB/JDK proxy
        ↓
  Built-in Spring aspects:
  TransactionInterceptor → @Transactional (127)
  CacheAspectSupport     → @Cacheable
  MethodSecurityInterceptor → @Secured
```

---

### 💻 Code Example

**Example 1 — Complete audit aspect with named pointcuts:**

```java
@Aspect
@Component
@Slf4j
public class AuditAspect {
  private final AuditRepository audit;

  public AuditAspect(AuditRepository audit) {
    this.audit = audit;
  }

  // Named pointcut — reused across advice methods
  @Pointcut("execution(* com.example.service..*Service.*(..))"
          + " && !execution(* *.get*(..))")
  public void mutatingServiceOperations() {}

  @AfterReturning(
      pointcut = "mutatingServiceOperations()",
      returning = "result")
  public void logSuccess(JoinPoint jp, Object result) {
    audit.save(AuditEntry.success(
        jp.getSignature().toShortString(),
        jp.getArgs(),
        SecurityContextHolder.getContext()
          .getAuthentication().getName()
    ));
  }

  @AfterThrowing(
      pointcut = "mutatingServiceOperations()",
      throwing  = "ex")
  public void logFailure(JoinPoint jp, Exception ex) {
    audit.save(AuditEntry.failure(
        jp.getSignature().toShortString(), ex));
  }
}
```

**Example 2 — Aspect for retry with @Around:**

```java
@Aspect
@Component
public class RetryAspect {
  @Around("@annotation(retryable)")
  public Object retry(ProceedingJoinPoint pjp,
      Retryable retryable) throws Throwable {
    int maxAttempts = retryable.maxAttempts();
    long backoffMs  = retryable.backoffMs();
    Throwable lastEx = null;
    for (int attempt = 1; attempt <= maxAttempts; attempt++) {
      try {
        return pjp.proceed();
      } catch (Exception e) {
        lastEx = e;
        if (attempt < maxAttempts) {
          Thread.sleep(backoffMs * attempt); // backoff
        }
      }
    }
    throw lastEx;
  }
}

// Usage — service unchanged except for annotation:
@Service class InventoryClient {
  @Retryable(maxAttempts = 3, backoffMs = 200)
  public Inventory fetchInventory(String sku) {
    return httpClient.get("/inventory/" + sku);
  }
}
```

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| @Aspect alone makes the class a Spring bean | @Aspect only marks the class for AOP scanning. @Component (or @Bean) is still required to make it a container-managed bean |
| An aspect can advise itself | A Spring AOP aspect is managed as a regular bean. If the aspect itself triggers a pointcut it defines, the call is NOT intercepted — aspects cannot proxy themselves |
| Aspect ordering controls execution sequence for all advice types | @Order controls the aspect "nesting" order: lower order = outermost. @Before of lower-order fires first; @After of lower-order fires last |
| Declaring multiple @Aspect classes is inefficient | Spring processes all @Aspect beans efficiently at startup. Multiple small aspects are better than one monolithic god-aspect |

---

### 🔥 Pitfalls in Production

**1. Aspect not applied because @Component missing**

```java
// BAD: @Aspect without @Component — never detected
@Aspect
// Missing: @Component
public class MetricsAspect {
  @Around("execution(* com.example.service.*.*(..))")
  public Object measure(ProceedingJoinPoint p) throws Throwable {
    // Never fires! Aspect bean not in container
    return p.proceed();
  }
}

// GOOD: both annotations required
@Aspect
@Component
public class MetricsAspect { ... }
```

**2. Aspect depends on @Transactional bean — BPP ordering issue**

```java
// BAD: @Autowired @Transactional bean in @Aspect
// → The @Transactional bean created before AOP proxy applied
@Aspect
@Component
public class AuditAspect {
  @Autowired
  AuditService audit; // @Transactional — created early, unproxied!
}

// GOOD: @Lazy breaks the BPP early-creation cycle
@Aspect
@Component
public class AuditAspect {
  @Autowired @Lazy
  AuditService audit; // resolved lazily — fully proxied
}
```

---

### 🔗 Related Keywords

- `AOP` — the paradigm; Aspect is its primary unit of modularisation
- `Advice` — the code that runs within an aspect at a matched join point
- `Pointcut` — the expression within an aspect that selects target join points
- `JoinPoint` — the runtime execution context passed to advice methods
- `@Transactional` — powered by Spring's built-in `TransactionInterceptor` (an aspect)
- `BeanPostProcessor` — detects and applies aspects during bean creation

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ KEY IDEA     │ @Aspect class = container for pointcuts   │
│              │ and advice that implement a cross-cutting │
│              │ concern; @Component required to activate  │
├──────────────┼───────────────────────────────────────────┤
│ USE WHEN     │ Extracting audit, metrics, retry,         │
│              │ security, rate limiting into one module   │
├──────────────┼───────────────────────────────────────────┤
│ AVOID WHEN   │ Business logic in aspects (use services); │
│              │ advising Spring framework beans directly  │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "An aspect is your cross-cutting concern  │
│              │  living in one place instead of fifty."  │
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ Advice (120) → Pointcut (121) →           │
│              │ JoinPoint (122)                           │
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** An aspect uses `@Around` advice to measure execution time and store metrics in a `MeterRegistry`. The aspect is annotated `@Order(Integer.MAX_VALUE)` (innermost). A `@Transactional` service method is called. Describe the exact sequence of proxy interception, explaining whether the timing includes or excludes the transaction commit time — and argue for the correct `@Order` value for a metrics aspect depending on whether you want to measure "business logic time" vs "total infrastructure time."

**Q2.** Spring AOP cannot advise `@Aspect` beans themselves — the aspect is not proxied. But AspectJ's full compile-time weaving CAN. Explain the architectural reason Spring avoids proxying aspect beans, describe what would happen if Spring tried to proxy a `@Aspect @Transactional` class, and explain how `@DeclareParents` in full AspectJ achieves something Spring AOP's proxy model structurally cannot.

