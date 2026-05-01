---
layout: default
title: "Database per Service"
parent: "Microservices"
nav_order: 661
permalink: /microservices/database-per-service/
number: "661"
category: Microservices
difficulty: ★★★
depends_on: "Data Isolation per Service, Microservices Architecture"
used_by: "Shared Database Anti-Pattern, CQRS in Microservices, Event-Driven Microservices"
tags: #advanced, #microservices, #distributed, #database, #architecture, #pattern
---

# 661 — Database per Service

`#advanced` `#microservices` `#distributed` `#database` `#architecture` `#pattern`

⚡ TL;DR — **Database per Service** is the microservices data management pattern that gives each service its own private database instance (or schema), accessible only by that service. Enables independent deployment, technology choice, scaling, and schema evolution. Creates the distributed data challenges that CQRS, Sagas, and Event-Driven architecture are designed to solve.

| #661            | Category: Microservices                                                         | Difficulty: ★★★ |
| :-------------- | :------------------------------------------------------------------------------ | :-------------- |
| **Depends on:** | Data Isolation per Service, Microservices Architecture                          |                 |
| **Used by:**    | Shared Database Anti-Pattern, CQRS in Microservices, Event-Driven Microservices |                 |

---

### 📘 Textbook Definition

**Database per Service** is a microservices data management pattern (Chris Richardson, microservices.io) in which each service has its own persistent data store — either a dedicated database server, a dedicated database within a shared server, or at minimum a separate schema with enforced access control. No service accesses another service's database directly. This pattern is the physical implementation of the **Data Isolation per Service** principle and the direct solution to the **Shared Database Anti-Pattern**. Benefits: **independent schema evolution** — each service's schema can be changed without coordination; **technology heterogeneity** — each service chooses the database best suited for its access patterns (PostgreSQL for ACID writes, Redis for fast reads, Cassandra for time-series, Elasticsearch for search); **independent scaling** — scale a service's database independently of others; **fault isolation** — one service's database failure doesn't cascade to others. Trade-offs: distributed data management (no cross-service JOINs); no distributed ACID transactions (use Saga instead); data consistency across services is eventual; more infrastructure to operate.

---

### 🟢 Simple Definition (Easy)

Each microservice has its own private database. No other service can access it. If `OrderService` needs customer data, it asks `CustomerService` via API — it cannot connect directly to `CustomerService`'s database. Like each department having its own filing system: you request documents through official channels, not by walking into their office.

---

### 🔵 Simple Definition (Elaborated)

`CustomerService` → PostgreSQL `customerdb` (ACID writes, complex customer queries)
`OrderService` → PostgreSQL `orderdb` (relational, order lifecycle management)
`InventoryService` → Redis `inventory-cache` + PostgreSQL `inventorydb` (ultra-fast stock reads)
`SearchService` → Elasticsearch `products-index` (full-text product search)
`AnalyticsService` → ClickHouse `analyticsdb` (columnar, fast aggregation queries)

Each service uses the database that best fits its needs. Each database is independently sized, scaled, backed up, and upgraded. `CustomerService`'s PostgreSQL downtime affects only `CustomerService` — other services continue operating normally (using local projections or cached data).

---

### 🔩 First Principles Explanation

**Database technology decision matrix per service:**

```
SERVICE TYPE            OPTIMAL DATABASE    REASON
──────────────────────────────────────────────────────────────────
User/Customer profiles  PostgreSQL          Relational, ACID, complex queries
Order management        PostgreSQL          Transactions, status lifecycle
Product catalog         Elasticsearch       Full-text search, faceted filtering
Session data            Redis               In-memory, TTL, fast key-value
Shopping cart           Redis               In-memory, user-session scoped
Real-time inventory     Redis               O(1) DECR for stock level
Time-series metrics     InfluxDB/TimescaleDB Write-optimized for time-series
Activity feed           Cassandra           Wide-column, high write throughput
Social graph            Neo4j               Graph traversal, relationships
Blob storage            S3 + metadata in PG Binary files, CDN delivery
Analytics/reporting     ClickHouse          Columnar, aggregation queries
Configuration           etcd                Distributed key-value, consensus
```

**Physical isolation options — from weakest to strongest:**

```
LEVEL 1 — Separate schemas (same DB instance):
  customerdb (PostgreSQL) contains:
    schema "customer_schema" → CustomerService's tables
    schema "order_schema"    → OrderService's tables

  Enforcement: DB user "order_user" has NO GRANT on "customer_schema"
  Cost: shared CPU, RAM, disk, connection pool, WAL, vacuum processes
  Use for: development environments, early migration stages

LEVEL 2 — Separate databases (same DB server):
  PostgreSQL server at db.internal:
    database "customerdb" → CustomerService
    database "orderdb"    → OrderService

  Enforcement: createdb privilege; "order_user" can only connect to "orderdb"
  Benefit: separate pg_stat, separate VACUUM, less cross-contamination
  Cost: still shares server CPU, RAM, disk I/O

LEVEL 3 — Separate database servers (dedicated instances):
  customer-db.internal:5432  → CustomerService (3 CPU, 8GB RAM, 100GB SSD)
  order-db.internal:5432     → OrderService (8 CPU, 32GB RAM, 500GB SSD)

  Benefit: fully independent: sizing, maintenance windows, failover, backups
  Cost: more infrastructure to manage (partially mitigated by managed DB services)
  Use for: production microservices at scale

LEVEL 4 — Managed cloud databases (recommended for Kubernetes-based services):
  CustomerService → AWS RDS PostgreSQL (Multi-AZ)
  OrderService    → AWS Aurora PostgreSQL (serverless)
  InventoryService → AWS ElastiCache Redis
  SearchService   → AWS OpenSearch Service

  Each DB independently managed, backed up, auto-scaling by cloud provider
  Teams: zero DBA operational overhead for common tasks
```

**Kubernetes: Database per Service deployment patterns:**

```yaml
# Option 1: Sidecar PostgreSQL (dev/test only — data not persistent across pod restarts):
apiVersion: apps/v1
kind: Deployment
metadata:
  name: customer-service
spec:
  template:
    spec:
      containers:
        - name: customer-service
          image: customer-service:1.0
          env:
            - name: DB_URL
              value: jdbc:postgresql://localhost:5432/customerdb
        - name: postgres # sidecar DB (NOT production-grade)
          image: postgres:15
          env:
            - name: POSTGRES_DB
              value: customerdb

# Option 2: Separate StatefulSet per service (production):
# Each service has its own StatefulSet for its DB with PersistentVolumeClaims.
# CustomerService PostgreSQL StatefulSet → PVC: customer-db-data
# OrderService PostgreSQL StatefulSet → PVC: order-db-data
# Each PVC backed by separate EBS volumes (or equivalent cloud storage)

# Option 3: Managed DB (recommended for production):
# CustomerService reads DB connection string from Kubernetes Secret
# Secret populated by Terraform / Helm from AWS RDS connection info
# No DB management in Kubernetes at all
```

**Cross-service query problem — three solutions compared:**

```
QUERY: "All orders with customer name and product title"

SOLUTION 1: API Composition (Gateway pattern)
  OrderGateway:
    orders = orderClient.findAll()
    for each order:
      order.customerName = customerClient.getName(order.customerId)
      order.productTitle = productClient.getTitle(order.productId)
  Pros: simple, always consistent
  Cons: N+1 problem (1 order query + N customer queries + N product queries)
  Fix: batch endpoints (GET /customers?ids=1,2,3), cache

SOLUTION 2: Local Projection (Event-Carried State Transfer)
  OrderService maintains:
    customer_projection (id, name) — updated from CustomerUpdated events
    product_projection (id, title) — updated from ProductUpdated events
  Orders query: JOIN with local projections (single-service, fast)
  Pros: fast, no inter-service calls at query time
  Cons: eventual consistency (projection may lag), projection storage overhead

SOLUTION 3: CQRS Read Model (dedicated reporting service)
  ReportingService: its own ClickHouse DB, populated by all services' events
  Pre-joined view: order_id, customer_name, product_title, status, amount
  Pros: optimal query performance, cross-service join done offline by projector
  Cons: eventual consistency, separate service to maintain
```

---

### ❓ Why Does This Exist (Why Before What)

When multiple services share one database, the database becomes the coupling point — changes require coordination, resources are shared, failure cascades. Database per Service eliminates this coupling. The cost: distributed data queries must now happen at the application level (via APIs or events). The benefit: services can be deployed, scaled, and evolved independently — the core promise of microservices.

---

### 🧠 Mental Model / Analogy

> Database per Service is like independent bank vaults for each department in a company. Accounting has its own vault with its own lock. HR has its own vault. Sales has its own vault. If you're Accounting and need a document from HR, you call HR and request it through official channels — you don't have a key to their vault. This is slower than shared access but provides: security, auditability, and the ability to upgrade HR's vault without affecting Accounting. The cost: you cannot do a "simultaneous audit" of all vaults at once — you must request reports from each department.

---

### ⚙️ How It Works (Mechanism)

**Spring Boot multi-datasource configuration (multiple services' DBs in one app for comparison):**

```yaml
# ❌ Shared database (anti-pattern):
spring:
  datasource:
    url: jdbc:postgresql://shared-db:5432/appdb  # all services point here

# ✅ Database per service (correct — each service application.yml):
# CustomerService application.yml:
spring:
  datasource:
    url: jdbc:postgresql://customer-db.internal:5432/customerdb
    username: customer_app
    password: ${CUSTOMER_DB_PASSWORD}  # from Kubernetes Secret, not hardcoded

# OrderService application.yml:
spring:
  datasource:
    url: jdbc:postgresql://order-db.internal:5432/orderdb
    username: order_app
    password: ${ORDER_DB_PASSWORD}

# InventoryService application.yml:
spring:
  data:
    redis:
      host: inventory-redis.internal
      port: 6379
  datasource:  # separate PostgreSQL for durable inventory records
    url: jdbc:postgresql://inventory-db.internal:5432/inventorydb
```

---

### 🔄 How It Connects (Mini-Map)

```
Microservices Architecture
(autonomous services)
        │
        ▼
Database per Service  ◄──── (you are here)
(physical implementation of data isolation)
        │
        ├── Data Isolation per Service → the principle; Database per Service → the pattern
        ├── Shared Database Anti-Pattern → what this replaces
        ├── Event-Driven Microservices → how data flows between isolated DBs
        ├── CQRS → reporting across isolated databases
        └── Saga Pattern → transactions across isolated databases
```

---

### 💻 Code Example

**Terraform: Separate RDS instances per service (infrastructure as code):**

```hcl
# customer-service RDS instance:
resource "aws_db_instance" "customer_service_db" {
  identifier        = "customer-service-db"
  engine            = "postgres"
  engine_version    = "15.3"
  instance_class    = "db.t3.medium"
  allocated_storage = 50
  db_name           = "customerdb"
  username          = "customer_app"
  password          = var.customer_db_password
  multi_az          = true
  backup_retention_period = 7
  vpc_security_group_ids  = [aws_security_group.customer_service_db_sg.id]
  # Only CustomerService security group has inbound access on port 5432
}

# order-service Aurora cluster (higher throughput):
resource "aws_rds_cluster" "order_service_db" {
  cluster_identifier = "order-service-db"
  engine             = "aurora-postgresql"
  engine_version     = "15.3"
  master_username    = "order_app"
  master_password    = var.order_db_password
  vpc_security_group_ids = [aws_security_group.order_service_db_sg.id]
}

# Separate security groups enforce network-level isolation:
resource "aws_security_group" "customer_service_db_sg" {
  name = "customer-service-db-sg"
  ingress {
    from_port       = 5432
    to_port         = 5432
    protocol        = "tcp"
    security_groups = [aws_security_group.customer_service_app_sg.id]  # ONLY customer-service pods
  }
}
```

---

### ⚠️ Common Misconceptions

| Misconception                                                  | Reality                                                                                                                                                                                                                                                                                |
| -------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Database per Service means one database technology per company | It means each service chooses its own technology. Different services CAN use the same technology (multiple PostgreSQL instances) or different ones. The key is per-service ownership, not per-service uniqueness of technology                                                         |
| Database per Service makes ACID impossible                     | ACID within a single service remains fully available. Multi-service ACID is replaced by Sagas (eventual consistency). Most business transactions actually only span one service's data — multi-service ACID needs were often an artefact of shared schema design                       |
| You need Kubernetes/cloud to implement Database per Service    | Database per Service is an architectural principle applicable with any infrastructure. Even on bare metal, each service can have its own PostgreSQL instance or at minimum its own database/schema                                                                                     |
| Database per Service increases storage costs significantly     | With modern managed cloud databases, most cost is compute (CPU, memory) not storage. Running separate small instances costs similar to one large shared instance. Benefits of independent scaling, failure isolation, and team autonomy typically far exceed marginal cost differences |

---

### 🔥 Pitfalls in Production

**Polyglot persistence debt — maintaining too many database technologies:**

```
SCENARIO:
  Organisation adopted Database per Service 2 years ago.
  Current database estate:
    12 PostgreSQL instances (RDS)
    8 Redis clusters (ElastiCache)
    3 MongoDB clusters
    2 Cassandra clusters
    1 Elasticsearch cluster
    1 ClickHouse instance
    1 Neo4j instance
  = 28 distinct database clusters to maintain, monitor, backup, upgrade.

  Operational challenges:
  - 28 separate backup jobs, 28 separate monitoring dashboards
  - 8 different database technologies to retain expertise for
  - Security patches: 8 technology vendors, different release schedules
  - Cost: 28 instances minimum baseline cost
  - Expertise: 4 DBA engineers cannot cover 8 database technologies competently

LESSONS LEARNED:
  1. Default to one relational DB (PostgreSQL) unless there's a clear, proven need
     for a different technology. "Maybe we'll need Cassandra-level write throughput
     someday" is not a good reason to adopt Cassandra now.

  2. Treat non-standard DB choices as tech debt until they prove their value.

  3. Consolidate: multiple services using Redis can share a Redis cluster
     (separate keyspace prefixes or separate DBs within one Redis instance)
     if they don't conflict on operational concerns.

  4. Managed services reduce (but don't eliminate) operational burden.
```

---

### 🔗 Related Keywords

- `Data Isolation per Service` — the principle that Database per Service implements
- `Shared Database Anti-Pattern` — the problem that this pattern solves
- `CQRS in Microservices` — handles cross-service queries with isolated databases
- `Saga Pattern (Microservices)` — handles multi-service transactions with isolated databases

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ PATTERN      │ Each service → its own private database   │
│ ENFORCEMENT  │ Network ACLs + credentials + architecture │
├──────────────┼───────────────────────────────────────────┤
│ LEVELS       │ Separate schema → DB → server → managed   │
│ TECH CHOICE  │ PostgreSQL, Redis, Cassandra, Elasticsearch│
│              │ based on access pattern per service        │
├──────────────┼───────────────────────────────────────────┤
│ TRADE-OFFS   │ Distributed data challenges (Saga, CQRS)  │
│ WARNING      │ Polyglot persistence debt: default to PG   │
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** You are the lead architect for a payment processing microservices system. `PaymentService` uses PostgreSQL (ACID, strong consistency). `FraudDetectionService` uses Redis for real-time fraud scoring. `AuditService` requires all payment events retained for 7 years (regulatory requirement). Design the database architecture for these three services: database technology choice, isolation level (schema/instance/managed), backup/retention strategy for AuditService, and the data flow mechanism ensuring AuditService receives every payment event exactly once — even if AuditService is temporarily down.

**Q2.** Performance testing reveals that your `OrderService` PostgreSQL (primary instance) handles 3,000 write operations per second but your `ReportingService`'s analytics queries run against the same `orderdb` and cause p95 read latency to spike to 8 seconds during business hours. You need to fix this without violating Database per Service. List three distinct architectural options (with trade-offs) for providing `ReportingService` with its own view of order data. Which would you recommend for a team of 6 engineers running 15 microservices?
