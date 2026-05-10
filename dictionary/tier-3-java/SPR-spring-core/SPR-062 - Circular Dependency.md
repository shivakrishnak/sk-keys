---
version: 2
layout: default
title: "Circular Dependency"
parent: "Spring Core"
grand_parent: "Technical Dictionary"
nav_order: 62
permalink: /spring/circular-dependency/
id: SPR-080
category: Spring Core
difficulty: ★★★
depends_on: Bean, Bean Lifecycle, DI, "@Autowired", BeanFactory
used_by: Spring Container, @Lazy, Constructor Injection Design
related: Bean Scope, CGLIB Proxy, BeanPostProcessor, "@Lazy"
tags:
  - spring
  - springboot
  - advanced
  - pattern
  - antipattern
---

# SPR-062 - Circular Dependency

⚡ TL;DR - A circular dependency occurs when bean A depends on bean B which depends on bean A; Spring can resolve this for setter/field injection via the "three-level cache" but throws `BeanCurrentlyInCreationException` for constructor injection - the fix is design refactoring, not workarounds.

| #383            | Category: Spring Core                                 | Difficulty: ★★★ |
| :-------------- | :---------------------------------------------------- | :-------------- |
| **Depends on:** | Bean, Bean Lifecycle, DI, @Autowired, BeanFactory     |                 |
| **Used by:**    | Spring Container, @Lazy, Constructor Injection Design |                 |
| **Related:**    | Bean Scope, CGLIB Proxy, BeanPostProcessor, @Lazy     |                 |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
Two Spring beans `UserService` and `OrderService` each inject the other. With constructor injection, Spring tries to create `UserService` → needs `OrderService` → tries to create `OrderService` → needs `UserService` → tries to create `UserService` → infinite recursion. Spring detects this at startup and throws `BeanCurrentlyInCreationException`. Without a resolution mechanism, circular dependencies - even accidental ones in large codebases - cause immediate application failure.

**THE DEEPER PROBLEM:**
Circular dependencies are usually a symptom of poor design (SRP violations, god objects, missing abstractions), but in large codebases they sometimes arise from legitimate bidirectional relationships. Spring's container must _detect_ them reliably, _resolve_ them where safe, and _fail explicitly_ where resolution would create subtle bugs.

**THE INVENTION MOMENT:**
"This is exactly why Spring's three-level singleton cache and @Lazy exist."

---

### 📘 Textbook Definition

A **circular dependency** (or dependency cycle) occurs when bean A's creation requires bean B, and bean B's creation requires bean A (or any chain A→B→C→A). Spring's `DefaultSingletonBeanRegistry` uses a **three-level cache** to break setter/field injection cycles:

1. **singletonObjects** - fully initialized singletons
2. **earlySingletonObjects** - early references (not yet post-processed)
3. **singletonFactories** - factories that produce early object references

For constructor injection, the cycle is unresolvable - the object cannot be partially created without its constructor arguments, so Spring throws `BeanCurrentlyInCreationException`. The `@Lazy` annotation can break a constructor injection cycle by injecting a CGLIB proxy instead of the real bean, deferring actual initialization until first use.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
Bean A needs Bean B to be created; Bean B needs Bean A to be created - deadlock, unless Spring can provide a "half-built" A to B.

**One analogy:**

> A circular dependency is like two builders who each refuse to start work until the other has finished. With field injection, Spring can hand builder A a "construction site placeholder" for builder B - builder A starts work with the placeholder, and later the real B replaces it. With constructor injection, there's no placeholder - you must pass the final object to the constructor, so the deadlock is unresolvable.

**One insight:**
The three-level cache exists specifically to provide "early object references" - incomplete but instantiated beans - that can be injected into a circular dependency partner before the bean finishes initialization. This is a safe resolution for field/setter injection because the injected value is the same object reference that will eventually be fully initialized. For constructor injection, no partially-constructed object exists, making this impossible.

---

### 🔩 First Principles Explanation

**CORE INVARIANTS:**

1. Constructor injection cycle → unresolvable → `BeanCurrentlyInCreationException` at startup.
2. Setter/field injection cycle → resolvable via three-level cache → both beans eventually fully initialized.
3. Three-level cache resolution is implicit for field/setter injection - no annotation required.
4. `@Lazy` on a constructor parameter → Spring injects a CGLIB proxy → real bean created on first method call.
5. The real fix for any circular dependency is design refactoring.

**WHAT GOES WRONG WITH NAIVE RESOLUTION:**
If Spring simply returns the same partially-initialized object to the circular partner, the partner might call a method on the bean _before_ the bean's `@PostConstruct` or post-processing runs. The bean's state would be incomplete. Spring's three-level cache allows post-processors (`BeanPostProcessor`) to wrap beans with proxies (e.g., AOP) before exposing them - but circular dependencies involving AOP proxies require that the early reference is already the proxy, not the raw object.

**THE TRADE-OFFS:**

**Allowing field/setter cycles:** Convenient, handles accidental cycles in legacy code. Dangerous if the early reference is accessed before the bean is fully initialized (e.g., `@PostConstruct` on a bean involved in a cycle).

**Disallowing all cycles (Spring Boot 2.6+ default):** Fails fast on all circular dependencies, forcing design fixes. Enabled by default since Spring Boot 2.6: `spring.main.allow-circular-references=false`.

---

### 🧪 Thought Experiment

**SETUP:**
`UserService` and `OrderService` are bidirectionally coupled:

```java
@Service class UserService {
    @Autowired OrderService orderService;
}
@Service class OrderService {
    @Autowired UserService userService;
}
```

**THREE-LEVEL CACHE RESOLUTION (field injection):**

```
1. Create UserService:
   - singletonFactories["userService"] = factory (produces raw UserService instance)
   - Start UserService field injection

2. Need OrderService:
   - Not in singletonObjects or earlySingletonObjects
   - Start creating OrderService

3. OrderService needs UserService:
   - Check singletonObjects: NOT found
   - Check earlySingletonObjects: NOT found
   - Check singletonFactories: FOUND → call factory → get raw UserService
   - Move raw UserService to earlySingletonObjects
   - Inject raw UserService into OrderService (partially initialized)

4. OrderService finishes initialization:
   - Move to singletonObjects["orderService"]

5. Resume UserService initialization:
   - Inject (now-complete) OrderService
   - Run @PostConstruct on UserService
   - Move to singletonObjects["userService"]
   - earlySingletonObjects["userService"] cleared
```

**CONSTRUCTOR CYCLE FAILURE:**

```
1. Create UserService(OrderService):
   - Need OrderService before UserService can exist at all
2. Create OrderService(UserService):
   - Need UserService before OrderService can exist at all
3. singletonFactories is empty (no partial object exists)
4. Deadlock detected → BeanCurrentlyInCreationException
```

**THE INSIGHT:**
Field injection can be "rescued" by pre-registering the object factory before injection starts. Constructor injection has no rescue because the object doesn't exist yet - constructors are atomic.

---

### 🧠 Mental Model / Analogy

> Think of Spring's bean creation as building with two puzzle pieces that only lock together in one specific orientation. Field injection is like two puzzle pieces where you can snap one side together first, hold the pieces loosely, snap the other side, and then press firmly. Constructor injection is like two pieces that must be fully formed before they can connect - if each piece requires the other to be complete before it can be formed, you're stuck.

- "Snap one side first" → singletonFactories providing an early reference
- "Hold loosely" → earlySingletonObjects (not yet post-processed)
- "Press firmly" → move to singletonObjects after full initialization
- "Must be fully formed before connecting" → constructor injection requirement

**Where this analogy breaks down:** The early reference in the three-level cache is the _same Java object_ - not a copy. When UserService eventually finishes initialization, the OrderService that held the early reference automatically "has" the fully initialized UserService, because it's the same reference. No update is needed.

---

### 📶 Gradual Depth - Four Levels

**Level 1 - What it is (anyone can understand):**
Bean A needs Bean B to start up, and Bean B needs Bean A to start up - a chicken-and-egg problem. Spring handles this for some cases but fails for others, and the real solution is to redesign the code.

**Level 2 - How to use it (junior developer):**
If you see `BeanCurrentlyInCreationException`, find the cycle: `A → B → A`. Fix options: (1) extract a new class for the shared concern (best), (2) make one dependency `@Lazy`, (3) switch to setter injection for one side. As of Spring Boot 2.6+, all circular dependencies fail at startup by default - you must explicitly enable them with `spring.main.allow-circular-references=true`.

**Level 3 - How it works (mid-level engineer):**
`AbstractBeanFactory.doGetBean()` calls `getSingleton()` which checks the three-level cache. Before a bean is created, its name is added to `singletonsCurrentlyInCreation`. If `getSingleton()` encounters a name already in `singletonsCurrentlyInCreation`, it returns the early reference from `singletonFactories` if present. Post-processing (AOP proxying) happens after full initialization - if a circular dependency forces early exposure, the AOP proxy must be generated at the `singletonFactories` stage, not at the post-processing stage, which is why `SmartInstantiationAwareBeanPostProcessor.getEarlyBeanReference()` exists.

**Level 4 - Why it was designed this way (senior/staff):**
The three-level cache was a pragmatic decision to support legacy codebases with accidental cycles. Spring Boot 2.6's decision to fail by default on circular dependencies reflects the modern consensus that they indicate design problems. The `@Lazy` workaround is deliberately made "inconvenient enough" to discourage its use except as a temporary fix. From an architectural standpoint, a circular dependency between `UserService` and `OrderService` suggests both are too large - the shared concern (e.g., "notification when order is placed by a user") belongs in a third class (`OrderNotificationService`) that both can depend on without creating a cycle.

---

### ⚙️ How It Works (Mechanism)

**Three-level cache internals:**

```java
// DefaultSingletonBeanRegistry
Map<String, Object> singletonObjects;           // level 1: complete
Map<String, Object> earlySingletonObjects;      // level 2: early refs
Map<String, ObjectFactory<?>> singletonFactories; // level 3: factories

// getSingleton resolution sequence:
Object getSingleton(String beanName) {
    Object bean = singletonObjects.get(beanName);  // level 1
    if (bean == null && isSingletonCurrentlyInCreation(beanName)) {
        bean = earlySingletonObjects.get(beanName);  // level 2
        if (bean == null) {
            ObjectFactory<?> factory = singletonFactories.get(beanName);  // level 3
            if (factory != null) {
                bean = factory.getObject();  // calls getEarlyBeanReference()
                earlySingletonObjects.put(beanName, bean);
                singletonFactories.remove(beanName);
            }
        }
    }
    return bean;
}
```

**AOP proxy consideration:**

```
Normal (no cycle):          Circular dependency:
create bean                 create bean (partial)
    ↓                           ↓
@PostConstruct              register in singletonFactories
    ↓                           ↓
BeanPostProcessor           another bean requests it
(AOP wrap)                      ↓
    ↓                       getEarlyBeanReference() → AOP proxy
singletonObjects            inject AOP proxy into circular partner
                                ↓
                            finish initialization
                                ↓
                            singletonObjects
```

---

### 🔄 The Complete Picture - End-to-End Flow

**DETECTION AND RESOLUTION:**

```
Context refresh started
    ↓
UserService creation begins
    ↓
singletonsCurrentlyInCreation.add("userService")
    ↓
Field injection: @Autowired OrderService
    ↓
OrderService creation begins
    ↓
singletonsCurrentlyInCreation.add("orderService")
    ↓
Field injection: @Autowired UserService
    ↓
"userService" in singletonsCurrentlyInCreation?
    YES → check singletonFactories ← YOU ARE HERE
    ↓
singletonFactories["userService"].getObject()
    → getEarlyBeanReference() → early UserService ref
    ↓
Early UserService injected into OrderService
    ↓
OrderService fully initialized → singletonObjects
    ↓
Resume: OrderService injected into UserService
    ↓
UserService fully initialized → singletonObjects
    ↓
Context refresh complete
```

**WHAT CHANGES AT SCALE:**
In Spring Boot 2.6+ with `spring.main.allow-circular-references=false` (default), all cycles fail at startup. This is intentional - catching design problems early. At scale, circular dependencies are architectural red flags: they prevent modular decomposition (you can't extract either service into a separate module without taking the other). Graph-based analysis tools (`ArchUnit`, `jdeps`, `Structurizr`) can detect dependency cycles across packages before they become Spring runtime failures.

---

### 💻 Code Example

**Example 1 - The cycle and the failure:**

```java
@Service
public class UserService {
    public UserService(OrderService orderService) { ... }
}

@Service
public class OrderService {
    public OrderService(UserService userService) { ... }
}
// → BeanCurrentlyInCreationException: constructor cycle
```

**Example 2 - @Lazy to break a constructor cycle (temporary fix):**

```java
@Service
public class UserService {
    private final OrderService orderService;

    public UserService(@Lazy OrderService orderService) {
        // orderService is a CGLIB proxy here
        // real OrderService created on first method call
        this.orderService = orderService;
    }
}
```

**Example 3 - Design fix (preferred): extract shared concern:**

```java
// BEFORE: UserService ↔ OrderService cycle
// UserService.createOrder() → OrderService
// OrderService.getUser() → UserService

// AFTER: Extract the shared concern
@Service
public class UserOrderFacade {
    private final UserRepository userRepo;
    private final OrderRepository orderRepo;
    // UserService and OrderService no longer need each other
}

@Service
public class UserService {
    private final UserRepository userRepo;
    // No dependency on OrderService!
}

@Service
public class OrderService {
    private final OrderRepository orderRepo;
    // No dependency on UserService!
}
```

**Example 4 - Application properties to explicitly enable cycles (Spring Boot 2.6+):**

```properties
# application.properties - use only as temporary migration aid
spring.main.allow-circular-references=true
```

---

### ⚖️ Comparison Table

| Injection Type      | Circular Dependency Handling        | Spring Boot 2.6+ Default | Production Recommendation |
| ------------------- | ----------------------------------- | ------------------------ | ------------------------- |
| Constructor         | Unresolvable - fails with exception | Fails                    | Fix the design            |
| Field               | Resolved via 3-level cache          | Fails (option disabled)  | Fix the design            |
| Setter              | Resolved via 3-level cache          | Fails (option disabled)  | Fix the design            |
| Constructor + @Lazy | Resolved via CGLIB proxy            | Works                    | Temporary fix only        |

**Resolution priority:** Design fix > @Lazy > setter injection > `allow-circular-references=true`

---

### ⚠️ Common Misconceptions

| Misconception                                             | Reality                                                                                                                                                                                                           |
| --------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Circular dependencies are always fine for field injection | Field injection cycles work mechanically, but the early reference is injected before @PostConstruct runs - if the early reference is used in @PostConstruct, you get NullPointerException or unexpected behavior. |
| @Lazy permanently solves the cycle                        | @Lazy creates a proxy that delays initialization, but the cycle still exists architecturally. It's a workaround, not a fix.                                                                                       |
| Spring Boot 2.6+ completely forbids circular deps         | By default it does, but `spring.main.allow-circular-references=true` re-enables them. The default change is a nudge toward better design, not a hard prohibition.                                                 |
| Circular dependency means the code is broken              | Mechanically it might work, but it always signals a design concern worth addressing - even if Spring resolves it silently.                                                                                        |

---

### 🚨 Failure Modes & Diagnosis

**BeanCurrentlyInCreationException (constructor cycle)**

**Symptom:**

```
BeanCurrentlyInCreationException: Error creating bean with name 'userService':
Requested bean is currently in creation: Is there an unresolvable circular reference?
```

**Root Cause:**
Constructor injection cycle - bean A's constructor needs bean B before bean A exists, and bean B's constructor needs bean A.

**Diagnostic Command / Tool:**

```bash
# Enable debug logging to see the full cycle
--debug flag or:
logging.level.org.springframework.beans.factory=DEBUG

# The log will show the dependency chain:
# "Creating shared instance of singleton bean 'userService'"
# "Creating shared instance of singleton bean 'orderService'"
# "Error creating bean with name 'userService'"
```

**Fix:**

```java
// Option 1: Design fix - extract shared concern (preferred)
// Option 2: @Lazy on constructor parameter
public UserService(@Lazy OrderService orderService)
// Option 3: Use setter/field injection for one side
@Service
public class UserService {
    @Autowired  // field injection - allows 3-level cache resolution
    private OrderService orderService;
}
```

**Prevention:** Enforce no dependency cycles via ArchUnit:

```java
ArchRule noCycles = SlicesRuleDefinition
    .slices().matching("com.example.(*)..").should().beFreeOfCycles();
```

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**

- `Bean Lifecycle` - understanding initialization phases clarifies why constructor cycles are unresolvable
- `DI` - circular dependency is a pathology of the DI pattern
- `@Autowired` - @Autowired is the injection mechanism that triggers the cycle

**Builds On This (learn these next):**

- `CGLIB Proxy` - @Lazy uses CGLIB to create the proxy that breaks constructor cycles
- `BeanPostProcessor` - post-processors run after the 3-level cache resolution - understanding their timing explains when early references are safe
- `@Lazy` - the injection-point annotation that defers initialization

**Alternatives / Comparisons:**

- `@Lazy` - defers dependency initialization to break cycles
- `ApplicationContext.getBean()` - manual lookup avoids injection-time cycles but is an anti-pattern

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ WHAT IT IS   │ Bean A needs B which needs A - a cycle    │
│              │ in the dependency graph                   │
├──────────────┼───────────────────────────────────────────┤
│ PROBLEM IT   │ Deadlock during bean creation; fail-fast  │
│ CAUSES       │ BeanCurrentlyInCreationException          │
├──────────────┼───────────────────────────────────────────┤
│ KEY INSIGHT  │ Field/setter cycles resolved by 3-level   │
│              │ cache; constructor cycles unresolvable.   │
│              │ Both are design problems.                 │
├──────────────┼───────────────────────────────────────────┤
│ DETECT WITH  │ Spring Boot default (2.6+) fails on all   │
│              │ cycles; ArchUnit for pre-startup detection│
├──────────────┼───────────────────────────────────────────┤
│ FIX          │ 1. Extract shared concern (design fix)    │
│              │ 2. @Lazy (workaround)                     │
│              │ 3. Setter injection (last resort)         │
├──────────────┼───────────────────────────────────────────┤
│ TRADE-OFF    │ Allowing cycles: zero refactoring work,   │
│              │ subtle init-ordering bugs; fixing: better │
│              │ design, modular codebase                  │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "A circular dependency is two beans in a  │
│              │  deadlock - fix the design, not the cycle"│
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ CGLIB Proxy → JDK Dynamic Proxy → AOP     │
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** Spring Boot 2.6+ defaults to `allow-circular-references=false`. When you upgrade an existing application from Spring Boot 2.5 to 2.6, you might find previously working circular dependencies now fail at startup. Beyond just adding `spring.main.allow-circular-references=true`, what's a systematic approach to identifying and eliminating all circular dependencies in a large codebase? What tools and techniques would you use?

**Q2.** `@Lazy` breaks a constructor cycle by injecting a CGLIB proxy instead of the real bean. The real bean is then created on the first method call through the proxy. But what happens if the "first method call" occurs inside `@PostConstruct` of the bean that holds the `@Lazy` proxy? Does the proxy correctly defer to the real bean? Are there any initialization ordering guarantees at that point?
