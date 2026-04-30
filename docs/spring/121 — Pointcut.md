---
layout: default
title: "Pointcut"
parent: "Spring & Spring Boot"
nav_order: 121
permalink: /spring/pointcut/
number: "121"
category: Spring & Spring Boot
difficulty: ★★☆
depends_on: "Aspect, AOP, JoinPoint, Spring AOP"
used_by: "Advice targeting, Spring AOP filtering, @Transactional, Custom aspects"
tags: #java, #spring, #intermediate, #pattern
---

# 121 — Pointcut

`#java` `#spring` `#intermediate` `#pattern`

⚡ TL;DR — An AspectJ expression that selects the specific join points (method executions) where an aspect's advice should be applied.

| #121 | Category: Spring & Spring Boot | Difficulty: ★★☆ |
|:---|:---|:---|
| **Depends on:** | Aspect, AOP, JoinPoint, Spring AOP | |
| **Used by:** | Advice targeting, Spring AOP filtering, @Transactional, Custom aspects | |

---

### 📘 Textbook Definition

A **Pointcut** is a predicate that matches join points. In Spring AOP, pointcuts are expressed using the AspectJ Pointcut Expression Language and declared via `@Pointcut`-annotated methods or inline in advice annotations. Spring AOP supports a subset of AspectJ designators: `execution` (method signature matching), `within` (type matching), `@annotation` (annotation presence), `@within` (type annotation), `args` (argument type matching), `@args` (argument annotation), `bean` (Spring bean name) and `&&`, `||`, `!` logical operators. When a pointcut matches a bean's method, `AbstractAutoProxyCreator` creates a proxy for that bean and adds the matched advice to its interceptor chain.

---

### 🟢 Simple Definition (Easy)

A pointcut is the "WHERE" in AOP. It's an expression that says "apply this advice to all methods matching this pattern" — like a filter that selects which methods get intercepted.

---

### 🔵 Simple Definition (Elaborated)

A pointcut expression is similar to a SQL `WHERE` clause applied to method executions. Instead of filtering rows, it filters method calls — by class name, method name, parameter types, return type, annotations present, or bean name. Spring evaluates pointcut expressions at startup when building the proxy's interceptor chain, and checks them per method invocation at runtime. Complex pointcuts can be composed with `&&`, `||`, and `!` — a named `@Pointcut` method acts as a reusable alias. `@Transactional` works with an internal pointcut that matches "any method decorated with @Transactional."

---

### 🔩 First Principles Explanation

**Pointcut expression anatomy — `execution` designator:**

```
execution( modifiers? return-type declaring-type? name( params ) throws? )

execution(* com.example.service.*.*(..))

  *                   → any return type
  com.example.service  → package
  .*                   → any class in that package
  .*                   → any method name
  (..)                 → any parameters

More specific:
execution(public Order com.example.OrderService.place(..))
  public              → access modifier
  Order               → return type
  com.example.OrderService → declaring class
  .place              → method name
  (..)                → any parameters
```

**Five most commonly used designators:**

```
┌───────────────────────────────────────────────────────┐
│  execution(* com.example.service.*.*(..))             │
│  → all methods in any service class in package        │
│                                                       │
│  @annotation(org.springframework.transaction.         │
│              annotation.Transactional)                │
│  → any method annotated with @Transactional           │
│                                                       │
│  within(com.example.service..*)                       │
│  → any join point in service package (incl sub-pkgs)  │
│                                                       │
│  args(java.lang.String, ..)                           │
│  → any method where first arg is String               │
│                                                       │
│  bean(*Service)                                       │
│  → any method on beans whose name ends with "Service" │
└───────────────────────────────────────────────────────┘
```

---

### ❓ Why Does This Exist (Why Before What)

**WITHOUT pointcut expressions:**

```
Without a pointcut DSL:

  Option A: List all target classes explicitly
    advice.addTarget(OrderService.class);
    advice.addTarget(PaymentService.class);
    advice.addTarget(UserService.class);
    // Add new service → must update this list
    // Rename class → silent miss

  Option B: Marker interface on every class
    implements Transactable {...}
    // Every class must explicitly opt in
    // Forget on one class → silent miss

  Neither approach:
    → Can't target by annotation presence
    → Can't target by package hierarchy
    → Maintenance burden with every refactor
```

**WITH pointcut expressions:**

```
→ execution(* com.example.service.*.*(..))
  → automatically includes ALL new services in that package
→ @annotation(Transactional)
  → zero configuration: add annotation → advice applied
→ Refactor-safe: move class within package → still matched
→ Composed: security AND service layer AND NOT health:
  pointcut = "@annotation(Secured) && within(..service..)"
           + " && !execution(* *.health*(..))"
```

---

### 🧠 Mental Model / Analogy

> A pointcut is like a **search filter on your email inbox**. "Show me all emails from domain @example.com, subject contains 'urgent', received this week." Email rules act on matching emails (advice fires on matched join points). You don't have to list each email address explicitly — the pattern matches all current and future messages that fit. Adding a new sender in that domain automatically matches the existing rule.

"Search filter expression" = pointcut expression
"Emails matching the filter" = method invocations matching pointcut
"Email rule action" = advice that fires on match
"New sender automatically matched" = new service method auto-matched
"Multiple filter criteria (AND/OR)" = pointcut composition with && / ||

---

### ⚙️ How It Works (Mechanism)

**Named pointcut methods and composition:**

```java
@Aspect
@Component
public class LayeredAspect {
  // Named pointcuts — reusable references (body always empty)
  @Pointcut("within(com.example.service..*)")
  private void serviceLayer() {}

  @Pointcut("within(com.example.repository..*)")
  private void repositoryLayer() {}

  @Pointcut("@annotation(org.springframework"
           + ".transaction.annotation.Transactional)")
  private void transactional() {}

  // Exclude: any method whose name starts with "get"
  @Pointcut("execution(* *.get*(..))")
  private void readOnlyMethods() {}

  // Composed: service layer, transactional, and NOT read-only
  @Pointcut("serviceLayer() && transactional()"
           + " && !readOnlyMethods()")
  public void mutatingServiceOps() {}

  // Advice using composed pointcut
  @Before("mutatingServiceOps()")
  void auditMutation(JoinPoint jp) {
    audit.log(jp.getSignature().toShortString());
  }
}
```

**`bean` designator — Spring-specific:**

```java
// Only available in Spring AOP (not pure AspectJ)
@Pointcut("bean(*Repository)")
private void allRepositories() {}
// Matches: userRepository, orderRepository, etc.
// Does NOT match: userService, orderService

@Around("allRepositories()")
public Object wrapRepoCall(ProceedingJoinPoint pjp)
    throws Throwable {
  // All repository calls automatically retried on failure
}
```

**Performance — pointcut caching:**

Spring caches pointcut match results per method. If `execution(* com.example.*.*(..))` matches `OrderService.place()`, the result is cached — the expression is NOT re-evaluated on every call. Expensive pointcuts (many `||` alternatives) only impact startup, not runtime.

---

### 🔄 How It Connects (Mini-Map)

```
@Aspect class defines:
        ↓
  POINTCUT (121)  ← you are here
  (AspectJ expression selecting join points)
        ↓
  Evaluated at startup:
  Which beans need proxying? (static match)
        ↓
  Evaluated at runtime:
  Does this specific method call match? (dynamic check)
        ↓
  If match: Advice (120) fires
  If no match: method invoked directly (no chain)
        ↓
  Used by all Spring AOP features:
  @Transactional → @annotation(Transactional) pointcut
  @Cacheable → @annotation(Cacheable) pointcut
  @Secured → @annotation(Secured) pointcut
```

---

### 💻 Code Example

**Example 1 — Common pointcut patterns in production:**

```java
@Aspect @Component
public class CommonPointcuts {
  // All public methods in service layer
  @Pointcut("execution(public * com.example.service..*.*(..))")
  public void allServiceMethods() {}

  // Any method on class annotated @RestController
  @Pointcut("@within(org.springframework.web.bind"
           + ".annotation.RestController)")
  public void restControllerMethods() {}

  // Methods taking a Long ID as first parameter
  @Pointcut("args(id, ..) && execution(* *.findById*(..))")
  public void findByIdMethods(Long id) {}

  // Methods annotated with a custom @RateLimit annotation
  @Pointcut("@annotation(com.example.RateLimit)")
  public void rateLimitedMethods() {}
}

// Advice using shared pointcut library:
@Aspect @Component
class RateLimitAspect {
  @Around("com.example.CommonPointcuts.rateLimitedMethods()")
  Object enforceRateLimit(ProceedingJoinPoint pjp)
      throws Throwable {
    rateLimiter.acquire();
    return pjp.proceed();
  }
}
```

**Example 2 — Pointcut with bound parameter:**

```java
// Binding argument from pointcut to advice parameter
@Aspect @Component
class ValidationAspect {
  @Before("execution(* com.example.service.*.save*(..))"
        + " && args(entity, ..)")
  public void validateBeforeSave(JoinPoint jp, Object entity) {
    // entity is bound from the first argument in args(entity,..)
    if (entity instanceof Validatable v) {
      v.validate(); // throws if invalid → method prevented
    }
  }
}
```

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| Pointcut expressions are evaluated on every method call at runtime | Spring caches static pointcut matches at proxy creation time (per bean + per method). Dynamic checks (args, target) are re-evaluated per call, but static execution() matches are cached |
| A broad pointcut like execution(* *.*(..)) advises every method in the app | Spring AOP only creates proxies for Spring-managed beans. Methods on non-bean objects or on the beans themselves via self-calls are not affected |
| @Pointcut method body must contain logic | @Pointcut method body is always empty — it is a signature-only declaration that serves as a named alias for the expression in the annotation |
| execution() and within() are equivalent | execution() matches method signatures (return type, class, name, params). within() matches any method inside a type or package — broader and type-oriented |

---

### 🔥 Pitfalls in Production

**1. Overly broad pointcut degrading startup performance**

```java
// BAD: matches every method in every class in the app
@Pointcut("execution(* *(..))")
void everythingEverywhere() {}

@Before("everythingEverywhere()")
void logAll(JoinPoint jp) {
  log.trace("...");
}
// Causes Spring to create CGLIB proxies for ALL beans
// → 3× normal startup time, 2× memory at startup
// → Even non-service utility beans get proxied

// GOOD: scope to your own packages + necessary layers
@Pointcut("execution(* com.example.service..*.*(..))"
        + " || execution(* com.example.api..*.*(..))")
void applicationLayer() {}
```

**2. Missing `..` in package wildcard — no sub-packages matched**

```java
// BAD: only matches classes directly in .service, not sub-pkgs
@Pointcut("within(com.example.service.*)")
// Misses: com.example.service.order.OrderService

// GOOD: .. in within() or execution() includes sub-packages
@Pointcut("within(com.example.service..*)")
//                                       ^^ double dot
```

---

### 🔗 Related Keywords

- `Aspect` — contains the @Pointcut declarations and the advice that uses them
- `Advice` — the code that executes at join points selected by the pointcut
- `JoinPoint` — the runtime execution context at a matched pointcut
- `Spring AOP` — evaluates pointcuts to determine which beans need proxying
- `@annotation` — the pointcut designator used by @Transactional, @Cacheable internals
- `execution()` — the most commonly used designator: matches by method signature

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ KEY IDEA     │ AspectJ expression selecting which method │
│              │ calls trigger advice — the "WHERE" of AOP │
├──────────────┼───────────────────────────────────────────┤
│ USE WHEN     │ Scoped to package: within(com.example..*) │
│              │ By annotation: @annotation(MyAnnotation)  │
├──────────────┼───────────────────────────────────────────┤
│ AVOID WHEN   │ Overly broad execution(*.*(*)) — proxies  │
│              │ every bean → slow startup, high memory    │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "A pointcut is the WHERE clause —         │
│              │  it filters method calls like SQL rows."  │
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ JoinPoint (122) → @Transactional (127) →  │
│              │ Spring AOP internals                      │
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** Spring AOP uses a two-phase pointcut check: a static check during proxy creation (does any advice's pointcut match this bean's methods?) and an optional dynamic check per invocation (do the runtime argument values match `args()` or `target()`?). Explain what a "static" vs "dynamic" pointcut is in Spring's `Pointcut` interface (`ClassFilter` + `MethodMatcher`), describe the performance implications of a dynamic `MethodMatcher.isRuntime()` returning true, and explain why `execution()` expressions are always static but `args()` with specific types forces a dynamic runtime check.

**Q2.** The `bean()` designator is Spring AOP-specific and cannot be used in standalone AspectJ. Explain why the `bean()` designator fundamentally cannot be compiled into AspectJ bytecode at compile time — what information about bean names is unavailable at compile time — and describe the scenario where using `bean()` in a pointcut causes a class to escape proxying in a Spring Boot test using `@WebMvcTest` (which only loads a slice of the application context and may not register the full set of beans).

