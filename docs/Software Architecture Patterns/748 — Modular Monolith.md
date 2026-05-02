---
layout: default
title: "Modular Monolith"
parent: "Software Architecture Patterns"
nav_order: 748
permalink: /software-architecture/modular-monolith/
number: "748"
category: Software Architecture Patterns
difficulty: ★★★
depends_on: "Bounded Context, Microservices, Layered Architecture"
used_by: "Medium-complexity systems, Pre-microservices migration"
tags: #advanced, #architecture, #monolith, #modules, #deployment
---

# 748 — Modular Monolith

`#advanced` `#architecture` `#monolith` `#modules` `#deployment`

⚡ TL;DR — A **Modular Monolith** is a single deployable unit with clearly defined internal module boundaries — combining the operational simplicity of a monolith with the domain organization of microservices, without the distributed systems complexity.

| #748            | Category: Software Architecture Patterns               | Difficulty: ★★★ |
| :-------------- | :----------------------------------------------------- | :-------------- |
| **Depends on:** | Bounded Context, Microservices, Layered Architecture   |                 |
| **Used by:**    | Medium-complexity systems, Pre-microservices migration |                 |

---

### 📘 Textbook Definition

A **Modular Monolith** is an architectural style where an application is built as a single deployable unit with clearly defined, loosely coupled internal modules — each module corresponding to a bounded context with its own domain model, database tables (logically separated), and public API (module interface). Unlike a "Big Ball of Mud" monolith (all code entangled), the Modular Monolith enforces: (1) **Strong encapsulation**: modules expose only their public interface; internal classes are inaccessible from other modules. (2) **Domain ownership**: each module owns its data; direct cross-module database access is forbidden. (3) **Explicit dependencies**: cross-module calls go through defined interfaces (events or public module APIs). (4) **Single deployment**: the entire application deploys as one unit. Unlike microservices (separate deployments), Modular Monolith: one deployment, one JVM, one CI/CD pipeline, no network latency between modules, no distributed transactions.

---

### 🟢 Simple Definition (Easy)

An office building vs. separate buildings. Microservices: 10 separate buildings — each team has their own building, own address, own phone line. Easy to scale each building independently, but: complicated logistics (inter-building communication, each building needs its own reception, maintenance). Modular Monolith: one well-designed building with separate floors — each floor has a clearly defined space, locked stairwell doors (module boundaries), and a reception desk (module public API). Communication between floors: via the building's intercom (events). Same operational simplicity as one building; clear organization of one floor per team.

---

### 🔵 Simple Definition (Elaborated)

A Spring Boot application structured as modules: `ordering-module`, `inventory-module`, `billing-module`, `shipping-module` — each a separate Maven/Gradle subproject. The `ordering-module` cannot import `com.company.inventory.internal.*`; only `com.company.inventory.api.*` is accessible. The inventory module owns its own tables; the ordering module cannot run `SELECT * FROM inventory_items`. Cross-module communication: via in-process events (Spring `ApplicationEventPublisher`) or the module's public service interface. Deploy: one JAR. Database: one schema per module (or separate schemas). Test: one integration test suite. Operational simplicity of a monolith; domain clarity of microservices.

---

### 🔩 First Principles Explanation

**Modular Monolith vs. Big Ball of Mud vs. Microservices:**

```
THE THREE OPTIONS:

  1. BIG BALL OF MUD MONOLITH:

     One deployment. No module boundaries. All code entangled.

     com.company/
         services/
             OrderService.java  — imports InventoryService, BillingService, UserService
             InventoryService.java — imports OrderService, ProductService
             BillingService.java — imports OrderService, InventoryService
             // Every class imports every other class.
             // "Business logic" spread everywhere.
             // Change one thing: ripple effects everywhere.

     Characteristics:
       ✓ Simple to start (no structure required)
       ✓ Simple deployment (one JAR)
       ✗ Hard to understand (where does anything live?)
       ✗ Hard to change without breaking things
       ✗ No team ownership
       ✗ No domain model clarity

  2. MODULAR MONOLITH:

     One deployment. Strong module boundaries. Modules are independent by design.

     modules/
         ordering/
             api/             — public interface (allowed to import from other modules)
                 OrderingModule.java  — public facade
                 dto/             — public DTOs
                 events/          — published events
             internal/        — private (other modules cannot import)
                 domain/
                 application/
                 infrastructure/
         inventory/
             api/             — public interface
                 InventoryModule.java
                 dto/
                 events/
             internal/        — private
         billing/
             api/
             internal/

     Characteristics:
       ✓ Simple deployment (one JAR, one CI/CD)
       ✓ No network latency between modules
       ✓ No distributed transactions needed
       ✓ Simple local debugging
       ✓ Strong domain ownership per module
       ✓ Easy migration to microservices (modules → services)
       ✗ One JVM: one module's memory leak affects all
       ✗ Cannot scale individual modules independently
       ✗ One technology stack (all Java, all Spring)

  3. MICROSERVICES:

     Multiple deployments. Strong service boundaries. Network between services.

     order-service/ — deploys independently. Own DB. Own CI/CD.
     inventory-service/ — deploys independently.
     billing-service/ — deploys independently.

     Characteristics:
       ✓ Independent deployment and scaling
       ✓ Technology diversity
       ✓ Fault isolation
       ✗ Network latency between services
       ✗ Distributed transaction complexity
       ✗ Operational complexity (many services to manage)
       ✗ Hard to debug across services

MODULAR MONOLITH BOUNDARY ENFORCEMENT:

  In Java: Architectural tests (ArchUnit) enforce boundaries:

    @Test
    void ordering_should_not_depend_on_inventory_internals() {
        JavaClasses classes = new ClassFileImporter().importPackages("com.company");

        ArchRule rule = noClasses()
            .that().resideInAPackage("com.company.ordering..")
            .should().dependOnClassesThat()
            .resideInAPackage("com.company.inventory.internal..");

        rule.check(classes);
    }

  Or: Java 9 modules (module-info.java):

    // ordering/module-info.java:
    module ordering {
        exports com.company.ordering.api;      // Only this is visible to others
        // com.company.ordering.internal: NOT exported — invisible to other modules
    }

    // inventory/module-info.java:
    module inventory {
        exports com.company.inventory.api;     // Only this is visible
        requires ordering;                     // Can import ordering.api
    }

DATABASE MODULE ISOLATION:

  Option 1: Separate schemas in one database:
    schema: ordering   → tables: orders, order_items
    schema: inventory  → tables: inventory_items, stock_reservations
    schema: billing    → tables: invoices, payments

    Rule: No cross-schema JOINs in application code.
    Ordering can't: SELECT o.*, i.name FROM orders o JOIN inventory.inventory_items i...

  Option 2: Separate databases per module (stronger isolation):
    ordering_db   — separate connection pool, separate instance
    inventory_db  — separate connection pool

    Stronger isolation. Harder operational management (still one JVM).

  Why data isolation matters:
    Without data isolation: OrderService queries InventoryService's tables directly.
    This is WORSE than cross-module code imports: schema coupling without type safety.
    Data isolation forces explicit cross-module communication via module APIs.

WHEN TO CHOOSE MODULAR MONOLITH:

  PERFECT FIT:
    - Team size: 5–20 engineers.
    - Domain: well-understood, 3–8 bounded contexts.
    - Load: single deployment can handle (no massive per-module scaling needs).
    - Stage: early product (high uncertainty about what will change).
    - Plan: potentially extract microservices later (modules become service boundaries).

  CONSIDER MICROSERVICES INSTEAD:
    - Team > 50 engineers, multiple fully independent teams.
    - Proven high-load module that needs independent scaling.
    - Technology diversity required (one module needs Node.js, another Python).
    - Compliance: module must be deployed in isolated environment.
```

---

### ❓ Why Does This Exist (Why Before What)

WITHOUT Modular Monolith structure (Big Ball of Mud):

- No team ownership: every team touches every file — constant merge conflicts
- No domain clarity: business logic scattered, impossible to find where "order cancellation" is

WITHOUT jumping to Microservices:

- Network calls replace method calls → distributed transaction complexity, latency
- 10 services on day 1: operational overhead larger than team can handle

WITH Modular Monolith:
→ Domain clarity without distributed systems complexity
→ Team ownership: each module owned by one team
→ Migration path: well-defined module boundaries → extract to service when needed

---

### 🧠 Mental Model / Analogy

> An apartment building vs. separate houses vs. an open-plan office. Open-plan office (Big Ball of Mud): everyone in one space — no separation, constant noise, anyone can interrupt anyone. Separate houses (Microservices): maximum independence, but: each house needs its own utilities, mailbox, and you need a car to visit neighbors. Apartment building (Modular Monolith): separate apartments (modules), locked doors (module boundaries), shared utilities (one JVM, one deployment), easy elevator communication (in-process events). Right balance for most teams: separate space without separate utility management.

"Apartment (private space, locked door)" = module (encapsulated, private internals)
"Building intercom / elevator" = in-process events between modules
"Shared utilities (electricity, water)" = shared JVM, shared deployment
"Separate houses (separate utility bills)" = microservices (separate deployments)

---

### ⚙️ How It Works (Mechanism)

```
MODULAR MONOLITH CROSS-MODULE COMMUNICATION:

  OrderingModule publishes event:
      applicationEventPublisher.publish(new OrderPlacedEvent(orderId, items));
      │
      ├─ InventoryModule.on(OrderPlacedEvent) → reserves inventory
      └─ BillingModule.on(OrderPlacedEvent)  → creates invoice

  Or via public API:
      InventoryModule.api.checkAvailability(productId, quantity)
      // OrderingModule calls Inventory's PUBLIC API. Not internals.
```

---

### 🔄 How It Connects (Mini-Map)

```
Big Ball of Mud Monolith (single deployment, no boundaries)
        │
        ▼ (add module boundaries within single deployment)
Modular Monolith ◄──── (you are here)
(one deployment; strong module boundaries; bounded context per module)
        │
        ▼ (extract modules to separate deployments)
Microservices
(multiple deployments; network boundaries; independent scaling)
```

---

### 💻 Code Example

```java
// Module public API (only this is accessible to other modules):
package com.company.inventory.api;

public interface InventoryModule {
    InventoryAvailability checkAvailability(ProductId productId, Quantity quantity);
    ReservationResult reserve(ReservationRequest request);
}

// Cross-module DTOs (part of module API, NOT domain objects):
public record InventoryAvailability(
    ProductId productId,
    boolean inStock,
    int availableQuantity
) {}

// Module implementation (NOT accessible from other modules — private):
package com.company.inventory.internal.application;

@Service
class InventoryAvailabilityService implements InventoryModule {

    public InventoryAvailability checkAvailability(ProductId productId, Quantity qty) {
        // Internal domain logic — not visible outside module:
        InventoryItem item = inventoryRepo.findByProductId(productId).orElseThrow();
        return new InventoryAvailability(productId, item.hasStock(qty), item.availableQty());
    }
}

// Another module uses the API:
package com.company.ordering.internal.application;

@Service
class PlaceOrderService {
    private final InventoryModule inventoryModule; // Uses INTERFACE, not internal class

    void placeOrder(PlaceOrderCommand cmd) {
        // Check availability via module's public API:
        InventoryAvailability availability =
            inventoryModule.checkAvailability(cmd.productId(), cmd.quantity());

        if (!availability.inStock()) throw new OutOfStockException(cmd.productId());
        // ... rest of order placement
    }
}
```

---

### ⚠️ Common Misconceptions

| Misconception                                     | Reality                                                                                                                                                                                                                                                                                                                                                |
| ------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| Modular Monolith is just a monolith with packages | No. Packages in Java are organizational, not enforced. Modular Monolith uses enforced boundaries: Java 9 modules (module-info.java exports), ArchUnit tests, separate Maven subprojects, or package-by-module with access enforcement. The key: OTHER modules CANNOT access internals — not just "they shouldn't" but "they can't compile if they try" |
| Modular Monolith doesn't scale                    | Single deployment can scale horizontally (run 3 instances of the monolith). What it doesn't support: scaling individual modules independently. If one module needs 10x the resources of others: microservices. If the whole system scales proportionally: Modular Monolith horizontal scaling works fine                                               |
| Modular Monolith = steppingstone to microservices | Sometimes, but not always. For many organizations: Modular Monolith is the correct long-term architecture. The operational overhead of microservices is real. Not every system needs independent service deployment. If no module requires independent scaling or independent deployment: Modular Monolith may be the right permanent choice           |

---

### 🔥 Pitfalls in Production

**Module boundary violated via shared database tables:**

```java
// BAD: OrderingModule directly queries InventoryModule's table:
@Repository
class OrderRepository {
    List<OrderItemWithStock> findOrdersWithInventory() {
        // DIRECT JOIN across module boundary — couples schema:
        return entityManager.createNativeQuery(
            "SELECT o.*, i.qty_available " +
            "FROM ordering.orders o " +
            "JOIN inventory.inventory_items i ON i.product_id = o.product_id"
        ).getResultList();
        // If inventory schema changes: this query breaks.
        // OrderingModule now has schema coupling to InventoryModule.
    }
}

// FIX: Ordering only queries its own tables; gets inventory data via module API:
@Repository
class OrderRepository {
    List<Order> findAllOrders() {
        return entityManager.createQuery("SELECT o FROM Order o", Order.class)
                            .getResultList();
        // Only ordering tables. No cross-module join.
    }
}

class OrderDisplayService {
    List<OrderWithInventory> getOrdersWithInventory() {
        List<Order> orders = orderRepo.findAllOrders();
        // Get inventory info via module API (not direct DB access):
        return orders.stream().map(order -> {
            InventoryAvailability avail = inventoryModule.checkAvailability(
                order.productId(), order.quantity());
            return new OrderWithInventory(order, avail);
        }).toList();
        // Two queries instead of one JOIN — slight performance cost, correct isolation.
    }
}
```

---

### 🔗 Related Keywords

- `Bounded Context` — each module in a Modular Monolith corresponds to a bounded context
- `Microservices` — the extraction target when Modular Monolith modules need independent deployment
- `Layered Architecture` — the internal structure of each module (domain, application, infrastructure)
- `Hexagonal Architecture` — can be applied within each module for ports-and-adapters isolation
- `Domain Events` — how modules communicate asynchronously without direct coupling

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ KEY IDEA     │ One deployment with enforced module       │
│              │ boundaries. Domain clarity without        │
│              │ distributed systems complexity.           │
├──────────────┼───────────────────────────────────────────┤
│ USE WHEN     │ Small-medium team; proven domain but      │
│              │ not needing independent scaling; avoiding │
│              │ microservices operational overhead        │
├──────────────┼───────────────────────────────────────────┤
│ AVOID WHEN   │ Module genuinely needs independent scale; │
│              │ teams fully independent (different tech   │
│              │ stacks needed); compliance requires       │
│              │ deployment isolation                      │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "Apartment building: separate apartments  │
│              │  (modules), locked doors, but shared      │
│              │  utilities — no separate houses needed."  │
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ Bounded Context → Microservices →         │
│              │ Domain Events → Hexagonal Architecture    │
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** A Modular Monolith has an `orders` module and an `inventory` module. The product team requests a feature: "Show order list with real-time stock availability next to each item." The current design: Orders module queries its own tables; gets stock via `inventoryModule.checkAvailability()` per order item. For a page showing 50 orders with 5 items each: 250 individual API calls from Orders → Inventory. How do you solve this N+1 problem within a Modular Monolith WITHOUT violating module boundaries (no cross-module JOINs)?

**Q2.** Your team has a Modular Monolith that has grown to 12 modules. The `payments` module is experiencing 5x the load of other modules during flash sales — it needs to scale independently. The `auth` module has a compliance requirement to be deployed in an isolated network segment. All other 10 modules are happy in the Modular Monolith. What is the migration strategy? Do you extract ALL modules to microservices, or just the two problematic ones? How do you manage the hybrid architecture where some modules are internal (in-process) and some are external (network calls)?
