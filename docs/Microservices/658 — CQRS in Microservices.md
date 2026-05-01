---
layout: default
title: "CQRS in Microservices"
parent: "Microservices"
nav_order: 658
permalink: /microservices/cqrs-in-microservices/
number: "658"
category: Microservices
difficulty: ★★★
depends_on: "Event-Driven Microservices, Data Isolation per Service"
used_by: "Event Sourcing in Microservices, Eventual Consistency (Microservices)"
tags: #advanced, #microservices, #distributed, #database, #architecture, #pattern
---

# 658 — CQRS in Microservices

`#advanced` `#microservices` `#distributed` `#database` `#architecture` `#pattern`

⚡ TL;DR — **CQRS (Command Query Responsibility Segregation)** separates the write model (commands) from the read model (queries) into distinct paths, optimized independently. In microservices: commands go to the service's write store (normalized, ACID); queries are served from read projections (denormalized, eventually consistent) updated by events. Eliminates the write-read performance tension; enables cross-service reporting without violating data isolation.

| #658            | Category: Microservices                                               | Difficulty: ★★★ |
| :-------------- | :-------------------------------------------------------------------- | :-------------- |
| **Depends on:** | Event-Driven Microservices, Data Isolation per Service                |                 |
| **Used by:**    | Event Sourcing in Microservices, Eventual Consistency (Microservices) |                 |

---

### 📘 Textbook Definition

**CQRS (Command Query Responsibility Segregation)** is an architectural pattern (Greg Young, Udi Dahan, 2010) that separates operations that change state (**Commands**) from operations that read state (**Queries**) into separate models with separate data stores. Commands go through the write model — typically normalized, transactionally consistent, designed for write throughput. Queries go through the read model (projection) — denormalized, optimized for specific query patterns, may be eventually consistent. In microservices CQRS: the write side processes commands and publishes domain events. One or more read side projectors subscribe to these events and maintain query-optimized views (in Elasticsearch, Redis, Cassandra, or a relational read DB). Read queries are served directly from these projections. The key benefits: write DB optimized for writes (fewer indexes, normalized) without compromising read performance; read projections denormalized for specific query patterns (no complex JOINs at runtime); cross-service reporting via projections that aggregate events from multiple services (without violating data isolation); independent scaling of read and write paths.

---

### 🟢 Simple Definition (Easy)

CQRS: use one database for saving data, a different database for reading data. When you save an order, it goes to the "write" database (PostgreSQL, normalized). When you display a list of orders, it reads from the "read" database (Elasticsearch, pre-built for fast search). The read database is automatically kept up to date by listening to events from the write side.

---

### 🔵 Simple Definition (Elaborated)

Write-heavy optimization: `OrderService` write DB (PostgreSQL) — 3 indexes, normalized, ACID transactions. Handles 5,000 writes/sec with low overhead. Read-heavy optimization: a separate `OrderReadModel` (Elasticsearch) — denormalized, contains customer name, product name, payment status all pre-joined. Serves 50,000 reads/sec with sub-5ms response. When an order is placed: write to PostgreSQL → publish `OrderPlaced` event → projector updates Elasticsearch. Read requests: query Elasticsearch directly (no JOINs, no PostgreSQL touch). Result: PostgreSQL optimized purely for writes; Elasticsearch optimized purely for reads.

---

### 🔩 First Principles Explanation

**Why CQRS exists — the read-write tension in a single model:**

```
TRADITIONAL SINGLE MODEL:
  One DB table "orders" serves both writes and reads.

  WRITE REQUIREMENTS:
  - Normalized (no duplication)
  - Few indexes (indexes slow down writes)
  - Row-level locking for concurrent updates
  - ACID transactions

  READ REQUIREMENTS:
  - Denormalized (all data in one query, no JOINs)
  - Many indexes (fast WHERE, ORDER BY, full-text search)
  - Read replicas (horizontal scaling)
  - Aggregations (COUNT, SUM, GROUP BY)
  - Full-text search capabilities (not built into relational DBs efficiently)

  THE TENSION:
  Adding index for read performance → slows down writes
  Normalizing for write integrity → requires JOINs for reads (slow)
  Write locks → read latency spikes
  You cannot optimize one model for both simultaneously.

CQRS RESOLUTION:
  Write Model (Command Side):
    - PostgreSQL, 3 indexes, normalized, ACID
    - Handles: INSERT order, UPDATE order status, DELETE order
    - Publishes domain events on every state change

  Read Model (Query Side):
    - Elasticsearch, denormalized, pre-computed joins
    - Handles: search orders, filter by status, sort by date, full-text search
    - Updated by projector consuming events from write side
    - May have multiple projections for different query patterns

  Result: both sides optimized independently; no compromises
```

**Projection building — one event stream, multiple projections:**

```
EVENTS from OrderService (single Kafka topic):
  OrderPlaced        → {"orderId", "customerId", "productId", "amount", "placedAt"}
  OrderShipped       → {"orderId", "trackingNumber", "shippedAt"}
  OrderDelivered     → {"orderId", "deliveredAt"}
  OrderCancelled     → {"orderId", "reason", "cancelledAt"}
  PaymentProcessed   → {"orderId", "paymentId", "method", "processedAt"}

PROJECTION 1 — "OrderListView" (Elasticsearch):
  Stores: orderId, customerName*, productName*, status, amount, placedAt, shippedAt
  (* fetched from CustomerService and InventoryService events, denormalized in)
  Used for: customer order history page ("My Orders")
  Updated by: OrderPlaced, OrderShipped, OrderDelivered, OrderCancelled

PROJECTION 2 — "OrderAnalytics" (ClickHouse columnar DB):
  Stores: orderId, productId, categoryId, amount, date, region
  Used for: business analytics ("Revenue by category by month")
  Updated by: OrderPlaced only (immutable analytics event)

PROJECTION 3 — "FulfillmentQueue" (Redis sorted set):
  Stores: orderId sorted by placedAt (priority queue for warehouse)
  Used for: warehouse picking queue — "which orders to pack next?"
  Updated by: OrderPlaced (add to queue), OrderShipped (remove from queue)

SAME EVENTS → 3 completely different views, each optimized for its use case.
Each projector is an independent consumer group; one slow projector doesn't affect others.
```

**Handling projection rebuilding (critical operational concern):**

```
SCENARIO: Bug in the OrderListView projector miscalculates order totals.
  7 days of incorrect data in Elasticsearch.

SOLUTION: Replay and rebuild the projection from scratch.

STEPS:
  1. Stop projector consumer group "order-list-projector"
  2. Truncate Elasticsearch index (or create new index version: "orders-v2")
  3. Reset Kafka consumer group offset to EARLIEST:
     kafka-consumer-groups.sh --reset-offsets --to-earliest
       --group order-list-projector --topic order-events --execute
  4. Restart projector → replays all events from beginning
  5. When projector catches up to current time: switch read traffic to rebuilt projection

REQUIREMENTS for replay to work:
  - Kafka must retain events long enough for rebuild (set retention.ms high enough)
  - Projector must be idempotent (replaying already-seen event = same result)
  - Projector must handle events in order (use orderId as partition key → ordered per order)

KAFKA RETENTION FOR CQRS:
  Set retention.ms = -1 (infinite retention) for event log topics
  OR use log compaction: keeps latest event per key (memory-efficient, lossy history)
  For full rebuild capability: infinite retention or external event store
```

---

### ❓ Why Does This Exist (Why Before What)

Traditional systems have a single database serving both writes and complex queries. As data volume grows, adding indexes for read performance degrades write throughput. Complex reporting JOINs lock rows and slow down concurrent writes. CQRS resolves this by saying: writes and reads are fundamentally different operations with opposing requirements — separate them. Stop trying to optimize one database for both.

---

### 🧠 Mental Model / Analogy

> CQRS is like a restaurant with a kitchen and a menu display board. The kitchen (write model) handles new orders: normalized operations, one recipe file per dish, updated when the chef changes a recipe. The display board (read model) shows customers what's available with prices, photos, allergens, and reviews — pre-assembled for display, no live kitchen access. When the kitchen adds a new dish, it "publishes" the update; the display board is updated. A customer reading the menu doesn't slow down the kitchen. The kitchen processing orders doesn't slow down menu display. The trade-off: the board may be 30 seconds behind the kitchen (eventual consistency).

---

### ⚙️ How It Works (Mechanism)

**Spring Boot CQRS implementation — write side + read side:**

```java
// ══════════════════════════════════════
// WRITE SIDE (Command side — PostgreSQL)
// ══════════════════════════════════════

// Command: create order (write model)
@Service
class OrderCommandService {
    @Autowired OrderRepository orderRepository;      // PostgreSQL JPA
    @Autowired KafkaTemplate<String, OrderEvent> kafkaTemplate;

    @Transactional
    public String placeOrder(PlaceOrderCommand command) {
        Order order = new Order(
            UUID.randomUUID().toString(),
            command.getCustomerId(),
            command.getProductId(),
            command.getQuantity(),
            command.getTotalAmount(),
            OrderStatus.PLACED
        );
        orderRepository.save(order);  // write to PostgreSQL

        kafkaTemplate.send("order-events", order.getId(),
            new OrderPlacedEvent(order.getId(), order.getCustomerId(),
                order.getProductId(), order.getTotalAmount(), Instant.now()));
        return order.getId();
    }
}

// ══════════════════════════════════════
// READ SIDE (Projector + Query — Elasticsearch)
// ══════════════════════════════════════

// Projector: updates Elasticsearch from events
@Service
class OrderProjector {
    @Autowired ElasticsearchOperations elasticsearchOps;
    @Autowired CustomerClient customerClient;  // to fetch customer name

    @KafkaListener(topics = "order-events", groupId = "order-list-projector")
    void project(ConsumerRecord<String, OrderEvent> record) {
        if (record.value() instanceof OrderPlacedEvent e) {
            String customerName = customerClient.getName(e.customerId());
            elasticsearchOps.save(new OrderDocument(
                e.orderId(), customerName, e.totalAmount(), "PLACED", e.placedAt()
            ));
        } else if (record.value() instanceof OrderShippedEvent e) {
            OrderDocument doc = elasticsearchOps.get(e.orderId(), OrderDocument.class);
            doc.setStatus("SHIPPED");
            doc.setShippedAt(e.shippedAt());
            elasticsearchOps.save(doc);
        }
    }
}

// Query: reads from Elasticsearch (fast, denormalized)
@Service
class OrderQueryService {
    @Autowired ElasticsearchOperations elasticsearchOps;

    public Page<OrderDocument> searchOrders(String customerId, String status, Pageable pageable) {
        Criteria criteria = new Criteria("customerId").is(customerId);
        if (status != null) criteria = criteria.and("status").is(status);
        Query query = new CriteriaQuery(criteria).setPageable(pageable);
        return elasticsearchOps.search(query, OrderDocument.class).toPage();
    }
}
```

---

### 🔄 How It Connects (Mini-Map)

```
Data Isolation per Service
(each service owns its data)
        │
        ▼
CQRS in Microservices  ◄──── (you are here)
(separate write + read models)
        │
        ├── Event-Driven Microservices → events are the sync mechanism for projections
        ├── Event Sourcing → events are the write model itself (not just sync mechanism)
        ├── Eventual Consistency → read projections lag behind write model
        └── Data Isolation → CQRS read model allows cross-service data without DB sharing
```

---

### 💻 Code Example

**Cross-service reporting projection — aggregating events from multiple services:**

```java
// ReportingService: owns its own DB (ClickHouse), populated by events from 3 services.
// No data isolation violation: reads from its OWN projection DB.

@KafkaListener(topics = {"order-events", "payment-events", "inventory-events"},
               groupId = "reporting-projector")
@Transactional
void projectForReporting(ConsumerRecord<String, Object> record) {
    switch (record.topic()) {
        case "order-events" -> {
            if (record.value() instanceof OrderPlacedEvent e) {
                reportingRepository.mergeOrder(
                    new OrderFact(e.orderId(), e.customerId(), e.productId(),
                                  e.totalAmount(), e.placedAt(), null, null)
                );
            }
        }
        case "payment-events" -> {
            if (record.value() instanceof PaymentProcessedEvent e) {
                reportingRepository.updatePaymentStatus(e.orderId(), e.method(), e.processedAt());
            }
        }
        case "inventory-events" -> {
            if (record.value() instanceof InventoryReservedEvent e) {
                reportingRepository.updateInventoryStatus(e.orderId(), e.reservedAt());
            }
        }
    }
}

// Now: "Orders with customer, product, payment, inventory status" query
// → ReportingService queries its own projection DB (ClickHouse)
// → No service boundary violations
// → Query response: <10ms (pre-joined columnar store)
```

---

### ⚠️ Common Misconceptions

| Misconception                                                  | Reality                                                                                                                                                                                                                                                                               |
| -------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| CQRS requires a separate microservice for reads and writes     | CQRS can be applied within a single service (separate code paths + separate DB tables) or across services. The separation is logical (different code and data models) — not necessarily an entire separate deployment                                                                 |
| CQRS always requires event sourcing                            | CQRS and Event Sourcing are complementary but independent. CQRS: separate read/write models. Event Sourcing: events as the write model. You can use CQRS with a traditional relational write model (non-event-sourced), publishing events from write operations to update projections |
| CQRS makes the system more complex without significant benefit | CQRS shines when: (a) read volume >> write volume and different optimization needed, (b) cross-service reporting required, (c) multiple different query patterns on same data. For a simple CRUD service with uniform load: standard single model is simpler and preferable           |
| The read model is just a read replica of the write DB          | A read replica is an identical copy of the write DB. A CQRS read model is a completely different schema, potentially in a different database technology (Elasticsearch, Redis), pre-computed and denormalized for specific query patterns                                             |

---

### 🔥 Pitfalls in Production

**Projection rebuild takes longer than Kafka retention:**

```
SCENARIO:
  Kafka retention: 7 days (default)
  OrderListView projection bug discovered after 3 months.
  Events older than 7 days: deleted from Kafka.
  Cannot rebuild projection from full history.
  Elasticsearch projection has 3 months of corrupted data.

RESOLUTION (urgent):
  Short-term: rebuild from last 7 days events only.
  Seed projection with "current state" snapshot from write DB:
    SELECT order_id, status, customer_id, amount FROM orders;  ← write DB
    Bulk-import into Elasticsearch as best-effort current state.
    Then apply 7 days of events on top.
  Gaps: orders 7-90 days old may have incorrect status in projection.
  Communicate known data quality issue to business stakeholders.

PREVENTION:
  Option 1: Increase Kafka retention for critical event topics:
    retention.ms = -1 (infinite) on "order-events"
    Cost: disk storage (calculate: events/day × avg_event_size × days_to_retain)

  Option 2: Event store (separate from Kafka):
    EventStoreDB or custom "events" table in PostgreSQL
    Kafka for delivery; event store for durability + replay
    Kafka retention can be short (24h); replay from event store

  Option 3: Regular projection snapshots:
    Snapshot projection state to durable storage daily
    Rebuild: restore snapshot + apply events since snapshot
    Reduces retention window needed for full rebuild
```

---

### 🔗 Related Keywords

- `Event-Driven Microservices` — events are the mechanism that keeps read projections updated
- `Event Sourcing in Microservices` — CQRS where the write model is an event log
- `Data Isolation per Service` — CQRS enables cross-service reads without DB sharing
- `Eventual Consistency (Microservices)` — read projections lag behind write model by design

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ COMMAND SIDE │ Normalized write DB (PostgreSQL, ACID)    │
│ QUERY SIDE   │ Denormalized projection (ES, Redis, CH)   │
│ SYNC MECH    │ Domain events → projector consumer        │
├──────────────┼───────────────────────────────────────────┤
│ BENEFITS     │ Independent read/write optimization       │
│              │ Cross-service reporting without DB sharing │
│              │ Multiple read models from same events      │
├──────────────┼───────────────────────────────────────────┤
│ TRADE-OFFS   │ Eventual consistency on read side          │
│              │ Projection rebuild complexity              │
│              │ Operational complexity (2 data stores)     │
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** A projector in your CQRS system processes `OrderShippedEvent` and updates the Elasticsearch `OrderDocument`. Due to a network glitch, the same event is delivered twice (Kafka at-least-once delivery). The projector processes it twice: first update sets status="SHIPPED", shippedAt=T1. Second delivery: same event, same data. Describe how you implement an idempotent projector that handles duplicate events safely. What metadata do you need to store in the projection to detect duplicates? How does this interact with the `@Version` field from optimistic locking?

**Q2.** Your CQRS read projection (Elasticsearch) is 45 minutes behind the write model due to a consumer lag incident. A customer service representative uses a React dashboard backed by the Elasticsearch projection to verify a customer's order status. The customer is calling in saying "my order shows PLACED but I received the shipping confirmation email 30 minutes ago." The rep sees PLACED in the dashboard. How do you: (a) indicate data freshness to the rep in the UI (lag timestamp?), (b) allow the rep to force a "fresh" lookup from the write model for this specific order, (c) prevent this scenario from recurring?
