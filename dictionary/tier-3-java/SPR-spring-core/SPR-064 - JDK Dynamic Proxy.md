---
version: 2
layout: default
title: "JDK Dynamic Proxy"
parent: "Spring Core"
grand_parent: "Technical Dictionary"
nav_order: 64
permalink: /spring/jdk-dynamic-proxy/
id: SPR-082
category: Spring Core
difficulty: ★★★
depends_on: Bean, AOP, CGLIB Proxy, Bean Lifecycle
used_by: "@Transactional, AOP, Spring Data Repository Interfaces"
related: CGLIB Proxy, Aspect, Weaving, InvocationHandler, Proxy Pattern
tags:
  - spring
  - springboot
  - advanced
  - pattern
  - internals
---

# SPR-064 - JDK Dynamic Proxy

⚡ TL;DR - JDK Dynamic Proxy creates a runtime implementation of an interface (not a class subclass) by delegating all calls through a single `InvocationHandler`, which Spring uses to intercept @Transactional, AOP advice, and Spring Data repository method calls for interface-typed beans.

| #385            | Category: Spring Core                                          | Difficulty: ★★★ |
| :-------------- | :------------------------------------------------------------- | :-------------- |
| **Depends on:** | Bean, AOP, CGLIB Proxy, Bean Lifecycle                         |                 |
| **Used by:**    | @Transactional, AOP, Spring Data Repository Interfaces         |                 |
| **Related:**    | CGLIB Proxy, Aspect, Weaving, InvocationHandler, Proxy Pattern |                 |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
To add transaction management or logging around a `UserRepository`, you'd write a `UserRepositoryWrapper` class by hand: implement the interface, delegate every method to the real repository, and add pre/post logic. With 50 repositories and 10 concerns (transactions, caching, auditing, logging...), you need 500 wrapper classes. Every time a method is added to a repository interface, every wrapper must be updated. The combinatorial explosion makes it economically impossible to apply cross-cutting concerns systematically.

**THE BREAKING POINT:**
The boilerplate is O(methods × concerns): every new method means N new wrapper implementations. The wrappers must exactly mirror the interface. Forgetting to delegate one method silently drops functionality. Adding a new cross-cutting concern requires editing every existing wrapper class.

**THE INVENTION MOMENT:**
"This is exactly why `java.lang.reflect.Proxy` was created - and why Spring wraps it for AOP and repository magic."

---

### 📘 Textbook Definition

A **JDK Dynamic Proxy** is a runtime-generated class that implements one or more Java interfaces. Created by `java.lang.reflect.Proxy.newProxyInstance(ClassLoader, Class<?>[], InvocationHandler)`, the generated class intercepts all interface method calls and routes them through a single `InvocationHandler.invoke(Object proxy, Method method, Object[] args)` method. The `InvocationHandler` can execute pre-logic, delegate to the real object, execute post-logic, or not delegate at all. Spring uses JDK dynamic proxies as the default AOP proxy mechanism when the target bean implements at least one interface (and `proxyTargetClass=false`, the default). Spring Data uses JDK dynamic proxies to implement repository interfaces entirely (no real class - the `InvocationHandler` IS the implementation).

---

### ⏱️ Understand It in 30 Seconds

**One line:**
JDK Dynamic Proxy creates a fake-but-real implementation of your interface at runtime, with your custom code running before/after each method.

**One analogy:**

> JDK Dynamic Proxy is a universal receptionist. You give her a script (InvocationHandler) and a list of responsibilities (interface methods). For every call that comes in ("save a user," "find all orders"), she handles the paperwork first (start transaction), passes the request to the real employee (real service), then handles more paperwork (commit/rollback). She never specializes - she handles all calls through the same universal script. The caller only knows there's a receptionist at the desk (the interface), not what's behind her.

**One insight:**
The proxy IS the interface implementation - the caller cannot tell whether they're talking to the original class or the proxy. This is the Proxy design pattern: the proxy has the same interface as the subject, and callers are unaware of the indirection.

---

### 🔩 First Principles Explanation

**CORE INVARIANTS:**

1. JDK proxies can ONLY proxy interfaces - not concrete classes.
2. The generated proxy class is a new class that `implements` all specified interfaces.
3. All method calls go through ONE `InvocationHandler.invoke()` - no per-method configuration in the generated class.
4. The proxy is-a the interface type (`instanceof UserRepository` → true).
5. The proxy is NOT-A the concrete class (`instanceof JpaUserRepository` → false).

**DERIVED DESIGN:**
`Proxy.newProxyInstance()` generates bytecode at runtime that:

```
interface UserRepository:
    User findById(Long id);
    User save(User user);
    void delete(Long id);

Generated class (conceptual):
class $Proxy42 implements UserRepository {
    InvocationHandler h;

    public User findById(Long id) {
        return h.invoke(this, findByIdMethod, new Object[]{id});
    }
    public User save(User user) {
        return h.invoke(this, saveMethod, new Object[]{user});
    }
    public void delete(Long id) {
        h.invoke(this, deleteMethod, new Object[]{id});
    }
}
```

**THE TRADE-OFFS:**

**Gain:** Works without any code generation library; built into JDK since 1.3; lightweight (proxy class is tiny - all logic in InvocationHandler); `null` delegation possible (Spring Data repositories: no real class needed).

**Cost:** Interface required; concrete classes cannot be proxied; `instanceof ConcreteClass` returns false (callers must use the interface type); method reflection overhead per call (optimized by JIT, negligible in practice).

---

### 🧪 Thought Experiment

**SETUP:**
Apply transaction management to `UserRepository` (an interface, implemented by `JpaUserRepository`).

**WITHOUT JDK PROXY (hand-written wrapper):**

```java
class TransactionalUserRepository implements UserRepository {
    private final UserRepository real;
    private final TransactionManager tm;

    public User save(User user) {
        TransactionStatus tx = tm.begin();
        try {
            User result = real.save(user);  // delegate
            tm.commit(tx);
            return result;
        } catch (Exception e) {
            tm.rollback(tx);
            throw e;
        }
    }
    // + 15 more identical methods
}
```

50 repositories → 50 wrappers. Each with the same try/begin/commit/rollback pattern. Pure boilerplate.

**WITH JDK PROXY:**

```java
InvocationHandler handler = (proxy, method, args) -> {
    TransactionStatus tx = tm.begin();
    try {
        Object result = method.invoke(realRepository, args);  // delegate to real
        tm.commit(tx);
        return result;
    } catch (Exception e) {
        tm.rollback(tx);
        throw e;
    }
};

UserRepository proxy = (UserRepository) Proxy.newProxyInstance(
    loader,
    new Class[]{UserRepository.class},
    handler
);
```

One `InvocationHandler`. Works for ALL repositories. Zero per-method code. Adding a new method to the interface: zero changes to the transaction handler.

**THE INSIGHT:**
A single `InvocationHandler` replaces O(methods × concerns) wrapper methods with O(concerns) handlers. The methods are generic - every method goes through the same handler, which dispatches generically.

---

### 🧠 Mental Model / Analogy

> JDK Dynamic Proxy is a postal forwarder. You set up an address (the interface) and a forwarding service (InvocationHandler). Every letter (method call) that arrives at the address goes through the forwarding office, which stamps it (pre-processing), forwards it to the real recipient (target bean), receives the reply, stamps it again (post-processing), and returns it to the sender. The sender's address book shows the forwarding address - they never know the real address.

- "Address (interface)" → `UserRepository.class`
- "Forwarding office" → `InvocationHandler.invoke()`
- "Stamps" → AOP advice, transaction management
- "Real recipient" → `JpaUserRepository` instance
- "Sender's address book" → `@Autowired UserRepository repo`

**Where this analogy breaks down:** The forwarding office (InvocationHandler) can decide NOT to forward at all - Spring Data repositories do exactly this: the InvocationHandler IS the implementation, and there's no "real recipient" class behind it.

---

### 📶 Gradual Depth - Four Levels

**Level 1 - What it is (anyone can understand):**
JDK Dynamic Proxy is Java's built-in way to create a "fake" object that implements an interface. Every method call to the fake object runs your custom code. Spring uses this to sneak transactions, logging, and other behavior around your service calls without you writing wrapper code.

**Level 2 - How to use it (junior developer):**
You don't create JDK proxies manually in Spring. Spring creates them automatically when: (1) a bean implements an interface and has `@Transactional`, (2) AOP advice targets an interface-implementing bean, (3) you declare a Spring Data repository interface. Your code just uses the interface type. Constraint: always inject using the interface type (`UserRepository repo`), not the concrete class (`JpaUserRepository repo`) - the proxy IS the interface, not the concrete class.

**Level 3 - How it works (mid-level engineer):**
`DefaultAopProxyFactory.createAopProxy()` checks: does the target implement non-Spring interfaces? Is `proxyTargetClass=false`? If yes → creates `JdkDynamicAopProxy` which implements `InvocationHandler`. Spring's `JdkDynamicAopProxy.invoke()` method: (1) finds the applicable `Advisor` chain for the method, (2) wraps them in a `ReflectiveMethodInvocation`, (3) calls `proceed()` which chains through interceptors and eventually reflectively calls the target method. Spring Data's `JdkDynamicAopProxy` equivalent is `SimpleJpaRepository` for JPA repositories, but the `@Repository` interface itself is what callers get - the JDK proxy is the repository.

**Level 4 - Why it was designed this way (senior/staff):**
JDK Dynamic Proxy was chosen as Spring's default (vs CGLIB) because it uses only JDK APIs - no third-party library required, no bytecode manipulation, no class loader complexity. The interface requirement aligns with good OOP practice: programming to interfaces is generally preferred over concrete class coupling. Spring's design nudges users toward interfaces by making JDK proxy the default - if you must write an interface to get `@Transactional`, you're incentivized to design with interfaces. Spring Data took this further: repository interfaces are PURE interface - there's no concrete class at all. The `InvocationHandler` dispatches to generic query execution logic based on method name parsing, annotations, and metadata - enabling the "magic" of `findByFirstNameAndLastName(String, String)` without any implementation code.

---

### ⚙️ How It Works (Mechanism)

**Proxy creation:**

```
Bean creation: JpaUserRepository (implements UserRepository)
    ↓
BeanPostProcessors: AnnotationAwareAspectJAutoProxyCreator
    ↓
Should this bean be proxied? (has @Transactional / AOP advice?)
    YES ↓
DefaultAopProxyFactory.createAopProxy():
    Target implements interfaces AND proxyTargetClass=false?
        YES → JdkDynamicAopProxy
    ↓
JdkDynamicAopProxy.getProxy(classLoader):
    Proxy.newProxyInstance(
        classLoader,
        targetInterfaces,  // [UserRepository.class]
        this              // JdkDynamicAopProxy implements InvocationHandler
    )
    ↓
Returns: $Proxy42 implementing UserRepository
```

**Method call interception:**

```
$Proxy42.save(user)
    ↓
JdkDynamicAopProxy.invoke(proxy, saveMethod, [user])
    ↓
Chain of Interceptors:
  1. ExposeInvocationInterceptor
  2. TransactionInterceptor.invoke()
        → TransactionManager.begin()
        → proceed() →
  3. target.save(user)  // JpaUserRepository.save(user)
        → result
  ← back through chain
  → commit transaction
    ↓
return result
```

**Spring Data - proxy with no real class:**

```
Repository interface: UserRepository extends JpaRepository<User, Long>
No @Repository implementation class written by developer
    ↓
RepositoryFactoryBean.createRepository():
    → JdkDynamicAopProxy with RepositoryMethodInterceptor
    → Method "findByEmail": parse → generate JPA query → execute
    → Method "save": delegate to SimpleJpaRepository.save()
    ↓
Returns: $ProxyN implementing UserRepository
    (no JpaUserRepository ever exists in memory!)
```

---

### 🔄 The Complete Picture - End-to-End Flow

**NORMAL FLOW:**

```
@Transactional UserService depends on UserRepository
    ↓
UserService created → @Transactional → CGLIB proxied
    ↓
UserRepository interface registered
    ↓
Spring Data: JdkDynamicAopProxy created for UserRepository
   ← YOU ARE HERE (JDK proxy is the UserRepository)
    ↓
@Autowired UserRepository → injects the JDK proxy
    ↓
userRepository.save(user) call:
    JDK proxy → InvocationHandler → query execution → DB
    ↓
Return result
```

**WHAT CHANGES AT SCALE:**
JDK proxy method calls go through `Method.invoke()` reflection, which was historically slow but is heavily JIT-optimized in modern JVMs. At scale (millions of calls/sec), the difference vs direct method calls is negligible. The larger concern is the number of proxy objects: one per proxied bean. For short-lived objects (prototype-scope), proxy creation overhead per request can matter - prefer singleton scope for proxied beans.

---

### 💻 Code Example

**Example 1 - JDK proxy in action (Spring @Transactional on interface implementor):**

```java
public interface UserRepository {
    User findById(Long id);
    User save(User user);
}

@Repository
@Transactional  // Spring will JDK-proxy this (has interface)
public class JpaUserRepository implements UserRepository {
    @PersistenceContext EntityManager em;
    public User findById(Long id) { return em.find(User.class, id); }
    public User save(User user) { return em.merge(user); }
}

@Service
public class UserService {
    @Autowired
    UserRepository repo;  // receives JDK proxy, NOT JpaUserRepository

    // This works:
    System.out.println(repo instanceof UserRepository);      // true
    // This fails:
    System.out.println(repo instanceof JpaUserRepository);   // false!
}
```

**Example 2 - Manual JDK proxy (to understand the mechanism):**

```java
// For educational purposes only
UserRepository real = new JpaUserRepository(em);

UserRepository proxy = (UserRepository) Proxy.newProxyInstance(
    UserRepository.class.getClassLoader(),
    new Class<?>[]{ UserRepository.class },
    (p, method, args) -> {
        long start = System.currentTimeMillis();
        Object result = method.invoke(real, args);  // delegate
        long ms = System.currentTimeMillis() - start;
        System.out.printf("%s took %dms%n", method.getName(), ms);
        return result;
    }
);

proxy.save(new User());  // prints "save took 12ms"
```

**Example 3 - Spring Data repository - no impl class needed:**

```java
// No implementation class needed - JDK proxy IS the implementation
public interface UserRepository extends JpaRepository<User, Long> {
    List<User> findByEmail(String email);  // Spring Data parses → JPA query
    Optional<User> findByUsernameIgnoreCase(String username);
}

// Spring creates JDK proxy with RepositoryMethodInterceptor
// No JpaUserRepository class ever written
@Autowired UserRepository repo;  // JDK proxy
repo.findByEmail("alice@example.com");  // InvocationHandler generates/executes JPQL
```

**Example 4 - Forced CGLIB (when you need concrete class injection):**

```java
// Force CGLIB even when interface exists
@EnableAspectJAutoProxy(proxyTargetClass = true)
// OR per-class:
@Scope(proxyMode = ScopedProxyMode.TARGET_CLASS)

// Then injection by concrete type works:
@Autowired JpaUserRepository repo;  // CGLIB proxy of JpaUserRepository
```

---

### ⚖️ Comparison Table

| Feature                         | JDK Dynamic Proxy                   | CGLIB Proxy                             |
| ------------------------------- | ----------------------------------- | --------------------------------------- |
| **Mechanism**                   | Implements interface                | Subclasses concrete class               |
| **Interface required**          | Yes                                 | No                                      |
| **Final class support**         | N/A (interface-based)               | No (can't subclass final)               |
| **instanceof concrete class**   | false                               | true                                    |
| **Self-invocation intercepted** | No                                  | No                                      |
| **Library dependency**          | JDK built-in                        | CGLIB (Spring-bundled)                  |
| **Used for**                    | @Transactional + iface, Spring Data | @Configuration, @Transactional no-iface |

**How to choose:** Spring chooses automatically. You influence it via `proxyTargetClass=true` (force CGLIB) or by ensuring beans implement interfaces (JDK default). Prefer JDK proxies: they use only JDK APIs and nudge toward interface-based design.

---

### ⚠️ Common Misconceptions

| Misconception                                          | Reality                                                                                                                                                          |
| ------------------------------------------------------ | ---------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| JDK proxy == CGLIB proxy for callers                   | For callers using the interface type, behavior is identical. The difference matters for instanceof checks on the concrete type and for self-invocation behavior. |
| Self-invocation works with JDK proxy                   | No - self-invocation bypasses all Spring proxies (JDK and CGLIB). Neither intercepts this.method() calls. AspectJ weaving is needed for that.                    |
| @Autowired by concrete class type works with JDK proxy | No - injecting by concrete type (JpaUserRepository instead of UserRepository) fails when JDK proxy is used, because the proxy doesn't extend the concrete class. |
| JDK proxies are slower than CGLIB                      | Modern JIT eliminates most of the Method.invoke() overhead. Benchmarks show negligible difference in throughput for typical business logic.                      |

---

### 🚨 Failure Modes & Diagnosis

**ClassCastException: Cannot cast proxy to concrete type**

**Symptom:**
`ClassCastException: com.sun.proxy.$Proxy42 cannot be cast to com.example.JpaUserRepository`

**Root Cause:**
Code is trying to cast the JDK proxy (`$Proxy42`, which implements `UserRepository`) to the concrete class `JpaUserRepository`. The proxy is not a `JpaUserRepository`.

**Fix:**

```java
// BAD: casting to concrete type
@Autowired UserRepository repo;
JpaUserRepository concrete = (JpaUserRepository) repo;  // ClassCastException!

// GOOD: use interface type everywhere
@Autowired UserRepository repo;
// Use repo directly via the interface

// OR: force CGLIB to make the proxy extend the concrete class
@EnableAspectJAutoProxy(proxyTargetClass = true)
@Autowired JpaUserRepository repo;  // CGLIB proxy → instanceof JpaUserRepository = true
```

---

**@Transactional not applied (injecting by concrete type)**

**Symptom:**
Transactions are not started. A database error that should rollback the transaction doesn't.

**Root Cause:**
`@Autowired JpaUserRepository repo` (concrete type). Spring can't inject the JDK proxy here (it's not a `JpaUserRepository`). Spring falls back to injecting the real object, bypassing all proxy advice.

**Fix:**

```java
// Inject by interface - gets the transaction-enabled proxy
@Autowired UserRepository repo;  // interface type
```

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**

- `CGLIB Proxy` - understand the contrast; together CGLIB and JDK Dynamic Proxy cover all Spring proxy scenarios
- `AOP` - JDK Dynamic Proxy is one of two mechanisms Spring AOP uses
- `Bean Lifecycle` - proxy wrapping happens in the BeanPostProcessor phase

**Builds On This (learn these next):**

- `AOP (Aspect-Oriented Programming)` - the concept that JDK proxy enables
- `@Transactional` - the most common consumer of JDK dynamic proxies in Spring
- `Spring Data JPA` - the most visible use of "pure JDK proxy" (no real impl class)

**Alternatives / Comparisons:**

- `CGLIB Proxy` - subclass-based; no interface required; used when interface not present or `proxyTargetClass=true`
- `AspectJ weaving` - compile/load-time; intercepts `this.method()` calls; not proxy-based

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ WHAT IT IS   │ Runtime-generated interface implementation │
│              │ that routes all calls through InvocationH. │
├──────────────┼───────────────────────────────────────────┤
│ PROBLEM IT   │ Boilerplate wrapper classes for each       │
│ SOLVES       │ interface × cross-cutting concern          │
├──────────────┼───────────────────────────────────────────┤
│ KEY INSIGHT  │ One InvocationHandler handles ALL methods; │
│              │ Spring Data uses this - no impl class needed│
├──────────────┼───────────────────────────────────────────┤
│ REQUIRES     │ Target must implement at least one non-    │
│              │ Spring interface. Inject by interface type. │
├──────────────┼───────---────────────────────────────────┤
│ SELF-        │ Bypasses proxy - same as CGLIB. AOP/       │
│ INVOCATION   │ @Transactional won't fire on this.method() │
├──────────────┼───────────────────────────────────────────┤
│ TRADE-OFF    │ Built-in (no CGLIB) vs interface-required; │
│              │ concrete-type injection fails              │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "A forged interface implementation that    │
│              │  runs your code before every method call." │
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ AOP → Aspect → Advice → Pointcut           │
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** Spring Data repositories are JDK dynamic proxies with no backing class. When you call `userRepository.findByEmail("alice@example.com")`, the InvocationHandler must: (1) parse the method name, (2) generate a JPQL query, (3) execute it, (4) map results. Does Spring do this on every call, or is the query cached? Trace what happens on the first call vs the hundredth call to the same repository method.

**Q2.** You have a `UserRepository` interface (JDK-proxied for @Transactional) and you want to write an `AspectJ` pointcut that intercepts calls to ALL repository methods. Should you define the pointcut against the interface type or the concrete implementation type? Does it matter which proxy type (JDK vs CGLIB) is used? How does Spring AOP's pointcut matching interact with proxy type in this scenario?
