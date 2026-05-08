---
layout: default
title: "Modular Monolith Patterns"
parent: "Software Architecture Patterns"
grand_parent: "Technical Dictionary"
nav_order: 39
permalink: /software-architecture/modular-monolith-patterns/
id: SAP-039
category: Software Architecture Patterns
difficulty: ★★★
depends_on: Bounded Context, Layered Architecture, Domain Model, Monolith vs Microservices
used_by: Medium-scale applications, Microservices migration, Teams choosing architecture
related: Microservices, Layered Architecture, Bounded Context, Vertical Slice Architecture
tags:
  - architecture
  - pattern
  - deep-dive
  - modular
  - advanced
---

# SAP-039 - Modular Monolith Patterns

⚡ TL;DR - A Modular Monolith structures a single deployable application into strong, isolated domain modules with explicit boundaries - combining the deployment simplicity of a monolith with the code organization principles of microservices.

---

### 📊 Entry Metadata

| #752            | Category: Software Architecture Patterns                                          | Difficulty: ★★★ |
| :-------------- | :-------------------------------------------------------------------------------- | :-------------- |
| **Depends on:** | Bounded Context, Layered Architecture, Domain Model, Monolith vs Microservices    |                 |
| **Used by:**    | Medium-scale applications, Microservices migration, Teams choosing architecture   |                 |
| **Related:**    | Microservices, Layered Architecture, Bounded Context, Vertical Slice Architecture |                 |

---

### 🔥 The Problem This Solves

**THE FALSE DICHOTOMY:**
"We need to scale our architecture - let's go microservices." But the team is 8 developers. The domain is still being understood. Microservices now means managing 12 separate deployments, distributed transactions, network failures between services, distributed tracing, and separate CI/CD pipelines for each service. The operational complexity overwhelms the development value.

**THE SPAGHETTI MONOLITH:**
Alternatively: stay in the monolith but let it become a tangle of cross-cutting imports. `OrderService` imports from `InventoryRepository` directly. `BillingService` imports from `OrderDomainObject`. Everything knows about everything. Refactoring anything becomes a maze.

**THE MODULAR MONOLITH SOLUTION:**
Single deployment, but with rigorous internal module boundaries. Each module owns its own domain model, its own persistence, and its own public API. Cross-module communication goes through the public API only - never via direct class imports across module boundaries. Get the code organization benefits of microservices without the operational overhead.

---

### 📘 Textbook Definition

A Modular Monolith is an architectural style where a single deployable application unit is internally organized into well-defined, isolated modules, each representing a distinct Bounded Context or domain area. Each module has explicit boundaries, a documented public API, and encapsulated internal implementation. Modules communicate through their public interfaces, not through shared internal classes. The Modular Monolith is sometimes described as the ideal first architecture for a new system - it provides clear organizational boundaries that can be extracted into microservices if and when that's warranted, without the premature operational complexity.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
One deployable unit, but internally organized like microservices - strong module boundaries, public APIs between modules.

**One analogy:**

> An office building where departments have assigned floors and you must go through the reception desk to visit another department. You're all in the same building (monolith), but access between departments is controlled and formalized. You don't wander through Finance's open-plan area to get to Legal - you have a meeting through proper channels. The modules are the departments; the public module APIs are the reception desks.

**One insight:**
A well-structured Modular Monolith is easier to extract into microservices than a poorly structured one. The module boundaries in the monolith become the service boundaries in microservices. If you can't identify where one module ends and another begins in your monolith, you won't be able to split it into services either.

---

### 🔩 First Principles Explanation

**MODULAR MONOLITH VS ALTERNATIVES:**

```
┌──────────────────────────────────────────────────────────┐
│         ARCHITECTURE OPTION COMPARISON                   │
├──────────────────────────────────────────────────────────┤
│                                                          │
│  Big Ball of Mud (Monolith, no structure):               │
│    Deploy: 1 unit  Module isolation: none                │
│    Team scale: breaks at ~5 devs                         │
│    Ops complexity: low                                   │
│                                                          │
│  Modular Monolith:                                       │
│    Deploy: 1 unit  Module isolation: explicit            │
│    Team scale: works well at 10-50 devs                  │
│    Ops complexity: low                                   │
│                                                          │
│  Microservices:                                          │
│    Deploy: N units Module isolation: physical            │
│    Team scale: designed for 50+ devs, many teams         │
│    Ops complexity: high                                  │
│                                                          │
│  Sweet spot for Modular Monolith:                        │
│    5-50 developers, domain still evolving,               │
│    team doesn't yet need independent deployment          │
└──────────────────────────────────────────────────────────┘
```

**ENFORCING MODULE BOUNDARIES:**

```
┌──────────────────────────────────────────────────────────┐
│          BOUNDARY ENFORCEMENT TECHNIQUES                 │
├──────────────────────────────────────────────────────────┤
│                                                          │
│  Technique 1: Java modules (JPMS)                        │
│    module-info.java declares what is exported            │
│    Compiler enforces: only exported packages accessible  │
│    Strongest enforcement - compile-time                  │
│                                                          │
│  Technique 2: Separate Maven/Gradle modules              │
│    Each module is a JAR                                  │
│    Dependencies must be explicit in build files          │
│    Good enforcement - build-time                         │
│                                                          │
│  Technique 3: ArchUnit rules                             │
│    Architecture tests enforce package dependencies       │
│    Fails build if module A directly imports module B     │
│    Test-time enforcement - catches violations in CI      │
│                                                          │
│  Technique 4: Package-by-module convention               │
│    Weakest - depends on team discipline                  │
│    Package: com.acme.orders, com.acme.inventory          │
│    No compile-time enforcement                           │
└──────────────────────────────────────────────────────────┘
```

---

### 🧪 Thought Experiment

**BEFORE MODULAR MONOLITH (spaghetti monolith):**

```java
// OrderService directly imports from multiple modules
import com.acme.inventory.InventoryRepository;
import com.acme.billing.PaymentRecord;
import com.acme.customers.CustomerEntity;
import com.acme.shipping.ShipmentStatus;

// Any change to InventoryRepository potentially breaks this
// Cannot move Inventory to a separate service without
// finding all these implicit dependencies first
```

**AFTER MODULAR MONOLITH:**

```java
// Orders module only knows about its own domain
// + the public API of other modules
import com.acme.orders.domain.Order;
import com.acme.inventory.api.InventoryService;  // public API
import com.acme.inventory.api.StockLevel;       // public API DTO

// InventoryService is an interface - not the implementation
// Can be replaced by an HTTP client to a separate service
// with zero change to the Orders module
```

---

### 🧠 Mental Model / Analogy

> A Modular Monolith is like a body: one organism, but made of separate organs. The liver knows nothing about the kidney's internal structure - it interacts with the kidney through the bloodstream (the public API). You can study, modify, and even (in extreme cases) transplant an organ without knowing the implementation details of all other organs. The organ boundaries are real even though the body is one unit.

---

### 📶 Gradual Depth - Four Levels

**Level 1 - What it is (anyone):**
One application, but internally divided into isolated sections. Each section only talks to other sections through a formal, documented interface - not by directly reaching into the other section's code.

**Level 2 - How to structure it (junior):**
Package your code by module (domain area), not by layer (controllers in one package, services in another). Each module has: a `domain` package (private), an `application` package (private), an `infrastructure` package (private), and an `api` package (public - the only part other modules can import). Use ArchUnit to enforce that `com.acme.orders` cannot import from `com.acme.inventory` except via `com.acme.inventory.api`.

**Level 3 - Cross-module communication (mid-level):**
Three options for cross-module communication:

1. **Synchronous method call via interface**: `InventoryService.checkStock(productId)` - simple, direct, but creates synchronous dependency.
2. **In-process event bus**: Orders publishes `OrderPlacedEvent` to Spring's `ApplicationEventPublisher`; Inventory listens. Decoupled but still in-process.
3. **Shared database tables**: modules have their own schema namespaces; a view provides read access across modules. Simple but creates data coupling.

**Level 4 - Migration to microservices (senior/staff):**
The Modular Monolith is the ideal preparation for microservices. When a module needs independent scaling, deployment, or technology stack, extract it as a service. The extraction path: 1) Ensure all module communication goes through the public API (already done). 2) Replace the direct method call to `InventoryService.checkStock()` with an HTTP client calling the now-separate inventory service. 3) Replace in-process events with Kafka messages. The module's public API becomes the service's HTTP/messaging API. Teams that skip the Modular Monolith phase and jump to microservices often find their "microservices" are actually tightly coupled distributed monoliths that are harder to change than a well-structured monolith.

---

### ⚙️ How It Works (Mechanism)

**Module structure:**

```
┌──────────────────────────────────────────────────────────┐
│         MODULAR MONOLITH - DIRECTORY STRUCTURE           │
├──────────────────────────────────────────────────────────┤
│                                                          │
│  src/main/java/com/acme/                                 │
│  ├── orders/                  ← Orders Module            │
│  │   ├── api/                 ← PUBLIC (other modules)   │
│  │   │   ├── OrdersModule.java                           │
│  │   │   ├── PlaceOrderCommand.java                      │
│  │   │   ├── OrderSummaryDto.java                        │
│  │   │   └── events/                                     │
│  │   │       └── OrderPlacedEvent.java                   │
│  │   ├── domain/              ← PRIVATE                  │
│  │   │   ├── Order.java                                  │
│  │   │   ├── OrderItem.java                              │
│  │   │   └── OrderRepository.java (interface)            │
│  │   ├── application/         ← PRIVATE                  │
│  │   │   └── OrderApplicationService.java                │
│  │   └── infrastructure/      ← PRIVATE                  │
│  │       └── JpaOrderRepository.java                     │
│  │                                                       │
│  ├── inventory/               ← Inventory Module         │
│  │   ├── api/                 ← PUBLIC                   │
│  │   │   ├── InventoryModule.java                        │
│  │   │   └── InventoryService.java (interface)           │
│  │   ├── domain/              ← PRIVATE                  │
│  │   └── ...                                             │
│  │                                                       │
│  └── billing/                 ← Billing Module           │
│      └── ...                                             │
└──────────────────────────────────────────────────────────┘
```

---

### 🔄 The Complete Picture

**ArchUnit enforcement of module boundaries:**

```
┌──────────────────────────────────────────────────────────┐
│       ARCHUNIT RULES - BOUNDARY ENFORCEMENT              │
├──────────────────────────────────────────────────────────┤
│                                                          │
│  Test: Orders module may only access Inventory           │
│  via the Inventory module's public API                   │
│                                                          │
│  @ArchTest                                               │
│  static ArchRule orders_only_uses_inventory_api =        │
│    classes()                                             │
│      .that().resideInAPackage("..orders..")              │
│      .should().onlyAccessClassesThat()                   │
│        .resideInAnyPackage(                              │
│          "..orders..",       // own module               │
│          "..inventory.api..", // inventory public API    │
│          "java..",           // JDK                      │
│          "org.springframework.." // framework            │
│        );                                                │
│                                                          │
│  This test FAILS if orders module directly imports:      │
│  com.acme.inventory.domain.StockLevel (private!)         │
└──────────────────────────────────────────────────────────┘
```

---

### 💻 Code Example

**Module API definition:**

```java
// inventory/api/InventoryService.java - the module's public API
// This is the ONLY thing the Orders module imports from Inventory
public interface InventoryService {
    StockCheckResult checkStock(String productId, int qty);
    ReservationId reserveStock(String productId,
                                int qty,
                                String orderId);
    void releaseStock(ReservationId reservationId);
}

// The implementation is in inventory/application/ - PRIVATE
@Service
class InventoryApplicationServiceImpl
        implements InventoryService {
    // Orders module cannot see this class
    // Orders module only knows InventoryService (interface)
    ...
}

// Cross-module configuration - wiring the interface
@Configuration
class ModuleConfiguration {
    // Spring DI connects the interface to the implementation
    // If Inventory moves to separate service: swap implementation
    // with InventoryServiceHttpClient - zero changes in orders module
    @Bean
    public InventoryService inventoryService(
            InventoryApplicationServiceImpl impl) {
        return impl;
    }
}
```

---

### ⚖️ Comparison Table

| Aspect                         | Modular Monolith         | Big Ball of Mud | Microservices      |
| ------------------------------ | ------------------------ | --------------- | ------------------ |
| Deployment complexity          | Low (1 deploy)           | Low             | High (N deploys)   |
| Module boundary enforcement    | Explicit (ArchUnit/JPMS) | None            | Physical (network) |
| Team independence              | Moderate                 | None            | High               |
| Distributed systems complexity | None                     | None            | High               |
| Good first choice              | Yes                      | No              | Rarely             |
| Microservices migration path   | Clear                    | Very difficult  | N/A                |

---

### ⚠️ Common Misconceptions

| Misconception                                                | Reality                                                                                                               |
| ------------------------------------------------------------ | --------------------------------------------------------------------------------------------------------------------- |
| Monolith = bad; microservices = good                         | Monolith is a deployment model; good/bad depends on team size, domain maturity, and organizational needs              |
| Modular Monolith is a compromise                             | Modular Monolith is often the optimal architecture for medium-scale teams - not a stepping stone                      |
| Once you have a modular monolith, you need microservices     | Many successful, large-scale applications are well-structured monoliths (Shopify ran as a monolith at enormous scale) |
| Module boundaries need to be microservice-ready from day one | Start with clean module boundaries; decide on microservices extraction when there's a real operational need           |

---

### 🚨 Failure Modes & Diagnosis

**Silent boundary violations**

**Symptom:** Module A directly instantiates classes from Module B's private packages. No build failures, but any internal change to Module B breaks Module A.

**Root Cause:** No enforcement mechanism for module boundaries.

**Fix:** Add ArchUnit tests. Better: move to separate Maven/Gradle modules so the build fails on unauthorized imports.

---

### 🔗 Related Keywords

**Prerequisites:**

- `Bounded Context` - the domain concept that modules map to
- `Layered Architecture` - contrasts with module-first organization

**Related:**

- `Microservices` - the architecture style modules can be extracted into
- `Vertical Slice Architecture` - alternative module organization by feature

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ WHAT IT IS   │ Single deployment, microservice-like     │
│              │ internal module boundaries               │
├──────────────┼───────────────────────────────────────────┤
│ KEY RULE     │ Cross-module access via public API only  │
├──────────────┼───────────────────────────────────────────┤
│ ENFORCE WITH │ ArchUnit, JPMS, separate Maven modules   │
├──────────────┼───────────────────────────────────────────┤
│ USE WHEN     │ 5-50 devs; domain evolving; no need for  │
│              │ independent deployment yet               │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "One building, separate departments with  │
│              │  formal reception desks"                  │
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** Your Modular Monolith has an `Orders` module and an `Inventory` module that communicate through a public interface. The `Orders` module calls `InventoryService.reserveStock()` synchronously during `order.submit()`. This call is slow (50ms) and occasionally times out. How do you redesign the cross-module communication to make order submission resilient to inventory service slowness, while still ensuring stock is reserved before the order is confirmed?

**Q2.** You've built a Modular Monolith with 8 modules. The `Orders` module is now handling 10x the traffic of other modules and needs to scale independently - something a monolith deployment can't do per-module. What is the extraction path to make Orders a separate microservice, and what specifically needs to change in the remaining monolith when Orders is extracted?
