---
layout: default
title: "Event Sourcing Pattern"
parent: "Software Architecture Patterns"
nav_order: 731
permalink: /software-architecture/event-sourcing-pattern/
number: "731"
category: Software Architecture Patterns
difficulty: ★★★
depends_on: "CQRS Pattern, Domain Events, Eventual Consistency"
used_by: "Axon Framework, EventStore, Kafka + custom event sourcing, financial systems"
tags: #advanced, #architecture, #event-sourcing, #audit-log, #immutable-events
---

# 731 — Event Sourcing Pattern

`#advanced` `#architecture` `#event-sourcing` `#audit-log` `#immutable-events`

⚡ TL;DR — **Event Sourcing** stores the **history of events** (not current state) as the source of truth — current state is derived by replaying events, giving you a complete audit log and the ability to reconstruct any past state.

| #731            | Category: Software Architecture Patterns                                     | Difficulty: ★★★ |
| :-------------- | :--------------------------------------------------------------------------- | :-------------- |
| **Depends on:** | CQRS Pattern, Domain Events, Eventual Consistency                            |                 |
| **Used by:**    | Axon Framework, EventStore, Kafka + custom event sourcing, financial systems |                 |

---

### 📘 Textbook Definition

**Event Sourcing** is an architectural pattern where, instead of storing the current state of an entity (overwriting the previous value), the system stores an **append-only, immutable log of events** that describe every state transition. Current state is derived by **replaying** all events from the beginning (or from a snapshot). Key concepts: (1) **Event** — an immutable fact that happened in the past (past tense: OrderPlaced, PaymentProcessed, ItemShipped). (2) **Event Store** — append-only storage for events (EventStore DB, Kafka, PostgreSQL with an events table). (3) **Projection** — a read model built by replaying events into a specific view. (4) **Snapshot** — a point-in-time capture of state, used to avoid replaying all history on every load. (5) **Aggregate** — the domain object whose events are stored; loaded by replaying its events. Benefits: complete audit log, temporal queries ("what was the account balance on Tuesday?"), event replay for new projections, natural fit with CQRS. Drawbacks: complexity (replaying long event streams is slow without snapshots), eventual consistency in projections, no simple SQL query of current state (must query projections).

---

### 🟢 Simple Definition (Easy)

Your bank account: instead of storing "Balance: $350," the bank stores: "Deposit $200, Deposit $500, Withdraw $350." Current balance = $200 + $500 - $350 = $350. Same answer, but now you have the full history. Can answer: "What was my balance on Monday?" Replay events up to Monday. Can answer: "Was there unauthorized activity?" See every transaction. Can answer: "How many deposits this month?" Count deposit events. The event log is the source of truth. The $350 balance: a derived value.

---

### 🔵 Simple Definition (Elaborated)

Traditional storage: UPDATE orders SET status='SHIPPED' WHERE id=123. Gone: the history. No way to know: was it ever PENDING? CONFIRMED before SHIPPED? How long did it sit in each state? Event Sourcing: instead of UPDATE, store: OrderPlaced, OrderConfirmed, OrderShipped. Replay → SHIPPED. Advantage: full audit trail for free. Generate a new report: "Average time from order placement to shipping" — replay all OrderPlaced and OrderShipped events, compute the delta. No schema migration needed. This new report is available for all historical data, not just future data. The event log is a time machine.

---

### 🔩 First Principles Explanation

**Event store structure, aggregate loading, snapshots, and projections:**

```
EVENT STORE SCHEMA (simple PostgreSQL implementation):

  events table:
  ┌────────┬──────────────┬──────────────────┬───────────┬────────────────────────┐
  │ id     │ aggregate_id │ aggregate_type   │ sequence  │ event_data (JSON)      │
  ├────────┼──────────────┼──────────────────┼───────────┼────────────────────────┤
  │ 1      │ order-123    │ Order            │ 1         │ {"type":"OrderPlaced", │
  │        │              │                  │           │  "customerId":"c-1",   │
  │        │              │                  │           │  "items":[...],        │
  │        │              │                  │           │  "timestamp":"..."}    │
  ├────────┼──────────────┼──────────────────┼───────────┼────────────────────────┤
  │ 2      │ order-123    │ Order            │ 2         │ {"type":"PaymentConfirmed",
  │        │              │                  │           │  "amount": 59.99}      │
  ├────────┼──────────────┼──────────────────┼───────────┼────────────────────────┤
  │ 3      │ order-123    │ Order            │ 3         │ {"type":"ItemShipped", │
  │        │              │                  │           │  "trackingId":"TRK1"}  │
  └────────┴──────────────┴──────────────────┴───────────┴────────────────────────┘

  Rules:
    - APPEND ONLY: never UPDATE or DELETE rows.
    - sequence: monotonically increasing per aggregate. Used for optimistic locking.
    - event_data: JSON payload of the event.

LOADING AN AGGREGATE (replay):

  public Order loadOrder(String orderId) {
      // 1. Fetch all events for this aggregate (in sequence order):
      List<Event> events = eventStore.loadEvents("order-" + orderId);

      // 2. Replay events to reconstruct current state:
      Order order = new Order();  // Empty initial state.
      for (Event event : events) {
          order.apply(event);  // Each event transitions state.
      }
      return order;
  }

  // Aggregate: handles each event type:
  public class Order {
      private UUID id;
      private UUID customerId;
      private List<OrderItem> items;
      private OrderStatus status;
      private String trackingId;

      void apply(Event event) {
          switch (event) {
              case OrderPlaced e -> {
                  this.id = e.orderId();
                  this.customerId = e.customerId();
                  this.items = e.items();
                  this.status = OrderStatus.PLACED;
              }
              case PaymentConfirmed e -> {
                  this.status = OrderStatus.CONFIRMED;
              }
              case ItemShipped e -> {
                  this.status = OrderStatus.SHIPPED;
                  this.trackingId = e.trackingId();
              }
              // No default: unknown events silently ignored (forward compatibility).
          }
      }
  }

HANDLING COMMANDS (aggregate generates events):

  public class OrderCommandHandler {

      public void handle(ShipOrderCommand command) {
          // 1. Load aggregate by replaying events:
          Order order = loadOrder(command.orderId());

          // 2. Validate business rule:
          if (order.status() != OrderStatus.CONFIRMED) {
              throw new InvalidStateException("Cannot ship unconfirmed order");
          }

          // 3. Generate new event (NOT direct state mutation):
          ItemShippedEvent event = new ItemShippedEvent(
              command.orderId(), command.trackingId(), Instant.now()
          );

          // 4. Apply event to aggregate (update in-memory state):
          order.apply(event);

          // 5. Append event to event store (the only "write"):
          eventStore.append("order-" + command.orderId(),
                           order.version(),  // For optimistic locking.
                           event);

          // 6. Publish event for projections to consume:
          eventBus.publish(event);
      }
  }

OPTIMISTIC LOCKING WITH SEQUENCE:

  Problem: two concurrent commands try to ship the same order.

  Both load the aggregate at version 3 (3 events so far).
  Both generate ItemShippedEvent.
  Both try to append at version 4.

  First write succeeds: event stored at sequence 4.
  Second write: FAILS. "Expected sequence 4, but sequence 4 already exists."
  Second command: must reload (now sees the first command's event) and retry or fail.

  // eventStore.append: include expected version:
  // INSERT INTO events ... WHERE aggregate_id = ? AND MAX(sequence) = expectedVersion
  // If MAX(sequence) != expectedVersion: concurrent modification → reject.

SNAPSHOTS (performance optimization for long event streams):

  Problem: Order with 500 events. Every load: replay 500 events.
  Solution: periodically store a snapshot of aggregate state.

  snapshots table: { aggregate_id, sequence, snapshot_data, created_at }

  Load with snapshot:
    1. Load most recent snapshot for order-123: { status: CONFIRMED, at_sequence: 480 }
    2. Load events AFTER sequence 480: events 481-500.
    3. Apply only 20 events (not 500).

  Snapshot creation: after every N events, or periodically (e.g., every 100 events).

  Snapshotting strategy: trade-off between snapshot storage cost and replay speed.

PROJECTIONS (building read models from events):

  // Read model: order list for a customer (denormalized for fast UI):
  @EventHandler
  public class CustomerOrdersProjection {
      private final OrderSummaryRepository readRepo;

      void on(OrderPlacedEvent event) {
          readRepo.save(new OrderSummary(event.orderId(), event.customerId(),
                                        "PLACED", event.items().size(), event.total()));
      }

      void on(ItemShippedEvent event) {
          readRepo.updateStatus(event.orderId(), "SHIPPED");
          readRepo.updateTracking(event.orderId(), event.trackingId());
      }
  }

  REBUILDING A PROJECTION:
    New requirement: "show estimated delivery date on order list."
    Old projection: doesn't have delivery date.

    WITHOUT Event Sourcing: need to run data migration, populate delivery date column.
    WITH Event Sourcing:
      1. Add delivery date field to projection schema.
      2. Update the projection event handler to compute delivery date from ItemShippedEvent.
      3. REPLAY ALL EVENTS from beginning through the projection:
         eventStore.replayAll("Order", customerOrdersProjection);
      4. Projection rebuilt with delivery dates for ALL historical orders.
      No data migration. No "old data without delivery date." Event store is the source of truth.

TEMPORAL QUERIES (the time machine):

  "What was order-123's status on January 15th at 3:00 PM?"

  WITH Event Sourcing:
    Load all events for order-123 with timestamp <= Jan 15 15:00.
    Replay those events. → Status at that point in time.

  WITHOUT Event Sourcing:
    Only have the current status. History is gone.
    Need a separate audit log (which is essentially event sourcing anyway).

EVENT SCHEMA EVOLUTION:

  Challenge: OrderPlaced event from 2020 has different fields than 2024.

  Strategies:
    1. Upcasting: transform old event format to new format on load.
       EventUpcaster: reads v1 event → produces v2 event structure.
       Aggregate: only handles v2 events.

    2. Weak schema (just add optional fields to JSON): v1 events missing new fields = null.
       Aggregate: handles null gracefully.

    3. Never delete or rename fields: only add new optional fields (additive changes).
```

---

### ❓ Why Does This Exist (Why Before What)

WITHOUT Event Sourcing:

- UPDATE overwrites state: history lost forever
- Audit log: separate concern, often inconsistent or incomplete
- New report on historical data: impossible (past state gone)
- Rebuild a new view of data: must migrate existing data (risky)

WITH Event Sourcing:
→ Complete, immutable history — every state transition recorded
→ Rebuild any projection from scratch: replay event log
→ Temporal queries: reconstruct any past state
→ Audit trail is inherent — not an afterthought

---

### 🧠 Mental Model / Analogy

> A version control system (Git) for your data. Git doesn't store "the current file" — it stores every commit (event). Current state = apply all commits. Checkout any past commit: see any past state. `git log` = full history. `git blame` = who changed what and when. Now: apply this to your entire database. Every change is a "commit" (event). Current balance = replay all transactions. Yesterday's balance = replay only yesterday's events. New "feature" (report) = compute from existing event history.

"Git commit" = Domain Event
"git log" = Event Store
"Current file contents" = Current aggregate state (derived from replaying commits)
"git checkout <commit>" = Temporal query (replay events up to a point in time)
"New branch with different history" = New projection (different view of same events)

---

### ⚙️ How It Works (Mechanism)

```
EVENT SOURCING WRITE FLOW:

  1. Command arrives: ShipOrderCommand(orderId="123")
  2. Load aggregate: eventStore.loadEvents("order-123") → replay → Order in state CONFIRMED
  3. Validate: order.status == CONFIRMED → can ship
  4. Generate event: ItemShippedEvent(orderId="123", trackingId="TRK-456")
  5. Apply event to in-memory aggregate: order.status = SHIPPED
  6. Append to event store: INSERT INTO events (aggregate_id, sequence, event_data)
  7. Publish event: eventBus.publish(ItemShippedEvent) → projections update
```

---

### 🔄 How It Connects (Mini-Map)

```
Domain Events (events as first-class domain concepts)
        │
        ▼ (store events as the source of truth)
Event Sourcing ◄──── (you are here)
(append-only event log; current state = replay; projections for reads)
        │
        ├── CQRS: commands generate events (write); projections serve queries (read)
        ├── Projection: read models built from event replay
        └── Snapshot: performance optimization for long event streams
```

---

### 💻 Code Example

```java
// Minimal Event Sourcing with Axon Framework (Java):

// 1. Aggregate:
@Aggregate
public class BankAccount {
    @AggregateIdentifier
    private String id;
    private BigDecimal balance;

    // Command handler (decides to act, emits event):
    @CommandHandler
    public void handle(WithdrawMoneyCommand cmd) {
        if (balance.compareTo(cmd.amount()) < 0) throw new InsufficientFundsException();
        AggregateLifecycle.apply(new MoneyWithdrawnEvent(id, cmd.amount()));
        // apply() stores the event AND calls the @EventSourcingHandler below.
    }

    // Event sourcing handler (updates state from event — used on REPLAY too):
    @EventSourcingHandler
    public void on(MoneyWithdrawnEvent event) {
        this.balance = balance.subtract(event.amount());
        // Pure state transition. No business logic here. Logic is in @CommandHandler.
    }
}

// 2. Projection (read model):
@ProcessingGroup("bank-accounts")
public class AccountBalanceProjection {
    @EventHandler
    public void on(MoneyWithdrawnEvent event) {
        // Update denormalized read model for balance queries:
        readRepo.debit(event.accountId(), event.amount());
    }
}
```

---

### ⚠️ Common Misconceptions

| Misconception                                 | Reality                                                                                                                                                                                                                                                                                                                                                                                        |
| --------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Event Sourcing means Kafka is the event store | Kafka is an excellent event bus but is NOT designed as a permanent event store. Kafka retention is time-based or size-based — old events are deleted. EventStore, a PostgreSQL events table with append-only semantics, or a dedicated event store: these are event stores. Kafka can be used to distribute events to projections, but the durable event store must retain events indefinitely |
| Event Sourcing makes queries complex and slow | Queries in Event Sourcing don't use the event log directly — they use pre-built projections (read models). Querying a projection is as fast as querying any optimized read model (Redis, Elasticsearch, PostgreSQL table). The complexity is in building and maintaining projections. For read-heavy systems: projections are highly optimized for specific query patterns                     |
| You must replay all events on every load      | Snapshots solve this. For aggregates with long histories: store periodic snapshots. Load: use most recent snapshot + events since snapshot. Replay: only the delta since last snapshot. Well-designed Event Sourcing systems snapshot frequently enough that no aggregate ever needs to replay more than ~100-200 events from a snapshot                                                       |

---

### 🔥 Pitfalls in Production

**Event schema evolution breaks replay — events from 2 years ago can't be deserialized:**

```
SCENARIO:
  OrderPlacedEvent (2022): { "type": "OrderPlaced", "items": [...], "customerId": "..." }
  New requirement (2024): add "channelId" field (web, mobile, API).
  Team: renames "customerId" to "buyerId" (breaking change!) and adds "channelId".

  // New code deserializes event:
  public record OrderPlacedEvent(String orderId, String buyerId, List<Item> items, String channelId) {}

  // Old event from 2022 event store:
  // { "customerId": "c-123", "items": [...] }   ← no buyerId, no channelId

  DESERIALIZATION FAILS:
    Jackson: can't map "customerId" to "buyerId" field.
    Null "channelId": NullPointerException if any code assumes channelId is non-null.

  Replay of any 2022 order: crashes.
  Loading any order created in 2022: broken.
  ALL HISTORICAL ORDERS: unloadable.

BAD: Renaming or deleting fields in event records:
  // Breaking change: renamed "customerId" to "buyerId"
  public record OrderPlacedEvent(String orderId, String buyerId, ...) {}
  // All stored events with "customerId" JSON field: now fail to deserialize.

FIX 1: Never rename or delete fields in events. Only ADD new optional fields.
  // Safe change: add channelId as @JsonProperty(required=false):
  public record OrderPlacedEvent(
      String orderId,
      String customerId,        // KEEP original name. Never rename.
      List<Item> items,
      @JsonProperty("channelId") String channelId  // New field: nullable. Default: null.
  ) {
      // Null = "web" (backward compatibility assumption):
      public String channelIdOrDefault() {
          return channelId != null ? channelId : "web";
      }
  }
  // Old events: channelId = null. New events: channelId = "mobile" or "web" or "api".

FIX 2: Upcasting (transform old event format to new format on load):
  // Upcast v1 (with customerId) to v2 (with buyerId):
  public class OrderPlacedEventUpcaster {
      public ObjectNode upcast(ObjectNode event) {
          if (!event.has("buyerId") && event.has("customerId")) {
              // Old format: rename customerId to buyerId.
              event.set("buyerId", event.get("customerId"));
              event.remove("customerId");
              event.put("channelId", "web");  // Default for old events.
          }
          return event;
      }
  }
  // Upcaster runs on deserialization: old events transformed to new schema before aggregate sees them.

FIX 3: Version events explicitly:
  public record OrderPlacedEvent(
      int schemaVersion,   // e.g., 1 for 2022 events, 2 for 2024 events.
      String orderId,
      ...
  ) {}
  // Load logic: switch on schemaVersion → apply different mapping.

PREVENTION:
  Before merging any event schema change:
    "Does this change break deserialization of existing stored events?"
    Run a test: load 100 random historical events → verify all deserialize correctly.
    CI check: replay test on sample event stream with schema change applied.
```

---

### 🔗 Related Keywords

- `CQRS Pattern` — the read/write separation that complements Event Sourcing naturally
- `Domain Events` — the domain-level concept; events are first-class domain facts
- `Projection` — read models built by replaying events
- `Snapshot` — performance optimization for aggregates with long event histories
- `Axon Framework` — Java framework implementing CQRS + Event Sourcing out of the box

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ KEY IDEA     │ Store events (state transitions), not    │
│              │ current state. Current state = replay.   │
│              │ Complete audit trail. Rebuild any view.  │
├──────────────┼───────────────────────────────────────────┤
│ USE WHEN     │ Audit requirements; temporal queries;    │
│              │ complex domain; multiple read views;     │
│              │ need full history (finance, healthcare)  │
├──────────────┼───────────────────────────────────────────┤
│ AVOID WHEN   │ Simple CRUD; no audit requirements;      │
│              │ team unfamiliar with pattern; small app  │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "Git for your data: store every commit   │
│              │  (event); current state = replay all."  │
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ CQRS → Projection → Domain Events →     │
│              │ Axon Framework → Snapshot               │
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** An e-commerce platform uses Event Sourcing. Over 5 years: 500 million OrderPlaced events. A new business requirement: "show each order's original placement channel (web/mobile/API)." Events from 2019-2021: don't have a channelId field. Events from 2022+: have channelId. You need to rebuild the OrderListProjection to include channelId. Design the complete process: upcaster for old events, projection rebuild procedure, how long it takes to replay 500M events, and how you keep the system running (serving reads) during the multi-hour replay.

**Q2.** Your system uses Event Sourcing for an Order aggregate. A customer places an order with 3 items. Over 2 years, this order accumulates 847 events (status changes, payment retries, partial shipments, address updates, customer notes, etc.). Without snapshots: loading this order takes 850ms (replay 847 events). With a snapshot at event 800: load = snapshot + 47 events = 12ms. Design the snapshotting strategy: when do you create a snapshot, where is it stored, how do you invalidate stale snapshots, and what happens if a snapshot is corrupted?
