---
id: DST-065
title: "Event Sourcing"
category: Distributed Systems
tier: tier-5-distributed-architecture
folder: DST-distributed-systems
difficulty: ★★★
depends_on: DST-061
related: DST-061, DST-063, DST-056
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
nav_order: 59
permalink: /distributed-systems/event-sourcing/
---

# DST-062 - Event Sourcing

⚡ TL;DR - Event Sourcing stores the complete history of state changes as an immutable sequence of domain events, rather than storing only current state — enabling full audit trails, temporal queries, and deterministic state reconstruction at any point in time.

| Metadata        |                           |     |
| :-------------- | :------------------------ | :-- |
| **Depends on:** | DST-061                   |     |
| **Related:**    | DST-061, DST-063, DST-056 |     |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
A banking system stores current account balance: `UPDATE accounts SET balance=5000 WHERE id=123`. A customer disputes a transaction: "I never authorized that $200 withdrawal." The database shows balance=5000 — but how did it get there? The full transaction history is either in separate logs (scattered, hard to query) or in a transactions table (added as an afterthought, not the authoritative source of truth). To answer "what was the balance at 3:47 PM on Tuesday?" — you must reconstruct it from log files, which may not be complete. The state (current balance) is all that's persisted; the history (how it got there) is an afterthought.

**THE BREAKING POINT:**
CRUD systems discard history. An `UPDATE` overwrites the previous state — the "before" is gone. Audit logging is added as an afterthought (triggers, interceptors) but is not the authoritative source. When the audit log and the actual state diverge (which happens during bugs, migrations, or manual fixes): which is the truth? If you store only current state: you cannot answer temporal queries ("what was the state at T?"), cannot reconstruct how a bug affected state, cannot replay history with corrected business logic.

**THE INVENTION MOMENT:**
Martin Fowler described Event Sourcing (2005) as an architectural pattern for storing domain events as the primary store. Greg Young applied it to DDD aggregates and combined it with CQRS (2010). The insight: the accounting ledger has used this model for centuries — every transaction is recorded, never deleted, and the current balance is derived by summing the ledger. Event Sourcing applies the accounting ledger model to software systems.

**EVOLUTION:**
2005: Martin Fowler — Event Sourcing pattern described. 2010: Greg Young — CQRS + Event Sourcing combination. 2011: Event Store (eventstore.com) — purpose-built event store database. 2013: Axon Framework — Java CQRS + ES framework. 2014+: Event Sourcing in microservices. 2016+: Kafka as event store (append-only log — natural Event Sourcing storage). 2018+: Event Sourcing mainstream in DDD communities. Today: well-understood pattern; recognized as complex and not universally appropriate — apply to bounded contexts that need full audit history, temporal queries, or CQRS read model rebuilding.

---

### 📘 Textbook Definition

**Event Sourcing** is an architectural pattern in which the system's state is not stored as a snapshot of current values but as an append-only sequence of domain events. Each event represents a fact that occurred: `OrderPlaced`, `PaymentProcessed`, `ItemShipped`. Current state is derived by replaying the event log from the beginning (or from a snapshot). **Core properties:** (1) **Immutability:** events are never modified or deleted once written. An event log is append-only. (2) **Completeness:** the event log is the authoritative source of truth — not any derived state. (3) **Replayability:** any state at any point in time can be reconstructed by replaying events up to that time. (4) **Audit trail:** every state change is recorded with who caused it, when, and why. **Snapshots:** replaying the entire event log from the beginning is expensive for aggregates with thousands of events. Snapshots: periodically capture the current state, store as an optimization. Replay from the most recent snapshot + events after it. **Relationship to CQRS (DST-061):** Event Sourcing is the write-side storage mechanism; CQRS provides the read model built from events. They are complementary but independent.

---

### ⏱️ Understand It in 30 Seconds

**One line:** Store every change as an immutable event, not just the current state — current state is always derivable from the event history.

> Event Sourcing is like a bank's transaction ledger. The bank doesn't just store your current balance ($5,000). It stores every transaction: deposit $1,000, withdrawal $200, fee $5, deposit $4,205. The current balance is derived by summing the ledger. Crucially: the bank can reconstruct your balance at any historical date, identify every transaction, and answer any audit question — because no information was ever overwritten or deleted.

**One insight:** In CRUD systems: state is truth, events are derived (logs). In Event Sourcing: events are truth, state is derived (projections). This inversion makes history a first-class concern, not an afterthought.

---

### 🔩 First Principles Explanation

**CORE INVARIANTS:**

1. **Events are immutable facts.** `OrderPlaced{orderId: 123, items: [...], at: 2024-01-15T10:00}` is a fact — it happened. Events are never updated or deleted. They represent what occurred, not the desired current state. Attempting to "update" an event is a domain model error — model the correction as a new event (`OrderCorrected`).
2. **State is computed, not stored (primarily).** Current state of an aggregate = apply(events[0..N]). Storing state is an optimization (snapshot) not the source of truth. If the state and the event log disagree: the event log is correct.
3. **Event log is append-only.** The event store accepts only `append(event)` operations. No `update`, no `delete`. This is the structural guarantee of immutability. Kafka (append-only topic) and EventStore (append-only streams) both enforce this.
4. **Snapshotting is optional optimization.** Replaying 10,000 events per request is too slow. Snapshot after every N events: `Snapshot{aggregateId, state, version}`. Replay from snapshot + events since snapshot. The snapshot can be discarded and rebuilt — it is not the authoritative source.

**DERIVED DESIGN:**

```
Event Store (append-only):
  stream: order-123
    [OrderPlaced v1] → [PaymentProcessed v2]
    → [ItemShipped v3] → [OrderCompleted v4]

Load aggregate:
  1. Load all events for order-123
  2. Apply each in order:
     state = OrderPlaced.apply(emptyState)
     state = PaymentProcessed.apply(state)
     state = ItemShipped.apply(state)
     state = OrderCompleted.apply(state)
  3. Return final state

Append event:
  1. Load current aggregate state
  2. Validate command against state
  3. Produce new event(s)
  4. Append to event store (with optimistic locking)
```

**THE TRADE-OFFS:**
**Gain:** Complete audit trail. Temporal queries ("state at T"). Rebuild read models (replay events with corrected projection code). Event-driven architecture naturally (events are already published). Root cause analysis (replay events to find when a bug was introduced).
**Cost:** Eventual consistency (current state requires replaying events). Schema evolution complexity (old events with old schema must be readable forever). Query complexity (finding "all orders with status=PENDING" requires a read model projection — cannot query the event store directly). Snapshotting infrastructure. Steep learning curve.

**ESSENTIAL vs ACCIDENTAL COMPLEXITY:**
**Essential:** Schema evolution is inherently complex in Event Sourcing. Old events stored 5 years ago have old schemas. New code must handle both old and new event schemas. This complexity exists regardless of implementation.
**Accidental:** EventStore proprietary query language. Axon Framework's complex annotation model. Event versioning strategies (upcasters). These are implementation details.

---

### 🧪 Thought Experiment

**SETUP:** Financial system. A bug in the payment processing logic caused incorrect fee calculations for 6 months. Detect it. Determine which accounts were affected. Recalculate correct balances.

**WITHOUT EVENT SOURCING:**

- Current database: shows current (wrong) balances.
- Transaction logs: may be incomplete, in a different format, not the authoritative source.
- Fix: write a complex migration script to reconstruct what "should have happened" vs "what happened." Requires assumptions, manual review, and risk of further errors.
- Determine affected accounts: examine application logs from the past 6 months. Logs may be incomplete (rotated, deleted). Timeline: weeks. Confidence: low.

**WITH EVENT SOURCING:**

- Event store: has every `PaymentProcessedEvent` for all accounts for 6 months.
- Fix the fee calculation bug in the projection code.
- Rebuild all account balance projections by replaying all events with corrected code.
- All accounts: correct balances derived from the correct application of the fee calculation to historical events.
- Determine affected accounts: query events where `feeAmount != correctFeeAmount(event)` — automated, complete.
- Timeline: rebuild projection (hours for large event log). Confidence: complete.

**THE INSIGHT:** Event Sourcing treats historical events as first-class data, making business logic bugs fixable retroactively by replaying events with corrected logic. CRUD systems treat history as optional — bugs that corrupted state cannot be corrected without assumptions.

---

### 🧠 Mental Model / Analogy

> Event Sourcing is like the source control (Git) for your data. Git stores every commit (event) — not just the current file state. You can check out any version of the codebase at any point in time. You can see who changed what and when. You can branch (create projections). You can rebase (replay events with corrected logic). The current file state is derived from the commit history — not stored independently. If the working directory is corrupted, you can restore it from the commit history.

**Mapping:**

- **Git commit** → domain event (immutable fact, timestamped, who caused it)
- **Git repository (all commits)** → event store (all events for all aggregates)
- **Checked-out working tree** → current aggregate state (derived, rebuildable)
- **`git checkout <commit-hash>`** → replay events up to T (temporal query)
- **Branch** → read model projection (derived view of event history)
- **Squash/force-push (forbidden)** → deleting events (forbidden — events are immutable)

Where this analogy breaks down: Git events (commits) contain diffs (what changed). Domain events should contain the full business fact, not diffs (`OrderPlaced` with all order details, not `changed field X from A to B`). Git commits reference file paths; domain events reference aggregate IDs and domain concepts. The structural analogy is strong; the content of events differs.

---

### 📶 Gradual Depth - Four Levels

**Level 1 - What it is (anyone can understand):**
Normally, when data changes, the old value is overwritten. Event Sourcing never overwrites anything — it adds a record for every change. "Balance was $1000. User deposited $500. Balance is now $1500." Both the $1000 and the $500 deposit are recorded. To find the balance: sum all the deposits and withdrawals. You can find the balance at any point in history because all changes are preserved.

**Level 2 - How to use it (junior developer):**
With Axon Framework:

```java
@Aggregate
public class OrderAggregate {
    @AggregateIdentifier
    private String orderId;
    private OrderStatus status;

    @CommandHandler
    public OrderAggregate(PlaceOrderCommand cmd) {
        // Emit event — Axon stores it
        apply(new OrderPlacedEvent(cmd.getOrderId(),
            cmd.getItems(), cmd.getTotal()));
    }

    @EventSourcingHandler
    public void on(OrderPlacedEvent event) {
        // Rebuild state from event
        this.orderId = event.getOrderId();
        this.status = OrderStatus.PLACED;
    }

    @CommandHandler
    public void handle(ShipOrderCommand cmd) {
        if (status != OrderStatus.PAID)
            throw new IllegalStateException("Not paid");
        apply(new OrderShippedEvent(orderId,
            cmd.getTrackingNumber()));
    }

    @EventSourcingHandler
    public void on(OrderShippedEvent event) {
        this.status = OrderStatus.SHIPPED;
    }
}
```

**Level 3 - How it works (mid-level engineer):**
The event store is an append-only log, organized by aggregate stream. An aggregate stream is identified by aggregate type + ID (e.g., `Order-123`). When a command is processed: (1) Load aggregate — read all events from stream `Order-123`, apply them in order to reconstruct current state. (2) Validate command. (3) Produce new event(s). (4) Append to stream with optimistic concurrency control: `appendToStream(streamId, events, expectedVersion)`. If another writer appended to the same stream concurrently → version mismatch → conflict → retry. Optimistic locking prevents lost updates. The event store guarantees: ordered, atomic append per stream. Across streams: no global ordering guarantee (this is the distributed systems CAP trade-off — global ordering would require coordination).

**Level 4 - Why it was designed this way (senior/staff):**
Event Sourcing's design choice — events as source of truth, state as derived — is motivated by the recognition that business domain knowledge is encoded in the HISTORY of changes, not just the current state. An accountant doesn't care only about your current balance; they care about every transaction that produced it (audit). A fraud detection system cares about the pattern of transactions over time (temporal query). An SRE debugging a production incident cares about the sequence of events that led to the failure (root cause). CRUD systems discard this information. The cost of Event Sourcing (schema evolution, snapshot management, projection infrastructure) is the price of keeping this information as a first-class concern. The decision to use Event Sourcing should be driven by: "Does this bounded context genuinely need audit trails, temporal queries, or projection replay?" If the answer is no for a simple CRUD use case: Event Sourcing adds complexity with no benefit.

**Expert Thinking Cues:**

- "Aggregate load time growing as event log grows" → Snapshot needed. After N events (100-500 typically), snapshot the aggregate state. Load = snapshot + events since snapshot. EventStore: use Snapshots API. Axon: configure `@Aggregate(snapshotTriggerDefinition = "...")`. Monitor aggregate load time as the primary metric for snapshot threshold.
- "Old event cannot be deserialized — schema changed" → Upcaster: a function that transforms an old event schema to the new schema at deserialization time. EventStore and Axon support upcaster chains. Never delete old events; write an upcaster instead. Schema evolution in Event Sourcing: additive changes are safe (new optional field). Removing or renaming fields: requires upcaster.
- "How to query 'all orders with status PENDING'?" → You cannot query the event store directly for aggregate state (it's optimized for appending and reading streams by ID). Build a read model (CQRS projection) that maintains a table of order statuses, updated by consuming events. This is why CQRS + Event Sourcing is the natural combination: Event Sourcing provides the event log; CQRS projections provide queryable views.

---

### ⚙️ How It Works (Mechanism)

**Event store append + load:**

```
EventStore (ordered, append-only)
stream: Order-123
  pos=1: OrderPlaced{items=[...], total=150}
  pos=2: PaymentProcessed{amount=150}
  pos=3: ItemShipped{tracking=XYZ}
  pos=4: OrderCompleted{}

Load aggregate:
  events = store.readStream("Order-123", from=0)
  state = {}
  for event in events:
    state = applyEvent(state, event)
  return state (fully reconstructed)

Append:
  store.appendToStream("Order-123", [new_event],
    expectedVersion=4)
  → if store has version=4: success (append at 5)
  → if store has version=5: conflict (concurrent write)
```

**Snapshot optimization:**

```
Every 100 events:
  snapshot = serializeState(state)
  snapshotStore.save("Order-123", snapshot, version=100)

Load with snapshot:
  snapshot = snapshotStore.load("Order-123")
  events = store.readStream("Order-123", from=snapshot.version)
  state = applyAll(events, startFrom=snapshot.state)
  [only reads events since snapshot]
```

---

### 🔄 The Complete Picture - End-to-End Flow

**COMMAND → EVENT → PROJECTION:**

```
Client  API  CmdHandler  EventStore  EventBus  Projection  ReadStore
  │     │       │            │          │          │           │
  │─cmd─▶       │            │          │          │           │
  │      │─dispatch▶          │          │          │           │
  │      │       │ load stream│          │          │           │
  │      │       │─────────────▶         │          │           │
  │      │       │◀─events────│          │          │           │
  │      │       │ apply events          │          │           │
  │      │       │ validate cmd          │          │           │
  │      │       │ produce event         │          │           │
  │      │       │─append──────▶         │          │           │
  │      │       │─publish──────────────▶│          │           │
  │◀─202─│       │            │     ← YOU ARE HERE  │           │
  │      │       │            │          │─consume──▶           │
  │      │       │            │          │          │─upsert────▶│
```

**WHAT CHANGES AT SCALE:**
At scale (millions of aggregates, billions of events): stream reads become expensive even with snapshots. Shard the event store by aggregate ID (Kafka partitioning, EventStore sharding). Read model projections must process events at high throughput (Kafka consumer groups for parallel projection). Event log retention: events stored forever (or until legal retention period). Kafka log compaction is incompatible with Event Sourcing (compaction can remove earlier events). Use Kafka with `retention.ms=-1` (indefinite) for event sourcing topics.

---

### 💻 Code Example

**BAD - CRUD: state-only storage, no event history:**

```java
// BAD: UPDATE overwrites previous state
// No audit trail
// Cannot answer "what was balance at T?"
// Bug in fee calculation: corrupts state permanently

@Repository
public class AccountRepository {
    public void debit(String accountId, BigDecimal amount) {
        // Previous balance is gone after this update
        // No record of WHO, WHEN, WHY this change occurred
        jdbcTemplate.update(
            "UPDATE accounts SET balance = balance - ? "
            + "WHERE id = ?",
            amount, accountId);
    }
}
```

**GOOD - Event Sourcing: append domain events:**

```java
// GOOD: every state change is a domain event
// Full audit trail preserved
// State reconstructable at any point in time

public class Account {
    private String id;
    private BigDecimal balance = BigDecimal.ZERO;
    private List<DomainEvent> events = new ArrayList<>();

    // Command handler: validate + produce event
    public void debit(BigDecimal amount, String reason) {
        if (balance.compareTo(amount) < 0)
            throw new InsufficientFundsException(id, amount);
        // Produce event — not state mutation yet
        applyAndRecord(new AccountDebited(id, amount,
            reason, Instant.now()));
    }

    // Apply event — state mutation from event
    private void applyAndRecord(DomainEvent event) {
        apply(event);           // update state
        events.add(event);      // track for persistence
    }

    // EventSourcingHandler: rebuild state from event
    public void apply(AccountDebited event) {
        this.balance = balance.subtract(event.amount());
    }

    // Reconstruct from event history
    public static Account reconstitute(
        List<DomainEvent> history) {
        Account account = new Account();
        for (DomainEvent e : history) account.apply(e);
        return account;
    }
}

// Repository: append events, not update state
public class EventSourcedAccountRepository {

    public Account load(String accountId) {
        List<DomainEvent> events = eventStore
            .readStream("account-" + accountId);
        return Account.reconstitute(events);
    }

    public void save(Account account) {
        eventStore.appendToStream(
            "account-" + account.getId(),
            account.getUncommittedEvents(),
            account.getExpectedVersion()); // optimistic lock
    }
}
```

---

### ⚖️ Comparison Table

|                     | Event Sourcing          | Traditional CRUD          | Change Data Capture          |
| :------------------ | :---------------------- | :------------------------ | :--------------------------- |
| Source of truth     | Append-only event log   | Current state (table row) | Current state (+ CDC stream) |
| Audit trail         | Complete (all events)   | None (unless added)       | Partial (DB operation level) |
| Temporal queries    | Native (replay to T)    | Manual reconstruction     | Limited                      |
| Rebuild read model  | Yes (replay events)     | No                        | Partial                      |
| Schema evolution    | Complex (upcasters)     | Simple                    | Simple                       |
| Query current state | Via projection/snapshot | Direct SQL                | Direct SQL                   |
| Complexity          | Very high               | Low                       | Medium                       |

---

### ⚠️ Common Misconceptions

| Misconception                                                     | Reality                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                  |
| :---------------------------------------------------------------- | :------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| "Event Sourcing means you never store current state"              | Snapshots store current state as an optimization. The difference: the snapshot is NOT the source of truth — it is derived from events and can be discarded and rebuilt. CRUD stores current state as the authoritative value (the "truth"). Event Sourcing stores events as the authoritative truth; current state is a cache of the derived state.                                                                                                                                                      |
| "Event Sourcing requires Kafka"                                   | Any append-only storage works as an event store: EventStore (dedicated event database), PostgreSQL (append-only table — `INSERT` only, no `UPDATE`/`DELETE`), Kafka (append-only log). Kafka is optimized for streaming events to consumers (projection pipeline). PostgreSQL works for small-to-medium scale and simpler operations. EventStore provides native event sourcing features (stream APIs, snapshots, subscriptions). Choice depends on volume, consistency needs, and ecosystem.            |
| "Events should be stored as minimal deltas (only changed fields)" | Events should be stored as rich business facts, not minimal diffs. `AccountDebited{accountId, amount, reason, by, at}` — not `FieldChanged{field: "balance", from: "1000", to: "800"}`. Rich events: self-describing, human-readable, can drive projections without additional context. Minimal diffs: hard to interpret without the full aggregate state for context, brittle when field names change. Store the business fact completely; don't optimize for storage size at the expense of semantics. |
| "Event Sourcing provides strong consistency"                      | Event Sourcing with CQRS provides eventual consistency between the command side (event store) and query side (read model projections). The event store itself can provide strong consistency per aggregate stream (the aggregate's events are totally ordered). But read models are populated asynchronously → eventual consistency. If strong consistency reads are required: query the aggregate directly by replaying events (expensive) or accept eventual consistency from projections.             |

---

### 🚨 Failure Modes & Diagnosis

**Failure Mode 1: Schema Evolution Breaks Deserialization**

**Symptom:** A field in `OrderPlacedEvent` was renamed from `totalPrice` to `totalAmount` in a refactor. After deployment, loading any historical `Order` aggregate fails with `JsonMappingException: Unrecognized field 'totalPrice'` for events stored before the rename. The aggregate cannot be reconstituted → all commands on those orders fail.
**Root Cause:** Old events in the event store have schema version 1 (`totalPrice`). New code expects version 2 (`totalAmount`). No migration or upcaster was written. Old events are immutable — they cannot be changed. The new code does not know how to deserialize the old schema.
**Diagnostic:**

```bash
# Check error in service logs:
kubectl logs order-service | grep "JsonMappingException"
# Should show: field name mismatch between stored event and expected

# Read a raw event from EventStore:
curl http://eventstore:2113/streams/Order-123/0 \
  -H "Accept: application/json"
# Check: does the event JSON have 'totalPrice' (old) or 'totalAmount' (new)?

# Axon: check event store for schema:
SELECT payload FROM domain_event_entry WHERE type='OrderPlacedEvent'
LIMIT 1;
# Inspect JSON payload for old field names
```

**Fix:** Write an upcaster (event transformer): transforms old schema events at deserialization time:

```java
@Component
public class OrderPlacedEventUpcaster
    extends SingleEventUpcaster {
    @Override
    protected boolean canUpcast(EventRepresentation event) {
        return event.getType().equals("OrderPlacedEvent")
            && event.getMetaData()
                .get("eventSchemaVersion", 0) < 2;
    }
    @Override
    protected GenericDomainEventMessage<?> doUpcast(
        EventRepresentation event) {
        // Rename field in JSON payload
        JsonNode payload = (JsonNode) event.getData();
        ((ObjectNode) payload).set("totalAmount",
            payload.get("totalPrice"));
        ((ObjectNode) payload).remove("totalPrice");
        return event.withPayload(payload);
    }
}
```

**Prevention:** Never rename, remove, or change the type of an existing event field. Only add new OPTIONAL fields to existing events. For breaking changes: create a new event type (`OrderPlacedV2`) and write an upcaster that converts V1 to V2. Schema registry enforces compatibility.

**Failure Mode 2: Event Store Growth Causes Unbounded Memory Load**

**Symptom:** Aggregate with 50,000 events. Loading the aggregate (for every command) requires reading and applying 50,000 events. Command latency: 8 seconds. Service appears hung under concurrent load. Memory: loading 50,000 events into memory per request.
**Root Cause:** Snapshot threshold not configured. Aggregate has been active for years with no snapshot taken. Every aggregate load replays the entire event history. As the event count grows: command latency grows linearly.
**Diagnostic:**

```bash
# Count events for an aggregate:
# EventStore:
curl http://eventstore:2113/streams/Order-123/info \
  -H "Accept: application/json" | jq .headEventNumber
# If headEventNumber > 500 and no snapshot: problem

# Axon: check domain_event_entry table:
SELECT COUNT(*) FROM domain_event_entry
WHERE aggregate_identifier = '123';
# High count + no snapshot_event_entry = issue

# Measure command latency vs aggregate event count:
# Metrics: histogram of command latency by aggregate age
```

**Fix:** Enable snapshotting. Axon:

```java
@Aggregate(snapshotTriggerDefinition = "snapshotTrigger")
public class OrderAggregate { ... }

@Bean
public SnapshotTriggerDefinition snapshotTrigger(
    Snapshotter snapshotter) {
    return new EventCountSnapshotTriggerDefinition(
        snapshotter, 100); // snapshot every 100 events
}
```

**Prevention:** Configure snapshot threshold BEFORE deploying Event Sourcing in production. Monitor event count per aggregate. Alert when any aggregate exceeds 500 events without a snapshot.

**Failure Mode 3: Security - Sensitive Data in Immutable Events**

**Symptom:** GDPR right-to-erasure request: a user requests deletion of their personal data. Investigation reveals: `UserRegisteredEvent` stored in the event store contains: full name, email, date of birth, national ID number. Events are immutable — they cannot be deleted. The system cannot comply with the GDPR erasure request. Legal and compliance risk.
**Root Cause:** Sensitive PII data was stored directly in domain events. The immutability of the event store — a feature for audit purposes — conflicts with the legal requirement to delete personal data.
**Diagnostic:**

```bash
# Audit events for PII content:
# Search event payload for fields containing PII:
SELECT type, payload FROM domain_event_entry
WHERE payload::text LIKE '%nationalId%'
   OR payload::text LIKE '%dateOfBirth%';
# If results: PII is embedded in immutable events

# Count affected events:
SELECT COUNT(*), type FROM domain_event_entry
WHERE aggregate_identifier IN (
  SELECT aggregate_id FROM user_pii_registry
  WHERE user_id = 'user-123')
GROUP BY type;
```

**Fix (architectural):** Crypto-shredding: store a per-user encryption key. Encrypt PII fields in events using the user's key. Upon GDPR erasure: delete the encryption key → PII is unreadable (the encrypted data remains but is effectively erased). Events remain immutable (encrypted bytes unchanged) but PII is inaccessible.

```java
// Store encrypted PII in event:
String encryptedId = encryptionService.encrypt(
    nationalId, userEncryptionKey);
apply(new UserRegisteredEvent(userId, name, email,
    encryptedId));
// On GDPR erasure: delete userEncryptionKey
// Events remain in store but PII is unreadable
```

**Prevention:** Event design review: before storing any event, classify each field (PII? sensitive?). Store PII by reference (userId only in events; resolve PII from a separate, erasable store at read time). Crypto-shredding for PII that must be in events for audit purposes.

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**

- DST-061 - CQRS (Event Sourcing is the write-side complement to CQRS)

**Builds On This (learn these next):**

- DST-063 - Outbox Pattern (reliable event publishing from the event store)
- DST-056 - Saga Pattern (orchestrating long-running processes using events)

**Alternatives / Comparisons:**

- DST-061 - CQRS (CQRS can be implemented without Event Sourcing)

---

### 📌 Quick Reference Card

```
+------------------+--------------------------------+
| WHAT IT IS       | Store state changes as an      |
|                  | append-only sequence of domain |
|                  | events; state is derived       |
+------------------+--------------------------------+
| PROBLEM SOLVED   | CRUD discards history; no      |
|                  | audit trail, no temporal       |
|                  | queries, no projection replay  |
+------------------+--------------------------------+
| KEY INSIGHT      | Events are truth; state is     |
|                  | derived. Invert CRUD model.    |
|                  | Same as accounting ledger.     |
+------------------+--------------------------------+
| USE WHEN         | Audit trail required; temporal |
|                  | queries needed; CQRS read model|
|                  | rebuild needed; complex domain |
|                  | with rich event history        |
+------------------+--------------------------------+
| AVOID WHEN       | Simple CRUD; team lacks DDD    |
|                  | expertise; no need for audit;  |
|                  | GDPR compliance complexity     |
|                  | is not manageable              |
+------------------+--------------------------------+
| TRADE-OFF        | Complete history + replay vs   |
|                  | schema evolution complexity +  |
|                  | snapshot management overhead   |
+------------------+--------------------------------+
| ONE-LINER        | Append-only event log is truth;|
|                  | state is a derived projection  |
+------------------+--------------------------------+
| NEXT EXPLORE     | DST-061 CQRS; DST-063 Outbox   |
|                  | Pattern; Axon Framework docs   |
+------------------+--------------------------------+
```

**If you remember only 3 things:**

1. Events are immutable facts — never delete or modify. Schema evolution is the hardest problem in Event Sourcing: old events must be readable forever. Add new optional fields; never rename or remove. Write upcasters for breaking changes.
2. Current state = apply(all events). This is expensive at scale → snapshots every N events. Snapshot is not the source of truth — it's a cache. Monitor aggregate event count and configure snapshot threshold BEFORE production.
3. PII in events violates GDPR right-to-erasure (events are immutable). Use crypto-shredding (encrypt PII with per-user key; delete key on erasure) or store PII by reference (userId only in events; resolve PII from erasable store).

**Interview one-liner:**
"Event Sourcing stores the domain's history as an append-only sequence of immutable events (`OrderPlaced`, `PaymentProcessed`). Current aggregate state is derived by replaying events (not stored directly). This provides: complete audit trail, temporal queries (replay to any point in time), and projection replay (rebuild CQRS read models with corrected logic). Trade-offs: schema evolution complexity (old events must be readable forever — upcasters), snapshot management (replay 10,000 events is slow — snapshot every N events), and GDPR compliance (PII in immutable events — use crypto-shredding). Best combined with CQRS (DST-061): Event Sourcing provides the event log; CQRS provides queryable read models from those events."

---

### 💎 Transferable Wisdom

**Reusable Engineering Principle:**
Record history as a first-class concern, not an afterthought. The principle: systems that need to answer "what happened, when, and why?" must record events, not just outcomes. This applies universally: source control (Git) records every code change as a commit (event), not just the current state. Financial ledgers record every transaction, not just the balance. Physics records observations (experiments), not just theories derived from them. Engineering systems that log only current state are brittle under temporal queries, audits, and post-hoc analysis. Event Sourcing formalizes this: make history the authoritative source, make current state the derived view.

**Where else this pattern appears:**

- **Git version control:** Git is Event Sourcing for source code. Every commit is an immutable event: author, timestamp, parent commit, diff. The current file state (working tree) is derived by replaying commits from the initial commit. `git checkout <sha>` is a temporal query — reconstruct state at a specific event. `git blame` is a projection — compute who last changed each line. `git log --graph` is another projection — visualize the event tree. Snapshots: Git's pack files (compressed representation of many commits) are the snapshot analog. Git proves Event Sourcing works at global scale (millions of repositories, trillions of events).
- **Kafka as event log (Kafka Streams):** Kafka topics as append-only event logs enable Event Sourcing at the messaging layer. Kafka's log compaction provides a "snapshot" — only the latest value per key is retained. Kafka Streams builds stateful applications by consuming events and maintaining derived state (KTables). The `changelog` topic in Kafka Streams is the event log for the KTable state. This is the Event Sourcing pattern applied to streaming applications: the stream is the event log; the KTable is the read model.
- **Blockchain:** A blockchain is a distributed, append-only event log where each block is an immutable ordered set of transactions (events). The current account balance of each address is derived by replaying all transactions from genesis. "Smart contracts" are projection logic — applied to events to derive state. UTXO model (Bitcoin) vs account model (Ethereum) are different projection strategies over the same event log. Blockchain proves that Event Sourcing can operate without a trusted central authority (distributed append-only log with consensus).

---

### 💡 The Surprising Truth

Event Sourcing was inspired by and is structurally identical to the accounting ledger — a practice unchanged since Luca Pacioli formalized double-entry bookkeeping in 1494. The surprising truth: accounting systems have used Event Sourcing for 530 years because accountants discovered that auditing requires complete, immutable history. The "General Ledger" is an append-only event log. "Account balance" is a projection derived from ledger entries. "Trial balance" is a materialized view. When programmers "discovered" Event Sourcing in 2005-2010, they were rediscovering a 500-year-old practice. The architectural insight — that events are the source of truth and state is derived — has been proven correct by every functioning financial system in history. Software engineering took 60 years of database-first thinking (CRUD) before rediscovering what accountants knew in 1494. The lesson: look at domains that have solved the same problem at scale for centuries — they often encode architectural wisdom that software engineering is still rediscovering.

---

### 🧠 Think About This Before We Continue

**Q1 (A - System Interaction):** An Event Sourcing system publishes events to both the event store and an external Kafka topic (for CQRS projections). The command handler: (1) appends the event to the event store (transaction A), (2) publishes to Kafka (transaction B). These are two different systems — they cannot participate in a single ACID transaction. What can go wrong, and how does the Outbox Pattern (DST-063) solve this?
_Hint:_ What can go wrong: (1) Event appended to event store (success) → Kafka publish fails (network timeout, Kafka unavailable). Event store has the event; Kafka does not. Projection never receives the event → read model is permanently inconsistent. (2) Kafka published (success) → event store append fails. Kafka has an event for an order that doesn't exist in the authoritative store. Projections show an order that the command side cannot find. Both cases: the two stores are out of sync. Cannot use distributed transactions (2PC) across event store + Kafka without sacrificing availability. Solution: Outbox Pattern (DST-063). Write the event ONLY to the event store (single transaction). A separate process (Change Data Capture or polling) reads new events from the event store and publishes to Kafka reliably. The event store is the authoritative record; Kafka delivery is a reliable downstream delivery concern. No dual-write, no distributed transaction needed.

**Q2 (D - Root Cause):** A team built an Event Sourcing system. Six months after launch, they receive a GDPR erasure request for user ID 12345. Investigation reveals: 847 events reference user ID 12345, stored across 6 different aggregate streams (Orders, Payments, Reviews, Addresses, UserProfile, Cart). Each event contains name, email, and shipping address directly in the payload. The events are immutable. The engineering team says "we can't erase the data." What are the available options, and what are the trade-offs of each?
_Hint:_ Options: (1) **Crypto-shredding:** each user has an encryption key stored in a key management service (KMS). PII fields in events are encrypted with the user's key at write time. On GDPR erasure: delete the encryption key from KMS. Events remain in the store (immutable) but PII is unreadable without the key. Trade-off: adds encryption overhead at write time; all reads must decrypt; if encryption key is lost before erasure: data is unrecoverable (but that's the point). (2) **Reference by ID only:** events contain `userId: 12345` — no name, email, or address. PII lives in a separate, erasable user profile service. At read time: resolve userId → PII. On GDPR erasure: delete from the user profile service → PII is gone; events remain but contain only opaque IDs. Trade-off: read-time join required; PII resolver service must always be available. (3) **Tombstone events:** append a `UserDataErased` event. Projections that consume events check for tombstone → replace PII fields with null/redacted. Historical events still contain PII in the event store — potentially non-compliant depending on jurisdiction. (4) **Accept non-compliance (not recommended):** acknowledge the limitation in the privacy policy — "we may retain data for audit purposes for X years." Limited legal basis. Which is correct: option 1 (crypto-shredding) or option 2 (reference by ID) depends on whether PII must be IN the event for audit purposes. Financial events (include amount, account — not PII) → option 2. Events where PII IS the audit data → option 1.

**Q3 (C - Design Trade-off):** Two teams debate Event Sourcing vs traditional CRUD for a new product catalog service (50,000 products, ~100 updates/day, queries: search by category/price/rating). Team A: "Event Sourcing gives us auditability and CQRS for search." Team B: "This is a simple CRUD case — Event Sourcing is massive over-engineering." Who is right, and how would you decide?
_Hint:_ Evaluate the CQRS + Event Sourcing benefit triggers: (1) Do you need temporal queries ("what was the product price on Tuesday?")? For a product catalog: maybe useful for pricing audits, but not a core user requirement. (2) Do you need complete audit trail for compliance? Product catalog: generally no legal requirement for price change audit (unlike financial transactions). (3) Do you need to rebuild read models from scratch? Product catalog: if Elasticsearch index is corrupted, you can rebuild from the current database state without a full event log. (4) Is the read:write ratio high enough to justify CQRS? 50,000 products, ~100 updates/day: this is EXTREMELY low write volume. CRUD with a read replica and Elasticsearch index built via CDC (Change Data Capture) achieves the same search performance without Event Sourcing complexity. Verdict: Team B is right for this case. CQRS (for search) is justified — use CDC to build the Elasticsearch index. Event Sourcing is NOT justified — no audit requirements, no temporal queries, no projection replay need. The rule: Event Sourcing earns its complexity cost only when the domain genuinely needs complete, auditable, replayable history — not when a CRUD + CDC + search index solves the problem.

