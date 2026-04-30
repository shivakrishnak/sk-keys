---
layout: default
title: "AOP (Aspect-Oriented Programming)"
parent: "Spring Core"
nav_order: 386
permalink: /spring/aop/
number: "386"
category: Spring Core
difficulty: ★★★
depends_on: "CGLIB Proxy, JDK Dynamic Proxy, BeanPostProcessor, OOP"
used_by: "@Transactional, Spring Security, @Async, @Cacheable, Logging"
tags: #java, #spring, #internals, #advanced, #deep-dive, #pattern
---

# 386 — AOP (Aspect-Oriented Programming)

`#java` `#spring` `#internals` `#advanced` `#deep-dive` `#pattern`

⚡ TL;DR — A programming paradigm that extracts cross-cutting concerns (transactions, security, logging) into reusable modules called aspects that are applied transparently to target code.

| #386 | category: Spring Core
|:---|:---|:---|
| **Depends on:** | CGLIB Proxy, JDK Dynamic Proxy, BeanPostProcessor, OOP | |
| **Used by:** | @Transactional, Spring Security, @Async, @Cacheable, Logging | |

---

### 📘 Textbook Definition

**Aspect-Oriented Programming (AOP)** is a programming paradigm that addresses **cross-cutting concerns** — behaviour that spans multiple unrelated modules (transaction management, security, logging, metrics, retry) — by modularising them into **aspects** that are applied to target code without modifying it. Spring AOP is a proxy-based AOP implementation: rather than compile-time bytecode weaving (as in full AspectJ), it creates runtime CGLIB or JDK proxies that intercept method calls and apply advice from registered aspects. Spring AOP supports a subset of AspectJ's pointcut expression language for targeting join points. The full Spring AOP vocabulary comprises: **Aspect**, **Advice**, **Pointcut**, **Join Point**, and **Weaving**.

---

### 🟢 Simple Definition (Easy)

AOP lets you add behaviour (like "start a transaction" or "check security") to many methods without editing those methods. You define the "what" and "where" once in an aspect — Spring wires it in automatically.

---

### 🔵 Simple Definition (Elaborated)

In OOP, concerns like "open a transaction before and commit after every service method" must be written into each method — or delegated via design patterns (Template Method, Decorator). AOP externalises these concerns into aspects. An aspect defines when to intercept (pointcut), what to do before/after (advice), and Spring applies it transparently at runtime via proxy. This is exactly how `@Transactional` works: Spring has a built-in `TransactionInterceptor` aspect that applies to every `@Transactional` method — you write zero transaction-management code in your services.

---

### 🔩 First Principles Explanation

**The cross-cutting problem:**

```
Security check → repeat in every controller method
  Auth fails? → 401. OK? → proceed.

Transaction management → repeat in every service method
  Begin. Execute. Commit / rollback.

Audit logging → repeat in every data-modification method
  log("user X called method Y with args Z")

Retry logic → repeat in every network-calling method
  Try → catch → wait → retry × 3

Without AOP: 4 classes × 10 methods = 40 copies of boilerplate
With AOP:    4 aspects define the logic once
             Spring applies them via proxy to all 40 methods
```

**Spring AOP implementation — proxy-based:**

```
┌─────────────────────────────────────────────────────┐
│  SPRING AOP COMPONENTS                              │
│                                                     │
│  ASPECT — the module containing cross-cutting code  │
│  POINTCUT — expression selecting target methods     │
│  ADVICE — code to run at a join point               │
│  JOIN POINT — execution point the advice can target │
│  WEAVING — applying advice to target objects        │
│                                                     │
│  HOW PROXY INVOCATION FLOWS:                        │
│  Client → Proxy → Advice Chain → Target Method      │
│  Proxy wraps target, applies each advice in order   │
│  Client never knows a proxy is involved             │
└─────────────────────────────────────────────────────┘
```

---

### ❓ Why Does This Exist (Why Before What)

**WITHOUT AOP:**

```
Without AOP all cross-cutting concerns are scattered:

  Every service method that needs a transaction:
    + 8 lines of TransactionTemplate boilerplate
  Every controller that needs auth:
    + 3 lines of SecurityContext check
  Every repo call that needs audit:
    + 2 lines of audit log write
  Every external call that needs retry:
    + 10 lines of retry loop

  Result:
  Business logic buried in infrastructure boilerplate
  Change "log before" to "log after" → edit 50 methods
  Add new cross-cutting concern → edit all existing methods
  Test business logic → must account for all boilerplate
```

**WITH AOP:**

```
→ @Transactional is 1 annotation — zero boilerplate in service
→ @Secured("ROLE_ADMIN") is 1 annotation — zero security code
→ @Retryable(3) is 1 annotation — zero retry loops
→ Change logging strategy: edit ONE aspect, not 50 methods
→ Add new cross-cutting concern: add one aspect, zero
  changes to existing code (Open/Closed Principle)
→ Test services: mock aspect or @BeforeEach disable
```

---

### 🧠 Mental Model / Analogy

> AOP is like a **building's centralised HVAC and power system** versus individual room heaters and generators. Without AOP: each room has its own thermostat, heater, and generator — 50 rooms × 3 systems = 150 units to manage. With AOP: one HVAC system serves all rooms, activated by a thermostat trigger in each room. Change the heating algorithm: update one central system, not 50 rooms. Add air conditioning: install one central unit and connect it without touching each room.

"Centralised HVAC" = the aspect (defined once)
"Thermostat trigger in each room" = pointcut (selects target methods)
"Heating the room" = advice (code applied)
"Room requesting heat" = join point (method execution)
"Connecting HVAC to rooms" = weaving (applying aspect via proxy)

---

### ⚙️ How It Works (Mechanism)

**Spring AOP proxy interception chain:**

```
Client calls: orderService.place(req)
        ↓
  1. CGLIB proxy intercepts the call
        ↓
  2. Spring builds interceptor chain for this method:
     [SecurityInterceptor, CachingInterceptor,
      TransactionInterceptor]
        ↓
  3. Chain executes in order:
     SecurityInterceptor.invoke() → checks @Secured
     CachingInterceptor.invoke() → checks @Cacheable
     TransactionInterceptor.invoke() → begins TX
        ↓
  4. Inner call: target.place(req) (real method)
        ↓
  5. Chain unwinds:
     TransactionInterceptor → commit/rollback
     CachingInterceptor → store result
     SecurityInterceptor → (no post-action needed)
        ↓
  6. Result returned to client
```

**Spring AOP limitations vs full AspectJ:**

```
SPRING AOP:                    FULL ASPECTJ:
  Proxy-based (runtime)          Compile-time weaving
  Method execution only          Field access, constructor,
                                  static methods
  Bean methods only              Any class, any type
  Spring-managed beans only      Any Java object
  No private method interception Any method any visibility
```

**Enabling AOP:**

```java
@SpringBootApplication
// Spring Boot: AOP auto-enabled via AopAutoConfiguration

// Plain Spring:
@Configuration
@EnableAspectJAutoProxy // enables @Aspect processing
public class AppConfig {}
```

---

### 🔄 How It Connects (Mini-Map)

```
OOP defines classes + methods
        ↓
  Cross-cutting concerns emerge (tx, security, log)
        ↓
  AOP (118)  ← you are here
  (modularise cross-cutting into aspects)
        ↓
  Components:
  Aspect (119) → module containing advice + pointcut
  Advice (120) → code: @Before, @After, @Around
  Pointcut (121) → method selection expression
  JoinPoint (122) → runtime context of interception
        ↓
  Applied via:
  CGLIB Proxy (116) or JDK Proxy (117)
  (created in BPP.postProcessAfterInitialization)
        ↓
  Powers: @Transactional (127), @Async, @Cacheable,
          Spring Security method security
```

---

### 💻 Code Example

**Example 1 — Custom @Around AOP aspect for timing:**

```java
@Aspect
@Component
public class PerformanceAspect {
  private final MeterRegistry metrics;

  public PerformanceAspect(MeterRegistry metrics) {
    this.metrics = metrics;
  }

  @Around("@annotation(Timed)")         // custom annotation
  public Object timeExecution(
      ProceedingJoinPoint pjp) throws Throwable {
    long start = System.nanoTime();
    try {
      return pjp.proceed();              // call real method
    } finally {
      long elapsed = System.nanoTime() - start;
      metrics.timer(
          "method.exec",
          "class",  pjp.getTarget().getClass().getSimpleName(),
          "method", pjp.getSignature().getName()
      ).record(elapsed, TimeUnit.NANOSECONDS);
    }
  }
}

// Usage — zero code in service:
@Service
class OrderService {
  @Timed  // custom annotation — PerformanceAspect intercepts
  public Order place(OrderRequest req) {
    return orderRepo.save(Order.from(req));
  }
}
```

**Example 2 — @Before for audit logging:**

```java
@Aspect
@Component
public class AuditAspect {
  private final AuditLog auditLog;

  @Before("execution(* com.example.service.*Service.*(..))")
  public void logServiceCall(JoinPoint jp) {
    auditLog.record(
        jp.getTarget().getClass().getSimpleName(),
        jp.getSignature().getName(),
        Arrays.toString(jp.getArgs())
    );
  }
}
// Fires for every public method in all *Service classes
// Zero changes to any service class required
```

**Example 3 — AOP advice ordering with @Order:**

```java
// Multiple aspects on the same method — control order
@Aspect @Component @Order(1)  // runs outermost
class SecurityAspect {
  @Around("@annotation(Secured)")
  Object checkSecurity(ProceedingJoinPoint pjp) throws Throwable {
    verifyAuth();
    return pjp.proceed();
  }
}

@Aspect @Component @Order(2)  // runs inside security
class TransactionAspect {
  @Around("@annotation(Transactional)")
  Object manageTransaction(ProceedingJoinPoint pjp) throws Throwable {
    // Lower order number = outermost (runs first before, last after)
  }
}
// Call: Client → Security.before → TX.before → method
//       → TX.after → Security.after → Client
```

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| Spring AOP intercepts private methods | Spring AOP uses proxies — only public non-final methods on managed beans can be intercepted. Private methods are never proxied |
| AOP works on all objects, not just Spring beans | Spring AOP only applies to beans managed by the Spring container. Objects created with new are not proxied |
| @Transactional on a private method works | The proxy cannot override private methods — @Transactional on private methods is silently ignored |
| AspectJ and Spring AOP are the same | Spring AOP is proxy-based (runtime), limited to method execution. AspectJ is compile-time or load-time weaving, supports field access, constructors, static methods |
| Calling this.method() inside a bean triggers advice | Calling this. bypasses the proxy entirely — the advice is NOT applied. The real object's method runs without any AOP |

---

### 🔥 Pitfalls in Production

**1. Self-invocation bypassing aspect advice**

```java
@Service
@Transactional
public class OrderService {
  public void processAll(List<OrderRequest> reqs) {
    reqs.forEach(r -> this.place(r)); // bypasses proxy!
  }

  @Transactional(propagation = REQUIRES_NEW)
  public Order place(OrderRequest req) {
    // REQUIRES_NEW never fires — this. bypasses proxy
    return orderRepo.save(Order.from(req));
  }
}

// FIX: inject self-reference to use proxy
@Service
public class OrderService {
  @Autowired @Lazy OrderService self;

  public void processAll(List<OrderRequest> reqs) {
    reqs.forEach(r -> self.place(r)); // via proxy
  }
}
```

**2. Aspect ordering causing wrong transaction boundary**

```java
// BAD: Security check runs INSIDE transaction
// → Connection held while waiting for Auth
@Aspect @Order(2) class SecurityAspect { ... }
@Aspect @Order(1) class TxAspect { ... }
// Lower order = outer wrapper
// TX opens first → security check inside TX → wastes conn

// GOOD: Security first, then TX
@Aspect @Order(1) class SecurityAspect { ... }  // outer
@Aspect @Order(2) class TxAspect { ... }        // inner
```

---

### 🔗 Related Keywords

- `Aspect` — the module that encapsulates cross-cutting logic with advice and pointcuts
- `Advice` — the code executed at a join point (Before, After, Around)
- `Pointcut` — the expression that selects which join points receive advice
- `JoinPoint` — the runtime context (method, args, target) at an interception point
- `CGLIB Proxy` — Spring's default AOP proxy mechanism for class-based beans
- `@Transactional` — the most widely-used application of Spring AOP in production

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ KEY IDEA     │ Cross-cutting concerns extracted to       │
│              │ aspects — applied via proxy, not source   │
├──────────────┼───────────────────────────────────────────┤
│ USE WHEN     │ Transaction, security, audit, retry,      │
│              │ metrics — any concern spanning classes    │
├──────────────┼───────────────────────────────────────────┤
│ AVOID WHEN   │ Private methods; non-Spring-managed       │
│              │ objects; self-invocation (this.) calls    │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "AOP is the centralised HVAC —            │
│              │  connect once, heat every room."          │
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ Aspect (119) → Advice (120) →             │
│              │ Pointcut (121) → @Transactional (127)     │
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** Spring AOP uses `@Order` to control which aspect wraps which when multiple aspects apply to the same method. Lower `@Order` value = outer wrapper. A common real-world scenario: SecurityAspect (`@Order(1)`) wraps TransactionAspect (`@Order(2)`). If an `AccessDeniedException` is thrown in the security check, describe the full unwinding sequence — which aspects' `@AfterThrowing` and `@After` advice fire, in what order, and what happens to the database transaction (hint: it was never opened). Now reverse the order and describe the transaction leak scenario.

**Q2.** Spring AOP `@Around` advice receives a `ProceedingJoinPoint`. If the advice catches an exception thrown by `pjp.proceed()` and does NOT rethrow it, Spring's `@Transactional` will try to commit the transaction (because no exception propagated to the `TransactionInterceptor`). Describe this precise failure mode that occurs when a `@Around` logging aspect silently swallows exceptions from `@Transactional` methods — what data state results in the database — and explain why `@AfterThrowing` is safer than `@Around` with catch for exception logging use cases.

