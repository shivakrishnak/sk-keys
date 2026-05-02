---
layout: default
title: "Dependency Injection"
parent: "Design Patterns"
nav_order: 796
permalink: /design-patterns/dependency-injection/
number: "796"
category: Design Patterns
difficulty: ★★☆
depends_on: "Object-Oriented Programming, Inversion of Control, Open-Closed Principle, Strategy Pattern"
used_by: "Spring Framework, testing, modular design, loose coupling"
tags: #intermediate, #design-patterns, #creational, #solid, #spring, #ioc, #testability
---

# 796 — Dependency Injection

`#intermediate` `#design-patterns` `#creational` `#solid` `#spring` `#ioc` `#testability`

⚡ TL;DR — **Dependency Injection** removes a class's responsibility for creating its own dependencies — instead they are provided ("injected") from outside, enabling loose coupling, substitutability, and testability without modifying the class.

| #796            | Category: Design Patterns                                                                  | Difficulty: ★★☆ |
| :-------------- | :----------------------------------------------------------------------------------------- | :-------------- |
| **Depends on:** | Object-Oriented Programming, Inversion of Control, Open-Closed Principle, Strategy Pattern |                 |
| **Used by:**    | Spring Framework, testing, modular design, loose coupling                                  |                 |

---

### 📘 Textbook Definition

**Dependency Injection (DI)** (Martin Fowler, 2004; originally termed "Inversion of Control" by Robert C. Martin): a design pattern where a class receives its dependencies from external sources rather than creating them internally. The class declares what it needs; a container or caller provides it. DI is a specific form of IoC (Inversion of Control): instead of the class controlling its own dependencies' lifecycle, control is inverted to an external assembler. Types: **Constructor injection** (preferred; dependencies passed via constructor); **Setter injection** (optional dependencies); **Field injection** (via reflection, convenient but less testable). Java: Spring Framework's `ApplicationContext` is the IoC container. CDI (Jakarta), Guice (Google), Dagger (Android).

---

### 🟢 Simple Definition (Easy)

A car that needs a battery. Without DI: car manufactures its own battery (`new Battery()`). With DI: car asks for a battery in its constructor — whoever builds the car provides the battery. The car works with any battery that fits. To test the car: give it a mock battery. To swap to a better battery: no changes to the car. DI: don't build your dependencies — ask for them.

---

### 🔵 Simple Definition (Elaborated)

`OrderService` needs `OrderRepository` and `EmailService`. Without DI: `this.repo = new JdbcOrderRepository(dataSource)` — hard-wired. With DI: `OrderService(OrderRepository repo, EmailService email)` — constructor declares needs. Spring provides the implementations. In tests: `new OrderService(mockRepo, mockEmail)` — inject mocks. In production: Spring injects real implementations. `OrderService` never changes regardless of which implementations are used.

---

### 🔩 First Principles Explanation

**How DI decouples class from instantiation and enables substitution:**

```
WITHOUT DI — HARD-WIRED DEPENDENCIES:

  class OrderService {
      private final JdbcOrderRepository repo;    // concrete class!
      private final SmtpEmailService email;      // concrete class!
      private final StripePaymentGateway payment; // concrete class!

      OrderService() {
          // Service creates its own dependencies — tightly coupled:
          DataSource ds = new HikariDataSource(jdbcConfig());
          this.repo    = new JdbcOrderRepository(ds);
          this.email   = new SmtpEmailService("smtp.gmail.com", 587, "user", "pass");
          this.payment = new StripePaymentGateway("sk_live_abc123");
      }
  }
  // Problems:
  // ✗ To test OrderService: must have real DB, real SMTP, real Stripe connection.
  // ✗ To swap MySQL → Postgres: modify OrderService.
  // ✗ To change email provider: modify OrderService.
  // ✗ OrderService violates SRP: also responsible for building its dependencies.

WITH DEPENDENCY INJECTION — CONSTRUCTOR INJECTION:

  class OrderService {
      private final OrderRepository repo;      // interface!
      private final EmailService email;        // interface!
      private final PaymentGateway payment;   // interface!

      // Constructor DECLARES what's needed; assembler provides it:
      OrderService(OrderRepository repo, EmailService email, PaymentGateway payment) {
          this.repo    = Objects.requireNonNull(repo);
          this.email   = Objects.requireNonNull(email);
          this.payment = Objects.requireNonNull(payment);
      }

      void processOrder(Order order) {
          repo.save(order);
          payment.charge(order.getTotal(), order.getPaymentMethod());
          email.sendConfirmation(order.getCustomerEmail(), order.getId());
      }
  }

  // PRODUCTION WIRING (Spring):
  @Configuration
  class Config {
      @Bean OrderRepository orderRepository(DataSource ds) {
          return new JdbcOrderRepository(ds);
      }
      @Bean EmailService emailService() {
          return new SmtpEmailService(smtpProps());
      }
      @Bean PaymentGateway paymentGateway() {
          return new StripePaymentGateway(stripeApiKey());
      }
      @Bean OrderService orderService(OrderRepository r, EmailService e, PaymentGateway p) {
          return new OrderService(r, e, p);   // Spring calls this; all deps auto-resolved
      }
  }

  // TESTING — inject mocks:
  @Test
  void shouldSendEmailAfterOrder() {
      OrderRepository mockRepo    = mock(OrderRepository.class);
      EmailService mockEmail      = mock(EmailService.class);
      PaymentGateway mockPayment  = mock(PaymentGateway.class);

      OrderService service = new OrderService(mockRepo, mockEmail, mockPayment);

      Order order = new Order("customer@test.com", new BigDecimal("50.00"));
      service.processOrder(order);

      verify(mockEmail).sendConfirmation("customer@test.com", order.getId());
      // No real DB, no real SMTP, no real Stripe — fast, isolated unit test.
  }

SPRING DI — ANNOTATIONS:

  @Service  // Spring creates and manages this bean
  class OrderService {

      private final OrderRepository repo;
      private final EmailService email;

      @Autowired  // Spring injects matching beans (optional on single-constructor)
      OrderService(OrderRepository repo, EmailService email) {
          this.repo  = repo;
          this.email = email;
      }

      // Single-constructor: @Autowired is implicit in Spring 4.3+:
      // Just: OrderService(OrderRepository repo, EmailService email) { ... }
  }

  // Spring scans @Service, @Repository, @Component classes.
  // Builds dependency graph. Instantiates in dependency order.
  // Resolves @Autowired via type matching (and @Qualifier for ambiguity).

INJECTION TYPES — PROS AND CONS:

  CONSTRUCTOR INJECTION (PREFERRED):
  @Service
  class OrderService {
      private final OrderRepository repo;  // final: immutable after construction

      OrderService(OrderRepository repo) { this.repo = repo; }  // explicit, required deps
  }
  ✓ Dependencies explicit (contract clear)
  ✓ Fields can be final (immutable)
  ✓ Easy unit testing (just call constructor)
  ✓ Circular dependencies detected at startup (Spring exception)

  SETTER INJECTION (optional deps):
  @Service
  class OrderService {
      private EmailService email;

      @Autowired(required = false)
      void setEmailService(EmailService email) { this.email = email; }
  }
  ✓ Optional dependencies that may not always be available
  ✗ Object may be in incomplete state if setter not called

  FIELD INJECTION (convenient but discouraged):
  @Service
  class OrderService {
      @Autowired private OrderRepository repo;  // injected via reflection
  }
  ✓ Concise
  ✗ Cannot make final (mutable)
  ✗ Cannot test without Spring container or reflection hacks
  ✗ Hides dependencies (not in constructor — not obvious what's needed)
  ✗ Circular dependencies not detected early

DI vs SERVICE LOCATOR:

  SERVICE LOCATOR (anti-pattern for most uses):
  class OrderService {
      void processOrder(Order order) {
          OrderRepository repo = ServiceLocator.get(OrderRepository.class); // hidden dep
          repo.save(order);
      }
  }
  ✗ Dependencies hidden inside method bodies
  ✗ Hard to test (must configure ServiceLocator in tests)
  ✗ Tight coupling to the locator

  DI: dependencies explicit in constructor — preferred.
```

---

### ❓ Why Does This Exist (Why Before What)

WITHOUT DI:

- Classes create dependencies: `new EmailService(...)` inside business logic
- Testing requires real infrastructure; swapping implementations requires code changes

WITH DI:
→ Dependencies declared, not created. Tests inject mocks. Spring wires production implementations. Business logic stays clean and substitutable.

---

### 🧠 Mental Model / Analogy

> A chef at a restaurant. The chef (class) needs: knives, pans, ingredients. Without DI: chef goes shopping, buys all equipment, sources ingredients — chef responsible for sourcing everything. With DI: the restaurant (container/assembler) equips the kitchen: provides knives, pans, ingredients before the chef starts cooking. Chef just cooks. New ingredients (implementation swap): restaurant provides them — chef doesn't change their cooking process.

"Chef" = your class (OrderService)
"Knives, pans, ingredients" = dependencies (OrderRepository, EmailService)
"Chef goes shopping" = class creates own dependencies (`new JdbcOrderRepository()`)
"Restaurant equips kitchen" = DI container (Spring) injects dependencies
"Chef just cooks" = class focuses on its own responsibility
"Different ingredients, same recipe" = swap implementations — class unchanged

---

### ⚙️ How It Works (Mechanism)

```
DI CONTAINER LIFECYCLE (SPRING):

  1. Scan: find @Component, @Service, @Repository, @Controller classes
  2. Build dependency graph: which beans depend on which
  3. Instantiate in dependency order (resolve topological sort)
  4. Inject: call constructors with resolved dependencies
  5. Post-process: @PostConstruct, BeanPostProcessor
  6. Serve: beans available from ApplicationContext

  Scope:
  @Scope("singleton") (default): one instance per ApplicationContext
  @Scope("prototype"): new instance per injection
  @RequestScope: one instance per HTTP request
  @SessionScope: one instance per HTTP session
```

---

### 🔄 How It Connects (Mini-Map)

```
Remove class's responsibility for creating dependencies; inject from outside
        │
        ▼
Dependency Injection ◄──── (you are here)
(constructor/setter/field injection; IoC container manages lifecycle)
        │
        ├── Strategy Pattern: DI injects the right Strategy implementation at runtime
        ├── Inversion of Control: DI is a specific form of IoC
        ├── Factory Method: DI container uses factories to create beans
        └── Open-Closed Principle: DI enables OCP — swap implementations without modifying clients
```

---

### 💻 Code Example

```java
// Constructor injection — Spring Boot style:
@Service
public class OrderService {
    private final OrderRepository orderRepository;
    private final PaymentGateway paymentGateway;
    private final OrderEventPublisher eventPublisher;

    // Spring 4.3+: single constructor — @Autowired implicit
    public OrderService(OrderRepository orderRepository,
                        PaymentGateway paymentGateway,
                        OrderEventPublisher eventPublisher) {
        this.orderRepository = orderRepository;
        this.paymentGateway  = paymentGateway;
        this.eventPublisher  = eventPublisher;
    }

    @Transactional
    public Order placeOrder(PlaceOrderCommand cmd) {
        Order order = Order.from(cmd);
        orderRepository.save(order);
        paymentGateway.charge(order.getTotal(), cmd.paymentDetails());
        eventPublisher.publish(new OrderPlacedEvent(order));
        return order;
    }
}

// Test — zero Spring, zero infrastructure:
class OrderServiceTest {
    @Test void shouldChargePaymentOnOrderPlacement() {
        var repo      = mock(OrderRepository.class);
        var gateway   = mock(PaymentGateway.class);
        var publisher = mock(OrderEventPublisher.class);
        var service   = new OrderService(repo, gateway, publisher);  // plain constructor

        service.placeOrder(new PlaceOrderCommand("customer", new BigDecimal("99.00"), ...));

        verify(gateway).charge(eq(new BigDecimal("99.00")), any());
    }
}
```

---

### ⚠️ Common Misconceptions

| Misconception                                         | Reality                                                                                                                                                                                                                                                                                                                                                                           |
| ----------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| DI requires a framework (Spring, Guice)               | DI is a design principle, not a framework requirement. Manual DI (poor man's DI): just pass dependencies in constructors — no framework needed. `new OrderService(new JdbcOrderRepository(ds), new SmtpEmailService(...))`. Frameworks (Spring, Guice) automate the wiring for large numbers of beans. Small services or applications can use manual DI effectively.              |
| Field injection (@Autowired on field) is equally good | Field injection is strongly discouraged. It hides dependencies (not visible in constructor), prevents `final` fields (mutability risk), makes unit testing harder (requires Spring context or reflection), and can mask circular dependencies. Constructor injection is the Java community consensus for good reason. Even Spring's own team recommends constructor injection.    |
| DI is only useful for swapping implementations        | DI has multiple benefits: testability (inject mocks), lifecycle management (container manages singletons), loose coupling (depend on interfaces), and discoverability (constructor signature documents requirements). Even if you never swap an implementation, constructor injection makes your code more testable and your dependencies explicit — both valuable independently. |

---

### 🔥 Pitfalls in Production

**Circular dependencies with constructor injection:**

```java
// CIRCULAR DEPENDENCY: A depends on B, B depends on A — Spring throws at startup:
@Service
class ServiceA {
    ServiceA(ServiceB b) { ... }  // A needs B
}

@Service
class ServiceB {
    ServiceB(ServiceA a) { ... }  // B needs A — CIRCULAR!
}
// Spring startup: BeanCurrentlyInCreationException
// "The dependencies of some of the beans in the application context form a cycle"

// This is actually GOOD — circular dependency usually indicates design problem.
// Common causes: God classes, missing abstraction.

// FIX 1: Refactor — extract shared functionality to a third service C:
@Service class ServiceC { ... }  // shared behavior extracted here
@Service class ServiceA { ServiceA(ServiceC c) { ... } }
@Service class ServiceB { ServiceB(ServiceC c) { ... } }

// FIX 2: Setter injection (breaks circular, but hides the design smell):
@Service
class ServiceA {
    private ServiceB b;
    @Autowired void setB(ServiceB b) { this.b = b; }  // Spring injects after construction
}

// FIX 3: Use ApplicationContext to look up lazily (last resort):
@Service
class ServiceA {
    @Autowired ApplicationContext ctx;
    ServiceB getB() { return ctx.getBean(ServiceB.class); }
}
// ONLY if refactoring is not possible. Prefer fixing the design.
```

---

### 🔗 Related Keywords

- `Inversion of Control` — DI is the most common form of IoC: container controls dependency lifecycle
- `Strategy Pattern` — DI injects the right strategy/implementation at runtime
- `Open-Closed Principle` — DI enables classes to be open for extension (swap impl) without modification
- `Spring Framework` — Java's dominant DI container; manages bean lifecycle, wiring, scoping
- `Factory Method` — IoC containers use factories internally to create and manage bean instances

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ KEY IDEA     │ Don't create dependencies — declare them. │
│              │ Container/caller provides implementations.│
│              │ Business logic stays clean and testable.  │
├──────────────┼───────────────────────────────────────────┤
│ USE WHEN     │ Want to swap implementations; need unit  │
│              │ tests without infrastructure; building   │
│              │ modular, loosely-coupled systems         │
├──────────────┼───────────────────────────────────────────┤
│ AVOID WHEN   │ Simple scripts; utility classes with no  │
│              │ state; when DI framework overhead is not │
│              │ justified (tiny apps)                    │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "Restaurant kitchen: chef just cooks —   │
│              │  restaurant provides knives, ingredients;│
│              │  chef doesn't go shopping."              │
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ Inversion of Control → Spring Framework →│
│              │ Strategy Pattern → Open-Closed Principle  │
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** Spring's `@Autowired` resolves dependencies by type. When there are multiple beans implementing the same interface (e.g., two `PaymentGateway` implementations: `StripeGateway` and `PayPalGateway`), Spring throws `NoUniqueBeanDefinitionException`. Disambiguation tools: `@Primary` (one default), `@Qualifier("stripe")` (explicit name), `@ConditionalOnProperty` (active based on config), or injecting a `List<PaymentGateway>` (all implementations). How does the `List<PaymentGateway>` injection pattern relate to the Strategy pattern? When is each disambiguation approach most appropriate?

**Q2.** Constructor injection enforces that dependencies are non-null at construction time (assuming you add `Objects.requireNonNull()` checks). This means if Spring fails to find a bean to inject, the application FAILS AT STARTUP rather than failing at runtime when the first request uses the missing dependency. How does this "fail-fast" behavior improve production reliability compared to field injection (which can inject null if the bean isn't found)? What Spring property (`spring.main.fail-on-error`) relates to this concept?
