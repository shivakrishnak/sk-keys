---
layout: default
title: "JDK Dynamic Proxy"
parent: "Spring Core"
nav_order: 385
permalink: /spring/jdk-dynamic-proxy/
number: "385"
category: Spring Core
difficulty: ★★★
depends_on: "Bean Lifecycle, AOP (Aspect-Oriented Programming), BeanPostProcessor, CGLIB Proxy"
used_by: "AOP (Aspect-Oriented Programming), @Transactional, Weaving"
tags: #advanced, #spring, #internals, #jvm, #deep-dive
---

# 385 — JDK Dynamic Proxy

`#advanced` `#spring` `#internals` `#jvm` `#deep-dive`

⚡ TL;DR — A **JDK Dynamic Proxy** creates a runtime proxy object that implements one or more Java interfaces, routing all method calls through an `InvocationHandler`. Spring uses it to apply AOP advice when the target bean implements at least one interface and `proxyTargetClass = false`.

| #385            | Category: Spring Core                                                             | Difficulty: ★★★ |
| :-------------- | :-------------------------------------------------------------------------------- | :-------------- |
| **Depends on:** | Bean Lifecycle, AOP (Aspect-Oriented Programming), BeanPostProcessor, CGLIB Proxy |                 |
| **Used by:**    | AOP (Aspect-Oriented Programming), @Transactional, Weaving                        |                 |

---

### 📘 Textbook Definition

**JDK Dynamic Proxy** is a Java standard library feature (`java.lang.reflect.Proxy`) that creates a proxy class at runtime which implements a specified set of interfaces. The proxy routes all method calls to a provided `InvocationHandler.invoke(Object proxy, Method method, Object[] args)`. Spring's `JdkDynamicAopProxy` implements `InvocationHandler` and routes calls through the AOP advice chain before delegating to the real target bean. JDK proxies are used by Spring when: (a) the target bean implements at least one non-Spring interface, and (b) `proxyTargetClass = false` (not the Spring Boot default). Since the proxy only implements interfaces, any code that holds a reference to the proxy must use the interface type — casting to the concrete class causes `ClassCastException`. Because JDK proxies implement interfaces rather than extending classes, they do not require the target class to be non-final and have no restriction on `final` class methods. However, only interface methods are interceptable — concrete class methods not declared in an interface are never called through the proxy.

---

### 🟢 Simple Definition (Easy)

JDK Dynamic Proxy creates a fake object that implements the same interface as your real bean. All calls through the interface go through an interceptor, which applies advice (e.g., transaction logic) before calling the real bean.

---

### 🔵 Simple Definition (Elaborated)

Java's standard library can create proxy objects at runtime that implement any set of interfaces you specify. Spring uses this to insert cross-cutting behaviour: when `OrderService` implements `OrderServiceInterface`, Spring creates a proxy that also implements `OrderServiceInterface`. Any call through that interface is intercepted by Spring's advice chain — for a `@Transactional` method, the interceptor opens a transaction, calls your real method, then commits or rolls back. The caller holds a reference to the proxy (same interface type), so nothing in the application code changes. The limitation is that the proxy only covers interface methods — methods not declared in the interface are invisible to the proxy and cannot have advice applied.

---

### 🔩 First Principles Explanation

**The Java standard library mechanism:**

```java
// java.lang.reflect.Proxy — the JDK mechanism
public static Object newProxyInstance(
    ClassLoader loader,     // class loader for the generated class
    Class<?>[] interfaces,  // interfaces the proxy must implement
    InvocationHandler h     // handler called for every method invocation
)

// InvocationHandler — your interception code
public interface InvocationHandler {
    Object invoke(Object proxy, Method method, Object[] args) throws Throwable;
}
```

**Minimal JDK proxy example — understanding the mechanism:**

```java
// Target interface
interface OrderService {
    Order placeOrder(OrderRequest req);
    Order findOrder(Long id);
}

// Real implementation
class OrderServiceImpl implements OrderService {
    public Order placeOrder(OrderRequest req) { /* DB save */ return order; }
    public Order findOrder(Long id)           { /* DB query */ return order; }
}

// InvocationHandler with timing logic
class TimingInvocationHandler implements InvocationHandler {
    private final Object target; // wrapped real object

    TimingInvocationHandler(Object target) { this.target = target; }

    @Override
    public Object invoke(Object proxy, Method method, Object[] args)
            throws Throwable {
        long start = System.nanoTime();
        try {
            return method.invoke(target, args); // call real method
        } finally {
            log.info("{} took {}ms", method.getName(),
                     (System.nanoTime() - start) / 1_000_000);
        }
    }
}

// Create proxy
OrderServiceImpl realService = new OrderServiceImpl();
OrderService proxy = (OrderService) Proxy.newProxyInstance(
    OrderService.class.getClassLoader(),
    new Class<?>[] { OrderService.class }, // must implement this interface
    new TimingInvocationHandler(realService)
);

// proxy.placeOrder(req) → TimingInvocationHandler.invoke() → realService.placeOrder(req)
```

**How Spring's JdkDynamicAopProxy works:**

```java
// Spring's JdkDynamicAopProxy (simplified concept)
class JdkDynamicAopProxy implements InvocationHandler {
    private final Object target;
    private final List<MethodInterceptor> advisors; // TransactionInterceptor, etc.

    @Override
    public Object invoke(Object proxy, Method method, Object[] args)
            throws Throwable {
        // Build an invocation chain through all applicable interceptors
        MethodInvocation invocation = new ReflectiveMethodInvocation(
            proxy, target, method, args, targetClass, chain);
        return invocation.proceed(); // run chain → eventually calls target.method()
    }
}

// For @Transactional on OrderService.placeOrder():
// invocation.proceed():
//   → TransactionInterceptor.invoke() [begins transaction]
//     → target.placeOrder(args)        [real method]
//   → TransactionInterceptor.invoke() [commits/rolls back]
```

**JDK proxy vs CGLIB — decision table:**

```
Condition                          | Proxy Type Used
─────────────────────────────────────────────────────
proxyTargetClass = true            | Always CGLIB
  (Spring Boot 2.x+ default)       |
                                   |
proxyTargetClass = false           |
  + Bean has interface             | JDK Dynamic Proxy
  + Bean has NO interface          | CGLIB
                                   |
Bean is @Configuration class       | Always CGLIB
  (regardless of interfaces)       |
```

---

### ❓ Why Does This Exist (Why Before What)

WITHOUT JDK Dynamic Proxy:

What breaks without it:

1. Interface-based beans require subclassing for AOP — CGLIB only, violating the principle that proxying via contract (interface) is cleaner than proxying via inheritance.
2. No standard Java way to create transparent, interface-compatible wrappers — every cross-cutting concern requires code generation tools.
3. Mocking in tests would require real subclasses or bytecode manipulation for every interface.

WITH JDK Dynamic Proxy:
→ Any interface can be transparently proxied with zero code generation frameworks.
→ Spring's AOP works cleanly for interface-typed beans — the application only sees the interface.
→ Test mocking frameworks (Mockito) use JDK proxies for interface mocks — same mechanism.
→ Remoting frameworks (RMI, Java web services) use JDK proxies to intercept interface calls for serialisation.

---

### 🧠 Mental Model / Analogy

> Think of JDK Dynamic Proxy as a receptionist at a company. Callers interact only with the receptionist (the proxy), who follows the same script (interface) as the real employee they are trying to reach. When a call comes in for "process this order" (a method call), the receptionist applies the company's standard procedure (AOP advice — start a transaction, log the call), then transfers the call to the real employee (target bean). The caller never speaks directly to the employee — only through the receptionist. But the receptionist can only handle calls listed in the company directory (declared interface methods); direct extensions (non-interface methods) bypass the receptionist entirely.

"Receptionist following company script" = JDK proxy implementing the interface
"Company directory of calls" = Java interface method signatures
"Standard procedure applied before transfer" = AOP advice chain (InvocationHandler)
"The real employee" = the target bean (`OrderServiceImpl`)
"Direct extensions bypassing receptionist" = concrete class methods not in the interface

---

### ⚙️ How It Works (Mechanism)

**JDK proxy class generation at the JVM level:**

```
Proxy.newProxyInstance(loader, interfaces, handler):
  1. Look up in cache: is a proxy class for these interfaces already generated?
     YES → use cached proxy class
     NO  → generate new proxy class:
       a. Create bytecode for class $Proxy0 (or $Proxy1, etc.)
       b. $Proxy0 implements ALL specified interfaces
       c. Each interface method → delegates to InvocationHandler.invoke()
       d. Load class via ClassLoader
  2. Instantiate the generated class, inject the InvocationHandler
  3. Return the proxy instance

The generated class looks like (approximate):
  final class $Proxy0 extends java.lang.reflect.Proxy implements OrderService {
      public Order placeOrder(OrderRequest req) {
          return (Order) h.invoke(this, placeOrderMethod, new Object[]{req});
      }
      public Order findOrder(Long id) {
          return (Order) h.invoke(this, findOrderMethod, new Object[]{id});
      }
  }
  // h = the InvocationHandler passed to newProxyInstance
```

**Why Spring Boot defaults to CGLIB (proxyTargetClass = true):**

```java
// The ClassCastException problem with JDK proxy (motivates CGLIB default):

@Service
class OrderServiceImpl implements OrderService { ... }

// With JDK proxy (proxyTargetClass = false):
// ApplicationContext holds: "orderService" → $Proxy0 (implements OrderService)

// Injecting by interface → WORKS
@Autowired OrderService service; // injects $Proxy0 — fine

// Injecting by concrete class → ClassCastException
@Autowired OrderServiceImpl service; // $Proxy0 is NOT an OrderServiceImpl!
// Throws: java.lang.ClassCastException

// Spring Boot switched to CGLIB by default to avoid this surprise
// CGLIB produces a subclass → instanceof OrderServiceImpl passes
```

---

### 🔄 How It Connects (Mini-Map)

```
BeanPostProcessor (AnnotationAwareAspectJAutoProxyCreator, phase 6)
        │
        ▼
Proxy Type Decision:
        │
        ├── has interface + proxyTargetClass=false
        │         │
        │         ▼
        │   JDK Dynamic Proxy  ◄──── (you are here)
        │   (Proxy.newProxyInstance, implements interfaces)
        │         │
        └── else  │
                  ▼
            CGLIB Proxy
            (generates subclass)
        │
        ▼
AOP Advice Chain (InvocationHandler / MethodInterceptor)
  TransactionInterceptor → target.method()
        │
        ▼
Result stored in ApplicationContext
(proxy, not original bean)
```

---

### 💻 Code Example

**Demonstrating JDK proxy vs CGLIB proxy in Spring:**

```java
// Interface-based bean — with proxyTargetClass = false, JDK proxy is used
public interface PaymentService {
    PaymentResult process(Payment payment);
}

@Service
@Transactional
public class StripePaymentService implements PaymentService {
    @Override
    public PaymentResult process(Payment payment) {
        // ... Stripe API call
        return result;
    }
}

// In application:
// proxyTargetClass = false (explicit):
@EnableAspectJAutoProxy(proxyTargetClass = false)
@Configuration class AopConfig {}

// ctx.getBean(PaymentService.class):
//   Returns: $Proxy0 implements PaymentService (JDK proxy)
//   AopUtils.isJdkDynamicProxy(bean) → true

// ctx.getBean(StripePaymentService.class):
//   ALSO returns the proxy (Spring finds by assignability)
//   But casting to StripePaymentService: ClassCastException

// Verifying proxy type at runtime:
@Component class ProxyChecker implements CommandLineRunner {
    @Autowired PaymentService paymentService;

    @Override
    public void run(String... args) {
        boolean isJdk  = AopUtils.isJdkDynamicProxy(paymentService); // true
        boolean isCglib = AopUtils.isCglibProxy(paymentService);      // false
        System.out.printf("JDK proxy: %s, CGLIB proxy: %s%n", isJdk, isCglib);
        // JDK proxy: true, CGLIB proxy: false
    }
}
```

**Writing a custom InvocationHandler for audit logging:**

```java
public class AuditLoggingProxy implements InvocationHandler {
    private final Object target;
    private final String userId;

    public AuditLoggingProxy(Object target, String userId) {
        this.target = target;
        this.userId = userId;
    }

    @Override
    public Object invoke(Object proxy, Method method, Object[] args)
            throws Throwable {
        String action = method.getDeclaringClass().getSimpleName()
                      + "." + method.getName();
        AuditLog.record(userId, action, args); // log before

        try {
            Object result = method.invoke(target, args);
            AuditLog.recordSuccess(userId, action);
            return result;
        } catch (InvocationTargetException e) {
            AuditLog.recordFailure(userId, action, e.getCause());
            throw e.getCause(); // unwrap reflection exception
        }
    }

    @SuppressWarnings("unchecked")
    public static <T> T wrap(T target, Class<T> iface, String userId) {
        return (T) Proxy.newProxyInstance(
            iface.getClassLoader(),
            new Class<?>[]{ iface },
            new AuditLoggingProxy(target, userId)
        );
    }
}

// Usage:
OrderService auditedService = AuditLoggingProxy.wrap(
    realOrderService, OrderService.class, currentUserId);
```

---

### ⚠️ Common Misconceptions

| Misconception                                                  | Reality                                                                                                                                                                                                                    |
| -------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| JDK Dynamic Proxy is faster than CGLIB                         | Benchmarks show JDK proxy and CGLIB perform comparably for typical method calls. Any difference is negligible in application code. CGLIB's startup cost (class generation) is slightly higher; runtime dispatch is similar |
| JDK proxy can intercept all methods on the target class        | JDK proxy only intercepts methods declared in the specified interfaces. Methods on the implementation class that are NOT in the interface are never routed through the proxy and cannot have advice applied                |
| Spring always chooses JDK proxy when the bean has an interface | Spring Boot 2.x+ sets `proxyTargetClass = true` by default, overriding JDK proxy selection. CGLIB is used even for interface-based beans unless `proxyTargetClass = false` is explicitly set                               |
| A JDK proxy object is an instance of the implementation class  | A JDK proxy is an instance of the interface(s) only. `proxy instanceof OrderServiceImpl` is `false`. `proxy instanceof OrderService` is `true`. Casting to the implementation class causes `ClassCastException`            |

---

### 🔥 Pitfalls in Production

**Calling a non-interface method through the proxy — AOP advice not applied:**

```java
public interface OrderService {
    Order placeOrder(OrderRequest req); // interface method — proxied
}

@Service
@Transactional
class OrderServiceImpl implements OrderService {
    public Order placeOrder(OrderRequest req) { ... } // proxied

    // This method is NOT in the interface — it is NOT proxied
    @Transactional // IGNORED for JDK proxy
    public void bulkImport(List<OrderRequest> requests) { ... }
}

// With JDK proxy: calling bulkImport() via a direct reference bypasses the proxy
// There is no proxy method for bulkImport() — @Transactional does nothing
// Fix: add bulkImport() to the OrderService interface, or use CGLIB
```

---

### 🔗 Related Keywords

- `CGLIB Proxy` — the alternative proxy mechanism; subclass-based, works for non-interface classes
- `AOP (Aspect-Oriented Programming)` — the paradigm that requires proxy generation; JDK proxy is one implementation
- `BeanPostProcessor` — `AnnotationAwareAspectJAutoProxyCreator` decides JDK vs CGLIB proxy in Phase 6
- `@Transactional` — the most common annotation driving proxy creation; works via both JDK and CGLIB proxy
- `Weaving` — the act of applying advice; JDK proxy implements runtime weaving for interface-typed beans

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ MECHANISM    │ Proxy.newProxyInstance() — interface-based│
│              │ InvocationHandler intercepts all calls    │
├──────────────┼───────────────────────────────────────────┤
│ USED WHEN    │ Bean has interface +                      │
│              │ proxyTargetClass=false (non-Boot default) │
├──────────────┼───────────────────────────────────────────┤
│ LIMITATION   │ Only interface methods are intercepted    │
│              │ Casting to concrete class → ClassCastEx   │
├──────────────┼───────────────────────────────────────────┤
│ SPRING BOOT  │ proxyTargetClass=true by default →        │
│              │ CGLIB used even when interface exists     │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "JDK proxy = receptionist who only takes  │
│              │  calls listed in the company directory."  │
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** A JDK Dynamic Proxy's `InvocationHandler.invoke()` is called for every interface method, including `equals()`, `hashCode()`, and `toString()`. Describe how Spring's `JdkDynamicAopProxy` handles these special methods: are `equals()` and `hashCode()` delegated to the target object or compared on the proxy identity? If two `@Autowired` references to the same Spring bean are compared with `==`, do they compare equal? What about `equals()`? Explain the surprising behaviour that can occur when a proxy-based bean is stored in a `HashSet` or as a `Map` key.

**Q2.** JDK Dynamic Proxy requires that all interfaces be loaded by the same `ClassLoader` (or a parent/child ClassLoader). In a modular application (OSGi, application server with multiple classloaders), this restriction causes proxy creation to fail with `IllegalArgumentException: interface X is not visible from class loader`. Describe the classloader isolation problem, explain how Spring works around it with `ProxyCreatorSupport.evaluateProxyInterfaces()`, and identify the alternative approach (CGLIB) that avoids classloader interface visibility issues because subclassing only requires the parent classloader to be accessible.
