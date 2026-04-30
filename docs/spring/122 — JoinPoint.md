---
layout: default
title: "JoinPoint"
parent: "Spring & Spring Boot"
nav_order: 122
permalink: /spring/joinpoint/
number: "122"
category: Spring & Spring Boot
difficulty: ★☆☆
depends_on: "AOP, Aspect, Advice, Spring AOP"
used_by: "Advice methods, @Around, @Before, @After, custom audit aspects"
tags: #java, #spring, #foundational, #pattern
---

# 122 — JoinPoint

`#java` `#spring` `#foundational` `#pattern`

⚡ TL;DR — The runtime object passed to advice methods that provides access to the intercepted method's signature, arguments, target object, and proxy — the "what is happening right now" context.

| #122 | Category: Spring & Spring Boot | Difficulty: ★☆☆ |
|:---|:---|:---|
| **Depends on:** | AOP, Aspect, Advice, Spring AOP | |
| **Used by:** | Advice methods, @Around, @Before, @After, custom audit aspects | |

---

### 📘 Textbook Definition

A **JoinPoint** is a point during the execution of a programme — in Spring AOP, this is always a method execution. The `JoinPoint` interface (from AspectJ) is passed as the first parameter to `@Before`, `@After`, `@AfterReturning`, and `@AfterThrowing` advice methods, providing runtime metadata: the method signature (`getSignature()`), the actual arguments (`getArgs()`), the target bean (`getTarget()`), and the proxy object (`getThis()`). The `ProceedingJoinPoint` subinterface — used exclusively in `@Around` advice — adds the `proceed()` and `proceed(Object[] args)` methods that invoke the actual target method (or the next advice in the chain).

---

### 🟢 Simple Definition (Easy)

A JoinPoint is the "what just happened" information passed to your advice code. It tells you which method was called, with what arguments, on which object — so your advice can act on that information.

---

### 🔵 Simple Definition (Elaborated)

When your advice fires, it doesn't just run in a vacuum — it receives a `JoinPoint` object describing the exact interception context. You can read the method name, class name, actual parameter values, and the target bean. This lets your advice be generic yet context-aware: one audit aspect can log "OrderService.place called with args [OrderRequest{id=42}]" without knowing anything about `OrderService` at compile time. `ProceedingJoinPoint` extends this with the ability to actually invoke the target method — which is why only `@Around` advice receives it.

---

### 🔩 First Principles Explanation

**What advice needs to be useful:**

If advice only runs blindly — "transaction opened" — it has limited introspection. Production advice needs:
- Which class/method triggered it? (for logging, metrics tagging)
- What were the arguments? (for validation, audit trails)
- What is the target object? (for feature-flag checks, tenant routing)
- For @Around: the ability to invoke (or skip) the actual method

The `JoinPoint` API provides exactly this context:

```
JoinPoint from the inside:
  Signature:   getSignature()      // MethodSignature
    getName()       → "place"
    getDeclaringType() → OrderService.class
    toShortString() → "OrderService.place(..)"

  Arguments:   getArgs()           // Object[]
    [0] → OrderRequest{id=42, amount=99.99}

  Target:      getTarget()         // the real bean object
  Proxy:       getThis()           // the proxy object
  Kind:        getKind()           // "method-execution"
```

---

### ❓ Why Does This Exist (Why Before What)

**WITHOUT JoinPoint context:**

```
Without JoinPoint in advice:

  @Before("serviceLayer()")
  void logCall() {
    log.info("A service method was called.");
    // Which one? With what args? On which bean?
    // USELESS for debugging and auditing
  }

  Validation impossible:
    Can't read arguments to validate them
    Can't stop execution based on arg values

  Metrics tagging impossible:
    Can't tag metrics with method/class names
    → One undifferentiated counter for all service calls
```

**WITH JoinPoint:**

```
→ Audit: "UserService.register called with [admin@co.com]"
→ Validation: read args[0], validate, throw if invalid
→ Metrics: tag timer with class + method name
→ Tenant routing: inspect target.getTenantId()
→ @Around: proceed(modifiedArgs) to pass sanitised input
→ Security: inspect args for authorisation decisions
→ Tracing: extract method name for span name
```

---

### 🧠 Mental Model / Analogy

> `JoinPoint` is like the **court case file handed to a judge** when a case is called. The file contains who is involved (target), what is alleged (method name and signature), the evidence presented (arguments), and which court is hearing it (proxy context). The judge (advice) uses this file to make informed decisions — log the hearing, validate the evidence, or proceed with the trial. A `ProceedingJoinPoint` adds the judge's authority to actually start the trial (`proceed()`).

"Court case file" = JoinPoint
"Who is involved" = getTarget() — the real bean
"What is alleged / charged" = getSignature() — method name
"Evidence presented" = getArgs() — method arguments
"Starting the trial" = ProceedingJoinPoint.proceed()

---

### ⚙️ How It Works (Mechanism)

**JoinPoint API reference:**

```java
@Aspect
@Component
public class InspectionAspect {
  @Before("execution(* com.example.service.*.*(..))")
  public void inspect(JoinPoint jp) {
    // CLASS and METHOD
    Class<?> targetClass = jp.getTarget().getClass();
    String methodName    = jp.getSignature().getName();

    // FULL SIGNATURE (includes params, return type)
    MethodSignature sig  = (MethodSignature) jp.getSignature();
    Method method        = sig.getMethod();
    Class<?> returnType  = sig.getReturnType();

    // RUNTIME ARGUMENTS
    Object[] args        = jp.getArgs();
    for (int i = 0; i < args.length; i++) {
      log.debug("  arg[{}] = {}", i, args[i]);
    }

    // THE PROXY (not the real object — use sparingly)
    Object proxy         = jp.getThis();

    // SHORT HUMAN-READABLE REPRESENTATION
    String shortStr      = jp.getSignature().toShortString();
    // → "OrderService.place(OrderRequest)"
    String longStr       = jp.getSignature().toLongString();
    // → "public Order c.e.OrderService.place(OrderRequest)"
  }
}
```

**ProceedingJoinPoint — @Around exclusive:**

```java
@Around("execution(* com.example.service.*.*(..))")
public Object aroundCall(ProceedingJoinPoint pjp)
    throws Throwable {
  // Can inspect all JoinPoint info:
  log.debug("→ {}", pjp.getSignature().toShortString());

  // Modify args before proceeding:
  Object[] newArgs = Arrays.copyOf(pjp.getArgs(),
                                   pjp.getArgs().length);
  if (newArgs[0] instanceof String s) {
    newArgs[0] = s.trim();
  }

  // Invoke method (with modified args):
  Object result = pjp.proceed(newArgs);

  // Or skip the method entirely:
  // return CachedResult.forKey(cacheKey);

  // Or modify the result:
  if (result instanceof String str) {
    return str.toLowerCase();
  }
  return result;
}
```

---

### 🔄 How It Connects (Mini-Map)

```
Client calls proxied method
        ↓
  Proxy intercepts → builds MethodInvocation
        ↓
  JOINPOINT (122)  ← you are here
  (runtime context: target, sig, args, proxy)
        ↓
  Passed to advice methods in:
  @Before, @After, @AfterReturning, @AfterThrowing
        ↓
  ProceedingJoinPoint (subtype):
  Passed to @Around — adds proceed() method
        ↓
  Used in:
  Audit logging, metrics, validation, caching,
  argument sanitisation, tenant routing
```

---

### 💻 Code Example

**Example 1 — Audit aspect using full JoinPoint context:**

```java
@Aspect
@Component
public class AuditAspect {
  private final AuditRepository audit;

  public AuditAspect(AuditRepository audit) {
    this.audit = audit;
  }

  @AfterReturning(
      pointcut  = "execution(* com.example.service."
                + "*.save*(..))",
      returning = "result")
  public void auditSave(JoinPoint jp, Object result) {
    MethodSignature sig =
        (MethodSignature) jp.getSignature();

    audit.save(AuditEntry.builder()
        .className(sig.getDeclaringType().getSimpleName())
        .methodName(sig.getName())
        .arguments(Arrays.toString(jp.getArgs()))
        .result(String.valueOf(result))
        .principal(SecurityContextHolder.getContext()
            .getAuthentication().getName())
        .timestamp(Instant.now())
        .build());
  }
}
```

**Example 2 — Performance timer tagging by class and method:**

```java
@Aspect
@Component
public class MetricsAspect {
  private final MeterRegistry registry;

  @Around("within(com.example.service..*)")
  public Object time(ProceedingJoinPoint pjp)
      throws Throwable {
    String className  = pjp.getTarget()
                           .getClass()
                           .getSimpleName();
    String methodName = pjp.getSignature().getName();

    return Timer
        .builder("service.method.duration")
        .tag("class",  className)
        .tag("method", methodName)
        .register(registry)
        .recordCallable(pjp::proceed);
  }
}
// Results in metrics: service.method.duration{class=OrderService,method=place}
```

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| JoinPoint and ProceedingJoinPoint are interchangeable | ProceedingJoinPoint extends JoinPoint and is only available in @Around advice. Using ProceedingJoinPoint in @Before causes a startup error |
| getTarget() returns the proxy | getTarget() returns the REAL target object (the actual bean). getThis() returns the proxy. Most advice should use getTarget() |
| getArgs() returns a copy — modifying it affects the method call | getArgs() returns the actual argument array. Modifying it in place MAY affect the method call, but the safe approach is to call pjp.proceed(modifiedArgs) explicitly |
| JoinPoint is always available in @Around advice | @Around advice must declare ProceedingJoinPoint, not JoinPoint. Using just JoinPoint in @Around compiles but proceed() is unavailable |

---

### 🔥 Pitfalls in Production

**1. Using getThis() instead of getTarget() — gets proxy, not bean**

```java
// BAD: getThis() returns proxy — not what you usually want
@Before("serviceLayer()")
void inspect(JoinPoint jp) {
  Object obj = jp.getThis(); // $Proxy42 or CGLIB subclass
  log.info("Class: {}", obj.getClass().getName());
  // Logs: "com.example.OrderService$$SpringCGLIB$$0"

  // Reflection on proxy class finds no @Transactional etc.
}

// GOOD: getTarget() returns the real underlying object
Object realObj = jp.getTarget(); // real OrderService
log.info("Class: {}",
    AopUtils.getTargetClass(jp.getTarget()).getSimpleName());
// Logs: "OrderService"
```

**2. Casting getSignature() without checking type**

```java
// BAD: assuming it's always a MethodSignature
@Before("execution(* *.*(..))")
void inspect(JoinPoint jp) {
  // ClassCastException if this is a constructor join point
  // (rare in Spring AOP, but defensive coding matters)
  MethodSignature sig = (MethodSignature) jp.getSignature();
}

// GOOD: guard with instanceof
if (jp.getSignature() instanceof MethodSignature sig) {
  Method method = sig.getMethod();
  // use method safely
}
```

---

### 🔗 Related Keywords

- `Aspect` — the class that defines advice methods which receive JoinPoint
- `Advice` — the method that accepts JoinPoint as its first parameter
- `Pointcut` — determines which join points are eligible for advice invocation
- `ProceedingJoinPoint` — JoinPoint subtype used in @Around advice; adds proceed()
- `Spring AOP` — the framework that creates proxies and passes JoinPoint to advice
- `MethodSignature` — the castable subtype of Signature for method join points

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ KEY IDEA     │ Runtime context object passed to advice:  │
│              │ method name, args, target, proxy          │
├──────────────┼───────────────────────────────────────────┤
│ USE WHEN     │ Advice needs method name (logging/metrics)│
│              │ or args (validation, audit, sanitisation) │
├──────────────┼───────────────────────────────────────────┤
│ AVOID WHEN   │ Using ProceedingJoinPoint in non-@Around  │
│              │ advice; using getThis() when getTarget()  │
│              │ is intended                               │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "JoinPoint is the court file —            │
│              │  everything the judge needs to decide."   │
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ Weaving (123) → @Transactional (127) →    │
│              │ Spring AOP in production                  │
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** An `@Around` advice receives a `ProceedingJoinPoint`. The advice calls `pjp.getArgs()`, modifies the array in place (e.g. `args[0] = sanitised`), then calls `pjp.proceed()` (without passing the modified array). Trace exactly what arguments the target method receives — does in-place modification of the array affect the proceed() call, or must you use `pjp.proceed(args)` explicitly? Reference the Spring AOP source behaviour for `ReflectiveMethodInvocation.proceed()` to justify your answer.

**Q2.** In a distributed tracing system (e.g. OpenTelemetry with Spring), an `@Around` aspect creates a span named `jp.getSignature().toShortString()`. For a `@Transactional` service method `OrderService.place()` that is called 10,000 times per second, the span-naming call uses string concatenation. Profile the overhead: `toShortString()` involves reflection on every call. Explain why Spring caches `MethodSignature` internally between invocations, what object is reused vs what is freshly allocated on each `pjp.getArgs()` call, and how you would minimise allocation pressure in a high-throughput aspect while preserving observability.

