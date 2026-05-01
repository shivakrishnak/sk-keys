---
layout: default
title: "Weaving"
parent: "Spring Core"
nav_order: 391
permalink: /spring/weaving/
number: "391"
category: Spring Core
difficulty: ★★★
depends_on: "AOP (Aspect-Oriented Programming), Aspect, Pointcut, CGLIB Proxy, JDK Dynamic Proxy"
used_by: "AOP (Aspect-Oriented Programming), @Transactional, Aspect"
tags: #advanced, #spring, #internals, #jvm, #deep-dive
---

# 391 — Weaving

`#advanced` `#spring` `#internals` `#jvm` `#deep-dive`

⚡ TL;DR — **Weaving** is the process of applying Aspects to target objects. Spring AOP uses **runtime weaving** (via proxy generation at context startup), while AspectJ supports **compile-time** and **load-time** weaving for field access and non-managed objects.

| #391            | Category: Spring Core                                                               | Difficulty: ★★★ |
| :-------------- | :---------------------------------------------------------------------------------- | :-------------- |
| **Depends on:** | AOP (Aspect-Oriented Programming), Aspect, Pointcut, CGLIB Proxy, JDK Dynamic Proxy |                 |
| **Used by:**    | AOP (Aspect-Oriented Programming), @Transactional, Aspect                           |                 |

---

### 📘 Textbook Definition

**Weaving** is the AOP process of linking Aspects to target objects or types — inserting Advice code at Pointcut-matched JoinPoints to create the advised object. There are three weaving strategies: **compile-time weaving (CTW)** — the AspectJ compiler (`ajc`) modifies the class bytecode during compilation, inserting advice directly; **load-time weaving (LTW)** — a Java agent (`javaagent`) intercepts class loading and instruments bytecode as classes are loaded into the JVM; and **runtime weaving** — the approach Spring AOP uses, creating proxy objects at context startup that wrap the target bean and route calls through the advice chain. Spring's runtime weaving is performed by `AnnotationAwareAspectJAutoProxyCreator` (a `BeanPostProcessor`) in `postProcessAfterInitialization`, creating a CGLIB or JDK proxy for any bean that has applicable Advice. Spring also supports LTW via `@EnableLoadTimeWeaving` and the Spring `InstrumentationLoadTimeWeaver`, enabling full AspectJ features (field interception, `@Configurable`) for non-proxy scenarios.

---

### 🟢 Simple Definition (Easy)

Weaving is when Spring "stitches" cross-cutting behaviour (advice) into your beans. Spring does this at runtime by creating proxy objects that wrap the real beans — the weaving happens as the application starts up.

---

### 🔵 Simple Definition (Elaborated)

Imagine your code is a fabric and AOP advice is decorative thread. "Weaving" is the act of threading the advice through the fabric at the right places (join points). Spring weaves at runtime: after all beans are created, it wraps each applicable bean in a proxy that intercepts method calls. This is transparent — the application code only sees the interface, not the proxy wrapping. The alternative is compile-time weaving where the advice is literally compiled into the class bytecode — the fabric comes pre-threaded from the loom. Compile-time weaving is faster at runtime (no proxy overhead) but requires a special compiler and cannot be changed after compilation. Load-time weaving is a middle ground — classes are unmodified until loaded, then the Java agent instruments them on the fly.

---

### 🔩 First Principles Explanation

**The three weaving approaches compared:**

```
┌──────────────────┬──────────────────────────────────────────────────────┐
│ Approach         │ When it happens, how it works, what it enables       │
├──────────────────┼──────────────────────────────────────────────────────┤
│ Compile-Time     │ During javac/ajc compilation                         │
│ Weaving (CTW)    │ AspectJ compiler modifies .class bytecode            │
│                  │ Advice is inlined directly into target class         │
│                  │ Enables: field access, constructor execution,        │
│                  │          static initializer join points              │
│                  │ Requires: ajc compiler (not standard javac)          │
│                  │ Pros: fastest at runtime (no proxy overhead)         │
│                  │ Cons: build toolchain complexity, no runtime change  │
├──────────────────┼──────────────────────────────────────────────────────┤
│ Load-Time        │ During JVM class loading (with -javaagent)           │
│ Weaving (LTW)    │ Java agent intercepts ClassLoader.loadClass()        │
│                  │ AspectJ weaver modifies bytecode before JVM uses it  │
│                  │ Enables: same as CTW (all AspectJ join points)       │
│                  │ Enables: @Configurable (DI for non-Spring objects)   │
│                  │ Requires: -javaagent:spring-instrument.jar JVM arg   │
│                  │ Pros: no source changes, runtime flexibility         │
│                  │ Cons: startup overhead, classloading complexity      │
├──────────────────┼──────────────────────────────────────────────────────┤
│ Runtime Weaving  │ At Spring ApplicationContext startup                 │
│ (Spring AOP)     │ BeanPostProcessor creates CGLIB/JDK proxy            │
│                  │ Proxy intercepts method calls at runtime             │
│                  │ Enables: method execution join points ONLY           │
│                  │ Requires: nothing special (auto in Spring Boot)      │
│                  │ Pros: zero configuration, no compiler changes        │
│                  │ Cons: only method execution, self-invocation bypass  │
└──────────────────┴──────────────────────────────────────────────────────┘
```

**Spring's runtime weaving — step by step:**

```
APPLICATION CONTEXT STARTUP:
  1. All beans are defined (BeanDefinitions registered)
  2. AnnotationAwareAspectJAutoProxyCreator (AAPC) BPP is registered
  3. All @Aspect beans are created and parsed:
     → Pointcuts compiled to AspectJExpressionPointcut
     → Advice methods wrapped as Advisors (Pointcut + Advice)
  4. For each regular singleton bean (postProcessAfterInitialization):
     a. AAPC tests each Advisor's Pointcut against the bean's class
     b. If at least one Advisor matches:
        → Determine proxy type: CGLIB or JDK
        → Create proxy wrapping the original bean
        → Attach matching Advisors as MethodInterceptors
        → Register proxy in ApplicationContext (not the original bean)
     c. If no Advisors match:
        → Return original bean unchanged (no proxy overhead)
  5. Context is READY — all applicable beans are woven proxies
```

**Load-time weaving with @Configurable (beyond proxy-based AOP):**

```java
// Without LTW: DI only works for Spring-managed beans
Order order = new Order(); // plain new — Spring doesn't know this exists
// order.orderRepo is null — Spring can't inject into it

// With LTW + @Configurable: Spring injects into ANY object on instantiation
@Configurable // AspectJ load-time weaver intercepts 'new Order()'
public class Order {
    @Autowired
    private OrderRepository orderRepo; // injected by LTW on 'new Order()'!
}

Order order = new Order(); // LTW intercepts constructor call
// order.orderRepo is now injected from the Spring context!

// Required setup:
// 1. JVM: -javaagent:spring-instrument.jar
// 2. Spring: @EnableLoadTimeWeaving on a @Configuration class
// 3. META-INF/aop.xml declaring @Configurable aspects
```

---

### ❓ Why Does This Exist (Why Before What)

WITHOUT Weaving:

What breaks without it:

1. AOP Aspects cannot be applied — there is no mechanism to intercept method calls.
2. `@Transactional`, `@Cacheable`, `@PreAuthorize` do not work — they rely on weaving.
3. Non-Spring-managed objects (JPA entities, domain objects created with `new`) cannot have DI injected.
4. Cross-cutting concerns must be manually coded into each class.

WITH Weaving (specifically runtime weaving):
→ Zero-configuration AOP for all Spring-managed beans.
→ `@Transactional` transparently wraps methods in transaction boundaries.
→ New beans automatically receive weaving — no re-compilation or agent restart required.
→ Changing Aspects does not require recompiling target classes.

---

### 🧠 Mental Model / Analogy

> Think of weaving as a building inspection process. Compile-time weaving is like embedding safety features during the construction of a building — the fire suppression system is built into the walls while they are being built; it is permanent and efficient. Load-time weaving is like installing safety features when the building is opened — inspectors retrofit fire suppression before occupants enter; flexible but adds opening delay. Runtime weaving (Spring AOP) is like putting a safety officer at the entrance — every person entering passes through the officer first; the building itself is unchanged, but all access is monitored. The safety officer (proxy) can intercept and apply policies without modifying the building (class).

"Building construction" = compilation
"Building opening" = class loading (JVM)
"Occupants in operation" = bean instantiation and method calls
"Compile-time weaving" = safety features built into walls during construction
"Load-time weaving" = retrofit before opening
"Runtime weaving" = safety officer at the entrance (proxy)

---

### ⚙️ How It Works (Mechanism)

**How AAPC determines which beans to weave:**

```java
// Simplified AAPC.postProcessAfterInitialization logic:
@Override
public Object postProcessAfterInitialization(Object bean, String beanName) {
    if (isInfrastructureClass(bean.getClass())) return bean; // skip BPPs, etc.

    List<Advisor> advisors = findEligibleAdvisors(bean.getClass(), beanName);
    if (advisors.isEmpty()) return bean; // no weaving needed

    return createProxy(bean, beanName, advisors, targetSource);
    // Returns CGLIB or JDK proxy — the woven object
}

// createProxy:
// 1. ProxyFactory.setTargetSource(target)
// 2. For each advisor: proxyFactory.addAdvisors(advisors)
// 3. proxyFactory.setProxyTargetClass(true/false)
// 4. return proxyFactory.getProxy() → CGLIB or JDK proxy
```

**Detecting if a bean is woven (proxy):**

```java
Object bean = ctx.getBean("orderService");

// Is it any kind of Spring proxy?
AopUtils.isAopProxy(bean)         // true if CGLIB or JDK proxy

// Specific proxy type:
AopUtils.isCglibProxy(bean)       // true if CGLIB subclass proxy
AopUtils.isJdkDynamicProxy(bean)  // true if JDK interface proxy

// Get all applied advisors on a proxy:
Advised advised = (Advised) bean;
for (Advisor a : advised.getAdvisors()) {
    log.info("Applied advisor: {}", a.getClass().getSimpleName());
}

// Unwrap to get target:
Object target = ((Advised) bean).getTargetSource().getTarget();
```

---

### 🔄 How It Connects (Mini-Map)

```
Aspect (Pointcut + Advice definitions)
        │
        ▼
Weaving  ◄──── (you are here)
(the process of applying Aspects to beans)
        │
        ├──── Runtime Weaving (Spring AOP, default)
        │     → AnnotationAwareAspectJAutoProxyCreator (BPP)
        │     → Creates CGLIB or JDK proxy at context startup
        │     → Method execution join points ONLY
        │
        ├──── Load-Time Weaving (AspectJ LTW)
        │     → -javaagent:spring-instrument.jar
        │     → All AspectJ join points (fields, constructors)
        │     → @Configurable for non-Spring-managed objects
        │
        └──── Compile-Time Weaving (AspectJ CTW)
              → ajc compiler modifies bytecode
              → Fastest runtime, most join point types
              → Complex build setup
```

---

### 💻 Code Example

**Enabling Load-Time Weaving in a Spring Boot application:**

```java
// 1. application.properties or JVM launch flag:
// Spring Boot: spring.aop.proxy-target-class=true (default runtime weaving)
// LTW: requires JVM arg: -javaagent:${SPRING_HOME}/spring-instrument.jar

// 2. Enable LTW in Spring:
@SpringBootApplication
@EnableLoadTimeWeaving(aspectjWeaving = EnableLoadTimeWeaving.AspectJWeaving.AUTODETECT)
class App { ... }

// 3. META-INF/aop.xml — tells AspectJ weaver what to instrument:
// <aspectj>
//   <weaver options="-verbose -debug">
//     <include within="com.example..*"/>
//   </weaver>
//   <aspects>
//     <aspect name="com.example.aspects.TransactionAspect"/>
//   </aspects>
// </aspectj>

// 4. @Configurable domain object:
@Configurable(autowire = Autowire.BY_TYPE)
public class OrderCreatedEvent {
    @Autowired  // injected by LTW on 'new OrderCreatedEvent()'
    private EventPublisher publisher;

    public OrderCreatedEvent(Order order) {
        publisher.publish(this); // works! publisher injected by LTW
    }
}
```

---

### ⚠️ Common Misconceptions

| Misconception                                                | Reality                                                                                                                                                                                                                                                          |
| ------------------------------------------------------------ | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Spring AOP and AspectJ weaving are the same thing            | Spring AOP uses AspectJ's annotation syntax and pointcut language but implements weaving via proxies (runtime). Full AspectJ implements weaving by modifying bytecode (compile-time or load-time). Spring AOP cannot intercept field access; AspectJ can         |
| Runtime weaving creates proxy overhead for every method call | Only beans with applicable Advice are proxied. Beans with no matching Pointcut are returned unchanged — no proxy, no overhead. For proxied beans, the per-call overhead is one extra method dispatch — negligible for typical application code                   |
| Load-time weaving is required for `@Transactional` to work   | `@Transactional` works via Spring AOP's default runtime weaving (proxy-based). LTW is only needed for non-proxy scenarios: field interception, constructor interception, `@Configurable`, or self-invocation bypass                                              |
| Compile-time weaving is always faster than runtime weaving   | CTW eliminates proxy object creation and dispatch but adds complexity to the build pipeline. For typical web applications, the runtime proxy overhead is negligible. CTW is primarily chosen for JoinPoint types that proxies cannot handle, not for performance |

---

### 🔥 Pitfalls in Production

**Runtime weaving limitation: self-invocation bypasses the proxy**

```java
@Service
class PaymentService {
    // Called externally → goes through proxy → @Transactional WORKS
    public void processPayment(Payment p) {
        this.audit(p); // 'this' = raw bean → proxy BYPASSED → @Audited IGNORED
    }

    @Audited   // only works when called through the proxy
    public void audit(Payment p) { ... }
}

// Fix with LTW: AspectJ weaves directly into the class bytecode
// self.audit(p) is woven at the bytecode level — 'this' is intercepted too

// Fix with runtime: extract audit() to separate bean, inject it
```

---

### 🔗 Related Keywords

- `AOP (Aspect-Oriented Programming)` — the paradigm; weaving is how AOP is applied in practice
- `Aspect` — the module being woven; weaving applies Aspect Advice to target JoinPoints
- `CGLIB Proxy` — the proxy mechanism used for runtime weaving of class-based beans
- `JDK Dynamic Proxy` — the proxy mechanism used for runtime weaving of interface-based beans
- `BeanPostProcessor` — `AnnotationAwareAspectJAutoProxyCreator` performs runtime weaving in Phase 6
- `@Transactional` — the most common annotation that triggers runtime weaving

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ WEAVING TYPE │ WHEN           │ TOOL                     │
│ Compile-time │ javac/ajc run  │ AspectJ compiler (ajc)   │
│ Load-time    │ Class loading  │ -javaagent (Spring inst.) │
│ Runtime      │ Context startup│ AAPC BPP → CGLIB/JDK     │
├──────────────┼────────────────────────────────────────────┤
│ SPRING AOP   │ Runtime only, method exec join points      │
│              │ Self-invocation bypasses proxy             │
├──────────────┼────────────────────────────────────────────┤
│ LTW NEEDED   │ @Configurable, field interception,         │
│              │ constructor interception, self-invoke fix  │
├──────────────┼────────────────────────────────────────────┤
│ ONE-LINER    │ "Weaving = stitching advice into code:     │
│              │  at build time (CTW), at load time (LTW),  │
│              │  or at runtime via proxy (Spring AOP)."   │
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** Spring AOP uses runtime weaving — proxies are created at context startup. This means the weaving configuration is baked into the running application and cannot change without a restart. AspectJ load-time weaving re-instruments on each class load — in theory, you could hot-replace Aspect bytecode. Describe the specific OSGi or modular deployment scenario where LTW's per-classload nature provides a deployment advantage, explain why LTW still requires application restart when Aspect definitions change (since `aop.xml` is read at context initialisation), and identify the one practical LTW advantage that remains: instrumenting classes loaded by classloaders that Spring's proxy factory cannot reach (e.g., third-party library classes loaded before the Spring context).

**Q2.** `@Configurable` with LTW allows Spring to inject dependencies into objects created with `new` (e.g., domain objects). Describe the `AnnotationBeanConfigurerAspect` that AspectJ weaves into `@Configurable` classes: at what JoinPoint does it apply advice, how does it obtain the Spring `ApplicationContext` (it needs the context but is applied before Spring is done starting), and what is the `dependencyCheck` attribute for? Also explain the circular dependency risk: if a `@Configurable` domain object is created in a `@PostConstruct` method of a bean that Spring is still initialising, can `AnnotationBeanConfigurerAspect` safely inject dependencies into it?
