---
id: SYD-058
title: CQRS
category: System Design
tier: tier-5-distributed-architecture
folder: SYD-system-design
difficulty: ★★★
depends_on: SYD-033, SYD-057
used_by: ""
related: SYD-033, SYD-057, SYD-059, SYD-031
tags:
  - architecture
  - cqrs
  - read-write
  - design
  - advanced
status: complete
version: 4
layout: default
parent: "System Design"
grand_parent: "Technical Dictionary"
nav_order: 58
permalink: /syd/cqrs/
---

# SYD-058 - CQRS

⚡ TL;DR - CQRS (Command-Query Responsibility Segregation)
separates the write model (commands that change state)
from the read model (queries that return data). Instead of
one data model serving both reads and writes, you have two:
a write-optimized store (normalized, consistent) and one or
more read-optimized stores (denormalized, fast, eventually
consistent). Commands return nothing (or just an ID).
Queries return data but never change state. The key benefit:
you can scale reads and writes independently, and optimize
each model for its specific access patterns.

| #058 | Category: System Design | Difficulty: ★★★ |
|:---|:---|:---|
| **Depends on:** | Database Internals, Event-Driven Architecture | |
| **Related:** | Database Internals, Event-Driven Architecture, Event Sourcing, Sharding | |

---

### 🔥 The Problem This Solves

An e-commerce site has two very different access patterns:
- Writes: one order at a time, must be consistent
  (can't oversell), complex business rules
- Reads: 1,000x more reads than writes, need denormalized
  data (product name + price + image + stock in one query),
  must be fast (< 50ms)

One relational model with JOINs cannot serve both:
- Normalize for writes → slow reads (many JOINs)
- Denormalize for reads → write anomalies (data duplicated
  in many rows, hard to keep consistent)

CQRS solution: write to a normalized model (PostgreSQL),
project changes to a denormalized read model (Elasticsearch
or Redis). Reads are blazing fast; writes are strongly
consistent.

---

### 📘 Textbook Definition

**CQRS (Command-Query Responsibility Segregation):**
An architectural pattern by Greg Young (2010) that
separates the interfaces for reading and writing
data. Commands mutate state and return nothing.
Queries read state and never mutate anything.

**Command:** A request to change the system state.
Named in imperative: PlaceOrder, CancelOrder.
Returns void (or just the ID of the new entity).
Validated against business rules before processing.

**Query:** A request to read data.
Returns a DTO (Data Transfer Object) optimized for
the caller's view. Never modifies state.

**Projection (read model):** A denormalized view of
state, built by consuming events produced by the
write side. Optimized for a specific query pattern.
May lag behind the write side (eventual consistency).

---

### ⏱️ Understand It in 30 Seconds

**One line:**
Write model: normalized, consistent. Read model:
denormalized, fast. Two separate models; one system.

**One analogy:**
> A library's catalog system:
> When you return a book (command), the librarian updates
> a precise internal database (write model): which shelf,
> which copy, which borrower returned it.
> When you search for a book (query), you use a separate
> index card system (read model): organized by title, author,
> subject - optimized for lookup speed, not for tracking
> individual copies.
> The index card system is periodically updated from the
> internal database - it may be slightly out of date
> (eventual consistency), but it answers search queries
> in seconds.

**One insight:**
CQRS is not about having two databases. It is about
acknowledging that the write use case and the read use case
have genuinely different requirements. Trying to serve both
with one model forces compromises that hurt both. The
complexity cost is real (two models to maintain, eventual
consistency to reason about), so CQRS is not the right
choice for simple CRUD applications with balanced read/write
loads.

---

### 🔩 First Principles Explanation

**THE TWO SIDES OF CQRS:**
```
WRITE SIDE (Command Model):
  Input: PlaceOrder command
  Validate: business rules (stock available, payment valid)
  Execute: update normalized state
  Output: emit domain event (OrderPlaced)
  Returns: nothing (or order_id only)
  
  Database: normalized relational (PostgreSQL)
  Consistency: strong (ACID transactions)
  Optimization: optimized for correct, consistent writes

READ SIDE (Query Model):
  Input: GetOrderHistory query
  Returns: pre-computed, denormalized view
  
  Database: denormalized (Elasticsearch, Redis, DynamoDB)
  Consistency: eventual (lags behind write side by
    milliseconds to seconds)
  Optimization: optimized for fast reads
  
SYNCHRONIZATION (how read model is updated):
  Option 1: Synchronous update (in same transaction)
    Con: read model failures block writes.
    Only use for simple cases.
    
  Option 2: Event-driven projection (recommended)
    Write side publishes event → Kafka →
    Projection worker consumes event →
    Updates read model.
    
    Pro: decoupled; read model failures don't
    affect writes.
    Con: read model lags (eventual consistency).
```

**PROJECTION DESIGN:**
```
Problem: a user's order history page needs:
  - Order date, status, items, total
  - Product name, price (at time of order)
  - Delivery address
  
Joins required in normalized model:
  orders JOIN order_items JOIN products JOIN addresses
  
With CQRS read model:
  Build one document per user:
  {
    user_id: 123,
    orders: [
      {
        order_id: "abc",
        date: "2024-01-01",
        status: "delivered",
        total: 99.99,
        items: [
          { product_name: "Widget A",
            price_at_order: 29.99,
            quantity: 2 }
        ],
        delivery_address: "123 Main St"
      }
    ]
  }
  
  Stored in Elasticsearch or MongoDB.
  One document fetch = complete order history.
  No JOINs at query time.
  Price at time of order is preserved (denormalized).
```

**COMMAND VALIDATION:**
```
Commands must pass business validation before
updating state. Validation happens on the write side.

Order placement validation:
  1. User is authenticated (identity)
  2. Product exists and is active (entity exists)
  3. Requested quantity <= available stock (invariant)
  4. User has a valid payment method (precondition)
  
If any check fails: command rejected with error.
No state changes occur.
No event emitted.
  
Validation style: rich domain model.
Entities enforce their own invariants:
  order.place() throws InsufficientStockException
  Not: if order.items > stock then return error
  
The domain model is the authoritative source of
business rules. Validation is NOT in the controller
or service layer; it is in the domain.
```

---

### 🧪 Thought Experiment

**SCALING: 1,000:1 read-to-write ratio**

An e-commerce site: 100 orders per second (writes),
100,000 product page views per second (reads).

**Without CQRS (shared model):**
PostgreSQL handles both.
Reads: 100,000 queries with JOINs → table lock contention.
Writes: 100 insertions → slow behind read backlog.
Scale horizontally: read replicas for reads.
But: read replicas still run the same JOIN-heavy queries.
Scaling reads requires more replicas (expensive).

**With CQRS:**
PostgreSQL (write): 100 writes/sec → trivial load.
Elasticsearch (read): 100K product views/sec → trivial.
Scale independently:
- Write side: 1 Postgres primary (2 replicas for HA)
- Read side: 5 Elasticsearch nodes, add more as reads grow
No coupling between scaling the read and write sides.

**Consistency tradeoff:**
After PlaceOrder, the order history projection lags by
50-200ms (Kafka consumer processing time).
If user refreshes immediately: may not see their order.
Solutions:
1. Read-your-own-writes: after placing an order, fetch
   directly from the write model (not projection) for
   the immediate post-order page.
2. Show a "Your order has been placed!" confirmation
   without showing the full history immediately.
3. Refresh the order history page after 2 seconds.

---

### 🧠 Mental Model / Analogy

> CQRS is like a specialized kitchen:
>
> The prep kitchen (write side) carefully measures
> and combines ingredients (commands). Everything is
> precise and follows strict recipes (business rules).
> The food is stored in the main fridge (write model).
>
> The serving station (read side) has pre-portioned,
> ready-to-serve dishes (projections). When a customer
> orders, the food is served immediately - no cooking
> needed. These pre-portioned dishes are periodically
> restocked from the main fridge.
>
> If you had only one kitchen serving both prep and
> customers, the kitchen would be chaotic: customers
> waiting while prep is happening, prep disrupted by
> customers asking questions.
>
> CQRS separates these concerns: precise prep (writes)
> and fast service (reads) never interfere.

---

### 📶 Gradual Depth - Five Levels

**Level 1 - What it is (anyone can understand):**
CQRS means "reads and writes use different data models."
Writes update a careful, precise database.
Reads use a pre-organized, fast lookup system.
The two are synced automatically.

**Level 2 - How to use it (junior developer):**
Define commands (PlaceOrder) and handlers.
Define queries (GetOrderHistory) and handlers.
Commands: validate, update write DB, emit event.
Queries: read from a denormalized projection (Redis,
Elasticsearch).
Projection builder: consumes events, updates read store.

**Level 3 - How it works (mid-level engineer):**
Command handler validates business rules against the
write model. On success: saves to write DB and emits
domain events. Projection consumers read events from
Kafka and update read models (one per query pattern).
Queries read from the projection - no JOINs. Idempotent
projection updates (can replay events if projection
needs to be rebuilt).

**Level 4 - Why it was designed this way (senior/staff):**
CQRS is justified when: (a) read and write patterns are
fundamentally different and one model serves both poorly,
(b) read scale vastly exceeds write scale (1000:1 is
common), (c) multiple read formats are needed for the
same data (mobile API, web API, analytics). The cost:
eventual consistency on reads (projection may lag), two
codepaths to maintain (command side + query side + projection
builders), and the cognitive overhead of explaining to
developers that "you just wrote something, and the read
model might not show it for 500ms." This is not a trivial
trade-off. CQRS is often over-applied to simple CRUD
systems where it adds complexity without benefit.

**Level 5 - Mastery (distinguished engineer):**
CQRS is most powerful when combined with Event Sourcing:
the write model stores events (not state), and multiple
projections are built from the event log, each optimized
for a different query pattern. This gives infinite flexibility:
add a new read model by building a new projection from the
same event log. Microsoft Azure's architecture for
CosmosDB Change Feed is essentially CQRS at the infrastructure
level: change feed = event stream from the write model;
consumers build materialized views (projections) in secondary
stores. This pattern - "change data capture into projections"
- is CQRS even if not named as such.

---

### ⚙️ How It Works (Mechanism)

```
┌──────────────────────────────────────────────────────┐
│ CQRS FLOW                                           │
│                                                      │
│ CLIENT                                              │
│  │─── POST /orders (command) ──────────────────────►│
│  │                                                   │
│  │   COMMAND HANDLER                               │
│  │     Validate business rules                     │
│  │     Update write DB (PostgreSQL, ACID)          │
│  │     Emit event: OrderPlaced → Kafka             │
│  │     Return: 202 Accepted, order_id              │
│  │◄── order_id ────────────────────────────────────│
│                                                      │
│         KAFKA (event stream)                        │
│              │                                      │
│              ▼                                      │
│   PROJECTION WORKER (async)                        │
│     Consumes OrderPlaced event                     │
│     Updates Elasticsearch: order history doc       │
│     Updates Redis: order count for user            │
│     Commits Kafka offset                           │
│                                                      │
│  CLIENT (later)                                    │
│  │─── GET /orders/history (query) ─────────────────►│
│  │                                                   │
│  │   QUERY HANDLER                                 │
│  │     Read from Elasticsearch (no joins)          │
│  │     Return pre-built order history doc          │
│  │◄── Order history (fast) ────────────────────────│
└──────────────────────────────────────────────────────┘
```

---

### 💻 Code Example

**Example 1 - CQRS command and query handlers**
```python
from dataclasses import dataclass
from typing import List
import uuid

# ======= WRITE SIDE (Command Model) =======

@dataclass
class PlaceOrderCommand:
    user_id: str
    items: List[dict]
    payment_method_id: str

@dataclass
class OrderPlacedEvent:
    event_id: str
    order_id: str
    user_id: str
    items: List[dict]
    total: float

class OrderCommandHandler:
    def __init__(self, write_db, event_bus):
        self.write_db = write_db
        self.event_bus = event_bus

    def handle_place_order(
            self, cmd: PlaceOrderCommand) -> str:
        # Validate business rules
        for item in cmd.items:
            stock = self.write_db.get_stock(
                item["product_id"])
            if stock < item["quantity"]:
                raise ValueError(
                    f"Insufficient stock: "
                    f"{item['product_id']}")

        # Calculate total
        total = sum(
            self.write_db.get_price(item["product_id"])
            * item["quantity"]
            for item in cmd.items
        )

        # Persist (write model)
        order_id = str(uuid.uuid4())
        self.write_db.create_order({
            "order_id": order_id,
            "user_id": cmd.user_id,
            "items": cmd.items,
            "total": total,
            "status": "PENDING"
        })

        # Emit event (async projection update)
        self.event_bus.publish(OrderPlacedEvent(
            event_id=str(uuid.uuid4()),
            order_id=order_id,
            user_id=cmd.user_id,
            items=cmd.items,
            total=total
        ))
        return order_id  # Return only ID


# ======= READ SIDE (Query Model) =======

@dataclass
class OrderHistoryQuery:
    user_id: str
    page: int = 1
    page_size: int = 20

class OrderQueryHandler:
    def __init__(self, read_store):
        # read_store = Elasticsearch, Redis, etc.
        self.read_store = read_store

    def handle_order_history(
            self, query: OrderHistoryQuery) -> dict:
        # Direct lookup in denormalized projection
        # No JOINs, no heavy queries
        return self.read_store.get_order_history(
            user_id=query.user_id,
            page=query.page,
            page_size=query.page_size
        )


# ======= PROJECTION BUILDER (Event Consumer) =======

class OrderHistoryProjection:
    def __init__(self, read_store):
        self.read_store = read_store

    def on_order_placed(
            self, event: OrderPlacedEvent):
        """
        Update the read model when an order is placed.
        Called asynchronously (Kafka consumer).
        Must be idempotent.
        """
        # Idempotency: skip if already projected
        if self.read_store.event_processed(
                event.event_id):
            return

        self.read_store.append_order_to_history(
            user_id=event.user_id,
            order={
                "order_id": event.order_id,
                "date": "now",
                "total": event.total,
                "status": "PENDING",
                "items": event.items
            }
        )
        self.read_store.mark_event_processed(
            event.event_id)
```

**Example 2 - Shared model with JOINs (BAD)**
```python
# BAD: Single model - slow for reads, hard to scale

def get_order_history_bad(user_id: str) -> list:
    # This JOIN query runs on the same DB as writes
    # Under load: table locks, slow JOINs
    # Adding columns for the UI requires changing
    # the core orders table (write-optimized)
    return db.query("""
        SELECT o.order_id, o.status, o.created_at,
               oi.quantity, p.name, p.price,
               a.street, a.city
        FROM orders o
        JOIN order_items oi ON o.order_id = oi.order_id
        JOIN products p ON oi.product_id = p.product_id
        JOIN addresses a ON o.address_id = a.address_id
        WHERE o.user_id = %s
        ORDER BY o.created_at DESC
        LIMIT 20
    """, [user_id])

# GOOD: Query reads from pre-built projection (CQRS)
def get_order_history_good(user_id: str) -> dict:
    # Direct fetch from read model - no JOINs
    return elasticsearch.get(
        index="order_history",
        id=user_id  # Pre-built document per user
    )
```

---

### ⚖️ Comparison Table

| Pattern | Consistency | Read Perf | Write Perf | Complexity | Best For |
|---|---|---|---|---|---|
| **Shared model (CRUD)** | Strong | Poor (JOINs) | Good | Low | Simple CRUD, balanced R/W |
| **Read replicas** | Eventual | Better | Good | Low | Read-heavy, same data format |
| **CQRS (separate models)** | Eventual | Excellent | Excellent | High | 1000:1 R/W, multiple read formats |
| **CQRS + Event Sourcing** | Eventual | Excellent | Good | Very High | Audit, replay, multiple projections |

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| CQRS requires separate databases | CQRS is a logical separation, not necessarily a physical one. For simple cases, you can have separate read and write models in the same database. Separate physical stores (Postgres write + Elasticsearch read) are needed when the performance requirements genuinely differ. Don't over-engineer a simple application with two separate databases for CQRS if the same Postgres with read replicas would suffice. |
| Commands can return data | A command mutates state and returns nothing (or only the ID of the created entity). If it returned data, it would be doing two things - a violation of the single responsibility principle that CQRS enforces. To get the result of a command, execute a query after it. This forces clear separation and enables the projections to be the single source of read data. |
| CQRS means eventual consistency everywhere | The read model is eventually consistent with the write model. But the write model itself can and should be strongly consistent (ACID transactions). The key is being explicit: "this read model lags by up to 500ms" is a known and acceptable trade-off. The write model still returns a consistent result when you check if stock is available; the display of stock on product pages (read model) may lag. |

---

### 🚨 Failure Modes & Diagnosis

**Read Model Drifts from Write Model (Projection Bug)**

**Symptom:**
Users see incorrect data: wrong order totals, missing
items, duplicate entries in their history. Support tickets
spike. Write model (PostgreSQL) has correct data. Read
model (Elasticsearch) shows wrong data. Inconsistency
is permanent (not just temporary lag).

**Root Cause:**
Projection builder bug: event was processed incorrectly.
Non-idempotent projection: event processed twice, count
doubled. Missing event: Kafka consumer skipped an offset
due to error, and committed the offset anyway.

**Fix - Rebuild projection from event log:**
```python
def rebuild_projection(event_bus, read_store):
    """
    Rebuild the read model from the event log.
    Kafka retains events; consumers can seek to offset 0.
    """
    # Clear the read model
    read_store.clear_order_history()
    read_store.clear_processed_events()

    # Replay all events from the beginning
    consumer = KafkaConsumer(
        "order.events",
        bootstrap_servers=["kafka:9092"],
        group_id="projection-rebuild-" + uuid4(),
        auto_offset_reset="earliest",  # Start from beginning
        enable_auto_commit=False,
    )

    projection = OrderHistoryProjection(read_store)
    for message in consumer:
        event = deserialize(message.value)
        if event["event_type"] == "OrderPlaced":
            projection.on_order_placed(event)
        consumer.commit()
        # Continue until caught up to current offset

# This is one of the key advantages of CQRS + event log:
# the read model can always be rebuilt from the event log.
# The event log is the source of truth.
```

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**
- `Database Internals` - understanding how ACID
  transactions work is needed to appreciate why the
  write model uses a normalized relational database
- `Event-Driven Architecture` - the projection update
  mechanism relies on events flowing from write to read

**Builds On This (learn these next):**
- `Event Sourcing` - combines with CQRS: the write model
  stores all state changes as events; projections are
  built from the event log
- `Sharding` - the read model (Elasticsearch) uses sharding
  for horizontal scalability

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ CORE IDEA   │ Commands: mutate state, return nothing.   │
│             │ Queries: read state, never mutate.        │
├─────────────┼──────────────────────────────────────────  │
│ WRITE MODEL │ Normalized, ACID, strongly consistent.   │
│             │ PostgreSQL, MySQL. Business rules enforced│
├─────────────┼──────────────────────────────────────────  │
│ READ MODEL  │ Denormalized, fast, eventually consistent.│
│             │ Elasticsearch, Redis, DynamoDB.           │
├─────────────┼──────────────────────────────────────────  │
│ SYNC        │ Write side emits events → Kafka →        │
│             │ Projection builder updates read store.   │
├─────────────┼──────────────────────────────────────────  │
│ PROJECTION  │ Must be idempotent (event may replay).   │
│             │ Can be rebuilt from event log.           │
├─────────────┼──────────────────────────────────────────  │
│ WHEN TO USE │ 1000:1 R/W ratio. Multiple read formats. │
│             │ Reads and writes need different models.  │
├─────────────┼──────────────────────────────────────────  │
│ ONE-LINER   │ "Commands change state. Queries read     │
│             │  pre-built projections. Separate models."│
├─────────────┼──────────────────────────────────────────  │
│ NEXT        │ Event Sourcing → Circuit Breaker         │
└──────────────────────────────────────────────────────────┘
```

**If you remember only 3 things:**
1. Commands mutate state and return nothing. Queries read
   state and never mutate. This hard separation is the
   core of CQRS - it forces you to build models optimized
   for each concern.
2. The read model (projection) is built by consuming events
   from the write side. It is eventually consistent - lags
   by milliseconds to seconds. This is a known trade-off,
   not a bug. Handle it explicitly (e.g., read-your-own-writes
   for the immediate post-write result).
3. Projections can always be rebuilt from the event log.
   This is the safety net: if the read model has bugs or
   drifts, replay all events from the beginning to rebuild
   a correct projection. This requires Kafka to retain
   events long-term.

**Interview one-liner:**
"CQRS: commands (PlaceOrder) update the write model (normalized PostgreSQL, ACID),
emit domain events to Kafka. Queries (GetOrderHistory) read from a denormalized
projection (Elasticsearch/Redis), built asynchronously by a projection consumer
that processes events. Read model is eventually consistent (lags 50-500ms). Benefit:
scale reads and writes independently (1000:1 ratio), add read formats without
changing write side. Cost: eventual consistency, two codepaths, projection must
be idempotent (events may replay). Rebuild projection from event log when drift
detected."
