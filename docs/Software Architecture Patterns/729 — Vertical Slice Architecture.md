---
layout: default
title: "Vertical Slice Architecture"
parent: "Software Architecture Patterns"
nav_order: 729
permalink: /software-architecture/vertical-slice-architecture/
number: "729"
category: Software Architecture Patterns
difficulty: ★★★
depends_on: "Layered Architecture, CQRS, MediatR"
used_by: "ASP.NET Core + MediatR, Spring + custom, Node.js feature modules"
tags: #advanced, #architecture, #feature-modules, #cqrs, #slices
---

# 729 — Vertical Slice Architecture

`#advanced` `#architecture` `#feature-modules` `#cqrs` `#slices`

⚡ TL;DR — **Vertical Slice Architecture** organizes code by **feature** (not layer) — each feature (use case) owns its own handler, request, response, and data access in one cohesive slice, eliminating cross-feature coupling.

| #729            | Category: Software Architecture Patterns                         | Difficulty: ★★★ |
| :-------------- | :--------------------------------------------------------------- | :-------------- |
| **Depends on:** | Layered Architecture, CQRS, MediatR                              |                 |
| **Used by:**    | ASP.NET Core + MediatR, Spring + custom, Node.js feature modules |                 |

---

### 📘 Textbook Definition

**Vertical Slice Architecture**, popularized by Jimmy Bogard (creator of MediatR and AutoMapper), is an architectural pattern where the codebase is organized by **feature** (vertical slices) rather than by **technical concern** (horizontal layers). A "slice" is a thin, feature-specific cross-section of the application from API endpoint to database: it contains the request/command, the handler (business logic), and the data access — all in one place. Key insight: **coupling is minimized within slices (each slice is self-contained) and between slices (slices don't call each other directly)**. Contrast with layered architecture: adding a feature requires touching the Controller layer, the Service layer, AND the Repository layer — multiple horizontal layers. With Vertical Slice: adding a feature means creating one new slice (one new folder/package). Vertical Slice often uses **CQRS** (separating Commands from Queries) and **Mediator pattern** to route requests to the appropriate slice handler. Benefits: strong cohesion within feature, low coupling between features, easy to add/remove features, natural fit for microservices decomposition. Drawback: common logic (validation, authorization) can be duplicated across slices if not managed carefully.

---

### 🟢 Simple Definition (Easy)

A pizza shop: instead of organizing staff by role (all chefs together, all cashiers together), organize by pizza type (a Margherita team handles ordering, cooking, boxing Margheritas; a Pepperoni team handles everything for pepperonis). Each "pizza team" owns the whole process for their pizza. Add a new pizza: add a new team. Horizontal layers (Chef layer, Cashier layer): every new pizza requires changes to every layer. Vertical slices (Margherita team, Pepperoni team): each team is self-contained. New pizza = new team, zero changes to existing teams.

---

### 🔵 Simple Definition (Elaborated)

In layered architecture: 50 features × 3 layers = 150 files you must coordinate. Adding "GetOrderHistory" means: add a method to OrderController (Layer 1), add a method to OrderService (Layer 2), add a method to OrderRepository (Layer 3). Change three files, risk touching unrelated code. In vertical slices: "GetOrderHistory" is one file (GetOrderHistoryHandler.java). It contains the query, the handler logic, and the data access. Other features are unaffected. The handler is testable in isolation without mocking layers. Tradeoff: common logic (e.g., validation, logging) must be handled via cross-cutting concerns (behaviors/middleware), not shared service classes.

---

### 🔩 First Principles Explanation

**Slice structure, MediatR-style pipeline, command/query separation:**

```
VERTICAL SLICE vs LAYERED (adding a feature):

  LAYERED (adding "CreateProduct" feature):

  Files to touch:
    controllers/ProductController.java    ← Add createProduct() endpoint
    services/ProductService.java          ← Add createProduct() method
    repositories/ProductRepository.java   ← Add save() method (or use existing)
    dto/CreateProductRequest.java         ← New DTO
    dto/ProductResponse.java              ← New DTO

  Problem: ProductController.java already has getProduct, listProducts, updateProduct.
  Adding a method: risk of touching unrelated methods.
  ProductService.java: 50 methods. Adding createProduct(): near 50 others. Hard to find.

  VERTICAL SLICE (adding "CreateProduct" feature):

  New folder: features/create-product/

  New files (single location):
    features/create-product/
    ├── CreateProductCommand.java         ← Input (command = write operation)
    ├── CreateProductResponse.java        ← Output
    ├── CreateProductHandler.java         ← ALL logic: validation, business rule, DB write
    └── CreateProductValidator.java       ← Optional: validation logic

  Existing features: ZERO files touched.

SLICE STRUCTURE (Java/Spring example):

  // Command (input data):
  public record CreateProductCommand(String name, BigDecimal price, String category) {}

  // Response (output data):
  public record CreateProductResponse(UUID productId, String name) {}

  // Handler (the "slice" — contains everything for this feature):
  @Component
  public class CreateProductHandler implements Handler<CreateProductCommand, CreateProductResponse> {
      private final ProductRepository productRepository;
      private final CategoryValidator categoryValidator;

      public CreateProductResponse handle(CreateProductCommand command) {
          // Validation (inline or via validator):
          categoryValidator.validate(command.category());
          if (command.price().compareTo(BigDecimal.ZERO) <= 0) {
              throw new ValidationException("Price must be positive");
          }

          // Business logic:
          Product product = Product.create(command.name(), command.price(), command.category());

          // Data access (directly — no separate service layer):
          Product saved = productRepository.save(product);

          return new CreateProductResponse(saved.id(), saved.name());
      }
  }

  // Controller (thin — just dispatches to handler):
  @RestController
  @RequestMapping("/api/products")
  public class ProductController {
      private final Mediator mediator;  // Routes commands to handlers.

      @PostMapping
      public ResponseEntity<CreateProductResponse> create(@RequestBody CreateProductCommand cmd) {
          CreateProductResponse response = mediator.send(cmd);
          return ResponseEntity.status(201).body(response);
      }
  }

MEDIATOR PATTERN (routes request to handler):

  Mediator: runtime registry of Command/Query type → Handler mappings.

  mediator.send(new CreateProductCommand(...))
    → looks up: CreateProductHandler registered for CreateProductCommand
    → calls: CreateProductHandler.handle(command)
    → returns: CreateProductResponse

  No direct coupling between Controller and Handler.
  Controllers: thin HTTP adapters, no business logic.

  Mediator also enables: cross-cutting behaviors (middleware pipeline):
    1. LoggingBehavior: logs all commands/queries.
    2. ValidationBehavior: validates all commands before handler runs.
    3. TransactionBehavior: wraps commands in a transaction.
    4. AuthorizationBehavior: checks permissions.

  THESE BEHAVIORS APPLY TO ALL SLICES: no duplication per handler.

CQRS IN VERTICAL SLICES:

  Commands (writes): CreateProduct, UpdatePrice, DeleteProduct
    → Each in its own slice.
    → Typically: validate, modify state, persist, return minimal response.

  Queries (reads): GetProduct, ListProducts, SearchProducts
    → Each in its own slice.
    → Can use optimized read models (not through domain entities).
    → Queries: often thin — just fetch and map to DTO, no domain rules.

  Example of query slice (thin — no domain objects needed):

  // Query:
  public record GetProductQuery(UUID productId) {}

  // Query Handler (reads directly from DB — no domain object needed):
  @Component
  public class GetProductHandler implements Handler<GetProductQuery, ProductDTO> {
      private final JdbcTemplate jdbc;  // Direct JDBC — no JPA entity, no domain entity.

      public ProductDTO handle(GetProductQuery query) {
          // Direct SQL: optimized for reading. No domain rules needed for simple read.
          return jdbc.queryForObject(
              "SELECT id, name, price, category FROM products WHERE id = ?",
              (rs, row) -> new ProductDTO(rs.getString("id"), rs.getString("name"),
                                         rs.getBigDecimal("price"), rs.getString("category")),
              query.productId()
          );
      }
  }
  // Query: directly reads DB with JDBC. No JPA entity load, no domain entity creation.
  // Much simpler than going through layered architecture just to read data.

SHARING CODE BETWEEN SLICES:

  Problem: multiple slices need: product validation, authorization checks, audit logging.

  WRONG: create a "shared service" ProductValidationService that slices depend on.
    Coupling returns: all slices depend on the shared service.
    Change the service: affects all slices.

  RIGHT: Use pipeline behaviors (cross-cutting):
    ValidationBehavior: auto-validates all commands via FluentValidation/Jakarta Validation.
    AuthorizationBehavior: checks permissions via annotations.
    AuditBehavior: logs command execution to audit log.

  ALSO RIGHT: inline validation per slice (for truly slice-specific logic).
  ALSO RIGHT: Value Objects from domain (e.g., Price, Email validation) as shared domain primitives.

FOLDER STRUCTURE:

  src/
  ├── features/
  │   ├── create-product/
  │   │   ├── CreateProductCommand.java
  │   │   ├── CreateProductHandler.java
  │   │   └── CreateProductResponse.java
  │   ├── get-product/
  │   │   ├── GetProductQuery.java
  │   │   ├── GetProductHandler.java
  │   │   └── ProductDTO.java
  │   ├── update-price/
  │   │   └── ...
  │   └── list-products/
  │       └── ...
  ├── common/                   ← Shared infrastructure only
  │   ├── mediator/Mediator.java
  │   ├── behaviors/ValidationBehavior.java
  │   └── domain/Product.java   ← Shared domain entities (if domain is shared)
  └── infrastructure/
      └── persistence/...
```

---

### ❓ Why Does This Exist (Why Before What)

WITHOUT Vertical Slice Architecture (layered):

- Each new feature: changes 3-5 different layer files (risk of regression in other features)
- "All Orders" endpoint: buried in OrderService with 30 other order-related methods
- Deleting a feature: must find and remove methods from every layer

WITH Vertical Slice Architecture:
→ Each feature is self-contained in one folder: add, find, delete features without touching others
→ Testing: test one slice in isolation without mocking an entire service layer
→ Team scalability: different developers own different feature slices without merge conflicts

---

### 🧠 Mental Model / Analogy

> A newspaper: instead of organizing by role (all photographers together, all writers together, all editors together), organize by story (each story has its own writer, photographer, and editor as a team). The "Local Crime" team owns writing, photography, and editing for crime stories. Add a new beat (Sports): add a Sports team. The Crime team is completely unaffected. Horizontal layer organization (all writers in one room): every new story requires coordinating multiple rooms. Vertical slice (story teams): each story team works independently.

"Story team" = vertical slice (one feature)
"Writer, photographer, editor within a story team" = handler, validator, data access within a slice
"Adding a new beat" = adding a new feature (new slice folder)
"Horizontal layer organization" = traditional layered architecture

---

### ⚙️ How It Works (Mechanism)

```
VERTICAL SLICE REQUEST FLOW:

  1. HTTP POST /api/products → ProductController.create(command)
  2. Controller: mediator.send(command)
  3. Mediator: routes to CreateProductHandler (registered for CreateProductCommand)
  4. Mediator pipeline: ValidationBehavior → TransactionBehavior → CreateProductHandler
  5. CreateProductHandler.handle(): validate, domain logic, DB write — all in ONE class
  6. Handler returns: CreateProductResponse
  7. Mediator pipeline returns response through behaviors
  8. Controller: HTTP 201 response
```

---

### 🔄 How It Connects (Mini-Map)

```
CQRS (separates commands from queries — natural fit for slices)
        │
        ▼ (organize each command/query as independent slice)
Vertical Slice Architecture ◄──── (you are here)
(features organized vertically, Mediator routes to handlers)
        │
        ├── Layered Architecture: horizontal alternative (layer-based organization)
        ├── Mediator Pattern: routing mechanism for commands/queries to handlers
        └── CQRS: separates read and write slices
```

---

### 💻 Code Example

```java
// Complete minimal vertical slice (Spring Boot):

// 1. Command (input):
public record PlaceOrderCommand(UUID customerId, List<OrderItem> items) {}

// 2. Response (output):
public record PlaceOrderResponse(UUID orderId, BigDecimal total) {}

// 3. Handler (the entire slice — validation + logic + DB write):
@Component
@Transactional
public class PlaceOrderHandler {
    private final OrderRepository orderRepo;
    private final InventoryPort inventory;

    public PlaceOrderResponse handle(PlaceOrderCommand cmd) {
        // Validation (slice-specific):
        if (cmd.items().isEmpty()) throw new ValidationException("Order must have items");

        // Domain logic:
        inventory.reserve(cmd.items());  // Throws if insufficient stock.
        Order order = Order.place(cmd.customerId(), cmd.items());

        // Persistence:
        Order saved = orderRepo.save(order);
        return new PlaceOrderResponse(saved.id(), saved.total());
    }
}

// 4. Controller (thin dispatcher):
@PostMapping("/orders")
public ResponseEntity<PlaceOrderResponse> placeOrder(@RequestBody PlaceOrderCommand cmd) {
    return ResponseEntity.status(201).body(placeOrderHandler.handle(cmd));
    // No service layer indirection. Controller → Handler directly (or via Mediator).
}
```

---

### ⚠️ Common Misconceptions

| Misconception                                           | Reality                                                                                                                                                                                                                                                                                                                                                                              |
| ------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| Vertical slices mean no shared code at all              | Shared domain entities, value objects, infrastructure configuration, and cross-cutting behaviors (logging, validation pipeline, transaction handling) are still shared. What's NOT shared: feature-specific logic between slices. The rule: if changing logic in one feature shouldn't affect another feature, don't share it. If it's infrastructure or domain primitives: share it |
| Vertical Slice Architecture replaces Clean Architecture | They're orthogonal. Clean Architecture: describes dependency direction (inward). Vertical Slice: describes organization (by feature). You can have vertical slices that also follow the Dependency Rule (domain entities don't depend on infrastructure). Jimmy Bogard himself combines Vertical Slice with Clean Architecture dependency rules in some projects                     |
| Vertical slices lead to duplicate code                  | Code duplication is a risk, but explicit duplication is often better than wrong abstraction. If two slices have similar code: first verify the similarity is accidental (should duplicate) vs. essential (should share). "Wrong abstraction is worse than duplication" (Sandi Metz). Pipeline behaviors handle true cross-cutting duplication without coupling slices                |

---

### 🔥 Pitfalls in Production

**Slice explosion — too many small slices with duplicated domain logic:**

```
PROBLEM: Team takes "one file per feature" too literally.

  features/
  ├── get-user-by-id/GetUserByIdHandler.java        (50 lines)
  ├── get-user-by-email/GetUserByEmailHandler.java  (48 lines — 90% identical to above)
  ├── get-user-by-phone/GetUserByPhoneHandler.java  (47 lines — 95% identical)
  └── get-user-by-username/GetUserByUsernameHandler.java (49 lines — 92% identical)

  Each handler has same: authorization check, user-not-found handling, DTO mapping.
  Bug in DTO mapping: must fix in 4 places.
  New field in UserDTO: must add to 4 handlers.

BAD APPROACH: copy-paste handler per query variant:
  public class GetUserByIdHandler {
      public UserDTO handle(GetUserByIdQuery query) {
          User user = userRepo.findById(query.id()).orElseThrow(UserNotFoundException::new);
          return new UserDTO(user.id(), user.email(), user.name(), user.phone());
          // ^ This exact mapping duplicated in 3 other handlers.
      }
  }

FIX 1: Consolidate similar queries into one slice when they share core logic:
  // One "GetUser" slice that handles multiple lookup strategies:
  public class GetUserHandler {
      public UserDTO handle(GetUserQuery query) {
          User user = switch (query.lookupType()) {
              case BY_ID -> userRepo.findById(query.id()).orElseThrow(UserNotFoundException::new);
              case BY_EMAIL -> userRepo.findByEmail(query.email()).orElseThrow(UserNotFoundException::new);
              case BY_PHONE -> userRepo.findByPhone(query.phone()).orElseThrow(UserNotFoundException::new);
          };
          return UserMapper.toDTO(user);  // Shared mapper — one place to fix DTO mapping.
      }
  }

FIX 2: Share the DTO mapper as a common utility (not a shared service with logic):
  public class UserMapper {
      public static UserDTO toDTO(User user) {
          return new UserDTO(user.id(), user.email(), user.name(), user.phone());
          // One place. All user-read slices use this mapper.
      }
  }

FIX 3: Know when to slice and when to consolidate:
  SLICE: when feature has genuinely distinct business logic (PlaceOrder vs CancelOrder: very different).
  CONSOLIDATE: when features differ only in a parameter (GetUserById vs GetUserByEmail: same core logic).

RULE OF THUMB:
  If two "features" share > 70% of logic: consider one handler with a parameter.
  If two "features" have < 30% overlap: definitely two separate slices.
  50-70% overlap: judgment call. Prefer duplication if the divergence is likely to grow.
```

---

### 🔗 Related Keywords

- `CQRS` — the pattern that separates read (query) and write (command) slices
- `Mediator Pattern` — routing mechanism that decouples controllers from handlers
- `Layered Architecture` — the horizontal alternative to vertical slicing
- `Clean Architecture` — orthogonal: can apply dependency rule within vertical slices
- `Feature Modules` — module-level manifestation of the same vertical-slicing principle

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ KEY IDEA     │ Organize by feature (vertical), not layer │
│              │ (horizontal). Each slice owns: request,  │
│              │ handler, data access. Self-contained.    │
├──────────────┼───────────────────────────────────────────┤
│ USE WHEN     │ Many distinct features; feature teams;   │
│              │ layered services becoming too large;     │
│              │ CQRS-heavy applications                  │
├──────────────┼───────────────────────────────────────────┤
│ AVOID WHEN   │ Very few features; high logic sharing    │
│              │ across features; team unfamiliar with    │
│              │ Mediator/CQRS pattern                    │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "Story teams: each story has its own    │
│              │  writer, photographer, editor. Add a    │
│              │  beat = add a team."                    │
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ CQRS → Mediator Pattern → Clean          │
│              │ Architecture → Layered Architecture      │
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** You have 200 feature slices in your vertical slice application. A new cross-cutting requirement: every command must emit a domain event to an event bus after successful execution. In layered architecture: add this to the Service layer base class — done once. In vertical slices: how do you add this to all 200 command handlers without touching all 200 files? Design the exact mechanism (pipeline behavior, AOP, or other approach).

**Q2.** Two slices: `CreateInvoice` and `CreateQuote` share 80% identical logic (both create financial documents, validate amounts, check customer credit limits). A junior developer wants to extract a shared `FinancialDocumentService` that both slices call. A senior developer says: "Don't share it — keep the duplication." Who is right? Under what conditions is the senior developer correct? Under what conditions should you extract the shared service?
