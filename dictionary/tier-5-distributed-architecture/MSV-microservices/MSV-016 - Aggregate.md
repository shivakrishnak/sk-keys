---
layout: default
title: "Aggregate"
parent: "Microservices"
grand_parent: "Technical Dictionary"
nav_order: 16
permalink: /microservices/aggregate/
id: MSV-016
category: Microservices
difficulty: ★★★
depends_on: Domain-Driven Design, Bounded Context, Object-Oriented Programming
used_by: Event Sourcing in Microservices, CQRS in Microservices, Saga Pattern
related: Bounded Context, Domain Events, Repository Pattern
tags:
  - microservices
  - architecture
  - pattern
  - deep-dive
  - distributed
status: complete
version: 1
---

# MSV-016 - Aggregate

⚡ TL;DR - An Aggregate is a DDD tactical pattern that groups related domain objects under a single root entity, ensuring all business invariants are enforced atomically within one transaction boundary.

| #631 | Category: Microservices | Difficulty: ★★★ |
|:---|:---|:---|
| **Depends on:** | Domain-Driven Design, Bounded Context, Object-Oriented Programming | |
| **Used by:** | Event Sourcing in Microservices, CQRS in Microservices, Saga Pattern | |
| **Related:** | Bounded Context, Domain Events, Repository Pattern | |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
An e-commerce application allows concurrent order modifications. One service thread processes "add item to order," another processes "apply discount to order." Both read the order at the same time, both modify it, both save it. The last write wins - either the item is added without the discount, or the discount is applied without the new item. A third thread meanwhile confirms the order without noticing it is in an inconsistent state. Business rules like "a confirmed order must have at least one item" are scattered across 12 service methods, enforced inconsistently.

**THE BREAKING POINT:**
You cannot trust the database holds valid business data. Rules are enforced by convention, not by design. Every new developer must know all 12 enforcement points. An invariant is violated when someone misses one.

**THE INVENTION MOMENT:**
This is exactly why the Aggregate pattern was created - to define a consistency boundary around related objects so that all invariants are enforced by the aggregate root before any change is persisted.


**EVOLUTION:**
The Aggregate pattern was formalised by Eric Evans in "Domain-Driven Design" (2003) as the solution to cross-object invariant enforcement. Early OO systems tried to keep each individual object valid independently, but found that business invariants spanning multiple objects were violated when objects were modified separately. The Aggregate defines a transactional consistency boundary: all changes within an aggregate happen in one transaction; changes across aggregates happen through domain events. In microservices, aggregates became the unit of service decomposition: each service owns one or more aggregates and their persistence.
---

### 📘 Textbook Definition

An **Aggregate** is a cluster of domain objects - one **Aggregate Root** (an Entity with a globally unique ID) plus zero or more subordinate Entities and Value Objects - that is treated as a single unit for the purposes of data changes. All modifications to the aggregate are made exclusively through the Aggregate Root, which enforces all business invariants. An aggregate is the unit of transactional consistency: all changes to the aggregate are committed atomically. Aggregates reference other aggregates only by their Root ID, never by direct object reference.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
An aggregate is a cluster of related objects managed as one unit, with one boss in charge of all changes.

**One analogy:**
> Think of a corporate department. The department head (Aggregate Root) controls all changes to the team. You cannot reassign someone from the department without going through the head. You cannot change the team's budget without the head approving it. External departments only know the department head's name (ID) - they don't talk directly to individual team members.

**One insight:**
The Aggregate Root is not just a container - it is the guardian of business rules. Any method on the root that changes state is an opportunity to check invariants. If a change would violate a rule, the root throws a domain exception before persisting anything.

---

### 🔩 First Principles Explanation

**CORE INVARIANTS:**
1. External code may hold only a reference to the Aggregate Root - never to internal entities directly.
2. All mutations to the aggregate go through the Root's methods - the Root enforces invariants before accepting any change.
3. An aggregate is one transaction: all changes within it commit or roll back together. Changes across aggregates use eventual consistency.

**DERIVED DESIGN:**
Given Invariant 1, if `Order` is the Aggregate Root and `OrderLine` is an internal entity, no class outside the aggregate ever holds an `OrderLine` reference. External classes reference `Order` and call methods on it to modify lines. This prevents bypassing the Root's rules.

Given Invariant 3, a transaction never spans multiple aggregates - if it did, aggregate size would be unpredictable and locking scope undefined. Cross-aggregate coordination uses Domain Events: `Order.confirm()` publishes `OrderConfirmed`; the Inventory aggregate subscribes and decrements stock as a separate transaction.

**Designing aggregate boundaries - key questions:**
- Must A and B change together in the same transaction? → Same aggregate
- Can A and B change independently, with eventual consistency tolerated? → Different aggregates
- If they were separate aggregates, what is the worst case if they are temporarily inconsistent?

**THE TRADE-OFFS:**
**Gain:** Centralized invariant enforcement, clear consistency boundary, testable domain logic (unit-test the root without a database).
**Cost:** Eventual consistency between aggregates, potential performance overhead from loading entire aggregate to modify one property, design complexity for boundary identification.

---

### 🧪 Thought Experiment

**SETUP:**
An `Order` with `OrderLines`. Rules: (1) a confirmed order cannot be modified; (2) an order with no lines cannot be confirmed.

**WHAT HAPPENS WITHOUT AGGREGATE:**
`OrderService.addLine()` checks rule (1). `OrderService.confirm()` checks rule (2). A developer writes `OrderAdminService.forceAddLine()` and skips rule (1). Six months later: confirmed orders have lines mysteriously added via the admin service. Production incident.

**WHAT HAPPENS WITH AGGREGATE:**
```
Order.addLine()    → checks: status == DRAFT? Yes → adds line
Order.confirm()    → checks: lines.size() > 0? Yes → confirms
Order.addLine()    → checks: status == DRAFT? No → throws OrderException
                             (admin service tries to use forceAdd but
                              there is no such method on the root - 
                              the only way is through addLine())
```
Rules cannot be bypassed because they live inside the only mutation entry point.

**THE INSIGHT:**
Business rules enforced by design are unbreakable. Business rules enforced by convention are broken by every developer under time pressure.

---

### 🧠 Mental Model / Analogy

> An Aggregate is like a bank vault with a vault manager. Anyone who wants to access the contents must go through the manager. The manager checks your authorisation, checks the current vault state, and either grants access (completing the business rule) or refuses. Nobody slides money in through a side ventilation shaft. The vault manager is always in control.

- "Vault manager" → Aggregate Root (the entry point for all mutations)
- "Vault contents" → internal Entities and Value Objects
- "Authorisation check" → business invariant enforcement in domain methods
- "Side ventilation shaft" → direct access to internal entities, bypassing root

Where this analogy breaks down: a bank vault stores physical objects; an aggregate stores domain state that can be queried by external code (read-only) without going through the root. The invariant is only on mutations, not reads.

---

### 📶 Gradual Depth - Four Levels

**Level 1 - What it is (anyone can understand):**
An aggregate is a group of related things managed by one leader. Only the leader can approve changes. This guarantees rules are always checked before anything changes.

**Level 2 - How to use it (junior developer):**
Identify which entities must change together to maintain a business rule. Make one entity the "root." Put all methods that change state on the root. Mark internal entities as package-private or non-public. Use a Repository to load and save only the root aggregate.

**Level 3 - How it works (mid-level engineer):**
When a command arrives, the application service loads the aggregate root via a Repository. The aggregate root's method enforces invariants and mutates state. Domain events are collected (not yet published). The Repository saves the aggregate (one DB transaction). Post-save, domain events are published. Subscribers (other aggregates) react in separate transactions. This is idempotent - replay is safe if events are tracked by version.

**Level 4 - Why it was designed this way (senior/staff):**
Evans' key insight was that database transactions are a design smell when used as a business rule enforcement mechanism. A 3-table transaction that says "order, orderline, and inventory must all change or all fail" encodes business logic in infrastructure. Aggregates pushes consistency decisions up to the domain layer. The rule "keep aggregates small" (ideally 2–5 objects) was validated empirically: large aggregates cause lock contention, slow load times, and merge conflicts. Vernon's "Implementing DDD" recommends starting with one entity per aggregate and only expanding when invariants require it.

---

### ⚙️ How It Works (Mechanism)

**Aggregate lifecycle:**

```
┌───────────────────────────────────────────────┐
│            Aggregate Lifecycle                │
├───────────────────────────────────────────────┤
│ 1. Command arrives (e.g., ConfirmOrder)        │
│ 2. App Service loads Aggregate from Repo       │
│    (SELECT * WHERE aggregate_id = ?)          │
│ 3. App Service calls root method               │
│    order.confirm()                            │
│ 4. Root enforces invariants                    │
│    - lines.size() > 0? → ok                   │
│    - status == DRAFT? → ok                    │
│ 5. Root mutates state: status = CONFIRMED      │
│ 6. Root registers DomainEvent: OrderConfirmed  │
│ 7. Repository saves aggregate (UPDATE SQL)    │
│ 8. App Service publishes registered events     │
│ 9. Response: success                          │
│                                               │
│ On invariant violation at step 4:             │
│ - DomainException thrown                      │
│ - No save, no event                           │
│ - Caller gets 422 Unprocessable Entity        │
└───────────────────────────────────────────────┘
```

**Aggregate version field for optimistic locking:**

```java
@Entity
public class Order {  // Aggregate Root
    @Id
    private UUID id;

    @Version  // JPA optimistic lock version
    private Long version;  // prevents lost updates

    private OrderStatus status;
    @OneToMany(cascade = ALL, orphanRemoval = true)
    private List<OrderLine> lines = new ArrayList<>();

    public void addLine(ProductId productId, int qty, Money price) {
        requireState(status == OrderStatus.DRAFT,
            "Cannot add to non-draft order");
        lines.add(new OrderLine(productId, qty, price));
    }

    public void confirm() {
        requireState(!lines.isEmpty(),
            "Cannot confirm order with no lines");
        this.status = OrderStatus.CONFIRMED;
        registerEvent(new OrderConfirmedEvent(id, getTotal()));
    }

    private void requireState(boolean condition, String msg) {
        if (!condition) throw new OrderInvariantViolation(msg);
    }
}
```

**Cross-aggregate communication via events (no direct reference):**

```java
// Inventory Aggregate subscribes to OrderConfirmedEvent
// from Orders Aggregate - SEPARATE transaction
@TransactionalEventListener
public void on(OrderConfirmedEvent event) {
    for (OrderItemDto item : event.items()) {
        // Loads Inventory aggregate separately
        StockAggregate stock = stockRepo
            .findByProduct(item.productId());
        stock.reserve(item.quantity()); // own invariants enforced
        stockRepo.save(stock);
    }
}
// If this fails: compensating event (stock not reserved)
// handled by Saga pattern
```

---

### 🔄 The Complete Picture - End-to-End Flow

**NORMAL FLOW:**
HTTP POST /orders/{id}/confirm → Application Service → Load Order Aggregate ← YOU ARE HERE → `order.confirm()` validates invariants → State updated → OrderConfirmedEvent registered → Repository saves (atomic DB transaction) → Event published to message bus → Inventory Aggregate reserves stock (separate transaction)

**FAILURE PATH:**
`order.confirm()` finds `lines.isEmpty()` → `OrderInvariantViolation` thrown → Application Service catches → 422 returned → No database write → No event published → Idempotent: retry is safe

**WHAT CHANGES AT SCALE:**
At 10,000 concurrent order confirms, the `@Version` optimistic lock means many concurrent requests for the same aggregate will fail with `OptimisticLockException` (version mismatch). Solution: reduce aggregate size (fewer fields to lock), use commands per aggregate that naturally don't conflict, or accept the retry cost. At 100x, aggregates written to in hot paths (e.g., a popular product's inventory) become bottlenecks - partition by product ID to spread write load.

---

### 💻 Code Example

**Example 1 - Complete Order Aggregate with invariants:**

```java
public class Order {
    private final OrderId id;
    private OrderStatus status = OrderStatus.DRAFT;
    private final List<OrderLine> lines = new ArrayList<>();
    private final List<DomainEvent> events = new ArrayList<>();

    public OrderId getId() { return id; }

    // Only mutation method - enforces invariant
    public void addLine(ProductId product, int qty, Money price) {
        if (status != OrderStatus.DRAFT) {
            throw new OrderException(
                "Lines can only be added to DRAFT orders"
            );
        }
        if (qty <= 0) {
            throw new OrderException("Quantity must be positive");
        }
        lines.add(new OrderLine(product, qty, price));
    }

    public void confirm() {
        if (lines.isEmpty()) {
            throw new OrderException(
                "Cannot confirm an order with no lines"
            );
        }
        this.status = OrderStatus.CONFIRMED;
        events.add(new OrderConfirmedEvent(id, getTotal()));
    }

    public Money getTotal() {
        return lines.stream()
            .map(OrderLine::lineTotal)
            .reduce(Money.ZERO, Money::add);
    }

    // Repository calls this to get events to publish
    public List<DomainEvent> pullDomainEvents() {
        List<DomainEvent> fired = List.copyOf(events);
        events.clear();
        return fired;
    }
}
```

**Example 2 - Repository and Application Service:**

```java
// Repository: persistence abstraction
public interface OrderRepository {
    Order findById(OrderId id);
    void save(Order order);
}

// Application Service: orchestrates, does not contain domain logic
@Service
@Transactional
public class OrderApplicationService {
    private final OrderRepository orders;
    private final ApplicationEventPublisher events;

    public void confirmOrder(UUID orderId) {
        Order order = orders.findById(OrderId.of(orderId));
        order.confirm();           // business rule enforced in root
        orders.save(order);        // one transaction
        // After commit: publish collected domain events
        order.pullDomainEvents().forEach(events::publishEvent);
    }
}
```

**Example 3 - Unit testing the aggregate (no Spring, no DB):**

```java
@Test
void cannotConfirmEmptyOrder() {
    Order order = new Order(OrderId.generate());
    // No lines added

    assertThrows(OrderException.class, order::confirm);
}

@Test
void confirmedOrderCannotAddLines() {
    Order order = new Order(OrderId.generate());
    order.addLine(ProductId.of("p1"), 2, Money.of(10, USD));
    order.confirm();

    assertThrows(OrderException.class,
        () -> order.addLine(ProductId.of("p2"), 1, Money.of(5, USD))
    );
}
// Pure unit test - no DB, no Spring context, runs in <1ms
```

---

### ⚖️ Comparison Table

| Consistency Model | Scope | Latency | Use When |
|---|---|---|---|
| **Aggregate (single transaction)** | Within aggregate | Low | Invariants MUST be enforced atomically |
| Saga Pattern | Cross-aggregate/service | Medium-High | Distributed workflow with compensation |
| Two-Phase Commit (2PC) | Cross-DB | Very High | Legacy systems; avoid in microservices |
| Eventual Consistency only | Cross-service | Low-Medium | Invariants can tolerate temporary inconsistency |

How to choose: use aggregate-level consistency for the core business invariants of each domain concept; use eventual consistency via events for coordination across aggregates and services.

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| Aggregates can be as large as needed | Large aggregates cause DB lock contention, slow load times, and merge conflicts. Keep them to 3–5 objects max |
| The Aggregate Root is just the parent entity | The Root is the sole entry point for mutations - it actively enforces every invariant on every state change |
| External code can hold references to internal entities if it doesn't modify them | Rule: external code never holds internal entity references. Pass IDs or DTOs across the aggregate boundary |
| Aggregates solve distributed transaction problems | Aggregates only solve intra-aggregate consistency. Cross-aggregate and cross-service consistency requires Saga Pattern or other distributed patterns |
| A Repository is just a DAO or data access layer | A Repository loads and persists the complete aggregate as a single unit - it is conceptually part of the domain model, not the infrastructure |

---

### 🚨 Failure Modes & Diagnosis

**1. Oversized Aggregate Causing Contention**

**Symptom:** High DB lock wait times on the `orders` table; `OptimisticLockException` flood in logs at peak hours; order confirmation throughput drops from 5000/sec to 200/sec.

**Root Cause:** The `Order` aggregate includes invoice history, customer preferences, and product details - all loaded and version-locked for every order modification.

**Diagnostic:**
```bash
# PostgreSQL: find contended tables
SELECT relname, n_deadlocks, n_lock_timeouts
FROM pg_stat_user_tables
WHERE relname = 'orders';

# Check JPA optimistic lock failures
grep "OptimisticLockException\|StaleObjectStateException" \
  application.log | wc -l
```

**Fix:** Extract product details (reference by ID), customer preferences (separate aggregate or value object), and invoice history (separate aggregate). The Order aggregate should contain only what must change in the same transaction as an order.

**Prevention:** Apply the single-responsibility principle to aggregates; if modifying field A and field B never happen in the same command, they don't belong in the same aggregate.

**2. Business Rules Scattered Outside the Aggregate**

**Symptom:** A bug causes orders with zero-price items to be confirmed. Post-mortem shows the validation existed in the controller but not in the aggregate - a new API endpoint bypassed the controller.

**Root Cause:** Invariants encoded in service or controller layer are bypassed by any call that doesn't go through that layer.

**Diagnostic:**
```bash
# Find validation logic outside aggregate roots
grep -rn "order.getStatus()\|if.*CONFIRMED\|if.*DRAFT" \
  src/main/java --include="*.java" | \
  grep -v "domain\|aggregate"  # should be zero results
```

**Fix:** Move every invariant check into the aggregate root methods. Delete all duplicate validation in services, controllers, and validators.

**Prevention:** Domain rule: if you can express a rule as "the aggregate is invalid if...", it belongs in the aggregate root.

**3. Missing Optimistic Locking on Aggregate Root**

**Symptom:** Concurrent requests to add items to the same order result in lost updates - two threads read version 5, both write version 6, one overwrites the other.

**Root Cause:** No `@Version` or equivalent optimistic-lock field on the aggregate root table row.

**Diagnostic:**
```bash
# Check if version column exists on aggregate table
psql -c "\d orders" | grep version
# Missing 'version' column = no optimistic lock
```

**Fix:**
```java
// Add @Version to aggregate root entity
@Entity
public class Order {
    @Version
    private Long version;  // JPA will throw on stale writes
}
// Now concurrent writes throw OptimisticLockException
// - handle with retry at application service level
```

**Prevention:** Always add a `version` column to every aggregate root table from day one.

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**
- `Domain-Driven Design` - the overarching framework within which the Aggregate pattern is defined
- `Bounded Context` - the strategic boundary within which aggregates are defined and owned
- `Value Objects` - immutable domain objects that compose aggregates alongside entities

**Builds On This (learn these next):**
- `Event Sourcing in Microservices` - stores aggregate state as a sequence of domain events instead of current state
- `CQRS in Microservices` - separates the aggregate's write model from optimised read models
- `Saga Pattern` - coordinates workflows that span multiple aggregates via events and compensations

**Alternatives / Comparisons:**
- `Transaction Script` - locates all logic in service methods rather than domain objects; simpler but doesn't scale with domain complexity

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ WHAT IT IS   │ A cluster of related objects with one     │
│              │ Root entity that enforces all invariants  │
├──────────────┼───────────────────────────────────────────┤
│ PROBLEM IT   │ Business rules scattered across services  │
│ SOLVES       │ which are bypassed and violated           │
├──────────────┼───────────────────────────────────────────┤
│ KEY INSIGHT  │ Rules enforced by design cannot be        │
│              │ bypassed. Rules enforced by convention    │
│              │ will be bypassed under pressure           │
├──────────────┼───────────────────────────────────────────┤
│ USE WHEN     │ Multiple related entities must change     │
│              │ together and invariants must hold at all  │
│              │ times                                     │
├──────────────┼───────────────────────────────────────────┤
│ AVOID WHEN   │ Simple CRUD - the aggregate is overkill   │
│              │ when there are no real business invariants│
├──────────────┼───────────────────────────────────────────┤
│ TRADE-OFF    │ Invariant safety vs eventual consistency  │
│              │ complexity for cross-aggregate workflows  │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "One boss, one transaction, no exceptions."│
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ Saga Pattern → Event Sourcing →           │
│              │ CQRS in Microservices                     │
└──────────────────────────────────────────────────────────┘
```


---

### 💎 Transferable Wisdom

**Reusable Engineering Principle:**
An aggregate is a transactional consistency boundary, not a grouping of related objects. Objects can be related without requiring transactional consistency - they belong in different aggregates if they can change independently. The correct aggregate boundary is the smallest set of objects that must change atomically to enforce a business invariant. Making aggregates too large increases contention; making them too small pushes invariant enforcement outside the transaction boundary.

**Where else this pattern appears:**
- **Database transactions:** A database transaction is an aggregate boundary at the persistence layer - all operations in the transaction must succeed or all fail, enforcing consistency across the included rows.
- **UI form validation:** A form that validates all fields before submission is an aggregate at the UI layer - the form is the consistency boundary that prevents partial state from being committed.
- **Shopping cart:** A Cart + CartItems aggregate enforces invariants (total within budget, items in stock) across all items together - the same pattern as a DDD aggregate applied to UI state.

---

### 💡 The Surprising Truth

The most common Aggregate design mistake is making aggregates too large. Eric Evans explicitly warns against this: large aggregates lead to contention (many concurrent operations lock the same aggregate root) and frequent optimistic concurrency conflicts. The guidance is to make aggregates as small as possible while still maintaining their invariants. In practice, most aggregates should contain only 1-3 domain objects. An Order aggregate containing Order + OrderLines is reasonable; an Order aggregate containing Order + Customer + Product catalogue is a design smell that will manifest as write throughput bottlenecks at scale.
---

### 🧠 Think About This Before We Continue

**Q1.** You have a social network where a `Post` aggregate contains `Comments`. The rule is: a post with more than 1000 comments locks down and allows no more comments. With 10,000 concurrent users commenting on a viral post, what concurrency problems arise with the aggregate's optimistic locking strategy? How would you redesign the aggregate boundary (perhaps making `Comment` its own aggregate) while still enforcing the 1000-comment rule?

*Hint:* Think about what optimistic locking does under high concurrency: many threads read the same aggregate version, each increments, only one write succeeds per cycle - the rest fail and retry. At 10,000 concurrent writers, retry storms can make the aggregate unwriteable at sustained rates. Explore whether making Comment its own aggregate (separate from Post) allows comments to be added without locking the Post aggregate, and how the 1000-comment rule could be enforced as an eventually consistent read-side check (count domain events, enforce on a domain service query) rather than a write-side aggregate invariant.

**Q2.** Your `Order` aggregate emits `OrderConfirmed` events consumed by `Inventory`, `Billing`, and `Notifications` aggregates in separate transactions. A network failure means the event is delivered to Inventory but never reaches Billing. The order is confirmed, inventory reserved, but the customer is never invoiced. Trace the complete failure scenario and design the idempotency and compensation strategy that makes this resilient to exactly this kind of partial failure.

*Hint:* Think about what partial delivery means with the outbox pattern: the Order aggregate writes OrderConfirmed to an outbox table in the same transaction as the order commit. A background relay reads the outbox and delivers to each consumer independently. Explore whether at-least-once delivery (relay retries until acknowledged) plus consumer-side idempotency (each consumer deduplicates by event ID before processing) makes the system resilient to partial delivery without requiring distributed transactions.

**Q3 (Design Trade-off):** Your checkout operation must atomically validate stock, reserve stock, create an Order aggregate, and clear the Cart aggregate. These span two aggregates (Cart and Order) and an external Inventory service. How do you design the checkout transaction to maintain aggregate consistency without a distributed transaction?

*Hint:* Think about which operations must be atomic vs which can be eventually consistent. Explore whether the Cart-to-Order transition can use the Saga pattern: create the Order atomically (one transaction), then publish OrderCreated event that triggers Cart clearing and Inventory reservation as compensatable steps. Identify what the inconsistency window looks like (briefly unconverted cart, briefly unreserved inventory) and whether the business can tolerate it.
