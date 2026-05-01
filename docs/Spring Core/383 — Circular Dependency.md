---
layout: default
title: "Circular Dependency"
parent: "Spring Core"
nav_order: 383
permalink: /spring/circular-dependency/
number: "383"
category: Spring Core
difficulty: ★★★
depends_on: "Bean, DI (Dependency Injection), @Autowired, Bean Lifecycle, CGLIB Proxy"
used_by: "Bean Lifecycle, BeanPostProcessor"
tags: #advanced, #spring, #internals, #architecture, #deep-dive
---

# 383 — Circular Dependency

`#advanced` `#spring` `#internals` `#architecture` `#deep-dive`

⚡ TL;DR — A **circular dependency** occurs when Bean A depends on Bean B and Bean B depends on Bean A (directly or transitively). Constructor injection fails fast at startup; setter/field injection is silently "resolved" by Spring via early bean exposure — a pattern that signals a design flaw.

| #383            | Category: Spring Core                                                    | Difficulty: ★★★ |
| :-------------- | :----------------------------------------------------------------------- | :-------------- |
| **Depends on:** | Bean, DI (Dependency Injection), @Autowired, Bean Lifecycle, CGLIB Proxy |                 |
| **Used by:**    | Bean Lifecycle, BeanPostProcessor                                        |                 |

---

### 📘 Textbook Definition

A **circular dependency** in Spring is a situation where two or more beans mutually depend on each other — directly (A → B → A) or through a chain (A → B → C → A). With **constructor injection**, Spring detects this at context startup and throws `BeanCurrentlyInCreationException` immediately, since it cannot instantiate A without B and cannot instantiate B without A. With **setter or field injection**, Spring uses a "three-level cache" mechanism to partially satisfy circular dependencies: when A is being created, Spring places an `ObjectFactory<A>` (early reference factory) into a `singletonFactories` map. When B requests A during its own initialisation, Spring retrieves the early reference (the raw, partially initialised A) and injects it into B. B completes, A completes. This workaround succeeds for singletons with field/setter injection but fails if A has an AOP proxy (the early reference is the raw bean, not the proxy) or if the beans use the `@Transactional` annotation. Spring Boot 2.6+ disabled circular dependency tolerance by default (`spring.main.allow-circular-references=false`). Circular dependencies almost always indicate a design flaw — typically a violation of the Single Responsibility Principle.

---

### 🟢 Simple Definition (Easy)

A circular dependency is when A needs B to be created and B needs A to be created — a chicken-and-egg problem. Constructor injection refuses to start; setter injection masks the problem with a workaround.

---

### 🔵 Simple Definition (Elaborated)

When Spring creates a singleton bean A, it needs A's dependencies ready first. If A needs B, Spring starts creating B. If B needs A — Spring is stuck: A is not finished yet. With constructor injection, Spring immediately throws an error at startup, which is the correct behaviour because you cannot pass A into B's constructor when A does not exist yet. With field/setter injection, Spring has a workaround: it creates an empty (uninitialised) A object, notes it as "being created," then starts creating B and injects the empty A shell into B. B finishes. Then Spring finishes setting up A. This "works" in simple cases but creates subtle bugs: B holds a reference to the early A which may not have AOP proxies applied yet — B may bypass transactions. Spring Boot 2.6+ prevents this workaround by default, forcing developers to fix the underlying design issue.

---

### 🔩 First Principles Explanation

**Constructor circular dependency — fails fast (correct behaviour):**

```java
// Bean A depends on Bean B via constructor
@Service
class ServiceA {
    private final ServiceB b;
    ServiceA(ServiceB b) { this.b = b; }
}

// Bean B depends on Bean A via constructor
@Service
class ServiceB {
    private final ServiceA a;
    ServiceB(ServiceA a) { this.a = a; }
}

// Spring startup:
//   Creating ServiceA → needs ServiceB
//   Creating ServiceB → needs ServiceA
//   ServiceA is currently being created → CIRCULAR!
//   Throws: BeanCurrentlyInCreationException:
//     "Requested bean is currently in creation:
//      Is there an unresolvable circular reference?"
```

**Field/setter circular dependency — Spring's three-level cache workaround:**

```java
@Service
class ServiceA {
    @Autowired ServiceB b; // field injection — deferred
}

@Service
class ServiceB {
    @Autowired ServiceA a; // field injection — deferred
}

// Spring's three-level cache:
//   singletonObjects:    fully initialised singletons
//   earlySingletonObjects: early references (bean constructed, not yet fully init)
//   singletonFactories:  ObjectFactory<T> that produces early reference

// Startup sequence:
//   1. Start creating ServiceA
//      → constructor runs (no deps in constructor) → raw ServiceA@123 exists
//      → Spring registers ObjectFactory<ServiceA> in singletonFactories
//   2. Begin @Autowired field injection for ServiceA → need ServiceB
//   3. Start creating ServiceB
//      → constructor runs → raw ServiceB@456 exists
//      → registers ObjectFactory<ServiceB> in singletonFactories
//   4. Begin @Autowired field injection for ServiceB → need ServiceA
//      → ServiceA is in singletonFactories → get early reference!
//      → early ServiceA@123 (raw, BPP not yet applied) injected into ServiceB
//   5. ServiceB fully initialised → moved to singletonObjects
//   6. ServiceA's @Autowired field 'b' = ServiceB@456 (fully done)
//   7. ServiceA fully initialised → moved to singletonObjects

// Result: "works" but ServiceB.a is the RAW ServiceA, not its AOP proxy
```

**The AOP proxy problem with circular dependencies:**

```java
// ServiceA has @Transactional — Spring wraps it in a proxy in BPP phase
@Service
class ServiceA {
    @Autowired ServiceB b; // creates circular dep
}

@Service
class ServiceB {
    @Autowired ServiceA a; // ServiceB gets EARLY reference to RAW ServiceA
    // a is NOT the @Transactional proxy — it is the raw bean
    // Calling a.doSomething() bypasses the transaction!
}
// Spring detects this and logs:
// "Bean 'serviceA' does not match the expected type [ServiceA$$EnhancerBySpring...]"
// And may throw:
// BeanNotOfRequiredTypeException if proxy type checking is strict
```

---

### ❓ Why Does This Exist (Why Before What)

What causes circular dependencies (root causes):

1. **SRP violation** — a class has too many responsibilities and must call back into a class that it serves.
2. **Service-service coupling** — `OrderService` calls `NotificationService`, and `NotificationService` calls `OrderService` for status.
3. **Lazy evaluation not used** — a class needs a peer for rare operations but declares it as a direct dependency.
4. **Framework infrastructure** — Spring's own `AnnotationAwareAspectJAutoProxyCreator` (a `BeanPostProcessor`) can cause circular dependencies with beans it processes.

Why the strict Spring Boot 2.6+ default (`allow-circular-references=false`) exists:
→ Silent circular dependency resolution via early bean exposure masked design flaws for years.
→ AOP proxy bypass (described above) caused hard-to-diagnose transaction bugs in production.
→ Forcing failures at startup pushes developers to fix the underlying design.

---

### 🧠 Mental Model / Analogy

> Think of two employees who each need the other's completed work to start their own. Employee A says "I'll start my report after I get B's section." Employee B says "I'll start my section after I get A's summary." With constructor injection, HR (Spring) detects this at hiring time and refuses to bring either on board — deadlock detected, fix the process. With setter injection, HR's workaround is: bring A on board with an empty desk (raw bean), let B borrow A's empty desk, B produces their work, then A gets B's work and finishes their report. The problem: B may try to use A's desk before A has put anything on it — B calls A's methods on the uninitialised shell.

"Employee needing another's completed work first" = constructor dependency
"Empty desk (raw, uninitialised)" = early bean reference in `singletonFactories`
"HR refuses to hire either" = `BeanCurrentlyInCreationException` on constructor cycle
"B borrowing A's empty desk" = B receiving A's early reference (pre-proxy)
"B calling A's methods on uninitialised shell" = bypassing AOP proxy on early reference

---

### ⚙️ How It Works (Mechanism)

**Spring's three-level cache (DefaultSingletonBeanRegistry):**

```
Level 1: singletonObjects        (ConcurrentHashMap)
  → Fully initialised, ready beans (normal lookup)

Level 2: earlySingletonObjects   (HashMap)
  → Partially initialised beans exposed for circular dep resolution
  → Populated from Level 3 when a circular dep is detected

Level 3: singletonFactories      (HashMap)
  → ObjectFactory<T> per bean being created
  → Produces the early reference when needed
  → Registered immediately after constructor call, before @Autowired injection

Lookup sequence for getBean("serviceA"):
  1. Check Level 1 → not found
  2. Check Level 2 → not found
  3. Check Level 3 → found ObjectFactory → call factory.getObject()
     → moves early ref to Level 2 (earlySingletonObjects)
     → removes Level 3 factory
  4. Return early reference (raw bean, before BPP.postProcessAfterInit)
```

---

### 🔄 How It Connects (Mini-Map)

```
Bean (managed object)
        │
        ▼
DI / @Autowired
(declares dependencies)
        │  mutual dependency
        ▼
Circular Dependency  ◄──── (you are here)
        │
        ├── constructor injection ──► BeanCurrentlyInCreationException (startup)
        │
        ├── field/setter injection ─► three-level cache workaround
        │                              │
        │                              ▼
        │                          Early bean reference (pre-proxy)
        │                          AOP proxy bypass risk
        │
        └── Spring Boot 2.6+ ─────► allow-circular-references=false (default)
                                    Forces constructor injection failures
```

---

### 💻 Code Example

**Correct fix: extract a shared dependency to break the cycle:**

```java
// PROBLEM: ServiceA and ServiceB are coupled
@Service class ServiceA {
    @Autowired ServiceB b;
    void processOrder(Order o) { b.notifyShipped(o); }
}
@Service class ServiceB {
    @Autowired ServiceA a;
    void notifyShipped(Order o) { a.updateStatus(o, SHIPPED); }
}

// ROOT CAUSE: NotificationService needs order-update logic from ServiceA
// FIX: Extract shared logic to OrderStatusService — breaks the cycle

@Service class OrderStatusService {
    void updateStatus(Order o, Status s) { ... } // extracted from ServiceA
}
@Service class ServiceA {
    private final OrderStatusService statusService;
    ServiceA(OrderStatusService statusService) { this.statusService = statusService; }
    void processOrder(Order o) { statusService.updateStatus(o, PROCESSING); }
}
@Service class ServiceB {
    private final OrderStatusService statusService;
    ServiceB(OrderStatusService statusService) { this.statusService = statusService; }
    void notifyShipped(Order o) { statusService.updateStatus(o, SHIPPED); }
}
// No circular dependency — both depend on a shared third service
```

**Alternative fix: use @Lazy to defer instantiation:**

```java
// @Lazy: Spring injects a proxy that creates the real bean on first method call
@Service
class ServiceA {
    private final ServiceB b;
    // @Lazy: inject a CGLIB proxy for ServiceB; real bean created on first use
    ServiceA(@Lazy ServiceB b) { this.b = b; }
}
@Service
class ServiceB {
    private final ServiceA a;
    ServiceB(ServiceA a) { this.a = a; } // resolves normally now
}
// ServiceA can be created (ServiceB proxy injected instead)
// ServiceB is created when ServiceA.b.someMethod() is first called
// WARNING: if both methods are called at startup, circular dep still fails
// Use @Lazy only as a last resort when refactoring is not possible
```

**Alternative fix: use ApplicationEvents to decouple:**

```java
// Decouple ServiceA and ServiceB via Spring's event system
@Service
class ServiceA {
    private final ApplicationEventPublisher events;
    ServiceA(ApplicationEventPublisher events) { this.events = events; }

    void processOrder(Order o) {
        // Fire event instead of calling ServiceB directly
        events.publishEvent(new OrderProcessedEvent(o));
    }
}

@Service
class ServiceB implements ApplicationListener<OrderProcessedEvent> {
    @Override
    public void onApplicationEvent(OrderProcessedEvent event) {
        notifyShipped(event.getOrder()); // no dependency on ServiceA
    }
}
// Clean: ServiceA publishes events; ServiceB listens — no coupling
```

---

### 🔁 Flow / Lifecycle

**Three-level cache resolution sequence (field injection circular dep):**

```
CONTEXT STARTUP
       │
       ▼
Creating ServiceA
  ├── constructor() → ServiceA@raw exists
  ├── register ObjectFactory<ServiceA> in singletonFactories (Level 3)
  ├── begin @Autowired injection → need ServiceB
  │
  ▼
Creating ServiceB
  ├── constructor() → ServiceB@raw exists
  ├── register ObjectFactory<ServiceB> in singletonFactories (Level 3)
  ├── begin @Autowired injection → need ServiceA
  │   └── getBean("serviceA"):
  │         Check Level 1: not found
  │         Check Level 2: not found
  │         Check Level 3: found! → factory.getObject() → ServiceA@raw
  │         Move to Level 2 (earlySingletonObjects)
  ├── ServiceA@raw injected into ServiceB.a field
  ├── BPP.postProcessBeforeInit for ServiceB
  ├── @PostConstruct for ServiceB
  ├── BPP.postProcessAfterInit for ServiceB → any proxy created
  └── ServiceB fully initialised → moved to Level 1
       │
       ▼
Continue ServiceA initialisation
  ├── ServiceB injected into ServiceA.b field
  ├── BPP.postProcessBeforeInit for ServiceA
  ├── @PostConstruct for ServiceA
  ├── BPP.postProcessAfterInit → if @Transactional: AOP proxy created
  │   PROBLEM: ServiceB already holds ServiceA@raw (not the proxy)
  └── ServiceA fully initialised → Level 1 has ServiceA@proxy
      BUT ServiceB.a still points to ServiceA@raw!
```

---

### ⚠️ Common Misconceptions

| Misconception                                                  | Reality                                                                                                                                                                                                     |
| -------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Spring always resolves circular dependencies silently          | Constructor injection throws `BeanCurrentlyInCreationException` immediately. Spring Boot 2.6+ throws for field/setter circular deps too unless `allow-circular-references=true` is set                      |
| Using `@Lazy` on one side of the cycle is a safe permanent fix | `@Lazy` is a workaround, not a fix. It defers the circular dependency problem to first use instead of resolving it. If first use occurs at startup, the circular dep still manifests                        |
| Circular dependencies only happen between two beans            | Circular deps can involve chains: A → B → C → D → A. Spring detects these transitive cycles too with the same exception                                                                                     |
| Field injection fixes circular dependencies                    | Field injection changes when the dep is satisfied (deferred vs constructor-time), allowing Spring's three-level cache to paper over the cycle. But the AOP proxy bypass risk remains — it is not a true fix |

---

### 🔥 Pitfalls in Production

**AOP proxy bypass: ServiceB holds early reference to raw ServiceA — @Transactional ignored**

```java
@Service
class ServiceA {
    @Autowired ServiceB b;
    @Transactional
    public void performTransaction() { ... } // wrapped in proxy
}
@Service
class ServiceB {
    @Autowired ServiceA a;
    // a is the RAW ServiceA — @Transactional NOT applied!
    public void doWork() {
        a.performTransaction(); // NO TRANSACTION — bypasses proxy!
        // Data operations inside performTransaction() are NOT atomic
    }
}
// Fix: break the circular dependency — do not mask it with field injection
```

---

### 🔗 Related Keywords

- `Bean Lifecycle` — circular deps manifest during Phase 1 and 2 (construction and injection)
- `BeanPostProcessor` — AOP proxy creation in Phase 6; early references miss this phase
- `CGLIB Proxy` — the proxy type used for `@Transactional`; early reference bypasses it
- `@Autowired` — the injection mechanism through which circular deps arise
- `DI (Dependency Injection)` — the pattern; circular deps are a pathological case of DI design

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ DETECTION    │ Constructor: fails at startup (good)      │
│              │ Field/setter: masked by 3-level cache     │
├──────────────┼───────────────────────────────────────────┤
│ RISK         │ AOP proxy bypass: early reference = raw   │
│              │ bean → @Transactional silently skipped    │
├──────────────┼───────────────────────────────────────────┤
│ SPRING BOOT  │ 2.6+: circular refs disabled by default   │
│              │ allow-circular-references=true to restore │
├──────────────┼───────────────────────────────────────────┤
│ REAL FIX     │ Extract shared logic to a third bean      │
│              │ Or use ApplicationEvents to decouple      │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "Circular dep = A needs B to exist,       │
│              │  B needs A to exist — break the cycle,    │
│              │  don't paper over it."                   │
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** In Spring's three-level cache, `singletonFactories` stores an `ObjectFactory` per bean being constructed. For beans that have AOP advice (`@Transactional`, `@Cacheable`), Spring registers a special `ObjectFactory` that calls `SmartInstantiationAwareBeanPostProcessor.getEarlyBeanReference()` instead of returning the raw bean. Explain how this method allows the early reference to be the AOP proxy rather than the raw bean, describe the limitations of this approach (what information is unavailable when the early proxy is created vs during normal `postProcessAfterInitialization`), and identify a scenario where even this mechanism fails and `BeanNotOfRequiredTypeException` is still thrown.

**Q2.** The `@DependsOn("serviceA")` annotation forces bean creation ordering — Spring creates serviceA before serviceB regardless of DI declarations. Explain the difference between `@DependsOn` (ordering without injection) and a direct `@Autowired` dependency: in what scenario would `@DependsOn` cause a circular ordering conflict distinct from a circular `@Autowired` dependency? And describe a legitimate use case for `@DependsOn` that is NOT a circular dependency but still requires careful ordering (e.g., database migration tools like Flyway/Liquibase needing to run before JPA `EntityManagerFactory` is initialised).
