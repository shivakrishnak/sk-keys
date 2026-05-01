---
layout: default
title: "IoC (Inversion of Control)"
parent: "Spring Core"
nav_order: 371
permalink: /spring/ioc/
number: "371"
category: Spring Core
difficulty: ★☆☆
depends_on: Object-Oriented Programming (OOP), Design Patterns, Dependency Injection
used_by: DI (Dependency Injection), ApplicationContext, BeanFactory, Spring Framework
tags: #foundational, #spring, #architecture, #pattern
---

# 371 — IoC (Inversion of Control)

`#foundational` `#spring` `#architecture` `#pattern`

⚡ TL;DR — IoC inverts the flow of control: instead of a class creating its own dependencies, an external container creates them and injects them — removing tight coupling from application code.

| #371            | Category: Spring Core                                           | Difficulty: ★☆☆ |
| :-------------- | :-------------------------------------------------------------- | :-------------- |
| **Depends on:** | Object-Oriented Programming (OOP), Design Patterns              |                 |
| **Used by:**    | DI (Dependency Injection), ApplicationContext, Spring Framework |                 |

---

### 📘 Textbook Definition

**Inversion of Control** (IoC) is a design principle in which the creation, configuration, and lifecycle management of objects is delegated to an external entity — typically a framework or container — rather than being controlled by the objects themselves. The principle inverts the traditional flow: normally a class creates its dependencies (`new OrderRepository()`); with IoC the container creates dependencies and pushes them into the class. IoC is an umbrella principle; _Dependency Injection_ is the most common concrete implementation. In Spring, the IoC container (`ApplicationContext` / `BeanFactory`) is the external entity responsible for instantiating beans, wiring their dependencies, and managing their lifecycle.

---

### 🟢 Simple Definition (Easy)

Instead of a class creating what it needs, you let Spring create it and hand it over. The class no longer controls how its dependencies come to life — Spring does.

---

### 🔵 Simple Definition (Elaborated)

In traditional code, a class is in full control: `OrderService` does `new PaymentGateway()` and `new OrderRepository()` inside its constructor. It is tightly coupled — you cannot swap `PaymentGateway` for a mock in tests without changing `OrderService`. IoC flips this: Spring reads the application configuration, creates all the objects, and hands them to whoever needs them. `OrderService` declares "I need a `PaymentGateway`" — Spring creates one and gives it to `OrderService`. `OrderService` no longer knows or cares how `PaymentGateway` was constructed. This decoupling is why Spring-managed code is easily testable and configurable without source changes.

---

### 🔩 First Principles Explanation

**The problem: direct instantiation creates rigid, untestable coupling.**

```java
// WITHOUT IoC — tight coupling
class OrderService {
    // OrderService CONTROLS the creation of its dependencies
    private final PaymentGateway gateway   = new StripeGateway();     // hardcoded
    private final OrderRepository repo     = new JpaOrderRepository(); // hardcoded
    private final EmailSender sender       = new SmtpEmailSender();    // hardcoded

    void placeOrder(Order order) {
        gateway.charge(order);
        repo.save(order);
        sender.sendConfirmation(order);
    }
}
```

Problems:

1. **Untestable** — a unit test for `placeOrder` hits the real Stripe API, real database, and real SMTP server. There is no way to inject fakes.
2. **Unconfigurable** — changing to a `PayPalGateway` requires modifying `OrderService` source code.
3. **Not reusable** — every environment (dev, test, prod) uses the same hardcoded implementations.

**The IoC solution — invert who does the constructing:**

```java
// WITH IoC — control inverted to the container
class OrderService {
    // OrderService DECLARES what it needs; it does NOT create it
    private final PaymentGateway  gateway;
    private final OrderRepository repo;
    private final EmailSender     sender;

    // The container calls this constructor with ready-made objects
    OrderService(PaymentGateway gateway, OrderRepository repo,
                 EmailSender sender) {
        this.gateway = gateway;
        this.repo    = repo;
        this.sender  = sender;
    }
}
// Spring configuration declares which implementations to use:
// PaymentGateway → StripeGateway (prod) or FakeGateway (test)
```

`OrderService` is now a passive recipient. The container has control over what gets instantiated.

**The Hollywood Principle — "Don't call us, we'll call you":**

IoC is sometimes summarised as the Hollywood Principle. A class does not call `new` to create collaborators; it waits for the container to call its constructor or setter with the collaborators ready-made.

---

### ❓ Why Does This Exist (Why Before What)

WITHOUT IoC:

What breaks without it:

1. Unit tests must use real infrastructure (database, payment API, email server) because there is no way to substitute fakes.
2. Changing a dependency implementation requires editing every class that instantiates it.
3. Object graph construction (A needs B needs C needs D) is duplicated wherever A is created.
4. Configuration (connection strings, timeouts) is hardcoded in constructors rather than externalised.

WITH IoC:
→ Dependencies are interfaces; implementations are swapped per environment without code changes.
→ Unit tests inject mocks/stubs in place of real implementations — no infrastructure required.
→ The container constructs the entire object graph from configuration — no manual wiring.
→ Cross-cutting concerns (logging, security, transactions) are added by the container without touching business classes.

---

### 🧠 Mental Model / Analogy

> Think of a staffing agency vs. direct hire. In direct hire (no IoC), a company goes out and recruits each employee itself — it is tightly coupled to the hiring process. If it needs a Java developer, it posts the job, interviews, and hires. With a staffing agency (IoC), the company says "I need a Java developer" and the agency provides one. The company does not know or care how the agency found the developer — it just receives a ready-to-work person. Swapping the developer (swapping an implementation) is the agency's problem, not the company's.

"Company declaring a role" = class declaring a dependency type (interface)
"Staffing agency" = Spring IoC container
"Ready-to-work developer" = instantiated and configured bean
"Company going out to hire directly" = class calling `new ConcreteImpl()`

---

### ⚙️ How It Works (Mechanism)

**IoC container flow in Spring:**

```
┌──────────────────────────────────────────────┐
│         Spring IoC Container                 │
│                                              │
│  1. Read configuration                       │
│     (@ComponentScan, @Configuration,         │
│      XML, auto-config)                       │
│           ↓                                  │
│  2. Build BeanDefinition registry            │
│     (class, scope, dependencies)            │
│           ↓                                  │
│  3. Instantiate beans in dependency order    │
│     (PaymentGateway before OrderService)    │
│           ↓                                  │
│  4. Inject dependencies                      │
│     (constructor / setter / field)           │
│           ↓                                  │
│  5. Run BeanPostProcessors                   │
│     (AOP proxies, @Autowired wiring)        │
│           ↓                                  │
│  6. Call @PostConstruct / afterPropertiesSet │
│           ↓                                  │
│  7. Beans ready — ApplicationContext starts  │
└──────────────────────────────────────────────┘
```

**Concrete IoC in Spring Boot:**

```java
// 1. Declare the dependency via an interface (not a concrete class)
@Service
class OrderService {
    private final PaymentGateway gateway;

    // Constructor injection — Spring calls this
    OrderService(PaymentGateway gateway) {
        this.gateway = gateway;
    }
}

// 2. Spring finds StripeGateway implementing PaymentGateway via @ComponentScan
@Component
class StripeGateway implements PaymentGateway { ... }

// 3. Spring instantiates StripeGateway, then calls:
//    new OrderService(stripeGatewayInstance)
// OrderService never called 'new StripeGateway()' itself
```

---

### 🔄 How It Connects (Mini-Map)

```
Object-Oriented Programming
(classes and interfaces)
        │
        ▼
IoC (Inversion of Control)  ◄──── (you are here)
        │  ← concrete implementation →
        ▼
DI (Dependency Injection)
        │
        ├───────────────────────────────────┐
        ▼                                   ▼
ApplicationContext                  BeanFactory
(Spring's IoC container)           (base container)
        │
        ▼
Bean Lifecycle / Bean Scope
```

---

### 💻 Code Example

**Example 1 — Before and after IoC:**

```java
// BEFORE IoC: tight coupling, untestable
class ReportService {
    private final DataSource ds = new HikariDataSource(config); // new!
    void generateReport() { /* uses ds */ }
}
// To test: needs a real database. Cannot be unit-tested.

// AFTER IoC: Spring injects DataSource
@Service
class ReportService {
    private final DataSource ds;          // declared, not created

    ReportService(DataSource ds) {        // Spring provides it
        this.ds = ds;
    }

    void generateReport() { /* uses ds */ }
}
// To test: inject DataSource mock → no database needed
```

**Example 2 — Swapping implementations without touching business code:**

```java
// Production: real gateway provided by Spring (auto-detected @Component)
@Component
@Profile("prod")
class StripeGateway implements PaymentGateway { ... }

// Test: fake gateway registered only in test context
@Component
@Profile("test")
class FakePaymentGateway implements PaymentGateway {
    public void charge(Order o) { /* no-op */ }
}

// OrderService is identical in both profiles — IoC makes it transparent
```

---

### ⚠️ Common Misconceptions

| Misconception                   | Reality                                                                                                                                                              |
| ------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| IoC and DI are the same thing   | IoC is the principle; DI is the most common implementation of it. Service Locator is another form of IoC that does NOT use DI                                        |
| IoC requires Spring             | IoC is a language-agnostic design principle. Angular uses IoC, Guice uses IoC, CDI uses IoC. Spring is one implementation                                            |
| IoC means you never use `new`   | You use `new` for value objects, DTOs, and simple local variables. IoC applies to service-layer dependencies that need to be swappable and managed                   |
| IoC always improves performance | The container adds startup overhead for reflection, proxy creation, and graph wiring. The benefit is developer productivity and testability — not runtime throughput |

---

### 🔥 Pitfalls in Production

**Bypassing IoC with `new` inside a Spring bean — proxy bypass**

```java
// BAD: creating a Spring-managed class with 'new' bypasses Spring
@Service
class OrderService {
    void processOrder(Order order) {
        // AuditService has @Transactional — but this bypasses the Spring proxy!
        AuditService audit = new AuditService(); // NOT the Spring-managed bean
        audit.record(order); // @Transactional on audit.record() does NOTHING
    }
}

// GOOD: inject the Spring-managed bean so the proxy is used
@Service
class OrderService {
    private final AuditService auditService; // injected by Spring
    OrderService(AuditService auditService) { this.auditService = auditService; }

    void processOrder(Order order) {
        auditService.record(order); // uses the Spring proxy — @Transactional works
    }
}
```

---

**Slow startup due to unnecessary eager bean initialisation**

```java
// BAD: heavyweight bean with long init eagerly created at startup
@Component
class ReportCacheWarmer {
    @PostConstruct
    void warmUp() {
        // Queries 10 million rows — runs on every startup including tests!
        reportRepository.findAll().forEach(cache::put);
    }
}

// GOOD: make it lazy or conditional
@Component
@Lazy                        // initialised on first use, not at startup
@ConditionalOnProperty(name = "cache.warm-up.enabled", havingValue = "true")
class ReportCacheWarmer { ... }
```

---

### 🔗 Related Keywords

- `DI (Dependency Injection)` — the primary concrete mechanism implementing the IoC principle in Spring
- `ApplicationContext` — Spring's full-featured IoC container that manages the bean lifecycle
- `BeanFactory` — the base Spring IoC container; `ApplicationContext` extends it
- `Bean` — any object whose lifecycle is managed by the Spring IoC container
- `Bean Lifecycle` — the sequence of phases a bean passes through inside the IoC container
- `@Autowired` — Spring's annotation that triggers IoC-driven dependency injection
- `CGLIB Proxy` — the proxy mechanism Spring uses to add cross-cutting concerns via IoC-managed beans

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ KEY IDEA     │ External container controls creation and  │
│              │ wiring of objects — not the objects       │
├──────────────┼───────────────────────────────────────────┤
│ PRINCIPLE    │ Hollywood: "Don't call us, we'll call you"│
│              │ Declare needs; container fulfils them     │
├──────────────┼───────────────────────────────────────────┤
│ BENEFIT      │ Loose coupling → testable, configurable,  │
│              │ swappable implementations                 │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "Let Spring build the engine; you just    │
│              │ describe which parts you need."           │
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ DI (Dependency Injection) → Bean →        │
│              │ ApplicationContext → Bean Lifecycle        │
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** A team migrates from a Service Locator pattern (where classes call `ServiceRegistry.get(PaymentGateway.class)` to retrieve dependencies) to constructor-based IoC/DI. Both patterns achieve loose coupling from concrete implementations. Identify three specific differences in testability, error detection timing, and dependency graph visibility between the two approaches — and explain why the Spring community strongly prefers IoC/DI over Service Locator despite both achieving decoupling.

**Q2.** A Spring Boot application has 500 beans. Startup takes 45 seconds in a Kubernetes pod. The liveness probe fails because the pod takes too long to become ready, causing rolling deployment failures. Without disabling IoC, describe at least three Spring-specific techniques to reduce startup time, explaining which part of the IoC container initialisation each technique addresses and what trade-off each introduces at runtime.
