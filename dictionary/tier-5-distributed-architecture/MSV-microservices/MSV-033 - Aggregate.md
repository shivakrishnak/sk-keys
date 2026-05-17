---
id: MSV-033
title: Aggregate
category: Microservices
tier: tier-5-distributed-architecture
folder: MSV-microservices
difficulty: ★★★
depends_on: MSV-031, MSV-032, MSV-034
used_by: MSV-046, MSV-054, MSV-057
related: MSV-031, MSV-032, MSV-034, MSV-046, MSV-054, MSV-057, MSV-058, MSV-051
tags:
  - microservices
  - architecture
  - deep-dive
  - ddd
status: complete
version: 4
layout: default
parent: "Microservices"
grand_parent: "Technical Dictionary"
nav_order: 33
permalink: /microservices/aggregate/
---

# MSV-033 - Aggregate

⚡ TL;DR - Aggregate is a DDD Tactical pattern that
defines a cluster of domain objects (Entity + Value
Objects) that are treated as a single unit for data
changes. The Aggregate Root is the only entry point:
all changes go through it. One transaction = one
aggregate. Aggregates that need to communicate do so
via Domain Events, not direct calls. In microservices:
aggregates define the consistency boundary within a
service; the Saga pattern handles consistency across
multiple aggregates/services.

| #033 | Category: Microservices | Difficulty: ★★★ |
|:---|:---|:---|
| **Depends on:** | Domain-Driven Design (DDD), Bounded Context, Ubiquitous Language | |
| **Used by:** | Saga Pattern, Outbox Pattern, Compensating Transaction | |
| **Related:** | Domain-Driven Design (DDD), Bounded Context, Ubiquitous Language, Saga Pattern, Outbox Pattern, Compensating Transaction, Idempotency in Microservices, Event Sourcing in Microservices | |

---

### 🔥 The Problem This Solves

**THE CONSISTENCY PROBLEM:**
An e-commerce Order contains OrderItems. The total price
of the Order = sum of all OrderItem prices * quantities.
If you allow direct updates to OrderItems from multiple
places in the codebase: it's possible to update an
OrderItem without recalculating the Order total. The
Order is now in an inconsistent state: `order.total`
does not match `sum(items.price * qty)`.

In a distributed system without aggregate boundaries:
two concurrent requests update the same Order. Both
read the current state, both apply their change, the
last write wins. One change is silently lost (lost update
problem). No transaction boundary enforced consistency.

The Aggregate solves this: the Order is the root. All
changes go through Order.addItem(), Order.removeItem().
The total is always recalculated inside the aggregate.
Transaction boundary = aggregate boundary. No direct
updates to OrderItems from outside the Order.

---

### 📘 Textbook Definition

**Aggregate** is a cluster of associated domain objects
(Entities and Value Objects) that are treated as a unit
for the purpose of data changes. Each Aggregate has a
single root Entity (the **Aggregate Root**). The following
rules apply: (1) External objects may only reference
the Aggregate Root, not internal objects directly.
(2) Only the Aggregate Root can be obtained directly
from the database via a Repository. (3) A transaction
should not span multiple Aggregates. (4) Delete the root
= delete all members. In microservices: aggregates map
to the consistency boundary; the service owns one or
more aggregates; cross-aggregate consistency uses eventual
consistency via Domain Events (Saga Pattern).

---

### ⏱️ Understand It in 30 Seconds

**One line:**
An Aggregate is a group of related objects with one
boss (the root) - all changes must go through the boss,
and the whole group is saved or nothing is saved.

**One analogy:**
> A car is an aggregate. The car itself is the root.
The engine, wheels, and seats are members. You don't
> directly replace a seat without going through the car
> (service appointment, car is the unit of change).
> You can't take the engine from one car and the wheels
> from another and call it consistent. The car's registration,
> VIN, and ownership are tied to the car as a unit.
> "One transaction, one car (aggregate)." You don't
> transfer ownership of just the engine independently.

**One insight:**
The most important aggregate design rule is: keep aggregates
small. A small aggregate (2-3 entities + value objects)
has high concurrency (less contention), fast persistence,
and clear responsibility. Large aggregates (20 entities)
have high lock contention, slow saves, and unclear
responsibility. When in doubt: one entity per aggregate,
add members only when they have no meaning without
the root.

---

### 🔩 First Principles Explanation

**AGGREGATE DESIGN RULES:**

```
RULE 1 - SINGLE ROOT:
  Every aggregate has exactly one root entity.
  External access ONLY through the root.
  OrderItem cannot be loaded directly from DB:
  it's always loaded through its Order root.

RULE 2 - REFERENCE BY ID ACROSS AGGREGATES:
  Aggregates reference other aggregates by ID only,
  not by object reference.
  Order does NOT contain a Customer object.
  Order contains a customerId (UUID).
  Loading the Customer is done by a separate query
  in the application layer if needed.

RULE 3 - ONE TRANSACTION PER AGGREGATE:
  A single transaction should not span multiple aggregates.
  Creating an Order AND reserving inventory:
  NOT in one transaction.
  
  Correct approach:
  1. Transaction 1: Create Order (Order aggregate)
  2. Publish OrderCreated event
  3. Transaction 2: Inventory reserves stock (Inventory aggregate)
  This is eventual consistency.

RULE 4 - SMALL AGGREGATES:
  Include in an aggregate ONLY objects that must change
  together to maintain invariants.
  Order Aggregate: Order (root) + OrderItems
  Reason: Order total must equal sum of item totals.
  These change together.
  
  NOT in Order Aggregate: Customer, Product catalog data,
  Inventory levels. These have independent lifecycles.

RULE 5 - INVARIANT ENFORCEMENT IN ROOT:
  All business rules (invariants) that span multiple
  members must be enforced in the root.
  Rule: Order total cannot exceed $10,000.
  Enforced in: Order.addItem() - checks total after add.
  NOT in: OrderItemService.add() - service layer.
```

**AGGREGATE vs ENTITY vs VALUE OBJECT:**

```
VALUE OBJECT:
  No identity. Defined by attributes. Immutable.
  Example: Money(100.00, USD), Address("123 Main", "NYC")
  Two Money(100.00, USD) are equal and interchangeable.

ENTITY:
  Has identity. Can change state. Tracked over time.
  Example: OrderItem (has OrderItemId; can change quantity)
  Two OrderItems with different IDs are different
  even if all other attributes are equal.

AGGREGATE ROOT (special Entity):
  Entry point for the aggregate cluster.
  Has global identity (used in Repository lookup).
  Ensures all members remain consistent.
  Raises Domain Events on significant state changes.
  Example: Order (root), with OrderItems (entities)
  and Money (value objects) as members.
```

---

### 🧪 Thought Experiment

**AGGREGATE BOUNDARY - WHAT TO INCLUDE:**

```
SCENARIO: Should Product be part of Order Aggregate?

  Order aggregate contains OrderItems.
  Each OrderItem references a Product.
  
  OPTION A: Include Product in Order Aggregate:
    class Order {
        List<OrderItem> items;
        // OrderItem has: Product product (full object)
    }
    
    Problem: Order aggregate loads the entire Product
    catalog data for every order. Product catalog changes
    (price update) affect all open Orders (they hold
    a reference). Order aggregate is now enormous.
    Saving an order updates product data. Concurrent
    orders conflict on the same product. WRONG.

  OPTION B: Reference by ID (correct):
    class OrderItem {
        ProductId productId;    // reference by ID
        String productName;     // snapshot at order time
        Money unitPrice;        // snapshot at order time
    }
    
    Order doesn't know about current product details.
    When order is placed: snapshot the price and name.
    Future product price changes don't affect old orders.
    Product aggregate is independent. No contention.
    CORRECT.

CONCLUSION:
  Include in aggregate only what is needed to enforce
  the aggregate's own invariants. Product invariants
  are in Product Aggregate. Order invariants (total,
  item limits) are in Order Aggregate.
```

---

### 🧠 Mental Model / Analogy

> An Aggregate is like a government department's
> decision-making unit. The department head (root)
> makes all decisions for the department. Sub-teams
> (member entities) execute within the department
> but don't make commitments to external parties without
> going through the department head. All the department's
> work is in one transaction (the department either
> delivers or doesn't, as a unit). Cross-department
> coordination goes through official channels (Domain
> Events / APIs), not direct sub-team-to-sub-team contact.

---

### 📶 Gradual Depth - Five Levels

**Level 1 - What it is (anyone can understand):**
An Aggregate is a group of related objects where one
object is the "boss" (root). All changes go through
the boss. You save the whole group together. This
ensures the group is always consistent.

**Level 2 - How to use it (junior developer):**
In Spring Boot + JPA: the Aggregate Root is your main
`@Entity`. Members are `@OneToMany` with
`CascadeType.ALL`. You load and save only through the
root repository. Business methods are on the root entity.
Don't make members `@Entity` with their own `@Repository`.

**Level 3 - How it works (mid-level engineer):**
For cross-aggregate consistency: use Spring Data's
`@DomainEvents` to publish events when the aggregate
state changes. The event is published AFTER the transaction
commits (using `@TransactionalEventListener(phase=
AFTER_COMMIT)`). The event listener starts a new
transaction for the downstream aggregate. This ensures:
the originating aggregate change is committed before
the event is processed, and a failure in the downstream
processing doesn't roll back the originating change
(they're separate transactions).

**Level 4 - Why it was designed this way (senior/staff):**
Aggregate = unit of optimistic locking. JPA's `@Version`
on the aggregate root means: two concurrent requests
trying to modify the same aggregate: one will get an
`ObjectOptimisticLockingFailureException`. This prevents
lost updates. Small aggregates: lower contention, fewer
collisions. Large aggregates: high contention, frequent
locking failures under load. This is why aggregate
size is not just a design question but a performance
question. At 1000 req/s, a large aggregate with frequent
concurrent updates will see consistent locking failures.

**Level 5 - Mastery (distinguished engineer):**
Event Sourcing replaces aggregate state storage with
an append-only event log. Instead of storing the current
state of an Order: store all events that happened to
the Order (OrderCreated, ItemAdded, ItemRemoved,
OrderSubmitted). Current state = replay of all events.
This enables: full audit trail, temporal queries ("what
was the Order state at 2pm yesterday?"), and temporal
decoupling (event log grows, no table locking). The
downside: query complexity (need projections/read models).
Event Sourcing is the extreme form of Domain Event
usage - combining the Aggregate pattern with event
sourcing creates the ES+CQRS architecture that powers
high-scale, audit-heavy systems (banking, trading).

---

### ⚙️ How It Works (Mechanism)

**AGGREGATE ROOT IMPLEMENTATION:**

```java
@Entity
@Table(name = "orders")
public class Order extends AbstractAggregateRoot<Order> {
    
    @Id
    @GeneratedValue
    private UUID id;
    
    @Version  // Optimistic locking
    private Long version;
    
    private UUID customerId;  // ID reference, not object
    
    @Enumerated(EnumType.STRING)
    private OrderStatus status = OrderStatus.DRAFT;
    
    @OneToMany(
        mappedBy = "order",
        cascade = CascadeType.ALL,
        orphanRemoval = true)
    private List<OrderItem> items = new ArrayList<>();
    
    // Business invariant enforced in root
    public void addItem(UUID productId,
            String name, BigDecimal price, int qty) {
        if (status != OrderStatus.DRAFT)
            throw new DomainException(
                "Cannot add items: order is " + status);
        if (totalItems() >= 50)
            throw new DomainException(
                "Order cannot have more than 50 items");
        
        items.add(new OrderItem(this, productId,
            name, price, qty));
        // Spring Data: registers event for post-commit publish
        registerEvent(new ItemAddedEvent(
            this.id, productId, qty, price));
    }
    
    public void submit() {
        if (status != OrderStatus.DRAFT)
            throw new DomainException("Order not in DRAFT");
        if (items.isEmpty())
            throw new DomainException("Cannot submit empty order");
        
        this.status = OrderStatus.SUBMITTED;
        registerEvent(new OrderSubmittedEvent(
            this.id, this.customerId, calculateTotal()));
    }
    
    private Money calculateTotal() {
        return items.stream()
            .map(i -> i.getUnitPrice().multiply(i.getQty()))
            .reduce(Money.ZERO, Money::add);
    }
    
    private int totalItems() {
        return items.stream()
            .mapToInt(OrderItem::getQty).sum();
    }
}

// REPOSITORY: only for Aggregate Root
public interface OrderRepository
        extends JpaRepository<Order, UUID> {
    // No OrderItemRepository - items loaded via Order
}
```

---

### 🔄 The Complete Picture - End-to-End Flow

**CROSS-AGGREGATE CONSISTENCY VIA DOMAIN EVENTS:**

```
SCENARIO: Order submitted -> Inventory reserved

STEP 1: Order Aggregate (Transaction 1)
  order.submit()
  -> registers OrderSubmittedEvent
  -> Transaction 1 commits
  -> OrderSubmittedEvent published (post-commit)

STEP 2: Event Listener (Transaction 2)
  @TransactionalEventListener(AFTER_COMMIT)
  void onOrderSubmitted(OrderSubmittedEvent event) {
      // New transaction
      inventoryService.reserve(
          event.getOrderId(),
          event.getItems());
  }
  // Inventory Aggregate updated in Transaction 2

STEP 3: Inventory Aggregate
  inventory.reserve(orderId, items)
  -> reduces stock levels
  -> registers StockReservedEvent
  -> Transaction 2 commits

FAILURE SCENARIO:
  If Transaction 2 fails (inventory insufficient):
  Transaction 1 is already committed (order exists)
  Compensating action needed: publish OrderCancellationEvent
  This is the Saga Pattern (orchestrated or choreographed)
```

---

### 💻 Code Example

**Example 1 - Wrong vs Right: direct member access**

```java
// BAD: direct modification of aggregate member
// bypassing the aggregate root's invariant enforcement
@Service
public class OrderService {
    public void addItemToOrder(Long orderId, Long productId) {
        Order order = orderRepo.findById(orderId);
        OrderItem item = new OrderItem(productId, 1);
        order.getItems().add(item);  // WRONG: bypass root
        orderItemRepo.save(item);    // WRONG: own repo
        // total never recalculated
        // no event published
        // status not checked (can add to SHIPPED order!)
    }
}
```

```java
// GOOD: all changes through aggregate root
@Service
public class OrderApplicationService {
    public void addItemToOrder(
            UUID orderId, UUID productId,
            String name, BigDecimal price, int qty) {
        // Load aggregate via root repository
        Order order = orderRepo.findById(orderId)
            .orElseThrow(() -> new OrderNotFoundException(orderId));
        
        // All changes through root method
        // Root enforces: status check, item limit, event registration
        order.addItem(productId, name, price, qty);
        
        // Save root (cascades to OrderItems)
        orderRepo.save(order);
        // Total recalculated, invariants enforced,
        // ItemAddedEvent registered for post-commit publish
    }
}
```

---

### ⚖️ Comparison Table

| Aspect | Small Aggregate | Large Aggregate |
|---|---|---|
| **Concurrency** | Low contention (small lock scope) | High contention (many concurrent updates) |
| **Performance** | Fast save (few objects) | Slow save (many objects to load/save) |
| **Complexity** | Clear responsibility | Multiple responsibilities |
| **Consistency** | Strong (tight boundary) | Strong (but expensive) |
| **Cross-boundary** | More events needed | Fewer events needed |

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| Aggregate = database table | An Aggregate is a domain concept. It often maps to multiple tables (Order table + OrderItems table). The aggregate boundary is a consistency boundary, not a table boundary. |
| One aggregate per service | A service typically has multiple aggregates. Order Service might have: Order aggregate, OrderBatch aggregate, OrderTemplate aggregate. Each has its own root and repository. |
| Aggregates must avoid eventual consistency | Aggregates use strong consistency (ACID transaction) WITHIN the aggregate. Cross-aggregate consistency IS eventual (Domain Events, Sagas). This is by design: strong consistency within boundaries, eventual consistency across boundaries. |

---

### 🚨 Failure Modes & Diagnosis

**Aggregate root too large: performance and contention**

**Symptom:**
Shop order processing slows down under load. Database
profiler shows ORDER table updates taking 800ms. Logs
show frequent `ObjectOptimisticLockingFailureException`
during peak traffic. Retry logic causes additional latency.

**Root Cause:**
Order aggregate has grown to include: OrderItems, Shipments,
PaymentAttempts, CustomerNotes, and ActivityLog. Saving
an Order loads and saves 50+ rows. Every request that
touches the Order locks the entire aggregate. At 100
concurrent order updates: frequent version conflicts,
retry cascades.

**Diagnostic:**
```java
// Check aggregate size in production (JPA debug logging)
logging:
  level:
    org.hibernate.SQL: DEBUG
    org.hibernate.type.descriptor.sql: TRACE
// Count SELECTs per save: > 5 joins = aggregate too large

// Check OptimisticLockingFailureException rate:
// Micrometer counter:
counter.increment("aggregate.optimistic_lock_failure",
    "aggregate", "order");
```

**Fix:**
1. Extract Shipments to a Shipment aggregate (separate
   lifecycle from Order)
2. Extract PaymentAttempts to a Payment aggregate
3. Extract ActivityLog to a separate write-only log
   (not part of any aggregate - append-only table)
4. Order aggregate: Order + OrderItems only
   (the only invariant relationship: total = sum of items)
5. Cross-aggregate: Domain Events (OrderShipped event
   triggers Shipment aggregate creation)

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**
- `Domain-Driven Design (DDD)` - Aggregate is a Tactical
  DDD pattern
- `Bounded Context` - Aggregates exist within Bounded
  Contexts
- `Ubiquitous Language` - Aggregate names and methods
  use the business language

**Builds On This:**
- `Saga Pattern` - cross-aggregate consistency when
  transactions can't span aggregates
- `Outbox Pattern` - reliable Domain Event publishing
  from aggregate state changes
- `Compensating Transaction` - undoing aggregate changes
  when a multi-step saga fails
- `Event Sourcing in Microservices` - storing aggregate
  changes as an event log

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ RULES        │ 1. External access: root only           │
│              │ 2. Reference other aggregates by ID     │
│              │ 3. One transaction per aggregate        │
│              │ 4. Keep aggregates small               │
├──────────────┼───────────────────────────────────────────┤
│ CROSS-AGG    │ Domain Events -> eventual consistency   │
│              │ Saga Pattern for multi-aggregate flows  │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "Consistency boundary: all changes      │
│              │  via root; one transaction; small"      │
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ Saga Pattern → Outbox Pattern           │
└──────────────────────────────────────────────────────────┘
```

**If you remember only 3 things:**
1. Aggregate Root = only entry point. External code
   never accesses or modifies members directly.
2. One transaction per aggregate. Cross-aggregate
   consistency uses Domain Events (eventual consistency).
3. Keep aggregates small (2-3 entities max). Large
   aggregates = high lock contention under load.

**Interview one-liner:**
"An Aggregate is a DDD Tactical pattern: a cluster of
domain objects with one root entity. All changes go
through the root (invariant enforcement, event publishing).
One DB transaction per aggregate. Reference other
aggregates by ID only, not by object. For cross-aggregate
consistency: Domain Events + Saga Pattern. Aggregate
size matters: small aggregates (2-3 entities) have low
contention and fast saves; large aggregates lock under
concurrency."

---

### 💡 The Surprising Truth

The most common aggregate mistake is treating the aggregate
as a unit of retrieval rather than a unit of change.
Developers load a large Order aggregate with all its
members to display a summary (order count, total).
This loads 50 objects to display 3 fields. The fix:
CQRS (Command Query Responsibility Segregation). The
Aggregate (write model) is only loaded when CHANGING
state. For READING: a separate read model (view/projection)
with exactly the fields needed. A Prometheus query:
"I want total order value by customer" should never
load Order aggregates. It should query a pre-computed
read model. Aggregate = write concern. Read model =
query concern. Mixing them creates N+1 load problems
and unnecessarily large aggregates.

---

### ✅ Mastery Checklist

**You've mastered this when you can:**
1. **DESIGN** Given a business scenario, identify the
   aggregate boundaries: what is the root, what members
   belong inside, what should be referenced by ID only.
2. **IMPLEMENT** Code a Spring Boot aggregate root
   with business invariants enforced in domain methods,
   `@Version` for optimistic locking, and `@DomainEvents`
   for Domain Event publishing.
3. **SIZE** Evaluate whether an existing aggregate is
   too large by measuring load time, optimistic locking
   failure rate, and counting entity relationships.
4. **DECOUPLE** Redesign a service where two aggregates
   were in one transaction to use Domain Events and
   separate transactions with compensating actions.
5. **QUERY** Apply CQRS to separate the write model
   (aggregate) from the read model (projection), and
   explain why loading aggregates for read operations
   is an anti-pattern.

---

### 🧠 Think About This Before We Continue

**Q1.** Design the Aggregate for a bank account:
BankAccount (root), Transactions (members?), Customer
(member or reference?), Branch (member or reference?).
Apply the aggregate design rules. What invariants must
the BankAccount aggregate enforce? What is the transaction
boundary?

**Q2.** Two concurrent API requests both try to place
orders for the same limited-stock item. Both read
stockLevel=1 and both proceed to create an order.
Both succeed. Stock is now -1. What aggregate design
change prevents this overselling? (Hint: consider
where the stock level invariant should live.)

**Q3.** You have an Order aggregate that, when submitted,
must: (1) process payment, (2) reserve inventory,
(3) send confirmation email. All three must happen.
If payment succeeds but inventory fails, the order
must be cancelled. Design this using Aggregates and
Domain Events. Which patterns are involved?