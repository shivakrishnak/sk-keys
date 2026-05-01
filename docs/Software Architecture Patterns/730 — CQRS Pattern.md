---
layout: default
title: "CQRS Pattern"
parent: "Software Architecture Patterns"
nav_order: 730
permalink: /software-architecture/cqrs-pattern/
number: "730"
category: Software Architecture Patterns
difficulty: ★★★
depends_on: "Command-Query Separation, Event Sourcing, Vertical Slice Architecture"
used_by: "Event-driven systems, Axon Framework, MediatR, EventStore, DDD applications"
tags: #advanced, #architecture, #cqrs, #event-sourcing, #command-query
---

# 730 — CQRS Pattern

`#advanced` `#architecture` `#cqrs` `#event-sourcing` `#command-query`

⚡ TL;DR — **CQRS** (Command Query Responsibility Segregation) splits the system into two separate models: a **Write Model** (commands that change state) and a **Read Model** (queries that return data) — enabling each to be optimized independently.

| #730            | Category: Software Architecture Patterns                                    | Difficulty: ★★★ |
| :-------------- | :-------------------------------------------------------------------------- | :-------------- |
| **Depends on:** | Command-Query Separation, Event Sourcing, Vertical Slice Architecture       |                 |
| **Used by:**    | Event-driven systems, Axon Framework, MediatR, EventStore, DDD applications |                 |

---

### 📘 Textbook Definition

**CQRS** (Command Query Responsibility Segregation), coined by Greg Young (building on Bertrand Meyer's Command-Query Separation principle), is an architectural pattern that uses separate models for reads (queries) and writes (commands). A **Command** is an intent to change state — it may fail, returns no data (or minimal acknowledgment). A **Query** is a request for data — it has no side effects, always returns data. Benefits of separation: (1) **Independent scaling** — reads and writes scale differently (read-heavy apps: scale read model horizontally). (2) **Optimized models** — write model: normalized, domain-rule-enforcing. Read model: denormalized, query-optimized projections. (3) **Technology freedom** — write to PostgreSQL (ACID), read from Elasticsearch (search) or Redis (cache). (4) **Event Sourcing integration** — CQRS pairs naturally with Event Sourcing: commands generate events; events build read model projections. CQRS adds complexity: two models must stay in sync (eventual consistency). Only appropriate for complex, high-scale, or event-driven systems — overkill for simple CRUD.

---

### 🟢 Simple Definition (Easy)

A library: when adding a book (command/write), the librarian follows strict rules: validate ISBN, check duplicates, update the master catalog. When searching for a book (query/read), a fast search index is used: no validation, no rules, just fast lookup. Two different systems for two different jobs. The write system is strict and correct; the read system is fast and denormalized. The search index is updated when new books are added (projection). Most people search — rarely does anyone add a new book. Scale the search index independently from the add-book system.

---

### 🔵 Simple Definition (Elaborated)

Without CQRS: one model (the JPA entity) handles both reads and writes. Problem: writes need transaction handling, domain rules, complex validations. Reads need fast response, JOIN-heavy queries, different views per user type (admin sees more data than regular user). Serving all these needs from one model: compromise. With CQRS: write model is your normalized domain model (with rules). Read model is a dedicated projection — a view optimized for exactly what the frontend needs. Change an item name: write model updates the item table. A projection listener updates the item's denormalized representation in the read model. Next read: fast, pre-computed, no JOIN needed.

---

### 🔩 First Principles Explanation

**Write model, read model, projection, sync strategies, and CQRS levels:**

```
CQRS LEVELS (choose complexity appropriate to your needs):

  LEVEL 1: Simple CQRS (same database, separate models in code):

    Write Model:                        Read Model:
    ┌─────────────────────────┐        ┌─────────────────────────┐
    │ Order (domain entity)   │        │ OrderSummaryDTO          │
    │ - id                    │        │ - orderId               │
    │ - customerId            │        │ - customerName          │
    │ - items: List<Item>     │        │ - itemCount             │
    │ - status: OrderStatus   │        │ - total                 │
    │ - rules: confirm(),     │        │ - statusLabel           │
    │   cancel(), ship()      │        │ (denormalized for UI)   │
    └─────────────────────────┘        └─────────────────────────┘

    Both models: read from SAME database.
    Write path: uses JPA entities + domain rules.
    Read path: uses JDBC/JPA projections mapped to flat DTOs.

    BENEFIT: Optimized SQL queries for reads (no domain object overhead).
    COMPLEXITY: Low. Same DB. No eventual consistency.

  LEVEL 2: Separate Read Store:

    Commands:                           Queries:
    ┌──────────────────────┐           ┌──────────────────────┐
    │ Command Handler       │           │ Query Handler         │
    │ → Domain Model        │           │ → Read Model          │
    │ → PostgreSQL (write)  │◄─────────►│ → Elasticsearch       │
    └──────────────────────┘   sync    └──────────────────────┘

    Write: PostgreSQL (ACID, normalized, domain model).
    Read: Elasticsearch (full-text search, fast, denormalized documents).
    Sync: event listener / projection updates Elasticsearch on write.

    BENEFIT: Each store optimized for its purpose.
    COMPLEXITY: Eventual consistency between stores.

  LEVEL 3: CQRS + Event Sourcing (full):

    Commands:                           Events:                     Read Models:
    ┌───────────────┐  generates   ┌──────────────┐  projects   ┌──────────────┐
    │ Command       │─────────────►│ Event Store   │────────────►│ Projection 1 │
    │ Handler       │              │ (append-only) │             │ (OrderView)  │
    │               │              │               │────────────►│ Projection 2 │
    └───────────────┘              └──────────────┘             │ (Analytics)  │
                                                                  └──────────────┘

    Write: commands produce events (immutable log).
    Read: event projections build multiple read model views.

    BENEFIT: Full audit trail; temporal queries; multiple specialized views.
    COMPLEXITY: High. Eventual consistency. Projection management.

COMMAND HANDLING:

  Command: intent to change state. Named in imperative: PlaceOrder, CancelOrder, ApprovePayment.

  @Component
  public class PlaceOrderCommandHandler {
      private final OrderRepository orderRepo;
      private final EventBus eventBus;

      public PlaceOrderAcknowledgment handle(PlaceOrderCommand command) {
          // 1. Load write-side aggregate (domain model):
          Customer customer = customerRepo.findById(command.customerId());

          // 2. Apply business rules:
          customer.validateCanPlaceOrder();
          Order order = Order.place(command.customerId(), command.items());

          // 3. Persist (write model):
          orderRepo.save(order);

          // 4. Publish event (triggers read model projection):
          eventBus.publish(new OrderPlacedEvent(order.id(), command.customerId(), order.total()));

          // 5. Return minimal acknowledgment (NOT the full order — queries do that):
          return new PlaceOrderAcknowledgment(order.id());
      }
  }

QUERY HANDLING:

  Query: read-only. Uses read model (optimized projection).

  @Component
  public class GetOrderSummaryQueryHandler {
      private final OrderSummaryProjection readModel;

      public OrderSummaryDTO handle(GetOrderSummaryQuery query) {
          // No domain model. No JPA entity. Direct read from projection.
          return readModel.findById(query.orderId());
          // readModel: could be a Redis hash, Elasticsearch document, denormalized DB view.
          // No domain rules applied — read models are simple data fetchers.
      }
  }

READ MODEL PROJECTION (kept in sync with write model):

  @EventHandler
  public class OrderSummaryProjectionUpdater {
      private final OrderSummaryProjection readModel;

      // Triggered when OrderPlacedEvent is published:
      public void on(OrderPlacedEvent event) {
          // Fetch additional data needed for the read model:
          String customerName = customerReadRepo.getNameById(event.customerId());

          // Build denormalized read model entry:
          OrderSummaryDTO dto = new OrderSummaryDTO(
              event.orderId(),
              customerName,          // Denormalized: customer name pre-joined.
              event.items().size(),  // Denormalized: item count pre-computed.
              event.total(),
              "PENDING"
          );
          readModel.save(dto);
      }

      public void on(OrderCancelledEvent event) {
          readModel.updateStatus(event.orderId(), "CANCELLED");
      }
  }

CQRS WITHOUT EVENT SOURCING:

  Commands → update write database → trigger projection update (synchronously or via DB trigger).

  Synchronous projection:
    After command saves to PostgreSQL: immediately update Redis read cache.
    Advantage: consistent. Disadvantage: write latency includes cache update.

  Asynchronous projection (Debezium CDC):
    Command writes to PostgreSQL.
    Debezium reads PostgreSQL WAL (write-ahead log) → publishes change events.
    Kafka consumer: updates read model asynchronously.
    Advantage: decoupled, fast writes. Disadvantage: read model eventually consistent.

CONSISTENCY IMPLICATIONS:

  "I placed an order. Now query it immediately."
  In eventually consistent CQRS: the query read model may not yet have the new order.

  Solutions:
    1. Return the command result (the new entity) from the command response.
       Client: uses command response for immediate display. Fetches from read model later.

    2. Wait for projection with correlation ID.
       Command returns orderId. Client polls: "GET /orders/{id}/status" until read model ready.

    3. Optimistic UI: client assumes success, displays immediately. Background sync confirms.

    4. Synchronous projection: update read model in same transaction as write.
       Consistent but: defeats the purpose of separate read model (tight coupling, no async).
```

---

### ❓ Why Does This Exist (Why Before What)

WITHOUT CQRS:

- One model handles reads and writes: compromises on both (normalized schema is slow to query; denormalized is hard to write to correctly)
- Can't scale reads independently from writes (same database, same model)
- Adding a new "view" of data requires JOIN-heavy queries or polluting the domain model

WITH CQRS:
→ Write model: lean, domain-rule-enforcing, normalized — optimized for correctness
→ Read model: denormalized, pre-computed projections — optimized for query speed
→ Independent scaling: add read replicas/caches without touching write path

---

### 🧠 Mental Model / Analogy

> An accounting firm: the bookkeeper (write side) records every transaction with strict rules, validation, and audit trails in the official ledger. The CFO (read side) uses a separate summary dashboard — denormalized, pre-computed, shows revenue by region, month, category. The dashboard is built from the ledger but in a different format optimized for executive consumption. Commands: "record this expense." Queries: "show me Q3 profitability by region." Two separate models for two separate jobs.

"Official ledger" = write model (normalized, domain rules)
"CFO dashboard" = read model (denormalized, query-optimized projection)
"Bookkeeper recording transaction" = command handler
"CFO reading dashboard" = query handler
"Dashboard updated from ledger" = projection/sync mechanism

---

### ⚙️ How It Works (Mechanism)

```
CQRS FLOW:

  COMMAND PATH:
    Client → POST /orders → Command Handler → Domain Model → Write DB → Publish Event

  PROJECTION PATH:
    Event → Projection Handler → Build/Update Read Model → Read DB/Cache

  QUERY PATH:
    Client → GET /orders/summary → Query Handler → Read DB/Cache → DTO → Response

  KEY: Command path and Query path are INDEPENDENT.
       Scale read path: add more read model replicas.
       Scale write path: add more command processors.
```

---

### 🔄 How It Connects (Mini-Map)

```
Command-Query Separation (CQS) — the method-level principle CQRS elevates to architecture
        │
        ▼ (architectural-scale CQS)
CQRS Pattern ◄──── (you are here)
(separate write model + read model, projections to sync)
        │
        ├── Event Sourcing: write model generates events; events build projections
        ├── Vertical Slice Architecture: commands/queries are natural slice boundaries
        └── Event-Driven Architecture: event bus carries domain events to projections
```

---

### 💻 Code Example

```java
// Level 1 CQRS: Same DB, separate code paths:

// COMMAND (write path):
@Transactional
public ConfirmationId handle(CreateOrderCommand cmd) {
    Order order = Order.create(cmd.customerId(), cmd.items());  // Domain rules applied.
    orderWriteRepo.save(order);  // Writes to normalized orders table.
    return new ConfirmationId(order.id());
}

// QUERY (read path — no domain object, direct SQL projection):
public OrderListDTO handle(GetOrdersForCustomerQuery query) {
    // Direct SQL JOIN + projection: no domain object needed for a simple read:
    return jdbcTemplate.query(
        """
        SELECT o.id, o.created_at, o.status, COUNT(oi.id) as item_count, SUM(oi.price) as total
        FROM orders o
        JOIN order_items oi ON o.id = oi.order_id
        WHERE o.customer_id = ?
        GROUP BY o.id, o.created_at, o.status
        ORDER BY o.created_at DESC
        """,
        (rs, row) -> new OrderListItem(
            rs.getObject("id", UUID.class),
            rs.getTimestamp("created_at").toInstant(),
            rs.getString("status"),
            rs.getInt("item_count"),
            rs.getBigDecimal("total")
        ),
        query.customerId()
    );
}
```

---

### ⚠️ Common Misconceptions

| Misconception                | Reality                                                                                                                                                                                                                                                                                                                                   |
| ---------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| CQRS requires Event Sourcing | CQRS and Event Sourcing are independent patterns that complement each other well but are not required together. Level 1 CQRS: same database, separate code paths. Level 2: separate databases. Level 3: Event Sourcing + CQRS. Most applications benefit from Level 1 CQRS (separate query paths) without Event Sourcing complexity       |
| Commands must return nothing | While CQS says commands return void, pragmatic CQRS allows commands to return a confirmation ID or acknowledgment. Returning the full entity from a command blurs the boundary (the read model should serve that). Returning just the new entity's ID is common and acceptable: it lets the client query the read model for the full view |
| CQRS means two databases     | Two databases are one option, not a requirement. Level 1 CQRS: one database, two code paths. Even with one database, separate query projections and domain models provide most of CQRS's testability and separation benefits                                                                                                              |

---

### 🔥 Pitfalls in Production

**Read model eventually consistent — client reads stale data immediately after write:**

```
SCENARIO:
  User: places an order. POST /orders → 201 Created with orderId = "abc-123".
  User: immediately navigates to order history page.
  Frontend: GET /orders?customerId=X → uses read model.

  Write model: saved to PostgreSQL (sync, successful).
  Projection: asynchronously updating Elasticsearch via Kafka (lag: ~500ms).

  READ RESULT 200ms after write:
    Elasticsearch: order "abc-123" NOT YET in index (projection lag).
    Response: order history doesn't include "abc-123".
    User: "Where is my order? I just placed it!"

BAD: Assuming read model immediately reflects write:
  @PostMapping("/orders")
  public ResponseEntity<String> placeOrder(@RequestBody PlaceOrderCommand cmd) {
      commandBus.send(cmd);
      return ResponseEntity.status(201).body("Order placed");
      // Frontend: GET /orders immediately. Read model: stale. UX issue.
  }

FIX 1: Return enough data in command response for optimistic UI:
  @PostMapping("/orders")
  public ResponseEntity<OrderConfirmation> placeOrder(@RequestBody PlaceOrderCommand cmd) {
      OrderId orderId = commandBus.send(cmd);
      // Return the created order data in the command response:
      // Client doesn't need to immediately query the read model.
      return ResponseEntity.status(201).body(new OrderConfirmation(
          orderId, cmd.items(), Instant.now(), "PENDING"
      ));
  }
  // Frontend: displays order from command response. No immediate GET /orders needed.
  // Eventually consistent read model: used when user refreshes (by then, projection done).

FIX 2: Include a "version" in the command response. Client waits for read model to catch up:
  // Command response includes a version or event sequence number:
  // { orderId: "abc-123", commandVersion: 42 }

  // Client polls: GET /orders/abc-123?minVersion=42
  // Query handler: if read model version < 42, return 202 Accepted (not ready yet).
  // Client: retry after 100ms. Eventually: read model at version 42+. Return order.

FIX 3: For critical reads immediately after write — query the WRITE model:
  @GetMapping("/orders/{id}/status")
  public OrderStatus getOrderStatus(@PathVariable UUID id) {
      // Read from write model (PostgreSQL) for strong consistency:
      return orderWriteRepo.findById(id).map(Order::status).orElseThrow();
      // Slightly slower (hits primary DB, not cache/Elasticsearch).
      // Use for: "Is my payment confirmed?" (critical). Not for: "List all my orders."
  }
  // Hybrid: critical reads → write model; non-critical reads → read model.
```

---

### 🔗 Related Keywords

- `Event Sourcing` — natural companion: commands generate events; events build read model projections
- `Command-Query Separation` — the method-level principle CQRS elevates to architecture
- `Vertical Slice Architecture` — commands and queries become natural slice boundaries
- `Eventual Consistency` — the tradeoff when read and write models are asynchronously synced
- `Projection` — the mechanism that builds the read model from write-side events or changes

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ KEY IDEA     │ Split: Write Model (commands, domain      │
│              │ rules, normalized) + Read Model (queries, │
│              │ denormalized, optimized). Each side       │
│              │ optimized independently.                  │
├──────────────┼───────────────────────────────────────────┤
│ USE WHEN     │ Read/write asymmetric load; need          │
│              │ different views of data; Event Sourcing;  │
│              │ complex domain + simple queries           │
├──────────────┼───────────────────────────────────────────┤
│ AVOID WHEN   │ Simple CRUD; small team; low complexity;  │
│              │ eventual consistency unacceptable         │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "Bookkeeper uses the ledger; CFO uses     │
│              │  the dashboard. Same data, two models."  │
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ Event Sourcing → Projection → Eventual   │
│              │ Consistency → Vertical Slice → Axon      │
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** Your CQRS application has a read model in Elasticsearch and write model in PostgreSQL. The projection pipeline (Kafka + Debezium CDC) has a bug: it has been silently dropping events for 2 days. The Elasticsearch read model is now missing 5% of orders. How do you detect this problem? How do you rebuild the read model from scratch? Design the recovery procedure — what data do you use, what's the downtime, how do you prevent this from happening again?

**Q2.** A product manager asks: "Can users see their order immediately after placing it?" You're using eventually consistent CQRS with Kafka projections (typical lag: 300ms, worst case: 5 seconds during high load). Design the user experience strategy: when should the client read from the command response, when from the read model, and when from the write model directly? Draw the decision tree for each scenario (placing order, checking payment status, browsing order history).
