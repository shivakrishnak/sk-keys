---
id: SAP-039
title: Modular Monolith Patterns
category: Software Architecture Patterns
tier: tier-5-distributed-architecture
folder: SAP-software-architecture
difficulty: ★★★
depends_on: SAP-013, SAP-050, SAP-051
used_by:
related: SAP-011, SAP-012, SAP-040
tags:
  - architecture
  - pattern
  - deep-dive
status: complete
version: 1
layout: default
parent: "Software Architecture Patterns"
grand_parent: "Technical Dictionary"
nav_order: 39
permalink: /software-architecture/modular-monolith-patterns/
  - advanced
---

# SAP-039 - Modular Monolith Patterns

⚡ TL;DR - A Modular Monolith structures a single deployable application into strong, isolated domain modules with explicit boundaries - combining the deployment simplicity of a monolith with the code organization principles of microservices.

| Field          | Value                     |
| -------------- | ------------------------- |
| **Depends on** | SAP-013, SAP-050, SAP-051 |
| **Used by**    | -                         |
| **Related**    | SAP-011, SAP-012, SAP-040 |

---

### 🔥 The Problem This Solves

**THE FALSE DICHOTOMY:**
"We need to scale our architecture - let's go microservices." But the team is 8 developers. The domain is still being understood. Microservices now means managing 12 separate deployments, distributed transactions, network failures between services, distributed tracing, and separate CI/CD pipelines for each service. The operational complexity overwhelms the development value.

**THE SPAGHETTI MONOLITH:**
Alternatively: stay in the monolith but let it become a tangle of cross-cutting imports. `OrderService` imports from `InventoryRepository` directly. `BillingService` imports from `OrderDomainObject`. Everything knows about everything. Refactoring anything becomes a maze.

**THE MODULAR MONOLITH SOLUTION:**
Single deployment, but with rigorous internal module boundaries. Each module owns its own domain model, its own persistence, and its own public API. Cross-module communication goes through the public API only - never via direct class imports across module boundaries. Get the code organization benefits of microservices without the operational overhead.

**EVOLUTION:**
The Modular Monolith concept existed informally as good software engineering practice (cohesion and coupling principles) long before microservices. The pattern became explicitly named and advocated by Simon Brown ("Software Architecture for Developers," 2014) as a corrective to the microservices hype. Sam Newman's "Monolith to Microservices" (2019) further validated it as the recommended STARTING architecture before considering microservices. Shopify's 2019 blog post on their modular monolith gave it mainstream credibility. Today, Java's Java Platform Module System (JPMS, Java 9+) provides compile-time enforcement of module boundaries, and frameworks like Spring Modulith (2023) provide runtime enforcement and test support.

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

### 💎 Transferable Wisdom

**Reusable Engineering Principle:** Enforce module boundaries at the code level, not just through team conventions. If the boundary can be bypassed by any developer who imports a class directly, it will eventually be bypassed. Code enforcement (package access rules, module system constraints) is stronger than documentation enforcement.

**Where else this pattern appears:**

- **Departmental budgets:** A company operates as a single organization (monolith) but enforces department-level budget accountability. Each department has its own budget, its own P&L, and cross-department requests go through formal approval channels, not informal hallway requests.
- **Microkernel operating systems:** The OS kernel provides core services (the monolith), but device drivers and filesystem implementations are separate modules loaded at runtime. The kernel boundary is enforced by the privilege level of the CPU - modules can't bypass it.
- **Java Platform Module System (JPMS):** Java 9+ enforces module boundaries at compile time and runtime - a class in a module cannot be accessed by code outside the module unless explicitly exported. This is module boundary enforcement at the language/runtime level.

---

### 💡 The Surprising Truth

The Modular Monolith is often the correct FINAL architecture for a product, not just a stepping stone to microservices. For many teams and products, microservices introduce distributed systems complexity (network failures, distributed transactions, operational overhead) that exceeds the benefit of independent deployability. Shopify runs a large portion of its commerce platform as a modular monolith ("Majestic Monolith") and has explicitly chosen NOT to fully migrate to microservices for many of its core services. The assumption that microservices are always the maturity destination - and that Modular Monolith is a temporary state - is wrong. Modular Monolith may be the permanent destination for many products.

---

### �🔗 Related Keywords

**Prerequisites (understand these first):**

- SAP-013 - Layered Architecture (modular monolith is an evolution of layered architecture where the horizontal layers are replaced by vertical modules with their own layers)
- SAP-050 - Cohesion and SAP-051 - Coupling (the principles that define module boundaries; high cohesion within modules, low coupling between modules)

**Builds On This (learn these next):**

- SAP-011 - Loose Coupling of Frontend Modules (the frontend equivalent of Modular Monolith; same principles applied to JavaScript/TypeScript frontend module organization)
- SAP-012 - Micro-Frontend Architecture (the distributed form of Modular Monolith for frontends; understanding Modular Monolith first helps avoid premature micro-frontend adoption)
- SAP-040 - Plugin Architecture (a way to extend the modular monolith without modifying core modules)

**Alternatives / Comparisons:**

- Microservices (distributed form; same bounded context boundaries but separate deployment units; appropriate when independent scalability, technology choice, or team autonomy justifies the operational overhead)
- SAP-017 - Vertical Slice Architecture (complementary; vertical slices are an internal organization pattern within each module of a modular monolith)

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

_Hint:_ Research the "Saga" pattern applied to in-process module communication - specifically the "eventual consistency within a monolith" approach where `Orders` publishes an `OrderSubmitted` in-process event, and `Inventory` subscribes and reserves stock asynchronously. The order is placed in "pending" state; it moves to "confirmed" when inventory reservation succeeds. Research Spring Modulith's `@ApplicationModuleListener` which delivers events asynchronously between modules while maintaining transactional guarantees.

**Q2.** You've built a Modular Monolith with 8 modules. The `Orders` module is now handling 10x the traffic of other modules and needs to scale independently - something a monolith deployment can't do per-module. What is the extraction path to make Orders a separate microservice, and what specifically needs to change in the remaining monolith when Orders is extracted?

_Hint:_ Research the "Strangler Fig" pattern for module extraction and specifically: what changes when Orders becomes a separate service? (1) Cross-module interface calls become HTTP/gRPC calls or events; (2) Shared database tables must be split (Orders gets its own DB schema); (3) Cross-module transactions become Sagas; (4) The remaining monolith modules that depended on `OrdersModule` now depend on an `OrdersClient` ACL. Research how the modular monolith's clean boundaries make this extraction 10x easier than extracting from a spaghetti monolith.

**Q3.** A team is starting a new greenfield project. Should they start with a Modular Monolith or Microservices? What decision criteria should guide this choice, and how do you design the system to keep the eventual migration to microservices cheap if it becomes necessary?

_Hint:_ Research Sam Newman's "When to use Microservices" decision framework from "Monolith to Microservices" (2019) - specifically the three scenarios where microservices are justified from day one: (1) you need different technology stacks per service, (2) you need independent scaling by service, (3) you have independent teams who own separate services. For all other cases, start with Modular Monolith. The key design decision that keeps migration cheap: ensure module-to-module communication uses only in-process interfaces (no direct DB access across modules), so extraction only requires replacing those interfaces with HTTP clients.
