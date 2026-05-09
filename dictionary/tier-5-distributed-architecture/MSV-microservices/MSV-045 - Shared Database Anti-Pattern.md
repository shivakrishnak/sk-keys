---
layout: default
title: "Shared Database Anti-Pattern"
parent: "Microservices"
grand_parent: "Technical Dictionary"
nav_order: 45
permalink: /microservices/shared-database-anti-pattern/
id: MSV-045
category: Microservices
difficulty: ★★★
depends_on: Data Isolation per Service, Microservices, Bounded Context
used_by: Database per Service, Service Decomposition
related: Database per Service, Data Isolation per Service, Strangler Fig Pattern
tags:
  - microservices
  - anti-pattern
  - database
  - architecture
  - deep-dive
status: complete
version: 1
---

# MSV-045 - Shared Database Anti-Pattern

⚡ TL;DR - The shared database anti-pattern occurs when multiple microservices directly access the same database, creating hidden coupling that defeats microservices autonomy.

| #660            | Category: Microservices                                                 | Difficulty: ★★★ |
| :-------------- | :---------------------------------------------------------------------- | :-------------- |
| **Depends on:** | Data Isolation per Service, Microservices, Bounded Context              |                 |
| **Used by:**    | Database per Service, Service Decomposition                             |                 |
| **Related:**    | Database per Service, Data Isolation per Service, Strangler Fig Pattern |                 |

---

### 🔥 The Problem This Solves

**WORLD WITH THIS ANTI-PATTERN:**
You decomposed a monolith into five microservices but pointed them all at the same PostgreSQL instance. This works initially. Then: the Inventory team renames `product_qty` to `available_stock` - the Order Service breaks at midnight because no one knew it was reading that column directly. The Pricing Service adds a heavy `FULL TABLE SCAN` query at peak hours - the Checkout Service times out because the shared DB is saturated. The Security team rotates the DB password - all five teams must coordinate the rotation simultaneously. At 3AM, one service has a query bug that holds locks - all five services start failing.

**THE BREAKING POINT:**
"Microservices" with a shared database is a distributed monolith: you have the operational complexity of distributed services (network calls, latency, deployment coordination) combined with the coupling of a monolith (shared schema, shared failure modes). You get the worst of both worlds.

**THE INVENTION MOMENT:**
Naming this as an anti-pattern - and defining Database per Service as the correct pattern - was the breakthrough that made microservices truly deliver on their promise of independent deployability.


**EVOLUTION:**
Shared database became an anti-pattern in the microservices era but was the standard practice in SOA (2000s). SOA encouraged service decoupling at the interface level while sharing underlying data stores. 'Integration databases' (shared databases serving multiple applications) were documented as an enterprise integration pattern (Martin Fowler). The microservices movement (2012-2015) reacted against this: Sam Newman's 'Building Microservices' (2015) established 'Database per Service' as a core principle. The discipline evolved from 'share data, not code' to 'own data, expose it only through your API.'
---

### 📘 Textbook Definition

The **shared database anti-pattern** in microservices is the practice where two or more independently-deployed services share direct read/write access to the same database (or the same tables within a database). This violates the principle of service autonomy because the database schema becomes a shared contract between services, preventing independent evolution, independent scaling, and independent failure isolation. It is classified as an anti-pattern because it negates the primary architectural benefits that justify microservices' complexity cost.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
You built microservices at the API level but kept a monolith at the data level - you have all the costs of microservices and none of the benefits.

**One analogy:**

> You decomposed a company into 5 departments with separate management teams. But every department uses the same shared spreadsheet for all records, and anyone can edit any row. When the Sales team reformats the spreadsheet, Finance's macros break. When HR locks rows during payroll, everyone waits. Departments cannot be independent if they share the same uncontrolled data store.

**One insight:**
The shared database anti-pattern is often the first and most common mistake when decomposing a monolith into microservices. It feels harmless at T=0 but creates exponentially increasing pain as teams and services grow.

---

### 🔩 First Principles Explanation

**WHAT COUPLING ACTUALLY MEANS:**
Two services are coupled if a change in one can break the other without any API change. A shared database creates coupling at three levels:

1. **Schema coupling**: Service A changes a column name → Service B's SQL query breaks. No API was touched.
2. **Data coupling**: Service A inserts invalid data (NULL in a non-null column) → Service B gets NPE. No API change.
3. **Operational coupling**: Service A's query causes lock contention → Service B's queries time out. No code change.

**THE FORMS OF THIS ANTI-PATTERN:**

**Form 1 - Shared tables:**

```sql
-- Order Service writes
INSERT INTO products ...

-- Inventory Service reads (same table)
SELECT stock FROM products WHERE id = ?

-- Both services share schema contract
```

**Form 2 - Cross-schema direct queries:**

```java
// In Inventory Service
@Query("SELECT o.total FROM order_service.orders o WHERE ...")
// Directly queries Order Service's schema
```

**Form 3 - Shared DB instance with separate schemas (better but still risky):**

```
order_schema.orders      ← owned by Order Service
inventory_schema.stock   ← owned by Inventory Service
-- Physical isolation ok; operational coupling remains
-- DB failure = all services fail
-- DB upgrade = all services must coordinate
```

**THE CONSEQUENCES:**

| Consequence                                     | Mechanism                                          |
| ----------------------------------------------- | -------------------------------------------------- |
| Schema changes require coordination             | Any column rename/remove breaks dependent services |
| Cannot change DB technology per service         | All services must agree on the single DB           |
| Cannot scale reads/writes per service           | One DB instance must serve all traffic profiles    |
| One service's bug corrupts shared data          | No service-level isolation                         |
| DB failure = total system failure               | Single point of failure                            |
| Security: one breach exposes all services' data | No data-level isolation                            |

**THE TRADE-OFFS:**
**"Gain" (why teams do it):** Easier initial development; simple joins across "service" boundaries; no need to replicate data; familiar operational pattern.
**Cost:** Every other microservices benefit is eliminated; technical debt compounds exponentially.

---

### 🧪 Thought Experiment

**SETUP:**
You have three services: Order, Inventory, Customer - all sharing one PostgreSQL database.

**SCENARIO: The Inventory team wants to migrate to MongoDB** (better for their document-shaped inventory data).

**With shared DB:** The Order Service queries `inventory.products` table directly. The Customer Service queries `inventory.categories` for product display. If Inventory migrates to MongoDB, all cross-DB queries break. Migration requires rewriting queries in Order and Customer services, coordinating three teams, migrating and testing everything simultaneously. This is effectively impossible without downtime.

**With Database per Service:** Order Service has its own product snapshot (from events). Customer Service calls Inventory Service API for category data. Inventory team migrates their DB to MongoDB internally - zero impact on other services.

**THE INSIGHT:**
The shared database doesn't just couple teams at one moment in time - it permanently prevents technology evolution. A "simple" migration becomes a multi-team, multi-month coordinated effort.

---

### 🧠 Mental Model / Analogy

> Think of a shared database as a shared kitchen in an office building (for 5 companies). When Company A's chef reorganises the pantry shelves (schema change), Company B's cooks can't find anything. When Company C runs the dishwasher at noon (heavy query load), Company D can't use the sink. When the building shuts the kitchen for maintenance (DB upgrade/failure), all five companies can't cook. Each company would be better served with their own private kitchen - even if it requires buying their own utensils.

- "Shared kitchen" → shared database
- "Reorganise shelves" → schema change
- "Can't find ingredients" → query breaks after schema change
- "Running dishwasher at noon" → heavy query load
- "Can't use the sink" → query contention / timeout
- "Private kitchen" → Database per Service

---

### 📶 Gradual Depth - Four Levels

**Level 1 - What it is (anyone can understand):**
When multiple separate services all connect to and modify the same database, they become secretly dependent on each other - even though they look independent from the outside. This is the anti-pattern.

**Level 2 - How to identify it (junior developer):**
Look for: multiple services listed in the same database's connection string; services that import or reference another service's DB schema/table names; schema migrations that must be coordinated across teams; shared `DataSource` beans in a multi-service codebase.

**Level 3 - How to fix it (mid-level engineer):**
Use the Strangler Fig pattern to incrementally move to Database per Service. Step 1: identify which tables each service actually "owns" (writes to). Step 2: replicate cross-service reads via API calls or event-driven snapshots. Step 3: add service-level permission barriers (revoke direct DB access for other services). Step 4: move tables to separate schemas or DB instances. Step 5: remove the legacy shared access.

**Level 4 - Why it persists (senior/staff):**
The shared database anti-pattern persists because it is the path of least resistance when decomposing a monolith. The monolith has one DB; the initial decomposition simply splits the code into services while leaving the DB unchanged. The coupling is invisible until teams begin independent evolution. The fix - event-driven data replication, API-mediated cross-service reads - requires substantial investment in event infrastructure and often forces teams to abandon comfortable join-based queries. Organisations under delivery pressure choose the visible short-term win (faster feature delivery) over the invisible long-term cost (coupling that grows over months and years). Naming it explicitly as an anti-pattern, and making the long-term costs visible, is the mechanism for changing this default.

---

### ⚙️ How It Works (Mechanism) - Why It Breaks

```
┌─────────────────────────────────────────────────────────┐
│         Shared Database Anti-Pattern - Failure Modes    │
└─────────────────────────────────────────────────────────┘

Services A, B, C all connected to shared DB:

         ┌────────────────────────────────────┐
         │           Shared PostgreSQL        │
         │  orders  products  customers  stock│
         └──┬──────────┬────────────┬─────────┘
            │          │            │
     Service A     Service B     Service C
     (Orders)    (Inventory)   (Customer)

COUPLING EVENT 1: Schema change
  Service B renames products.qty → available_stock
  Service A: SELECT qty FROM products → BREAKS (no API change)

COUPLING EVENT 2: Lock contention
  Service B: LOCK TABLE products
  Service A: SELECT ... FROM products → WAITS

COUPLING EVENT 3: DB failure
  PostgreSQL down → A, B, AND C all fail simultaneously
  (monolith failure mode despite microservices architecture)

COUPLING EVENT 4: Security
  Service C has SQL injection bug
  Attacker reads orders.credit_card_tokens
  (data belonging to Service A, accessed via shared DB)
```

---

### 🔄 The Complete Picture - Migration Path

**PHASE 1: Identify ownership (read-only analysis)**

```
Audit: which service writes to which tables?
  orders          → owned by Order Service
  products        → owned by Inventory Service
  order_lines     → owned by Order Service
  customers       → owned by Customer Service

Cross-reads:
  Order Service reads products.price (should go via API)
  Customer Service reads orders.status (should go via API)
```

**PHASE 2: Add service APIs for cross-reads**

```
Replace: SELECT price FROM products WHERE id=?
With:    productApiClient.getPrice(productId)

Replace: SELECT status FROM orders WHERE id=?
With:    orderApiClient.getStatus(orderId)
```

**PHASE 3: Enforce DB isolation**

```
Revoke DB permissions: order_service_user → products table
Revoke DB permissions: customer_service_user → orders table
Monitor: alert on any remaining direct cross-table reads
```

**PHASE 4: Separate schemas/instances**

```
Move products → inventory_db (owned by Inventory Service only)
Move orders → order_db (owned by Order Service only)
```

---

### 💻 Code Example

**Example 1 - The anti-pattern:**

```java
// ❌ ANTI-PATTERN: Order Service directly queries Product table
@Repository
public class OrderRepository {
  @Autowired JdbcTemplate sharedDb;  // shared DB connection

  public OrderWithProduct getOrderWithProduct(String orderId) {
    // WRONG: joins across service boundaries via shared DB
    return sharedDb.queryForObject(
      "SELECT o.id, o.status, p.name, p.price " +
      "FROM orders o " +
      "JOIN products p ON o.product_id = p.id " +  // cross-service join
      "WHERE o.id = ?",
      orderWithProductMapper, orderId);
  }
}
```

**Example 2 - The correct pattern:**

```java
// ✅ CORRECT: Order Service calls Product Service API
@Service
public class OrderDisplayService {
  @Autowired OrderRepository orderRepo;      // OWN DB
  @Autowired ProductApiClient productClient; // API call

  public OrderDisplay getOrderDisplay(String orderId) {
    Order order = orderRepo.findById(orderId);

    // Call Product Service API - not its database
    ProductInfo product = productClient
      .getProduct(order.getProductId());

    return OrderDisplay.of(order, product);
  }
}

// Or even better: snapshot at order creation time
@Service
public class OrderCommandService {
  public Order createOrder(CreateOrderRequest req) {
    // Capture product data at time of order
    ProductInfo product = productClient
      .getProduct(req.getProductId());

    Order order = Order.builder()
      .productId(req.getProductId())
      .productName(product.getName())    // snapshot
      .priceAtCapture(product.getPrice()) // snapshot
      .build();

    return orderRepo.save(order);
    // No ongoing dependency on Product DB
  }
}
```

---

### ⚖️ Comparison Table

| Pattern                            | Coupling | Independent Deploy | Independent Scale    | Data Isolation |
| ---------------------------------- | -------- | ------------------ | -------------------- | -------------- |
| **Shared Database (anti-pattern)** | High     | No                 | No                   | None           |
| Separate schemas, shared instance  | Medium   | Partial            | No (shared instance) | Partial        |
| Database per Service               | None     | Yes                | Yes                  | Full           |
| Shared DB + service API layer      | Medium   | Partial            | Partial              | Partial        |

**How to choose:** Database per Service is the only approach that fully delivers microservices benefits. Separate schemas in a shared instance is an acceptable migration step.

---

### ⚠️ Common Misconceptions

| Misconception                                                | Reality                                                                                               |
| ------------------------------------------------------------ | ----------------------------------------------------------------------------------------------------- |
| "It's fine because we have separate schemas"                 | Separate schemas on the same instance = same operational coupling (DB failure/upgrade affects all)    |
| "We only have read access from other services - that's fine" | Read access to another service's tables = schema coupling; any schema change breaks dependent readers |
| "Our services are small, it's not a problem yet"             | The coupling compounds; the longer you wait to fix it, the more expensive it becomes                  |
| "We can use DB views to decouple"                            | Views provide abstraction but not real decoupling; they still live in the same shared DB              |
| "This only matters at scale"                                 | It matters at any scale where services are independently developed by different teams                 |

---

### 🚨 Failure Modes & Diagnosis

**The 3AM Schema Incident**

**Symptom:** Service A goes down with `Unknown column 'qty'` at 3AM; root cause is Service B's migration ran at 2AM.

**Diagnostic Query:**

```sql
-- Find all service users accessing the renamed/dropped column
SELECT application_name, query, query_start
FROM pg_stat_activity
WHERE query LIKE '%qty%';  -- replace with column name
```

**Fix (short-term):** Revert Service B's migration; coordinate redeploy. Fix (long-term): break the shared dependency.

---

**Cross-Service Lock Contention**

**Symptom:** Service A's queries timeout periodically; root cause is Service B holds locks on the shared table.

**Diagnostic Query:**

```sql
SELECT blocked.pid, blocking.pid AS blocking_pid,
       blocked.query, blocking.query
FROM pg_stat_activity AS blocked
JOIN pg_stat_activity AS blocking
  ON blocking.pid = ANY(pg_blocking_pids(blocked.pid))
WHERE NOT blocked.granted;
```

**Fix:** Identify and fix Service B's locking query. Long-term: separate the data stores.

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**

- `Microservices` - defines the architectural context where this anti-pattern appears
- `Data Isolation per Service` - the principle this anti-pattern violates
- `Bounded Context` - defines the domain boundaries that should map to service data ownership

**Builds On This (learn these next):**

- `Database per Service` - the correct pattern that replaces this anti-pattern
- `Service Decomposition` - the process of decomposing a monolith, where this anti-pattern often appears
- `Strangler Fig Pattern` - the migration strategy from shared DB to Database per Service

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ WHAT IT IS   │ Multiple services sharing direct DB       │
│              │ access - the most common microservices    │
│              │ mistake                                   │
├──────────────┼───────────────────────────────────────────┤
│ PROBLEM IT   │ Creates schema, data, and operational     │
│ CAUSES       │ coupling; eliminates service autonomy     │
├──────────────┼───────────────────────────────────────────┤
│ KEY INSIGHT  │ You have a distributed monolith - all     │
│              │ microservices costs, none of the benefits  │
├──────────────┼───────────────────────────────────────────┤
│ HOW TO FIX   │ Database per Service + API/event-based    │
│              │ cross-service data sharing                │
├──────────────┼───────────────────────────────────────────┤
│ DETECT IT    │ Services connecting to same DB; cross-    │
│              │ service SQL joins; shared migration files │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "Microservices API, monolith database =   │
│              │  worst of both worlds"                    │
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ Database per Service → Strangler Fig →    │
│              │ Data Isolation per Service                │
└──────────────────────────────────────────────────────────┘
```


---

### 💎 Transferable Wisdom

**Reusable Engineering Principle:**
A shared database is a shared contract at the deepest level. A schema change in one service breaks other services without any API change, without any interface violation, and without any test failure at the API level. The database is a hidden API that bypasses all the service boundaries you thought you had established. Any shared storage between services (database, cache, filesystem) is a dependency that must be managed with the same discipline as an explicit API contract.

**Where else this pattern appears:**
- **Shared config files:** Multiple processes reading the same config file share a hidden contract - a change to the file format affects all readers without any API change.
- **Shared Redis namespaces:** Multiple services writing to the same Redis key namespace share implicit coupling - a key format change in one service breaks other services' cache reads.
- **Shared Kafka topic schemas:** Multiple services consuming from the same topic are coupled through the message schema - the same coupling as shared database schema, at the messaging layer.

---

### 💡 The Surprising Truth

Teams migrating from a shared database to separate databases often discover that the shared database was doing more work than they realised - specifically, acting as the consistency boundary for all cross-service operations. Removing the shared database removes this consistency boundary. Teams must then implement explicit eventual consistency patterns (sagas, outbox, event-driven updates) for every cross-service data relationship that previously relied on a single database transaction. The visible complexity of the microservices system increases during migration - which is the correct sign that the complexity was always there, just hidden inside the transactions.
---

### 🧠 Think About This Before We Continue

**Q1.** Your team inherited a system where three microservices share one PostgreSQL database. The Order Service, Inventory Service, and Customer Service all have direct table access to each other's data. The business is growing fast - two new services are being added next quarter. Describe a concrete 4-phase migration plan to reach full Database per Service, prioritising by risk, without requiring a "big bang" rewrite or significant downtime.

*Hint:* Think about what a 4-phase migration looks like concretely: Phase 1 (identify ownership: determine which service owns which tables, add API endpoints for each cross-service access pattern currently done via direct SQL); Phase 2 (dual access: route some cross-service reads through APIs while keeping the shared DB as fallback); Phase 3 (API only: remove all direct cross-service SQL, enforce API-only access); Phase 4 (split databases: move each service's tables to separate instances). Explore what the rollback strategy is at each phase and which phase has the highest risk.

**Q2.** A colleague argues: "Our three services use separate schemas in the same PostgreSQL instance. Each service only accesses its own schema. This satisfies Data Isolation - we don't need to move to separate DB instances." Evaluate this argument. Under what conditions is separate schemas sufficient, and under what conditions does it fall short? What additional risk remains even with perfect schema isolation?

*Hint:* Think about what separate schemas in the same PostgreSQL instance prevents vs what it doesn't prevent: logical isolation (no accidental JOIN) vs physical isolation. Separate schemas do NOT prevent: (1) a PostgreSQL instance outage affecting all services simultaneously; (2) a runaway query from one service consuming all connections; (3) one service's table growth filling the disk and blocking others' writes; (4) a DBA granting cross-schema access under operational pressure. Separate schemas are logical isolation; separate instances are physical isolation. The choice depends on your operational failure modes.

**Q3 (Design Trade-off):** Three months after completing migration to Database per Service, the data team requires real-time analytics (sub-second latency) joining Order Service, Customer Service, and Inventory Service data. Design the analytics architecture that meets the latency requirement without violating data isolation.

*Hint:* Think about what 'sub-second analytics joining 3 service databases' requires: a read model that has already joined and denormalised the data from all 3 services, so the analytics query hits a single table. Explore whether an event-driven analytics store (each service publishes events to Kafka, a stream processor joins and aggregates into a denormalised analytics table, queries hit the analytics store) provides sub-second read latency while maintaining write isolation, and what consistency lag exists between a service event and the analytics store update (typically milliseconds to seconds).
