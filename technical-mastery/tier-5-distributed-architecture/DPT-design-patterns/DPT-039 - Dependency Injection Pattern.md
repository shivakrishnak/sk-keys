---
id: DPT-039
title: Dependency Injection Pattern
category: Design Patterns
tier: tier-5-distributed-architecture
folder: DPT-design-patterns
difficulty: ★★☆
depends_on: DPT-001, DPT-005, DPT-027, DPT-038
used_by: DPT-064, DPT-073
related: DPT-038, DPT-027, DPT-073, DPT-078
tags:
  - pattern
  - creational
  - intermediate
  - spring
  - ioc
  - constructor-injection
  - testability
status: complete
version: 4
layout: default
parent: "Design Patterns"
grand_parent: "Technical Mastery"
nav_order: 39
permalink: /technical-mastery/design-patterns/dependency-injection/
---

⚡ TL;DR - Dependency Injection (DI) is a design pattern
where a class receives its dependencies from outside
(injected by the container or caller) rather than creating
them itself, making dependencies explicit, configurable,
and testable.

| #39 | Category: Design Patterns | Difficulty: ★★☆ |
|:---|:---|:---|
| **Depends on:** | DPT-001, DPT-005, DPT-027, DPT-038 | |
| **Used by:** | DPT-064, DPT-073 | |
| **Related:** | DPT-038, DPT-027, DPT-073, DPT-078 | |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
```java
class OrderService {
    private final EmailService emailService = new EmailService(
        "smtp.corp.example.com", 587, "user", "pass"); // hard-coded

    private final OrderRepository repo =
        new JdbcOrderRepository(
            DriverManager.getConnection(
                "jdbc:mysql://db:3306/orders", "root", "secret"));
                // hard-coded

    void placeOrder(Order order) {
        repo.save(order);
        emailService.sendConfirmation(order);
    }
}
```

**THE PROBLEMS:**
1. UNTESTABLE: cannot test `OrderService` without a real
   SMTP server and a real MySQL database.
2. NOT CONFIGURABLE: changing the email server or database
   requires recompiling `OrderService`.
3. VIOLATES OCP: adding a test double email service
   requires modifying `OrderService`.
4. HARD TO REASON ABOUT: `OrderService`'s dependencies
   are hidden inside method bodies, not visible at the
   class contract level.
5. LIFECYCLE ISSUES: `OrderService` owns the connection;
   who closes it? When?

**THE INVENTION MOMENT:**
Dependency Injection: `OrderService` declares what it
NEEDS (interfaces) as constructor parameters. Something
ELSE (the DI container, or the test itself) provides
the concrete implementations. `OrderService` is focused
purely on its responsibility (order processing).

---

### 📘 Textbook Definition

**Dependency Injection (DI)** is a design pattern in which
a class receives its dependencies (the objects it works
with) from an external source rather than creating them
itself. The pattern implements the Dependency Inversion
Principle: high-level modules depend on abstractions
(interfaces), not concrete implementations. In Java,
DI is typically implemented by frameworks (Spring, CDI)
that scan for dependency declarations (`@Autowired`,
constructor parameters) and inject the appropriate
implementations. Three injection modes: constructor
injection (recommended), setter injection, and field
injection (discouraged). DI is the modern replacement
for the Service Locator pattern.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
DI means "tell me what you need in your constructor;
I'll give it to you" instead of "go find what you need."

**One analogy:**
> A car factory (DI container) assembles cars (objects).
> The engine specification (interface) says: "I need a
> fuel injector and an alternator." The factory provides
> the specific parts (implementations) during assembly.
> The car design (class) says what it needs; the factory
> decides which specific parts to install. Testing: the
> factory installs mock parts (test doubles) for QA.

**One insight:**
Dependency Injection IS the Strategy pattern applied
to all of a class's dependencies. Each dependency is
a pluggable strategy. The constructor declares the
"strategy interfaces" it needs. The DI container
injects the right "strategy implementations."

---

### 🔩 First Principles Explanation

**THREE INJECTION MODES:**

**1. Constructor Injection (PREFERRED):**
```java
class OrderService {
    private final EmailService emailService;
    private final OrderRepository repository;

    // Dependencies declared in constructor: explicit, visible
    @Autowired // optional in Spring 4.3+ for single constructor
    OrderService(EmailService emailService,
        OrderRepository repository) {
        this.emailService  = Objects.requireNonNull(emailService);
        this.repository    = Objects.requireNonNull(repository);
    }
}
```
Dependencies: explicit in constructor signature. Immutable
(`final`). Null-safe (check at construction). Testable
without DI container (just `new OrderService(mock, mock)`).

**2. Setter Injection (USE ONLY FOR OPTIONAL DEPS):**
```java
class OrderService {
    private EmailService emailService; // not final, mutable

    @Autowired
    void setEmailService(EmailService emailService) {
        this.emailService = emailService;
    }
}
```
Problems: object can be used before `setEmailService()`
is called. Dependencies are not immutable.
Use: optional dependencies with defaults.

**3. Field Injection (AVOID IN PRODUCTION CODE):**
```java
class OrderService {
    @Autowired
    private EmailService emailService; // hidden, not final
}
```
Problems: cannot mock without DI container or Mockito
`@InjectMocks`. Dependencies are invisible in the
constructor. Cannot verify nullability at construction.
Only acceptable in test classes.

**IOC CONTAINER:**
The Inversion of Control (IoC) container (Spring's
`ApplicationContext`) is responsible for:
1. Scanning classes for `@Component`, `@Service`, etc.
2. Resolving the dependency graph (which beans depend on what).
3. Instantiating beans in the correct order.
4. Injecting dependencies into constructors/setters.
5. Managing lifecycles (`@PostConstruct`, `@PreDestroy`).

**TRADE-OFFS:**

**Gain:** Testable (inject mocks). Configurable (inject
different implementations for different environments).
Follows OCP, DIP. Centralized lifecycle management.
Explicit dependencies (via constructor injection).

**Cost:** Learning curve for DI framework. Startup time
(scanning, wiring). Complex multi-module dependency graphs
can be hard to debug. Circular dependencies cause
exceptions at startup.

---

### 🧪 Thought Experiment

**SETUP:**
Test `OrderService.placeOrder()` without hitting real infrastructure.

**WITHOUT DI:**
`OrderService` creates real `EmailService` and `JdbcRepository`.
Unit test sends real emails, hits real database. UNACCEPTABLE.

**WITH DI (constructor injection):**
```java
@Test
void placeOrder_shouldSaveAndSendEmail() {
    EmailService mockEmail = mock(EmailService.class);
    OrderRepository mockRepo = mock(OrderRepository.class);

    OrderService service = new OrderService(mockEmail, mockRepo);
    service.placeOrder(testOrder);

    verify(mockRepo).save(testOrder);
    verify(mockEmail).sendConfirmation(testOrder);
}
```
No DI container needed. No real infrastructure. Pure unit test.

---

### 🧠 Mental Model / Analogy

> DI is CATERING FOR AN EVENT. You (the class) say "I need
> appetizers, a main course, and dessert." The caterer
> (DI container) provides: for a formal dinner (production)
> = real courses; for a rehearsal (testing) = sample
> dishes. You focus on running the event. The caterer
> handles food sourcing. You never enter the kitchen.

- "What you need" = constructor parameter types
- "Caterer" = Spring DI container
- "Provides formal/rehearsal food" = real bean vs test mock
- "You focus on the event" = class focuses on its responsibility
- "Never entering the kitchen" = never creating dependencies via `new`

---

### 📶 Gradual Depth - Five Levels

**Level 1 - What it is (anyone can understand):**
DI means a class gets its tools handed to it when it's
created, rather than going to get the tools itself.
If you need a hammer and a screwdriver to build a bookshelf,
DI means someone gives you the hammer and screwdriver.
Without DI: you'd have to find the toolbox yourself.

**Level 2 - How to use it (junior developer):**
In Spring: annotate class with `@Service` or `@Component`.
Declare dependencies in the constructor. Spring creates
the class and provides the dependencies automatically.
In tests: use `new MyClass(mockDep1, mockDep2)` to
inject test doubles without Spring context. ALWAYS prefer
constructor injection.

**Level 3 - How it works (mid-level engineer):**
Spring Boot's auto-scanning: `@SpringBootApplication`
triggers component scan. Spring BeanFactory scans all
classes annotated with `@Component`, `@Service`, `@Repository`,
`@Controller`. It builds a `BeanDefinition` graph.
For each bean: resolves constructor parameters to
other beans. Creates beans in dependency order (leaf
beans first). If circular dependency: Spring throws
`BeanCurrentlyInCreationException` at startup (fail-fast).
`@Scope("prototype")`: new instance per injection.
`@Scope("singleton")`: shared instance (default).
`@Qualifier("beanName")`: choose among multiple
implementations of the same interface.

**Level 4 - Why it was designed this way (senior/staff):**
DI implements the Dependency Inversion Principle (DIP):
"High-level modules should not depend on low-level modules.
Both should depend on abstractions. Abstractions should
not depend on details." In DI terms: `OrderService`
(high-level) depends on `EmailService` (interface, abstraction).
`GmailEmailService` and `MockEmailService` (low-level
details) implement the abstraction. `OrderService` never
imports `GmailEmailService`. The DI container chooses
which detail to inject. This is why DI is foundational
to layered architecture: domain services depend only
on repository interfaces (defined in the domain layer);
the infrastructure layer provides the implementations.
Domain imports nothing from infrastructure; infrastructure
imports the interfaces from domain.

**Level 5 - Mastery (distinguished engineer):**
DI is not just a testing convenience - it is the
enforcement mechanism for the Dependency Inversion
Principle at the class level. When taken to the
architectural level: Hexagonal Architecture (Ports
and Adapters) uses DI to enforce that the domain (core)
imports no infrastructure. The domain defines "ports"
(interfaces: `OrderRepository`, `EmailPort`). The infrastructure
layer implements "adapters" (classes: `JpaOrderRepository`,
`SmtpEmailAdapter`). DI injects the adapters into the
domain at runtime. The domain package can be compiled
and tested without any infrastructure dependency. This
architectural purity is testable: a pure domain unit
test has zero classpath dependencies on Spring, JPA,
or SMTP libraries. DI is the runtime mechanism; the
architectural principle is DIP. Without DI: DIP is
aspirational. With DI: DIP is enforced by the compiler
(if you try to import `JpaOrderRepository` into the
domain, the build fails because the dependency is inverted).

---

### ⚙️ How It Works (Mechanism)

```
Spring DI Lifecycle
┌─────────────────────────────────────────────────────────┐
│ Application startup:                                    │
│   1. @ComponentScan: finds all @Service/@Component beans│
│   2. Creates BeanDefinitions (metadata: class, scope,   │
│      constructor params, lifecycle callbacks)           │
│   3. Resolves dependency order (topological sort of DAG)│
│   4. Instantiates beans:                                │
│      new OrderService(emailBean, repoBean)              │
│   5. @PostConstruct: lifecycle init callbacks           │
│   6. Application is ready                               │
│                                                         │
│ Circular dependency detection:                          │
│   A needs B, B needs A → BeanCurrentlyInCreationExceptio│
│   (fails at startup, not at runtime)                    │
│                                                         │
│ @Qualifier for multiple implementations:                │
│   @Service("gmailEmailService") class GmailEmailService │
│   @Service("mockEmailService")  class MockEmailService  │
│                                                         │
│   @Autowired @Qualifier("gmailEmailService")            │
│   EmailService emailService; ← Spring picks gmailBean   │
└─────────────────────────────────────────────────────────┘
```

---

### 🔄 The Complete Picture - End-to-End Flow

```
Order service wiring in Spring Boot:

@Service
class OrderService {
    private final EmailService email;
    private final OrderRepository repo;

    OrderService(EmailService email, OrderRepository repo)
      {
        this.email = email;
        this.repo = repo;
    }
}

@Service
class GmailEmailService implements EmailService { ... }

@Repository
class JpaOrderRepository implements OrderRepository { ... }

Spring Boot startup:
  1. Scans: finds OrderService, GmailEmailService,
    JpaOrderRepository
  2. OrderService needs: EmailService, OrderRepository
  3. EmailService → GmailEmailService (only impl)
  4. OrderRepository → JpaOrderRepository (only impl)
  5. Creates: new OrderService(gmailEmailService,
    jpaOrderRepo)
  6. All beans wired

Unit test (no Spring, no infrastructure):
  OrderService svc = new
    OrderService(mock(EmailService.class),
                                      mock(OrderRepository.
  svc.placeOrder(order);
  verify(mock).save(order);
```

---

### 💻 Code Example

**Example 1 - Constructor injection vs field injection:**

```java
// BAD: field injection (hidden deps, not testable without container)
@Service
class BadOrderService {
    @Autowired
    private EmailService email;  // hidden, not final

    @Autowired
    private OrderRepository repo; // hidden, not final

    void placeOrder(Order o) {
        repo.save(o);
        email.sendConfirmation(o);
    }
    // Test: must use @SpringBootTest or @MockBean with Mockito
    // @InjectMocks
    // Cannot use simple new BadOrderService() in tests
}
```

```java
// GOOD: constructor injection (explicit, immutable, testable)
@Service
class OrderService {
    private final EmailService email;       // immutable
    private final OrderRepository repo;     // immutable

    // Spring 4.3+: @Autowired optional for single constructor
    OrderService(EmailService email, OrderRepository repo) {
        this.email = Objects.requireNonNull(email,
            "EmailService must not be null");
        this.repo  = Objects.requireNonNull(repo,
            "OrderRepository must not be null");
    }

    void placeOrder(Order order) {
        repo.save(order);
        email.sendConfirmation(order);
    }
}

// Test: zero Spring context overhead
@Test
void placeOrder_savesAndSendsEmail() {
    EmailService mockEmail = mock(EmailService.class);
    OrderRepository mockRepo = mock(OrderRepository.class);

    OrderService service = new OrderService(mockEmail, mockRepo);
    service.placeOrder(testOrder);

    verify(mockRepo).save(testOrder);
    verify(mockEmail).sendConfirmation(testOrder);
}
```

**Example 2 - Multiple implementations + @Qualifier:**

```java
// Two implementations of EmailService
@Service("smtpEmailService")
class SmtpEmailService implements EmailService {
    @Override
    public void sendConfirmation(Order order) { /* SMTP */ }
}

@Service("sendGridEmailService")
class SendGridEmailService implements EmailService {
    @Override
    public void sendConfirmation(Order order) { /* SendGrid API */ }
}

// Inject specific implementation
@Service
class OrderService {
    private final EmailService email;

    OrderService(
            @Qualifier("sendGridEmailService") EmailService email,
            OrderRepository repo) {
        this.email = email;
        this.repo  = repo;
    }
}

// Or: @ConditionalOnProperty for environment-based selection
@Service
@ConditionalOnProperty(name = "email.provider",
    havingValue = "sendgrid")
class SendGridEmailService implements EmailService { ... }
```

**Example 3 - @Configuration for complex wiring:**

```java
// @Configuration: explicit bean creation with complex setup
@Configuration
class DataConfig {

    @Bean
    DataSource dataSource(
            @Value("${db.url}") String url,
            @Value("${db.user}") String user,
            @Value("${db.password}") String pass) {
        // Complex initialization not possible with @Service
        HikariConfig config = new HikariConfig();
        config.setJdbcUrl(url);
        config.setUsername(user);
        config.setPassword(pass);
        config.setMaximumPoolSize(20);
        config.setConnectionTimeout(3000);
        return new HikariDataSource(config);
    }

    @Bean
    OrderRepository orderRepository(DataSource dataSource) {
        return new JpaOrderRepository(dataSource);
    }
}
```

**Example 4 - Circular dependency prevention:**

```java
// Circular dependency: A depends on B, B depends on A
@Service class A {
    A(B b) {} // A needs B
}

@Service class B {
    B(A a) {} // B needs A
}
// Spring: BeanCurrentlyInCreationException at startup
// GOOD: detects the problem at startup, not at runtime

// Fix option 1: extract shared logic to C, both depend on C
// Fix option 2: one dependency uses @Lazy (lazy proxy)
@Service class B {
    B(@Lazy A a) {} // A is lazily initialized (proxy injected)
}
// Fix option 3: redesign - circular deps indicate design problem
```

---

### ⚖️ Comparison Table

| Injection Type | Immutability | Testability | Visibility | Spring recommendation |
|---|---|---|---|---|
| Constructor | Yes (final) | Best (just new()) | Explicit | PREFERRED |
| Setter | No | Good (call setter) | Ok | Optional deps only |
| Field | No | Poor (needs container) | Hidden | AVOID in prod |

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| @Autowired on field is the same as constructor injection | Field injection hides dependencies, prevents immutability, and requires a DI container to test. Constructor injection is visible, immutable, and testable without a container. They are NOT equivalent |
| DI requires Spring | DI is a design pattern. Constructor injection is just "declare what you need in the constructor." Spring is a DI CONTAINER that automates the injection. You can use DI without Spring: just wire dependencies manually in `main()` or in a factory |
| More @Autowired annotations = more DI | Too many injected dependencies in one class indicates a Single Responsibility violation. If a class needs 8 @Autowired fields: split the class. A class needing 3-4 dependencies is typical; more than 5 is a design smell |
| DI containers add significant startup overhead | Spring Boot's startup overhead is primarily classpath scanning and bean initialization (often 1-5 seconds for medium apps). This is one-time cost at startup. Request-level overhead is negligible (beans are pre-wired) |

---

### 🚨 Failure Modes & Diagnosis

**BeanCurrentlyInCreationException (Circular Dependency)**

**Symptom:**
Spring fails at startup with:
`BeanCurrentlyInCreationException: Error creating bean 'orderService':
Requested bean is currently in creation: Is there an
unresolvable circular reference?`

**Root Cause:**
`OrderService` depends on `PaymentService`; `PaymentService`
depends on `OrderService`. Spring cannot create either
without the other.

**Diagnosis:**
Read the exception message: it lists the bean names in
the cycle. `OrderService → PaymentService → OrderService`.

**Fix:**
1. Redesign: extract a shared dependency `OrderEventPublisher`
   that both services use, breaking the cycle.
2. `@Lazy` on one injection point: `@Lazy @Autowired
   PaymentService payment;` - injects a proxy, resolved
   lazily on first use.
3. Use setter injection for one direction (breaks the
   initialization cycle, not ideal).

---

**NoUniqueBeanDefinitionException (Multiple Implementations)**

**Symptom:**
`NoUniqueBeanDefinitionException: expected single matching
bean but found 2: smtpEmailService, sendGridEmailService`

**Root Cause:**
Two beans implement `EmailService`. Spring cannot choose.

**Fix:**
```java
// Option 1: @Qualifier on injection point
@Autowired
@Qualifier("sendGridEmailService")
EmailService email;

// Option 2: @Primary on the default implementation
@Service
@Primary
class SendGridEmailService implements EmailService { ... }

// Option 3: @ConditionalOnProperty for environment-based selection
```

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**
- `Service Locator` - DPT-038; DI is the superior
  alternative to Service Locator; understand both
- `Strategy` - DPT-027; DI is Strategy applied to
  all dependencies of a class

**Builds On This (learn these next):**
- `Dependency Inversion Principle` - DPT-078; DI is
  the runtime mechanism that enforces DIP at compile
  time via interface-based dependencies

---

### 📌 Quick Reference Card

```
┌─────────────────────────────────────────────────────────┐
│ WHAT IT IS   │ Receive dependencies from outside (PUSH) │
│              │ not fetch them from registry (PULL)      │
├──────────────┼──────────────────────────────────────────┤
│ RULE 1       │ Constructor injection ALWAYS; avoid field│
│              │ injection in production code             │
├──────────────┼──────────────────────────────────────────┤
│ RULE 2       │ Never call new() for dependencies inside │
│              │ a class that is managed by Spring        │
├──────────────┼──────────────────────────────────────────┤
│ CIRCULAR DEP │ BeanCurrentlyInCreationException at start│
│              │ = circular dependency; redesign or @Lazy │
├──────────────┼──────────────────────────────────────────┤
│ MULTIPLE IMPL│ @Qualifier or @Primary to resolve        │
│              │ NoUniqueBeanDefinitionException          │
├──────────────┼──────────────────────────────────────────┤
│ NEXT EXPLORE │ Specification Pattern → CQRS → Outbox    │
└─────────────────────────────────────────────────────────┘
```

**If you remember only 3 things:**
1. Constructor injection is ALWAYS preferred: makes dependencies
   explicit (visible in constructor), immutable (`final`),
   and testable without a DI container (`new MyClass(mock, mock)`).
   Field injection (`@Autowired` on a field) hides dependencies
   and prevents immutability.
2. DI is the Strategy pattern applied to all class dependencies.
   Each `@Autowired` dependency is a pluggable strategy
   that can be swapped (test double in tests, different
   implementation in a different environment).
3. DI implements the Dependency Inversion Principle: high-level
   modules depend on interfaces (abstractions), not concrete
   classes. Spring injects the concrete class at runtime.
   This allows domain code to be compiled and tested without
   any infrastructure dependency.

