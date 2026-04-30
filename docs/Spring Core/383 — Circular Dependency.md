---
layout: default
title: "Circular Dependency"
parent: "Spring Core"
nav_order: 383
permalink: /spring/circular-dependency/
number: "383"
category: Spring Core
difficulty: ★★☆
depends_on: "Bean Lifecycle, Dependency Injection, ApplicationContext, IoC"
used_by: "Spring Boot startup, @Lazy injection, refactoring, architecture"
tags: #java, #spring, #springboot, #intermediate, #architecture
---

# 383 — Circular Dependency

`#java` `#spring` `#springboot` `#intermediate` `#architecture`

⚡ TL;DR — A situation where bean A depends on bean B and bean B depends on bean A — a design smell that constructor injection makes impossible to ignore and field injection dangerously hides.

| #383 | category: Spring Core
|:---|:---|:---|
| **Depends on:** | Bean Lifecycle, Dependency Injection, ApplicationContext, IoC | |
| **Used by:** | Spring Boot startup, @Lazy injection, refactoring, architecture | |

---

### 📘 Textbook Definition

A **circular dependency** exists when bean A depends on bean B and bean B (directly or transitively) depends on bean A, forming a dependency cycle. With constructor injection, Spring 6.x throws `BeanCurrentlyInCreationException` at startup because the container cannot fulfil A's constructor before B is created, and cannot fulfil B's constructor before A is created — a genuine deadlock. With setter or field injection, Spring historically used "early bean references" (partially-initialised proxies) to resolve the cycle silently, but this was disabled by default in Spring Boot 2.6 / Spring 6 due to the class of subtle bugs it produced. Circular dependencies are a design smell indicating that responsibilities should be redesigned.

---

### 🟢 Simple Definition (Easy)

A circular dependency is when two classes need each other to exist — service A needs service B, but service B also needs service A. Spring can't create either first — a chicken-and-egg problem.

---

### 🔵 Simple Definition (Elaborated)

When Spring creates beans, it resolves dependencies in order: to create A, it first creates B; to create B, it first creates A. With a cycle, the creation of either requires the other to already exist. Constructor injection exposes this immediately as a startup crash — which is good because it forces you to fix the design. Field and setter injection can work around it using Spring's "early reference" mechanism, but this creates subtle bugs: the injected reference may be a half-initialised object or a raw instance instead of the AOP proxy, leading to missing `@Transactional` behaviour or NPEs.

---

### 🔩 First Principles Explanation

**The creation deadlock:**

```
┌─────────────────────────────────────────────────────┐
│  CIRCULAR DEPENDENCY DEADLOCK                       │
│                                                     │
│  Creating OrderService:                             │
│  → needs PaymentService                             │
│  → start creating PaymentService                    │
│  → PaymentService needs OrderService               │
│  → OrderService is being created (not ready yet)   │
│  → DEADLOCK: neither can complete                  │
│                                                     │
│  Constructor injection: FAILS FAST at startup       │
│  BeanCurrentlyInCreationException thrown            │
│                                                     │
│  Field injection (Spring 5.x): uses early ref       │
│  → OrderService receives half-init PaymentService   │
│  → PaymentService gets UNPROXIED OrderService       │
│  → @Transactional on OrderService → MISSING         │
└─────────────────────────────────────────────────────┘
```

**Why Spring Boot 2.6 disabled field-injection circular resolution:**

Spring Boot 2.6 set `spring.main.allow-circular-references=false` by default. The field-injection workaround produced a class of bugs where beans were injected as raw objects (bypassing AOP) rather than proxied beans. The AOP proxy is created AFTER the full lifecycle — but the early reference bypasses this, so `@Transactional` on circulary-injected beans silently didn't work.

---

### ❓ Why Does This Exist (Why Before What)

**WHY circular dependencies emerge:**

```
Common causes:

  1. God services:
     OrderService handles orders, payments, notifications
     PaymentService handles payments, order status updates
     → Both need each other's functionality

  2. Missing event bus:
     ServiceA calls ServiceB.onXxx()
     ServiceB calls ServiceA.onYyy()
     → Callback coupling creates tight cycle

  3. Shared state without a dedicated service:
     Two services accessing the same concept
     without a third dedicated owner for that concept

  4. Framework integration patterns:
     @Aspect proxy class sometimes causes
     transient cycles during BPP processing
```

**WITH proper redesign:**

```
→ Extract shared logic to a third service (C)
  → A depends on C, B depends on C — no cycle
→ Use events: A publishes, B subscribes
  → A depends on EventPublisher (not B)
  → B depends on EventPublisher (not A)
→ If genuinely optional: @Lazy on one injection point
  → breaks creation cycle while honouring the dep
```

---

### 🧠 Mental Model / Analogy

> A circular dependency is like two government offices that each require a form stamped by the other office before they'll issue anything. "Get form A from Office B." "Office B needs form B stamped by Office A." "Office A won't stamp without form A from Office B." The deadlock is real and unfixable within the current design — you need a third office (or a redesigned process) that both can use independently.

"Office A requiring Office B's stamp" = A depends on B
"Office B requiring Office A's stamp" = B depends on A
"The deadlock" = BeanCurrentlyInCreationException
"Third office both use" = extract shared logic to service C
"Redesigned process" = event-driven decoupling

---

### ⚙️ How It Works (Mechanism)

**Detection:**

Spring Boot 2.6+ catches cycles at startup with clear diagnostics:

```
The dependencies of some of the beans in the application
context form a cycle:

orderService → paymentService → orderService

|  orderService defined in ... OrderService.java      |
↑                                                     ↓
|  paymentService defined in ... PaymentService.java  |
```

**Three resolution strategies:**

```java
// STRATEGY 1: Extract to third service (BEST)
@Service class SharedOrderState {
  void updateOrderStatus(long id, OrderStatus s) {...}
  OrderStatus getOrderStatus(long id) {...}
}

@Service class OrderService {
  OrderService(PaymentService p, SharedOrderState shared) {}
}
@Service class PaymentService {
  PaymentService(SharedOrderState shared) {}
  // No dependency on OrderService!
}

// STRATEGY 2: @Lazy on one injection point (acceptable)
@Service
class OrderService {
  private final PaymentService payment;

  OrderService(@Lazy PaymentService payment) {
    this.payment = payment;
    // A proxy is injected here, real bean obtained on first call
  }
}

// STRATEGY 3: Events (best for decoupling)
@Service
class OrderService {
  private final ApplicationEventPublisher events;

  void completeOrder(Order order) {
    events.publishEvent(new OrderCompletedEvent(order));
    // No direct dep on PaymentService
  }
}

@Service
class PaymentService {
  @EventListener
  void onOrderCompleted(OrderCompletedEvent e) {
    processPayment(e.getOrder());
  }
  // No direct dep on OrderService
}
```

---

### 🔄 How It Connects (Mini-Map)

```
Bean creation starts (constructor injection)
        ↓
  CIRCULAR DEPENDENCY detected  ← you are here
  (A needs B, B needs A → creation deadlock)
        ↓
  Spring 6 / Boot 2.6+: BeanCurrentlyInCreationException
  (fails fast — correct behaviour)
        ↓
  Fix options:
  1. Extract service C → remove cycle
  2. Use ApplicationEvents → decouple entirely
  3. @Lazy on one side → deferred proxy injection
  4. allow-circular-references=true → NOT recommended
         ↓
  Root cause: low cohesion / high coupling in design
  → Circular deps = warning signal to refactor
```

---

### 💻 Code Example

**Example 1 — Diagnosing the cycle:**

```java
// CYCLE: UserService ↔ NotificationService
@Service
class UserService {
  // NotificationService to send welcome email on register
  public UserService(NotificationService notif) {
    this.notif = notif;
  }
  public void register(User u) { notif.sendWelcome(u); }
}

@Service
class NotificationService {
  // UserService to look up user preferences
  public NotificationService(UserService users) {
    this.users = users;
  }
  public void sendWelcome(User u) {
    Prefs p = users.getPrefs(u.getId());
  }
}
// Spring Boot: Circular reference (BeanCurrentlyInCreationException)
```

**Example 2 — Fix with event-driven design:**

```java
// FIX: decouple via events — no direct dependency

@Service
class UserService {
  private final ApplicationEventPublisher events;

  public UserService(ApplicationEventPublisher events) {
    this.events = events; // no dep on NotificationService
  }

  public User register(User u) {
    User saved = repo.save(u);
    events.publishEvent(new UserRegisteredEvent(saved));
    return saved;
  }

  public Prefs getPrefs(long id) { ... }
}

@Service
class NotificationService {
  // No dep on UserService — gets data from event
  @EventListener
  public void onUserRegistered(UserRegisteredEvent e) {
    Prefs prefs = e.getUser().getDefaultPrefs();
    sendWelcomeEmail(e.getUser(), prefs);
  }
}
```

**Example 3 — Enabling (temporarily) in Spring Boot:**

```yaml
# application.properties
# Only use as LAST RESORT while refactoring a legacy app
spring:
  main:
    allow-circular-references: true
# WARNING: AOP proxies may not be applied correctly
# @Transactional on circular beans may silently not work
# This is a tech-debt register item — must be fixed
```

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| Circular dependencies only happen with field injection | Circular deps can exist with any injection style. Constructor injection makes them fail fast; setter/field injection attempts to resolve them silently (and dangerously) |
| @Lazy solves the design problem | @Lazy is an acceptable workaround for AOP/framework-induced cycles but does not fix the design. It should not be used to resolve application-level circular dependencies |
| allow-circular-references=true is safe for production | It re-enables the early-reference mechanism that Spring Boot 2.6 disabled precisely because it caused AOP proxy bypass bugs in @Transactional and @Secured |
| Spring always detects all circular dependencies | Spring only detects cycles it encounters during eager singleton creation. Prototype-scoped and lazy beans may not surface cycles until first retrieval |

---

### 🔥 Pitfalls in Production

**1. allow-circular-references=true causing silent @Transactional failure**

```java
// BAD: circular dep resolved via allow-circular-references=true
// OrderService gets raw (non-proxied) PaymentService
@Service @Transactional
class PaymentService {
  PaymentService(OrderService orders) {...}
}
@Service
class OrderService {
  OrderService(PaymentService payment) {...}
  void process() {
    payment.charge(order); // calls raw PaymentService!
    // @Transactional proxy NOT applied → no transaction!
    // Silent data corruption: partial updates committed
  }
}

// FIX: extract shared logic to remove cycle
```

**2. @Aspect class creating transient cycle**

```java
// Spring AOP creates proxies via CGLIB
// Self-referencing @Aspect classes can trigger cycles
// during BeanPostProcessor chain processing

@Aspect @Component
class AuditAspect {
  @Autowired AuditRepository auditRepo; // fine

  // Transient cycle: AuditAspect depends on AuditRepository
  // AuditRepository is @Transactional → AuditAspect BPP
  // must run before AuditRepository is fully created
  // → Use @Lazy on AuditRepository injection in aspect
  @Autowired @Lazy AuditRepository auditRepo;
}
```

---

### 🔗 Related Keywords

- `Dependency Injection` — the mechanism that exposes or hides circular dependencies
- `Bean Lifecycle` — circular deps prevent the normal lifecycle from completing
- `@Lazy` — defers proxy resolution to break a cycle as a temporary workaround
- `ApplicationContext` — throws BeanCurrentlyInCreationException when cycle is detected
- `Cohesion` — circular deps indicate low cohesion and high coupling in design
- `@EventListener` — the cleanest solution: replace direct calls with published events

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ KEY IDEA     │ A → B → A: creation deadlock; design      │
│              │ smell; constructor injection exposes it    │
├──────────────┼───────────────────────────────────────────┤
│ USE WHEN     │ Never intentionally — it is a problem     │
│              │ to solve, not a pattern to use            │
├──────────────┼───────────────────────────────────────────┤
│ AVOID WHEN   │ Don't use allow-circular-references=true  │
│              │ in production — fix the design instead    │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "Two classes needing each other is two    │
│              │  classes needing a third one."            │
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ CGLIB Proxy (116) → Spring AOP (118) →    │
│              │ @Transactional (127)                      │
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** Spring Boot 2.6 disabled circular dependency resolution by default with `allow-bean-definition-overriding` also changed. Trace exactly what happens during startup when A (constructor-injected) depends on B (constructor-injected) which depends on A — which internal Spring class throws the exception, what data structure it uses to detect the cycle (hint: a Set tracking "currently being created" beans), and whether the detection covers transitive cycles (A→B→C→A) or only direct cycles.

**Q2.** The `@Aspect` class in Spring AOP occasionally causes a BeanCurrentlyInCreationException that is unrelated to application design problems — it's caused by the ordering of `BeanPostProcessor` creation. Explain the specific mechanism: why is `AbstractAutoProxyCreator` (a BPP) trying to create the `@Aspect` bean at a time when `@Aspect`'s dependencies are not yet fully proxied — and describe why `@Lazy` on the aspect's dependencies is the correct idiomatic workaround rather than redesigning the aspect.

