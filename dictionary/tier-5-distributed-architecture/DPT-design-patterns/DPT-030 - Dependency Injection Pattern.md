---
layout: default
title: "Dependency Injection Pattern"
parent: "Design Patterns"
grand_parent: "Technical Dictionary"
nav_order: 30
permalink: /design-patterns/dependency-injection-pattern/
id: DPT-025
category: Design Patterns
difficulty: ★★☆
depends_on:
used_by:
related:
tags:
  - pattern
  - intermediate
  - architecture
  - java
  - bestpractice
status: complete
version: 2
tier: tier-5-distributed-architecture
folder: DPT-design-patterns
---

# DPT-027 - Dependency Injection Pattern

⚡ TL;DR - Dependency Injection hands an object its dependencies from outside rather than letting the object create them - making classes testable, configurable, and loosely coupled.

| DPT-027 | Category: Design Patterns | Difficulty: ★★☆ |
|:---|:---|:---|
| **Depends on:** | Object-Oriented Programming (OOP), Interface, Inversion of Control (IoC), Coupling | |
| **Used by:** | Spring Core, Testing, Service Locator Replacement, Plugin Frameworks | |
| **Related:** | Service Locator, IoC Container, Strategy, Factory Method, Proxy | |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
`OrderService` needs a `PaymentGateway`. Without DI: `this.paymentGateway = new StripeGateway(API_KEY)`. `OrderService` now knows about `StripeGateway` - a concrete class. Unit testing is impossible without hitting the real Stripe API. Swapping to PayPal requires modifying `OrderService`. The API key is hardcoded in the business logic file. All configuration (URL, timeout, API keys) bleeds up into business classes.

**THE BREAKING POINT:**
Direct instantiation couples the class to its dependencies' concrete types AND their construction requirements. A change to `StripeGateway`'s constructor (add TLS configuration) forces changes in every class that instantiates it. Unit tests become integration tests because real implementations always run.

**THE INVENTION MOMENT:**
This is exactly why DI was formalised. The object receives a `PaymentGateway` interface reference. Someone outside (the IoC container, the test, the main method) decides which concrete implementation to provide. The object doesn't create or find its dependencies - it receives them.

**EVOLUTION:**
Dependency Injection as a named pattern emerged from Martin
Fowler's 2004 article formalising what Spring Framework (Rod
Johnson, 2002) had demonstrated in code. Spring popularised
constructor injection; later field injection (`@Autowired`)
became common despite being less testable. Spring Boot (2013)
added auto-configuration, creating zero-XML DI. Jakarta EE
standardised DI with CDI (Contexts and Dependency Injection,
2009). Micronaut and Quarkus (2018-2019) moved DI processing
to compile time, eliminating reflection overhead. Java 21 records
and sealed classes enable lightweight manual DI without a container.

---

### 📘 Textbook Definition

**Dependency Injection (DI)** is a design pattern in which an object's dependencies are provided externally rather than created internally. The three injection forms are: **constructor injection** (dependencies in the constructor - preferred), **setter injection** (dependencies via setters - optional dependencies), and **field injection** (via `@Autowired` on fields - convenient but not recommended for testability). DI implements the Dependency Inversion Principle (the D in SOLID): high-level modules depend on abstractions, not concrete implementations. IoC containers (Spring) automate DI by wiring dependencies based on configuration or annotations.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
Give an object what it needs instead of letting it reach out and get it.

**One analogy:**
> When you hire a chef (create an object), you don't tell the chef to go shopping for ingredients (create dependencies). You supply the kitchen stocked with what the chef needs (inject dependencies). The chef focuses on cooking; someone else manages sourcing. The same chef with different ingredients produces different results - that's configurability.

**One insight:**
DI transforms dependencies from private decisions (hardcoded in constructors) into public declarations (constructor parameters). Once they're public declarations, substitution becomes trivial: tests substitute fakes; production substitutes real implementations; environments substitute configured versions.

---

### 🔩 First Principles Explanation

**CORE INVARIANTS:**
1. A class should depend on abstractions, not concrete implementations.
2. The responsibility for creating and wiring dependencies belongs outside the dependent class.
3. Dependencies must be visible - discoverable from the class interface.

**DERIVED DESIGN:**
Given invariant 1: classes accept `PaymentGateway` (interface), not `StripeGateway` (concrete). Given invariant 2: constructor parameters declare what is needed; an external entity (IoC container or wiring code) satisfies the parameters. Given invariant 3: constructor parameters are the natural declaration point - they're part of the class's public API. The type system enforces the contract at compile time.

**Three injection forms:**
- **Constructor:** `OrderService(PaymentGateway pg)` - mandatory, set at construction, immutable; preferred.
- **Setter:** `setPaymentGateway(PaymentGateway pg)` - optional, changeable post-construction; for optional collaborators.
- **Field:** `@Autowired private PaymentGateway pg` - convenient but forces reflection (Spring) or a public field; not testable without a DI container.

**THE TRADE-OFFS:**
**Gain:** Testability (inject mocks); loose coupling; configurable implementations; explicit dependency declarations; framework-managed lifecycle.
**Cost:** More configuration code (wiring); DI container at test time if field injection used; over-injection can hide design problems (too many dependencies = design smell, not a DI problem); constructor injection with many params signals class doing too much.

---

### 🧪 Thought Experiment

**SETUP:**
Test `OrderService.processOrder()` without hitting the real payment system.

**WITHOUT DI:**
```java
class OrderService {
    private final PaymentGateway pg = new StripeGateway(KEY);
}
// Test: cannot substitute StripeGateway - it's hardcoded.
// Every test makes real Stripe API calls. CI fails without network.
```

**WITH DI:**
```java
class OrderService {
    private final PaymentGateway pg;
    OrderService(PaymentGateway pg) { this.pg = pg; }
}
// Test:
OrderService svc = new OrderService(mock(PaymentGateway.class));
svc.processOrder(order); // No Stripe call. Fast. Isolated.
```

**THE INSIGHT:**
DI makes the class portable: the same `OrderService` class can run with `StripeGateway` in production, `BraintreeGateway` in staging, and a `MockPaymentGateway` in tests - all without changing a line of business logic. Portability comes from the dependency declaration being external-facing rather than internal.

---

### 🧠 Mental Model / Analogy

> DI is like a vending machine powered by a replaceable power cord. The machine (class) has a power socket (constructor parameter of interface type). In the factory, you plug in a 240V cable (production implementation). In the testing lab, you plug in a bench power supply providing exact voltage (mock implementation). The machine itself is identical - only the power source changes. The socket is the interface; the cords are concrete implementations.

- "Vending machine" → class (OrderService)
- "Power socket" → interface type (PaymentGateway)
- "Factory power cable" → production implementation (StripeGateway)
- "Test bench supply" → mock (MockPaymentGateway)
- "Plugging in the cable" → constructor injection
- "Machine unchanged in both environments" → business logic untouched

Where this analogy breaks down: power supplies are physical; DI implementations are type-checked at compile time. An incorrect DI injection type fails at compile time (constructor injection) or application startup, not at runtime operation - stricter than plugging in the wrong voltage.

---

### 📶 Gradual Depth - Four Levels

**Level 1 - What it is (anyone can understand):**
DI means: don't build what you need - receive it. Instead of a class creating its own tools, someone gives it the tools it needs. The class uses the tool without caring about where it came from.

**Level 2 - How to use it (junior developer):**
Use constructor injection. Define the dependency as an interface. Accept it as a constructor parameter. Store in a `final` field. In Spring: `@Autowired` on the constructor (or implied with one constructor). Spring creates beans and automatically wires them by type. In tests: `new MyService(new MockDependency())` - no Spring needed.

**Level 3 - How it works (mid-level engineer):**
Spring's DI container is a `BeanFactory` that stores bean definitions. On startup, Spring resolves constructor parameters by scanning the classpath (`@ComponentScan`) and bean definitions (`@Bean`). It builds a dependency graph and instantiates beans in dependency-order. Circular dependencies with constructor injection = startup failure (detected before any request). Spring creates proxies for `@Transactional`, `@Async` beans - the actual class receives the proxy, not the raw bean. `@Scope("prototype")` creates a new instance per injection; `@Scope("singleton")` (default) shares one instance.

**Level 4 - Why it was designed this way (senior/staff):**
DI is the practical application of the Dependency Inversion Principle (Robert C. Martin, 1996) and the Inversion of Control principle. Before Spring (2003), J2EE developers relied on JNDI lookups (Service Locator) to obtain DataSources and EJBs. Martin Fowler's 2004 paper "Inversion of Control Containers and the Dependency Injection pattern" formalised the pattern and described its three forms. Spring made DI mainstream in Java. The debate over constructor vs field injection is resolved in the ecosystem: constructor injection is the only form recommended by Spring themselves (as of Spring 4+), Guice, and the JSR-330 spec. Field injection (`@Autowired` on fields) is discouraged because it requires a DI container to test, hides dependencies from the constructor signature, and prevents the class from being `final`. Constructor injection + `final` fields + immutable objects = the ideal. Null safety in Kotlin and the use of `@Inject` (JSR-330) further push this direction.

---

### ⚙️ How It Works (Mechanism)

```
┌──────────────────────────────────────────────────────┐
│  DEPENDENCY INJECTION - THREE FORMS                  │
│                                                      │
│  Constructor (PREFERRED):                            │
│  OrderService(PaymentGateway pg) {                   │
│      this.pg = Objects.requireNonNull(pg);           │
│  }                                                   │
│  → Dependency mandatory; immutable after init        │
│  → Testable without DI container                     │
│                                                      │
│  Setter (optional deps):                             │
│  setLogger(Logger logger) {                          │
│      this.logger = logger;                           │
│  }                                                   │
│  → Dependency optional; changeable after init        │
│  → Null risk if not set                              │
│                                                      │
│  Field (NOT recommended):                            │
│  @Autowired                                          │
│  private PaymentGateway pg; // hidden dependency     │
│  → Requires DI container to test                     │
│  → Dependency not visible in public interface        │
└──────────────────────────────────────────────────────┘
```

---

### 🔄 The Complete Picture - End-to-End Flow

**SPRING DI STARTUP FLOW:**
```
Spring application starts
  → scans @Component, @Service, @Repository classes
  → reads @Bean factory methods
  → builds BeanDefinitionRegistry (dependency graph)
        ← YOU ARE HERE (container resolves deps)
  → detects circular dependencies → fail fast
  → instantiates in dependency order:
    PaymentGateway → EmailService → OrderService
  → all singletons wired and ready
  → application accepts requests
```

**FAILURE PATH:**
```
OrderService requires PaymentGateway (constructor param)
→ No @Bean or @Component for PaymentGateway registered
→ Spring throws NoSuchBeanDefinitionException AT STARTUP
→ Application fails to start before handling any request
→ This is GOOD: fail fast beats fail at runtime
```

**WHAT CHANGES AT SCALE:**
At 1,000-bean applications, Spring startup time can be significant (5–30 seconds). Spring Boot auto-configuration reduces manual wiring; lazy bean initialization (`spring.main.lazy-initialization=true`) defers bean creation to first use. Native Image (GraalVM) compiles the DI wiring at build time, eliminating reflection and dramatically reducing startup time to <100 ms.

---

### 💻 Code Example

**Example 1 - Constructor injection (preferred):**
```java
// Interface - the abstraction
public interface PaymentGateway {
    PaymentResult charge(BigDecimal amount, String token);
}

// Concrete implementation
@Component
public class StripeGateway implements PaymentGateway {
    private final StripeClient client;
    @Override
    public PaymentResult charge(BigDecimal amount,
                                 String token) {
        return client.createCharge(amount, token);
    }
}

// Service - depends on interface, not concrete class
@Service
public class OrderService {
    private final PaymentGateway paymentGateway;
    private final EmailService emailService;

    // Constructor injection - @Autowired implicit in Spring 4+
    // Both deps are REQUIRED and FINAL (immutable after init)
    public OrderService(PaymentGateway paymentGateway,
                        EmailService emailService) {
        this.paymentGateway = Objects.requireNonNull(
            paymentGateway);
        this.emailService = Objects.requireNonNull(
            emailService);
    }

    public Order processOrder(OrderRequest req) {
        PaymentResult payment =
            paymentGateway.charge(req.total(), req.token());
        emailService.sendConfirmation(req.email());
        return new Order(req, payment);
    }
}

// Test - zero Spring context needed
@Test
void processOrder_chargesPayment() {
    PaymentGateway mockGateway = Mockito.mock(
        PaymentGateway.class);
    EmailService mockEmail = Mockito.mock(EmailService.class);

    when(mockGateway.charge(any(), any()))
        .thenReturn(PaymentResult.success("txn123"));

    OrderService service =
        new OrderService(mockGateway, mockEmail);
    Order result = service.processOrder(orderRequest);

    assertThat(result.paymentStatus()).isEqualTo("success");
    verify(mockGateway).charge(eq(BigDecimal.TEN), anyString());
}
```

**Example 2 - Multiple implementations, qualifier:**
```java
// Two payment gateways
@Component("stripe")
public class StripeGateway implements PaymentGateway { ... }

@Component("paypal")
public class PayPalGateway implements PaymentGateway { ... }

// Service: choose by config
@Service
public class CheckoutService {
    private final PaymentGateway gateway;

    // @Qualifier selects which bean to inject
    public CheckoutService(
        @Qualifier("stripe") PaymentGateway gateway) {
        this.gateway = gateway;
    }
}
// Or: use @ConditionalOnProperty to select by environment
```

**Example 3 - WRONG: field injection (avoid):**
```java
// BAD: field injection - hidden + not testable without Spring
@Service
public class ProblemService {
    @Autowired  // hidden dependency - not in constructor!
    private PaymentGateway pg;

    public void process(Order o) {
        pg.charge(o.total(), o.token()); // pg may be null!
    }
}
// Test must either:
// 1. Start full Spring context (slow, brittle)
// 2. Use reflection to set the field (fragile)
// Neither is ideal - avoid field injection
```

---

### ⚖️ Comparison Table

| Injection Form | Testability | Visibility | Mutability | Recommended |
|---|---|---|---|---|
| **Constructor** | Best (no container) | Explicit in API | Immutable | ✅ Always |
| Setter | Good (call setter in test) | Visible as method | Mutable | ✅ Optional deps |
| Field | Slower (reflection/Spring) | Hidden | Mutable | ❌ Avoid |
| Service Locator | Harder (shared global) | Hidden | Mutable | ❌ Avoid in standard code |

How to choose: always use constructor injection for mandatory dependencies. Use setter injection for optional, reconfigurable dependencies. Never use field injection in production code.

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| DI requires a framework (Spring, Guice) | Constructor injection is pure Java - `new MyService(new MyDep())`. Frameworks automate wiring; DI itself is just passing dependencies. |
| @Autowired on fields is equivalent to constructor injection | Field injection requires a DI container to test; constructor injection does not. They are NOT equivalent in testability |
| More constructor parameters = DI working well | Too many constructor parameters (>4–5) signals that the class has too many responsibilities - not that DI is good |
| DI prevents circular dependencies | DI with constructor injection fails fast on circular dependencies at startup. Field/setter injection can mask circular deps until runtime - and Spring may even satisfy them with proxies, hiding a design problem |
| Setter injection is equivalent to constructor injection for mandatory deps | Setter injection allows calling code to forget to inject a mandatory dependency. Constructor injection + `requireNonNull` fails fast. For mandatory deps, constructor injection is categorically safer |

---

### 🚨 Failure Modes & Diagnosis

**1. NoSuchBeanDefinitionException - Missing Bean**

**Symptom:** Application fails to start with: `No qualifying bean of type 'PaymentGateway' available`.

**Root Cause:** `PaymentGateway` implementation not registered as a Spring bean; missing `@Component`, `@Service`, or `@Bean` annotation; component scan not covering the implementation's package.

**Diagnostic:**
```bash
# Check what's in the Spring context
./mvnw spring-boot:run --debug 2>&1 | grep PaymentGateway
# Or in tests:
@SpringBootTest
public class ContextTest {
    @Autowired ApplicationContext context;
    @Test void allBeansDefined() {
        context.getBean(PaymentGateway.class); // fails if missing
    }
}
```

**Fix:** Add `@Component` or `@Bean` to the implementation. Verify `@ComponentScan` includes the package.

**Prevention:** Write a context load test (`@SpringBootTest`) that verifies all critical beans are present.

---

**2. Circular Dependency - Constructor Injection**

**Symptom:** Application fails to start with `The dependencies of some of the beans in the application context form a cycle: A → B → A`.

**Root Cause:** Bean A's constructor requires Bean B; Bean B's constructor requires Bean A. Spring cannot instantiate either first.

**Diagnostic:** The exception message explicitly shows the cycle.

**Fix:**
```java
// Option 1: Break cycle by refactoring
// Option 2: Introduce a third bean that both depend on
// (never depend on each other directly)
// Option 3: Use setter injection for one direction
//   (but investigate if cycle indicates design problem)
class A {
    private B b;
    @Autowired // setter injection breaks constructor cycle
    public void setB(B b) { this.b = b; }
}
```

**Prevention:** Circular dependency = design problem. Extract shared functionality into a third bean. Architectural tools like ArchUnit can detect circular package dependencies.

---

**3. Wrong Scope - Stateful Singleton**

**Symptom:** Data from one user's request appears in another user's response. Intermittent, load-dependent.

**Root Cause:** `@RequestScoped` or prototype-scoped state stored in a singleton bean's field. Singleton lifecycle exceeds request lifecycle.

**Diagnostic:**
```bash
# Check bean scope
grep "@Scope\|@Component\|@Service" src/ -rn
# Singleton holding request-scoped data = problem
```

**Fix:**
```java
// BAD: singleton stores per-request state
@Service // singleton by default
public class OrderService {
    private String currentUserId; // shared across ALL requests!
}

// GOOD: pass request state as method parameters
@Service
public class OrderService {
    public Order processOrder(String userId, Cart cart) {
        // userId is passed in - not stored in the bean
    }
}
```

**Prevention:** Singletons must be stateless or hold globally constant state. Per-request data must be method parameters or `ThreadLocal`.

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**
- `Interface` - DI depends on coding to interfaces; the injected dependency must be declared as an interface type for substitution to work
- `Inversion of Control (IoC)` - DI is one form of IoC; understanding IoC (the control of object creation inverted from within the object to external wiring) drives DI's design
- `Coupling` - DI's primary goal is reducing coupling; understanding tight coupling explains why DI matters

**Builds On This (learn these next):**
- `Spring Core` - Spring is the canonical Java DI framework; `@Autowired`, `@Bean`, `@Component` are how Spring implements DI
- `IoC Container` - the component that automates DI - registering beans, resolving dependencies, managing lifecycle
- `Strategy Pattern` - DI is the delivery mechanism for Strategy; inject different strategy implementations at configuration time

**Alternatives / Comparisons:**
- `Service Locator` - same dependency management problem, different approach; DI is explicit and preferred; Service Locator is implicit and usually avoided
- `Factory Method` - abstracts object creation; DI abstracts object wiring; both decouple but at different levels
- `Null Object` - sometimes injected as a dependency to provide safe defaults; exemplifies DI's configurability

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ WHAT IT IS   │ Receive dependencies from outside rather  │
│              │ than creating them internally             │
├──────────────┼───────────────────────────────────────────┤
│ PROBLEM IT   │ Direct instantiation couples class to     │
│ SOLVES       │ concrete deps; makes testing impossible   │
├──────────────┼───────────────────────────────────────────┤
│ KEY INSIGHT  │ Constructor params = dependency contract; │
│              │ visible, type-safe, compile-time checked  │
├──────────────┼───────────────────────────────────────────┤
│ USE WHEN     │ Always - default pattern for all          │
│              │ non-trivial object dependency management  │
├──────────────┼───────────────────────────────────────────┤
│ AVOID WHEN   │ Field injection: use constructor instead; │
│              │ simple value objects need no DI at all    │
├──────────────┼───────────────────────────────────────────┤
│ TRADE-OFF    │ Loose coupling + testability vs wiring    │
│              │ ceremony (Spring reduces this cost)       │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "Tell me what you need;                   │
│              │  I'll make sure you have it."             │
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ Spring Core → IoC Container →             │
│              │ Service Locator (comparison)              │
└──────────────────────────────────────────────────────────┘
```


---

### 💎 Transferable Wisdom

**Reusable Engineering Principle:**
An object should not be responsible for acquiring its own
dependencies. Dependencies should be provided by an external
caller or container. This externalises the "who provides what"
decision, making it observable, changeable, and testable.

**Where else this pattern appears:**
- **Restaurant supply chain:** A chef does not source their own
  ingredients -- the restaurant manager (the container) provides
  standardised supplies. The chef (the component) specifies what
  it needs; the manager provides it.
- **Unix process environment variables:** A process declares
  what environment variables it reads; the OS (container) injects
  the values at process start. No hard-coded paths in the binary.
- **Kubernetes ConfigMap/Secret injection:** Pods declare named
  environment variables or volume mounts; Kubernetes injects the
  values from ConfigMaps and Secrets at pod start.

---

### 💡 The Surprising Truth

Field injection with `@Autowired` -- by far the most common DI
style in Spring applications -- is actively discouraged by the
Spring team itself. The Spring documentation states: "Always use
constructor injection in your beans." Field injection makes
dependencies invisible in the public API, allows object creation
without all dependencies present (a partially-constructed bean),
and makes unit testing without a Spring context impossible without
reflection-based hacks. The pattern that made Spring famous also
has a widely-used anti-pattern variant that the framework's own
authors warn against on every page of their documentation.
---

### 🧠 Think About This Before We Continue

**Q1.** A class `ReportGenerator` has 9 constructor parameters (all injected via Spring). A code reviewer says "this is an indication of a design smell, not a problem with DI." Explain the specific design smell that 9 constructor parameters most likely indicates (name the principle being violated), describe the refactoring that would address it, and explain why reducing to constructor injection with 3 dependencies makes the class better-designed - not just cosmetically tidier.

*Hint: Look at the First Principles section for the core invariants and the Failure Modes section for where this scenario appears as a documented issue.*

**Q2.** A Spring service `AccountService` is a `@Singleton` bean. It injects a `UserPreferencesRepository` which is a `@RequestScope` bean. Explain the exact problem that occurs when Spring wires these, describe the Spring mechanism that resolves this problem (by name), and identify the one scenario where even this mechanism does not work correctly.



*Hint: The Comparison Table and Level 3-4 explanations contain the mechanism that determines which approach wins in this scenario.*

**Q3 (Design Trade-off):** A `PaymentService` uses constructor
injection for `PaymentGateway`, `FraudDetector`, and
`AuditLogger`. A new requirement: `PaymentService` should also
optionally use a `CurrencyConverter`, but not all deployments
have one available. Design the injection model for the optional
dependency and compare: (a) nullable constructor parameter,
(b) `Optional<CurrencyConverter>` constructor parameter,
(c) `@Autowired(required=false)` field injection.

*Hint: The First Principles CORE INVARIANTS say dependencies
should be declared, not discovered. Each option makes the
optional dependency more or less explicit -- map to testability
and clarity in the code review.*
