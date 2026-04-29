---
layout: default
title: "JoinPoint"
parent: "Spring Framework"
nav_order: 122
permalink: /spring/joinpoint/
---

`#spring` `#internals` `#intermediate`

⚡ TL;DR — JoinPoint is the runtime context object passed to advice methods — providing access to the intercepted method's name, arguments, target object, and signature.
## 📘 Textbook Definition
In Spring AOP, a JoinPoint represents a point during program execution at which an aspect can be plugged in. It is the runtime handle passed to `@Before`, `@After`, `@AfterReturning`, and `@AfterThrowing` advice methods, containing metadata about the intercepted method invocation. `ProceedingJoinPoint` (used in `@Around`) extends JoinPoint with the ability to control method execution via `proceed()`.
## 🟢 Simple Definition (Easy)
JoinPoint is the "who called what with what arguments" information available inside your advice method. When Spring intercepts a method call to give to your aspect, it packages all the details into a JoinPoint object.
## 💻 Code Example
```java
@Aspect @Component
public class InspectionAspect {
    @Before("execution(* com.example.service.*.*(..))")
    public void inspect(JoinPoint jp) {
        System.out.println("Method: " + jp.getSignature().getName());
        System.out.println("Class:  " + jp.getTarget().getClass().getSimpleName());
        System.out.println("Args:   " + Arrays.toString(jp.getArgs()));
        System.out.println("Kind:   " + jp.getKind()); // "method-execution"
    }
    // ProceedingJoinPoint adds proceed() for @Around
    @Around("execution(* com.example.service.*.*(..))")
    public Object wrap(ProceedingJoinPoint pjp) throws Throwable {
        Object[] args = pjp.getArgs();
        // Modify args if needed
        args[0] = sanitize(args[0]);
        return pjp.proceed(args); // call with potentially modified args
    }
}
```
## ⚠️ Common Misconceptions
| ❌ Wrong Belief | ✅ Correct Reality |
|---|---|
| JoinPoint is available for all advice types | @Around uses ProceedingJoinPoint (extend of JoinPoint); others use JoinPoint |
| jp.getThis() and jp.getTarget() are always the same | getThis() = proxy; getTarget() = real target bean — different! |
## 🔗 Related Keywords
- **[Advice](./120 — Advice.md)** — the method that receives JoinPoint
- **[Pointcut](./121 — Pointcut.md)** — selects which JoinPoints advice applies to
## 📌 Quick Reference Card
```
+------------------------------------------------------------------+
| jp.getSignature()  | Method name, return type, declaring class    |
+------------------------------------------------------------------+
| jp.getArgs()       | Arguments passed to the method              |
+------------------------------------------------------------------+
| jp.getTarget()     | Real bean (not the proxy)                   |
+------------------------------------------------------------------+
| pjp.proceed()      | @Around only — execute the real method       |
+------------------------------------------------------------------+
```
