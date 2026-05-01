---
layout: default
title: "Event Sourcing in Microservices"
parent: "Microservices"
nav_order: 659
permalink: /microservices/event-sourcing-in-microservices/
number: "659"
category: Microservices
difficulty: ★★★
depends_on: "CQRS in Microservices, Event-Driven Microservices"
used_by: "Distributed Transaction, Saga Pattern (Microservices)"
tags: #advanced, #microservices, #distributed, #database, #architecture, #pattern, #deep-dive
---

# 659 — Event Sourcing in Microservices

`#advanced` `#microservices` `#distributed` `#database` `#architecture` `#pattern` `#deep-dive`

⚡ TL;DR — **Event Sourcing** stores the complete history of an entity's state changes as an immutable, append-only log of events — not the current state. Current state is derived by replaying events. Enables: full audit trail, time-travel queries, projection rebuilding, and natural event publication for CQRS. The trade-off: queries require rebuilding state from events; schema evolution is complex; snapshots are needed for performance on long-lived entities.

| #659            | Category: Microservices                               | Difficulty: ★★★ |
| :-------------- | :---------------------------------------------------- | :-------------- |
| **Depends on:** | CQRS in Microservices, Event-Driven Microservices     |                 |
| **Used by:**    | Distributed Transaction, Saga Pattern (Microservices) |                 |

---

### 📘 Textbook Definition

**Event Sourcing** is a persistence pattern (Greg Young, 2010) where instead of storing the current state of an entity (the "last-write-wins" model of traditional databases), you store all the **events** that caused the entity to reach its current state. The event log is the **source of truth** — the current state is a derived view obtained by replaying all events in order. The event store is append-only: events are never updated or deleted (immutable). In microservices, Event Sourcing is frequently combined with CQRS: the write side is the event store (append events); the read side consists of projections built from the event stream. Benefits: complete audit trail (every state change has a reason and timestamp); ability to replay events to rebuild projections or add new ones retroactively; temporal queries ("what was the state at time T?"); natural event publication (the write operation IS event publication — no separate `kafkaTemplate.send()` needed). Challenges: querying current state requires event replay (mitigated by snapshots); schema evolution of historical events is complex; no `UPDATE`/`DELETE` so corrections require compensating events (not overwrites).

---

### 🟢 Simple Definition (Easy)

Instead of saving "Order status is SHIPPED," you save every thing that happened: "Order was placed," "Payment was received," "Order was packed," "Order was shipped." To know the current status, you replay all events in order. Like a bank account: you don't just store "balance = $500" — you store every deposit and withdrawal. The balance is calculated by summing transactions.

---

### 🔵 Simple Definition (Elaborated)

Traditional database: `UPDATE orders SET status='SHIPPED' WHERE id=123`. History lost — you only know the current state. Event Sourcing: append `{type: "OrderShipped", orderId: 123, at: T3}` to the events table. Previous events: `{type: "OrderPlaced", at: T1}`, `{type: "PaymentReceived", at: T2}` — still there. Replay all three → current state: SHIPPED. Query "what was the state at T2?" → replay T1 and T2 events only → state: PAYMENT_RECEIVED. Full history always queryable. No `UPDATE` ever touches past events.

---

### 🔩 First Principles Explanation

**Event store schema and replay mechanics:**

```sql
-- Event store table (append-only, no UPDATE/DELETE):
CREATE TABLE order_events (
    id          BIGSERIAL PRIMARY KEY,
    aggregate_id VARCHAR(36) NOT NULL,    -- e.g. orderId
    aggregate_type VARCHAR(50) NOT NULL,  -- e.g. "Order"
    event_type  VARCHAR(100) NOT NULL,    -- e.g. "OrderPlaced", "OrderShipped"
    event_version INT NOT NULL,           -- monotonic sequence per aggregate
    payload     JSONB NOT NULL,           -- event data (serialized)
    occurred_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    caused_by   VARCHAR(36),              -- command ID that caused this event (audit)
    user_id     VARCHAR(36)               -- who triggered it (audit)
);

-- Optimistic concurrency check: no duplicate version per aggregate
CREATE UNIQUE INDEX idx_aggregate_version
    ON order_events(aggregate_id, event_version);

-- Efficient replay: fetch all events for an aggregate in order
CREATE INDEX idx_aggregate_id_version
    ON order_events(aggregate_id, event_version ASC);

-- Example rows for Order ord-123:
-- id | aggregate_id | event_type      | event_version | payload
--  1 | ord-123      | OrderPlaced     | 1             | {"productId":"p1","amount":49.99,"customerId":"c1"}
--  2 | ord-123      | PaymentReceived  | 2             | {"paymentId":"pay-1","method":"CARD"}
--  3 | ord-123      | OrderShipped    | 3             | {"trackingNumber":"TRK-999","carrier":"FedEx"}
```

**Aggregate reconstruction from event stream:**

```java
// Aggregate: Order — current state derived from events
class Order {
    private String id;
    private String customerId;
    private String productId;
    private BigDecimal amount;
    private OrderStatus status;
    private String trackingNumber;
    private int version;  // current event version (for optimistic concurrency)

    // Static factory: reconstruct from event stream
    public static Order reconstitute(List<OrderEvent> events) {
        Order order = new Order();
        events.forEach(order::apply);  // apply each event in order
        return order;
    }

    // Apply each event type → mutate state
    private void apply(OrderEvent event) {
        this.version = event.getEventVersion();
        switch (event) {
            case OrderPlacedEvent e -> {
                this.id = e.getOrderId();
                this.customerId = e.getCustomerId();
                this.productId = e.getProductId();
                this.amount = e.getAmount();
                this.status = OrderStatus.PLACED;
            }
            case PaymentReceivedEvent e -> this.status = OrderStatus.PAID;
            case OrderShippedEvent e -> {
                this.status = OrderStatus.SHIPPED;
                this.trackingNumber = e.getTrackingNumber();
            }
            case OrderCancelledEvent e -> this.status = OrderStatus.CANCELLED;
            default -> throw new IllegalArgumentException("Unknown event type: " + event.getClass());
        }
    }

    // Command handler: ship order
    public OrderShippedEvent ship(String trackingNumber) {
        if (this.status != OrderStatus.PAID)
            throw new IllegalStateException("Cannot ship order in status: " + this.status);
        return new OrderShippedEvent(this.id, trackingNumber, Instant.now(), this.version + 1);
    }
}
```

**Snapshots — solving the performance problem for long-lived aggregates:**

```java
// PROBLEM: Order with 500 events → rebuild requires loading + applying 500 events
// SOLUTION: Snapshot = state at a point in time, stored periodically

@Entity
class OrderSnapshot {
    @Id String aggregateId;
    int snapshotVersion;          // event version at snapshot time
    String stateJson;             // serialized Order state
    Instant snapshotAt;
}

// Optimized load: snapshot + only events AFTER snapshot version
class OrderRepository {
    public Order load(String orderId) {
        Optional<OrderSnapshot> snapshot = snapshotRepository.findById(orderId);

        if (snapshot.isPresent()) {
            // 1. Deserialize snapshot (fast)
            Order order = objectMapper.readValue(snapshot.get().getStateJson(), Order.class);
            int fromVersion = snapshot.get().getSnapshotVersion();

            // 2. Load only events AFTER snapshot (few events since last snapshot)
            List<OrderEvent> recentEvents = eventRepository
                .findByAggregateIdAndVersionGreaterThan(orderId, fromVersion);

            // 3. Apply recent events on top of snapshot state
            recentEvents.forEach(order::apply);
            return order;
        }

        // No snapshot: full replay
        List<OrderEvent> allEvents = eventRepository.findByAggregateId(orderId);
        return Order.reconstitute(allEvents);
    }

    @Transactional
    public void saveWithSnapshot(Order order, List<OrderEvent> newEvents) {
        // Append new events
        eventRepository.saveAll(newEvents);

        // Create snapshot every N events (e.g., every 50 events):
        if (order.getVersion() % 50 == 0) {
            snapshotRepository.save(new OrderSnapshot(
                order.getId(), order.getVersion(), objectMapper.writeValueAsString(order), Instant.now()
            ));
        }
    }
}
```

---

### ❓ Why Does This Exist (Why Before What)

Traditional databases only store current state. An `UPDATE` overwrites history permanently. Business frequently needs: "who changed this and when?", "what did the state look like before the bug was introduced?", "replay all events to feed a new analytics system." Standard audit tables are bolted-on, inconsistently applied, and can be mutated. Event Sourcing makes history the primary data — current state is just a view over history.

---

### 🧠 Mental Model / Analogy

> Event Sourcing is like a version control system (Git) for your data. Git doesn't store "current file state" — it stores every commit (event) that changed the file. Current state = replaying all commits from the beginning (`git log`). "What did this file look like in 2022?" → `git checkout <commit>`. You can create new branches (projections) from any point in history. Commits are immutable: you can't change history (only `git revert` adds a new commit that undoes old changes — the equivalent of a compensating event). If the entire repo was deleted but you have the commit log, you can reconstruct everything.

---

### ⚙️ How It Works (Mechanism)

**Command → Event → Projection pipeline:**

```
User/API → OrderCommandService.placeOrder(command)
    │
    ├── 1. Load aggregate: Order.reconstitute(events from event store)
    ├── 2. Execute command logic: order.place(command)
    │      → validates business rules
    │      → returns OrderPlacedEvent (NOT saved yet)
    ├── 3. Optimistic concurrency check: expected version = current version + 1
    ├── 4. Append event to event store (unique constraint on aggregate+version)
    ├── 5. Publish event to Kafka (or Transactional Outbox)
    └── 6. Return response to caller

Kafka consumer (Projector):
    ├── Receives OrderPlacedEvent
    ├── Updates Elasticsearch OrderDocument
    └── Updates ClickHouse analytics fact
```

---

### 🔄 How It Connects (Mini-Map)

```
Event-Driven Microservices
(events as integration mechanism)
        │
        ▼
Event Sourcing in Microservices  ◄──── (you are here)
(events as the write model / source of truth)
        │
        ├── CQRS → natural pair: event store = command side; projections = query side
        ├── Saga Pattern → saga state stored as saga events in event store
        └── Distributed Transaction → event sourcing enables saga-based alternative
```

---

### 💻 Code Example

**Temporal query — state at a point in time:**

```java
// "What was Order ord-123's status at 2024-01-15 10:00:00 UTC?"
public Order getStateAtTime(String orderId, Instant pointInTime) {
    List<OrderEvent> eventsUpToTime = eventRepository
        .findByAggregateIdAndOccurredAtLessThanEqualOrderByEventVersion(
            orderId, pointInTime
        );
    if (eventsUpToTime.isEmpty()) {
        throw new OrderNotFoundException("Order not found or didn't exist at " + pointInTime);
    }
    return Order.reconstitute(eventsUpToTime);
}
// Use case: "Customer disputes a charge. What was the order status when the payment was taken?"
// Answer: replay events up to payment timestamp → exact state at dispute time
```

---

### ⚠️ Common Misconceptions

| Misconception                               | Reality                                                                                                                                                                                                                                                        |
| ------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Event Sourcing means you never delete data  | You can delete events for GDPR compliance via "crypto-shredding": encrypt personal data in events with a per-user key; delete the key to effectively erase personal data while keeping event structure intact                                                  |
| Event Sourcing is suitable for all services | Event Sourcing adds significant complexity. Use it when: audit trail is critical, temporal queries are needed, or event publication is a core requirement. For simple CRUD services (CMS pages, config settings), traditional persistence is simpler           |
| Event Sourcing stores events in Kafka       | Kafka is a message bus with limited retention. The event STORE (source of truth) should be a database with infinite retention (EventStoreDB, PostgreSQL events table, DynamoDB). Kafka is used for event delivery to consumers — not as the event store itself |
| Current state is not stored anywhere        | Projections (CQRS read models) ARE current state, derived from events. For performance-critical lookups, snapshots cache the reconstructed aggregate state. The point: current state is derived and can always be rebuilt from events                          |

---

### 🔥 Pitfalls in Production

**Event schema evolution — breaking changes in immutable history:**

```
PROBLEM:
  OrderPlacedEvent v1: {"orderId": "123", "amount": 49.99}
  3 months later: team renames "amount" to "totalAmount"
  OrderPlacedEvent v2: {"orderId": "123", "totalAmount": 49.99}

  Event store: contains millions of v1 events and new v2 events.
  Projector code reads "totalAmount" → fails on v1 events (field missing).
  Projection rebuild: crashes immediately on first v1 event.

STRATEGY 1: Upcasting (event transformation on read):
  Register upcasters: v1 → v2 transformation applied at read time.
  Upcaster: map "amount" field to "totalAmount" if "totalAmount" is missing.
  Event store: unchanged (immutable v1 events preserved).
  Projector code: always receives v2 events (upcasted).
  Axon Framework: built-in upcasting support.

STRATEGY 2: Additive-only schema changes:
  Never rename fields. Add new optional fields alongside old ones.
  v1: {"orderId": "123", "amount": 49.99}
  v2: {"orderId": "123", "amount": 49.99, "totalAmount": 49.99}  ← both present
  Old readers: read "amount" (still present)
  New readers: read "totalAmount" (present in new events)
  After migration complete: old "amount" field deprecated but not removed
  Cost: event size grows over time

STRATEGY 3: Versioned event types:
  "OrderPlacedV1", "OrderPlacedV2" as separate event types
  Projector: handles both types with different parsing logic
  Cleanest separation, most verbose
```

---

### 🔗 Related Keywords

- `CQRS in Microservices` — natural partner: event store = write side; projections = read side
- `Event-Driven Microservices` — events published from the event store drive downstream services
- `Saga Pattern (Microservices)` — saga state can be stored as saga events in event store
- `Distributed Transaction` — event sourcing enables saga alternative to 2PC

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ CORE IDEA    │ Immutable event log = source of truth      │
│ CURRENT STATE│ Derived by replaying events (or snapshot) │
│ EVENT STORE  │ Append-only DB (NOT Kafka — Kafka delivers)│
├──────────────┼───────────────────────────────────────────┤
│ BENEFITS     │ Audit trail, time-travel, projection replay│
│ CHALLENGES   │ Schema evolution, snapshot management,    │
│              │ GDPR erasure (crypto-shredding)            │
├──────────────┼───────────────────────────────────────────┤
│ USE WHEN     │ Audit critical, temporal queries needed    │
│ SKIP WHEN    │ Simple CRUD, no audit requirement          │
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** Your order service uses event sourcing. A production bug caused 10,000 `OrderShippedEvent` events to be written with incorrect tracking numbers (all set to "INVALID-TRACKING"). You need to correct the data. You cannot delete the incorrect events (immutable event log). Design the correction strategy: (a) what compensating event do you create? (b) How does the aggregate handle the sequence: `OrderShipped(v3, tracking=INVALID)` → `TrackingNumberCorrected(v4, tracking=TRK-999)`? (c) How do you bulk-apply the correction for 10,000 affected orders without downtime?

**Q2.** Your event store has grown to 2 billion events across all aggregates over 3 years. A new "CustomerLifetimeValue" service wants to consume ALL historical order events to calculate per-customer lifetime value. The full replay will take 72 hours to process. During those 72 hours, new `OrderPlaced` events are arriving in real time. How do you design the catch-up subscription mechanism? Specifically: when does the service switch from reading from the historical event store to reading from the live Kafka stream, and how do you ensure no events are missed or double-processed during the transition?
