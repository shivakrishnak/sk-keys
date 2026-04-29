---
layout: default
title: "Advice"
parent: "Spring Framework"
nav_order: 120
permalink: /spring/advice/
---
⚡ TL;DR — Advice is the actual code (the action) an aspect runs at a matched join point — it defines WHEN (@Before, @After, @Around) and what happens.
## 📘 Textbook Definition
In Spring AOP, Advice is the action taken by an aspect at a particular join point. Types include: `@Before` (executes before method), `@AfterReturning` (after normal return), `@AfterThrowing` (after exception), `@After` (after any outcome), and `@Around` (wraps the method — most powerful, must call `pjp.proceed()`).
## 🟢 Simple Definition (Easy)
Advice is the "what happens" part of AOP. "Before the method runs, log the call." That "log the call" part is the advice. Pointcut selects which methods; advice defines what extra code runs.
## 🔩 First Principles Explanation
**Five advice types:**
```
@Before          — runs before the method (can't stop execution)
@AfterReturning  — runs after normal completion (sees return value)
@AfterThrowing   — runs when exception thrown (sees exception)
@After           — runs always (like finally block)
@Around          — wraps entire method — most powerful (must call proceed())
```
**@Around execution order:**
```
@Around starts
    → @Before runs
        → method executes
    → @AfterReturning / @AfterThrowing runs
    → @After runs
@Around ends
```
## 💻 Code Example
```java
@Aspect @Component
public class TimingAspect {
    @Before("execution(* com.example.service.*.*(..))")
    public void beforeService(JoinPoint jp) {
        System.out.println("About to call: " + jp.getSignature());
    }
    @AfterReturning(pointcut = "execution(* com.example.service.*.*(..))",
                    returning = "result")
    public void afterSuccess(JoinPoint jp, Object result) {
        System.out.println("Returned: " + result);
    }
    @AfterThrowing(pointcut = "execution(* com.example.service.*.*(..))",
                   throwing = "ex")
    public void afterException(JoinPoint jp, Exception ex) {
        System.out.println("Exception in " + jp.getSignature() + ": " + ex.getMessage());
    }
    @Around("@annotation(com.example.Timed)")
    public Object measureTime(ProceedingJoinPoint pjp) throws Throwable {
        long start = System.nanoTime();
        try {
            return pjp.proceed(); // MUST call or method never executes!
        } finally {
            long elapsed = System.nanoTime() - start;
            System.out.printf("%s: %.2fms%n", pjp.getSignature(), elapsed / 1e6);
        }
    }
}
```
## 🔗 Related Keywords
- **[Aspect](./119 — Aspect.md)** — the class that holds advice
- **[Pointcut](./121 — Pointcut.md)** — selects which join points advice applies to
- **[JoinPoint](./122 — JoinPoint.md)** — the runtime context passed to advice
## 📌 Quick Reference Card
```
+------------------------------------------------------------------+
| @BEFORE     | Runs before — can't prevent (unless exception)      |
+------------------------------------------------------------------+
| @AROUND     | Wraps entire method — must call proceed()            |
+------------------------------------------------------------------+
| @AFTERRETURNING | Sees return value on normal completion           |
+------------------------------------------------------------------+
| @AFTERTHROWING  | Sees exception when thrown                      |
+------------------------------------------------------------------+
```
