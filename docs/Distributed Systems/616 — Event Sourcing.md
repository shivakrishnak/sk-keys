---
layout: default
title: "Event Sourcing"
parent: "Distributed Systems"
nav_order: 616
permalink: /distributed-systems/event-sourcing/
number: "0616"
category: Distributed Systems
difficulty: ★★★
depends_on: CQRS, Domain Events, Append-Only Log, Event-Driven Architecture
used_by: CQRS, Audit Logs, Outbox Pattern, Saga Pattern, Time Travel Queries
related: CQRS, Outbox Pattern, Saga Pattern, Domain Events, Append-Only Log
tags:
  - distributed
  - architecture
  - data
  - pattern
  - deep-dive
---

# 616 — Event Sourcing

⚡ TL;DR — Event Sourcing stores the history of changes as an immutable, append-only log of domain events — state is never updated in-place but derived by replaying events; this provides complete audit history, temporal queries ("what was the state at T-3 days?"), and the ability to reconstruct any past or present state from events alone.

| #616            | Category: Distributed Systems                                       | Difficulty: ★★★ |
| :-------------- | :------------------------------------------------------------------ | :-------------- |
| **Depends on:** | CQRS, Domain Events, Append-Only Log, Event-Driven Architecture     |                 |
| **Used by:**    | CQRS, Audit Logs, Outbox Pattern, Saga Pattern, Time Travel Queries |                 |
| **Related:**    | CQRS, Outbox Pattern, Saga Pattern, Domain Events, Append-Only Log  |                 |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
A bank account's current balance is `$1,247.63`. The customer calls support: "Why is my balance so low?" You look at the accounts table: `{id: 123, balance: 1247.63, updated_at: 2024-01-15}`. That's all. No trace of what transactions occurred. Application logs might have some history, but they're not complete, not queryable, not authoritative. The "what happened" is lost — permanently.

**BREAKING POINT:**
Financial systems using event sourcing have a complete record of every credit and debit. "Why is my balance $1,247.63?" — query the event log: `[$5000 initial deposit, -$2000 rent, -$400 groceries, +$150 refund, -$1502.37 tuition...]`. The current state is always derivable from the events, and the events themselves ARE the system of record, not the current state.

---

### 📘 Textbook Definition

**Event Sourcing** is an architectural pattern where application state is derived by replaying a sequence of immutable domain events, rather than stored as current state. The system's **source of truth** is the event log. Current state is a **projection** — a materialized view derived from replaying events. **Core properties:** (1) **Append-only**: events are never modified or deleted (except in compliance scenarios with specific GDPR deletion procedures). (2) **Temporal queries**: replay events up to any point in time to reconstruct historical state. (3) **Natural audit log**: every state change has a corresponding event with timestamp, user, and context. (4) **Event evolution**: events are versioned; projections handle multiple event versions. **Snapshot pattern**: to avoid replaying all events since epoch, periodically capture current state as a snapshot; on load, apply snapshot + events since snapshot.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
Instead of storing "current balance = $1,247", store every transaction that led there — the current state is always computable from the transaction history.

**One analogy:**

> Event sourcing is like maintaining a general ledger in accounting (double-entry bookkeeping). You never "update" the ledger — you only append new journal entries. The current balance isn't stored; it's the sum of all entries. The ledger IS the truth. The balance is derived, not stored. Any audit, any reconstruction, any "what happened on March 15th?" is answered by reading the ledger.

**One insight:**
Every database is implicitly event-sourced at the WAL (Write-Ahead Log) level — the WAL is an append-only log of all changes. Event sourcing makes this the explicit application-level model. PostgreSQL's WAL, Kafka's immutable log, git's commit history — all are event-sourced systems. Git's core architecture: your codebase's state = applying all commits from the beginning. You can `git checkout <sha>` to any historical state. Event sourcing is git for application state.

---

### 🔩 First Principles Explanation

**EVENT STORE STRUCTURE:**

```
Table: order_events
  aggregate_id  | version | event_type       | event_data                          | timestamp
  order-123     |    1    | OrderPlaced      | {"customer":"alice","total":150.00}  | 2024-01-10 10:00:00
  order-123     |    2    | ItemReserved     | {"sku":"SKU-001","qty":2}            | 2024-01-10 10:00:01
  order-123     |    3    | PaymentCharged   | {"amount":150.00,"chargeId":"ch_1"} | 2024-01-10 10:00:02
  order-123     |    4    | ShipmentCreated  | {"trackingNo":"TRK-999"}             | 2024-01-10 10:30:00
  order-123     |    5    | OrderDelivered   | {"deliveredAt":"2024-01-12"}         | 2024-01-12 14:22:00

Loading Order-123 current state = replay events 1-5:
  v1 OrderPlaced:    status=PLACED, total=150
  v2 ItemReserved:   items[SKU-001: reserved]
  v3 PaymentCharged: paymentStatus=CHARGED, chargeId=ch_1
  v4 ShipmentCreated: trackingNo=TRK-999, status=SHIPPED
  v5 OrderDelivered: status=DELIVERED, deliveredAt=2024-01-12

To know state at 2024-01-10 10:30:01 (between v3 and v4):
  Replay only events 1-3 → status=PLACED (payment charged but not yet shipped)
```

**AGGREGATE LOADING + COMMAND HANDLING:**

```java
@Aggregate
public class OrderAggregate {
    private String orderId;
    private OrderStatus status;
    private BigDecimal total;
    private String chargeId;

    // Reconstruct from event history (replaying events via @EventSourcingHandler):
    @EventSourcingHandler
    public void on(OrderPlacedEvent e) {
        this.orderId = e.getOrderId();
        this.status = OrderStatus.PLACED;
        this.total = e.getTotal();
    }

    @EventSourcingHandler
    public void on(PaymentChargedEvent e) {
        this.status = OrderStatus.PAYMENT_CHARGED;
        this.chargeId = e.getChargeId();
    }

    // Handle new command — check invariants, apply new event:
    @CommandHandler
    public void handle(ShipOrderCommand cmd) {
        if (status != OrderStatus.PAYMENT_CHARGED) {
            throw new IllegalStateException("Can only ship paid orders");
        }
        // Emit event (do not directly modify state here):
        AggregateLifecycle.apply(new ShipmentCreatedEvent(orderId, cmd.getTrackingNo()));
    }

    @EventSourcingHandler
    public void on(ShipmentCreatedEvent e) {
        this.status = OrderStatus.SHIPPED;
    }
}
```

**SNAPSHOT PATTERN:**

```
Problem: Order-123 has 10,000 events (1 order per day over 27 years — bank account).
Loading this aggregate for every command = replay 10,000 events = slow.

Snapshot Pattern:
  Periodically (e.g., every 100 events) capture current state:

  Table: order_snapshots
    aggregate_id | version | state_json                              | created_at
    order-123    |  5000   | {"status":"DELIVERED","total":150.0,...} | 2024-01-12

  Loading Order-123 with snapshot:
  1. Load latest snapshot: version=5000, state={...}
  2. Apply only events with version > 5000 (say events 5001-5003)
  3. Ready: only 3 events replayed, not 5003

  Trade-off: snapshot storage cost vs. replay cost.
  Practical threshold: snapshot every 50-500 events depending on event size and load.
```

**OPTIMISTIC CONCURRENCY CONTROL:**

```
Problem: Two commands arrive simultaneously for Order-123.
Both load aggregate at version=5. Both apply a command. Both try to append at version=6.

Event Store enforces optimistic locking:
  INSERT INTO order_events (aggregate_id, version, ...)
  VALUES ('order-123', 6, ...)
  WHERE NOT EXISTS (SELECT 1 FROM order_events
                    WHERE aggregate_id='order-123' AND version=6)

  First insert: succeeds. Event version=6 stored.
  Second insert: CONFLICT (version=6 already exists) → raises ConcurrencyException.

  Handler: catch ConcurrencyException → reload aggregate (now at version=6) → retry command.
```

---

### 🧪 Thought Experiment

**GDPR RIGHT TO ERASURE vs. APPEND-ONLY LOG:**

Event sourcing is append-only. GDPR says users have the right to erasure of personal data. Contradiction?

**Solutions:**

1. **Crypto-shredding**: when PII is stored in events, encrypt it with a per-user key stored separately. On GDPR erasure request: delete the per-user encryption key. The events remain but the PII is now unreadable (effectively erased). Event payloads decrypt to garbage. Audit trail preserved; PII unrecoverable.

2. **Event tombstone**: append a `UserDataErasedEvent` to indicate erasure. Projections handling this event clear PII from read models. The original events remain in the event store but are flagged as erased. On replay, projectors skip PII fields from events before the tombstone.

3. **PII-separate storage**: store PII outside the event payload (in a separate "PII vault" referenced by an anonymous ID). Events reference the anonymous ID. GDPR erasure deletes from the PII vault. Events are PII-free.

---

### 🧠 Mental Model / Analogy

> Event sourcing is git for your application state. A git repository doesn't store "current file state" — it stores a series of commits (events: "added function X, fixed bug Y"). The current state of your codebase = applying all commits from the beginning. `git log` is the event log. `git checkout <sha>` = temporal query (state at a specific commit). Event sourcing applies this architecture to your domain model: the commit log IS the source of truth; the working directory (current state) is derived.

---

### 📶 Gradual Depth — Four Levels

**Level 1:** Event sourcing records every change as an event in an append-only log. Current state = replay all events. Never update state directly — only append new events.

**Level 2:** Event store structure: aggregate_id, version (monotonic). @EventSourcingHandler applies events to aggregate. Commands check invariants, apply new events. Snapshot pattern prevents O(n) replay for old aggregates. Optimistic concurrency: version conflicts retried.

**Level 3:** Event versioning (schema evolution): events change over time. Strategies: upcasting (transform old event to new format on load), multiple @EventSourcingHandler signatures (handle v1 and v2 of the same event), event migration scripts. CQRS + event sourcing: events published to Kafka → projectors update multiple read models. GDPR compliance: crypto-shredding per user.

**Level 4:** Event store implementations: EventStoreDB (Greg Young, purpose-built), Axon Server (Java), Kafka (as lightweight event store, configurable log retention), PostgreSQL (custom event table). EventStoreDB provides: optimistic concurrency, event subscriptions (projector triggers), catch-up subscriptions (replay from position), persistent subscriptions (consumer groups). Performance: event store writes are sequential appends (fast). Reads (aggregate load) are sequential scans of one aggregate's events (fast with index on aggregate_id). Complex projections (all orders for a customer) require separate read models — the event store is not efficient for cross-aggregate queries.

---

### ⚙️ How It Works (Mechanism)

**EventStoreDB Client (Java):**

```java
// Append events to stream:
public void saveEvents(String aggregateId, int expectedVersion,
                        List<DomainEvent> events) {
    String streamName = "order-" + aggregateId;
    List<EventData> eventData = events.stream()
        .map(e -> EventData.builderAsJson(e.getClass().getSimpleName(), e).build())
        .collect(Collectors.toList());

    // expectedVersion: optimistic concurrency check
    eventStoreDBClient.appendToStream(streamName,
        AppendToStreamOptions.get().expectedRevision(expectedVersion),
        eventData.iterator()).get();
}

// Load aggregate (replay events):
public OrderAggregate loadAggregate(String aggregateId) {
    String streamName = "order-" + aggregateId;
    ReadStreamOptions options = ReadStreamOptions.get()
        .fromStart()
        .forwards()
        .notResolveLinkTos();

    ReadResult result = eventStoreDBClient.readStream(streamName, options).get();

    OrderAggregate aggregate = new OrderAggregate();
    result.getEvents().forEach(resolvedEvent -> {
        DomainEvent event = deserialize(resolvedEvent);
        aggregate.apply(event);  // calls @EventSourcingHandler
    });
    return aggregate;
}
```

---

### ⚖️ Comparison Table

| Aspect           | Traditional CRUD              | Event Sourcing                                |
| ---------------- | ----------------------------- | --------------------------------------------- |
| Storage          | Current state only            | Full history                                  |
| Audit trail      | Manual (separate audit table) | Built-in (event log IS the audit trail)       |
| Temporal queries | Not supported                 | Native (replay to any point)                  |
| Complexity       | Low                           | High                                          |
| Debugging        | "What is current state?"      | "Why is state this way?"                      |
| CQRS fit         | Can use separately            | Natural pairing                               |
| Performance      | Fast reads (direct state)     | Slower loads (replay), mitigated by snapshots |

---

### ⚠️ Common Misconceptions

| Misconception                                     | Reality                                                                                                                                                                           |
| ------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Event sourcing replaces the database              | Event sourcing IS the database pattern for the write side. You still need a database — just an event store instead of a state store                                               |
| You always need event sourcing with CQRS          | CQRS and Event Sourcing are independent. You can have CQRS with a regular relational write DB. You can have Event Sourcing without CQRS (though rare)                             |
| Events are immutable = you can never fix mistakes | You can append a corrective event. "OrderTotalCorrectedEvent" appended after a bugs. The history shows: original event (incorrect) + correction event. Full audit trail preserved |

---

### 🚨 Failure Modes & Diagnosis

**Event Schema Breaking Change — Projector Crash on Old Events**

**Symptom:** Developer renames a field in OrderPlacedEvent (orderId → order_id during a
naming cleanup). On deployment, the projector tries to deserialize old events with the
new schema → NullPointerException → projector crashes → dead letter queue fills.

Cause: Event schema is not backward compatible. Old events don't have the new field name.

**Fix:** (1) Never rename event fields — add new fields, deprecate old ones.
(2) Implement upcasters: a function that transforms old event JSON to new event
format before deserialization.
(3) Use flexible deserialization (@JsonProperty alternatives, Jackson's
`FAIL_ON_UNKNOWN_PROPERTIES=false`) to handle missing new fields with defaults.
(4) Prevention: test projectors with events from the oldest version in the event store,
not just the current version (use golden event files in test suite).

---

### 🔗 Related Keywords

- `CQRS` — separates write/read models; event sourcing is the write-model implementation
- `Outbox Pattern` — reliably publishes domain events from event store to message broker
- `Saga Pattern` — sagas are implemented as sequences of domain events; event store persists saga state
- `Domain Events` — the individual unit stored in the event store
- `Append-Only Log` — the data structure underlying event stores; same concept as Kafka's topic log

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│  EVENT SOURCING: events as source of truth               │
│  State = replay all events (aggregate_id stream)         │
│  Snapshots: prevent O(n) replay for old aggregates       │
│  Optimistic lock: version conflict → reload + retry      │
│  Temporal query: replay events up to timestamp T         │
│  GDPR: crypto-shredding (encrypt PII, delete key)        │
│  Schema evolution: upcasters for old event formats       │
│  Tools: EventStoreDB, Axon, Kafka (lightweight)          │
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** An e-commerce system uses event sourcing for orders. The business wants to implement a "re-order" feature: users can re-order any past order at the current prices. Explain how event sourcing specifically enables (or simplifies) this feature compared to a traditional CRUD system that only stores the current order state.

**Q2.** A system has been running for 3 years with event sourcing. The ShoppingCart aggregate has an average of 8,000 events per cart (customers add/remove items frequently). Loading any cart takes 12 seconds (replaying 8,000 events). Design a complete snapshot strategy: (a) what triggers snapshot creation, (b) what is stored in the snapshot, (c) how does the aggregate load with a snapshot, (d) what happens if the snapshot is corrupted, and (e) what are the consistency guarantees between the snapshot and new events?
