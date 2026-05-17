---
id: MSV-053
title: Database per Service
category: Microservices
tier: tier-5-distributed-architecture
folder: MSV-microservices
difficulty: ★★★
depends_on: MSV-002, MSV-052
used_by: MSV-049, MSV-050, MSV-052
related: MSV-052, MSV-050, MSV-054, MSV-049, MSV-046, MSV-020
tags:
  - microservices
  - database
  - deep-dive
  - pattern
status: complete
version: 4
layout: default
parent: "Microservices"
grand_parent: "Technical Dictionary"
nav_order: 53
permalink: /microservices/database-per-service/
---

# MSV-053 - Database per Service

⚡ TL;DR - Database per Service: each microservice
owns its own database (separate instance or at minimum
separate schema with enforced boundaries). No other
service can directly access its data. Cross-service
data is accessed via APIs or events. Enables: true
service autonomy (independent schema evolution,
independent technology choice), independent scaling,
failure isolation. Trade-offs: no cross-service SQL
JOINs (use CQRS projections or API aggregation),
eventual consistency for cross-service data, higher
operational complexity (more databases to manage).

| #053 | Category: Microservices | Difficulty: ★★★ |
|:---|:---|:---|
| **Depends on:** | Microservice (definition), Shared Database Anti-Pattern | |
| **Used by:** | Eventual Consistency in Microservices, CQRS in Microservices, Shared Database Anti-Pattern | |
| **Related:** | Shared Database Anti-Pattern, CQRS in Microservices, Outbox Pattern, Eventual Consistency in Microservices, Saga Pattern, API Gateway | |

---

### 🔥 The Problem This Solves

With shared database: schema changes require coordinating
multiple teams. One service's load degrades all others.
Deployments must be coordinated. Technology is locked
(you can't use MongoDB for one service if it must
share PostgreSQL with others). Database per Service
enables each service team to: evolve schema independently,
choose the best database technology for their use
case, scale their database based on their own load,
and deploy without coordinating with other teams.

---

### 📘 Textbook Definition

**Database per Service** is a microservice data
management pattern where each service has its own
database. The database (including schema, tables,
indexes, and stored procedures) is owned exclusively
by the service. Other services cannot access it
directly (no direct SQL queries, no shared credentials).
Cross-service data access is through the service's
API (HTTP/gRPC) or via events (Kafka/RabbitMQ).
Each service can use the database technology best
suited to its requirements: relational (PostgreSQL,
MySQL), document (MongoDB), key-value (Redis),
graph (Neo4j), time-series (InfluxDB), or search
(Elasticsearch). The pattern is the primary mechanism
for achieving data isolation in microservices.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
Database per Service: one service = one database.
No shared access. Cross-service data via API or events.
Enables true autonomy.

**One analogy:**
> Each department at a company has its own filing
> cabinet (database). HR has employee records. Finance
> has financial records. Engineering has project records.
> One department CANNOT open another department's
> cabinet. To get information: you request it via
> official channels (API: send a request form; get
> the answer back). Or: HR publishes a company directory
> (events: employee names available to all departments).
> HR can reorganize their filing system (schema change)
> without telling Engineering. Finance can lock their
> cabinets (security policy) independently. If HR's
> cabinet is on fire (service failure): Finance and
> Engineering continue working.

**One insight:**
Database per Service is not primarily about technology
choice or scaling - it's about TEAM AUTONOMY. When
each service team owns their database completely:
they can make schema changes on their own release
cycle, with their own testing and rollback plan.
No Slack messages to 3 other teams. No coordinated
release windows. No schema governance committee.
This autonomy is the primary driver of microservice
velocity at scale.

---

### 🔩 First Principles Explanation

**DATABASE ISOLATION LEVELS:**

```
LEVEL 1 - TABLE ISOLATION (weakest, not recommended):
  All services: same DB instance, same schema
  Convention: each service only touches its tables
  Problem: convention not enforced; any service
  can query any table (SELECT * FROM other_service_table)
  Schema migrations: still affect all services
  NOT Database per Service

LEVEL 2 - SCHEMA ISOLATION (pragmatic starting point):
  All services: same DB instance, separate schemas
  order-service -> orders schema (orders.orders,
                                  orders.order_items)
  customer-service -> customers schema
  Enforce: separate DB credentials per service
  (order-service user: only has access to orders schema)
  Benefit: schema changes isolated per schema
  Risk: shared DB server: operational coupling remains
  When to use: cost constraints; early stage migration

LEVEL 3 - INSTANCE ISOLATION (recommended for production):
  Each service: separate DB instance
  order-service -> orders-db (PostgreSQL)
  customer-service -> customers-db (PostgreSQL)
  analytics-service -> analytics-db (Elasticsearch)
  catalog-service -> catalog-db (MongoDB)
  Benefit: full isolation (schema + operational)
  Cost: more DB instances to manage
  Use: RDS, Cloud SQL, Atlas (managed services reduce
       management overhead)

LEVEL 4 - TECHNOLOGY DIVERSITY (polyglot persistence):
  Each service: best DB for its needs
  OLTP (orders): PostgreSQL
  Session/cache: Redis
  Catalog search: Elasticsearch
  Recommendations: Neo4j (graph)
  Events: EventStoreDB
  Time-series metrics: InfluxDB
  Document/flexible: MongoDB
  Trade-off: operational knowledge diversity
```

**CROSS-SERVICE DATA ACCESS PATTERNS:**

```
PATTERN 1: API CALL AT QUERY TIME
  order-service needs customer name:
  -> HTTP GET /customers/{id}
  -> customerClient.getCustomer(id)
  Use when: low volume, real-time required
  Risk: availability coupling (customer-service down
        -> order-service reads fail)
  Mitigation: resilience patterns (Circuit Breaker,
              timeout, fallback)

PATTERN 2: CQRS READ PROJECTION (preferred for reads)
  order-service subscribes to CustomerUpdated events
  Builds local customer_view table (copy of relevant
  fields: customer_id, name, email, tier)
  Read: from local customer_view (no service call)
  Eventual consistency: ~100ms lag
  Availability: reads work even if customer-service
  is down (using last known data)

PATTERN 3: API COMPOSITION (for complex queries)
  API Gateway aggregates responses from multiple
  services at query time
  Useful for: UI-specific composite queries
  Risk: availability of all component services
  
PATTERN 4: SAGA (for cross-service writes)
  Distributed transaction across services
  Without shared database: cannot use 2PC
  Use: Saga pattern with events/orchestrator
  Consistency: eventual (saga may take seconds)
```

---

### 🧪 Thought Experiment

**POLYGLOT PERSISTENCE - CHOOSING THE RIGHT DB:**

```
E-COMMERCE PLATFORM services and data requirements:

order-service:
  Needs: ACID transactions (payment + inventory)
         Relational joins (order_items)
         Strong consistency within service
  Choice: PostgreSQL (ACID, relational, battle-tested)

product-catalog-service:
  Needs: Full-text search ("find shoes with good reviews")
         Flexible schema (different attributes per category)
         Read-heavy (1000x more reads than writes)
  Choice: Elasticsearch (search) + MongoDB (flexible)
         Or: PostgreSQL with Elasticsearch for search only

recommendation-service:
  Needs: Graph queries ("customers who bought X also bought")
         Relationship traversals
  Choice: Neo4j (native graph DB)

session-service:
  Needs: Microsecond reads/writes
         TTL (sessions expire)
         No persistence required
  Choice: Redis (in-memory, TTL support)

analytics-service:
  Needs: OLAP queries (large aggregations)
         Time-series data (events over time)
         Append-only writes
  Choice: ClickHouse or BigQuery
  
With shared database: NONE of these optimizations
possible. With Database per Service: each service
chooses the best tool for its job.
```

---

### 🧠 Mental Model / Analogy

> Database per Service is like specialized tools
> in a workshop. A carpenter has woodworking tools
> (chisels, planes). A welder has welding equipment
> (MIG welder, grinder). A machinist has metalworking
> tools (lathe, mill). Each trades person uses the
> tools optimized for their material. Sharing one
> set of tools (shared database): constant waiting
> (contention), wrong tool for the job (SQL for
> graph queries), one broken tool stops everyone
> (single DB failure). Separate workshops (Database
> per Service): each person fully equipped, works
> independently, optimized toolset. They share
> outputs (APIs/events), not tools (databases).

---

### 📶 Gradual Depth - Five Levels

**Level 1 - What it is (anyone can understand):**
Each service has its own database that only it can
access. To get data from another service: ask the
service, not its database. Like: each department
has its own files; you don't search other departments'
cabinets.

**Level 2 - How to apply it (junior developer):**
Practical rules: (1) service credentials are exclusive
(order-service DB user: no access to customer DB).
(2) No Flyway/Liquibase migrations for tables owned
by other services. (3) No ORMs with entities that
cross service boundaries. (4) Cross-service reads:
via API client or Kafka consumer projection.

**Level 3 - How to implement (mid-level engineer):**
For Kubernetes: each service has its own K8s Secret
for DB credentials. Separate DB instances in cloud
(RDS PostgreSQL per service, or separate schemas
with enforced credentials). Flyway migrations: in
each service's resources/db/migration - only touches
that service's schema. Integration tests: each service
test container has its own embedded DB (H2 or
Testcontainers PostgreSQL).

**Level 4 - Why it matters (senior engineer):**
Database per Service enables the "Reverse Conway
Maneuver": design service boundaries to match the
team boundaries you want. Each team owns their service
and their database. No cross-team DB access means
no accidental coupling. The database boundary enforces
the domain boundary. If two teams fight over schema
ownership: the domain boundary is wrong; split or
merge accordingly. The data model is the clearest
signal of true service decomposition.

**Level 5 - Mastery (principal engineer):**
At scale: Database per Service creates the data
fabric challenge. 50 microservices = 50 databases
= 50 sets of: connection pools, backups, failover
configuration, monitoring, schema migration pipelines,
encryption keys. Managed cloud databases reduce
but don't eliminate this overhead. Solutions:
centralized DBA tooling (Flyway Hub, Liquibase Pro),
service mesh data plane metrics (database calls
via Istio sidecar), shared observability (all DB
logs to centralized Datadog/Prometheus). And:
balance service granularity with database overhead.
Fine-grained microservices may share a database if
both are owned by the same team (pragmatic: separate
schemas, same team = acceptable).

---

### ⚙️ How It Works (Mechanism)

```yaml
# Kubernetes: separate DB secrets per service
apiVersion: v1
kind: Secret
metadata:
  name: order-service-db-secret
type: Opaque
data:
  # order-service DB user: only has access to
  # orders schema in orders-db
  url: amRiYzpwb3N0Z3Jlc3FsOi8vb3JkZXJzLWRiOjU0MzIv...
  username: b3JkZXItc3Zj  # order-svc (limited perms)
  password: ...
---
apiVersion: v1
kind: Secret
metadata:
  name: customer-service-db-secret
type: Opaque
data:
  # customer-service DB user: only has access to
  # customers schema in customers-db
  url: amRiYzpwb3N0Z3Jlc3FsOi8vY3VzdG9tZXJzLWRiOjU0...
  username: Y3VzdG9tZXItc3Zj  # customer-svc
  password: ...
```

```java
// Spring Boot: service reads its own DB only
@Configuration
public class OrderDatabaseConfig {

    @Bean
    @ConfigurationProperties("spring.datasource.orders")
    public DataSource ordersDataSource() {
        // Reads from: ORDERS_DB_URL env var
        // Credential: order-service-db-secret
        // Accesses: ONLY orders schema
        return DataSourceBuilder.create().build();
    }

    @Bean
    public JdbcTemplate ordersJdbcTemplate(
            @Qualifier("ordersDataSource") DataSource ds) {
        return new JdbcTemplate(ds);
    }
    // NO: customer DB datasource here
    // NO: CustomerEntity in this service's JPA
}

// WRONG: cross-service DB access
@Entity
@Table(name = "customers") // Wrong: customer-service's table!
public class Customer { ... }  // Not allowed!

// CORRECT: cross-service data via event projection
@Entity
@Table(name = "customer_view")  // Local projection!
public class CustomerView {
    private String customerId;
    private String name;   // Copied from events
    private String email;  // Not the source of truth
    // Source: CustomerUpdated events from customer-service
}
```

---

### 🔄 The Complete Picture - End-to-End Flow

```
DATABASE PER SERVICE TOPOLOGY:

  order-service
  |-- orders-db (PostgreSQL)
  |   |-- schema: orders
  |   |-- tables: orders, order_items, customer_view
  |   |   (customer_view = local CQRS projection)
  |-- Kafka producer: OrderCreated, OrderCancelled
  |-- Kafka consumer: CustomerUpdated, ProductUpdated
  
  customer-service
  |-- customers-db (PostgreSQL)
  |   |-- schema: customers
  |   |-- tables: customers, addresses, preferences
  |-- Kafka producer: CustomerCreated, CustomerUpdated
  
  catalog-service
  |-- catalog-db (Elasticsearch + MongoDB)
  |   |-- Elasticsearch: product search index
  |   |-- MongoDB: product catalog documents
  |-- Kafka producer: ProductUpdated, ProductCreated
  
  Data flow:
  CustomerUpdated -> [order-service consumes]
                     -> updates customer_view
  GET /orders?customerId=123:
    -> JOIN orders + customer_view (local, no call)
    -> returns result without calling customer-service
```

---

### 💻 Code Example

**Example 1 - Wrong vs Right: accessing another service's DB**

```java
// BAD: order-service uses customer-service's DB directly
@Repository
public class OrderRepo {
    // TWO datasources = shared database anti-pattern
    @Autowired
    @Qualifier("ordersDb")
    private JdbcTemplate ordersDb;
    
    @Autowired
    @Qualifier("customersDb")  // WRONG: not our DB!
    private JdbcTemplate customersDb;
    
    public List<OrderDto> getOrdersWithCustomer() {
        // Accessing customer-service's tables directly!
        Map<String,String> customers = customersDb.query(
            "SELECT id, name FROM customers", ...)
            .stream().collect(...);
        return ordersDb.query("SELECT * FROM orders", ...)
            .stream().map(o -> new OrderDto(
                o, customers.get(o.customerId)))
            .collect(toList());
    }
}
```

```java
// GOOD: order-service reads its local CQRS projection
@Repository
public class OrderRepo {
    @Autowired
    private JdbcTemplate ordersDb;  // ONLY orders DB

    public List<OrderDto> getOrdersWithCustomer() {
        // customer_view is a LOCAL table in orders schema
        // Populated by consuming CustomerUpdated events
        // No access to customer-service's database
        return ordersDb.query(
            "SELECT o.*, cv.name AS customer_name " +
            "FROM orders o " +
            "JOIN customer_view cv " +
            "  ON o.customer_id = cv.customer_id",
            rowMapper);
    }
}
// customer-service can change its schema freely
// order-service: unaffected (reads its own projection)
```

---

### ⚖️ Comparison Table

| Aspect | Shared Database | Database per Service |
|---|---|---|
| **Schema autonomy** | Coordinated changes | Independent changes |
| **Technology choice** | One for all | Best for each |
| **Failure isolation** | One DB down = all down | One DB down = one service |
| **Cross-service reads** | SQL JOINs (easy) | Events/API + projections |
| **Cross-service writes** | 2PC transaction | Saga pattern (eventual) |
| **Operational overhead** | Low (one DB) | High (many DBs) |

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| Database per Service means every service needs a separate cloud DB instance | Not necessarily. For teams starting out: separate schemas with enforced credentials (schema-level isolation) is a practical starting point. As scale warrants: migrate to separate instances. The key principle is data ownership and access control, not the physical infrastructure topology. |
| Cross-service reads are impossible without shared DB | They're possible via: (1) API call to owner service, (2) CQRS projection (local copy built from events), (3) GraphQL federation. Each has trade-offs. The CQRS projection is most scalable: reads are local, no runtime dependency on other services. The trade-off: eventual consistency and projection maintenance. |
| All services must use different databases (polyglot) | Using the same database technology (e.g., all PostgreSQL) but different instances IS Database per Service. Polyglot persistence (different technologies) is an additional optimization but not required. Many successful microservices architectures: all PostgreSQL, separate instances. |

---

### 🚨 Failure Modes & Diagnosis

**Cascading failure: customer-service DB down, order reads fail**

**Symptom:**
Customer-service database has a failover event
(primary down, replica promotion: 30 seconds).
During those 30 seconds: order-service GET /orders
API also returns 503. Order-service has no dependency
on customer data for its own order reads.

**Root Cause:**
Despite having a "separate database", order-service
still makes a synchronous API call to customer-service
at query time to fetch customer names. Customer-service
is unavailable during DB failover -> order-service's
reads fail. Operational coupling via synchronous API.

**Fix:**
1. Implement CQRS projection in order-service:
   consume CustomerUpdated events and build a local
   `customer_view` table. Reads: from local projection
   (no runtime dependency on customer-service).
2. Short-term: add Circuit Breaker (Resilience4j)
   around customerClient calls. If circuit open:
   return order WITHOUT customer name (graceful
   degradation: show order data, indicate customer
   name temporarily unavailable).
3. Long-term: CQRS projection eliminates the runtime
   dependency entirely. Customer-service DB failover:
   no impact on order reads.

---

### 🔗 Related Keywords

**The problem:**
- `Shared Database Anti-Pattern` - the opposite
  pattern; what Database per Service prevents

**Enables:**
- `CQRS in Microservices` - projections needed
  for cross-service reads without shared DB
- `Eventual Consistency in Microservices` - cross-
  service data is eventually consistent

**Required patterns:**
- `Outbox Pattern` - atomic write + event publish
  when cross-service data propagation needed
- `Saga Pattern` - cross-service transactions
  without 2PC (no shared database)

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ PATTERN      │ One service = one database (exclusively)  │
│              │ No cross-service direct DB access         │
├──────────────┼───────────────────────────────────────────┤
│ BENEFIT      │ Schema autonomy, tech choice, isolation   │
│              │ Independent deployability per service     │
├──────────────┼───────────────────────────────────────────┤
│ CROSS-SVC    │ Reads: CQRS projections (preferred)       │
│              │ Writes: Saga pattern; API for sync calls  │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "Service owns data; others ask, not grab; │
│              │  polyglot persistence as bonus benefit"   │
└──────────────────────────────────────────────────────────┘
```

**If you remember only 3 things:**
1. One service = one database (exclusive ownership).
   No other service reads or writes it directly.
2. Cross-service reads: CQRS projection (local copy
   built from events). No runtime API calls at query
   time.
3. Cross-service writes: Saga pattern. No 2PC.
   Accept eventual consistency.

**Interview one-liner:**
"Database per Service: each microservice owns its
database exclusively (separate instance or strictly
enforced schema). No cross-service direct access.
Benefits: schema autonomy (each team evolves schema
independently), technology choice (best DB per
use case), failure isolation (one DB failure = one
service). Trade-offs: cross-service reads need CQRS
projections (eventual consistency), cross-service
writes need Saga (no 2PC), higher operational overhead
(more databases to manage). The operational overhead
is offset by managed cloud DB services."

---

### 💡 The Surprising Truth

The hardest part of Database per Service is not the
technology - it's identifying service boundaries
that result in minimal cross-service data access.
If you find that every feature requires data from
4 different services (each with its own DB), and
you're building CQRS projections and Sagas for every
user story: your service boundaries are wrong. The
boundaries should correspond to real business
boundaries (Domain-Driven Design bounded contexts)
where most operations are self-contained within
one service. Poor service decomposition + Database
per Service = immense complexity for no benefit.
Get the service boundaries right first; Database
per Service becomes natural once boundaries match
business domains.

---

### ✅ Mastery Checklist

**You've mastered this when you can:**
1. **DESIGN** Given a monolith with 30 tables: propose
   service boundaries and assign table ownership.
   Identify which tables have multi-service access
   and propose the resolution (split table, new
   service, event-based projection).
2. **CROSS-SERVICE** For a specific feature requiring
   data from 3 services: design the full solution
   using CQRS projections. Specify: events to subscribe
   to, projection schema, and how projections stay
   current.
3. **POLYGLOT** Recommend database technology for
   5 different services in an e-commerce platform.
   Justify each choice (relational, document, search,
   cache, graph).
4. **MIGRATION** Describe the step-by-step migration
   from shared database (3 services, 20 tables) to
   Database per Service. How do you avoid downtime?
   How do you validate correctness?
5. **OPERATIONAL** Name 3 operational challenges
   of Database per Service at 50 services. For each:
   the tooling or process that addresses it.

---

### 🧠 Think About This Before We Continue

**Q1.** You have 15 microservices, each with a
separate PostgreSQL instance. Your DBA team has
approved using Amazon RDS. Calculate the monthly
cost for 15 RDS instances (db.t3.medium, Multi-AZ,
100GB storage each). Is this cost justified? What
alternatives reduce cost while maintaining isolation
(RDS with multiple schemas, Aurora Serverless,
shared RDS with strict access controls)?

**Q2.** An order-service needs to know if a customer's
payment method is valid BEFORE creating the order
(synchronous validation, cannot be eventual). How
do you implement this validation given Database
per Service? The payment method data is owned by
payment-service. Describe the API design and
consider: what if payment-service is temporarily
unavailable?

**Q3.** You're implementing a GDPR deletion request.
Customer data is replicated across CQRS projections
in 8 different services' databases. How do you
implement the deletion across all projections? What
is the consistency guarantee: can you commit to
all data being deleted within 24 hours? How do
you verify completeness?