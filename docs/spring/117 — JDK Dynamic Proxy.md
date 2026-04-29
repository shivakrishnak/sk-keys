---
layout: default
title: "JDK Dynamic Proxy"
parent: "Spring Framework"
nav_order: 117
permalink: /spring/jdk-dynamic-proxy/
---
⚡ TL;DR — JDK Dynamic Proxy uses Java's built-in reflection API to create an interface-implementing proxy at runtime, which Spring uses to intercept method calls on interface-based beans.
## 📘 Textbook Definition
A JDK Dynamic Proxy is a runtime-generated proxy class created by `java.lang.reflect.Proxy` that implements one or more interfaces, delegating method invocations through an `InvocationHandler`. Spring uses JDK dynamic proxies when the target bean implements at least one interface and `proxyTargetClass=false` (the default for interface-based beans).
## 🟢 Simple Definition (Easy)
If your class implements an interface, Spring creates a fake "middle-man" object that implements the same interface. When you call a method, the middle-man can run extra code (like starting a transaction) before and after calling your real method.
## 🔵 Simple Definition (Elaborated)
JDK Dynamic Proxy is Java's built-in proxy mechanism. Spring uses it as the preferred proxy type when the target bean has an interface — it creates an object that "looks like" the interface to callers, intercepts calls via `InvocationHandler`, runs advice (AOP, transaction code), then delegates to the real bean. No external library is needed — it's pure Java reflection.
## 🔩 First Principles Explanation
```java
// Java's built-in Proxy.newProxyInstance:
Object proxy = Proxy.newProxyInstance(
    targetClass.getClassLoader(),
    new Class[]{UserService.class},   // must be interface!
    (proxyObj, method, args) -> {
        // ← run before-advice here (e.g., start transaction)
        Object result = method.invoke(target, args);  // call real method
        // ← run after-advice here (e.g., commit transaction)
        return result;
    }
);
// The proxy IS-A UserService (interface), but is NOT-A UserServiceImpl
```
**When Spring chooses JDK vs CGLIB:**
```
@Autowired UserService us; // us declared as interface
      ↓
Target bean (UserServiceImpl) implements UserService interface
      ↓
By default: JDK Dynamic Proxy (implements UserService)
      ↓
If you inject UserServiceImpl directly → beans must use CGLIB
      ↓
Or set spring.aop.proxy-target-class=true → forces CGLIB for all
```
## 💻 Code Example
```java
public interface PaymentService { void charge(double amount); }
@Service
@Transactional  // Spring wraps with JDK proxy (interface exists)
public class StripePaymentService implements PaymentService {
    @Override
    public void charge(double amount) { /* stripe API */ }
}
// What Spring actually registers:
// Proxy object that implements PaymentService
// → intercepts charge() → starts TX → calls real method → commits TX
// Usage:
@Autowired PaymentService paymentService; // gets JDK proxy — OK
// @Autowired StripePaymentService stripe; // FAILS! proxy only implements PaymentService, not StripePaymentService
```
## ⚠️ Common Misconceptions
| ❌ Wrong Belief | ✅ Correct Reality |
|---|---|
| JDK proxy works on any class | JDK proxy requires the target to implement at least one interface |
| You can inject JDK proxy by concrete class | JDK proxy only implements interfaces; injecting by concrete type fails |
| JDK proxy is always slower than CGLIB | Performance difference is negligible in modern Java |
## 🔗 Related Keywords
- **[CGLIB Proxy](./116 — CGLIB Proxy.md)** — used when no interface; subclass-based
- **[AOP](./118 — AOP (Aspect-Oriented Programming).md)** — uses either JDK or CGLIB proxy
- **[@Transactional](./127 — @Transactional.md)** — the most common use of proxies
## 📌 Quick Reference Card
```
+------------------------------------------------------------------+
| USED WHEN   | Bean implements an interface (default)              |
+------------------------------------------------------------------+
| IMPLEMENTS  | Same interface(s) as target                         |
+------------------------------------------------------------------+
| LIMITATION  | Cannot inject by concrete class — only by interface |
+------------------------------------------------------------------+
| OVERRIDE    | spring.aop.proxy-target-class=true forces CGLIB     |
+------------------------------------------------------------------+
```
## 🧠 Think About This Before We Continue
**Q1.** If a `@Service` implements two interfaces, which does the JDK proxy implement? How do you inject a bean that implements multiple interfaces?
**Q2.** What happens when you set `spring.aop.proxy-target-class=true` globally? Are there any downsides?
**Q3.** In a Spring application using JDK proxies, if you `instanceof` the proxy object against the interface vs. the implementation class, what do you get?
