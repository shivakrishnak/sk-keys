---
layout: default
title: "CQRS in Microservices"
parent: "Microservices"
nav_order: 43
permalink: /microservices/cqrs-in-microservices/
id: MSV-043
category: Microservices
difficulty: ★★★
depends_on: CQRS, Event-Driven Microservices, Data Isolation per Service
used_by: Event Sourcing in Microservices, Eventual Consistency (Microservices), Distributed Logging
related: Event Sourcing in Microservices, Read Model, Saga Pattern (Microservices)
tags:
  - microservices
  - architecture
  - database
  - distributed
  - deep-dive
---

# MSV-043 — CQRS in Microservices

⚡ TL;DR — CQRS separates command (write) and query (read) models within or across microservices, enabling each to be optimised, scaled, and evolved independently.

| #658            | Category: Microservices                                                                    | Difficulty: ★★★ |
| :-------------- | :----------------------------------------------------------------------------------------- | :-------------- |
| **Depends on:** | CQRS, Event-Driven Microservices, Data Isolation per Service                               |                 |
| **Used by:**    | Event Sourcing in Microservices, Eventual Consistency (Microservices), Distributed Logging |                 |
| **Related:**    | Event Sourcing in Microservices, Read Model, Saga Pattern (Microservices)                  |                 |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
Your Order Service has one `orders` table. The checkout API writes to it. The dashboard API reads from it — with complex joins to customer, product, and shipping tables. The checkout needs a normalised schema for write integrity. The dashboard needs denormalised data for fast reads. You add read-optimised indexes that hurt write performance. You add write-optimised constraints that require complex joins for reads. Every schema change must satisfy both write and read patterns simultaneously. Under load, read traffic (100k/sec) starves write throughput (1k/sec) because they share the same database and connection pool.

**THE BREAKING POINT:**
A single data model cannot be simultaneously optimised for both writes (normalised, transactionally consistent) and reads (denormalised, precomputed, fast). Forcing them to share a schema means compromising both.

**THE INVENTION MOMENT:**
This is exactly why CQRS in microservices was adopted — separate the write model (commands) from the read model (queries), allowing each to be designed, stored, and scaled for its specific purpose.

---

### 📘 Textbook Definition

**CQRS (Command Query Responsibility Segregation) in microservices** is an architectural pattern where the responsibility for handling write operations (commands: create, update, delete) is separated from read operations (queries), using different models, often different data stores, and sometimes different services. Commands mutate state in the write store; domain events are published on state changes; read models (projections) subscribe to events and maintain denormalised, query-optimised views. Queries read from projections — never from the write store. This enables independent scaling, evolution, and optimisation of reads and writes.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
Separate the database that you write to from the database that you read from — each optimised for its purpose.

**One analogy:**

> A library has a card catalogue (the read model) and the actual book registration ledger (the write model). When a new book arrives (command), the librarian updates the ledger (write model) and also updates the card catalogue (read model). Patrons always look up books in the card catalogue — never in the ledger. The card catalogue is denormalised and fast; the ledger is accurate and official.

**One insight:**
In most production systems, reads outnumber writes by 100:1. CQRS lets you build the read path for exactly that scale: pre-computed, denormalised, replicated — without contaminating the write path's normalised, transactionally consistent model.

---

### 🔩 First Principles Explanation

**CORE INVARIANTS:**

1. Write operations need ACID consistency and normalised schemas to prevent data corruption.
2. Read operations need pre-computed, denormalised data to achieve sub-millisecond latency at scale.
3. These two requirements are in direct tension — you cannot optimise one schema for both.

**DERIVED DESIGN:**
Given these invariants: maintain two separate data representations. Commands write to a normalised _write store_ — the source of truth. When the write store changes, domain events trigger updates to the _read store_ (projection) — a denormalised representation optimised for specific query patterns. Reads always go to the read store.

**What "CQRS in microservices" looks like:**

**Intra-service CQRS:**

```
One service, two internal data models:
  Write store: relational DB (normalised)
  Read store: same DB, different tables (denormalised)
             or separate DB technology
  Projection updated via event handler
```

**Inter-service CQRS:**

```
Write Service → publishes events → Query Service
  Write Service owns write store
  Query Service owns read store (projection)
  Separate deployable services
  Query Service scales independently of Write Service
```

**Projection types:**

- **Tabular projections**: denormalised tables optimised for specific queries
- **Search projections**: Elasticsearch index for full-text/filtered search
- **Analytics projections**: ClickHouse/BigQuery for aggregations
- **Cache projections**: Redis for sub-millisecond point lookups

**THE TRADE-OFFS:**
**Gain:** Independent scaling of reads and writes; query models optimised per access pattern; write model free from read performance pressure; multiple read models for different consumers.
**Cost:** Eventual consistency between write and read store; operational complexity (two data stores); event projection failures must be detected and recovered; debugging cross-store flows is harder.

---

### 🧪 Thought Experiment

**SETUP:**
An order management system must handle:

- **Write**: 1,000 orders/sec (normalised, transactionally consistent)
- **Read 1**: 100,000 order list queries/sec (paginated list with customer name, status, total)
- **Read 2**: 500 real-time analytics queries/sec (orders by region, revenue by product)
- **Read 3**: 50 full-text search queries/sec ("find all orders for customer 'Smith'")

**WITHOUT CQRS:**
One PostgreSQL DB must serve all patterns. The dashboard query joins 5 tables. Under 100k read QPS, the DB is saturated. Indexes for read patterns slow down write performance. Schema evolution for reads breaks write constraints.

**WITH CQRS:**

- **Write store**: PostgreSQL (normalised). 1k writes/sec — no problem.
- **Read store 1**: PostgreSQL read replicas with denormalised `order_views` table. 100k reads/sec, served from replicas.
- **Read store 2**: ClickHouse columnar DB. 500 analytics queries/sec — sub-second aggregations.
- **Read store 3**: Elasticsearch full-text index. 50 search queries/sec — instant results.

**THE INSIGHT:**
Each read model is independently optimised for its access pattern. The write model is clean and consistent. Adding a new read pattern (e.g., mobile app API) means creating a new projection — zero impact on existing models or the write model.

---

### 🧠 Mental Model / Analogy

> Think of a manufacturing company with two systems: the inventory management system (write model — every transaction recorded with full detail, normalised) and the warehouse picking list (read model — denormalised, optimised for the warehouse worker to quickly find items). When the inventory system records a new stock receipt (command), the picking list is automatically updated (projection). Workers never check the inventory system directly — too complex, too slow. They use the picking list. Finance never relies on the picking list — too imprecise. They use the inventory system.

- "Inventory management system" → write store (normalised, transactional)
- "Picking list" → read store (denormalised, optimised)
- "Stock receipt recorded" → command + domain event
- "Picking list updated" → projection update
- "Finance uses inventory system" → commands / mutations go to write store
- "Workers use picking list" → queries go to read store

Where this analogy breaks down: the picking list update may have a brief lag after inventory update (eventual consistency). In the analogy, this would mean a worker might briefly see a stale picking list.

---

### 📶 Gradual Depth — Four Levels

**Level 1 — What it is (anyone can understand):**
Two databases for one service: one you write to (carefully, correctly), one you read from (fast, pre-computed). When the write database changes, it automatically updates the read database.

**Level 2 — How to use it (junior developer):**
Define commands (write operations) and queries (read operations) separately. Commands go to the write store; return minimal response (id, timestamp). After a successful command, publish a domain event. An event handler updates the read store (projection). Queries always read from the projection — never from the write store.

**Level 3 — How it works (mid-level engineer):**
The projection is built by replaying events. If you replay all events from time zero, you rebuild the projection from scratch — this is the _projection rebuild_ pattern for fixing corrupt read models. The key concern: **projection lag** (write store updated but read store hasn't caught up yet — same as eventual consistency window). Handle with: read-your-writes (serve command result directly after write); optimistic UI (show predicted state while projection updates). Projection versioning: when you change a projection's logic (add a new field, change aggregation), you create a new projection version (V1 → V2), rebuild it from event history, then flip reads from V1 to V2 — zero downtime migration.

**Level 4 — Why it was designed this way (senior/staff):**
CQRS in microservices is the natural consequence of two insights: (1) reads and writes have fundamentally different scaling characteristics (reads scale with replicas; writes scale with sharding + eventual consistency); (2) different consumers need the same data in different shapes. Pre-relational systems (mainframe ISAM) already embodied this: separate sequential files for different access patterns. Relational databases temporarily unified this (the "one true schema"), but at internet scale this unification became a bottleneck. CQRS is the principled reintroduction of multiple, purpose-built data representations — but with explicit event-driven synchronisation instead of batch ETL jobs. When combined with Event Sourcing, CQRS reaches its full power: the event log is the source of truth; all projections are derived views, re-buildable at any time.

---

### ⚙️ How It Works (Mechanism)

```
┌─────────────────────────────────────────────────────────┐
│           CQRS in Microservices — Flow                  │
└─────────────────────────────────────────────────────────┘

           Commands (Write)          Queries (Read)
               │                          │
               ▼                          ▼
    ┌──────────────────┐       ┌────────────────────┐
    │  Command Handler │       │   Query Handler    │
    │                  │       │                    │
    │  Validate        │       │  Read from         │
    │  Apply business  │       │  Projection only   │
    │  rules           │       │                    │
    │  Persist to      │       │  Never from        │
    │  Write Store     │       │  Write Store       │
    └──────┬───────────┘       └────────────────────┘
           │                          ▲
           │ Publish event            │
           ▼                          │
    ┌──────────────┐                  │
    │  Event Bus   │                  │
    │  (Kafka)     │                  │
    └──────┬───────┘                  │
           │                          │
           ▼                          │
    ┌─────────────────────────────────┴──┐
    │      Projection Builder            │
    │                                    │
    │  Consume event                     │
    │  Transform to read model shape     │
    │  Upsert into Read Store            │
    └────────────────────────────────────┘

Write Store: PostgreSQL (normalised)
Read Store: PostgreSQL (denormalised) | Elasticsearch | Redis
```

---

### 🔄 The Complete Picture — End-to-End Flow

**NORMAL FLOW:**

```
[Client: POST /orders (command)]
  → [Command Handler: validate + write to PostgreSQL orders table]
  → [Publish OrderPlaced event]
  → [Return 202 Accepted with orderId]
  → [Return immediately — don't wait for projection]

[Projection Builder: consume OrderPlaced]
  → [Upsert order_views: orderId, customerName, status, total]
  → [Upsert Elasticsearch order document]

[Client: GET /orders?customerId=X (query)]
  → [Query Handler: SELECT from order_views WHERE customer_id=X]
  → [Return pre-joined, pre-formatted result immediately]
```

**PROJECTION REBUILD FLOW:**

```
[Bug found: order_views has wrong total calculation]
  → [Fix projection builder logic]
  → [Create new projection: order_views_v2]
  → [Replay all OrderPlaced events from Kafka beginning]
  → [Rebuild order_views_v2 with correct logic]
  → [Flip query handler to read from order_views_v2]
  → [Drop old order_views]
  → [Zero downtime migration]
```

---

### 💻 Code Example

**Example 1 — Command Handler (write side):**

```java
@Service
public class OrderCommandHandler {

  @Autowired OrderRepository orderRepo;       // write store
  @Autowired EventPublisher eventPublisher;

  @Transactional
  public CreateOrderResult handle(CreateOrderCommand cmd) {
    // Validate
    if (!inventoryClient.isAvailable(cmd.getProductId(),
                                     cmd.getQuantity())) {
      throw new InsufficientStockException();
    }
    // Write to normalised write store
    Order order = Order.create(cmd);
    orderRepo.save(order);  // normalised: orders + order_lines

    // Publish event for projections
    eventPublisher.publish(
      OrderPlacedEvent.from(order));

    // Return minimal response — don't return from read model
    return new CreateOrderResult(order.getId(),
                                 order.getCreatedAt());
  }
}
```

**Example 2 — Projection Builder (sync to read store):**

```java
@Component
public class OrderViewProjection {

  @Autowired OrderViewRepository orderViewRepo; // read store

  @KafkaListener(topics = "order-events",
                 groupId = "order-view-projection")
  public void on(OrderPlacedEvent event) {
    // Build denormalised view — optimised for list queries
    OrderView view = OrderView.builder()
      .orderId(event.getOrderId())
      .customerId(event.getCustomerId())
      .customerName(event.getCustomerName()) // denormalised
      .status("PENDING")
      .totalAmount(event.getTotalAmount())
      .itemCount(event.getItemCount())       // precomputed
      .createdAt(event.getOccurredAt())
      .build();

    orderViewRepo.upsert(view); // idempotent upsert
  }

  @KafkaListener(topics = "order-events",
                 groupId = "order-view-projection")
  public void on(OrderStatusUpdatedEvent event) {
    orderViewRepo.updateStatus(event.getOrderId(),
                               event.getNewStatus());
  }
}
```

**Example 3 — Query Handler (read side):**

```java
@Service
public class OrderQueryHandler {

  @Autowired OrderViewRepository orderViewRepo; // read store ONLY

  public Page<OrderSummary> getOrdersByCustomer(
      String customerId, Pageable pageable) {
    // Read from denormalised view — no joins, fast
    return orderViewRepo
      .findByCustomerId(customerId, pageable)
      .map(OrderSummary::from);
  }

  // NEVER: direct query to write store for reads
  // WRONG: orderWriteRepo.findByCustomerId(...)
}
```

---

### ⚖️ Comparison Table

| Approach                            | Write Optimisation | Read Optimisation     | Consistency | Complexity |
| ----------------------------------- | ------------------ | --------------------- | ----------- | ---------- |
| **CQRS (separate stores)**          | Full               | Full (per pattern)    | Eventual    | High       |
| CQRS (same store, different models) | Partial            | Partial               | Eventual    | Medium     |
| Single model (traditional)          | Compromise         | Compromise            | Strong      | Low        |
| Read replicas only                  | Compromise         | Partial (same schema) | Eventual    | Medium     |

**How to choose:** Use **CQRS** when read and write access patterns are significantly different, or when read scale >> write scale. Use a **single model** for simple CRUD services with balanced read/write and no complex query patterns.

---

### ⚠️ Common Misconceptions

| Misconception                                             | Reality                                                                                                                                 |
| --------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------- |
| CQRS requires separate microservices for reads and writes | You can implement CQRS within a single service with two internal data stores                                                            |
| CQRS is too complex for most systems                      | Intra-service CQRS (different tables) is low complexity; inter-service CQRS is complex                                                  |
| Queries can't use the write store at all                  | In simple cases, querying the write store is fine; CQRS adds separation when scale requires it                                          |
| CQRS and Event Sourcing are the same thing                | CQRS is about separate read/write models; Event Sourcing is about storing state as event history. They combine well but are independent |
| The read model is just a cache                            | The read model is a first-class data representation, built from events, with its own schema and SLA                                     |

---

### 🚨 Failure Modes & Diagnosis

**Stale Read Model — Query Returns Outdated Data**

**Symptom:** User places order successfully (command returns 200); immediately queries order list; new order not visible.

**Root Cause:** Projection lag — event published but projection builder hasn't consumed and updated read store yet.

**Diagnostic Command:**

```bash
# Check projection consumer lag
kafka-consumer-groups.sh --bootstrap-server kafka:9092 \
  --describe --group order-view-projection
# If LAG > 0, read model is behind
```

**Fix:** Implement read-your-writes: cache the just-created order in Redis for 5 seconds; serve from cache before projection catches up. Or: accept the lag and display a spinner / "Processing your order…" for 1–2 seconds.

**Prevention:** Design the UI to anticipate eventual consistency; don't assume immediate read consistency after write.

---

**Projection Corruption — Read Model Has Wrong Data**

**Symptom:** Order view shows wrong total amounts; some orders missing from list; totals don't match write store.

**Root Cause:** Projection builder had a bug; some events were processed incorrectly; duplicate processing without idempotency.

**Diagnostic Command:**

```sql
-- Compare counts between write and read store
SELECT count(*) FROM orders;                  -- write store
SELECT count(*) FROM order_views;             -- read store
-- If different: projection has missed events
```

**Fix:** Fix the projection builder logic. Rebuild the projection from event history (replay all events into new `order_views_v2` table). Flip reads to new table.

**Prevention:** Implement idempotency in projection builder (upsert, not insert); monitor write store vs read store record count discrepancy; alert on divergence.

---

**Event Schema Breaking Change — Projection Fails to Deserialise**

**Symptom:** Projection builder logs `SerializationException`; consumer lag grows; read model stops updating.

**Root Cause:** Command side changed event schema without backward compatibility; projection builder can't parse new event format.

**Diagnostic Command:**

```bash
# Check consumer error logs
kubectl logs deployment/order-view-projection \
  | grep -i "serialization\|deserialization\|schema"
```

**Fix:** Roll back event schema change or deploy compatible projection builder that handles both old and new event versions.

**Prevention:** Enforce backward-compatible schema evolution via Schema Registry; test projection builder against event schema changes in CI.

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**

- `CQRS` — the foundational pattern (Command Query Responsibility Segregation)
- `Event-Driven Microservices` — the mechanism for propagating state changes to read models
- `Data Isolation per Service` — ensures read and write models are owned by appropriate services

**Builds On This (learn these next):**

- `Event Sourcing in Microservices` — stores write side as event log; read models are projections of the log
- `Eventual Consistency (Microservices)` — the consistency model between write and read stores
- `Read Model` — the query-optimised data store that CQRS produces

**Alternatives / Comparisons:**

- `Saga Pattern (Microservices)` — often used alongside CQRS for cross-service state management
- `Database per Service` — complementary; each service (including query service) owns its store
- `Shared Database Anti-Pattern` — what CQRS avoids at the read/write level

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ WHAT IT IS   │ Separate write model (commands) from      │
│              │ read model (queries); different stores    │
├──────────────┼───────────────────────────────────────────┤
│ PROBLEM IT   │ Single data model cannot be optimised     │
│ SOLVES       │ for both write integrity and read speed   │
├──────────────┼───────────────────────────────────────────┤
│ KEY INSIGHT  │ Reads outnumber writes 100:1 — pre-       │
│              │ compute denormalised read models          │
├──────────────┼───────────────────────────────────────────┤
│ USE WHEN     │ Read/write patterns diverge; read scale   │
│              │ >> write scale; multiple query consumers  │
├──────────────┼───────────────────────────────────────────┤
│ AVOID WHEN   │ Simple CRUD; reads and writes use same    │
│              │ shape; low traffic                        │
├──────────────┼───────────────────────────────────────────┤
│ TRADE-OFF    │ Optimised reads + writes vs eventual      │
│              │ consistency + operational complexity      │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "Write to one store; read from another"   │
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ Event Sourcing → Read Model → Projection  │
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** Your Order Service implements CQRS. The write store (PostgreSQL) contains a `discount_percentage` column added last month. Your read store (denormalised `order_views`) was built from events that predate this column. The `OrderPlaced` event schema didn't include `discount_percentage`. Dashboard queries need to show discounted totals. How do you backfill this data into the read store without taking downtime and without directly querying the write store from the projection builder?

**Q2.** You implement CQRS in your Order Service. The write store has 5M orders. Your projection builder has a bug — `order_views` has incorrect `total_amount` for orders with promotional codes. You fix the projection builder logic. Describe the complete, zero-downtime procedure to rebuild `order_views` with correct data while the system continues processing new orders and serving reads.
