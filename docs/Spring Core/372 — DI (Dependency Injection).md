---
layout: default
title: "DI (Dependency Injection)"
parent: "Spring Core"
nav_order: 372
permalink: /spring/di-dependency-injection/
number: "372"
category: Spring Core
difficulty: ★★☆
depends_on: IoC, Abstraction, Interfaces, Coupling
used_by: ApplicationContext, @Autowired, Bean, Unit Testing, Spring Boot
tags: #java, #spring, #springboot, #pattern, #intermediate, #testing
---

# 372 — DI (Dependency Injection)

`#java` `#spring` `#springboot` `#pattern` `#intermediate` `#testing`

⚡ TL;DR — The IoC mechanism where a component's dependencies are provided externally at construction time rather than being instantiated inside the component.

| #372 | category: Spring Core
|:---|:---|:---|
| **Depends on:** | IoC, Abstraction, Interfaces, Coupling | |
| **Used by:** | ApplicationContext, @Autowired, Bean, Unit Testing, Spring Boot | |

---

### 📘 Textbook Definition

**Dependency Injection (DI)** is a design pattern and the primary implementation mechanism of the IoC principle. A component (the dependent) declares the interfaces it requires; an external injector (the Spring container) creates instances of those interfaces and provides them to the component — either through a constructor, a setter method, or a field. DI decouples components from the concrete implementations they use, relying on abstractions (interfaces) instead. This makes components independently testable with mock collaborators, independently deployable, and reconfigurable without source-code changes.

---

### 🟢 Simple Definition (Easy)

Dependency Injection means you don't create the objects your class needs — someone else creates them and passes them in. Your class just declares what it needs in its constructor.

---

### 🔵 Simple Definition (Elaborated)

Without DI, a `UserService` calls `new JdbcUserRepository()` itself — it is coupled to that specific implementation. With DI, `UserService` declares "I need a `UserRepository`" in its constructor, and Spring creates the right implementation and passes it in automatically. The `UserService` never knows whether it's talking to a JDBC, JPA, or in-memory implementation. This single change makes `UserService` fully testable with a mock, configurable via Spring configuration, and reusable across different contexts.

---

### 🔩 First Principles Explanation

**Three DI styles — and why constructor injection wins:**

```
┌─────────────────────────────────────────────────────┐
│  DI INJECTION TYPES                                 │
├─────────────────────────────────────────────────────┤
│  1. CONSTRUCTOR injection (preferred)               │
│     Deps declared in constructor signature          │
│     → Immutable — deps set once, never change       │
│     → Testable without Spring context               │
│     → Detects circular deps at startup              │
│     → NullPointerException impossible after ctor    │
│                                                     │
│  2. SETTER injection (optional deps)                │
│     Deps set via setX() after construction          │
│     → Allows optional dependencies                 │
│     → Mutable — allows reconfiguration             │
│     → Risk: object used before setter called        │
│                                                     │
│  3. FIELD injection (avoid)                         │
│     @Autowired directly on private fields           │
│     → Requires reflection — breaks encapsulation    │
│     → Invisible dependencies — no constructor hint  │
│     → Untestable without Spring or Mockito magic    │
└─────────────────────────────────────────────────────┘
```

**Why constructor injection prevents hidden surprises:**

```java
// Constructor injection: self-documenting
public OrderService(PaymentGateway gw,
                    InventoryService inv,
                    AuditLogger audit) {
  // Caller MUST provide all three — compiler enforces it
  this.gw    = Objects.requireNonNull(gw);
  this.inv   = Objects.requireNonNull(inv);
  this.audit = Objects.requireNonNull(audit);
}
// This class literally cannot be instantiated
// with a missing dependency → fail fast at startup

// Field injection: invisible
@Service
class OrderService {
  @Autowired PaymentGateway gw;     // invisible
  @Autowired InventoryService inv;  // invisible
  @Autowired AuditLogger audit;     // invisible
  // Class appears to have no deps until runtime NPE
}
```

---

### ❓ Why Does This Exist (Why Before What)

**WITHOUT DI:**

```
Without DI:

  Hard to test:
    new UserService() → inside: new JdbcRepo(dataSource)
    → unit test requires a real database
    → 100ms per test → 10,000 tests = 17 minutes

  Hard to configure:
    Database URL in UserService constructor
    → change DB URL = recompile UserService
    → prod DB URL in source code

  Hard to swap:
    Using JPA? Want to switch to MongoDB?
    → rewrite every class that uses the old repo
    → massive cascading change

  Hard to share:
    Each new UserService() creates a new connection pool
    → run out of DB connections at 100 concurrent users
```

**WITH DI:**

```
→ Test: inject mock UserRepository — no DB needed
→ Config: Spring reads URL from application.properties
→ Swap: change @Bean definition — zero class changes
→ Share: container creates one repo, injects everywhere
→ Audit: all injection points visible in constructors
```

---

### 🧠 Mental Model / Analogy

> DI is like a **catering company supplying a restaurant kitchen**. The chef (your class) declares "I need fresh tomatoes, mozzarella, and basil today." The catering manager (Spring container) sources the right ingredients and delivers them to the kitchen door. The chef never goes shopping. If the supplier changes from organic to conventional tomatoes, the chef doesn't notice — they just use what's delivered. Only the catering manager needs to know where the tomatoes come from.

"Chef declaring ingredients needed" = constructor parameter list
"Catering manager sourcing ingredients" = Spring container creating beans
"Delivering to kitchen door" = injection at construction time
"Chef not caring about supplier" = component only knows interfaces
"Supplier changes" = swapping implementation in @Bean config

---

### ⚙️ How It Works (Mechanism)

**Constructor injection (Spring 4.3+: single-constructor auto-detected):**

```java
@Service
public class PaymentService {
  private final PaymentGateway gateway;
  private final AuditRepository audit;

  // Spring 4.3+: @Autowired not required on single ctor
  public PaymentService(PaymentGateway gateway,
                        AuditRepository audit) {
    this.gateway = gateway;
    this.audit   = audit;
  }
}
```

**Setter injection (for optional dependencies):**

```java
@Service
public class NotificationService {
  private SmsProvider smsProvider;

  // Optional: SMS provider may not be configured
  @Autowired(required = false)
  public void setSmsProvider(SmsProvider smsProvider) {
    this.smsProvider = smsProvider;
  }
}
```

**How Spring resolves the injection:**

```
┌─────────────────────────────────────────────────────┐
│  RESOLUTION ORDER                                   │
│                                                     │
│  1. Find beans matching the parameter TYPE          │
│     (PaymentGateway.class)                          │
│                                                     │
│  2. If one match → inject it                        │
│                                                     │
│  3. If multiple matches:                            │
│     a. Check for @Primary on one candidate         │
│     b. Check @Qualifier on injection point          │
│     c. Match by parameter NAME as bean name         │
│     d. If still ambiguous → NoUniqueBeanException  │
│                                                     │
│  4. If zero matches:                               │
│     → NoSuchBeanDefinitionException (or optional)  │
└─────────────────────────────────────────────────────┘
```

---

### 🔄 How It Connects (Mini-Map)

```
IoC Principle (103)
(control inverted — declare needs)
        ↓
  DI MECHANISM  ← you are here
  (constructor / setter / field injection)
        ↓
  Implemented by:
  ApplicationContext (105) scanning @Component beans
  @Autowired (112) marking injection points
        ↓
  Resolution via:
  @Qualifier (113) — pick by name
  @Primary (113) — default candidate
        ↓
  Enables:
  Unit testing with mocks (no Spring context)
  Configurable implementations (dev vs prod)
```

---

### 💻 Code Example

**Example 1 — Comparing all three injection styles:**

```java
// FIELD injection — AVOID in production code
@Service
class UserServiceBad {
  @Autowired UserRepository repo; // hidden dependency
  @Autowired PasswordEncoder encoder; // hidden
}

// SETTER injection — for optional dependencies only
@Service
class UserServiceOkay {
  private MetricsRecorder metrics;

  @Autowired(required = false) // optional
  public void setMetrics(MetricsRecorder m) {
    this.metrics = m;
  }
}

// CONSTRUCTOR injection — ALWAYS prefer this
@Service
class UserService {
  private final UserRepository repo;
  private final PasswordEncoder encoder;

  // @Autowired optional for single constructor (Spring 4.3+)
  public UserService(UserRepository repo,
                     PasswordEncoder encoder) {
    this.repo    = Objects.requireNonNull(repo);
    this.encoder = Objects.requireNonNull(encoder);
    // Immutable, explicit, testable
  }
}
```

**Example 2 — Testing with constructor injection (zero Spring magic):**

```java
class UserServiceTest {
  private UserService service;
  private UserRepository mockRepo;

  @BeforeEach
  void setUp() {
    mockRepo = mock(UserRepository.class);
    var encoder = new BCryptPasswordEncoder();
    // Pure Java — no @SpringBootTest, no context startup
    service = new UserService(mockRepo, encoder);
  }

  @Test
  void registerUser_shouldEncodePassword() {
    service.register(new RegisterRequest("a@b.com", "pass"));
    verify(mockRepo).save(argThat(u ->
        !u.getPassword().equals("pass") // encoded
    ));
  }
}
```

**Example 3 — Injecting multiple implementations by qualifier:**

```java
// Two implementations of same interface
@Component("stripeGateway")
class StripePaymentGateway implements PaymentGateway {...}

@Component("paypalGateway")
class PayPalPaymentGateway implements PaymentGateway {...}

// Inject specific implementation by name
@Service
class CheckoutService {
  public CheckoutService(
      @Qualifier("stripeGateway") PaymentGateway gw) {
    this.gateway = gw;
  }
}
```

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| Field injection and constructor injection are equivalent | Field injection hides dependencies, prevents final fields, breaks non-Spring unit tests, and can cause NullPointerExceptions if Spring hasn't run |
| DI requires a framework | DI is achievable in plain Java — just pass dependencies via constructors. Spring automates discovery and wiring at scale |
| @Autowired on a constructor is mandatory | Since Spring 4.3, a single-constructor class is auto-detected — @Autowired is not needed on the constructor |
| DI makes code harder to trace | Constructor injection makes the full dependency graph explicit and visible in the source — easier to trace than scattered new calls |
| All bean types should use DI | Value objects, DTOs, and domain entities created transiently should use new — only application-layer beans need container-managed injection |

---

### 🔥 Pitfalls in Production

**1. Optional dependency NPE when not checking for null**

```java
// BAD: optional dep used without null check
@Service
class NotificationService {
  @Autowired(required = false)
  private SmsProvider smsProvider;

  public void notify(String msg) {
    smsProvider.send(msg); // NPE if SMS not configured!
  }
}

// GOOD: null-safe use of optional dependency
public void notify(String msg) {
  if (smsProvider != null) {
    smsProvider.send(msg);
  }
  emailFallback.send(msg); // always falls through to email
}
// Or use Optional<SmsProvider> injection
```

**2. Injecting Spring ApplicationContext directly instead of specific beans**

```java
// BAD: Service Locator anti-pattern hidden in DI
@Service
class OrderService {
  @Autowired ApplicationContext ctx; // pulls the entire container

  public void process(Order order) {
    // Dynamic lookup defeats the purpose of DI
    PaymentGateway gw = ctx.getBean(PaymentGateway.class);
    gw.charge(order);
  }
}

// GOOD: declare the specific dependency in constructor
@Service
class OrderService {
  private final PaymentGateway gateway;
  public OrderService(PaymentGateway gateway) {
    this.gateway = gateway;
  }
}
```

---

### 🔗 Related Keywords

- `IoC` — the overarching principle; DI is the implementation mechanism
- `@Autowired` — Spring's annotation for declaring injection points
- `ApplicationContext` — the container that performs the actual injection
- `@Qualifier` — resolves ambiguity when multiple beans match an injection point
- `Bean` — the objects the container creates and injects
- `Unit Testing` — the primary beneficiary of constructor DI: no Spring context needed for tests

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ KEY IDEA     │ Dependencies provided externally at       │
│              │ construction — declare needs, don't build  │
├──────────────┼───────────────────────────────────────────┤
│ USE WHEN     │ Always prefer constructor injection;      │
│              │ setter for optional; never field inject   │
├──────────────┼───────────────────────────────────────────┤
│ AVOID WHEN   │ Value objects / DTOs — use new instead    │
│              │ Field injection — hides dependencies      │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "Don't build your tools —                 │
│              │  have them delivered to your door."       │
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ ApplicationContext (105) → Bean (107) →   │
│              │ @Autowired (112)                          │
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** Spring's DI container resolves injection by type. A large microservice has 3 different `MessageSender` implementations: `EmailSender`, `SmsSender`, `PushSender`. A `NotificationService` needs all three. Explain the type-resolution ambiguity and describe the three different Spring mechanisms for resolving it — `@Qualifier`, `@Primary`, and injecting a `List<MessageSender>` — including the specific scenario where each approach is the right choice and what the trade-off is.

**Q2.** Constructor injection creates immutable beans with `final` fields. But Spring also supports lazy-initialised beans (`@Lazy`) that are created only on first access. Explain the mechanism Spring uses to inject a `@Lazy` dependency into a constructor-injected bean — what object is actually passed to the constructor at startup, how the real bean is resolved on first method call, and why injecting a prototype-scoped bean into a singleton via a constructor is subtly different from `@Lazy` injection.

