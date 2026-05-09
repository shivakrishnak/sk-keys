---
version: 1
layout: default
title: "Advice"
parent: "Spring Core"
grand_parent: "Technical Dictionary"
nav_order: 36
permalink: /spring/advice/
id: SPR-036
category: Spring Core
difficulty: ★★☆
depends_on: AOP, Aspect, Pointcut, JoinPoint, CGLIB Proxy
used_by: "@Transactional, @Cacheable, Logging, Security, Retry"
related: Aspect, Pointcut, JoinPoint, ProceedingJoinPoint, "@Around"
tags:
  - spring
  - springboot
  - intermediate
  - pattern
  - bestpractice
---

# SPR-036 - Advice

⚡ TL;DR - Advice is the code that runs at a matched join point in Spring AOP - `@Before` (pre-method), `@After` (always post), `@AfterReturning` (post on success), `@AfterThrowing` (post on exception), `@Around` (wraps the entire call with full control).

| #388            | Category: Spring Core                                     | Difficulty: ★★☆ |
| :-------------- | :-------------------------------------------------------- | :-------------- |
| **Depends on:** | AOP, Aspect, Pointcut, JoinPoint, CGLIB Proxy             |                 |
| **Used by:**    | @Transactional, @Cacheable, Logging, Security, Retry      |                 |
| **Related:**    | Aspect, Pointcut, JoinPoint, ProceedingJoinPoint, @Around |                 |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
You need to start a timer before a method executes and log the duration after it returns. Without Advice types, you have one generic "intercept" hook and must manually check whether you're before or after the real method. Differentiating "success return" from "exception throw" requires try/catch scaffolding. Choosing not to call the real method requires a boolean flag system. A structured set of Advice types - Before, After, AfterReturning, AfterThrowing, Around - makes common interception patterns first-class.

**THE INVENTION MOMENT:**
"Advice types are the vocabulary of AOP - they name the exact moment and condition of interception."

---

### 📘 Textbook Definition

**Advice** in Spring AOP is the action taken by an Aspect at a particular join point. Spring supports five types: **@Before** - executes before the method; cannot prevent execution unless throwing an exception. **@AfterReturning** - executes after the method returns normally; receives the return value. **@AfterThrowing** - executes after the method throws an exception; receives the exception. **@After** - executes after the method regardless of outcome (finally-block semantics). **@Around** - wraps the entire method call; controls invocation via `ProceedingJoinPoint.proceed()`; can prevent execution, modify arguments, modify the return value, and suppress or replace exceptions. `@Around` is the most powerful and the most commonly used for any non-trivial cross-cutting concern.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
Advice is "the code that runs" - the five types give you precise control over _when_ in the method lifecycle your cross-cutting code executes.

**One analogy:**

> Advice types are like event handlers for a method's lifecycle. `@Before` = "method starting" event. `@AfterReturning` = "method succeeded" event. `@AfterThrowing` = "method failed" event. `@After` = "method completed" event (always). `@Around` = a wrapper that handles all events with full control, including deciding whether to even trigger the "method started" event.

**One insight:**
`@Around` can do everything the other four do - but each specific type expresses intent more clearly. `@AfterReturning` communicates "I only care about success." `@AfterThrowing` communicates "I only care about failures." Choosing the right Advice type makes the Aspect self-documenting.

---

### 🔩 First Principles Explanation

**CORE INVARIANTS:**

1. `@Before` cannot prevent method execution (short of throwing an exception itself).
2. `@AfterReturning` receives the actual return value - but cannot modify it. `@Around` can modify the return value.
3. `@AfterThrowing` receives the exception - but cannot suppress it. `@Around` can suppress exceptions.
4. `@After` runs regardless of success or exception - like a `finally` block.
5. `@Around` must call `pjp.proceed()` to invoke the target; not calling it skips the target entirely.
6. Only `@Around` receives `ProceedingJoinPoint`; others receive `JoinPoint`.

**ADVICE EXECUTION ORDER (around one method):**

```
@Around before-part
    @Before
        [method execution]
    @AfterReturning OR @AfterThrowing
    @After
@Around after-part
```

**THE TRADE-OFFS:**

**Using specific advice types (@Before, @AfterReturning):** More readable, less error-prone (can't accidentally skip `proceed()` call), expresses intent.

**Using @Around for everything:** Maximum flexibility, but more boilerplate (must call `proceed()`), easier to make mistakes (forget to return the result).

---

### 🧪 Thought Experiment

**SETUP:**
You're implementing a caching aspect. The cache check must happen BEFORE the real method. Cache store must happen AFTER, but only on success (not exception). Cache invalidation on certain methods.

**WHY @Around IS NEEDED (not just @Before + @AfterReturning):**

```
@Before: check cache
    if found → return cached value?  ← IMPOSSIBLE with @Before (can't return early)
    if not found → continue

@AfterReturning: store in cache ← OK

But @Before cannot short-circuit - @Around is required for conditional execution
```

**WITH @Around:**

```java
@Around("@annotation(Cacheable)")
public Object cache(ProceedingJoinPoint pjp) throws Throwable {
    String key = generateKey(pjp);
    Object cached = cacheStore.get(key);
    if (cached != null) return cached;  // short-circuit - no real method call!

    Object result = pjp.proceed();       // call real method
    cacheStore.put(key, result);         // store result
    return result;
}
```

**THE INSIGHT:**
`@Before` + `@AfterReturning` together CANNOT implement caching because they can't communicate a return value between them, and neither can short-circuit the method. `@Around` is necessary when the advice needs to conditionally skip or substitute the real method call.

---

### 🧠 Mental Model / Analogy

> The five Advice types are like different roles in a restaurant kitchen pass-through system. `@Before` is the expeditor checking tickets before dishes leave - they can flag problems but can't take the food back. `@AfterReturning` is quality control at the exit - they inspect successful dishes. `@AfterThrowing` is the incident report handler - they only activate when something is sent back. `@After` is the cleanup crew - they always show up regardless of outcome. `@Around` is the head chef - they see everything, can modify the dish, can refuse to send it out, and control the entire flow.

- "Expeditor" → `@Before` - pre-check, can't prevent unless it fails loudly
- "Quality control" → `@AfterReturning` - sees returned value
- "Incident handler" → `@AfterThrowing` - sees the exception
- "Cleanup crew" → `@After` - always runs
- "Head chef" → `@Around` - full control

---

### 📶 Gradual Depth - Four Levels

**Level 1 - What it is (anyone can understand):**
Advice is the code inside an Aspect that actually does something. The five types tell Spring exactly when to run your code: before the method, after success, after failure, always after, or fully wrapped around.

**Level 2 - How to use it (junior developer):**
Choose the right type:

- `@Before` for validation, security pre-checks
- `@AfterReturning` for audit on success (with `returning` param for the result)
- `@AfterThrowing` for error tracking, alerting (with `throwing` param for exception)
- `@After` for cleanup that must always run (like a `finally`)
- `@Around` for caching, retry, timing, or anything needing to control execution flow

**Level 3 - How it works (mid-level engineer):**
Each advice annotation is processed by `ReflectiveAspectJAdvisorFactory` into a corresponding interceptor: `@Before` → `AspectJMethodBeforeAdvice`, `@AfterReturning` → `AspectJAfterReturningAdvice`, `@AfterThrowing` → `AspectJAfterThrowingAdvice`, `@After` → `AspectJAfterAdvice`, `@Around` → `AspectJAroundAdvice`. All implement `MethodInterceptor` (CGLIB callback interface). At call time, `ReflectiveMethodInvocation.proceed()` chains them in order. For `@Around`, the advice method receives `ProceedingJoinPoint`, which has a `proceed()` that calls the next interceptor in the chain (or the real method if it's the last).

**Level 4 - Why it was designed this way (senior/staff):**
The five Advice types map to AspectJ's semantics (borrowed verbatim). The separation exists because each type enables different guarantees: `@Before` cannot accidentally swallow exceptions thrown by the target. `@AfterReturning` is guaranteed to have the return value. `@AfterThrowing` is guaranteed to have the exception. These guarantees make advice more predictable and reduce bugs. The power of `@Around` comes at the cost of these guarantees - the developer must explicitly call `pjp.proceed()` and return its result. This is why Spring's own built-in aspects (`TransactionInterceptor`, `CacheInterceptor`) all use the equivalent of `@Around` - they need full execution control. Application developers should prefer the specific types over `@Around` wherever possible, both for clarity and to avoid the common bug of forgetting to return `pjp.proceed()`'s result.

---

### ⚙️ How It Works (Mechanism)

**Advice execution chain for one method call:**

```
proxy.save(user)
    ↓
ReflectiveMethodInvocation.proceed()
    ↓
Chain traversal (interceptors in order):
  [0] ExposeInvocationInterceptor
  [1] AspectJAroundAdvice (@Around)
        → advice-before-part executes
        → calls pjp.proceed() → [2]
  [2] AspectJMethodBeforeAdvice (@Before)
        → advice executes
        → calls invocation.proceed() → [3]
  [3] AspectJAfterAdvice (@After)
        → wraps [4] in try/finally
        → calls invocation.proceed() → [4]
  [4] AspectJAfterReturningAdvice (@AfterReturning)
        → wraps [5], captures return value
        → calls invocation.proceed() → [5]
  [5] AspectJAfterThrowingAdvice (@AfterThrowing)
        → wraps [real method], captures exceptions
  [6] REAL METHOD → target.save(user)
        ↑ result propagates back up chain
  [5] no exception → skip, return result
  [4] AfterReturning advice runs with result
  [3] After advice (finally) runs
  [2] Before advice already ran (nothing after)
  [1] Around after-part executes with result
    ↓
result returned to caller
```

---

### 🔄 The Complete Picture - End-to-End Flow

**NORMAL FLOW:**

```
Method call intercepted by proxy
    ↓
@Around before part runs
    ↓
@Before advice runs ← YOU ARE HERE (Advice executes)
    ↓
Target method executes
    ↓
@AfterReturning runs (success path)
    ↓
@After runs (always)
    ↓
@Around after part runs
    ↓
Return result
```

**EXCEPTION FLOW:**

```
Method call intercepted
    ↓
@Around before part runs
    ↓
@Before advice runs
    ↓
Target method throws exception
    ↓
@AfterThrowing runs (exception path)
    ↓
@After runs (always - like finally)
    ↓
@Around can catch and handle the exception
    ↓
Exception propagated (or suppressed by @Around)
```

---

### 💻 Code Example

**Example 1 - All five advice types on one aspect:**

```java
@Aspect
@Component
public class MethodLifecycleAspect {

    // 1. @Before - runs before method, cannot short-circuit
    @Before("execution(* com.example.service.*.*(..))")
    public void beforeMethod(JoinPoint jp) {
        log.debug("BEFORE: {}", jp.getSignature().getName());
    }

    // 2. @AfterReturning - runs on success, receives return value
    @AfterReturning(
        pointcut = "execution(* com.example.service.*.*(..))",
        returning = "result"
    )
    public void afterReturning(JoinPoint jp, Object result) {
        log.debug("RETURNED: {} → {}", jp.getSignature().getName(), result);
    }

    // 3. @AfterThrowing - runs on exception, receives the exception
    @AfterThrowing(
        pointcut = "execution(* com.example.service.*.*(..))",
        throwing = "ex"
    )
    public void afterThrowing(JoinPoint jp, Exception ex) {
        log.error("THREW: {} → {}", jp.getSignature().getName(), ex.getMessage());
    }

    // 4. @After - runs always (like finally)
    @After("execution(* com.example.service.*.*(..))")
    public void afterMethod(JoinPoint jp) {
        log.debug("AFTER (always): {}", jp.getSignature().getName());
    }

    // 5. @Around - full control
    @Around("execution(* com.example.service.*.*(..))")
    public Object aroundMethod(ProceedingJoinPoint pjp) throws Throwable {
        long start = System.nanoTime();
        try {
            Object result = pjp.proceed();  // MUST call this!
            long ms = (System.nanoTime() - start) / 1_000_000;
            log.debug("AROUND: {} took {}ms", pjp.getSignature().getName(), ms);
            return result;  // MUST return this!
        } catch (Throwable t) {
            log.error("AROUND exception: {}", t.getMessage());
            throw t;
        }
    }
}
```

**Example 2 - @Around for caching (demonstrates short-circuit):**

```java
@Aspect
@Component
public class CachingAspect {

    private final Map<String, Object> cache = new ConcurrentHashMap<>();

    @Around("@annotation(com.example.annotation.Cacheable)")
    public Object cacheResult(ProceedingJoinPoint pjp) throws Throwable {
        String key = pjp.getSignature().toLongString()
            + Arrays.toString(pjp.getArgs());

        Object cached = cache.get(key);
        if (cached != null) {
            log.debug("Cache HIT: {}", key);
            return cached;  // short-circuit - real method NOT called
        }

        Object result = pjp.proceed();  // real method called
        cache.put(key, result);
        log.debug("Cache MISS + stored: {}", key);
        return result;
    }
}
```

---

### ⚖️ Comparison Table

| Advice Type       | When Runs       | Can Short-Circuit     | Receives Return | Receives Exception | Use For                              |
| ----------------- | --------------- | --------------------- | --------------- | ------------------ | ------------------------------------ |
| `@Before`         | Before method   | No (only by throwing) | No              | No                 | Validation, security pre-check       |
| `@AfterReturning` | After success   | No                    | Yes             | No                 | Audit on success, caching            |
| `@AfterThrowing`  | After exception | No                    | No              | Yes                | Error alerting, compensation         |
| `@After`          | Always after    | No                    | No              | No                 | Cleanup, resource release            |
| `@Around`         | Wraps all       | Yes                   | Yes (return it) | Yes (catch it)     | Caching, retry, timing, full control |

---

### ⚠️ Common Misconceptions

| Misconception                               | Reality                                                                                                                                                 |
| ------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------- |
| @Around must call pjp.proceed()             | Not required - you can return any value without calling proceed() (effectively replacing the method). But unintentionally omitting it is a serious bug. |
| @After runs only on success                 | @After runs always - it's like a finally block. For success-only, use @AfterReturning.                                                                  |
| @Before can prevent method execution        | @Before cannot prevent execution unless it throws an exception itself. To conditionally skip execution, use @Around.                                    |
| @AfterReturning can modify the return value | It receives the return value but cannot modify it. Use @Around and return a different value from pjp.proceed().                                         |

---

### 🚨 Failure Modes & Diagnosis

**@Around returns null (forgot to return pjp.proceed())**

**Symptom:**
Methods return `null` unexpectedly despite the real implementation returning a valid object.

**Root Cause:**
`@Around` advice calls `pjp.proceed()` but doesn't return its result:

```java
@Around("...")
public Object doAround(ProceedingJoinPoint pjp) throws Throwable {
    pjp.proceed();   // called but result discarded!
    // returns null implicitly
}
```

**Fix:**

```java
@Around("...")
public Object doAround(ProceedingJoinPoint pjp) throws Throwable {
    Object result = pjp.proceed();
    // ... post-processing ...
    return result;  // MUST return the result
}
```

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**

- `AOP` - Advice is the action part of AOP
- `Aspect` - contains the Advice and Pointcut
- `Pointcut` - specifies WHICH methods receive the Advice

**Builds On This (learn these next):**

- `JoinPoint` - the execution context available inside Advice
- `Pointcut` - the matching logic that selects which calls receive the Advice

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ @Before        │ Before method; no short-circuit         │
│ @AfterReturning│ On success; receives return value       │
│ @AfterThrowing │ On exception; receives exception        │
│ @After         │ Always (finally semantics)              │
│ @Around        │ Wraps all; full control via pjp.proceed()│
├────────────────┼─────────────────────────────────────────┤
│ KEY INSIGHT    │ @Around can do everything, but specific  │
│                │ types express intent more clearly       │
├────────────────┼─────────────────────────────────────────┤
│ COMMON BUG     │ @Around forgetting to return            │
│                │ pjp.proceed() → method returns null     │
├────────────────┼─────────────────────────────────────────┤
│ ONE-LINER      │ "The code that runs at a join point -   │
│                │  pick the type that fits your need."    │
└────────────────┴─────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** `@Around` is the most powerful Advice type - it can prevent the real method from running, modify arguments, and modify the return value. But all of `@Before`, `@AfterReturning`, `@AfterThrowing`, and `@After` can be simulated with `@Around`. Why do the other types exist? Is there any scenario where a specific type provides a behavioral guarantee that `@Around` cannot?

**Q2.** You have an `@Around` advice that catches ALL exceptions (`catch (Throwable t)`) and returns null instead of rethrowing. What are the consequences for `@AfterThrowing` and `@After` advice in the same aspect chain? Does `@AfterThrowing` still run? Does the caller see an exception or null?
