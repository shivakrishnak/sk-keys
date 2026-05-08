---
layout: default
title: "Weaving"
parent: "Spring Core"
grand_parent: "Technical Dictionary"
nav_order: 39
permalink: /spring/weaving/
id: SPR-039
category: Spring Core
difficulty: ★★★
depends_on: AOP, Aspect, CGLIB Proxy, JDK Dynamic Proxy, Bean Lifecycle
used_by: Spring AOP, AspectJ, "@Transactional", "@Cacheable"
related: Aspect, Advice, Pointcut, CGLIB Proxy, JDK Dynamic Proxy, AspectJ
tags:
  - spring
  - springboot
  - advanced
  - pattern
  - internals
---

# SPR-039 - Weaving

⚡ TL;DR - Weaving is the process of applying aspect advice to target objects - Spring performs _runtime weaving_ via proxies (applied during bean creation), while full AspectJ also supports _compile-time_ and _load-time weaving_ which intercept self-invocations that proxy-based weaving cannot.

| #391            | Category: Spring Core                                             | Difficulty: ★★★ |
| :-------------- | :---------------------------------------------------------------- | :-------------- |
| **Depends on:** | AOP, Aspect, CGLIB Proxy, JDK Dynamic Proxy, Bean Lifecycle       |                 |
| **Used by:**    | Spring AOP, AspectJ, @Transactional, @Cacheable                   |                 |
| **Related:**    | Aspect, Advice, Pointcut, CGLIB Proxy, JDK Dynamic Proxy, AspectJ |                 |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
You've defined an `@Aspect` with transaction advice. But the advice is just a class - it doesn't automatically intercept anything. The "application" of aspects to targets is the missing step. Weaving is the mechanism that connects the aspect to the target: it's the difference between having a security plan and actually enforcing it.

**THE INVENTION MOMENT:**
"Weaving answers the question: _when_ and _how_ does an Aspect get applied to a target class?"

---

### 📘 Textbook Definition

**Weaving** is the process of linking aspects with other application types (target objects) to create an advised object. In Spring AOP, weaving occurs at **runtime** - specifically during the bean creation phase (via `AbstractAutoProxyCreator`), where target beans are wrapped in proxies. AspectJ supports three weaving modes: **Compile-Time Weaving (CTW)** - the AspectJ compiler (`ajc`) modifies target class bytecode during compilation; the compiled `.class` files contain the woven aspect code directly. **Load-Time Weaving (LTW)** - a Java agent (`-javaagent:aspectjweaver.jar`) modifies bytecode as classes are loaded by the classloader. **Runtime Weaving** - Spring AOP creates proxy objects around already-loaded classes (no bytecode modification). Spring Boot exclusively uses runtime weaving via the proxy mechanism.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
Weaving is "when and how aspects get fused with target code" - Spring does it at runtime via proxies; AspectJ can do it earlier, at compile or load time.

**One analogy:**

> Weaving is like installing security cameras in a building. Compile-time weaving is building the cameras into the walls during construction - permanent, zero runtime overhead. Load-time weaving is installing cameras while people walk through security on entry day - once installed, permanent for that session. Runtime weaving (Spring AOP) is stationing a security guard at each door - the guard intercepts entry/exit, but the room itself is unchanged. The guard approach works for most scenarios but can't intercept movement inside the room (self-invocation).

**One insight:**
The weaving time determines what the aspect CAN intercept. Runtime proxy weaving can only intercept calls that pass through the proxy (from outside the bean). Compile/load-time weaving modifies the bytecode itself, enabling interception of self-invocations, constructors, and field access.

---

### 🔩 First Principles Explanation

**THREE WEAVING TYPES:**

| Type         | When                  | How                                | Can Intercept                                 | Spring Boot?               |
| ------------ | --------------------- | ---------------------------------- | --------------------------------------------- | -------------------------- |
| Compile-time | `javac` / `ajc` phase | Bytecode modification at compile   | Everything (self-calls, constructors, fields) | No (requires ajc)          |
| Load-time    | Class loading         | Java agent intercepts class loader | Everything                                    | Optional (with -javaagent) |
| Runtime      | Bean creation         | Proxy wrapping                     | Cross-bean calls only (no self-calls)         | Default                    |

**SPRING RUNTIME WEAVING PROCESS:**

```
Spring context refresh
    ↓
AbstractBeanFactory.doCreateBean(beanName):
  1. Instantiate bean
  2. Populate fields (@Autowired)
  3. BeanPostProcessor.postProcessAfterInitialization():
     AbstractAutoProxyCreator.postProcessAfterInitialization():
       Does any Aspect match this bean?
         YES → wrapIfNecessary(bean) → createProxy(bean, advisors)
     ← WEAVING HAPPENS HERE (proxy created, aspect woven in)
  4. Return proxy (not raw bean) to container
```

**THE TRADE-OFFS:**

**Runtime weaving (Spring AOP):**

- Pros: Zero build-step changes; pure Java; simple configuration
- Cons: Only method execution join points; no self-invocation; bean must be Spring-managed

**Compile-time weaving (AspectJ CTW):**

- Pros: No runtime overhead (woven into bytecode); ALL join points; self-invocation intercepted
- Cons: Requires AspectJ compiler; separate build step; harder to debug

**Load-time weaving (AspectJ LTW):**

- Pros: Same capability as CTW; no build step change
- Cons: Java agent required; class loading overhead; complex setup

---

### 🧪 Thought Experiment

**SETUP:**
`@Transactional` on `UserService.save()`. `UserService.createAndSave()` calls `this.save()` internally.

**WITH RUNTIME WEAVING (Spring AOP):**

```
externalCaller.createAndSave()
    ↓
CGLIB proxy (woven at bean creation)
    ↓ ← weaving interception point
TransactionInterceptor: begin transaction
    ↓
UserService.createAndSave() {
    this.save(user);  // self-call!
    // 'this' = real UserService, not proxy
    // proxy is NOT in the call chain here
    // @Transactional on save() = IGNORED
}
```

**WITH LOAD-TIME WEAVING (AspectJ):**

```
externalCaller.createAndSave()
    ↓
Bytecode-woven UserService.createAndSave():
    // AspectJ inserted transaction code INTO the class bytecode
    begin transaction for createAndSave()
    ↓
    this.save(user);  // AspectJ woven inside save() too
    // @Transactional on save() → woven into save() bytecode
    // REQUIRES_NEW works correctly!
```

**THE INSIGHT:**
The self-invocation limitation is not a Spring bug - it's a fundamental constraint of proxy-based runtime weaving. Moving to load-time weaving removes this limitation at the cost of a Java agent requirement.

---

### 🧠 Mental Model / Analogy

> Weaving types are like installing a telephone interception system. Compile-time weaving is building tap hardware into the phone itself during manufacture - every call from the phone is intercepted, including internal components calling each other. Load-time weaving is installing tap hardware at the phone company's exchange when the phone connects - same capability, done later. Runtime weaving is hiring someone to intercept calls AT THE WALL JACK - they catch external calls coming in/out, but can't intercept internal phone-to-phone extensions (self-invocations) inside the building.

---

### 📶 Gradual Depth - Four Levels

**Level 1 - What it is (anyone can understand):**
Weaving is the actual "applying" of an Aspect to code. Defining an Aspect is just writing code. Weaving is when Spring (or AspectJ) takes that code and wraps it around the target methods.

**Level 2 - How to use it (junior developer):**
For Spring Boot, runtime weaving is automatic - no configuration needed. For load-time weaving with AspectJ, add `-javaagent:aspectjweaver.jar` to JVM args and `@EnableLoadTimeWeaving` to config. For compile-time weaving, use the AspectJ Maven plugin.

**Level 3 - How it works (mid-level engineer):**
Spring's `AnnotationAwareAspectJAutoProxyCreator` (a `BeanPostProcessor` with `Ordered.LOWEST_PRECEDENCE - 1` priority) calls `wrapIfNecessary(bean, beanName)` during `postProcessAfterInitialization`. `wrapIfNecessary` calls `getAdvicesAndAdvisorsForBean()` → `findEligibleAdvisors()` → creates proxy if advisors found. The proxy is the "woven" bean. Load-time weaving uses `ClassFileTransformer` API - `AspectJWeavingEnabler` registers an `AspectJClassBypassingClassFileTransformer` with the JVM's instrumentation API.

**Level 4 - Why it was designed this way (senior/staff):**
Spring's runtime weaving was chosen as the default because it requires no changes to the build process, no external tools, and no JVM agent - just a dependency on `spring-aspects` and `spring-aop`. This reflects Spring's core philosophy: maximum effect with minimum friction. The proxy approach was "good enough for 95% of use cases" and the 5% that need self-invocation interception have a documented escape hatch (LTW). The cost - no self-invocation - is disclosed and understood. Spring 6 + GraalVM reversed this decision for native images: runtime proxy generation is impossible in native executables, so AOT (Ahead-of-Time) compilation moves proxy generation to build time - effectively a form of compile-time weaving, bringing the native-image behavior closer to AspectJ CTW semantics.

---

### ⚙️ How It Works (Mechanism)

**Runtime weaving (Spring default):**

```
BeanPostProcessor chain for UserService:
  AbstractAutoProxyCreator.postProcessAfterInitialization():
    wrapIfNecessary(userService, "userService"):
      getAdvicesAndAdvisorsForBean("userService"):
        → [TransactionAdvisor, LoggingAdvisor]
      createProxy(userService, [advisors]):
        ProxyFactory.getProxy():
          → CglibAopProxy.getProxy() (no interface case)
          → Returns UserService$$CGLIB (woven object)
    ↓
singletonObjects["userService"] = UserService$$CGLIB  ← WOVEN BEAN
```

**Load-time weaving setup:**

```java
// Enable LTW:
@Configuration
@EnableLoadTimeWeaving(aspectjWeaving = AspectJWeaving.ENABLED)
public class LtwConfig {}

// JVM arg required:
// -javaagent:/path/to/aspectjweaver.jar

// aop.xml (on classpath, in META-INF/):
<aspectj>
    <weaver options="-verbose -showWeaveInfo">
        <include within="com.example..*"/>
    </weaver>
    <aspects>
        <aspect name="com.example.LoggingAspect"/>
    </aspects>
</aspectj>
```

---

### 🔄 The Complete Picture - End-to-End Flow

**WEAVING IN THE BEAN LIFECYCLE:**

```
Bean instantiated (new UserService())
    ↓
@Autowired fields populated
    ↓
BeanPostProcessors run
    ↓
AbstractAutoProxyCreator: match aspects to bean ← WEAVING DECISION
    ↓
YES match → create proxy → return proxy
    ↓
NO match → return raw bean
    ↓
singletonObjects[beanName] = result (proxy or raw)
    ↓
@Autowired into other beans: get proxy (if woven) or raw bean
```

---

### 💻 Code Example

**Example 1 - Verifying weaving occurred:**

```java
@Component
public class WeavingVerifier {

    @Autowired ApplicationContext ctx;
    @Autowired UserService userService;  // might be woven (proxied)

    @PostConstruct
    public void verifyWeaving() {
        // Check if bean is proxied (woven)
        System.out.println("Is proxy: " + AopUtils.isAopProxy(userService));
        System.out.println("Is CGLIB: " + AopUtils.isCglibProxy(userService));
        System.out.println("Is JDK: " + AopUtils.isJdkDynamicProxy(userService));
        System.out.println("Actual class: " + userService.getClass().getName());
        // Output if woven:
        // Is proxy: true
        // Is CGLIB: true (assuming no interface)
        // Actual class: com.example.UserService$$EnhancerBySpringCGLIB$$abc123

        // Get the real target (unwrap proxy):
        UserService realBean = (UserService) AopProxyUtils.getSingletonTarget(userService);
        System.out.println("Real class: " + realBean.getClass().getName());
        // Output: com.example.UserService
    }
}
```

**Example 2 - Enabling Load-Time Weaving for self-invocation support:**

```java
@Configuration
@EnableLoadTimeWeaving
public class LtwConfig {}

// application.properties or JVM args:
// spring.aop.proxy-target-class=false  (use AspectJ LTW instead of Spring proxies)
// JVM: -javaagent:/path/to/aspectjweaver.jar
```

---

### ⚖️ Comparison Table

| Aspect                  | Runtime (Spring AOP)  | LTW (AspectJ)          | CTW (AspectJ)         |
| ----------------------- | --------------------- | ---------------------- | --------------------- |
| **Self-invocation**     | Not intercepted       | Intercepted            | Intercepted           |
| **Join points**         | Method execution only | All                    | All                   |
| **Build impact**        | None                  | None (agent only)      | Requires ajc compiler |
| **Runtime impact**      | Proxy per bean        | Class loading overhead | Zero (compiled in)    |
| **Complexity**          | Low                   | Medium                 | High                  |
| **Spring Boot default** | YES                   | Optional               | No                    |

---

### ⚠️ Common Misconceptions

| Misconception                                        | Reality                                                                                                                                           |
| ---------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------- |
| Spring AOP and AspectJ weaving are the same          | Spring AOP uses proxy-based runtime weaving. Full AspectJ uses bytecode modification. Same annotation syntax, fundamentally different mechanisms. |
| Adding -javaagent enables Spring AOP self-invocation | -javaagent enables AspectJ LTW, which IS different from Spring AOP. Both can coexist.                                                             |
| All beans are woven (proxied) by default             | Only beans that have at least one matching aspect are proxied. Beans with no aspect matches are not wrapped.                                      |

---

### 🚨 Failure Modes & Diagnosis

**@Transactional not working on self-invocation (runtime weaving limitation)**

**Symptom:** Transaction REQUIRES_NEW doesn't create a new transaction when called from within the same class.

**Root Cause:** Runtime weaving only intercepts cross-bean calls. Self-invocations bypass the proxy.

**Fix (options in order of preference):**

1. Refactor method into separate bean
2. Enable AspectJ LTW (`-javaagent:aspectjweaver.jar` + `@EnableLoadTimeWeaving`)
3. Inject self via `@Autowired private UserService self`
4. Use `AopContext.currentProxy()` (requires `@EnableAspectJAutoProxy(exposeProxy = true)`)

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**

- `AOP` - Weaving is the application phase of AOP
- `CGLIB Proxy / JDK Dynamic Proxy` - the mechanisms used in Spring's runtime weaving
- `Aspect` - what gets woven into the target

**Builds On This (learn these next):**

- `@Transactional` - the most visible consumer of Spring's runtime weaving
- `DispatcherServlet` - the MVC pattern; not AOP but same "interception" concept

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ WHAT IT IS   │ Process of applying Aspects to targets   │
│              │ (runtime=proxy, load-time=agent, CTW=ajc) │
├──────────────┼───────────────────────────────────────────┤
│ SPRING       │ Runtime weaving: proxy created in         │
│ DEFAULT      │ postProcessAfterInitialization()          │
├──────────────┼───────────────────────────────────────────┤
│ KEY          │ Runtime = no self-invocation interception  │
│ LIMITATION   │ LTW/CTW = self-invocation intercepted     │
├──────────────┼───────────────────────────────────────────┤
│ VERIFY       │ AopUtils.isAopProxy(bean)                  │
│              │ AopProxyUtils.getSingletonTarget(proxy)   │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "The act of applying aspect code to       │
│              │  targets - Spring does it at bean creation"│
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** Spring Boot's runtime weaving creates proxies during `postProcessAfterInitialization`. But what if an `@Aspect` bean itself has `@Transactional` on one of its methods? When Spring processes the `@Aspect` bean through `AbstractAutoProxyCreator`, does it create a proxy for the aspect class too? Or is the aspect class excluded from proxy creation? What would happen if Spring tried to apply AOP to the aspect class?

**Q2.** GraalVM native images don't allow runtime bytecode generation (no CGLIB at runtime). Spring 6 solves this with "AOT proxy generation" - generating proxy classes at build time. Conceptually, what's the difference between Spring 6 AOT proxy generation and AspectJ compile-time weaving? What can AOT proxy generation do that CTW cannot, and vice versa?
