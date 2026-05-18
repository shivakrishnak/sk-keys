---
version: 2
layout: default
title: "DI (Dependency Injection)"
parent: "Spring Core"
grand_parent: "Technical Mastery"
nav_order: 7
permalink: /technical-mastery/spring/di-dependency-injection/
id: SPR-048
category: Spring Core
difficulty: ★☆☆
depends_on: IoC, Object-Oriented Programming, Interfaces
used_by: ApplicationContext, Bean, Spring Core, Testing with Mocks
related: IoC, Constructor Injection, Field Injection, Setter Injection
tags:
  - spring
  - springboot
  - pattern
  - foundational
  - architecture
---

⚡ TL;DR - Dependency Injection is the technique of passing an object's collaborators from outside rather than letting the object create them itself.

| #372            | Category: Spring Core                                         | Difficulty: ★☆☆ |
| :-------------- | :------------------------------------------------------------ | :-------------- |
| **Depends on:** | IoC, Object-Oriented Programming, Interfaces                  |                 |
| **Used by:**    | ApplicationContext, Bean, Spring Core, Testing with Mocks     |                 |
| **Related:**    | IoC, Constructor Injection, Field Injection, Setter Injection |                 |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
A `NotificationService` sends emails and SMS. Without DI, it creates its own `EmailClient` and `SmsClient` inside its constructor or methods. Testing it requires a real SMTP server and a live SMS gateway. Adding a push notification channel means editing `NotificationService` itself. Switching from `SendGrid` to `Mailgun` requires modifying the service class - a class that should only know about _sending notifications_, not about _which vendor to use_.

**THE BREAKING POINT:**
Business logic becomes entangled with infrastructure instantiation. Every change to a dependency (a new constructor parameter, a changed API key source) ripples into every class that creates that dependency. Unit tests are impossible without the real infrastructure. Mocking requires bytecode manipulation (PowerMock) rather than clean interface substitution. The codebase grows harder to test and to change with every added dependency.

**THE INVENTION MOMENT:**
"This is exactly why Dependency Injection was created."

---

### 📘 Textbook Definition

**Dependency Injection** (DI) is an implementation of Inversion of Control in which an object receives its dependencies - the other objects it needs to do its work - from an external source rather than creating them itself. The external source is typically an IoC container (Spring's `ApplicationContext`), but can also be a test setup or a manual factory. DI comes in three forms: _constructor injection_ (dependencies passed via constructor parameters), _setter injection_ (passed via setter methods), and _field injection_ (injected directly into fields via reflection). Spring recommends constructor injection for mandatory dependencies.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
DI means you receive your tools ready-made instead of building them yourself.

**One analogy:**

> A chef doesn't grow vegetables, raise animals, or mine salt. The restaurant's supply chain delivers those ingredients to the kitchen. The chef focuses entirely on cooking. DI is the supply chain: it delivers the ingredients (dependencies) to the class (chef) so it can focus on its job.

**One insight:**
DI separates two responsibilities that are always mixed in naive code: _"I need a database connection"_ (use) and _"I'll create a database connection"_ (construction). Separating these two concerns means you can swap any dependency without touching the class that uses it - which is exactly what makes testing and refactoring possible.

---

### 🔩 First Principles Explanation

**CORE INVARIANTS:**

1. A class should declare its dependencies as constructor parameters or interface properties - not create them with `new`.
2. The injector (container or test setup) is the only place where concrete implementations are selected.
3. The class under construction should be oblivious to whether its dependencies are real, cached, mocked, or proxied.

**DERIVED DESIGN:**
Given these invariants, any correct DI system needs:

- A way for classes to _declare_ what they need (annotations, constructor parameters)
- A registry of available implementations
- A wiring mechanism that resolves declarations to implementations

Spring satisfies all three with `@Autowired` declarations, the component registry, and `AutowiredAnnotationBeanPostProcessor`.

**THE TRADE-OFFS:**

**Gain:** Complete decoupling between users of a dependency and creators of a dependency. Enables effortless swapping of implementations (JDBC → JPA, real → mock).

**Cost:** Object graphs become implicit - tracing "where does this `repo` come from?" requires navigating the Spring context, not just reading the constructor. IDE support helps, but new team members face a steeper learning curve. Misconfiguration (wrong profile, missing bean) is only caught at runtime.

---

### 🧪 Thought Experiment

**SETUP:**
`ReportService` produces monthly reports using `DataWarehouse` for data and `PdfRenderer` for output. Your task: test that `ReportService` generates the correct PDF when the warehouse returns empty data.

**WHAT HAPPENS WITHOUT DI:**

1. `ReportService` constructor: `this.dw = new RedshiftWarehouse(credentials)`.
2. The test calls `new ReportService()`.
3. `RedshiftWarehouse` constructor tries to open a TCP connection to AWS Redshift.
4. In a developer's local machine, the connection times out after 30 seconds.
5. The test fails before `ReportService`'s logic even runs.
6. You've tested a network connection, not report generation logic.

**WHAT HAPPENS WITH DI:**

1. `ReportService` constructor: `ReportService(DataWarehouse dw, PdfRenderer renderer)`.
2. In the test: `new ReportService(new InMemoryWarehouse(emptyData), new FakePdfRenderer())`.
3. `InMemoryWarehouse.query()` instantly returns empty data.
4. `ReportService`'s branching logic for empty data runs immediately.
5. `FakePdfRenderer` captures the generated PDF bytes.
6. The test asserts the correct "No data for this month" PDF was generated - in milliseconds.

**THE INSIGHT:**
DI turns every class into a pure function of its inputs. A class that declares its dependencies can be tested in isolation with predictable, controllable substitutes - removing the environment from the equation entirely.

---

### 🧠 Mental Model / Analogy

> A surgeon doesn't manufacture their own scalpels. A nurse prepares the instrument tray and hands instruments to the surgeon on demand. The surgeon declares "scalpel" - and receives a scalpel. DI is the nurse: preparing and delivering exactly what's needed, exactly when it's needed.

- "Surgeon's declaration 'scalpel'" → `@Autowired` or constructor parameter
- "Nurse preparing the tray" → Spring IoC container resolving the bean
- "Scalpel on the tray" → configured bean in the application context
- "Different scalpel for a training session" → mock bean in a test context

**Where this analogy breaks down:** Unlike a nurse who hands instruments sequentially, Spring resolves all dependencies at once before the object is used - and in a specific order determined by the dependency graph, not by runtime requests.

---

### 📶 Gradual Depth - Four Levels

**Level 1 - What it is (anyone can understand):**
Instead of building your own tools, you receive them pre-built. Your class says "I need a database" and Spring hands you one - ready to use. You never write `new Database()`.

**Level 2 - How to use it (junior developer):**
Declare dependencies in the constructor and annotate with `@Autowired` (optional since Spring 4.3 for single constructors). Annotate your dependency classes with `@Component`, `@Service`, or `@Repository`. Spring scans the classpath, finds everything, and wires it together before `main()` returns. In tests, use `@MockBean` to substitute fakes.

**Level 3 - How it works (mid-level engineer):**
Spring uses `AutowiredAnnotationBeanPostProcessor`, which processes beans after instantiation. For constructor injection, Spring uses the constructor with the `@Autowired` annotation (or the sole constructor) to resolve and inject dependencies at bean creation time. Field injection uses `ReflectionUtils.makeAccessible()` to inject directly after construction. The resolution is type-based by default; `@Qualifier` is used for disambiguation. All resolution happens against the singleton cache plus prototype factories.

**Level 4 - Why it was designed this way (senior/staff):**
Constructor injection was chosen as Spring's official recommendation because it makes dependencies visible (they appear in the constructor signature), enforces immutability (`final` fields), and prevents circular dependencies at design time. Field injection was popular historically because it reduced boilerplate, but it hides dependencies, makes classes harder to instantiate outside a container, and breaks with `final`. The recommendation changed from field injection to constructor injection as the community recognized that convenience at authoring time creates cost at testing and maintenance time.

---

### ⚙️ How It Works (Mechanism)

Spring supports three injection types. Each is processed differently:

**Constructor Injection (recommended):**

```
Bean B needs to be created
    ↓
Spring inspects constructor parameters
    ↓
For each parameter type, resolve from context
    ↓
Construct B with resolved dependencies
    ↓
No proxy needed - full instance immediately
```

**Field Injection (legacy):**

```
Bean B constructed (zero-arg or no-@Autowired constructor)
    ↓
AutowiredAnnotationBeanPostProcessor runs
    ↓
Finds @Autowired fields via reflection
    ↓
For each field: resolve type from context
    ↓
ReflectionUtils.makeAccessible(field)
    ↓
field.set(bean, resolvedDependency)
```

**Setter Injection (rare):**

```
Bean B constructed
    ↓
PostProcessor finds @Autowired setter methods
    ↓
Calls setter(resolvedDependency)
    ↓
Good for optional dependencies (can set a default)
```

**Resolution Algorithm:**

```
Type matching:
  1. Find all beans of the required type
  2. If exactly one: inject it
  3. If zero: throw NoSuchBeanDefinitionException
  4. If multiple: check for @Primary
  5. If no @Primary: check @Qualifier at injection point
  6. If no @Qualifier: try matching by field/param name
  7. If still ambiguous: throw
    NoUniqueBeanDefinitionException
```

---

### 🔄 The Complete Picture - End-to-End Flow

**NORMAL FLOW:**

```
@SpringBootApplication detected
    ↓
Component scan finds @Service, @Repository, @Component
    ↓
BeanDefinitions registered in context
    ↓
Context.refresh() instantiates singletons
    ↓
DI resolution: constructor params resolved recursively
   ← YOU ARE HERE (Spring injects dependencies)
    ↓
Fully-wired beans placed in singleton cache
    ↓
Application ready; all beans available
```

**FAILURE PATH:**

```
DI resolution fails (missing bean / ambiguous type)
    ↓
UnsatisfiedDependencyException thrown
    ↓
Context refresh aborted
    ↓
Application exits with non-zero status
    ↓
Deployment pipeline fails (fail-fast)
```

**WHAT CHANGES AT SCALE:**
DI resolution is entirely a startup-time operation - at scale, there is zero per-request cost from DI itself. What scales poorly is the _number of beans_ increasing startup time. Netflix reported Spring Boot startup times of 30+ seconds with 2,000+ beans; lazy initialization (`spring.main.lazy-initialization=true`) and GraalVM native compilation address this at the cost of delayed failure detection.

---

### 💻 Code Example

**Example 1 - Field injection (legacy, avoid):**

```java
@Service
public class UserService {

    @Autowired  // BAD: hidden dependency, not testable without Spring
    private UserRepository repo;

    // No constructor - can't instantiate outside Spring context
    // Can't inject mock without @SpringBootTest overhead
}
```

**Example 2 - Constructor injection (recommended):**

```java
@Service
public class UserService {

    private final UserRepository repo;  // immutable

    // Spring detects single constructor - @Autowired optional
    public UserService(UserRepository repo) {
        this.repo = Objects.requireNonNull(repo);
    }
}

// In tests - no Spring context needed:
class UserServiceTest {
    @Test
    void findsUserByEmail() {
        UserRepository mock = Mockito.mock(UserRepository.class);
        when(mock.findByEmail("alice@example.com"))
            .thenReturn(Optional.of(new User("Alice")));

        UserService service = new UserService(mock);  // plain new!
        Optional<User> result =
            service.findByEmail("alice@example.com");
        assertTrue(result.isPresent());
    }
}
```

**Example 3 - Multiple implementations with @Qualifier:**

```java
public interface NotificationSender {
    void send(String message, String recipient);
}

@Component("emailSender")
public class EmailNotificationSender implements
    NotificationSender { ... }

@Component("smsSender")
public class SmsNotificationSender implements
    NotificationSender { ... }

@Service
public class AlertService {
    private final NotificationSender primary;
    private final NotificationSender fallback;

    public AlertService(
        @Qualifier("emailSender") NotificationSender primary,
        @Qualifier("smsSender") NotificationSender fallback
    ) {
        this.primary = primary;
        this.fallback = fallback;
    }
}
```

**Example 4 - Optional dependencies:**

```java
@Service
public class MetricsService {
    private final MeterRegistry registry;

    // Optional: use default no-op registry if none is configured
    public MetricsService(
        @Autowired(required = false) MeterRegistry registry
    ) {
        this.registry = registry != null
            ? registry
            : new SimpleMeterRegistry();
    }
}
```

---

### ⚖️ Comparison Table

| Injection Type  | Testability          | Immutability | Circular Dep Support  | Visibility       |
| --------------- | -------------------- | ------------ | --------------------- | ---------------- |
| **Constructor** | Excellent            | Yes (final)  | No (fails at startup) | High (signature) |
| Field           | Poor (needs context) | No           | Yes (via proxy cache) | Low (hidden)     |
| Setter          | Good                 | No           | Yes                   | Medium           |

**How to choose:** Always use constructor injection for mandatory dependencies. Use setter injection for truly optional dependencies. Avoid field injection in new code - it couples your class to Spring's container.

---

### ⚠️ Common Misconceptions

| Misconception                                        | Reality                                                                                                                                             |
| ---------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------- |
| DI and IoC are synonyms                              | IoC is the principle (invert control of object creation). DI is one implementation of IoC.                                                          |
| @Autowired is required for injection                 | Since Spring 4.3, a class with a single constructor is auto-wired without @Autowired.                                                               |
| Field injection is fine for production code          | Field injection makes classes impossible to instantiate without Spring, breaks final fields, and hides dependencies.                                |
| Constructor injection prevents circular dependencies | It prevents them at runtime (throws exception). Field injection allows circular deps via proxies - but circular deps are a design smell regardless. |
| DI has runtime overhead per request                  | DI resolution happens once at startup. Per-request, Spring simply returns the cached singleton - there is no injection overhead.                    |

---

### 🚨 Failure Modes & Diagnosis

**NoUniqueBeanDefinitionException**

**Symptom:**
`NoUniqueBeanDefinitionException: expected single matching bean but found 2: emailSender, smsSender`

**Root Cause:**
Two beans implement the same interface. Spring can't select one without guidance.

**Diagnostic Command / Tool:**

```bash
# Check which beans satisfy an interface via Actuator
curl -s http://localhost:8080/actuator/beans | \
  jq '.contexts | to_entries[].value.beans |
      to_entries[] |
      select(.value.type | contains("NotificationSender")) |
      {(.key): .value.type}'
```

**Fix:**

```java
// Option A: mark the default
@Primary
@Component("emailSender")
public class EmailNotificationSender implements NotificationSender { }

// Option B: qualify at injection point
@Autowired
@Qualifier("smsSender")
private NotificationSender fallbackSender;
```

**Prevention:** Design one canonical implementation per interface for production. Use `@Primary` as the default and `@Qualifier` only when intentionally injecting a specific alternative.

---

**NullPointerException in field-injected beans used in constructors**

**Symptom:**
`NullPointerException` when another bean's constructor calls a method on a field-injected dependency.

**Root Cause:**
Field injection happens _after_ construction. If a constructor calls `this.repo.save(...)`, `repo` is still null at that point.

**Diagnostic Command / Tool:**

```bash
# Enable Spring debug to see bean construction order
logging.level.org.springframework.beans=DEBUG
# Look for "Creating instance" before "Injecting autowired element"
```

**Fix:**

```java
// BAD: field injected, used in constructor
@Service
public class StartupLoader {
    @Autowired
    private DataLoader loader;  // null during construction

    public StartupLoader() {
        loader.load();  // NullPointerException!
    }
}

// GOOD: constructor injection
@Service
public class StartupLoader {
    private final DataLoader loader;

    public StartupLoader(DataLoader loader) {
        this.loader = loader;  // fully injected before body runs
        loader.load();  // safe
    }
}
```

**Prevention:** Use constructor injection. Dependencies are guaranteed to be non-null when the constructor body executes.

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**

- `IoC (Inversion of Control)` - DI is the primary implementation of IoC; understanding the principle clarifies why DI exists
- `Interfaces (Java)` - DI's power comes from injecting interface types, enabling polymorphic substitution
- `Bean` - the objects Spring manages and injects

**Builds On This (learn these next):**

- `ApplicationContext` - the container that implements DI at application scale
- `BeanFactory` - the low-level factory that resolves and injects beans
- `BeanPostProcessor` - the mechanism that processes @Autowired annotations after bean creation
- `@Qualifier / @Primary` - tools for resolving ambiguous DI situations

**Alternatives / Comparisons:**

- `Service Locator` - another IoC pattern where code _pulls_ dependencies from a registry; DI _pushes_ them in
- `Manual Construction` - the alternative to DI; creates tight coupling
- `@Inject (JSR-330)` - the standard Java annotation alternative to Spring's @Autowired

---

### 📌 Quick Reference Card

```
┌─────────────────────────────────────────────────────────┐
│ WHAT IT IS   │ Passing dependencies in from outside     │
│              │ instead of constructing them inside      │
├──────────────┼──────────────────────────────────────────┤
│ PROBLEM IT   │ Classes tightly coupled to their         │
│ SOLVES       │ dependencies' concrete implementations   │
├──────────────┼──────────────────────────────────────────┤
│ KEY INSIGHT  │ The class that USES a dependency should  │
│              │ never be the one that CREATES it         │
├──────────────┼──────────────────────────────────────────┤
│ USE WHEN     │ Any class with collaborators (almost     │
│              │ always - it's the default Spring style)  │
├──────────────┼──────────────────────────────────────────┤
│ AVOID WHEN   │ Value objects, DTOs, pure data classes   │
│              │ that have no behavioral dependencies     │
├──────────────┼──────────────────────────────────────────┤
│ TRADE-OFF    │ Testability + loose coupling vs          │
│              │ implicit object graph (hard to trace)    │
├──────────────┼──────────────────────────────────────────┤
│ ONE-LINER    │ "Don't build your tools; receive them."  │
├──────────────┼──────────────────────────────────────────┤
│ NEXT EXPLORE │ IoC → ApplicationContext → BeanFactory   │
└─────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** Constructor injection prevents circular dependencies - if A depends on B and B depends on A, Spring throws an exception at startup. But some real systems have legitimate mutual dependencies (e.g., two services that call each other under different conditions). What patterns exist to break these cycles while keeping constructor injection, and what are their trade-offs?

**Q2.** DI makes classes testable by allowing mock injection. But a test that injects 10 mocks and asserts behavior against all 10 is arguably harder to maintain than the original coupled code. At what point does heavy DI use become a design smell in itself, and what does that smell tell you about the class's responsibilities?
