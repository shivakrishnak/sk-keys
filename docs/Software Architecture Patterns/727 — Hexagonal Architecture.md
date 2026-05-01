---
layout: default
title: "Hexagonal Architecture"
parent: "Software Architecture Patterns"
nav_order: 727
permalink: /software-architecture/hexagonal-architecture/
number: "727"
category: Software Architecture Patterns
difficulty: ★★★
depends_on: "Layered Architecture, Dependency Inversion Principle, Ports and Adapters"
used_by: "Domain-Driven Design applications, Clean Code projects, Spring Boot, Quarkus"
tags: #advanced, #architecture, #ddd, #ports-and-adapters, #dependency-inversion
---

# 727 — Hexagonal Architecture

`#advanced` `#architecture` `#ddd` `#ports-and-adapters` `#dependency-inversion`

⚡ TL;DR — **Hexagonal architecture** (Ports and Adapters) puts the **domain at the center**, with all external concerns (HTTP, DB, MQ) as **adapters** plugged in through **ports (interfaces)** — so the domain never depends on infrastructure; infrastructure depends on domain.

| #727            | Category: Software Architecture Patterns                                     | Difficulty: ★★★ |
| :-------------- | :--------------------------------------------------------------------------- | :-------------- |
| **Depends on:** | Layered Architecture, Dependency Inversion Principle, Ports and Adapters     |                 |
| **Used by:**    | Domain-Driven Design applications, Clean Code projects, Spring Boot, Quarkus |                 |

---

### 📘 Textbook Definition

**Hexagonal architecture**, coined by Alistair Cockburn (2005), also known as **Ports and Adapters**, is an architectural pattern that isolates the application's core domain from all external dependencies (frameworks, databases, UIs, message queues) by using **ports** (interfaces defined by the domain) and **adapters** (implementations that connect external systems to those interfaces). The central insight: **the domain defines what it needs (ports); external systems adapt to meet those needs (adapters)**. Direction of dependency: always inward toward the domain — the domain depends on nothing outside itself. The hexagon shape (6 sides): each side is a port. **Primary ports** (driving ports): how the outside world drives the application (HTTP, CLI, tests). **Secondary ports** (driven ports): how the application talks to external services (database, email, cache). Benefits: (1) technology-agnostic domain (no framework imports). (2) Fully testable domain without infrastructure. (3) Swap adapters freely (PostgreSQL → MongoDB: change adapter, not domain). Closely related to **Clean Architecture** (Robert Martin) and **Onion Architecture** (Jeffrey Palermo) — all enforce the same dependency rule.

---

### 🟢 Simple Definition (Easy)

A laptop with USB ports: you can plug in a keyboard, mouse, or printer via the USB port. The laptop's CPU (domain) doesn't care what's plugged in — it just knows the port interface. The keyboard, mouse, and printer are adapters that speak the USB protocol (port). You can swap a wired keyboard for a wireless one without changing the laptop. Hexagonal architecture: the domain is the laptop's CPU. Ports: USB interfaces defined by the domain. Adapters: the specific keyboards, databases, REST APIs that plug into those ports.

---

### 🔵 Simple Definition (Elaborated)

In a traditional layered architecture: Service calls Repository directly. The Service layer knows about JPA, SQL, Hibernate. To test the Service: need a database. In hexagonal architecture: Service calls an interface (port). The concrete JPA implementation (adapter) is injected at runtime. Testing: inject a mock/in-memory adapter. No real database needed. Swap PostgreSQL for DynamoDB: write a new adapter implementing the same port interface. Domain unchanged. Frameworks (Spring, Quarkus): details — the domain doesn't import them. This is the Dependency Inversion Principle applied at architectural scale.

---

### 🔩 First Principles Explanation

**Ports, adapters, dependency direction, and Spring implementation:**

```
HEXAGONAL ARCHITECTURE STRUCTURE:

                   ┌─────────────────────────┐
    HTTP Adapter   │                         │   JPA Adapter
  (REST Controller)│      APPLICATION        │  (Implements UserRepository Port)
         │         │       DOMAIN            │         ▲
         │         │                         │         │
         ▼         │  - Domain Entities      │         │
  ┌──────────┐     │  - Domain Services      │   ┌──────────┐
  │ Driving  │──►  │  - Ports (interfaces)   │──►│ Driven   │
  │ Adapter  │     │    defined BY domain    │   │ Adapter  │
  └──────────┘     │                         │   └──────────┘
                   │  No framework imports   │
    CLI Adapter    │  No DB imports          │   Email Adapter
  (Command line)   └─────────────────────────┘  (Implements EmailPort)

DEPENDENCY DIRECTION:

  WRONG (layered — domain depends on infrastructure):
    UserService → UserRepository (JPA implementation)
    UserService imports: javax.persistence, org.springframework.data.jpa
    Problem: can't test UserService without a database.

  RIGHT (hexagonal — infrastructure depends on domain):
    UserService → UserRepositoryPort (interface, defined in domain package)
    JpaUserRepository implements UserRepositoryPort (in infrastructure package)

    Domain package imports: nothing external (only Java stdlib + domain classes)
    Infrastructure package imports: JPA, Spring, etc.

PORTS (defined in domain):

  // Driven port (secondary — domain drives external system):
  // Lives in: domain/ports/out/ package
  public interface UserRepositoryPort {
      Optional<User> findById(UserId id);
      User save(User user);
      List<User> findByEmail(Email email);
  }

  // Driven port (secondary — outgoing notification):
  public interface EmailNotificationPort {
      void sendWelcomeEmail(Email email, UserName name);
  }

  // Driving port (primary — external world drives the application):
  // Lives in: domain/ports/in/ package
  public interface RegisterUserUseCase {
      User register(RegisterUserCommand command);
  }

ADAPTERS (in infrastructure package):

  // Driven adapter: JPA implementation of UserRepositoryPort
  // Lives in: infrastructure/adapters/out/persistence/
  @Repository
  public class JpaUserRepositoryAdapter implements UserRepositoryPort {
      private final SpringDataUserRepository jpaRepo;

      @Override
      public Optional<User> findById(UserId id) {
          return jpaRepo.findById(id.value()).map(UserMapper::toDomain);
          // Note: toDomain() maps JPA entity to domain entity. Domain entity is clean.
      }

      @Override
      public User save(User user) {
          UserJpaEntity entity = UserMapper.toJpaEntity(user);
          return UserMapper.toDomain(jpaRepo.save(entity));
      }
  }

  // Driving adapter: REST controller
  // Lives in: infrastructure/adapters/in/web/
  @RestController
  @RequestMapping("/api/users")
  public class UserRestAdapter {
      private final RegisterUserUseCase registerUserUseCase;  // Driving port.

      @PostMapping("/register")
      public ResponseEntity<UserResponse> register(@RequestBody RegisterRequest request) {
          RegisterUserCommand command = new RegisterUserCommand(request.email(), request.name());
          User user = registerUserUseCase.register(command);  // Calls domain through port.
          return ResponseEntity.status(201).body(UserResponse.from(user));
      }
  }

DOMAIN SERVICE (pure domain — no infrastructure):

  // Lives in: domain/services/ or domain/usecases/
  @Service  // Spring annotation is optional here — domain is framework-agnostic
  public class UserDomainService implements RegisterUserUseCase {
      private final UserRepositoryPort userRepository;   // Port (interface).
      private final EmailNotificationPort emailService;  // Port (interface).

      public User register(RegisterUserCommand command) {
          // Pure domain logic. No JPA, no HTTP, no Spring:
          if (userRepository.findByEmail(command.email()).isPresent()) {
              throw new UserAlreadyExistsException(command.email());
          }
          User user = User.create(command.email(), command.name());  // Domain factory.
          User saved = userRepository.save(user);  // Calls port (adapter injected at runtime).
          emailService.sendWelcomeEmail(saved.email(), saved.name());  // Calls port.
          return saved;
      }
  }

PACKAGE STRUCTURE:

  src/main/java/
  ├── domain/                    ← PURE DOMAIN (no external imports)
  │   ├── entities/
  │   │   ├── User.java
  │   │   └── UserId.java
  │   ├── ports/
  │   │   ├── in/                ← Driving ports (use cases)
  │   │   │   └── RegisterUserUseCase.java
  │   │   └── out/               ← Driven ports (infrastructure)
  │   │       ├── UserRepositoryPort.java
  │   │       └── EmailNotificationPort.java
  │   └── services/
  │       └── UserDomainService.java
  └── infrastructure/            ← ADAPTERS (imports frameworks freely)
      ├── adapters/
      │   ├── in/
      │   │   └── web/
      │   │       └── UserRestAdapter.java
      │   └── out/
      │       ├── persistence/
      │       │   ├── JpaUserRepositoryAdapter.java
      │       │   └── UserJpaEntity.java
      │       └── email/
      │           └── SendgridEmailAdapter.java
      └── config/
          └── BeanConfig.java    ← Spring wiring: inject adapters into domain services.

TESTING ADVANTAGE:

  // Unit test for domain service — NO database, NO HTTP:
  @Test
  void shouldRejectDuplicateEmailRegistration() {
      // Use mocks/stubs instead of real adapters:
      UserRepositoryPort repo = mock(UserRepositoryPort.class);
      when(repo.findByEmail(email)).thenReturn(Optional.of(existingUser));

      UserDomainService service = new UserDomainService(repo, mock(EmailNotificationPort.class));

      assertThrows(UserAlreadyExistsException.class,
          () -> service.register(new RegisterUserCommand(email, name)));
      // Test runs in milliseconds. No Spring context. No database.
  }
```

---

### ❓ Why Does This Exist (Why Before What)

WITHOUT hexagonal architecture:

- Domain logic coupled to JPA: can't test without database
- Change from MySQL to DynamoDB: affects domain service code
- Add a Kafka consumer alongside HTTP API: must duplicate domain logic

WITH hexagonal architecture:
→ Domain tested in isolation: inject mock adapters, no infrastructure required
→ Multiple delivery mechanisms: REST, CLI, Kafka — all use same domain through ports
→ Swap database adapter: domain unchanged; only swap adapter implementation

---

### 🧠 Mental Model / Analogy

> A USB hub: the hub (domain) defines the USB port standard. Any device (keyboard, mouse, hard drive) that speaks USB (adapts to the port) can plug in. The hub doesn't care what's plugged in — it just knows the interface. Crucially: the hub defines the port standard; devices adapt to the hub's standard. The hub doesn't adapt to each device. This is the inversion: domain defines the contract; external systems adapt to meet it.

"USB hub" = Application domain
"USB port standard" = Port interfaces defined by the domain
"Keyboard/mouse/hard drive" = Adapters (REST controller, JPA repository, email sender)
"Adapting to USB standard" = Implementing the port interfaces

---

### ⚙️ How It Works (Mechanism)

```
REQUEST FLOW (hexagonal):

  1. HTTP request → UserRestAdapter (driving adapter)
  2. Adapter calls: registerUserUseCase.register(command) [driving port]
  3. UserDomainService.register() — PURE domain logic, no infrastructure
  4. Service calls: userRepository.save(user) [driven port]
  5. JpaUserRepositoryAdapter.save(user) — JPA implements the port
  6. Response: JPA entity → domain entity → DTO → JSON (each layer converts cleanly)
```

---

### 🔄 How It Connects (Mini-Map)

```
Dependency Inversion Principle (high-level modules don't depend on low-level)
        │
        ▼ (applied architecturally)
Hexagonal Architecture ◄──── (you are here)
(domain defines ports; adapters implement ports; domain at center)
        │
        ├── Clean Architecture: same dependency rule, different naming (entities/use cases/adapters)
        ├── Onion Architecture: concentric rings with domain at center
        └── Layered Architecture: traditional alternative (domain depends on infrastructure)
```

---

### 💻 Code Example

```java
// See the full code example in the First Principles section above.
// Key summary of the pattern:

// 1. Port (domain defines the interface):
public interface PaymentGatewayPort {
    PaymentResult charge(CreditCard card, Money amount);
}

// 2. Adapter (infrastructure implements the port):
public class StripePaymentAdapter implements PaymentGatewayPort {
    private final StripeClient stripe;  // External library — only here, not in domain.

    @Override
    public PaymentResult charge(CreditCard card, Money amount) {
        StripeCharge charge = stripe.charge(card.number(), amount.cents());
        return PaymentResult.from(charge.status());
    }
}

// 3. Alternative adapter (swap infrastructure, domain unchanged):
public class PayPalPaymentAdapter implements PaymentGatewayPort {
    @Override
    public PaymentResult charge(CreditCard card, Money amount) {
        // PayPal-specific implementation. Domain is completely unaffected.
    }
}

// 4. Domain service (knows nothing about Stripe or PayPal):
public class OrderService {
    private final PaymentGatewayPort paymentGateway;  // Port, not Stripe or PayPal.

    public Order checkout(Cart cart, CreditCard card) {
        PaymentResult result = paymentGateway.charge(card, cart.total());
        if (!result.isSuccessful()) throw new PaymentFailedException();
        return Order.create(cart);
    }
}
```

---

### ⚠️ Common Misconceptions

| Misconception                                                              | Reality                                                                                                                                                                                                                                                                                                                                                                                                                               |
| -------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Hexagonal architecture means the domain package has no Spring annotations  | Spring annotations (@Service, @Component) in the domain are acceptable if the team treats them as metadata. The real rule: domain should NOT import JPA entities, StripeClient, HttpServletRequest, etc. Spring's core annotations (@Service) are often considered acceptable; Spring Data JPA repositories are not. The test is: can you instantiate and test your domain service with `new DomainService(mockPort)` without Spring? |
| Hexagonal architecture eliminates all integration testing                  | Hexagonal architecture eliminates the need for infrastructure in UNIT tests of domain logic. But you still need integration tests: does the JPA adapter actually produce the right SQL? Does the Stripe adapter handle failures correctly? Hexagonal: makes unit testing easy; still need integration tests for adapters. Net result: fewer slow integration tests (domain fully covered by fast unit tests)                          |
| Creating a port for every external dependency is always the right approach | For small services or early-stage projects: creating ports and adapters for every dependency is over-engineering. A direct JPA repository with `@Repository` in a small service is fine. Hexagonal architecture is most valuable: when the domain is complex, when multiple delivery mechanisms exist (REST + Kafka + CLI), or when the database is likely to change. Match architectural complexity to problem complexity            |

---

### 🔥 Pitfalls in Production

**Domain entity and JPA entity conflation — the most common hexagonal architecture mistake:**

```
BAD: Using JPA entity as domain entity (directly in domain package):

  // WRONG: JPA annotations inside domain entity.
  @Entity
  @Table(name = "users")
  public class User {  // This is in domain/entities/User.java
      @Id @GeneratedValue
      private Long id;

      @Column(name = "email")
      private String email;

      // JPA requires no-args constructor. Domain entity: should be immutable.
      public User() {}  // JPA-required. Breaks domain encapsulation.
  }

  PROBLEMS:
    - Domain entity is coupled to JPA (imports javax.persistence).
    - JPA requires mutable public no-args constructor → violates domain encapsulation.
    - JPA annotations are persistence concerns, not domain concerns.
    - Can't use the domain entity without the JPA runtime (Hibernate on classpath).
    - "Anemic domain model" emerges because JPA entities can't have complex constructors.

FIX: Separate domain entity from JPA entity. Map between them in the adapter:

  // DOMAIN entity (pure, no JPA):
  // domain/entities/User.java
  public final class User {
      private final UserId id;
      private final Email email;
      private final UserName name;

      public static User create(Email email, UserName name) {
          return new User(UserId.generate(), email, name);  // Factory method. No public constructor.
      }
      // Getters only. Immutable. No JPA annotations. No framework imports.
  }

  // JPA ENTITY (infrastructure concern, in adapter package):
  // infrastructure/adapters/out/persistence/UserJpaEntity.java
  @Entity
  @Table(name = "users")
  public class UserJpaEntity {
      @Id Long id;
      String email;
      String name;
      public UserJpaEntity() {}  // JPA-required. Fine here — this is infrastructure.
  }

  // MAPPER (in adapter — converts between domain and JPA):
  public class UserMapper {
      public static User toDomain(UserJpaEntity entity) {
          return new User(UserId.of(entity.id), Email.of(entity.email), UserName.of(entity.name));
      }
      public static UserJpaEntity toJpaEntity(User user) {
          UserJpaEntity e = new UserJpaEntity();
          e.id = user.id().value();
          e.email = user.email().value();
          e.name = user.name().value();
          return e;
      }
  }
  // Extra effort: writing the mapper. Payoff: clean domain, testable, JPA-independent.
```

---

### 🔗 Related Keywords

- `Clean Architecture` — same dependency rule, different layers: entities → use cases → adapters → frameworks
- `Ports and Adapters` — the synonymous alternative name for hexagonal architecture
- `Onion Architecture` — similar: concentric rings with domain at center
- `Layered Architecture` — traditional alternative: domain depends on infrastructure (inverted)
- `Dependency Inversion Principle` — the core SOLID principle underlying hexagonal architecture

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ KEY IDEA     │ Domain at center. Ports = interfaces the │
│              │ domain defines. Adapters = infrastructure│
│              │ plugged into ports. Domain depends on    │
│              │ nothing external.                        │
├──────────────┼───────────────────────────────────────────┤
│ USE WHEN     │ Complex domain; multiple delivery        │
│              │ mechanisms (REST+Kafka+CLI); DDD;        │
│              │ need to test domain without infra        │
├──────────────┼───────────────────────────────────────────┤
│ AVOID WHEN   │ Simple CRUD service; early-stage project;│
│              │ overhead outweighs benefit               │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "USB hub: hub defines the port standard; │
│              │  devices adapt to plug in. Domain        │
│              │  defines; infrastructure adapts."        │
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ Clean Architecture → Onion Architecture →│
│              │ DDD → Repository Pattern → DIP           │
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** You have a hexagonal architecture application with a `UserRepositoryPort` interface. Currently: one adapter (JpaUserRepositoryAdapter for PostgreSQL). New requirement: some user data must be cached in Redis for performance; user authentication data must stay in PostgreSQL for consistency. Design: do you create a new `CacheUserRepositoryPort` or modify the existing port? Where does the cache-aside logic live? In the adapter? The domain service? A separate "caching adapter" that wraps the JPA adapter?

**Q2.** A team argument: "Hexagonal architecture adds too many files — ports, adapters, mappers, domain entities, JPA entities. For our 30-endpoint CRUD API, layered architecture is simpler." Evaluate this argument. What threshold of complexity justifies hexagonal over layered? Give 3 concrete signals in your codebase that indicate you've outgrown layered architecture and should migrate toward hexagonal.
