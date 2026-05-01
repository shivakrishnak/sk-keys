---
layout: default
title: "Pointcut"
parent: "Spring Core"
nav_order: 389
permalink: /spring/pointcut/
number: "389"
category: Spring Core
difficulty: ★★☆
depends_on: "Aspect, Advice, AOP (Aspect-Oriented Programming), JoinPoint"
used_by: "Advice, JoinPoint, Weaving, @Transactional"
tags: #intermediate, #spring, #architecture, #pattern
---

# 389 — Pointcut

`#intermediate` `#spring` `#architecture` `#pattern`

⚡ TL;DR — A **Pointcut** is an expression that selects which join points (method executions) an Aspect's Advice should be applied to — the "where" in AOP. Spring uses AspectJ expression syntax: `execution(...)`, `within(...)`, `@annotation(...)`, `@within(...)`, and others.

| #389            | Category: Spring Core                                        | Difficulty: ★★☆ |
| :-------------- | :----------------------------------------------------------- | :-------------- |
| **Depends on:** | Aspect, Advice, AOP (Aspect-Oriented Programming), JoinPoint |                 |
| **Used by:**    | Advice, JoinPoint, Weaving, @Transactional                   |                 |

---

### 📘 Textbook Definition

In Spring AOP, a **Pointcut** is a predicate that matches join points — it answers the question "which method executions should this advice apply to?" Pointcuts are expressed using AspectJ's Pointcut Expression Language (PEL) and can be defined as `@Pointcut`-annotated methods in an `@Aspect` class (reusable, named definitions) or inline in advice annotations (anonymous). Spring AOP supports the following Pointcut designators: `execution(pattern)` — matches method execution by signature; `within(type)` — matches all methods in a type or package; `this(type)` — matches when the proxy is of the given type; `target(type)` — matches when the target object is of the given type; `args(types)` — matches when method arguments match the types; `@annotation(annotation)` — matches methods annotated with the given annotation; `@within(annotation)` — matches all methods in a class annotated with the given annotation; `@args(annotation)` — matches when arguments are annotated. Pointcuts can be combined with `&&` (AND), `||` (OR), and `!` (NOT) operators. The `execution` designator is the most commonly used.

---

### 🟢 Simple Definition (Easy)

A Pointcut is the filter that tells Spring which methods to intercept. It is an expression like "all public methods in the service package" or "all methods annotated with @Transactional."

---

### 🔵 Simple Definition (Elaborated)

An Aspect knows what to do (Advice), but it needs to know where to apply it. Pointcuts specify the "where" using expressions. The expression `execution(* com.example.service.*.*(..))` means "any method in any class in the service package, any return type, any arguments." The expression `@annotation(org.springframework.transaction.annotation.Transactional)` means "any method annotated with `@Transactional`." Pointcuts can be composed: `execution(* *.*(..)) && @annotation(Transactional)` means "any method that is also annotated with `@Transactional`." Spring evaluates pointcut expressions at startup to build an efficient match cache, so the per-call overhead of checking is minimal.

---

### 🔩 First Principles Explanation

**The `execution` designator — the primary pointcut:**

```
Pattern: execution([visibility] returnType [declaringType].methodName(paramTypes) [throws])

execution(* *(..))
  *     = any return type
  *     = any method in any class
  (..)  = any number of any parameters

execution(public * com.example.service.*.*(..))
  public     = visibility: public methods only
  *          = any return type
  com.example.service.*.*(..): classes in service package, any method, any args

execution(String com.example.service.UserService.findBy*(String))
  String     = return type must be String
  findBy*    = method name starts with "findBy"
  (String)   = exactly one String parameter

execution(* *(..) throws Exception)
  throws Exception = method declares throws Exception or subclass
```

**All Pointcut designators with examples:**

```java
// 1. execution — match by method signature
@Pointcut("execution(public * com.example.service.*.*(..))")
void publicServiceMethods() {}

// 2. within — match all methods in a type or package
@Pointcut("within(com.example.service..*)")
void withinServicePackage() {} // "..*" = service package and subpackages

// 3. @annotation — match methods annotated with given annotation
@Pointcut("@annotation(org.springframework.transaction.annotation.Transactional)")
void transactionalMethod() {}

// 4. @within — match all methods in a class annotated with given annotation
@Pointcut("@within(org.springframework.stereotype.Service)")
void inServiceAnnotatedClass() {}

// 5. target — match when target object is instance of type
@Pointcut("target(com.example.service.OrderService)")
void targetOrderService() {}

// 6. args — match when args match types
@Pointcut("args(java.lang.String, ..)")
void firstArgString() {} // first arg is String, followed by any args

// 7. @args — match when argument types have given annotation
@Pointcut("@args(com.example.Validated)")
void validatedArgument() {} // first arg's type has @Validated

// 8. bean — Spring-specific: match by bean name pattern
@Pointcut("bean(order*)")
void orderBeans() {} // beans whose name starts with "order"

// COMPOSITION
@Pointcut("publicServiceMethods() && !withinServicePackage()")
void externalServiceCalls() {}  // public service methods NOT in service package

@Pointcut("transactionalMethod() || inServiceAnnotatedClass()")
void transactionalOrService() {} // OR composition
```

**The `execution` pattern in detail with wildcards:**

```
Wildcard  Meaning
*         Any single type/name/package element (not including dots)
..        Any sequence (including nothing): in type = any package depth,
          in args = any number of any type parameters
+         Subtype: OrderService+ = OrderService and all its subclasses/implementations

Examples:
  com.example.service.*         → classes directly in service package
  com.example.service..*       → classes in service package and ALL subpackages
  OrderService+                → OrderService and all types that extend/implement it
  set*                         → methods starting with "set" (setters)
  *(OrderRequest, ..)          → methods whose first arg is OrderRequest
```

---

### ❓ Why Does This Exist (Why Before What)

WITHOUT Pointcuts:

What breaks without it:

1. AOP Aspects would have to be applied manually to each method — no automatic matching.
2. No way to apply Advice to dynamically discovered classes (e.g., all `@Service` beans).
3. `@Transactional` processing would require enumerating every class method explicitly.
4. Cross-cutting concerns cannot be expressed as "all methods that match this pattern."

WITH Pointcuts:
→ One expression covers all matching methods — add new service methods without changing any AOP configuration.
→ Pattern-based matching means Aspects self-apply as the codebase grows.
→ Composed pointcuts express complex rules cleanly (`serviceLayer() && !readOnly()`).
→ `@annotation` pointcuts let annotations become AOP activation markers — the standard Spring pattern.

---

### 🧠 Mental Model / Analogy

> Think of a Pointcut as a filter rule for email. You set up a rule: "apply the 'Important' label to all emails from @company.com that have 'urgent' in the subject line (`@annotation(Urgent)` + `within(@company.com domain)`)." The filter applies automatically to every matching email — you don't manually label each one. The Advice is the action ("apply label"); the Pointcut is the filter condition. New emails automatically get labelled if they match — no rule updates needed.

"Filter rule for email" = the Pointcut expression
"All emails from @company.com with 'urgent' in subject" = the predicate (like `execution` + `@annotation`)
"Apply 'Important' label" = the Advice
"Automatic labelling of new matching emails" = the Aspect applies automatically to new beans/methods

---

### ⚙️ How It Works (Mechanism)

**How Spring evaluates Pointcuts at startup vs runtime:**

```
At Startup (per-class evaluation):
  AnnotationAwareAspectJAutoProxyCreator.postProcessAfterInitialization(bean):
    For each registered Aspect's Pointcut:
      → Compile pointcut expression (AspectJ's PointcutParser)
      → Check if the pointcut COULD match any method on this bean's class
        (ClassFilter.matches(targetClass))
      → If YES: add Advisor to the proxy's MethodInterceptor chain
      → If NO:  skip this Advisor

At Runtime (per-method evaluation):
  When a proxied method is called:
    → Check MethodMatcher.matches(method, targetClass) for each Advisor
    → If matches: add Advice to the invocation chain for this call
    → Execute the chain

Performance optimisation:
  Spring caches method→advisors mappings after first evaluation
  For most Pointcuts, the per-call overhead is just a HashMap lookup
```

**Named vs anonymous Pointcuts:**

```java
// Named (reusable) — preferred
@Pointcut("execution(* com.example.service.*.*(..))")
private void serviceLayer() {}

@Before("serviceLayer()")  // reuses the named pointcut
void logEntry(JoinPoint jp) { ... }

@Around("serviceLayer()")  // reuses again
Object measureTime(ProceedingJoinPoint pjp) throws Throwable { ... }

// Anonymous (inline) — convenient for one-off use
@Before("execution(* com.example.service.*.*(..))")
void logEntry(JoinPoint jp) { ... }

// Cross-aspect reuse: reference another @Aspect's named pointcut
@Before("com.example.aspects.CommonPointcuts.serviceLayer()")
void externalPointcutUsage(JoinPoint jp) { ... }
```

---

### 🔄 How It Connects (Mini-Map)

```
Aspect (the container class)
        │
        ├──── Pointcut  ◄──── (you are here)
        │     (expression: which methods to intercept)
        │     │
        │     ▼
        │     Evaluated against all beans at startup
        │     by AnnotationAwareAspectJAutoProxyCreator
        │
        └──── Advice
              (what to run at matched join points)
              │
              ▼
              JoinPoint (the specific matched method execution context)
              │
              ▼
              Weaving (proxy creation for matched beans)
```

---

### 💻 Code Example

**Common library of reusable Pointcuts:**

```java
@Aspect // naming convention: Pointcuts class, not a full Aspect
public class ApplicationPointcuts {

    // All public methods in any @Service-annotated bean
    @Pointcut("@within(org.springframework.stereotype.Service)")
    public void serviceLayer() {}

    // All public methods in any @RestController bean
    @Pointcut("@within(org.springframework.web.bind.annotation.RestController)")
    public void webLayer() {}

    // All methods annotated with @Transactional
    @Pointcut("@annotation(org.springframework.transaction.annotation.Transactional)")
    public void transactional() {}

    // All repository methods (interface or class)
    @Pointcut("within(org.springframework.data.repository.Repository+)")
    public void dataAccessLayer() {}

    // All methods EXCEPT those in package "internal"
    @Pointcut("!within(com.example.internal..*)")
    public void notInternal() {}

    // Public methods in service layer, not internal
    @Pointcut("serviceLayer() && notInternal()")
    public void externalServiceMethods() {}
}

// Usage in another Aspect:
@Aspect
@Component
public class AuditAspect {
    @Before("com.example.aspects.ApplicationPointcuts.externalServiceMethods()")
    public void audit(JoinPoint jp) {
        auditService.record(jp.getSignature().toShortString(), jp.getArgs());
    }
}
```

---

### ⚠️ Common Misconceptions

| Misconception                                                                                            | Reality                                                                                                                                                                                                                                   |
| -------------------------------------------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `execution(* com.example.*.*(..))` matches subpackages                                                   | The single `*` in the package expression matches ONE package level. `com.example.*` matches classes directly in `com.example` only. Use `com.example..*` (two dots) to match all subpackages recursively                                  |
| `within(com.example.service.OrderService)` and `target(com.example.service.OrderService)` are equivalent | `within` matches based on the compile-time type of the class being executed. `target` matches based on the runtime type of the target object. For proxied beans, `target` matches the real bean type; `within` may match the proxy type   |
| Named `@Pointcut` methods can have any return type                                                       | Named `@Pointcut` methods must return `void`. Any other return type causes an error. The method body is ignored — only the annotation value (the expression) matters                                                                      |
| `@annotation(Transactional)` requires the fully qualified class name                                     | The fully qualified name is required unless the annotation class is imported in the `@Aspect` class. Best practice: use fully qualified names to avoid ambiguity: `@annotation(org.springframework.transaction.annotation.Transactional)` |

---

### 🔥 Pitfalls in Production

**Single asterisk in package pattern — subpackages not matched, silent miss**

```java
// INTENDED: match all service classes including subpackages
// ACTUAL: matches ONLY classes directly in com.example.service
@Pointcut("execution(* com.example.service.*.*(..))") // BUG: single *
void serviceLayer() {}

// New classes added in com.example.service.order.* are NOT matched
// No error — the Aspect just silently does not apply

// CORRECT: use double dots for recursive subpackage matching
@Pointcut("execution(* com.example.service..*.*(..))") // double dots before *
void serviceLayer() {}
```

---

**@annotation Pointcut on an interface method — concrete class not matched**

```java
public interface UserService {
    @Audited // annotation on interface method
    void createUser(User user);
}

@Service
class UserServiceImpl implements UserService {
    public void createUser(User user) { ... } // no @Audited here
}

// Spring AOP's @annotation pointcut looks at the TARGET class method,
// not the interface method. @Audited on the interface is NOT seen.
// The Aspect does NOT apply to UserServiceImpl.createUser()

// FIX: place @Audited on the IMPLEMENTATION method, not the interface
@Service
class UserServiceImpl implements UserService {
    @Audited // annotation on concrete method — now matched
    public void createUser(User user) { ... }
}
```

---

### 🔗 Related Keywords

- `Aspect` — the class that declares `@Pointcut` methods and references them in Advice
- `Advice` — what code to run; Pointcut tells Spring where to run it
- `JoinPoint` — a specific matched method execution instance that passed the Pointcut filter
- `AOP (Aspect-Oriented Programming)` — the paradigm defining Pointcut's role
- `Weaving` — the result of applying Pointcut-matched Advice to target beans via proxy

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ DESIGNATORS  │ execution(*), within(*), @annotation(*), │
│              │ @within(*), target(*), args(*), bean(*)  │
├──────────────┼───────────────────────────────────────────┤
│ WILDCARDS    │ * = one element, .. = any depth/args,     │
│              │ + = subtype                              │
├──────────────┼───────────────────────────────────────────┤
│ COMBINE      │ && (AND), || (OR), ! (NOT)               │
├──────────────┼───────────────────────────────────────────┤
│ SUBPKG TRAP  │ *.* = direct package only               │
│              │ ..*.* = recursive subpackages            │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "Pointcut = the email filter rule:        │
│              │  defines which messages get the label,    │
│              │  not what the label is."                 │
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** You write a Pointcut: `@annotation(com.example.Cacheable)`. Your `@Cacheable` annotation is placed on an interface method, but the concrete implementation does not have it. Spring AOP's `@annotation` Pointcut looks at the proxied method on the target class — which does NOT have `@Cacheable`. Explain how you would fix this using `@within` instead of `@annotation` if the annotation is on the class level, and how you could write a Pointcut that matches methods where EITHER the method itself OR its interface declaration has the annotation — noting that Spring AOP's standard expression language cannot directly look at interface annotations.

**Q2.** `execution` Pointcuts are evaluated at startup to determine which beans need proxying. A Pointcut like `execution(* com.example..*.*(..))` could match every method in the application. Describe how Spring's `ClassFilter` and `MethodMatcher` optimise this: does Spring create a proxy for EVERY bean if the Pointcut expression could potentially match everything? How does the two-phase evaluation (`ClassFilter` first, then `MethodMatcher`) reduce proxy creation? And what is the startup performance impact of having many broad Pointcuts vs narrow Pointcuts?
