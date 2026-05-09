---
layout: default
title: "CQRS Pattern"
parent: "Design Patterns"
grand_parent: "Technical Dictionary"
nav_order: 52
permalink: /design-patterns/cqrs-pattern/
id: DPT-052
category: Design Patterns
difficulty: ★★★
depends_on:
used_by:
related:
tags:
  - pattern
  - architecture
  - deep-dive
  - distributed
  - java
status: complete
version: 1
tier: tier-5-distributed-architecture
folder: DPT-design-patterns
---

# DPT-052 - CQRS Pattern

⚡ TL;DR - CQRS separates the model for reading data from the model for writing data, allowing each to be optimised independently for its specific workload.

| DPT-052 | Category: Design Patterns | Difficulty: ★★★ |
|:---|:---|:---|
| **Depends on:** | Design Patterns, Event Sourcing Pattern, Repository Pattern, Command Pattern, Domain Model | |
| **Used by:** | Event Sourcing, Microservices, System Design, Read-Heavy vs Write-Heavy Design | |
| **Related:** | Event Sourcing Pattern, Saga Pattern, Repository Pattern, Outbox Pattern, Domain Events | |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
An e-commerce platform has a single `Order` domain object that serves every use case: creating orders (writes complex validation, business rules, domain events), and displaying the order history dashboard (reads joining orders, products, addresses, discounts across 7 tables). The domain model is optimised for neither. Complex joins slow writes because they must maintain normalised consistency. Business rules slow reads because data must be restructured per query. A single slow query can block an entire domain object's transactions.

**THE BREAKING POINT:**
At scale, read traffic dwarfs write traffic (10:1 to 100:1 typical). The write model is constrained by consistency requirements (transactions, locks). Forcing reads through the same model applies those constraints to queries that do not need them. Performance and scalability of reads and writes become coupled - you cannot scale them independently.

**THE INVENTION MOMENT:**
This is exactly why CQRS (Command Query Responsibility Segregation) was formalised by Greg Young - separating the write side (Commands, complex business rules, domain integrity) from the read side (Queries, projections, denormalised views) so each can be optimised, scaled, and evolved independently.

**EVOLUTION:**
CQRS was formalised by Greg Young (2010) as a step beyond the
CQS (Command Query Separation) principle Bertrand Meyer introduced
in "Object-Oriented Software Construction" (1988). CQS is a method-
level principle; CQRS scales it to the architectural level.
Event Sourcing frequently accompanies CQRS: commands produce events
that are the source of truth; read models are projections of those
events. Axon Framework (Java) and EventStore are dedicated CQRS/ES
platforms. Cloud providers offer managed event stores (AWS
EventBridge, Azure Event Hub) that enable CQRS at infrastructure
scale without operational overhead.

---

### 📘 Textbook Definition

Command Query Responsibility Segregation (CQRS) is an architectural pattern that separates the model used to update data (Commands) from the model used to read data (Queries). Commands change state and are processed by the write model (rich domain objects, business rules, validation, event emission). Queries return data and are processed by the read model (denormalised projections, optimised views, potentially separate data stores). The two models may share a physical database or use separate stores; the conceptual separation is the defining feature.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
Read and write data through separate models - each optimised for its job.

**One analogy:**
> A restaurant has two areas: the kitchen (the write model) and the dining room service (the read model). Orders go to the kitchen where they are prepared with specialist equipment and processes. The dining room serves pre-plated, quickly accessible dishes to customers who do not touch the kitchen. CQRS is that separation: the kitchen (write model) does complex preparation; the dining room (read model) delivers quickly.

**One insight:**
The insight is not technical but semantic: reads and writes have fundamentally different requirements. Writes need consistency guarantees, business rule enforcement, and audit trails. Reads need speed, flexibility of projection, and minimal latency. Forcing both through the same model serves neither well.

---

### 🔩 First Principles Explanation

**CORE INVARIANTS:**
1. Commands change state and may fail validation - they return either success or a domain error, never data.
2. Queries only return data and never change state - a query has no side effects.
3. The read model can be a projection of the write model - it may be derived (eventually consistent) and denormalised for query efficiency.

**DERIVED DESIGN:**
From the first invariant: the write side can enforce domain invariants without worrying about query efficiency. From the second: the read side can be completely denormalised, indexed, pre-joined, or stored in a different engine (ElasticSearch, Redis, read replica) without violating any business rule. From the third: a synchronisation mechanism (event stream, CDC, eventual consistency) propagates write-side state changes to the read-side projections.

The read-side stores can be purpose-built: a document store for profile queries, an Elasticsearch index for full-text search, a Redis sorted set for leaderboards - all derived from the same write-side events.

**THE TRADE-OFFS:**
**Gain:** Independent scaling of reads and writes; read models optimised per query pattern; write model freed from query concerns.
**Cost:** Eventual consistency between write and read models (immediately vs. eventually consistent queries); operational complexity of maintaining read projections; increased overall system complexity.

---

### 🧪 Thought Experiment

**SETUP:**
An order management system handles 1,000 writes/second and 50,000 reads/second. The domain model is a PostgreSQL table with 12 columns, normalised across 7 related tables.

**WHAT HAPPENS without CQRS:**
Order list queries (joining 7 tables, aggregating discount data, formatting for UI) run at 80ms each on the primary database. Write transactions (acquiring row locks, validating inventory, publishing events) share the same connection pool. Under peak load, slowreed queries hold connections, increasing latency for writes. Since reads are 50x writes, the read workload degrades write performance. Horizontal scaling adds read replicas but the normalised schema still requires 7-table joins at 80ms.

**WHAT HAPPENS with CQRS:**
The write model is a normalised PostgreSQL schema - fast writes, clear domain model. Domain events are published to Kafka after each write. A read-side projector consumes events and maintains a denormalised ElasticSearch index: one document per order with all related data pre-joined. Order list queries hit ElasticSearch at 5ms. Writes hit PostgreSQL in isolation. Reads and writes scale independently.

**THE INSIGHT:**
CQRS is not about two databases - it is about two models that can be independently optimised after they are separated. The database choice follows from the model's requirements, not from coupling to CRUD.

---

### 🧠 Mental Model / Analogy

> Think of accounting: every financial transaction goes through a double-entry ledger (the write model - authoritative, consistent, audited). The management reports (P&L, balance sheet, cash flow) are derived projections from that ledger (read models - denormalised, pre-aggregated, optimised for decision-making). The ledger and the reports are not the same model. The reports are derived from the ledger. CQRS is that same separation: the write ledger stays consistent; the reports are derived projections.

- "Double-entry ledger" → the write model (authoritative, consistent, normalised)
- "Management reports" → read model projections (denormalised, pre-aggregated)
- "Calculating reports from the ledger" → event-driven projection building
- "Stale reports" → eventual consistency between write and read models

Where this analogy breaks down: accounting reports are usually calculated on demand (batch). CQRS read models are typically maintained continuously (event-driven) for low-latency queries.

---

### 📶 Gradual Depth - Four Levels

**Level 1 - What it is (anyone can understand):**
CQRS means having two different data models: one for changing data and one for reading data. This lets you make each model exactly right for its job - the writing model can have strict rules, and the reading model can be shaped exactly for what the screen needs to show.

**Level 2 - How to use it (junior developer):**
CQRS starts with separation of interfaces. Don't return data from command handlers. Implement a `CommandBus` and `QueryBus` separately. For a simple start: same database, separate service layer. `CreateOrderCommand` is handled by `OrderCommandService` (writes to normalised DB). `GetOrderSummaryQuery` is handled by `OrderQueryService` (reads from same DB but via a denormalised view or read-optimised query). This is "baby CQRS" - conceptual separation without physical separation.

**Level 3 - How it works (mid-level engineer):**
Full CQRS: the write side emits domain events (`OrderCreated`, `OrderItemAdded`, `OrderShipped`). Event handlers (projectors) consume these events and maintain read-side stores. Projectors are idempotent - replaying events from scratch should produce the same read model. The read model schema is designed per query (not per domain) - one projection per UI/API view. This enables zero-migration UI changes: adding a new field to a read model requires a new projector, not a database schema change on the write side.

**Level 4 - Why it was designed this way (senior/staff):**
CQRS addresses the fundamental tension in domain-driven design: a rich domain model (aggregates, value objects, invariants) is designed for correctness, not queryability. Forcing the domain model to also serve as the query model either corrupts the domain model (with query-specific denormalisation) or produces poor query performance (with complex joins across aggregate boundaries). CQRS resolves this by making the tension explicit and structural. At the data store level, CQRS enables polyglot persistence: the write store is chosen for consistency (PostgreSQL, MongoDB), the read stores are chosen for query patterns (ElasticSearch for search, Redis for counters, Cassandra for time series). The event stream (Kafka, EventStore) becomes the source of truth for projecting new read models without touching the write side.

---

### ⚙️ How It Works (Mechanism)

```
┌─────────────────────────────────────────────────────┐
│  CQRS ARCHITECTURE                                  │
│                                                     │
│  Client                                             │
│    │                                                │
│    ├─ COMMAND ──→ CommandBus                        │
│    │               │                               │
│    │             CommandHandler                    │
│    │               │                               │
│    │           Write Model (Aggregate)             │
│    │               │                               │
│    │         Domain Events emitted                 │
│    │               │                               │
│    │         Event Store / Message Bus             │
│    │               │                               │
│    │           Projector (async)                   │
│    │               │                               │
│    │      Read Model (denormalised store)          │
│    │                                               │
│    └─ QUERY ───→ QueryBus                          │
│                    │                               │
│                QueryHandler                        │
│                    │                               │
│             Read Model Store                       │
│            (ElasticSearch/Redis)                   │
│                    │                               │
│            Response (DTO)                          │
└─────────────────────────────────────────────────────┘
```

Write side flow:
1. Client sends `CreateOrderCommand`
2. `OrderCommandHandler` validates command
3. `Order` aggregate enforces business rules
4. If valid: `OrderCreated` event stored and published
5. Projectors consume `OrderCreated` asynchronously
6. Read model updated (eventual consistency)

Read side flow:
1. Client sends `GetOrderSummaryQuery(orderId)`
2. `OrderQueryHandler` reads from denormalised read store
3. Returns pre-built DTO - no joins, no computation

---

### 🔄 The Complete Picture - End-to-End Flow

**NORMAL FLOW:**
```
POST /orders (CreateOrder command)
  → CommandBus → OrderCommandHandler
  → Order aggregate validates: item in stock?
    payment method valid? address valid?
  → Order written to PostgreSQL (write store)
  → OrderCreated event published to Kafka
  → OrderProjector consumes event (async)
    [← YOU ARE HERE: eventual consistency boundary]
  → Read model (Elasticsearch) updated
  → GET /orders/summary now shows new order
```

**FAILURE PATH:**
```
Projector fails to process OrderCreated event
  → Read model temporarily stale
  → GET /orders shows old data
  → Symptom: "order not visible in dashboard"
  → Fix: projector retries event from DLQ
  → Alternatively: trigger full read model rebuild
    from event log
```

**WHAT CHANGES AT SCALE:**
At 1,000 writes/second, a single read model projector may lag. At 10,000 writes/second, read model lag becomes visible to users (seconds). At 100,000 writes/second, partitioned projectors per entity type and parallel projection rebuilds are required to maintain sub-second read model freshness. The write-side remains unaffected by read model lag - this is the key architectural benefit.

---

### 💻 Code Example

**Example 1 - CQRS command handler (Spring):**

```java
// Command: represents user intent to change state
public record CreateOrderCommand(
    UUID customerId,
    List<OrderItemDto> items,
    PaymentMethodDto payment) {}

// Command Handler: enforces domain rules, emits events
@Service
public class CreateOrderCommandHandler {
    private final OrderRepository orders;
    private final InventoryService inventory;
    private final OrderEventPublisher events;

    public UUID handle(CreateOrderCommand cmd) {
        // 1. Validate invariants
        inventory.reserveItems(cmd.items());
        // 2. Create aggregate (domain object)
        Order order = Order.create(
            cmd.customerId(), cmd.items(), cmd.payment());
        // 3. Persist write model
        orders.save(order);
        // 4. Publish domain events for projectors
        order.domainEvents().forEach(events::publish);
        return order.id();
    }
}
```

**Example 2 - CQRS query handler:**

```java
// Query: asks for data, no side effects
public record GetOrderSummaryQuery(UUID orderId) {}

// Query Handler: reads from denormalised read store
@Service
public class GetOrderSummaryQueryHandler {
    // Reads from Elasticsearch - denormalised, fast
    private final OrderReadRepository readStore;

    public OrderSummaryDto handle(GetOrderSummaryQuery q) {
        // No joins. No domain logic.
        // Pre-built projection. Typically < 5ms.
        return readStore.findSummaryById(q.orderId())
            .orElseThrow(() -> new OrderNotFoundException(
                q.orderId()));
    }
}
```

**Example 3 - Read model projector:**

```java
// Projector: subscribes to events, maintains read model
@Service
public class OrderSummaryProjector {
    private final OrderReadRepository readStore;

    @KafkaListener(topics = "order-events")
    public void on(OrderCreated event) {
        // Build denormalised document for read queries
        OrderSummaryDocument doc = new OrderSummaryDocument(
            event.orderId(),
            event.customerName(),  // denormalised
            event.items(),
            event.totalAmount(),
            event.createdAt()
        );
        readStore.save(doc);
    }

    @KafkaListener(topics = "order-events")
    public void on(OrderShipped event) {
        // Update existing document
        readStore.updateShippingStatus(
            event.orderId(),
            event.trackingNumber(),
            event.shippedAt()
        );
    }
}
```

---

### ⚖️ Comparison Table

| Pattern | Consistency | Complexity | Scalability | Best For |
|---|---|---|---|---|
| CRUD (single model) | Strong | Low | Coupled | Simple domains < 10k req/sec |
| **CQRS (same DB)** | Strong | Medium | Partially decoupled | Medium complexity, same SLA |
| CQRS (separate stores) | Eventual | High | Independent | High read:write ratio, complex queries |
| CQRS + Event Sourcing | Eventual | Very high | Very high | Audit-first, event-replay domains |

How to choose: start with CRUD. Add CQRS when read and write performance requirements diverge or when the domain model becomes incompatible with query requirements. Add separate read stores only when read queries require structures incompatible with the write store.

---

### 🔁 Flow / Lifecycle

```
┌──────────────────────────────────────────────────┐
│  COMMAND LIFECYCLE                               │
│                                                  │
│  Receive → Validate → Execute → Emit Event      │
│  [Request]  [Rules]   [State]   [Kafka/Bus]      │
│                                                  │
│  READ MODEL PROJECTION LIFECYCLE                 │
│                                                  │
│  Event received → Upsert projection document    │
│  → Read store updated → Query can read it       │
│                                                  │
│  REBUILD LIFECYCLE (when stale/corrupt):         │
│                                                  │
│  Disable write to read store                    │
│  → Replay all events from Event Log             │
│  → Rebuild projections from scratch             │
│  → Re-enable                                    │
└──────────────────────────────────────────────────┘
```

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| CQRS requires two databases | CQRS requires two models (conceptually). Starting with the same database and different query/command paths is valid CQRS |
| CQRS means eventual consistency | CQRS with a shared database can be strongly consistent. Eventual consistency only appears when separate physical stores are used |
| CQRS is only for microservices | CQRS is applicable within a monolith. The pattern addresses a design concern (model separation), not a deployment concern |
| CQRS and Event Sourcing are the same | CQRS separates read/write models. Event Sourcing stores state as a sequence of events. They are often combined but are independent patterns |
| Commands should return data | By definition, commands change state and should return only success/failure (and optionally a generated ID). Returning data from a command creates a mixed responsibility |

---

### 🚨 Failure Modes & Diagnosis

**1. Read Model Staleness Causing User Confusion**

**Symptom:** User creates an order and immediately navigates to the order list - the order is not visible. User reports "the order was lost."

**Root Cause:** Read model projection is asynchronous and has not yet processed the `OrderCreated` event. The user experienced the eventual consistency window.

**Diagnostic:**
```bash
# Check Kafka consumer lag for the projector:
kafka-consumer-groups.sh \
  --bootstrap-server kafka:9092 \
  --describe \
  --group order-projector-group
# Lag > 0: projector is behind. Lag > 100: visible delay.
```

**Fix:** For user-facing immediacy, use "read-your-own-writes" strategy: after a command succeeds, query the write store (strongly consistent) for the immediate response, then switch to read store for subsequent queries.

**Prevention:** Monitor projector consumer lag in dashboards. Alert at lag > 10s. Design the UI to show "order processing" state while lag is non-zero.

---

**2. Read Model Projection Rebuild Failure**

**Symptom:** A schema change in the read model requires rebuilding the projection. The rebuild fails halfway - read model is now partially correct.

**Root Cause:** Projection rebuild is not idempotent or not transactional. Partial rebuild corrupts the projection.

**Diagnostic:**
```bash
# Check projection rebuild logs:
kubectl logs deployment/order-projector \
  | grep "ERROR\|rebuild\|corrupt"
# Check event replay position:
kafka-consumer-groups.sh --describe \
  --group projection-rebuild-group
```

**Fix:** Projection rebuilds must be implemented as: (1) write to a new index/collection, (2) validate new projection completeness, (3) atomically swap old → new. Never rebuild in-place.

**Prevention:** Test projection rebuild in staging on every schema change. Use blue/green read model deployment.

---

**3. Command Returns Data - Model Breaks Down**

**Symptom:** Commands return full domain objects rather than IDs. Read-side queries become redundant. The CQRS boundary erodes.

**Root Cause:** Developers find it convenient to return data from commands. Over time, commands accumulate read-side responsibilities and CQRS offers no benefit.

**Diagnostic:**
```bash
# Check command handler return types:
grep -rn "public.*handle.*Command" \
  src/ --include="*.java" \
  | grep -v "void\|UUID\|CommandResult"
# Non-void, non-ID returns from commands = CQRS violation
```

**Fix:** Command handlers return only void, a generated ID, or a `CommandResult` (success/failure metadata). Any data retrieval goes through a query.

**Prevention:** Add an ArchUnit test: command handlers must return void, a primitive ID, or a `CommandResult` - never a domain object or DTO.

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**
- `Command Pattern` - the GOF Command Pattern is the foundational concept for CQRS's write model; commands encapsulate intent to change state
- `Repository Pattern` - both the write and read models use repositories as data access abstractions; understanding the repository pattern clarifies CQRS data access
- `Domain Model` - CQRS is most valuable when a rich domain model (aggregates, invariants) creates tension with query requirements

**Builds On This (learn these next):**
- `Event Sourcing Pattern` - CQRS is commonly combined with Event Sourcing; instead of storing current state, the write model stores a sequence of events that is used to rebuild projections
- `Outbox Pattern` - the Outbox Pattern solves the reliable event publication problem in CQRS: how to atomically persist the write model state and publish the event

**Alternatives / Comparisons:**
- `CRUD` - the simpler alternative: a single model for reads and writes; correct for simple domains where read and write requirements do not diverge
- `CQRS in Microservices` - at the microservice level, CQRS is applied per service; the read and write stores may each be separate microservices (Query Service, Command Service)

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ WHAT IT IS   │ Separate write model (commands) from read │
│              │ model (queries) - independently optimised │
├──────────────┼───────────────────────────────────────────┤
│ PROBLEM IT   │ A single model cannot serve both         │
│ SOLVES       │ write-side consistency AND read-side      │
│              │ query performance well                    │
├──────────────┼───────────────────────────────────────────┤
│ KEY INSIGHT  │ Commands change state, queries return     │
│              │ data - these are different responsibilities│
│              │ requiring different models                │
├──────────────┼───────────────────────────────────────────┤
│ USE WHEN     │ Read:write ratio > 10:1, or domain model  │
│              │ conflicts with query requirements         │
├──────────────┼───────────────────────────────────────────┤
│ AVOID WHEN   │ Simple CRUD domains; small teams where    │
│              │ eventual consistency would confuse users  │
├──────────────┼───────────────────────────────────────────┤
│ TRADE-OFF    │ Independent scalability + query power     │
│              │ vs. eventual consistency + system         │
│              │ complexity                                │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "Commands change the world; queries       │
│              │  observe it - they need different models."│
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ Event Sourcing → Outbox Pattern →         │
│              │ Saga Pattern → Polyglot Persistence       │
└──────────────────────────────────────────────────────────┘
```


---

### 💎 Transferable Wisdom

**Reusable Engineering Principle:**
Read patterns and write patterns for the same data differ
fundamentally. Reads need denormalised, query-optimised views;
writes need normalised, consistent, transactional models.
Serving both from the same data model forces compromises in each.

**Where else this pattern appears:**
- **Data warehousing (OLTP vs OLAP):** Transactional databases
  are normalised for write correctness; analytical databases
  are denormalised star schemas for read performance -- CQRS
  at the database architecture level.
- **Microservices read replicas:** A service maintains a write
  model in its primary database and a read model in Elasticsearch
  or a denormalised replica -- CQRS between service layers.
- **DNS (authoritative vs. resolver):** Authoritative servers are
  the "write side" (source of truth); resolver caches are the
  "read side" (eventually consistent copies optimised for
  fast lookup).

---

### 💡 The Surprising Truth

Greg Young, who popularised CQRS, has repeatedly warned that
most applications do not need CQRS at the architectural level.
In his 2012 talk "8 Lines of Code," he argued that the majority
of CQRS adopters apply it to systems that would be better served
by a simple CRUD architecture. The pattern pays off specifically
when read and write load are dramatically different (100:1 read/
write ratio is a common threshold) or when the query shape is
fundamentally incompatible with the write model structure.
For the average business application, CQRS adds two data
sources, eventual consistency complexity, and significant
operational overhead for minimal benefit.
---

### 🧠 Think About This Before We Continue

**Q1.** A team implements CQRS with a Kafka-based projector maintaining an Elasticsearch read model. The projector has a consumer lag of 0 normally but spikes to 5,000 messages (roughly 30 seconds) during a marketing promotion when write volume is 50x normal. Users keep refreshing and see stale data. Design a strategy to handle this: what changes to the read side, the write side, and the UI layer would make this acceptable to users - without requiring sub-second consistency?

*Hint: Look at the First Principles section for the core invariants and the Failure Modes section for where this scenario appears as a documented issue.*

**Q2.** A developer proposes: "Our audit requirements say we must log every state change. Instead of CQRS + Event Sourcing, I'll just add a write-ahead log to the write model. The WAL serves as our audit log." Is this CQRS? Is it Event Sourcing? What is the precise difference between a write-ahead log used for durability (PostgreSQL WAL), an audit log used for compliance, and an event store used for Event Sourcing - and which of the CQRS invariants (if any) each satisfies?



*Hint: The Comparison Table and Level 3-4 explanations contain the mechanism that determines which approach wins in this scenario.*

**Q3 (Design Trade-off):** An e-commerce system uses CQRS:
`OrderCommandService` writes to a normalised `orders` database;
`OrderQueryService` reads from an Elasticsearch index. A
product price update triggers: (1) write to the command side,
(2) event published, (3) read model updated in Elasticsearch.
Step 3 has a 2-second propagation delay. A customer queries
their cart during this 2-second window. Describe the exact
inconsistency they see and three strategies to handle it.

*Hint: The WHAT CHANGES AT SCALE section addresses eventual
consistency. The three strategies are: accept inconsistency,
add a version check (read-your-writes using session tokens),
or short-circuit the query side for the write originator.*
