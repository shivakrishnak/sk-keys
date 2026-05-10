---
id: SAP-013
title: Layered Architecture
category: Software Architecture Patterns
tier: tier-5-distributed-architecture
folder: SAP-software-architecture
difficulty: ★☆☆
depends_on: SAP-043, SAP-050, SAP-051
used_by: SAP-014, SAP-015, SAP-021
related: SAP-014, SAP-015, SAP-016, SAP-017
tags:
  - architecture
  - pattern
  - foundational
  - mental-model
  - bestpractice
status: complete
version: 3
layout: default
parent: "Software Architecture Patterns"
grand_parent: "Technical Dictionary"
nav_order: 13
permalink: /software-architecture/layered-architecture/
---

# SAP-013 - Layered Architecture

⚡ TL;DR - Layered Architecture organises code into horizontal tiers where each tier can only communicate with the tier directly below it.

| Field          | Value                              |
| -------------- | ---------------------------------- |
| **Depends on** | SAP-043, SAP-050, SAP-051          |
| **Used by**    | SAP-014, SAP-015, SAP-021          |
| **Related**    | SAP-014, SAP-015, SAP-016, SAP-017 |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
Imagine a web application where HTTP request parsing, business logic, and SQL queries are all mixed together in a single class. The developer who added the feature three months ago has left. You need to change the database from MySQL to PostgreSQL. You open the code and find that SQL strings are embedded directly in the same methods that validate user input and format HTTP responses. To change the database, you must read and modify hundreds of interlocked lines of code. Every change risks breaking unrelated behaviour.

**THE BREAKING POINT:**
A routine database migration takes three weeks. A bug fix in payment logic accidentally breaks email formatting. Testing becomes impossible because you can't isolate the database from business rules. Onboarding a new developer takes months because nothing is predictable.

**THE INVENTION MOMENT:**
This is exactly why Layered Architecture was created - to draw clear boundaries between concerns so that changes in one area don't cascade unpredictably through the whole system.

**EVOLUTION:**
Layered Architecture was formalised by the OSI network model (ISO 7498, 1984) - the most widely deployed layered design in computing history. In application software, the three-tier model became standard through the 1990s enterprise Java era (EJB, then Spring, then Spring Boot all defaulted to layered architecture). Its dominance peaked in the 2000s; alternatives emerged as CRUD-heavy layering proved insufficient for complex domain logic. Today, layered architecture remains the default starting point for enterprise applications but is frequently extended by hexagonal or clean variants for complex domains.

---

### 📘 Textbook Definition

Layered Architecture (also called N-Tier Architecture) is a structural architectural pattern that organises software into horizontal layers, each with a distinct responsibility. Each layer communicates only with the layer directly beneath it, creating a strict dependency hierarchy. The most common variant separates Presentation, Business Logic, and Data Access into three discrete layers, though four-layer variants are common in enterprise systems.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
Stack your code in floors - UI on top, logic in the middle, data at the bottom.

**One analogy:**

> A restaurant has a clear separation: the dining room (presentation) takes orders from customers, the kitchen (business logic) cooks the meal, and the pantry and suppliers (data layer) provide ingredients. Diners never walk into the pantry. The kitchen never seats customers. Each floor has one job.

**One insight:**
The power of layering is not just organisation - it's that you can swap out an entire floor without touching the others. Replace MySQL with PostgreSQL, or a REST controller with a CLI, and only that layer changes. The dependency always flows downward, never upward.

---

### 🔩 First Principles Explanation

**CORE INVARIANTS:**

1. Each layer has a single, well-defined responsibility.
2. Dependencies flow strictly downward - upper layers depend on lower layers, never the reverse.
3. Layers communicate only through defined interfaces (not through shared global state).

**DERIVED DESIGN:**
Given these invariants, any correct layered system must look like this: the Presentation Layer receives external input and delegates to the Business Logic Layer. The Business Logic Layer contains domain rules and orchestrates operations. The Data Access Layer handles persistence. No layer skips a tier - the presentation layer never calls the database directly.

This constraint produces a system where:

- You can test business logic without starting a web server.
- You can change the database engine without touching business rules.
- You can replace a REST API with a message-driven interface without rewriting logic.

**THE TRADE-OFFS:**
**Gain:** Predictability, testability, and independent replaceability of layers.
**Cost:** You pay a coordination tax on every request. A simple "get user" call travels through all four layers even when no business logic is needed. This produces a pattern called "shotgun surgery through layers" - where a trivial change requires touching the same concept in every layer.

Could we do this differently? Yes - Vertical Slice Architecture (entry 730) groups code by feature rather than by layer, addressing precisely this overhead. But for large teams with separate frontend, backend, and DBA specialists, the horizontal division remains natural.

---

### 🧪 Thought Experiment

**SETUP:**
You have a `UserController` that needs to return a user's account balance. The balance comes from a database. You have three developers: one owns the UI, one owns business rules, one owns the database.

**WHAT HAPPENS WITHOUT LAYERED ARCHITECTURE:**
The UI developer writes SQL directly in the controller: `SELECT balance FROM accounts WHERE id = ?`. When the DBA changes the table name to `user_accounts`, the controller breaks. The business logic developer, wanting to add a "blocked account" check, modifies the same method. Two developers collide. The change breaks the mobile API because it shares the same controller. A two-line fix becomes a three-day debugging session.

**WHAT HAPPENS WITH LAYERED ARCHITECTURE:**
The controller calls `accountService.getBalance(userId)`. The service checks the business rule (blocked accounts). The service calls `accountRepository.findBalance(userId)`. The DBA changes only the repository. The business rule developer changes only the service. The controller never changes. All three developers work independently without collision.

**THE INSIGHT:**
Layering converts coordination problems into interface problems - and interface problems are far easier to manage.

---

### 🧠 Mental Model / Analogy

> Think of a skyscraper's floors: the lobby (presentation) is open to the public and directs traffic upward; the office floors (business logic) do the actual work; the basement (data access) holds the infrastructure. Visitors enter through the lobby. Workers on floor 30 don't go to the basement themselves - they call building services.

- "Lobby" → Presentation Layer (controllers, views, API handlers)
- "Office floors" → Business / Domain Layer (services, use cases, rules)
- "Basement" → Data Access Layer (repositories, ORMs, raw SQL)
- "Building services" → interfaces between layers
- "Fire escape bypassing floors" → anti-pattern: controller calling DB directly

Where this analogy breaks down: In a real building, people can go to any floor directly. In layered architecture, this is explicitly forbidden - skipping layers is the most common violation.

---

### 📶 Gradual Depth - Four Levels

**Level 1 - What it is (anyone can understand):**
Layered Architecture means splitting your application into separate sections, where each section has one job. The top section handles user interaction, the middle section handles business rules, and the bottom section handles saving and loading data.

**Level 2 - How to use it (junior developer):**
In a Spring Boot application, you'll have `@Controller` classes for HTTP, `@Service` classes for logic, and `@Repository` classes for database access. The controller calls the service, the service calls the repository. Never call the repository from the controller directly - that breaks the layer contract.

**Level 3 - How it works (mid-level engineer):**
Each layer boundary is enforced through interfaces and dependency injection. The service layer depends on a `UserRepository` interface, not a concrete `JpaUserRepository`. This allows the data layer to be swapped (e.g., from JPA to MongoDB) without the service knowing. The presentation layer maps between external DTOs and internal domain objects, preventing data model leakage. This boundary translation is often where most of the "boring" but important code lives.

**Level 4 - Why it was designed this way (senior/staff):**
The layered model emerged from mainframe-era separation of I/O, computation, and storage. Its durability comes from mapping cleanly to organisational structure: separate teams for frontend, backend, and DBA. Its weakness is that it optimises for technical similarity (all repositories together) rather than business cohesion (all user-related code together). This is precisely the tension that Domain-Driven Design (DDD) and Vertical Slice Architecture resolve by reorganising around feature boundaries rather than technical tier.

---

### ⚙️ How It Works (Mechanism)

A four-layer architecture (Presentation → Application → Domain → Infrastructure) processes a typical request as follows:

```
┌─────────────────────────────────────────────────┐
│              LAYERED ARCHITECTURE               │
│                REQUEST FLOW                     │
├─────────────────────────────────────────────────┤
│  HTTP Request                                   │
│       ↓                                         │
│  ┌──────────────────────────────────────────┐   │
│  │  Presentation Layer                      │   │
│  │  (Controllers, DTOs, Request mapping)    │   │
│  └──────────────────┬───────────────────────┘   │
│                     ↓ calls                     │
│  ┌──────────────────────────────────────────┐   │
│  │  Application / Service Layer             │   │
│  │  (Orchestration, transactions, ACLs)     │   │
│  └──────────────────┬───────────────────────┘   │
│                     ↓ calls                     │
│  ┌──────────────────────────────────────────┐   │
│  │  Domain Layer                            │   │
│  │  (Business rules, entities, value objs)  │   │
│  └──────────────────┬───────────────────────┘   │
│                     ↓ calls                     │
│  ┌──────────────────────────────────────────┐   │
│  │  Infrastructure / Data Layer             │   │
│  │  (Repositories, ORM, external services)  │   │
│  └──────────────────────────────────────────┘   │
│       ↓                                         │
│  Database / External Service                    │
└─────────────────────────────────────────────────┘
```

**Step-by-step walkthrough:**

1. **HTTP arrives at Presentation Layer.** The controller deserialises the request body into a DTO. It validates field formats (not business rules - that's the service's job). It calls the service with clean input.

2. **Application Layer orchestrates.** The service method opens a transaction boundary (if needed), calls domain objects to apply business rules, and calls repositories to load or persist state. It does NOT contain if-statements for business rules - those belong in domain objects.

3. **Domain Layer applies rules.** Pure Java/C#/Python objects - no framework annotations, no database calls. An `Order` object checks whether it can be shipped. A `Payment` object validates the amount. This layer is the easiest to unit test because it has no external dependencies.

4. **Infrastructure Layer persists.** A repository implementation (e.g., `JpaOrderRepository`) converts domain objects to persistence entities and executes SQL. ORM frameworks live here. REST clients to external APIs live here.

5. **Response travels back up.** The result passes upward through each layer. Each layer may transform it (domain entity → service DTO → HTTP response JSON).

**When something goes wrong:**
If the database is unavailable, the Infrastructure layer throws a `DataAccessException`. The Service layer may retry or translate it to a domain exception. The Presentation layer catches the exception and returns an appropriate HTTP 503 response. Each layer handles only what it owns.

---

### 🔄 The Complete Picture - End-to-End Flow

**NORMAL FLOW:**

```
HTTP Request → Controller (parse DTO)
  → Service (business logic + transaction)
  → Repository ← YOU ARE HERE (data access)
  → Database → Result → Repository → Service
  → Controller (map to response DTO) → HTTP Response
```

**FAILURE PATH:**

```
Database timeout → DataAccessException
  → Service catches → translates to ServiceException
  → Controller catches → returns HTTP 503
  → Client receives error response
```

**WHAT CHANGES AT SCALE:**
At scale, the data access layer becomes the bottleneck first - connection pool exhaustion, slow queries, lock contention. The layered model helps isolate this: you can add a caching layer between the service and repository without changing anything else. At very high scale, a single vertical stack per request becomes a horizontal scaling problem - you deploy multiple instances behind a load balancer, each running the same layered stack.

---

### 💻 Code Example

**Example 1 - Wrong: controller calling repository directly:**

```java
// BAD - skips service layer, no transaction, no validation
@RestController
public class UserController {
    @Autowired
    private UserRepository userRepository; // direct DB access!

    @GetMapping("/users/{id}")
    public User getUser(@PathVariable Long id) {
        return userRepository.findById(id).orElseThrow();
    }
}
```

**Example 2 - Right: clean layer separation:**

```java
// Presentation Layer - only HTTP concerns
@RestController
@RequiredArgsConstructor
public class UserController {
    private final UserService userService;

    @GetMapping("/users/{id}")
    public UserResponseDto getUser(@PathVariable Long id) {
        return userService.getUser(id);  // delegates to service
    }
}

// Application Layer - orchestration, no SQL
@Service
@RequiredArgsConstructor
@Transactional(readOnly = true)
public class UserService {
    private final UserRepository userRepository;

    public UserResponseDto getUser(Long id) {
        User user = userRepository.findById(id)
            .orElseThrow(() -> new UserNotFoundException(id));
        user.verifyActive();  // domain rule on domain object
        return UserResponseDto.from(user);
    }
}

// Infrastructure Layer - persistence only
@Repository
public interface UserRepository
        extends JpaRepository<User, Long> {
    // Spring Data generates SQL - service never sees SQL
}
```

---

### ⚖️ Comparison Table

| Pattern                     | Coupling         | Feature cohesion           | Best For                                  |
| --------------------------- | ---------------- | -------------------------- | ----------------------------------------- |
| **Layered Architecture**    | Low within layer | Low (spread across layers) | Teams split by technical role             |
| Hexagonal Architecture      | Very low         | Medium                     | Domain-heavy applications                 |
| Vertical Slice Architecture | Medium per slice | High                       | Feature-team organisations                |
| Modular Monolith            | Low              | High                       | Transition from monolith to microservices |

**How to choose:** Use Layered Architecture when your team is organised by technical specialty (frontend, backend, DBA) or when you need a simple, well-understood structure for a CRUD-heavy application. Choose Vertical Slice when features change frequently and you want to minimise cross-layer coordination.

---

### ⚠️ Common Misconceptions

| Misconception                                         | Reality                                                                                   |
| ----------------------------------------------------- | ----------------------------------------------------------------------------------------- |
| Layers must map 1:1 to deployment tiers               | Logical layers and physical tiers are independent - a 4-layer app can run on one server   |
| More layers = better architecture                     | Every layer adds indirection and latency; use only layers that earn their place           |
| The service layer should contain all logic            | Domain objects should contain business rules; the service layer orchestrates, not decides |
| Layered architecture prevents microservices migration | Layered monoliths actually migrate more cleanly because boundaries are already explicit   |
| You can skip layers for performance                   | Skipping layers couples unrelated concerns and is the #1 source of maintenance debt       |

---

### 🚨 Failure Modes & Diagnosis

**God Service (Fat Service Layer)**

**Symptom:** Service classes grow to thousands of lines. Every service method begins with 15 lines of loading entities, then 30 lines of conditionals.

**Root Cause:** Business logic that belongs in domain objects accumulates in the service layer because domain objects are treated as dumb data containers (anemic domain model).

**Diagnostic Command / Tool:**

```bash
# Find suspiciously large service files
find . -name "*Service.java" -exec wc -l {} + \
  | sort -rn | head -20
```

**Fix:** Move business rules into domain objects. Services should read: "load → call domain method → persist → return."

**Prevention:** At design time, ask "does this rule live on the object or on the orchestrator?" If it describes what an object IS, it belongs on the object.

---

**Layer Bypass (Presentation → Repository)**

**Symptom:** Controllers import repository classes. Integration tests require a full database to test a single validation rule.

**Root Cause:** Developer bypasses the service layer for "simple" reads, creating a precedent that spreads.

**Diagnostic Command / Tool:**

```bash
# Detect controllers importing repositories
grep -rn "import.*Repository" src/main/java/**/controller/
```

**Fix:** All database access must go through the service layer, even for simple reads.

**Prevention:** Use architecture fitness function tools (ArchUnit) to enforce layer boundaries in CI.

---

**Leaking Domain Objects to Presentation Layer**

**Symptom:** Changing a database column name breaks the API response JSON. Hibernate lazy-loading exceptions appear in JSON serialisation.

**Root Cause:** Domain entities are returned directly from controllers instead of being mapped to DTOs at the layer boundary.

**Diagnostic Command / Tool:**

```bash
# Find controllers returning @Entity classes directly
grep -rn "@Entity" src/main/java/**/controller/
grep -rn "return.*Entity" src/main/java/**/controller/
```

**Fix:** Map entities to DTOs in the service or controller layer before returning.

**Prevention:** Define explicit DTO classes for each API response; never expose `@Entity` annotated objects outside the service layer.

---

### 💎 Transferable Wisdom

**Reusable Engineering Principle:** Constraints on dependency direction are a general mechanism for managing complexity. The direction of allowed dependencies determines where change propagates through a system. By constraining propagation to flow downward only, layered architecture limits the blast radius of any given change to the layers above it.

**Where else this pattern appears:**

- **OSI network model:** the internet is built on 7 layers where each layer provides services to the layer above through a stable interface - changes in the transport layer (TCP) do not require changes in the application layer (HTTP).
- **Legal hierarchy:** constitutional law constrains statutory law constrains regulations constrains enforcement - a lower layer cannot override a higher layer's principles; changes propagate upward, not downward.
- **Supply chains:** finished goods depend on components; components do not depend on how goods are used - the same dependency direction constraint manages change propagation in physical manufacturing.

---

### 💡 The Surprising Truth

Layered Architecture does not actually eliminate coupling - it redirects it. In a strict layered system, the domain layer is still tightly coupled to the data layer through DAO interfaces. When a Layered Architecture suffers from "transaction script seeping into the domain," the root cause is not indiscipline - it is that the layered model provides no structural mechanism to prevent it. The dependency rule in Layered Architecture is convention, not constraint. ArchUnit or similar fitness functions are required to enforce it mechanically, because the architecture alone cannot stop a developer from directly calling a repository from a controller.

---

### �🔗 Related Keywords

**Prerequisites (understand these first):**

- SAP-043 - SOLID Principles (the design principles that justify why layers should depend on interfaces, not concretions)
- SAP-050 - Cohesion and SAP-051 - Coupling (the core concepts; layered architecture is a mechanism for managing coupling between concerns)

**Builds On This (learn these next):**

- SAP-014 - Hexagonal Architecture (extends layering by inverting all dependencies toward the domain)
- SAP-015 - Clean Architecture (applies strict dependency rules with explicit concentric rings)
- SAP-017 - Vertical Slice Architecture (an alternative that organises by feature instead of technical tier)

**Alternatives / Comparisons:**

- SAP-017 - Vertical Slice Architecture (groups code by feature rather than by technical tier; preferred when teams own end-to-end features)
- SAP-039 - Modular Monolith Patterns (adds horizontal module boundaries that layered architecture lacks)

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ WHAT IT IS   │ Code split into horizontal tiers;         │
│              │ UI → Logic → Data                         │
├──────────────┼───────────────────────────────────────────┤
│ PROBLEM IT   │ Mixed concerns cause fragile, untestable  │
│ SOLVES       │ code impossible to change safely          │
├──────────────┼───────────────────────────────────────────┤
│ KEY INSIGHT  │ Dependencies flow DOWN only - upper       │
│              │ layers never know about lower layers'     │
│              │ implementations                           │
├──────────────┼───────────────────────────────────────────┤
│ USE WHEN     │ Team is split by technical specialty;     │
│              │ CRUD-heavy enterprise applications        │
├──────────────┼───────────────────────────────────────────┤
│ AVOID WHEN   │ Feature teams own end-to-end slices;      │
│              │ simple scripts or single-purpose tools    │
├──────────────┼───────────────────────────────────────────┤
│ TRADE-OFF    │ Testability vs coordination overhead      │
│              │ for simple cross-cutting changes          │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "Every floor has one job; use the stairs" │
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ Hexagonal → Clean Architecture → DDD     │
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** In a standard four-layer architecture, a new requirement arrives: "Send an email whenever an order is placed." The emailing logic is an infrastructure concern, but it must be triggered by a business event in the domain layer. The domain layer is not allowed to depend on infrastructure. How do you satisfy both the dependency rule and the business requirement without putting email code in the domain?

*Hint:* Research the Observer pattern and specifically the Domain Event pattern from DDD - the domain publishes an event (OrderPlaced) without knowing who listens; an infrastructure event listener subscribes and sends the email. This inverts the dependency without violating the layering rule.

**Q2.** A team adopts strict layered architecture, enforcing it with ArchUnit tests. Six months later, a performance profiling session shows that 40% of response time is spent mapping objects between layers (entity -> domain object -> DTO). The team wants to eliminate the domain object for simple read operations and return database results directly to the controller. What does this decision cost architecturally, and under what precise conditions is it a valid trade-off rather than technical debt?

*Hint:* Research the CQRS pattern - specifically how it separates the read model (which can bypass layers for performance) from the write model (which must honour domain invariants). This gives a principled framework for the "bypass the domain for reads" decision rather than making it an unprincipled exception.

**Q3.** An engineering team is adopting Domain-Driven Design within their existing layered architecture. They want to move business logic from service classes into rich domain entities. However, their ORM (JPA/Hibernate) requires entity classes to be mutable (public setters, no-arg constructor) for session management, which conflicts with DDD's always-valid entity and immutable value object principles. How do you design the boundary between ORM entity classes and DDD domain objects to get the benefits of both?

*Hint:* Research Vaughn Vernon's "Implementing Domain-Driven Design" chapter on persistence and the concept of separating the ORM persistence model from the domain model using a mapping layer - then compare with the Spring Data "Active Record for JPA" approach to understand the trade-off between mapping overhead and persistence purity.
