---
layout: default
title: "CQRS"
parent: "Distributed Systems"
nav_order: 615
permalink: /distributed-systems/cqrs/
number: "0615"
category: Distributed Systems
difficulty: ★★★
depends_on: Event Sourcing, Saga Pattern, Eventual Consistency, CRUD
used_by: Event Sourcing, Outbox Pattern, Read Model Projections, DDD
related: Event Sourcing, Saga Pattern, Outbox Pattern, Eventual Consistency, Domain Events
tags:
  - distributed
  - architecture
  - pattern
  - data
  - deep-dive
---

# 615 — CQRS

⚡ TL;DR — CQRS (Command Query Responsibility Segregation) splits an application's data model into two: a Write model (Commands — optimized for transactional writes) and a Read model (Queries — optimized for read patterns), allowing each to be independently optimized, scaled, and structured.

| #615 | Category: Distributed Systems | Difficulty: ★★★ |
|:---|:---|:---|
| **Depends on:** | Event Sourcing, Saga Pattern, Eventual Consistency, CRUD | |
| **Used by:** | Event Sourcing, Outbox Pattern, Read Model Projections, DDD | |
| **Related:** | Event Sourcing, Saga Pattern, Outbox Pattern, Eventual Consistency, Domain Events | |

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
An order system uses one SQL schema for both writes (place order, update status, add item) and reads (dashboard showing order count by customer, order details page, admin overview). The write model is normalized (3NF, transactional). The read model needs denormalized joins — a `GET /orders/dashboard` query joins Orders, Customers, Products, Inventory, and Shipment tables: 5 JOINs, slow. The schema can't be optimized for both: normalizing for writes hurts reads; denormalizing for reads introduces write anomalies.

**WITH CQRS:**
Write path: normalized relational DB, small transactions, ACID guarantees. Each write emits a domain event. Read path: separate read model (projected from domain events) — fully denormalized, pre-joined, structured exactly for each query. Dashboard query: `SELECT * FROM order_dashboard_projection WHERE customer_id = ?` — one row, zero joins, instant. Read model and write model can be different databases (RDBMS for writes, Elasticsearch/Redis for reads).

---

### 📘 Textbook Definition

**CQRS** (Command Query Responsibility Segregation) is an architectural pattern that separates operations that **change state** (Commands) from operations that **read state** (Queries). Each side has its own model: the **Command model** handles state mutations and enforces business invariants; the **Query model** is denormalized and optimized for specific read patterns. The two models are synchronized — typically via domain events published by the command side, consumed by read model projectors that update the query database. **CQS vs CQRS**: CQS (Bertrand Meyer) says methods should either return a value (Query) or modify state (Command) — never both. CQRS extends this to architecture: completely separate models at the data layer, not just method signatures. **Consistency**: CQRS with event-based projection introduces **eventual consistency** — the read model lags behind writes by the event propagation latency (milliseconds to seconds).

---

### ⏱️ Understand It in 30 Seconds

**One line:**
Separate the database for writes (normalized, transactional) from the database for reads (denormalized, query-optimized) — and sync them via events.

**One analogy:**
> CQRS is like an accounting department split into two teams: the bookkeepers (command side) record all transactions with rigorous double-entry accounting (normalized, transactional). The reports analysts (query side) maintain pre-computed summary spreadsheets for management (read projections). Each bookkeeping entry automatically updates the summary spreadsheets. The analysts never write to the books; the bookkeepers don't compute reports. Each team's tools are optimized for their job.

**One insight:**
CQRS solves the **impedance mismatch** between write schemas (optimized for consistency → normalized) and read schemas (optimized for speed → denormalized). Most systems are read-heavy (10:1 to 100:1 read/write ratio). CQRS allows the read path — which serves 90–99% of traffic — to be independently optimized, scaled, and structured without any constraint from write-side schema requirements.

---

### 🔩 First Principles Explanation

**CQRS + EVENT SOURCING ARCHITECTURE:**
```
WRITE SIDE (Command Model):
  POST /orders — creates Order aggregate
    1. Load Order aggregate from event store.
    2. Apply command: order.placeOrder(items, customerId).
    3. Generate domain events: [OrderPlaced, ItemsReserved].
    4. Persist events to event store.
    5. Publish events to event bus (Kafka/RabbitMQ).
    
  → Write DB: Event Store (append-only log of domain events)
    Events: [OrderPlaced, OrderConfirmed, OrderShipped, OrderDelivered]

READ SIDE (Query Model — Event Projectors):
  Event Projector subscribes to domain events:
    ON OrderPlaced:
      INSERT INTO order_summary_projection (id, customer, status, total)
      VALUES (event.orderId, event.customer, 'PLACED', event.total)
      
    ON OrderShipped:
      UPDATE order_summary_projection 
      SET status='SHIPPED', trackingNo=event.trackingNo
      WHERE id = event.orderId
      
    ON OrderDelivered:
      UPDATE order_summary_projection
      SET status='DELIVERED', deliveredAt=event.timestamp
      WHERE id = event.orderId
      
  → Read DB: Relational DB / Redis / Elasticsearch (pre-computed, denormalized)
    GET /orders/customer/123 → SELECT * FROM order_summary_projection WHERE customer=123
    Zero joins. Millisecond response.
```

**SEPARATE MODELS, SEPARATE SCALING:**
```
Traffic profile: 1000 reads/second, 10 writes/second (100:1 ratio)

Without CQRS:
  One database serving both. Must scale for 1000 reads/second.
  Write queries compete with read queries for database connections.
  Adding read replicas helps reads but write DB is still constrained.

With CQRS:
  Write DB: 10 writes/second. Can use a small RDS instance. ACID, normalized.
  Read DB: 1000 reads/second. Can use distributed Redis or Elasticsearch.
             Can add sharding/replicas independently.
  Write DB is now a quiet, reliable transaction store.
  Read DB scales horizontally for read traffic.
```

**SPRING CQRS IMPLEMENTATION (AXON FRAMEWORK):**
```java
// COMMAND SIDE — handle OrderPlaceCommand:
@Aggregate
public class OrderAggregate {

    @AggregateIdentifier
    private String orderId;
    private OrderStatus status;

    @CommandHandler
    public OrderAggregate(PlaceOrderCommand command) {
        // Validate, then apply event:
        AggregateLifecycle.apply(new OrderPlacedEvent(
            command.getOrderId(),
            command.getItems(),
            command.getCustomerId()
        ));
    }

    @EventSourcingHandler
    public void on(OrderPlacedEvent event) {
        this.orderId = event.getOrderId();
        this.status = OrderStatus.PLACED;
    }
}

// READ SIDE — project OrderPlacedEvent into read model:
@Component
public class OrderSummaryProjection {

    @Autowired
    private OrderSummaryRepository readRepo;

    @EventHandler
    public void on(OrderPlacedEvent event) {
        readRepo.save(OrderSummary.builder()
            .id(event.getOrderId())
            .customerId(event.getCustomerId())
            .status("PLACED")
            .itemCount(event.getItems().size())
            .createdAt(event.getTimestamp())
            .build());
    }

    @QueryHandler
    public List<OrderSummary> handle(GetCustomerOrdersQuery query) {
        return readRepo.findByCustomerId(query.getCustomerId());
    }
}
```

---

### 🧪 Thought Experiment

**READ MODEL REBUILD:**

Production incident: a bug in the projector populated the read model incorrectly for 3 days. Order totals are wrong in the dashboard.

**With event sourcing + CQRS**: fix the projector code. Drop the read model table entirely. Replay all events from the event store from the beginning. Projector re-processes every event with the fixed code → read model rebuilt correctly. Duration: depends on event count (minutes to hours for large systems).

**Without event sourcing (just CQRS with synchronous projection)**: the source of truth is the write DB (relational). To rebuild: query all orders from write DB, reproject each one. Same outcome.

**Key insight**: CQRS without event sourcing is valid and simpler — the write side is a regular relational DB; projections are computed from the write DB state on change. CQRS WITH event sourcing adds the ability to replay and rebuild read models from the complete event history, at the cost of complexity.

---

### 🧠 Mental Model / Analogy

> CQRS is like a bookstore: the stock management system (write side) tracks exact inventory with SKU, location, quantity — optimized for accurate inventory changes. The customer-facing website (read side) shows a product catalog optimized for browsing — images, descriptions, "In Stock" indicators, pre-computed. Any purchase (command) updates inventory and triggers an event that updates the catalog's "In Stock" indicator within seconds. The catalog is eventually consistent — but it serves millions of page views efficiently.

---

### 📶 Gradual Depth — Four Levels

**Level 1:** CQRS = separate write model and read model. Writes use normalized schema. Reads use denormalized, query-optimized schema. Sync via events. Reads are eventually consistent.

**Level 2:** Command model: aggregate-based, enforces invariants, emits domain events. Query model: projections from events, denormalized per read use-case, separate DB (Redis/Elasticsearch/SQL). Separate scaling. Rebuild read models by replaying events.

**Level 3:** Axon Framework: Java CQRS+EventSourcing framework. Event projectors: idempotent (same event replayed = same result). Multi-projection: same event feeds multiple read models (dashboard projection, search index projection, notifications service — all from the same event stream). Eventual consistency window: milliseconds in Kafka-backed systems; acceptable for most read use-cases.

**Level 4:** CQRS complexity is only justified for: (1) significantly different read vs. write scaling requirements, (2) multiple read patterns with conflicting schema needs, (3) audit/rebuild requirements (event sourcing). For simple CRUDs: CQRS is over-engineering. Mistake pattern: applying CQRS to every microservice regardless of complexity. Only use where the read/write model impedance mismatch is measurable. DDD Aggregates align naturally with CQRS: each aggregate's command handler is the write side; its domain events project to read side. Eventual consistency management: expose `ETag`/version in write response; read-side includes version; client retries read until version matches write (read-your-writes consistency pattern on top of eventual consistency).

---

### ⚙️ How It Works (Mechanism)

**Simple CQRS without Event Sourcing (Spring, PostgreSQL + Redis):**
```java
// Write service: updates normalized DB + publishes event
@Transactional
public OrderId placeOrder(PlaceOrderRequest cmd) {
    Order order = new Order(cmd.getCustomerId(), cmd.getItems());
    Order saved = orderRepository.save(order); // Write to normalized PostgreSQL
    
    // Publish domain event (via Outbox Pattern for reliability):
    outboxRepository.save(new OutboxMessage("order.placed", 
        objectMapper.writeValueAsString(new OrderPlacedEvent(saved.getId(), ...))));
    
    return saved.getId();
}

// Event projector (runs async after Outbox publishes to Kafka):
@KafkaListener(topics = "order.placed")
public void projectOrderPlaced(OrderPlacedEvent event) {
    // Update Redis read model (pre-computed for dashboard):
    redisTemplate.opsForValue().set(
        "order:summary:" + event.getOrderId(),
        new OrderSummaryDto(event.getOrderId(), event.getStatus(), event.getTotal()),
        Duration.ofDays(30)
    );
    
    // Update Elasticsearch (for search):
    elasticsearchClient.index(i -> i
        .index("orders")
        .id(event.getOrderId())
        .document(new OrderSearchDoc(event))
    );
}

// Read query — zero DB joins:
public OrderSummaryDto getOrderSummary(String orderId) {
    return redisTemplate.opsForValue().get("order:summary:" + orderId);
}
```

---

### ⚖️ Comparison Table

| Aspect | CRUD (Single Model) | CQRS |
|---|---|---|
| Schema | One schema for all operations | Separate write (normalized) + read (denormalized) |
| Read performance | JOINs required for complex views | Pre-projected, zero joins |
| Write performance | Direct, simple | Same; plus event publishing overhead |
| Consistency | Immediate (same DB) | Eventual (projection lag) |
| Complexity | Low | High |
| Best for | Simple stable data models | Complex reads, high read:write ratio, audit needs |

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| CQRS requires event sourcing | CQRS and Event Sourcing are independent patterns. CQRS organizes the read/write separation; Event Sourcing is an option for the write model (append-only events as source of truth) |
| CQRS means two different microservices | CQRS can be implemented within one service (two internal models, two data stores). Splitting into separate services adds more complexity — only justified if teams own the models independently |
| Read model is always eventually consistent | With synchronous projection (in same transaction as write): read can be immediately consistent. Async/event-based projection = eventually consistent |

---

### 🚨 Failure Modes & Diagnosis

**Read Model Desync (Projector Failure)**

Symptom: Customer dashboard shows orders as "PLACED" but they were actually shipped
yesterday. Event projector has a bug that causes it to skip `OrderShipped` events.
Dead letter queue is filling up with unprocessed events.

Cause: Projector threw an uncaught exception on `OrderShipped` events (NPE — tracking
number was null in test data, not expected in production).

Fix: (1) Immediately: fix the projector to handle null tracking numbers.
(2) Recovery: replay `OrderShipped` events from the DLQ (dead letter queue).
(3) Verify: compare read model checksums against write model counts.
(4) Prevention: projectors must be idempotent (replay-safe); add specific test for
events with null/missing optional fields. Consider projector crash as a P1 alert
(users see stale data — business impact, not just technical).

---

### 🔗 Related Keywords

- `Event Sourcing` — often used as the write model in CQRS; provides rebuild-from-events capability
- `Saga Pattern` — commands trigger sagas; saga completion events update read models
- `Outbox Pattern` — ensures reliable event publishing from command side to read model projectors
- `Eventual Consistency` — the consistency model for CQRS read models
- `Domain Events` — the communication mechanism between command and query sides

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│  CQRS: Command (write) / Query (read) separation         │
│  Write model: normalized, ACID, aggregate-based          │
│  Read model: denormalized, query-optimized, per-use-case │
│  Sync: domain events from write → projectors → read DB   │
│  Consistency: eventual (projector lag) or sync (same tx) │
│  Rebuild: replay events → repopulate read model          │
│  Use when: complex reads, high read:write ratio, audit   │
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** An order management system uses CQRS. A customer places an order via POST (command side responds 201 with the new orderId). The customer immediately fetches their order list via GET. The read model projector has a 200ms lag. The GET returns a list that doesn't include the just-placed order. What strategies can you use to provide read-your-writes consistency for this scenario without eliminating the CQRS separation? Describe at least two approaches.

**Q2.** A CQRS system has 5 different read projections built from the same domain events (order_summary, order_search_index, customer_order_stats, admin_dashboard, notification_triggers). A business requirement changes: OrderPlacedEvent now includes a new `promotionCode` field. Which projections need to be updated? If a projection is NOT updated, what happens when it receives an OrderPlacedEvent with the new field? Design a schema evolution strategy for CQRS projections that minimizes the risk of projection breakage when domain events evolve.
