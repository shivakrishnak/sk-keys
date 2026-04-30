---
layout: default
title: "Circular Dependency"
parent: "Spring Framework"
nav_order: 115
permalink: /spring/circular-dependency/
number: "115"
category: Spring & Spring Boot
difficulty: ★★☆
depends_on: Bean, DI
used_by: @Lazy injection, proxy-based resolution
tags: #spring, #internals, #intermediate
---

# 115 — Circular Dependency

`#spring` `#internals` `#intermediate`

⚡ TL;DR — A circular dependency occurs when Bean A depends on Bean B and Bean B depends on Bean A, creating a dependency loop Spring cannot resolve with constructor injection.

| #115 | Category: Spring & Spring Boot | Difficulty: ★★☆ |
|:---|:---|:---|
| **Depends on:** | Bean, DI | |
| **Used by:** | @Lazy injection, proxy-based resolution | |

---

### 📘 Textbook Definition

A circular dependency in Spring occurs when two or more beans mutually depend on each other, directly or transitively, creating a cycle in the dependency graph. Constructor injection circular dependencies are unsolvable and throw `BeanCurrentlyInCreationException`. Setter/field injection cycles can sometimes be resolved by Spring using a three-level cache (singletons only).

### 🟢 Simple Definition (Easy)

Bean A needs Bean B to be created. Bean B needs Bean A to be created. Neither can be created first — deadlock! Spring detects this and throws an error.

### 🔵 Simple Definition (Elaborated)

Circular dependencies are an architectural smell — they indicate that two classes are too tightly coupled and should be refactored. Spring can work around *setter/field* injection cycles using its singleton cache (by injecting a partially-initialized bean), but this is dangerous. Constructor injection correctly refuses to resolve cycles, making the problem visible and forcing a better design.

### 🔩 First Principles Explanation

**Why constructor cycles are impossible:**
```
To create A: need B (call B's constructor)
To create B: need A (call A's constructor)
Neither can return until the other is ready → deadlock
```
**Why field/setter cycles are "resolved" (but problematic):**
```
1. Create A's instance (empty, no deps yet)
2. Add A's instance to "early singleton cache"
3. Try to inject B into A — create B
4. B needs A — find A in early cache (partially initialized!)
5. Inject partially-initialized A into B
6. Complete B initialization
7. Inject B into A
8. Complete A initialization
```
This works but A was injected into B before it was fully set up — can cause NPEs for fields set in @PostConstruct.

### 💻 Code Example
```java
// Problem: constructor circular dependency
@Service
public class ServiceA {
    public ServiceA(ServiceB b) {} // needs B
}
@Service
public class ServiceB {
    public ServiceB(ServiceA a) {} // needs A → BeanCurrentlyInCreationException!
}
// Fix 1: Refactor to break the cycle (BEST)
// Extract the shared logic into ServiceC that both A and B depend on
// Fix 2: @Lazy on one side (defers creation to first use)
@Service
public class ServiceA {
    public ServiceA(@Lazy ServiceB b) {} // B created on first use, not at startup
}
// Fix 3: Setter injection on one side
@Service
public class ServiceA {
    private ServiceB b;
    @Autowired public void setServiceB(ServiceB b) { this.b = b; }
}
// Spring Boot 2.6+ additional safety:
// spring.main.allow-circular-references=false (default) — fails fast on ALL cycles
```

### ⚠️ Common Misconceptions

| ❌ Wrong Belief | ✅ Correct Reality |
|---|---|
| Circular deps with field injection are safe | Field injection cycles use partially-initialized beans — subtle bugs possible |
| @Lazy permanently solves circular deps | @Lazy delays, doesn't fix the architectural problem |
| Spring automatically resolves all cycles | Only field/setter cycles for singletons; constructor cycles always fail |

### 🔗 Related Keywords

- **[DI (Dependency Injection)](./104 — DI (Dependency Injection).md)** — the mechanism that exposes circular deps
- **[Bean Lifecycle](./108 — Bean Lifecycle.md)** — partially-initialized beans in early cache
- **[CGLIB Proxy](./116 — CGLIB Proxy.md)** — proxies can introduce unexpected circular deps

### 📌 Quick Reference Card
```
+------------------------------------------------------------------+
| PROBLEM     | A needs B, B needs A — can't create either first    |
+------------------------------------------------------------------+
| CONSTRUCTOR | Always fails — BeanCurrentlyInCreationException      |
+------------------------------------------------------------------+
| FIELD/SETTER| May work but uses partially-initialized beans        |
+------------------------------------------------------------------+
| BEST FIX    | Refactor! Extract shared dependency into 3rd bean    |
+------------------------------------------------------------------+
| QUICK FIX   | @Lazy on one side (hides the smell)                  |
+------------------------------------------------------------------+
```

### 🧠 Think About This Before We Continue

**Q1.** Why might a circular dependency that worked in Spring Boot 2.5 suddenly fail in 2.6+?
**Q2.** A circular dependency involving a `@Transactional` bean and a `@Async` bean is especially dangerous. Why?
**Q3.** Draw the dependency graph for: A→B, B→C, C→A. Is this a circular dependency? How would you detect and break it?
