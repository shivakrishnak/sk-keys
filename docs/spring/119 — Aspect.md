---
layout: default
title: "Aspect"
parent: "Spring Framework"
nav_order: 119
permalink: /spring/aspect/
number: "119"
category: Spring & Spring Boot
difficulty: ★★☆
depends_on: AOP
used_by: Pointcut, Advice, @Aspect annotation
tags: #spring, #internals, #intermediate
---

# 119 — Aspect

`#spring` `#internals` `#intermediate`

⚡ TL;DR — An Aspect is a class (annotated @Aspect) that encapsulates a cross-cutting concern — it packages pointcuts and advice together into a named, reusable module.

| #119 | Category: Spring & Spring Boot | Difficulty: ★★☆ |
|:---|:---|:---|
| **Depends on:** | AOP | |
| **Used by:** | Pointcut, Advice, @Aspect annotation | |

---

### 📘 Textbook Definition
In Spring AOP, an Aspect is a modularization of a cross-cutting concern. Declared via the `@Aspect` annotation on a Spring-managed class, it contains one or more advice methods annotated with `@Before`, `@After`, `@AfterReturning`, `@AfterThrowing`, or `@Around`, and pointcut declarations scoping which join points each advice applies to.
### 🟢 Simple Definition (Easy)
An Aspect is the "where and what" of AOP packed together. It says: "At these methods (pointcut), do this extra thing (advice)." One aspect can apply its behavior to hundreds of methods without changing any of them.
### 💻 Code Example
```java
@Component   // register as a Spring bean
@Aspect      // declare it as an AOP aspect
public class SecurityAspect {
    // Reusable pointcut (named — can be referenced by other methods)
    @Pointcut("execution(* com.example.controller.*.*(..))")
    public void controllerMethods() {}
    // Advice: check auth before every controller method
    @Before("controllerMethods()")
    public void checkAuthentication(JoinPoint jp) {
        Authentication auth = SecurityContextHolder.getContext().getAuthentication();
        if (auth == null || !auth.isAuthenticated()) {
            throw new AccessDeniedException("Not authenticated");
        }
    }
    // Advice: audit log after successful controller calls
    @AfterReturning("controllerMethods()")
    public void auditLog(JoinPoint jp) {
        auditService.log(jp.getSignature().getName(), getCurrentUser());
    }
}
```
### ⚠️ Common Misconceptions
| ❌ Wrong Belief | ✅ Correct Reality |
|---|---|
| @Aspect alone makes it work | Also need @Component (or @Bean) so Spring manages the aspect bean |
| One aspect = one advice | An aspect can have multiple pointcuts and multiple advice methods |
### 🔗 Related Keywords
- **[AOP](./118 — AOP (Aspect-Oriented Programming).md)** — the paradigm Aspect implements
- **[Advice](./120 — Advice.md)** — the action inside an Aspect
- **[Pointcut](./121 — Pointcut.md)** — the selector inside an Aspect
### 📌 Quick Reference Card
```
+------------------------------------------------------------------+
| KEY IDEA    | AOP module — groups pointcuts + advice together     |
+------------------------------------------------------------------+
| ANNOTATION  | @Aspect (class) + @Component (to be a bean)         |
+------------------------------------------------------------------+
| ONE-LINER   | "The where-and-what unit of cross-cutting logic"      |
+------------------------------------------------------------------+
```
