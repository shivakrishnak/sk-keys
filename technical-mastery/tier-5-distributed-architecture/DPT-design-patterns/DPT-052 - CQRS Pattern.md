---
id: DPT-052
title: CQRS Pattern
category: Design Patterns
tier: tier-5-distributed-architecture
folder: DPT-design-patterns
difficulty: ★★★
depends_on: DPT-001, DPT-005, DPT-039, DPT-040
used_by: DPT-064, DPT-065
related: DPT-053, DPT-054, DPT-079, DPT-040
tags:
  - pattern
  - architecture
  - advanced
  - cqrs
  - distributed-systems
  - event-sourcing
  - read-write-separation
status: complete
version: 4
layout: default
parent: "Design Patterns"
grand_parent: "Technical Mastery"
nav_order: 52
permalink: /technical-mastery/design-patterns/cqrs/
---

⚡ TL;DR - CQRS (Command Query Responsibility Segregation)
separates read operations (Queries) from write operations
(Commands) into distinct models - enabling each to be
independently optimized, scaled, and evolved.

| #52 | Category: Design Patterns | Difficulty: ★★★ |
|:---|:---|:---|
| **Depends on:** | DPT-001, DPT-005, DPT-039, DPT-040 | |
| **Used by:** | DPT-064, DPT-065 | |
| **Related:** | DPT-053, DPT-054, DPT-079, DPT-040 | |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT CQRS:**
A single `OrderRepository` with a single `Order` entity
serves both reads and writes. The entity is normalized
for writes (3NF: `Order`, `OrderItem`, `Customer`, `Address`
tables). A dashboard query needs `Order` with customer
name, item count, total, and last-updated-by user. This
requires 4 joins. At 10,000 dashboard page loads/min:
4 × 10,000 = 40,000 JOIN operations/min on transactional
tables that are also handling incoming orders.

The write path needs ACID transactions and strong consistency.
The read path needs flat, fast projections optimized for
the query. Using the same model for both forces trade-offs:
optimize for writes (complex reads), or denormalize for
reads (complicates writes and risks inconsistency).

**THE BREAKING POINT:**
A reporting team wants to add complex aggregation queries
to the same database. A customer-facing team wants
sub-100ms dashboard loads. A payments team needs strict
ACID semantics for order placement. One database model
cannot serve all three without significant compromise.

**THE INVENTION MOMENT:**
Separate the write model (optimized for consistency and
change) from the read model (optimized for fast, flat
query results). The read model is a derived, potentially
denormalized projection of the write model, maintained
synchronously or asynchronously.

---

### 📘 Textbook Definition

**CQRS (Command Query Responsibility Segregation)**
is an architectural pattern that separates write operations
(Commands - change state) from read operations (Queries -
read state) into distinct models, typically with distinct
data stores.

**CQS Principle (basis):**
Bertrand Meyer's Command-Query Separation: "A method
should either change state (Command) or return state
(Query), never both." CQRS applies this principle at
the architectural level.

**Command side:** Receives commands (`PlaceOrderCommand`).
Validates business rules. Updates the write model (normalized
relational or event store). Publishes domain events.
Must be strongly consistent.

**Query side:** Receives queries (`GetOrderDashboardQuery`).
Reads from the read model (denormalized, optimized
for the specific query). Returns a read model DTO.
May be eventually consistent. No business logic.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
CQRS = separate databases/models for reads and writes
so each can be independently optimized.

**One analogy:**
> A library has one catalog for returning books (write:
> "this book is back in location A-23") and a different
> catalog for searching books (read: indexed by author,
> subject, availability). The return catalog is optimized
> for fast, accurate updates. The search catalog is
> optimized for complex searches. They are synchronized
> when a book is returned. Neither model would work
> well if it had to serve both purposes.

**One insight:**
CQRS is not "one database for reads, one for writes."
It is "one MODEL for reads, one MODEL for writes." The
models can share the same physical database (light CQRS)
or use completely different storage technologies (full
CQRS). The key is the MODEL separation, which enables
independent evolution.

---

### 🔩 First Principles Explanation

**WHY READS AND WRITES NEED DIFFERENT MODELS:**

**Write model requirements:**
- Normalized (3NF): minimizes update anomalies
- ACID: transactional consistency
- Optimized for change: easy to apply domain logic
- Validates business invariants before persisting

**Read model requirements:**
- Denormalized: pre-joins data for fast reads
- No business logic: pure data retrieval
- Optimized for specific queries (composite indexes on read fields)
- May be eventually consistent (seconds behind writes is acceptable)
- May use a completely different storage technology
  (Elasticsearch for full-text search, Redis for real-time dashboards)

**THE INEVITABLE CONCLUSION:**
A model optimized for writes is NOT optimized for reads.
A model optimized for reads is NOT optimized for writes.
CQRS acknowledges this and builds separate models for each.

**SYNCHRONIZATION:**
The write model publishes domain events when state changes.
The read model subscribes to these events and updates
its projections. This creates eventual consistency:
the read model is usually seconds behind the write model.

**LIGHT vs FULL CQRS:**
- Light CQRS: same database, separate model classes.
  Commands use `OrderRepository` → `Order` entity.
  Queries use `OrderQueryRepository` → `OrderSummaryDto`.
  Benefit: simpler, same consistency. Trade-off: single
  DB still needs to support both workloads.
- Full CQRS: separate databases. Commands → write DB
  (PostgreSQL). Events published. Queries → read DB
  (Elasticsearch, Redis, denormalized PostgreSQL).
  Benefit: independent scaling, optimized storage.
  Trade-off: eventual consistency, operational complexity.

---

### 🧪 Thought Experiment

**BEFORE CQRS:**
Order dashboard query: `SELECT o.id, c.name, COUNT(oi.id),
SUM(oi.price), o.status FROM orders o JOIN customers c
ON o.customer_id = c.id JOIN order_items oi ON
o.id = oi.order_id WHERE o.status = 'ACTIVE' GROUP BY
o.id, c.name, o.status`. Executes on the write DB.
At 10,000 req/min: DB CPU at 80%. Placing orders slows
down (competing for the same connection pool and CPU).

**AFTER FULL CQRS:**
Dashboard query: `GET /api/orders/dashboard` → reads
from Elasticsearch `order_dashboard` index with pre-joined
flat document. Sub-10ms. Zero impact on write DB.
Orders placed: write to PostgreSQL, publish event,
Elasticsearch read model updated asynchronously (1-2s lag).
Dashboard data is 1-2 seconds old. This is acceptable.
Write DB: relieved of all read load. Order placement
response time: 50% faster.

---

### 🧠 Mental Model / Analogy

> CQRS is the OLTP vs OLAP distinction at the service level.
> OLTP (Online Transaction Processing): normalized, ACID,
> optimized for individual row operations.
> OLAP (Online Analytical Processing): denormalized,
> optimized for aggregate queries across many rows.
> Data warehouses synchronize OLAP from OLTP via ETL.
>
> CQRS does this at the service level:
> Write side = OLTP (transactional updates)
> Read side = OLAP projection (fast query model)
> Synchronization = domain events
>
> The insight: most applications need BOTH but usually
> build only the OLTP model and suffer slow reads.

---

### 📶 Gradual Depth - Five Levels

**Level 1 - What it is:**
CQRS means having two separate ways to access your data:
one optimized for changing data (commands), one optimized
for reading data (queries). They can use the same or
different databases.

**Level 2 - How to implement it:**
Create separate command and query objects. Command objects
change state and return void (or a command ID). Query
objects read state and return DTOs. Use separate repositories:
one for writes (uses domain entities), one for reads
(uses flat DTOs, possibly different storage).

**Level 3 - Synchronization mechanics:**
The write side publishes domain events after successful
writes. Event handlers on the read side consume these
events and update read model projections. The read model
is a "pre-computed join" - whatever the most common
query needs, stored ready to read.

**Level 4 - When CQRS is justified:**
CQRS adds significant complexity: two models, event
publishing, projection updates, eventual consistency.
Justified when:
- Read and write workloads have significantly different
  scaling requirements.
- The read model requires fundamentally different structure
  from the write model (complex aggregations, multiple
  joins).
- Multiple specialized read stores are needed (Elasticsearch
  for search, Redis for real-time, reporting DB for analytics).
Not justified for simple CRUD applications - the overhead
exceeds the benefit.

**Level 5 - Event Sourcing + CQRS:**
CQRS and Event Sourcing are often combined but are
independent patterns. Event Sourcing stores the HISTORY
of events (the write model IS the event log; current
state is derived by replaying events). CQRS builds
read projections from this event log. Together: the
audit log (every state change), time-travel debugging
(replay events to any point), and optimized read models
(project events to any read format). The trade-offs:
significantly higher complexity, eventual consistency,
and operational overhead of event replays.

---

### ⚙️ How It Works (Mechanism)

```
CQRS Architecture Flow

WRITE SIDE:
┌─────────────────────────────────────────────────────┐
│ Client → PlaceOrderCommand → CommandHandler         │
│          → validate → persist (write DB)            │
│          → publish OrderPlacedEvent                 │
└─────────────────────────────────────────────────────┘
                         │ event
                         ▼
READ SIDE (async update):
┌─────────────────────────────────────────────────────┐
│ OrderPlacedEvent → ProjectionUpdater                │
│                  → update order_dashboard (read DB) │
└─────────────────────────────────────────────────────┘

READ SIDE (query):
┌─────────────────────────────────────────────────────┐
│ Client → GetOrderDashboardQuery → QueryHandler      │
│          → read from order_dashboard (read DB)      │
│          → return flat DTO (no joins, fast)         │
└─────────────────────────────────────────────────────┘

Write DB: PostgreSQL (normalized, ACID)
Read DB:  Elasticsearch / Redis / denormalized PG
Sync:     ~1-2 second eventual consistency lag
```

---

### 💻 Code Example

**Example 1 - Symmetric CRUD (anti-pattern in complex domains):**

```java
// BAD: One repository serves both reads and writes
// Dashboard query performs 4 joins on the write DB

@Repository
interface OrderRepository extends JpaRepository<Order, String> {
    // Write query: fine, operates on normalized entity
    Optional<Order> findById(String id);

    // READ QUERY: 4-table join, complex grouping
    // This runs on the same DB handling all writes
    @Query("SELECT new OrderDashboardDto(o.id, c.name, " +
           "COUNT(oi), SUM(oi.price), o.status) " +
           "FROM Order o JOIN o.customer c " +
           "JOIN o.items oi WHERE o.status = :status " +
           "GROUP BY o.id, c.name, o.status")
    List<OrderDashboardDto> getDashboard(OrderStatus status);
    // Scales poorly: dashboard queries compete with writes
    // Cannot use Elasticsearch for full-text or Redis for speed
}
```

**Example 2 - Light CQRS (same DB, separate model objects):**

```java
// GOOD (Light CQRS): Separate command and query sides

// COMMAND SIDE: domain model, business rules
@Service
class OrderCommandService {
    @Autowired OrderWriteRepository writeRepo;
    @Autowired ApplicationEventPublisher events;

    @Transactional
    public String placeOrder(PlaceOrderCommand cmd) {
        Order order = Order.create(cmd);  // domain model
        order.validate();
        writeRepo.save(order);
        events.publishEvent(new OrderPlacedEvent(order.getId()));
        return order.getId();
        // Returns command ID, not the read model
    }
}

// QUERY SIDE: flat DTO, no domain logic
@Service
class OrderQueryService {
    @Autowired OrderReadRepository readRepo;

    public OrderDashboardDto getDashboard(String customerId) {
        // Reads from a separate view or denormalized table
        return readRepo.findDashboard(customerId);
        // No joins, no entity loading, fast DTO projection
    }
}

// SEPARATE REPOSITORIES:
interface OrderWriteRepository extends JpaRepository<Order, String> {
    // Full domain entity access
}

interface OrderReadRepository extends Repository<OrderDashboard,
    String> {
    // Read model: denormalized, query-optimized DTOs
    @Query("SELECT new OrderDashboardDto(o.id, o.customerName,
        ...) " +
           "FROM OrderDashboard o WHERE o.customerId = :customerId")
    OrderDashboardDto findDashboard(String customerId);
}
```

**Example 3 - Full CQRS with event-driven projection:**

```java
// Full CQRS: events drive read model updates

// Command side publishes events:
@EventListener
class OrderProjectionUpdater {

    @Autowired ElasticsearchOrderRepository esRepo;

    // When an order is placed: update the Elasticsearch read model
    @Async
    @TransactionalEventListener(phase = AFTER_COMMIT)
    public void onOrderPlaced(OrderPlacedEvent event) {
        Order order = orderWriteRepo.findById(event.getOrderId())
            .orElseThrow();
        // Build the flat read model from the domain entity
        OrderSearchDocument doc = OrderSearchDocument.builder()
            .id(order.getId())
            .customerName(order.getCustomer().getFullName())
            .itemCount(order.getItems().size())
            .total(order.calculateTotal())
            .status(order.getStatus().name())
            .build();
        esRepo.save(doc); // Update the Elasticsearch read model
        // Query side will see this update in ~1 second
    }
}

// Query side reads from Elasticsearch (sub-10ms, full-text search):
@Service
class OrderQueryService {
    @Autowired ElasticsearchOrderRepository esRepo;

    public List<OrderSearchDocument> searchOrders(String text) {
        // Full-text search, impossible with SQL efficiently
        return esRepo.findByCustomerNameOrItemName(text);
    }
}
```

---

### ⚖️ When to Use CQRS

| Factor | Without CQRS | With CQRS |
|---|---|---|
| Read/write ratio | ~Equal | Reads >> Writes (10:1+) |
| Read complexity | Simple lookups | Complex joins, aggregations |
| Scale requirements | Single DB handles both | Read/write scale independently |
| Consistency tolerance | Strong consistency required | Eventual consistency acceptable |
| Team experience | CRUD familiar | Distributed systems experience |
| Application type | Simple CRUD | Complex domain, high traffic |

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| CQRS requires Event Sourcing | They are complementary but independent. CQRS separates read and write models. Event Sourcing stores state as a sequence of events. Many CQRS implementations use traditional relational writes + domain events for read model projection |
| CQRS means two databases | CQRS means two models. They can share a database (light CQRS). Full CQRS uses separate storage, but this is an optimization, not a requirement |
| CQRS is always better than standard CRUD | CQRS adds significant complexity. For simple CRUD applications, CQRS introduces two models, eventual consistency, event infrastructure, and projection maintenance for zero benefit |
| Read models must be eventually consistent | Light CQRS with a single DB can have synchronous read model updates. Full CQRS with separate stores introduces eventual consistency, but this is a consequence of the distributed storage choice, not of CQRS itself |

---

### 🚨 Failure Modes & Diagnosis

**Read Model Out of Sync**

**Symptom:**
User places an order. Immediately refreshes the dashboard.
Order not visible. Visible 2 seconds later.

**Root Cause:**
Eventual consistency lag: the Elasticsearch projection
is updated asynchronously after the write commits.

**Diagnosis:**
Check Kafka consumer lag on the projection update topic.
Check `OrderProjectionUpdater` logs for processing time.

**Fix:**
For critical read-after-write scenarios: after placing
an order, redirect to a "confirmation" page that reads
directly from the write DB (not the read model). Use
the read model for searches and dashboards, not for
immediate post-write confirmation.

---

### 🔗 Related Keywords

**Prerequisite:**
- `Specification Pattern` - DPT-040: query side uses
  Specifications as predicates
- `Dependency Injection` - DPT-039

**Builds on this:**
- `Outbox Pattern` - DPT-053: reliably publish events
  from the write side to the read model
- `Saga Pattern` - DPT-054: coordinate multi-step commands

---

### 📌 Quick Reference Card

```
┌─────────────────────────────────────────────────────────┐
│ WHAT IT IS   │ Separate read model (Query) from write   │
│              │ model (Command): each independently      │
│              │ optimized                                │
├──────────────┼──────────────────────────────────────────┤
│ COMMAND SIDE │ Validates business rules, writes, emits  │
│              │ domain events. Returns command ID.       │
├──────────────┼──────────────────────────────────────────┤
│ QUERY SIDE   │ Reads from denormalized read model.      │
│              │ Fast, flat, no business logic.           │
├──────────────┼──────────────────────────────────────────┤
│ CONSISTENCY  │ Light CQRS: synchronous (same DB)        │
│              │ Full CQRS: eventual (~seconds lag)       │
├──────────────┼──────────────────────────────────────────┤
│ USE WHEN     │ Reads >>> Writes AND complex queries AND │
│              │ different scaling for read vs write      │
├──────────────┼──────────────────────────────────────────┤
│ NEXT EXPLORE │ DPT-053: Outbox Pattern                  │
└─────────────────────────────────────────────────────────┘
```

**If you remember only 3 things:**
1. CQRS = separate models for reads (Query) and writes
   (Command). Write model: normalized, ACID, domain rules.
   Read model: denormalized, fast, query-optimized. Each
   independently optimized and scaled.
2. Synchronization: the write side publishes events when
   state changes. The read side consumes events and updates
   its projections. Result: eventual consistency (seconds).
3. Use CQRS when reads and writes have fundamentally
   different requirements (complexity, scale, storage technology).
   Do NOT use for simple CRUD - the complexity far exceeds
   the benefit.

