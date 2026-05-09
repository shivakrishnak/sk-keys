---
id: SAP-017
title: Vertical Slice Architecture
category: Software Architecture Patterns
tier: tier-5-distributed-architecture
folder: SAP-software-architecture
difficulty: ★★★
depends_on: SAP-013, SAP-043
used_by: SAP-039
related: SAP-013, SAP-014, SAP-015, SAP-018
tags:
  - architecture
  - pattern
  - advanced
  - tradeoff
status: complete
version: 1
layout: default
parent: "Software Architecture Patterns"
grand_parent: "Technical Dictionary"
nav_order: 17
permalink: /software-architecture/vertical-slice-architecture/
---

# SAP-017 - Vertical Slice Architecture

⚡ TL;DR - Vertical Slice Architecture organises code by feature rather than by technical layer, keeping everything for one feature together in a single slice.

| Field          | Value                              |
| -------------- | ---------------------------------- |
| **Depends on** | SAP-013, SAP-043                   |
| **Used by**    | SAP-039                            |
| **Related**    | SAP-013, SAP-014, SAP-015, SAP-018 |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
You're building a "Create Invoice" feature in a layered application. You open `InvoiceController.java`, add an endpoint. You open `InvoiceService.java`, add a method. You open `InvoiceRepository.java`, add a query. You open `InvoiceMapper.java`, add a mapping. You open `InvoiceValidator.java`, add validation rules. You open `InvoiceDto.java`, add a new DTO. Six files, six packages, for one conceptual feature. When a code review comes in, the reviewer must navigate between six locations to understand "create invoice." When the feature is deleted, you must remember to clean up all six locations.

**THE BREAKING POINT:**
A new developer joins and asks: "Show me all the code for creating an invoice." You say: "It's in the controller, the service, the repository, the mapper, the validator, and the DTOs - scattered across six packages." The architecture makes every simple feature feel complex, and complex features feel impossible.

**THE INVENTION MOMENT:**
This is exactly why Vertical Slice Architecture was created - to keep everything that changes together, located together, so that understanding and changing a feature requires touching one place, not six.

**EVOLUTION:**
Jimmy Bogard popularised Vertical Slice Architecture around 2018 through his MediatR library and NDC conference talks. MediatR's handler-per-request model provides the mechanical implementation: each request type gets exactly one handler class that contains all the logic for that feature. The pattern was implicit in feature-flag-driven development and microservices slicing long before Bogard named it explicitly. Today, .NET developers using MediatR with Vertical Slices is one of the most common architectural patterns for medium-to-large ASP.NET Core applications, and the idea has been adopted in Java through command bus frameworks.

---

### 📘 Textbook Definition

Vertical Slice Architecture, popularised by Jimmy Bogard, is a structural architectural pattern that organises application code around use cases (features, commands, queries) rather than around technical layers. Each "slice" is a self-contained vertical cut through all the technical concerns needed for one feature - from HTTP endpoint down to database query. Slices may share common infrastructure (database connections, middleware) but are deliberately isolated from each other's logic, minimising coupling between features.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
One feature = one folder; everything that changes together lives together.

**One analogy:**

> Traditional layered architecture is like sorting a recipe book by ingredient type: all flour-based items in one section, all proteins in another. Vertical Slice Architecture is like sorting by dish: all the steps to make pizza - dough, sauce, toppings, baking - are in one recipe card. When you want to change the pizza recipe, you have one card, not six ingredient chapters.

**One insight:**
The guiding law of Vertical Slice Architecture is Conway's Law in reverse: if your feature teams work end-to-end on a feature, your architecture should match that organisation. When a feature team owns "invoicing," all invoicing code should live in one place, not scattered across horizontal technical layers that require coordination between teams.

---

### 🔩 First Principles Explanation

**CORE INVARIANTS:**

1. A slice contains exactly what one feature needs to function - handler, request/response objects, validation, persistence query, and domain logic.
2. Slices are coupled to the framework and infrastructure at the slice level - they do not share business logic with other slices.
3. Shared infrastructure (database, cache, event bus) is extracted, but shared business logic is treated as a warning signal - it suggests a missing abstraction.

**DERIVED DESIGN:**

```
┌────────────────────────────────────────────────────────┐
│           VERTICAL SLICE ARCHITECTURE                  │
├────────────────────────────────────────────────────────┤
│                                                        │
│  LAYERED (horizontal)     VERTICAL SLICE               │
│                                                        │
│  ┌──────────────────┐     Feature A │ Feature B │ ...  │
│  │   Controllers    │     ──────────┼───────────┼───   │
│  ├──────────────────┤     Handler   │ Handler   │      │
│  │   Services       │     Validator │ Validator │      │
│  ├──────────────────┤     DB Query  │ DB Query  │      │
│  │   Repositories   │     DTO       │ DTO       │      │
│  └──────────────────┘     ──────────┴───────────┴───   │
│                                                        │
│  Dependencies: horizontal    Dependencies: isolated    │
│  cross-layer                 per feature               │
└────────────────────────────────────────────────────────┘
```

**THE TRADE-OFFS:**
**Gain:** Adding a new feature touches exactly one location. Deleting a feature is a folder delete. Understanding a feature requires reading one file or folder. Feature teams map cleanly to feature folders.
**Cost:** Code duplication is encouraged over abstraction. Two features doing similar database operations will duplicate the query. This is intentional - accidental coupling via shared abstractions is considered worse than duplication. Over time, the definition of "what belongs in a slice" vs "what belongs in shared infrastructure" requires architectural judgement.

---

### 🧪 Thought Experiment

**SETUP:**
Your application has 50 features. Using layered architecture, each feature touches 5–6 files in 5–6 packages. You add the 51st feature: "List Unpaid Invoices."

**WHAT HAPPENS WITH LAYERED ARCHITECTURE:**
You open `InvoiceController` (add endpoint), `InvoiceService` (add method), `InvoiceRepository` (add query), `InvoiceMapper` (add mapping). Each file already has 500 lines. You risk accidentally breaking "Create Invoice" while editing the shared `InvoiceService`. The test for "List Unpaid Invoices" is in `InvoiceServiceTest` alongside tests for 12 other invoice operations. When a bug is reported in "List Unpaid Invoices," you search through 4 files to find the cause.

**WHAT HAPPENS WITH VERTICAL SLICE ARCHITECTURE:**
You create `features/invoices/list-unpaid/ListUnpaidInvoicesQuery.java`. It contains: the query request class, the handler, the SQL/JPA call, and the response mapping. It's 80 lines. The test is `ListUnpaidInvoicesQueryTest.java` - 30 lines, testing exactly this one feature. When the feature has a bug, the file is immediately obvious. When the feature is deleted, it's one folder delete.

**THE INSIGHT:**
The biggest win in Vertical Slice Architecture is not less code - it's less cognitive load. You only need to understand what's in one slice to make a change to that feature.

---

### 🧠 Mental Model / Analogy

> Think of a hospital organised by disease type (vertical slices) versus a hospital organised by department type (layered). In a disease-type hospital, the cardiology team handles every cardiology patient from diagnosis to surgery to rehabilitation - one team, one patient journey. In a department-type hospital, every patient visits radiology, then surgery, then physiotherapy - each department separately. When you need to change the cardiology treatment protocol, you update one team's procedures, not three departments.

- "Disease-type team" → vertical slice (feature team, one slice per feature)
- "Department" → horizontal layer (controller department, service department)
- "Patient journey" → feature use case
- "Shared infrastructure" → blood lab, pharmacy - used by all teams but owned by none

Where this analogy breaks down: Hospitals must coordinate across departments for patient safety; features in VSA can and should be truly independent. The coordination overhead justification differs.

---

### 📶 Gradual Depth - Four Levels

**Level 1 - What it is (anyone can understand):**
Instead of having a "controllers" folder and a "services" folder, you have a "create-invoice" folder and a "list-invoices" folder. Each folder contains everything that feature needs.

**Level 2 - How to use it (junior developer):**
Each feature lives in a folder under `features/`. Inside, create a `Command` or `Query` class (the input), a `Handler` class (the logic), a `Result` class (the output), and optionally a `Validator` class. Use a mediator library (MediatR in .NET, Axon in Java) to route incoming requests to the correct handler. The handler contains all the logic - no separate service class.

**Level 3 - How it works (mid-level engineer):**
The mediator pattern decouples the HTTP controller from the handler. The controller sends a command/query to the mediator; the mediator routes it to the registered handler. Each handler is independently registered. Validation is a pipeline behaviour in the mediator - cross-cutting concerns (logging, tracing, caching) are configured once as pipeline steps that execute for every command/query. Feature-specific validation lives in the feature folder; cross-cutting validation (authentication) lives in the shared pipeline.

**Level 4 - Why it was designed this way (senior/staff):**
Bogard's insight was that the "reuse" enabled by horizontal layers is often coupling in disguise. Sharing an `InvoiceService` between 12 features means that changing one feature requires understanding all 12. The Stable Dependency Principle says depend on things that change less often than you. A shared service is less stable than a single feature. Vertical Slice Architecture rejects the premise that reuse of business logic code is desirable - it embraces duplication within slices to achieve independence between slices. The pattern scales naturally to microservices: each slice can evolve into a microservice with clear boundaries.

---

### ⚙️ How It Works (Mechanism)

**Request processing via mediator pipeline:**

```
┌──────────────────────────────────────────────────────────┐
│      VERTICAL SLICE - REQUEST PIPELINE                   │
├──────────────────────────────────────────────────────────┤
│                                                          │
│  HTTP Request → Controller                               │
│      ↓ creates Command/Query object                      │
│  Controller → Mediator.Send(command)                     │
│      ↓ pipeline behaviours (cross-cutting)               │
│  [Logging Behaviour] → [Auth Behaviour]                  │
│      → [Validation Behaviour]                            │
│      ↓ routes to feature handler                         │
│  CreateInvoiceHandler.Handle(command)  ← YOU ARE HERE    │
│      ↓ all logic in one place                            │
│  Validate → Apply domain rules → Persist → Return result │
│      ↑                                                   │
│  Single file, single folder, single concern              │
└──────────────────────────────────────────────────────────┘
```

**Folder structure:**

```
features/
  invoices/
    create/
      CreateInvoiceCommand.java
      CreateInvoiceHandler.java    ← all logic here
      CreateInvoiceValidator.java
      CreateInvoiceResult.java
    list-unpaid/
      ListUnpaidInvoicesQuery.java
      ListUnpaidInvoicesHandler.java
      ListUnpaidInvoicesResult.java
  payments/
    process/
      ProcessPaymentCommand.java
      ProcessPaymentHandler.java
shared/
  database/
    DatabaseConfiguration.java
  middleware/
    LoggingBehaviour.java
    AuthenticationBehaviour.java
```

**What handlers look like - complete self-contained slice:**

```java
@Component
public class CreateInvoiceHandler
        implements RequestHandler<CreateInvoiceCommand,
                                  CreateInvoiceResult> {
    private final EntityManager em;    // shared infra only
    private final EventBus events;     // shared infra only

    @Override
    @Transactional
    public CreateInvoiceResult handle(
            CreateInvoiceCommand cmd) {
        // ALL logic for this one feature right here:
        validateBusinessRules(cmd);
        Invoice invoice = Invoice.create(
            cmd.customerId(), cmd.lineItems()
        );
        em.persist(invoice);
        events.publish(new InvoiceCreatedEvent(
            invoice.id()
        ));
        return new CreateInvoiceResult(invoice.id());
    }

    private void validateBusinessRules(
            CreateInvoiceCommand cmd) {
        // Business validation specific to THIS feature
        if (cmd.lineItems().isEmpty()) {
            throw new ValidationException(
                "Invoice must have at least one line item"
            );
        }
    }
}
```

---

### 🔄 The Complete Picture - End-to-End Flow

**NORMAL FLOW:**

```
HTTP POST /invoices
  → InvoiceController (creates CreateInvoiceCommand)
  → Mediator.send(command)
  → [Logging Behaviour] → [Validation Behaviour]
  → CreateInvoiceHandler.handle()  ← YOU ARE HERE
  → Invoice.create() (domain logic)
  → EntityManager.persist() (database)
  → EventBus.publish() (domain event)
  → CreateInvoiceResult → HTTP 201
```

**FAILURE PATH:**

```
Validation fails (empty line items)
  → ValidationException thrown in handler
  → Mediator pipeline catches
  → HTTP 422 Unprocessable Entity
Database fails
  → Transaction rolls back in handler
  → Exception propagates to controller
  → HTTP 500 / 503
```

**WHAT CHANGES AT SCALE:**
At scale, vertical slices map naturally to microservices - each slice can be extracted into its own service with clear boundaries. Read slices (queries) can be directed to read replicas or dedicated read models (CQRS). Write slices (commands) go through full transactional paths. The mediator pipeline allows cross-cutting concerns (rate limiting, caching) to be added without modifying any slice.

---

### 💻 Code Example

**Example 1 - Wrong: shared service couples unrelated features:**

```java
// BAD - shared service couples 12 different features
@Service
public class InvoiceService {
    // Feature 1's logic
    public InvoiceDto createInvoice(CreateCmd cmd) { ... }
    // Feature 2's logic
    public List<InvoiceDto> listUnpaid() { ... }
    // Feature 3's logic (now coupled to Feature 1 via class)
    public void voidInvoice(VoidCmd cmd) { ... }
    // 9 more features...
    // Changing any one risks breaking the others
}
```

**Example 2 - Right: isolated vertical slice (Java + Spring):**

```java
// Each feature in its own class - no coupling
// Feature 1: Create Invoice
@Component
@RequiredArgsConstructor
public class CreateInvoiceHandler {
    private final InvoiceJpaRepository repo;

    @Transactional
    public CreateInvoiceResult handle(
            CreateInvoiceCommand cmd) {
        Invoice invoice = new Invoice(
            cmd.customerId(), cmd.items()
        );
        repo.save(invoice);
        return new CreateInvoiceResult(invoice.getId());
    }
}

// Feature 2: List Unpaid - completely separate
@Component
@RequiredArgsConstructor
public class ListUnpaidInvoicesHandler {
    private final InvoiceJpaRepository repo;

    public List<InvoiceSummary> handle(
            ListUnpaidInvoicesQuery query) {
        return repo.findByStatus(UNPAID)
            .stream()
            .map(InvoiceSummary::from)
            .toList();
    }
}
// Changing Feature 2 cannot affect Feature 1
```

**Example 3 - MediatR-style pipeline (cross-cutting):**

```java
// Shared behaviour - runs for EVERY command/query
@Component
public class LoggingBehaviour<TRequest, TResponse>
        implements PipelineBehaviour<TRequest, TResponse> {

    private final Logger log =
        LoggerFactory.getLogger(getClass());

    @Override
    public TResponse handle(
            TRequest request,
            RequestHandlerDelegate<TResponse> next) {
        log.info("Handling {}", request.getClass().getSimpleName());
        long start = System.currentTimeMillis();
        TResponse response = next.handle();
        log.info("Handled {} in {}ms",
            request.getClass().getSimpleName(),
            System.currentTimeMillis() - start);
        return response;
    }
}
// Slices never need to add logging themselves
```

---

### ⚖️ Comparison Table

| Aspect            | Vertical Slice     | Layered Architecture | Clean Architecture     |
| ----------------- | ------------------ | -------------------- | ---------------------- |
| Organisation axis | Feature / use case | Technical concern    | Dependency direction   |
| Change locality   | High (one folder)  | Low (all layers)     | Medium (one ring)      |
| Code duplication  | Accepted           | Minimised            | Minimised              |
| New feature cost  | Low                | High (many files)    | Very high (many rings) |
| Team alignment    | Feature teams      | Tech-role teams      | Either                 |

**How to choose:** Use Vertical Slice Architecture when your team is organised into feature teams, when you have many distinct features with low cross-feature logic sharing, or when you want to eventually migrate toward microservices. Use Layered Architecture when your team has distinct technical specialisms (frontend, backend, DBA).

---

### ⚠️ Common Misconceptions

| Misconception                                 | Reality                                                                                                                  |
| --------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------ |
| Vertical slices have no layers at all         | Slices still use layers internally - handler uses repositories uses database - but they don't share layers across slices |
| Code duplication is always bad                | In Vertical Slice Architecture, duplication within a slice is preferred over coupling between slices                     |
| Every feature needs a separate database table | Slices share the same database; they're isolated at the code level, not the data level                                   |
| This only works with CQRS                     | CQRS complements VSA naturally but is not required - any routing mechanism (direct DI, mediator) works                   |
| Vertical slices cannot share any code         | Shared infrastructure (DB connections, auth) is explicitly shared; only business logic is isolated                       |

---

### 🚨 Failure Modes & Diagnosis

**Implicit coupling via shared domain objects**

**Symptom:** Changing the `Invoice` class to support a new field breaks 8 handlers across different slices.

**Root Cause:** Slices share domain model classes that embed too many assumptions. Domain objects become coupling points across slices.

**Diagnostic Command / Tool:**

```bash
# Find shared domain objects referenced across many slices
grep -rn "class Invoice\|Invoice " \
  src/main/java/**/features/ \
  | awk -F: '{print $1}' | sort | uniq -c | sort -rn
```

**Fix:** Give each slice its own request/response representation. Use feature-specific projections rather than shared domain objects.

**Prevention:** Each slice should define its own request model. Shared objects should be infrastructure types (IDs, Money values), not feature-specific entities.

---

**Handler God Object**

**Symptom:** Handlers grow to 500+ lines, containing orchestration, validation, persistence, and notification logic all mixed together.

**Root Cause:** Developers treat the handler as the new "service" and accumulate all logic there without further organisation.

**Diagnostic Command / Tool:**

```bash
# Find large handler files
find . -name "*Handler.java" \
  -exec wc -l {} + | sort -rn | head -20
```

**Fix:** Extract inline classes within the slice folder for validation, business rules, and persistence - but keep them all in the same feature folder.

**Prevention:** Handler's `handle()` method should be 10–20 lines: validate, apply rule, persist, publish. Extract complexity into private methods or slice-local helper classes.

---

**Cross-slice business logic leakage**

**Symptom:** A handler imports and calls another handler. Features depend on each other's internal logic.

**Root Cause:** A use case genuinely needs data or logic from another use case, and the developer reaches directly across slice boundaries.

**Diagnostic Command / Tool:**

```bash
# Handlers importing other handlers
grep -rn "import.*Handler" \
  src/main/java/**/features/
```

**Fix:** Shared business logic that appears in multiple slices belongs in a shared domain service or a new slice that both can call independently.

**Prevention:** Slices communicate via events or through shared domain model objects, never by calling each other's handlers.

---

### � Transferable Wisdom

**Reusable Engineering Principle:** Organise by what changes together, not by what looks similar. The axis of decomposition should match the axis of change - code that changes for the same reason belongs in the same place, not in the same technical category.

**Where else this pattern appears:**

- **Git commits:** a good commit contains exactly the files that changed for one reason - the vertical slice of a feature, not "all the service classes edited today" - because commits are reviewed and reverted as units.
- **Team organisation:** Conway's Law predicts that feature teams (each team owns their feature end-to-end) naturally produce vertical slices, while component teams (each team owns a technical layer) naturally produce layered architecture.
- **Microservice decomposition:** each microservice IS a vertical slice - it contains its own data store, business logic, and API, organised around a business capability rather than a technical tier.

---

### 💡 The Surprising Truth

Vertical Slice Architecture does not eliminate technical layers - it relocates them. Each slice typically still has its own handler (controller equivalent), validation (service equivalent), and data access (repository equivalent). The difference is that these layers are private to the slice, not shared globally across the application. An internal structure of `Handler`, `Validator`, `Query` classes inside each slice folder is expected and correct. VSA is frequently misunderstood as "no layers" when it is actually "private layers per feature" rather than "public shared layers across features."

---

### �🔗 Related Keywords

**Prerequisites (understand these first):**

- SAP-013 - Layered Architecture (what Vertical Slice Architecture explicitly reacts against; understanding the problem makes the solution clear)
- SAP-043 - SOLID Principles (specifically Single Responsibility Principle applied at the feature/module level, not just the class level)

**Builds On This (learn these next):**

- SAP-039 - Modular Monolith Patterns (slices naturally evolve into modules; a modular monolith is VSA with enforced inter-module boundaries)
- SAP-018 - CQRS Pattern (the most common companion pattern; command slices handle writes, query slices handle reads)

**Alternatives / Comparisons:**

- SAP-013 - Layered Architecture (organises by technical tier instead of feature; preferred when teams are organised by technical specialty)
- SAP-015 - Clean Architecture (organises by dependency direction and ring; more prescriptive about cross-feature structure)
- `Clean Architecture` - organises by dependency direction; more prescriptive about ring structure
- `Modular Monolith Patterns` - adds module-level boundaries to vertical slices

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ WHAT IT IS   │ Code organised by feature, not by layer;  │
│              │ one folder per use case                   │
├──────────────┼───────────────────────────────────────────┤
│ PROBLEM IT   │ Layered apps scatter one feature across   │
│ SOLVES       │ many files in many packages               │
├──────────────┼───────────────────────────────────────────┤
│ KEY INSIGHT  │ Duplication within slices is safer than   │
│              │ coupling between slices                   │
├──────────────┼───────────────────────────────────────────┤
│ USE WHEN     │ Feature teams; many independent features; │
│              │ planning microservices migration          │
├──────────────┼───────────────────────────────────────────┤
│ AVOID WHEN   │ Heavy cross-feature shared logic;         │
│              │ team organised by technical specialty     │
├──────────────┼───────────────────────────────────────────┤
│ TRADE-OFF    │ Feature isolation vs cross-feature logic  │
│              │ duplication                               │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "One recipe card per dish,                │
│              │  not one chapter per ingredient"          │
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ CQRS → Modular Monolith → Microservices  │
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** In a Vertical Slice Architecture, you have a "Create Order" slice and a "Verify Customer Credit" slice. The order creation process requires a customer credit check. If you call the credit verification handler from the order creation handler, you create cross-slice coupling. If you duplicate the credit check logic, you have two places to update when credit rules change. What is the architecturally correct resolution, and how does it affect slice independence?

*Hint:* Research how Jimmy Bogard addresses the "shared logic" problem in VSA - specifically the pattern of extracting shared logic into a "SharedKernel" or "Common" folder (not a slice) that contains pure domain logic with no handler infrastructure, and the rule that only stateless pure domain logic should be shared; handler orchestration should never be shared between slices.

**Q2.** A system uses Vertical Slice Architecture with 200 features/slices. Analysis shows that 40 slices all query the same "customer account balance" data in slightly different ways. A team proposes extracting a shared `AccountBalanceService` that all 40 slices call. What is the precise architectural consequence of this extraction, and under what conditions would you accept vs reject the proposal?

*Hint:* Research the "Bounded Context" concept from DDD and apply it to this problem - specifically whether "customer account balance" is a concept that belongs in a separate bounded context (which would mean the 40 slices should call an internal service for that context, not a shared service class), versus whether the variations are cosmetic query differences that a single read model can serve.

**Q3.** In a Vertical Slice Architecture, each slice is meant to be independently understandable and changeable. Cross-cutting concerns (authentication, logging, validation, error handling) affect all slices. How does VSA handle cross-cutting concerns without creating cross-slice coupling, and what mechanism makes this architectural separation possible?

*Hint:* Research MediatR's `IPipelineBehavior<TRequest, TResponse>` interface - specifically how pipeline behaviours implement cross-cutting concerns (logging, validation, caching) as middleware that wraps every handler WITHOUT any handler knowing about it. The handler knows nothing about logging; the logger knows nothing about the handler's domain logic. This is the VSA answer to cross-cutting concerns.
