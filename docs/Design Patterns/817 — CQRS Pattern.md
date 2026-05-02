---
layout: default
title: "CQRS Pattern"
parent: "Design Patterns"
nav_order: 817
permalink: /design-patterns/cqrs-pattern/
number: "817"
category: Design Patterns
difficulty: ★★★
depends_on: "Event-Driven Pattern, Saga Pattern, Domain-Driven Design, Event Sourcing"
used_by: "Microservices, high-read/write disparity, complex domain models, Axon Framework"
tags: #advanced, #design-patterns, #architecture, #microservices, #cqrs, #event-sourcing
---

# 817 — CQRS Pattern

`#advanced` `#design-patterns` `#architecture` `#microservices` `#cqrs` `#event-sourcing`

⚡ TL;DR — **CQRS (Command Query Responsibility Segregation)** separates the write model (Commands that mutate state) from the read model (Queries that return data), allowing each to be independently optimized and scaled.

| #817            | Category: Design Patterns                                                       | Difficulty: ★★★ |
| :-------------- | :------------------------------------------------------------------------------ | :-------------- |
| **Depends on:** | Event-Driven Pattern, Saga Pattern, Domain-Driven Design, Event Sourcing        |                 |
| **Used by:**    | Microservices, high-read/write disparity, complex domain models, Axon Framework |                 |

---

### 📘 Textbook Definition

**CQRS (Command Query Responsibility Segregation)** (Greg Young, 2010; extending Bertrand Meyer's CQS — Command-Query Separation, "Object-Oriented Software Construction", 1988): an architectural pattern that separates a system's read operations (Queries) from its write operations (Commands). Commands: intents to change state — they do not return domain data, only acknowledgement or an identifier. Queries: requests to read state — they do not mutate state. Consequence: separate data models, separate classes, potentially separate databases or services for reads vs. writes. Often combined with Event Sourcing (write model = event log; read model = materialized views built from events). In Spring/Java: Axon Framework provides native CQRS + Event Sourcing infrastructure.

---

### 🟢 Simple Definition (Easy)

One interface for writing (Commands: CreateOrder, UpdateOrder, CancelOrder — mutate state, return nothing meaningful). A completely separate interface for reading (Queries: GetOrder, ListOrders — return data, never mutate state). The write side and read side can have different data models, different databases, and different scaling strategies. Read-heavy? Scale the query side independently without scaling the command side.

---

### 🔵 Simple Definition (Elaborated)

E-commerce order management: Write side (command side): receives `CreateOrder`, `UpdateOrderStatus`, `CancelOrder` commands — complex domain logic, validation, business rules, writes to a normalized relational schema. Read side (query side): `GetOrderById`, `ListOrdersByCustomer`, `GetOrderDashboard` — denormalized, pre-joined, indexed view optimized purely for the specific query. Read model updated asynchronously from command-side events. Result: write model normalized for integrity; read model denormalized for performance. 95% of traffic is reads: scale query side 10× without touching command side.

---

### 🔩 First Principles Explanation

**CQRS implementation with Axon Framework (Spring Boot):**

```
CQRS CONCEPTUAL FLOW:

  Command Side (Write):          Query Side (Read):
  ─────────────────────          ──────────────────
  Command (intent to change)  →  Event → Update read model
  CommandHandler processes it    QueryHandler returns from read model
  Domain logic, invariants       Denormalized, pre-joined
  Writes to command DB           Reads from query DB
  Returns acknowledgement        Returns DTOs

  Temporal coupling:
  Command completes → Event published → Read model updated (async)
  Client may query before read model updated → eventual consistency gap

AXON FRAMEWORK CQRS:

  // COMMAND SIDE:

  // 1. Command class (immutable data bag — no behaviour):
  @Value public class CreateOrderCommand {
      @TargetAggregateIdentifier
      String orderId;      // Axon uses this to route to the correct aggregate
      String customerId;
      List<OrderItem> items;
      BigDecimal total;
  }

  // 2. Aggregate: command handler + event applier (the domain model):
  @Aggregate
  public class OrderAggregate {
      @AggregateIdentifier
      private String orderId;
      private String customerId;
      private OrderStatus status;

      @CommandHandler
      public OrderAggregate(CreateOrderCommand cmd) {
          // Validate business rules (no direct state mutation here):
          if (cmd.getItems().isEmpty()) {
              throw new IllegalArgumentException("Order must have at least one item");
          }
          // Publish event (state mutation happens in @EventSourcingHandler):
          AggregateLifecycle.apply(
              new OrderCreatedEvent(cmd.getOrderId(), cmd.getCustomerId(),
                                   cmd.getItems(), cmd.getTotal()));
      }

      @EventSourcingHandler
      public void on(OrderCreatedEvent event) {
          // Mutate aggregate state (only place state is changed):
          this.orderId = event.getOrderId();
          this.customerId = event.getCustomerId();
          this.status = OrderStatus.PENDING;
      }

      @CommandHandler
      public void handle(CancelOrderCommand cmd) {
          if (this.status == OrderStatus.SHIPPED) {
              throw new IllegalStateException("Cannot cancel a shipped order");
          }
          AggregateLifecycle.apply(new OrderCancelledEvent(cmd.getOrderId(), cmd.getReason()));
      }

      @EventSourcingHandler
      public void on(OrderCancelledEvent event) {
          this.status = OrderStatus.CANCELLED;
      }
  }

  // QUERY SIDE:

  // 3. Event handler: updates the read model (projection):
  @Component @ProcessingGroup("order-projection")
  public class OrderProjection {
      private final OrderReadModelRepository readModelRepo;

      @EventHandler
      public void on(OrderCreatedEvent event) {
          // Create denormalized read model entry:
          OrderReadModel rm = OrderReadModel.builder()
              .orderId(event.getOrderId())
              .customerId(event.getCustomerId())
              .status("PENDING")
              .totalAmount(event.getTotal())
              .itemCount(event.getItems().size())
              .createdAt(Instant.now())
              .build();
          readModelRepo.save(rm);
      }

      @EventHandler
      public void on(OrderCancelledEvent event) {
          readModelRepo.findById(event.getOrderId())
              .ifPresent(rm -> {
                  rm.setStatus("CANCELLED");
                  rm.setCancellationReason(event.getReason());
                  readModelRepo.save(rm);
              });
      }
  }

  // 4. Query handler: serves read model data:
  @Component
  public class OrderQueryHandler {
      private final OrderReadModelRepository readModelRepo;

      @QueryHandler
      public OrderReadModel handle(FindOrderByIdQuery query) {
          return readModelRepo.findById(query.getOrderId())
              .orElseThrow(() -> new OrderNotFoundException(query.getOrderId()));
      }

      @QueryHandler
      public List<OrderReadModel> handle(FindOrdersByCustomerQuery query) {
          return readModelRepo.findByCustomerId(query.getCustomerId());
      }
  }

  // 5. REST controller dispatches commands and queries:
  @RestController @RequiredArgsConstructor
  public class OrderController {
      private final CommandGateway commandGateway;
      private final QueryGateway queryGateway;

      @PostMapping("/orders")
      public CompletableFuture<String> createOrder(@RequestBody CreateOrderRequest req) {
          String orderId = UUID.randomUUID().toString();
          return commandGateway.send(
              new CreateOrderCommand(orderId, req.getCustomerId(), req.getItems(), req.getTotal()));
      }

      @GetMapping("/orders/{id}")
      public CompletableFuture<OrderReadModel> getOrder(@PathVariable String id) {
          return queryGateway.query(new FindOrderByIdQuery(id), OrderReadModel.class);
      }
  }
```

---

### ❓ Why Does This Exist (Why Before What)

WITHOUT CQRS:

- Single unified domain model serves both reads and writes → compromises on both
- Write model: complex domain logic, normalized; forcing it to also serve complex queries = joins, projections, N+1 problems
- Read model: denormalized for queries; forcing it to also handle writes = complex validation and invariant enforcement
- Result: model optimized for neither; read performance limited by write model normalization

WITH CQRS:
→ Command side: rich domain model, strict invariants, event-sourced history. Query side: flat, denormalized, indexed read model per specific use case. Each independently scaled, independently optimized.

---

### 🧠 Mental Model / Analogy

> A library system. The Librarian who checks books in and out (write side): strict rules — must verify membership, check for holds, update the inventory accurately. Uses a detailed, normalized card catalog (write model). The Library Patron browsing the catalog (read side): wants a simple, pre-organized view: "All science fiction books by author, in stock". This read view is a printed, pre-compiled catalog — denormalized, optimized for browsing. Not updated in real-time (updated nightly from the librarian's records). Two models: one for careful, rule-enforced writes; one for fast, convenient reads.

"Librarian checking books in/out" = CommandHandler processing commands with domain rules
"Strict membership/inventory rules" = business invariants enforced on command side
"Normalized card catalog" = normalized write model (command store / event store)
"Patron browsing printed catalog" = QueryHandler returning from read model
"Pre-compiled, pre-organized view" = denormalized read model optimized per query pattern
"Updated nightly from librarian's records" = async read model projection updated by events
"Not real-time" = eventual consistency between write and read models

---

### ⚙️ How It Works (Mechanism)

```
CQRS FLOW:

  ┌─────────────────────────────────────────────────────────┐
  │  Client                                                  │
  │  POST /orders (CreateOrder) → CommandGateway → Aggregate │
  │  GET /orders/123 (GetOrder) → QueryGateway → QueryHandler│
  └─────────────────────────────────────────────────────────┘

  WRITE PATH:
  Client → CommandGateway → CommandHandler (@CommandHandler in Aggregate)
         → business logic, invariant check
         → AggregateLifecycle.apply(OrderCreatedEvent)
         → @EventSourcingHandler updates aggregate state (for future commands)
         → Event stored in Axon EventStore (PostgreSQL / MongoDB / Axon Server)
         → Event published to Event Bus

  PROJECTION PATH:
  Event Bus → @EventHandler in OrderProjection
            → updates OrderReadModel in read DB
            → (async — may be milliseconds behind command)

  READ PATH:
  Client → QueryGateway → @QueryHandler in OrderQueryHandler
         → reads OrderReadModel from read DB
         → returns DTO directly (no domain logic)

  DATABASES:
  Write DB: Axon EventStore (event log, never mutated) or relational (current state)
  Read DB: PostgreSQL optimized for queries, or Elasticsearch, or Redis

EVENTUAL CONSISTENCY GAP:

  CreateOrder command completes: OrderCreatedEvent stored.
  GET /orders/123 immediately after POST → read model may not yet be updated.

  Mitigation:
  1. Return orderId from command; client polls until order appears in read model.
  2. Optimistic UI: immediately show order as "pending" in frontend without querying.
  3. Subscription queries (Axon): server pushes update to client when projection updates.
```

---

### 🔄 How It Connects (Mini-Map)

```
Complex domain requiring both write integrity and read performance
        │
        ▼
CQRS Pattern ◄──── (you are here)
(Commands: write side; Queries: read side; separate models; eventual consistency)
        │
        ├── Event Sourcing: write model = event log; CQRS often combined with ES
        ├── Saga Pattern: sagas coordinate multi-aggregate commands; CQRS structures each aggregate
        ├── Transactional Outbox: reliable event publishing from command side to projection side
        └── Domain-Driven Design: Aggregates = natural command handlers in CQRS
```

---

### 💻 Code Example

(See First Principles — complete Axon Framework example with Aggregate, CommandHandler, EventHandler, QueryHandler, and Controller.)

---

### ⚠️ Common Misconceptions

| Misconception                                         | Reality                                                                                                                                                                                                                                                                                                                                                                                                                                                                      |
| ----------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| CQRS requires separate databases                      | CQRS only requires separate models (separate classes). You can implement CQRS with a single database by using separate tables for write and read models, or even by having separate query methods that return DTOs without domain behavior. Separate databases: an optimization, not a requirement. Start with one DB; separate when read/write scaling needs diverge.                                                                                                       |
| CQRS and Event Sourcing are the same thing            | They are complementary but independent. CQRS: separates read and write models. Event Sourcing: stores state as a sequence of events rather than current state. You can use CQRS without Event Sourcing (write to a relational table; project into a read model from DB change events or CDC). You can use Event Sourcing without CQRS (one model that replays events for both reads and writes). Axon Framework combines both — but they are separable concepts.             |
| CQRS adds unnecessary complexity for all applications | CQRS is overkill for simple CRUD applications with uniform read/write patterns. The complexity of separate models, eventual consistency, projection management, and event handling is only justified when: (1) read and write complexity differ significantly; (2) read/write scaling needs diverge; (3) multiple specialized read views are needed; (4) audit history/Event Sourcing is required. Default: use simple CRUD until the need for CQRS is clearly demonstrated. |

---

### 🔥 Pitfalls in Production

**Read model rebuild failure leaving system in inconsistent state:**

```java
// ANTI-PATTERN — projection update not idempotent:

@EventHandler
public void on(OrderCreatedEvent event) {
    // PROBLEM: duplicate event (Axon replays on failure) → duplicate read model entry
    OrderReadModel rm = new OrderReadModel(event.getOrderId(), ...);
    readModelRepo.save(rm);  // If orderId already exists: creates duplicate (if no PK constraint)
}

// ANTI-PATTERN — projection not recoverable:
// If read DB is corrupted: how do you rebuild?
// If @EventHandler was not idempotent: replay creates duplicates.

// FIX — idempotent projection update:
@EventHandler
public void on(OrderCreatedEvent event) {
    // Upsert: safe if event replayed:
    if (!readModelRepo.existsById(event.getOrderId())) {
        readModelRepo.save(new OrderReadModel(event.getOrderId(), event.getCustomerId(),
            "PENDING", event.getTotal(), event.getItems().size(), Instant.now()));
    }
    // Or use save() with a unique constraint on orderId (let DB enforce idempotency)
}

// FIX — enable read model rebuild:
// Axon: @ResetHandler marks method to run when projection is reset:
@ResetHandler
public void onReset() {
    readModelRepo.deleteAll();  // Clear read model before replay
}

// Trigger replay (rebuilds read model from event store):
// EventProcessingConfigurer: queryUpdateEmitter + replay from beginning:
// processingGroup.resetTokens();
// processingGroup.start();
// Axon replays all events from EventStore → projection rebuilt from scratch.
// Production: replay on separate instance, swap when complete (blue/green projection).
```

---

### 🔗 Related Keywords

- `Event Sourcing` — write model as immutable event log; naturally combined with CQRS
- `Saga Pattern` — sagas coordinate multi-service commands; CQRS structures each aggregate's command handling
- `Domain-Driven Design` — Aggregates map directly to CQRS command-side objects
- `Transactional Outbox` — reliable event publishing from command side to projection update
- `Axon Framework` — Java framework providing native CQRS + Event Sourcing infrastructure

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ KEY IDEA     │ Separate write model (Commands) from read │
│              │ model (Queries). Optimize each side       │
│              │ independently. Eventual consistency.      │
├──────────────┼───────────────────────────────────────────┤
│ USE WHEN     │ Read/write complexity or scale differ;    │
│              │ multiple specialized read views needed;   │
│              │ Event Sourcing required; DDD aggregates   │
├──────────────┼───────────────────────────────────────────┤
│ AVOID WHEN   │ Simple CRUD; uniform read/write patterns; │
│              │ small team; strong consistency required   │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "Library: one system for librarians       │
│              │  (strict write rules), a different        │
│              │  printed catalog for patrons (fast reads)."│
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ Event Sourcing → Axon Framework →         │
│              │ Saga Pattern → DDD Aggregates             │
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** In CQRS with Event Sourcing (Axon Framework), the write model state is reconstructed by replaying all events for an aggregate. For an aggregate with 10,000 events (an order with a long history): replaying all 10,000 events on every command is expensive. Axon supports "snapshots" — periodically capturing aggregate state as a snapshot, so replay only needs to start from the latest snapshot. What is the tradeoff between snapshot frequency and event replay cost, and how do you decide the snapshot interval in production?

**Q2.** CQRS read models are eventually consistent with the command side. A user submits a command (CreateOrder), receives 201 Created, then immediately queries `GET /orders/{id}` — and gets 404 because the projection hasn't been updated yet. This breaks the user's expectation of seeing their newly created order. What strategies (optimistic UI, return value from command, subscription queries, client-side caching, read-your-writes session token) do teams use in practice to handle this eventual consistency user experience problem?
