---
layout: default
title: "IoC (Inversion of Control)"
parent: "Spring & Spring Boot"
nav_order: 103
permalink: /spring/ioc/
number: "103"
category: Spring & Spring Boot
difficulty: ★★☆
depends_on: Object-Oriented Programming, Coupling, Design Patterns, Abstraction
used_by: Dependency Injection, ApplicationContext, Bean, Spring Framework
tags: #java, #spring, #architecture, #pattern, #intermediate
---

# 103 — IoC (Inversion of Control)

`#java` `#spring` `#architecture` `#pattern` `#intermediate`

⚡ TL;DR — The design principle of surrendering control of object creation and wiring to an external container rather than constructing dependencies yourself.

| #103 | Category: Spring & Spring Boot | Difficulty: ★★☆ |
|:---|:---|:---|
| **Depends on:** | Object-Oriented Programming, Coupling, Design Patterns, Abstraction | |
| **Used by:** | Dependency Injection, ApplicationContext, Bean, Spring Framework | |

---

### 📘 Textbook Definition

**Inversion of Control (IoC)** is a software design principle in which the control flow of a programme is inverted relative to traditional procedural design: instead of application code creating and assembling its own dependencies, that responsibility is delegated to an external framework or container. The classic formulation is the "Hollywood Principle" — "Don't call us, we'll call you." IoC is a broad principle with several implementations; Dependency Injection is the most prevalent form in object-oriented systems. Spring's IoC container (ApplicationContext) creates, wires, and manages the lifecycle of all application objects declared as beans.

---

### 🟢 Simple Definition (Easy)

Normally your code creates the objects it needs. IoC reverses this — instead of your code assembling everything, a container does the assembly and hands you what you need.

---

### 🔵 Simple Definition (Elaborated)

In traditional code, a class constructs its own dependencies using `new`. The class controls lookup and creation. IoC flips this: the class declares what it needs (through constructor parameters or annotations), and an external container reads that declaration and provides the right objects at runtime. This separates "what I need" from "how to get it." Spring's ApplicationContext is the "how to get it." Your application code only knows about interfaces, not concrete implementations — making it testable and configurable without code changes.

---

### 🔩 First Principles Explanation

**Problem — tight coupling through direct instantiation:**

```java
// TIGHT COUPLING: OrderService builds its own graph
class OrderService {
  private final PaymentGateway gateway;
  private final InventoryService inventory;

  public OrderService() {
    // Hard-wired: can't swap, test, or configure
    this.gateway   = new StripePaymentGateway();
    this.inventory = new MySQLInventoryService(
        new DataSource("jdbc:mysql://prod/shop")
    );
  }
}
```

**The cascade of problems:**

- Test `OrderService` → requires a real Stripe API key and MySQL
- Swap `StripeGateway` for `PayPalGateway` → rewrite constructor
- Two components need the same gateway instance → creates duplicates
- Database URL is hardcoded → no external configuration possible

**Insight — invert the dependency direction:**

```
┌───────────────────────────────────────────────┐
│  TRADITIONAL (caller controls creation)       │
│  OrderService → new StripeGateway()           │
│  Caller owns the factory decision             │
│                                               │
│  IoC (container controls creation)            │
│  Container creates StripeGateway              │
│  Container injects it into OrderService       │
│  Caller declares need — container fulfils     │
└───────────────────────────────────────────────┘
```

The container reads all declarations, builds a dependency graph, resolves creation order, and injects everything. Application code only declares interfaces.

---

### ❓ Why Does This Exist (Why Before What)

**WITHOUT IoC:**

```
Without IoC:

  Instantiation scattered everywhere:
    Every class builds its own deep dependency tree
    → assembling an OrderService requires knowing how
      to build PaymentGateway and InventoryService too

  Testing requires real infrastructure:
    Unit test OrderService → must start MySQL,
    configure Stripe test keys, resolve ports
    → 10-second test setup per class

  Configuration is hardcoded in source:
    DB URLs in constructors → secrets in git history
    → prod vs staging requires recompilation

  Shared singletons require manual management:
    Connection pools duplicated per module → OOM
```

**WITH IoC:**

```
→ Container assembles object graph from declarations
→ Unit tests inject mocks via constructor
  → no infrastructure required
→ Config in application.properties / env vars
  → secrets management, no recompilation needed
→ Singletons managed by container — one instance
  shared across the entire application
→ Swap implementation: change config, not code
```

---

### 🧠 Mental Model / Analogy

> IoC is like a **hotel concierge service**. Without it: you find the restaurant, make the reservation, arrange transport yourself. With concierge: you declare "dinner for two at 7pm" and the concierge handles all details — selecting restaurant, booking, transport. You declare the need; the concierge fulfils it. You never know (or care) which specific restaurant was chosen.

"Hotel guest declaring a need" = component declaring dependencies
"Concierge arranging fulfilment" = IoC container assembling the graph
"Which restaurant chosen" = which concrete implementation is injected
"Guest never knowing details" = component knowing only interfaces

---

### ⚙️ How It Works (Mechanism)

**The IoC container's three responsibilities:**

```
┌─────────────────────────────────────────────────┐
│  IoC CONTAINER RESPONSIBILITIES                 │
├─────────────────────────────────────────────────┤
│  1. DISCOVER  — scan classpath for components   │
│     @Component, @Service, @Repository, @Bean    │
│                                                 │
│  2. INSTANTIATE — create objects in order       │
│     Resolve dependency graph, create instances  │
│     Manage lifecycle (init, destroy callbacks)  │
│                                                 │
│  3. WIRE — inject dependencies                  │
│     Constructor injection (preferred)           │
│     Setter injection                            │
│     Field injection (@Autowired)                │
└─────────────────────────────────────────────────┘
```

**IoC vs DI — the distinction:**

IoC is the *principle* (control is inverted). DI is the *mechanism* by which IoC is implemented in Spring. Other IoC forms include: Service Locator (pull from registry), Template Method (framework calls your hook), Event-driven callbacks. Spring uses constructor DI as its recommended IoC mechanism.

---

### 🔄 How It Connects (Mini-Map)

```
Application class declares dependencies
(constructor params, @Autowired, interfaces)
        ↓
  IoC PRINCIPLE  ← you are here
  (control of object creation inverted)
        ↓
  Implemented via:
  Dependency Injection (104)
        ↓
  Managed by:
  ApplicationContext (105) — the container
        ↓
  Enables all of:
  Bean Lifecycle (108), AOP Proxy,
  @Transactional (127), Auto-Configuration (133)
```

---

### 💻 Code Example

**Example 1 — Without IoC vs with IoC:**

```java
// WITHOUT IoC: tight coupling, untestable
class ReportService {
  private final UserRepository repo;
  public ReportService() {
    this.repo = new JdbcUserRepository( // hard-coded
        DriverManager.getConnection(
            "jdbc:postgresql://db/app", "u", "p"));
  }
}

// WITH IoC: constructor injection, fully testable
@Service
class ReportService {
  private final UserRepository repo;

  public ReportService(UserRepository repo) {
    this.repo = repo; // container provides it
  }
}
```

**Example 2 — IoC enabling easy unit testing:**

```java
// No Spring context needed — pure unit test
class ReportServiceTest {
  @Test
  void shouldGenerateReport() {
    // IoC through constructor injection
    var mockRepo = mock(UserRepository.class);
    var service  = new ReportService(mockRepo);

    when(mockRepo.findAll()).thenReturn(testUsers());
    Report report = service.generate();

    assertThat(report.getUserCount()).isEqualTo(3);
  }
}
```

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| IoC and Dependency Injection are the same thing | IoC is the broad principle; DI is one implementation of it. Service Locator is also an IoC form |
| IoC requires a framework like Spring | IoC is achievable in plain Java by passing dependencies via constructors — Spring automates this at scale |
| IoC makes code harder to understand | Constructor injection makes the dependency graph *explicit* — more readable than scattered `new` calls |
| Field injection is equivalent to constructor injection | Field injection hides dependencies, prevents immutability, and breaks unit tests without a Spring context |
| Service Locator and DI are both good IoC | DI pushes dependencies in; Service Locator requires components to pull from a registry — still coupling to the locator |

---

### 🔥 Pitfalls in Production

**1. Field injection hiding dependency explosion**

```java
// BAD: 12 @Autowired fields — class is doing too much
@Service
class MegaService {
  @Autowired UserRepo userRepo;
  @Autowired OrderRepo orderRepo;
  @Autowired PaymentService payment;
  @Autowired EmailService email;
  // ... 8 more injected fields
  // Class needs splitting — field injection hides this
}

// GOOD: constructor injection reveals the problem
@Service
class MegaService {
  public MegaService(UserRepo userRepo,
                     OrderRepo orderRepo,
                     PaymentService payment /* ... */) {
    // > 5 constructor params = clear signal to split class
  }
}
```

**2. Circular dependency masking design problems**

```java
// BAD: A → B → A (circular)
@Service class AService {
  @Autowired BService b;
}
@Service class BService {
  @Autowired AService a;
}
// Throws: BeanCurrentlyInCreationException
// (or resolves silently with field injection — worse)

// GOOD: extract shared state into EventBus or
// third dedicated service to break the cycle
```

---

### 🔗 Related Keywords

- `Dependency Injection` — the primary mechanism through which IoC is implemented in Spring
- `ApplicationContext` — the Spring IoC container that manages the object lifecycle
- `Bean` — an object whose lifecycle and wiring is managed by the container
- `Coupling` — IoC's primary benefit is dramatically reducing inter-class coupling
- `@Autowired` — the annotation that declares injection points for the container to fulfil
- `Service Locator` — an alternative IoC pattern where components pull from a registry

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ KEY IDEA     │ Surrender control of object creation to   │
│              │ a container — declare needs, not builds   │
├──────────────┼───────────────────────────────────────────┤
│ USE WHEN     │ All Spring applications — IoC is the core │
│              │ design principle, not optional            │
├──────────────┼───────────────────────────────────────────┤
│ AVOID WHEN   │ Avoid field injection — use constructor   │
│              │ injection to make dependencies visible    │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "Don't call us, we'll call you —          │
│              │  declare your needs, we'll provide them." │
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ DI (104) → ApplicationContext (105) →     │
│              │ Bean Lifecycle (108)                      │
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** Spring Boot with `@SpringBootApplication` scans the classpath and auto-wires hundreds of beans at startup. For services doing 1,000 deploys/day, startup time directly impacts deployment risk and canary switch latency. Explain at a technical level what happens during Spring's component scan and bean graph resolution — and then describe two specific Spring Boot features (one at the JVM level, one at the Spring level) that reduce startup time from ~3 seconds to under 200ms.

**Q2.** The Service Locator pattern is also an IoC implementation, but Spring documentation explicitly recommends DI over Service Locator. Both invert control. Explain exactly what makes DI *more* IoC than Service Locator — trace the dependency lookup direction in each, explain why Service Locator still creates a hidden coupling to the registry itself, and describe the one production scenario where Service Locator is genuinely more appropriate than DI.

