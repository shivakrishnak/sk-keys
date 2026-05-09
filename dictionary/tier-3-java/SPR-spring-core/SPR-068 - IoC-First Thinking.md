---
id: SPR-068
title: IoC-First Thinking
category: Spring Core
tier: tier-3-java
folder: SPR-spring-core
difficulty: ★★★
depends_on: SPR-001, SPR-019, SPR-020, SPR-064
used_by:
related: SPR-067, SPR-069, SPR-070
tags:
  - spring
  - java
  - advanced
  - mental-model
  - bestpractice
  - architecture
status: complete
version: 1
layout: default
parent: "Spring Core"
grand_parent: "Technical Dictionary"
nav_order: 68
permalink: /spr/ioc-first-thinking/
---

# SPR-068 - IoC-First Thinking

⚡ TL;DR - IoC-first design means structuring code so dependencies are declared, not acquired; objects express what they need and the container decides how to fulfil it.

| Field          | Value                                                                                                                                                                                        |
| -------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Depends on** | [[SPR-001 - What Is Spring - History and Philosophy]], [[SPR-019 - IoC (Inversion of Control)]], [[SPR-020 - DI (Dependency Injection)]], [[SPR-064 - Spring Framework Internals Deep Dive]] |
| **Used by**    | -                                                                                                                                                                                            |
| **Related**    | [[SPR-067 - Spring Specification and Extension Points]], [[SPR-069 - Spring Configuration Trade-off Framing]], [[SPR-070 - Framework Selection Mental Model]]                                |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**

A `PaymentService` creates its own `PaymentGateway`: `this.gateway = new StripeGateway(config)`. A `ReportService` creates its own `Database`: `this.db = new MySQLDatabase(url, user, password)`. Every class controls its own dependencies. Testing requires running the actual Stripe API. Swapping MySQL for PostgreSQL requires recompiling every class that instantiates `MySQLDatabase`. Configuration is scattered across every class that constructs a dependency.

**THE BREAKING POINT:**

A class that creates its own dependencies cannot be unit-tested in isolation. It is tightly coupled to the specific implementation. The test must set up the full dependency graph every time. When the `StripeGateway` constructor changes, every class that instantiates it breaks at compile time.

**THE INVENTION MOMENT:**

Martin Fowler formalised IoC in 2004 in "Inversion of Control Containers and the Dependency Injection pattern." The core insight: a class knowing how to acquire its dependencies is a design flaw. A class should declare what it needs; something external should provide it. This reversal (inversion) of the control flow for dependency acquisition is the principle that makes testability, substitutability, and configuration centralisation possible.

**EVOLUTION:**

- **2003-2004:** Rod Johnson's EJB critique → Spring IoC container as the solution
- **2004:** Fowler's essay names and formalises IoC/DI patterns
- **2009:** Constructor injection preferred over setter injection (Josh Bloch's influence on immutable objects)
- **2014:** Spring 4.0 - `@Autowired` on constructor is implicit when single constructor exists
- **2016:** Spring team officially recommends constructor injection; field injection `@Autowired` discouraged
- **2021:** Spring Boot 3 - `@Autowired` on constructors optional; compiler enforces single-constructor injection

---

### 📘 Textbook Definition

**IoC-first thinking** is the design discipline of expressing all object dependencies as _declarations_ (constructor parameters, interface types) rather than _acquisitions_ (`new`, service locator calls, `static` factory methods). In practice: (1) prefer **constructor injection** over field injection (`@Autowired` on fields) for mandatory dependencies; (2) depend on **interfaces** not concrete classes; (3) never call `ApplicationContext.getBean()` in application code (service locator anti-pattern); (4) treat the container as an external assembly mechanism, not an accessible registry; (5) design classes so all dependencies are visible at the constructor boundary.

---

### ⏱️ Understand It in 30 Seconds

**One line:** IoC-first means classes ask for what they need; they never go looking for it themselves.

> A restaurant order taker does not go to the kitchen to fetch ingredients. They take the order and the kitchen delivers. IoC-first thinking is the same: a class declares its order (constructor parameters), and the Spring container is the kitchen that delivers the right ingredients (beans). Classes that walk to the kitchen themselves (service locator, `ApplicationContext.getBean()`) break this contract.

**One insight:** Constructor injection makes dependencies visible, enforces immutability, and makes the class testable without a container - three properties that emerge naturally from one design rule.

---

### 🔩 First Principles Explanation

**CORE INVARIANTS:**

1. A class that can only be constructed via its declared constructor cannot have hidden dependencies
2. All dependencies visible at the constructor boundary can be inspected without running the application
3. An object that cannot be constructed without its dependencies cannot be in an invalid state
4. The container is an assembly mechanism, not an accessible registry
5. Depending on an interface makes the calling code independent of the implementation

**DERIVED DESIGN:**

From invariant 1+2 → constructor injection: every dependency is a constructor parameter; the class is a self-documenting specification of its needs.
From invariant 3 → mandatory dependencies via constructor, optional dependencies via setter (with sensible defaults). A class with required `@Autowired` field injection can be constructed in a broken state (null field).
From invariant 4 → no `ApplicationContext.getBean()` in application code; this is the service locator anti-pattern. Injection is the contract; direct lookup breaks it.
From invariant 5 → inject `PaymentGateway` (interface), not `StripeGateway` (implementation). Tests inject `MockPaymentGateway`.

**THE TRADE-OFFS:**

**Gain:** Testability without container; immutable objects by default; self-documenting dependencies; substitutability of implementations; detected missing dependencies at startup.

**Cost:** Large constructor parameter lists signal a class with too many responsibilities (valuable signal, not a problem to hide); interface proliferation for every dependency; slight verbosity compared to field injection.

**ESSENTIAL vs ACCIDENTAL COMPLEXITY:**

**Essential:** Declaring dependencies at the constructor boundary is the minimum complexity needed to make a class's requirements explicit and enforceable.

**Accidental:** Field injection (`@Autowired` on private fields) hides complexity by making dependencies invisible at construction time. Reflection-based injection is a convenience that trades clarity for brevity.

---

### 🧪 Thought Experiment

**SETUP:** `OrderService` needs a `PaymentGateway` and an `EmailSender`. You are writing the unit test.

**WITHOUT IoC-first design (field injection):**

```java
@Service
public class OrderService {
    @Autowired
    private PaymentGateway gateway;  // hidden dep

    @Autowired
    private EmailSender emailSender;  // hidden dep
}
```

Test: `OrderService service = new OrderService()` - compiles, but `gateway` and `emailSender` are null. Test crashes with `NullPointerException` unless a Spring context is spun up (slow) or `ReflectionTestUtils.setField()` is used (fragile, tied to field names).

**WITH IoC-first design (constructor injection):**

```java
@Service
public class OrderService {
    private final PaymentGateway gateway;
    private final EmailSender emailSender;

    public OrderService(
            PaymentGateway gateway,
            EmailSender emailSender) {
        this.gateway = gateway;
        this.emailSender = emailSender;
    }
}
```

Test: `OrderService service = new OrderService(mockGateway, mockSender)` - compiles and works without Spring. All dependencies visible. Fields are final - immutable after construction.

**THE INSIGHT:**

Constructor injection makes the test failure mode a _compile error_ ("missing argument") rather than a _runtime error_ ("NullPointerException in production").

---

### 🧠 Mental Model / Analogy

> IoC-first thinking is like designing a car's engine. A well-designed engine declares its inputs (fuel line connector, air intake, cooling line) as defined interfaces at the engine boundary. The car chassis (container) connects fuel, air, and coolant. The engine does not reach out and drill holes in the fuel tank to connect itself. Field injection is like an engine that drills its own fuel connection - it works, but now the engine has intimate knowledge of the fuel tank, making it impossible to run the engine on a test bench without the full car.

**Element mapping:**

- Car engine → your Spring `@Service` class
- Fuel line/air intake/cooling connectors → constructor parameters (declared dependencies)
- Car chassis connecting everything → Spring container
- Engine that drills its own connections → field injection / service locator
- Test bench → unit test (should work without the full chassis)
- Running engine on test bench → unit test without Spring context

Where this analogy breaks down: engines have a fixed physical design; software classes can be refactored. Field injection's cost is paid in test infrastructure complexity, not physical impossibility.

---

### 📶 Gradual Depth - Four Levels

**Level 1 - What it is (anyone can understand):**
IoC-first means your code never reaches out to grab things it needs - instead it announces what it needs, and something external (Spring) hands those things in. This small discipline makes your code much easier to test and change.

**Level 2 - How to use it (junior developer):**
Replace `@Autowired` on fields with a constructor that takes the same dependencies. Add `final` to all injected fields. Remove `@Autowired` (Spring injects single-constructor automatically since Spring 4.3). In tests, pass mock objects directly to the constructor without `@SpringBootTest`. If a constructor has more than 4-5 parameters, the class has too many responsibilities - split it.

**Level 3 - How it works (mid-level engineer):**
Constructor injection aligns with SOLID principles: S (single responsibility - a class with many constructor params is doing too much), O (depend on abstractions), L (implementation can be substituted), I (depend on narrow interfaces), D (depend on abstractions, not concretions). IoC-first thinking applies at every level: interfaces for repositories, separate configuration for environment-specific beans, `ApplicationEventPublisher` for decoupled cross-service communication within the same application.

**Level 4 - Why it was designed this way (senior/staff):**
The service locator pattern (`ApplicationContext.getBean()`) is not _wrong_ - it is the right tool for plugin architectures and frameworks that must load types at runtime. The problem is using it in application code where the type is known at compile time. Service locator hides dependencies behind a registry lookup; it makes the class's contract invisible and the container an implicit dependency. Constructor injection externalises assembly; the class has no container dependency at all. At scale, this distinction matters: a service locator-dependent class cannot be instantiated outside a container (limits reuse in non-Spring contexts, batch jobs, CLI tools); a constructor-injected class is a plain Java object.

**Expert Thinking Cues:**

- "Tell, don't ask" principle: a class should declare what it needs, not ask for it
- Circular dependency via constructor injection is a design smell (impossible to resolve); via field injection it "works" but masks the architectural problem
- Test pyramid: IoC-first design enables the base (unit tests without Spring) to be large and fast

---

### ⚙️ How It Works (Mechanism)

```
IoC-first Design Checklist:

✓ Constructor injection for mandatory dependencies
  → All deps visible at construction
  → Fields can be final (immutable)
  → Class testable without Spring context

✗ Field injection (@Autowired on private field)
  → Dependencies hidden (not in constructor)
  → Fields mutable (can be null after construction)
  → Requires Spring or ReflectionTestUtils to test

✓ Interface types for dependencies
  → PaymentGateway, not StripeGateway
  → Substitutable in tests and prod configs

✗ Concrete type injection
  → Ties class to specific implementation
  → Cannot substitute without changing code

✓ Single-constructor (no @Autowired needed)
  → Spring auto-injects since Spring 4.3
  → Lombok @RequiredArgsConstructor works

✗ ApplicationContext.getBean() in service code
  → Service locator anti-pattern
  → Container becomes hidden dependency
  → Class not portable outside Spring

✓ @Lazy for circular dependency (if unavoidable)
  → Breaks circular constructor dep
  → But signals refactoring need
```

---

### 🔄 The Complete Picture - End-to-End Flow

**NORMAL FLOW - IoC-first `OrderService`:**

```
[Design time: OrderService declared]
     |
     ├─ Constructor: (PaymentGateway, EmailSender)
     |    └─ Deps expressed as interfaces
     |         ← YOU ARE HERE (design decision)
     |
[Unit test: new OrderService(mock, mock)]
     |    └─ No Spring context needed
     |
[Spring assembly: ApplicationContext]
     |    ├─ Resolves PaymentGateway → StripeGateway
     |    └─ Resolves EmailSender → SendGridSender
     |
[Production: OrderService.processOrder()]
     |    ├─ gateway.charge() → Stripe
     |    └─ emailSender.send() → SendGrid
```

**FAILURE PATH:**

- Constructor with 8+ parameters → violates Single Responsibility; class does too much
- `@Autowired` on `Optional<T>` field → field is `null` if not set; prefer `Optional<T>` constructor parameter
- Circular constructor injection → `BeanCurrentlyInCreationException`; reveals architectural cycle

**WHAT CHANGES AT SCALE:**

In large codebases, IoC-first thinking is enforced by code review rules and architecture tests (ArchUnit). Violations (field injection, `getBean()` calls) are detectable statically:

```java
// ArchUnit test: no field injection
noFields().that()
  .areAnnotatedWith(Autowired.class)
  .should().beDeclaredInClassesThat()
  .areNotAnnotatedWith(TestComponent.class)
  .check(importedClasses);
```

---

### 💻 Code Example

**BAD - field injection, service locator, concrete dependency:**

```java
@Service
public class OrderService {
    // Hidden: invisible at construction
    @Autowired
    private StripeGateway stripeGateway;  // concrete

    // Service locator: container dependency
    @Autowired
    private ApplicationContext context;

    public void process(Order order) {
        // Service locator call in business code
        EmailSender sender =
            context.getBean(EmailSender.class);
        stripeGateway.charge(order.amount());
        sender.send(order.email(),
            "Order confirmed");
    }
}
```

**GOOD - constructor injection, interface dependencies:**

```java
@Service
public class OrderService {
    // All deps visible, final, injected via ctor
    private final PaymentGateway gateway;
    private final EmailSender emailSender;

    // Spring auto-injects (single ctor, no @Autowired)
    public OrderService(
            PaymentGateway gateway,
            EmailSender emailSender) {
        this.gateway = Objects.requireNonNull(gateway);
        this.emailSender =
            Objects.requireNonNull(emailSender);
    }

    public void process(Order order) {
        // Depends on interface, not implementation
        gateway.charge(order.amount());
        emailSender.send(
            order.email(), "Order confirmed");
    }
}

// Unit test - no Spring context
class OrderServiceTest {
    @Test
    void process_chargesGatewayAndSendsEmail() {
        var gateway = mock(PaymentGateway.class);
        var emailSender = mock(EmailSender.class);
        var service =
            new OrderService(gateway, emailSender);

        service.process(
            new Order("test@e.com", 100.0));

        verify(gateway).charge(100.0);
        verify(emailSender).send(
            "test@e.com", "Order confirmed");
    }
}
```

---

### ⚖️ Comparison Table

| Pattern                        | Testability                      | Immutability       | Dependency visibility                  | Spring coupling           |
| ------------------------------ | -------------------------------- | ------------------ | -------------------------------------- | ------------------------- |
| Constructor injection          | High - no container needed       | Yes (final fields) | Explicit (constructor params)          | None                      |
| Setter injection               | Medium - can set null            | No                 | Partial (setter visible, not required) | None                      |
| Field injection (`@Autowired`) | Low - needs Spring or reflection | No                 | Hidden (private field)                 | Implicit                  |
| Service locator                | Low - needs container            | No                 | None (runtime lookup)                  | Hard (container required) |
| `@Lookup` method injection     | Medium                           | No                 | Visible (abstract method)              | Moderate                  |

---

### ⚠️ Common Misconceptions

| Misconception                                              | Reality                                                                                                                                                                           |
| ---------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| "Field injection is fine, it's less code"                  | Field injection hides dependencies, prevents `final`, and requires reflection or a Spring context to test. Constructor injection is worth the extra 4 lines.                      |
| "Constructor injection is verbose for large classes"       | A constructor with 6+ parameters is a design smell telling you the class has too many responsibilities. Field injection hides this smell; constructor injection surfaces it.      |
| "Setter injection is acceptable for optional dependencies" | `Optional<T>` constructor parameter is better - it makes optionality explicit at construction time without enabling a partially-initialised state.                                |
| "`ApplicationContext.getBean()` is the same as @Autowired" | No. `@Autowired` is resolved once at startup by the container. `getBean()` is a runtime registry lookup. The former is injection; the latter is service locator.                  |
| "IoC is just about Spring"                                 | IoC is a general principle. Pure dependency injection without any framework - passing `new StripeGateway()` to `new OrderService(gateway)` manually - is IoC without a container. |

---

### 🚨 Failure Modes & Diagnosis

**Mode 1: `NullPointerException` in unit test due to field injection**

**Symptom:** Unit test with `new OrderService()` compiles but throws `NullPointerException` when `processOrder()` calls `this.gateway.charge()`.

**Root Cause:** `gateway` is `@Autowired` on a private field. `new OrderService()` does not trigger Spring injection. `gateway` is null.

**Diagnostic:**

```java
// Reveals the problem: NullPointerException in test
OrderService service = new OrderService();
// gateway is null - Spring never injected it
assertThrows(NullPointerException.class,
    () -> service.process(new Order(100.0)));
```

**Fix:** Switch to constructor injection. Use `@RequiredArgsConstructor` (Lombok) to remove boilerplate.

**Prevention:** ArchUnit rule detecting `@Autowired` on non-test class fields; enforced in CI.

---

**Mode 2: Circular constructor dependency prevents startup**

**Symptom:** `BeanCurrentlyInCreationException: Error creating bean with name 'A': Requested bean is currently in creation.`

**Root Cause:** `A` requires `B` in constructor; `B` requires `A` in constructor. Spring cannot create either - they form a dependency cycle that has no valid ordering.

**Diagnostic:**

```bash
# Spring's error message shows the cycle:
# A -> B -> A
# Enable startup failure analysis
spring.main.fail-on-contextual-cycles=true
```

**Fix:** Refactor to extract the shared logic to a third class `C` that neither `A` nor `B` depends on the other for. Alternatively: event-based decoupling (A publishes event; B listens without depending on A).

**Prevention:** ArchUnit cycle detection (`slices().matching("..service.(*)..").should().beFreeOfCycles()`).

---

**Mode 3: `getBean()` in hot path creates container coupling (Security failure mode)**

**Symptom:** `SecurityService.checkPermission()` calls `context.getBean("permissionChecker")` on every request. A malicious `BeanDefinitionRegistryPostProcessor` replaces `permissionChecker` with a no-op implementation between requests.

**Root Cause:** `getBean()` on every request allows the registry to be queried dynamically - if the registry is mutable (via `BeanDefinitionOverrideException` disabled), the looked-up bean can change at runtime.

**Diagnostic:**

```java
// Security audit: scan for getBean() calls
// in non-infrastructure code
grep -r "getBean\(" src/main/java \
  --include="*.java" | grep -v "@Configuration"
```

**Fix:** Inject `PermissionChecker` via constructor at startup - the resolved bean is immutable after context refresh. `getBean()` is no longer called at request time.

**Prevention:** Code review policy: `ApplicationContext.getBean()` in non-`@Configuration` / non-infrastructure code requires explicit senior review sign-off.

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**

- [[SPR-019 - IoC (Inversion of Control)]] - the principle being applied
- [[SPR-020 - DI (Dependency Injection)]] - the mechanism
- [[SPR-001 - What Is Spring - History and Philosophy]] - why IoC is Spring's core design

**Builds On This (learn these next):**

- [[SPR-069 - Spring Configuration Trade-off Framing]] - when to choose `@Bean` vs `@Component`
- [[SPR-070 - Framework Selection Mental Model]] - IoC as a framework selection criterion
- [[SPR-067 - Spring Specification and Extension Points]] - IoC applied to framework extension

**Alternatives / Comparisons:**

- Dagger 2 / Hilt (Android) - compile-time DI; IoC-first is equally important
- Manual DI (no framework) - `new OrderService(new StripeGateway(...))` in `main()` - still IoC, no container
- Service locator pattern - the anti-pattern IoC-first is designed to replace

---

### 📌 Quick Reference Card

```
+----------------------------------------------------------+
| WHAT IT IS    | Design discipline: deps declared, not    |
|               | acquired; container assembles the graph  |
| PROBLEM       | Tight coupling, hidden deps, untestable  |
|               | classes that create their own objects    |
| KEY INSIGHT   | Constructor injection = self-documenting |
|               | contract; field injection hides it       |
| USE WHEN      | Always - applies to every Spring class   |
| AVOID WHEN    | N/A - but use @Lazy for unavoidable       |
|               | circular deps (rare, signals refactor)   |
| TRADE-OFF     | More visible constructor vs less obvious |
|               | coupling from field injection brevity    |
| ONE-LINER     | Declare needs via constructor; let Spring|
|               | satisfy them; never reach for getBean()  |
| NEXT EXPLORE  | SPR-069 (Config Trade-offs),             |
|               | SPR-067 (Extension Points)               |
+----------------------------------------------------------+
```

**If you remember only 3 things:**

1. Constructor injection over field injection: dependencies visible, final, testable without Spring
2. Depend on interfaces, not implementations: `PaymentGateway`, not `StripeGateway`
3. No `ApplicationContext.getBean()` in application code: that is service locator, not IoC

**Interview one-liner:** "IoC-first thinking means classes declare dependencies as constructor parameters (not acquiring them via `new` or service locator), depending on interfaces not concretions - this makes classes testable without a container, substitutable, and self-documenting."

---

### 💎 Transferable Wisdom

**Reusable Engineering Principle:** _Make dependencies explicit at the boundary._ Any system component that hides its inputs (via global state, service locator, or static access) is difficult to test, reason about, and replace. Components with explicit, typed inputs at their boundary are composable, substitutable, and testable in isolation. This principle transcends Spring.

**Where else this pattern appears:**

- **Functional programming** - pure functions declare all inputs as parameters; no hidden state, no side effects - ultimate IoC
- **Terraform modules** - input variables declare what a module needs; the caller provides values - IoC for infrastructure
- **React components** - props are the explicit boundary; `useContext()` for global state is the service locator equivalent (powerful but consider the trade-off)

---

### 💡 The Surprising Truth

The term "Inversion of Control" predates Spring by more than a decade. It was coined by Michael Mattson in 1996 in the context of framework design (Hollywood Principle: "don't call us, we'll call you"). Martin Fowler's 2004 essay on DI containers was a _reframing_ of an existing principle - not an invention. The surprising truth is that the design principle that made Spring famous was not new when Spring was created. What Spring did was make IoC _accessible_ - before Spring, IoC containers (EJB, CORBA) were heavyweight and complex. Spring's lightweight IoC container demonstrated that the principle could be applied without ceremony, which catalysed its adoption across the industry. The principle was sound for 7 years before its tooling became practical.

---

### 🧠 Think About This Before We Continue

**Question 1 (E - First Principles):** A class has 7 constructor parameters, all injected by Spring. A junior developer suggests switching to field injection to reduce "constructor clutter." A senior developer disagrees, saying the 7-parameter constructor is _valuable information_. Explain from first principles what information the large constructor provides that field injection would hide, and what the correct response to a 7-parameter constructor should be.

_Hint:_ The constructor is a public declaration of a class's responsibilities. 7 dependencies suggest 7 concerns. Single Responsibility Principle says a class should have one reason to change. What does the constructor tell you about the class's design?

**Question 2 (C - Design Trade-off):** In a Spring application, `UserService` needs a `NotificationService`, and `NotificationService` needs a `UserService` (to look up user preferences before sending notifications). This is a legitimate business relationship. Two solutions are proposed: (A) extract user preference lookup to a `UserPreferenceRepository` that `NotificationService` depends on directly; (B) use `@Lazy` on one of the circular constructor parameters. Evaluate both solutions from an IoC-first perspective.

_Hint:_ Solution A breaks the cycle at the architectural level - it removes the cycle. Solution B breaks the cycle at the container level but keeps the cycle in the design. Which produces better code? Which is simpler to implement?

**Question 3 (A - System Interaction):** Spring Boot's `@TestConfiguration` and `@MockBean` annotations are used to replace production beans with mocks in `@SpringBootTest` tests. From an IoC-first perspective, is this a good practice or does it indicate a design problem? Justify your answer by considering what the test is actually testing and what the alternative would be.

_Hint:_ `@SpringBootTest` with `@MockBean` starts a full Spring context but replaces some beans. IoC-first says the class should be testable with `new Class(mockDep1, mockDep2)`. When would you _legitimately_ need `@SpringBootTest` + `@MockBean` vs a pure unit test?
