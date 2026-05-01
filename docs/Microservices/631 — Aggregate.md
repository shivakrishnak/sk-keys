---
layout: default
title: "Aggregate"
parent: "Microservices"
nav_order: 631
permalink: /microservices/aggregate/
number: "631"
category: Microservices
difficulty: ★★★
depends_on: "Domain-Driven Design (DDD), Bounded Context, Ubiquitous Language"
used_by: "Saga Pattern (Microservices), Event Sourcing in Microservices, CQRS in Microservices"
tags: #advanced, #architecture, #microservices, #pattern, #deep-dive
---

# 631 — Aggregate

`#advanced` `#architecture` `#microservices` `#pattern` `#deep-dive`

⚡ TL;DR — An **Aggregate** is a cluster of domain objects (entities + value objects) treated as a single unit for data changes. The **Aggregate Root** is the only entry point — external code can only modify the cluster through the root. One transaction = one aggregate.

| #631            | Category: Microservices                                                              | Difficulty: ★★★ |
| :-------------- | :----------------------------------------------------------------------------------- | :-------------- |
| **Depends on:** | Domain-Driven Design (DDD), Bounded Context, Ubiquitous Language                     |                 |
| **Used by:**    | Saga Pattern (Microservices), Event Sourcing in Microservices, CQRS in Microservices |                 |

---

### 📘 Textbook Definition

An **Aggregate** is a cluster of associated domain objects (Entities and Value Objects) that are treated as a single unit for the purpose of data changes. The cluster has a single **Aggregate Root** — the entity through which all external access must flow. The Aggregate Root is responsible for enforcing all invariants (business rules) for the entire cluster. The aggregate boundary defines the transactional consistency boundary: when you load an aggregate and perform an operation, all changes within the aggregate are committed atomically in a single database transaction. The Aggregate Root has a global identity (used from outside); other entities within the aggregate have local identities (valid only within the aggregate). Key Aggregate design rules: (1) external objects may hold a reference only to the Aggregate Root, not to internal entities; (2) each transaction should modify only ONE aggregate; (3) changes to other aggregates happen asynchronously via Domain Events; (4) aggregates should be as small as possible while still maintaining consistency.

---

### 🟢 Simple Definition (Easy)

An Aggregate is a group of related objects that must stay consistent together. The Aggregate Root is the "manager" — all changes go through it. One transaction changes one aggregate. If changing one aggregate requires changing another, you use events.

---

### 🔵 Simple Definition (Elaborated)

An Order contains OrderItems. You cannot have an OrderItem without an Order — they are a cluster. The Order is the Aggregate Root: to add an item, you call `order.addItem(...)`, not `item.setOrderId(orderId)`. The Order validates the invariant ("no more than 50 items"), updates its total, and fires an event. No external code ever modifies an OrderItem directly. This design ensures that the Order's business rules are always enforced — you cannot corrupt the order's state by bypassing the root. And because one transaction = one aggregate, all the complexity of "partial save failures" is eliminated within a single aggregate's operations.

---

### 🔩 First Principles Explanation

**Aggregate design rules with examples:**

```
RULE 1: Only the Aggregate Root has global identity
  ✓ Order has ID (external code can reference it)
  ✗ OrderItem has "local" ID (only meaningful within the Order aggregate)
    → external code never holds a reference to OrderItem directly

RULE 2: External objects reference the Aggregate Root only
  ✓ PaymentService holds an OrderId reference
  ✗ PaymentService holds an OrderItemId reference
    → if external code can reference internals, the aggregate boundary leaks

RULE 3: One transaction per Aggregate (DDD rule)
  ✓ order.addItem(product, qty) → one transaction, saves Order aggregate
  ✗ Within one transaction: modify Order AND modify Inventory
    → Breaks aggregate isolation, creates multi-aggregate transaction
    → Instead: order.addItem() fires OrderItemAdded event
               InventoryService handles event asynchronously → separate transaction

RULE 4: Changes to other aggregates via Domain Events
  order.place() → fires OrderPlacedEvent → InventoryService.reserve()
  If inventory reservation fails → compensating event → OrderCancelledEvent
  (Saga pattern)

RULE 5: Aggregates should be small (Single Aggregate Principle)
  BAD: one huge Order aggregate containing Customer, Payment, Shipment
    → Any change to any sub-concept requires loading the entire aggregate
    → High contention (one lock covers too much)
  GOOD: Order aggregate contains only order-specific data
    → PaymentId (reference to Payment aggregate, not the Payment itself)
    → ShipmentId (reference to Shipment aggregate)
```

**Aggregate boundary — what belongs inside vs outside:**

```java
// Order Aggregate:
//   ROOT:    Order (id, customerId, status, totalAmount, createdAt)
//   INSIDE:  OrderItem (productId, quantity, unitPrice, lineTotal)
//            OrderAddress (street, city, postal, country)  ← value object
//   OUTSIDE: Customer (separate aggregate, referenced by CustomerId only)
//            Product  (separate aggregate, referenced by ProductId only)
//            Payment  (separate aggregate, referenced by PaymentId only)

// WHY OrderItem is inside:
// - Cannot exist without Order (no independent identity)
// - Order invariants depend on items (total amount calculation, max items)
// - Always loaded together with Order (not lazy-loaded independently)
// - Changed only through Order methods

// WHY Customer is outside:
// - Has independent existence and lifecycle
// - Order only needs CustomerId to associate, not the full Customer
// - Customer changes (address update) don't trigger Order revalidation
```

**The single aggregate transaction rule in practice:**

```java
@Service
class OrderApplicationService {

    @Autowired OrderRepository orderRepo;
    @Autowired ApplicationEventPublisher eventPublisher;

    @Transactional  // ONE transaction, ONE aggregate
    public void addItemToOrder(AddItemCommand cmd) {
        // Load the SINGLE aggregate we're modifying
        Order order = orderRepo.findById(cmd.orderId())
            .orElseThrow(() -> new OrderNotFoundException(cmd.orderId()));

        // All changes are within this one aggregate
        order.addItem(cmd.productId(), cmd.quantity(), cmd.unitPrice());

        // Save the one aggregate atomically
        orderRepo.save(order);

        // Domain events are published AFTER commit (via @TransactionalEventListener)
        order.getDomainEvents().forEach(eventPublisher::publishEvent);

        // Inventory is NOT modified here!
        // InventoryService will handle the domain event in its own transaction
    }
}
```

---

### ❓ Why Does This Exist (Why Before What)

WITHOUT Aggregate design:

What breaks without it:

1. No single place enforces business invariants — any code can corrupt an Order by directly modifying OrderItems.
2. Transaction scope is unclear — developers accidentally span multiple "aggregate-like" objects in one transaction, creating long locks and contention.
3. "Lazy loading hell" — loading an object triggers loading its entire graph (Order → Items → Products → ProductImages).
4. Distributed systems race conditions — two concurrent requests modify the same "domain cluster" inconsistently.

WITH Aggregates:
→ Invariants are enforced in one place (the Aggregate Root) — cannot be bypassed.
→ Transaction scope is explicit — one aggregate per transaction.
→ Optimistic locking on the Aggregate Root prevents lost updates (version field).
→ Aggregate boundary defines what must be consistent NOW vs what can be eventually consistent.

---

### 🧠 Mental Model / Analogy

> An Aggregate is like a filing cabinet with a single point of access — a lock and a key holder (the Aggregate Root). All files in the cabinet (entities/value objects) can only be accessed by giving the key holder a request ("add this document," "remove this folder"). The key holder checks the rules ("this cabinet only holds invoices for 2024"), makes the change, and ensures consistency. External staff never directly rummage in the cabinet — they always ask the key holder. And you never lock two cabinets at the same time for one operation — if changes are needed in both, you leave a note in one cabinet and handle the other one separately.

"Filing cabinet" = Aggregate cluster
"Lock and key holder" = Aggregate Root
"Files in the cabinet" = Entities and Value Objects within the aggregate
"Checking rules" = invariant enforcement
"Never lock two cabinets at once" = one transaction per aggregate
"Leave a note for the other cabinet" = Domain Event → async update of other aggregate

---

### ⚙️ How It Works (Mechanism)

**Optimistic locking on Aggregate Root:**

```java
@Entity
@Table(name = "orders")
public class Order {
    @Id
    private Long id;

    @Version  // JPA optimistic locking — version is incremented on every save
    private Long version;

    private OrderStatus status;
    // ...

    // If two transactions load Order(id=1, version=3) and both try to save:
    // T1 saves: version 3 → 4 (success)
    // T2 saves: version 3 → 4 (FAIL! version 3 already updated to 4 by T1)
    // → T2 gets OptimisticLockException → retry or return conflict error
    // → No lost updates within the aggregate
}
```

**Aggregate design — too large vs too small:**

```
TOO LARGE (anti-pattern):
  CustomerAggregate: Customer + ALL Addresses + ALL Orders + ALL Payments
  → Loading customer = loading all orders (could be thousands of records)
  → Editing customer name = locking entire order history
  → High contention: any order change locks the customer aggregate

TOO SMALL (anti-pattern):
  Order aggregate has no OrderItems — items are separate entities
  → Adding an item is a separate aggregate operation
  → Cannot enforce "order total < credit limit" within one aggregate
  → Order and Item can get out of sync (Order total wrong)

JUST RIGHT:
  Order + OrderItems (always loaded together, business rules span both)
  Customer + ContactDetails (small, changes together)
  Payment + PaymentAttempts (payment history is part of payment aggregate)
```

---

### 🔄 How It Connects (Mini-Map)

```
Domain-Driven Design (DDD)
Bounded Context
        │
        ▼
Aggregate  ◄──── (you are here)
(transactional consistency boundary: root + entities + value objects)
        │
        ├── Domain Events → cross-aggregate changes via async events
        ├── Saga Pattern  → orchestrating changes across multiple aggregates
        ├── Event Sourcing → storing domain events instead of current state
        └── CQRS          → separate read model from aggregate write model
```

---

### 💻 Code Example

**Complete Aggregate with invariants, domain events, and optimistic locking:**

```java
@Entity
@Table(name = "orders")
public class Order extends AbstractAggregateRoot<Order> {

    @Id @GeneratedValue
    private Long id;

    @Version
    private Long version; // optimistic locking

    @Enumerated(EnumType.STRING)
    private OrderStatus status = OrderStatus.DRAFT;

    @OneToMany(cascade = ALL, orphanRemoval = true, fetch = LAZY)
    @JoinColumn(name = "order_id")
    private List<OrderItem> items = new ArrayList<>();

    @Embedded
    private Money totalAmount = Money.ZERO;

    // Aggregate Root methods enforce invariants:

    public void addItem(ProductId productId, int quantity, Money unitPrice) {
        requireStatus(OrderStatus.DRAFT);
        if (items.size() >= 50) throw new OrderItemLimitExceededException(id);

        items.add(new OrderItem(productId, quantity, unitPrice));
        recalculateTotalAmount();
        // Domain event registered for publishing after commit:
        registerEvent(new OrderItemAddedEvent(id, productId, quantity));
    }

    public void place() {
        requireStatus(OrderStatus.DRAFT);
        if (items.isEmpty()) throw new EmptyOrderException(id);
        this.status = OrderStatus.PLACED;
        registerEvent(new OrderPlacedEvent(id, totalAmount));
    }

    public void cancel(CancellationReason reason) {
        if (status == OrderStatus.SHIPPED) throw new CannotCancelShippedOrderException(id);
        this.status = OrderStatus.CANCELLED;
        registerEvent(new OrderCancelledEvent(id, reason));
    }

    private void requireStatus(OrderStatus required) {
        if (this.status != required)
            throw new InvalidOrderStateException(id, required, this.status);
    }

    private void recalculateTotalAmount() {
        this.totalAmount = items.stream()
            .map(OrderItem::getLineTotal)
            .reduce(Money.ZERO, Money::add);
    }
}
```

---

### ⚠️ Common Misconceptions

| Misconception                                                           | Reality                                                                                                                                                                                                                                                                                      |
| ----------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| An Aggregate is the same as a JPA Entity                                | An Aggregate is a domain design concept — it may be mapped to JPA entities, but the mapping is incidental. The Aggregate design (boundary, invariants, identity) should be driven by domain rules, not by database normalization or JPA convenience                                          |
| All entities within one Aggregate must be in the same database table    | Aggregates map to potentially multiple tables (Order table + OrderItems table). What matters is that all tables are written in the same transaction and never accessed from outside via direct SQL                                                                                           |
| Large aggregates are safer because they include more in one transaction | Large aggregates increase lock contention (many concurrent requests contend for the same lock), increase load time (large object graph), and increase optimistic locking conflicts. Small aggregates with Domain Events are the correct approach for consistency across aggregate boundaries |
| Aggregates can have bidirectional references                            | Aggregates should have one-directional references from root to children. Children should NOT hold a reference back to the root (only the root's ID, if needed). Bidirectional references create circular loading and loading the entire graph unintentionally                                |

---

### 🔥 Pitfalls in Production

**Cross-aggregate transaction — the most common DDD rule violation**

```java
// WRONG: modifying two aggregates in one transaction
@Transactional
public void placeOrder(PlaceOrderCommand cmd) {
    Order order = orderRepo.findById(cmd.orderId()).orElseThrow();
    order.place(); // modifies Order aggregate
    orderRepo.save(order);

    // VIOLATION: second aggregate in same transaction
    Inventory inventory = inventoryRepo.findByProduct(cmd.productId()).orElseThrow();
    inventory.reserve(cmd.quantity()); // modifies Inventory aggregate
    inventoryRepo.save(inventory);
    // If inventory.reserve() throws, order.place() is rolled back
    // But what if inventory is slow? Long-held locks on Order table
    // What if they're in different services/DBs? Transaction fails entirely
}

// CORRECT: one aggregate per transaction, events for the other
@Transactional
public void placeOrder(PlaceOrderCommand cmd) {
    Order order = orderRepo.findById(cmd.orderId()).orElseThrow();
    order.place(); // fires OrderPlacedEvent inside
    orderRepo.save(order);
    // OrderPlacedEvent published after commit
    // InventoryService handles it in its own transaction — eventually consistent
}
```

---

### 🔗 Related Keywords

- `Domain-Driven Design (DDD)` — the methodology that defines Aggregate as a tactical pattern
- `Bounded Context` — the context within which an Aggregate's model applies
- `Saga Pattern (Microservices)` — coordinates changes across multiple aggregates via events
- `Event Sourcing in Microservices` — stores the sequence of Domain Events on an Aggregate as its state
- `CQRS in Microservices` — separates Aggregate write model from read models

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ CLUSTER      │ Aggregate Root + Entities + Value Objects │
│ ACCESS       │ Only via Aggregate Root (no direct access  │
│              │ to internal entities from outside)        │
├──────────────┼───────────────────────────────────────────┤
│ TRANSACTION  │ One aggregate per transaction              │
│ RULE         │ Cross-aggregate = Domain Events (async)   │
├──────────────┼───────────────────────────────────────────┤
│ INVARIANTS   │ Enforced only by Aggregate Root           │
│              │ External code cannot bypass them          │
├──────────────┼───────────────────────────────────────────┤
│ LOCKING      │ @Version on Aggregate Root                │
│              │ → optimistic concurrency                  │
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** The "one transaction per aggregate" rule means cross-aggregate operations are eventually consistent. This creates a window where the system is in a partially applied state (Order is PLACED but Inventory is not yet reserved). Describe the user-visible implications of this window: can the customer see an order as "Placed" while simultaneously being told "out of stock"? Describe the compensating flow: what Domain Events need to fire if inventory reservation fails, and how does the Order aggregate transition back to a consistent state? What is the user-facing message during the eventual consistency window?

**Q2.** Aggregate Root optimistic locking (`@Version`) protects against lost updates within one aggregate. But what about "business-level optimistic locking"? In a ticketing system, 500 users simultaneously try to book the last ticket (one Ticket aggregate). Describe the behaviour: 499 of them will receive `OptimisticLockException` when Hibernate detects version conflicts. How should the application layer handle this exception (retry strategy? immediately return "sold out"?)? And for the aggregate that represents a "seat pool" (many tickets sold from one aggregate), explain the "aggregate contention hotspot" problem and the patterns that address it (Concurrent Aggregate, Sharding by seat block).
