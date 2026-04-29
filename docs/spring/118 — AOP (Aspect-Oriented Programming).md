---
layout: default
title: "AOP (Aspect-Oriented Programming)"
parent: "Spring Framework"
nav_order: 118
permalink: /spring/aop-aspect-oriented-programming/
---

`#spring` `#internals` `#pattern` `#intermediate`

⚡ TL;DR — AOP separates cross-cutting concerns (logging, security, transactions) from business logic by applying them declaratively via aspects — without modifying the business code.
## 📘 Textbook Definition
Aspect-Oriented Programming (AOP) is a programming paradigm that aims to increase modularity by allowing the separation of cross-cutting concerns. In Spring AOP, aspects are defined using pointcut expressions to select join points (method executions), and advice to define what runs at those join points. Spring AOP is proxy-based — it uses JDK Dynamic Proxy or CGLIB to weave advice at runtime.
## 🟢 Simple Definition (Easy)
AOP lets you say "run this code every time any service method is called" without modifying every service. You write the extra code once (in an Aspect), declare where it applies (Pointcut), and Spring handles the wiring.
## 🔵 Simple Definition (Elaborated)
Common cross-cutting concerns — logging every method call, checking security on every endpoint, managing transactions, measuring performance — would normally add dozens of lines to every method. AOP externalizes this. You define an `@Aspect` class with advice methods, specify which methods they apply to via pointcut expressions, and Spring proxies your beans to inject the advice transparently at runtime.
## 🔩 First Principles Explanation
**Without AOP:**
```java
public void placeOrder(Order order) {
    log.info("placeOrder called");           // logging concern
    checkPermission("PLACE_ORDER");          // security concern
    startTransaction();                      // transaction concern
    // actual business logic...
    commitTransaction();
    log.info("placeOrder completed");
}
// Repeat this boilerplate in EVERY method!
```
**With AOP:**
```java
public void placeOrder(Order order) {
    // ONLY business logic — clean!
}
// Cross-cutting concerns declared ONCE in aspects:
// @Before("execution(* OrderService.*(..))")
// @AfterReturning / @Around / @AfterThrowing
```
**Core concepts:**
```
Aspect     = the module containing cross-cutting logic
Advice     = the code that runs (before, after, around)
Pointcut   = expression selecting which methods to intercept
JoinPoint  = a specific method execution being intercepted
Weaving    = applying aspect to target (Spring does it at runtime via proxies)
```
## 💻 Code Example
```java
@Component
@Aspect
public class LoggingAspect {
    // Pointcut: any method in com.example.service package
    @Pointcut("execution(* com.example.service.*.*(..))")
    public void serviceLayer() {}
    // Before advice: runs before matched methods
    @Before("serviceLayer()")
    public void logBefore(JoinPoint jp) {
        System.out.println("Called: " + jp.getSignature().getName());
    }
    // After returning: runs when method completes normally
    @AfterReturning(pointcut = "serviceLayer()", returning = "result")
    public void logAfter(JoinPoint jp, Object result) {
        System.out.println("Returned: " + result);
    }
    // Around: most powerful — wraps the entire method
    @Around("@annotation(Timed)")  // on methods annotated with @Timed
    public Object measureTime(ProceedingJoinPoint pjp) throws Throwable {
        long start = System.currentTimeMillis();
        Object result = pjp.proceed();  // call the real method
        long elapsed = System.currentTimeMillis() - start;
        System.out.println(pjp.getSignature() + " took " + elapsed + "ms");
        return result;
    }
}
```
## ⚠️ Common Misconceptions
| ❌ Wrong Belief | ✅ Correct Reality |
|---|---|
| AOP modifies source code | Spring AOP works via runtime proxies — source is untouched |
| AOP intercepts everything | Spring AOP only intercepts public methods on Spring-managed beans |
| @Around replaces the method | @Around must call pjp.proceed() or the real method never runs |
| Private method @Transactional works via AOP | AOP can't intercept private methods — proxies can only override public/protected |
## 🔥 Pitfalls in Production
**Pitfall: Self-invocation bypasses AOP**
```java
@Service
public class OrderService {
    @Transactional
    public void placeOrder() {
        processPayment(); // DIRECT CALL — not through proxy!
    }
    @Transactional(propagation = REQUIRES_NEW) // this doesn't take effect!
    public void processPayment() { ... }
}
// Fix: inject OrderService into itself (@Autowired @Lazy OrderService self)
// or extract processPayment to another service bean
```
## 🔗 Related Keywords
- **[Aspect](./119 — Aspect.md)** — the AOP module class
- **[Advice](./120 — Advice.md)** — what runs at the join point
- **[Pointcut](./121 — Pointcut.md)** — expression selecting join points
- **[CGLIB Proxy](./116 — CGLIB Proxy.md)** — runtime weaving mechanism
- **[@Transactional](./127 — @Transactional.md)** — Spring's most-used AOP application
## 📌 Quick Reference Card
```
+------------------------------------------------------------------+
| KEY IDEA    | Separate cross-cutting concerns from business logic  |
+------------------------------------------------------------------+
| MECHANISM   | Runtime proxies (JDK or CGLIB)                       |
+------------------------------------------------------------------+
| LIMITATION  | Public methods on Spring beans only                  |
+------------------------------------------------------------------+
| COMMON USES | Logging, @Transactional, @Secured, @Async, @Cacheable|
+------------------------------------------------------------------+
```
## 🧠 Think About This Before We Continue
**Q1.** What is the performance impact of Spring AOP (proxy-based) vs. AspectJ (compile-time/load-time weaving)?
**Q2.** You annotate a private method `@Transactional`. The app runs with no errors, but transactions never begin. Why?
**Q3.** How would you write a pointcut that matches only methods annotated with a custom annotation `@Audited`?
