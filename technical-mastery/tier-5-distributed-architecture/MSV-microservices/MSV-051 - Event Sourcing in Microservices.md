---
id: MSV-051
title: Event Sourcing in Microservices
category: Microservices
tier: tier-5-distributed-architecture
folder: MSV-microservices
difficulty: ★★★
depends_on: MSV-048, MSV-050
used_by: MSV-048, MSV-050, MSV-054
related: MSV-048, MSV-050, MSV-054, MSV-046, MSV-059, MSV-049
tags:
  - microservices
  - pattern
  - deep-dive
  - events
status: complete
version: 4
layout: default
parent: "Microservices"
grand_parent: "Technical Mastery"
nav_order: 51
permalink: /technical-mastery/microservices/event-sourcing-in-microservices/
---

⚡ TL;DR - Event Sourcing: instead of storing current
state (UPDATE orders SET status='CONFIRMED'), store
every state change as an immutable event (OrderCreated,
PaymentProcessed, OrderConfirmed). Current state:
replay events. Benefits: complete audit trail, time-
travel (reconstruct state at any past moment), event
replay for new projections, natural fit for CQRS.
Trade-offs: event schema evolution complexity, query
complexity (must project events to read), storage
growth, snapshot required for performance at scale.

| #051 | Category: Microservices | Difficulty: ★★★ |
|:---|:---|:---|
| **Depends on:** | Event-Driven Microservices, CQRS in Microservices | |
| **Used by:** | Event-Driven Microservices, CQRS in Microservices, Outbox Pattern | |
| **Related:** | Event-Driven Microservices, CQRS in Microservices, Outbox Pattern, Saga Pattern, Event-Carried State Transfer, Eventual Consistency in Microservices | |

---

### 🔥 The Problem This Solves

**TRADITIONAL STATE STORAGE LOSES HISTORY:**
You have a bug in production: an order was incorrectly
confirmed even though payment failed. You check the
database: `status=CONFIRMED`. There is no record
of what happened before - no payment failure record,
no sequence of status transitions. You cannot tell
if the bug is in the payment service, the saga
orchestrator, or the order service. The database
shows only the final state, not how it got there.

With Event Sourcing: the event store contains:
`OrderCreated`, `PaymentFailed`, `OrderConfirmed`
(incorrect - bug). You see the exact sequence. You
can replay the events without the bug to get the
correct state. You can issue a compensating event.
Full auditability is a structural property, not
an afterthought.

---

### 📘 Textbook Definition

**Event Sourcing** (Martin Fowler, 2005) is a pattern
where the state of an aggregate is determined by
a sequence of events. Instead of persisting current
state (CRUD: update the row to the latest value),
you persist every state change as an immutable event
in an append-only event store. Current state is
obtained by replaying the event sequence. In
microservices context: each service has its own
event store; events are the source of truth; CQRS
projections (read models) are derived from events.
The event store serves both as: durable storage AND
the event bus for propagating changes to other services.
Core characteristics: append-only, immutable events,
time-ordered log, complete history, replayable.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
Event Sourcing: persist state changes (events), not
current state. Current state = replay all events.
Complete history = free. Audit trail = structural.

**One analogy:**
> Accounting uses double-entry bookkeeping. Every
> transaction is recorded as a journal entry (event):
> Jan 5: Revenue +$1000, Accounts Receivable +$1000.
> The current account balance: sum all journal entries.
> You cannot DELETE or UPDATE a journal entry: you
> issue a REVERSING entry (compensating event).
> The balance sheet (current state) is derived from
> the journal (event log). You can reconstruct the
> account balance at ANY point in time: replay entries
> up to that date. This is Event Sourcing applied
> to financial records. Banks have done this for
> centuries; Event Sourcing brings it to software.

**One insight:**
Event Sourcing solves the temporal query problem:
what was the state of order #123 at 2pm yesterday
before the fraud investigation update? With CRUD:
impossible (history overwritten). With Event Sourcing:
replay events up to 2pm yesterday, reconstruct the
state. This is invaluable for debugging, auditing,
and legal compliance requirements.

---

### 🔩 First Principles Explanation

**EVENT STORE STRUCTURE:**

```
TRADITIONAL CRUD (loses history):
  orders table:
  +----------+-------------+------------+
  | order_id | customer_id | status     |
  +----------+-------------+------------+
  | 001      | cust-1      | CONFIRMED  |  <- only current
    state
  | 002      | cust-2      | CANCELLED  |  <- history lost
  +----------+-------------+------------+

EVENT SOURCING (complete history):
  order_events table:
  +----------+----------+------------------+---------------
  | event_id | order_id | event_type       | payload
    |
  +----------+----------+------------------+---------------
  | 1        | 001      | OrderCreated     | {cust-1,
    items}  |
  | 2        | 001      | PaymentProcessed | {amount:
    99.99}  |
  | 3        | 001      | OrderConfirmed   | {}
    |
  | 4        | 002      | OrderCreated     | {cust-2,
    items}  |
  | 5        | 002      | PaymentFailed    | {reason:
    no_funds}|
  | 6        | 002      | OrderCancelled   | {reason:
    payment}|
  +----------+----------+------------------+---------------
  
  Current state of order-001:
    Replay events 1,2,3 -> CONFIRMED
  Current state of order-002:
    Replay events 4,5,6 -> CANCELLED
  State at event 4 (before payment):
    Replay event 4 only -> PENDING
  Full history: preserved, auditable
```

**AGGREGATE + APPLY PATTERN:**

```
Event Sourcing implementation pattern:
  1. Load events for aggregate from event store
  2. Replay events to reconstruct current state
  3. Execute command (validate business rules)
  4. Produce new event(s)
  5. Append new event(s) to event store
  6. Publish event(s) to message broker for
     downstream consumers

Snapshot optimization (large event count):
  Snapshots: periodic state snapshots
  Load: latest snapshot + events AFTER snapshot
  Avoids: replaying 10,000 events on every load
  Rule of thumb: snapshot every 100-500 events
```

---

### 🧪 Thought Experiment

**EVENT SCHEMA EVOLUTION:**

```
CHALLENGE:
  Year 1: OrderCreated { orderId, customerId, items }
  Year 2: Add giftWrap field to OrderCreated
  Year 3: Replace items[] with orderLines[]
  
  Event store: contains 3 years of events
  Year 1 events: no giftWrap, no orderLines
  Year 3 aggregate code: expects orderLines
  
  Replaying year 1 events with year 3 code -> crash!

SOLUTIONS:
  Option A: Upcasting (recommended)
    Event upcaster: converts old event schema
    to new schema before applying to aggregate
    V1 -> V2: add giftWrap=false
    V2 -> V3: rename items -> orderLines
    Aggregate code: always handles latest schema
    Upcasters: versioned, chained
  
  Option B: Event versioning
    Keep OrderCreated_V1, OrderCreated_V2 handlers
    Aggregate applies correct handler per version
    Complexity grows with versions
  
  Option C: Migration (expensive)
    Read all old events; write new events
    Requires full event store migration
    Risky; usually last resort
  
BEST PRACTICE: Upcasting + schema registry
  Register all event versions
  Enforce backward compatibility at publish time
  Apply upcasters on read
```

---

### 🧠 Mental Model / Analogy

> Event Sourcing is like Git for your data. Git never
> deletes commits (events are immutable). `git log`
> shows every change (full history). `git show <SHA>`
> shows state at a specific commit (temporal queries).
> `git checkout <branch>` reconstructs state at any
> point (replay events). `git revert` adds a new commit
> that undoes a previous one (compensating event;
> doesn't modify history). `git blame` traces who
> changed what and when (audit trail). The HEAD
> (current branch tip) is the current state; it's
> derived from the commit history, not stored separately.
> Event Sourcing: your database IS the commit log.

---

### 📶 Gradual Depth - Five Levels

**Level 1 - What it is (anyone can understand):**
Instead of saving the current state (the answer),
save every step that got you there (the work).
Current answer: redo all the steps. Benefit:
you can audit, debug, and replay from any point.

**Level 2 - How to use it (junior developer):**
Event store table: `(event_id, aggregate_id,
event_type, payload, timestamp)`. Append only.
Aggregate loads events, applies each to rebuild
state. `apply(OrderCreated e)` sets initial state.
`apply(PaymentProcessed e)` updates payment info.
`apply(OrderConfirmed e)` sets status=CONFIRMED.

**Level 3 - How it works (mid-level engineer):**
Optimistic concurrency: event store must prevent
concurrent writes to the same aggregate. Append
with expected_version: `INSERT ... WHERE max(version)
= expected_version`. If concurrent write: INSERT
fails (version conflict). Retry: reload events,
replay, retry command. This prevents lost updates
without distributed locks.

**Level 4 - Why it was designed this way (senior/staff):**
Event Sourcing solves audit + temporal query requirements
structurally. With CRUD: auditing = bolt-on (trigger-
based change log, often incomplete). Temporal queries:
impossible without separate history tables. Event
Sourcing: audit trail is structural (the event store IS
the source of truth). Temporal queries: replay up to
any timestamp. The trade-off: read complexity
(always via projection) and storage growth. Justified
when: financial/legal audit trails required, temporal
query needed, event replay for new services needed.

**Level 5 - Mastery (distinguished engineer):**
Event Sourcing at scale: the snapshot problem becomes
critical. An order with 500 state transitions (B2B
enterprise orders, amendment history): replaying 500
events on every read = unacceptable. Snapshot strategy:
store aggregate state as snapshot at version N.
Load: latest snapshot + events since snapshot.
Snapshot invalidation: when event schema changes,
existing snapshots may be stale. Snapshot store
needs versioning. EventStoreDB, Axon Framework,
and Marten (for .NET) provide built-in snapshot
support. Kafka-based event sourcing: compacted topics
for snapshots (latest message per key = latest snapshot).

---

### ⚙️ How It Works (Mechanism)

```java
// AGGREGATE with Event Sourcing
public class Order {
    private OrderId id;
    private OrderStatus status;
    private CustomerId customerId;
    private List<OrderItem> items;
    private Money total;
    private int version;  // for optimistic concurrency

    // List of uncommitted events (to be persisted + published)
    private final List<DomainEvent> uncommittedEvents
        = new ArrayList<>();

    // Reconstruct from event history
    public static Order reconstitute(
            List<DomainEvent> events) {
        Order order = new Order();
        for (DomainEvent event : events) {
            order.apply(event);  // No side effects
            order.version++;
        }
        return order;
    }

    // COMMAND: Place order
    public void placeOrder(CustomerId customerId,
                           List<OrderItem> items) {
        if (status != null) throw new IllegalStateException(
            "Order already exists");
        // Validate, produce event
        Money total = calculateTotal(items);
        OrderCreatedEvent event = new OrderCreatedEvent(
            this.id, customerId, items, total);
        apply(event);  // Apply to in-memory state
        uncommittedEvents.add(event);  // Queue for persistence
    }

    // EVENT APPLIERS (pure state transitions, no side effects)
    private void apply(OrderCreatedEvent e) {
        this.id = e.getOrderId();
        this.customerId = e.getCustomerId();
        this.items = e.getItems();
        this.total = e.getTotal();
        this.status = OrderStatus.PENDING;
    }

    private void apply(PaymentProcessedEvent e) {
        // No status change yet; payment recorded
    }

    private void apply(OrderConfirmedEvent e) {
        this.status = OrderStatus.CONFIRMED;
    }

    private void apply(OrderCancelledEvent e) {
        this.status = OrderStatus.CANCELLED;
    }

    // Dispatcher - routes to correct applier
    private void apply(DomainEvent event) {
        if (event instanceof OrderCreatedEvent e)
            apply(e);
        else if (event instanceof PaymentProcessedEvent e)
            apply(e);
        else if (event instanceof OrderConfirmedEvent e)
            apply(e);
        else if (event instanceof OrderCancelledEvent e)
            apply(e);
    }
}

// EVENT STORE: append-only persistence
@Repository
public class EventSourcedOrderRepository {

    @Transactional
    public void save(Order order) {
        List<DomainEvent> events =
            order.getUncommittedEvents();
        for (DomainEvent event : events) {
            // Append with optimistic concurrency check
            int inserted = jdbc.update(
                "INSERT INTO order_events " +
                "(order_id, event_type, payload, " +
                " version, occurred_at) " +
                "VALUES (?, ?, ?, " +
                "  (SELECT COALESCE(MAX(version),0)+1 " +
                "   FROM order_events WHERE order_id=?), " +
                "  NOW())",
                event.getOrderId(), event.getType(),
                serialize(event), event.getOrderId());
            if (inserted == 0) throw new
                ConcurrencyException("Version conflict");
        }
        // After DB persist: publish to Kafka
        events.forEach(eventPublisher::publish);
    }

    public Order load(OrderId orderId) {
        List<DomainEvent> events = jdbc.query(
            "SELECT * FROM order_events " +
            "WHERE order_id = ? ORDER BY version",
            eventMapper, orderId);
        return Order.reconstitute(events);
    }
}
```

---

### 🔄 The Complete Picture - End-to-End Flow

```
EVENT SOURCING WRITE + READ FLOW:

WRITE:
  1. Load order (replay events from event store)
  2. Execute command: confirmOrder()
  3. Validate: is payment processed? yes
  4. Produce: OrderConfirmedEvent
  5. Apply: order.status = CONFIRMED (in-memory)
  6. Append: INSERT INTO order_events
  7. Publish: OrderConfirmedEvent to Kafka

READ (via CQRS projection):
  Kafka consumer receives OrderConfirmedEvent
  Updates: order_list_view.status = CONFIRMED
  GET /orders/001 -> reads from order_list_view
  Returns: CONFIRMED (projection is up to date)

TEMPORAL QUERY (debugging):
  "What was order-001 state at T=10am yesterday?"
  Load all events for order-001
  Filter: events WHERE occurred_at <= T
  Replay filtered events -> state at T
  Answer: PENDING (payment hadn't processed yet)
```

---

### 💻 Code Example

**Example 1 - Wrong vs Right: mutable state vs event log**

```java
// BAD: UPDATE in place - history lost
@Transactional
public void confirmOrder(OrderId id) {
    Order order = orderRepo.findById(id).orElseThrow();
    order.setStatus(OrderStatus.CONFIRMED);  // State lost!
    orderRepo.save(order);
    // No record of WHEN it changed, WHY, or what was before
    // Bug investigation: impossible to trace flow
}
```

```java
// GOOD: Append immutable event - history preserved
@Transactional
public void confirmOrder(OrderId id) {
    Order order = eventRepo.load(id);  // Replay events
    order.confirm();  // Validates + produces event
    eventRepo.save(order);  // Appends OrderConfirmedEvent
    // Full history: OrderCreated -> PaymentProcessed
    //               -> OrderConfirmed (with timestamp)
    // Bug investigation: replay events to trace exact flow
    // Audit: complete trail in event store
}
```

---

### ⚖️ Comparison Table

| Aspect | CRUD (Mutable State) | Event Sourcing |
|---|---|---|
| **Storage** | Current state only | Full event history |
| **Audit trail** | Requires extra work | Structural |
| **Temporal queries** | Impossible without history tables | Replay to any timestamp |
| **Query complexity** | Direct SELECT | Must project events |
| **Storage growth** | Bounded (overwrite) | Unbounded (append-only) |
| **Schema change** | Migrate rows | Upcasting + rebuild projections |
| **Debug capability** | Limited (state only) | Replay and inspect any point |

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| Event Sourcing replaces the database | Event Sourcing uses a database - specifically an append-only event store. The event store IS the database. EventStoreDB, PostgreSQL (append-only table), Kafka (compacted topics) are all valid event stores. The difference: you never UPDATE or DELETE; you only INSERT (append). |
| Event Sourcing means Kafka is the event store | Kafka is a message broker, not a durable event store. Kafka retention defaults to 7 days; events older than retention are deleted. True event stores: EventStoreDB, PostgreSQL (no deletions), or Kafka with infinite retention + compaction. If you use Kafka as your event store: disable compaction, set retention.ms=unlimited, use log compaction only for snapshots. |
| You can fix bugs by editing events | Events are immutable. If an event was wrong: issue a compensating event. `OrderConfirmedInError` followed by `OrderCancelledAsCompensation`. The history records the mistake AND the correction. This is non-negotiable for financial/audit systems. |

---

### 🚨 Failure Modes & Diagnosis

**Aggregate load performance degrades over time**

**Symptom:**
Initially, order API response time: 5ms. After 12
months of operation: response time for high-activity
orders (B2B orders with many amendments): 2000ms.
Database query shows: some orders have 5,000+ events.

**Root Cause:**
No snapshot strategy. Every order load: replays ALL
events from the beginning. 5,000 events per order,
10 JSON deserialization + apply() calls per ms =
500ms per load. Plus database I/O for loading 5,000
rows = 1500ms total.

**Fix:**
```java
// Add snapshot support to event repository
public Order load(OrderId orderId) {
    // 1. Load latest snapshot (if exists)
    Optional<OrderSnapshot> snapshot =
        snapshotRepo.findLatest(orderId);
    
    int fromVersion = 0;
    Order order;
    
    if (snapshot.isPresent()) {
        // Start from snapshot state
        order = Order.fromSnapshot(snapshot.get());
        fromVersion = snapshot.get().getVersion();
    } else {
        order = new Order();
    }
    
    // 2. Load only events AFTER snapshot version
    List<DomainEvent> events = jdbc.query(
        "SELECT * FROM order_events " +
        "WHERE order_id = ? AND version > ? " +
        "ORDER BY version",
        eventMapper, orderId, fromVersion);
    
    // 3. Apply only new events
    return Order.reconstitute(order, events);
}

// Snapshot every 100 events
@EventHandler
public void onAnyEvent(DomainEvent event, Order order) {
    if (order.getVersion() % 100 == 0) {
        snapshotRepo.save(OrderSnapshot.from(order));
    }
}
// Before: load 5,000 events
// After: load latest snapshot + <=100 events
// P95 response: 2000ms -> 8ms
```

---

### 🔗 Related Keywords

**Complements Event Sourcing:**
- `CQRS in Microservices` - read projections derived
  from event store; natural pair with Event Sourcing
- `Event-Driven Microservices` - events published from
  event store feed downstream consumers

**Requires for correctness:**
- `Outbox Pattern` - ensures atomic event store +
  broker publish; alternative: event store IS the
  outbox (publish from event store directly)

**Related patterns:**
- `Saga Pattern` - Saga choreography uses events;
  Event Sourcing makes Saga state auditable
- `Event-Carried State Transfer` - events carry full
  state; fits naturally with Event Sourcing

---

### 📌 Quick Reference Card

```
┌─────────────────────────────────────────────────────────┐
│ CORE IDEA    │ Persist events, not state                │
│              │ Current state = replay events            │
├──────────────┼──────────────────────────────────────────┤
│ BENEFITS     │ Audit trail (free), temporal queries     │
│              │ Event replay for new projections         │
├──────────────┼──────────────────────────────────────────┤
│ COMPLEXITY   │ Schema evolution (upcasting), snapshots  │
│              │ Query via projections (no direct reads)  │
├──────────────┼──────────────────────────────────────────┤
│ ONE-LINER    │ "Store state changes as events; replay   │
│              │  to reconstruct; Git for your data"      │
└─────────────────────────────────────────────────────────┘
```

**If you remember only 3 things:**
1. Events are immutable append-only records.
   Current state = replay all events for that aggregate.
   History is structural, not bolt-on.
2. Always use with CQRS: read models are projections
   of event history. Never query event store directly
   for reads at scale.
3. Snapshots are required for performance: store
   periodic snapshots so you replay the last N events,
   not all events from beginning.

**Interview one-liner:**
"Event Sourcing: store every state change as an
immutable event; current state = replay events.
Benefits: structural audit trail, temporal queries
(state at any past point), event replay for new
projections, natural fit for CQRS. Trade-offs: schema
evolution via upcasting, snapshot strategy for
performance (don't replay all events forever), all
reads via projections (no direct state queries).
Use when: audit/compliance required, temporal queries
needed, event replay for new analytical services."

---

### 💡 The Surprising Truth

The most surprising aspect of Event Sourcing: you
cannot query the current state directly. `SELECT
status FROM orders WHERE order_id = 123` is not how
Event Sourcing works. You load events, replay, get
state. This feels very wrong to SQL-trained engineers.
The insight: Event Sourcing is WRITE-optimized by
design. Reads are always via projections (CQRS read
models). The projection IS the queryable state. The
event store is the write-authoritative storage. Once
you internalize this: Event Sourcing is simple.
The complexity is in accepting that you have two
stores: event store (authoritative, write) and
projection store (derived, read). They serve different
purposes and have different consistency guarantees.

---

### ✅ Mastery Checklist

**You've mastered this when you can:**
1. **IMPLEMENT** Implement an `Order` aggregate with
   Event Sourcing: `placeOrder()`, `confirmOrder()`,
   `cancelOrder()` commands each produce events;
   `apply()` methods for each event type; load
   from event history; snapshot logic every 100
   events.
2. **SCHEMA** An `OrderCreated` event needs a new
   required field `channel` (WEB, MOBILE, API). How
   do you handle existing events that don't have
   this field? Implement the upcaster.
3. **TEMPORAL** Given order-001's event history:
   write a function that returns the order state
   at a given timestamp. Which events are included?
4. **CONCURRENCY** Two concurrent requests try to
   confirm order-001. Both load current state (PENDING).
   Both produce OrderConfirmedEvent. How does the
   event store prevent duplicate confirm? Walk
   through optimistic locking with expected_version.
5. **KAFKA** Is Kafka a valid event store? What are
   the risks? What settings would you need for Kafka
   to function as a durable, non-expiring event store?

---

### 🧠 Think About This Before We Continue

**Q1.** You have an Event Sourced order service in
production with 100M events. A bug is discovered:
for 3 months, the OrderConfirmedEvent was being
applied twice (double-confirmed). The aggregate
state (in-memory via replay) was CONFIRMED, but
some orders were double-processed. How do you:
a) identify affected orders, b) fix the state without
destroying event history, c) prevent future occurrences.

**Q2.** A GDPR request comes in: delete all data
for customer-123. Your Event Sourced order service
has 500 events containing customer-123's personal
data (name, address, email). Events are immutable.
How do you comply with GDPR's right to erasure
while maintaining Event Sourcing principles? (Hint:
crypto-shredding)

**Q3.** Your Event Sourced service handles 10,000
orders/second at peak. Each order has an average of
15 events. You want to rebuild a projection from
scratch (schema change). Calculate: how long will
the rebuild take given: 2 years of history, 15
events/order, 10 TB of event data, 50,000 events/sec
projection rebuild throughput? What is the customer
impact during rebuild?