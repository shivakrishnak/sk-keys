---
layout: default
title: "CQRS"
parent: "Distributed Systems"
nav_order: 615
permalink: /distributed-systems/cqrs/
number: "615"
category: Distributed Systems
difficulty: ★★★
depends_on: "Event Sourcing, Domain-Driven Design"
used_by: "Axon Framework, EventStoreDB, Kafka, Apache Kafka Streams"
tags: #advanced, #distributed, #architecture, #patterns, #scalability
---

# 615 — CQRS

`#advanced` `#distributed` `#architecture` `#patterns` `#scalability`

⚡ TL;DR — **CQRS** (Command Query Responsibility Segregation) separates read and write operations into distinct models: write side handles commands (mutate state), read side handles queries (return data) — enabling each to be scaled, optimized, and evolved independently.

| #615            | Category: Distributed Systems                             | Difficulty: ★★★ |
| :-------------- | :-------------------------------------------------------- | :-------------- |
| **Depends on:** | Event Sourcing, Domain-Driven Design                      |                 |
| **Used by:**    | Axon Framework, EventStoreDB, Kafka, Apache Kafka Streams |                 |

---

### 📘 Textbook Definition

**CQRS** (Command Query Responsibility Segregation — Greg Young, Udi Dahan, ~2010, derived from Bertrand Meyer's CQS principle) separates the application model into two distinct sides: **Command** side — handles write operations (create, update, delete); mutates state; returns void or a result confirming success. **Query** side — handles read operations; returns data; never mutates state. In simple CQRS: same database, separate models (command model uses domain aggregates; query model uses read-optimized DTOs). In full CQRS + Event Sourcing: separate write and read stores. Write store: event log (append-only). Read store: projections/materialized views optimized for specific query patterns (denormalized, pre-joined). Synchronization: commands → events → projections updated via event handlers (async). This introduces **eventual consistency** between write and read sides. Benefits: independent scaling (reads can be replicated; writes remain on primary), query-optimized read models (no N+1, no complex joins), simplified write models (domain logic without query optimization constraints). Complexity cost: higher architectural complexity, eventual consistency, projection maintenance.

---

### 🟢 Simple Definition (Easy)

Restaurant: the waiter taking your order (command) is different from the person reading the menu board (query). Write side: kitchen takes orders, modifies inventory. Read side: menu board shows what's available. They're separate. The board updates when stock changes (eventual consistency: small delay). Benefit: the kitchen (write side) can be optimized for transaction processing; the menu board (read side) can be a fast-lookup cache, replicated to 10 screens around the restaurant.

---

### 🔵 Simple Definition (Elaborated)

Traditional CRUD: one model does everything — handles complex write transactions AND serves complex read queries. As scale grows: the write model (normalized for data integrity) performs poorly for reads (N+1 queries, complex joins). Adding indexes to speed up reads slows down writes. CQRS: the write model cares only about correctness and domain rules. The read model is denormalized, pre-computed, and optimized for specific queries. Each independently scalable: 1 write replica + 10 read replicas.

---

### 🔩 First Principles Explanation

**Command handling, event projection, and read model synchronization:**

```
SIMPLE CQRS (same database, separate objects):

  Write side: Command + CommandHandler + Aggregate (domain model)
  Read side: QueryHandler + ReadModel (DTO, simplified view)

  // Command: intent to change state.
  public record PlaceOrderCommand(String userId, List<OrderItem> items, String paymentMethod) {}

  // CommandHandler: validates and executes.
  @CommandHandler
  public class OrderCommandHandler {
      public OrderId handle(PlaceOrderCommand cmd) {
          // Domain validation (business rules).
          User user = userRepo.findById(cmd.userId());
          if (!user.isEligibleToBuy()) throw new UserNotEligibleException();

          Order order = Order.create(cmd.userId(), cmd.items(), cmd.paymentMethod());
          orderRepo.save(order);
          return order.getId();
          // Returns only the ID, not the full order (commands return void or minimal data).
      }
  }

  // Query: request for data (no mutation).
  public record GetOrderSummaryQuery(String orderId) {}

  // QueryHandler: returns read-optimized DTO.
  @QueryHandler
  public class OrderQueryHandler {
      // Read model: denormalized, pre-joined, query-optimized.
      public OrderSummaryDTO handle(GetOrderSummaryQuery query) {
          return orderSummaryRepo.findById(query.orderId()); // Pre-computed view.
          // No domain model, no business rules — just data retrieval.
      }
  }

FULL CQRS + EVENT SOURCING:

  Write side:  Command → Aggregate → Domain Events → Event Store (append-only)
  Read side:   Event Store → Event Handler (projection) → Read Store (materialized view)

  WRITE FLOW:

    1. PlaceOrderCommand received.
    2. OrderAggregate loaded from event store (replays all past OrderCreated, OrderUpdated events).
    3. OrderAggregate.placeOrder(): validates business rules.
    4. Generates: OrderPlacedEvent {orderId, userId, items, timestamp}.
    5. Event stored to event store (append-only):
       event_store: [OrderPlacedEvent, ItemAddedEvent, PaymentConfirmedEvent, ...]

  READ FLOW (projection):

    6. Event handler receives OrderPlacedEvent.
    7. Updates read store:
       OrderSummaryView {
           orderId: "abc-123",
           customerName: "Alice",     // Denormalized (joined with user table)
           itemCount: 3,
           totalAmount: 75.00,
           status: "PLACED",
           placedAt: "2024-01-15T10:00:00Z"
       }
       Also updates:
       OrdersByUserView {userId: "u-456", orders: [...]}
       PendingOrdersView {orders: [...]}

    8. Query: GetOrderSummary(orderId) → reads from OrderSummaryView.
       No joins. No N+1. Pre-computed, instant.

  EVENTUAL CONSISTENCY:
    Gap between step 5 and step 7: may be milliseconds (sync) or seconds (async).
    User: places order → immediately queries order status.
    If projection not yet updated: query returns stale data (e.g., status still "UNKNOWN").

    UI HANDLING:
    Option 1: Show optimistic UI state immediately (before query confirms).
    Option 2: Query with version-based polling:
      "return order when version >= 5" (wait until event #5 is projected).
    Option 3: Accept eventual consistency: "Order placed! It will appear in your list shortly."

READ MODEL PROJECTIONS — MULTIPLE VIEWS PER AGGREGATE:

  Event: OrderPlacedEvent → updates MANY read models simultaneously.

  OrderSummaryView     → for order detail page
  CustomerOrdersView   → for "my orders" list
  PendingOrdersReport  → for operations dashboard
  RevenueMetricsView   → for business analytics
  InventoryDepletionView → for warehouse system

  Each view: optimized for its specific query.
  No JOIN queries at read time: all denormalized at write time (projection).

  PROJECTION REBUILD:
    New analytics view needed: "orders by geographic region."
    No new events needed.
    Replay ALL historical OrderPlacedEvents → build new view.
    Event sourcing: enables retroactive projections.
    This is impossible with traditional CRUD (historical data overwritten).

AXON FRAMEWORK (JAVA CQRS + EVENT SOURCING):

  @Aggregate
  public class OrderAggregate {

      @AggregateIdentifier
      private String orderId;
      private OrderStatus status;

      @CommandHandler
      public OrderAggregate(PlaceOrderCommand cmd) {
          // Domain validation.
          if (cmd.items().isEmpty()) throw new EmptyOrderException();

          // Emit event (do NOT change state here — only emit event).
          AggregateLifecycle.apply(new OrderPlacedEvent(
              cmd.orderId(), cmd.userId(), cmd.items()));
      }

      @EventSourcingHandler
      public void on(OrderPlacedEvent event) {
          // Update aggregate state from event.
          this.orderId = event.orderId();
          this.status = OrderStatus.PLACED;
          // Called when event is applied AND when aggregate is replayed from event store.
      }

      @CommandHandler
      public void handle(CancelOrderCommand cmd) {
          if (this.status == OrderStatus.SHIPPED) {
              throw new CannotCancelShippedOrderException();
          }
          AggregateLifecycle.apply(new OrderCancelledEvent(this.orderId));
      }
  }

  // Read side projection:
  @Component
  public class OrderSummaryProjection {

      @EventHandler
      @Transactional
      public void on(OrderPlacedEvent event) {
          // Update denormalized read model.
          orderSummaryRepo.save(new OrderSummaryDocument(
              event.orderId(),
              event.userId(),
              event.items().size(),
              OrderStatus.PLACED,
              event.timestamp()
          ));
      }

      @QueryHandler
      public OrderSummaryDTO handle(GetOrderSummaryQuery query) {
          return orderSummaryRepo.findById(query.orderId())
              .map(doc -> new OrderSummaryDTO(doc))
              .orElseThrow(OrderNotFoundException::new);
      }
  }

CQRS WITHOUT EVENT SOURCING:

  Common misconception: CQRS requires event sourcing.
  Reality: CQRS is independently useful even with a traditional database.

  Pattern: Command side → writes to normalized relational DB.
           Query side → reads from separate denormalized read DB (replicated slave, or dedicated views).

  Synchronization: DB replication (async), or application-level sync via domain events.
  Benefit: write model keeps normalization; read model uses denormalized projections.
  Complexity: much lower than full event sourcing.

  USEFUL WHEN:
    Read/write ratio is very high (e.g., 99:1 reads to writes).
    Query patterns are complex and diverse (different views need different shapes).
    Write logic is complex domain (aggregates, invariants) but reads are simple lookups.
```

---

### ❓ Why Does This Exist (Why Before What)

WITHOUT CQRS:

- Same model for reads and writes: indexes optimized for reads slow down writes
- Complex query requirements contaminate domain model with query-specific fields
- Can't scale reads independently of writes

WITH CQRS:
→ Write model: optimized for correctness and domain rules (no query-specific code)
→ Read model: denormalized, indexed for fast queries, independently scalable
→ With event sourcing: full audit trail, retroactive projections, time-travel queries

---

### 🧠 Mental Model / Analogy

> Library: the librarian (write side) manages the catalog — adding, removing books, recording checkouts. The reading room index cards (read side) are pre-sorted by title, author, subject for quick lookup. They're updated by the librarian after each transaction (eventual consistency). The librarian's catalog (normalized, transactional) and the reading room index (denormalized, fast-lookup) serve different needs — kept separate.

"Librarian managing the catalog" = command side with domain model
"Reading room index cards" = read side with denormalized projections
"Librarian updates index after each transaction" = event handlers updating read models
"Small delay between catalog update and index update" = eventual consistency gap

---

### ⚙️ How It Works (Mechanism)

```
CQRS + EVENT SOURCING FLOW:

  Client → Command Bus → Command Handler → Aggregate → Event Store
                                                           │
                                               Event Bus → Event Handlers
                                                           │
                                               Read Store (projections)
                                                           │
  Client → Query Bus → Query Handler ← Read Store (fast queries)
```

---

### 🔄 How It Connects (Mini-Map)

```
CQS (Bertrand Meyer: methods either query or mutate, not both)
        │
        ▼ (CQS applied at architectural level)
CQRS ◄──── (you are here)
(separate command/query models and handlers)
        │
        ├── Event Sourcing: write side stores events (perfect CQRS complement)
        ├── Domain-Driven Design: aggregates = CQRS write side model
        └── Eventual Consistency: read side is eventually consistent with write side
```

---

### 💻 Code Example

```java
// Minimal CQRS without event sourcing (Spring Boot):

// COMMAND SIDE
public record CreateProductCommand(String name, BigDecimal price, int stock) {}

@Service
public class ProductCommandService {

    @Transactional
    public String createProduct(CreateProductCommand cmd) {
        // Domain model: rich, validates business rules.
        Product product = Product.create(cmd.name(), cmd.price(), cmd.stock());
        productRepo.save(product);

        // Publish domain event for projection update.
        eventPublisher.publishEvent(new ProductCreatedEvent(
            product.getId(), product.getName(), product.getPrice()));

        return product.getId();
    }
}

// READ SIDE — separate model, optimized for query
@Document  // MongoDB document for flexible schema
public class ProductCatalogView {
    String id;
    String name;
    String priceFormatted;  // "$29.99" — pre-formatted for display
    boolean inStock;        // Pre-computed from stock > 0
    String categoryPath;    // Denormalized: "Electronics > Phones > Accessories"
}

@Service
public class ProductQueryService {

    public ProductCatalogView getProduct(String id) {
        return productCatalogViewRepo.findById(id)
            .orElseThrow(() -> new ProductNotFoundException(id));
        // No joins, no domain logic — just data retrieval.
    }

    public Page<ProductCatalogView> searchProducts(String keyword, Pageable pageable) {
        return productCatalogViewRepo.findByNameContaining(keyword, pageable);
        // Full-text search on pre-indexed read model.
    }
}

// Projection updater: keeps read model in sync.
@EventListener
public class ProductProjectionUpdater {
    @TransactionalEventListener
    public void on(ProductCreatedEvent event) {
        productCatalogViewRepo.save(new ProductCatalogView(
            event.id(), event.name(),
            "$" + event.price().setScale(2), // Pre-format
            true // New product: in stock
        ));
    }
}
```

---

### ⚠️ Common Misconceptions

| Misconception                        | Reality                                                                                                                                                                                                                                                                                                                                                                                                                |
| ------------------------------------ | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| CQRS requires event sourcing         | CQRS (separate command/query models) is independent of event sourcing (storing events as the source of truth). They complement each other well, but CQRS works with a traditional database. And event sourcing works without CQRS (single model consuming events). The combination is powerful but adds complexity; start with CQRS alone if event sourcing isn't needed                                               |
| CQRS means two separate databases    | In simple CQRS: same database, different model objects (Command uses domain aggregates; Query uses DTOs). In full CQRS: separate stores (event store for write, read-optimized store for queries). The key distinction is model separation, not database separation. Many successful CQRS implementations use one database with separate tables/views for read models                                                  |
| CQRS solves all performance problems | CQRS improves read scalability and query optimization but adds eventual consistency complexity. The read model lag can cause issues: user updates, then immediately queries — gets stale data. Also: projections can become stale or corrupt (bugs in projection logic). More moving parts = more failure modes. CQRS is not a general performance improvement; it's a specific pattern for specific scaling scenarios |
| Commands should return void          | While the strict CQS principle says commands return nothing, in practice commands commonly return the ID of the created/modified resource. This simplifies client code (client needs the ID to navigate to the new resource). Returning the full resource state is the anti-pattern (that's a query). Returning minimal identifiers (ID, version) is widely accepted in CQRS implementations                           |

---

### 🔥 Pitfalls in Production

**Stale read model after command — user sees old data:**

```
SCENARIO: User places order → redirected to order confirmation page.
  Page loads: queries order status → returns "ORDER_NOT_FOUND" (projection not yet updated).
  User: "I was just charged but my order doesn't exist?!"

BAD: Redirect immediately after command, then query:
  POST /orders → 201 Created {orderId: "abc-123"}
  → Frontend: immediately GET /orders/abc-123 → 404 Not Found
  → Projection lag: 500ms behind

FIX 1: Optimistic UI (most common, best UX):
  Frontend: after POST /orders → immediately show order confirmation using data from the POST request.
  Don't query until user navigates away and returns.
  Projection: updated by the time user navigates back.

FIX 2: Wait for projection (if API must return data):
  CommandHandler: after saving event → wait for projection update (max 2 seconds).
  POST /orders → waits until OrderSummaryView is updated → returns full order data.
  Downside: couples command side to read side latency.

FIX 3: Version-based read:
  Command returns: {orderId: "abc-123", version: 5}
  Client: GET /orders/abc-123?minVersion=5
  Query handler: waits until projection is at version >= 5 (long-poll or retry).

FIX 4: Return command result directly (no projection):
  After PlaceOrderCommand: return the result object constructed directly from command data.
  Not from the projection. User sees the data they just submitted.
  Simplest fix. Trade-off: not from the read model (no enrichment, no denormalization).

PROJECTION BUG — corrupted read model:
  Event handler bug: incorrectly updates projection.
  Symptoms: read model shows wrong data (prices wrong, orders missing).

  Recovery with event sourcing:
    1. Fix the projection bug.
    2. Drop the corrupted read model (truncate the read store).
    3. Replay all events from the event store → rebuild projection from scratch.
    4. No data loss: source of truth is the event store (immutable).
    5. Downtime: only during projection rebuild (can build in parallel with shadow read store).

  Without event sourcing (traditional DB write side):
    Data already overwritten. Projection bug = potentially unrecoverable corruption.
    Lesson: event sourcing's immutable event log makes projection bugs recoverable.
```

---

### 🔗 Related Keywords

- `Event Sourcing` — stores events as the write side source of truth; natural partner to CQRS
- `Domain-Driven Design` — aggregates and bounded contexts align with CQRS command side
- `Eventual Consistency` — read side is eventually consistent with write side
- `Axon Framework` — Java framework purpose-built for CQRS + Event Sourcing
- `Materialized View` — the database-level analogue of a CQRS read model projection

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ KEY IDEA     │ Write side: commands → domain aggregates │
│              │ Read side: queries → denormalized views.  │
│              │ Each independently optimized and scalable.│
├──────────────┼───────────────────────────────────────────┤
│ USE WHEN     │ High read/write ratio; complex domain     │
│              │ logic + diverse query needs; need full   │
│              │ audit trail (+ event sourcing)            │
├──────────────┼───────────────────────────────────────────┤
│ AVOID WHEN   │ Simple CRUD; small teams; eventual        │
│              │ consistency is unacceptable; domain logic │
│              │ is straightforward (over-engineering risk)│
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "Library catalog vs. reading room index: │
│              │  one for writes, one for reads — optimal."│
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ Event Sourcing → Axon Framework → Saga   │
│              │ Pattern → Domain-Driven Design → Eventual │
│              │ Consistency                               │
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** You implement CQRS. The write side uses PostgreSQL (normalized, ACID). The read side uses Elasticsearch (denormalized, full-text search). The projection updater is asynchronous (Kafka event → Elasticsearch update). Average projection lag: 500ms. A compliance requirement states: "Any user must be able to see their order within 1 second of placing it." Is this achievable? Design the specific solution that satisfies the compliance requirement while keeping the async projection architecture.

**Q2.** You have CQRS without event sourcing. A bug in the projection updater ran for 3 days, incorrectly computing order totals (off by 10%). The write side (PostgreSQL) has the correct raw order data. The read side (MongoDB projections) has corrupted totals. How do you recover? Write a migration strategy — without event sourcing, you need to rebuild projections from the write side data. What are the steps, and what is the downtime impact?
