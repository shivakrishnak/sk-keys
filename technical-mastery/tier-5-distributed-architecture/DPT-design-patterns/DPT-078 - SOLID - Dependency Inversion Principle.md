---
id: DPT-078
title: "SOLID: Dependency Inversion Principle"
category: Design Patterns
tier: tier-5-distributed-architecture
folder: DPT-design-patterns
difficulty: ★★★
depends_on: DPT-001, DPT-074, DPT-077
used_by: []
related: DPT-073, DPT-074, DPT-075, DPT-076, DPT-077
tags:
  - concept
  - solid
  - advanced
  - dependency-inversion
  - dependency-injection
  - inversion-of-control
status: complete
version: 4
layout: default
parent: "Design Patterns"
grand_parent: "Technical Mastery"
nav_order: 78
permalink: /technical-mastery/design-patterns/dip/
---

⚡ TL;DR - High-level modules should not depend on low-level
modules. Both should depend on abstractions. Abstractions
should not depend on details. Details should depend
on abstractions. DIP decouples policy (business rules)
from mechanism (database, network, framework).

| #78 | Category: Design Patterns | Difficulty: ★★★ |
|:---|:---|:---|
| **Depends on:** | DPT-001, DPT-074, DPT-077 | |
| **Used by:** | N/A | |
| **Related:** | DPT-073, DPT-074, DPT-075, DPT-076, DPT-077 | |

---

### 🔥 The Problem This Solves

**HIGH-LEVEL POLICY COUPLED TO LOW-LEVEL MECHANISM:**
The `OrderService` (high-level business policy: coordinate
an order placement) directly instantiates a
`MySQLOrderRepository` (low-level mechanism: persist to MySQL):

```java
class OrderService {
    private MySQLOrderRepository repo = new MySQLOrderRepository();
    void placeOrder(Order order) {
        repo.save(order); // Directly coupled to MySQL
    }
}
```

**THE PROBLEMS:**
1. To test `OrderService`, a real MySQL database must exist.
   Unit tests cannot run without infrastructure.
2. To switch from MySQL to PostgreSQL: modify `OrderService`.
   The business logic source file changes for a database migration.
3. To support multiple storage backends (MySQL + in-memory for tests,
   Redis for caching): `OrderService` must know all backends.
4. High-level business rules (the "policy") are coupled to
   low-level infrastructure choices (the "mechanism").

**DIP SOLUTION:**
Both `OrderService` AND `MySQLOrderRepository` depend on
the abstraction `OrderRepository`. The dependency direction
is INVERTED: the mechanism now depends on the abstraction
defined by the policy layer, not the other way around.

---

### 📘 Textbook Definition

The **Dependency Inversion Principle (DIP)** is the fifth
SOLID principle (Robert C. Martin):

> "A. High-level modules should not depend on low-level modules.
>  Both should depend on abstractions.
>  B. Abstractions should not depend on details.
>  Details should depend on abstractions."

**"High-level module":**
The module containing business policy, business rules,
application logic. The "why" of what the software does.

**"Low-level module":**
The module containing implementation details, infrastructure,
persistence, communication. The "how" of what the software does.

**"Inversion":**
Without DIP: High-level depends on low-level (natural direction).
With DIP: BOTH depend on an abstraction owned by the high-level.
The dependency direction is INVERTED for the low-level module:
instead of "being used" by the high-level, it now depends on
an abstraction that the high-level defines.

**DIP ≠ Dependency Injection:**
DIP is a design principle (where dependencies point).
Dependency Injection (DI) is a technique that helps
implement DIP (provide dependencies from outside, not
instantiated inside). See DPT-073 for the DI/DIP distinction.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
Business logic should not depend on databases, frameworks,
or external systems directly. It should depend on abstractions
that those details implement.

**One analogy:**
> Electrical outlets.
>
> Without DIP: every appliance is hardwired to a specific
> power plant. To switch power sources (hydro to solar),
> rewire every appliance.
>
> With DIP: appliances depend on the OUTLET STANDARD
> (the abstraction). Power plants implement the standard.
> Switch from hydro to solar: rewire the power plant.
> All appliances: unaffected (they depend on the standard,
> not the specific power source).
>
> DIP: high-level (appliance = business logic) depends
> on the abstraction (outlet = repository interface).
> Low-level (power plant = database) depends on and
> implements the abstraction.

---

### 🔩 First Principles Explanation

**THE NATURAL DEPENDENCY DIRECTION:**
Without DIP, dependencies flow top-down:
```
UI → Business Logic → Data Access → Database
```
Each layer imports and uses the layer below it. Changes
in the database layer propagate upward.

**THE INVERTED DIRECTION:**
With DIP, the high-level layer OWNS the abstraction.
The low-level layer implements it:
```
UI → Business Logic → [Repository Interface (owned by
  Business Logic)]
                                ↑ implements
                         Data Access (MySQL)
```
`Repository Interface` is in the `Business Logic` package.
`Data Access` depends on `Business Logic` (to implement the interface).
Business logic does not depend on data access. Dependency arrow
is INVERTED for the low-level module.

**THE "OWNERSHIP" KEY:**
The CRUCIAL insight: the interface belongs to the HIGH-LEVEL
module, not the low-level module. If `OrderRepository`
is in the `com.example.data` package and `OrderService`
(in `com.example.business`) imports it: DIP is violated.
`OrderRepository` should be in `com.example.business`.
`MySQLOrderRepository` (in `com.example.data`) imports
from `com.example.business`. Correct direction.

**DIP AND CLEAN ARCHITECTURE:**
Robert C. Martin's Clean Architecture places business
entities and use cases at the center (inner layer).
All dependencies point INWARD. Infrastructure (databases,
frameworks, UI) is the outer layer - it depends on
inner abstractions. Inner layers define interfaces;
outer layers implement them. This is DIP applied
at the entire architectural level.

---

### 🧪 Thought Experiment

**TESTABILITY AS DIP PROOF:**
If a class is hard to unit test without infrastructure
(database, network, filesystem), DIP is likely violated.

`OrderService` without DIP: requires MySQL running.
`OrderService` with DIP: use an in-memory `FakeOrderRepository`
implementing `OrderRepository`. Test in milliseconds.

The testability improvement is not coincidental: it is
the direct result of depending on the abstraction.
A fake implementation satisfies the abstraction;
the real infrastructure is not needed for testing.

**"WHAT DO I OWN?"**
Mental model for correct DIP application:
"Which abstractions does my business logic OWN (define)?"
Those are the interfaces in the business layer.
"Which details implement my abstractions?"
Those are the infrastructure/data modules that import
the business layer's interfaces.

---

### 🧠 Mental Model / Analogy

> DIP = the "plug standard" model.
>
> USB standard. The USB standard is defined by the
> device ecosystem (high-level: "what must a USB device do?").
> USB devices (keyboards, drives, cameras = low-level)
> implement the USB standard.
>
> The host device (computer) depends on the USB standard,
> not on specific keyboards or drives.
> Keyboards depend on the USB standard to get included
> in the ecosystem.
>
> Neither the computer nor the keyboard depends on
> the other directly. Both depend on the USB standard.
> The standard is OWNED by the "system" (business domain).
>
> DIP: write the interface from the perspective of the
> business use case (what does the business need?).
> The infrastructure implements the business's interface.
> Not: write the interface to match what the database
> naturally exposes.

---

### 📶 Gradual Depth - Three Levels

**Level 1 - Identifying DIP violations:**
Signals: `new ConcreteService()` inside a business class.
`import com.example.data.*` inside a business logic class.
Business logic methods returning or accepting framework-specific
types (JPA Entity, Hibernate Session, Spring HttpRequest).
Unit tests that require a running database or server.

**Level 2 - Applying DIP via interfaces:**
Define the abstraction (interface) FROM THE PERSPECTIVE
of the business use case: what operations does the business
logic need? The interface is named for the business concept
(`OrderRepository`, `NotificationSender`), not the implementation
(`JdbcOrderRepository`, `SmtpNotificationSender`).
The business class depends on this abstraction.
The infrastructure class implements it.

**Level 3 - DIP and the Dependency Rule:**
In Clean Architecture, DIP is generalized as the
"Dependency Rule": source code dependencies must point
ONLY inward (toward business entities and use cases).
Nothing in an inner circle can know anything about
an outer circle. This means: interfaces cross boundaries
inward; implementations live in outer layers.
Spring Framework implements this via `@Autowired` or
constructor injection: the business class declares
what it needs (the interface); the Spring container
provides the implementation at runtime.

---

### ⚙️ How It Works (Mechanism)

```
DIP: Dependency Direction Inversion
┌─────────────────────────────────────────────────────────┐
│ WITHOUT DIP:                                            │
│   BusinessLayer  ───depends on──►  DataAccessLayer     │
│   (OrderService)                   (MySQLRepo)          │
│                                                         │
│   Changing MySQL → Postgres: modify OrderService.java   │
│   Testing OrderService: need MySQL.                    │
│                                                         │
│ WITH DIP:                                               │
│   BusinessLayer owns the interface:                    │
│   com.example.business                                 │
│     OrderService  ───depends on──►  OrderRepository    │
│     (interface defined here, owned by business layer)  │
│                                                         │
│   com.example.data                                     │
│     MySQLOrderRepo ──implements──► OrderRepository     │
│     (depends on business layer to implement interface) │
│                                                         │
│   Changing MySQL → Postgres:                           │
│     + 1 new file: PostgresOrderRepository              │
│     0 changes to OrderService                          │
│   Testing OrderService:                                │
│     + 1 fake: InMemoryOrderRepository                  │
│     0 infrastructure needed                            │
└─────────────────────────────────────────────────────────┘
```

---

### 💻 Code Example

**Example 1 - DIP violation and fix:**

```java
// BAD: High-level (OrderService) depends on low-level
// (MySQLOrderRepository) directly.

// com.example.data:
class MySQLOrderRepository {
    void save(Order order) { /* MySQL INSERT */ }
    Order findById(long id) { /* MySQL SELECT */ return null; }
}

// com.example.business - imports data layer:
import com.example.data.MySQLOrderRepository; // VIOLATION

class OrderService {
    // Direct instantiation: hardcoded to MySQL.
    private MySQLOrderRepository repo =
        new MySQLOrderRepository();

    void placeOrder(Order order) {
        repo.save(order);
    }
}
// Testing: requires MySQL. Migrating to Postgres: edit OrderService.
```

```java
// GOOD: Both depend on abstraction owned by business layer.

// com.example.business - defines the abstraction (owns it):
interface OrderRepository {          // OWNED by business layer
    void save(Order order);
    Order findById(long id);
}

class OrderService {
    private final OrderRepository repo; // depends on abstraction

    OrderService(OrderRepository repo) { // injected, not new'd
        this.repo = repo;
    }

    void placeOrder(Order order) {
        repo.save(order);           // depends on interface only
    }
}

// com.example.data - depends on business layer's abstraction:
import com.example.business.OrderRepository; // depends inward

class MySQLOrderRepository implements OrderRepository {
    public void save(Order order) { /* MySQL INSERT */ }
    public Order findById(long id) { /* MySQL SELECT */
        return null; }
}

// Testing - no MySQL needed:
class InMemoryOrderRepository implements OrderRepository {
    private final Map<Long, Order> store = new HashMap<>();
    public void save(Order o) { store.put(o.getId(), o); }
    public Order findById(long id) { return store.get(id); }
}

// Test:
class OrderServiceTest {
    @Test
    void placeOrder_savesToRepository() {
        InMemoryOrderRepository repo = new InMemoryOrderRepository();
        OrderService service = new OrderService(repo);
        Order order = new Order(1L, ...);
        service.placeOrder(order);
        assertNotNull(repo.findById(1L)); // milliseconds. No MySQL.
    }
}
```

---

### ⚖️ DIP in Practice

| Scenario | Correct DIP application |
|---|---|
| Business logic needs data persistence | Business layer defines `XxxRepository` interface. Data layer implements it |
| Business logic sends notifications | Business layer defines `NotificationSender` interface. Infrastructure (SMTP, SMS gateway) implements it |
| Business logic calls external service | Business layer defines `ExternalServiceClient` interface. HTTP/REST implementation is in infrastructure layer |
| Framework class (HttpServletRequest) in business layer | DIP violation. Business logic should not import framework types. Wrap framework input in a business-layer value object |

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| DIP = Dependency Injection | DIP is a design principle (dependency direction). DI is an implementation technique. DI helps implement DIP, but they are distinct. A class can use constructor injection without following DIP (if the interface is in the wrong package). See DPT-073 |
| The interface can be anywhere | The interface should be OWNED by the high-level module. If `OrderRepository` is in the `data` package and `OrderService` imports it: the dependency still points from business to data. Not inverted. Interface location matters |
| DIP means all classes need interfaces | DIP applies to relationships ACROSS ARCHITECTURAL BOUNDARIES (business logic to infrastructure). Utility classes, value objects, and domain entities typically do not need interfaces for DIP compliance |
| Spring's @Autowired implements DIP | Spring DI satisfies the "inject from outside" requirement (which helps DIP) but does not GUARANTEE DIP. You can use @Autowired and still have business logic depending on JPA entities (importing from the data layer). DIP = dependency direction, not just injection |

---

### 📌 Quick Reference Card

```
┌─────────────────────────────────────────────────────────┐
│ DEFINITION   │ High-level (policy) and low-level       │
│              │ (mechanism) both depend on abstractions │
├──────────────┼──────────────────────────────────────────┤
│ KEY RULE     │ Interface OWNED by high-level module.   │
│              │ Low-level implements the interface.     │
├──────────────┼──────────────────────────────────────────┤
│ VIOLATION    │ Business class imports from data layer. │
│              │ new ConcreteImpl() inside business class│
│              │ Business method accepts framework type  │
├──────────────┼──────────────────────────────────────────┤
│ DIP ≠ DI     │ DIP = which way dependencies point.     │
│              │ DI = technique for providing dependencies│
├──────────────┼──────────────────────────────────────────┤
│ TESTABILITY  │ DIP = no infrastructure needed for unit │
│              │ tests. Fake/in-memory impls are possible│
├──────────────┼──────────────────────────────────────────┤
│ NEXT EXPLORE │ DPT-079: Repository Pattern             │
└─────────────────────────────────────────────────────────┘
```

**If you remember only 3 things:**
1. DIP = both high-level AND low-level depend on the
   abstraction. The abstraction is OWNED by the high-level
   module. The low-level module depends on the high-level
   module to implement the interface. Dependency direction
   is inverted for the low-level.
2. If business logic contains `new SomeConcrete()` or
   imports from infrastructure packages: DIP is violated.
   Business logic should depend only on interfaces
   it defines in its own package.
3. DIP ≠ Dependency Injection. DI is a technique that
   helps achieve DIP. You can have DI without DIP
   (interface in wrong layer). DIP tells you WHERE
   the abstraction lives; DI tells you HOW dependencies
   are provided.

