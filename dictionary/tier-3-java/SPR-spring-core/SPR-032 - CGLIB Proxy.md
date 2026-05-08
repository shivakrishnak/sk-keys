---
layout: default
title: "CGLIB Proxy"
parent: "Spring Core"
grand_parent: "Technical Dictionary"
nav_order: 32
permalink: /spring/cglib-proxy/
id: SPR-032
category: Spring Core
difficulty: ★★★
depends_on: Bean, "@Configuration / @Bean", AOP, Bean Lifecycle, Circular Dependency
used_by: "@Configuration, @Transactional, @Cacheable, AOP, @Lazy"
related: JDK Dynamic Proxy, Aspect, Weaving, Proxy Pattern, ByteBuddy
tags:
  - spring
  - springboot
  - advanced
  - pattern
  - internals
---

# SPR-032 - CGLIB Proxy

⚡ TL;DR - CGLIB Proxy is Spring's subclass-based bytecode proxy - it generates a new class that extends the target class at runtime, enabling Spring to intercept method calls without requiring an interface, used for `@Configuration`, `@Transactional`, `@Cacheable`, and AOP on concrete classes.

| #384            | Category: Spring Core                                                  | Difficulty: ★★★ |
| :-------------- | :--------------------------------------------------------------------- | :-------------- |
| **Depends on:** | Bean, @Configuration / @Bean, AOP, Bean Lifecycle, Circular Dependency |                 |
| **Used by:**    | @Configuration, @Transactional, @Cacheable, AOP, @Lazy                 |                 |
| **Related:**    | JDK Dynamic Proxy, Aspect, Weaving, Proxy Pattern, ByteBuddy           |                 |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
You annotate a concrete class `UserService` (no interface) with `@Transactional`. The transaction advice must intercept calls to `save()` to start/commit/rollback transactions. But JDK dynamic proxies only work with interfaces. `UserService` has no interface. Without CGLIB, `@Transactional` would be silently ignored for classes without interfaces - or you'd be forced to extract an interface for every service just to get transaction management.

**THE BREAKING POINT:**
Java interfaces are a design decision about API contracts, not a technical requirement for method interception. Forcing every transactional class to implement an interface to enable transaction management couples a non-functional concern (transaction advice) to an architectural pattern (interface extraction). This conflates infrastructure concerns with design concerns.

**THE INVENTION MOMENT:**
"This is exactly why CGLIB bytecode generation was integrated into Spring."

---

### 📘 Textbook Definition

**CGLIB (Code Generation Library) Proxy** is a mechanism whereby Spring generates a new Java class at runtime (or build time in Spring 6 AOT) that _extends_ the target bean class. The generated subclass overrides each non-final method with interception logic that calls Spring's `MethodInterceptor` chain before and/or after delegating to the original method (`super.method()`). Unlike JDK dynamic proxies (which require an interface), CGLIB proxies require only that the class is non-final and has non-private, non-final methods to intercept. Spring uses CGLIB in two contexts: (1) `@Configuration` class enhancement (singleton guarantees), and (2) AOP proxying when the target bean has no interfaces (or `proxyTargetClass=true` is set).

---

### ⏱️ Understand It in 30 Seconds

**One line:**
CGLIB creates a subclass of your class that sneaks extra code (transactions, caching, logging) around every method call.

**One analogy:**

> CGLIB proxy is like a mannequin wearing your clothes, standing at your desk. Visitors (method callers) talk to the mannequin first - it handles paperwork (transaction management, caching), then calls you for the actual work, then handles more paperwork (commit/rollback). From the visitor's perspective, they talked to "you" (same class type). The mannequin (subclass) is a perfect physical stand-in.

**One insight:**
The subclassing approach means the CGLIB proxy IS a `UserService` (it's a subclass) - `instanceof UserService` returns `true`, and type-safe injection works without declaring interfaces. The constraint is that you can't intercept `final` methods - the mannequin can't override things the original declared as unchangeable.

---

### 🔩 First Principles Explanation

**CORE INVARIANTS:**

1. CGLIB creates a subclass at runtime - the proxy IS-A the original class.
2. The target bean class must not be `final`.
3. Methods to be intercepted must not be `final` or `private`.
4. `@Configuration` classes are ALWAYS CGLIB-proxied (for `@Bean` singleton guarantees).
5. AOP advice: CGLIB is used when no interface exists, or `proxyTargetClass=true`.
6. The constructor of the proxied class is called once - the subclass constructor calls `super()`.

**DERIVED DESIGN:**
The proxy pattern: `CallerCode → CGLIBProxy.method() → interceptors → TargetObject.method()`. The CGLIB subclass intercepts the call, runs the advice, then calls `super.method()` (the original) on the _real_ bean object stored inside the proxy.

Wait - CGLIB wraps the original object, it doesn't call `super()` on itself for business logic. The generated class holds a reference to the _original_ bean instance and delegates:

```java
class UserService$$CGLIB extends UserService {
    private final UserService target;  // real bean
    private final MethodInterceptor[] interceptors;

    @Override
    public User save(User user) {
        // CGLIB interception chain
        for (MethodInterceptor i : interceptors) i.intercept(target, method, args);
        // Then delegate
        return target.save(user);
    }
}
```

**THE TRADE-OFFS:**

**Gain:** Works on concrete classes; type-compatible (IS-A); enables `@Transactional`, `@Cacheable`, AOP without interface extraction.

**Cost:** Restricted to non-final classes/methods; one extra object (the proxy) per bean; constructor called → constructor side-effects run; CGLIB class generation overhead at startup; Spring 6 AOT moves generation to build time.

---

### 🧪 Thought Experiment

**SETUP:**
`@Transactional` on `UserService.save()`. Spring must begin a transaction before the method and commit/rollback after.

**WITHOUT CGLIB (JDK proxy, interface required):**

```java
// Must extract interface
interface UserServiceInterface { User save(User user); }
@Service class UserService implements UserServiceInterface {
    public User save(User user) { ... }
}
// JDK proxy wraps the interface
UserServiceInterface proxy = Proxy.newProxyInstance(
    loader, new Class[]{UserServiceInterface.class}, handler);
```

`UserService` (concrete) cannot be injected where `UserService` is the type - must use `UserServiceInterface`.

**WITH CGLIB (concrete class):**

```java
@Service
@Transactional
public class UserService {  // No interface needed
    public User save(User user) { ... }
}
// Spring generates:
// class UserService$$EnhancerBySpringCGLIB$$abc123 extends UserService
// Injects the CGLIB subclass wherever UserService is @Autowired
```

`@Autowired UserService svc` → gets the CGLIB proxy. `svc instanceof UserService` → `true`. Method calls intercepted transparently.

**THE INSIGHT:**
The "mannequin wears the same clothes" - the CGLIB proxy IS-A `UserService`, making it transparently injectable via `@Autowired UserService`. No interface extraction, no caller changes.

---

### 🧠 Mental Model / Analogy

> CGLIB is a genetic engineering lab. You bring in your `UserService` DNA (class definition), and CGLIB sequences it, modifies the genome (adds method interception code), and prints a new organism (subclass) that behaves identically except at specific trigger points (annotated methods) where it does extra work (transactions, caching). The new organism is genetically "the same species" (`instanceof UserService = true`), so it fits anywhere the original would.

- "DNA" → bytecode of the original class
- "Genetic modification" → CGLIB bytecode weaving
- "New organism" → the generated `UserService$$EnhancerBy...` class
- "Trigger points" → annotated methods (@Transactional, @Cacheable)
- "Same species" → `instanceof UserService` returns `true`

**Where this analogy breaks down:** CGLIB generates a Java class, not bytecode modification of the original class. The original class is unchanged. The generated subclass is a _new_ class that holds a reference to an instance of the original class.

---

### 📶 Gradual Depth - Four Levels

**Level 1 - What it is (anyone can understand):**
CGLIB creates a "wrapper class" that extends your class. When someone calls a method on the wrapper, it runs extra code (transactions, caching) before and after calling your real method. You never see the wrapper - Spring hides it.

**Level 2 - How to use it (junior developer):**
You don't use CGLIB directly. It's used automatically by Spring when: (1) your class has `@Configuration`, (2) your class or method has `@Transactional` and no interface exists, (3) you use AOP on a concrete class. Constraints: don't make these classes `final`. Don't make methods you want intercepted `final` or `private`. Be aware that self-invocation (calling `this.save()` from within the class) bypasses the proxy.

**Level 3 - How it works (mid-level engineer):**
Spring uses `Enhancer` from the CGLIB library (`net.sf.cglib.proxy.Enhancer` or the Spring-repackaged `org.springframework.cglib.proxy.Enhancer`). `Enhancer.setSuperclass(UserService.class)` sets the target. `Enhancer.setCallbackFilter(new ProxyCallbackFilter(...))` assigns callbacks per method. `Enhancer.create()` generates and loads the subclass bytecode. The generated class is named `UserService$$EnhancerBySpringCGLIB$$<hash>`. `DefaultAopProxyFactory.createAopProxy()` decides CGLIB vs JDK based on: `proxyTargetClass=true`, or target has no interfaces, or target has only Spring-internal interfaces.

**Level 4 - Why it was designed this way (senior/staff):**
The choice to use CGLIB for `@Configuration` was specific and intentional: `@Configuration` classes need method-call interception within the class itself (not just from outside), which JDK proxies cannot do (JDK proxies intercept calls from _outside_ the proxy, not `this.method()` calls). CGLIB subclassing intercepts all calls via the subclass method override, including within-class calls if the outer caller holds the proxy reference. The `@Configuration` enhancement specifically leverages this to ensure `@Bean` method calls from within `@Configuration` go through the CGLIB proxy and return the cached singleton. Spring 6 introduced AOT (Ahead-of-Time) compilation support, which generates CGLIB proxy classes at build time instead of runtime - this is essential for GraalVM native images, which cannot load dynamically generated classes at runtime.

---

### ⚙️ How It Works (Mechanism)

**CGLIB proxy creation:**

```
AbstractAutoProxyCreator.postProcessAfterInitialization(bean, beanName)
    ↓
Should this bean be proxied? (has @Transactional, is AOP target?)
    YES ↓
DefaultAopProxyFactory.createAopProxy(AdvisedSupport config):
    config.isProxyTargetClass() || !config.hasInterfaceProxies()?
        YES → create CglibAopProxy
        NO  → create JdkDynamicAopProxy
    ↓
CglibAopProxy.getProxy(ClassLoader classLoader):
    Enhancer enhancer = new Enhancer()
    enhancer.setSuperclass(targetClass)       // UserService.class
    enhancer.setInterfaces(proxiedInterfaces) // if any
    enhancer.setCallbacks(callbacks)          // interceptors
    enhancer.setCallbackFilter(filter)        // method → callback mapping
    return enhancer.create()                  // generate + load class
```

**Method interception at runtime:**

```
caller.save(user)  →  UserService$$CGLIB.save(user) (override)
    ↓
CglibMethodInvocation.proceed()
    ↓
TransactionInterceptor.invoke():
    begin transaction
    proceed()  →  target.save(user)  (real bean)
    commit or rollback
    ↓
return result to caller
```

**Self-invocation problem:**

```java
@Service
public class UserService {
    @Transactional
    public void createAndNotify(User user) {
        save(user);         // ← calls this.save() - bypasses proxy!
        sendNotification(); // same - bypasses proxy!
    }

    @Transactional(propagation = REQUIRES_NEW)
    public void save(User user) {
        // The REQUIRES_NEW never activates when called via this.save()
    }
}
```

---

### 🔄 The Complete Picture - End-to-End Flow

**CREATION AND INJECTION:**

```
@Service UserService class detected by component scan
    ↓
UserService bean created (real object)
    ↓
BeanPostProcessor chain: AbstractAutoProxyCreator
    ↓
Checks: @Transactional present on class or methods?
    YES ← YOU ARE HERE (CGLIB proxy decision made)
    ↓
CglibAopProxy.getProxy() → generates UserService$$CGLIB
    ↓
Returns UserService$$CGLIB to container
    ↓
singletonObjects["userService"] = UserService$$CGLIB instance
    ↓
@Autowired UserService svc → gets UserService$$CGLIB
    ↓
svc.save(user) → UserService$$CGLIB.save() → interceptors → real save()
```

**WHAT CHANGES AT SCALE:**
CGLIB class generation adds to JVM startup time (one class per proxied bean). At scale (hundreds of proxied beans), this is measurable. Spring Boot 3.x with GraalVM native images moves CGLIB generation to build time - eliminating all runtime overhead. For regular JVM deployments, the overhead is generally acceptable but can be reduced by using JDK proxies where possible (provide interfaces, avoid `proxyTargetClass=true` globally).

---

### 💻 Code Example

**Example 1 - @Transactional on a class with no interface:**

```java
// No interface needed - CGLIB handles proxying
@Service
@Transactional
public class UserService {

    private final UserRepository repo;

    public UserService(UserRepository repo) {
        this.repo = repo;
    }

    public User save(User user) {
        return repo.save(user);  // runs inside transaction
    }
}

// Injection - gets CGLIB proxy, not UserService directly
@RestController
public class UserController {
    @Autowired
    UserService userService;  // actually UserService$$EnhancerBySpringCGLIB...

    @PostMapping("/users")
    public User create(@RequestBody User user) {
        return userService.save(user);  // proxy intercepts → transaction starts
    }
}
```

**Example 2 - Detecting CGLIB proxy at runtime:**

```java
@Component
public class ProxyInspector {

    @Autowired
    ApplicationContext ctx;

    @PostConstruct
    public void inspect() {
        Object userService = ctx.getBean("userService");
        System.out.println(userService.getClass().getName());
        // "com.example.UserService$$EnhancerBySpringCGLIB$$a1b2c3"
        System.out.println(AopUtils.isCglibProxy(userService));  // true
        System.out.println(userService instanceof UserService);  // true
    }
}
```

**Example 3 - Self-invocation bypass (the footgun):**

```java
@Service
public class ReportService {

    @Transactional
    public void generateReport(Long id) {
        // Direct call - goes to THIS object, not through the CGLIB proxy
        // @Transactional on saveAudit() is IGNORED here!
        saveAudit(id);
    }

    @Transactional(propagation = REQUIRES_NEW)
    public void saveAudit(Long id) {
        // This runs in the SAME transaction as generateReport()
        // because the proxy was bypassed by self-invocation
    }
}

// FIX: Inject self reference to force proxy routing
@Service
public class ReportService {
    @Autowired
    private ReportService self;  // CGLIB proxy of this bean

    @Transactional
    public void generateReport(Long id) {
        self.saveAudit(id);  // goes through CGLIB proxy → REQUIRES_NEW works
    }
}
```

---

### ⚖️ Comparison Table

| Proxy Type      | Mechanism           | Interface Required | Final Class OK         | Self-Invocation Intercepted | Used For                                        |
| --------------- | ------------------- | ------------------ | ---------------------- | --------------------------- | ----------------------------------------------- |
| **CGLIB**       | Subclass generation | No                 | No (must be non-final) | No                          | @Configuration, @Transactional on concrete, AOP |
| **JDK Dynamic** | Interface impl      | Yes                | Yes                    | No                          | @Transactional on interface-impl, AOP           |
| **ByteBuddy**   | Bytecode agent      | No                 | With agent             | Possible (with agent)       | Mockito mocks, some frameworks                  |

**How to choose:** Spring makes this decision automatically. The developer's role: don't make classes or methods `final` if they need Spring interception. Prefer programming to interfaces to enable JDK proxies where proxy semantics need to be controlled precisely.

---

### ⚠️ Common Misconceptions

| Misconception                                     | Reality                                                                                                                                   |
| ------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------- |
| CGLIB modifies the original class bytecode        | CGLIB generates a NEW subclass. The original class is untouched.                                                                          |
| @Transactional works on private methods via CGLIB | Private methods cannot be overridden by subclasses - CGLIB cannot intercept them. @Transactional on private methods is silently ignored.  |
| instanceof checks fail on CGLIB proxies           | False - the CGLIB proxy IS-A the original class (it's a subclass). instanceof returns true.                                               |
| CGLIB proxy intercepts self-invocations           | No - self-invocations via `this.method()` bypass the proxy entirely. The proxy only intercepts calls from outside the object.             |
| Spring always uses CGLIB for @Transactional       | Spring uses JDK proxy when the bean implements interfaces (unless proxyTargetClass=true). CGLIB is the fallback for no-interface classes. |

---

### 🚨 Failure Modes & Diagnosis

**Cannot subclass final class**

**Symptom:**
`BeanCreationException: Could not generate CGLIB subclass of class UserService: Common causes of this problem include using a final class`

**Root Cause:**
`UserService` is declared `final`. CGLIB cannot create a subclass of a final class.

**Fix:**

```java
// BAD:
@Service
@Transactional
public final class UserService { ... }  // final prevents CGLIB

// GOOD:
@Service
@Transactional
public class UserService { ... }  // CGLIB can subclass
```

---

**@Transactional silently not working (self-invocation)**

**Symptom:**
`@Transactional(propagation = REQUIRES_NEW)` doesn't start a new transaction. The `save()` method runs in the same transaction as the caller.

**Root Cause:**
`save()` is called via `this.save()` inside the same class. `this` is the raw bean, not the CGLIB proxy. The proxy is bypassed.

**Diagnostic Command / Tool:**

```java
// At the start of saveAudit(), log the transaction name:
TransactionSynchronizationManager.getCurrentTransactionName()
// If it shows the caller's transaction name, the proxy was bypassed
```

**Fix:**

```java
// Option 1: Inject self
@Autowired private ReportService self;
self.saveAudit(id);

// Option 2: Use AspectJ weaving (intercepts this.method() calls)
// Option 3: Refactor into separate bean
```

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**

- `AOP` - CGLIB is the mechanism that enables AOP for non-interface beans
- `@Configuration / @Bean` - @Configuration is always CGLIB-proxied
- `Bean Lifecycle` - CGLIB proxying happens in the BeanPostProcessor phase

**Builds On This (learn these next):**

- `JDK Dynamic Proxy` - the interface-based alternative; understand both to know when each is used
- `@Transactional` - the most common reason a concrete bean gets CGLIB-proxied
- `Weaving` - the AOP concept that CGLIB proxying implements at runtime

**Alternatives / Comparisons:**

- `JDK Dynamic Proxy` - interface-based, lighter weight, requires interface
- `AspectJ weaving` - compile-time or load-time, intercepts self-invocation, not Spring-proxy-based

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ WHAT IT IS   │ Runtime subclass generation that          │
│              │ intercepts method calls for AOP/advice    │
├──────────────┼───────────────────────────────────────────┤
│ PROBLEM IT   │ JDK proxies require interfaces; CGLIB     │
│ SOLVES       │ works on concrete classes                 │
├──────────────┼───────────────────────────────────────────┤
│ KEY INSIGHT  │ CGLIB proxy IS-A the original class (sub- │
│              │ class), so injection works without iface  │
├──────────────┼───────────────────────────────────────────┤
│ CONSTRAINTS  │ Class must not be final; methods must not │
│              │ be final or private                       │
├──────────────┼───────────────────────────────────────────┤
│ SELF-        │ this.method() BYPASSES the proxy - AOP/   │
│ INVOCATION   │ @Transactional won't fire on self-calls   │
├──────────────┼───────────────────────────────────────────┤
│ TRADE-OFF    │ No interface required vs final restriction │
│              │ and self-invocation bypass                │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "CGLIB makes a genetic clone of your      │
│              │  class that intercepts method calls."     │
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ JDK Dynamic Proxy → AOP → @Transactional  │
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** Spring's `@Configuration` always uses CGLIB, even when `proxyTargetClass=false`. Why? What specific behavior does `@Configuration` require that JDK dynamic proxies cannot provide, even if the `@Configuration` class implements an interface?

**Q2.** In Spring Boot 3 + GraalVM native images, CGLIB bytecode generation at runtime is not possible. Spring 6 solved this with "proxyBeanMethods=false" on `@Configuration` (lite mode) and build-time AOT proxy generation. If you set `proxyBeanMethods=false` on your `@Configuration` class in a standard JVM application (not native), what changes in behavior? Is this safe, and under what conditions?
