---
layout: default
title: "Event Sourcing"
parent: "Distributed Systems"
nav_order: 616
permalink: /distributed-systems/event-sourcing/
number: "616"
category: Distributed Systems
difficulty: ★★★
depends_on: "CQRS, Domain-Driven Design"
used_by: "Axon Framework, EventStoreDB, Apache Kafka, CQRS projections"
tags: #advanced, #distributed, #architecture, #patterns, #audit-log
---

# 616 — Event Sourcing

`#advanced` `#distributed` `#architecture` `#patterns` `#audit-log`

⚡ TL;DR — **Event Sourcing** stores state changes as an immutable, append-only log of domain events instead of the current state — the current state is derived by replaying events, giving you full history, audit trail, and the ability to rebuild any projection.

| #616            | Category: Distributed Systems                                | Difficulty: ★★★ |
| :-------------- | :----------------------------------------------------------- | :-------------- |
| **Depends on:** | CQRS, Domain-Driven Design                                   |                 |
| **Used by:**    | Axon Framework, EventStoreDB, Apache Kafka, CQRS projections |                 |

---

### 📘 Textbook Definition

**Event Sourcing** is a persistence pattern where instead of storing the current state of an entity (e.g., `orders.status = 'SHIPPED'`), you store the sequence of events that led to that state (`OrderPlaced, PaymentConfirmed, OrderShipped`). The current state is derived by replaying the event sequence. The **event store** is an append-only log — events are never deleted or modified. Key properties: (1) **Immutability** — once written, events cannot change; they represent facts that occurred. (2) **Complete history** — all state transitions recorded, not just the latest. (3) **Temporal queries** — reconstruct state at any point in time ("what was the order status at 3 PM yesterday?"). (4) **Projection flexibility** — new read models built by replaying events (retroactive analytics). (5) **Auditability** — built-in compliance audit trail. Tradeoff: higher storage requirements; eventual consistency between event store and projections; snapshot optimization needed for long-lived aggregates; steep learning curve. Used in: financial systems (transaction ledger), e-commerce (order history), gaming (player action replay), DDD-heavy domains.

---

### 🟢 Simple Definition (Easy)

Your bank account: traditional approach stores "current balance: $500." Event sourcing stores: "deposit $1000, withdrawal $200, withdrawal $300 = $500." The balance is derived from the history. You can ask: "What was my balance last Tuesday?" (replay to Tuesday). You can ask: "Why is my balance $500?" (full transaction history). Can't fake or hide a transaction: the event log is append-only. This is how financial ledgers have always worked — event sourcing is the software equivalent.

---

### 🔵 Simple Definition (Elaborated)

Traditional CRUD: `UPDATE orders SET status='SHIPPED' WHERE id=123`. History gone. You know the order is shipped, but not who shipped it, what happened before, or how to rebuild reporting after a bug. Event sourcing: every state change = an event appended to the log. Report data wrong? Replay events to rebuild. New analytics needed? Replay all events into a new view. Compliance audit: "show all changes to order 123" — the event log IS the audit trail. Cost: you must replay events to get current state (mitigated by snapshots).

---

### 🔩 First Principles Explanation

**Event store, aggregate loading, snapshots, and projection replay:**

```
EVENT STORE STRUCTURE:

  Events stored in streams. Each aggregate has its own stream.

  Stream: "Order-abc-123"
  | # | Event Type              | Payload                                    | Timestamp              | Version |
  |---|-------------------------|--------------------------------------------|------------------------|---------|
  | 1 | OrderPlaced             | {userId: "u-456", items: [...], total: 75} | 2024-01-15T10:00:00Z   | 1       |
  | 2 | PaymentAuthorized       | {paymentId: "p-789", method: "VISA"}       | 2024-01-15T10:00:05Z   | 2       |
  | 3 | ItemReserved            | {itemId: "i-001", warehouseId: "w-east"}   | 2024-01-15T10:01:00Z   | 3       |
  | 4 | OrderShipped            | {trackingId: "UPS-XYZ", carrier: "UPS"}    | 2024-01-15T14:30:00Z   | 4       |
  | 5 | OrderDelivered          | {deliveredAt: "2024-01-17T09:00:00Z"}      | 2024-01-17T09:00:00Z   | 5       |

  Current state DERIVED from replaying events 1-5:
    status = DELIVERED (last status event)
    total = 75 (from event 1)
    trackingId = "UPS-XYZ" (from event 4)
    paymentId = "p-789" (from event 2)

  TEMPORAL QUERY: "What was the order status on 2024-01-15 at 12:00?"
    Replay events 1-3 (up to 10:01): status = IN_FULFILLMENT.

AGGREGATE LOADING FROM EVENT STORE:

  NAIVE (full replay every time):
    Load: read ALL events for "Order-abc-123" from beginning.
    Apply: each event to rebuild aggregate state.
    Problem: if order has 1000 events → read 1000 events per command.

  WITH SNAPSHOTS (optimization):
    Snapshot: capture aggregate state at event version N.
    Snapshot stored: {state: {status: DELIVERED, total: 75, ...}, version: 5}

    Next load:
    1. Check: is there a snapshot for "Order-abc-123"? Yes, version 5.
    2. Load snapshot (instead of events 1-5).
    3. Load only events AFTER version 5 (events 6, 7, ...).
    4. Apply new events to snapshot state.

    Snapshot trigger: every N events (e.g., every 50 events).
    Storage: snapshots stored alongside event stream.

    SNAPSHOTTING CODE (Axon Framework):
    @Aggregate
    public class OrderAggregate {
        // Axon auto-snapshots every 50 events (configurable).
        // No manual snapshot code needed.

        @EventSourcingHandler
        public void on(OrderPlacedEvent event) {
            this.orderId = event.orderId();
            this.status = OrderStatus.PLACED;
            // This method called during both normal execution AND replay.
            // MUST be side-effect free (no external calls).
        }
    }

EVENT STORE IMPLEMENTATIONS:

  1. EventStoreDB (purpose-built):
     Designed specifically for event sourcing.
     Features: stream-based storage, subscriptions (push events to consumers),
     catch-up subscriptions (replay from any position), projections.
     Client: Java SDK, .NET SDK.

  2. Apache Kafka (as event store):
     Append-only log: naturally fits event sourcing.
     BUT: Kafka deletes old messages (retention period).
     For event sourcing: configure infinite retention for event topics.
     Kafka Streams: build projections from event topics.
     Limitation: no per-aggregate stream. All events in topic (aggregate ID as key).
     Optimistic concurrency: harder (no built-in version checking per aggregate).

  3. PostgreSQL (as event store):
     events table:
       CREATE TABLE events (
           id BIGSERIAL PRIMARY KEY,
           stream_id VARCHAR NOT NULL,          -- e.g., "Order-abc-123"
           event_type VARCHAR NOT NULL,          -- e.g., "OrderPlaced"
           payload JSONB NOT NULL,
           version INT NOT NULL,
           created_at TIMESTAMPTZ DEFAULT NOW(),
           UNIQUE (stream_id, version)           -- Optimistic concurrency check
       );
     Insert event with version check:
       INSERT INTO events (stream_id, event_type, payload, version)
       VALUES ('Order-abc-123', 'OrderPlaced', '{"total": 75}', 1);
       -- If another process already inserted version 1: UNIQUE violation = optimistic lock conflict.

  4. Axon Server (Axon Framework default):
     Built-in event store for Axon Framework.
     Auto-handles: serialization, versioning, snapshotting.
     Cluster mode: HA event store.

OPTIMISTIC CONCURRENCY IN EVENT SOURCING:

  Problem: two simultaneous commands on same aggregate.
    Thread A: loads aggregate at version 3. Generates event: version 4.
    Thread B: loads aggregate at version 3. Generates event: version 4.
    Both try to write version 4: conflict!

  Solution: version-based optimistic locking.
    Thread A: INSERT INTO events WHERE version=4 AND NOT EXISTS (WHERE stream_id='Order-abc-123' AND version=4)
    Thread A: succeeds. Version 4 written.
    Thread B: fails (version 4 already exists). Must retry: reload aggregate (now at version 4), re-apply command.

  This is the event sourcing equivalent of "Optimistic Locking" in RDBMS.

UPCASTING (EVENT SCHEMA EVOLUTION):

  Problem: EventV1 {name: "John Smith"} → needs to become EventV2 {firstName: "John", lastName: "Smith"}.
  Events are IMMUTABLE: can't modify stored events.

  Solution: Upcaster — transforms old event format to new format ON READ.
  Old events: stored as V1. Upcaster: transforms to V2 when loaded by application.
  Application always sees V2 format. Historical events: still in V1 (untouched).

  Axon Framework: @Upcaster annotation handles this transparently.

  PITFALL: Never delete event fields (consumers may still rely on them).
  PATTERN: Add new fields, mark old fields as deprecated. Upcaster fills new fields from old.

PROJECTION LIFECYCLE:

  Projection: built from events; answers specific queries.

  Active projection: subscribes to event store, processes new events in real-time.

  FULL REBUILD:
    1. Need new analytics projection: "total revenue by category".
    2. New EventHandler created: handles OrderPlacedEvent → updates revenue table.
    3. Replay ALL historical OrderPlacedEvents → build complete projection from scratch.
    4. Time: depends on event volume. 10M events → may take minutes/hours.
    5. During rebuild: old version serves queries. New version ready: flip the switch.
    6. Zero historical data loss: event store is the source of truth.

  This power is impossible in traditional CRUD: historical data is gone.
```

---

### ❓ Why Does This Exist (Why Before What)

WITHOUT event sourcing:

- UPDATE overwrites history: "who changed this? when? what was the old value?" — unknowable
- Bugs in business logic: corrupted state with no way to recover
- New reporting requirement: you need historical data that no longer exists

WITH event sourcing:
→ Complete audit trail: every state change traceable to a specific event
→ Projection bugs: rebuild from immutable event log (no data loss)
→ New analytics: replay historical events into new projections retroactively

---

### 🧠 Mental Model / Analogy

> Double-entry bookkeeping ledger: accountants NEVER erase an entry. If a mistake is made: you add a correcting entry. The ledger is append-only. "Current balance" is computed by summing all entries. "Balance on Jan 1st" is computed by summing entries before Jan 1st. Tax audit: here's every transaction since day one. Event sourcing is double-entry bookkeeping for software — the event log is the ledger.

"Ledger entry" = domain event appended to event store
"Balance computed by summing entries" = aggregate state derived by replaying events
"Balance on Jan 1st" = temporal query (replay events up to a specific date)
"Correcting entry instead of erasure" = compensating events instead of deletes

---

### ⚙️ How It Works (Mechanism)

```
AGGREGATE COMMAND PROCESSING:

  1. Command received: CancelOrderCommand(orderId="abc-123")
  2. Load aggregate: read events from stream "Order-abc-123", apply each EventSourcingHandler.
     Aggregate state: {status: PLACED, total: 75, ...}
  3. Business rule check: can PLACED order be cancelled? Yes.
  4. Generate event: OrderCancelledEvent{orderId, reason, refundAmount}
  5. Write to event store (version check: optimistic lock)
  6. Event handlers: update read projections
  7. Return: success
```

---

### 🔄 How It Connects (Mini-Map)

```
Traditional CRUD (UPDATE current state — history lost)
        │
        ▼ (event sourcing: store events, derive state)
Event Sourcing ◄──── (you are here)
(immutable event log = source of truth)
        │
        ├── CQRS: event store is the write side; projections are the read side
        ├── Outbox Pattern: event sourcing already handles reliable event publishing
        └── Snapshot: optimization for long-lived aggregates (too many events to replay)
```

---

### 💻 Code Example

```java
// EventStoreDB Java client — store and load events:
EventStoreDBClient client = EventStoreDBClient.create(
    EventStoreDBClientSettings.builder().addHost("localhost", 2113).build());

// Store event:
OrderPlacedEvent event = new OrderPlacedEvent("abc-123", "u-456", items, 75.00);
EventData eventData = EventData.builderAsJson("OrderPlaced", event).build();

// Append with optimistic concurrency: expect stream at version 0 (new stream):
client.appendToStream("Order-abc-123",
    AppendToStreamOptions.get().expectedRevision(ExpectedRevision.NO_STREAM),
    eventData).get();

// Load events to rebuild aggregate:
ReadStreamOptions options = ReadStreamOptions.get().fromStart().forwards();
ReadResult result = client.readStream("Order-abc-123", options).get();

OrderAggregate aggregate = new OrderAggregate();
result.getEvents().forEach(event -> {
    // Deserialize and apply each event to rebuild state.
    aggregate.apply(deserialize(event));
});
// aggregate now has current state derived from all events.
```

---

### ⚠️ Common Misconceptions

| Misconception                                                   | Reality                                                                                                                                                                                                                                                                                                                                                   |
| --------------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Event sourcing stores events AND current state                  | Event sourcing: the event log IS the only authoritative source of truth. Current state is computed by replaying events (or from a snapshot, which itself is derived from events). No separate "current state" table that must be kept in sync. Projections are derived views (can be rebuilt), not authoritative sources                                  |
| Event sourcing is only for high-scale systems                   | Event sourcing's primary benefits are auditability and correctness (full history, projection rebuild), not scale. Any system where "why did this change?" is important benefits from event sourcing: financial systems (regulatory), healthcare records, legal case management. Scale is a secondary benefit (read models can be optimized independently) |
| Events should be as granular as possible (every field change)   | Events should be meaningful business facts, not technical state changes. "OrderShipped" is a business event. "OrderShippingStatus changed from PROCESSING to SHIPPED" is technical. "Customer address field updated to..." is too granular. Rule: events should represent things that HAPPENED in the business domain that an expert would recognize      |
| Deleting personal data (GDPR) is impossible with event sourcing | Crypto-shredding: encrypt PII data with a per-customer key. On deletion request: delete the key (data becomes unreadable = "forgotten"). Events remain in the store but PII is unrecoverable. Or: store PII outside the event store, referenced by ID in events. On deletion: delete PII store record. Events contain only the ID (no PII to delete)      |

---

### 🔥 Pitfalls in Production

**Side effects in EventSourcingHandler — double execution on replay:**

```
SCENARIO: EmailService called inside EventSourcingHandler.
  Order aggregate replayed (10 past events): emailService.sendConfirmation() called 10 times.
  Customer: receives 10 confirmation emails.

BAD: Side effects in EventSourcingHandler:
  @EventSourcingHandler
  public void on(OrderPlacedEvent event) {
      this.orderId = event.orderId();
      this.status = OrderStatus.PLACED;
      emailService.sendConfirmation(event.userId()); // WRONG: called on EVERY replay!
  }

  EventSourcingHandlers: called during:
    1. Normal execution (first time event is applied)
    2. Aggregate loading (replay to rebuild state)
    3. Snapshot creation
    Result: side effects triggered multiple times.

FIX: EventSourcingHandler ONLY updates aggregate state. Zero side effects.
  @EventSourcingHandler
  public void on(OrderPlacedEvent event) {
      this.orderId = event.orderId();   // State update only.
      this.status = OrderStatus.PLACED; // NO external calls.
  }

  // Side effects belong in @EventHandler (projection/notification side):
  @EventHandler  // Called ONCE, not during replay.
  public void on(OrderPlacedEvent event) {
      emailService.sendConfirmation(event.userId()); // Correct: called once.
      orderSummaryProjection.update(event);
  }

  RULE:
    @EventSourcingHandler: state mutation ONLY. Pure function (event → new state).
    @EventHandler (Axon) / Saga event handler: side effects, projections, notifications.

LARGE AGGREGATE — slow loading due to many events:
  Order aggregate: 5000 events over 3 years (many updates).
  Loading: replay 5000 events. Command latency: 2-3 seconds.

  FIX: Snapshot every 100 events.
  // Axon configuration:
  @Bean
  public SnapshotTriggerDefinition snapshotTrigger(Snapshotter snapshotter) {
      return new EventCountSnapshotTriggerDefinition(snapshotter, 100);
      // After 100 events: take snapshot. Next load: snapshot + at most 100 events.
  }
```

---

### 🔗 Related Keywords

- `CQRS` — event sourcing is the write side; CQRS provides the read side projections
- `Outbox Pattern` — event sourcing naturally solves the dual-write problem for events
- `Axon Framework` — Java framework for CQRS + Event Sourcing
- `EventStoreDB` — purpose-built database for event sourcing
- `Temporal Queries` — replaying events up to a timestamp to get historical state

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ KEY IDEA     │ Never update/delete state. Append events.│
│              │ Current state = replay of all events.    │
│              │ Full history, audit trail, rebuild power.│
├──────────────┼───────────────────────────────────────────┤
│ USE WHEN     │ Audit trail required (finance, legal);   │
│              │ debugging state changes matters;         │
│              │ retroactive analytics needed; DDD heavy  │
├──────────────┼───────────────────────────────────────────┤
│ AVOID WHEN   │ Simple CRUD with no history needs; team  │
│              │ new to DDD; simple read-heavy systems    │
│              │ (over-engineering); GDPR-heavy without   │
│              │ crypto-shredding plan                    │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "Bank ledger: never erase, only add.    │
│              │  Balance = sum of all entries."          │
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ CQRS → Axon Framework → EventStoreDB →  │
│              │ Snapshot → Crypto-Shredding → Upcasting  │
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** A CustomerAggregate has been live for 2 years and has accumulated 50,000 events per customer. Your system has 1 million customers = 50 billion events in the store. A new compliance requirement: "replay all customer events to audit for suspicious activity." How long will this take? Design the architecture for large-scale event replay — consider parallelization, Kafka as the backbone, and how to handle aggregate boundaries during replay.

**Q2.** You receive a GDPR "right to erasure" request from a customer. Your event store has 200 events containing the customer's email, name, and address in the event payloads. You cannot delete events (immutable log). Design the crypto-shredding implementation: how are events stored, how is the key managed, what happens when the key is deleted, and how do projections that already denormalized the PII get handled?
