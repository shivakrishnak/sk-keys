---
layout: default
title: "Data Isolation per Service"
parent: "Microservices"
grand_parent: "Technical Dictionary"
nav_order: 42
permalink: /microservices/data-isolation-per-service/
id: MSV-042
category: Microservices
difficulty: ★★★
depends_on: Bounded Context, Domain-Driven Design (DDD), Database per Service
used_by: Eventual Consistency (Microservices), CQRS in Microservices, Shared Database Anti-Pattern
related: Database per Service, Shared Database Anti-Pattern, Bounded Context
tags:
  - microservices
  - database
  - architecture
  - distributed
  - deep-dive
---

# MSV-042 — Data Isolation per Service

⚡ TL;DR — Each microservice owns and exclusively controls its own data store; no other service may access that data directly, only through the service's API.

| #657            | Category: Microservices                                                                   | Difficulty: ★★★ |
| :-------------- | :---------------------------------------------------------------------------------------- | :-------------- |
| **Depends on:** | Bounded Context, Domain-Driven Design (DDD), Database per Service                         |                 |
| **Used by:**    | Eventual Consistency (Microservices), CQRS in Microservices, Shared Database Anti-Pattern |                 |
| **Related:**    | Database per Service, Shared Database Anti-Pattern, Bounded Context                       |                 |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
Five microservices all query the same PostgreSQL `products` table. The Inventory Service does `UPDATE products SET stock=? WHERE id=?`. The Pricing Service does `SELECT price, discount FROM products`. The Catalog Service does `SELECT name, description, images FROM products`. Any service can read or write any column. When the Inventory Service needs to add a `warehouse_zone` column, it can — but it breaks a Pricing Service query that selects `SELECT *`. When the Order Service adds a new index for its query pattern, it degrades Inventory Service query performance. All five services are coupled at the database level, defeating the purpose of microservices.

**THE BREAKING POINT:**
Shared databases create hidden coupling: schema changes require coordinating all teams simultaneously; one service's query pattern degrades another's performance; one service's migration can corrupt another service's data. You have autonomous-looking services at the API level but a shared, centrally-locked database.

**THE INVENTION MOMENT:**
Data isolation per service — the principle that each service owns its data exclusively — was formalised to make microservices truly autonomous at the data level.

---

### 📘 Textbook Definition

**Data isolation per service** is the design principle in microservices architecture that each service owns its data exclusively. A service's data may only be accessed or modified through that service's published API — not by direct database queries from other services. Each service may use any database technology appropriate to its needs (polyglot persistence). This boundary enforces that the service's data schema, storage technology, and access patterns are internal implementation details, freely changeable without coordinating with other teams.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
Your service's database is your private implementation detail — no one else gets to read or write it directly.

**One analogy:**

> A bank doesn't let you reach into their ledger and change your own balance. All changes must go through their teller (API). The bank owns the data; you access it only through their interface. This protects data integrity and lets the bank change their internal ledger system without telling you.

**One insight:**
This principle is what allows truly independent deployability. If two services share a database, you cannot change one service's schema without coordinating the other. Data isolation makes each service's schema an internal detail — enabling independent evolution.

---

### 🔩 First Principles Explanation

**CORE INVARIANTS:**

1. A service that cannot freely change its own schema is not truly independent.
2. A service that can be corrupted by another service's bug is not truly isolated.
3. A service whose performance is degraded by another service's query is not truly autonomous.

**DERIVED DESIGN:**
Given these invariants: each service must own a data store that no other service can access directly. The interface to data is the service's API. Other services that need the data ask via API or maintain their own copy via event replication.

**What "data isolation" means concretely:**

- ✅ Separate database instances (strongest)
- ✅ Separate database schemas within one instance (medium)
- ✅ Separate tables with enforced permission barriers (minimum)
- ❌ Shared tables (violates isolation)
- ❌ Direct DB reads from another service (violates isolation)
- ❌ DB-level foreign keys between services (violates isolation)

**The key pattern: own your data, share via events:**

```
Product Service ──publishes──► ProductPriceChanged event
                                        │
                                        ▼
                            Order Service (local copy)
                              maintains product_prices table
                              updated by consuming events
```

Each service maintains a local "read model" of the data it needs from other services. This is _not_ the authoritative copy — it's a replicated view. The Product Service owns the authoritative price.

**THE TRADE-OFFS:**
**Gain:** Independent schema evolution; independent scaling; independent technology choice; fault isolation (one service's DB going down doesn't cascade).
**Cost:** Data duplication across services; eventual consistency for cross-service reads; complex join-like operations require choreography; referential integrity must be enforced at application level, not database level.

---

### 🧪 Thought Experiment

**SETUP:**
You have Order Service and Product Service. Order needs to display product name and price for each order line item. Product Service owns product data.

**OPTION A — Shared DB (no isolation):**
Order Service queries `products.product_catalog_db` directly. Works at T=0. At T+6 months, Product Service changes their schema: splits `price` into `list_price` + `sale_price`. They update their code. Order Service breaks at 3AM because its direct query suddenly gets NULL from `price`. Incident.

**OPTION B — API call (isolation, no caching):**
Order Service calls `GET /products/{id}` for each order display. Works. At 10k orders/sec, displaying order history means 100k product API calls/sec. Product Service becomes the bottleneck. Latency degrades.

**OPTION C — Event replication (isolation + performance):**
Product Service publishes `ProductUpdated` events. Order Service maintains its own `product_snapshot` table with just the fields it needs: `product_id, name, price_at_capture`. When displaying order history, Order Service reads its own table — no API call. Product Service can change its schema freely; Order Service's snapshot is stable and owned by the Order Service.

**THE INSIGHT:**
Option C achieves isolation AND performance. The cost: data duplication and eventual consistency. The key insight is that an Order's line items should record the price at time of purchase — not the current price. Data isolation naturally leads to the right domain model.

---

### 🧠 Mental Model / Analogy

> Think of microservices as countries. Each country has its own laws, its own currency system, and manages its own records. If you want information about a citizen from another country, you go through official diplomatic channels (API) — not by breaking into their records office (direct DB access). Each country can change its internal record-keeping system (schema) without notifying every other country. Data shared across borders is replicated via treaties (event propagation), not by sharing a single database.

- "Country's records" → service's database
- "Diplomatic channels" → service's API
- "Breaking into records" → direct cross-service DB query
- "Change internal records system" → schema migration
- "Treaties" → event-driven data replication

Where this analogy breaks down: unlike countries, microservice events are near-instantaneous, not negotiated over years.

---

### 📶 Gradual Depth — Four Levels

**Level 1 — What it is (anyone can understand):**
Each service has its own database that only it can use. If you need data from another service, you ask that service nicely (via API) — you don't go look in their database directly.

**Level 2 — How to use it (junior developer):**
Never write code that connects to another service's database. If you need data from another service, call its API. If you need that data often or at high volume, subscribe to its events and cache a local copy in your own database. Never add database-level foreign keys across service boundaries.

**Level 3 — How it works (mid-level engineer):**
The practical implementation has three layers:

1. **Network isolation**: Service B's DB is on a VPC/network only service B's processes can reach. No other service has credentials.
2. **Schema isolation**: If sharing one DB instance, each service uses its own schema/prefix. Schema permissions granted only to the owning service's user.
3. **Ownership documentation**: Schema migrations are owned by the service team; no other team can submit migrations to your schema.
   Foreign key enforcement moves from DB to application (saga compensation, event-driven consistency). Joins across services become API compositions or local read model queries.

**Level 4 — Why it was designed this way (senior/staff):**
Data isolation per service is the enforcement mechanism for Conway's Law at the data tier. If teams share a database, they share a schema — and schema changes require coordination across teams, which recreates the monolith at the data layer. By mandating data isolation, you force each team to define their service contract explicitly (API) and own their data model completely. This enables the core promise of microservices: independent deployability. The "polyglot persistence" benefit is secondary — the primary benefit is the schema independence that enables teams to move without coordination. The implementation cost (no cross-service DB joins) forces better domain modelling: if services need to share a lot of data, they may be in the same bounded context and should be merged.

---

### ⚙️ How It Works (Mechanism)

```
┌─────────────────────────────────────────────────────────┐
│       Data Isolation per Service — Architecture         │
└─────────────────────────────────────────────────────────┘

┌──────────────────┐    API only    ┌──────────────────┐
│  Order Service   │──────────────► │  Product Service  │
│                  │                │                  │
│  ┌────────────┐  │                │  ┌────────────┐  │
│  │ orders DB  │  │                │  │ products DB│  │
│  │ (Postgres) │  │                │  │  (MongoDB) │  │
│  └────────────┘  │                │  └────────────┘  │
│                  │                │                  │
│  ┌────────────┐  │ event replication                 │
│  │product_    │◄─┤──── ProductUpdated ───────────────┤
│  │snapshots   │  │                │                  │
│  └────────────┘  │                │                  │
└──────────────────┘                └──────────────────┘

Rules:
  ✅ Order Service queries its own orders DB
  ✅ Order Service queries its own product_snapshots
  ✅ Order Service calls Product API for authoritative data
  ✅ Order Service consumes ProductUpdated events
  ❌ Order Service queries products DB directly
  ❌ Any cross-service database connection
  ❌ DB-level foreign key: orders.product_id → products.id
```

**Cross-service referential integrity (application level):**

```java
// Instead of DB FK constraint:
//   orders.product_id REFERENCES products.id

// Application-level validation:
public OrderLine createOrderLine(String productId, int qty) {
  // Validate via API (at creation time only)
  Product product = productApiClient.getProduct(productId);
  if (product == null) {
    throw new ProductNotFoundException(productId);
  }
  // Snapshot the relevant data into the order
  return new OrderLine(
    productId,
    product.getName(),      // captured at time of order
    product.getPrice(),     // captured at time of order
    qty);
  // Order is now self-contained — no FK needed
}
```

---

### 🔄 The Complete Picture — End-to-End Flow

**NORMAL FLOW:**

```
[User: view order history]
  → [Order Service: query own orders DB + product_snapshots]
  → [No cross-service call needed]
  → [Return complete order view]

[User: place order]
  → [Order Service: call Product API to validate + get current price]
  → [Capture price into order line item (snapshot)]
  → [No ongoing dependency on Product Service]
```

**SCHEMA EVOLUTION FLOW:**

```
[Product Team: split price into list_price + sale_price]
  → [Update products DB schema]
  → [Update Product Service API (backward compatible)]
  → [Deploy Product Service independently]
  → [Update ProductUpdated event schema]
  → [Order Service consumes events: updates its snapshot]
  → [Zero coordination with Order team needed]
```

---

### 💻 Code Example

**Example 1 — Violation: direct cross-service DB access:**

```java
// ❌ WRONG: Order Service directly queries Product DB
@Repository
public class ProductDirectRepository {
  @Autowired DataSource productServiceDataSource; // DO NOT DO THIS

  public Product findById(String id) {
    // Violates data isolation: direct cross-service DB query
    return jdbcTemplate.queryForObject(
      "SELECT * FROM product_catalog.products WHERE id=?",
      productRowMapper, id);
  }
}
```

**Example 2 — Correct: API call for authoritative data:**

```java
// ✅ RIGHT: API call for current authoritative data
@Component
public class ProductApiClient {
  private final RestTemplate restTemplate;
  private final String productServiceUrl;

  public ProductInfo getProduct(String productId) {
    return restTemplate.getForObject(
      productServiceUrl + "/products/" + productId,
      ProductInfo.class);
  }
}
```

**Example 3 — Correct: local read model via event replication:**

```java
// ✅ RIGHT: local snapshot for high-frequency reads
@Component
public class ProductSnapshotConsumer {

  @KafkaListener(topics = "product-events",
                 groupId = "order-service-product-sync")
  public void onProductUpdated(ProductUpdatedEvent event) {
    // Update local snapshot — owned by Order Service
    productSnapshotRepo.upsert(
      new ProductSnapshot(
        event.getProductId(),
        event.getName(),
        event.getCurrentPrice(),
        event.getOccurredAt()));
  }
}

// Order Service reads its own snapshot — zero dependency
@Service
public class OrderDisplayService {
  public OrderView getOrderView(String orderId) {
    Order order = orderRepo.findById(orderId);
    // No cross-service call: read local snapshot
    Map<String, ProductSnapshot> products =
      productSnapshotRepo.findByIds(
        order.getProductIds());
    return OrderView.assemble(order, products);
  }
}
```

---

### ⚖️ Comparison Table

| Approach                       | Isolation | Flexibility | Cross-Service Joins | Complexity |
| ------------------------------ | --------- | ----------- | ------------------- | ---------- |
| **Data Isolation per Service** | Full      | Maximum     | Via API / events    | High       |
| Shared Database                | None      | Minimal     | Native SQL join     | Low        |
| Schema per Service (same DB)   | Partial   | Medium      | Limited via views   | Medium     |
| Separate DB Instances          | Full      | Maximum     | None (by design)    | High       |

**How to choose:** Full data isolation (separate DB instances or schemas with enforced permissions) is the correct target for production microservices. Schema-per-service in a shared instance is an acceptable stepping stone during migration from monolith.

---

### ⚠️ Common Misconceptions

| Misconception                                                    | Reality                                                                                                                |
| ---------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------- |
| Data isolation means each service must have a separate DB server | Separate schemas with permission enforcement satisfies the principle; different server is optimal but not mandatory    |
| Data isolation eliminates the need for data consistency          | It shifts consistency from DB-level constraints to application-level patterns (sagas, events)                          |
| You can never query across service data                          | Via API or event replication — just never via direct DB connection                                                     |
| Data isolation means data duplication is bad                     | Intentional replication (event-based snapshots) is correct pattern; unintentional duplication with no ownership is bad |
| Data isolation prevents joining data from two services           | It prevents DB-level joins; application-level joins (assemble from two API responses) are fine                         |

---

### 🚨 Failure Modes & Diagnosis

**Ghost Data — Orphaned Records After Service Changes**

**Symptom:** Order lines reference product IDs that no longer exist in Product Service; order display shows "Product not found."

**Root Cause:** Product Service deleted a product; Order Service has no DB FK constraint to prevent the reference; old orders reference deleted productId.

**Diagnostic Query:**

```sql
-- In Order Service DB (checking own data)
SELECT ol.product_id, count(*)
FROM order_lines ol
LEFT JOIN product_snapshots ps
  ON ol.product_id = ps.product_id
WHERE ps.product_id IS NULL
GROUP BY ol.product_id;
```

**Fix:** Order lines should snapshot all needed display data at creation time (price, name, description). A product_id in an old order is a historical reference — it doesn't need the product to still "exist."

**Prevention:** Capture and snapshot all display-required data at order time. Don't rely on looking up from another service at display time.

---

**Schema Drift — Local Snapshot Out of Sync**

**Symptom:** Order display shows outdated product names/prices; consumer lag spike correlates with data divergence.

**Root Cause:** Event consumer fell behind; Kafka topic retention expired before lagging consumer could catch up; events permanently lost.

**Diagnostic Command:**

```bash
kafka-consumer-groups.sh \
  --bootstrap-server kafka:9092 \
  --describe --group order-service-product-sync
# Check LAG column and LOG-END-OFFSET vs CURRENT-OFFSET
```

**Fix:** If topic retention hasn't expired: restart consumer, let it catch up. If expired: trigger full re-sync from Product Service API (pagination endpoint to rebuild snapshot from scratch).

**Prevention:** Set Kafka topic retention > maximum expected consumer lag. Implement reconciliation job that periodically compares snapshot against Product API for key items.

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**

- `Bounded Context` — defines the domain boundary that determines service scope
- `Domain-Driven Design (DDD)` — provides the conceptual framework for service data ownership
- `Database per Service` — the infrastructure pattern implementing data isolation

**Builds On This (learn these next):**

- `Eventual Consistency (Microservices)` — the consistency model required once data is isolated
- `CQRS in Microservices` — pattern for separating read models from write models within a service
- `Shared Database Anti-Pattern` — the violation of this principle and why it fails

**Alternatives / Comparisons:**

- `Shared Database Anti-Pattern` — the anti-pattern this principle avoids
- `Aggregate` — DDD concept that defines the atomic unit within a service's data boundary
- `Anti-Corruption Layer` — isolates a service's data model from external concepts

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ WHAT IT IS   │ Each service exclusively owns its data;   │
│              │ no direct cross-service DB access         │
├──────────────┼───────────────────────────────────────────┤
│ PROBLEM IT   │ Shared databases create hidden coupling   │
│ SOLVES       │ that prevents independent deployability   │
├──────────────┼───────────────────────────────────────────┤
│ KEY INSIGHT  │ Schema is a private implementation detail │
│              │ — API is the public interface             │
├──────────────┼───────────────────────────────────────────┤
│ USE WHEN     │ Always — in a microservices system        │
├──────────────┼───────────────────────────────────────────┤
│ AVOID WHEN   │ Simple CRUD apps with no team or domain   │
│              │ boundaries (use a monolith instead)       │
├──────────────┼───────────────────────────────────────────┤
│ TRADE-OFF    │ Independent deployability + schema freedom │
│              │ vs data duplication + eventual consistency │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "Own your data; share via API, not schema" │
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ Shared DB Anti-Pattern → Database per     │
│              │ Service → CQRS in Microservices           │
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** You have an Order Service and an Inventory Service. Order Service creates orders; Inventory Service manages stock levels. How do you enforce referential integrity (can't order a non-existent product; can't order more than available stock) without a cross-service database foreign key? Describe the exact mechanism, including what happens if the Inventory Service is temporarily down when an order is placed.

**Q2.** Your team wants to generate a report combining order data (from Order Service DB) and customer data (from Customer Service DB). Both services follow strict data isolation. Describe three different approaches to produce this report, and explain the trade-offs of each. Which would you recommend for a weekly batch report vs. a real-time dashboard?
