---
layout: default
title: "Shared Database Anti-Pattern"
parent: "Microservices"
nav_order: 660
permalink: /microservices/shared-database-anti-pattern/
number: "660"
category: Microservices
difficulty: ★★★
depends_on: "Data Isolation per Service, Microservices Architecture"
used_by: "Database per Service, CQRS in Microservices"
tags: #advanced, #microservices, #distributed, #database, #architecture, #pattern
---

# 660 — Shared Database Anti-Pattern

`#advanced` `#microservices` `#distributed` `#database` `#architecture` `#pattern`

⚡ TL;DR — The **Shared Database Anti-Pattern** occurs when multiple microservices read from and write to the same database directly. It creates implicit coupling through the schema: one service's schema change can break another at runtime, services cannot scale independently, and different services' queries contend for the same DB resources. The fix is **Database per Service** with API/event-driven integration.

| #660            | Category: Microservices                                | Difficulty: ★★★ |
| :-------------- | :----------------------------------------------------- | :-------------- |
| **Depends on:** | Data Isolation per Service, Microservices Architecture |                 |
| **Used by:**    | Database per Service, CQRS in Microservices            |                 |

---

### 📘 Textbook Definition

The **Shared Database Anti-Pattern** (also known as **Integration Database** — Martin Fowler) describes a microservices architecture where multiple services share a single database — querying and modifying shared tables directly, often with JOINs across logical service boundaries. This was common in SOA (Service-Oriented Architecture) and early microservices migrations. The anti-pattern creates **schema coupling**: the database schema becomes the integration contract between services, bypassing API boundaries. Consequences: schema changes in one service's tables require coordinated deployment of all services that touch those tables; services cannot adopt different database technologies; one service's heavy queries or long-running transactions can degrade other services' performance; database becomes the single point of failure for the entire system; and independent scaling is impossible (all services scale together with the database). Chris Richardson (microservices.io) and Sam Newman (Building Microservices) both identify the shared database as the most common microservices anti-pattern.

---

### 🟢 Simple Definition (Easy)

Multiple services all using the same database is like multiple departments all working out of the same shared spreadsheet. If one department changes the column names, everyone's formulas break. If one department's massive report query makes the spreadsheet slow, everyone suffers. The fix: each department gets its own system, and they share data by sending each other reports (events/API calls) — not by editing the same file.

---

### 🔵 Simple Definition (Elaborated)

`OrderService`, `PaymentService`, and `ShippingService` all query the same `ordersdb` PostgreSQL database. `OrderService` renames `customer_name` to `customer_full_name` for a new feature. `PaymentService` and `ShippingService` break at 2am on Saturday when the migration runs — their queries now return `null`. Even if the tables are in different schemas, they're in the same physical database: `OrderService`'s massive analytics report at month-end locks the database and causes payment processing timeouts. These problems disappear when each service has its own database.

---

### 🔩 First Principles Explanation

**Why the shared database feels appealing — and why it fails:**

```
INITIAL APPEAL:
  1. Simple: one DB to manage, one connection pool, one backup
  2. JOINs work: SELECT o.*, c.name FROM orders o JOIN customers c ON ...
  3. No distributed transactions needed: ACID across tables in same DB
  4. No event infrastructure: no Kafka, no event schemas

WHY IT FAILS AT SCALE:

PROBLEM 1 — SCHEMA COUPLING (deploy coupling):
  OrderService adds column: ALTER TABLE orders ADD COLUMN discount_code VARCHAR(50)
  ShippingService INSERT query: INSERT INTO orders (id, status) VALUES (?, ?)
  → Postgres: OK (new column nullable, INSERT still works)
  But next migration: ALTER TABLE orders ALTER COLUMN discount_code SET NOT NULL
  → ShippingService INSERT: fails (cannot insert NULL into NOT NULL column)
  → ShippingService production writes failing — needs emergency deploy
  → RESULT: OrderService and ShippingService must be deployed TOGETHER

PROBLEM 2 — PERFORMANCE COUPLING (resource contention):
  Analytics team runs report: SELECT COUNT(*), SUM(amount) FROM orders
                              GROUP BY product_id, EXTRACT(MONTH FROM created_at)
  This query: full table scan, 100M rows, 45 seconds.
  Simultaneously: payment processing queries slowed (shared I/O, shared lock manager)
  → Checkout latency spikes from 50ms to 3+ seconds during month-end reports
  → RESULT: OrderService and AnalyticsService compete for the same resources

PROBLEM 3 — INDEPENDENT SCALING FAILURE:
  PaymentService needs more database connections (high transaction volume).
  OrderService needs more CPU (complex order calculation).
  Shared DB: cannot scale PaymentService's DB independently.
  Must scale the ENTIRE shared database instance.
  Cost: scaling the shared DB scales resources for ALL services simultaneously.
  → RESULT: wasted resources, no independent scaling

PROBLEM 4 — TECHNOLOGY LOCK-IN:
  All services must use the same database technology.
  InventoryService would benefit from Redis (in-memory, O(1) stock lookups).
  Cannot adopt Redis because InventoryService data is in shared PostgreSQL.
  → RESULT: suboptimal technology choices forced on all services

PROBLEM 5 — SINGLE POINT OF FAILURE:
  Shared DB downtime: ALL services fail simultaneously.
  Proper microservices: DB failure affects only the owning service.
  → RESULT: one DB failure = total system outage
```

**Identifying the anti-pattern in code reviews:**

```java
// 🚩 RED FLAG: Service imports @Entity class from a different service's package:
import com.example.customerservice.domain.Customer;  // ← CustomerService entity
import com.example.productservice.domain.Product;    // ← ProductService entity

@Service
public class OrderServiceImpl {
    @Autowired CustomerRepository customerRepository;  // ← accessing CustomerService's DB
    @Autowired ProductRepository productRepository;   // ← accessing ProductService's DB

    public Order createOrder(CreateOrderRequest request) {
        // 🚩 VIOLATION: joining across service boundaries in application code
        Customer customer = customerRepository.findById(request.getCustomerId()).orElseThrow();
        Product product = productRepository.findById(request.getProductId()).orElseThrow();
        return new Order(customer.getName(), product.getPrice(), request.getQuantity());
    }
}
// CORRECT: OrderService calls CustomerService API + ProductService API
// OR: uses local projections updated by events
```

**The "strangler fig" migration path — from shared DB to isolated DBs:**

```
STEP 1: IDENTIFY (assess current state)
  Map: which tables does each service read/write?
  Identify: tables shared across 3+ services (highest risk)
  Identify: tables owned by exactly one service (easiest to migrate)

STEP 2: OWN (assign table ownership)
  Declare: "CustomerService owns the 'customers' table."
  Add: DB-level access grants (only CustomerService DB user can write to 'customers')
  Other services: still read-only access (transitional)

STEP 3: ENCAPSULATE (replace cross-service DB reads with API calls)
  OrderService currently: SELECT name FROM customers WHERE id = ?
  Replace with: GET http://customer-service/api/v1/customers/{id}
  Feature flag: toggle between old DB read and new API call
  Run both in parallel briefly → validate equivalence → remove DB read

STEP 4: MIGRATE (physically separate the database)
  Once no service reads CustomerService's tables directly:
  Create separate 'customerdb' PostgreSQL instance
  Migrate data: pg_dump + pg_restore
  Update CustomerService connection strings
  Remove shared DB access for CustomerService tables
  Validate: no other service has connection credentials for 'customerdb'

STEP 5: REPEAT per service
  Priority: high-coupling tables first (where schema changes cause most pain)
  Takes: months to years for large legacy systems
```

---

### ❓ Why Does This Exist (Why Before What)

The shared database pattern was the default in enterprise Java (J2EE) and SOA systems where "services" were just different modules of the same application sharing a database. When organisations split these systems into "microservices" without splitting the database, they got distributed monolith — the worst of both worlds: distributed system complexity WITHOUT independent deployability. The anti-pattern persists because DB separation is hard: it requires resolving distributed data queries, handling cross-service joins, and introducing event infrastructure.

---

### 🧠 Mental Model / Analogy

> The Shared Database Anti-Pattern is like having all employees work on the same Google Doc simultaneously. Simple for a 3-person startup: everyone sees everything, edits are immediate. Catastrophic for 500 people: one person's bulk replace breaks everyone's work; one department's charts slow down the document; you can't give Finance a different tool without migrating all their data out. The fix: each department has their own document (database), and they share data through official exports/imports (events/APIs) — not by editing each other's documents.

---

### ⚙️ How It Works (Mechanism)

**Detecting shared database access in a Spring Boot codebase:**

```bash
# Find services that import entity classes from other services:
grep -r "import com.example.customerservice" ./order-service/src/
grep -r "import com.example.productservice" ./order-service/src/

# Find datasource connections (all services pointing to same DB):
grep -r "spring.datasource.url" ./*/src/main/resources/application*.yml
# If all show: jdbc:postgresql://shared-db:5432/appdb → Shared Database Anti-Pattern

# Find direct SQL queries joining across logical service tables:
grep -r "JOIN customers" ./order-service/src/
grep -r "JOIN products" ./payment-service/src/
```

---

### 🔄 How It Connects (Mini-Map)

```
Microservices Architecture
(autonomous services, independent deployment)
        │
        ▼
Shared Database Anti-Pattern  ◄──── (you are here)
(violation of service autonomy at data layer)
        │
        ├── Database per Service → the correct pattern (fix)
        ├── Data Isolation per Service → the principle being violated
        ├── CQRS → cross-service queries solved via read projections
        └── Event-Driven Microservices → replaces cross-service DB reads
```

---

### 💻 Code Example

**Before/after — migrating from shared DB to API:**

```java
// ❌ BEFORE: OrderService directly joins customers + products (shared DB):
@Query("""
    SELECT o.id, c.name, p.title, o.quantity, o.total
    FROM orders o
    JOIN customers c ON o.customer_id = c.id
    JOIN products p ON o.product_id = p.id
    WHERE o.id = :orderId
    """)
OrderDetailView findOrderDetail(@Param("orderId") String orderId);

// ✅ AFTER: OrderService fetches from APIs + uses local projections
@Service
class OrderDetailService {
    // Local projections (updated by events — no cross-DB access):
    @Autowired CustomerProjectionRepository customerProjection;
    @Autowired ProductProjectionRepository productProjection;
    @Autowired OrderRepository orderRepository;

    public OrderDetailResponse getOrderDetail(String orderId) {
        Order order = orderRepository.findById(orderId).orElseThrow();
        CustomerProjection customer = customerProjection.findById(order.getCustomerId())
            .orElseGet(() -> CustomerProjection.unknown());  // graceful fallback
        ProductProjection product = productProjection.findById(order.getProductId())
            .orElseGet(() -> ProductProjection.unknown());

        return new OrderDetailResponse(
            order.getId(), customer.getName(), product.getTitle(),
            order.getQuantity(), order.getTotal()
        );
    }
}
```

---

### ⚠️ Common Misconceptions

| Misconception                                                   | Reality                                                                                                                                                                                                                                                                                               |
| --------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Sharing a database is fine if services are in different schemas | Schema-level separation in the same database instance still shares: I/O resources, connection limits, backup/restore, and failure domain. It is better than no separation (prevents accidental JOINs) but does not achieve operational independence. Use it as a transitional step, not a final state |
| Splitting the database requires rewriting all the queries       | The strangler fig migration pattern allows gradual migration: introduce API calls alongside existing DB queries, validate they return equivalent results, then remove DB queries. No big-bang rewrite required                                                                                        |
| Separate databases make transactions impossible                 | Distributed transactions (Saga pattern) replace ACID transactions across services. The cost is eventual consistency — but this is an acceptable trade-off for most business operations                                                                                                                |
| The shared database is only a problem at scale                  | Schema coupling causes pain at ANY scale. A 3-service system with a shared database will have a Saturday 2am outage when one team's migration breaks another team's service. Scale amplifies the problem but doesn't create it                                                                        |

---

### 🔥 Pitfalls in Production

**Silent coupling through database-level foreign keys:**

```
SCENARIO:
  Both OrderService and CustomerService connect to the same DB.
  Schema has FK: orders.customer_id REFERENCES customers(id)

  CustomerService team: migrates customers to new 'customerdb' instance.
  Remove old 'customers' table from shared DB.
  → IMMEDIATE PRODUCTION FAILURE: orders.customer_id FK constraint now broken.
  All INSERT into orders fails with:
    ERROR: insert or update on table "orders" violates foreign key constraint

  Worse: if the FK was never noticed by the OrderService team,
  this failure is completely unexpected.

ROOT CAUSE: DB-level FK = implicit cross-service dependency not visible in code.

DETECTION BEFORE MIGRATION:
  SELECT
    tc.table_name,
    kcu.column_name,
    ccu.table_name AS foreign_table_name
  FROM information_schema.table_constraints AS tc
  JOIN information_schema.key_column_usage AS kcu ON tc.constraint_name = kcu.constraint_name
  JOIN information_schema.constraint_column_usage AS ccu ON ccu.constraint_name = tc.constraint_name
  WHERE tc.constraint_type = 'FOREIGN KEY';

  → Lists all FK relationships → identify cross-service FKs to remove before migration.

PREVENTION:
  In microservices: NO database-level FKs across logical service boundaries.
  Enforce referential integrity at APPLICATION level (check customer exists via API).
  DB-level FKs: only within a service's own tables.
```

---

### 🔗 Related Keywords

- `Database per Service` — the correct pattern that fixes the shared database anti-pattern
- `Data Isolation per Service` — the principle that shared databases violate
- `Event-Driven Microservices` — replaces cross-service DB reads with event subscriptions
- `CQRS in Microservices` — solves cross-service reporting queries correctly

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ ANTI-PATTERN │ Multiple services → same database         │
│ SYMPTOMS     │ Coordinated deploys, shared DB outages,   │
│              │ cross-service JOINs, schema coupling       │
├──────────────┼───────────────────────────────────────────┤
│ FIX          │ Database per Service + events/API          │
│ MIGRATION    │ Strangler Fig (gradual, not big-bang)      │
├──────────────┼───────────────────────────────────────────┤
│ RED FLAGS    │ Shared datasource URL in all services      │
│              │ Cross-service @Entity imports              │
│              │ DB-level FK across logical service tables  │
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** You're reviewing a PR for a "microservices" system where `OrderService` and `ReportingService` share the same PostgreSQL database. The team argues: "they're in separate schemas, it's fine." Construct a specific, concrete scenario (with table names, SQL statements, and deployment sequence) that demonstrates why separate schemas in the same database instance is still problematic. Include at least two distinct failure modes: one deployment-related and one operational/performance-related.

**Q2.** Your organisation has a 6-year-old monolith being decomposed into microservices. The strangler fig pattern is being applied. Currently: 3 services have been extracted (`CustomerService`, `ProductService`, `OrderService`) but they all still use the shared monolith database. What is the specific order of migration steps you would follow to safely extract `CustomerService` to its own database? At which step does `CustomerService` get its own database? What happens to the existing `orders.customer_id` foreign key during migration, and how do you validate the migration was successful without a production incident?
