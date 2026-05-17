---
id: MSV-052
title: Shared Database Anti-Pattern
category: Microservices
tier: tier-5-distributed-architecture
folder: MSV-microservices
difficulty: ★★★
depends_on: MSV-002, MSV-053
used_by: MSV-053
related: MSV-002, MSV-053, MSV-050, MSV-054, MSV-020, MSV-036
tags:
  - microservices
  - antipattern
  - deep-dive
  - database
status: complete
version: 4
layout: default
parent: "Microservices"
grand_parent: "Technical Dictionary"
nav_order: 52
permalink: /microservices/shared-database-anti-pattern/
---

# MSV-052 - Shared Database Anti-Pattern

⚡ TL;DR - The Shared Database Anti-Pattern occurs
when multiple microservices access the same database
(same schema, same tables). On the surface: convenient
(easy joins, no eventual consistency). In practice:
services become tightly coupled at the database level.
Deploying one service can break another. Schema
changes require coordinating all service teams. The
database becomes a single point of failure and a
scaling bottleneck. Violates microservice isolation
principles. Migration path: identify service boundaries,
assign table ownership, use events for cross-service
communication.

| #052 | Category: Microservices | Difficulty: ★★★ |
|:---|:---|:---|
| **Depends on:** | Microservice (definition), Database per Service | |
| **Used by:** | Database per Service | |
| **Related:** | Microservice, Database per Service, CQRS in Microservices, Outbox Pattern, API Gateway, Strangler Fig Pattern | |

---

### 🔥 The Problem This Solves

**THE MICROSERVICES LIE:**
A team "migrates to microservices" by splitting the
monolith into multiple services (order-service,
customer-service, product-service) but keeps them
all pointing to the same PostgreSQL database. They
have services (network boundaries) but no data
isolation. This is the distributed monolith: all
the complexity of distributed systems (network calls,
latency, deployment coordination) plus all the
coupling of a monolith (shared schema, shared database
schema lock, shared bottleneck). It's worse than
both. The Shared Database Anti-Pattern explains
WHY this fails and how to escape it.

---

### 📘 Textbook Definition

**Shared Database Anti-Pattern** is a microservices
antipattern where two or more services read from or
write to the same database instance, schema, or table.
This creates implicit coupling: any schema change
(rename column, add NOT NULL constraint, change
index) requires coordinating all services that
access the affected tables. Services cannot be deployed
or scaled independently. The shared database becomes
a coupling point that undermines the autonomy that
microservices are meant to provide. Defined in contrast
to the "Database per Service" pattern (MSV-053)
which each service owns its own data store. The
anti-pattern includes: shared schema (different
services, same tables), shared schema with separate
tables (still shared instance/credentials), or
direct SQL joins across service boundaries.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
Shared database = services coupled at data layer;
schema changes, scaling, failures are shared.
Defeats the purpose of microservices.

**One analogy:**
> Three companies sharing the same office building,
> same filing cabinets, same file organization system.
> Company A wants to rename a folder: must coordinate
> with B and C (they use it too). Company B has a
> security audit: all companies' files are at risk
> (shared access). Company C grows: can't expand
> storage (shared cabinets). They're independent
> companies on paper but operationally entangled.
> The filing cabinet is the shared database. True
> independence: each company has its own office and
> filing system. They share information by sending
> memos (events/APIs), not by sharing physical files.

**One insight:**
The Shared Database Anti-Pattern is almost always
an evolutionary mistake, not a design choice. Teams
start with a monolith, extract services for deployment
independence, but forget that the database is where
most coupling actually lives. You have achieved
service-level independence but zero data independence.
The database coupling is more constraining than
service coupling because it's invisible (no clear
interface contract) and pervasive (any service can
read/write any table).

---

### 🔩 First Principles Explanation

**WHY SHARED DATABASE CREATES COUPLING:**

```
3 TYPES OF DATABASE COUPLING:

1. SCHEMA COUPLING:
   order-service and customer-service both query:
   SELECT * FROM customers WHERE id = ?
   Change: rename customers.phone -> customers.phone_number
   Impact: BOTH services break
   Fix required: update both services simultaneously
   Deployment: must coordinate; one cannot go before other

2. TRANSACTION COUPLING:
   order-service: INSERT INTO orders ...
                  UPDATE customer_loyalty SET points += ?
   customer-service: SELECT SUM(points) FROM customer_loyalty
   Same transaction touches both tables
   Order-service "owns" loyalty points implicitly
   Customer-service reads loyalty written by order-service
   No clear ownership: race conditions possible

3. SCALING COUPLING:
   order-service: 10M orders/day; high write throughput
   customer-service: 100K customers; low write; high read
   Shared database: must be sized for highest peak
   (order-service peak) even though customer-service
   doesn't need that capacity
   Cannot choose different database technologies:
   order-service wants: Cassandra (high write)
   customer-service wants: PostgreSQL (complex queries)
   Shared database: one technology for both
   -> always a compromise
```

**RECOGNITION SIGNS:**

```
YOU HAVE THE ANTI-PATTERN IF:
  - Service A has SELECT permission on Service B's tables
  - Services share a database connection string
  - Schema migrations require coordinating multiple teams
  - You do JOINs across service boundaries in SQL
  - Service A's bugs corrupt Service B's data
  - One service's slow query degrades all other services
    (shared connection pool, shared DB server load)
  - Test environment: must run all services together
    because they share the same test database
  - Services are deployed together to avoid schema mismatch
```

---

### 🧪 Thought Experiment

**SCHEMA MIGRATION COORDINATION HELL:**

```
SCENARIO:
  customers table has: email (VARCHAR 100, NOT NULL)
  3 services use this table: orders, customers, loyalty
  
  Requirement: increase email max length to 200
  ALTER TABLE customers ALTER COLUMN email VARCHAR(200)
  
  PROBLEM: ALTER TABLE acquires a brief table lock
  During lock: all 3 services fail for 2-3 seconds
  At 100 req/sec: 200-300 requests fail
  
  BIGGER PROBLEM: After migration, revert?
  Decrease column size: data truncation risk
  Cannot safely rollback without coordinating all
  3 services to stop using the new length
  
  BIGGER PROBLEM: Table redesign
  customers table needs: add customer_segment column
  order-service wants to JOIN on segment for pricing
  loyalty-service does NOT want segment data there
  (should be in a separate segmentation service)
  
  Who owns the customers table?
  All 3 teams: their code touches it
  Nobody: feels ownership
  Migrations: political negotiations
  
COMPARE TO DATABASE PER SERVICE:
  customer-service owns customers table entirely
  Other services: subscribe to CustomerUpdated events
  Migration: customer-service team decides alone
  No coordination required
  Other services: update their local projections
  when they receive updated events
```

---

### 🧠 Mental Model / Analogy

> The Shared Database Anti-Pattern is like a city
> where all buildings share the same plumbing, electrical,
> and HVAC system. Building A wants to remodel:
> must coordinate with every other building (shared
> infrastructure). Building B overuses power: all
> buildings suffer brownouts. Building C's pipes
> burst: all buildings lose water. Each building
> is "independent" in name but not in practice.
> True independence: each building has its own
> utility connections. They connect to the city grid
> (shared network/events) via standardized interfaces
> (APIs/events), not by sharing internal infrastructure.

---

### 📶 Gradual Depth - Five Levels

**Level 1 - What it is (anyone can understand):**
The anti-pattern: multiple microservices using the
same database. Problem: they are not truly independent;
changing the database affects all of them at once.
Goal: each service should own its own data.

**Level 2 - How to identify it (junior developer):**
Signs: services share a database URL in config.
Schema migration takes all services offline. Cross-
service SQL JOINs exist. One service's slow query
affects another service's response time. Test
environment requires all services running (shared
test DB). If any of these: you have the anti-pattern.

**Level 3 - How to fix it (mid-level engineer):**
Migration path: (1) identify table ownership (which
service is the "system of record" for each table).
(2) Other services: stop direct DB access; call the
owner service's API or subscribe to its events.
(3) Move non-owner tables to the owner's schema.
(4) Establish event contracts for cross-service data.
(5) Implement CQRS projections for cross-service reads.

**Level 4 - Why it matters (senior engineer):**
The Shared Database Anti-Pattern prevents independent
deployability - the primary value proposition of
microservices. Without independent deployability:
microservices are costlier than a monolith (distributed
complexity without distributed benefits). Sam Newman
("Building Microservices"): "If you need to deploy
two services together to avoid breaking changes,
they should be one service." Shared database:
forces coordinated deployments indefinitely.

**Level 5 - Mastery (principal engineer):**
The most insidious form: separate schemas on the
same database instance. Not the same tables, but
same server. When order-service's connection pool
exhausts (high load): customer-service also cannot
connect (shared server connection limit). When the
database server needs an OS patch: both services
down simultaneously. This is operational coupling,
not just schema coupling. True isolation: separate
database instances (or managed services) per service.
For cost: shared read replicas are acceptable
(read-only coupling), but write master must be isolated.

---

### ⚙️ How It Works (Mechanism)

**MIGRATION STRATEGY FROM SHARED TO ISOLATED:**

```java
// PHASE 1: Identify table ownership
// customers table: customer-service owns it
// order-service is READING customers.name, customers.email

// PHASE 2: Create API abstraction
// Instead of: SQL JOIN orders o JOIN customers c
// order-service calls customer-service API:
@FeignClient(name = "customer-service")
public interface CustomerClient {
    @GetMapping("/customers/{id}")
    CustomerDto getCustomer(@PathVariable String id);
}

// PHASE 3: Replace SQL JOIN with API call
// (interim step - will replace with CQRS projection)
public OrderDetail getOrderDetail(OrderId orderId) {
    Order order = orderRepo.findById(orderId);
    // Replacing: JOIN customers c ON o.customer_id = c.id
    CustomerDto customer = customerClient
        .getCustomer(order.getCustomerId().toString());
    return OrderDetail.from(order, customer);
}

// PHASE 4: Replace API call with CQRS projection
// order-service subscribes to CustomerUpdated events
// Builds local projection: customer_view table
// Query: reads from local projection (no service call)

// PHASE 5: Remove shared DB access
// Remove customer-service's DB credentials from order-service
// Remove order-service's DB credentials from customer-service
// Schema migrations: no coordination needed
```

---

### 🔄 The Complete Picture - End-to-End Flow

```
BEFORE (Shared Database Anti-Pattern):

  order-service ----+
                    |--> shared PostgreSQL DB
  customer-service -+      (same tables)
  loyalty-service --+
  
  Deploy order-service: schema migration runs
  customer-service: schema changed under its feet
  loyalty-service: schema changed under its feet
  All 3: potentially broken simultaneously

AFTER (Database per Service):

  order-service ----> orders-db (PostgreSQL)
                      owns: orders, order_items
  
  customer-service -> customers-db (PostgreSQL)
                      owns: customers
  
  loyalty-service ---> loyalty-db (MongoDB)
                       owns: loyalty_accounts
  
  Cross-service data: via Kafka events
  Deploy order-service: only orders-db migration
  customer-service: unaffected
  loyalty-service: unaffected
  Each team: autonomous schema decisions
```

---

### 💻 Code Example

**Example 1 - Wrong vs Right: cross-service SQL JOIN**

```java
// BAD: order-service JOINs customer-service's table
@Repository
public class OrderRepository {
    public List<OrderWithCustomer> findOrdersWithCustomer() {
        // Cross-service JOIN: order-service accesses
        // customers table owned by customer-service
        return jdbc.query(
            "SELECT o.*, c.name, c.email " +
            "FROM orders o " +
            "JOIN customers c ON o.customer_id = c.id",
            rowMapper);
        // Problem: customer-service can never rename
        // the customers table without breaking this
    }
}
```

```java
// GOOD: CQRS projection - local read model
// (Built by subscribing to CustomerUpdated events)
@Repository
public class OrderQueryRepository {
    public List<OrderWithCustomer> findOrdersWithCustomer() {
        // Reads from local projection built from events
        // No cross-service table access
        return jdbc.query(
            "SELECT o.*, cv.name, cv.email " +
            "FROM orders o " +
            "JOIN customer_view cv " +  // LOCAL projection
            "ON o.customer_id = cv.customer_id",
            rowMapper);
        // customer_view: updated by CustomerUpdated events
        // customer-service: can rename anything freely
        // order-service: reads from its own copy
    }
}
```

---

### ⚖️ Comparison Table

| Aspect | Shared Database | Database per Service |
|---|---|---|
| **Schema changes** | Coordinate all services | Service team decides alone |
| **Independent deploy** | Must coordinate | True independence |
| **Technology choice** | One DB for all | Best DB for each service |
| **Scaling** | Scale entire DB | Scale per service needs |
| **Failure isolation** | DB failure = all down | DB failure = one service |
| **Cross-service data** | SQL JOIN (easy, but coupled) | Events/API (harder, but isolated) |

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| Separate schemas on same DB instance is Database per Service | Separate schemas on the same DB server is still the Shared Database Anti-Pattern for operations: shared connection pool, shared server resources, shared failure domain. True Database per Service means separate DB instances (or managed services). For cost constraints: separate schemas with careful resource limits is a pragmatic starting point, but is not the end goal. |
| The anti-pattern only matters at scale | Even for small teams (2-3 developers): shared database prevents independent deployability. Every schema migration must be coordinated. This creates developer friction that grows super-linearly with team size. The anti-pattern is harmful at any scale; it just becomes MORE painful at larger scale. |
| Fixing it requires a big-bang rewrite | Strangler Fig Pattern: incrementally add table ownership and event contracts. Start with the highest-friction tables (most commonly argued over). One service, one table, one event at a time. Teams in production have taken 12-18 months to complete the migration without downtime. |

---

### 🚨 Failure Modes & Diagnosis

**Deployed order-service schema migration; broke customer-service**

**Symptom:**
After deploying order-service v2.1 (which included
a schema migration that added a NOT NULL column to
the customers table without a default): customer-
service started throwing `null constraint violation`
when creating new customers. customer-service team
never knew about the migration.

**Root Cause:**
Shared database. order-service ran Flyway migration:
`ALTER TABLE customers ADD COLUMN marketing_opt_in
BOOLEAN NOT NULL`. customer-service INSERT query:
doesn't include `marketing_opt_in` in the column
list -> DB rejects INSERT. customer-service team:
not aware of migration, not included in review.

**Fix (immediate):**
```sql
-- Add default to make the column nullable initially
ALTER TABLE customers
  ALTER COLUMN marketing_opt_in
  SET DEFAULT false;
-- customer-service: INSERTs work again
-- order-service: reads the column correctly
```

**Fix (structural):** Implement Database per Service.
If `customers` is owned by customer-service:
order-service should not have migration scripts
that touch the customers table. Only customer-
service's Flyway migrations should modify customers.
Add CI/CD check: service X's migrations only affect
service X's tables (schema prefix or separate DB).

---

### 🔗 Related Keywords

**The solution:**
- `Database per Service` - each service owns its
  data store; the fix for this anti-pattern

**Enables after fixing:**
- `CQRS in Microservices` - projections replace
  cross-service SQL JOINs
- `Outbox Pattern` - atomic write + event for
  cross-service data propagation

**Related anti-patterns:**
- `Microservice` (definition) - shared DB violates
  the autonomy principle that defines microservices
- `Strangler Fig Pattern` - incremental migration
  away from shared DB

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ ANTI-PATTERN │ Multiple services, one database          │
│              │ Schema coupling defeats service autonomy  │
├──────────────┼───────────────────────────────────────────┤
│ SYMPTOMS     │ Coordinated deploys, cross-service JOINs  │
│              │ One migration breaks multiple services    │
├──────────────┼───────────────────────────────────────────┤
│ FIX          │ Database per Service; events for cross-   │
│              │ service data; CQRS projections for reads  │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "Distributed monolith: service split but  │
│              │  data coupling remains; fix: DB per svc"  │
└──────────────────────────────────────────────────────────┘
```

**If you remember only 3 things:**
1. Shared database = schema coupling = forced
   coordinated deployments = distributed monolith.
   Defeats the autonomy goal of microservices.
2. Signs: cross-service SQL JOINs, migrations break
   multiple services, services must deploy together.
3. Fix: Database per Service + events for cross-
   service data + CQRS projections for reads.

**Interview one-liner:**
"Shared Database Anti-Pattern: multiple microservices
access the same database. Creates schema coupling
(migrations require team coordination), operational
coupling (one service's load affects all), and
deployment coupling (coordinated releases to avoid
breaking changes). Creates a distributed monolith:
distributed complexity without distributed benefits.
Fix: Database per Service (separate DB instances
or schemas), event-based data propagation, CQRS
read projections for cross-service queries."

---

### 💡 The Surprising Truth

The Shared Database Anti-Pattern is so common because
it's the natural migration path from monolith to
microservices. The monolith has one database. You
extract a service. The service still needs the same
data. The easiest path: keep pointing at the same
database. This works for days or weeks. After 6
months with 5 teams and 10 services all pointing
at the same database: the friction is unbearable.
Migrations cause incidents. Deployments require
cross-team Slack messages. Nobody "owns" the shared
schema. The irony: you split services for team
autonomy; the shared database eliminated all the
autonomy you were trying to gain.

---

### ✅ Mastery Checklist

**You've mastered this when you can:**
1. **IDENTIFY** Given a microservices architecture
   diagram, identify all instances of the Shared
   Database Anti-Pattern. Include: same DB instance
   (obvious), same schema different tables (schema
   coupling), and separate schemas but same server
   (operational coupling).
2. **MIGRATION PLAN** For a monolith with 20 tables
   and 4 proposed services: map table ownership,
   identify tables that are currently accessed by
   multiple future services, propose the migration
   plan using Strangler Fig Pattern.
3. **CQRS REPLACEMENT** Replace a specific cross-
   service SQL JOIN with a CQRS projection. Specify:
   which events trigger projection updates, what the
   projection schema looks like, and how you handle
   the initial data load for existing records.
4. **INCIDENT** Describe an incident caused by a
   shared database (schema change broke another
   service). Explain the root cause analysis and
   the long-term architectural fix.
5. **PRAGMATICS** When is a shared database acceptable
   (not just anti-pattern)? Describe 2 scenarios
   where the trade-off is justified (startup, monolith
   not yet split, etc.).

---

### 🧠 Think About This Before We Continue

**Q1.** You join a startup as the first architect.
5 microservices all share a single PostgreSQL database.
The database has 50 tables. The team of 8 engineers
has 3 months before a major customer demo. Propose
a prioritized migration plan. Which tables do you
isolate first? What is the minimum viable migration
that reduces the most friction in 3 months?

**Q2.** Two services share a database but you've
been told: "We can never change this because of
compliance - auditors require all data in a single
database for query access." Is this compliance
requirement real or misunderstood? What architectural
pattern allows compliance (all data accessible in
one place for auditing) while maintaining service
isolation?

**Q3.** You're reviewing a pull request for a new
microservice. The PR includes a Flyway migration
that ALTERs a table owned by a different service.
How do you respond? What is the correct process
for this change? Draft the PR comment.