---
layout: default
title: "Pointcut"
parent: "Spring Core"
nav_order: 37
permalink: /spring/pointcut/
id: SPR-037
category: Spring Core
difficulty: ★★☆
depends_on: AOP, Aspect, Advice, JoinPoint
used_by: "@Transactional, @Cacheable, @Async, Custom Aspects"
related: Aspect, Advice, JoinPoint, AspectJ Expression Language, "@Pointcut"
tags:
  - spring
  - springboot
  - intermediate
  - pattern
  - bestpractice
---

# SPR-037 — Pointcut

⚡ TL;DR — A Pointcut is a predicate expression that selects which method executions (JoinPoints) in the application an Advice should intercept — Spring uses AspectJ Pointcut Expression Language to define these predicates.

| #389            | Category: Spring Core                                             | Difficulty: ★★☆ |
| :-------------- | :---------------------------------------------------------------- | :-------------- |
| **Depends on:** | AOP, Aspect, Advice, JoinPoint                                    |                 |
| **Used by:**    | @Transactional, @Cacheable, @Async, Custom Aspects                |                 |
| **Related:**    | Aspect, Advice, JoinPoint, AspectJ Expression Language, @Pointcut |                 |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
You want to apply logging to all service methods, transactions to all repository methods, and security checks to all methods annotated with `@Secured`. Without a declarative predicate language, you must hardcode the target method names into the aspect, or worse, apply advice to ALL methods and check inside the advice code: `if (method.getName().startsWith("get")) return;`. This is fragile, verbose, and not reusable across aspects.

**THE INVENTION MOMENT:**
"A Pointcut is the 'targeting system' of AOP — it's how you describe which methods to intercept without listing them by name."

---

### 📘 Textbook Definition

A **Pointcut** in Spring AOP is a predicate defined using the AspectJ Pointcut Expression Language (PEL) that matches zero or more **JoinPoints** (method executions in the application). Pointcuts are declared using `@Pointcut` on a void method within an `@Aspect` class, or inline in advice annotations (`@Before("execution(...)")`, `@Around("execution(...)")`). Common designators: **`execution`** — matches method signatures. **`within`** — matches all methods in a type/package. **`@annotation`** — matches methods with a specific annotation. **`@within`** — matches all methods in a type with a specific annotation. **`args`** — matches based on argument types. **`bean`** — matches by Spring bean name. Pointcut expressions can be combined with `&&`, `||`, `!`.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
A Pointcut is a regex-like pattern for method executions — "match all public methods in the service package."

**One analogy:**

> A Pointcut is a mailing list filter. Instead of listing every person's email address who should receive the newsletter, you define a rule: "everyone in the Marketing department with a @company.com address." Any method that matches the rule gets the advice automatically. Add a new method that fits the rule — it's automatically targeted without changing the aspect.

**One insight:**
Pointcut expressions are evaluated at startup (to determine which beans to proxy) and per method call (to determine if a specific method invocation should receive advice). Spring optimizes this: if no method on a bean matches the pointcut at startup, no proxy is created. If the pointcut matches the class but not all methods, the check is per-call.

---

### 🔩 First Principles Explanation

**CORE DESIGNATORS:**

| Designator    | Matches On           | Example                                                                 |
| ------------- | -------------------- | ----------------------------------------------------------------------- |
| `execution`   | Method signature     | `execution(* com.example.service.*.*(..))`                              |
| `within`      | Type/package         | `within(com.example.service.*)`                                         |
| `@annotation` | Method annotation    | `@annotation(org.springframework.transaction.annotation.Transactional)` |
| `@within`     | Class annotation     | `@within(org.springframework.stereotype.Service)`                       |
| `args`        | Method args types    | `args(java.lang.String, ..)`                                            |
| `@args`       | Args with annotation | `@args(com.example.Validated)`                                          |
| `bean`        | Spring bean name     | `bean(userService)` or `bean(*Repository)`                              |
| `target`      | Target object type   | `target(com.example.service.UserService)`                               |
| `this`        | Proxy object type    | `this(com.example.service.UserService)`                                 |

**EXECUTION SYNTAX:**

```
execution([visibility] return-type [declaring-type.]method-name(params) [throws])

Examples:
execution(* *(..))                           // all methods
execution(public * *(..))                    // public methods only
execution(* com.example.service.*.*(..))     // all in service package
execution(* com.example..*.*(..))            // service and sub-packages (..)
execution(* *Service.*(..))                  // beans with "Service" in name
execution(* get*(..))                        // getter-named methods
execution(void save*(..))                    // void save* methods
execution(* *(String))                       // single String arg
execution(* *(.., String))                   // last arg is String
```

**THE TRADE-OFFS:**

**Broad pointcuts (`execution(* com.example..*.*(..))`):** Catch-all, low maintenance, but might accidentally match unintended methods (utility classes, DTOs). Higher proxy creation overhead at startup.

**Narrow pointcuts (`@annotation(Transactional)`):** Precise, opt-in per method, but requires adding annotations everywhere.

---

### 🧪 Thought Experiment

**SETUP:**
You want to add security checks to all REST controller endpoints, but not to service-layer methods.

**BROAD APPROACH (execution):**

```java
@Pointcut("execution(* com.example.controller.*.*(..))")
// Matches everything in the controller package
// BUT: also matches utility methods, non-endpoint methods
```

**ANNOTATION-BASED (precise):**

```java
@Pointcut("@annotation(org.springframework.web.bind.annotation.GetMapping) || "
         + "@annotation(org.springframework.web.bind.annotation.PostMapping) || "
         + "@annotation(org.springframework.web.bind.annotation.RequestMapping)")
// Matches exactly HTTP-mapped methods — nothing else
```

**COMBINED (best):**

```java
@Pointcut("within(com.example.controller..*) && "
         + "@annotation(org.springframework.web.bind.annotation.RequestMapping)")
// In controllers AND annotated — doubly precise
```

**THE INSIGHT:**
Pointcut expressions are a precision targeting system. The right expression balances specificity (don't over-apply advice) with maintainability (don't list every method by name).

---

### 🧠 Mental Model / Analogy

> A Pointcut is a SQL WHERE clause for method executions. Just as `SELECT * FROM orders WHERE amount > 1000 AND status = 'PENDING'` selects specific rows without naming them individually, a pointcut `execution(* *.save*(..)) && @annotation(Transactional)` selects specific methods without listing them. The "table" is all method executions in the application; the WHERE clause is the pointcut expression.

- "Table" → all method executions (join points)
- "WHERE clause" → pointcut expression
- "Selected rows" → matched join points that receive advice
- "Index scan optimization" → startup proxy decision (class matches) vs per-call check (method matches)

---

### 📶 Gradual Depth — Four Levels

**Level 1 — What it is (anyone can understand):**
A Pointcut is a pattern that describes "which methods" should have your cross-cutting code applied. Like a SQL query that selects rows, a pointcut selects methods.

**Level 2 — How to use it (junior developer):**
Use `@Pointcut` on a void method in your `@Aspect` class to define a reusable pointcut. Reference it by `methodName()` in advice annotations. Combine with `&&`, `||`, `!`. Use `execution` for signature-based matching. Use `@annotation` for annotation-based opt-in. Use `within` for package-based matching.

**Level 3 — How it works (mid-level engineer):**
Spring uses AspectJ's `PointcutParser` to parse expressions into `PointcutExpression` objects. At startup, `AopUtils.canApply(pointcut, targetClass)` checks class-level match (can any method match?). If yes, the bean gets a proxy. At call time, `AspectJExpressionPointcut.matches(Method, Class)` checks the specific method. Spring caches pointcut matching results per method to avoid re-evaluation on every call. The `execution` designator uses `ShadowMatch` from AspectJ — a three-valued result (YES/NO/MAYBE) where MAYBE triggers per-call rechecking.

**Level 4 — Why it was designed this way (senior/staff):**
AspectJ's Pointcut Expression Language was borrowed wholesale rather than inventing a new language. This was deliberate: AspectJ is the de facto standard for AOP expressions, with extensive documentation, tooling support, and community knowledge. Using the same language means Spring AOP knowledge is transferable to full AspectJ. The `execution` designator's wildcard semantics (`*`, `..`) follow AspectJ conventions with full type-system support — `execution(* com.example..*.*(..))` correctly matches all subtypes in `com.example` and all sub-packages. The `@annotation` designator enables the most common modern pattern: annotation-based opt-in (like `@Transactional`) which is more explicit and refactoring-friendly than package-based wildcards.

---

### ⚙️ How It Works (Mechanism)

**Pointcut evaluation — two stages:**

```
STAGE 1: Startup (class-level, per-bean)
  AnnotationAwareAspectJAutoProxyCreator:
    For each candidate bean class:
      For each registered Pointcut:
        AspectJExpressionPointcut.matches(beanClass):
          Can ANY method of this class match?
            YES → create proxy for this bean
            NO  → skip (no proxy overhead)

STAGE 2: Runtime (method-level, per-call)
  Proxy.method() called
    ↓
  Advisor chain check:
    For each Advisor:
      Pointcut.matches(method, targetClass)?
        YES → apply advice
        NO  → skip advice, proceed to next interceptor
```

**Pointcut combination:**

```java
@Aspect @Component
public class SecurityAspect {

    @Pointcut("within(com.example.controller..*)")
    public void inControllerLayer() {}

    @Pointcut("@annotation(com.example.annotation.RequiresAdmin)")
    public void requiresAdmin() {}

    @Pointcut("inControllerLayer() && requiresAdmin()")
    public void adminEndpoint() {}

    @Before("adminEndpoint()")
    public void checkAdminRole(JoinPoint jp) {
        // only runs on controller methods annotated @RequiresAdmin
    }
}
```

---

### 🔄 The Complete Picture — End-to-End Flow

**POINTCUT IN THE AOP LIFECYCLE:**

```
@Aspect bean registered with @Pointcut expressions
    ↓
ApplicationContext.refresh()
    ↓
For each bean being created:
  "Does this bean match any pointcut?" ← YOU ARE HERE (startup check)
    ↓
  YES → create proxy wrapping bean
    ↓
  Request: proxy.save(user)
    ↓
  "Does this specific method match the pointcut?" (runtime check)
    ↓
  YES → apply advice chain
  NO  → pass through to target directly
```

---

### 💻 Code Example

**Example 1 — Common pointcut patterns:**

```java
@Aspect @Component
public class PointcutLibrary {

    // All public methods in service layer
    @Pointcut("execution(public * com.example.service..*.*(..))")
    public void serviceLayer() {}

    // All Spring @Repository beans
    @Pointcut("within(@org.springframework.stereotype.Repository *)")
    public void repositoryLayer() {}

    // Annotation-based: any method with @Audited
    @Pointcut("@annotation(com.example.Audited)")
    public void auditedMethod() {}

    // Bean name pattern
    @Pointcut("bean(*Service)")
    public void serviceBean() {}

    // Methods with specific first argument type
    @Pointcut("execution(* com.example..*.*(com.example.domain.User, ..))")
    public void methodsWithUserArg() {}

    // Combined: public service methods that are audited
    @Pointcut("serviceLayer() && auditedMethod()")
    public void auditedServiceMethod() {}
}
```

**Example 2 — Reusing pointcuts from another aspect:**

```java
@Aspect @Component
public class PerformanceAspect {

    // Reference pointcut from another aspect class (fully qualified)
    @Around("com.example.aop.PointcutLibrary.serviceLayer()")
    public Object time(ProceedingJoinPoint pjp) throws Throwable {
        long start = System.nanoTime();
        Object result = pjp.proceed();
        long ms = (System.nanoTime() - start) / 1_000_000;
        if (ms > 200) log.warn("SLOW: {} took {}ms", pjp.getSignature(), ms);
        return result;
    }
}
```

**Example 3 — Binding pointcut arguments to advice parameters:**

```java
@Aspect @Component
public class UserAuditAspect {

    // Bind matched annotation instance to advice parameter
    @Before("@annotation(audited)")  // 'audited' must match parameter name
    public void audit(JoinPoint jp, Audited audited) {
        // Access annotation values:
        String action = audited.action();  // from @Audited(action = "CREATE")
        log.info("Auditing action: {} on method: {}", action, jp.getSignature());
    }
}

// Usage annotation:
@Target(ElementType.METHOD) @Retention(RetentionPolicy.RUNTIME)
public @interface Audited {
    String action();
}

// On service:
@Audited(action = "USER_SAVE")
public User save(User user) { ... }
```

---

### ⚖️ Comparison Table

| Designator    | Use Case                 | Precision | Example                                    |
| ------------- | ------------------------ | --------- | ------------------------------------------ |
| `execution`   | Signature-based          | High      | `execution(* com.example.service.*.*(..))` |
| `within`      | All methods in type/pkg  | Medium    | `within(com.example.service.*)`            |
| `@annotation` | Annotation-driven opt-in | Very High | `@annotation(Transactional)`               |
| `@within`     | Class-level annotation   | Medium    | `@within(Service)`                         |
| `bean`        | Bean name pattern        | Medium    | `bean(*Repository)`                        |
| `args`        | Argument type filter     | Variable  | `args(java.lang.String, ..)`               |

---

### ⚠️ Common Misconceptions

| Misconception                                                | Reality                                                                                                                                                                                                                      |
| ------------------------------------------------------------ | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `..*` and `.*` are equivalent                                | `.*` matches exactly one sub-level. `..*` matches all sub-packages recursively. `com.example.service.*` matches `UserService` but NOT `com.example.service.impl.UserServiceImpl`. Use `..` for recursive matching.           |
| `@annotation` matches class-level annotations                | @annotation matches METHOD-level annotations only. Use `@within` for class-level annotations.                                                                                                                                |
| Pointcut expressions are re-evaluated on every call          | Spring caches class-level and method-level pointcut matching results. The expressions are not re-parsed on every method call.                                                                                                |
| `within` and `execution` are equivalent for package matching | `within(com.example.service.*)` matches ALL methods in ALL classes in the package. `execution(* com.example.service.*.*(..))` matches public methods matching the signature pattern. They can differ for non-public methods. |

---

### 🚨 Failure Modes & Diagnosis

**Pointcut too broad — advice applied to unwanted methods**

**Symptom:**
Security aspect is running on utility methods or DTO methods, not just HTTP endpoints.

**Diagnostic Command / Tool:**

```java
// Test pointcut matching programmatically
@Autowired
AspectJExpressionPointcut pointcut;

@PostConstruct
public void testPointcut() throws Exception {
    Method saveMethod = UserService.class.getMethod("save", User.class);
    System.out.println(pointcut.matches(saveMethod, UserService.class));
}
```

**Fix:**
Combine designators for precision:

```java
// BEFORE (too broad):
@Pointcut("within(com.example..*)")

// AFTER (precise):
@Pointcut("within(com.example.service..*) && "
         + "execution(public * *(..))")
```

---

**Pointcut expression syntax error**

**Symptom:**
`IllegalArgumentException: Pointcut is not well-formed` at startup.

**Root Cause:**
Typo or syntax error in the pointcut expression string.

**Fix:**
Use the Spring AspectJ integration test or IntelliJ's AOP inspection (highlights invalid expressions). Common errors: missing `*` for return type, wrong wildcard (`*` vs `..` for packages), missing parentheses in combinations.

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**

- `AOP` — Pointcut is how AOP targets join points
- `Aspect` — contains the Pointcut definitions
- `Advice` — the code applied at matched join points

**Builds On This (learn these next):**

- `JoinPoint` — the execution context available when a Pointcut matches
- `@Transactional` — Spring's annotation-based opt-in approach uses `@annotation` pointcuts internally

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ WHAT IT IS   │ Predicate expression selecting which      │
│              │ method executions receive Advice          │
├──────────────┼───────────────────────────────────────────┤
│ KEY SYNTAX   │ execution(* com.example.service.*.*(..))  │
│              │ @annotation(Transactional)                │
│              │ within(com.example.service.*)             │
│              │ Combine: expr1() && expr2()               │
├──────────────┼───────────────────────────────────────────┤
│ KEY INSIGHT  │ `*` = one level; `..` = any depth.        │
│              │ @annotation = method-level annotation     │
│              │ @within = class-level annotation          │
├──────────────┼───────────────────────────────────────────┤
│ BEST PRACTICE│ Define @Pointcut named methods in a       │
│              │ dedicated class; reuse across aspects     │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "The WHERE clause that selects which      │
│              │  method executions get the Advice."       │
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** Spring evaluates pointcut expressions at two stages: class-level at startup (to decide which beans to proxy) and method-level at runtime (to decide whether to apply advice). The class-level check determines proxy creation, which is irreversible. What happens when a pointcut matches a class but only 1 of 50 methods? Does all 50 methods get proxy overhead, or only the matching one? What's the performance implication?

**Q2.** `@annotation(Transactional)` is a pointcut that matches methods with `@Transactional`. But `@Transactional` can be placed on a class (applies to all methods) or inherited from an interface. Does Spring's `@annotation` pointcut match interface-declared annotations? Class-level annotations? Does the pointcut engine understand annotation inheritance semantics?
