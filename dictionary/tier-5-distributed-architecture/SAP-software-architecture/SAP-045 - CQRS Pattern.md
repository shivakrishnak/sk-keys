---
id: SAP-036
title: CQRS Pattern
category: Software Architecture Patterns
tier: tier-5-distributed-architecture
folder: SAP-software-architecture
difficulty: ★★★
depends_on: SAP-009, SAP-065, SAP-068
used_by: SAP-018
related: SAP-018, SAP-009, SAP-068
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
nav_order: 45
permalink: /software-architecture/cqrs-pattern/
---

# SAP-008 - CQRS Pattern

⚡ TL;DR - CQRS separates the model used to read data from the model used to write data, allowing each to be independently optimised.

| Field          | Value                     |
| -------------- | ------------------------- |
| **Depends on** | SAP-009, SAP-065, SAP-068 |
| **Used by**    | SAP-018                   |
| **Related**    | SAP-018, SAP-009, SAP-068 |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
Your e-commerce application uses a single `Order` domain model for both writing orders (place, cancel, ship) and reading order data (customer history list, admin dashboard, reports). The write model needs strict consistency, locking, and aggregate validation. The read model needs denormalised, joined views across many tables for dashboard performance. They share the same database schema. To optimise the dashboard query, you add indexes that slow down writes. To support a new write-side aggregate rule, you add columns that complicate reads. The model can't simultaneously be optimised for both concerns.

**THE BREAKING POINT:**
The dashboard loads in 8 seconds because the write-optimised schema requires 12 table joins. Adding an index to speed reads causes write throughput to drop 40%. Every optimisation for one side damages the other.

**THE INVENTION MOMENT:**
This is exactly why CQRS was created - to use a completely different model, different schema, and potentially different database for reads versus writes, allowing each side to be perfectly optimised for its own workload.

**EVOLUTION:**
Greg Young coined CQRS around 2010, explicitly extending Bertrand Meyer's and Martin Fowler's Command-Query Separation (CQS) principle from the method level to the system/service level. Udi Dahan co-developed many of the practical patterns. Young's key contribution was the observation that once command and query objects are separated, each can use completely different persistence strategies. CQRS became widely known through DDD community discussions on InfoQ and cqrs.nu. Today, frameworks like Axon (Java) and MediatR with Entity Framework (C#) make the pattern accessible for production use.

---

### 📘 Textbook Definition

Command Query Responsibility Segregation (CQRS) is an architectural pattern, introduced by Greg Young building on Bertrand Meyer's Command-Query Separation principle, that divides a service into two distinct models: a Command model that handles writes (create, update, delete) with a write-optimised schema maintaining strict domain consistency, and a Query model that handles reads with a read-optimised schema (denormalised, pre-aggregated, or different database technology). The two models are kept synchronised through domain events or event sourcing.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
Use one database model for writing and a different, optimised one for reading.

**One analogy:**

> A library keeps two systems: the cataloguing system used by librarians to track acquisitions, condition, and location (write side - precise, consistent, normalised) and the card catalogue or search terminal used by visitors to find books (read side - denormalised, fast, pre-indexed by subject, author, keyword). Both systems describe the same books but are optimised for completely different users.

**One insight:**
The non-obvious truth: in most applications, reads outnumber writes by 10:1 to 100:1. CQRS acknowledges this asymmetry explicitly rather than forcing both workloads to share a schema designed for neither.

---

### 🔩 First Principles Explanation

**CORE INVARIANTS:**

1. Commands change state and return nothing (or just an acknowledgment). They go through the write model, enforce domain rules, and emit events.
2. Queries read state and return data. They never change state. They go through the read model.
3. The read model is a projection of the write model, updated asynchronously (eventually consistent) or synchronously depending on requirements.

**DERIVED DESIGN:**

```
┌──────────────────────────────────────────────────────────┐
│                    CQRS OVERVIEW                         │
├──────────────────────────────────────────────────────────┤
│                                                          │
│  Client                                                  │
│    │                                                     │
│    ├─── Command (write) ─────────────────────────────    │
│    │       ↓                                            │
│    │  Command Handler                                   │
│    │       ↓                                            │
│    │  Write Model (domain objects, strict rules)        │
│    │       ↓                                            │
│    │  Write DB (normalised, consistent)                 │
│    │       ↓ publishes domain event                     │
│    │  ────────────────────────────────────              │
│    │       ↓ event projection                           │
│    │  Read Model (denormalised views)                   │
│    │       ↓                                            │
│    │  Read DB (optimised for queries)                   │
│    │                                                    │
│    └─── Query (read) ─────────────────────────────────  │
│            ↓                                            │
│       Query Handler → Read DB → Return DTO              │
│                                                         │
└──────────────────────────────────────────────────────────┘
```

**THE TRADE-OFFS:**
**Gain:** Read side can use a completely different technology (Elasticsearch, Redis, read replica, materialised view). Write side enforces domain rules without read-side performance pressure. Each side scales independently.
**Cost:** Eventual consistency between write and read sides. A client writes data and immediately queries - the read model may not yet reflect the write. This is confusing and requires careful UX handling. Operational complexity doubles: two data stores to maintain, sync, and monitor.

---

### 🧪 Thought Experiment

**SETUP:**
An e-commerce system tracks 10 million orders. The write side places and updates orders - strict consistency required. The admin dashboard shows "orders by status by region by day" - needs sub-second response.

**WHAT HAPPENS WITHOUT CQRS:**
The dashboard query JOINs `orders`, `order_items`, `customers`, `regions`, and `products` - 5 tables across 10 million rows. It runs in 12 seconds. You add a covering index - writes slow down from 5ms to 18ms average. The index fills 40GB. The database now serves two incompatible workloads simultaneously: high-throughput transactional writes and massive analytical reads.

**WHAT HAPPENS WITH CQRS:**
The write side maintains the `orders` table (normalised, write-optimised). Every time an order changes status, a `OrderStatusChangedEvent` is published. A projection handler subscribes and updates a `order_dashboard_summary` materialised view - pre-aggregated by status, region, and date. The dashboard queries this view: 1 table, pre-computed, sub-100ms. Write performance is unaffected. The read model can be dropped and rebuilt from the event history at any time.

**THE INSIGHT:**
CQRS works because reads and writes have fundamentally different consistency requirements. Writes need instant consistency; reads are often acceptable with 100–500ms delay. Once you acknowledge this asymmetry, maintaining two optimised models becomes obviously correct.

---

### 🧠 Mental Model / Analogy

> Think of a large newspaper. The editorial room (write side) maintains the master record: every article, correction, and update with full audit history, strict fact-checking, editorial approval. The printing room (read side) takes that record and produces the final newspaper - optimised for reading, laid out beautifully, perhaps slightly behind the editorial room by a few hours.

- "Editorial room master record" → Write model (write-optimised database)
- "Printed newspaper" → Read model (read-optimised projection)
- "Publishing event" → Domain event that synchronises the two
- "Article correction" → Command (write) that updates the master
- "Reader browsing" → Query (read) that hits the printed version

Where this analogy breaks down: A newspaper reader accepts that news is from this morning, not this second. In CQRS, the lag is measured in milliseconds to seconds - but some UX scenarios (e.g., "show me the order I just placed") require special handling to bridge this gap.

---

### 📶 Gradual Depth - Four Levels

**Level 1 - What it is (anyone can understand):**
CQRS means you use one database design for saving data and a different, faster-to-read design for showing data. They stay synchronised automatically.

**Level 2 - How to use it (junior developer):**
When you receive a command (e.g., `PlaceOrderCommand`), process it through a write handler that validates business rules and saves to the write database. After saving, publish a domain event. A separate event handler subscribes to domain events and updates the read database (a denormalised, pre-joined view). Queries go directly to the read database - no joins, no aggregation at query time.

**Level 3 - How it works (mid-level engineer):**
The projection layer is the heart of CQRS. When an event arrives (`OrderPlacedEvent`), the projector inserts or updates rows in the read store. Projectors are idempotent - replaying the same event produces the same read model state. The read model can be rebuilt from scratch by replaying all events. This means the read model has no permanent state of its own - it's a derived view. Common read stores: PostgreSQL read replica (simple CQRS), Elasticsearch (full-text search), Redis (high-speed dashboard), or MongoDB (document views).

**Level 4 - Why it was designed this way (senior/staff):**
Greg Young's insight was that CQS (Meyer's principle) applied at the object level doesn't scale to the system level. At system scale, you need separate execution paths, not just separate methods. The event-sourcing connection is natural: if you already store events as the source of truth (write side), projections are just fold operations over the event stream - you can project any read model you need from the same event history. At Google/Netflix scale, CQRS enables the read side to be geographically distributed (nearest region serves queries) while the write side maintains global consistency.

---

### ⚙️ How It Works (Mechanism)

**Write path (command processing):**

1. Client sends `PlaceOrderCommand`.
2. Command handler loads `Order` aggregate from write store.
3. `Order.place()` validates business rules, applies state changes.
4. Handler persists the updated aggregate to write store.
5. Handler publishes `OrderPlacedEvent` to event bus (Kafka, RabbitMQ, in-process).

**Read path (query processing):**

1. Projector subscribes to `OrderPlacedEvent`.
2. Projector inserts a pre-joined row into `order_summary_view`.
3. Client sends `GetOrderSummaryQuery`.
4. Query handler reads directly from `order_summary_view` - no joins.
5. Returns a DTO. No domain model, no business rules.

```
┌──────────────────────────────────────────────────────────┐
│                   CQRS FULL FLOW                         │
├──────────────────────────────────────────────────────────┤
│                                                          │
│  WRITE PATH:                                             │
│  PlaceOrderCommand                                       │
│    → CommandHandler (validates domain rules)             │
│    → Write DB (orders table - normalised)                │
│    → OrderPlacedEvent published to event bus             │
│                          ↓                               │
│  SYNC PATH (projection):                                 │
│    OrderProjector.on(OrderPlacedEvent)                   │
│    → Read DB (order_summary - denormalised)  ← YOU HERE  │
│                          ↓                               │
│  READ PATH:                                              │
│  GetOrderDashboardQuery                                  │
│    → QueryHandler (no business logic)                    │
│    → Read DB (single-table scan)                         │
│    → OrderDashboardDto returned                          │
│                                                          │
└──────────────────────────────────────────────────────────┘
```

---

### 🔄 The Complete Picture - End-to-End Flow

**NORMAL FLOW:**

```
POST /orders (PlaceOrderCommand)
  → CommandHandler → Order.place() [domain rules]
  → Write DB (PostgreSQL) persists
  → OrderPlacedEvent → Kafka topic
  → OrderProjector consumes event
  → Read DB (Elasticsearch) upsert  ← YOU ARE HERE
  → GET /orders/dashboard (query)
  → QueryHandler → Read DB → DTO → HTTP 200
```

**FAILURE PATH:**

```
OrderProjector fails (Kafka lag or DB down)
  → Read model falls behind write model
  → Queries return stale data (eventual consistency gap)
  → Monitor: consumer lag metric exceeds threshold alert
  → Rebuild: replay events from Kafka to rebuild read model
```

**WHAT CHANGES AT SCALE:**
At 1M events/day, the projection process must be idempotent and parallelisable. At 10M events/day, you need multiple projection consumers and partitioned event streams. At 1B events, the read model must be rebuilt from a checkpoint (recent snapshot + delta events) rather than from the beginning. The write model typically stays small and fast regardless of read volume.

---

### 💻 Code Example

**Example 1 - Command handler (write side):**

```java
@Component
@RequiredArgsConstructor
public class PlaceOrderCommandHandler {
    private final OrderRepository writeRepo;  // write model
    private final DomainEventPublisher events;

    @Transactional
    public OrderId handle(PlaceOrderCommand cmd) {
        Order order = Order.place(
            cmd.customerId(), cmd.items()
        );
        writeRepo.save(order);
        // Publish event to sync read model
        events.publish(new OrderPlacedEvent(
            order.id(), order.customerId(),
            order.total(), order.status(),
            Instant.now()
        ));
        return order.id();
    }
}
```

**Example 2 - Event projector (read model sync):**

```java
@Component
@RequiredArgsConstructor
public class OrderSummaryProjector {
    private final OrderSummaryRepository readRepo;

    @EventHandler  // subscribes to OrderPlacedEvent
    public void on(OrderPlacedEvent event) {
        // Insert/update denormalised read model
        OrderSummaryEntity summary =
            new OrderSummaryEntity(
                event.orderId().value(),
                event.customerId().value(),
                event.total(),
                event.status().name(),
                event.occurredAt()
            );
        readRepo.save(summary);
        // No joins at query time - everything pre-joined
    }
}
```

**Example 3 - Query handler (read side - pure data retrieval):**

```java
@Component
@RequiredArgsConstructor
public class GetOrderSummaryQueryHandler {
    // Read from the denormalised store - NOT the write DB
    private final OrderSummaryRepository readRepo;

    public OrderSummaryDto handle(
            GetOrderSummaryQuery query) {
        return readRepo.findById(query.orderId())
            .map(OrderSummaryDto::from)
            .orElseThrow(() ->
                new OrderNotFoundException(query.orderId())
            );
        // No domain logic, no business rules, no joins
    }
}
```

---

### ⚖️ Comparison Table

| Approach            | Read perf | Write perf | Consistency    | Complexity | Best For                              |
| ------------------- | --------- | ---------- | -------------- | ---------- | ------------------------------------- |
| **CQRS**            | Excellent | Excellent  | Eventual       | High       | High-scale, read/write asymmetry      |
| Single model (CRUD) | Good      | Good       | Immediate      | Low        | Simple apps, balanced read/write      |
| Read replica only   | Good      | Excellent  | Eventual       | Medium     | Read scaling without model split      |
| Materialised views  | Good      | Excellent  | Near-real-time | Medium     | DB-level projection without event bus |

**How to choose:** Use CQRS when read and write workloads have very different performance characteristics, when reads significantly outnumber writes, or when the read model needs fundamentally different structure (document, graph, search index). Avoid CQRS for simple CRUD applications - the operational and consistency complexity will not be offset by the performance benefit.

---

### ⚠️ Common Misconceptions

| Misconception                                  | Reality                                                                                                                    |
| ---------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------- |
| CQRS requires event sourcing                   | CQRS and event sourcing are independent - you can have CQRS with a traditional database using domain events                |
| CQRS means two separate databases              | You can implement CQRS with materialised views in the same database - it's a logical, not always physical, separation      |
| Queries should never have any side effects     | Queries must never change observable state, but side effects like audit logs are accepted in many implementations          |
| The read model is always eventually consistent | Synchronous projections (same transaction) make the read model immediately consistent - eventual consistency is optional   |
| CQRS eliminates the need for transactions      | The write side still requires transactions; the challenge is that write and read side updates cannot be in one transaction |

---

### 🚨 Failure Modes & Diagnosis

**Projection lag (read model falling behind write)**

**Symptom:** Users see stale data. "I just placed an order but it's not in my order history." Consumer lag increases over time.

**Root Cause:** Projection consumer is slower than the event production rate. Backpressure builds in the event queue.

**Diagnostic Command / Tool:**

```bash
# Kafka consumer lag per partition
kafka-consumer-groups.sh \
  --bootstrap-server localhost:9092 \
  --describe --group order-projector-group
# Look for LAG column exceeding acceptable threshold
```

**Fix:** Scale projector consumers horizontally. Partition events by aggregate ID so multiple consumers can work in parallel without ordering conflicts.

**Prevention:** Set alerting on consumer lag > 1000 events; design projectors to be idempotent so they can safely replay.

---

**Projector not idempotent (duplicate events)**

**Symptom:** Read model shows duplicate rows or incorrect aggregated counts after a projector restart.

**Root Cause:** The projector's `on(event)` method inserts instead of upserts, so replayed events create duplicates.

**Diagnostic Command / Tool:**

```bash
# Check for duplicate order summaries
SELECT order_id, COUNT(*) as cnt
FROM order_summary
GROUP BY order_id
HAVING COUNT(*) > 1;
```

**Fix:** Use upsert (INSERT ON CONFLICT DO UPDATE) in all projector write operations. Include event ID in the upsert key to deduplicate.

**Prevention:** Write projectors using UPSERT semantics by default. Test projectors by replaying the same event twice and asserting the result is identical.

---

**Write model bleeding into query handlers**

**Symptom:** Query handlers call domain services, load full aggregates, and apply business rules before returning data. Read latency increases as business logic grows.

**Root Cause:** The CQRS boundary isn't respected - developers add logic to query handlers that belongs in projectors (at projection time, not query time).

**Diagnostic Command / Tool:**

```bash
# Query handlers with non-trivial logic
grep -rn "Service\|if\|validate" \
  src/main/java/**/query/*Handler.java
```

**Fix:** Move all calculation and transformation logic into the projector. The query handler should be a simple key-value or filter lookup on a pre-computed view.

**Prevention:** Query handlers should have exactly one job: retrieve and map a pre-computed record. Any logic in a query handler is a smell.

---

### � Transferable Wisdom

**Reusable Engineering Principle:** Separating read and write paths allows each to be optimised independently. This principle appears wherever read and write workloads have fundamentally different characteristics - the optimisation strategies for "retrieve current state quickly" and "ensure a state transition is valid and atomic" are incompatible when combined in a single model.

**Where else this pattern appears:**

- **Database read replicas:** the primary database handles writes with full transaction consistency; read replicas serve queries with eventual consistency and read-scale - the architectural pattern that CQRS formalises at the application level already exists at the database infrastructure level.
- **DNS resolution:** write operations (zone changes) go through the authoritative nameserver with full validation; reads are served by distributed caching resolvers with eventual consistency - the same asymmetric read/write design.
- **HTAP databases:** Hybrid Transactional/Analytical Processing (TiDB, Google Spanner) separates row-oriented OLTP storage (writes) from columnar OLAP storage (reads) at the engine level - the same CQRS principle applied at the storage layer.

---

### 💡 The Surprising Truth

CQRS does not require Event Sourcing. This is the single most common misconception about CQRS. A simple CQRS implementation uses one SQL database, with the write side using normalised tables (for integrity) and the read side using materialised views or denormalised query tables (for performance). Event Sourcing is one implementation strategy for the write side - a powerful combination but not a requirement. Most production CQRS systems use a simpler, database-only approach with no event store.

---

### �🔗 Related Keywords

**Prerequisites (understand these first):**

- SAP-009 - Command-Query Separation (the method-level principle that CQRS extends to the architectural level)
- SAP-065 - Domain Model (the write side typically uses a rich domain model with aggregate roots enforcing invariants)
- SAP-068 - Domain Events (the mechanism connecting write-side state changes to read-side projection updates)

**Builds On This (learn these next):**

- SAP-018 - Event Sourcing Pattern (frequently combined with CQRS; events become the source of truth for the write side and projectors build read models from them)

**Alternatives / Comparisons:**

- SAP-009 - Command-Query Separation (same principle at method level, not system level; simpler and with no eventual consistency)
- Single CRUD model - simpler; cannot independently optimise read and write paths; correct for most applications

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ WHAT IT IS   │ Separate write model (commands) from      │
│              │ read model (queries), each optimised      │
├──────────────┼───────────────────────────────────────────┤
│ PROBLEM IT   │ Single model can't simultaneously         │
│ SOLVES       │ optimise for writes and reads             │
├──────────────┼───────────────────────────────────────────┤
│ KEY INSIGHT  │ Reads outnumber writes; their models      │
│              │ should reflect that asymmetry             │
├──────────────┼───────────────────────────────────────────┤
│ USE WHEN     │ Read/write workload asymmetry; need       │
│              │ different schemas for read vs write       │
├──────────────┼───────────────────────────────────────────┤
│ AVOID WHEN   │ Simple CRUD; team can't manage eventual   │
│              │ consistency complexity                    │
├──────────────┼───────────────────────────────────────────┤
│ TRADE-OFF    │ Independent optimisation of each side     │
│              │ vs eventual consistency + two data stores │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "Writes need correctness;                 │
│              │  reads need speed - serve both"           │
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ Event Sourcing → Saga Pattern → Outbox   │
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** A user places an order and immediately navigates to their order history page. The write side has committed the order. The read model projector has a 200ms average lag. The user sees "No orders placed yet." What are the three architectural options to handle this UX problem, what does each cost technically, and which is most appropriate for a B2C e-commerce application with millions of users?

*Hint:* Research the "read your own writes" consistency problem documented in Amazon Dynamo and Cassandra literature - specifically the three solutions: (1) sticky sessions routing reads to the write node for that user's session, (2) version tokens/causality tokens passed in the write response and required in the subsequent read, (3) synchronous projection update for the specific user's most recent write. Each has a different consistency guarantee and scalability cost.

**Q2.** A team uses CQRS with Event Sourcing. After 3 years, the event store contains 500 million events. Rebuilding the read model from scratch now takes 8 hours. A critical bug in the projector is discovered - the read model has been wrong for 6 months. Trace step-by-step how you recover the read model, and what architectural decisions made during the initial design determine whether this recovery is possible and how long it takes.

*Hint:* Research "projection reset and replay" strategies in EventStoreDB and Axon Framework - specifically the concept of "catch-up subscriptions" and how snapshot events reduce replay time from O(total events) to O(events since last snapshot). Look at how event partitioning by aggregate stream enables parallel replay to reduce the 8-hour window.

**Q3.** A CQRS system sends domain events to update the read model via a message broker. The projector crashes after applying 3 of 10 events in a batch. When it restarts, it replays from the broker offset before the crash, potentially re-applying the first 3 events to a read model that already has them applied. What two design properties must the projector possess to handle this safely, and how are they implemented in practice?

*Hint:* Research "idempotent projectors" and "checkpointing" - specifically that the projector must store its current event position alongside the read model data in the same atomic write (so the position is never ahead of the applied state), and that applying the same event twice must produce the same result as applying it once. Look at how EventStoreDB persistent subscriptions implement at-least-once delivery and what application-level idempotency means in this context.
