---
id: DPT-018
title: Proxy
category: Design Patterns
tier: tier-5-distributed-architecture
folder: DPT-design-patterns
difficulty: ★★☆
depends_on: DPT-001, DPT-005, DPT-012
used_by: DPT-041, DPT-064
related: DPT-012, DPT-015, DPT-016, DPT-038
tags:
  - pattern
  - structural
  - intermediate
  - architecture
  - spring
status: complete
version: 4
layout: default
parent: "Design Patterns"
grand_parent: "Technical Mastery"
nav_order: 18
permalink: /technical-mastery/design-patterns/proxy/
---

⚡ TL;DR - Proxy wraps a real subject with the SAME
interface, intercepting access to add cross-cutting
behavior (security, caching, lazy loading, remote access)
without changing the subject or its clients.

| #18 | Category: Design Patterns | Difficulty: ★★☆ |
|:---|:---|:---|
| **Depends on:** | DPT-001, DPT-005, DPT-012 | |
| **Used by:** | DPT-041, DPT-064 | |
| **Related:** | DPT-012, DPT-015, DPT-016, DPT-038 | |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
You need to add transaction management to every service
method in a Spring application: begin transaction,
call method, commit on success, rollback on exception.
Option 1: add try/catch transaction code in every service
method (hundreds of methods). Option 2: wrap every service
call in the controller with transaction boilerplate.
Both options produce duplication across hundreds of call
sites, and every future method must also add the same
boilerplate.

**THE BREAKING POINT:**
A new service method is added without the transaction
boilerplate. Data corruption occurs. The issue: the
behavior is not tied to the object - it is tied to manual
convention. The compiler cannot enforce it.

**THE INVENTION MOMENT:**
Proxy: instead of calling `service.doWork()` directly,
call it through a proxy object that wraps the service.
The proxy intercepts the call, begins the transaction,
delegates to the real service, commits/rolls back.
Neither the service implementation nor the calling code
knows the proxy exists - both see the same interface.

**EVOLUTION:**
Spring's `@Transactional` annotation generates a proxy
at application startup. The proxy wraps every `@Transactional`
bean. When you call a Spring service, you call the proxy,
not the service directly. `@Cacheable`, `@Async`,
`@Retryable` all work through proxies. Hibernate lazy
loading generates subclass proxies for entity relations.
Java RMI, EJB remote calls, gRPC client stubs - all
are Remote Proxies. The pattern is pervasive in Java
enterprise.

---

### 📘 Textbook Definition

The **Proxy** pattern is a Structural design pattern that
provides a surrogate or placeholder for another object to
control access to it. A Proxy and its subject implement
the same interface; the proxy holds a reference to the
subject; all operations on the proxy are forwarded to
the subject after the proxy adds its own behavior. Four
common proxy types: Virtual Proxy (creates expensive
subject on first use), Protection Proxy (adds authorization
checks), Remote Proxy (handles network communication to
a remote subject), Cache Proxy (returns cached results
for repeated calls).

---

### ⏱️ Understand It in 30 Seconds

**One line:**
Proxy is a "middleman with the same ID" - it looks like
the real thing but adds checks, logging, or delay before
passing through.

**One analogy:**
> A bank teller as Proxy for the vault. Customers interact
> with the teller (same interface: deposit, withdraw, check
> balance). The teller verifies identity (protection proxy),
> logs transactions (audit proxy), and either accesses the
> vault or uses available cash (the real subject). Customers
> never interact with the vault directly.

**One insight:**
The key distinguishing feature of Proxy vs all other
structural patterns: the Proxy has THE SAME INTERFACE
as the real subject. Clients cannot tell they are talking
to a proxy. This transparency is what makes it possible
to inject cross-cutting behavior without changing any
calling code.

---

### 🔩 First Principles Explanation

**CORE INVARIANTS:**
1. Proxy and Subject share the same interface (or supertype).
2. Proxy holds a reference to the subject; it DELEGATES
   operations to the subject (does not reimplement them).
3. Clients are unaware of the proxy; they use the Subject
   interface.

**DERIVED DESIGN:**
Three participants:
- **Subject interface**: the common interface for Proxy
  and RealSubject
- **RealSubject**: the actual implementation; contains
  the core behavior
- **Proxy**: implements Subject; holds a reference to
  RealSubject; intercepts calls and adds behavior before/
  after delegating to RealSubject

**FOUR PROXY TYPES:**
- **Virtual Proxy**: delays creation of expensive subject
  until first use (lazy initialization)
- **Protection Proxy**: adds authorization checks
- **Remote Proxy**: handles communication to a remote object
  (serialization, network, deserialization)
- **Cache Proxy**: returns cached results; calls subject
  only on cache miss

**TRADE-OFFS:**

**Gain:** Cross-cutting concerns (transactions, security,
caching, remote access) are isolated in the proxy and
applied transparently. Subject code stays clean.

**Cost:** Indirection adds slight latency. Dynamic proxies
(e.g., JDK reflection proxy) have performance overhead vs
direct calls. Stack traces become harder to read (proxy
method names appear in the stack). Proxy wraps one object:
each cross-cutting concern may require a separate proxy
layer.

---

### 🧪 Thought Experiment

**SETUP:**
An API for loading user profile images. Images are large
(500KB each), stored in S3, and expensive to load.
Most users request the same popular profiles. Without
a proxy: every call loads from S3.

**VIRTUAL PROXY:**
`LazyImageProxy` implements `Image`. It holds the S3 key
but does not load the image. On first `getPixelData()`
call, the proxy loads from S3 and caches the result.
Subsequent calls return the cache. Clients call
`image.getPixelData()` - indistinguishable from a real
image object, but loading happens only when needed.

**CACHE PROXY:**
`CachedImageProxy` wraps the S3 loader. On `getPixelData(key)`:
check an in-memory cache (Map<key, Image>). If present:
return cached result without hitting S3. If absent: load
from S3, cache, return. 10x the same popular image: 1 S3
call, 9 cache hits.

**THE INSIGHT:**
Both use-cases add behavior (lazy loading, caching) to
the same Subject interface without modifying the S3 loader
or the clients. They are transparent to callers.

---

### 🧠 Mental Model / Analogy

> Proxy is a BODYGUARD who looks exactly like the VIP.
> Visitors interact with the bodyguard (same appearance,
> same "how can I help you?"). The bodyguard checks if
> the visitor is authorized (Protection Proxy), logs the
> visit (Audit Proxy), and then passes through to the VIP
> (delegates). The VIP does the real work; the bodyguard
> handles the surrounding concerns.

- "Bodyguard" = Proxy
- "VIP" = RealSubject
- "Looks exactly the same" = same interface
- "Authorization check, logging" = proxy-added behavior
- "Passes through" = delegation to RealSubject

**Where this analogy breaks down:**
A bodyguard can refuse entry entirely (protection proxy
denying access). A Virtual Proxy may also substitute for
a not-yet-created subject, which has no analogy in the
bodyguard metaphor.

---

### 📶 Gradual Depth - Five Levels

**Level 1 - What it is (anyone can understand):**
Proxy is a stand-in that looks exactly like the real thing
but adds extra behavior before or after passing through
to it. Like calling customer service - you talk to a rep
(proxy) who checks your account, notes the call, and
connects you to the right department (subject).

**Level 2 - How to use it (junior developer):**
Create an interface. Implement it in the real class.
Create a Proxy class that also implements the interface.
In the Proxy, hold a reference to the real object.
In each method: add your pre/post behavior, then call
the same method on the real object.

**Level 3 - How it works (mid-level engineer):**
Spring's `@Transactional` works exactly this way. At
application startup, Spring's `DefaultAdvisorAutoProxyCreator`
wraps every bean with `@Transactional` methods in a
`CglibAopProxy` (or `JdkDynamicProxy` if the bean
implements an interface). The proxy intercepts every method
call: opens a transaction, calls the real method, commits
on success / rolls back on exception. The `@Service` bean
you inject is actually the proxy, not the actual service.
This is why calling a `@Transactional` method from another
method IN THE SAME CLASS does not start a new transaction:
the call bypasses the proxy.

**Level 4 - Why it was designed this way (senior/staff):**
Proxy enables Aspect-Oriented Programming (AOP) without
language-level support. The "aspect" (transaction, logging,
security) is implemented in the Proxy. The proxy intercepts
calls at defined "join points" (method calls). Spring AOP
uses Proxy as its underlying mechanism. The alternatives
without Proxy: bytecode weaving (AspectJ - more powerful
but requires a special compiler/agent) or manual wrapping
(error-prone, violates DRY). Proxy is the middle ground:
no instrumentation required, Java-standard mechanism.

**Level 5 - Mastery (distinguished engineer):**
JDK Dynamic Proxy (`java.lang.reflect.Proxy`) creates
proxy classes at runtime using reflection: `Proxy
.newProxyInstance(classLoader, interfaces, handler)`.
The generated class implements all specified interfaces;
every method call on the proxy invokes
`InvocationHandler.invoke(proxy, method, args)`. This is
why Spring's JDK proxy only works for interface-based beans:
the proxy implements the interface. CGLIB proxy subclasses
the bean class at runtime (bytecode generation) and
overrides each method. CGLIB works for concrete classes
but cannot proxy final classes or final methods. This is
why `@Transactional` on a final method in Spring silently
has no effect: CGLIB cannot override a final method.

---

### ⚙️ How It Works (Mechanism)

```
Proxy Structure
┌─────────────────────────────────────────────────────────┐
│  Subject (interface)                                    │
│  + operation(): Result                                  │
│                                                         │
│  RealSubject implements Subject                         │
│  + operation(): Result      ← actual logic here         │
│                                                         │
│  Proxy implements Subject   ← same interface            │
│  - realSubject: RealSubject ← holds reference           │
│  + operation(): Result                                  │
│      // Pre-behavior (check auth, start tx, log)        │
│      result = realSubject.operation() ← DELEGATE        │
│      // Post-behavior (commit tx, cache, log result)    │
│      return result                                      │
│                                                         │
│  Client                                                 │
│      Subject s = new Proxy(new RealSubject())           │
│      s.operation() ← calls Proxy, not RealSubject       │
│      // Client sees Subject interface; unaware of Proxy │
└─────────────────────────────────────────────────────────┘
```

---

### 🔄 The Complete Picture - End-to-End Flow

**SPRING @TRANSACTIONAL PROXY FLOW:**
```
Client calls: orderService.placeOrder(order)
  → Actually calls: OrderServiceProxy.placeOrder(order)
  → Proxy: TransactionManager.begin()
  → Proxy: realOrderService.placeOrder(order)  ← delegate
      → real method executes
  → On success: TransactionManager.commit()
  → On RuntimeException: TransactionManager.rollback()
  ← Returns result to client
Client never knows a proxy was involved
```

**FAILURE CASE - same-class invocation:**
```
OrderServiceProxy.placeOrder()
  → realOrderService.placeOrder()
      → this.reserveInventory()  ← bypasses proxy!
        // @Transactional on reserveInventory: IGNORED
        // Call went through 'this', not through proxy
```

---

### 💻 Code Example

**Example 1 - Manual proxy for transaction management:**

```java
// BAD: transaction boilerplate in every method
class OrderServiceImpl {
    void placeOrder(Order order) {
        txManager.begin();              // boilerplate
        try {
            // actual logic
            inventoryRepo.reserve(order);
            paymentService.charge(order);
            txManager.commit();         // boilerplate
        } catch (Exception e) {
            txManager.rollback();       // boilerplate
            throw e;
        }
    }
    // Every method needs the same 6 lines
}
```

**Example 2 - Proxy centralizes cross-cutting concerns:**

```java
// GOOD: Proxy handles transactions; service stays clean

interface OrderService {
    void placeOrder(Order order);
    OrderStatus getStatus(String orderId);
}

// Real subject: pure business logic, no boilerplate
class OrderServiceImpl implements OrderService {
    @Override
    public void placeOrder(Order order) {
        inventoryRepo.reserve(order);
        paymentService.charge(order);
        // No transaction code - Proxy handles it
    }

    @Override
    public OrderStatus getStatus(String orderId) {
        return orderRepo.findById(orderId).getStatus();
    }
}

// Proxy: same interface, adds transaction management
class TransactionalOrderServiceProxy implements OrderService {
    private final OrderService delegate;
    private final TransactionManager txManager;

    TransactionalOrderServiceProxy(
        OrderService delegate, TransactionManager txManager) {
        this.delegate = delegate;
        this.txManager = txManager;
    }

    @Override
    public void placeOrder(Order order) {
        txManager.begin();
        try {
            delegate.placeOrder(order); // delegate to real
            txManager.commit();
        } catch (RuntimeException e) {
            txManager.rollback();
            throw e;
        }
    }

    @Override
    public OrderStatus getStatus(String orderId) {
        // Read-only: no transaction needed
        return delegate.getStatus(orderId);
    }
}

// Client: uses OrderService interface - unaware of proxy
OrderService orderService =
    new TransactionalOrderServiceProxy(
        new OrderServiceImpl(), txManager);
orderService.placeOrder(order); // calls proxy transparently
```

**Example 3 - JDK Dynamic Proxy (how Spring AOP works):**

```java
// Dynamic proxy created at runtime - no proxy class to write

interface PaymentService {
    void processPayment(Payment p);
}

class PaymentServiceImpl implements PaymentService {
    @Override
    public void processPayment(Payment p) {
        // actual processing
    }
}

// InvocationHandler: the "proxy behavior" for all methods
class LoggingInvocationHandler implements InvocationHandler {
    private final Object target;

    LoggingInvocationHandler(Object target) {
        this.target = target;
    }

    @Override
    public Object invoke(
        Object proxy, Method method, Object[] args)
        throws Throwable {
        System.out.println("Calling: " + method.getName());
        long start = System.currentTimeMillis();
        Object result = method.invoke(target, args); // delegate
        long elapsed = System.currentTimeMillis() - start;
        System.out.println(method.getName()
            + " took " + elapsed + "ms");
        return result;
    }
}

// Create proxy at runtime - no proxy class needed
PaymentService proxy = (PaymentService) Proxy.newProxyInstance(
    PaymentService.class.getClassLoader(),
    new Class[]{PaymentService.class},
    new LoggingInvocationHandler(new PaymentServiceImpl())
);
proxy.processPayment(payment); // calls InvocationHandler
// Spring @Transactional and @Cacheable work exactly this way
```

**Example 4 - The @Transactional same-class trap:**

```java
// FAILURE: self-invocation bypasses Spring proxy
@Service
class OrderService {
    @Transactional
    public void placeOrder(Order order) {
        // Calls this.reserveInventory - bypasses proxy!
        reserveInventory(order);
        processPayment(order);
    }

    @Transactional(propagation = REQUIRES_NEW)
    public void reserveInventory(Order order) {
        // TRAP: @Transactional here is IGNORED when called
        // from placeOrder() - the proxy is bypassed
        // 'this' is the real bean, not the proxy
        inventoryRepo.save(order.items());
    }
}

// FIX: inject the service into itself (gets the proxy)
// or split into two separate Spring beans
@Service
class OrderService {
    @Autowired
    private InventoryService inventoryService; // separate bean

    @Transactional
    public void placeOrder(Order order) {
        inventoryService.reserveInventory(order);
        // goes through proxy
        processPayment(order);
    }
}
```

**How to test/verify correctness:**
Test the proxy behavior in isolation by mocking the subject.
Verify pre/post behavior is called. Verify delegation
occurs. For Spring proxies: test that `@Transactional`
methods throw in one class, then verify via ROLLBACK that
the transaction was rolled back.

---

### ⚖️ Comparison Table

| Aspect | Proxy | Decorator | Adapter | Facade |
| --- | --- | --- | --- | --- |
| Interface | SAME as Subject | SAME as Component | DIFFERENT | SIMPLER |
| Wraps | 1 object | 1 object | 1 object | System |
| Purpose | Control access | Add behavior | Convert interface | Simplify |
| Subject knows? | No | No | No (Adaptee does) | No |
| Stackable | Not typically | Yes (chain) | No | N/A |

**How to choose:**
- Same interface + controlling access/adding cross-cutting
  concerns: Proxy
- Same interface + adding behavior to a component you can
  extend at runtime: Decorator
- Different interface needed: Adapter
- Simplify a subsystem: Facade

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| Proxy and Decorator are the same | Decorator and Proxy have the same structure but DIFFERENT INTENT: Decorator adds behavior by wrapping; Proxy controls ACCESS to the subject. Spring's `@Transactional` proxy intercepts to control transactionality; `@Async` proxy intercepts to offload execution. Decorator adds behavior the component itself should offer |
| @Transactional always works on any method call | @Transactional only works when called THROUGH THE PROXY. Self-invocation (calling from within the same class using `this`) bypasses the proxy and ignores @Transactional - a very common Spring bug |
| Virtual Proxy and Object Pool solve the same problem | Virtual Proxy: delays creation of ONE expensive object (lazy init). Object Pool: pre-creates MANY objects for reuse. Virtual Proxy: created on first access, never "returned." Pool: temporary exclusive loan, returned on completion |
| Remote Proxy is just serialization | Remote Proxy hides all remote call complexity: serialization, network transport, error handling, retry, timeout. To the client, calling the proxy is no different from calling a local object |
| JDK Dynamic Proxy is the only option in Spring | Spring uses JDK Dynamic Proxy for interface-based beans, CGLIB for class-based beans. CGLIB generates a subclass at runtime. Final classes/methods cannot be proxied by CGLIB - this is a common configuration problem |

---

### 🚨 Failure Modes & Diagnosis

**The Same-Class @Transactional Bypass (Most Common Spring Bug)**

**Symptom:**
A method `A()` calls `B()` in the same service. `B()` is
annotated `@Transactional(propagation = REQUIRES_NEW)`.
The test passes, but in production, `B()` runs in the
SAME transaction as `A()` - not a new one. When `A()` fails
after `B()`, `B()`'s changes are rolled back, causing
data loss.

**Root Cause:**
`A()` calls `this.B()`. `this` is the actual bean, not
the Spring proxy. The `@Transactional` on `B()` is only
enforced when called THROUGH the proxy. Self-invocation
bypasses the proxy.

**Diagnostic Signal:**
`@Transactional` behavior is silently ignored. Transactions
are not started/committed as expected. Isolate by calling
`B()` from a DIFFERENT Spring bean - if it works correctly,
self-invocation bypass is confirmed.

```java
// Diagnose in test: verify method IS transactional
// when called from a separate bean:
@Autowired AnotherService anotherService;
anotherService.callB(); // if @Transactional works here
                        // but not from same class: bypass confirmed
```

**Fix:**
Option 1: Move `B()` to a separate Spring bean.
Option 2: Inject the service bean into itself via
`@Autowired private OrderService self;` and call `self.B()`.
Option 3: Use AspectJ weaving instead of Spring proxy AOP
(requires more configuration but supports self-invocation).

---

**CGLIB Proxy Fails on Final Class or Method**

**Symptom:**
`@Transactional` on a service method has no effect.
No exception is thrown. Transactions are not committed.
The service class has `final` on the class declaration
or on the annotated method.

**Root Cause:**
Spring uses CGLIB to proxy concrete classes. CGLIB works
by creating a subclass. `final` prevents subclassing
(final class) or method override (final method). CGLIB
cannot create the proxy; Spring may silently skip it
or create a non-functional proxy.

**Diagnostic Signal:**
Add `logging.level.org.springframework.aop=DEBUG`.
Look for: "Unable to proxy..." or "Method is final, skipping
transaction advice." Or: add breakpoint in the method and
observe that the call stack has no `CglibAopProxy` frame
(proxy is not wrapping the call).

**Fix:**
Remove `final` from the class/method. Or: extract an
interface and use the JDK Dynamic Proxy path.

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**
- `Adapter` - understand single-object wrapping before
  studying Proxy; helps clarify the Proxy vs Adapter
  interface distinction

**Builds On This (learn these next):**
- `Decorator vs Proxy vs Adapter` - the critical three-way
  comparison for structural patterns
- `Dependency Injection Pattern` - DI is what injects
  proxies transparently in frameworks like Spring

**Alternatives / Comparisons:**
- `Decorator` - same structure, different intent; Decorator
  adds to behavior; Proxy controls access
- `Adapter` - Adapter changes the interface; Proxy keeps
  the same interface

---

### 📌 Quick Reference Card

```
┌─────────────────────────────────────────────────────────┐
│ WHAT IT IS   │ Surrogate with SAME interface as subject;│
│              │ intercepts calls to add cross-cutting    │
│              │ behavior before/after delegation         │
├──────────────┼──────────────────────────────────────────┤
│ KEY PROPERTY │ Client cannot tell if it has a proxy     │
│              │ or the real subject (same interface)     │
├──────────────┼──────────────────────────────────────────┤
│ 4 TYPES      │ Virtual (lazy), Protection (authz),      │
│              │ Remote (network), Cache (memoize)        │
├──────────────┼──────────────────────────────────────────┤
│ SPRING PROXY │ @Transactional, @Cacheable, @Async,      │
│              │ @Retryable all work via proxy            │
├──────────────┼──────────────────────────────────────────┤
│ CRITICAL TRAP│ @Transactional ignored on self-invocation│
│              │ (this.method() bypasses the proxy)       │
├──────────────┼──────────────────────────────────────────┤
│ CGLIB TRAP   │ final class/method cannot be proxied     │
│              │ by CGLIB - @Transactional silently ignore│
├──────────────┼──────────────────────────────────────────┤
│ VS DECORATOR │ Same structure, different intent:        │
│              │ Proxy = access control; Decorator = add  │
│              │ behavior                                 │
├──────────────┼──────────────────────────────────────────┤
│ NEXT EXPLORE │ Chain of Responsibility → Command        │
└─────────────────────────────────────────────────────────┘
```

**If you remember only 3 things:**
1. Proxy has the SAME interface as the real subject -
   clients cannot tell they are talking to a proxy (this
   is what makes cross-cutting concerns transparent)
2. Spring's `@Transactional`, `@Cacheable`, and `@Async`
   all work via Proxy - the bean you inject IS the proxy
3. Self-invocation (`this.method()`) bypasses the Spring
   proxy - `@Transactional` is silently ignored on methods
   called within the same class

**Interview one-liner:**
"Proxy provides a surrogate with the same interface as the
real subject to control access or add cross-cutting behavior.
Spring's @Transactional, @Cacheable, and @Async all use
proxies generated at startup. The classic trap: calling a
@Transactional method from within the same class uses 'this'
which bypasses the proxy, silently ignoring the annotation."

---

### 💎 Transferable Wisdom

**Reusable Engineering Principle:**
Cross-cutting concerns (security, transactions, logging,
caching, retry) should be ISOLATED in the proxy layer,
not scattered across domain objects. Domain objects should
contain only domain logic. Proxy is the structural
pattern that makes this separation possible without
changing callers or subjects.

**Where else this pattern appears:**
- **Hibernate lazy loading** - `@OneToMany` relations
  return a proxy (HibernateProxyList) until the collection
  is accessed; accessing the collection triggers the SQL
  query; the calling code sees `List<Order>` interface
- **Java RMI stubs** - the client-side stub IS a Remote
  Proxy: it implements the same interface as the server-side
  object; method calls are serialized, sent over network,
  deserialized, and executed on the server; results are
  returned the same way
- **Service mesh sidecars (Envoy proxy)** - in Kubernetes
  with Istio, every pod has a sidecar proxy (Envoy) that
  intercepts all network traffic; the application code
  talks to localhost (the proxy); the proxy handles
  TLS, retries, circuit breaking, and observability -
  exactly the Proxy pattern at the infrastructure level

**Industry applications:**
- **CDN as Cache Proxy** - a CDN (Cloudflare, Akamai) is a
  Cache Proxy for origin servers: same request interface,
  cached response on hit, delegated to origin on miss
- **Spring Security filter chain** - each security filter
  is a Protection Proxy: checks authentication/authorization
  before delegating to the next filter or servlet
- **gRPC client stub** - generated stub is a Remote Proxy:
  implements the service interface; handles serialization
  (protobuf), HTTP/2 transport, and error handling

---

### 💡 The Surprising Truth

Every call to a Spring `@Service` bean in a Spring application
is actually a call to a proxy object - not the service
you wrote. This means your service class is NEVER directly
instantiated as a Spring bean when it has cross-cutting
annotations. Spring replaces your bean with a proxy at
startup. If you set a breakpoint in a `@Transactional`
service method and look at the call stack, you will see
`CglibAopProxy` or `JdkDynamicProxy` frames before your
method - those are the proxy interceptors running. Every
Spring developer uses Proxy every day without realizing
it. The pattern is so deeply embedded in the framework
that it is invisible - which is exactly what good Proxy
design achieves.

---

### ✅ Mastery Checklist

**You have mastered this when you can:**
1. [DISTINGUISH] Explain in one sentence why `@Transactional`
   on a method called via `this.method()` from within
   the same Spring bean has no effect - connecting to how
   Spring generates and uses proxies
2. [CLASSIFY] Given Spring's `@Cacheable`, `@Async`,
   `@Transactional`, and `@Validated`, name which of the
   four proxy types (Virtual, Protection, Cache, Remote)
   each represents
3. [BUILD] Write a manual proxy class for an `EmailService`
   interface that adds retry-on-failure (3 attempts with
   exponential backoff) without modifying `EmailServiceImpl`
   or the calling code
4. [DIAGNOSE] Given a Spring application where `@Transactional(
   propagation = REQUIRES_NEW)` on method `B()` is not
   creating a new transaction when called from method `A()`
   in the same service - identify the root cause and two
   valid fix approaches
5. [EXPLAIN] Explain why Spring cannot use CGLIB to proxy
   a `final` class, connecting to how CGLIB generates proxy
   classes at runtime

---

### 🧠 Think About This Before We Continue

**Q1.** Spring's `@Transactional` method can call a
non-transactional method in the same class without issues.
But a non-transactional method calling `@Transactional`
in the same class silently breaks. Why is it one-directional?
And if you MUST have a transactional method called from
within the same class, what are ALL the available fix
strategies?

*Hint: The proxy is only involved at the entry point of
the call from OUTSIDE the bean. Once inside the bean's
real object, all calls are on `this` - the real bean,
not the proxy. Calling @Transactional from a non-transactional
in the same class: the non-transactional method is also
inside the real bean, so its call goes to `this`, bypassing
the proxy. Fix strategies: (1) Move @Transactional method
to separate bean. (2) Self-inject the bean (`@Autowired
OrderService self`). (3) Use AspectJ weaving (load-time
or compile-time). (4) Programmatic transaction management
with TransactionTemplate inside the method.*

**Q2.** You implement a Caching Proxy over a `ProductService`.
The Cache Proxy returns cached Product objects. A bug
is reported: after a product price update (calling
`updatePrice(id, newPrice)` on the actual service), the
old price is still returned for 30 minutes. What design
flaw caused this and how would you fix it?

*Hint: The Cache Proxy caches the Product object, but
when `updatePrice` is called, the proxy does not invalidate
the cache entry. The cached stale Product is returned for
the cache TTL. Two fixes: (1) Cache-Aside with explicit
invalidation: proxy's `updatePrice` delegates to real service,
then removes the cached entry for that ID. (2) TTL reduction
(blunt fix, not ideal). (3) Use a write-through cache:
proxy writes to both real service and cache simultaneously.
The core lesson: a Cache Proxy must implement BOTH read
AND write paths to maintain cache coherence.*

---

### 🎯 Interview Deep-Dive

**Q1: How does Spring's @Transactional annotation work
internally? What happens when you annotate a service method?**

*Why they ask:* Classic question for Spring developers;
tests knowledge of the underlying proxy mechanism.

*Strong answer includes:*
- At application startup, Spring's AOP auto-proxy creator
  scans beans for @Transactional annotations
- For each annotated bean, Spring generates a proxy class:
  CGLIB for concrete classes (generates a subclass), JDK
  Dynamic Proxy for interface-based beans
- The proxy REPLACES the original bean in the ApplicationContext
- When you inject `@Autowired OrderService`, you get the
  PROXY, not the original service
- When a @Transactional method is called through the proxy:
  proxy calls TransactionInterceptor.invoke(); it starts
  a transaction (or joins existing), delegates to the real
  method, commits on success / rolls back on RuntimeException
- Self-invocation bypasses the proxy (call through `this`)
  because `this` references the real bean, not the proxy

**Q2: What is the difference between Proxy and Decorator?
They have the same structure.**

*Why they ask:* The most common structural pattern confusion.

*Strong answer includes:*
- Structure IS the same: both wrap an object, implement
  the same interface, delegate to the wrapped object
- INTENT differs:
  - Proxy: CONTROLS ACCESS to the subject; cross-cutting
    concerns (security, transactions, remote access);
    the subject does not ask for the proxy
  - Decorator: ENRICHES the component's behavior; adds
    optional features the component itself could have
    had; components are often combined (stacked decorators)
- Spring @Transactional: Proxy (the service does not "want"
  transactions; they are externally imposed)
- `BufferedInputStream`: Decorator (adds buffering capability
  to any InputStream - extending its I/O behavior)
- Test: "Does the wrapped object 'want' the added behavior?"
  If no (externally imposed): Proxy.
  If yes (optional capability extension): Decorator.

**Q3: Why can't Spring's @Transactional work when a method
calls another @Transactional method in the same class?**

*Why they ask:* A critical Spring gotcha that any senior
developer must know and explain.

*Strong answer includes:*
- Spring AOP uses Proxy-based implementation: @Transactional
  behavior is enforced by the PROXY that wraps the service
- When code OUTSIDE the bean calls a method: the call
  goes through the proxy - @Transactional is enforced
- When code INSIDE the bean calls another method: it uses
  `this.method()` - `this` is the REAL bean, not the proxy
- The proxy is not in the call path; @Transactional is
  SILENTLY IGNORED
- This is a fundamental limitation of proxy-based AOP vs
  aspect-oriented compile-time weaving (AspectJ)
- Fix: separate beans (each call from outside = through proxy),
  self-injection (@Autowired private OrderService self),
  or AspectJ weaving

