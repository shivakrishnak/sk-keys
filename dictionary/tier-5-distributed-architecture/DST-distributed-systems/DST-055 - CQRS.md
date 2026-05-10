---
id: DST-055
title: "CQRS"
category: Distributed Systems
tier: tier-5-distributed-architecture
folder: DST-distributed-systems
difficulty: ★★★
depends_on: DST-049, DST-056
related: DST-056, DST-049, DST-033
tags:
  - distributed
  - architecture
  - pattern
  - deep-dive
  - advanced
status: complete
version: 2
layout: default
parent: "Distributed Systems"
grand_parent: "Technical Dictionary"
nav_order: 55
permalink: /distributed-systems/cqrs/
---

# DST-055 - CQRS

⚡ TL;DR - CQRS (Command Query Responsibility Segregation) separates the write model (commands that mutate state) from the read model (queries that return data), allowing each to be independently optimized, scaled, and evolved — at the cost of eventual consistency between them.

| Metadata        |                           |     |
| :-------------- | :------------------------ | :-- |
| **Depends on:** | DST-049, DST-056          |     |
| **Related:**    | DST-056, DST-049, DST-033 |     |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
A traditional e-commerce system uses one database for both writes (create order, update inventory, process payment) and reads (product catalog search, order history, dashboard analytics). This unified model (CRUD) works at low scale. As the system grows: the read queries become complex (join 8 tables, aggregate across 3 years of data, filter by 15 criteria). Indexes added for reads hurt write performance. Indexes needed for writes conflict with read query plans. Database scale: you can read-scale with replicas, but the write primary is a bottleneck. The domain model (optimized for transactional correctness) is not optimal for reporting (optimized for query speed). One model trying to serve two conflicting optimization targets.

**THE BREAKING POINT:**
Bertrand Meyer's Command Query Separation (CQS) principle (1988): "every method should either be a command that performs an action, or a query that returns data to the caller, but not both." Greg Young extended this to the architectural level in 2010: if commands and queries have different characteristics (read/write ratio, data structure, scale requirements) — they should be implemented as entirely separate models, each optimized for its purpose. The result: CQRS — not a framework, but an architectural pattern.

**THE INVENTION MOMENT:**
Greg Young's 2010 article and conference talks formally described CQRS as an architectural pattern, separate from Event Sourcing (DST-056) — though the two are frequently combined. The key insight: the data model that is optimal for writes (normalized, transactionally consistent, domain-rich) is NEVER optimal for reads (denormalized, pre-joined, query-friendly). Trying to optimize one model for both is a constraint that limits both. Removing the constraint enables independent optimization.

**EVOLUTION:**
1988: Meyer's Command Query Separation (method level). 2003: Domain-Driven Design (Evans) — domain model for commands. 2010: Greg Young — CQRS pattern formalized. 2010+: Event Sourcing + CQRS combination popularized. 2012: Axon Framework (Java) — CQRS + Event Sourcing framework. 2014+: CQRS in microservices — each service has separate command/query models. 2015+: CQRS with eventual consistency explicitly acknowledged — not a bug, a feature. Today: CQRS is a well-understood pattern; the consensus is that it adds significant complexity and is only justified when read/write loads or models are significantly asymmetric.

---

### 📘 Textbook Definition

**CQRS (Command Query Responsibility Segregation)** is an architectural pattern that separates the handling of commands (operations that change system state) from queries (operations that return data) into distinct models: (1) **Command model (write side):** receives commands (`PlaceOrderCommand`, `CancelOrderCommand`), validates business rules, mutates state (updates domain objects, publishes events). Optimized for transactional correctness and domain rule enforcement. (2) **Query model (read side):** handles queries (`GetOrderHistoryQuery`, `SearchProductsQuery`), returns read-optimized data. Maintained by projections that consume events published by the command side. Optimized for query performance (denormalized, pre-joined, indexed for specific query patterns). **Synchronization:** the command model publishes domain events (e.g., `OrderPlaced`). The query model consumes these events and updates its read store (may be a separate database, cache, or Elasticsearch index). The synchronization is asynchronous → eventual consistency: the read model may be milliseconds to seconds behind the command model. **Relationship to Event Sourcing (DST-056):** CQRS and Event Sourcing are independent patterns. CQRS can use traditional databases for both sides. Event Sourcing stores the command model as a sequence of events rather than current state. They are often combined because they complement each other naturally.

---

### ⏱️ Understand It in 30 Seconds

**One line:** Separate the model that changes data from the model that reads it — each optimized independently.

> CQRS is like separating the kitchen (command model) from the dining room menu (query model) in a restaurant. The kitchen (write side) maintains the actual inventory, recipes, and preparation state — optimized for cooking. The menu (read side) is a denormalized, customer-friendly view of what's available — optimized for reading. When the kitchen updates inventory (command): the menu is updated eventually (query model). The menu is NOT the kitchen's internal state — it's a prepared view of it.

**One insight:** CQRS does not mean two databases are required. It means two models. At the simplest level: one service handles commands (validates, mutates), another handles queries (returns pre-computed views). The "database" could be the same — but the models are separate concerns.

---

### 🔩 First Principles Explanation

**CORE INVARIANTS:**

1. **Commands never return data (except acknowledgment).** A command `PlaceOrderCommand` returns either `CommandAccepted` (202 Accepted) or error. It does NOT return the created order object. The caller must query the read model for the result. This eliminates the need for the write model to serve read concerns.
2. **Queries never mutate state.** A query handler reads from the query store and returns data. It does not modify any state. This eliminates read-write contention on the write model.
3. **Read model is derived from write model events.** The query model has no independent authoritative state. It is a projection of the command model's history. If the query store is destroyed: it can be rebuilt by replaying events from the command side. This makes the read model a "cache" of a specific query pattern.
4. **Eventual consistency is explicit and bounded.** After a command is accepted, the read model reflects the change "eventually" (after event propagation). This delay (usually milliseconds to seconds) must be acceptable for the use case. Not acceptable: banking balance display (strong consistency needed). Acceptable: order history page (slight delay acceptable).

**DERIVED DESIGN:**

```
Command Side:                    Query Side:
  Client─POST /orders──────────▶   Client─GET /orders──────▶
  │                               │
  CommandHandler:                 QueryHandler:
    validate domain rules           reads from
    update write store              denormalized
    publish OrderPlaced event       read store
                   │                      ▲
                   └─event bus────────────┘
                                 Projection:
                                   consumes OrderPlaced
                                   updates read store
                                   (async, eventual)
```

**THE TRADE-OFFS:**
**Gain:** Write model optimized for domain correctness (normalized, transactional). Read model optimized for query performance (denormalized, indexed). Independent scaling (read replicas for query side, write optimization for command side). Separate evolution (change read projection without touching write model).
**Cost:** Eventual consistency (read model lags behind write model). Complexity (two models to maintain, event propagation infrastructure). Debugging complexity (a failed projection update → stale read model → hard to diagnose). Only justified when read/write models or loads are significantly different.

**ESSENTIAL vs ACCIDENTAL COMPLEXITY:**
**Essential:** Eventual consistency is unavoidable when read and write models are separated. The time to propagate an event from write store to read store is irreducible. Applications must handle the case where a command has succeeded but the read model not yet reflects it.
**Accidental:** Axon Framework's annotation-based command/query routing. Event sourcing store implementations (EventStore, Kafka, Axon Server). Framework-imposed complexity on top of the core pattern.

---

### 🧪 Thought Experiment

**SETUP:** An e-commerce platform has 1,000,000 products. Users search by: category, price range, rating, in-stock status, tags. Search must return in < 200ms. Products are updated (price, stock) at 10,000 updates/second.

**WITHOUT CQRS (unified CRUD model):**

- Write path: `UPDATE products SET price=X WHERE id=Y` — fast, simple.
- Read path: `SELECT * FROM products WHERE category=? AND price BETWEEN ? AND ? AND in_stock=true ORDER BY rating DESC LIMIT 20` — hits the same table.
- Problem: indexes for write (B-tree on id) conflict with indexes for read (composite on category, price, rating, in_stock). Write performance degrades as read indexes grow. At 10K updates/second: lock contention on the products table under concurrent reads.
- Result: write throughput limited by read index maintenance. Read latency high due to complex query execution on normalized schema. Neither side is optimal.

**WITH CQRS:**

- Write path: `CommandHandler` accepts `UpdatePriceCommand`. Writes to write store (simple normalized table, B-tree on id only). Publishes `ProductPriceUpdated` event.
- Projection: consumes event, updates Elasticsearch index (denormalized document: {id, category, price, rating, inStock, tags}). Elasticsearch: pre-indexed for all search query patterns.
- Read path: `QueryHandler` accepts `SearchProductsQuery`. Queries Elasticsearch. Returns < 50ms.
- Result: write path is simple and fast (no complex indexes for reads). Read path is pre-optimized for the query pattern. Tradeoff: Elasticsearch may be 100-500ms behind the write store. Users searching immediately after a price update: may see old price briefly.

**THE INSIGHT:** CQRS eliminates the impedance mismatch between the data model optimal for transactional writes and the data model optimal for query reads. The cost is explicit eventual consistency — which is often acceptable in practice.

---

### 🧠 Mental Model / Analogy

> CQRS is like the difference between a company's internal accounting ledger (command model) and its published financial reports (query model). The ledger records every transaction in precise double-entry format — normalized, consistent, auditable. The financial report (balance sheet, income statement) is derived from the ledger but formatted for fast reading: pre-summarized, restructured, and presented in a reader-friendly format. No analyst reads the raw ledger to check the company's health — they read the report. The report is a projection of the ledger's current state, prepared for query. The ledger is the command model; the report is the read model; the preparation of the report from the ledger is the projection.

**Mapping:**

- **Company's internal ledger** → command model (write side)
- **Published financial report** → query model (read side / read store)
- **Report preparation process** → projection (event consumer that builds the read model)
- **Quarterly reporting cycle** → eventual consistency lag (report reflects last-quarter data)
- **Auditors checking the raw ledger** → direct query to the write store (exceptional case, not normal operation)

Where this analogy breaks down: financial reports are updated quarterly (high latency). CQRS query models are typically updated in milliseconds to seconds (event-driven, near-real-time). The "eventual consistency" of CQRS is much tighter than the quarterly delay analogy suggests. The analogy is good for the structural relationship (ledger → report) but overstates the lag.

---

### 📶 Gradual Depth - Four Levels

**Level 1 - What it is (anyone can understand):**
Normally, one database handles both saving data and displaying it. CQRS says: use different "views" for saving and showing. When you save an order (command), it updates a write model (optimized for saving correctly). A separate read model (optimized for displaying quickly) is kept up-to-date automatically. Showing orders comes from the read model — fast because it's pre-formatted for display.

**Level 2 - How to use it (junior developer):**
Simple Spring Boot CQRS without Event Sourcing:

```java
// Command: mutates state, returns void/acknowledgment
@CommandHandler
public OrderId handle(PlaceOrderCommand cmd) {
    Order order = Order.place(cmd.customerId(),
        cmd.items()); // domain logic
    orderWriteRepository.save(order);
    eventPublisher.publish(new OrderPlacedEvent(
        order.getId(), order.getItems(),
        order.getTotal()));
    return order.getId();
}

// Query: reads from denormalized read store
@QueryHandler
public OrderSummary handle(GetOrderSummaryQuery q) {
    return orderReadRepository
        .findById(q.orderId())  // pre-denormalized view
        .orElseThrow();
}

// Projection: updates read model from events
@EventHandler
public void on(OrderPlacedEvent event) {
    OrderSummary summary = OrderSummary.from(event);
    orderReadRepository.save(summary); // read store
}
```

**Level 3 - How it works (mid-level engineer):**
The write model uses domain aggregate objects (DDD aggregates — self-contained, enforce invariants). When an aggregate processes a command: it validates business rules and records the state change. The write store: a relational database table per aggregate (denormalized aggregate state), or an event store (Event Sourcing — DST-056). Events are published to an event bus (Kafka, RabbitMQ, Axon). Projection listeners consume events and update the read store. The read store is optimized per query pattern: one read store for "order history" (relational table, indexed by customerId), another for "product search" (Elasticsearch), another for "dashboard metrics" (Redis sorted set). CQRS does not mandate one read store — you can have N read stores, each optimized for a specific query pattern (this is the "polyglot persistence" benefit of CQRS).

**Level 4 - Why it was designed this way (senior/staff):**
CQRS's architectural justification is the incompatibility of the write optimization target (ACID transactions, domain rule enforcement, normalized schema) and the read optimization target (denormalized, pre-joined, query-specific indexing, scale-out read replicas). In a unified CRUD model: every index added for reads degrades write performance (index maintenance on INSERT/UPDATE). Every read query that requires joins forces the write schema to maintain referential integrity for read purposes. CQRS eliminates this constraint entirely: the write schema is designed exclusively for write correctness (normalize for update anomalies). The read schema is designed exclusively for read performance (denormalize for query speed). This is the correct application of the Single Responsibility Principle at the data model level. The cost — eventual consistency + projection infrastructure — is real. The pattern is only justified when the read/write models are genuinely different (different optimization targets) and the scale of reads significantly exceeds writes (10:1 or higher read:write ratio is a common threshold).

**Expert Thinking Cues:**

- "User places order (command succeeds, 202 Accepted) then immediately loads order history (read model returns old state)" → Read-after-write inconsistency. The projection hasn't processed the `OrderPlaced` event yet. Mitigation: (1) After command success: client polls with exponential backoff until order appears in read model. (2) Include version in command response: `{orderId: 123, expectedversion: 2}`. Query includes `?minVersion=5`. Read API returns 202 if read model version < 5. (3) For non-critical flows: accept eventual consistency (order history is eventually consistent, most users don't reload immediately). (4) Return the created object from the command response (breaks pure CQRS but simplifies client code). Each approach is a different trade-off.
- "Projection is failing — read model is stale for 30 minutes" → Event processing backlog. Check: is the event consumer group lagging? `kafka-consumer-groups.sh --describe --group projection-group`. If lag is high: consumer is too slow, or a poison-pill event is blocking the consumer. Dead letter queue: unconsumable events should go to a DLQ, not block the consumer. Check: does the projection handler throw exceptions that stop processing?
- "Multiple projections need to be rebuilt after a bug in projection code" → Replay events from the beginning. If using Kafka: reset consumer group offset to beginning. If using Axon Server: replay all events for specific aggregate type. Read store is rebuilt from scratch. This is a key advantage of CQRS + Event Sourcing: read models are disposable and rebuildable. Pure CQRS without Event Sourcing: if the write store only stores current state (not events), replay is impossible → projection bugs corrupt read state permanently.

---

### ⚙️ How It Works (Mechanism)

**Command flow:**

```
Client  API  CommandBus  CommandHandler  WriteStore  EventBus
  │     │       │              │             │           │
  │─POST▶       │              │             │           │
  │     │─command▶             │             │           │
  │     │        │─dispatch────▶             │           │
  │     │        │              │ validate   │           │
  │     │        │              │ business   │           │
  │     │        │              │ rules      │           │
  │     │        │              │─save───────▶           │
  │     │        │              │─publish event──────────▶
  │     │        │◀─orderId─────│             │           │
  │     │◀─202──│              │             │           │
```

**Query flow (from pre-built read store):**

```
Client  API  QueryBus  QueryHandler  ReadStore
  │     │      │            │           │
  │─GET─▶      │            │           │
  │     │─query▶            │           │
  │     │      │─dispatch───▶           │
  │     │      │             │─SELECT───▶ (pre-denormalized)
  │     │      │             │◀─data────│
  │     │◀─200─│            │           │
```

**Projection (async, eventual):**

```
EventBus  Projection  ReadStore
  │           │           │
  │─event─────▶           │
  │           │ transform  │
  │           │ to read   │
  │           │ format     │
  │           │─UPSERT─────▶ (denormalized)
  │           │           │ [read model now reflects event]
```

---

### 🔄 The Complete Picture - End-to-End Flow

**ORDER PLACEMENT WITH CQRS:**

```
Client  API    CmdHandler  WriteDB  EventBus  Projection  ReadDB
  │      │         │          │        │          │          │
  │─POST─▶         │          │        │          │          │
  │       │─cmd─────▶          │        │          │          │
  │       │         │ validate │        │          │          │
  │       │         │─save─────▶        │          │          │
  │       │         │─publish───────────▶           │          │
  │◀─202──│         │          │        │           │          │
  │                             [async] │─consume───▶           │
  │                                     │           │─upsert───▶│
  │                                     │     ← YOU ARE HERE   │
  │─GET /orders/123──────────────────────────────────────────────▶
  │                                              [may be stale] │
  │◀─order data ─────────────────────────────────────────────────│
```

**WHAT CHANGES AT SCALE:**
At scale: the event bus (Kafka) becomes the backbone. Multiple projections consume the same events to build specialized read stores. Event ordering per aggregate must be preserved (Kafka partitioning by aggregateId ensures ordering). At very high read scale: the read store scales independently (Elasticsearch cluster, Redis cluster) — no write bottleneck. Write side can use a smaller database (only current aggregate state). Eventual consistency window: Kafka processing → projection → read store update: typically 10-200ms under normal load, higher under projection backlog.

---

### 💻 Code Example

**BAD - Unified CRUD: one model serves reads and writes:**

```java
// BAD: OrderService does both mutation AND query
// Reads go to the same database as writes
// No separation of concerns
// Read queries add join complexity to write schema

@Service
public class OrderService {
    // Read: complex join query, slow at scale
    public List<OrderSummaryDto> getOrderHistory(
        String customerId, LocalDate from, LocalDate to) {
        // Joins: orders, order_items, products, payments
        // This query forces indexes that hurt writes
        return orderRepo.findByCustomerAndDateRange(
            customerId, from, to);
    }

    // Write: creates order
    public Order placeOrder(PlaceOrderRequest req) {
        Order order = new Order(req.customerId(),
            req.items());
        return orderRepo.save(order);
        // No event published — read side has no separation
    }
}
```

**GOOD - CQRS: separate command handler and query handler:**

```java
// GOOD: Command side - validates + mutates + publishes event
@Component
public class PlaceOrderCommandHandler {

    @CommandHandler
    public OrderId handle(PlaceOrderCommand cmd) {
        // Validate domain rules (write model responsibility)
        OrderAggregate order = OrderAggregate.place(
            cmd.customerId(),
            cmd.items(),
            inventoryService // domain service check
        );
        orderWriteRepo.save(order);

        // Publish event for projections to consume
        eventPublisher.publish(OrderPlacedEvent.from(order));
        return order.getId();
    }
}

// Projection: consumes events, updates read store
@Component
public class OrderHistoryProjection {

    @EventHandler
    public void on(OrderPlacedEvent event) {
        // Build denormalized read model entry
        OrderHistoryEntry entry = OrderHistoryEntry.builder()
            .orderId(event.orderId())
            .customerId(event.customerId())
            .totalAmount(event.total())
            .itemCount(event.items().size())
            .status("PLACED")
            .placedAt(event.occurredAt())
            .build();
        // Save to read store (separate table or DB)
        orderHistoryReadRepo.save(entry);
    }

    @EventHandler
    public void on(OrderShippedEvent event) {
        orderHistoryReadRepo.updateStatus(
            event.orderId(), "SHIPPED");
    }
}

// Query side: reads from denormalized read store
@Component
public class OrderHistoryQueryHandler {

    @QueryHandler
    public Page<OrderHistoryEntry> handle(
        GetOrderHistoryQuery query) {
        // Simple indexed query - no joins
        // Read store is pre-denormalized
        return orderHistoryReadRepo.findByCustomerId(
            query.customerId(),
            query.dateRange(),
            query.pageable()
        );
    }
}
```

---

### ⚖️ Comparison Table

|                    | CQRS                       | CRUD (unified model)     | Event Sourcing            |
| :----------------- | :------------------------- | :----------------------- | :------------------------ |
| Write model        | Domain-optimized           | Mixed (serves reads too) | Append-only event log     |
| Read model         | Query-optimized projection | Same as write            | Projection from events    |
| Consistency        | Eventual (between models)  | Strong (single model)    | Eventual (projection lag) |
| Complexity         | High                       | Low                      | Very high                 |
| Rebuild read model | Yes (if events available)  | No                       | Yes (replay events)       |
| Audit trail        | Partial (if events stored) | No                       | Full (all events)         |
| Scale read path    | Independent                | Coupled to write         | Independent               |

---

### ⚠️ Common Misconceptions

| Misconception                                                | Reality                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                  |
| :----------------------------------------------------------- | :--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| "CQRS requires Event Sourcing"                               | CQRS and Event Sourcing (DST-056) are independent patterns that are often combined but do NOT require each other. CQRS with traditional databases: command handler writes to a relational write table; an event is published; projection updates a separate read table. No Event Sourcing required. Event Sourcing without CQRS: store events as the write model, serve queries from reconstructed aggregate state. Combining them (CQRS + ES) is common because they complement each other well, but each can be used independently.    |
| "CQRS is too complex — only for large systems"               | CQRS complexity is real and often unjustified. Greg Young himself said: "CQRS is not something you should apply globally — rather, it's a local architectural option." Apply CQRS only to bounded contexts where: (1) read/write loads are significantly different, (2) read and write data models are genuinely different optimization targets, or (3) you need separate scaling. A simple CRUD application for managing user profiles does not benefit from CQRS. Apply it selectively to the parts of the system where it adds value. |
| "The read model is always up-to-date"                        | The read model is eventually consistent — it lags behind the command model by the time it takes for events to be published and projections to update the read store. Under normal operation: typically 10-500ms. Under load or projection failure: minutes or longer. Applications must be designed to handle stale reads gracefully. UI patterns: show the command result optimistically while the read model catches up; display a "processing" state until read model confirms.                                                       |
| "CQRS means microservices with separate read/write services" | CQRS is an architectural pattern — it can be implemented within a single service, within a monolith, or across microservices. The simplest implementation: one service with two packages (command and query), one database with two schemas (write and read tables). Microservices are not required. Distributing commands and queries across separate services is one deployment option, not a requirement of the pattern.                                                                                                              |

---

### 🚨 Failure Modes & Diagnosis

**Failure Mode 1: Projection Poisoned by Malformed Event**

**Symptom:** Read model stops updating. Users complain that order history is stale (showing data from 2 hours ago). No application errors visible in logs. Investigation: Kafka consumer group for the projection has high lag — it's not consuming new messages.
**Root Cause:** A malformed event (null field, unexpected format from a schema migration) was published to Kafka. The projection consumer attempts to deserialize/process it → throws an exception. The consumer retries the same message N times → eventually stops consuming. Because Kafka consumer offsets only advance after successful processing: the consumer is stuck at the malformed message. All subsequent events are blocked.
**Diagnostic:**

```bash
# Check consumer group lag:
kafka-consumer-groups.sh --bootstrap-server kafka:9092 \
  --describe --group order-projection-consumer
# Look for: LAG column > 0 and growing

# Find the stuck offset:
# CURRENT-OFFSET column shows where consumer is stuck
# Check the message at that offset:
kafka-console-consumer.sh --bootstrap-server kafka:9092 \
  --topic order-events \
  --partition 0 --offset 12345 --max-messages 1

# Check projection service logs for exceptions:
kubectl logs -n production order-projection-svc | \
  grep "ERROR\|Exception" | tail -50
```

**Fix:** Short-term: move the poisoned message to a Dead Letter Queue (DLQ). Skip the bad offset manually: `kafka-consumer-groups.sh --reset-offsets --to-offset 12346 --topic order-events --group order-projection-consumer --execute`. Long-term: configure automatic DLQ routing for deserialization failures.
**Prevention:** Implement a Dead Letter Queue for ALL projection consumers. Schema registry (Confluent Schema Registry, AWS Glue Schema Registry) — enforce schema compatibility on publish. Never break backward compatibility on events. Projection consumer: catch deserialization exceptions → route to DLQ → continue processing.

**Failure Mode 2: Read-After-Write Inconsistency Visible to User**

**Symptom:** User places an order via the UI (command API returns 200). User immediately clicks "My Orders" (query API). Their new order is not shown. User places the order again → duplicate order. Support reports multiple duplicate orders from confused users.
**Root Cause:** CQRS eventual consistency. Command processed and order saved. OrderPlaced event published to Kafka. But projection has not yet consumed and processed the event (10-500ms lag). User refreshes "My Orders" within this window → order not yet in read model → not shown → user thinks order failed → places again.
**Diagnostic:**

```bash
# Measure projection lag (time from event to read model update):
# Add timestamp to event: publishedAt
# Add timestamp to read model entry: projectedAt
# projectedAt - publishedAt = projection lag

# Check Kafka consumer lag in real time:
watch kafka-consumer-groups.sh --bootstrap-server kafka:9092 \
  --describe --group order-projection-consumer
# Under normal load: LAG should be < 100 (near-zero)
# Spike: projection falling behind
```

**Fix:** Multiple options: (1) **Optimistic UI:** after command success, show the new order in the UI immediately (client-side state) without waiting for read model. Mark it as "pending confirmation." (2) **Version-based polling:** command returns `{orderId: 123, version: 2}`. Client polls `GET /orders/123?minVersion=5` — read API returns 202 until read model has version >= 5. (3) **Hybrid command return:** return the new order object with the command response (breaks pure CQRS but eliminates the inconsistency). Choose based on business tolerance for eventual consistency.
**Prevention:** Explicit consistency contract in API documentation: "read model is eventually consistent; after placing an order, order may not appear in history for up to 2 seconds." Design UX to handle this (loading states, confirmation pages that don't immediately redirect to order history).

**Failure Mode 3: Security - Command Authorization Bypass via Query Side**

**Symptom:** Security audit reveals: a user can access another user's order details by directly querying the read store endpoint. The command side correctly validates that users can only modify their own orders. But the query side (`GET /orders/{orderId}`) does not validate that the requesting user owns the requested order — it returns any order to any authenticated user.
**Root Cause:** CQRS encourages separate teams to implement command and query sides. Command handlers implement authorization (user can only modify their own resources). Query handlers — built separately — forgot to implement authorization for read access. Since queries are "read-only" (no state change), developers may incorrectly assume authorization is not needed.
**Diagnostic:**

```bash
# Test: authenticated as user A, request user B's order:
curl -H "Authorization: Bearer <user-A-token>" \
  https://api.example.com/orders/<user-B-order-id>
# If 200 with order data: authorization missing on query side

# Check query handler code for authorization:
grep -r "getUserId\|currentUser\|authentication" \
  src/main/java/query/
# If not present in query handlers: missing auth
```

**Fix:** Authorization must be implemented on BOTH command AND query sides. Query handler: extract userId from JWT token, add `WHERE customer_id = :userId` to all queries. Apply Spring Security method-level security:

```java
@QueryHandler
@PreAuthorize("@orderAuthz.canView(#query.orderId, authentication)")
public OrderSummary handle(GetOrderSummaryQuery query) { ... }
```

**Prevention:** Security review checklist: "does every query endpoint validate that the requesting user has access to the requested resource?" CQRS does not reduce the need for authorization — it multiplies it (must implement on both sides). Integration test: create resource as user A, request as user B → expect 403.

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**

- DST-049 - Saga Pattern (command side orchestrates sagas for distributed transactions)
- DST-056 - Event Sourcing (write side alternative; CQRS + ES is the classic combination)

**Builds On This (learn these next):**

- DST-056 - Event Sourcing (natural extension of CQRS write side)
- DST-049 - Saga Pattern (commanding distributed workflows in CQRS systems)

**Alternatives / Comparisons:**

- DST-033 - Eventual Consistency (CQRS read model is eventually consistent — understand the trade-off)

---

### 📌 Quick Reference Card

```
+------------------+--------------------------------+
| WHAT IT IS       | Separate write model (commands)|
|                  | from read model (queries);     |
|                  | each independently optimized   |
+------------------+--------------------------------+
| PROBLEM SOLVED   | One CRUD model can't optimize  |
|                  | for both writes (normalized,   |
|                  | transactional) and reads       |
|                  | (denormalized, query-fast)     |
+------------------+--------------------------------+
| KEY INSIGHT      | Read model is a projection     |
|                  | (derived, rebuildable) — NOT   |
|                  | the authoritative source       |
+------------------+--------------------------------+
| USE WHEN         | Read:write ratio >10:1; read   |
|                  | and write models are genuinely |
|                  | different; independent scaling |
|                  | needed                         |
+------------------+--------------------------------+
| AVOID WHEN       | Simple CRUD; small scale;      |
|                  | team lacks distributed systems |
|                  | expertise; strong consistency  |
|                  | required on all reads          |
+------------------+--------------------------------+
| TRADE-OFF        | Independent optimization       |
|                  | vs eventual consistency +      |
|                  | significant complexity         |
+------------------+--------------------------------+
| ONE-LINER        | Commands mutate; queries read; |
|                  | projections sync; everything   |
|                  | eventual                       |
+------------------+--------------------------------+
| NEXT EXPLORE     | DST-056 Event Sourcing;        |
|                  | DST-049 Saga Pattern           |
+------------------+--------------------------------+
```

**If you remember only 3 things:**

1. CQRS and Event Sourcing are INDEPENDENT patterns. CQRS can use traditional databases for both sides. Event Sourcing can be used without CQRS. They are often combined (CQRS + ES) because they complement each other, but neither requires the other.
2. The read model is eventually consistent — it is always "behind" the write model by the event propagation time. Design all UI/API flows to handle stale reads. Provide version-based polling or optimistic UI updates to prevent user confusion after a command succeeds.
3. Apply CQRS selectively. It is not a global architecture — it is a local pattern for bounded contexts with significantly different read/write optimization needs. Greg Young: "CQRS should be used on specific bounded contexts." Applying it globally to a simple CRUD system adds massive complexity with no benefit.

**Interview one-liner:**
"CQRS separates the write model (commands: `PlaceOrderCommand` → validates domain rules, updates write store, publishes `OrderPlacedEvent`) from the read model (queries: `GetOrderHistoryQuery` → reads from pre-denormalized read store). A projection (event consumer) asynchronously updates the read store when events arrive from the command side. This enables independent optimization: write model is normalized for transactional correctness; read model is denormalized for query speed. Trade-off: eventual consistency — the read model is milliseconds to seconds behind the write model. Justified when read:write ratio is >10:1 or when read and write data models are genuinely incompatible optimization targets."

---

### 💎 Transferable Wisdom

**Reusable Engineering Principle:**
Separate concerns with different optimization targets at the model level, not just the code level. When two consumers of a data model have conflicting optimization requirements (writes want normalization to prevent update anomalies; reads want denormalization for query speed), the correct resolution is separate models — not a compromise model that serves both poorly. This principle appears in any system with competing access patterns: OLTP (transactional) vs OLAP (analytical) databases use the same pattern (separate transactional and analytical stores, synchronized via ETL or CDC). Cache-aside caching (DST) is a read-optimized copy of the write store, synchronized asynchronously. Read replicas in databases are the same pattern implemented at the infrastructure level. CQRS brings this pattern to the application model level.

**Where else this pattern appears:**

- **OLTP vs OLAP (data warehouse):** Operational databases (PostgreSQL, MySQL) are optimized for transactional writes (ACID, normalized schema, row-level locking). Data warehouses (Snowflake, Redshift, BigQuery) are optimized for analytical reads (columnar storage, denormalized star schema, massive parallel queries). The ETL/ELT pipeline that moves data from OLTP to the warehouse is the projection in CQRS. This is CQRS at the infrastructure level — the same conceptual pattern applied to the data platform. Business intelligence users query the warehouse (read model); application users transact in the OLTP database (write model).
- **DNS (Domain Name System):** DNS maintains a global distributed read model (highly cached, eventually consistent) for resolving domain names. The authoritative write model: DNS zone files on authoritative nameservers. TTL controls eventual consistency window. Recursive resolvers cache DNS records (the read model). When a DNS record changes (command), the change propagates globally over hours (projection lag = TTL). Clients read from caches (read model), not directly from authoritative servers. DNS is CQRS at planetary scale, with a multi-hour eventual consistency window.
- **Git log (commit history) vs working tree:** Git's working tree is the current state (the read model — what you see and edit). Git's commit history (the event log) is the authoritative write model. Every `git commit` appends an event (command side). `git checkout` or `git log` reads from the computed state (query side). `git blame` and `git log --graph` are projections that compute derived views from the event log. Git is CQRS + Event Sourcing for source code: immutable event log (commits) + derived working tree (read model) + projections (git blame, git log).

---

### 💡 The Surprising Truth

CQRS is often introduced to engineering teams alongside Event Sourcing (DST-056) as a combined pattern — and many developers believe they are inseparable. The surprising truth: the most valuable benefit of CQRS is not the architectural separation itself, but the mindset shift it forces. When teams design systems with CQRS, they must explicitly think: "What does the write model need to be consistent about? What does the read model need to optimize for? How much eventual consistency is acceptable?" This explicit reasoning about consistency and optimization — which unified CRUD models paper over — is where most of the value comes from. Teams that adopt CQRS often report that the biggest improvement was not performance or scalability (the typical justifications) but clarity of design: commands became explicit, validated operations; queries became explicit, contract-bound reads; the boundary between mutation and retrieval became unambiguous. The pattern enforces discipline that makes systems easier to reason about, test, and evolve — independent of whether the performance benefits materialize.

---

### 🧠 Think About This Before We Continue

**Q1 (D - Root Cause):** After deploying a bug fix to the order projection (correcting how order status is computed), the engineering team discovers that all historical order statuses in the read store are wrong — they were computed incorrectly by the old projection code. The fix is applied to new events, but historical records in the read store still show incorrect data. How do you fix the historical data, and what architectural property would make this easy?
_Hint:_ The fix depends on what the write side stores. If CQRS with Event Sourcing (events stored in event store): replay all historical events through the corrected projection. Wipe the read store, re-consume all events from the beginning → read store is rebuilt correctly. This is the "projection replay" capability — a major benefit of Event Sourcing. If CQRS without Event Sourcing (write side stores only current aggregate state, not events): you cannot replay. Events were not persisted. You only have the current state. Fix: migrate read store data directly (SQL update based on write store state). Or: accept that historical data is wrong and apply fix only to new events (data loss/corruption accepted). This is why CQRS + Event Sourcing is the recommended combination: Event Sourcing provides the event log needed to rebuild (and re-project) the read model from scratch at any time. Without Event Sourcing: projection bugs can permanently corrupt the read model.

**Q2 (B - Scale):** A system processes 5,000 commands/second (writes). Each command publishes 1 event. The read model has 3 projections: order history (Postgres), product search (Elasticsearch), dashboard metrics (Redis). At peak: how many events/second must each projection consumer process? What happens if one projection falls behind? What is the maximum acceptable lag for each read model, and what drives that decision?
_Hint:_ Event volume: 5,000 events/second per projection × 3 projections = 15,000 events/second total consumed (3 independent consumer groups). Each projection must process 5,000 events/second. If one projection falls behind (say Elasticsearch is slow at indexing): the Kafka consumer lag for the product search group grows. Events accumulate in Kafka (which has ample storage). Other projections are unaffected (independent consumer groups). Product search is stale for the duration of the lag. Maximum acceptable lag per model: (1) Dashboard metrics (Redis): 5-10 minutes acceptable — dashboards are refreshed every 5 minutes. (2) Order history (Postgres): seconds to 1 minute — users may refresh immediately after placing. (3) Product search (Elasticsearch): 1-10 seconds — acceptable for search, not for real-time inventory. What drives the lag tolerance: user expectations (how quickly will users query after a command?), business impact (stale product prices vs stale dashboard metrics), SLA requirements (order status must be visible within 30 seconds of placement). Design alerts on consumer group lag thresholds matching these tolerances: lag > equivalent of 10 seconds → alert for order history projection.

**Q3 (C - Design Trade-off):** A team is building a financial transaction system. Regulations require: (1) every balance query must return the exact current balance (no staleness), (2) all transactions must be recorded with full audit trail, (3) read scale: 1,000 balance queries/second, write scale: 10 transactions/second. Should they use CQRS? What alternatives exist? How do they satisfy the strong consistency requirement?
_Hint:_ CQRS with eventual consistency is incompatible with requirement (1): "balance query must return exact current balance." CQRS read model can be stale. If a deposit just happened and the user queries balance immediately: CQRS may show old balance. In financial systems: showing wrong balance is a compliance violation and a UX disaster. Options: (1) Don't use CQRS for the balance read. Use strong-consistent read directly from the write store (with read replicas for the 1,000 qps load — read replicas with synchronous replication or PostgreSQL synchronous_standby_names). Trade-off: read replicas with synchronous replication have write-side latency overhead. (2) Use CQRS ONLY for audit trail and reporting (requirement 2). The balance remains in the write store (strongly consistent). The audit log/event stream feeds into separate read models for reporting. CQRS is partial: not applied to the balance read, applied to reporting reads. (3) Account for read-your-writes consistency: after a transaction command, return the new balance in the command response. Client caches this value for its session. Subsequent balance reads: return the cached value until a fresher value arrives. This is consistent for the user who just transacted (reads own writes) while allowing eventual consistency for others. Lesson: CQRS is inappropriate for use cases requiring strong read consistency. Apply it only to read models where eventual consistency is acceptable.
