---
layout: default
title: "DI (Dependency Injection)"
parent: "Spring Core"
nav_order: 372
permalink: /spring/dependency-injection/
number: "372"
category: Spring Core
difficulty: ★☆☆
depends_on: IoC (Inversion of Control), Object-Oriented Programming (OOP), Interfaces
used_by: ApplicationContext, @Autowired, Spring Boot, Testability
tags: #foundational, #spring, #architecture, #pattern
---

# 372 — DI (Dependency Injection)

`#foundational` `#spring` `#architecture` `#pattern`

⚡ TL;DR — Dependency Injection is the technique of supplying a class's collaborators from outside rather than having the class construct them — the primary implementation of IoC in Spring.

| #372            | Category: Spring Core                                         | Difficulty: ★☆☆ |
| :-------------- | :------------------------------------------------------------ | :-------------- |
| **Depends on:** | IoC (Inversion of Control), Object-Oriented Programming (OOP) |                 |
| **Used by:**    | ApplicationContext, @Autowired, Spring Boot, Testability      |                 |

---

### 📘 Textbook Definition

**Dependency Injection** (DI) is a design pattern that implements the Inversion of Control principle by supplying an object's dependencies from an external source rather than having the object create them. The three canonical forms are: _constructor injection_ (dependencies passed as constructor parameters), _setter injection_ (dependencies set via setter methods after construction), and _field injection_ (dependencies assigned directly to fields, typically via reflection). In Spring, the IoC container reads bean definitions, instantiates the dependencies, and injects them into each bean via whichever injection style is configured. Constructor injection is the Spring team's recommended default because it makes dependencies explicit, ensures immutability, and prevents partially-constructed objects.

---

### 🟢 Simple Definition (Easy)

Instead of a class creating the things it needs (`new PaymentGateway()`), you pass them in from outside — Spring handles the passing. The class just declares what it needs.

---

### 🔵 Simple Definition (Elaborated)

DI is the "how" behind IoC. A class has _dependencies_ — other objects it needs to do its work. DI means those objects are _injected_ into the class rather than created by it. In Spring you have three injection styles: constructor (most recommended — dependencies are final, set once), setter (optional dependencies, can be changed), and field (convenient but hides dependencies). Spring reads your class, sees what it needs (via `@Autowired`, constructor types, or XML config), creates the required beans, and injects them. The class becomes a passive consumer: it declares its needs and the container fulfils them.

---

### 🔩 First Principles Explanation

**The three injection styles and their trade-offs:**

```java
// 1. CONSTRUCTOR INJECTION — recommended
@Service
class OrderService {
    private final PaymentGateway gateway;
    private final OrderRepository repo;

    // Spring calls this constructor with ready-made beans
    OrderService(PaymentGateway gateway, OrderRepository repo) {
        this.gateway = gateway;
        this.repo    = repo;
    }
    // Benefits:
    // - Dependencies are final (immutable after construction)
    // - Object is never in a partially-initialised state
    // - Dependencies visible in constructor signature
    // - Easy to test: just call new OrderService(mockGateway, mockRepo)
}

// 2. SETTER INJECTION — for optional dependencies
@Service
class ReportService {
    private EmailSender emailSender; // optional — may not be set

    @Autowired(required = false)
    void setEmailSender(EmailSender emailSender) {
        this.emailSender = emailSender;
    }
    // Use when a dependency is genuinely optional
    // Drawback: object can be used before injection is complete
}

// 3. FIELD INJECTION — convenient but discouraged
@Service
class NotificationService {
    @Autowired                          // Spring injects via reflection
    private PushNotifier notifier;      // NOT final — mutable after construction

    // Drawbacks:
    // - Cannot be tested without a Spring container (or reflection tricks)
    // - Hides the dependency — constructor doesn't show what is needed
    // - Cannot be declared final
}
```

**Why constructor injection is preferred:**

```java
// Constructor injection makes circular dependency visible at startup
// (Spring throws UnsatisfiedDependencyException immediately)
// Field injection hides the circular dep until runtime behaviour fails

// Constructor injection allows plain unit test:
class OrderServiceTest {
    @Test
    void testPlaceOrder() {
        // No Spring context needed — just pass mocks directly
        var service = new OrderService(
            mock(PaymentGateway.class),
            mock(OrderRepository.class)
        );
        service.placeOrder(new Order(...));
    }
}
```

---

### ❓ Why Does This Exist (Why Before What)

WITHOUT Dependency Injection:

What breaks without it:

1. Unit tests for `OrderService` require a real database, real payment API, and real email server — infrastructure tests, not unit tests.
2. Changing `StripeGateway` to `PayPalGateway` means finding every `new StripeGateway()` call and changing it.
3. Thread safety is unclear: is `new PaymentGateway()` inside a request handler safe to call concurrently?
4. Configuration (API keys, timeouts) is embedded in constructors rather than centralised.
5. Mocking frameworks cannot intercept `new ConcreteClass()` — they can only intercept injected interfaces.

WITH DI:
→ Unit tests inject mocks — no infrastructure needed: `new OrderService(mockGateway, mockRepo)`.
→ Implementations swapped via configuration only — zero business code changes.
→ Spring manages singleton beans correctly — thread safety is the container's concern.
→ Configuration externalised via `@Value`, environment variables, and `application.properties`.

---

### 🧠 Mental Model / Analogy

> Think of a restaurant kitchen. A cook without DI goes to the market every morning to buy their own ingredients — they know the supplier, negotiate the price, and carry the bags themselves. A cook WITH DI arrives to find all ingredients pre-sourced and laid out: the head chef (container) handles procurement. The cook just cooks. If the head chef swaps a supplier (implementation), the cook never needs to know — the ingredient (interface) looks the same.

"Cook going to market" = class calling `new ConcreteImpl()`
"Ingredients laid out on arrival" = dependencies injected by the container
"Head chef (container) handling procurement" = Spring IoC wiring dependencies
"Swapping a supplier" = swapping an implementation without changing the consumer

---

### ⚙️ How It Works (Mechanism)

**Spring DI resolution sequence:**

```
┌──────────────────────────────────────────────┐
│      DI Resolution for OrderService          │
│                                              │
│  Spring sees: OrderService needs             │
│    PaymentGateway (interface)                │
│    OrderRepository (interface)               │
│           ↓                                  │
│  Spring searches bean registry:              │
│    PaymentGateway → StripeGateway @Component │
│    OrderRepository → JpaOrderRepo @Repository│
│           ↓                                  │
│  Spring instantiates dependencies first:     │
│    new StripeGateway(httpClient)             │
│    new JpaOrderRepo(entityManager)           │
│           ↓                                  │
│  Spring injects into OrderService:           │
│    new OrderService(stripeGw, jpaRepo)       │
│           ↓                                  │
│  OrderService bean ready in context          │
└──────────────────────────────────────────────┘
```

**DI with `@Configuration` + `@Bean` (explicit wiring):**

```java
@Configuration
class AppConfig {
    // Explicit DI: you control exactly what gets injected
    @Bean
    PaymentGateway paymentGateway() {
        return new StripeGateway(apiKey(), httpClient());
    }

    @Bean
    OrderService orderService(PaymentGateway gateway,
                              OrderRepository repo) {
        return new OrderService(gateway, repo);
    }
    // Spring calls orderService() and injects the beans declared above
}
```

---

### 🔄 How It Connects (Mini-Map)

```
IoC (Inversion of Control)
(principle — the why)
        │  ← implements →
        ▼
DI (Dependency Injection)  ◄──── (you are here)
        │
        ├──────────────────────────────────────┐
        ▼                                      ▼
Constructor Injection (recommended)   Field Injection (discouraged)
        │                                      │
        ▼                                      ▼
ApplicationContext / BeanFactory       @Autowired annotation
(manages and performs the injection)   (marks injection points)
```

---

### 💻 Code Example

**Example 1 — Full constructor injection with Spring Boot:**

```java
@Service
public class UserRegistrationService {
    private final UserRepository userRepo;
    private final PasswordEncoder encoder;
    private final EventPublisher  events;

    // Single constructor — @Autowired optional in Spring 4.3+
    public UserRegistrationService(UserRepository userRepo,
                                    PasswordEncoder encoder,
                                    EventPublisher events) {
        this.userRepo  = userRepo;
        this.encoder   = encoder;
        this.events    = events;
    }

    public void register(String email, String rawPassword) {
        String hash = encoder.encode(rawPassword);
        User user   = userRepo.save(new User(email, hash));
        events.publish(new UserRegisteredEvent(user));
    }
}
```

**Example 2 — Testability via constructor injection (no Spring context):**

```java
class UserRegistrationServiceTest {
    @Test
    void shouldPublishEventOnRegistration() {
        // Arrange — plain Java mocks, no Spring needed
        UserRepository   mockRepo   = mock(UserRepository.class);
        PasswordEncoder  mockEnc    = mock(PasswordEncoder.class);
        EventPublisher   mockEvents = mock(EventPublisher.class);

        when(mockRepo.save(any())).thenReturn(new User("a@b.com", "hash"));
        when(mockEnc.encode("pass")).thenReturn("hash");

        var service = new UserRegistrationService(mockRepo, mockEnc, mockEvents);

        // Act
        service.register("a@b.com", "pass");

        // Assert — event published exactly once
        verify(mockEvents, times(1)).publish(any(UserRegisteredEvent.class));
    }
}
```

---

### ⚠️ Common Misconceptions

| Misconception                                             | Reality                                                                                                                                                                                     |
| --------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Field injection is fine because it is less verbose        | Field injection cannot be used without a Spring container, prevents `final` fields, hides dependencies, and makes constructors misleading. The Spring team officially discourages it        |
| Setter injection is outdated                              | Setter injection is correct for optional dependencies or for dependencies that can legitimately change after construction (rare but valid)                                                  |
| DI requires annotations (@Autowired)                      | Spring can perform DI through XML configuration, Java `@Configuration` classes, or implicit single-constructor injection — no annotations required                                          |
| DI and the Service Locator pattern achieve the same thing | DI pushes dependencies IN (passive recipient); Service Locator pulls dependencies OUT (active fetcher). DI is more testable; Service Locator introduces a hidden dependency on the registry |

---

### 🔥 Pitfalls in Production

**Field injection breaks testability — forced to use Spring context in unit tests**

```java
// BAD: field injection — cannot test without Spring
@Service
class InvoiceService {
    @Autowired
    private TaxCalculator calculator; // injected by Spring via reflection
    // No constructor that accepts TaxCalculator
    // Unit test must spin up a Spring context — slow, fragile
}

// GOOD: constructor injection — testable without Spring
@Service
class InvoiceService {
    private final TaxCalculator calculator;

    InvoiceService(TaxCalculator calculator) {
        this.calculator = calculator;
    }
    // Unit test: new InvoiceService(new FakeTaxCalculator())
}
```

---

**Injecting too many dependencies — hidden SRP violation**

```java
// BAD: 8 injected dependencies — SRP violation disguised as DI
@Service
class OrderService {
    OrderService(PaymentGateway g, OrderRepo r, EmailSender e,
                 SMSSender s, AuditLog a, InventoryService i,
                 PricingEngine p, FraudDetector f) { ... }
    // 8 deps = this class is doing too many things
    // DI makes it easy to add deps — but doesn't mean you should

// GOOD: extract responsibilities into focused services
@Service
class OrderService {
    OrderService(PaymentService payment,   // wraps gateway + fraud
                 FulfillmentService fulfil, // wraps inventory + shipping
                 NotificationService notify) { ... } // wraps email + SMS
    // 3 focused collaborators — each with single responsibility
}
```

---

### 🔗 Related Keywords

- `IoC (Inversion of Control)` — the principle DI implements; the "why" behind DI
- `@Autowired` — Spring's annotation for marking injection points in constructor, setter, or field
- `ApplicationContext` — the Spring container that performs DI for all beans at startup
- `Bean` — any object whose dependencies are managed and injected by the Spring container
- `@Qualifier / @Primary` — annotations that resolve ambiguity when multiple beans satisfy a dependency type
- `Circular Dependency` — a DI failure mode where A needs B and B needs A; constructor injection detects it at startup
- `BeanPostProcessor` — the Spring mechanism that processes `@Autowired` and performs field/setter injection

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ KEY IDEA     │ Pass dependencies in from outside rather  │
│              │ than having the class create them         │
├──────────────┼───────────────────────────────────────────┤
│ PREFER       │ Constructor injection: final fields,      │
│              │ immutable, visible, no-Spring testable    │
├──────────────┼───────────────────────────────────────────┤
│ AVOID        │ Field injection: hides deps, prevents     │
│              │ final, requires Spring context in tests   │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "Declare what you need; Spring provides   │
│              │ it — you're a consumer, not a builder."   │
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ @Autowired → ApplicationContext →         │
│              │ Bean Lifecycle → Circular Dependency      │
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** Spring Boot 2.2 made `@Autowired` optional on single-constructor beans (implicit constructor injection). A developer adds a second constructor to an existing service for a custom factory use case. This causes a `NoUniqueBeanException` at startup — the application won't start. Explain the exact Spring mechanism that determines which constructor to use for injection, what rules apply when there are multiple constructors, and how to resolve the ambiguity without removing the second constructor.

**Q2.** A Spring service uses setter injection for a dependency, claiming "it is optional." During load testing, threads calling the service concurrently observe a `NullPointerException` on the dependency field — even though the dependency was injected. Explain the specific race condition that setter injection introduces during bean initialisation that constructor injection eliminates, describe the memory visibility guarantee (or lack thereof) for setters vs. final fields in the Java Memory Model, and identify the Spring bean scope that makes this race condition impossible by design.
