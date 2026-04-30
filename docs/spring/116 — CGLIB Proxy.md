---
layout: default
title: "CGLIB Proxy"
parent: "Spring Framework"
nav_order: 116
permalink: /spring/cglib-proxy/
number: "116"
category: Spring & Spring Boot
difficulty: ★★★
depends_on: JVM, Bytecode, Proxy Pattern
used_by: AOP, @Transactional, @Configuration
tags: #spring, #jvm, #internals, #advanced
---

# 116 — CGLIB Proxy

`#spring` `#jvm` `#internals` `#advanced`

⚡ TL;DR — CGLIB Proxy is a subclass-based proxy Spring uses to add behavior (AOP, @Transactional) to classes that don't implement interfaces — by generating a subclass at runtime.

| #116 | Category: Spring & Spring Boot | Difficulty: ★★★ |
|:---|:---|:---|
| **Depends on:** | JVM, Bytecode, Proxy Pattern | |
| **Used by:** | AOP, @Transactional, @Configuration | |

---

### 📘 Textbook Definition
CGLIB (Code Generation Library) Proxy is a runtime code generation technique used by Spring to create proxy objects by subclassing the target class. Unlike JDK Dynamic Proxies which require an interface, CGLIB creates a byte-code-level subclass that overrides all non-final methods to intercept calls — enabling AOP advice, transaction management, and `@Configuration` singleton enforcement.
### 🟢 Simple Definition (Easy)
When Spring needs to add extra behavior to a class (like starting a transaction before a method), it creates a subclass of that class at runtime. This "fake subclass" (CGLIB proxy) intercepts your method call, runs extra code, then calls the real method.
### 🔵 Simple Definition (Elaborated)
Spring's AOP and `@Transactional` work by wrapping your beans in proxy objects. If your class implements an interface, Spring uses a JDK Dynamic Proxy (wraps the interface). If not, Spring uses CGLIB to generate a subclass at runtime that overrides your methods to inject the cross-cutting behavior. The caller never knows they're talking to a proxy.
### 🔩 First Principles Explanation
```
Your class:
  class OrderService {
    public void placeOrder() { // business logic }
  }
CGLIB generates at runtime:
  class OrderService$$SpringCGLIB$$0 extends OrderService {
    @Override
    public void placeOrder() {
      // Start transaction
      // Call super.placeOrder()
      // Commit transaction
    }
  }
Spring bean is the CGLIB subclass, not the original.
```
### 💻 Code Example
```java
// Proof: Spring injects a CGLIB proxy for @Configuration classes
@Configuration
public class AppConfig {
    @Bean public UserService userService() { return new UserService(); }
}
ApplicationContext ctx = new AnnotationConfigApplicationContext(AppConfig.class);
AppConfig config = ctx.getBean(AppConfig.class);
System.out.println(config.getClass()); 
// prints: class AppConfig$$SpringCGLIB$$0 — it's a subclass!
// @Transactional creates CGLIB proxy (if no interface)
@Service
public class OrderService {  // no interface
    @Transactional
    public void placeOrder() { ... }
}
// Spring creates: OrderService$$SpringCGLIB$$0 that adds TX management
// CGLIB limitation: final class/method cannot be proxied
@Service
public final class FinalService {  // ERROR! Can't subclass final class
    @Transactional
    public void save() { ... }           // won't work — CGLIB can't override
}
```
### ⚠️ Common Misconceptions
| ❌ Wrong Belief | ✅ Correct Reality |
|---|---|
| Spring always uses JDK proxy | Spring chooses: interface → JDK proxy; no interface → CGLIB |
| CGLIB is always slower | Modern CGLIB is comparable to JDK proxies; startup cost only |
| @Transactional works on private methods via CGLIB | CGLIB can't override private methods — transactions on private methods are silently ignored |
| You can safely cast CGLIB proxy to the original class | You can — it IS a subclass — but avoid relying on this |
### 🔗 Related Keywords
- **[JDK Dynamic Proxy](./117 — JDK Dynamic Proxy.md)** — alternative proxy type requiring interfaces
- **[AOP](./118 — AOP (Aspect-Oriented Programming).md)** — uses CGLIB/JDK proxies to apply advice
- **[@Transactional](./127 — @Transactional.md)** — implemented via CGLIB or JDK proxy
- **[@Configuration / @Bean](./114 — @Configuration @Bean.md)** — @Configuration classes are always CGLIB-proxied
### 📌 Quick Reference Card
```
+------------------------------------------------------------------+
| MECHANISM   | Runtime subclass generation via bytecode            |
+------------------------------------------------------------------+
| USED WHEN   | Target class has no interface, or @Configuration    |
+------------------------------------------------------------------+
| CANNOT PROXY| final classes, final methods, private methods       |
+------------------------------------------------------------------+
| ONE-LINER   | "A runtime subclass that intercepts method calls"    |
+------------------------------------------------------------------+
```
### 🧠 Think About This Before We Continue
**Q1.** Why are `@Configuration` classes ALWAYS proxied by CGLIB even if they implement an interface?
**Q2.** What happens if you call a `@Transactional` method from *within the same class* (self-invocation)? Why doesn't the proxy intercept it?
**Q3.** Spring Boot 3.x requires CGLIB proxy creation for some features. What was the performance improvement introduced in Spring 6 for CGLIB proxy creation?
