---
layout: default
title: "Dependency Injection Pattern"
parent: "Software Architecture Patterns"
nav_order: 762
permalink: /software-architecture/dependency-injection-pattern/
number: "762"
category: Software Architecture Patterns
difficulty: ★★☆
depends_on: "SOLID Principles, Cohesion and Coupling, Inversion of Control"
used_by: "Spring, Guice, Angular, Testability, Clean Architecture"
tags: #intermediate, #architecture, #ioc, #spring, #testability
---

# 762 — Dependency Injection Pattern

`#intermediate` `#architecture` `#ioc` `#spring` `#testability`

⚡ TL;DR — **Dependency Injection (DI)** inverts who creates an object's dependencies — instead of an object creating its own collaborators with `new`, they are provided (injected) from outside — enabling swappable implementations, loose coupling, and easy testing with mocks.

| #762            | Category: Software Architecture Patterns                      | Difficulty: ★★☆ |
| :-------------- | :------------------------------------------------------------ | :-------------- |
| **Depends on:** | SOLID Principles, Cohesion and Coupling, Inversion of Control |                 |
| **Used by:**    | Spring, Guice, Angular, Testability, Clean Architecture       |                 |

---

### 📘 Textbook Definition

**Dependency Injection (DI)** (Robert Martin, Martin Fowler — formalized in Fowler's "Inversion of Control Containers and the Dependency Injection pattern," 2004): a design pattern implementing the Dependency Inversion Principle (SOLID-D) in which an object receives (is injected with) its dependencies from an external source rather than creating them itself. Three forms: (1) **Constructor injection** — dependencies passed as constructor parameters; (2) **Setter injection** — dependencies set via setter methods after construction; (3) **Interface injection** — object implements an interface through which the injector passes dependencies. A **DI container** (Spring, Guice, Angular's DI, .NET's IServiceCollection) automates the wiring: registers implementations → resolves the dependency graph → injects into each object. DI is not the same as Inversion of Control (IoC) — IoC is the broader principle; DI is one specific implementation of it.

---

### 🟢 Simple Definition (Easy)

A lamp vs. a hard-wired light. Hard-wired (no DI): the light bulb is soldered inside the lamp. Replace it: disassemble the lamp. The lamp and bulb are inseparable. Socket (DI): the lamp has a socket. You plug in any E27 bulb. LED, incandescent, smart bulb — the lamp doesn't care. Testing: plug in a dim testing bulb. Production: plug in the bright LED. The lamp's behavior (socket interface) never changes; the bulb (dependency) is swappable.

---

### 🔵 Simple Definition (Elaborated)

`OrderService` needs to send emails. Without DI: `this.emailService = new SmtpEmailService("smtp.gmail.com", ...)` — hardcoded SMTP. Can't test without real SMTP. Can't switch to SendGrid. With DI: `OrderService(EmailService emailService)` — whatever you inject, it uses. Test: inject `FakeEmailService` that just captures sent emails. Production: Spring injects `SmtpEmailService`. Switch to SendGrid: inject `SendGridEmailService` — `OrderService` unchanged. The dependency is swappable because it's injected, not created internally.

---

### 🔩 First Principles Explanation

**DI, IoC, and DIP — three related but distinct concepts:**

```
THE PROBLEM WITHOUT DI:

  class OrderService {
      private final EmailService email;
      private final PaymentGateway payment;

      OrderService() {
          this.email   = new SmtpEmailService("smtp.gmail.com", 587, "user", "pass");
          this.payment = new StripePaymentGateway("sk_live_abc123...");
      }
  }

  Problems:
  1. HARD TO TEST: Constructor creates real SMTP connection, real Stripe call.
     Testing requires real email server + real credit card = impossible in unit tests.

  2. HARD TO SWAP: Need SendGrid? Modify OrderService. Violates OCP.

  3. TIGHT COUPLING: OrderService knows about SmtpEmailService, StripePaymentGateway.
     Transitive knowledge: also knows about SMTP configuration, Stripe API keys.

  4. SECRET DEPENDENCIES: OrderService has hidden dependencies (credentials) baked in.
     Not visible from the outside. Hard to audit or configure.

DI FIXES ALL FOUR:

  // CONSTRUCTOR INJECTION (recommended):
  class OrderService {
      private final EmailService email;       // interface
      private final PaymentGateway payment;   // interface

      OrderService(EmailService email, PaymentGateway payment) {
          this.email   = Objects.requireNonNull(email);
          this.payment = Objects.requireNonNull(payment);
      }
  }

  Benefits:
  1. TESTABLE:
     OrderService service = new OrderService(
         new FakeEmailService(),           // captures emails, no network
         new FakePaymentGateway()          // returns canned responses
     );

  2. SWAPPABLE:
     // Production: Spring wires SmtpEmailService + StripeGateway
     // Test: inject fakes
     // Staging: inject MockPaymentGateway that always succeeds

  3. LOOSE COUPLING: OrderService only knows EmailService and PaymentGateway interfaces.
     No knowledge of SMTP, Stripe, configuration.

  4. VISIBLE DEPENDENCIES: Dependencies declared in constructor — you can see them all.

THE THREE DI FORMS:

  1. CONSTRUCTOR INJECTION (preferred):

     class Service {
         Service(Dependency dep) { this.dep = dep; }
     }

     ✓ Dependencies required at construction — object always valid.
     ✓ Dependencies clearly visible in constructor signature.
     ✓ Easy to use without a DI container (just pass in constructors).
     ✓ Supports immutability (final fields).

  2. SETTER INJECTION (for optional dependencies):

     class Service {
         Dependency dep = new DefaultDependency(); // reasonable default
         void setDependency(Dependency dep) { this.dep = dep; }
     }

     ✓ Optional dependencies with defaults.
     ✓ Allows reconfiguration after construction.
     ✗ Object can be in invalid state (missing mandatory deps).
     ✗ Dependencies not visible from constructor.

  3. FIELD INJECTION (@Autowired — Spring):

     @Service
     class OrderService {
         @Autowired EmailService email;   // injected by Spring directly into field
     }

     ✗ Not testable without Spring container (can't inject without container).
     ✗ Hides dependencies — can't see what's needed just by reading class.
     ✗ Breaks final fields.
     ✓ Concise — popular but considered an anti-pattern outside frameworks.

DI CONTAINER vs. MANUAL DI:

  MANUAL DI (pure DI, composition root):

    EmailService email    = new SmtpEmailService(config.smtpHost(), config.smtpPort());
    PaymentGateway pay    = new StripeGateway(config.stripeKey());
    OrderRepository repo  = new JpaOrderRepository(dataSource);
    OrderService service  = new OrderService(email, pay, repo);
    OrderController ctrl  = new OrderController(service);

    All in "composition root" — one place wires everything.
    ✓ No magic, fully transparent.
    ✗ Verbose for large applications.

  DI CONTAINER (Spring, Guice):

    @Service class OrderService { @Autowired EmailService e; @Autowired PaymentGateway p; }

    Container: scans classes, builds dependency graph, instantiates in right order, injects.
    ✓ Eliminates wiring boilerplate.
    ✓ Lifecycle management (singletons, request scope, session scope).
    ✗ Magic wiring — hard to debug when something doesn't wire correctly.

  Spring constructor injection (best of both):

    @Service
    class OrderService {
        private final EmailService email;
        private final PaymentGateway payment;

        @Autowired  // or omit in Spring 4.3+ (single constructor auto-wired)
        OrderService(EmailService email, PaymentGateway payment) {
            this.email = email;
            this.payment = payment;
        }
    }
```

---

### ❓ Why Does This Exist (Why Before What)

WITHOUT DI:

- Unit test requires real database, real SMTP, real payment gateway — tests are slow, flaky, expensive
- New implementation: modify the class that uses it (OCP violation)

WITH DI:
→ Test with injected fakes: fast, isolated, reproducible
→ New implementation: register it in the DI config — all classes that need `EmailService` get the new one

---

### 🧠 Mental Model / Analogy

> A socket vs. a soldered connection. Soldered: the lamp and bulb are one unit. To change the bulb: cut and resolder wires. To test: use the actual lamp with real power. Socket (DI): any E27 bulb plugs in. Test: plug in a 5W test bulb. Production: plug in a smart LED. Stage: plug in a monitoring bulb. The lamp (class) is designed around the socket interface (dependency interface), not the specific bulb (implementation). The socket is DI: the bulb is provided from outside.

"Lamp's socket" = constructor/setter accepting an interface
"Any E27 bulb" = any implementation of the dependency interface
"Soldered connection" = `new ConcreteImplementation()` inside the class
"Test bulb vs. production bulb" = fake/mock in tests vs. real implementation in production

---

### ⚙️ How It Works (Mechanism)

```
DI CONTAINER LIFECYCLE:

  1. REGISTER (configuration phase):
     context.register(EmailService.class, SmtpEmailService.class)
     context.register(PaymentGateway.class, StripeGateway.class)
     context.register(OrderService.class) // Spring: @Service

  2. RESOLVE (startup phase):
     Container builds dependency graph:
     OrderService needs EmailService and PaymentGateway.
     SmtpEmailService needs SmtpConfig.
     StripeGateway needs StripeConfig.
     Order: SmtpConfig → SmtpEmailService → OrderService

  3. INSTANTIATE (create in dependency order):
     SmtpConfig.new() → SmtpEmailService(config) → StripeGateway(stripeKey) → OrderService(email, pay)

  4. INJECT (wire):
     OrderService receives the constructed SmtpEmailService and StripeGateway.

  5. USE:
     Application uses fully-wired OrderService.
```

---

### 🔄 How It Connects (Mini-Map)

```
Tight coupling from creating own dependencies (new ConcreteService())
        │
        ▼ (inject dependencies from outside)
Dependency Injection ◄──── (you are here)
(object receives dependencies; doesn't create them)
        │
        ├── Dependency Inversion Principle (SOLID-D): DI is the implementation of DIP
        ├── Inversion of Control (IoC): DI is one form of IoC
        ├── Service Locator: alternative (anti)pattern to DI (don't use: hides dependencies)
        └── Testability: DI enables mocking/faking of dependencies in unit tests
```

---

### 💻 Code Example

```java
// WITHOUT DI — tightly coupled:
class ReportService {
    private final ReportRepository repo = new PostgresReportRepository("jdbc:postgresql://...");
    private final EmailService email    = new SmtpEmailService("smtp.example.com", 587);

    void generateAndSend(ReportId id, String recipient) {
        // Can't test without real PostgreSQL + real SMTP. No mock possible.
    }
}

// ────────────────────────────────────────────────────────────────────

// WITH DI — loose coupling via constructor injection:
class ReportService {
    private final ReportRepository repo;
    private final EmailService email;

    ReportService(ReportRepository repo, EmailService email) {
        this.repo  = Objects.requireNonNull(repo);
        this.email = Objects.requireNonNull(email);
    }

    void generateAndSend(ReportId id, String recipient) {
        Report report = repo.findById(id).orElseThrow();
        email.send(recipient, report.asEmailBody());
    }
}

// UNIT TEST — inject fakes, no network, no DB:
@Test
void sendsReportToRecipient() {
    var fakeRepo  = new InMemoryReportRepository(List.of(testReport));
    var fakeEmail = new CapturingEmailService();

    var service = new ReportService(fakeRepo, fakeEmail);
    service.generateAndSend(testReport.id(), "user@example.com");

    assertThat(fakeEmail.sentMessages())
        .hasSize(1)
        .first().satisfies(msg -> assertThat(msg.to()).isEqualTo("user@example.com"));
}

// SPRING PRODUCTION WIRING:
@Service
class ReportService {
    @Autowired  // Spring auto-wires PostgresReportRepository and SmtpEmailService
    ReportService(ReportRepository repo, EmailService email) { ... }
}
```

---

### ⚠️ Common Misconceptions

| Misconception                                                  | Reality                                                                                                                                                                                                                                                                                                                                                  |
| -------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Dependency Injection requires a DI container (Spring, Guice)   | DI is a pattern, not a framework. Manual DI (pure DI): pass dependencies as constructor arguments. A "composition root" (one place in main() that wires everything together) is a valid, framework-free DI approach. DI containers automate the wiring but are not required for the pattern                                                              |
| @Autowired field injection is the idiomatic Spring DI approach | Spring's own documentation (since Spring 4.x) recommends constructor injection over field injection. Field injection (@Autowired on fields) is concise but: (1) requires Spring to test (can't inject without container), (2) hides dependencies, (3) breaks final fields. Constructor injection is idiomatic Spring DI                                  |
| DI and IoC are the same thing                                  | IoC (Inversion of Control) is a broad principle: the framework calls your code, rather than your code calling the framework. DI is one form of IoC (the "where does this object get its dependencies from" inversion). Other IoC forms: template method pattern, event-driven callbacks, reactive programming. DI is a specific, widely used form of IoC |

---

### 🔥 Pitfalls in Production

**Circular dependency — DI container cannot resolve:**

```java
// CIRCULAR DEPENDENCY (A → B → A):
@Service
class ServiceA {
    @Autowired ServiceB b; // A needs B
}

@Service
class ServiceB {
    @Autowired ServiceA a; // B needs A
}

// Spring: "The dependencies of some of the beans in the application context form a cycle"
// BeanCurrentlyInCreationException

// FIX 1: Redesign — circular dependency is usually a design smell.
// Both A and B need each other: extract the shared behavior into C.
// A → C, B → C. No cycle.

// FIX 2: @Lazy injection (defers construction until first use):
@Service
class ServiceA {
    @Autowired @Lazy ServiceB b; // B not constructed until first use of b
}

// FIX 3: Setter injection (one side uses setter instead of constructor):
@Service
class ServiceA {
    private ServiceB b;
    @Autowired
    void setServiceB(ServiceB b) { this.b = b; }
}

// Best practice: circular dependency usually signals wrong responsibility assignment.
// Redesign to eliminate the cycle — it's a design problem, not just a wiring problem.
```

---

### 🔗 Related Keywords

- `Dependency Inversion Principle` — SOLID-D: DI is the implementation of DIP in practice
- `Inversion of Control` — broader principle; DI is one form of IoC
- `Service Locator` — anti-pattern alternative to DI; hides dependencies, harder to test
- `Spring Framework` — Java's dominant DI container; @Autowired, @Component, @Bean
- `Testability` — primary benefit of DI: inject fakes/mocks to test in isolation

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ KEY IDEA     │ Object receives dependencies from outside │
│              │ (injected); doesn't create them with new. │
│              │ Enables swapping implementations.         │
├──────────────┼───────────────────────────────────────────┤
│ USE WHEN     │ Object needs external services (DB, email,│
│              │ HTTP); need to test in isolation; multiple│
│              │ implementations of a dependency exist    │
├──────────────┼───────────────────────────────────────────┤
│ AVOID WHEN   │ Value objects and simple entities: no     │
│              │ injected services needed. Injecting       │
│              │ everything creates over-abstraction      │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "Socket not solder: the lamp doesn't know │
│              │  which bulb is plugged in — any E27 bulb  │
│              │  fits the interface."                     │
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ Dependency Inversion Principle → IoC →   │
│              │ Spring Framework → Service Locator        │
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** A team says: "We use @Autowired field injection everywhere in Spring because it's less code than constructor injection. Why would we change it?" Make the argument for switching to constructor injection, addressing: (a) testability without Spring container; (b) visibility of dependencies; (c) ability to use final fields; (d) null-safety at construction time. When (if ever) is setter injection a better choice than constructor injection?

**Q2.** Service Locator is often cited as an alternative to DI. Instead of injecting `EmailService` into `OrderService`, `OrderService` calls `ServiceLocator.get(EmailService.class)` internally. Both achieve "decoupling from concrete implementation." Why is Service Locator considered an anti-pattern compared to DI? What specifically makes it worse for testability, dependency visibility, and maintainability?
