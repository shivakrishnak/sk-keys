---
layout: default
title: "Layered Architecture"
parent: "Software Architecture Patterns"
nav_order: 726
permalink: /software-architecture/layered-architecture/
number: "726"
category: Software Architecture Patterns
difficulty: ★★
depends_on: "Separation of Concerns, Cohesion, Coupling"
used_by: "Spring MVC, .NET MVC, Django, Rails, Enterprise Applications"
tags: #intermediate, #architecture, #design, #layers, #separation-of-concerns
---

# 726 — Layered Architecture

`#intermediate` `#architecture` `#design` `#layers` `#separation-of-concerns`

⚡ TL;DR — **Layered architecture** organizes code into horizontal layers (Presentation → Business Logic → Data Access → Database), where each layer only communicates with the layer directly below it — enforcing separation of concerns at architectural scale.

| #726            | Category: Software Architecture Patterns                     | Difficulty: ★★ |
| :-------------- | :----------------------------------------------------------- | :------------- |
| **Depends on:** | Separation of Concerns, Cohesion, Coupling                   |                |
| **Used by:**    | Spring MVC, .NET MVC, Django, Rails, Enterprise Applications |                |

---

### 📘 Textbook Definition

**Layered architecture** (also called **N-tier architecture**) is an architectural pattern that organizes an application into horizontal layers, each with a specific responsibility. The most common structure is the **three-tier** or **four-layer** model: (1) **Presentation Layer** — handles user interface and HTTP concerns (controllers, views, REST endpoints). (2) **Business Logic Layer** (Service Layer) — implements domain rules, use cases, orchestration. (3) **Data Access Layer** (Repository/DAO) — encapsulates database interactions. (4) **Database Layer** — the actual data store. A **strict layered architecture** enforces that each layer can only call the layer directly below it (no skipping layers). A **relaxed layered architecture** allows layers to call any layer below (Presentation can call Data Access directly). Benefits: separation of concerns, testability, replaceability of individual layers. Drawback: **sinkhole anti-pattern** — requests passing through many layers that only delegate without adding value.

---

### 🟢 Simple Definition (Easy)

A restaurant kitchen: (1) Waiter (Presentation) — takes orders from customers, delivers food. (2) Chef (Business Logic) — decides how to cook, manages recipes. (3) Sous-chef (Data Access) — retrieves ingredients from storage. (4) Pantry (Database) — stores all ingredients. The waiter doesn't go into the pantry directly — they always go through the chef. Each layer has one job. Change the pantry layout without affecting the waiter. Change the menu (business rules) without changing how the waiter interacts with customers.

---

### 🔵 Simple Definition (Elaborated)

In a Spring MVC application: Controller (Presentation) receives HTTP requests. Controller calls Service (Business Logic). Service calls Repository (Data Access). Repository talks to the database. Tests: mock the repository to test the service logic in isolation. Change from MySQL to PostgreSQL: only change the repository layer. Add a new delivery mechanism (GraphQL instead of REST): only change the presentation layer. Each layer is replaceable independently. Problem: large enterprise apps develop thick service layers; thin presentation and data layers that just delegate. The "sinkhole" pattern emerges where 80% of requests flow straight through all layers without any business logic.

---

### 🔩 First Principles Explanation

**Layer responsibilities, strict vs. relaxed, and the sinkhole problem:**

```
CLASSIC 4-LAYER SPRING MVC ARCHITECTURE:

  HTTP Request
       │
       ▼
  ┌──────────────────────────────┐
  │  PRESENTATION LAYER          │  (Controller, REST API)
  │  - HTTP request/response     │
  │  - Input validation (format) │
  │  - Serialization/JSON        │
  │  - Auth token extraction     │
  └──────────────┬───────────────┘
                 │ calls
                 ▼
  ┌──────────────────────────────┐
  │  SERVICE LAYER               │  (Business Logic)
  │  - Domain rules              │
  │  - Transaction boundaries    │
  │  - Use case orchestration    │
  │  - Business validation       │
  └──────────────┬───────────────┘
                 │ calls
                 ▼
  ┌──────────────────────────────┐
  │  REPOSITORY LAYER            │  (Data Access)
  │  - Database queries          │
  │  - ORM mapping               │
  │  - Cache integration         │
  │  - Query optimization        │
  └──────────────┬───────────────┘
                 │ calls
                 ▼
  ┌──────────────────────────────┐
  │  DATABASE LAYER              │
  │  - MySQL, PostgreSQL, etc.   │
  └──────────────────────────────┘

STRICT vs RELAXED LAYERING:

  STRICT (layers can only call directly adjacent below):
    Controller → Service ✅
    Controller → Repository ✗ (skips Service)
    Controller → Database ✗ (skips two layers)

    Enforced by: package visibility, architecture tests (ArchUnit).

  RELAXED (layers can call any layer below):
    Controller → Service ✅
    Controller → Repository ✅ (allowed, skips Service)
    Controller → Database ✅ (allowed, skips two layers)

    Common in practice. Risk: business logic leaks into controllers.

THE SINKHOLE ANTI-PATTERN:

  Problem: a request that flows through all 4 layers but each layer only delegates.

  BAD EXAMPLE:

  // Controller:
  @GetMapping("/users/{id}")
  public UserDTO getUser(@PathVariable Long id) {
      return userService.getUser(id);  // Just delegates. No added logic.
  }

  // Service (sinkhole):
  public UserDTO getUser(Long id) {
      return userRepository.findById(id);  // Just delegates. No added logic.
  }

  // Repository:
  public UserDTO findById(Long id) {
      return db.query("SELECT * FROM users WHERE id = ?", id);  // ACTUAL WORK.
  }

  // Result: Controller and Service layers add zero value for this use case.
  // Violating DRY and adding ceremonial boilerplate.
  // If 60-80% of use cases are sinkholes: wrong architecture choice.

WHEN LAYERED IS RIGHT:

  Simple CRUD applications: getUser, createUser, updateUser.
  Team structure: separate front-end, back-end, DBA teams.
  Stable, well-understood domain.
  Need clear testability boundaries.
  Regulatory/compliance requirements for separation.

WHEN LAYERED IS WRONG:

  Complex domain with many rules: layers become "pass-through" vessels.
  High performance requirements: each layer adds overhead (even if minimal).
  Microservices: each service is already small — internal layers add unnecessary ceremony.
  Rapid feature development: horizontal slicing slows feature work (changes all layers).

  Better alternative: Vertical Slice Architecture (VSlice) — each feature is its own slice
  through all layers (no artificial horizontal boundaries).
```

---

### ❓ Why Does This Exist (Why Before What)

WITHOUT layered architecture:

- Spaghetti code: SQL in controllers, business logic in database stored procedures, UI logic in services
- Change the database: affects every class in the codebase
- No testability: can't test business logic without a real database

WITH layered architecture:
→ Each layer replaceable independently (swap database: only change Repository layer)
→ Clear boundaries: business logic in Service, never in Controller or Repository
→ Testable: mock the layer below to unit-test each layer in isolation

---

### 🧠 Mental Model / Analogy

> A building with distinct floors: Ground floor (Reception/Presentation) greets visitors and routes requests. Second floor (Management/Business Logic) makes decisions and orchestrates work. Third floor (Archive/Data Access) stores and retrieves files. Basement (Physical Files/Database) holds the actual data. The receptionist doesn't go to the archive directly — they call management. Management decides what to retrieve and calls the archive. The archive fetches from the basement. Each floor has a clear job. Restructure the basement filing system without changing any other floor.

"Reception" = Presentation Layer / Controller
"Management floor" = Business Logic / Service Layer
"Archive floor" = Data Access / Repository Layer
"Basement" = Database

---

### ⚙️ How It Works (Mechanism)

```
REQUEST FLOW (Spring MVC):

  1. HTTP GET /users/42
  2. UserController.getUser(42) → calls UserService.getUser(42)
  3. UserService: validates business rules → calls UserRepository.findById(42)
  4. UserRepository: executes SQL → returns User entity
  5. UserService: maps entity to DTO, applies business rules → returns UserDTO
  6. UserController: serializes DTO to JSON → returns HTTP 200
```

---

### 🔄 How It Connects (Mini-Map)

```
Separation of Concerns (core principle enabling layered design)
        │
        ▼ (horizontal separation by layer)
Layered Architecture ◄──── (you are here)
(Presentation → Service → Repository → Database)
        │
        ├── Hexagonal Architecture: alternative with ports/adapters (inward dependencies)
        ├── Clean Architecture: strict dependency rule (domain at center)
        └── Vertical Slice Architecture: alternative with feature-based vertical slices
```

---

### 💻 Code Example

```java
// Classic 4-layer Spring Boot application:

// LAYER 1: Presentation (Controller)
@RestController
@RequestMapping("/api/orders")
public class OrderController {
    private final OrderService orderService;

    @PostMapping
    public ResponseEntity<OrderDTO> createOrder(@Valid @RequestBody CreateOrderRequest request) {
        OrderDTO order = orderService.createOrder(request.customerId(), request.items());
        return ResponseEntity.status(201).body(order);
    }
}

// LAYER 2: Business Logic (Service)
@Service
@Transactional
public class OrderService {
    private final OrderRepository orderRepository;
    private final InventoryService inventoryService;

    public OrderDTO createOrder(Long customerId, List<OrderItem> items) {
        // Business rules: validate inventory, apply discounts, check credit.
        inventoryService.reserveItems(items);  // Business orchestration.
        Order order = Order.create(customerId, items);  // Domain logic.
        Order saved = orderRepository.save(order);
        return OrderDTO.from(saved);
    }
}

// LAYER 3: Data Access (Repository)
@Repository
public class OrderRepository {
    private final JpaRepository<Order, Long> jpaRepo;

    public Order save(Order order) {
        return jpaRepo.save(order);  // ORM handles SQL. Layer 3's only concern.
    }
}
// LAYER 4: Database — MySQL/PostgreSQL (managed by ORM configuration)
```

---

### ⚠️ Common Misconceptions

| Misconception                                                                | Reality                                                                                                                                                                                                                                                                                                                                                                     |
| ---------------------------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Layered architecture means the presentation layer handles HTTP concerns only | In practice, many teams put input validation, authorization, and request mapping in controllers. These are presentation concerns. Business rules (discount logic, fraud detection) belong in the service layer. If business rules leak into controllers: the architecture degrades. Strictly enforce: controllers handle HTTP mechanics; services handle business decisions |
| More layers = better architecture                                            | Layers add indirection and ceremony. A simple CRUD microservice with 3 endpoints doesn't need 4 strict layers — a 2-layer design (HTTP handler + repository) may be more appropriate. Over-layering: the sinkhole anti-pattern. Add layers only when there is genuine complexity to separate. Amazon's two-pizza teams, microservices: minimal internal layers              |
| Layered architecture and microservices are complementary                     | They can conflict. Microservices decompose by business capability (vertical slicing). Layered architecture decomposes by technical concern (horizontal slicing). Inside a microservice: a thin layered structure makes sense. But applying enterprise 4-layer patterns to every microservice: over-engineering. Match architecture to scale and complexity                  |

---

### 🔥 Pitfalls in Production

**Business logic leaking into the wrong layer:**

```
BAD: Business logic in the Controller (presentation):
@PostMapping("/transfer")
public ResponseEntity<String> transfer(@RequestBody TransferRequest req) {
    // Business rule: maximum transfer amount check — IN THE CONTROLLER.
    if (req.amount() > 10000) {
        return ResponseEntity.badRequest().body("Transfer limit exceeded");
    }
    // Business rule: fraud detection — IN THE CONTROLLER.
    if (req.toAccount().equals(req.fromAccount())) {
        return ResponseEntity.badRequest().body("Cannot transfer to same account");
    }
    // Business rule: fee calculation — IN THE CONTROLLER.
    double fee = req.amount() > 1000 ? req.amount() * 0.01 : 1.0;
    bankService.transfer(req.fromAccount(), req.toAccount(), req.amount(), fee);
    return ResponseEntity.ok("Success");
}

PROBLEMS:
  - These rules must be duplicated in: CLI handler, Kafka consumer handler, batch job.
  - Controller can't be tested without HTTP machinery.
  - Changing fee structure: requires finding all controllers that calculate fees.
  - Rule changes in one place: doesn't update all delivery mechanisms.

FIX: Move all business rules to the Service layer:
@PostMapping("/transfer")
public ResponseEntity<String> transfer(@RequestBody TransferRequest req) {
    // Controller: ONLY HTTP concerns. No business logic.
    try {
        transferService.transfer(req.fromAccount(), req.toAccount(), req.amount());
        return ResponseEntity.ok("Success");
    } catch (TransferLimitExceededException e) {
        return ResponseEntity.badRequest().body(e.getMessage());
    }
}

@Service
public class TransferService {
    public void transfer(String from, String to, double amount) {
        // ALL business rules here — single place:
        if (amount > 10000) throw new TransferLimitExceededException("Limit: $10,000");
        if (from.equals(to)) throw new IllegalArgumentException("Cannot self-transfer");
        double fee = amount > 1000 ? amount * 0.01 : 1.0;
        accountRepository.debit(from, amount + fee);
        accountRepository.credit(to, amount);
    }
}
// Now: CLI, Kafka consumer, batch job all call transferService.transfer(). Single source of truth.
```

---

### 🔗 Related Keywords

- `Hexagonal Architecture` — alternative pattern with ports/adapters; dependencies point inward to domain
- `Clean Architecture` — strict dependency rule: domain at center, infrastructure at edge
- `Vertical Slice Architecture` — alternative: organize by feature (vertical) not layer (horizontal)
- `Repository Pattern` — the data access layer abstraction
- `Service Layer` — the business logic layer pattern

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ KEY IDEA     │ Horizontal layers: Presentation → Service │
│              │ → Repository → DB. Each layer calls only │
│              │ the layer below. Separation by concern.  │
├──────────────┼───────────────────────────────────────────┤
│ USE WHEN     │ Team split by role (FE/BE/DBA); stable   │
│              │ domain; testability focus; CRUD-heavy app│
├──────────────┼───────────────────────────────────────────┤
│ AVOID WHEN   │ Complex domain; high sinkhole ratio;     │
│              │ need rapid feature development across    │
│              │ concern boundaries                       │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "Restaurant: waiter, chef, sous-chef,   │
│              │  pantry — each has one job, clear chain."│
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ Hexagonal Architecture → Clean           │
│              │ Architecture → Vertical Slice →          │
│              │ Repository Pattern → Service Layer       │
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** Your team has a large e-commerce application using strict 4-layer architecture. You add a new feature: real-time product recommendations. The recommendation engine requires: user's browsing history (database), machine learning model inference (external API), and A/B test variant assignment (business logic). Describe: which layer each concern belongs in. What problem arises when the Service layer must call both the Repository AND an external ML API? How does this violate or not violate the layered model?

**Q2.** You're building a REST API with 50 endpoints. After 6 months of development, you measure: 75% of your endpoints are "sinkholes" (Controller → Service → Repository, zero logic in Service). What does this measurement tell you about your architecture choice? What alternative architecture pattern would be more appropriate? How would you migrate the codebase without a full rewrite?
