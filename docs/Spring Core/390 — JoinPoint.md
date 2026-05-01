---
layout: default
title: "JoinPoint"
parent: "Spring Core"
nav_order: 390
permalink: /spring/joinpoint/
number: "390"
category: Spring Core
difficulty: ★★☆
depends_on: "Aspect, Advice, Pointcut, AOP (Aspect-Oriented Programming)"
used_by: "Advice, Weaving"
tags: #intermediate, #spring, #architecture, #pattern
---

# 390 — JoinPoint

`#intermediate` `#spring` `#architecture` `#pattern`

⚡ TL;DR — A **JoinPoint** is the context object passed to Advice methods — it represents the specific method execution being intercepted and provides access to the method name, arguments, target object, and proxy. `ProceedingJoinPoint` (for `@Around`) additionally allows calling the real method with `proceed()`.

| #390            | Category: Spring Core                                              | Difficulty: ★★☆ |
| :-------------- | :----------------------------------------------------------------- | :-------------- |
| **Depends on:** | Aspect, Advice, Pointcut, AOP (Aspect-Oriented Programming)        |                 |
| **Used by:**    | Advice, Weaving                                                    |                 |

---

### 📘 Textbook Definition

In AOP, a **JoinPoint** is a specific point in the execution of a program where an Aspect's Advice can be applied. In Spring AOP (proxy-based, method execution only), every intercepted method call is a JoinPoint. The `JoinPoint` interface (from `org.aspectj.lang`) is passed as the first parameter to `@Before`, `@After`, `@AfterReturning`, and `@AfterThrowing` advice methods and provides: `getArgs()` — the method arguments; `getTarget()` — the target object (original bean); `getThis()` — the proxy object; `getSignature()` — a `MethodSignature` with method name, return type, parameter types; `getSourceLocation()` — source file/line (compile-time weaving only). The `ProceedingJoinPoint` interface extends `JoinPoint` and is used only in `@Around` advice — it adds `proceed()` (call the real method with original args) and `proceed(Object[] args)` (call with modified args). Unlike full AspectJ which supports many join point types (field access, constructor execution), Spring AOP's JoinPoints are exclusively method executions on Spring-managed beans called through the proxy.

---

### 🟢 Simple Definition (Easy)

A JoinPoint is the "info object" passed to Advice code — it tells you which method is being intercepted, what arguments it received, and who the caller is. In `@Around`, the `ProceedingJoinPoint` also lets you call the real method.

---

### 🔵 Simple Definition (Elaborated)

When your Advice code runs, it needs context: which method triggered it, what arguments were passed, which object is being called, and which proxy intercepted the call. The JoinPoint provides all of this. For logging, you use `jp.getSignature().getName()` to get the method name. For argument inspection, you use `jp.getArgs()`. For identifying the target bean's class, you use `jp.getTarget().getClass()`. In `@Around` advice specifically, `ProceedingJoinPoint` is used instead — it has all the same information plus the crucial `proceed()` method that actually calls the real method on the target. Without calling `proceed()`, the real method never executes — your Advice must decide whether to call it, when to call it, and what arguments to pass.

---

### 🔩 First Principles Explanation

**JoinPoint interface — available data:**

```java
public interface JoinPoint {
    // The method being called (as Signature object)
    Signature getSignature();
    // For method execution: cast to MethodSignature for full details

    // Method arguments (Object[] — untyped)
    Object[] getArgs();

    // The TARGET object (the real bean — not the proxy)
    Object getTarget();

    // The PROXY object (the CGLIB or JDK proxy)
    Object getThis();

    // Human-readable description of the join point
    String toString();
    String toShortString();
    String toLongString();
}

// MethodSignature (most common join point type in Spring):
MethodSignature sig = (MethodSignature) jp.getSignature();
sig.getName();           // "placeOrder"
sig.getReturnType();     // Order.class
sig.getParameterTypes(); // [OrderRequest.class]
sig.getMethod();         // java.lang.reflect.Method object
sig.getDeclaringType();  // OrderService.class (declaring class)
```

**`getTarget()` vs `getThis()` — understanding the difference:**

```java
@Aspect
@Component
class DiagnosticAspect {
    @Before("execution(* com.example.service.*.*(..))")
    void diagnose(JoinPoint jp) {
        Object target = jp.getTarget(); // OrderService@123 (real bean)
        Object proxy  = jp.getThis();   // OrderService$$CGLIB@456 (proxy)

        // target: used to access the real bean's class, fields, state
        // jp.getThis(): the proxy — use when you need to pass a reference
        //               to the bean that goes through AOP

        log.info("Target class: {}", target.getClass().getSimpleName());
        // → "OrderService"

        log.info("Proxy class: {}", proxy.getClass().getSimpleName());
        // → "OrderService$$EnhancerBySpringCGLIB$$abc"
    }
}
```

**`ProceedingJoinPoint` — the @Around extension:**

```java
public interface ProceedingJoinPoint extends JoinPoint {
    // Call the real method with original arguments
    Object proceed() throws Throwable;

    // Call the real method with REPLACED arguments
    Object proceed(Object[] args) throws Throwable;
}

// Using proceed() — the three patterns:
@Around("execution(* com.example.service.*.*(..))")
public Object aroundExample(ProceedingJoinPoint pjp) throws Throwable {
    // Pattern 1: simple pre/post wrapping
    Object result = pjp.proceed(); // call with original args
    return result;

    // Pattern 2: modify arguments
    Object[] originalArgs = pjp.getArgs();
    Object[] sanitisedArgs = sanitise(originalArgs); // e.g., trim strings
    Object result = pjp.proceed(sanitisedArgs); // call with new args
    return result;

    // Pattern 3: modify return value
    Object result = pjp.proceed();
    return enrich(result); // transform the result

    // Pattern 4: skip the method entirely (circuit open)
    if (circuitOpen()) return fallbackValue();
    return pjp.proceed();
}
```

**Accessing typed arguments via MethodSignature:**

```java
@Before("execution(* com.example.service.OrderService.placeOrder(..))")
public void beforePlaceOrder(JoinPoint jp) {
    MethodSignature sig = (MethodSignature) jp.getSignature();

    // Get typed access to arguments
    String[] paramNames = sig.getParameterNames(); // ["order"] (needs debug info)
    Object[] args       = jp.getArgs();

    // Match param name to arg value
    for (int i = 0; i < paramNames.length; i++) {
        if ("order".equals(paramNames[i])) {
            Order order = (Order) args[i];
            log.info("Placing order: orderId={}, customerId={}",
                order.getId(), order.getCustomerId());
        }
    }
}
// Note: paramNames available only if compiled with -parameters flag
// or Spring has debug info. Alternatively, bind via args() in Pointcut.
```

---

### ❓ Why Does This Exist (Why Before What)

WITHOUT JoinPoint:

What breaks without it:
1. Advice code is context-blind — it cannot know which method triggered it, what arguments were passed, or which object was called.
2. Cannot write generic Advice that behaves differently based on the method being intercepted.
3. Cannot access method metadata for logging, auditing, or security decisions.
4. `@Around` cannot call the real method — the core purpose of `@Around` is impossible.

WITH JoinPoint:
→ Advice is context-aware — one generic Advice method handles all matched methods dynamically.
→ Method name, signature, arguments, and target are available for logging, auditing, metrics, and conditional logic.
→ `ProceedingJoinPoint.proceed()` gives `@Around` complete control over the method invocation.
→ `proceed(args)` enables argument modification for input validation, sanitisation, or enrichment.

---

### 🧠 Mental Model / Analogy

> Think of JoinPoint as the "call ticket" given to a quality controller at a factory checkpoint. The ticket says: which assembly line (method name), what parts were submitted (arguments), which factory built it (target bean class), and which inspector is reviewing it (proxy). The quality controller uses this ticket to decide what checks to apply and to record what happened. A `ProceedingJoinPoint` is a special call ticket that also includes a button labelled "Continue to next stage" (`proceed()`) — the quality controller can press it to let the item continue down the assembly line, or withhold it to redirect the item.

"Call ticket" = JoinPoint object
"Which assembly line" = `jp.getSignature().getName()` (method name)
"What parts were submitted" = `jp.getArgs()` (method arguments)
"Which factory built it" = `jp.getTarget().getClass()` (target bean class)
"Continue to next stage button" = `ProceedingJoinPoint.proceed()`
"Pressing the button with replacement parts" = `pjp.proceed(newArgs)`

---

### ⚙️ How It Works (Mechanism)

**How JoinPoint is constructed and passed to Advice:**

```
When a proxied method is called:
  1. Proxy intercepts the call
  2. Spring builds a ReflectiveMethodInvocation:
     - method:   java.lang.reflect.Method object
     - target:   the real bean
     - args:     Object[] of method arguments
     - proxy:    the proxy object
  3. For each Advice in the chain:
     → Wraps ReflectiveMethodInvocation as a JoinPoint
     → Passes to advice method as first parameter (if declared)
  4. For @Around: the ProceedingJoinPoint wraps the invocation
     → pjp.proceed() calls invocation.proceed()
     → invocation.proceed() calls the next interceptor or the real method

ReflectiveMethodInvocation.proceed():
  if (interceptorIndex == interceptors.size() - 1) {
      return invokeJoinpoint(); // call the real method on target
  }
  return interceptors[++interceptorIndex].invoke(this); // next interceptor
```

---

### 🔄 How It Connects (Mini-Map)

```
Pointcut
(selects which methods to intercept)
        │
        ▼
JoinPoint  ◄──── (you are here)
(runtime context for a specific matched method execution)
        │
        ├──── getSignature()  → method name, return type, params
        ├──── getArgs()       → method arguments
        ├──── getTarget()     → the real bean
        ├──── getThis()       → the proxy
        │
        ▼
ProceedingJoinPoint (extends JoinPoint, for @Around only)
        │
        └──── proceed()       → calls the real method
        └──── proceed(args)   → calls with replaced args
        │
        ▼
Advice method
(uses JoinPoint to implement context-aware cross-cutting behaviour)
```

---

### 💻 Code Example

**Complete audit logging using JoinPoint context:**

```java
@Aspect
@Component
public class AuditAspect {

    @Autowired private AuditService auditService;

    @Around("@annotation(audited)")
    public Object audit(ProceedingJoinPoint pjp, Audited audited) throws Throwable {
        MethodSignature sig   = (MethodSignature) pjp.getSignature();
        String methodName     = sig.getDeclaringType().getSimpleName()
                              + "." + sig.getName();
        Object[] args         = pjp.getArgs();
        String currentUser    = SecurityContextHolder.getContext()
                                   .getAuthentication().getName();

        // Record before execution
        AuditEntry entry = auditService.beginAudit(
            currentUser, methodName, args, audited.action());

        try {
            Object result = pjp.proceed(); // call the real method

            // Record successful outcome
            auditService.recordSuccess(entry, result);
            return result;

        } catch (Exception ex) {
            // Record failure
            auditService.recordFailure(entry, ex.getMessage());
            throw ex; // rethrow — don't suppress
        }
    }
}

// Usage: any @Service method annotated with @Audited is automatically audited
@Service
class UserService {
    @Audited(action = "USER_CREATION")
    public User createUser(CreateUserRequest req) {
        return userRepository.save(new User(req));
        // AuditAspect: logs entry, calls createUser(), logs result/error
    }
}
```

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| `jp.getTarget()` returns the proxy | `getTarget()` returns the REAL bean (the target of the proxy, not the proxy itself). To get the proxy, use `jp.getThis()`. Use `getTarget()` when you need the actual bean's class or fields |
| Modifying `jp.getArgs()[0]` changes what the method receives | `getArgs()` returns a reference to the args array. Modifying elements of this array DOES affect what gets passed to the method — this is intentional but potentially surprising. In `@Around`, use `pjp.proceed(modifiedArgs)` for clarity |
| `JoinPoint` can be used in `@Around` advice | `@Around` must use `ProceedingJoinPoint`, not plain `JoinPoint` — the `proceed()` method is only available on `ProceedingJoinPoint`. Spring will throw `IllegalStateException` if `JoinPoint` is used in `@Around` |
| `JoinPoint.getSignature().getName()` includes the class name | `getSignature().getName()` returns only the method name (e.g., `"placeOrder"`). For the full name including class, use `getSignature().toShortString()` (`"OrderService.placeOrder(..)"`), or `toLongString()` for full return type and parameters |

---

### 🔥 Pitfalls in Production

**Accessing `jp.getArgs()` and modifying the array — side effect on original invocation**

```java
// BAD: modifying args array directly is mutation of shared state
@Before("execution(* com.example.service.*.*(..))")
public void sanitiseArgs(JoinPoint jp) {
    Object[] args = jp.getArgs();
    for (int i = 0; i < args.length; i++) {
        if (args[i] instanceof String s) {
            args[i] = s.trim(); // modifies the shared args array!
            // In Spring AOP, this DOES affect what the target method receives
            // but the behaviour is undefined and proxy-type-dependent
        }
    }
}

// GOOD: use @Around with pjp.proceed(newArgs) for safe argument modification
@Around("execution(* com.example.service.*.*(..))")
public Object sanitiseArgs(ProceedingJoinPoint pjp) throws Throwable {
    Object[] originalArgs = pjp.getArgs();
    Object[] sanitisedArgs = Arrays.copyOf(originalArgs, originalArgs.length);
    for (int i = 0; i < sanitisedArgs.length; i++) {
        if (sanitisedArgs[i] instanceof String s) {
            sanitisedArgs[i] = s.trim();
        }
    }
    return pjp.proceed(sanitisedArgs); // explicit, safe, clear
}
```

---

### 🔗 Related Keywords

- `Advice` — the method in which JoinPoint is used as a parameter
- `Pointcut` — selects which methods become JoinPoints for the Advice
- `Aspect` — the class containing the Advice methods that receive JoinPoint
- `AOP (Aspect-Oriented Programming)` — the paradigm defining JoinPoint's conceptual role
- `Weaving` — the process that creates the proxy which captures and exposes JoinPoints

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ jp.getSignature() │ Method name, class, return type      │
│ jp.getArgs()      │ Method arguments (Object[])          │
│ jp.getTarget()    │ Real bean (NOT the proxy)            │
│ jp.getThis()      │ The proxy object                     │
├───────────────────┴───────────────────────────────────────┤
│ ProceedingJoinPoint (@Around only):                       │
│ pjp.proceed()         → call method with original args   │
│ pjp.proceed(newArgs)  → call method with replaced args   │
├───────────────────────────────────────────────────────────┤
│ @Around MUST use ProceedingJoinPoint, not JoinPoint       │
├───────────────────────────────────────────────────────────┤
│ ONE-LINER │ "JoinPoint = the call ticket: method name,   │
│           │  args, target. PJP adds the 'proceed' button."│
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** `ProceedingJoinPoint.proceed(Object[] args)` allows modifying arguments before the real method is called. Describe the type safety rules: if the original method signature is `placeOrder(Long orderId, OrderRequest req)` and you pass `proceed(new Object[]{"not-a-long", req})`, what happens? Does Spring/AspectJ validate argument types at the point of `proceed()` call, at the proxy level, or at the actual method invocation via reflection? And what exception is thrown — `ClassCastException`, `IllegalArgumentException`, or something else — and at what stack level?

**Q2.** `JoinPoint.getSignature()` returns a `MethodSignature` in Spring AOP (method execution join points). `MethodSignature.getParameterNames()` may return `null` if the bytecode was compiled without the `-parameters` flag. Describe the Java compilation flag that enables parameter name retention in bytecode, explain why Spring MVC's `@RequestParam` without a `value` attribute requires this flag (or the Spring `LocalVariableTableParameterNameDiscoverer` ASM-based fallback), and identify why AOP-based parameter-name binding via `args(paramName)` in Pointcut expressions also depends on this metadata.
