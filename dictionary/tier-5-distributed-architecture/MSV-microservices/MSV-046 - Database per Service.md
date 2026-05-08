---
layout: default
title: "Database per Service"
parent: "Microservices"
grand_parent: "Technical Dictionary"
nav_order: 46
permalink: /microservices/database-per-service/
id: MSV-046
category: Microservices
difficulty: ★★★
depends_on: Data Isolation per Service, Shared Database Anti-Pattern, Bounded Context
used_by: Event Sourcing in Microservices, CQRS in Microservices, Data Isolation per Service
related: Shared Database Anti-Pattern, Polyglot Persistence, Data Isolation per Service
tags:
  - microservices
  - database
  - architecture
  - distributed
  - deep-dive
---

# MSV-046 - Database per Service

⚡ TL;DR - Each microservice owns a separate, dedicated data store that no other service can access directly, enabling independent schema evolution, technology choice, and scaling.

| #661            | Category: Microservices                                                            | Difficulty: ★★★ |
| :-------------- | :--------------------------------------------------------------------------------- | :-------------- |
| **Depends on:** | Data Isolation per Service, Shared Database Anti-Pattern, Bounded Context          |                 |
| **Used by:**    | Event Sourcing in Microservices, CQRS in Microservices, Data Isolation per Service |                 |
| **Related:**    | Shared Database Anti-Pattern, Polyglot Persistence, Data Isolation per Service     |                 |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
Five microservices share one database. Any service can schema-migrate any table. The Inventory Service needs to shard for scale - but it can't, because the Order Service is doing cross-table joins against inventory tables and the sharding would break them. The Analytics Service needs a columnar store - but the DB is relational and all services depend on it. The teams can't evolve independently. Every release requires coordination across all teams.

**THE BREAKING POINT:**
A shared database is a shared public contract. Any service that reads or writes it becomes a stakeholder in every schema decision. As services grow, this coordination overhead grows quadratically - eventually paralysing the organisation.

**THE INVENTION MOMENT:**
Database per Service was formalised as the enabling pattern for true microservices autonomy - each service is the exclusive owner of its own data store, free to choose the right technology and evolve the schema independently.

---

### 📘 Textbook Definition

**Database per Service** is a microservices architecture pattern where each service owns and exclusively manages its own dedicated data store. No other service may directly connect to or query that data store. The data store may be a separate database instance, a separate schema within a shared instance with enforced permission barriers, or even a fundamentally different database technology (polyglot persistence). Cross-service data access is mediated through the service's published API or via event-driven replication. This pattern enforces the Data Isolation per Service principle at the infrastructure level.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
Every service gets its own database - it's that service's private property, not a shared resource.

**One analogy:**

> Each apartment in a building has its own kitchen. Residents don't share a communal kitchen (shared DB). If Apartment 3 wants to renovate their kitchen (schema migration), they do it without affecting anyone else. Apartment 7 can install a professional gas range (different DB technology) while everyone else keeps standard stoves. Each resident scales their own kitchen independently.

**One insight:**
Database per Service is not primarily about database instances - it's about _ownership boundaries_. Even a shared DB instance achieves most benefits if permission barriers are enforced and schemas are strictly separated.

---

### 🔩 First Principles Explanation

**THREE LEVELS OF ISOLATION:**

**Level 1 - Separate database instances (strongest isolation):**

```
Order Service    → order-db (PostgreSQL)
Inventory Service → inventory-db (MongoDB)
User Service      → user-db (PostgreSQL)
```

Pros: Complete isolation - schema, performance, failure, technology.
Cons: More infrastructure to manage; connection pool per service; DB admin overhead multiplied.

**Level 2 - Separate schemas, shared DB instance (middle ground):**

```
shared-postgres:
  order_schema.orders        → accessible only by order_service_user
  inventory_schema.products  → accessible only by inventory_service_user
  user_schema.users          → accessible only by user_service_user
```

Pros: Less infrastructure; still schema-isolated.
Cons: Operational coupling remains (shared instance = shared failure, shared upgrade, shared performance ceiling).

**Level 3 - Separate tables with permissions (weakest - anti-pattern still):**

```
shared_schema.orders         → grant to order_service_user
shared_schema.products       → grant to inventory_service_user
```

Cons: DB FK constraints still tempt cross-table references; schema namespace shared; marginal improvement over full shared DB.

**POLYGLOT PERSISTENCE:**
Database per Service enables choosing the right technology per domain:

| Service             | Technology    | Reason                        |
| ------------------- | ------------- | ----------------------------- |
| Order Service       | PostgreSQL    | ACID transactions, relational |
| Product Catalogue   | Elasticsearch | Full-text search              |
| Session Store       | Redis         | Sub-millisecond, TTL-based    |
| User Graph          | Neo4j         | Graph relationships           |
| Time-Series Metrics | InfluxDB      | Optimised for time-series     |
| Document Store      | MongoDB       | Flexible schemas              |

**THE TRADE-OFFS:**
**Gain:** Independent schema evolution; independent technology choice; independent scaling; failure isolation; security isolation (breach of one service's DB doesn't expose others).
**Cost:** No cross-service SQL joins (must use API/events); data duplication for cross-service reads; operational complexity multiplied (more DBs to manage, monitor, back up); eventual consistency required.

---

### 🧪 Thought Experiment

**SETUP:**
The Inventory Service needs to scale reads to 500k/sec (product availability checks). The Order Service needs ACID transactions with complex joins. Both currently share one PostgreSQL instance.

**WITH SHARED DB:**
To scale Inventory to 500k reads/sec on PostgreSQL, you need massive read replicas - which are shared with Order Service. Order Service's heavy write transactions cause replication lag, slowing Inventory reads. You can't use Redis or Cassandra for Inventory (which would be ideal for high-read availability lookups) because the schema is entangled with Order Service tables.

**WITH DATABASE PER SERVICE:**
Inventory Service migrates its availability data to Redis (hash lookup, sub-millisecond, scales horizontally). 500k reads/sec is trivial for Redis. PostgreSQL remains as Order Service's DB - no sharing, no interference. Teams deploy independently. Zero coordination required.

**THE INSIGHT:**
Database per Service doesn't just provide isolation - it enables the right technology for each problem. Forcing every service onto one DB technology is like requiring every department to use the same tool for every job.

---

### 🧠 Mental Model / Analogy

> Database per Service is like each developer having their own local development environment rather than all 20 developers sharing one remote server. When Developer A installs a new library (schema change), it doesn't break Developer B's environment. Developer C can use a Mac (MongoDB) while Developer D uses Linux (PostgreSQL). Each developer can restart their environment without affecting anyone else. Shared environments (shared DB) feel efficient at T=0 but become bottlenecks and conflict zones as the team grows.

- "Each developer's environment" → each service's database
- "Installing a library" → schema migration
- "Different OS" → polyglot persistence (different DB technology)
- "Restart without affecting others" → failure isolation
- "Shared remote server (shared DB)" → what this pattern replaces

---

### 📶 Gradual Depth - Four Levels

**Level 1 - What it is (anyone can understand):**
Each service gets its own database. Only that service can read or write its database. Other services must ask via the service's API.

**Level 2 - How to implement it (junior developer):**
Create separate DB schemas or instances per service. Grant DB credentials only to the owning service's connection pool. Remove all cross-service DB connections. Replace cross-service DB reads with API calls or event-driven snapshots. Add DB-level permissions to enforce boundaries.

**Level 3 - How to manage it operationally (mid-level engineer):**
Database per Service multiplies your operational surface. Manage with: centralised monitoring (Prometheus + Grafana, scraping all DB instances); infrastructure-as-code (Terraform/Helm charts templated per service); standard backup automation per service; schema migration CI/CD (Flyway/Liquibase per service, each in its own migration folder); service-level DB SLAs (each team owns its own DB uptime). Use a service mesh or API gateway to enforce that no direct DB connections cross service boundaries at the network level.

**Level 4 - Why it's worth the complexity (senior/staff):**
Database per Service is the data-tier equivalent of Conway's Law enforcement. When each team owns its own DB, schema changes are internal decisions - no inter-team approval needed. Technology choices are local decisions - the Inventory team doesn't need consensus to adopt MongoDB. Scaling decisions are local - the Analytics team can shard independently. This converts what would be organisation-wide coordination costs into local, autonomous team decisions. The operational cost (more DBs to manage) is real but amortised by infrastructure automation. At Google, Amazon, Netflix scale, the coordination costs of shared databases vastly exceed the operational costs of independent data stores. The long-term ROI of this pattern is why it is considered foundational - not optional - in mature microservices organisations.

---

### ⚙️ How It Works (Mechanism)

```
┌─────────────────────────────────────────────────────────┐
│            Database per Service - Architecture          │
└─────────────────────────────────────────────────────────┘

  Order Service          Inventory Service       User Service
  ┌───────────┐          ┌───────────────┐       ┌──────────┐
  │  order-   │          │ inventory-    │       │  user-   │
  │  service  │          │  service      │       │  service │
  └─────┬─────┘          └──────┬────────┘       └────┬─────┘
        │                       │                      │
        ▼                       ▼                      ▼
  ┌──────────┐          ┌──────────────┐         ┌──────────┐
  │order-db  │          │inventory-db  │         │ user-db  │
  │(Postgres)│          │  (MongoDB)   │         │(Postgres)│
  └──────────┘          └──────────────┘         └──────────┘

Cross-service data needs:
  ✅ Order Service → GET /inventory/{id} → Inventory Service API
  ✅ Order Service → subscribes ProductUpdated events → local cache
  ❌ Order Service → SELECT FROM inventory-db (FORBIDDEN)

Network enforcement:
  DB security groups: only allow connections from owning service's VPC
  DB credentials: unique per service, stored in secrets manager
  No shared credentials
```

---

### 🔄 The Complete Picture - Migration from Shared DB

**STEP 1: Audit ownership:**

```sql
-- Find who writes to what
SELECT application_name, query
FROM pg_stat_activity
WHERE state='active'
  AND query ~* '^(INSERT|UPDATE|DELETE)'
GROUP BY application_name, query;
```

**STEP 2: Add service API layer:**

```
Order Service reads inventory.products.stock
→ Create: GET /inventory/products/{id}/availability
→ Order Service calls API instead of direct DB
```

**STEP 3: Add schema-level permissions:**

```sql
-- Revoke cross-service access
REVOKE ALL ON inventory_schema.products
  FROM order_service_db_user;

-- Verify
\dp inventory_schema.products
```

**STEP 4: Separate to individual instances:**

```
pg_dump inventory_schema → inventory-db (new instance)
Update inventory-service: DB connection → inventory-db
Verify; remove old schema from shared instance
```

---

### 💻 Code Example

**Example 1 - Terraform: DB per service (separate instances):**

```hcl
# order-service database
resource "aws_db_instance" "order_db" {
  identifier        = "order-service-db"
  engine            = "postgres"
  instance_class    = "db.t3.medium"
  db_name           = "orders"
  username          = "order_svc"
  password          = var.order_db_password
  vpc_security_group_ids = [aws_security_group.order_db_sg.id]
}

# Only order-service pods can access order-db
resource "aws_security_group_rule" "order_db_ingress" {
  type                     = "ingress"
  from_port                = 5432
  to_port                  = 5432
  protocol                 = "tcp"
  source_security_group_id = aws_security_group.order_service_sg.id
  security_group_id        = aws_security_group.order_db_sg.id
}

# inventory-service database (separate instance, MongoDB)
resource "aws_docdb_cluster" "inventory_db" {
  cluster_identifier = "inventory-service-db"
  engine             = "docdb"
  master_username    = "inventory_svc"
  master_password    = var.inventory_db_password
  vpc_security_group_ids = [
    aws_security_group.inventory_db_sg.id]
}
```

**Example 2 - Kubernetes: DB secret per service:**

```yaml
# Each service gets its own DB secret - no sharing
apiVersion: v1
kind: Secret
metadata:
  name: order-service-db-secret
  namespace: order-service
stringData:
  DB_URL: "postgresql://order-svc:@order-db:5432/orders"
---
apiVersion: v1
kind: Secret
metadata:
  name: inventory-service-db-secret
  namespace: inventory-service
stringData:
  DB_URL: "mongodb://inventory-svc:@inventory-db:27017/inventory"
```

---

### ⚖️ Comparison Table

| Isolation Level                    | Schema Isolation | Failure Isolation | Tech Choice     | Mgmt Complexity |
| ---------------------------------- | ---------------- | ----------------- | --------------- | --------------- |
| **Separate DB Instances**          | Full             | Full              | Full (polyglot) | High            |
| Separate Schemas (shared instance) | Full             | None              | None            | Medium          |
| Separate Tables (shared schema)    | Partial          | None              | None            | Low             |
| Shared Tables (no isolation)       | None             | None              | None            | Minimal         |

**How to choose:** Separate DB instances is the target. Separate schemas in a shared instance is acceptable for smaller organisations or during migration. Never use shared tables in production microservices.

---

### ⚠️ Common Misconceptions

| Misconception                                        | Reality                                                                                       |
| ---------------------------------------------------- | --------------------------------------------------------------------------------------------- |
| Database per Service means always separate DB server | The principle is ownership + access control; separate instances are optimal but not mandatory |
| More databases = more cost and complexity            | True upfront; saves exponentially more in coordination and coupling costs at scale            |
| You can't do cross-service queries at all            | You can: via API calls or event-driven snapshots; just not via direct DB connections          |
| All services must use the same DB technology         | Database per Service enables polyglot persistence; each service chooses what fits             |
| This is only for large teams                         | Even 3-service systems with separate teams benefit from this pattern                          |

---

### 🚨 Failure Modes & Diagnosis

**DB Per Service Sprawl - Too Many DBs to Manage**

**Symptom:** 50 microservices = 50 separate DBs; operational overhead overwhelming; 30% of DBs have no monitoring; some DBs missing backups; credential rotation takes weeks.

**Root Cause:** Database per Service adopted without corresponding infrastructure automation.

**Fix:** Standardise with infrastructure-as-code (Terraform modules for standard DB provisioning); centralise monitoring (all DBs scraped by same Prometheus/Grafana stack); automate backups and credential rotation.

**Prevention:** Before adopting Database per Service at scale, build the automation platform first. The DB-per-service benefit requires automation investment.

---

**Service Can't Access Its DB After Deployment**

**Symptom:** New service version fails with `Connection refused` or `authentication failed`; DB exists but connection fails.

**Root Cause:** DB credentials rotated or security group changed; new deployment not updated with new credentials; VPC/network configuration error.

**Diagnostic Command:**

```bash
# Test connectivity from service pod to its DB
kubectl exec -it deployment/order-service -- \
  psql $DB_URL -c "SELECT 1"

# Check security group rules
aws ec2 describe-security-group-rules \
  --filters "Name=group-id,Values=sg-order-db"
```

**Fix:** Update secrets manager entry; verify security group allows egress from service to DB port.

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**

- `Data Isolation per Service` - the principle Database per Service implements
- `Shared Database Anti-Pattern` - the problem this pattern solves
- `Bounded Context` - defines the domain scope that maps to a service's database

**Builds On This (learn these next):**

- `Event Sourcing in Microservices` - now possible because each service owns its event store
- `CQRS in Microservices` - read models are first-class databases owned by query services
- `Polyglot Persistence` - the technology diversity enabled by this pattern

**Alternatives / Comparisons:**

- `Shared Database Anti-Pattern` - what this replaces
- `Strangler Fig Pattern` - how you migrate from shared DB to Database per Service
- `Event-Driven Microservices` - replaces cross-service joins with event replication

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ WHAT IT IS   │ Each service owns its dedicated data store;│
│              │ no direct cross-service DB access         │
├──────────────┼───────────────────────────────────────────┤
│ PROBLEM IT   │ Shared databases prevent independent       │
│ SOLVES       │ schema evolution, scaling, tech choice    │
├──────────────┼───────────────────────────────────────────┤
│ KEY INSIGHT  │ Ownership at data tier = true service      │
│              │ autonomy; without it, microservices fails  │
├──────────────┼───────────────────────────────────────────┤
│ USE WHEN     │ Always in production microservices         │
├──────────────┼───────────────────────────────────────────┤
│ AVOID WHEN   │ Single-team monolith; no need for          │
│              │ independent deployability                  │
├──────────────┼───────────────────────────────────────────┤
│ TRADE-OFF    │ Full service autonomy vs no SQL joins;     │
│              │ data duplication + eventual consistency    │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "Your data, your database, your decision"  │
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ Polyglot Persistence → Event-Driven →     │
│              │ Data Isolation                            │
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** You have 20 microservices, each with its own PostgreSQL database. Your operations team is overwhelmed: monitoring 20 DB instances, managing 20 backup schedules, rotating 20 sets of credentials. What platform-level investments reduce this operational overhead without compromising service isolation? Name 3 specific tools or patterns and explain how each helps.

**Q2.** The Customer Service (PostgreSQL) and Analytics Service (ClickHouse) both need the same customer event data. Customer Service is the authoritative source. You cannot give Analytics Service direct access to Customer DB. Design the data flow that gives Analytics Service access to near-real-time customer event data. What happens if the Analytics Service's ClickHouse instance is down for 4 hours? How does it recover?
