---
layout: default
title: "Event Sourcing in Microservices"
parent: "Microservices"
grand_parent: "Technical Dictionary"
nav_order: 44
permalink: /microservices/event-sourcing-in-microservices/
id: MSV-044
category: Microservices
difficulty: ★★★
depends_on: CQRS in Microservices, Event-Driven Microservices, Immutability
used_by: Saga Pattern (Microservices), Distributed Transaction, Audit Log
related: CQRS in Microservices, Temporal Decoupling, Event Store
tags:
  - microservices
  - architecture
  - database
  - distributed
  - deep-dive
---

# MSV-044 - Event Sourcing in Microservices

⚡ TL;DR - Instead of storing the current state, event sourcing stores the sequence of domain events that produced that state; current state is derived by replaying the event history.

| #659            | Category: Microservices                                          | Difficulty: ★★★ |
| :-------------- | :--------------------------------------------------------------- | :-------------- |
| **Depends on:** | CQRS in Microservices, Event-Driven Microservices, Immutability  |                 |
| **Used by:**    | Saga Pattern (Microservices), Distributed Transaction, Audit Log |                 |
| **Related:**    | CQRS in Microservices, Temporal Decoupling, Event Store          |                 |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
Your order system stores current state: `orders(id, status='SHIPPED', amount=150, ...)`. An auditor asks: "What was the order status on March 3rd? What changed it? Who approved the refund on March 7th?" You have no answer - you only have the current state. A bug modified some records incorrectly - but you don't know which ones, when, or how they were before. A business analyst asks: "Show me the sequence of events that led this order to be cancelled." Impossible with current-state storage.

**THE BREAKING POINT:**
Storing only current state permanently destroys the historical record of how that state was reached. For many domains (finance, healthcare, e-commerce), this history is not optional - it's a core business requirement and often a regulatory mandate.

**THE INVENTION MOMENT:**
This is exactly why event sourcing was created - instead of overwriting state, append each change as an immutable event. Current state is derived, not stored. History is the primary record.

---

### 📘 Textbook Definition

**Event Sourcing in microservices** is an architectural pattern where a service's state changes are persisted as an ordered, immutable sequence of domain events in an _event store_, rather than storing current state in a mutable record. The current state of an entity (aggregate) is derived by replaying its event history. Each event is a factual record of what happened (`OrderPlaced`, `PaymentReceived`, `OrderShipped`). The event store is append-only. This pattern provides a complete, auditable history of all state changes and enables temporal queries ("what was the state at time T?") and event replay.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
Don't store what something is - store everything that happened to it, then derive what it is now.

**One analogy:**

> A bank account doesn't store just your balance. It stores every transaction (deposit, withdrawal, transfer) in a ledger. Your current balance is derived by summing the ledger from the beginning. The ledger is the truth; the balance is a computed view. You can always reconstruct any historical balance by replaying the ledger up to any date.

**One insight:**
Event sourcing inverts the storage model: history is primary; current state is derived. This makes history free - you never lose it because it's the only thing you store.

---

### 🔩 First Principles Explanation

**CORE INVARIANTS:**

1. The cause of a state change is as important as the change itself - but traditional state storage discards the cause.
2. State can always be recomputed from a complete event history - the inverse is not true.
3. Auditing, debugging, and analytics all fundamentally require historical data.

**DERIVED DESIGN:**
Given these invariants: store events, not state. An aggregate starts at a blank initial state; its current state is derived by applying (folding) its event sequence in order. The event store is a persistent, ordered, append-only log keyed by aggregate ID + sequence number.

**The aggregate fold:**

```
Initial state: { status: null, amount: 0 }
Apply OrderPlaced      → { status: PENDING, amount: 150 }
Apply PaymentReceived  → { status: PAID, amount: 150 }
Apply OrderShipped     → { status: SHIPPED, amount: 150 }
Apply ReturnRequested  → { status: RETURN_PENDING, amount: 150 }

Current state = result of folding all 4 events
```

**Event store schema:**

```
event_store(
  aggregate_id  VARCHAR,  -- e.g. order-123
  aggregate_type VARCHAR, -- e.g. Order
  sequence_num  BIGINT,   -- monotonically increasing per aggregate
  event_type    VARCHAR,  -- e.g. OrderPlaced
  event_data    JSONB,    -- event payload
  occurred_at   TIMESTAMP,
  PRIMARY KEY (aggregate_id, sequence_num)
)
```

**Snapshotting:**
For aggregates with long event histories (10k+ events), replaying from scratch is slow. Snapshots are periodic captures of materialised state: `snapshot(aggregate_id, sequence_num, state)`. To rebuild current state: load the latest snapshot + replay events since the snapshot's sequence_num.

**THE TRADE-OFFS:**
**Gain:** Complete, immutable audit trail; temporal queries (state at any time T); event replay for debugging; natural event-driven integration; easy projection rebuild (CQRS); eliminates the "update lost" bug class.
**Cost:** Unfamiliar mental model; query by current state requires projections (CQRS); schema evolution of past events is hard; eventual consistency; event store becomes critical infrastructure; snapshotting adds complexity.

---

### 🧪 Thought Experiment

**SETUP:**
An insurance claims system. A claim goes through: Filed → UnderReview → DocumentsRequested → DocumentsReceived → Approved → Paid. A customer complains the claim was unfairly denied (status shows DENIED). With event sourcing:

**What you can reconstruct:**

```
ClaimFiled           {amount: 50000, date: Jan 3}
UnderReviewStarted   {analyst: "Jones", date: Jan 5}
DocumentsRequested   {docs: ["MedicalReport"], date: Jan 8}
DocumentsReceived    {quality: "poor", date: Jan 15}
ClaimDenied          {reason: "Insufficient documentation",
                      analyst: "Jones", date: Jan 16}
```

You can show the exact sequence, who did what, and when. The analyst made a judgment call on Jan 16 based on poor documentation quality. You can time-travel: "What was the claim state on Jan 10?" (UnderReview, awaiting documents).

**THE INSIGHT:**
Without event sourcing, you have: `status=DENIED`. With event sourcing, you have the entire narrative. For regulated industries, the audit trail is not optional.

---

### 🧠 Mental Model / Analogy

> Version control for data (like Git for code). Every commit is an event; HEAD is the current state. You can checkout any past commit to see the state at that time. `git log` is the event history. You never lose history - you can only add new commits. Rolling back is not deleting history; it's adding a new "revert" commit.

- "Git commit" → domain event
- "HEAD" → current aggregate state
- "git checkout <hash>" → temporal query (state at event N)
- "git log" → complete event history
- "git revert" → compensating transaction
- "Repository" → event store for one aggregate

Where this analogy breaks down: Git stores file diffs; event sourcing stores business domain events (semantic, not structural). Also, event stores are append-only with no ability to amend history (unlike `git commit --amend`).

---

### 📶 Gradual Depth - Four Levels

**Level 1 - What it is (anyone can understand):**
Instead of updating a record (and losing the old value), you add a new record saying what changed. You keep all the "what changed" records forever. To find the current state, you read all the changes in order.

**Level 2 - How to use it (junior developer):**
Define domain events for every state change. Implement an `apply(event)` method on your aggregate that transitions state. Write a `reconstitute(List<Event>)` that folds all events. Persist events to the event store; never delete or update them. Publish events to the message broker for CQRS projections and integration.

**Level 3 - How it works (mid-level engineer):**
Optimistic concurrency: each command includes the expected current sequence_num. The event store insert has a unique constraint on `(aggregate_id, sequence_num)`. If two commands conflict, the second insert fails (optimistic lock) - the command is retried with the updated sequence. This is safer than pessimistic locking and avoids deadlocks. Event upcasting: when an event's schema changes (e.g., `OrderPlaced` gains a new field), old events in the store still have the old schema. Upcasters transform old events to the new schema at read time - the store is never modified.

**Level 4 - Why it was designed this way (senior/staff):**
Event sourcing resolves a fundamental tension in data management: current-state databases (CRUD) are optimised for present-state queries but destroy history; event stores are optimised for history but require projections for present-state queries. For domains where the business process (the sequence of events) is as valuable as the current state, event sourcing is the correct model. The append-only constraint is not a limitation - it's a feature: it eliminates the "lost update" problem, enables concurrent readers with no locks, and makes the database an immutable log that can be streamed anywhere. Combined with CQRS, event sourcing gives you both: an immutable event log (write side) and fast, denormalised query models (read side) built from that log.

---

### ⚙️ How It Works (Mechanism)

```
┌─────────────────────────────────────────────────────────┐
│       Event Sourcing - Write and Read Paths             │
└─────────────────────────────────────────────────────────┘

WRITE PATH (Command)
  Command ──► Command Handler
               │
               ├── Load aggregate:
               │     SELECT * FROM event_store
               │     WHERE aggregate_id = 'order-123'
               │     ORDER BY sequence_num ASC
               │     → Fold into Order object
               │
               ├── Apply business logic
               │
               ├── Produce new events
               │
               └── Append to event store:
                     INSERT INTO event_store
                     (aggregate_id, sequence_num, event_type, ...)
                     VALUES ('order-123', 5, 'OrderShipped', ...)

READ PATH (Query / CQRS)
  EventStore ──► Projection Builder ──► Read Model (e.g. order_views)
                  (consumes events)         (denormalised, queryable)

TEMPORAL QUERY
  SELECT * FROM event_store
  WHERE aggregate_id = 'order-123'
    AND occurred_at <= '2026-03-07'
  ORDER BY sequence_num ASC
  → Fold into state at that point in time
```

---

### 🔄 The Complete Picture - End-to-End Flow

**NORMAL COMMAND FLOW:**

```
[Client: PATCH /orders/123/ship]
  → [Load order-123 events from event store → fold → Order{PAID}]
  → [Validate: can ship only if PAID ✓]
  → [Append OrderShipped event (sequence_num=5)]
  → [Publish OrderShipped to Kafka]
  → [Return 200 OK]

[Projection Builder: consume OrderShipped]
  → [UPDATE order_views SET status='SHIPPED']
```

**AGGREGATE REBUILD:**

```
[New instance / cache miss]
  → [SELECT * FROM event_store WHERE id='order-123' ORDER BY seq]
  → [Fold: OrderPlaced → PaymentReceived → OrderShipped]
  → [Current state: {status: SHIPPED, amount: 150}]
```

**PROJECTION REBUILD (after bug fix):**

```
[All events in event store → replay → new order_views_v2]
  → [Scan entire event_store in sequence order]
  → [Apply fixed projection logic]
  → [order_views_v2 complete]
  → [Flip reads to order_views_v2]
```

---

### 💻 Code Example

**Example 1 - Aggregate with event application:**

```java
public class Order {
  private String id;
  private OrderStatus status;
  private BigDecimal amount;
  private List<DomainEvent> uncommittedEvents = new ArrayList<>();

  // Reconstitute from event history
  public static Order reconstitute(
      List<DomainEvent> history) {
    Order order = new Order();
    history.forEach(order::apply);
    return order;
  }

  // Handle a command: validate + produce events
  public void ship(String trackingNumber) {
    if (status != OrderStatus.PAID) {
      throw new InvalidStateTransitionException(
        "Can only ship PAID orders, current: " + status);
    }
    // Produce event - don't mutate state directly here
    applyAndRecord(new OrderShipped(id, trackingNumber,
                                    Instant.now()));
  }

  private void applyAndRecord(DomainEvent event) {
    apply(event);                        // mutate state
    uncommittedEvents.add(event);        // queue for persistence
  }

  // Pure state transition - no side effects
  private void apply(DomainEvent event) {
    if (event instanceof OrderPlaced e) {
      this.id = e.getOrderId();
      this.status = OrderStatus.PENDING;
      this.amount = e.getAmount();
    } else if (event instanceof PaymentReceived) {
      this.status = OrderStatus.PAID;
    } else if (event instanceof OrderShipped) {
      this.status = OrderStatus.SHIPPED;
    }
  }
}
```

**Example 2 - Event store repository:**

```java
@Repository
public class EventStoreRepository {

  @Autowired JdbcTemplate jdbc;

  public Order load(String aggregateId) {
    List<DomainEvent> events = jdbc.query(
      "SELECT event_type, event_data, sequence_num " +
      "FROM event_store WHERE aggregate_id = ? " +
      "ORDER BY sequence_num ASC",
      eventRowMapper, aggregateId);

    if (events.isEmpty()) {
      throw new AggregateNotFoundException(aggregateId);
    }
    return Order.reconstitute(events);
  }

  @Transactional
  public void save(Order order) {
    List<DomainEvent> events = order.getUncommittedEvents();
    for (DomainEvent event : events) {
      try {
        jdbc.update(
          "INSERT INTO event_store " +
          "(aggregate_id, sequence_num, event_type, " +
          " event_data, occurred_at) " +
          "VALUES (?, ?, ?, ?::jsonb, ?)",
          event.getAggregateId(),
          event.getSequenceNum(),
          event.getClass().getSimpleName(),
          objectMapper.writeValueAsString(event),
          event.getOccurredAt());
      } catch (DuplicateKeyException e) {
        // Optimistic concurrency conflict
        throw new ConcurrencyConflictException(
          "Conflict at seq " + event.getSequenceNum());
      }
    }
    order.clearUncommittedEvents();
  }
}
```

---

### ⚖️ Comparison Table

| Approach                       | Audit Trail         | Current State Query       | Storage       | Complexity |
| ------------------------------ | ------------------- | ------------------------- | ------------- | ---------- |
| **Event Sourcing**             | Complete, immutable | Via projection (eventual) | Grows forever | High       |
| CRUD (current state)           | None (overwritten)  | Direct, fast              | Compact       | Low        |
| CRUD + audit log table         | Partial             | Direct, fast              | Medium        | Medium     |
| Soft deletes + history columns | Partial             | Direct                    | Medium        | Medium     |

**How to choose:** Use **event sourcing** when the sequence of state changes is as important as current state (finance, healthcare, e-commerce orders, compliance). Use **CRUD** for simple reference data or operational config where history is not needed.

---

### ⚠️ Common Misconceptions

| Misconception                                          | Reality                                                                                                                    |
| ------------------------------------------------------ | -------------------------------------------------------------------------------------------------------------------------- |
| Event sourcing requires a special event store database | A standard relational DB with an append-only events table works; dedicated stores (EventStoreDB, Axon Server) add features |
| Event sourcing means you can never change past events  | Past events are immutable; schema changes are handled via upcasting at read time                                           |
| Event sourcing replaces traditional databases entirely | The event store handles writes; projections (traditional DB tables) handle read queries                                    |
| Querying current state is slow with event sourcing     | With snapshotting and CQRS projections, current state queries are as fast as any read model                                |
| Event sourcing is always the right choice              | It adds significant complexity; use it only when the business truly needs event history                                    |

---

### 🚨 Failure Modes & Diagnosis

**Event Store Growing Without Bound**

**Symptom:** Event store table consuming TBs of storage; aggregate load time increasing as event count grows.

**Root Cause:** Event sourcing is append-only by design; high-volume aggregates (e.g., an account with millions of micro-transactions) accumulate enormous event histories.

**Diagnostic Query:**

```sql
SELECT aggregate_id, count(*) as event_count
FROM event_store
GROUP BY aggregate_id
ORDER BY event_count DESC
LIMIT 20;
```

**Fix:** Implement snapshotting for high-event-count aggregates. Every N events, persist a snapshot of current state; on load, start from latest snapshot + events after it.

**Prevention:** Design snapshotting from day one for any aggregate that will have frequent mutations; set snapshot threshold at ~100–500 events.

---

**Schema Evolution - Old Events Incompatible with New Code**

**Symptom:** New code version fails to load old aggregates; `UnrecognisedFieldException` or missing required fields.

**Root Cause:** Event schema changed (field renamed, required field added) without backward compatibility handling.

**Diagnostic Command:**

```bash
# Inspect old events in the store
psql event_db -c "SELECT event_data FROM event_store
  WHERE event_type='OrderPlaced'
  AND occurred_at < '2026-01-01' LIMIT 1"
# Compare schema against current OrderPlaced class
```

**Fix:** Implement an event upcaster that transforms old schema to new at deserialization time. Never modify the raw event_data in the store.

**Prevention:** Treat event schemas as public APIs - only add optional fields; never remove or rename fields; use upcasters for breaking changes; version your event types (`OrderPlacedV2`).

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**

- `CQRS in Microservices` - event sourcing + CQRS = the canonical combination
- `Event-Driven Microservices` - events are the communication mechanism
- `Immutability` - event records are immutable by design

**Builds On This (learn these next):**

- `Saga Pattern (Microservices)` - sagas use events to coordinate; event sourcing provides the event log
- `Distributed Transaction` - event sourcing avoids distributed transactions via saga compensation
- `Audit Log` - event store is the ultimate audit log

**Alternatives / Comparisons:**

- `CRUD` - the alternative; simpler but loses history
- `Change Data Capture (CDC)` - alternative for deriving events from existing CRUD databases
- `Temporal Tables` - DB-level history; simpler but less expressive than full event sourcing

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ WHAT IT IS   │ Store state changes as immutable events;  │
│              │ derive current state by replaying history  │
├──────────────┼───────────────────────────────────────────┤
│ PROBLEM IT   │ CRUD storage destroys the history of how  │
│ SOLVES       │ state was reached                         │
├──────────────┼───────────────────────────────────────────┤
│ KEY INSIGHT  │ History is primary; current state is      │
│              │ derived - the inverse of CRUD             │
├──────────────┼───────────────────────────────────────────┤
│ USE WHEN     │ Audit requirements; temporal queries;     │
│              │ regulated domains; event replay needed    │
├──────────────┼───────────────────────────────────────────┤
│ AVOID WHEN   │ Simple CRUD; no audit needs; team unfam-  │
│              │ iliar with pattern; rapid prototyping     │
├──────────────┼───────────────────────────────────────────┤
│ TRADE-OFF    │ Complete audit trail + temporal queries   │
│              │ vs complexity + projections required      │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "Don't store what it is; store what       │
│              │  happened to it"                          │
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ CQRS → Saga Pattern → Temporal Queries    │
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** An `Order` aggregate in your event store has 50,000 events (a heavily-updated order from a B2B client with 10,000 line item changes). Loading this aggregate takes 800ms due to event replay. Design a snapshotting strategy: when to snapshot, what to store, how to load efficiently, and how to handle the race condition where a new event is appended between snapshot read and latest-event read.

**Q2.** Six months after going live, the business decides to add `discountPercentage` to `OrderPlaced` events. Existing events in the store don't have this field. New code expects it. Describe the complete schema evolution strategy: upcaster design, backward compatibility for new code reading old events, and how you'd test this before deploying.
