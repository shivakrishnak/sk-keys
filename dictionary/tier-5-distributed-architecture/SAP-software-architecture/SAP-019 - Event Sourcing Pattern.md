---
id: SAP-019
title: Event Sourcing Pattern
category: Software Architecture Patterns
tier: tier-5-distributed-architecture
folder: SAP-software-architecture
difficulty: ★★★
depends_on: SAP-018, SAP-031
used_by: SAP-018
related: SAP-018, SAP-030, SAP-031
tags:
  - architecture
  - pattern
  - advanced
  - distributed
status: complete
version: 3
layout: default
parent: "Software Architecture Patterns"
grand_parent: "Technical Dictionary"
nav_order: 19
permalink: /software-architecture/event-sourcing-pattern/
---

# SAP-019 - Event Sourcing Pattern

⚡ TL;DR - Event Sourcing stores the history of domain events as the source of truth instead of the current state, allowing any past state to be reconstructed.

| Field          | Value                     |
| -------------- | ------------------------- |
| **Depends on** | SAP-018, SAP-031          |
| **Used by**    | SAP-018                   |
| **Related**    | SAP-018, SAP-030, SAP-031 |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
A financial trading system stores only the current account balance. An audit is requested: "Show us every transaction that led to this balance." Impossible - the history was overwritten. A bug is discovered: for three months, a currency conversion was calculating incorrectly. You need to find and correct all affected accounts. Impossible - the incorrect calculations replaced correct state. Regulators demand a full immutable history. Impossible - the database stores only the latest row.

**THE BREAKING POINT:**
"Show me the state of every account as of 3pm on Tuesday" is a simple business question. Without event history, answering it requires a full backup restore. Every system that stores only current state permanently discards the information needed to understand how that state was reached.

**THE INVENTION MOMENT:**
This is exactly why Event Sourcing was created - to preserve the complete history of what happened, not just the current result, making time travel, audit, and reconstruction fundamentally possible.

**EVOLUTION:**
Event Sourcing as a named pattern was popularised by Greg Young around 2010, but the concept is ancient: double-entry bookkeeping (Luca Pacioli, 1494) is event sourcing applied to financial accounts - never modify a ledger entry, only append new ones. Martin Fowler documented it in enterprise architecture contexts. The pattern gained traction through DDD communities and is now native to frameworks like Axon (Java), EventStoreDB, and Microsoft's reference architectures for CQRS and event sourcing. The key modern challenge is event schema evolution - events are permanent, but business understanding evolves over years and decades.

---

### 📘 Textbook Definition

Event Sourcing is an architectural pattern in which, instead of storing the current state of an entity, the system stores the complete ordered sequence of domain events that led to the current state. The current state is derived by replaying events from the beginning (or from a snapshot). Events are immutable - once stored, they are never updated or deleted. The event store is the single source of truth for the system's history.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
Instead of saving "balance is £500," save "deposited £200, withdrew £100, deposited £400."

**One analogy:**

> An accountant's ledger never erases entries - every transaction is added as a new line with a date and description. To know the current balance, you sum all the lines. To know the balance on a specific date, you sum only the lines up to that date. Event Sourcing is a software ledger.

**One insight:**
In traditional persistence, you DELETE the past every time you UPDATE. In Event Sourcing, you APPEND to the past every time something changes. This makes the system's history an explicit, first-class artefact - not an afterthought recovered from backup logs.

---

### 🔩 First Principles Explanation

**CORE INVARIANTS:**

1. Events are the primary record. The current state is derived from events, not stored directly.
2. Events are immutable and append-only. They represent facts that have occurred ("OrderPlaced") and cannot be changed.
3. The system can reconstruct any past state by replaying events up to a given point in time.

**DERIVED DESIGN:**
When a command arrives (`PlaceOrderCommand`), the aggregate:

1. Loads its event history from the event store.
2. Replays events to reconstruct current state.
3. Validates the command against current state.
4. Produces new events (`OrderPlacedEvent`) - does NOT directly mutate its state.
5. The event is applied to update in-memory state.
6. The new event is appended to the event store.

```
┌──────────────────────────────────────────────────────────┐
│               EVENT SOURCING FLOW                        │
├──────────────────────────────────────────────────────────┤
│                                                          │
│  Traditional:                                            │
│  [Load row] → [Mutate state] → [UPDATE row]              │
│  History: LOST                                           │
│                                                          │
│  Event Sourcing:                                         │
│  [Load events] → [Replay → current state]                │
│               → [Apply command] → [Emit new event]       │
│               → [APPEND event to store]                  │
│  History: PRESERVED FOREVER                              │
│                                                          │
│  State at any time T = replay(all events up to T)        │
└──────────────────────────────────────────────────────────┘
```

**THE TRADE-OFFS:**
**Gain:** Complete audit trail, time travel (reconstruct any past state), multiple read projections from one event stream, natural integration with CQRS.
**Cost:** Reading current state requires replaying events (solved by snapshots). The system must handle schema evolution of events over time (hard). Adding retroactive business rules to past events is impossible by design. The learning curve is steep - developers must think in events, not in state mutations.

---

### 🧪 Thought Experiment

**SETUP:**
A bank account starts at £0. Three transactions occur: deposit £500, withdraw £100, deposit £200. Current balance: £600.

**WHAT HAPPENS WITH TRADITIONAL PERSISTENCE:**

```sql
UPDATE account SET balance = 600 WHERE id = 1;
```

The history of how we reached 600 is gone. Six months later: "Was the withdrawal on Tuesday?" "Who authorised the £500 deposit?" "What was the balance on Wednesday?" All unanswerable without external audit logs.

**WHAT HAPPENS WITH EVENT SOURCING:**

```
Event 1: MoneyDeposited { amount: 500, timestamp: Monday }
Event 2: MoneyWithdrawn { amount: 100, timestamp: Tuesday }
Event 3: MoneyDeposited { amount: 200, timestamp: Wednesday }
```

"Balance on Tuesday evening?" → Replay events 1 and 2 → £400.
"All £500+ deposits this year?" → Scan event stream.
"Who authorised event 2?" → Event contains authoriser metadata.
Every question is answerable from the event stream.

**THE INSIGHT:**
An event store is not just a persistence mechanism - it is a complete description of everything that has ever happened in the system. Every question about "what happened" is trivially answerable. Every question about "current state" is derivable.

---

### 🧠 Mental Model / Analogy

> Think of a Git repository. Git doesn't store the current file state - it stores every commit (change) ever made. The current state is the result of applying all commits. You can check out any point in history. You can understand why any line exists by looking at the commit that introduced it. Event Sourcing is Git for your business data.

- "Git commits" → Domain events (immutable, ordered, append-only)
- "git checkout HEAD" → Replay all events → current state
- "git checkout <commit-hash>" → Replay events up to T → past state
- "git log" → Event store query showing full history
- "git stash" → Snapshot (checkpoint for performance optimisation)

Where this analogy breaks down: Git allows force-pushing and rewriting history; Event Sourcing explicitly forbids this. Events, once stored, are permanent facts - analogous to a signed legal document, not a draft.

---

### 📶 Gradual Depth - Four Levels

**Level 1 - What it is (anyone can understand):**
Instead of saving the current answer, save every step that led to the answer. To get the current answer, add up all the steps. This way you never lose history.

**Level 2 - How to use it (junior developer):**
For an `Order` aggregate: instead of saving `Order { status: SHIPPED }`, save three events: `OrderPlaced`, `OrderPaid`, `OrderShipped`. When loading an order, replay these events. Each event has an `apply(event)` method that updates the in-memory state. Never call `UPDATE` on the orders table - always `INSERT` a new event.

**Level 3 - How it works (mid-level engineer):**
The aggregate's `handle(command)` method produces events; `apply(event)` methods update in-memory state. The event store persists events with: aggregate type, aggregate ID, event sequence number, event type, payload (JSON), and timestamp. Optimistic concurrency: when saving, verify that the last sequence number in the store matches the expected version - if not, a concurrent modification occurred, and the command must be retried. Snapshots are taken every N events to avoid replaying the full history on every load.

**Level 4 - Why it was designed this way (senior/staff):**
Event Sourcing originated in financial systems where auditability is a regulatory requirement, not an afterthought. Greg Young applied it to DDD as the natural persistence mechanism for aggregates - events are the things aggregates produce, so storing events is more faithful to the domain model than storing derived state. The performance challenge (loading thousands of events per aggregate) led to the snapshot pattern. At scale, event streaming systems (Kafka, EventStoreDB) provide the durable, ordered, append-only semantics the pattern requires.

---

### ⚙️ How It Works (Mechanism)

**Loading and saving an aggregate:**

```
Load:
1. Query event store:
   SELECT * FROM events
   WHERE aggregate_id = ?
   ORDER BY sequence_number ASC

2. Replay each event:
   for (Event e : events) { aggregate.apply(e); }

3. Aggregate is now at current state.

Save:
1. Aggregate.handle(command) produces newEvents[]
2. INSERT events with expected version (optimistic lock):
   INSERT INTO events
     (aggregate_id, seq, type, payload)
   VALUES (?, expectedVersion + 1, ?, ?)
3. If unique constraint on (aggregate_id, seq) fails
   → concurrent modification → retry or reject
```

**Snapshot optimisation:**

```
┌──────────────────────────────────────────────────────────┐
│              EVENT SOURCING WITH SNAPSHOTS               │
├──────────────────────────────────────────────────────────┤
│                                                          │
│  Without snapshots:                                      │
│  Load 10,000 events → replay all → current state        │
│  (slow for old aggregates)                               │
│                                                          │
│  With snapshots (every 100 events):                      │
│  Load snapshot at event 9,900                            │
│   → apply events 9,901 → 10,000                         │
│   → current state (replay only 100 events)               │
│                                                          │
│  Snapshot = { aggregate state at version N }             │
│  Always reconstructable from events if deleted           │
└──────────────────────────────────────────────────────────┘
```

---

### 🔄 The Complete Picture - End-to-End Flow

**NORMAL FLOW:**

```
POST /orders (PlaceOrderCommand)
  → Load Order events from event store
  → Replay events → current Order state
  → Order.handle(PlaceOrderCommand)
  → Validates rules → produces OrderPlacedEvent
  → Append event to store  ← YOU ARE HERE
  → Publish event to read model projectors
  → CQRS read model updated
  → GET /orders/{id} → Query hits read model
```

**FAILURE PATH:**

```
Concurrent command on same aggregate:
  → INSERT fails (seq conflict)
  → Retry: reload events, replay, re-apply command
  → If retry limit exceeded → return 409 Conflict

Event store unavailable:
  → Command handler fails
  → No state change (event not stored = didn't happen)
  → Client retries safely (no partial state)
```

**WHAT CHANGES AT SCALE:**
At 100M+ events, loading an aggregate requires a snapshot strategy - rebuild from the most recent snapshot plus delta. At 1B+ events, the event store itself (EventStoreDB, Kafka with compaction) becomes a scaling concern. Read projections scale independently from the event store, processing the same stream in parallel.

---

### 💻 Code Example

**Example 1 - Aggregate with event sourcing:**

```java
public class Order {
    private OrderId id;
    private OrderStatus status;
    private List<OrderItem> items;
    private int version = 0;

    // Produces event - does NOT directly mutate state
    public OrderPlacedEvent handle(
            PlaceOrderCommand cmd) {
        if (status != null) {
            throw new OrderAlreadyExistsException(id);
        }
        // Return event - caller appends to store
        return new OrderPlacedEvent(
            cmd.orderId(), cmd.customerId(),
            cmd.items(), Instant.now()
        );
    }

    // Apply method reconstructs state from event
    public void apply(OrderPlacedEvent event) {
        this.id = event.orderId();
        this.status = OrderStatus.PLACED;
        this.items = event.items();
        this.version++;
    }

    // Static factory: rebuild from event history
    public static Order reconstitute(
            List<DomainEvent> events) {
        Order order = new Order();
        events.forEach(e -> {
            if (e instanceof OrderPlacedEvent placed)
                order.apply(placed);
            else if (e instanceof OrderShippedEvent shipped)
                order.apply(shipped);
            // ... other event types
        });
        return order;
    }
}
```

**Example 2 - Event store repository:**

```java
@Repository
@RequiredArgsConstructor
public class EventStoreOrderRepository {
    private final JdbcEventStore store;

    public Order load(OrderId id) {
        List<DomainEvent> events =
            store.loadEvents(id.value(), "Order");
        if (events.isEmpty()) {
            throw new OrderNotFoundException(id);
        }
        return Order.reconstitute(events);
    }

    public void save(Order order,
                     List<DomainEvent> newEvents,
                     int expectedVersion) {
        // Optimistic concurrency check built into store
        store.appendEvents(
            order.id().value(), "Order",
            newEvents, expectedVersion
        );
        // Events published to bus after successful save
    }
}
```

**Example 3 - Time travel query:**

```java
// Reconstruct order state at specific point in time
public Order getOrderAt(OrderId id, Instant pointInTime) {
    List<DomainEvent> eventsUpToTime =
        store.loadEvents(id.value(), "Order")
             .stream()
             .filter(e -> !e.occurredAt()
                            .isAfter(pointInTime))
             .toList();
    return Order.reconstitute(eventsUpToTime);
}
```

---

### ⚖️ Comparison Table

| Approach            | History    | Time travel | Audit    | Complexity | Best For                                |
| ------------------- | ---------- | ----------- | -------- | ---------- | --------------------------------------- |
| **Event Sourcing**  | Complete   | Yes (full)  | Built-in | Very high  | Finance, legal, audit-heavy domains     |
| CRUD with audit log | Partial    | No          | Limited  | Medium     | Most business applications              |
| Temporal tables     | State only | Limited     | Limited  | Medium     | Regulatory data without event semantics |
| Change Data Capture | Complete   | Partial     | Yes      | Medium     | Integration and sync use cases          |

**How to choose:** Use Event Sourcing when the history of changes is as important as the current state, when you need time-travel debugging, or when you're building financial/audit systems. Avoid Event Sourcing for simple CRUD - the conceptual and operational overhead is substantial.

---

### ⚠️ Common Misconceptions

| Misconception                                           | Reality                                                                                                                                |
| ------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------- |
| Event sourcing requires Kafka                           | Kafka is one implementation; a simple SQL event table with append-only writes works for many systems                                   |
| Events can be updated to fix bugs                       | Events are immutable facts. Fix bugs by appending compensating events, not by modifying existing ones                                  |
| Event sourcing and CQRS are the same thing              | They complement each other naturally but are separate patterns; CQRS addresses read/write models, Event Sourcing addresses persistence |
| Rebuilding state from events is too slow for production | Snapshots solve this; most systems use snapshot + recent events, not full replay on every load                                         |
| Event schemas never need to change                      | Schema evolution is the hardest part of Event Sourcing - events must support versioning and upcasting from the first day               |

---

### 🚨 Failure Modes & Diagnosis

**Event schema migration (old events with old schema)**

**Symptom:** After a field rename or type change, replaying old events throws deserialization exceptions. Old aggregates cannot be loaded.

**Root Cause:** Event schema changed without a migration strategy. Old events in the store have the old field names.

**Diagnostic Command / Tool:**

```bash
# Find events that fail to deserialise
SELECT aggregate_id, sequence_number, event_type, payload
FROM events
WHERE event_type = 'OrderPlacedEvent'
  AND payload::jsonb ->> 'oldFieldName' IS NOT NULL
LIMIT 10;
```

**Fix:** Implement upcasters - transformation functions that convert old event versions to the current schema before applying them to the aggregate. Register upcasters in the event store deserialization pipeline.

**Prevention:** Version every event schema from day one. Use an `EventVersion` field. Never rename or remove event fields - add new fields alongside old ones.

---

**Snapshot staleness after bug fix**

**Symptom:** After fixing an event application bug, existing snapshots contain the incorrect state. Aggregates loaded from snapshots return wrong state.

**Root Cause:** Snapshots store derived state; when the derivation logic (apply methods) changes, old snapshots are stale.

**Diagnostic Command / Tool:**

```bash
# Delete all snapshots for affected aggregate type
DELETE FROM snapshots
WHERE aggregate_type = 'Order'
  AND created_at < '2024-01-15'; -- date of bug fix
# System will rebuild from events on next load
```

**Fix:** Delete snapshots after any `apply()` method bug fix. Add snapshot version tracking - invalidate snapshots when aggregate version changes.

**Prevention:** Include a snapshot schema version. When aggregate code changes, bump the version and auto-invalidate old snapshots.

---

**Unbounded aggregate growth**

**Symptom:** Loading a specific aggregate takes 5+ seconds. The event table has millions of rows for one aggregate ID.

**Root Cause:** A high-frequency aggregate (e.g., a global counter) accumulates too many events before a snapshot.

**Diagnostic Command / Tool:**

```sql
SELECT aggregate_id, COUNT(*) as event_count
FROM events
GROUP BY aggregate_id
ORDER BY event_count DESC
LIMIT 10;
```

**Fix:** Reconsider the aggregate design - very high-frequency state changes may not suit event sourcing. Use frequent snapshots (every 50 events instead of 100). Consider a different aggregate boundary.

**Prevention:** Aggregates should not accumulate more than a few hundred events between snapshots. High-frequency counters are a design smell in event-sourced systems.

---

### � Transferable Wisdom

**Reusable Engineering Principle:** Treating a log of immutable events as the primary source of truth - with current state as a derived materialisation - provides complete history, reversibility, and the ability to rebuild any past state. The log is the truth; the database is a cache.

**Where else this pattern appears:**

- **Database WAL (Write-Ahead Log):** the transaction log IS the database's event store; the data files are the materialised read model that can always be rebuilt from the WAL - database engineers have used event sourcing at the storage engine level for decades.
- **Git version control:** the commit history is an event store; the working tree is the materialised current state; any past state can be reconstructed by replaying commits to a given point - `git checkout` is event replay.
- **Accounting ledger:** no journal entry is ever modified or deleted; debits and credits are appended entries; the account balance is the materialised projection of all entries - the original event sourcing system, predating software by 500 years.

---

### 💡 The Surprising Truth

Event Sourcing's hardest long-term problem is not event replay performance (solved with snapshots) or eventual consistency (managed with projectors) - it is event schema evolution. Events are permanent by design; you cannot delete or change them. When a domain model changes (a field is renamed, a new required field is added, an event is split into two), all existing events still use the old schema. Every projector and consumer must handle all historical schema versions forever. This schema evolution tax compounds over years and decades, and it is the primary reason experienced teams approach Event Sourcing with caution.

---

### �🔗 Related Keywords

**Prerequisites (understand these first):**

- SAP-018 - CQRS Pattern (the most common architectural companion; event sourcing provides the write-side implementation, CQRS provides the read-side separation)
- SAP-031 - Domain Events (events are the primitive unit of event sourcing; understanding domain events is prerequisite)

**Builds On This (learn these next):**

- SAP-018 - CQRS Pattern (learn how event sourcing and CQRS combine: events are sourced on the write side, projected into read models on the read side)
- SAP-030 - Aggregate Root (aggregates are the consistency boundary within which events are ordered and applied atomically)

**Alternatives / Comparisons:**

- CRUD persistence - simpler; stores only current state; loses history entirely; correct for the majority of applications
- Temporal tables (SQL Server, PostgreSQL) - database-level state history without domain event semantics; simpler but no business event model
- Change Data Capture - captures database-level changes as integration events, not domain events; a different trade-off

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ WHAT IT IS   │ Store events (what happened), not state   │
│              │ (what is). Derive state by replaying.     │
├──────────────┼───────────────────────────────────────────┤
│ PROBLEM IT   │ Traditional persistence destroys history  │
│ SOLVES       │ on every UPDATE                           │
├──────────────┼───────────────────────────────────────────┤
│ KEY INSIGHT  │ The event stream is the system's memory - │
│              │ state is a cache that can always be       │
│              │ rebuilt from events                       │
├──────────────┼───────────────────────────────────────────┤
│ USE WHEN     │ Audit requirements; time-travel needed;   │
│              │ financial/legal domains; CQRS projections │
├──────────────┼───────────────────────────────────────────┤
│ AVOID WHEN   │ Simple CRUD; no need for history; team    │
│              │ lacks Event Sourcing experience           │
├──────────────┼───────────────────────────────────────────┤
│ TRADE-OFF    │ Complete history + time travel vs event   │
│              │ schema evolution complexity               │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "The event log is the truth;              │
│              │  the database is just a cache"            │
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ CQRS → Saga Pattern → Outbox Pattern     │
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** A production Event Sourcing system discovers that for the past 90 days, a `MoneyWithdrawnEvent` was applied with the wrong sign - it accidentally increased balances instead of decreasing them. The event store contains 50 million events. You cannot modify existing events. Trace step-by-step the complete recovery process: which events are compensating vs correcting, how you rebuild projections, how you handle the gap between corrected and stale read models during the migration, and what the user-visible impact is.

*Hint:* Research "compensating events" (the Event Sourcing equivalent of a correction journal entry) and "event upcasting" in Axon Framework - specifically the difference between appending `MoneyWithdrawnCorrectedEvent` records (compensating: balance += correction_amount) versus replaying all events with a fixed projector. Also research the "blue-green projection" migration pattern where a corrected read model is built in parallel before switching traffic.

**Q2.** A domain expert argues: "Our loan approval process has 47 state transitions over the loan lifecycle. Each transition needs to be audited and legally defensible. But loading a loan aggregate might require replaying 200 events." How does the snapshot strategy interact with audit completeness requirements? If you snapshot at every 50 events, what happens to your legal audit trail?

*Hint:* Research how EventStoreDB and Axon Framework implement snapshots as auxiliary projections that NEVER delete events - the snapshot is stored alongside the event stream, not replacing it. The legal audit trail is intact because all original events are preserved. Look at the difference between a "snapshot" (performance optimisation that supplements the event log) versus "state overwrite" (which would destroy audit completeness).

**Q3.** A new service needs to join an existing Event Sourcing ecosystem and subscribe to domain events. The event store has 3 years of history. The new service's read model requires all historical events to initialise. Replaying 3 years of events takes 72 hours. How do you design the onboarding process for new event consumers to prevent "cold start" becoming a scaling bottleneck as the system grows?

*Hint:* Research "catch-up subscriptions" and "projection bootstrapping" strategies in EventStoreDB - specifically the pattern of taking a database snapshot of the current materialised state from an existing projector to bootstrap the new service (a "read model snapshot export"), combined with a delta replay for events after the snapshot date. Also look at event partitioning strategies that enable parallel replay across multiple worker threads.
