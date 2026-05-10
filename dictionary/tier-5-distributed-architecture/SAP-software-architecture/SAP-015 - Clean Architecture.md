---
id: SAP-015
title: Clean Architecture
category: Software Architecture Patterns
tier: tier-5-distributed-architecture
folder: SAP-software-architecture
difficulty: ★★★
depends_on: SAP-014, SAP-023, SAP-043
used_by: SAP-016, SAP-017
related: SAP-014, SAP-016, SAP-013, SAP-017
tags:
  - architecture
  - pattern
  - advanced
  - first-principles
status: complete
version: 2
layout: default
parent: "Software Architecture Patterns"
grand_parent: "Technical Dictionary"
nav_order: 15
permalink: /software-architecture/clean-architecture/
---

# SAP-015 - Clean Architecture

⚡ TL;DR - Clean Architecture enforces that all source code dependencies point inward toward business rules - frameworks, databases, and UIs are details at the outer ring.

| Field          | Value                              |
| -------------- | ---------------------------------- |
| **Depends on** | SAP-014, SAP-023, SAP-043          |
| **Used by**    | SAP-016, SAP-017                   |
| **Related**    | SAP-014, SAP-016, SAP-013, SAP-017 |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
Your Spring Boot application has grown to 200,000 lines of code. The business logic - the reason the company exists - is scattered across service classes annotated with `@Transactional`, `@Cacheable`, and `@RabbitListener`. To understand what the application does, you must understand Spring. To test a business rule, you must start an application context. To migrate from RabbitMQ to Kafka, you must read every service class. The architecture tells you nothing about the business. It tells you everything about Spring.

**THE BREAKING POINT:**
A senior developer joins and asks: "What does this application actually do?" No one can answer without walking through the framework configuration first. The architecture screams "Spring Boot application!" but whispers nothing about the business domain.

**THE INVENTION MOMENT:**
This is exactly why Clean Architecture was created - to produce systems where the architecture itself screams the business intent and treats frameworks, databases, and delivery mechanisms as interchangeable details.

**EVOLUTION:**
Robert Martin (Uncle Bob) published Clean Architecture in 2017 as a synthesis of Hexagonal Architecture (Cockburn, 2005), Onion Architecture (Jeffrey Palermo, 2008), and BCE (Entity-Control-Boundary by Jacobson, 1992). The key synthesis contribution was the explicit naming of the Use Case layer as a first-class citizen - Hexagonal Architecture had ports and adapters but no named use-case ring. The Dependency Rule formalised the implicit constraint of all predecessors into an explicit architectural invariant. Clean Architecture became one of the most discussed patterns in the late 2010s, particularly in Java and .NET communities, generating both strong adoption and equally strong criticism for over-engineering simple CRUD applications.

---

### 📘 Textbook Definition

Clean Architecture, introduced by Robert C. Martin (Uncle Bob) in 2012, is an architectural pattern that organises code into concentric rings, where the innermost ring contains enterprise-wide business rules (Entities), the next ring contains application-specific business rules (Use Cases), and the outer rings contain interface adapters and frameworks. The Dependency Rule mandates that source code dependencies may only point inward - outer rings can depend on inner rings, but inner rings may never reference outer rings. This makes the business logic deployable and testable independently of any framework, database, or UI.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
Business rules live at the centre; frameworks and databases are disposable outer skins.

**One analogy:**

> Think of an onion. The centre - the most valuable part - is the core business rules. Each outer layer wraps it: use cases, then interface adapters, then frameworks. You can remove and replace any outer layer without touching the centre. The centre doesn't know the outer layers exist.

**One insight:**
The provocative claim of Clean Architecture is that the database is an implementation detail - not a foundation. Your application should be able to run against an in-memory store, a PostgreSQL instance, or a file system with no change to the business logic. When this is possible, you have clean architecture.

---

### 🔩 First Principles Explanation

**CORE INVARIANTS:**

1. **The Dependency Rule:** Source code dependencies always point inward. An inner ring may never name something from an outer ring.
2. **Entities are pure business rules:** They contain enterprise-wide data and logic, independent of any application.
3. **Use Cases are application-specific rules:** They orchestrate entities to fulfill specific user goals. They do not know about HTTP, SQL, or UI.

**DERIVED DESIGN:**
The four standard rings are:

```
┌──────────────────────────────────────────────────────────┐
│              CLEAN ARCHITECTURE RINGS                    │
├──────────────────────────────────────────────────────────┤
│                                                          │
│    ┌─── Frameworks & Drivers (outermost) ────────┐       │
│    │  ┌─── Interface Adapters ───────────────┐   │       │
│    │  │  ┌─── Use Cases ───────────────┐     │   │       │
│    │  │  │  ┌─── Entities ────────┐    │     │   │       │
│    │  │  │  │  Business Rules     │    │     │   │       │
│    │  │  │  └─────────────────────┘    │     │   │       │
│    │  │  │  Application Logic          │     │   │       │
│    │  │  └─────────────────────────────┘     │   │       │
│    │  │  Controllers, Gateways, Presenters   │   │       │
│    │  └──────────────────────────────────────┘   │       │
│    │  Web, DB, Devices, External Interfaces       │       │
│    └──────────────────────────────────────────────┘       │
│                                                          │
│  Dependencies: outer → inner ONLY                        │
└──────────────────────────────────────────────────────────┘
```

**Ring responsibilities:**

- **Entities:** Business objects with methods that apply cross-application rules. An `Order` entity knows that an order total must be positive. It knows nothing about databases or HTTP.
- **Use Cases (Interactors):** Orchestrate entities to fulfill a specific use case: "Place Order," "Refund Payment." They call entity methods and call output ports.
- **Interface Adapters:** Convert data from use case format to format suitable for storage or UI. Controllers, Presenters, Gateways.
- **Frameworks & Drivers:** Spring, JPA, React, PostgreSQL driver. As far as the inner rings are concerned, these are all interchangeable plug-ins.

**THE TRADE-OFFS:**
**Gain:** The architecture makes intent visible. You can test the core completely without infrastructure. You can swap frameworks.
**Cost:** Significant upfront investment. For each use case you write: an input boundary interface, an output boundary interface, an interactor class, a presenter, a view model, and possibly a request/response model. A "create user" feature that takes 1 class in a layered app may take 6 classes in Clean Architecture.

---

### 🧪 Thought Experiment

**SETUP:**
You have a use case: "Approve a loan application." The rule: approve if credit score > 700 and income > 3× loan amount.

**WHAT HAPPENS WITHOUT CLEAN ARCHITECTURE:**
The `LoanController` calls `LoanService`, which has `@Autowired EntityManager`. The rule is written as: `if (applicant.getCreditScore() > 700 && applicant.getIncome() > loan.getAmount() * 3)`. When you decide to add a machine learning score alongside the credit score, you modify the service class - which is also the class handling transaction management, HTTP response mapping, and event publishing. The rule is buried in infrastructure noise.

**WHAT HAPPENS WITH CLEAN ARCHITECTURE:**
`ApproveLoanUseCase.execute(ApproveLoanRequest request)` contains only: `Applicant applicant = applicantGateway.findById(request.applicantId()); if (applicant.isEligibleFor(request.loanAmount())) { ... }`. The `isEligibleFor` rule lives on the `Applicant` entity. The use case test passes a `FakeApplicantGateway` containing test data. The rule is tested in microseconds with zero infrastructure. Adding ML scoring means adding a new input to `isEligibleFor` and updating the entity alone.

**THE INSIGHT:**
When the business rule is in the innermost ring, every change to infrastructure, delivery mechanism, or scoring algorithm leaves the rule untouched. The rule becomes the stable centre around which everything else rotates.

---

### 🧠 Mental Model / Analogy

> Think of a city's zoning plan: the financial district (entities) in the centre makes the rules that govern trade. Around it, business districts (use cases) execute trades. The transport network (adapters) carries information in and out. The roads and airports (frameworks) are the physical infrastructure that the financial district couldn't care less about - it operates the same whether people arrive by car or train.

- "Financial district rules" → Entities (enterprise business rules)
- "Business operations" → Use Cases (application business rules)
- "Transport network" → Interface Adapters (controllers, presenters, gateways)
- "Roads and airports" → Frameworks & Drivers (Spring, JPA, React)
- "Dependency rule" → Trucks don't redesign the financial district

Where this analogy breaks down: Cities evolve organically; Clean Architecture requires intentional, upfront discipline about dependencies. Without enforcement (ArchUnit, module boundaries), the rings collapse.

---

### 📶 Gradual Depth - Four Levels

**Level 1 - What it is (anyone can understand):**
Clean Architecture organises code into circles like a bullseye. The most important rules go in the middle. Everything else wraps around them. The stuff in the middle never knows about the stuff on the outside.

**Level 2 - How to use it (junior developer):**
For each feature, write an Interactor class (Use Case) that contains the logic. It talks to the outside world through interfaces (Output Boundaries). Controllers call the Interactor via an Input Boundary interface. Keep all `@Entity`, `@Controller`, `@Repository` annotations in the outer rings. The Interactor should have no framework imports.

**Level 3 - How it works (mid-level engineer):**
The critical mechanism is the Dependency Inversion Principle applied at ring crossings. When a Use Case (inner ring) needs to persist data, it cannot call a repository directly because that would create an inward-pointing dependency. Instead, the Use Case defines a `UserDataAccess` interface (inner ring). The outer ring implements `UserDataAccessImpl extends JpaRepository implements UserDataAccess`. The dependency still points inward (outer ring depends on inner ring interface) even though the inner ring calls the outer ring at runtime. This inversion is the architectural mechanism that makes Clean Architecture work.

**Level 4 - Why it was designed this way (senior/staff):**
Martin was reacting to "Framework-Centric Architecture" - where Spring or Rails becomes the architecture. His insight was that frameworks are tools, not architectures. The provocation "databases are details" challenges the assumption that schema design should drive application design. In practise, Clean Architecture is most valuable in applications that: live for 10+ years, have multiple delivery mechanisms, have complex and evolving business rules, or have teams large enough to specialise. For CRUD applications with simple logic, the indirection cost exceeds the benefit. Martin himself has acknowledged that not every application needs every layer.

---

### ⚙️ How It Works (Mechanism)

**Data crossing ring boundaries:**

Each ring crossing requires a data transformation. Raw HTTP request data becomes an Input Request Model at the adapter/use-case boundary. The Use Case processes it using Entities and produces an Output Response Model. The Presenter converts the response model into a View Model for the UI. This prevents data format from leaking across rings.

```
┌──────────────────────────────────────────────────────────┐
│         CLEAN ARCHITECTURE - DATA FLOW                   │
├──────────────────────────────────────────────────────────┤
│                                                          │
│  HTTP Request                                            │
│      ↓                                                   │
│  Controller (outer ring)                                 │
│      │ maps to InputRequestModel                         │
│      ↓ calls InputBoundary interface (inner ring)        │
│  Use Case Interactor ← YOU ARE HERE                      │
│      │ calls Entities (innermost)                        │
│      │ calls OutputBoundary interface                    │
│      ↓ passes OutputResponseModel                        │
│  Presenter (outer ring)                                  │
│      │ maps to ViewModel                                 │
│      ↓                                                   │
│  View (outermost - framework)                            │
│      ↓                                                   │
│  HTTP Response                                           │
│                                                          │
│  Data Gateway (outer) implements DataAccess (inner)      │
│  ← dependency inversion crosses the ring                 │
└──────────────────────────────────────────────────────────┘
```

**Key inversion pattern:**

```java
// Inner ring: Use Case defines the contract it needs
public interface UserRepository {         // inner ring
    User findById(UserId id);
}

// Outer ring: Infrastructure implements it
// (dependency points INWARD despite runtime call going out)
@Repository
public class JpaUserRepository
        implements UserRepository {       // outer ring
    // JPA implementation here
}
```

---

### 🔄 The Complete Picture - End-to-End Flow

**NORMAL FLOW:**

```
HTTP POST /orders
  → Controller (parse, map to InputRequestModel)
  → OrderInteractor.execute(request)  ← YOU ARE HERE
  → Order entity (apply business validation)
  → OrderRepository interface (inner ring port)
  → JpaOrderRepository (outer ring implementation)
  → PostgreSQL persists
  → OrderInteractor calls OutputBoundary.present(response)
  → Presenter maps to ViewModel
  → Controller returns HTTP 201
```

**FAILURE PATH:**

```
Entity validation fails (order total negative)
  → Use Case catches domain exception
  → Calls OutputBoundary.presentFailure(error)
  → Presenter maps to error ViewModel
  → Controller returns HTTP 422
Database unavailable
  → JpaOrderRepository throws DataAccessException
  → Use Case catches, calls OutputBoundary.presentFailure
  → HTTP 503
```

**WHAT CHANGES AT SCALE:**
At scale, the Use Case layer becomes a natural transaction boundary. Multiple instances can run concurrently because Use Cases are stateless. The boundary between Interface Adapters and Frameworks is where caching (Redis), event publishing (Kafka), and async processing are added - all without touching the Use Cases or Entities.

---

### 💻 Code Example

**Example 1 - Use Case (inner ring, no framework imports):**

```java
// Use Case - pure Java, zero framework imports
public class PlaceOrderUseCase
        implements PlaceOrderInputBoundary {

    private final OrderRepository orderRepo;  // inner interface
    private final PlaceOrderOutputBoundary outputBoundary;

    public PlaceOrderUseCase(
            OrderRepository orderRepo,
            PlaceOrderOutputBoundary outputBoundary) {
        this.orderRepo = orderRepo;
        this.outputBoundary = outputBoundary;
    }

    @Override
    public void execute(PlaceOrderRequest request) {
        // All business logic - no framework noise
        Order order = Order.create(
            CustomerId.of(request.customerId()),
            request.items().stream()
                .map(OrderItem::from)
                .toList()
        );
        orderRepo.save(order);
        outputBoundary.present(
            new PlaceOrderResponse(
                order.id().value(),
                order.total()
            )
        );
    }
}
```

**Example 2 - Controller (outer ring, framework-aware):**

```java
// Controller - framework code lives here
@RestController
@RequiredArgsConstructor
public class OrderController {
    // depends on inner ring interface - not the use case class
    private final PlaceOrderInputBoundary placeOrder;
    private final HttpPresenter presenter;

    @PostMapping("/orders")
    public ResponseEntity<?> placeOrder(
            @RequestBody PlaceOrderHttpRequest request) {
        placeOrder.execute(
            new PlaceOrderRequest(
                request.customerId(),
                request.items()
            )
        );
        return presenter.buildResponse();
    }
}
```

**Example 3 - Dependency Inversion across rings:**

```java
// WRONG: Use Case directly depends on JPA (outer ring)
public class PlaceOrderUseCase {
    @Autowired  // VIOLATION - framework in inner ring
    private JpaOrderRepository repo;
}

// RIGHT: Use Case depends on interface (inner ring)
public class PlaceOrderUseCase {
    private final OrderRepository repo;  // inner interface
    // JpaOrderRepository injected at config time
}
```

---

### ⚖️ Comparison Table

| Pattern                | Rings              | Strictness  | Boilerplate | Best For                        |
| ---------------------- | ------------------ | ----------- | ----------- | ------------------------------- |
| **Clean Architecture** | 4 explicit         | Very strict | Very high   | Long-lived enterprise systems   |
| Hexagonal Architecture | 2 (domain/outside) | Strict      | High        | Domain-rich + multi-delivery    |
| Onion Architecture     | 4 concentric       | Strict      | High        | DDD-heavy systems               |
| Layered Architecture   | 3–4 horizontal     | Moderate    | Low         | CRUD apps, technical-role teams |

**How to choose:** Use Clean Architecture when the application will live 5+ years and has complex, evolving business rules. Avoid it for prototypes, simple services, or teams without strong architectural discipline - the boilerplate can crush productivity without benefit.

---

### ⚠️ Common Misconceptions

| Misconception                                             | Reality                                                                                                                       |
| --------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------- |
| Clean Architecture is just Hexagonal Architecture renamed | They share the dependency rule but differ in ring structure - Clean Architecture explicitly separates Entities from Use Cases |
| The four rings are mandatory                              | Martin says the number of rings can vary - the Dependency Rule is mandatory, the exact rings are guidance                     |
| Clean Architecture means avoiding frameworks entirely     | Frameworks live in the outer ring and are used fully - they just don't infect the inner rings                                 |
| It makes applications faster                              | It has no effect on runtime performance - it addresses maintainability and testability                                        |
| Use Cases should be thin orchestrators                    | Use Cases should contain application-specific business logic; pure orchestration with no logic is a sign of anemic use cases  |

---

### 🚨 Failure Modes & Diagnosis

**Dependency Rule violation (inner ring referencing outer)**

**Symptom:** Use Case classes import Spring annotations or JPA classes. Tests require full Spring context to run any business logic.

**Root Cause:** Developer adds `@Transactional` to Use Case, or directly accesses `EntityManager` in an Interactor for "performance."

**Diagnostic Command / Tool:**

```bash
# Detect framework imports in use case layer
grep -rn "import org.springframework\
\|import javax.persistence\
\|import jakarta.persistence" \
  src/main/java/**/usecase/
```

**Fix:** Move `@Transactional` to the outer ring (controller or gateway). Use Cases declare their transaction needs through interface contracts.

**Prevention:** ArchUnit rule: `noClasses().that().resideInPackage("..usecase..").should().dependOnClassesThat().resideInPackage("org.springframework..")`.

---

**Anemic Use Case (no logic, just delegation)**

**Symptom:** Every Use Case is: `load entity → call one method → save entity`. Zero business rules visible at the Use Case level.

**Root Cause:** All logic was pushed into entities (correct) but the Use Case just becomes a thin pass-through, adding indirection without clarity.

**Diagnostic Command / Tool:**

```bash
# Find use cases with fewer than 5 non-trivial lines
wc -l src/main/java/**/usecase/*.java \
  | sort -n | head -20
```

**Fix:** Determine whether logic belongs in the Entity (enterprise rule) or Use Case (application-specific orchestration). Use Cases should show the steps of a specific user scenario.

**Prevention:** Write Use Case acceptance tests in plain English first, then code to match them.

---

**Presenter/ViewModel confusion**

**Symptom:** Controllers return domain objects or entity classes directly to clients. Changing a business field breaks the API contract.

**Root Cause:** The Presenter abstraction is skipped - controllers directly return whatever the Use Case produced.

**Diagnostic Command / Tool:**

```bash
# Controllers returning domain/entity objects
grep -rn "return.*Entity\|return.*Domain\
\|return.*Model" \
  src/main/java/**/controller/
```

**Fix:** Every controller response must use a dedicated ViewModel/DTO class. The Presenter maps Use Case output to the ViewModel.

**Prevention:** Code review checklist: every `@RestController` method returns a dedicated response DTO, never a domain or entity class.

---

### 💎 Transferable Wisdom

**Reusable Engineering Principle:** Enforcing inward-only dependencies as an architectural invariant is a generalisation of the Open/Closed Principle to entire architectural rings. The innermost ring is closed for modification by outer rings; outer rings can extend inward concepts by implementing interfaces defined at the inner boundary.

**Where else this pattern appears:**

- **Legal hierarchy:** constitutional principles constrain statutes; statutes constrain regulations; outer layers cannot modify inner principles - the same inward-only dependency direction applied to rule systems.
- **OS kernel design:** userspace programs depend on kernel syscalls; the kernel never depends on userspace application code - the same clean boundary between stable inner core and volatile outer behaviour.
- **Financial clearing systems:** clearing rules (the inner ring) define the API that all market participants (the outer ring) implement - the domain rules are stable and the participants conform to them, not the other way around.

---

### 💡 The Surprising Truth

Uncle Bob himself has acknowledged that Clean Architecture is not appropriate for all applications. For CRUD-heavy services with minimal business logic, the Use Case layer adds boilerplate with no return on investment. The mistake is not that Clean Architecture is wrong - it is that it is frequently applied to systems too simple to benefit from it, by engineers attracted to its intellectual elegance rather than its practical problem-solving power. The most honest evaluation of Clean Architecture is not "does it satisfy the Dependency Rule?" but "does the complexity of this domain justify 3-4 layers of indirection around every business operation?"

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**

- SAP-014 - Hexagonal Architecture (the direct predecessor; Clean Architecture explicitly builds on Ports and Adapters)
- SAP-043 - SOLID Principles (specifically the Dependency Inversion Principle - the Dependency Rule is a ring-level application of DIP)
- SAP-023 - Domain Model (the Entity ring content; understanding domain modelling is required to populate the inner rings meaningfully)

**Builds On This (learn these next):**

- SAP-016 - Onion Architecture (a very similar concentric ring pattern with a named domain service ring between entities and adapters)
- SAP-017 - Vertical Slice Architecture (an alternative that reorganises around features rather than rings; useful for evaluating the trade-off)

**Alternatives / Comparisons:**

- SAP-014 - Hexagonal Architecture (same dependency direction, less prescriptive ring naming, no explicit Use Case ring)
- SAP-013 - Layered Architecture (simpler; allows infrastructure influence on domain; conventional rather than mechanically enforced)

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ WHAT IT IS   │ Concentric rings; dependencies point      │
│              │ inward; frameworks are outer details      │
├──────────────┼───────────────────────────────────────────┤
│ PROBLEM IT   │ Framework-centric code hides business     │
│ SOLVES       │ intent; untestable without infrastructure │
├──────────────┼───────────────────────────────────────────┤
│ KEY INSIGHT  │ The database and the web framework are    │
│              │ details - the business rule is the app    │
├──────────────┼───────────────────────────────────────────┤
│ USE WHEN     │ Long-lived app, complex domain, need      │
│              │ to swap frameworks/databases              │
├──────────────┼───────────────────────────────────────────┤
│ AVOID WHEN   │ Prototypes, simple CRUD, small teams      │
│              │ without architectural maturity            │
├──────────────┼───────────────────────────────────────────┤
│ TRADE-OFF    │ Testability + longevity vs high upfront   │
│              │ boilerplate and indirection               │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "The architecture screams the business,   │
│              │  not the framework"                       │
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ Hexagonal → Onion Architecture → DDD     │
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** In Clean Architecture, the Use Case (inner ring) needs to trigger an email notification after an order is placed. Email sending is infrastructure (outer ring). The Dependency Rule forbids inner rings from referencing outer rings directly. Trace step by step how an architecturally compliant implementation enables the Use Case to trigger an email - including all intermediate classes and where each one lives in the ring structure.

_Hint:_ Research the Output Port pattern from Clean Architecture - the Use Case defines an output port interface (e.g. `NotificationPort`) in the use case ring; the infrastructure ring implements it (`EmailNotificationAdapter`); the DI container wires the adapter to the port at startup. This is the Dependency Inversion Principle applied at the ring boundary.

**Q2.** A team practises Clean Architecture strictly. After 18 months, they report that feature development is 40% slower than their previous layered architecture, but bug rates are 70% lower and the system has survived two major framework migrations without domain changes. At what team size, application complexity level, and business volatility does the Clean Architecture trade-off become the correct choice? What metrics would you use to make this decision?

_Hint:_ Research the concept of "fitness functions" from Building Evolutionary Architectures (Ford, Parsons, Kua) - specifically the idea of measuring cost-of-change metrics over time: how much does a business rule change cost in implementation hours, test hours, and deployment risk? Clean Architecture pays back when the marginal cost of each change decreases over time rather than increases.

**Q3.** The Screaming Architecture principle says the top-level folder structure should reflect business concepts, not framework choices. A team's top-level packages are `controllers`, `services`, `repositories`, `entities`. Another team's are `ordering`, `payments`, `inventory`, `notifications`. Describe the specific set of changes (package moves, interface extractions, dependency inversions) required to refactor the first team's structure into the second - and identify which changes are purely cosmetic versus which ones actually enforce the Dependency Rule.

_Hint:_ Research the "package by layer vs package by feature" debate (Coding the Architecture blog by Simon Brown) and specifically Tom Hombergs' work on "hexagonal architecture in practice" which shows the exact directory structure differences between layer-first and feature-first Clean Architecture organisation.
