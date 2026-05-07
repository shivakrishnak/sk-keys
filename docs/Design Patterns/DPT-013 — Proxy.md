---
layout: default
title: "Proxy"
parent: "Design Patterns"
nav_order: 13
permalink: /design-patterns/proxy/
number: "DPT-013"
category: Design Patterns
difficulty: ★★☆
depends_on: Object-Oriented Programming (OOP), Interface, Polymorphism, Lazy Loading
used_by: Spring AOP, Hibernate Lazy Loading, Remote Proxies, Security Interceptors
related: Decorator, Adapter, Facade, Dynamic Proxy, AOP
tags:
  - pattern
  - intermediate
  - architecture
  - java
  - performance
---

# DPT-013 — Proxy

⚡ TL;DR — Proxy provides a surrogate or placeholder for another object, controlling access to it for security, caching, lazy loading, or remote communication.

| #778 | Category: Design Patterns | Difficulty: ★★☆ |
|:---|:---|:---|
| **Depends on:** | Object-Oriented Programming (OOP), Interface, Polymorphism, Lazy Loading | |
| **Used by:** | Spring AOP, Hibernate Lazy Loading, Remote Proxies, Security Interceptors | |
| **Related:** | Decorator, Adapter, Facade, Dynamic Proxy, AOP | |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
An application loads a high-resolution image (50 MB) from disk every time an `ImageViewer` is opened, even if the user never scrolls to see it. The application starts slowly, consumes excessive memory, and downloads images that will never be viewed. In a security context: a `DatabaseConnection` is handed directly to any service that requests it — there is no gate, no audit log, no permission check between the service and the database.

**THE BREAKING POINT:**
Two concrete problems: (1) Eager resource loading wastes bandwidth, memory, and startup time — especially painful on mobile or slow connections where 90% of loaded images may never be viewed. (2) Direct object access provides no interception point for cross-cutting concerns (security, logging, caching, metering) without modifying every class that uses the object.

**THE INVENTION MOMENT:**
This is exactly why the Proxy pattern was created. A `ImageProxy` implements the same `Image` interface as `RealImage`. When displayed, it loads the real image lazily on first access. All other operations (metadata query, resize preview) work on the lightweight proxy without triggering the 50 MB load. For security: a `SecurityProxy` implements the same service interface, checks permissions, logs access, then delegates to the real service.

---

### 📘 Textbook Definition

The **Proxy** pattern is a structural design pattern that provides a surrogate or placeholder object for another object. The proxy implements the same interface as the real subject and controls access to it. Callers interact with the proxy without knowing whether they are working with the real object or the proxy. Common proxy types: Virtual Proxy (deferred creation), Protection Proxy (access control), Remote Proxy (local representative of a remote object), Caching Proxy (return cached results), and Smart Reference Proxy (reference counting, locking).

---

### ⏱️ Understand It in 30 Seconds

**One line:**
A stand-in for the real object that controls when and how the real object is accessed.

**One analogy:**
> A receptionist at a VIP executive's office. The receptionist (proxy) has the same telephone number as the executive (real subject). Calls go through the receptionist first. They check: Is the caller authorised? Is this already an answered question (cached)? Is the executive available? Only then does the call reach the executive. Callers dialling the number don't know they're speaking to a receptionist or the executive.

**One insight:**
The Proxy's key power is transparency. The caller uses the same interface whether talking to the proxy or the real subject. The proxy is invisible to callers — it inserts its cross-cutting logic (lazy loading, caching, access control) without requiring any change to callers.

---

### 🔩 First Principles Explanation

**CORE INVARIANTS:**
1. Access to an object must be controlled (intercepted, deferred, guarded) without changing the caller's code.
2. The real subject may be expensive to create, remote, or sensitive — direct access is undesirable or dangerous.
3. The proxy must be a transparent substitute — callers see the same interface.

**DERIVED DESIGN:**
Given invariant 1+3: the proxy implements the same interface as the real subject. Callers hold references of the interface type — they cannot tell that they have a proxy. Given invariant 2: the proxy decides WHEN to delegate to the real subject (lazy: on first access; security: after permission check; caching: after cache miss).

The proxy holds either: a reference to the real subject (for protection proxies where the subject is pre-created) or creates the subject on first access (for virtual proxies). In Spring, `@Transactional`, `@Cacheable`, and `@Secured` are implemented as Dynamic Proxies generated at runtime by Spring's AOP infrastructure — the real bean is wrapped in a proxy without writing any proxy class manually.

**THE TRADE-OFFS:**
**Gain:** Transparent interception of access; lazy loading reduces startup cost; security enforcement without modifying real subjects; caching without changing service code; remote transparency.
**Cost:** Introduces indirection (one extra method call per operation); mutable proxy state (cached value, creation flag) requires thread safety; debugging is harder when proxied calls behave differently from direct calls; proxy may hide important failures (lazy object creation failure occurs at use-time, not at proxy creation).

---

### 🧪 Thought Experiment

**SETUP:**
A document viewer loads 100 document thumbnails. Each thumbnail is a lazily-loadable `ThumbnailImage`. Most users only scroll to the first 10.

**WHAT HAPPENS WITHOUT PROXY (eager loading):**
All 100 thumbnails loaded on startup: 100 × 200 KB = 20 MB RAM used, 100 disk reads taking 2 seconds. User sees 10 thumbnails, closes the app. 90% of the loading was wasted.

**WHAT HAPPENS WITH VIRTUAL PROXY:**
100 `ThumbnailImageProxy` objects are created instantly (negligible memory). Each proxy holds a file path, not the image data. When the user scrolls to thumbnail #3, `thumbnail3.display()` is called — the proxy loads the real image on-demand, taking 20 ms. Thumbnails 11–100 are never loaded. Startup: instant. Memory: 10 × 200 KB = 2 MB.

**THE INSIGHT:**
The Virtual Proxy shifts the cost from "paid at object creation" to "paid at first access." When many objects might never be accessed, this can be a 10× to 100× improvement in both startup time and memory.

---

### 🧠 Mental Model / Analogy

> A Proxy is like a hotel concierge. Guests (callers) ask the concierge for things — a restaurant reservation (service call). The concierge checks your VIP status (security proxy), looks up whether they've made a similar reservation before (caching proxy), then contacts the restaurant if needed (real subject). Guests never know whether the concierge handled it directly or called the restaurant.

- "Hotel concierge" → the proxy object
- "VIP status check" → protection proxy permission check
- "Previously booked same restaurant?" → caching proxy lookup
- "Calling the restaurant" → delegating to real subject
- "Guest interface (just ask the concierge)" → same interface to caller

Where this analogy breaks down: a real concierge sometimes declines requests. A transparent proxy delegates all calls by contract — it only adds concerns (timing, caching, access control) but never completely blocks a valid call without returning an appropriate error through the interface.

---

### 📶 Gradual Depth — Four Levels

**Level 1 — What it is (anyone can understand):**
A Proxy is a "middleman" for an object. You ask the middleman for what you need. The middleman may handle it directly (from a cache, or with a quick check), or pass it along to the real thing. You never know whether you spoke to the middleman or the real thing — the interface is identical.

**Level 2 — How to use it (junior developer):**
Create a `Subject` interface. Implement `RealSubject` (the real thing). Create `ProxySubject implements Subject` with a `private RealSubject realSubject` field. In `ProxySubject.operation()`: perform pre-checks (security, cache lookup), then call `realSubject.operation()` (potentially creating it first for virtual proxy), then perform post-actions (cache store, logging). In Spring: use `@Transactional` and `@Cacheable` — Spring generates the proxy for you.

**Level 3 — How it works (mid-level engineer):**
Java provides two proxy mechanisms: (1) **Static proxy** — explicit class implementing the interface, as shown above. (2) **Dynamic proxy** (`java.lang.reflect.Proxy`) — generates a proxy class at runtime implementing any interface, delegating through `InvocationHandler`. Spring AOP uses a refined version (CGLIB for class-based proxies when there's no interface). `InvocationHandler.invoke(Object proxy, Method method, Object[] args)` receives all calls — useful for cross-cutting concerns without a separate method per interface method. A critical constraint: Java's `Proxy.newProxyInstance` only works with interfaces, not classes — hence Spring's requirement for interface-based injection in some cases.

**Level 4 — Why it was designed this way (senior/staff):**
Proxy is the foundational mechanism for AOP (Aspect-Oriented Programming). Every `@Transactional` method in Spring is a proxy-wrapped method: the proxy starts a transaction before the call and commits or rolls back after. This is possible only because the proxy intercepts the call before delegating. The limitation: self-invocation bypass. If `serviceA.methodA()` calls `this.methodB()` (both `@Transactional`), the transaction on `methodB()` is NOT applied — because `this.methodB()` bypasses the proxy. The proxy is only invoked on external calls. This is the most common production bug related to proxies. Spring's solution: inject `self` (the proxy reference) and call `self.methodB()` — or use `@Transactional(propagation = REQUIRES_NEW)` carefully.

---

### ⚙️ How It Works (Mechanism)

**Virtual Proxy (lazy loading):**
```
┌─────────────────────────────────────────────────┐
│  VIRTUAL PROXY — LAZY LOADING                   │
│                                                 │
│  Client holds: ImageProxy (lightweight, ~50B)   │
│                                                 │
│  Client calls: image.display()                  │
│                │                                │
│   if realImage == null:                         │
│       realImage = new RealImage(filePath)       │
│       (50MB loaded NOW, not at construction)    │
│   realImage.display()                           │
│                                                 │
│  Subsequent calls: realImage.display() directly │
│  (real image already loaded, proxy is thin)     │
└─────────────────────────────────────────────────┘
```

**Protection Proxy:**
```
Client → SecurityProxy.getData()
  ↓
  Check: currentUser.hasPermission("READ_DATA")
  ↓ yes
  realService.getData()  → return data
  ↓ no
  throw AccessDeniedException
```

**Caching Proxy:**
```
Client → CachingProxy.getProductById(123)
  ↓
  cache.get(123) → HIT? return cached product
                → MISS?
                     realRepo.findById(123)
                     cache.put(123, product)
                     return product
```

---

### 🔄 The Complete Picture — End-to-End Flow

**NORMAL FLOW (Spring @Transactional proxy):**
```
HTTP request reaches Spring Controller
  → calls orderService.placeOrder(request)
  → Spring intercepts via TransactionProxy
                              ← YOU ARE HERE
  → proxy opens transaction
  → delegates to OrderService.placeOrder()
  → service executes (DB writes etc.)
  → returns result
  → proxy commits transaction
  → result returned to controller
```

**FAILURE PATH:**
```
OrderService.placeOrder() throws RuntimeException
  → exception bubbles to TransactionProxy
  → proxy detects unchecked exception
  → proxy ROLLS BACK the transaction
  → exception re-thrown to controller
  → controller returns 500 error
  → database state: unchanged (rolled back)
```

**WHAT CHANGES AT SCALE:**
At 10,000 req/s, the proxy overhead per call is ~500 ns (JVM method dispatch through InvocationHandler reflection). Negligible for I/O-bound operations (DB calls are 5-50 ms). For CPU-bound in-memory operations called millions of times per second, proxy overhead becomes measurable. JIT compilation inlines frequently-called proxy methods after warm-up, reducing overhead. At extreme scale, consider direct calls for hot paths and reserving proxies for boundary operations.

---

### 💻 Code Example

**Example 1 — Static Virtual Proxy (lazy loading):**
```java
public interface Image {
    void display();
    int getWidth();
    int getHeight();
}

public class RealImage implements Image {
    private final String filename;
    private final BufferedImage data;

    public RealImage(String filename) {
        System.out.println("Loading " + filename + "...");
        this.filename = filename;
        this.data = ImageIO.read(new File(filename)); // slow
    }

    @Override public void display() {
        System.out.println("Displaying " + filename);
    }
    @Override public int getWidth() { return data.getWidth(); }
    @Override public int getHeight() { return data.getHeight(); }
}

// Virtual Proxy: defers RealImage creation until needed
public class LazyImageProxy implements Image {
    private final String filename;
    private RealImage realImage; // null until first display()

    public LazyImageProxy(String filename) {
        this.filename = filename;
        // RealImage NOT created here — proxy is cheap
    }

    @Override
    public void display() {
        if (realImage == null) {
            realImage = new RealImage(filename); // LAZY load
        }
        realImage.display();
    }

    @Override public int getWidth() {
        // Can return metadata without loading full image
        return getMetadata(filename).width();
    }
    @Override public int getHeight() {
        return getMetadata(filename).height();
    }
}

// Client: same interface, transparent proxy
Image img = new LazyImageProxy("large-photo.jpg");
// No disk access yet
System.out.println("Width: " + img.getWidth()); // metadata
img.display(); // FIRST display: loads from disk
img.display(); // SECOND display: uses cached realImage
```

**Example 2 — Dynamic Proxy (Java reflection):**
```java
public interface UserService {
    User getUser(Long id);
    void deleteUser(Long id);
}

// Logging InvocationHandler — wraps any service
public class LoggingInvocationHandler
        implements InvocationHandler {

    private final Object realService;

    public LoggingInvocationHandler(Object service) {
        this.realService = service;
    }

    @Override
    public Object invoke(Object proxy, Method method,
                         Object[] args) throws Throwable {
        long start = System.nanoTime();
        try {
            Object result = method.invoke(
                realService, args);
            long elapsed = System.nanoTime() - start;
            log.info("{} completed in {}µs",
                method.getName(), elapsed / 1000);
            return result;
        } catch (InvocationTargetException e) {
            log.error("{} failed: {}",
                method.getName(), e.getCause().getMessage());
            throw e.getCause();
        }
    }
}

// Create wrapped proxy at runtime:
UserService realService = new UserServiceImpl();
UserService proxy = (UserService) Proxy.newProxyInstance(
    realService.getClass().getClassLoader(),
    new Class[]{UserService.class},      // must be interface
    new LoggingInvocationHandler(realService));

// Caller uses proxy identically to real service:
User user = proxy.getUser(42L); // logged automatically
```

**Example 3 — Spring @Cacheable as managed Proxy:**
```java
@Service
public class ProductService {

    private final ProductRepository repo;

    @Cacheable(value = "products", key = "#id")
    public Product getProduct(Long id) {
        // Spring's CachingProxy checks cache first:
        // if cache hit: return cached value (never reaches here)
        // if cache miss: execute this method, cache result
        return repo.findById(id).orElseThrow();
    }

    @CacheEvict(value = "products", key = "#product.id")
    public void updateProduct(Product product) {
        repo.save(product);
        // Cache evict proxy removes entry after save
    }
}
// Spring generates a CGLIB proxy for ProductService
// @Cacheable logic lives in the proxy, not in this class
```

---

### ⚖️ Comparison Table

| Proxy Type | Purpose | Real Subject Created | Best For |
|---|---|---|---|
| **Virtual Proxy** | Defer expensive creation | On first access | Lazy loading images, documents |
| **Protection Proxy** | Control access | Pre-created | Security, permission checking |
| **Caching Proxy** | Return cached results | Pre-created | DB/API result caching |
| **Remote Proxy** | Represent remote object | Remote (RPC/HTTP) | gRPC stubs, REST client proxies |
| **Smart Reference** | Reference counting, locking | Pre-created | Ref-counted resources |
| Decorator | Add behaviour | Always delegated | Feature addition |

How to choose: use Virtual Proxy for lazy loading expensive objects. Use Protection Proxy for permission enforcement. Use Caching Proxy (or `@Cacheable`) when the same inputs frequently produce the same output. In modern Java: prefer Spring AOP-managed proxies over hand-rolled ones for cross-cutting concerns.

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| Proxy and Decorator are the same | Proxy controls ACCESS to the real subject; Decorator ADDS BEHAVIOUR. Both wrap same-interface objects. Intent is the distinction |
| Spring's @Transactional always works on any method call | @Transactional only works on external proxy-dispatch calls. `this.methodB()` inside the same class bypasses the proxy — the transaction annotation has no effect |
| A Proxy always delegates to a real object | Remote Proxy may delegate over a network. Null Object Proxy may not delegate at all. Caching Proxy may return without delegating. "Always delegates" is the Decorator contract, not Proxy's |
| Dynamic Proxy and static Proxy are interchangeable | Dynamic Proxy scales better (one InvocationHandler per concern covers all interface methods). Static Proxy requires one method override per interface method — unmaintainable for large interfaces |
| The Proxy hides the real object's existence | Callers typically know a proxy exists (they chose `@Cacheable`, or they see the CGLIB proxy class name in logs). The proxy's existence is transparent behaviourally but not always architecturally |

---

### 🚨 Failure Modes & Diagnosis

**1. Spring @Transactional Self-Invocation Bypass**

**Symptom:** A method annotated `@Transactional` is called from within the same class (`this.innerMethod()`). The transaction is NOT started or the rollback does NOT occur for the inner method.

**Root Cause:** Spring's proxy only intercepts external calls. Class-internal calls go directly to the target object, bypassing the proxy. The transaction demarcation exists only on the proxy.

**Diagnostic:**
```java
// Reproduce: log transaction context inside innerMethod()
@Transactional(propagation = REQUIRES_NEW)
public void innerMethod() {
    Transaction tx = TransactionSynchronizationManager
        .getCurrentTransactionName();
    log.info("Transaction: {}", tx);
    // If null when called via this.innerMethod():
    // self-invocation bypass confirmed
}
```

**Fix:**
```java
// Option 1: Inject self (the proxy)
@Autowired
private YourService self;
self.innerMethod();   // goes through proxy

// Option 2: Extract to separate @Service class
// so the call crosses a proxy boundary

// Option 3: Use AspectJ mode (compile-time weaving)
// which bypasses proxy limitations
```

**Prevention:** Avoid `@Transactional` on internal helper methods called from the same class. Structural rule: transaction boundaries should be at service class entry points only.

---

**2. Virtual Proxy Not Thread-Safe — Double Initialisation**

**Symptom:** Two threads call the same proxy simultaneously; `realSubject = new RealSubject()` executes twice. The expensive object is created twice, and one instance is discarded.

**Root Cause:** The `if (realSubject == null) realSubject = ...` check is not atomic. Two threads pass the null check simultaneously.

**Diagnostic:**
```java
// Add a counter to the real subject constructor:
public RealImage(String path) {
    int count = initCount.incrementAndGet();
    if (count > 1) log.warn(
        "Warning: initialised {} times", count);
}
// If count > 1 under concurrent load: thread-safety bug
```

**Fix:**
```java
// Use double-checked locking with volatile:
private volatile RealImage realImage;

public void display() {
    if (realImage == null) {
        synchronized (this) {
            if (realImage == null) {
                realImage = new RealImage(filename);
            }
        }
    }
    realImage.display();
}

// Or: use AtomicReference.compareAndSet()
```

**Prevention:** All virtual proxy implementations of lazy initialisation must use `volatile` + double-checked locking or `AtomicReference`.

---

**3. Protection Proxy Bypassed via Direct Reference**

**Symptom:** Users execute operations they should not have access to. A security audit reveals some code paths skip the proxy and call the real service directly.

**Root Cause:** The `RealService` class is accessible to callers (not package-private). A developer bypassed the proxy by injecting `RealServiceImpl` instead of the proxy.

**Diagnostic:**
```bash
# Find direct instantiation of real service (bypassing proxy)
grep -r "new RealServiceImpl\|@Autowired.*RealServiceImpl" \
  src --include="*.java"
# Any result outside the proxy/factory = bypass
```

**Fix:**
Make `RealServiceImpl` package-private or move to an internal package. All external access must go through the `ServiceInterface` which is implemented by the proxy.

**Prevention:** Use Java module system or package visibility to prevent external direct access to real subject classes.

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**
- `Interface` — proxy and real subject must share an interface; the proxy IS-A Subject via interface implementation
- `Polymorphism` — caller holds an interface reference; JVM dispatches to proxy rather than real subject transparently
- `Lazy Loading` — the virtual proxy's main purpose; understanding eager vs lazy initialisation drives correct proxy design

**Builds On This (learn these next):**
- `Aspect-Oriented Programming (AOP)` — generalises Proxy to any cross-cutting concern via aspects; Spring AOP is automated Dynamic Proxy generation
- `Dynamic Proxy (Java)` — `java.lang.reflect.Proxy` and CGLIB; the technical mechanism underlying all Spring proxy-based annotations
- `Decorator` — the pattern most commonly confused with Proxy; understanding the intent difference (access control vs behaviour addition) clarifies both

**Alternatives / Comparisons:**
- `Decorator` — adds new behaviour to the interface; Proxy controls access to same behaviour
- `Facade` — simplifies access to multiple subsystems; Proxy controls access to one subject with the same interface
- `Null Object` — a special Proxy that does nothing (safe stand-in when real subject is absent)

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ WHAT IT IS   │ Surrogate implementing same interface as  │
│              │ real subject, controlling access to it    │
├──────────────┼───────────────────────────────────────────┤
│ PROBLEM IT   │ Direct object access gives no interception│
│ SOLVES       │ for caching, security, or lazy loading    │
├──────────────┼───────────────────────────────────────────┤
│ KEY INSIGHT  │ Proxy is transparent to callers; it adds  │
│              │ control without changing either side      │
├──────────────┼───────────────────────────────────────────┤
│ USE WHEN     │ Access needs to be deferred, cached,      │
│              │ secured, or remotely transparent          │
├──────────────┼───────────────────────────────────────────┤
│ AVOID WHEN   │ Behaviour addition is needed (use         │
│              │ Decorator); complexity not warranted      │
├──────────────┼───────────────────────────────────────────┤
│ TRADE-OFF    │ Transparent access control vs indirection │
│              │ overhead and self-invocation limitations  │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "Same door, different gatekeeper —        │
│              │  caller doesn't know the difference."     │
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ Dynamic Proxy → AOP → Decorator           │
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** A Caching Proxy for `ProductService.getProduct(id)` uses an in-memory `HashMap` as the cache. The product team updates product prices in the database every 15 minutes. After a price update, users are seeing stale prices for up to 4 hours. Trace the exact mechanism: (a) how the stale cached value is returned, (b) why the 15-minute update cycle doesn't invalidate the cache, (c) what three different cache invalidation strategies could fix this and the trade-offs of each.

**Q2.** Spring creates CGLIB proxies for `@Service` classes and JDK dynamic proxies for interface-typed beans. A developer annotates a `FinalClass` (with the `final` keyword) with `@Transactional`. Spring throws `Cannot subclass final class: FinalClass`. Explain exactly why `final` prevents proxy generation for CGLIB but not JDK dynamic proxies, and describe two code changes that resolve the exception without removing `final` from the class.

