---
layout: default
title: "Proxy Pattern"
parent: "Design Patterns"
nav_order: 777
permalink: /design-patterns/proxy-pattern/
number: "777"
category: Design Patterns
difficulty: ★★☆
depends_on: "Object-Oriented Programming, Decorator Pattern, Adapter Pattern"
used_by: "Spring AOP, Lazy loading, Access control, Caching proxies, Remote proxies"
tags: #intermediate, #design-patterns, #structural, #oop, #aop, #access-control
---

# 777 — Proxy Pattern

`#intermediate` `#design-patterns` `#structural` `#oop` `#aop` `#access-control`

⚡ TL;DR — **Proxy** provides a surrogate or placeholder for another object to **control access** to it — intercepting method calls to add lazy initialization, access control, caching, logging, or remote communication, all while presenting the same interface as the real object.

| #777            | Category: Design Patterns                                                 | Difficulty: ★★☆ |
| :-------------- | :------------------------------------------------------------------------ | :-------------- |
| **Depends on:** | Object-Oriented Programming, Decorator Pattern, Adapter Pattern           |                 |
| **Used by:**    | Spring AOP, Lazy loading, Access control, Caching proxies, Remote proxies |                 |

---

### 📘 Textbook Definition

**Proxy** (GoF, 1994): a structural design pattern that provides a surrogate or placeholder for another object to control access to it. The proxy implements the same interface as the real subject and holds a reference to it. The proxy can intercept calls to the real subject and add behavior: lazy initialization (Virtual Proxy), access control (Protection Proxy), remote communication (Remote Proxy), caching (Caching Proxy), logging (Logging Proxy). GoF intent: "Provide a surrogate or placeholder for another object to control access to it." Key patterns using Proxy: Spring AOP (`@Transactional`, `@Cacheable`, `@Async`), JDK dynamic proxies, CGLIB proxies. Distinguished from Decorator: Proxy CONTROLS ACCESS; Decorator ADDS BEHAVIOR. Same interface — different intent.

---

### 🟢 Simple Definition (Easy)

A bodyguard. You (the real subject) are a celebrity. Your bodyguard (proxy) intercepts everyone who wants to meet you. The bodyguard checks: "Is this person on the approved list?" If yes, they get to meet you. If no, the bodyguard says no. From the visitor's perspective, they're "meeting the celebrity" — the bodyguard presents the same interface. You (the celebrity) don't have to deal with everyone — the proxy handles access control.

---

### 🔵 Simple Definition (Elaborated)

Spring `@Transactional`: your service method `orderService.placeOrder()` is called. But Spring has wrapped `orderService` in a CGLIB proxy. The proxy intercepts the call, opens a transaction, calls the real `placeOrder()` on the real service, then commits (or rolls back on exception), then returns. You call the same method on what looks like the same object — but you're calling a proxy. This is a Protection/Behavior proxy — it controls the transactional context around your method.

---

### 🔩 First Principles Explanation

**Proxy types and how Spring implements them:**

```
PROXY STRUCTURE:

  «interface» Subject
  ───────────────────
  +request(): Response

  RealSubject implements Subject        Proxy implements Subject
  ─────────────────────────────         ────────────────────────────
  +request(): Response                  -realSubject: Subject
      // actual work                    +request(): Response
                                            // BEFORE: check access, open tx
                                            realSubject.request()
                                            // AFTER: commit tx, log, return

  Client → Subject (interface) → might get RealSubject OR Proxy.
  Client doesn't know which — same interface.

PROXY TYPES:

  1. VIRTUAL PROXY — lazy initialization:

     class HeavyImageProxy implements Image {
         private Image realImage;       // created lazily
         private final String filename;

         HeavyImageProxy(String filename) { this.filename = filename; }

         @Override
         public void display() {
             if (realImage == null) {
                 System.out.println("Loading image: " + filename);
                 realImage = new RealImage(filename);  // expensive: disk I/O
             }
             realImage.display();   // delegate
         }
     }

     // Client:
     Image img = new HeavyImageProxy("photo.jpg");  // NO disk I/O yet
     // ... user may never call display() — RealImage never created
     img.display();  // FIRST call: loads image, then displays
     img.display();  // subsequent calls: image already loaded

  2. PROTECTION PROXY — access control:

     class SecureServiceProxy implements UserService {
         private final UserService realService;
         private final SecurityContext security;

         @Override
         public User getUser(String userId) {
             if (!security.currentUserHasRole("ROLE_ADMIN")) {
                 throw new AccessDeniedException("Admin role required");
             }
             return realService.getUser(userId);
         }

         @Override
         public void deleteUser(String userId) {
             if (!security.currentUserHasRole("ROLE_SUPER_ADMIN")) {
                 throw new AccessDeniedException("Super admin required");
             }
             realService.deleteUser(userId);
         }
     }

  3. CACHING PROXY:

     class CachingProductRepository implements ProductRepository {
         private final ProductRepository realRepo;
         private final Map<String, Product> cache = new ConcurrentHashMap<>();

         @Override
         public Optional<Product> findById(String id) {
             if (cache.containsKey(id)) {
                 return Optional.of(cache.get(id));  // cache hit — no DB call
             }
             Optional<Product> product = realRepo.findById(id);
             product.ifPresent(p -> cache.put(id, p));  // cache for next time
             return product;
         }
     }

  4. REMOTE PROXY — hides network communication:

     // RMI, REST client, gRPC stub — all are Remote Proxy patterns:
     // Client calls stub.getUser(id) (local call).
     // Stub serializes params, sends HTTP/RPC request, deserializes response.
     // Client doesn't know or care about network.

     // Spring's @FeignClient creates a Remote Proxy:
     @FeignClient(name = "user-service", url = "http://user-service:8080")
     interface UserServiceClient {
         @GetMapping("/users/{id}")
         User getUser(@PathVariable String id);
     }
     // Spring generates a proxy: calling getUser() sends HTTP GET request.

SPRING AOP — JDK DYNAMIC PROXY vs CGLIB:

  JDK Dynamic Proxy:
  - Created for interface-based beans.
  - Generates a proxy class implementing the SAME INTERFACE at runtime.
  - Proxy class generated via java.lang.reflect.Proxy.newProxyInstance().
  - ONLY works for classes that implement an interface.

  CGLIB Proxy:
  - Created when bean has no interface, OR @EnableAspectJAutoProxy(proxyTargetClass=true).
  - Generates a SUBCLASS of the target class at runtime.
  - Overrides methods to add interceptor logic.
  - Works for concrete classes without interfaces.
  - LIMITATION: cannot proxy final classes or final methods.

  // Example: @Transactional on OrderService:
  // Spring creates CGLIB proxy: OrderService$$EnhancerBySpringCGLIB$$abc123
  // When you @Autowire OrderService, you get the CGLIB proxy — not the real service.

  // COMMON BUG: self-invocation:
  @Service
  class OrderService {
      @Transactional
      public void placeOrder(Order o) {
          validateOrder(o);
          saveOrder(o);
          sendConfirmation(o);     // ← calls this.sendConfirmation()
      }

      @Transactional(propagation = REQUIRES_NEW)
      public void sendConfirmation(Order o) {  // <- won't start new transaction!
          emailService.send(o.getCustomerEmail(), "Confirmation");
      }
  }

  // BUG: placeOrder() calls sendConfirmation() via `this` — bypasses proxy!
  // Proxy is only involved when call comes THROUGH the proxy object.
  // this.sendConfirmation() goes directly to the real method — no AOP intercept.
  // FIX: inject the proxy: ApplicationContext.getBean(OrderService.class).sendConfirmation()
  //      or use @Autowired OrderService self; self.sendConfirmation(o);
```

---

### ❓ Why Does This Exist (Why Before What)

WITHOUT Proxy:

- Real subject handles access control, lazy init, caching — mixes concerns
- Every caller must handle cross-cutting concerns (transaction management, logging)

WITH Proxy:
→ Proxy intercepts calls before/after real subject — separates concerns
→ Real subject focuses on business logic only; cross-cutting added transparently via proxy

---

### 🧠 Mental Model / Analogy

> A building receptionist. To get to the CEO (real subject), you go through the receptionist (proxy). The receptionist checks: do you have an appointment? Are you on the authorized visitor list? If yes, they take you to the CEO. They might also log your visit, assign a visitor badge, notify the CEO you're arriving. The CEO's interface is unchanged ("I have a meeting with you"). The receptionist controls access transparently.

"CEO" = real subject (actual service/bean)
"Receptionist" = proxy (intercepts, checks, delegates)
"Same meeting interface" = proxy implements same interface as real subject
"Appointment check" = access control / precondition check
"Visitor log" = logging in the proxy (cross-cutting concern)

---

### ⚙️ How It Works (Mechanism)

```
PROXY INTERCEPT FLOW:

  Client → proxy.method(args)
              ─────────────────────────
              BEFORE advice:
                check auth, start tx, check cache, log entry
              ─────────────────────────
              → realSubject.method(args)
              ─────────────────────────
              AFTER advice:
                commit/rollback tx, update cache, log exit, handle exceptions
              ─────────────────────────
           ← returns result (from cache or from realSubject)
```

---

### 🔄 How It Connects (Mini-Map)

```
Need to intercept access to an object (lazy init, access control, caching, logging)
        │
        ▼
Proxy Pattern ◄──── (you are here)
(same interface as real subject; intercepts calls; controls access)
        │
        ├── Decorator: adds behavior (vs Proxy: controls access); structurally similar
        ├── Spring AOP: @Transactional, @Cacheable, @Async all use CGLIB/JDK proxies
        ├── Remote Proxy: @FeignClient, RMI stubs — hides network behind interface
        └── Facade: simplifies interface (vs Proxy: same interface, controls access)
```

---

### 💻 Code Example

```java
// JDK Dynamic Proxy example — logging proxy:

interface ProductService {
    Product findById(String id);
    void create(Product p);
}

class RealProductService implements ProductService {
    public Product findById(String id) { return repository.findById(id); }
    public void create(Product p)      { repository.save(p); }
}

// Proxy using JDK InvocationHandler:
class LoggingProxy implements InvocationHandler {
    private final Object target;
    private final Logger log = LoggerFactory.getLogger(LoggingProxy.class);

    LoggingProxy(Object target) { this.target = target; }

    @Override
    public Object invoke(Object proxy, Method method, Object[] args) throws Throwable {
        log.info("Calling {}.{}({})", target.getClass().getSimpleName(),
                 method.getName(), Arrays.toString(args));
        long start = System.currentTimeMillis();
        try {
            Object result = method.invoke(target, args);    // delegate to real object
            log.info("{} completed in {}ms", method.getName(),
                     System.currentTimeMillis() - start);
            return result;
        } catch (InvocationTargetException e) {
            log.error("{} failed: {}", method.getName(), e.getCause().getMessage());
            throw e.getCause();
        }
    }
}

// Create proxy:
ProductService real  = new RealProductService(repository);
ProductService proxy = (ProductService) Proxy.newProxyInstance(
    real.getClass().getClassLoader(),
    new Class[]{ProductService.class},
    new LoggingProxy(real)
);

// Client uses proxy — doesn't know it's a proxy:
proxy.findById("prod-123");  // logs: "Calling RealProductService.findById([prod-123])"
```

---

### ⚠️ Common Misconceptions

| Misconception                                  | Reality                                                                                                                                                                                                                                                                                                                                                                                                        |
| ---------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Proxy and Decorator are the same pattern       | Same structure (wraps object, same interface). Different INTENT. Decorator: ADD behavior — the new behavior IS the point. Proxy: CONTROL ACCESS — the access control/management IS the point. @Transactional adds transactional behavior (could be Decorator intent). But @Cacheable returns cached results instead of calling real method (bypasses target) — more clearly Proxy. The line blurs in practice. |
| Spring @Transactional works on any method call | Spring @Transactional ONLY works when the call comes through the Spring proxy. Self-invocation (`this.method()`) bypasses the proxy and the transaction management. This is a very common production bug. FIX: inject self-reference or restructure to avoid self-invocation.                                                                                                                                  |
| CGLIB proxy can proxy any class                | CGLIB proxies via subclassing. Cannot proxy: final classes (cannot be subclassed), final methods (cannot be overridden), private methods. @Transactional on private or final methods is silently ignored — no transaction is created.                                                                                                                                                                          |

---

### 🔥 Pitfalls in Production

**Spring self-invocation bug — @Transactional bypass:**

```java
// ANTI-PATTERN: Self-invocation bypasses Spring proxy:
@Service
class PaymentService {
    @Transactional
    public void processPayment(Payment payment) {
        chargeCard(payment);       // direct field access — goes through proxy? YES
        updateBalance(payment);    // direct call → goes through proxy? YES
        notifyUser(payment);       // calls this.notifyUser() → BYPASSES proxy → no new tx!
    }

    @Transactional(propagation = REQUIRES_NEW)  // intended: separate transaction
    public void notifyUser(Payment payment) {
        // This @Transactional is IGNORED because called via this.notifyUser()
        // Runs in processPayment's transaction (or no transaction if marked Propagation.REQUIRES_NEW)
        notificationRepository.save(new Notification(payment));
    }
}

// FIX OPTION 1: Inject self (avoid if possible — awkward):
@Service
class PaymentService {
    @Autowired PaymentService self;  // Spring injects the proxy!

    @Transactional
    public void processPayment(Payment payment) {
        ...
        self.notifyUser(payment);  // goes through proxy → @Transactional honored
    }
}

// FIX OPTION 2: Extract to separate Spring bean:
@Service class PaymentService {
    @Autowired NotificationService notificationService;  // separate bean

    @Transactional
    public void processPayment(Payment payment) {
        ...
        notificationService.notifyUser(payment);  // goes through Spring proxy
    }
}
// PREFERRED: separate bean = better cohesion + SRP + correct AOP behavior
```

---

### 🔗 Related Keywords

- `Decorator Pattern` — same structure; adds behavior (vs Proxy: controls access)
- `Spring AOP` — @Transactional, @Cacheable, @Async all implemented via JDK/CGLIB proxies
- `JDK Dynamic Proxy` — Java's built-in reflection-based proxy mechanism
- `CGLIB` — bytecode-level subclass proxy used by Spring when no interface available
- `Facade Pattern` — simplifies interface; Proxy controls access with same interface

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ KEY IDEA     │ Surrogate for the real object. Controls   │
│              │ access: lazy init, auth, cache, logging.  │
│              │ Same interface — client doesn't know.     │
├──────────────┼───────────────────────────────────────────┤
│ USE WHEN     │ Lazy init of expensive object; access     │
│              │ control; transparent caching; logging;   │
│              │ remote communication over local interface │
├──────────────┼───────────────────────────────────────────┤
│ AVOID WHEN   │ Simple delegation without control logic;  │
│              │ when Decorator is the right intent (adding│
│              │ behavior vs controlling access)           │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "Receptionist: you reach the CEO through  │
│              │  them — they check your appointment,     │
│              │  log your visit, pass you through."       │
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ Decorator Pattern → Spring AOP →          │
│              │ CGLIB Proxies → Chain of Responsibility   │
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** Spring Data JPA repositories (`UserRepository extends JpaRepository`) are created as JDK dynamic proxies at runtime — no implementation class is written by the developer. Spring generates the proxy that implements the interface. Query methods like `findByEmail(String email)` are intercepted by the proxy, which parses the method name into a JPQL query and executes it. How does this use of the Proxy pattern enable the Spring Data "query from method name" feature? What is the `InvocationHandler` equivalent in Spring Data's proxy creation?

**Q2.** Virtual Proxy is used for lazy loading in Hibernate: a `User` entity has a `@OneToMany(fetch = LAZY) List<Order> orders` field. Until you access `user.getOrders()`, no SQL is executed. The `orders` field holds a Hibernate proxy (a CGLIB-generated subclass of `List`). When you access it, the proxy fires a SQL query to load orders. What happens if you detach the entity from the Hibernate session BEFORE accessing `orders`? What is the `LazyInitializationException`, and how does the Virtual Proxy pattern explain why it occurs?
