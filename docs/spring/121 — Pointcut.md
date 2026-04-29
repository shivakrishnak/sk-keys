---
layout: default
title: "Pointcut"
parent: "Spring Framework"
nav_order: 121
permalink: /spring/pointcut/
---
⚡ TL;DR — A Pointcut is an expression that selects which method executions (join points) an advice should apply to — the "WHERE" of AOP.
## 📘 Textbook Definition
In Spring AOP, a Pointcut is a predicate that matches join points. Pointcut expressions use AspectJ pointcut language and select method executions based on class name, method name, parameter types, annotations, access modifiers, and return types.
## 🟢 Simple Definition (Easy)
A Pointcut is the targeting rule. "Apply this advice to all methods named `save` in any `Repository` class." The pointcut is that rule.
## 🔵 Simple Definition (Elaborated)
Pointcuts are written in AspectJ expression language. The most common expression type is `execution(...)` which matches method calls by signature pattern. You can also match by annotation (`@annotation()`), by type (`within()`), by bean name (`bean()`), or combine expressions with `&&`, `||`, `!`.
## 🔩 First Principles Explanation
**Pointcut Expression Patterns:**
```
execution(modifiers? return-type declaring-type? name(params) throws?)
Examples:
 execution(* com.example.service.*.*(..))
 — any method, any return type, any class in service package, any params
 execution(public * OrderService.*(..))
 — public methods of OrderService
 execution(* *Service.save*(String, ..))
 — methods starting with 'save' in any *Service class, first param String
 @annotation(com.example.Transactional)
 — methods annotated with @Transactional
 within(com.example.repository.*)
 — all methods within repository package
 bean(orderService)
 — methods on the "orderService" bean
```
## 💻 Code Example
```java
@Aspect @Component
public class AuditAspect {
    // Named reusable pointcut
    @Pointcut("execution(* com.example.service.*.*(..))")
    public void serviceLayer() {}
    // Combine pointcuts
    @Pointcut("serviceLayer() && @annotation(com.example.Audited)")
    public void auditableService() {}
    @Before("auditableService()")
    public void audit(JoinPoint jp) { /* log */ }
    // Inline pointcut — common pattern
    @Around("execution(* com.example..*Repository.*(..)) && args(entity,..)")
    public Object trackEntityWrite(ProceedingJoinPoint pjp, Object entity) throws Throwable {
        // entity = first argument of matched method
        return pjp.proceed();
    }
}
```
## ⚠️ Common Misconceptions
| ❌ Wrong Belief | ✅ Correct Reality |
|---|---|
| Pointcut patterns use regex | They use AspectJ expression language — different syntax |
| `execution(* *.*(..))` matches all methods | Only matches Spring beans' public methods (proxy limitation) |
## 🔗 Related Keywords
- **[Advice](./120 — Advice.md)** — what runs at matched join points
- **[JoinPoint](./122 — JoinPoint.md)** — the runtime execution context
- **[Aspect](./119 — Aspect.md)** — class that contains pointcuts and advice
## 📌 Quick Reference Card
```
+------------------------------------------------------------------+
| KEY IDEA    | Expression selecting which methods advice applies to |
+------------------------------------------------------------------+
| MOST COMMON | execution(* com.example.service.*.*(..))            |
+------------------------------------------------------------------+
| BY ANNOT.   | @annotation(com.example.Transactional)              |
+------------------------------------------------------------------+
| COMBINE     | pointcutA() && pointcutB() / || / !                 |
+------------------------------------------------------------------+
```
