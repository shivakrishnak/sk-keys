---
layout: default
title: "Advice"
parent: "Spring Core"
nav_order: 388
permalink: /spring/advice/
number: "388"
category: Spring Core
difficulty: ★★☆
depends_on: "Aspect, AOP (Aspect-Oriented Programming), Pointcut, JoinPoint"
used_by: "Weaving, @Transactional, JoinPoint"
tags: #intermediate, #spring, #architecture, #pattern
---

# 388 — Advice

`#intermediate` `#spring` `#architecture` `#pattern`

⚡ TL;DR — **Advice** is the actual code that runs at a matched join point — the "what to do" in AOP. Spring provides five types: `@Before`, `@After`, `@AfterReturning`, `@AfterThrowing`, and `@Around`, each running at a different point relative to the intercepted method.

| #388            | Category: Spring Core                                          | Difficulty: ★★☆ |
| :-------------- | :------------------------------------------------------------- | :-------------- |
| **Depends on:** | Aspect, AOP (Aspect-Oriented Programming), Pointcut, JoinPoint |                 |
| **Used by:**    | Weaving, @Transactional, JoinPoint                             |                 |

---

### 📘 Textbook Definition

In Spring AOP, **Advice** is the action taken by an Aspect at a particular JoinPoint — it is the code that executes in response to the Pointcut match. Spring AOP supports five advice types: **`@Before`** runs before the matched method executes; **`@AfterReturning`** runs after the method returns normally; **`@AfterThrowing`** runs after the method throws an exception; **`@After`** (also called "finally advice") runs after the method completes regardless of outcome; and **`@Around`** wraps the method entirely, giving the advice full control over whether the method executes, what arguments it receives, and what is returned. `@Around` is the most powerful type and subsumes all other types, but the narrower types (`@Before`, `@AfterReturning`) are preferred when full control is not needed — they are simpler, more readable, and less error-prone. Advice methods receive a `JoinPoint` parameter (available to all types) or `ProceedingJoinPoint` (`@Around` only, adds `proceed()` control). The `returning` and `throwing` attributes of `@AfterReturning`/`@AfterThrowing` bind the method's return value or thrown exception to a named parameter.

---

### 🟢 Simple Definition (Easy)

Advice is the code that runs when an AOP Aspect triggers. `@Before` advice runs before the method, `@After` runs after it, and `@Around` wraps the whole call — letting you control it completely.

---

### 🔵 Simple Definition (Elaborated)

Every Aspect has at least one Advice: the code that actually does something. Think of the Pointcut as the "when" (which methods) and the Advice as the "what" (what to do at those methods). `@Before` advice is the simplest — it runs your code before the method, then the method runs normally. `@After` is like Java's `finally` — always runs, regardless of whether the method threw an exception. `@AfterReturning` gets the return value so you can inspect or log it. `@AfterThrowing` gets the exception for error handling or monitoring. `@Around` has the most power: you control whether the method even runs, can modify its arguments, change the return value, or suppress exceptions — but requires careful use (forgetting to call `pjp.proceed()` means the method never executes).

---

### 🔩 First Principles Explanation

**The five advice types — execution timing:**

```
Method call lifecycle:
                    ┌─────────────────────────────┐
@Before             │  runs here                  │
                    ▼                             │
             [target method executes]             │
                    │                             │
             ├── normal return ──────────────────►│
             │         ↓                          │
             │   @AfterReturning(returning="r")   │
             │         ↓                          │
             │         ↓──────── @After ──────────┤
             │                                    │
             └── throws exception ───────────────►│
                       ↓                          │
                 @AfterThrowing(throwing="e")     │
                       ↓                          │
                       ↓──────── @After ──────────┘
```

**All five advice types with correct signatures:**

```java
@Aspect
@Component
public class AdviceExamplesAspect {

    // 1. @Before — runs before method, cannot prevent execution
    @Before("execution(* com.example.service.*.*(..))")
    public void beforeAdvice(JoinPoint jp) {
        // jp.getArgs() → method arguments
        // jp.getTarget() → the bean being called
        // jp.getSignature() → method name, return type, etc.
        log.debug("Entering: {}", jp.getSignature().toShortString());
    }

    // 2. @AfterReturning — runs after normal return; gets return value
    @AfterReturning(
        pointcut = "execution(* com.example.service.*.*(..))",
        returning = "result"  // must match parameter name
    )
    public void afterReturningAdvice(JoinPoint jp, Object result) {
        log.debug("Returned from {}: {}", jp.getSignature().getName(), result);
        // NOTE: cannot change the return value from @AfterReturning
        // Use @Around to modify the return value
    }

    // 3. @AfterThrowing — runs after exception; gets exception
    @AfterThrowing(
        pointcut = "execution(* com.example.service.*.*(..))",
        throwing = "ex"       // must match parameter name
    )
    public void afterThrowingAdvice(JoinPoint jp, Exception ex) {
        log.error("Exception in {}: {}", jp.getSignature().getName(), ex.getMessage());
        // NOTE: does NOT suppress the exception — it still propagates
        // Throw a different exception here to replace the original
    }

    // 4. @After — runs after method regardless of outcome (like finally)
    @After("execution(* com.example.service.*.*(..))")
    public void afterFinallyAdvice(JoinPoint jp) {
        log.debug("Completed (success or failure): {}", jp.getSignature().getName());
        // Use for cleanup: release resources, clear ThreadLocal, etc.
    }

    // 5. @Around — full control; wraps the entire method call
    @Around("execution(* com.example.service.*.*(..))")
    public Object aroundAdvice(ProceedingJoinPoint pjp) throws Throwable {
        log.debug("Before: {}", pjp.getSignature().getName());
        try {
            Object result = pjp.proceed();       // call the real method
            // Can modify result here: return transformResult(result);
            return result;
        } catch (Exception e) {
            log.error("Error in {}: {}", pjp.getSignature().getName(), e.getMessage());
            // Can suppress: return defaultValue; // suppress exception and return fallback
            throw e;                             // or rethrow
        } finally {
            log.debug("After: {}", pjp.getSignature().getName());
        }
    }
}
```

**Binding method parameters in Advice:**

```java
// Bind method arguments by name
@Before("execution(* com.example.service.OrderService.placeOrder(..)) && args(order)")
public void beforePlaceOrder(JoinPoint jp, Order order) {
    // 'order' is bound to the first argument of placeOrder
    log.info("Placing order for customer: {}", order.getCustomerId());
}

// Bind annotation attributes
@Around("@annotation(retryable)")
public Object aroundRetryable(ProceedingJoinPoint pjp, Retryable retryable)
        throws Throwable {
    int maxRetries = retryable.maxAttempts(); // access annotation attribute
    for (int attempt = 0; attempt < maxRetries; attempt++) {
        try {
            return pjp.proceed();
        } catch (RetryableException e) {
            if (attempt == maxRetries - 1) throw e;
            Thread.sleep(retryable.backoffMs());
        }
    }
    throw new IllegalStateException("unreachable");
}
```

---

### ❓ Why Does This Exist (Why Before What)

WITHOUT different Advice types:

What breaks without it:

1. Only one type means: you always use `@Around` for everything — complex, error-prone (forget `proceed()`).
2. Cannot cleanly express "run only on normal return" or "run only on exception" without conditional logic in `@Around`.
3. Return value capture requires `@Around` and explicit handling, even for simple post-processing.
4. Simple "log on entry" scenarios require heavy `@Around` infrastructure.

WITH five Advice types:
→ Use the simplest advice type that meets the need — reduces risk of bugs.
→ `@AfterReturning` and `@AfterThrowing` make success vs. failure paths explicit without conditionals.
→ `@Before` is the most readable for pre-condition checks.
→ `@After` covers cleanup reliably like `finally`.
→ `@Around` is reserved for cases that genuinely need full control (retry, circuit breaker, caching).

---

### 🧠 Mental Model / Analogy

> Think of a surgery team. `@Before` advice is the pre-op checklist — done before the patient enters the operating theatre. `@AfterReturning` is the post-op recovery assessment — only done when the surgery succeeded. `@AfterThrowing` is the incident report — only filled when something went wrong. `@After` is the sterilisation routine — always done after every surgery, success or failure. `@Around` is the anaesthesiologist — they have full control: they can decide whether surgery proceeds, can change the patient's state before handing off to the surgeon, and manage the critical monitoring during and after.

"`@Before` — pre-op checklist" = code that runs before the method
"`@AfterReturning` — post-op recovery" = code that runs on successful return (gets result)
"`@AfterThrowing` — incident report" = code that runs when exception is thrown (gets exception)
"`@After` — sterilisation" = always-runs code (like finally)
"`@Around` — anaesthesiologist" = full control: decides if surgery proceeds, can modify outcome

---

### ⚙️ How It Works (Mechanism)

**How Spring converts Advice annotations into MethodInterceptors:**

```
At startup:
  ReflectiveAspectJAdvisorFactory processes each @Aspect bean:
    → @Before   → MethodBeforeAdviceInterceptor
    → @After    → AspectJAfterAdvice (MethodInterceptor with finally block)
    → @AfterReturning → AfterReturningAdviceInterceptor
    → @AfterThrowing  → AspectJAfterThrowingAdvice
    → @Around   → AspectJAroundAdvice (calls ProceedingJoinPoint.proceed)

These interceptors form a chain (ReflectiveMethodInvocation):
  Security.@Before → Transaction.@Before → method() → Transaction.@After → Security.@After

@AfterReturning vs @After execution:
  @AfterReturning: invocation.proceed() returns normally → AfterReturningInterceptor runs
  @After (finally): wrapped in try { invocation.proceed() } finally { afterAdvice.run() }
  Both run after the method; @After always runs, @AfterReturning skips on exception
```

---

### 🔄 How It Connects (Mini-Map)

```
Aspect (the container class)
        │
        ▼
Advice  ◄──── (you are here)
(the code to execute at a JoinPoint)
        │
        ├──── @Before         (before method execution)
        ├──── @After          (always after, like finally)
        ├──── @AfterReturning (after normal return, gets result)
        ├──── @AfterThrowing  (after exception, gets exception)
        └──── @Around         (wraps entire call, full control)
                │
                ▼
        JoinPoint / ProceedingJoinPoint
        (context: method name, args, target)
                │
                ▼
        Weaving
        (applied to target via MethodInterceptor chain)
```

---

### 💻 Code Example

**Real-world caching Advice using @Around:**

```java
@Aspect
@Component
public class CachingAspect {

    private final Cache<String, Object> cache = Caffeine.newBuilder()
        .maximumSize(1000)
        .expireAfterWrite(Duration.ofMinutes(5))
        .build();

    @Around("@annotation(cacheable)")
    public Object cacheResult(ProceedingJoinPoint pjp, Cacheable cacheable)
            throws Throwable {
        // Build cache key from annotation name + serialised arguments
        String key = cacheable.value() + ":" + Arrays.toString(pjp.getArgs());

        Object cached = cache.getIfPresent(key);
        if (cached != null) {
            log.debug("Cache HIT for key: {}", key);
            return cached;
        }

        log.debug("Cache MISS for key: {}", key);
        Object result = pjp.proceed(); // call the real method

        if (result != null) {
            cache.put(key, result);    // cache the result
        }
        return result;
    }
}
```

**Real-world circuit breaker using @Around:**

```java
@Aspect
@Component
public class CircuitBreakerAspect {

    private final Map<String, CircuitState> states = new ConcurrentHashMap<>();

    @Around("@annotation(breaker)")
    public Object circuitBreaker(ProceedingJoinPoint pjp, CircuitBreaker breaker)
            throws Throwable {
        String key = pjp.getSignature().toShortString();
        CircuitState state = states.computeIfAbsent(key, k -> new CircuitState());

        if (state.isOpen()) {
            // Circuit is open — fail fast, do not call downstream
            return breaker.fallback().getDeclaredConstructor().newInstance()
                          .handle(pjp.getArgs());
        }

        try {
            Object result = pjp.proceed();
            state.recordSuccess();
            return result;
        } catch (Exception e) {
            state.recordFailure();
            if (state.shouldOpen(breaker.failureThreshold())) {
                state.open(Duration.ofSeconds(breaker.resetTimeoutSeconds()));
                log.warn("Circuit opened for: {}", key);
            }
            throw e;
        }
    }
}
```

---

### ⚠️ Common Misconceptions

| Misconception                                                              | Reality                                                                                                                                                                                                                                             |
| -------------------------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `@After` and `@AfterReturning` are the same                                | `@After` runs after method completion regardless of outcome (success OR exception), like `finally`. `@AfterReturning` runs ONLY after normal return — not if an exception is thrown                                                                 |
| `@AfterThrowing` suppresses the exception                                  | `@AfterThrowing` advice runs when an exception occurs but does NOT suppress it. The exception continues propagating after the advice completes. To suppress, use `@Around` with a try-catch that catches the exception and returns a fallback value |
| `@Around` is the best choice for all advice                                | `@Around` is the most powerful but requires the most careful use — forgetting `pjp.proceed()` silently skips the real method. Use the narrowest advice type that meets the need                                                                     |
| Advice can change the arguments passed to the original method in `@Before` | `@Before` advice cannot change what arguments the method receives. Only `@Around` can modify arguments by calling `pjp.proceed(newArgs)` with different arguments                                                                                   |

---

### 🔥 Pitfalls in Production

**@Around modifying return value incorrectly — returns wrong type**

```java
// BAD: casting return value without type safety
@Around("execution(* com.example.service.*.*(..))")
public Object logAndModify(ProceedingJoinPoint pjp) throws Throwable {
    Object result = pjp.proceed();
    // BUG: assuming all service methods return String
    return ((String) result).toUpperCase(); // ClassCastException if method returns int!
}

// GOOD: check type before transformation
@Around("execution(* com.example.service.*.*(..))")
public Object logAndModify(ProceedingJoinPoint pjp) throws Throwable {
    Object result = pjp.proceed();
    if (result instanceof String str) {
        return str.toUpperCase();
    }
    return result; // return unchanged for non-String results
}
```

---

### 🔗 Related Keywords

- `Aspect` — the class that contains Advice methods
- `Pointcut` — the expression that determines which JoinPoints trigger the Advice
- `JoinPoint` — the context object passed to Advice, providing method name, args, and target
- `AOP (Aspect-Oriented Programming)` — the paradigm that defines the role of Advice
- `Weaving` — the process of binding Advice to JoinPoints through proxy generation
- `@Transactional` — implemented as `@Around` Advice by `TransactionInterceptor`

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ ADVICE TYPE  │ WHEN IT RUNS          │ GETS               │
│ @Before      │ Before method         │ JoinPoint          │
│ @AfterReturn │ After normal return   │ JoinPoint, result  │
│ @AfterThrow  │ After exception       │ JoinPoint, ex      │
│ @After       │ Always (like finally) │ JoinPoint          │
│ @Around      │ Wraps entire call     │ ProceedingJoinPoint│
├──────────────┼───────────────────────────────────────────┤
│ RULE         │ @Around MUST call pjp.proceed()           │
│              │ @AfterThrowing does NOT suppress exception│
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "Advice = the code that fires:            │
│              │  @Before=pre-op, @After=cleanup,          │
│              │  @Around=anaesthesiologist."              │
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** `@AfterThrowing` advice is configured with `throwing = "ex"` bound to a parameter of type `ServiceException`. What happens when the intercepted method throws a `RuntimeException` that is NOT a `ServiceException`? Does the `@AfterThrowing` advice run? Is the `RuntimeException` suppressed or does it propagate? Now describe the scenario where you want `@AfterThrowing` to run for ALL exceptions but only access the exception as the declared type in some cases — what is the correct parameter type to declare, and how do you handle the subtype check?

**Q2.** An `@Around` advice calls `pjp.proceed(newArgs)` to pass modified arguments to the target method. Describe the JVM-level mechanism that makes this possible: how does `ReflectiveMethodInvocation.proceed()` use the provided args array? What type safety checks does Spring perform on the `newArgs`? And describe a production use case where modifying method arguments in `@Around` is useful — for example, input sanitisation or argument enrichment — along with the risks if the argument types in `newArgs` do not match the method's declared parameter types.
