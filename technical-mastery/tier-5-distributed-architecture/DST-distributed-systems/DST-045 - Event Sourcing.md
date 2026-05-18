---
id: DST-045
title: Event Sourcing
category: Distributed Systems
tier: tier-5-distributed-architecture
folder: DST-distributed-systems
difficulty: ★★☆
depends_on: DST-018, DST-028, DST-043, DST-044
used_by: DST-058
related: DST-018, DST-028, DST-043, DST-044
tags:
  - distributed
  - event-sourcing
  - event-store
  - audit-log
  - cqrs
status: complete
version: 4
layout: default
parent: "Distributed Systems"
grand_parent: "Technical Mastery"
nav_order: 45
permalink: /technical-mastery/distributed-systems/event-sourcing/
---

⚡ TL;DR - Event Sourcing stores every state change
as an immutable event in an append-only log (event
store), and derives current state by replaying those
events; it provides a complete audit trail, enables
temporal queries (state at any point in time), and
facilitates CQRS by using events to populate read
models, but introduces complexity in schema evolution,
snapshot management, and eventual consistency.

---

### 📋 Entry Metadata

| #045 | Category: Distributed Systems | Difficulty: ★★☆ |
|:---|:---|:---|
| **Depends on:** | Idempotency, Eventual Consistency, Saga Pattern, CQRS | |
| **Used by:** | Event-Driven Architecture | |
| **Related:** | Idempotency, Eventual Consistency, Saga Pattern, CQRS | |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
An e-commerce order has status: SHIPPED. A customer
calls support saying "I never received my order - why
was it marked shipped without my confirmation?" The
support agent looks at the database: `status = SHIPPED`.
There is no record of who changed it, when, what it
was before, or whether there was an intermediate step.
The database stores the current state, not the history.
Auditing is impossible. Rolling back to a prior state
is impossible. Understanding what sequence of events
led to the current state is impossible.

**THE INSIGHT:**
Instead of storing the current state (mutate in place),
store every event that led to the current state
(append only). The current state is always derived
by replaying all events from the beginning. The event
log IS the source of truth - the state is a derived
artifact. This gives you full history, audit, temporal
queries, and the ability to create new read models
from the same event log at any time.

---

### 📘 Textbook Definition

**Event Sourcing** is a persistence pattern where state
changes are stored as a sequence of domain events in
an append-only event store. The current state of an
entity (aggregate) is derived by replaying all events
from the beginning (or from the last snapshot).

**Key concepts:**
- **Event:** an immutable record of something that
  happened (past tense: OrderPlaced, PaymentCharged,
  ItemShipped)
- **Event Store:** append-only log of all events
- **Aggregate:** the entity whose state is derived
  from events (e.g., Order aggregate)
- **Projection:** a read model derived by processing
  events (used in CQRS)
- **Snapshot:** a periodic checkpoint of aggregate
  state to speed up replay

---

### ⏱️ Understand It in 30 Seconds

```
TRADITIONAL:
  Database: orders table
    id | status  | total | updated_at
    42 | SHIPPED | 99.99 | 2024-06-01
  Query: SELECT * FROM orders WHERE id=42
  Result: current state only, no history

EVENT SOURCING:
  Event store: order_events table
    stream_id | seq | event_type        | data
    order-42  |  1  | OrderPlaced       | {total:99.99}
    order-42  |  2  | PaymentReceived   | {method:card}
    order-42  |  3  | FulfillmentStarted| {warehouse:NY}
    order-42  |  4  | ItemShipped       | {tracking:UPS1}

  To get current state: replay events 1-4 in order:
    start with empty Order
    apply OrderPlaced → set total=99.99, status=PENDING
    apply PaymentReceived → status=PAID
    apply FulfillmentStarted → status=PROCESSING
    apply ItemShipped → status=SHIPPED

  To get state at sequence 2: replay events 1-2 only
  → status=PAID (temporal query for any point in time)
```

---

### 🔩 First Principles Explanation

**AGGREGATE REPLAY:**

```python
class Order:
    def __init__(self):
        self.order_id = None
        self.status = None
        self.total = 0.0
        self.items = []

    def apply(self, event: dict) -> None:
        """Apply a single event to update state."""
        if event["type"] == "OrderPlaced":
            self.order_id = event["data"]["order_id"]
            self.status = "PENDING"
            self.total = event["data"]["total"]
        elif event["type"] == "PaymentReceived":
            self.status = "PAID"
        elif event["type"] == "ItemShipped":
            self.status = "SHIPPED"
        # ... additional event types

def load_order(order_id: str, event_store) -> Order:
    """Reconstruct Order by replaying events."""
    events = event_store.get_events(
        stream_id=f"order-{order_id}"
    )
    order = Order()
    for event in events:
        order.apply(event)
    return order
```

**COMMAND HANDLING WITH EVENTS:**

```
INCOMING COMMAND: ShipOrder(order_id=42, tracking=UPS1)

1. Load current state: replay all events for order-42
   → current Order(status=PAID)

2. Validate command against current state:
   PAID → SHIPPED is valid transition

3. Generate event(s):
   ItemShipped(order_id=42, tracking_number=UPS1,
               timestamp=2024-06-01T10:00:00Z)

4. Append to event store:
   INSERT INTO order_events
     (stream_id, seq, event_type, data)
   VALUES
     ('order-42', 4, 'ItemShipped',
      '{"tracking":"UPS1"}')

5. Publish event to message broker (optional):
   → triggers read model update (CQRS projection)
   → triggers downstream services (email notification)

NOTE: Step 2 NEVER modifies existing events.
      Events are immutable. The only write is step 4.
```

**SNAPSHOTS:**

Replaying 1000+ events per aggregate load is slow.
Snapshots periodically save the current state:

```
Event stream: 1000 events for order-42
Snapshot at event 800: saved Order(status=PROCESSING, ...)

Load with snapshot:
  1. Load snapshot at seq=800
  2. Load events 801..1000 from event store
  3. Apply events 801..1000 to snapshot state
  → only 200 events replayed instead of 1000

Snapshot frequency: every N events (N=100 is common),
or triggered on specific events (OrderCompleted),
or scheduled (once per day for active aggregates).
```

**SCHEMA EVOLUTION:**

Events are immutable - you cannot change past events.
But event schemas change over time. Strategies:

```
UPCASTING: Transform old event format to new on read
  Old event: OrderPlaced(v1) = {price: 99}
  New event: OrderPlaced(v2) = {amount: {value:99,
    currency:"USD"}}
  Upcast function: transform v1 → v2 on load
  Result: apply() only needs to handle v2 format

WEAK SCHEMA: Use nullable/optional fields
  New fields default to None for old events
  apply() handles None gracefully

VERSIONED EVENTS: Keep old event handlers
  apply_v1_OrderPlaced(event)
  apply_v2_OrderPlaced(event)
  Dispatch by event schema version
```

---

### 🧠 Mental Model / Analogy

> Event Sourcing is like accounting ledgers. An
> accountant does not change past entries. Every
> transaction (deposit, withdrawal, fee) is a new
> line item in an append-only ledger. Your current
> balance is always derived by summing all entries
> from the beginning (or from the last audit checkpoint).
> If there is a discrepancy, you can audit exactly
> which transaction caused it. If you made an error,
> you add a correcting entry (compensating event) -
> you don't erase the original. The ledger IS the
> source of truth; the balance is a derived view.

---

### 📶 Gradual Depth - Five Levels

**Level 1 - What it is:**
Instead of saving "current state" (overwrite on update),
save every change as an event (append only). To find
current state: read all events and apply them in
order. Like watching a video from the start to find
where you are, rather than saving a snapshot.

**Level 2 - Why append-only:**
Appending is always safe; overwriting can lose history.
If you overwrite, the previous state is gone. With
append-only: every version of the aggregate is
recoverable by replaying up to a point. No data is
ever deleted (until explicit archival).

**Level 3 - Composition with CQRS:**
Events in the event store are published to message
brokers, consumed by projectors that build read models.
This is event-driven CQRS: the event store produces
the synchronization events needed by CQRS read models.
A new read model can be added at any time by replaying
all historical events through the new projector.

**Level 4 - Event store as system of record:**
In traditional systems, the database is the source
of truth. In Event Sourcing, the event store is the
source of truth. The relational database (if any)
is a derived read model. This has an important
implication: if a bug corrupts the read model, you
can delete and rebuild it from the event store.
The event store must never be corrupted or deleted.

**Level 5 - Exactly-once and event deduplication:**
Event Sourcing requires that events are processed
exactly once to avoid applying the same event twice
(which would corrupt aggregate state). Strategies:
idempotent event handlers (applying the same event
twice produces the same result as once), event
sequence numbers (detect and discard duplicate events
by tracking last processed sequence per stream), and
event store transactions (use database optimistic
locking to detect concurrent writes to the same stream).

---

### 💻 Code Example

**Event Store Append: Wrong vs Right**

```python
# BAD: No optimistic concurrency control
# Two concurrent commands can both append event at seq=4,
# corrupting the event stream

class BadEventStore:
    def append(
        self,
        stream_id: str,
        event_type: str,
        data: dict
    ) -> None:
        # BUG: No expected_version check
        # BUG: Race condition: two writers can append same seq
        self.db.execute(
            "INSERT INTO events(stream_id, event_type, data) "
            "VALUES (%s, %s, %s)",
            (stream_id, event_type, json.dumps(data))
        )
```

```python
# GOOD: Event store with optimistic concurrency control

import json
import psycopg2
from typing import list

class EventStore:

    def append(
        self,
        stream_id: str,
        event_type: str,
        data: dict,
        expected_version: int  # -1 = stream must not exist
    ) -> int:
        """Append event to stream, fail on version conflict."""
        try:
            cursor = self.conn.cursor()

            # Check current version
            cursor.execute(
                "SELECT MAX(seq) FROM events WHERE stream_id=%s",
                (stream_id,)
            )
            row = cursor.fetchone()
            current_version = row[0] if row[0] is not None else -1

            if current_version != expected_version:
                raise ConcurrencyError(
                    f"Expected version {expected_version}, "
                    f"got {current_version}"
                )
            # ConcurrencyError: another writer appended first.
            # Retry: reload aggregate and re-evaluate command.

            new_version = current_version + 1
            cursor.execute(
                "INSERT INTO events "
                "(stream_id, seq, event_type, data, occurred_at) "
                "VALUES (%s, %s, %s, %s, NOW())",
                (stream_id, new_version, event_type,
                 json.dumps(data))
            )
            self.conn.commit()
            return new_version

        except psycopg2.IntegrityError:
            # Unique constraint (stream_id, seq) violated:
            # another writer inserted same seq concurrently
            self.conn.rollback()
            raise ConcurrencyError("Concurrent write detected")

    def get_events(
        self,
        stream_id: str,
        from_seq: int = 0
    ) -> list[dict]:
        cursor = self.conn.cursor()
        cursor.execute(
            "SELECT seq, event_type, data, occurred_at "
            "FROM events "
            "WHERE stream_id=%s AND seq>=%s "
            "ORDER BY seq ASC",
            (stream_id, from_seq)
        )
        return [
            {
                "seq": row[0],
                "type": row[1],
                "data": json.loads(row[2]),
                "occurred_at": row[3].isoformat()
            }
            for row in cursor.fetchall()
        ]
```

---

### ⚖️ Comparison Table

| Property | Traditional CRUD | Event Sourcing |
|---|---|---|
| **Storage** | Current state | All events (history) |
| **Reads** | Direct table query | Replay events (or snapshot) |
| **History** | Lost on update | Complete audit trail |
| **Temporal queries** | Impossible | Any point in time |
| **Storage size** | Compact | Grows indefinitely |
| **Complexity** | Low | High |
| **Schema evolution** | ALTER TABLE | Upcasting + versioned handlers |
| **Debugging** | Limited | Full event replay |

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| "Event Sourcing is just an audit log" | An audit log is a secondary concern, added after the fact. In Event Sourcing, the event log IS the primary data store. The current state is derived from it. The audit trail is a consequence, not the purpose. |
| "Events are messages" | Events in Event Sourcing are facts about past state changes (immutable). Messages in messaging systems are commands or notifications (may be consumed and discarded). They overlap but serve different purposes. |
| "Event Sourcing is required for CQRS" | CQRS only requires separate read/write models. The write model can be a normal relational database with CQRS using database replication for read models. Event Sourcing is one way to implement the write model in CQRS. |
| "You can fix a bug by correcting past events" | Events are immutable. You fix bugs by appending compensating events (the equivalent of an accounting correction entry) and replaying all events through the fixed handler. You never modify existing events. |

---

### 🚨 Failure Modes & Diagnosis

**Event Stream Grows Unbounded**

**Symptom:** Loading an order aggregate takes 30+
seconds. CPU spikes on every command. The event
store has 10,000+ events per order stream.

**Root Cause:** No snapshot mechanism. Replay of
10,000 events per load is O(N) every time. High-
volume aggregates (orders with many status changes,
shopping carts with many add/remove actions) grow
indefinitely without snapshots.

**Diagnosis:**
```sql
-- Find streams with high event counts:
SELECT stream_id, COUNT(*) as event_count
FROM events
GROUP BY stream_id
ORDER BY event_count DESC
LIMIT 20;
-- If any stream has >500 events: snapshot candidate

-- Check load time distribution:
-- Application metric: aggregate_load_duration_ms
-- histogram_quantile(0.99, aggregate_load_duration_ms)
-- If P99 > 100ms: snapshot needed
```

**Fix:**
1. Add snapshot table:
```sql
CREATE TABLE aggregate_snapshots (
    stream_id    VARCHAR(255) PRIMARY KEY,
    seq          BIGINT NOT NULL,
    state        JSONB NOT NULL,
    created_at   TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
```
2. Save snapshot after every N events (N=100).
3. On load: query snapshot first, then replay events
   from snapshot.seq+1 to current.

---

### 🔗 Related Keywords

**Prerequisites:** `Idempotency` (DST-018),
`Eventual Consistency` (DST-028),
`Saga Pattern` (DST-043), `CQRS` (DST-044)

**Builds On This:** Event-Driven Architecture,
Apache Kafka (event log as distributed event store)

---

### 📌 Quick Reference Card

```
┌─────────────────────────────────────────────────────────┐
│ STORE      │ Append-only event log (never mutate)       │
│ STATE      │ Derived by replaying events                │
│ SNAPSHOT   │ Checkpoint every N events to speed replay  │
├────────────┼────────────────────────────────────────────┤
│ BENEFITS   │ Audit trail, temporal queries, CQRS feed   │
│ COSTS      │ Complexity, storage growth, schema evo     │
├────────────┼────────────────────────────────────────────┤
│ KEY RULE   │ Events are immutable: never edit, never    │
│            │ delete; correct with compensating events   │
│ CONCURRENCY│ Optimistic: check expected_version on write│
├────────────┼────────────────────────────────────────────┤
│ EVOLVE     │ Upcast old event schemas to current format │
├────────────┼────────────────────────────────────────────┤
│ ONE-LINER  │ "The event log is the truth; current state │
│            │  is a derived artifact."                  │
└─────────────────────────────────────────────────────────┘
```

---

### 💎 Transferable Wisdom

Event Sourcing makes explicit a principle that most
production systems discover through painful debugging:
you always need more history than you think. The
first time a support ticket comes in asking "how did
this account get into this state?" and you cannot
answer, you wish you had event sourcing. The pattern
is not always worth its complexity cost, but the
desire for audit trails, temporal queries, and event-
driven integration is universal. Partial solutions
(audit tables, change logs, database triggers) are
common alternatives that provide some of the benefit
with less architectural complexity. Know when the
full event sourcing pattern is warranted vs when a
simpler audit log suffices.

---

### 💡 The Surprising Truth

Martin Fowler, who popularized Event Sourcing in the
software community, explicitly warns against applying
it broadly in his writing. The pattern has significant
operational overhead: event schema evolution is
notoriously difficult (you can never delete an event
type once used), rebuilding projections from a large
event log takes hours in large systems, and debugging
becomes harder if the event log is the source of
truth but read models are what developers query day-
to-day. Fowler's position: Event Sourcing is worth
the cost only when the business genuinely needs the
audit trail, temporal queries, or event-driven
integration - not as a default architecture. The most
successful Event Sourcing implementations are in
financial services and healthcare, where the audit
requirements are legally mandated, not a nice-to-have.

---

### ✅ Mastery Checklist

1. [IMPLEMENT] Write an Order aggregate with
   apply(event) for OrderPlaced, PaymentReceived, and
   ItemShipped. Write load_order(id) that replays
   events to reconstruct state.
2. [DESIGN] Add snapshot support to the event store:
   write() saves state after every 100 events; load()
   reads the latest snapshot and replays remaining events.
3. [HANDLE] An event schema changes: OrderPlaced v1
   has `price` field; v2 has `amount` (object with
   value and currency). Implement an upcast function.
4. [DIAGNOSE] Orders are loading slowly. Write the
   SQL to identify streams with excessive event counts
   and describe the fix.
5. [COMPARE] Give three scenarios where a simple audit
   log table is a better choice than full event sourcing.
