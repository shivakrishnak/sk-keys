---
layout: default
title: "Advice"
parent: "Spring Core"
nav_order: 388
permalink: /spring/advice/
number: "388"
category: Spring Core
difficulty: ★★☆
depends_on: "Aspect, AOP, JoinPoint, Pointcut"
used_by: "@Transactional internals, @Cacheable, Custom aspects, Spring Security"
tags: #java, #spring, #intermediate, #pattern
---

# 388 — Advice

`#java` `#spring` `#intermediate` `#pattern`

⚡ TL;DR — The action an aspect takes at a join point — defined by type (@Before, @After, @Around, @AfterReturning, @AfterThrowing) and by what it does before, after, or around the target method.

| #388 | category: Spring Core
|:---|:---|:---|
| **Depends on:** | Aspect, AOP, JoinPoint, Pointcut | |
| **Used by:** | @Transactional internals, @Cacheable, Custom aspects, Spring Security | |

---

### 📘 Textbook Definition

**Advice** is the action taken by an aspect at a particular join point. Spring AOP supports five advice types: `@Before` (executes before the join point), `@AfterReturning` (executes after normal return with access to the return value), `@AfterThrowing` (executes when the method throws an exception), `@After` (always executes after the join point, like `finally`), and `@Around` (completely surrounds the join point — most powerful, controls whether and how the target proceeds). Each advice method receives a `JoinPoint` (or `ProceedingJoinPoint` for `@Around`) providing access to the target object, method signature, arguments, and proxy. Advice methods are invoked by the proxy's interceptor chain in `@Order`-defined sequence.

---

### 🟢 Simple Definition (Easy)

Advice is the code an aspect runs. "Before" advice runs before the method. "After" runs after. "Around" runs both and can change the result. Think of it as the interceptor action.

---

### 🔵 Simple Definition (Elaborated)

An aspect defines WHERE to intercept (pointcut) and WHAT to do there (advice). The five advice types cover every lifecycle point of a method call: before entry, after normal exit (with the return value), after an exception, always after (like a finally block), and wrapping the entire call. `@Around` is the most powerful — it controls whether the target method runs at all, can modify arguments, replace the return value, or swallow exceptions. `@Transactional` is implemented entirely as `@Around` advice: it opens a transaction before `proceed()`, calls your real method, then commits or rolls back after.

---

### 🔩 First Principles Explanation

**The five advice types — covering every invocation lifecycle point:**

```
Method call lifecycle:                  Advice type:
─────────────────────────────────────────────────────────
→ Before method entry               @Before
→ Method executes (normal)          → target.method()
→ After normal return               @AfterReturning(returning)
→ After exception thrown            @AfterThrowing(throwing)
→ After either (normal or ex)       @After  (like finally)
─────────────────────────────────────────────────────────
OR: entire lifecycle wrapped        @Around (intercepts all)
─────────────────────────────────────────────────────────
```

**Execution order within a single aspect:**

```
@Around before
  → @Before
    → target.method() executes
      ← @AfterReturning (or @AfterThrowing)
      ← @After
  ← @Around after
```

---

### ❓ Why Does This Exist (Why Before What)

**WITHOUT different advice types:**

```
Without distinct advice types (only @Around exists):

  Every interceptor must manually:
  try {
    doBeforeLogic();      // @Before equivalent
    Object result = jp.proceed();
    doAfterReturning(result); // @AfterReturning equiv
    return result;
  } catch (Exception e) {
    doAfterThrowing(e);   // @AfterThrowing equivalent
    throw e;
  } finally {
    doAfterAlways();      // @After equivalent
  }
  → Verbose, error-prone — must always remember rethrow
  → No static typing for return value or exception type
```

**WITH distinct advice annotations:**

```
→ @AfterReturning: type-safe access to return value
  (impossible with @Around without reflection)
→ @AfterThrowing: type-safe access to thrown exception
→ @After: clean finally-equivalent — no try/catch needed
→ @Before: simpler — no need to call proceed()
→ @Around: full control — use only when needed
→ Mistakes prevented: @AfterReturning can't accidentally
  swallow exceptions (@Around with catch can)
```

---

### 🧠 Mental Model / Analogy

> The five advice types are like the **five roles in a surgical procedure**: the pre-op nurse preps the patient before surgery starts (@Before). The surgeon performs the operation (@Around / proceed). The recovery nurse monitors the patient after a successful operation (@AfterReturning). The emergency team handles complications (@AfterThrowing). The post-op coordinator always debriefs regardless of outcome (@After / finally). Each role is specialised. Only the surgeon (@Around) can decide whether the operation proceeds.

"Pre-op prep" = @Before — runs before, cannot stop method
"Surgeon deciding to proceed" = @Around pjp.proceed()
"Recovery monitoring" = @AfterReturning — normal exit only
"Emergency team" = @AfterThrowing — exception exit only
"Post-op debrief regardless" = @After — always runs

---

### ⚙️ How It Works (Mechanism)

**All five advice types with full signatures:**

```java
@Aspect
@Component
public class LifecycleAspect {
  // 1. @Before — runs before method; cannot prevent execution
  //    Can throw to prevent proceeding
  @Before("execution(* com.example.service.*.*(..))")
  public void before(JoinPoint jp) {
    log.debug("→ Entering: {}", jp.getSignature().getName());
  }

  // 2. @AfterReturning — return value available
  //    NOT called if exception is thrown
  @AfterReturning(
      pointcut  = "execution(* com.example.service.*.*(..))",
      returning = "result")
  public void afterReturn(JoinPoint jp, Object result) {
    log.debug("← Success: {} returned {}", 
        jp.getSignature().getName(), result);
  }

  // 3. @AfterThrowing — exception available
  //    Does NOT suppress the exception (unlike @Around catch)
  @AfterThrowing(
      pointcut = "execution(* com.example.service.*.*(..))",
      throwing = "ex")
  public void afterThrowing(JoinPoint jp, Exception ex) {
    log.error("✗ Exception in {}: {}",
        jp.getSignature().getName(), ex.getMessage());
  }

  // 4. @After — always runs (finally-equivalent)
  //    Runs even if @AfterThrowing also fires
  @After("execution(* com.example.service.*.*(..))")
  public void afterAlways(JoinPoint jp) {
    MDC.remove("traceId"); // always clean up MDC
  }

  // 5. @Around — full control; MUST call pjp.proceed()
  @Around("execution(* com.example.service.*.*(..))")
  public Object around(ProceedingJoinPoint pjp)
      throws Throwable {
    long start = System.nanoTime();
    Object result = pjp.proceed(); // call real method
    long elapsed = (System.nanoTime() - start) / 1_000_000;
    log.debug("{} took {}ms",
        pjp.getSignature().getName(), elapsed);
    return result; // MUST return result (or replacement)
  }
}
```

**@Around — modifying arguments and return value:**

```java
@Around("@annotation(Sanitise)")
public Object sanitiseInputs(ProceedingJoinPoint pjp)
    throws Throwable {
  Object[] args = pjp.getArgs();
  // Sanitise String arguments
  for (int i = 0; i < args.length; i++) {
    if (args[i] instanceof String s) {
      args[i] = HtmlUtils.htmlEscape(s); // sanitise
    }
  }
  Object result = pjp.proceed(args); // pass modified args

  // Optionally modify result:
  if (result instanceof String s) {
    return s.trim(); // post-process return value
  }
  return result;
}
```

---

### 🔄 How It Connects (Mini-Map)

```
ASPECT (119) defines:
        ↓
  ADVICE (120)  ← you are here
  (@Before / @After / @Around / @AfterReturning / @AfterThrowing)
        ↓
  Receives at runtime:
  JOINPOINT (122) → target, method, args, proxy
        ↓
  Selection via:
  POINTCUT (121) → "execution(*...)" matching
        ↓
  Applied as:
  MethodInterceptor in CGLIB/JDK proxy chain
        ↓
  Powers: @Transactional, @Cacheable, @Async
```

---

### 💻 Code Example

**Example 1 — @Transactional implemented as @Around advice:**

```java
// Conceptual equivalent of TransactionInterceptor:
@Around("@annotation(Transactional)")
public Object manageTransaction(ProceedingJoinPoint pjp,
                                Transactional tx)
    throws Throwable {
  TransactionStatus status =
      txManager.getTransaction(new DefaultTxDef());
  try {
    Object result = pjp.proceed();  // real method
    txManager.commit(status);
    return result;
  } catch (RuntimeException | Error e) {
    txManager.rollback(status);
    throw e;
  }
}
// This is essentially what Spring's TransactionInterceptor does
```

**Example 2 — Choosing the right advice type:**

```java
@Aspect @Component
class AuditAspect {
  // USE @AfterReturning for "log success with result"
  @AfterReturning(
      pointcut = "execution(* *..*Service.save*(..))",
      returning = "saved")
  void logSaved(JoinPoint jp, Object saved) {
    audit.record("SAVED", saved);
    // automatically NOT called on exception — correct!
  }

  // USE @AfterThrowing for "log failure with exception"
  @AfterThrowing(
      pointcut = "execution(* *..*Service.save*(..))",
      throwing  = "ex")
  void logFailed(JoinPoint jp, DataAccessException ex) {
    audit.record("FAILED", ex.getMessage());
    // exception is NOT swallowed — still propagates
  }

  // AVOID @Around just for logging — rethrow risk:
  // @Around catches Exception → easy to forget rethrow
  // → silently swallows exception → transaction commits!
}
```

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| @After runs only on successful completion | @After is a finally-equivalent — it runs after @AfterReturning AND @AfterThrowing; it always fires after the method, like a finally block |
| @Around is the most useful advice and should always be used | @Around is the most powerful but also the most risky — forgetting to call pjp.proceed() silently skips the method. Use more specific types when full control isn't needed |
| @AfterThrowing suppresses the exception | @AfterThrowing does NOT suppress exceptions — it fires after the exception escapes, but the exception still propagates. Only @Around with a catch block can suppress |
| Advice methods can be private | Advice methods must be public — Spring AOP's proxy invokes them via reflection or bytecode and requires accessible methods |

---

### 🔥 Pitfalls in Production

**1. @Around forgetting to pass modified args to proceed()**

```java
// BAD: modified args not passed to proceed()
@Around("@annotation(Validate)")
public Object validate(ProceedingJoinPoint pjp)
    throws Throwable {
  Object[] args = pjp.getArgs();
  args[0] = sanitise(args[0]); // modify first arg

  return pjp.proceed(); // passes ORIGINAL args, not modified!
}

// GOOD: pass modified args explicitly
return pjp.proceed(args); // passes sanitised args
```

**2. @Around swallowing exception — silent transaction commit**

```java
// DANGEROUS BUG: exception swallowed in @Around logging
@Around("execution(* *..*Service.*(..))")
public Object logAll(ProceedingJoinPoint pjp) throws Throwable {
  try {
    Object result = pjp.proceed();
    log.info("Success: {}", pjp.getSignature().getName());
    return result;
  } catch (Exception e) {
    log.error("Error: {}", e.getMessage());
    return null; // SWALLOWS EXCEPTION
    // @Transactional never sees exception → COMMITS!
    // DB has partial data in corrupted state
  }
}

// GOOD: always rethrow in @Around
} catch (Exception e) {
  log.error("Error: {}", e.getMessage());
  throw e; // rethrow — TransactionInterceptor can rollback
}
```

---

### 🔗 Related Keywords

- `Aspect` — the class that contains advice methods and pointcut definitions
- `JoinPoint` — the runtime context passed to every non-Around advice method
- `ProceedingJoinPoint` — the @Around variant that can call `proceed()` to invoke the target
- `Pointcut` — the expression that determines which join points receive this advice
- `@Transactional` — Spring's built-in @Around advice for transaction management
- `@Order` — controls which aspect's advice wraps which when multiple aspects match

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ KEY IDEA     │ Five types: @Before @After @Around        │
│              │ @AfterReturning @AfterThrowing —          │
│              │ each covers a different lifecycle point   │
├──────────────┼───────────────────────────────────────────┤
│ USE WHEN     │ @Before: pre-validation; @AfterReturning: │
│              │ cache/audit; @Around: timing/tx/retry     │
├──────────────┼───────────────────────────────────────────┤
│ AVOID WHEN   │ @Around when simpler types suffice;       │
│              │ never swallow exceptions in @Around catch │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "@Around is the scalpel —                 │
│              │  use it precisely or it cuts too deep."  │
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ Pointcut (121) → JoinPoint (122) →        │
│              │ @Transactional (127)                      │
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** A `@Cacheable` method is also `@Transactional`. Spring applies two aspects: `CacheInterceptor` and `TransactionInterceptor`. The cache hit (returning cached value) avoids calling the real method. But what happens to the transaction state? Describe the full interception scenario when `@Order(1)` is on `@Cacheable` (outermost) and `@Order(2)` on `@Transactional` (inner) — is a transaction opened on a cache hit? Then describe what happens when the orders are reversed — is the cache populated inside or outside the transaction boundary, and which order is correct for read-through caching?

**Q2.** `@AfterThrowing` receives the thrown exception but does NOT suppress it. However, if an `@AfterThrowing` method itself throws a different exception, the original exception is replaced. Describe the exact JVM mechanism that causes this — what happens to the original exception's stack trace — and explain the specific scenario in a distributed tracing system where an `@AfterThrowing` aspect that tries to record the error to a failed tracing backend throws its own exception, causing the original business exception to be lost from the error tracking system.

