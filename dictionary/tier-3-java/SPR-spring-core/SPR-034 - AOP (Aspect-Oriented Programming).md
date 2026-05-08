---
layout: default
title: "AOP (Aspect-Oriented Programming)"
parent: "Spring Core"
grand_parent: "Technical Dictionary"
nav_order: 34
permalink: /spring/aop/
id: SPR-034
category: Spring Core
difficulty: ★★☆
depends_on: Bean, CGLIB Proxy, JDK Dynamic Proxy, BeanPostProcessor
used_by: "@Transactional, @Cacheable, @Async, Security, Logging, Tracing"
related: Aspect, Advice, Pointcut, JoinPoint, Weaving, AspectJ
tags:
  - spring
  - springboot
  - intermediate
  - pattern
  - bestpractice
---

# SPR-034 - AOP (Aspect-Oriented Programming)

⚡ TL;DR - AOP separates cross-cutting concerns (transactions, logging, security) from business logic by defining "aspects" that specify _when_ (pointcut) and _what_ (advice) to execute - Spring implements this via JDK/CGLIB proxies at runtime.

| #386            | Category: Spring Core                                          | Difficulty: ★★☆ |
| :-------------- | :------------------------------------------------------------- | :-------------- |
| **Depends on:** | Bean, CGLIB Proxy, JDK Dynamic Proxy, BeanPostProcessor        |                 |
| **Used by:**    | @Transactional, @Cacheable, @Async, Security, Logging, Tracing |                 |
| **Related:**    | Aspect, Advice, Pointcut, JoinPoint, Weaving, AspectJ          |                 |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
You need to add logging, transaction management, and security checks to 50 service methods. The "before logging" code is copy-pasted into the start of every method. The "transaction begin/commit/rollback" boilerplate is duplicated 50 times. The security check is copy-pasted into each method. When the logging format changes, you update 50 files. When the security logic changes, you update 50 files. Methods that were 5 lines of business logic are now 20 lines with 15 lines of infrastructure concern. Reading the code, you can't see the business logic through the infrastructure noise.

**THE BREAKING POINT:**
Cross-cutting concerns violate DRY (Don't Repeat Yourself) systematically. Unlike normal features that can be extracted into a helper class and called explicitly, cross-cutting concerns are woven _around_ method calls - they don't fit neatly into OOP's hierarchical decomposition. You can't inherit "add a log statement to every method" without overriding every method. You can't compose "start a transaction before every save" without modifying every save method.

**THE INVENTION MOMENT:**
"This is exactly why Aspect-Oriented Programming was invented."

---

### 📘 Textbook Definition

**Aspect-Oriented Programming (AOP)** is a programming paradigm that increases modularity by separating cross-cutting concerns into _aspects_. An **Aspect** defines: (1) a **Pointcut** - a predicate that matches join points (method executions) in the application, and (2) **Advice** - the code to execute at matched join points. **Spring AOP** is a proxy-based AOP framework that implements aspects using JDK dynamic proxies or CGLIB subclasses. Spring AOP supports AspectJ annotation syntax (`@Aspect`, `@Before`, `@After`, `@Around`, `@Pointcut`) but does NOT use full AspectJ - it processes the annotations and implements them via Spring proxies, not AspectJ's compile-time or load-time weaving. The result is that cross-cutting concerns are applied automatically to matching beans without modifying those beans' code.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
AOP lets you say "run this code every time a method matching this pattern is called" - without touching those methods.

**One analogy:**

> AOP is like airport security. Every passenger (method call) who flies (executes) must pass through security (the aspect). You don't install metal detectors inside each plane (method) - you install them at the gate (aspect). All passengers pass through automatically. The planes don't know about security; security doesn't know about the planes' destinations.

**One insight:**
AOP solves the problem that OOP cannot: OOP decomposes a system by _nouns_ (classes, objects). Cross-cutting concerns decompose a system by _when_ and _where_ code runs. These two axes of decomposition are orthogonal - AOP is the second axis.

---

### 🔩 First Principles Explanation

**CORE INVARIANTS:**

1. An **Aspect** = Pointcut + Advice. The pointcut says "where"; the advice says "what."
2. Spring AOP is **proxy-based**: aspects apply only to Spring-managed beans called from _outside_ the bean.
3. Spring AOP applies aspects to **method execution** join points only - field access, constructors, and static methods cannot be intercepted.
4. Spring AOP uses **AspectJ annotation syntax** but implements advice via proxies, not AspectJ byte-code weaving.
5. For full AOP (constructor join points, field access, `this.method()` interception), use AspectJ weaving instead of Spring AOP.

**DERIVED DESIGN:**
Aspects are applied by `AnnotationAwareAspectJAutoProxyCreator` (a `BeanPostProcessor`). After each bean is created, it checks: "does any aspect's pointcut match this bean?" If yes, it wraps the bean in a proxy (CGLIB or JDK). When a matching method is called through the proxy, the advice executes.

**THE TRADE-OFFS:**

**Gain:** Business code contains only business logic. Cross-cutting concerns are modular, testable, and centralized. Adding a new concern (tracing) doesn't touch existing code.

**Cost:** "Magic" execution - developers don't see advice calls in the code. Debugging is harder (stack traces show proxy frames). Self-invocation bypasses aspects. Proxy overhead (tiny but non-zero).

---

### 🧪 Thought Experiment

**SETUP:**
50 service methods that need execution-time logging: method name, args, return value, and duration.

**WITHOUT AOP:**

```java
public User save(User user) {
    log.info("save called with: {}", user);  // cross-cutting
    long start = System.currentTimeMillis();
    User result = repo.save(user);  // business logic
    long ms = System.currentTimeMillis() - start;
    log.info("save returned: {} in {}ms", result, ms);  // cross-cutting
    return result;
}
// × 50 methods = 300 lines of logging boilerplate
```

**WITH AOP:**

```java
// Business code: zero logging boilerplate
public User save(User user) {
    return repo.save(user);  // ONLY business logic
}

// Aspect: all logging in one place
@Aspect @Component
public class ExecutionLoggingAspect {
    @Around("execution(* com.example.service.*.*(..))")
    public Object log(ProceedingJoinPoint pjp) throws Throwable {
        log.info("{} called with: {}", pjp.getSignature(), pjp.getArgs());
        long start = System.currentTimeMillis();
        Object result = pjp.proceed();
        long ms = System.currentTimeMillis() - start;
        log.info("{} returned: {} in {}ms", pjp.getSignature(), result, ms);
        return result;
    }
}
// 50 methods → 0 logging lines. 1 aspect handles all.
```

**THE INSIGHT:**
AOP replaces O(methods × concerns) cross-cutting code with O(concerns) aspects. When the logging format changes, there's ONE place to change, regardless of how many methods exist.

---

### 🧠 Mental Model / Analogy

> AOP is a city's traffic camera network. Every camera (aspect) is placed at specific intersections (pointcut: "execution of save methods in service package"). Every car passing through (method call) is photographed (advice applied) automatically - the driver (method code) doesn't know or care about the cameras. The traffic authority (Spring AOP) manages where cameras are placed; the drivers manage where they're going. Complete separation of concerns.

- "Traffic camera" → Aspect
- "Specific intersection" → Pointcut
- "Photographing the car" → Advice execution
- "Car passing through" → Method call (JoinPoint)
- "City traffic authority" → Spring AOP proxy infrastructure
- "Cameras only on certain streets" → Pointcut expression filtering

**Where this analogy breaks down:** Traffic cameras are passive (only record). AOP advice is active - it can modify inputs (`@Around` can change args), outputs (can modify return value), or suppress the call entirely. And unlike cameras that capture everything, Spring AOP cannot capture calls made from within the same object (self-invocation).

---

### 📶 Gradual Depth - Four Levels

**Level 1 - What it is (anyone can understand):**
AOP lets you say "whenever this type of method runs, also run this other code" - without changing the original method. It's how Spring adds transactions, caching, and security to your code transparently.

**Level 2 - How to use it (junior developer):**
Enable with `@EnableAspectJAutoProxy` (Spring Boot enables it automatically). Create a class annotated with `@Aspect` and `@Component`. Write methods annotated with `@Before`, `@After`, `@Around`, etc., with pointcut expressions like `execution(* com.example.service.*.*(..))`. Use `@Around` for full control (can modify args, return values, handle exceptions). Use `@Before` for pre-processing only. Use `@AfterReturning` for post-processing on success.

**Level 3 - How it works (mid-level engineer):**
`AnnotationAwareAspectJAutoProxyCreator` extends `AbstractAutoProxyCreator` and is a `BeanPostProcessor`. In `postProcessAfterInitialization()`, it calls `findEligibleAdvisors(bean)` which uses `AspectJAwareAdvisorAutoProxyCreator` to check if any registered `@Aspect` beans have pointcuts matching the bean's methods. If matches found, `createProxy()` wraps the bean in a `ProxyFactory`-generated proxy with the matched `Advisor`s in the chain. At call time, `ReflectiveMethodInvocation.proceed()` chains through interceptors (each Advice is wrapped as `MethodInterceptor`).

**Level 4 - Why it was designed this way (senior/staff):**
Spring AOP was deliberately kept "simpler but restricted" compared to full AspectJ. The proxy-based approach means: (1) only method execution join points (not field access, constructors), (2) only Spring beans (not arbitrary objects), (3) no self-invocation interception. These restrictions were trade-offs for: (1) no bytecode agent required (pure Java), (2) no compile-time step required, (3) debuggable via standard Java stack traces. The restriction that you must use full AspectJ for advanced scenarios (compile/load-time weaving) was intentional - it avoids complexity in the common 95% case while the 5% case (needs `this.method()` interception) has a clear escape hatch.

---

### ⚙️ How It Works (Mechanism)

**AOP proxy creation pipeline:**

```
ApplicationContext.refresh()
    ↓
AnnotationAwareAspectJAutoProxyCreator registered as BeanPostProcessor
    ↓
@Aspect beans (LoggingAspect, TransactionAspect) created and registered
    ↓
For each service bean:
  postProcessAfterInitialization(userService, "userService")
    ↓
  findEligibleAdvisors("userService"):
    For each @Aspect bean:
      For each @Before/@After/@Around method:
        Does pointcut match userService's methods?
          YES → add Advisor to list
    ↓
  If advisors found:
    createProxy(userService, advisors)
    → ProxyFactory → JdkDynamicAopProxy or CglibAopProxy
    → Returns proxy wrapping userService
    ↓
singletonObjects["userService"] = proxy
```

**Advice execution order (for one method call):**

```
caller.save(user)
    ↓
Proxy.save(user)
    ↓
ReflectiveMethodInvocation.proceed():
  1. ExposeInvocationInterceptor
  2. @Around before-part (ProceedingJoinPoint before pjp.proceed())
  3. @Before advice
  4. proceed()
     ↓
     target.save(user)  ← actual method
     ↓
  5. @AfterReturning / @AfterThrowing
  6. @After (always runs)
  7. @Around after-part (after pjp.proceed())
    ↓
return result
```

---

### 🔄 The Complete Picture - End-to-End Flow

**NORMAL FLOW:**

```
UserService.save(user) called
    ↓
Intercepted by CGLIB/JDK proxy
    ↓
Advisor chain: [LoggingAdvisor, TransactionAdvisor, CachingAdvisor]
    ↓ ← YOU ARE HERE (AOP intercepts the call)
LoggingAdvisor @Before: log("save called with %s", user)
    ↓
TransactionAdvisor @Around: begin transaction
    ↓
CachingAdvisor: check cache - miss
    ↓
target.save(user) - real business logic executes
    ↓
CachingAdvisor: put result in cache
    ↓
TransactionAdvisor @Around: commit transaction
    ↓
LoggingAdvisor @AfterReturning: log("save returned %s", result)
    ↓
return result to caller
```

**WHAT CHANGES AT SCALE:**
Each advised method call incurs: (1) proxy method dispatch overhead (negligible), (2) aspect chain traversal (proportional to number of aspects), (3) reflection for `ProceedingJoinPoint` data (minor). For high-throughput services (10,000+ RPS), profiling may reveal aspect overhead. Mitigation: scope pointcuts narrowly (avoid `execution(* *.*(..))`) to reduce the number of advised methods.

---

### 💻 Code Example

**Example 1 - Logging aspect with @Around:**

```java
@Aspect
@Component
public class ExecutionLoggingAspect {

    private static final Logger log = LoggerFactory.getLogger(ExecutionLoggingAspect.class);

    @Around("execution(* com.example.service.*.*(..))")
    public Object logExecution(ProceedingJoinPoint pjp) throws Throwable {
        String sig = pjp.getSignature().toShortString();
        log.debug("→ {}", sig);
        long start = System.nanoTime();
        try {
            Object result = pjp.proceed();
            long ms = (System.nanoTime() - start) / 1_000_000;
            log.debug("← {} ({}ms)", sig, ms);
            return result;
        } catch (Throwable t) {
            log.error("✗ {} threw {}", sig, t.getMessage());
            throw t;
        }
    }
}
```

**Example 2 - Audit aspect with @AfterReturning:**

```java
@Aspect
@Component
public class AuditAspect {

    @Autowired AuditRepository auditRepo;

    @AfterReturning(
        pointcut = "execution(* com.example.service.OrderService.placeOrder(..))",
        returning = "order"
    )
    public void auditOrderPlaced(JoinPoint jp, Order order) {
        auditRepo.save(new AuditEvent(
            "ORDER_PLACED",
            order.getId(),
            SecurityContextHolder.getContext().getAuthentication().getName()
        ));
    }
}
```

**Example 3 - Reusable pointcut definition:**

```java
@Aspect
@Component
public class ServicePointcuts {

    // Define reusable pointcuts
    @Pointcut("execution(* com.example.service.*.*(..))")
    public void allServiceMethods() {}

    @Pointcut("@annotation(com.example.annotation.Retryable)")
    public void retryableAnnotated() {}

    @Pointcut("within(com.example.repository.*)")
    public void repositoryLayer() {}
}

@Aspect
@Component
public class RetryAspect {
    @Around("com.example.ServicePointcuts.retryableAnnotated()")
    public Object retry(ProceedingJoinPoint pjp) throws Throwable {
        int maxRetries = 3;
        for (int i = 0; i < maxRetries; i++) {
            try {
                return pjp.proceed();
            } catch (TransientDataAccessException e) {
                if (i == maxRetries - 1) throw e;
                Thread.sleep(100 * (i + 1));
            }
        }
        throw new IllegalStateException("unreachable");
    }
}
```

---

### ⚖️ Comparison Table

| Feature                  | Spring AOP              | AspectJ (Full)                                 |
| ------------------------ | ----------------------- | ---------------------------------------------- |
| **Mechanism**            | JDK/CGLIB proxy         | Bytecode weaving (compile/load/runtime)        |
| **Join points**          | Method execution only   | Method, constructor, field, static initializer |
| **Self-invocation**      | Not intercepted         | Intercepted                                    |
| **Spring bean required** | Yes                     | No - any Java object                           |
| **Configuration**        | @Aspect + Spring config | AspectJ compiler or agent                      |
| **Use case**             | 95% of real-world AOP   | Advanced (self-calls, non-Spring objects)      |

**How to choose:** Use Spring AOP for standard cross-cutting concerns (transactions, logging, caching, security). Use AspectJ for advanced scenarios: intercepting `this.method()` calls, non-Spring-managed objects, constructor interception, or field access interception.

---

### ⚠️ Common Misconceptions

| Misconception                                                                | Reality                                                                                                                                                                                      |
| ---------------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| AOP advice applies to all Java objects                                       | Spring AOP only applies to Spring-managed beans, and only for calls from outside the bean.                                                                                                   |
| @Transactional uses AOP - so does that mean all transactions go through AOP? | Yes - @Transactional is implemented as a Spring AOP aspect (TransactionInterceptor) wrapped around the target bean.                                                                          |
| @Before and @Around both run before the method - they're equivalent          | @Before runs before but cannot prevent method execution or modify args. @Around wraps the call entirely - it can prevent execution, modify args, modify return value, and handle exceptions. |
| AOP increases latency significantly                                          | The proxy overhead is nanoseconds per call, JIT-optimized. Aspect logic (SQL queries, logging I/O) is what adds latency, not the AOP mechanism itself.                                       |

---

### 🚨 Failure Modes & Diagnosis

**Aspect not applying (self-invocation)**

**Symptom:**
`@Transactional` / `@Cacheable` not triggering for a method called from within the same class.

**Root Cause:**
`this.method()` bypasses the Spring proxy. The aspect is wired to the proxy, not the real object.

**Diagnostic Command / Tool:**

```java
// Verify you're calling through the proxy:
System.out.println(AopContext.currentProxy());  // null if self-invocation
// Enable exposeProxy:
@EnableAspectJAutoProxy(exposeProxy = true)
// Then use:
((UserService) AopContext.currentProxy()).save(user);
```

**Fix:**

```java
// Option 1: Inject self (cleanest)
@Autowired private UserService self;
self.save(user);

// Option 2: AopContext.currentProxy() (requires exposeProxy=true)

// Option 3: Refactor into separate bean
```

---

**Aspect not applying (bean not Spring-managed)**

**Symptom:**
`@Transactional` on a method - no transaction started. Method runs without transaction despite annotation.

**Root Cause:**
The object was created with `new UserService()` instead of being injected by Spring. It's not a Spring bean, so no proxy was created.

**Fix:**
Ensure the bean is obtained via Spring injection (`@Autowired`) rather than `new`. Check that the class is in a component-scanned package or declared as a `@Bean`.

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**

- `CGLIB Proxy` - the mechanism Spring AOP uses for concrete class proxying
- `JDK Dynamic Proxy` - the mechanism Spring AOP uses for interface proxying
- `BeanPostProcessor` - `AnnotationAwareAspectJAutoProxyCreator` is a BeanPostProcessor

**Builds On This (learn these next):**

- `Aspect` - the complete AOP module containing pointcut + advice
- `Advice` - the code to run (@Before, @After, @Around)
- `Pointcut` - the predicate that selects which methods to intercept
- `@Transactional` - AOP's most impactful consumer in Spring

**Alternatives / Comparisons:**

- `AspectJ weaving` - full AOP for non-Spring scenarios
- `Decorator pattern` - manual AOP alternative (explicit wrapping, no magic)

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ WHAT IT IS   │ Separating cross-cutting concerns into    │
│              │ aspects that automatically wrap method    │
│              │ calls matching a pointcut expression      │
├──────────────┼───────────────────────────────────────────┤
│ PROBLEM IT   │ Copy-paste cross-cutting code (logging,   │
│ SOLVES       │ transactions) duplicated across N methods │
├──────────────┼───────────────────────────────────────────┤
│ KEY INSIGHT  │ Spring AOP = proxy-based; only intercepts │
│              │ calls FROM OUTSIDE the bean. No self-     │
│              │ invocation interception.                  │
├──────────────┼───────────────────────────────────────────┤
│ KEY TERMS    │ Aspect = Pointcut + Advice                 │
│              │ JoinPoint = a matched method execution    │
│              │ Weaving = applying aspect to target       │
├──────────────┼───────────────────────────────────────────┤
│ USE WHEN     │ Logging, security, transactions, caching, │
│              │ retry, rate-limiting across many methods  │
├──────────────┼───────────────────────────────────────────┤
│ AVOID WHEN   │ Avoid for logic that belongs in business  │
│              │ layer; avoid self-invocation patterns     │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "Run this code around every method that   │
│              │  matches this pattern - automatically."   │
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ Aspect → Advice → Pointcut → JoinPoint    │
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** Spring AOP uses `AnnotationAwareAspectJAutoProxyCreator` as a `BeanPostProcessor` to wrap beans in proxies. But this BeanPostProcessor itself is a bean. When Spring is processing beans for proxy wrapping, does it also try to proxy the AOP infrastructure beans (like the aspects themselves)? What prevents Spring from creating an infinite loop - proxying the aspect that proxies beans?

**Q2.** `@Transactional`, `@Cacheable`, and `@Async` are all implemented via Spring AOP. When a method has all three annotations, what order do the three aspects execute in? Does the order matter (e.g., does caching happen before or after the transaction starts)? How do you control the ordering if it matters?
