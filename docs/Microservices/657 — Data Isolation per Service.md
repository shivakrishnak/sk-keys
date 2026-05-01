---
layout: default
title: "Data Isolation per Service"
parent: "Microservices"
nav_order: 657
permalink: /microservices/data-isolation-per-service/
number: "657"
category: Microservices
difficulty: ★★★
depends_on: "Database per Service, Microservices Architecture"
used_on: "Eventual Consistency (Microservices), CQRS in Microservices, Shared Database Anti-Pattern"
tags: #advanced, #microservices, #distributed, #database, #architecture, #pattern
---

# 657 — Data Isolation per Service

`#advanced` `#microservices` `#distributed` `#database` `#architecture` `#pattern`

⚡ TL;DR — **Data Isolation per Service** means each microservice owns its data exclusively — no other service can read from or write to its database directly. All data access goes through the service's public API or published events. This enforces true loose coupling and enables services to evolve their data models independently.

| #657            | Category: Microservices                                                                   | Difficulty: ★★★ |
| :-------------- | :---------------------------------------------------------------------------------------- | :-------------- |
| **Depends on:** | Database per Service, Microservices Architecture                                          |                 |
| **Used by:**    | Eventual Consistency (Microservices), CQRS in Microservices, Shared Database Anti-Pattern |                 |

---

### 📘 Textbook Definition

**Data Isolation per Service** (also called **Data Sovereignty** or **Data Encapsulation**) is a microservices principle stating that each service is the sole owner and authority over its data store. Other services cannot directly query or mutate a service's data — they must invoke the owning service's API (synchronous) or react to its published events (asynchronous). This is the logical extension of the **Database per Service** pattern: not only does each service have its own physical database, but data ownership boundaries are strictly enforced in code and architecture. The principle prevents the most common microservices anti-pattern: services sharing a database and executing JOINs across service boundaries. Data isolation enables: independent schema evolution (service A can change its schema without affecting service B), independent technology choice (service A: PostgreSQL, service B: Cassandra), independent scaling of storage, and clear bounded contexts aligned with domain-driven design (DDD).

---

### 🟢 Simple Definition (Easy)

Each service has its own private data. Other services cannot peek into it directly — they must ask through the API or listen to events. Like each department having locked filing cabinets: if you need someone's data, you ask them, they give you what you're authorized to see. You can't walk into their office and read their files yourself.

---

### 🔵 Simple Definition (Elaborated)

`CustomerService` owns customer data (`name`, `email`, `credit_limit`). `OrderService` needs to display customer name on an order. Wrong approach: `SELECT name FROM CustomerService.customers WHERE id = ?` (direct DB access). Right approach: `GET /customers/{id}` (API call) or subscribe to `CustomerUpdated` events and maintain a local projection. Why does it matter? If `CustomerService` renames its `name` column to `full_name`, the direct DB query breaks silently at runtime. With API access, `CustomerService` controls what it exposes, and clients are shielded from internal schema changes.

---

### 🔩 First Principles Explanation

**Levels of data isolation — from weakest to strictest:**

```
LEVEL 0 — Shared Database, Shared Schema (monolith or worst-case microservices):
  All services: same DB, same schema, JOINs freely across tables
  Services write directly to each other's tables
  Zero isolation: change one table → potentially breaks every service
  This is the Shared Database Anti-Pattern.

LEVEL 1 — Shared Database, Separate Schemas:
  Same PostgreSQL instance
  OrderService → schema: "order_schema"
  CustomerService → schema: "customer_schema"
  Access control: OrderService DB user has no GRANT on customer_schema
  No JOINs across schemas (enforced by permissions)
  Still: same database instance → resource contention, shared failure domain
  Transitional state (monolith decomposition in progress)

LEVEL 2 — Separate Databases, Same Technology:
  OrderService → PostgreSQL instance A
  CustomerService → PostgreSQL instance B
  Physical separation: no shared resources, no cross-DB JOINs possible (cross-DB queries require federated query engines or application-level joins)
  Different team can scale, upgrade, tune their DB independently

LEVEL 3 — Separate Databases, Technology Freedom:
  OrderService → PostgreSQL (relational, ACID writes)
  CustomerService → DynamoDB (key-value, high throughput reads)
  InventoryService → Redis (in-memory, ultra-fast stock lookups)
  AnalyticsService → ClickHouse (columnar, aggregation queries)
  Each service uses the RIGHT database for its access patterns
  No technology lock-in across the organisation

LEVEL 4 — Full Data Sovereignty (strictest):
  Level 3 + enforcement: no service-to-service DB credentials shared
  All data access via API or events
  Even reporting/analytics: cannot JOIN across production service DBs
  Separate reporting DB populated by events (CQRS projections)
  Auditing: all data access logged through service API
```

**Enforcing data isolation — practical mechanisms:**

```java
// ❌ VIOLATION: OrderService directly queries CustomerService's DB:
// (even if technically possible via shared DB user)
@Repository
interface CustomerDatabaseRepository extends JpaRepository<CustomerEntity, Long> {
    // OrderService should NOT have this — it accesses CustomerService's data store directly
    @Query("SELECT c FROM CustomerEntity c WHERE c.id = :customerId")
    Optional<CustomerEntity> findCustomerById(@Param("customerId") Long customerId);
}

// ✅ CORRECT: OrderService calls CustomerService API:
@Service
class CustomerClient {
    private final RestTemplate restTemplate;

    public CustomerDTO getCustomer(Long customerId) {
        return restTemplate.getForObject(
            "http://customer-service/api/v1/customers/{id}",
            CustomerDTO.class,
            customerId
        );
    }
}

// ✅ CORRECT: OrderService maintains local projection from events:
@KafkaListener(topics = "customer-updated-events", groupId = "order-service-customer-projection")
void updateCustomerProjection(CustomerUpdatedEvent event) {
    customerProjectionRepository.save(new CustomerProjection(
        event.getCustomerId(),
        event.getFullName(),    // local copy of only the fields OrderService needs
        event.getTier()         // customer tier needed for order discounts
        // NOTE: OrderService doesn't store email, address, etc. — not its concern
    ));
}
```

**Reporting across service boundaries — the cross-service query problem:**

```
BUSINESS REQUIREMENT:
  "Show me all orders this month with customer name, product name, and payment status"

NAIVE APPROACH (violates data isolation):
  SELECT o.id, c.name, p.name, pay.status
  FROM orders o
  JOIN CustomerService.customers c ON o.customer_id = c.id
  JOIN InventoryService.products p ON o.product_id = p.id
  JOIN PaymentService.payments pay ON o.id = pay.order_id
  -- This requires access to 4 services' databases → VIOLATION

CORRECT APPROACHES:

OPTION 1: API Composition (for low-volume reports):
  Reporting service calls:
    GET /orders → list of orders
    For each order: GET /customers/{id}, GET /products/{id}, GET /payments/{id}
  Assembles result in memory
  Cost: N+1 query problem at scale

OPTION 2: CQRS Read Model (for high-volume reporting):
  Separate "ReportingDB" (ClickHouse or data warehouse)
  Populated by consuming events from all services:
    OrderPlaced → write to reporting.orders table
    CustomerUpdated → update reporting.customers table
    PaymentProcessed → write to reporting.payments table
  Reporting service queries ONLY ReportingDB (its own isolated data!)
  No violation: reporting service owns its projection DB
  Data is eventually consistent (event propagation lag)

OPTION 3: GraphQL Federation (API gateway composition):
  Each service exposes GraphQL schema
  Apollo Federation: gateway resolves cross-service fields
  Still calls each service's API — no DB violations
  Better developer experience for cross-entity queries
```

---

### ❓ Why Does This Exist (Why Before What)

When multiple services share a database, the database becomes the coupling point. Schema changes require coordinating all services simultaneously. One service's query can affect another's performance. Services cannot be deployed independently. Data isolation enforces the microservices principle that "the only thing you can call is what's behind the API boundary." This is the data equivalent of encapsulation in object-oriented programming: hide internal data, expose behaviour through an interface.

---

### 🧠 Mental Model / Analogy

> Data isolation per service is like a hospital's department data systems. The Radiology department owns X-ray images in its PACS system. The Pharmacy owns prescription records in its dispensing system. Billing owns financial records in its billing system. If a doctor needs radiology data, they use the radiology system's interface (PACS viewer). Billing cannot directly execute SQL queries against Radiology's database — they request structured reports through official channels. Why? Security, compliance (HIPAA), independent upgrades, and preventing one department's heavy queries from crashing another's system.

---

### ⚙️ How It Works (Mechanism)

**Local projection pattern — caching foreign data without violating isolation:**

```java
// OrderService needs customer tier for discount calculation.
// Instead of calling CustomerService API on every order creation:

// 1. Subscribe to CustomerUpdated events → maintain local projection
@Entity
class CustomerTierProjection {
    @Id Long customerId;
    CustomerTier tier;               // BRONZE, SILVER, GOLD
    Instant lastUpdated;
}

// 2. Use projection for order creation (no inter-service call needed):
@Service
class OrderCreationService {
    public Order createOrder(CreateOrderRequest req) {
        CustomerTier tier = customerTierProjectionRepository
            .findById(req.getCustomerId())
            .map(CustomerTierProjection::getTier)
            .orElse(CustomerTier.BRONZE);  // default for unknown customers

        BigDecimal discount = tier.getDiscountPercentage();
        // create order with discount...
    }
}
// Isolation maintained: OrderService DB has CustomerTierProjection table
// No direct access to CustomerService DB
// Trade-off: projection may be slightly stale (eventual consistency)
```

---

### 🔄 How It Connects (Mini-Map)

```
Microservices Architecture
(autonomous services principle)
        │
        ▼
Data Isolation per Service  ◄──── (you are here)
(enforce data ownership at storage level)
        │
        ├── Database per Service → physical implementation of isolation
        ├── Shared Database Anti-Pattern → what violating this looks like
        ├── Eventual Consistency → consequence of cross-service data propagation
        └── CQRS → pattern for cross-service reporting without violating isolation
```

---

### 💻 Code Example

**Architecture test enforcing data isolation (ArchUnit):**

```java
// Automated test to prevent OrderService from importing CustomerService DB classes:
@AnalyzeClasses(packages = "com.example.orderservice")
class DataIsolationArchTest {

    @ArchTest
    static final ArchRule noDirectAccessToCustomerDatabase =
        noClasses()
            .that().resideInAPackage("com.example.orderservice..")
            .should().accessClassesThat()
            .resideInAPackage("com.example.customerservice.infrastructure.persistence..")
            .because("OrderService must not access CustomerService's data layer directly. " +
                     "Use CustomerClient API or consume CustomerUpdated events instead.");

    @ArchTest
    static final ArchRule noSharedEntityClasses =
        noClasses()
            .that().resideInAPackage("com.example.orderservice..")
            .should().dependOnClassesThat()
            .areAnnotatedWith(Entity.class)
            .and().resideOutsideOfPackage("com.example.orderservice..")
            .because("Each service manages its own JPA entities. " +
                     "Do not import @Entity classes from other services.");
}
```

---

### ⚠️ Common Misconceptions

| Misconception                                                                  | Reality                                                                                                                                                                                                                                                                 |
| ------------------------------------------------------------------------------ | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Data isolation means you can never join data across services                   | Data isolation prevents direct database joins. Cross-service data can still be combined via API composition, CQRS read models, or local projections — the join just happens at the application level or in a dedicated reporting layer                                  |
| Data isolation always means completely separate database servers               | Separate schemas within the same database instance can provide logical isolation with enforced access control — though separate servers provide stronger operational isolation. The key is enforced access control, not necessarily separate hardware                   |
| Data isolation makes reporting impossible                                      | Reporting is solved by CQRS: a dedicated reporting service consumes events from all services and builds its own queryable projection. The reporting service owns its projection DB — no isolation violation                                                             |
| The "Database per Service" pattern is the same as "Data Isolation per Service" | Database per Service is the physical implementation (separate databases). Data Isolation per Service is the principle (ownership + enforced access boundaries). You can have separate DBs but still violate isolation by sharing credentials or using federated queries |

---

### 🔥 Pitfalls in Production

**Cascading failures from synchronous cross-service data calls:**

```
SCENARIO (violating data isolation leads to cascade failure):
  OrderService has no local projection.
  Every GET /orders/{id} call → synchronous GET /customers/{id} → CustomerService DB.
  CustomerService deployed with a slow migration (ALTER TABLE on 50M rows).
  CustomerService DB: queries taking 30+ seconds.
  OrderService: all HTTP threads blocked waiting for CustomerService responses.
  OrderService thread pool exhausted.
  Orders cannot be created OR read.
  → Cascade failure from one service's DB migration.

WITH LOCAL PROJECTION:
  OrderService reads customer name from local projection table.
  CustomerService slow migration: only affects CustomerService.
  OrderService: continues serving orders from local projection (slightly stale, but available).
  → Isolated failure: CustomerService degraded, OrderService unaffected.

LESSON: Local projections are a resilience pattern, not just a performance optimisation.
         They decouple your service's availability from other services' availability.
```

---

### 🔗 Related Keywords

- `Database per Service` — the physical implementation of data isolation
- `Shared Database Anti-Pattern` — the violation of this principle and its consequences
- `Eventual Consistency (Microservices)` — trade-off accepted when using local projections
- `CQRS in Microservices` — the pattern for cross-service reporting under data isolation

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ PRINCIPLE    │ Each service owns its data exclusively    │
│ RULE         │ No direct DB access from other services   │
│ ACCESS VIA   │ API (sync) or Events (async)              │
├──────────────┼───────────────────────────────────────────┤
│ REPORTING    │ CQRS read model / API composition         │
│ ISOLATION    │ Schemas → Separate DBs → Separate servers │
├──────────────┼───────────────────────────────────────────┤
│ BENEFIT      │ Independent schema evolution, scaling,    │
│              │ technology choice, failure isolation       │
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** Your organisation has 15 microservices, each with its own database. A new compliance requirement mandates: "All customer data (name, email, address) must be deleted within 24 hours of a deletion request (GDPR Right to Erasure)." The problem: customer data has been copied into local projections across 8 of the 15 services. How do you implement GDPR erasure across all 15 services? What is the "forget event" pattern, and how do services ensure their local projections are scrubbed? Does this challenge the event-sourcing model (where events are immutable by design)?

**Q2.** You are designing a "Product Catalog Service" that needs to JOIN product data with inventory levels from "Inventory Service" and pricing data from "Pricing Service" to return a single product listing response. You cannot violate data isolation. Design the data flow: (a) API composition approach — describe the request sequence, error handling when one service is down, and timeout strategy; (b) Local projection approach — describe event subscription, projection staleness handling, and storage requirements; (c) Which approach would you recommend for a product catalog that serves 10,000 requests/second with 100,000 active products?
