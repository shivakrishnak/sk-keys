---
id: DPT-073
title: Dependency Inversion vs Dependency Injection
category: Design Patterns
tier: tier-5-distributed-architecture
folder: DPT-design-patterns
difficulty: ★★★
depends_on: DPT-001, DPT-039, DPT-078
used_by: []
related: DPT-039, DPT-078, DPT-038, DPT-074
tags:
  - concept
  - solid
  - advanced
  - dependency-inversion
  - dependency-injection
  - ioc
status: complete
version: 4
layout: default
parent: "Design Patterns"
grand_parent: "Technical Mastery"
nav_order: 73
permalink: /technical-mastery/design-patterns/dependency-inversion-vs-injection/
---

⚡ TL;DR - Dependency Inversion (DIP) is a design PRINCIPLE:
high-level modules should not depend on low-level modules;
both should depend on abstractions. Dependency Injection
(DI) is a MECHANISM for implementing DIP: it passes
(injects) concrete implementations into high-level modules
at runtime. DIP is the what; DI is the how.

| #73 | Category: Design Patterns | Difficulty: ★★★ |
|:---|:---|:---|
| **Depends on:** | DPT-001, DPT-039, DPT-078 | |
| **Used by:** | N/A | |
| **Related:** | DPT-039, DPT-078, DPT-038, DPT-074 | |

---

### 🔥 The Problem This Solves

**THE NAMING CONFUSION:**
Most engineers use "dependency injection" and "dependency
inversion" interchangeably. They are NOT the same:
- DIP (D in SOLID): an architectural principle about
  where dependencies point in a design.
- DI (Dependency Injection): a technique for providing
  objects with their dependencies.

You can have DI without DIP (inject concrete classes,
not abstractions). You can have DIP without DI (a factory
resolves the inversion without injection). Understanding
the distinction enables correct use of both.

**THE PRACTICAL CONSEQUENCE:**
Teams using Spring's DI framework believe they are following
DIP. Not necessarily. If they inject concrete classes
(`@Autowired ConcretePaymentGateway`), they have DI without
DIP. The dependency direction has not been inverted.
High-level business logic still depends on low-level
concrete implementation.

---

### 📘 Textbook Definition

**Dependency Inversion Principle (DIP):**
One of the SOLID principles (Robert C. Martin):
> "High-level modules should not depend upon low-level
> modules. Both should depend upon abstractions. Abstractions
> should not depend upon details. Details should depend
> upon abstractions."

The key word: INVERSION. In traditional design, high-level
policy code depends on low-level detail code (database,
HTTP, filesystem). DIP inverts this: the detail code
depends on an abstraction owned by the high-level policy
code. The dependency arrow is reversed.

**Dependency Injection (DI):**
A technique (and Pattern, per Martin Fowler) for providing
a class with its dependencies from outside rather than
having the class create them internally. Three forms:
1. **Constructor injection**: dependencies provided at
   construction time.
2. **Setter injection**: dependencies provided via setters.
3. **Interface injection**: dependencies provided via
   a method call defined in an interface.

**Relationship:** DI is one way to implement DIP.
It is not the only way. A Factory or Service Locator
can also implement DIP. DI is also used without DIP
(injecting concrete classes without abstractions).

---

### ⏱️ Understand It in 30 Seconds

**One line:**
DIP is the principle (abstractions, inverted dependencies).
DI is one technique to implement it (pass dependencies in).

**One analogy:**
> PRINCIPLE: "Use interchangeable parts in manufacturing."
> (High-level assembly does not depend on specific screws.)
>
> MECHANISM: "Standardized thread sizes" (injection:
> the correct screw is passed to the assembler at assembly time).
>
> You could implement interchangeable parts with OTHER
> mechanisms too (3D printing to spec, custom order).
> And you could use standard thread sizes WITHOUT interchangeable
> parts (just to make assembly easier, with specific parts).
>
> DIP = "use interchangeable parts" principle.
> DI = "standardized thread sizes" mechanism.
> Related but not the same.

---

### 🔩 First Principles Explanation

**WHAT "INVERSION" MEANS:**

Without DIP (traditional direction):
```
[Order Service]  → depends on → [MySQL Database]
(high-level)                    (low-level detail)
```
Order Service imports MySQL-specific classes. Change
the database: change Order Service code.

With DIP (inverted direction):
```
[Order Service]  → depends on → [Repository Interface]
(high-level)                    (abstraction - owned by
                                 high-level domain)
                                      ↑ depends on
                               [MySQL Repository
                                 Implementation]
                               (low-level detail)
```
The MySQL implementation depends on the Repository
interface (which it must implement). The dependency
arrow FROM MySQL TO the interface points TOWARD the
high-level domain. The direction is INVERTED.

**DI WITHOUT DIP:**
```java
// DI used, but DIP violated: concrete class injected
@Service
class OrderService {
    @Autowired
    MySqlOrderRepository repository; // CONCRETE, not interface
    // DI: Spring injects this. DIP: violated (depends on
    // MySqlOrderRepository).
}
```

**DI WITH DIP:**
```java
// Both DI and DIP: interface injected
@Service
class OrderService {
    private final OrderRepository repository; // ABSTRACTION
    // DI: Spring injects the concrete implementation.
    // DIP: OrderService depends only on the OrderRepository
    // interface.
    OrderService(OrderRepository repository) {
        this.repository = repository;
    }
}
```

**DIP WITHOUT DI (Factory Method):**
```java
// DIP achieved without DI framework: factory provides the impl
class OrderService {
    private final OrderRepository repository;

    OrderService() {
        // Factory provides the concrete implementation.
        // OrderService depends on OrderRepository interface (DIP).
        // No DI framework used.
        this.repository = OrderRepositoryFactory.create();
    }
}
```

---

### 🧪 Thought Experiment

**THE TEST ISOLATION TEST:**

A service is correctly following DIP if you can test
it with a mock/stub implementation of its dependencies
WITHOUT a DI framework.

**Test with DIP (correct):**
```java
OrderService service = new OrderService(
    new InMemoryOrderRepository()); // stub, no framework
service.placeOrder(order); // runs without DB
```

**Test without DIP (injection but no inversion):**
```java
OrderService service = new OrderService();
// Cannot substitute MySqlOrderRepository with a stub
// without a DI framework's mock injection mechanism.
// DIP is violated: the class creates its own concrete dependency.
```

If you need a DI framework to test with a mock: DIP may
be violated. With DIP, constructor injection enables
testing without any framework.

---

### 🧠 Mental Model / Analogy

> DIP vs DI = "Policy vs Mechanism."
> A security policy: "All visitors must be authenticated."
> (DIP: high-level depends on abstraction "authenticated visitor,"
> not on the specific "password check" implementation.)
>
> Implementation mechanisms for authentication:
> - Password check
> - OAuth token
> - Biometric scan
> (DI: the specific mechanism is "injected" into the security
> checkpoint at runtime based on the context.)
>
> The policy (DIP) is independent of the mechanism (DI).
> You could implement the policy with any mechanism.
> The mechanism (DI framework) supports any policy, not just DIP.
>
> Policy (DIP) is about where the dependency arrow points.
> Mechanism (DI) is about how the concrete dependency is provided.

---

### 📶 Gradual Depth - Three Levels

**Level 1 - The practical distinction:**
DIP: always depend on interfaces/abstractions, never on
concrete classes in your core business logic.
DI: use constructor injection to receive those abstractions
from outside the class.
Applied together: testable, flexible, loosely coupled code.

**Level 2 - Ownership of the abstraction:**
DIP specifies not just "use an interface" but that the
ABSTRACTION IS OWNED BY THE HIGH-LEVEL MODULE. The Repository
interface is defined in the DOMAIN layer (high-level),
not in the infrastructure layer (low-level). This is the
"inversion" of typical dependency direction.

**Level 3 - Plugin Architecture:**
When DIP is applied consistently: the high-level policy
(domain logic) becomes independent of ALL low-level details
(database, messaging, HTTP, filesystem). Details become
"plugins" - they implement the interfaces owned by the
domain. This is the Plugin Architecture: the domain
is the stable core; infrastructure details are plugged in.
Spring, Hibernate, Kafka: all "plugins" in a well-designed
DIP system. The domain has no dependency on any of them.

---

### ⚙️ How It Works (Mechanism)

```
Dependency Direction: Traditional vs DIP
┌─────────────────────────────────────────────────────────┐
│ TRADITIONAL (without DIP)                               │
│                                                         │
│  [Domain Layer]  → import → [Infrastructure Layer]     │
│  OrderService       imports   MySqlOrderRepository      │
│  (high-level)                 (low-level)               │
│                                                         │
│  Change database → change OrderService code             │
│                                                         │
│ WITH DIP                                                │
│                                                         │
│  [Domain Layer]                                         │
│  OrderRepository  ← implements ← MySqlOrderRepository  │
│  (interface)          (depends on interface)            │
│      ↑ depends on                                       │
│  OrderService                                           │
│                                                         │
│  Change database → create new Infrastructure impl.      │
│  OrderService: unchanged.                               │
└─────────────────────────────────────────────────────────┘
```

---

### 💻 Code Example

**Example 1 - DI without DIP (common mistake):**

```java
// BAD: Dependency Injection used, but DIP violated.
// OrderService depends on a concrete class.

@Service
class OrderService {

    // Spring injects this (DI = YES).
    // But it's a concrete class (DIP = VIOLATED).
    @Autowired
    JdbcOrderRepository repository;

    // Also injects a concrete class:
    @Autowired
    SmtpEmailService emailService;

    public void placeOrder(Order order) {
        repository.save(order);
        emailService.sendConfirmation(order);
    }
}
// Cannot test without a real DB and real SMTP server.
// Change DB technology: change OrderService imports.
```

**Example 2 - DI with DIP (correct):**

```java
// GOOD: DI + DIP. Constructor injection of ABSTRACTIONS.
// Abstractions are owned by the Domain layer.

// Abstraction (owned by domain - in domain package):
public interface OrderRepository {     // domain package
    void save(Order order);
    Order findById(OrderId id);
}

public interface EmailService {        // domain package
    void sendConfirmation(Order order);
}

// High-level module: depends on abstractions only
@Service
public class OrderService {
    private final OrderRepository repository; // interface only
    private final EmailService emailService;  // interface only

    // Constructor injection (DI mechanism)
    public OrderService(
            OrderRepository repository,
            EmailService emailService) {
        this.repository = repository;
        this.emailService = emailService;
    }

    public void placeOrder(Order order) {
        repository.save(order);
        emailService.sendConfirmation(order);
    }
}

// Infrastructure: implements the domain abstractions
@Repository
class JdbcOrderRepository implements OrderRepository {...}

@Service
class SmtpEmailService implements EmailService {...}
```

```java
// Test: no Spring, no DB, no SMTP
class OrderServiceTest {
    @Test
    void testOrderPlacement() {
        // Constructor injection with stubs:
        OrderService service = new OrderService(
            new InMemoryOrderRepository(),  // stub
            new NoOpEmailService());        // stub
        service.placeOrder(new Order(...));
        // Test without infrastructure. DIP makes this possible.
    }
}
```

---

### ⚖️ DIP vs DI Summary

| Aspect | DIP (Principle) | DI (Mechanism) |
|---|---|---|
| What it is | SOLID D: design principle | Technique / pattern |
| What it says | Depend on abstractions, not concretions. Abstractions owned by high-level module | Pass dependencies from outside the class |
| Can exist without the other | Yes (Factory implements DIP without DI) | Yes (inject concrete classes without DIP) |
| Purpose | Decouple high-level from low-level | Decouple class from responsibility of creating dependencies |
| Indicator of correct use | Test domain with stubs without DI framework | Testability using constructor injection |

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| Using Spring @Autowired means you're following DIP | Not necessarily. If you inject concrete classes: DI yes, DIP no. DIP requires injecting ABSTRACTIONS (interfaces), not concrete implementations |
| DIP means always using interfaces for everything | DIP means high-level modules depend on abstractions. In practice: domain logic depends on interfaces; infrastructure implementations depend on those interfaces. Utility classes and value objects may not need interfaces |
| You need a DI framework to implement DIP | No. Manual constructor injection, factories, and service locators can all implement DIP without a framework. DI frameworks make it convenient but are not required |
| The "D" in SOLID is Dependency Injection | The "D" is Dependency Inversion Principle. DI (Dependency Injection) is a common mechanism for implementing DIP but is not itself the principle |

---

### 📌 Quick Reference Card

```
┌─────────────────────────────────────────────────────────┐
│ DIP = WHAT   │ Principle: high-level depends on         │
│              │ abstractions, not concretions. Arrows    │
│              │ point toward abstractions.              │
├──────────────┼──────────────────────────────────────────┤
│ DI = HOW     │ Mechanism: pass the concrete impl from   │
│              │ outside (constructor/setter injection).  │
├──────────────┼──────────────────────────────────────────┤
│ DI without   │ Inject concrete classes (e.g.,           │
│ DIP (wrong)  │ @Autowired MySqlRepository). DI used;   │
│              │ DIP violated.                           │
├──────────────┼──────────────────────────────────────────┤
│ DIP WITHOUT  │ Factory creates the concrete impl.       │
│ DI (valid)   │ High-level depends on interface (DIP).  │
│              │ No DI framework used.                   │
├──────────────┼──────────────────────────────────────────┤
│ DIP TEST     │ Can you test domain logic with a stub    │
│              │ without a DI framework? YES = DIP ok.   │
├──────────────┼──────────────────────────────────────────┤
│ NEXT EXPLORE │ DPT-074: SOLID - SRP                    │
└─────────────────────────────────────────────────────────┘
```

**If you remember only 3 things:**
1. DIP (principle): high-level modules depend on abstractions
   they OWN, not on low-level concretions. Dependency arrow
   is inverted: low-level implements interfaces owned by
   high-level.
2. DI (mechanism): pass dependencies from outside the class.
   DI implements DIP when the injected dependency is an
   abstraction. DI violates DIP when a concrete class is
   injected.
3. Test: if you can test domain logic with a stub constructed
   directly (without a DI framework), DIP is correctly
   applied. If you need Mockito or Spring test context
   to substitute a dependency: DIP is likely violated.

