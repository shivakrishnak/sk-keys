---
layout: default
title: "@Autowired"
parent: "Spring Core"
nav_order: 380
permalink: /spring/autowired/
number: "0380"
category: Spring Core
difficulty: ★★☆
depends_on: DI, BeanFactory, Bean, BeanPostProcessor
used_by: All Spring Beans, Spring MVC Controllers, Spring Services
related: "@Qualifier", "@Primary", "@Inject", Constructor Injection
tags:
  - spring
  - springboot
  - intermediate
  - pattern
  - bestpractice
---

# 380 — @Autowired

⚡ TL;DR — @Autowired tells Spring to resolve and inject a dependency by type automatically, eliminating manual bean lookup and wiring code.

| #380            | Category: Spring Core                                     | Difficulty: ★★☆ |
| :-------------- | :-------------------------------------------------------- | :-------------- |
| **Depends on:** | DI, BeanFactory, Bean, BeanPostProcessor                  |                 |
| **Used by:**    | All Spring Beans, Spring MVC Controllers, Spring Services |                 |
| **Related:**    | @Qualifier, @Primary, @Inject, Constructor Injection      |                 |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
Before `@Autowired` (pre-Spring 2.5), every dependency had to be declared in XML configuration: `<property name="userRepository" ref="userRepositoryBean"/>`. A service with 5 dependencies required 5 XML entries, plus the bean definition itself. A medium application had thousands of XML lines just for wiring. Refactoring a dependency's name meant updating both the Java class and the XML. Adding a dependency meant editing both code and config. The configuration file became a maintenance burden separate from and out-of-sync with the code.

**THE BREAKING POINT:**
XML-based wiring doesn't fail at compile time — it fails at startup when Spring can't find a bean reference. Typos in bean names cause runtime failures. Renaming a class requires updating XML files that are often in different modules. The XML configuration duplicates information already expressed by the code's constructor signatures and interfaces, violating DRY. Large teams struggled with XML merge conflicts.

**THE INVENTION MOMENT:**
"This is exactly why @Autowired was created."

---

### 📘 Textbook Definition

**@Autowired** is a Spring annotation (`org.springframework.beans.factory.annotation.Autowired`) that marks a constructor, field, or setter method for dependency injection by the Spring IoC container. When placed on a constructor (recommended), Spring resolves all constructor parameters by type from the application context. When placed on a field or setter, `AutowiredAnnotationBeanPostProcessor` resolves and injects the dependency after bean construction. By default, `@Autowired` requires the dependency to exist (`required = true`); setting `required = false` makes the dependency optional. Since Spring 4.3, a single-constructor class does not require `@Autowired` — it is implicit.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
@Autowired means "Spring: find the right object and inject it here."

**One analogy:**

> @Autowired is like ordering room service and checking "automatic substitution allowed." The hotel (Spring) finds the closest match for what you ordered — if you asked for "a vegetable," it sends broccoli (the registered bean of that type). You don't specify the brand; you specify the category, and the hotel fills the order from whatever it has.

**One insight:**
`@Autowired` resolves dependencies by _type_, not by name. This is its superpower (no spelling errors, rename-safe) and its weakness (ambiguous when two beans of the same type exist). The `@Qualifier` annotation adds name-based disambiguation on top of type matching.

---

### 🔩 First Principles Explanation

**CORE INVARIANTS:**

1. Resolution is by type first. If exactly one bean matches the required type, it's injected.
2. If zero beans match and `required = true` (default), startup fails with `NoSuchBeanDefinitionException`.
3. If multiple beans match, Spring attempts disambiguation: `@Primary` > `@Qualifier` > field/parameter name matching > fail.

**DERIVED DESIGN:**
The annotation approach moves wiring information into the code, co-locating declaration with usage. The `AutowiredAnnotationBeanPostProcessor` processes the annotation reflectively: it finds annotated elements, resolves dependencies from the context, and injects them via `ReflectionUtils.makeAccessible()` for fields or direct constructor invocation.

**Resolution algorithm (in order):**

```
1. Find all beans of the required type
2. If exactly 1: inject it
3. If 0: throw (or skip if required=false)
4. If >1: check for @Primary bean → inject that
5. If no @Primary: match by @Qualifier
6. If no @Qualifier: match by field/param name vs bean name
7. If still >1: throw NoUniqueBeanDefinitionException
```

**THE TRADE-OFFS:**

**Gain:** No XML wiring boilerplate. Rename-safe. IDE-navigable (Ctrl+Click takes you to the bean). Fail-fast (missing beans detected at startup).

**Cost:** "Magic" injection — new developers see `@Autowired UserRepository repo` and wonder where `repo` comes from. Multiple beans of the same type require explicit disambiguation. The application is coupled to Spring's `@Autowired` annotation (use JSR-330's `@Inject` to reduce coupling).

---

### 🧪 Thought Experiment

**SETUP:**
You have `OrderService` needing `PaymentProcessor` and `InventoryService`. The old approach: XML wiring. The new approach: `@Autowired`.

**WHAT HAPPENS WITHOUT @Autowired (XML approach):**

```xml
<bean id="orderService" class="com.example.OrderService">
    <property name="paymentProcessor" ref="stripeProcessor"/>
    <property name="inventoryService" ref="inventoryServiceImpl"/>
</bean>
```

Adding a third dependency → edit XML in a different file. Rename `stripeProcessor` to `stripePaymentProcessor` → XML breaks at runtime, not compile time. 50 services × 3 deps = 150 XML entries to maintain.

**WHAT HAPPENS WITH @Autowired:**

```java
@Service
public class OrderService {
    @Autowired
    public OrderService(PaymentProcessor payment,
                        InventoryService inventory) {
        this.payment = payment;
        this.inventory = inventory;
    }
}
```

Adding a third dependency → add constructor parameter. Rename a bean's class → compiler detects broken references. Zero separate configuration file. The constructor signature IS the wiring specification.

**THE INSIGHT:**
By making the code the configuration, `@Autowired` eliminates an entire class of maintenance overhead — the dual-maintenance of code plus separate XML. The code is now the single source of truth for its own dependencies.

---

### 🧠 Mental Model / Analogy

> `@Autowired` is like putting a label on an empty box saying "FILL WITH TOOLS." The warehouse worker (Spring) reads the label (type information), finds the right tools (beans of that type), and fills the box. If there's only one hammer in the warehouse, that's what goes in. If there are two hammers (two beans of the same type), you need to add a more specific label (@Qualifier: "the red-handled hammer").

- "Empty box with label" → `@Autowired` field/parameter
- "FILL WITH TOOLS" → required type (`UserRepository.class`)
- "Warehouse worker" → `AutowiredAnnotationBeanPostProcessor`
- "Right tools" → beans matching the type
- "More specific label" → `@Qualifier("jdbcUserRepository")`

**Where this analogy breaks down:** Unlike a warehouse worker who might just pick any matching item, Spring has a specific disambiguation algorithm — `@Primary` > `@Qualifier` > name matching — and fails explicitly when disambiguation is impossible, rather than making an arbitrary choice.

---

### 📶 Gradual Depth — Four Levels

**Level 1 — What it is (anyone can understand):**
@Autowired tells Spring "I need one of these objects — please find it and put it here." Spring looks through all the objects it knows about, finds one of the right type, and delivers it.

**Level 2 — How to use it (junior developer):**
Prefer constructor injection: add `@Autowired` (or nothing since Spring 4.3 for a single constructor) to your constructor. Declare each dependency as a constructor parameter. For optional dependencies, use `@Autowired(required = false)` or wrap in `Optional<T>`. Avoid field injection — it makes testing hard and hides dependencies.

**Level 3 — How it works (mid-level engineer):**
`AutowiredAnnotationBeanPostProcessor.postProcessBeforeInitialization()` calls `findAutowiringMetadata()` to inspect the bean class's constructors, fields, and methods for `@Autowired` annotations. For constructor injection, the injection happens in `doCreateBean()` before `postProcessBeforeInitialization`. For field/setter injection, `AutowiredFieldElement.inject()` uses `ReflectionUtils.makeAccessible(field)` and `field.set(bean, resolvedValue)`.

**Level 4 — Why it was designed this way (senior/staff):**
The annotation approach was a deliberate simplification over XML, but the Spring team initially preferred XML because annotations couple application code to the Spring library. `@Inject` (JSR-330) was introduced as a standard alternative to `@Autowired`, processable by any compliant DI framework. Spring 4.3's implicit single-constructor injection eliminated the last reason to put `@Autowired` on constructors, moving toward pure POJO style. The design evolution tracks toward progressively less Spring annotation coupling — with Spring 6 and GraalVM, the goal is code that requires no Spring annotations at all (all meta-configuration moved to `@Bean` methods in `@Configuration` classes).

---

### ⚙️ How It Works (Mechanism)

**Processing sequence:**

```
Bean class: UserService
  Constructor(UserRepository repo) ← @Autowired (or implicit)
  @Autowired UserEventPublisher events  ← field injection

During doCreateBean():
  1. Determine injection points:
     AutowiredAnnotationBeanPostProcessor.determineCandidateConstructors()
     → finds @Autowired constructor or single constructor

  2. Resolve constructor args:
     ConstructorResolver.autowireConstructor()
     → for each param type: findAutowireCandidates()
     → applies disambiguation algorithm
     → resolves each arg to a concrete bean

  3. Construct bean:
     UserService instance = constructor.newInstance(resolvedArgs)

  4. postProcessBeforeInitialization():
     AutowiredFieldElement.inject():
       → resolvedValue = beanFactory.resolveDependency(UserEventPublisher)
       → makeAccessible(field)
       → field.set(beanInstance, resolvedValue)
```

**Disambiguation algorithm:**

```
Required type: UserRepository
Candidates found: [jdbcUserRepository, jpaUserRepository]
    ↓
Check @Primary: is any candidate @Primary?
    ↓ (none)
Check @Qualifier at injection point:
    @Autowired @Qualifier("jdbcUserRepository") UserRepository repo
    ↓ (match found)
Inject: jdbcUserRepository
    ↓
No @Qualifier?
    Match field/param name: "repo" vs bean names?
    ↓ (no match)
Throw: NoUniqueBeanDefinitionException
```

---

### 🔄 The Complete Picture — End-to-End Flow

**NORMAL FLOW:**

```
Bean component scan → UserService detected
    ↓
BeanDefinition registered for UserService
    ↓
BeanDefinition registered for JpaUserRepository
    ↓
Context refresh → UserService being created
    ↓
AutowiredAnnotationBeanPostProcessor activated
    ↓
Resolves UserRepository from context (1 match)
   ← YOU ARE HERE (@Autowired resolves the dependency)
    ↓
JpaUserRepository injected into UserService constructor
    ↓
UserService stored in singleton cache (with repo injected)
    ↓
All beans that @Autowire UserService get the same instance
```

**FAILURE PATH:**

```
@Autowired UserRepository repo
Two candidates: jdbcUserRepository, jpaUserRepository
No @Primary, no @Qualifier
    ↓
NoUniqueBeanDefinitionException:
"expected single matching bean but found 2"
    ↓
Context refresh fails → application exits
```

**WHAT CHANGES AT SCALE:**
`@Autowired` resolution is a startup-time operation. At runtime, the resolved values are cached in the singleton. No per-request overhead. The startup-time cost is proportional to the number of injection points, not request volume. In very large applications (10,000+ injection points), the reflection-based scanning by `AutowiredAnnotationBeanPostProcessor` can add 2–5 seconds to startup — GraalVM native compilation moves this to build time.

---

### 💻 Code Example

**Example 1 — Constructor injection (recommended):**

```java
@Service
public class OrderService {

    private final OrderRepository orderRepo;
    private final PaymentService paymentService;

    // @Autowired optional since Spring 4.3 (single constructor)
    public OrderService(
            OrderRepository orderRepo,
            PaymentService paymentService) {
        this.orderRepo = Objects.requireNonNull(orderRepo);
        this.paymentService = Objects.requireNonNull(paymentService);
    }
}
```

**Example 2 — Optional dependency:**

```java
@Service
public class MetricsService {

    private final Optional<MeterRegistry> registry;

    @Autowired
    public MetricsService(
            @Autowired(required = false) MeterRegistry registry) {
        // registry may be null if Micrometer not on classpath
        this.registry = Optional.ofNullable(registry);
    }

    public void recordEvent(String name) {
        registry.ifPresent(r -> r.counter(name).increment());
    }
}
```

**Example 3 — Disambiguating with @Qualifier:**

```java
public interface NotificationChannel {
    void send(String message, String recipient);
}

@Component("email")
public class EmailChannel implements NotificationChannel { ... }

@Component("sms")
public class SmsChannel implements NotificationChannel { ... }

@Service
public class AlertService {

    private final NotificationChannel primary;
    private final NotificationChannel secondary;

    @Autowired
    public AlertService(
            @Qualifier("email") NotificationChannel primary,
            @Qualifier("sms") NotificationChannel secondary) {
        this.primary = primary;
        this.secondary = secondary;
    }
}
```

**Example 4 — Collection injection (all beans of a type):**

```java
@Service
public class HealthCheckService {

    // Spring injects ALL beans implementing HealthIndicator
    private final List<HealthIndicator> indicators;

    @Autowired
    public HealthCheckService(List<HealthIndicator> indicators) {
        this.indicators = indicators;
    }

    public HealthStatus checkAll() {
        return indicators.stream()
            .map(HealthIndicator::check)
            .reduce(HealthStatus.UP, HealthStatus::combine);
    }
}
```

---

### ⚖️ Comparison Table

| Injection Style            | Testability           | Immutability   | Required       | Coupling        |
| -------------------------- | --------------------- | -------------- | -------------- | --------------- |
| **Constructor @Autowired** | Excellent (plain new) | Yes (final)    | Yes by default | Low             |
| Field @Autowired           | Poor (needs context)  | No             | Yes by default | Medium          |
| Setter @Autowired          | Good                  | No             | Optional       | Low             |
| @Inject (JSR-330)          | Same as @Autowired    | Same as target | Yes            | None (standard) |

**How to choose:** Constructor injection for all mandatory dependencies. Setter injection for optional, reconfigurable dependencies. Avoid field injection in production code. Use `@Inject` if Spring framework coupling is a concern.

---

### ⚠️ Common Misconceptions

| Misconception                            | Reality                                                                                                                                                    |
| ---------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------- |
| @Autowired is always required            | required=false or Optional<T> parameter make it optional. A missing optional dependency results in null or empty Optional, not a startup failure.          |
| @Autowired injects by bean name          | @Autowired resolves by type first. Name-based resolution only occurs as a fallback when type resolution is ambiguous.                                      |
| You need @Autowired on every constructor | Since Spring 4.3, a single constructor is implicitly autowired. @Autowired is only needed for multiple constructors (to indicate which Spring should use). |
| @Autowired and @Inject are identical     | Functionally similar. @Inject doesn't have a required=false option. @Autowired is Spring-specific; @Inject is JSR-330 (portable).                          |
| Field @Autowired is fine in tests        | Field injection requires Spring context to inject. Unit tests without Spring context get null fields. Constructor injection works with plain new.          |

---

### 🚨 Failure Modes & Diagnosis

**NoUniqueBeanDefinitionException**

**Symptom:**
`NoUniqueBeanDefinitionException: expected single matching bean but found 2: emailChannel, smsChannel`

**Root Cause:**
Two beans satisfy the same `@Autowired` type. Spring's disambiguation failed.

**Diagnostic Command / Tool:**

```bash
# List all beans of a given type
curl -s http://localhost:8080/actuator/beans | \
  jq '.contexts[].beans |
      to_entries[] |
      select(.value.type | test("NotificationChannel")) |
      .key'
```

**Fix:**

```java
// Option 1: @Primary on the default implementation
@Primary
@Component("email")
public class EmailChannel implements NotificationChannel { ... }

// Option 2: @Qualifier at injection point
@Autowired
@Qualifier("sms")
private NotificationChannel fallbackChannel;
```

**Prevention:** Design interfaces with a single canonical production implementation. Use `@Primary` as the default; `@Qualifier` only for intentional alternates.

---

**NullPointerException with field injection in unit tests**

**Symptom:**
`NullPointerException` in a service method during unit tests. The `@Autowired` field that the method uses is null.

**Root Cause:**
Field injection requires `AutowiredAnnotationBeanPostProcessor` to inject values. In a plain unit test (`new UserService()`), no Spring context runs — fields are never injected.

**Diagnostic Command / Tool:**

```java
// Detect field injection at code review
// Any @Autowired on a non-constructor element in a non-test class
// is a candidate for this bug
```

**Fix:**

```java
// BAD: field injection — null in unit tests
@Service
public class UserService {
    @Autowired
    private UserRepository repo;  // null without Spring context
}

// GOOD: constructor injection — testable without Spring
@Service
public class UserService {
    private final UserRepository repo;

    public UserService(UserRepository repo) {
        this.repo = repo;
    }
}

// Unit test — no Spring context needed
class UserServiceTest {
    @Test
    void test() {
        UserRepository mock = mock(UserRepository.class);
        UserService svc = new UserService(mock);  // plain new!
        // ...
    }
}
```

**Prevention:** Enforce constructor injection via a code review rule or ArchUnit check: no `@Autowired` on non-constructor elements in production code.

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**

- `DI (Dependency Injection)` — @Autowired is the annotation that enables DI in Spring
- `Bean` — @Autowired resolves beans; must understand what a bean is
- `BeanPostProcessor` — AutowiredAnnotationBeanPostProcessor implements @Autowired processing

**Builds On This (learn these next):**

- `@Qualifier / @Primary` — the disambiguation tools when @Autowired finds multiple candidates
- `@Configuration / @Bean` — how to create beans that @Autowired can inject
- `Circular Dependency` — what happens when @Autowired creates a dependency cycle

**Alternatives / Comparisons:**

- `@Inject (JSR-330)` — the standard Java alternative to @Autowired; no required=false option
- `@Resource (JSR-250)` — name-based injection alternative; resolves by bean name, not type

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ WHAT IT IS   │ Annotation that triggers type-based       │
│              │ dependency resolution and injection       │
├──────────────┼───────────────────────────────────────────┤
│ PROBLEM IT   │ XML wiring boilerplate; manual bean       │
│ SOLVES       │ lookup; configuration-code duplication    │
├──────────────┼───────────────────────────────────────────┤
│ KEY INSIGHT  │ Resolves by TYPE, not name. Multiple      │
│              │ beans of same type → use @Qualifier or    │
│              │ @Primary to disambiguate                  │
├──────────────┼───────────────────────────────────────────┤
│ USE WHEN     │ Injecting any Spring-managed dependency   │
│              │ (almost always on constructors)           │
├──────────────┼───────────────────────────────────────────┤
│ AVOID WHEN   │ Avoid on fields/setters for mandatory     │
│              │ dependencies; use constructors instead    │
├──────────────┼───────────────────────────────────────────┤
│ TRADE-OFF    │ No-boilerplate wiring vs "magic" that     │
│              │ hides dependency origin from newcomers    │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "Find the right bean and put it here —   │
│              │  I'll tell you the type, not the name."  │
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ @Qualifier → @Primary → Circular Dep      │
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** `@Autowired` resolves by type, and `@Qualifier` adds name-based disambiguation. But what if you have 10 implementations of an interface and want to inject all 10 into a `List<MyInterface>`? Spring supports this — it injects all beans of the type. But what controls the order of beans in that list? And if order matters (e.g., a chain of security filters), what mechanism guarantees the correct order?

**Q2.** Spring 4.3 made `@Autowired` implicit on single-constructor classes. But some teams still add it explicitly for clarity. Beyond readability preferences, is there any runtime scenario where explicitly adding `@Autowired` to a single constructor changes Spring's behavior compared to not adding it?
