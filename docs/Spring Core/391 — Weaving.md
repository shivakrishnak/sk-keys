---
layout: default
title: "Weaving"
parent: "Spring Core"
nav_order: 391
permalink: /spring/weaving/
number: "391"
category: Spring Core
difficulty: ★★☆
depends_on: "AOP, Aspect, Advice, Pointcut, CGLIB Proxy"
used_by: "Spring AOP, AspectJ, @Transactional, @Async, @Cacheable"
tags: #java, #spring, #intermediate, #internals, #pattern
---

# 391 — Weaving

`#java` `#spring` `#intermediate` `#internals` `#pattern`

⚡ TL;DR — The process of applying aspects to target objects — Spring does this at runtime by creating proxy beans; AspectJ can do it at compile time or class-load time.

| #391 | category: Spring Core
|:---|:---|:---|
| **Depends on:** | AOP, Aspect, Advice, Pointcut, CGLIB Proxy | |
| **Used by:** | Spring AOP, AspectJ, @Transactional, @Async, @Cacheable | |

---

### 📘 Textbook Definition

**Weaving** is the process of linking aspects with application types or objects to create advised objects. In Spring AOP, weaving is performed **at runtime** during the `BeanPostProcessor` phase of ApplicationContext startup: `AbstractAutoProxyCreator` examines each bean, checks all `@Aspect` pointcuts against the bean's methods, and creates a CGLIB or JDK proxy if any pointcut matches. This proxy — the "woven" object — is registered in the context in place of the original bean. The full AspectJ framework supports two additional weaving strategies: **compile-time weaving** (AspectJ compiler modifies bytecode during build) and **load-time weaving** (LTW — a Java agent transforms bytecode as classes are loaded by the JVM).

---

### 🟢 Simple Definition (Easy)

Weaving is the act of "attaching" aspect code to your target classes. Spring does this at startup by creating proxy objects that wrap your beans. The result is woven code: your class + the aspect behaviour combined.

---

### 🔵 Simple Definition (Elaborated)

Weaving is what turns an aspect definition into actual running code. You define an `@Aspect` class with a pointcut and advice, but nothing actually intercepts method calls until weaving happens. Spring's runtime weaving creates a proxy at startup that wraps each matching bean — the proxy IS the woven result, combining your class's logic with the aspect's behaviour. Compile-time weaving (AspectJ) does the same at build time, modifying `.class` files so the aspect code is embedded directly — no proxy needed, and private methods can be intercepted.

---

### 🔩 First Principles Explanation

**Three weaving strategies:**

```
┌─────────────────────────────────────────────────────┐
│  WEAVING STRATEGIES                                 │
├─────────────────────────────────────────────────────┤
│  1. COMPILE-TIME WEAVING (CTW)                      │
│     Tool: AspectJ compiler (ajc)                    │
│     When: during javac / maven build                │
│     How: AspectJ compiler modifies .class files     │
│     Result: aspect code woven INTO class bytecode   │
│     Pros: private methods, no proxy overhead        │
│     Cons: build tooling required, no runtime flex   │
│                                                     │
│  2. LOAD-TIME WEAVING (LTW)                         │
│     Tool: -javaagent:aspectjweaver.jar              │
│     When: JVM class loading (ClassLoader phase)     │
│     How: Java agent transforms bytecode on load     │
│     Result: aspect code woven into loaded class     │
│     Pros: all AspectJ features, no build change     │
│     Cons: JVM startup arg needed, complex setup     │
│                                                     │
│  3. RUNTIME WEAVING (Spring AOP default)            │
│     Tool: Spring BeanPostProcessor + CGLIB/JDK      │
│     When: ApplicationContext startup                │
│     How: Creates proxy wrapping target bean         │
│     Result: proxy object IS the woven result        │
│     Pros: zero build tooling, Spring-integrated     │
│     Cons: no private method, no constructor, field  │
└─────────────────────────────────────────────────────┘
```

**Runtime weaving sequence (Spring AOP):**

```
For each singleton bean B:
  For each @Aspect A registered in context:
    For each advice method in A:
      Does A's pointcut match ANY method in B?
      If yes → B needs a proxy
  If B needs proxy:
    Create CGLIB (or JDK) proxy for B
    Attach all matching advisors to proxy's chain
    Register PROXY in context (not original B)
```

---

### ❓ Why Does This Exist (Why Before What)

**WITHOUT weaving (manual linking):**

```
Without weaving:

  Aspect defined → advice exists but does nothing
  Must manually register interceptors per bean:
    ProxyFactoryBean proxy = new ProxyFactoryBean();
    proxy.setTarget(orderService);
    proxy.addAdvice(new TransactionInterceptor());
    proxy.addAdvice(new SecurityInterceptor());
    // Repeat for every bean that needs advice

  Refactor: add new service → must update proxy config
  → Error-prone, verbose, not scalable at 100+ beans
```

**WITH weaving:**

```
→ Define aspect once with pointcut: "all service methods"
→ Spring auto-weaves at startup for all matching beans
→ Add new service class: automatically woven (no config)
→ Change aspect: all matching beans re-woven at next start
→ No manual proxy configuration ever needed
```

---

### 🧠 Mental Model / Analogy

> Weaving is like **embedding threads into fabric**. The base fabric is your class (the warp threads — the structure). The pattern thread is your aspect (the weft — the cross-cutting colour). Weaving is the loom action that interleaves them into a single unified fabric. Compile-time weaving is like weaving during manufacture — permanent. Runtime weaving is like applying a decorative jacket to the fabric — removable but covers it completely.

"Base fabric warp threads" = target class methods
"Pattern thread (colour)" = aspect advice code
"Loom interleaving them" = weaving process
"Fabric during manufacture" = compile-time weaving (AspectJ)
"Decorative jacket applied later" = runtime proxy weaving (Spring)

---

### ⚙️ How It Works (Mechanism)

**Spring runtime weaving — BPP phase:**

```java
// Conceptual: AnnotationAwareAspectJAutoProxyCreator
// (extends AbstractAutoProxyCreator, which is a BPP)

@Override
public Object postProcessAfterInitialization(
    Object bean, String beanName) {
  // 1. Is this bean itself an @Aspect? Skip it.
  if (isAspect(bean)) return bean;

  // 2. Get all registered advisors from @Aspect beans
  List<Advisor> advisors = findEligibleAdvisors(bean.getClass());

  // 3. No matching advisors → return original bean, no proxy
  if (advisors.isEmpty()) return bean;

  // 4. Create proxy with all matching advisors attached
  return createProxy(bean, beanName, advisors);
  // proxy returned here replaces original in context
}
```

**Load-time weaving setup (Spring + AspectJ agent):**

```java
// @EnableLoadTimeWeaving enables LTW in plain Spring
@Configuration
@EnableLoadTimeWeaving
public class LtwConfig {}

// JVM startup flag required:
// -javaagent:aspectjweaver-1.9.x.jar

// Now ALL classes are woven on load — including:
// Domain entities, DTOs, classes created with new
// → @Transactional works on domain objects!
// → private methods can be intercepted
```

---

### 🔄 How It Connects (Mini-Map)

```
@Aspect beans registered in ApplicationContext
        ↓
  WEAVING (123)  ← you are here
  (aspect + target → advised proxy / woven class)
        ↓
  Spring runtime weaving:
  AnnotationAwareAspectJAutoProxyCreator (BPP)
  runs at bean creation phase → creates proxy
        ↓
  Alternatively:
  Compile-time weaving (AspectJ ajc)
  Load-time weaving (AspectJ agent)
        ↓
  Result: woven object in ApplicationContext
  All method calls go through advice chain
```

---

### 💻 Code Example

**Example 1 — Verifying weaving occurred (proxy check):**

```java
@SpringBootTest
class WeavingVerificationTest {
  @Autowired OrderService orderService;
  @Autowired UserRepository userRepository;

  @Test
  void transactionalBeansAreWoven() {
    // @Transactional class → woven by runtime proxy
    assertThat(AopUtils.isAopProxy(orderService)).isTrue();
    assertThat(AopUtils.isCglibProxy(orderService)).isTrue();
    assertThat(orderService.getClass().getName())
        .contains("$$SpringCGLIB$$");

    // repository with no AOP → not woven (no proxy)
    // (unless @Transactional is on it)
    assertThat(AopUtils.isAopProxy(userRepository)).isFalse();
  }
}
```

**Example 2 — Load-time weaving to advise domain objects:**

```java
// CTW/LTW solves self-invocation AND non-Spring objects
// Domain entity with @Transactional (normally impossible):
@Entity
public class Invoice {
  @Transactional // works ONLY with AspectJ LTW!
  public void approve() {
    this.status = APPROVED;
    this.auditLog.add(new AuditEntry("approved"));
    // Transaction woven INTO the domain object itself
    // Not possible with Spring proxy-based weaving
  }
}
```

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| Weaving happens every time a method is called | Weaving (proxy creation) happens ONCE at startup. Method interception per-call is a result of the woven proxy, not repeated weaving |
| Spring AOP and full AspectJ weaving are equivalent | Spring AOP supports only method execution on Spring-managed beans. AspectJ CTW/LTW supports field access, constructors, static methods, and non-Spring objects |
| Load-time weaving needs @EnableAspectJAutoProxy | LTW uses the JVM agent (aspectjweaver.jar) — @EnableAspectJAutoProxy is for Spring's runtime proxy weaving, not LTW |
| Disabling AOP disables @Transactional | @Transactional is powered by Spring's proxy-based weaving. Disabling AOP (removing @EnableAspectJAutoProxy) disables custom @Aspect beans but @Transactional still works via its own infrastructure |

---

### 🔥 Pitfalls in Production

**1. Expecting compile-time weaving features from Spring AOP**

```java
// BAD: expecting @Transactional on entity domain method
@Entity
class Order {
  @Transactional  // Spring AOP CANNOT weave this
  public void cancel() {
    // No proxy exists for JPA-managed entity
    // @Transactional silently does nothing
  }
}
// FIX: move logic to @Service, OR use AspectJ LTW

@Service
class OrderService {
  @Transactional         // woven by Spring proxy
  public void cancelOrder(long id) {
    Order order = repo.findById(id).orElseThrow();
    order.cancel(); // domain call — no transaction needed here
    repo.save(order);
  }
}
```

**2. Adding -javaagent LTW to production without testing**

```bash
# LTW instruments ALL loaded classes — broad impact
# BAD: add LTW agent to prod without load testing
java -javaagent:aspectjweaver.jar -jar app.jar
# → 10-20% startup time increase
# → Increased memory (transformed bytecode held)
# → Interaction with other agents (profilers, APMs)

# GOOD: profile LTW overhead in staging first
# Measure: startup time, heap usage, CPU during load
# Consider: is compile-time weaving feasible instead?
```

---

### 🔗 Related Keywords

- `Aspect` — the module that is woven into target code
- `AOP` — the paradigm; weaving is the mechanism that makes it work
- `CGLIB Proxy` — the proxy created during Spring's runtime weaving
- `BeanPostProcessor` — the Spring hook where runtime weaving occurs
- `AspectJ` — provides compile-time and load-time weaving beyond Spring AOP
- `@Transactional` — woven at Spring startup; only method execution on proxied beans

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ KEY IDEA     │ Linking aspects to targets — Spring does  │
│              │ this at runtime via BPP proxy creation    │
├──────────────┼───────────────────────────────────────────┤
│ USE WHEN     │ Spring AOP (runtime): standard Spring use │
│              │ AspectJ CTW/LTW: domain objects, private  │
├──────────────┼───────────────────────────────────────────┤
│ AVOID WHEN   │ Don't expect Spring weaving to intercept  │
│              │ private methods or non-Spring objects     │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "Weaving is the loom that turns aspect    │
│              │  thread and class fabric into one cloth." │
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ DispatcherServlet (124) →                 │
│              │ @Transactional (127) → AspectJ LTW        │
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** Spring Boot 3 / Spring Framework 6 introduced AOT (Ahead-of-Time) compilation for GraalVM native images. In a native image, runtime weaving (CGLIB proxy generation) is fundamentally impossible because bytecode generation is prohibited at native runtime. Describe exactly how Spring AOT moves weaving from runtime to build time — what gets generated at build time to replace CGLIB proxy creation — and explain what AOP functionality is unavailable in a GraalVM native image even with AOT processing.

**Q2.** AspectJ's load-time weaving (LTW) uses a Java agent that installs a `ClassFileTransformer`. Explain the exact lifecycle: when does the transformer run relative to class loading, what ClassLoader hierarchy aspect does it interact with in a Spring Boot application (which uses a custom `LaunchedClassLoader`), and describe the specific failure mode when LTW is enabled in a Spring Boot fat JAR where the aspectjweaver agent cannot access nested JAR classes.

