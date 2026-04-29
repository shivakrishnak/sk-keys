---
layout: default
title: "Weaving"
parent: "Spring Framework"
nav_order: 123
permalink: /spring/weaving/
---

`#spring` `#internals` `#intermediate`

⚡ TL;DR — Weaving is the process of applying aspect code to the target objects — Spring AOP weaves at runtime via proxies; AspectJ weaves at compile-time or load-time.
## 📘 Textbook Definition
Weaving is the process of linking aspects with other application types or objects to create an advised object. Spring AOP uses **runtime weaving** — creating proxy objects that intercept method calls. AspectJ supports **compile-time weaving** (bytecode modification during compilation) and **load-time weaving** (bytecode modification when class is loaded by classloader).
## 🟢 Simple Definition (Easy)
Weaving is "when and how" the aspect code gets connected to your beans. Spring does it at runtime by wrapping your bean in a proxy. AspectJ modifies the actual bytecode directly at compile time.
## 🔩 First Principles Explanation
**Three weaving types:**
```
1. Compile-time weaving (AspectJ)
   Java source → [aspectj compiler] → Woven bytecode (.class with advice baked in)
   Fast at runtime. Requires aspectj compiler.
2. Load-time weaving (AspectJ LTW)
   .class file → [AspectJ ClassLoader] → Woven class loaded into JVM
   No compile step needed. Slower class loading.
3. Runtime weaving (Spring AOP — DEFAULT)
   Bean created → Spring wraps in Proxy → Proxy intercepts calls → runs advice
   Simplest. No special compiler. Limited to public method interception on Spring beans.
```
## 💻 Code Example
```java
// Spring AOP runtime weaving (DEFAULT — just annotations needed)
@EnableAspectJAutoProxy  // enables runtime proxy weaving (Spring Boot adds this automatically)
@Configuration
public class AopConfig { }
// AspectJ Load-Time Weaving (for intercepting non-Spring objects, private methods etc.)
// application.yml
// spring:
//   aop:
//     proxy-target-class: false
// META-INF/aop.xml (AspectJ LTW config)
// -javaagent:aspectjweaver.jar (JVM arg)
```
## ⚠️ Common Misconceptions
| ❌ Wrong Belief | ✅ Correct Reality |
|---|---|
| Spring AOP is AspectJ | Spring AOP uses AspectJ annotation syntax but NOT AspectJ weaving — they're different |
| Runtime weaving can intercept any code | Runtime weaving only works on Spring-managed beans' public methods |
| Compile-time AspectJ needs Spring | AspectJ works standalone; Spring AOP is a convenience layer on top |
## 🔗 Related Keywords
- **[AOP](./118 — AOP (Aspect-Oriented Programming).md)** — the paradigm weaving implements
- **[CGLIB Proxy](./116 — CGLIB Proxy.md)** — runtime weaving mechanism #1
- **[JDK Dynamic Proxy](./117 — JDK Dynamic Proxy.md)** — runtime weaving mechanism #2
## 📌 Quick Reference Card
```
+------------------------------------------------------------------+
| RUNTIME     | Spring AOP default — proxies at bean creation time  |
+------------------------------------------------------------------+
| COMPILE-TIME| AspectJ — bytecode modified during compilation      |
+------------------------------------------------------------------+
| LOAD-TIME   | AspectJ LTW — bytecode modified at classload         |
+------------------------------------------------------------------+
| SPRING AOP  | Runtime only — limited to public Spring bean methods |
+------------------------------------------------------------------+
```
