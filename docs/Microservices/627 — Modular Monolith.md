---
layout: default
title: "Modular Monolith"
parent: "Microservices"
nav_order: 627
permalink: /microservices/modular-monolith/
number: "627"
category: Microservices
difficulty: ★★☆
depends_on: "Monolith vs Microservices, Bounded Context, Domain-Driven Design (DDD)"
used_by: "Strangler Fig Pattern, Service Decomposition"
tags: #intermediate, #architecture, #microservices, #pattern
---

# 627 — Modular Monolith

`#intermediate` `#architecture` `#microservices` `#pattern`

⚡ TL;DR — A **Modular Monolith** is a single deployable unit with strong internal module boundaries enforced by the compiler or build tooling — the discipline of microservices organisation without the distributed systems overhead. It is the recommended starting point before microservices extraction.

| #627            | Category: Microservices                                                | Difficulty: ★★☆ |
| :-------------- | :--------------------------------------------------------------------- | :-------------- |
| **Depends on:** | Monolith vs Microservices, Bounded Context, Domain-Driven Design (DDD) |                 |
| **Used by:**    | Strangler Fig Pattern, Service Decomposition                           |                 |

---

### 📘 Textbook Definition

A **Modular Monolith** (also called "Majestic Monolith") is an application that is deployed as a single deployable unit but is internally divided into well-defined modules with explicit, enforced boundaries between them. Each module corresponds to a Bounded Context or business capability, owns its own domain model and data, and exposes a public API to other modules while keeping its internal implementation private. Communication between modules is strictly via public interfaces — no reaching into another module's internals. The boundaries can be enforced by Java Platform Module System (JPMS), package-private visibility, OSGi, or architectural fitness functions. A modular monolith retains the operational simplicity of a monolith (one deployment, ACID transactions, in-process calls, simple testing) while enabling the team to design, reason about, and evolve modules independently — making it a low-risk starting point and a stepping stone toward microservices extraction.

---

### 🟢 Simple Definition (Easy)

A Modular Monolith is a regular monolith application but carefully organised into distinct sections (modules), each with a clear boundary. It deploys as one app, but inside it is structured like microservices would be — without the network complexity.

---

### 🔵 Simple Definition (Elaborated)

The fundamental challenge with monoliths is accidental coupling — over time, code from different domains calls each other directly, creating a "big ball of mud." A Modular Monolith prevents this with enforced boundaries: the `orders` module can only see the `products` module's public API, not its internal classes. When a module's internals change, no other module breaks. This structure lets teams work on different modules in parallel with minimal coordination. And when a module genuinely needs to scale independently or be owned by a separate team, it can be extracted to a microservice with minimal refactoring — because its boundaries were already clean.

---

### 🔩 First Principles Explanation

**Module structure with enforced boundaries:**

```
com.example.
  ├── orders/
  │    ├── api/              ← PUBLIC: exposed to other modules
  │    │    ├── OrderService.java    (interface)
  │    │    ├── OrderRequest.java    (DTO)
  │    │    └── OrderResponse.java  (DTO)
  │    ├── internal/         ← PRIVATE: not accessible outside this module
  │    │    ├── OrderServiceImpl.java
  │    │    ├── OrderRepository.java
  │    │    └── Order.java           (domain entity)
  │    └── module-info.java
  │
  ├── products/
  │    ├── api/
  │    │    └── ProductCatalogApi.java   (interface)
  │    └── internal/
  │         └── ProductCatalogImpl.java
  │
  └── payments/
       ├── api/
       │    └── PaymentService.java
       └── internal/
            └── PaymentServiceImpl.java

module-info.java (orders module):
  module com.example.orders {
      requires com.example.products; // explicit dependency declaration
      exports com.example.orders.api; // ONLY the api package is visible
      // com.example.orders.internal is NOT exported → compiler error if accessed
  }
```

**Three enforcement mechanisms:**

```
1. JAVA PLATFORM MODULE SYSTEM (JPMS):
   module-info.java declares requires/exports
   → JVM enforces at compile time AND runtime
   → Cannot even reflect into unexported packages (strong encapsulation)

2. PACKAGE-PRIVATE + ARCHITECTURE FITNESS FUNCTIONS:
   Mark internal classes package-private
   Add ArchUnit tests that fail if cross-module access is detected:
     @Test
     void modulesShouldNotHaveCircularDependencies() {
         JavaClasses classes = new ClassFileImporter().importPackages("com.example");
         SlicesRuleDefinition.slices().matching("com.example.(*)..")
             .should().beFreeOfCycles()
             .check(classes);
     }

3. SEPARATE MAVEN/GRADLE MODULES:
   pom.xml:
     <modules>
       <module>orders-api</module>
       <module>orders-internal</module>
       <module>products-api</module>
     </modules>
   orders-internal depends on orders-api and products-api ONLY
   → other modules cannot declare dependency on orders-internal
```

**Module communication patterns:**

```
DIRECT CALL (synchronous, in-process):
  // orders module calls products via public API
  Product p = productApi.findById(req.getProductId());
  // One JVM → no serialisation, no network, no failure modes
  // Pros: simple, fast, testable without mocks
  // Cons: caller blocked during call (but microseconds, not milliseconds)

DOMAIN EVENT (in-process async via ApplicationEventPublisher):
  // orders module publishes an event
  eventPublisher.publishEvent(new OrderPlacedEvent(order.getId()));
  // inventory module listens without orders knowing about inventory
  @EventListener
  void onOrderPlaced(OrderPlacedEvent event) { ... }
  // Pros: decoupled — orders doesn't know about inventory module
  // Cons: no return value, harder to trace event flow

WHEN EXTRACTING TO MICROSERVICES:
  Direct call → HTTP/REST or gRPC call
  Domain event → Kafka/RabbitMQ message
  Shared data → database per service with data replication
  The boundary design is identical — only the transport changes
```

---

### ❓ Why Does This Exist (Why Before What)

WITHOUT a modular monolith discipline:

What breaks without it:

1. Monolith becomes a "big ball of mud" — everything calls everything, impossible to extract to microservices without a full rewrite.
2. Module A's database schema changes break module B's queries (no data isolation).
3. Teams constantly conflict on shared code, making independent work impossible.
4. Testability degrades — testing the "order service" requires instantiating the full application context.

WITH a modular monolith:
→ Clean boundaries make extraction to microservices a transport-layer change, not a domain redesign.
→ Each module can have its own schema tables — logically isolated even if physically in one database.
→ Teams can work on separate modules with minimal coordination.
→ Modules are independently testable with small, fast unit tests.

---

### 🧠 Mental Model / Analogy

> A Modular Monolith is like a well-organised office with clearly marked departments. Everyone works in the same building (one deployment), but the Sales department has its own files, its own processes, and its own manager. HR cannot access Sales' client database directly — they submit a request through the official inter-department channel (public module API). When the company grows and Sales becomes a subsidiary (extracted microservice), the hand-off is smooth: the official channels are already defined. An unmodular monolith is an office where everyone shares one big desk and anyone can read anyone else's files — quick to start but chaotic at scale.

"Same building" = single deployable unit (one JVM process)
"Clearly marked departments" = modules with enforced boundaries
"Official inter-department channel" = public module API
"Subsidiary" = extracted microservice
"Everyone sharing one big desk" = unmodular monolith ("big ball of mud")

---

### ⚙️ How It Works (Mechanism)

**Logical data isolation within one database:**

```sql
-- Each module has its own schema (or table prefix)
-- orders module tables:
CREATE TABLE orders.order_header (id BIGINT PRIMARY KEY, ...);
CREATE TABLE orders.order_item   (id BIGINT PRIMARY KEY, order_id BIGINT REFERENCES orders.order_header, ...);

-- products module tables:
CREATE TABLE products.product (id BIGINT PRIMARY KEY, ...);

-- RULE: orders module code only queries orders.* tables
-- If orders needs product info → call ProductCatalogApi (not direct SELECT on products.product)
-- When extracting to microservices:
--   Move orders.* tables to orders-db
--   Move products.* tables to products-db
--   Replace ProductCatalogApi in-process call with HTTP call to ProductService
```

---

### 🔄 How It Connects (Mini-Map)

```
Monolith vs Microservices
        │
        ▼
Modular Monolith  ◄──── (you are here)
(single deployment + enforced module boundaries)
        │
        ├── Bounded Context  → each module = one bounded context
        ├── DDD              → module internals follow DDD aggregate design
        ├── Strangler Fig    → extract individual modules to microservices over time
        └── Service Decomposition → module boundaries inform service boundaries
```

---

### 💻 Code Example

**ArchUnit test enforcing no cross-module internal access:**

```java
@AnalyzeClasses(packages = "com.example")
class ModularBoundaryTest {

    @ArchTest
    static final ArchRule ordersCannotAccessProductsInternals =
        noClasses().that().resideInAPackage("com.example.orders..")
            .should().accessClassesThat()
            .resideInAPackage("com.example.products.internal..");

    @ArchTest
    static final ArchRule noCyclicModuleDependencies =
        SlicesRuleDefinition.slices()
            .matching("com.example.(*)..")
            .should().beFreeOfCycles();

    @ArchTest
    static final ArchRule internalPackagesMustBePrivate =
        classes().that().resideInAPackage("..internal..")
            .should().bePackagePrivate()
            .orShould().bePrivate();
}
```

---

### ⚠️ Common Misconceptions

| Misconception                                                                               | Reality                                                                                                                                                                                                                            |
| ------------------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| A modular monolith is just a "better-organised monolith" with no architectural significance | A properly bounded modular monolith is functionally equivalent to microservices in terms of domain isolation — the only difference is deployment and transport. The boundary design work is the hard part; transport is mechanical |
| Modules in a modular monolith must share one database schema                                | Modules should have logical data isolation — separate schemas, table prefixes, or at minimum never querying each other's tables directly. Physical co-location in one database is fine; logical mixing is a boundary violation     |
| Modular monolith means you cannot use microservices later                                   | The opposite: a clean modular monolith is the best preparation for microservices. Modules with clear APIs extract cleanly. An unmodular monolith requires a full rewrite to extract any service                                    |
| JPMS (Java modules) is required to build a modular monolith                                 | JPMS provides the strongest enforcement but is complex to adopt. ArchUnit tests, package-private visibility, and Maven multi-module builds are equally effective and far easier to introduce incrementally                         |

---

### 🔥 Pitfalls in Production

**"Let me just quickly access that internal class" — boundary erosion**

```java
// The single most common modular monolith failure:
// Developer in orders module finds a useful utility in products.internal
import com.example.products.internal.ProductPricingEngine; // VIOLATION

class OrderPricingCalculator {
    @Autowired
    ProductPricingEngine pricingEngine; // reached into another module's internals

    // Now: orders module is coupled to products module's implementation
    // Consequence: if ProductPricingEngine changes, OrderPricingCalculator breaks
    // Consequence: cannot extract products module without also changing orders
}

// THE FIX: expose via public API
// In products.api package:
public interface ProductPricingApi {
    BigDecimal calculatePrice(Long productId, int quantity);
}

// In orders module:
import com.example.products.api.ProductPricingApi; // CORRECT
```

---

### 🔗 Related Keywords

- `Monolith vs Microservices` — the architectural choice that modular monolith bridges
- `Bounded Context` — each module = one bounded context with its own domain model
- `Domain-Driven Design (DDD)` — the design approach that informs module boundaries
- `Strangler Fig Pattern` — uses clean module boundaries to extract services incrementally
- `Service Decomposition` — deciding which modules to extract first as microservices

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ DEFINITION   │ Single deployment + enforced module       │
│              │ boundaries per bounded context            │
├──────────────┼───────────────────────────────────────────┤
│ ENFORCEMENT  │ JPMS module-info.java                     │
│              │ Maven multi-module + package-private      │
│              │ ArchUnit boundary tests                   │
├──────────────┼───────────────────────────────────────────┤
│ BENEFIT      │ Microservices discipline, monolith ops   │
│ VS MICRO     │ In-process calls, ACID txns, simple tests │
├──────────────┼───────────────────────────────────────────┤
│ EXTRACTION   │ Module → Microservice = transport change  │
│              │ (API already defined, data already iso'd) │
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** A modular monolith with logical data isolation (separate DB schemas per module) uses ACID transactions for cross-module operations — `orderRepo.save()` and `inventoryRepo.decrementStock()` in one `@Transactional` method are both in the same database. When this monolith is extracted to microservices with separate databases, that `@Transactional` boundary is broken — you cannot have a single ACID transaction across two databases. Describe the exact steps required to convert a `@Transactional` cross-module operation into a Saga pattern, identifying what consistency guarantees change.

**Q2.** The Modular Monolith's in-process event system (`ApplicationEventPublisher`) becomes a message broker (Kafka/RabbitMQ) when modules are extracted to microservices. Describe the semantics that change: in-process `publishEvent()` is synchronous by default (`@EventListener`) — the publisher waits for all listeners before proceeding. In Kafka, the publisher gets an acknowledgement from the broker, not from the consumers. How does this change the failure and consistency semantics? And what does `@TransactionalEventListener` (publish event only after the outer transaction commits) enable that is not possible in a Kafka-based system without the outbox pattern?
