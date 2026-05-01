---
layout: default
title: "Clean Architecture"
parent: "Software Architecture Patterns"
nav_order: 728
permalink: /software-architecture/clean-architecture/
number: "728"
category: Software Architecture Patterns
difficulty: ★★★
depends_on: "Hexagonal Architecture, Dependency Inversion Principle, SOLID Principles"
used_by: "Android (Google), .NET Clean Architecture Template, Domain-Driven Design"
tags: #advanced, #architecture, #clean-code, #dependency-rule, #use-cases
---

# 728 — Clean Architecture

`#advanced` `#architecture` `#clean-code` `#dependency-rule` `#use-cases`

⚡ TL;DR — **Clean Architecture** (Robert C. Martin) organizes code into four concentric rings — **Entities → Use Cases → Interface Adapters → Frameworks** — with a single **Dependency Rule**: source code dependencies can only point inward, never outward.

| #728            | Category: Software Architecture Patterns                                 | Difficulty: ★★★ |
| :-------------- | :----------------------------------------------------------------------- | :-------------- |
| **Depends on:** | Hexagonal Architecture, Dependency Inversion Principle, SOLID Principles |                 |
| **Used by:**    | Android (Google), .NET Clean Architecture Template, Domain-Driven Design |                 |

---

### 📘 Textbook Definition

**Clean Architecture**, described by Robert C. Martin in his 2017 book of the same name, is an architectural pattern that arranges code into four concentric circles, each representing a different level of abstraction: (1) **Entities** — enterprise-wide business rules; core domain objects that change least frequently. (2) **Use Cases** — application-specific business rules; orchestrate entity interactions to achieve a specific goal. (3) **Interface Adapters** — convert data between use cases/entities and external formats; contains controllers, presenters, gateways. (4) **Frameworks and Drivers** — the outermost ring; web frameworks, databases, UI, external APIs. The **Dependency Rule**: source code dependencies must only point inward. Nothing in an inner ring can know anything about something in an outer ring. Crucially: use cases depend on entities, but never on controllers or databases. Data structures that cross ring boundaries must be simple data objects (DTOs), not framework-specific types. Clean Architecture unifies ideas from Hexagonal Architecture, Onion Architecture, and DCI, all sharing the same goal: independent of frameworks, testable, independent of the UI, independent of the database.

---

### 🟢 Simple Definition (Easy)

An onion: layers around a core. The core (Entities) is at the center — fundamental business rules. The next ring (Use Cases) orchestrates those rules. The next ring (Adapters) converts between the core's language and the outside world's language. The outer ring (Frameworks) is where Spring, MySQL, and React live. The rule: each layer can only look inward. The onion's center doesn't know it's part of an onion. Entities don't know about the database. Use Cases don't know about HTTP. Frameworks are details — replaceable without touching the core.

---

### 🔵 Simple Definition (Elaborated)

Robert Martin's insight: "The database is a detail. The web is a detail. The framework is a detail." Entities (business rules) are what your company actually is — they'd exist even if you had no software. Use Cases are what your software does — coordinate entities to achieve business goals. Adapters and Frameworks are how you currently implement it — likely to change as technology evolves. If your business rules depend on MySQL, and MySQL is replaced by PostgreSQL, your business rules must change. But business rules didn't need to change — only the delivery mechanism did. Clean Architecture prevents this contamination.

---

### 🔩 First Principles Explanation

**Four rings, Dependency Rule, Use Case Interactor pattern, and crossing ring boundaries:**

```
CLEAN ARCHITECTURE RINGS:

              ┌─────────────────────────────────────────┐
              │  FRAMEWORKS & DRIVERS (outermost)       │
              │  - Web: Spring MVC, REST, HTTP          │
              │  - Database: PostgreSQL, JPA, Hibernate │
              │  - UI: React, Angular, Thymeleaf        │
              │  - External APIs: Stripe, SendGrid      │
              │                                         │
              │  ┌───────────────────────────────────┐  │
              │  │  INTERFACE ADAPTERS               │  │
              │  │  - Controllers (Web → Use Case)   │  │
              │  │  - Presenters (Use Case → View)   │  │
              │  │  - Gateways (Use Case → DB)       │  │
              │  │  - Data mappers (Entity ↔ DTO)    │  │
              │  │                                   │  │
              │  │  ┌─────────────────────────────┐  │  │
              │  │  │  USE CASES                  │  │  │
              │  │  │  - Application business rules│  │  │
              │  │  │  - Interactors               │  │  │
              │  │  │  - Orchestrate entities      │  │  │
              │  │  │  - Input/Output Ports        │  │  │
              │  │  │                             │  │  │
              │  │  │  ┌───────────────────────┐  │  │  │
              │  │  │  │  ENTITIES             │  │  │  │
              │  │  │  │  - Business objects   │  │  │  │
              │  │  │  │  - Core rules (domain)│  │  │  │
              │  │  │  │  - Enterprise-wide    │  │  │  │
              │  │  │  └───────────────────────┘  │  │  │
              │  │  └─────────────────────────────┘  │  │
              │  └───────────────────────────────────┘  │
              └─────────────────────────────────────────┘

DEPENDENCY RULE:
  Dependencies point INWARD only.
  Entities: depend on nothing.
  Use Cases: depend on Entities. NOT on Controllers or DB.
  Interface Adapters: depend on Use Cases (and Entities). NOT on Frameworks.
  Frameworks: depend on Interface Adapters.

  COROLLARY: No import of framework types in inner rings.
  Use Cases: NEVER import HttpServletRequest, JpaRepository, StripeClient.
  Entities: NEVER import anything framework-specific.

USE CASE (INTERACTOR) PATTERN:

  Each use case is a separate class (not a big Service class).
  Has an Input Port (interface for input) and Output Port (interface for output).

  // Input Port (interface, defined in Use Case ring):
  public interface RegisterUserInputPort {
      void register(RegisterUserRequest request);
  }

  // Output Port (interface, defined in Use Case ring):
  // What the use case needs from outside (inverted dependency):
  public interface RegisterUserOutputPort {
      void presentSuccess(RegisterUserResponse response);
      void presentError(String errorMessage);
  }

  // Use Case Interactor (implements Input Port, uses Output Port):
  public class RegisterUserUseCase implements RegisterUserInputPort {
      private final UserGateway userGateway;        // Interface (Adapter implements)
      private final RegisterUserOutputPort outputPort;  // Presenter implements this

      @Override
      public void register(RegisterUserRequest request) {
          // Pure use case logic:
          if (userGateway.existsByEmail(request.email())) {
              outputPort.presentError("Email already registered");
              return;
          }
          User user = new User(request.email(), request.name());
          userGateway.save(user);
          outputPort.presentSuccess(new RegisterUserResponse(user.id(), user.email()));
      }
  }

  // Controller (Interface Adapters ring):
  public class RegisterUserController {
      private final RegisterUserInputPort useCase;

      public void handleRequest(HttpRequest request) {
          RegisterUserRequest dto = parseRequest(request);
          useCase.register(dto);  // Calls use case through Input Port.
      }
  }

  // Presenter (Interface Adapters ring — implements Output Port):
  public class RegisterUserPresenter implements RegisterUserOutputPort {
      private ViewModel viewModel;

      @Override
      public void presentSuccess(RegisterUserResponse response) {
          viewModel = new SuccessViewModel(response.userId());
      }

      @Override
      public void presentError(String errorMessage) {
          viewModel = new ErrorViewModel(errorMessage);
      }

      public ViewModel getViewModel() { return viewModel; }
  }

DATA CROSSING BOUNDARIES:

  Inner ring → outer ring: simple data structures (DTOs), NOT inner ring's objects.

  WRONG: Use Case returns User entity to Controller:
    Controller: knows about User entity (inner ring concept). Creates dependency.

  RIGHT: Use Case returns RegisterUserResponse (simple DTO):
    RegisterUserResponse: a plain data object. No domain logic.
    Controller: converts RegisterUserResponse → HTTP response (JSON).
    User entity: never leaves the use case ring.

PACKAGE STRUCTURE:

  src/
  ├── entities/              ← Innermost ring. No imports from outer rings.
  │   ├── User.java
  │   └── Order.java
  ├── usecases/              ← Use Case ring.
  │   ├── RegisterUserUseCase.java
  │   ├── ports/
  │   │   ├── in/RegisterUserInputPort.java
  │   │   └── out/RegisterUserOutputPort.java
  │   └── gateways/
  │       └── UserGateway.java  (interface — DB gateway, implemented by Adapter)
  ├── adapters/              ← Interface Adapters ring.
  │   ├── web/
  │   │   ├── RegisterUserController.java
  │   │   └── RegisterUserPresenter.java
  │   └── persistence/
  │       └── UserJpaGateway.java  (implements UserGateway using JPA)
  └── frameworks/            ← Outermost ring.
      ├── web/SpringMvcConfig.java
      └── persistence/JpaConfig.java

CLEAN vs HEXAGONAL:

  Very similar. Key difference: Clean Architecture explicitly names 4 rings and distinguishes
  Entities from Use Cases (application rules vs. enterprise rules).
  Hexagonal: just "domain" vs. "adapters/ports."

  Clean Architecture: stricter — each Use Case is its own class (Interactor pattern).
  Hexagonal: looser — use case logic often in a Service class covering multiple use cases.

  Robert Martin: "These architectures, though different in their details,
  are very similar. They all have the same objective, which is the
  separation of concerns."
```

---

### ❓ Why Does This Exist (Why Before What)

WITHOUT Clean Architecture:

- Business rules in controllers: can't reuse for CLI/Kafka consumers
- Use cases import JPA: can't test without running database migrations
- Framework upgrades (Spring 5 → Spring 6): may require touching business logic

WITH Clean Architecture:
→ Entities: pure business rules, survive technology changes
→ Use Cases: testable without any framework or database
→ Frameworks: replaceable details — change the outer ring without touching the core

---

### 🧠 Mental Model / Analogy

> A city's water system: the water treatment plant (Entities) produces clean water — doesn't care who uses it. The distribution rules (Use Cases) decide which neighborhoods get priority and minimum pressure. The pipe network (Interface Adapters) physically routes water to houses and buildings. The houses themselves (Frameworks) consume the water. The treatment plant doesn't know about the pipes or the houses. If all pipes are replaced with better pipes: the treatment plant is unchanged. If all houses are demolished and rebuilt: treatment plant is unchanged.

"Water treatment plant" = Entities (core business rules)
"Distribution rules" = Use Cases (application-specific orchestration)
"Pipe network" = Interface Adapters (converts and routes)
"Houses" = Frameworks and Drivers (the consuming outer layer)

---

### ⚙️ How It Works (Mechanism)

```
CLEAN ARCHITECTURE CALL FLOW:

  1. HTTP request → Controller (Interface Adapters ring)
  2. Controller parses request → creates Input DTO
  3. Controller calls InputPort.execute(inputDTO) [Use Case ring]
  4. Use Case Interactor: applies business logic using Entities
  5. Interactor calls UserGateway.save(user) [interface in Use Case ring]
  6. JpaUserGateway (Adapters ring) implements: maps domain → JPA entity → DB
  7. Interactor calls OutputPort.present(responseDTO) [back to Adapters]
  8. Presenter (Adapters ring): builds ViewModel
  9. Controller: reads ViewModel → HTTP response
```

---

### 🔄 How It Connects (Mini-Map)

```
SOLID Principles (especially Dependency Inversion)
        │
        ▼ (applied at architectural scale)
Clean Architecture ◄──── (you are here)
(4 rings: Entities → Use Cases → Adapters → Frameworks; inward dependencies only)
        │
        ├── Hexagonal Architecture: same dependency rule, different terminology
        ├── Onion Architecture: same concept, emphasizes Domain Model layer
        └── CQRS / Event Sourcing: often implemented within Clean Architecture rings
```

---

### 💻 Code Example

```java
// Minimal Clean Architecture use case (without presenter pattern):

// ENTITIES RING: pure business object
public class Order {
    private final OrderId id;
    private final List<OrderItem> items;
    private OrderStatus status;

    public Money calculateTotal() {
        return items.stream().map(OrderItem::price).reduce(Money.ZERO, Money::add);
    }

    public void confirm() {
        if (status != OrderStatus.PENDING) throw new InvalidOrderStateException();
        this.status = OrderStatus.CONFIRMED;
    }
}

// USE CASES RING: gateway interface (no JPA imports)
public interface OrderGateway {
    Order findById(OrderId id);
    Order save(Order order);
}

// USE CASES RING: use case interactor
public class ConfirmOrderUseCase {
    private final OrderGateway orderGateway;
    private final PaymentGateway paymentGateway;  // Also an interface.

    public ConfirmOrderResponse execute(ConfirmOrderRequest request) {
        Order order = orderGateway.findById(request.orderId());
        paymentGateway.charge(order.customerId(), order.calculateTotal());
        order.confirm();  // Entity's business rule: validate state transition.
        orderGateway.save(order);
        return new ConfirmOrderResponse(order.id(), order.status());
    }
}

// ADAPTERS RING: JPA implementation of gateway
@Repository
public class JpaOrderGateway implements OrderGateway {
    private final SpringOrderRepository repo;
    @Override
    public Order findById(OrderId id) {
        return repo.findById(id.value()).map(OrderMapper::toDomain).orElseThrow();
    }
}
```

---

### ⚠️ Common Misconceptions

| Misconception                                             | Reality                                                                                                                                                                                                                                                                                                                                                                                   |
| --------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Clean Architecture means one class per use case           | Robert Martin's book describes the Interactor pattern (one class per use case). But this is a guideline, not a strict rule. Many teams implement Clean Architecture with Service classes that group related use cases (e.g., OrderService handles ConfirmOrder, CancelOrder, GetOrder). What matters is the Dependency Rule — services in the use case ring may not depend on outer rings |
| The four rings must be four separate Maven/Gradle modules | Physical module separation is a common approach but not required. The dependency rule can be enforced with package-by-layer structure + ArchUnit tests (automated dependency rule verification). Separate modules add compile-time enforcement but also build complexity. Small teams: single module with package structure; Large teams: separate modules to enforce boundaries          |
| Clean Architecture is incompatible with Spring Boot       | Spring Boot is in the outermost ring (Frameworks). Use it freely there. Domain services (Use Case ring) can use Spring's @Service annotation — it's just metadata. What's incompatible: importing Spring Data's JpaRepository inside a Use Case Interactor. Keep Spring's infrastructure concerns (JPA, MVC) in the Adapters or Frameworks rings only                                     |

---

### 🔥 Pitfalls in Production

**Dependency Rule violation — framework types leaking into use cases:**

```
BAD: Use Case imports Spring/JPA types (dependency rule violation):

  // In the USE CASES ring — should be inner ring, free of framework deps:
  @Service  // Fine — just metadata
  @Transactional  // PROBLEM: Spring's @Transactional in use case ring
  public class ConfirmOrderUseCase {

      @Autowired  // PROBLEM: Spring dependency injection annotation
      private JpaOrderRepository orderRepository;  // PROBLEM: JPA type in use case ring

      public OrderDTO confirmOrder(Long orderId) {
          // PROBLEM: Optional<OrderJpaEntity> in use case — JPA entity type
          Optional<OrderJpaEntity> entity = orderRepository.findById(orderId);
          if (entity.isEmpty()) throw new RuntimeException("Not found");
          entity.get().setStatus("CONFIRMED");  // JPA entity mutation in use case — WRONG
          orderRepository.save(entity.get());   // JPA save in use case — WRONG
          return new OrderDTO(entity.get().getId(), entity.get().getStatus());
      }
  }

PROBLEMS:
  - Use case is untestable without: Spring context, Hibernate, database.
  - Change from JPA to DynamoDB: must rewrite the use case.
  - @Transactional in use case ring: Spring-specific transaction management in business logic.
  - JPA entity in use case: ORM's model (with @Id, @Column) mixed with domain model.

FIX: Move framework types to Adapters ring; use gateway interfaces in Use Case:

  // USE CASE RING (no framework imports):
  public class ConfirmOrderUseCase {
      private final OrderGateway orderGateway;  // Interface — no JPA.

      public ConfirmOrderResponse execute(ConfirmOrderRequest request) {
          Order order = orderGateway.findById(request.orderId());  // Domain entity.
          order.confirm();  // Business rule on domain entity.
          orderGateway.save(order);  // Interface — implementation is in Adapters ring.
          return new ConfirmOrderResponse(order.id(), order.status());
      }
  }

  // ADAPTERS RING (JPA details here):
  @Repository
  @Transactional  // Transaction management in adapters ring — correct.
  public class JpaOrderGateway implements OrderGateway {
      private final JpaOrderRepository repo;  // Spring Data JPA — correct place.

      @Override
      public Order findById(OrderId id) {
          OrderJpaEntity entity = repo.findById(id.value()).orElseThrow(() ->
              new OrderNotFoundException(id));
          return OrderMapper.toDomain(entity);  // Map JPA entity to domain entity.
      }
  }

ENFORCE WITH ARCHUNIT (automated dependency rule verification):
  @Test
  void useCasesRingShouldNotDependOnSpringOrJpa() {
      JavaClasses classes = new ClassFileImporter().importPackages("com.example");

      ArchRule rule = noClasses()
          .that().resideInAPackage("..usecases..")
          .should().accessClassesThat()
          .resideInAnyPackage("org.springframework..", "javax.persistence..", "jakarta.persistence..");

      rule.check(classes);  // Fails if any use case class imports Spring/JPA. CI gate.
  }
```

---

### 🔗 Related Keywords

- `Hexagonal Architecture` — the closest sibling: same dependency rule, ports/adapters terminology
- `Onion Architecture` — same principle: domain at center, infrastructure at edges
- `SOLID Principles` — especially Dependency Inversion Principle: the theoretical basis
- `Use Case` — the application-layer concept Clean Architecture makes explicit and central
- `Dependency Injection` — the mechanism by which inner rings receive outer ring implementations

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ KEY IDEA     │ 4 rings: Entities → Use Cases →          │
│              │ Adapters → Frameworks. One rule:         │
│              │ dependencies only point inward.          │
│              │ Framework = detail. Entity = core truth. │
├──────────────┼───────────────────────────────────────────┤
│ USE WHEN     │ Complex domain; need long-term           │
│              │ testability; frameworks may change;      │
│              │ multiple delivery mechanisms             │
├──────────────┼───────────────────────────────────────────┤
│ AVOID WHEN   │ Simple CRUD apps; small team with        │
│              │ simple domain; overhead exceeds benefit  │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "Database is a detail. Framework is a   │
│              │  detail. Business rules are the truth." │
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ Hexagonal Architecture → Onion           │
│              │ Architecture → Use Case → SOLID →       │
│              │ ArchUnit (dependency enforcement)        │
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** Robert Martin says "the database is a detail." Your team's argument: "Our entire business logic is about efficient querying — complex joins, stored procedures, database-level triggers for audit logs. Moving query logic out of the database and into the Use Case ring is impractical and slow." Is this a valid objection? Can Clean Architecture accommodate database-heavy applications? Where should stored procedures and complex queries live in the ring model?

**Q2.** You're testing `ConfirmOrderUseCase.execute()` as a unit test. The use case calls `orderGateway.findById()` and `paymentGateway.charge()`. Write the test using mocks. Then identify: the test is testing behavior (what the use case does with the order and payment) but NOT testing: the actual SQL for finding the order, the actual payment API call. What tests are responsible for those missing parts? Describe the complete test pyramid for a Clean Architecture application.
