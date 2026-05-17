---
id: MSV-050
title: CQRS in Microservices
category: Microservices
tier: tier-5-distributed-architecture
folder: MSV-microservices
difficulty: ★★★
depends_on: MSV-048, MSV-049, MSV-053
used_by: MSV-048
related: MSV-048, MSV-049, MSV-051, MSV-053, MSV-059, MSV-064
tags:
  - microservices
  - pattern
  - deep-dive
  - reads
status: complete
version: 4
layout: default
parent: "Microservices"
grand_parent: "Technical Dictionary"
nav_order: 50
permalink: /microservices/cqrs-in-microservices/
---

# MSV-050 - CQRS in Microservices

⚡ TL;DR - CQRS (Command Query Responsibility Segregation)
separates the model for writes (Commands) from the
model for reads (Queries). Commands go to the write
model (normalized, transactionally consistent). Queries
read from a separate read model (denormalized,
optimized for the specific query). The read model
is populated by projecting events from the write side.
In microservices: enables each service to maintain
a read projection of data from other services without
calling them at query time. Solves: read/write scaling
mismatch, complex joins across service boundaries,
cacheable read models.

| #050 | Category: Microservices | Difficulty: ★★★ |
|:---|:---|:---|
| **Depends on:** | Event-Driven Microservices, Eventual Consistency in Microservices, Database per Service | |
| **Used by:** | Event-Driven Microservices | |
| **Related:** | Event-Driven Microservices, Eventual Consistency, Event Sourcing in Microservices, Database per Service, Event-Carried State Transfer, Distributed Logging | |

---

### 🔥 The Problem This Solves

**WITHOUT CQRS - THE JOIN PROBLEM:**
An order list page needs: orderId, status, customer
name, product names, total. These fields live in:
order-service, customer-service, product-service.
At query time: order-service calls customer-service
and product-service for each order. 100 orders: 200
service calls per page load. Or: use a shared database
(violates database-per-service). Or: JOIN across
microservice boundaries (impossible without shared DB).

With CQRS: order-service maintains a read model
(OrderListView) that includes customer name, product
names, and total. Populated by consuming events:
OrderCreated (from order-service), CustomerUpdated
(from customer-service), ProductUpdated (from product-
service). Query time: single read from OrderListView.
Zero service calls.

---

### 📘 Textbook Definition

**CQRS (Command Query Responsibility Segregation)**
(Greg Young, Udi Dahan, ~2010) is an architectural
pattern that uses separate models for reading and
writing data. The write model (Command side) handles
state changes; it enforces business rules and invariants;
stored normalized for consistency. The read model
(Query side) handles data retrieval; optimized for
specific queries; stored denormalized for read performance.
The read model is derived from the write model by
projecting (replaying) events or changes. In
microservices: a service can have multiple read models
(projections) each optimized for different query
patterns, potentially stored in different databases
(Elasticsearch for search, Redis for caching, PostgreSQL
for relational reports).

---

### ⏱️ Understand It in 30 Seconds

**One line:**
CQRS: separate write DB (normalized, consistent)
from read DB (denormalized, query-optimized).
Read model is a projection of write model events.

**One analogy:**
> A library has two catalogs: the acquisitions log
> (write model) - every book purchase recorded
> chronologically. The card catalog (read model) -
> indexed by author, title, subject, organized for
> fast lookup. The card catalog is derived from
> the acquisitions log. Updating a book's title:
> record the change in the acquisitions log, then
> update the card catalog to reflect the new title.
> You search the card catalog (fast, optimized for
> queries). Librarians update the acquisitions log
> (authoritative, consistent). Two separate systems
> for two different operations.

**One insight:**
CQRS solves the impedance mismatch between write
and read requirements. Writes need: ACID consistency,
normalized structure (no duplication, referential
integrity), transaction support. Reads need: fast,
denormalized (all data in one row/document), multiple
indexes, sometimes full-text search. The same
database optimized for both is a compromise that
serves neither perfectly. CQRS stops the compromise.

---

### 🔩 First Principles Explanation

**CQRS READ MODEL PROJECTIONS:**

```
WRITE SIDE (normalized, transactional):
  orders table:
    order_id, customer_id, status, created_at
  order_items table:
    item_id, order_id, product_id, qty, unit_price
  Writes: INSERT/UPDATE with ACID guarantees
  Reads from write side: only for consistency checks

READ SIDE (denormalized, optimized):
  order_list_view (one row per order, all data):
    order_id, status, customer_name, customer_email,
    item_count, total, created_at,
    items: [{productName, qty, price}]
  Stored in: MongoDB, Elasticsearch, Redis, or
             separate PostgreSQL schema
  Reads: single document lookup, no joins
  Writes: ONLY from event projection (not direct)

PROJECTION UPDATE (event-driven):
  Event: OrderCreated { orderId, customerId, items }
  Projection: build OrderListView from event data
  Event: CustomerNameChanged { customerId, name }
  Projection: update OrderListView.customer_name
              for ALL orders of this customer
  Event: ProductRenamed { productId, name }
  Projection: update OrderListView item names
  Result: OrderListView always fresh, eventually
```

**MULTIPLE PROJECTIONS FROM SAME EVENTS:**

```
EVENTS (single source of truth):
  OrderCreated, PaymentProcessed, OrderCancelled

PROJECTION 1: OrderListView (MongoDB)
  For: customer-facing order list page
  Fields: orderId, status, summary, date

PROJECTION 2: RevenueByRegionView (PostgreSQL)
  For: finance reporting
  Fields: region, revenue, month
  Aggregates: GROUP BY region, month

PROJECTION 3: RecentOrdersView (Redis sorted set)
  For: real-time activity feed
  Score: timestamp
  Value: orderId, customer

All 3 projections: fed by the same events
Each optimized for its specific query pattern
Events replay: rebuild any projection from scratch
```

---

### 🧪 Thought Experiment

**CROSS-SERVICE READ MODEL:**

```
SCENARIO: Order management dashboard
  Shows: orders with customer tier (Gold/Silver),
         product category, and logistics status
  Data lives in: order-service, customer-service,
                 product-service, logistics-service

OPTION A: API Gateway aggregation at query time
  Dashboard -> API Gateway -> 4 service calls
  per page, per request
  Latency: sum of 4 service latencies
  Coupling: dashboard depends on all 4 services
  Availability: any service down = dashboard broken

OPTION B: CQRS read model in order-service
  order-service subscribes to events:
  CustomerTierChanged (from customer-service)
  ProductCategoryUpdated (from product-service)
  ShipmentStatusUpdated (from logistics-service)
  Builds: DashboardOrderView projection locally
  
  Dashboard: single call to order-service
  Latency: 1 service call (local DB read)
  Coupling: order-service is read-model hub
            (but write-side has no coupling)
  Availability: even if customer-service is down,
                dashboard works (uses cached projection)
  Trade-off: data is eventually consistent
             (projection updated when events arrive)
```

---

### 🧠 Mental Model / Analogy

> CQRS is like the separation between a company's
> general ledger (write model) and its management
> reports (read models). Accountants write to the
> general ledger (journal entries, double-entry,
> strict rules). The CFO reads from pre-computed
> reports (P&L, balance sheet, cash flow) - derived
> from the ledger but formatted for their purpose.
> You don't run the CFO's reports against the raw
> ledger at meeting time (too slow, too complex).
> The reports are pre-computed (projected) from
> the ledger data. Multiple reports: same ledger,
> different projections, each optimized for its
> audience. CQRS applies this same separation to
> software services.

---

### 📶 Gradual Depth - Five Levels

**Level 1 - What it is (anyone can understand):**
Instead of one database for both saving and retrieving
data: have two. The "write database" saves your data
safely (normalized). The "read database" has the data
pre-organized for fast retrieval. Keep them in sync
via events.

**Level 2 - How to use it (junior developer):**
Write model: JPA entities, transactions, `@Repository`.
Read model: separate table (or MongoDB collection)
with all data denormalized. Event listener updates
read model when write model changes. Return read
model from GET endpoints. Write model only in
POST/PUT/DELETE handlers.

**Level 3 - How it works (mid-level engineer):**
Event consumer builds projections: `@KafkaListener`
receives events; applies projection logic (INSERT or
UPDATE read model row). Multiple events may update
the same projection row (OrderCreated initializes,
PaymentProcessed updates status, ShipmentCreated
adds tracking). Projection handlers must be idempotent
(event replay rebuilds the projection from scratch).

**Level 4 - Why it was designed this way (senior/staff):**
CQRS solves the read/write scalability mismatch.
In most systems: reads outnumber writes 10:1 to
100:1. Write model: scaled for consistency (smaller,
ACID database). Read model: scaled for throughput
(horizontal scaling, caching, CDN). Each scaled
independently. CQRS also solves event sourcing's
natural read problem: event sourcing stores events
(not state); reading current state requires replaying
events; CQRS provides pre-computed projections so
reads don't replay events at query time.

**Level 5 - Mastery (distinguished engineer):**
CQRS's hidden complexity: projection consistency
and rebuild. During system operation: read model
is a few events behind write model (Kafka consumer
lag). During projection rebuild (schema change,
bug fix): read model is DOWN or showing stale data.
Strategies: (1) blue/green projections (build new
projection in parallel, swap atomically), (2) version
projections (v1 and v2 run simultaneously during
transition), (3) Accept unavailability with load
shedding. Projection rebuild time at high event volume
(1B events): may take hours. Design for rebuilds
from day one.

---

### ⚙️ How It Works (Mechanism)

```java
// WRITE SIDE: Command handler
@Service
public class OrderCommandService {

    @Transactional
    public OrderId placeOrder(PlaceOrderCommand cmd) {
        // Write model: normalized, ACID
        Order order = Order.builder()
            .customerId(cmd.getCustomerId())
            .items(cmd.getItems())
            .status(OrderStatus.PENDING)
            .build();
        Order saved = orderRepo.save(order);

        // Publish event for projection update
        outboxRepo.save(new OutboxEvent(
            "OrderCreated", saved.getId(),
            serialize(new OrderCreatedEvent(saved))));

        return saved.getId();
    }
}

// READ SIDE: Projection builder
@Component
public class OrderListProjection {

    @KafkaListener(topics="order-events",
                   groupId="order-list-projection")
    @Transactional
    public void onOrderEvent(OrderEvent event) {
        switch (event.getType()) {
            case "OrderCreated" -> {
                // Fetch customer name from customer table
                // (or use event data if event-carried state)
                String customerName = customerView
                    .getNameById(event.getCustomerId());
                orderListViewRepo.save(
                    OrderListView.builder()
                        .orderId(event.getOrderId())
                        .customerName(customerName)
                        .status("PENDING")
                        .total(event.getTotal())
                        .createdAt(event.getTimestamp())
                        .build());
            }
            case "OrderConfirmed" ->
                orderListViewRepo.updateStatus(
                    event.getOrderId(), "CONFIRMED");
            case "OrderCancelled" ->
                orderListViewRepo.updateStatus(
                    event.getOrderId(), "CANCELLED");
        }
    }

    // Cross-service projection: customer name changed
    @KafkaListener(topics="customer-events",
                   groupId="order-list-customer-proj")
    @Transactional
    public void onCustomerEvent(CustomerEvent event) {
        if ("CustomerNameChanged".equals(event.getType())) {
            // Update all orders for this customer
            orderListViewRepo.updateCustomerName(
                event.getCustomerId(), event.getNewName());
        }
    }
}

// READ SIDE: Query handler
@RestController
public class OrderQueryController {

    @GetMapping("/orders")
    public List<OrderListView> getOrders(
            @RequestParam String customerId) {
        // Single read from projection - no joins
        return orderListViewRepo
            .findByCustomerId(customerId);
    }
}
```

---

### 🔄 The Complete Picture - End-to-End Flow

```
CQRS WRITE + READ FLOW:

WRITE (Command):
  POST /orders
  -> OrderCommandService.placeOrder()
  -> writes to orders table (normalized)
  -> writes OutboxEvent
  -> OutboxPoller: publishes to Kafka
  -> returns orderId immediately

READ (Query):
  GET /orders?customerId=123
  -> OrderQueryController.getOrders()
  -> reads from order_list_view table
  -> returns denormalized view (no joins)

PROJECTION UPDATE (async):
  Kafka: OrderCreatedEvent consumed
  -> OrderListProjection.onOrderEvent()
  -> inserts/updates order_list_view row
  Lag: ~50ms (Kafka + processing)
  
CROSS-SERVICE UPDATE:
  customer-service publishes CustomerNameChanged
  -> OrderListProjection.onCustomerEvent()
  -> updates customerName in all affected order rows
  Write side: no change (order-service doesn't care)
  Read side: updated to reflect customer name change
```

---

### 💻 Code Example

**Example 1 - Wrong vs Right: single model for complex queries**

```java
// BAD: Read from normalized write model at query time
@RestController
public class OrderController {
    @GetMapping("/dashboard")
    public List<DashboardRow> getDashboard() {
        // Complex join + N service calls
        List<Order> orders = orderRepo.findAll();
        return orders.stream().map(o -> {
            Customer c = customerClient.getById(
                o.getCustomerId());  // N+1 service call
            List<Product> ps = o.getItems().stream()
                .map(i -> productClient.getById(
                    i.getProductId()))  // N*M calls
                .collect(toList());
            return buildRow(o, c, ps);
        }).collect(toList());
        // 100 orders: 101-1001 service calls per request
    }
}
```

```java
// GOOD: Query from pre-computed CQRS read model
@RestController
public class OrderController {
    @GetMapping("/dashboard")
    public List<DashboardView> getDashboard() {
        // Single read from projection - all data pre-joined
        return dashboardViewRepo.findRecentOrders(100);
        // Projection: built by consuming events
        // Contains: orderId, customerName, productNames,
        //           total, status, region
        // 100 orders: 1 DB query, no service calls
    }
}
```

---

### ⚖️ Comparison Table

| Aspect | Single Model | CQRS Separate Models |
|---|---|---|
| **Read complexity** | Complex joins at query time | Pre-computed projection |
| **Write-read scaling** | Same database scales both | Independent scaling |
| **Cross-service reads** | N+1 service calls | Local projection (0 calls) |
| **Consistency** | Immediate | Eventual (projection lag) |
| **Complexity** | Low | High (projection maintenance) |
| **Schema flexibility** | One schema for both | Read schema optimized per use case |

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| CQRS requires two separate databases | CQRS can be implemented with a single database that has separate schemas or tables for reads vs writes. Two databases is a valid optimization for scaling, not a requirement. Start with a single DB; split only when scaling justifies complexity. |
| CQRS requires Event Sourcing | Event Sourcing (MSV-051) is often combined with CQRS (ES makes projection rebuilding natural) but is independent. CQRS with a standard mutable database: project by subscribing to change events from the write side. Many production systems use CQRS without Event Sourcing. |
| The read model is always stale | The read model is eventually consistent, typically 10-100ms behind. For most user-facing queries: imperceptible. For the specific user who just made a write: implement "read your own writes" by returning the write result directly rather than querying the read model. |

---

### 🚨 Failure Modes & Diagnosis

**Projection divergence: read model incorrect after event processing bug**

**Symptom:**
Order list page shows incorrect customer names for
orders placed 3 days ago. Customer changed their
name 3 days ago. Orders placed before the name change
still show the new name (correct). But orders placed
ON the day of the name change show neither the old
nor new name - some show empty string.

**Root Cause:**
Projection handler bug: when CustomerNameChanged
event is processed, the UPDATE query uses wrong
parameter binding. UPDATE affects 0 rows for orders
placed same day as name change (timestamp condition
bug in query). Projection diverged from truth.

**Diagnostic:**
```bash
# Compare write model vs read model
SELECT o.customer_id,
       c.name AS write_model_name,
       olv.customer_name AS read_model_name
FROM orders o
JOIN customers c ON o.customer_id = c.id
JOIN order_list_view olv ON o.id = olv.order_id
WHERE c.name != olv.customer_name;
-- Returns: diverged records

# Fix: rebuild projection
# Reset consumer offset to beginning
kafka-consumer-groups.sh --bootstrap-server kafka:9092 \
  --group order-list-projection \
  --reset-offsets --to-earliest \
  --topic order-events --execute
# Restart projection consumer: rebuilds from all events
```

**Fix:**
1. Fix the bug in CustomerNameChanged handler.
2. Rebuild projection (reset consumer offset; replay
   all events from beginning).
3. Add a periodic reconciliation job: compare write
   model vs read model; alert on divergence.
4. Add integration tests: after processing each
   event type, assert read model matches expected.

---

### 🔗 Related Keywords

**Patterns that combine with CQRS:**
- `Event-Driven Microservices` - events feed the
  projections that build read models
- `Event Sourcing in Microservices` - events are the
  write model; CQRS provides read projections
- `Eventual Consistency in Microservices` - read models
  are eventually consistent with write models

**Solves problems created by:**
- `Database per Service` - each service needs data
  from other services; CQRS read projections provide
  local cross-service data
- `Event-Carried State Transfer` - events carry enough
  data to build projections without additional calls

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ PATTERN      │ Commands (writes) to write model         │
│              │ Queries (reads) from read projections    │
├──────────────┼───────────────────────────────────────────┤
│ KEY BENEFIT  │ Cross-service queries without calls       │
│              │ Read model optimized per query pattern   │
├──────────────┼───────────────────────────────────────────┤
│ COMPLEXITY   │ Projection divergence, rebuild strategy  │
│              │ Eventual consistency on read side         │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "Separate write model (normalized) from  │
│              │  read model (denormalized projections)"   │
└──────────────────────────────────────────────────────────┘
```

**If you remember only 3 things:**
1. Commands -> write model (normalized, ACID).
   Queries -> read model (denormalized, fast).
   Read model is a projection of write model events.
2. Solves the N+1 cross-service call problem:
   read projections are local, no service calls at
   query time.
3. Complexity: projection divergence (handle with
   rebuild), eventual consistency (projection lags
   by event processing time, typically <100ms).

**Interview one-liner:**
"CQRS separates the write model (commands: normalized,
transactional) from read models (queries: denormalized
projections). Read models are built by consuming
events from the write side. Benefits: N+1 service
call elimination (cross-service data is local),
read scaling independent of writes, per-query
optimized schemas. Trade-offs: eventual consistency
(projection lag), projection divergence risk (requires
reconciliation), rebuild complexity for schema changes."

---

### 💡 The Surprising Truth

CQRS's most counterintuitive aspect: the read model
may contain DUPLICATE data - customer names in
multiple projection tables, product names stored
redundantly in order projections. This violates
normal form and feels wrong to anyone trained on
relational databases. But it's intentional: the
duplication enables queries to execute without joins.
Normalization is a write-side concern (preventing
anomalies during updates). Read models have no
update anomaly problem: they're only written by
centralized event projection handlers, not arbitrary
application code. CQRS gives up normalization for
read-model performance because the problem being
solved is read-side: queries across service boundaries
require data duplication to avoid service coupling.

---

### ✅ Mastery Checklist

**You've mastered this when you can:**
1. **DESIGN** Given an order management dashboard
   with data from 4 services: design the read model
   schema, list all events it subscribes to, and
   describe how each event updates the projection.
2. **REBUILD** Describe the procedure for rebuilding
   a CQRS projection from Kafka: how to reset offset,
   how to handle the rebuild window (serving stale
   data), and how to verify correctness after rebuild.
3. **TRADEOFFS** List 3 scenarios where CQRS is
   justified and 3 where it is over-engineering. The
   single-service CRUD app answer vs the cross-service
   dashboard answer.
4. **CONSISTENCY** How do you implement read-your-own-
   writes for a CQRS system? When a user creates
   an order, how do you show their order immediately
   on the order list page without waiting for the
   projection to update?
5. **DIVERGENCE** How do you detect read model
   divergence in production? Design the monitoring
   and reconciliation strategy.

---

### 🧠 Think About This Before We Continue

**Q1.** Your CQRS system uses Kafka for event delivery
to projections. A new feature requires changing the
read model schema: adding a new field. There are
10 million historical events. How do you migrate the
projection schema and rebuild the read model without:
a) taking the service down for hours, b) serving
incorrect data during rebuild, c) losing events
during the rebuild.

**Q2.** You have a CQRS read projection that combines
data from 3 services: orders, customers, products.
Customer-service has an outage for 20 minutes.
During the outage: 500 customers change their names.
After recovery: how do you ensure all 500 name changes
are reflected in the order list projection? What
if customer-service publishes events via Kafka: does
the outage cause event loss?

**Q3.** An audit regulation requires showing the
exact customer name that was on the order AT THE TIME
it was placed (not the current customer name). Your
CQRS projection currently shows the current customer
name. How do you change the projection design to
support point-in-time customer names without breaking
the existing behavior?