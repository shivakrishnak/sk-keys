---
layout: default
title: "DI (Dependency Injection)"
parent: "Spring Framework"
nav_order: 104
permalink: /spring/di-dependency-injection/
---

`#spring` `#springboot` `#internals` `#pattern` `#foundational`

⚡ TL;DR — Dependency Injection is the mechanism where a container *pushes* dependencies into an object rather than the object *pulling* (creating) them itself.

---

## 📘 Textbook Definition

Dependency Injection (DI) is a specific form of Inversion of Control in which an object's dependencies are supplied by an external entity (the injector/container) rather than created by the object itself. The three standard injection styles are **constructor injection**, **setter injection**, and **field injection**.

---

## 🟢 Simple Definition (Easy)

Instead of writing `new DatabaseService()` inside your class, you just say "I need a DatabaseService" in the constructor parameter, and Spring hands one to you automatically. Your class never creates its dependencies — it just receives them.

---

## 🔵 Simple Definition (Elaborated)

DI separates the creation of dependencies from their use. A class declares what it needs (via constructor parameters, setter methods, or annotated fields), and the Spring IoC container reads those declarations, creates the required objects, and injects them. This makes classes easier to test (inject mocks), reuse (inject any compatible implementation), and configure (swap implementations in config, not code).

---

## 🔩 First Principles Explanation

**The core tension: using vs. creating**

Every class either *uses* objects or *creates* objects. When a class does both, it becomes hard to test and reuse.

```
Class does TWO jobs:
1. Business logic (use objects)
2. Object creation (new Dependency())

Problem: Testing requires the real dependency
Problem: Changing implementation requires editing the class
```

**DI solves this by splitting the jobs:**

```
Class has ONE job: business logic only
Container has ONE job: create and inject dependencies
```

**Three injection styles:**

```
1. Constructor Injection (PREFERRED)
   ┌─────────────────────────────────┐
   │ class Service {                  │
   │   private final Repo repo;       │
   │   Service(Repo r) { repo = r; }  │  ← Container calls this
   │ }                                │
   └─────────────────────────────────┘

2. Setter Injection (OPTIONAL dependencies)
   ┌──────────────────────────────────┐
   │ class Service {                   │
   │   private Cache cache;            │
   │   @Autowired void setCache(       │  ← Container calls this
   │       Cache c) { cache = c; }     │
   │ }                                 │
   └──────────────────────────────────┘

3. Field Injection (AVOID in production)
   ┌──────────────────────────────────┐
   │ class Service {                   │
   │   @Autowired Repo repo;           │  ← Container injects via reflection
   │ }                                 │
   └──────────────────────────────────┘
```

---

## ❓ Why Does This Exist (Why Before What)

Without DI, unit testing requires spinning up real databases, HTTP servers, and external services. A simple `UserService` test ends up being an integration test because `UserService` hardwires `new JdbcUserRepository()`. DI makes each class independently testable by allowing mock implementations to be injected.

---

## 🧠 Mental Model / Analogy

> Think of DI like a **restaurant kitchen vs. a home cook**. A home cook (no DI) buys their own ingredients from the store every time they cook. A restaurant cook (with DI) just receives prepped ingredients from the prep team — the cook focuses only on cooking. The prep team (container) handles sourcing and preparing all ingredients (dependencies).

---

## ⚙️ How It Works (Mechanism)

Spring resolves injection in this order:

```
Container has BeanDefinitions for all beans
             ↓
For each bean, inspect constructors/@Autowired fields/setters
             ↓
Identify required types (e.g., UserRepository, EmailService)
             ↓
Look up matching beans in the container by type (then by name)
             ↓
Resolve @Qualifier if multiple candidates exist
             ↓
Inject: call constructor / invoke setter / set field via reflection
             ↓
Bean is fully initialized and ready
```

---

## 🔄 How It Connects (Mini-Map)

```
        [IoC Principle]
               ↓
    [DI — the mechanism] ←— implemented by
               ↓
    [@Autowired / @Inject]
       ↓         ↓         ↓
[Constructor] [Setter] [Field]
               ↓
    [BeanFactory creates dependencies]
               ↓
    [@Qualifier / @Primary for disambiguation]
```

---

## 💻 Code Example

```java
// ── Constructor Injection (BEST PRACTICE) ─────────────────────────────────
@Service
public class UserService {
    private final UserRepository userRepo;
    private final EmailService emailService;

    // Spring auto-injects both — no @Autowired needed (single constructor)
    public UserService(UserRepository userRepo, EmailService emailService) {
        this.userRepo = userRepo;
        this.emailService = emailService;
    }
}

// ── Setter Injection (for optional dependencies) ──────────────────────────
@Service
public class ReportService {
    private CacheService cache;

    @Autowired(required = false) // optional — won't fail if no bean exists
    public void setCache(CacheService cache) {
        this.cache = cache;
    }
}

// ── Field Injection (convenient but AVOID in production) ─────────────────
@Service
public class OrderService {
    @Autowired // hidden coupling — can't test without Spring context
    private PaymentService paymentService;
}

// ── Testing with DI: inject a mock ───────────────────────────────────────
@ExtendWith(MockitoExtension.class)
class UserServiceTest {
    @Mock UserRepository mockRepo;       // mock
    @Mock EmailService mockEmail;        // mock

    @InjectMocks UserService userService; // DI injects mocks into constructor

    @Test
    void testRegister() {
        when(mockRepo.save(any())).thenReturn(new User("alice"));
        userService.register("alice", "pw");
        verify(mockEmail).sendWelcome("alice");
    }
}
```

---

## ⚠️ Common Misconceptions

| ❌ Wrong Belief | ✅ Correct Reality |
|---|---|
| DI and IoC are the same thing | IoC is the principle; DI is one mechanism to achieve it |
| Field injection is fine | Field injection hides dependencies, breaks immutability, requires Spring to test |
| `@Autowired` is mandatory | Since Spring 4.3, single-constructor classes need no `@Autowired` |
| DI only works with Spring | DI is a pattern; Guice, Dagger, CDI, and plain Java all support it |
| DI adds overhead | DI wiring happens at startup; runtime performance is identical |

---

## 🔥 Pitfalls in Production

**Pitfall 1: Field injection makes testing painful**
```java
// Bad: requires full Spring context for unit tests
@Autowired private UserRepository repo;

// Good: testable with plain new
public UserService(UserRepository repo) { this.repo = repo; }
// Test: new UserService(mock(UserRepository.class))
```

**Pitfall 2: Mutable state from setter injection**
```java
// Bad: cache can be replaced at any time after construction
@Autowired public void setCache(Cache c) { this.cache = c; }

// Good: if required, use constructor injection to make it final
public UserService(Cache required, ...) { this.cache = required; }
```

**Pitfall 3: `required=true` (default) in missing beans**
```java
@Autowired SomeOptionalService optService; // if no bean → NoSuchBeanDefinitionException
// Fix: @Autowired(required = false) or use Optional<SomeOptionalService>
```

---

## 🔗 Related Keywords

- **[IoC (Inversion of Control)](./103 — IoC (Inversion of Control).md)** — the principle DI implements
- **[@Autowired](./112 — @Autowired.md)** — Spring's annotation to trigger DI
- **[@Qualifier / @Primary](./113 — @Qualifier @Primary.md)** — disambiguation when multiple beans match
- **[Bean](./107 — Bean.md)** — the objects being injected
- **[Circular Dependency](./115 — Circular Dependency.md)** — a common DI pitfall

---

## 📌 Quick Reference Card

```
+------------------------------------------------------------------+
| KEY IDEA    | Container pushes dependencies into objects          |
+------------------------------------------------------------------+
| USE WHEN    | Always — DI is the heart of Spring development      |
+------------------------------------------------------------------+
| PREFER      | Constructor injection (immutable, testable)         |
+------------------------------------------------------------------+
| AVOID       | Field injection in production code                  |
+------------------------------------------------------------------+
| ONE-LINER   | "Declare what you need; let Spring provide it"      |
+------------------------------------------------------------------+
| NEXT EXPLORE| @Autowired → @Qualifier → BeanFactory → Bean Scope  |
+------------------------------------------------------------------+
```

---

## 🧠 Think About This Before We Continue

**Q1.** Why is constructor injection preferred over field injection? Give at least three concrete reasons.

**Q2.** What happens when Spring finds two beans of the same type during injection with no `@Qualifier`? What exception is thrown?

**Q3.** How does DI relate to the Liskov Substitution Principle (LSP)? Why does DI naturally encourage coding to interfaces?

