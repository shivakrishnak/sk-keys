---
layout: default
title: "Unit of Work Pattern"
parent: "Software Architecture Patterns"
nav_order: 733
permalink: /software-architecture/unit-of-work-pattern/
number: "733"
category: Software Architecture Patterns
difficulty: ★★★
depends_on: "Repository Pattern, Transaction Management, Domain Model"
used_by: "Entity Framework (built-in), Hibernate Session, Spring @Transactional"
tags: #advanced, #architecture, #transactions, #data-access, #consistency
---

# 733 — Unit of Work Pattern

`#advanced` `#architecture` `#transactions` `#data-access` `#consistency`

⚡ TL;DR — The **Unit of Work** tracks all objects modified during a business transaction, coordinates writing changes to the database in a single atomic operation, and resolves concurrency problems — so you never partially save a business operation.

| #733            | Category: Software Architecture Patterns                              | Difficulty: ★★★ |
| :-------------- | :-------------------------------------------------------------------- | :-------------- |
| **Depends on:** | Repository Pattern, Transaction Management, Domain Model              |                 |
| **Used by:**    | Entity Framework (built-in), Hibernate Session, Spring @Transactional |                 |

---

### 📘 Textbook Definition

The **Unit of Work** pattern, described by Martin Fowler in "Patterns of Enterprise Application Architecture," maintains a list of objects affected by a business transaction and coordinates the writing of changes and the resolution of concurrency problems. It tracks: **new objects** (to be INSERTed), **dirty objects** (modified, to be UPDATEd), and **removed objects** (to be DELETEd). At the end of a business transaction (commit): the Unit of Work issues all necessary database statements in a single batch. Benefits: (1) **Atomicity** — all changes committed or none (transaction semantics). (2) **Batching** — multiple changes issued in one database round-trip. (3) **Identity Map** — ensures the same object is loaded only once per unit of work (no duplicate in-memory objects). (4) **Deferred writes** — reads happen immediately; writes are deferred to commit. In modern Java: Hibernate's `Session` IS a Unit of Work. Entity Framework's `DbContext` IS a Unit of Work. Spring `@Transactional`: demarcates unit of work boundaries at the method level.

---

### 🟢 Simple Definition (Easy)

Shopping cart at the supermarket: you pick up items (modify objects in memory), walk around the store (more changes), then pay at checkout all at once (commit). You don't pay for each item as you pick it up. The cashier (database) processes everything at once. If your card is declined (transaction failure): nothing is purchased. Unit of Work: the shopping experience — all changes tracked, committed together, rolled back together on failure.

---

### 🔵 Simple Definition (Elaborated)

Without Unit of Work: every `repository.save(entity)` immediately hits the database. Transfer $100 from Account A to Account B: `accountRepo.save(accountA)` (debit A — success), then something fails before `accountRepo.save(accountB)` (credit B) — money is debited but never credited. With Unit of Work: modifications are tracked in memory. Both changes accumulated. At `unitOfWork.commit()`: both changes written in one transaction. If anything fails: transaction rolls back. Both accounts stay consistent. This is what `@Transactional` in Spring does — it wraps the method in a Unit of Work.

---

### 🔩 First Principles Explanation

**Change tracking, identity map, transaction boundaries, and Hibernate Session as UoW:**

```
UNIT OF WORK COMPONENTS:

  1. CHANGE TRACKING: tracks which objects have been modified.

     unitOfWork.registerNew(account)    // Newly created — needs INSERT.
     unitOfWork.registerDirty(account)  // Modified — needs UPDATE.
     unitOfWork.registerDeleted(account)// Marked for deletion — needs DELETE.

  2. IDENTITY MAP: ensures one instance per identity within one UoW.

     Account a1 = accountRepo.findById("ACC-1");  // Loads from DB. Stored in identity map.
     Account a2 = accountRepo.findById("ACC-1");  // Returns SAME instance from identity map.
     a1 == a2: true. // Same Java object. Modifications to a1 are seen in a2.
     No duplicate objects. No stale reads within same UoW.

  3. COMMIT: writes all tracked changes in a single transaction.

     unitOfWork.commit():
       BEGIN TRANSACTION
       INSERT INTO accounts ... (for all new objects)
       UPDATE accounts SET ... (for all dirty objects, only changed columns)
       DELETE FROM accounts ... (for all removed objects)
       COMMIT

  4. ROLLBACK: on any failure, all tracked changes discarded.
     No partial updates. Database returns to state before UoW started.

HIBERNATE SESSION AS UNIT OF WORK:

  Hibernate Session = the Unit of Work implementation.

  @Transactional  // Opens Session (Unit of Work) for the duration of this method.
  public void transferFunds(AccountId from, AccountId to, Money amount) {
      Account source = accountRepo.findById(from);   // Session: loaded, tracked.
      Account target = accountRepo.findById(to);     // Session: loaded, tracked.

      source.debit(amount);   // source: now "dirty" in Session (Hibernate tracks this).
      target.credit(amount);  // target: now "dirty" in Session.

      // NO explicit save() needed! Hibernate detects changes automatically.
      // At method end: @Transactional commits Session.
      // Session: issues UPDATE for source AND UPDATE for target in one transaction.
      // If exception thrown: @Transactional rolls back. Neither account changes.
  }

  // This is "dirty checking": Hibernate compares entity state on load vs. state at commit.
  // Changed fields → UPDATE statement. Unchanged fields → no UPDATE.

CHANGE TRACKING INTERNALS (Hibernate):

  On load: Hibernate stores a "hydrated state" (snapshot of entity at load time).
  At commit (flush):
    Hibernate: iterates all tracked entities.
    For each entity: compares current state to hydrated state.
    Differences found: add to "dirty queue."
    Execute UPDATE for dirty entities: only changed columns (dynamic update).

  SNAPSHOT STORAGE:
    Every loaded entity: one extra copy of field values.
    Memory cost: 2× the entity data for tracked entities.
    For large result sets (1000+ entities): memory cost is significant.

UNIT OF WORK IN SPRING:

  @Transactional: method-level UoW boundary.

  @Service
  public class OrderService {

      @Transactional  // UoW: START. Opens Hibernate Session/JDBC transaction.
      public void fulfillOrder(OrderId orderId) {
          // All repository calls within this method: same Hibernate Session (UoW).
          Order order = orderRepository.findById(orderId);
          Inventory inventory = inventoryRepository.findByProductId(order.productId());

          order.markFulfilled();      // Order: dirty.
          inventory.decrementStock(); // Inventory: dirty.

          // No explicit save() calls. Hibernate dirty-checks and writes both.
      }  // UoW: COMMIT. Hibernate flushes changes. Transaction committed.
      // If any exception thrown before commit: rollback. Neither order nor inventory changes.

  @Transactional(readOnly = true)  // UoW: no dirty checking. Performance optimization for reads.
  public OrderDTO getOrder(OrderId orderId) {
      return orderRepository.findById(orderId).map(OrderDTO::from).orElseThrow();
  }
```

---

### ❓ Why Does This Exist (Why Before What)

WITHOUT Unit of Work:

- Partial commits: debit Account A succeeds, credit Account B fails → money disappears
- Multiple `save()` calls per operation: multiple round-trips to database per business action
- Same entity loaded twice: two independent objects, modifications to one not reflected in other

WITH Unit of Work:
→ Atomic commits: all or nothing — no partial state
→ Batched writes: one round-trip at commit, not one per `save()` call
→ Identity map: same object loaded once; all references see the same state

---

### 🧠 Mental Model / Analogy

> A notary preparing a contract: both parties make changes and requests throughout the meeting (modifications to in-memory state). The notary tracks every change on paper. At the end of the meeting: all changes are finalized together and officially signed (commit). If either party refuses to sign (exception): nothing is official, all changes reverted (rollback). You don't officially sign each sentence as you write it — you review and sign the final document as a whole.

"Notary tracking changes" = Unit of Work change tracking
"Changes on paper" = dirty/new/deleted object registry
"Official signing at the end" = commit (all changes written to DB atomically)
"Either party refuses to sign" = exception causes rollback

---

### ⚙️ How It Works (Mechanism)

```
UNIT OF WORK LIFECYCLE:

  1. Begin: open transaction, start Session (identity map + change tracker).
  2. Load entities: fetched from DB, hydrated state stored.
  3. Modify: entity fields changed in memory. Session detects dirtiness.
  4. More loads/modifications: all within same Session.
  5. Flush/Commit: Session issues all needed SQL (INSERT/UPDATE/DELETE) in transaction.
  6. Commit: transaction committed. DB consistent.
  7. Rollback (on exception): transaction rolled back. No DB changes.
```

---

### 🔄 How It Connects (Mini-Map)

```
Repository Pattern (domain-centric data access abstraction)
        │
        ▼ (coordinates multiple repository writes into one transaction)
Unit of Work ◄──── (you are here)
(tracks changes, batches writes, ensures atomicity)
        │
        ├── Hibernate Session: the JPA implementation of Unit of Work
        ├── Entity Framework DbContext: .NET's Unit of Work implementation
        └── @Transactional: Spring's annotation that demarcates Unit of Work boundaries
```

---

### 💻 Code Example

```java
// Custom Unit of Work (for non-Hibernate scenarios):
public interface UnitOfWork {
    OrderRepository orders();
    CustomerRepository customers();
    void commit();
    void rollback();
}

@Component
public class JpaUnitOfWork implements UnitOfWork {
    @PersistenceContext
    private EntityManager em;

    @Override public OrderRepository orders() { return new JpaOrderRepository(em); }
    @Override public CustomerRepository customers() { return new JpaCustomerRepository(em); }
    @Override public void commit() { em.getTransaction().commit(); }
    @Override public void rollback() { em.getTransaction().rollback(); }
}

// Usage (explicit UoW — useful when you want explicit control):
@Service
public class OrderService {
    private final UnitOfWork uow;

    public void placeAndConfirm(PlaceOrderCommand cmd) {
        try {
            Order order = Order.create(cmd.customerId(), cmd.items());
            uow.orders().save(order);

            Customer customer = uow.customers().findById(cmd.customerId()).orElseThrow();
            customer.recordOrderPlaced();  // Dirty — tracked by UoW.

            uow.commit();  // Both order INSERT and customer UPDATE in one transaction.
        } catch (Exception e) {
            uow.rollback();
            throw e;
        }
    }
}
// In Spring: just use @Transactional on the method — Spring manages the UoW lifecycle.
```

---

### ⚠️ Common Misconceptions

| Misconception                                                              | Reality                                                                                                                                                                                                                                                                                                                                                                                                             |
| -------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Unit of Work and Transaction are the same thing                            | A transaction is a database concept (ACID guarantee). Unit of Work is an application pattern (change tracking, identity map, batched writes). A transaction is one tool the Unit of Work uses at commit time. Unit of Work can exist without a database transaction (e.g., writing to a file). Most commonly: one transaction per Unit of Work, but they're conceptually distinct                                   |
| Every `repository.save()` immediately writes to the database in Spring JPA | With `@Transactional` + Hibernate: `save()` (or simply modifying an entity) does NOT immediately write to the database. Hibernate defers writes to the end of the transaction (flush). Exception: explicit `em.flush()` forces immediate write. This is why you can modify multiple entities within one `@Transactional` method and have them all written atomically                                                |
| You must explicitly call `save()` after every modification in Hibernate    | In Hibernate's "managed" mode (within a transaction), loaded entities are automatically tracked. Modify a field on a loaded entity → Hibernate's dirty checking detects it at flush time → issues UPDATE automatically. No `repository.save(entity)` needed. However: explicitly calling `save()` is harmless and makes the intent clearer. Spring Data JPA convention often includes explicit `save()` for clarity |

---

### 🔥 Pitfalls in Production

**Open Session in View — Unit of Work spanning HTTP request causes N+1 and long transactions:**

```
SCENARIO: Spring Boot application.
  Default (in older Spring Boot versions): OpenSessionInViewInterceptor enabled.

  WHAT OPEN SESSION IN VIEW DOES:
    Opens Hibernate Session at the START of the HTTP request.
    Closes Session at the END of the HTTP request (after view renders).

  PROBLEM — Lazy loading during view rendering:
    Controller:
      @GetMapping("/orders/{id}")
      public String getOrder(@PathVariable Long id, Model model) {
          Order order = orderRepository.findById(id);  // Loads Order. Items: lazy (not loaded yet).
          model.addAttribute("order", order);
          return "order-view";  // Thymeleaf template renders here.
      }

    Thymeleaf template:
      <th:each="item : ${order.items}">  <!-- Triggers lazy load of items. -->
      <!-- Hibernate: SELECT * FROM order_items WHERE order_id = ?  -->
      <!-- This happens during view rendering, OUTSIDE the service method. -->
      <!-- OSIV: session still open, so lazy load works. -->

  SURFACE PROBLEM: Works. No LazyInitializationException.

  HIDDEN PROBLEMS:
    1. N+1: 20 orders on a list page, each lazily loads items = 21 queries.
       These extra queries happen in the View layer — invisible to service code.

    2. Long transactions: DB transaction open for entire request duration (including view rendering).
       Controller: 10ms. Serialization: 50ms. Total: transaction holds DB connection 60ms.
       At 1000 concurrent requests: 1000 connections held 60ms = connection pool exhausted.

    3. Business logic in views: OSIV enables lazy loading in views = views can trigger DB queries.
       Coupling view layer to database.

BAD: spring.jpa.open-in-view=true (default in older Spring Boot versions):
  # Hides LazyInitializationException. Enables N+1 in view layer. Long transactions.

FIX: Disable OSIV. Eagerly load what's needed in the service layer:
  # application.properties:
  spring.jpa.open-in-view=false
  # LazyInitializationException will now surface if view tries to lazy-load.
  # This is GOOD: forces proper data loading in service layer.

  # Service: load what the view needs explicitly:
  @Transactional(readOnly = true)
  public OrderDetailDTO getOrderWithItems(Long id) {
      Order order = orderRepository.findByIdWithItems(id);  // Eager JOIN fetch.
      return OrderDetailDTO.from(order);  // Map to DTO WITHIN transaction.
  }

  # Spring Data:
  @EntityGraph(attributePaths = {"items", "shippingAddress"})
  Optional<Order> findByIdWithItems(Long id);
  // Or: @Query("SELECT o FROM Order o JOIN FETCH o.items WHERE o.id = :id")

  # Controller: receives DTO (no Hibernate entities). Transaction closed in service.
  @GetMapping("/orders/{id}")
  public String getOrder(@PathVariable Long id, Model model) {
      model.addAttribute("order", orderService.getOrderWithItems(id));
      // DTO: no lazy loading. No Hibernate session needed. View just renders data.
      return "order-view";
  }
```

---

### 🔗 Related Keywords

- `Repository Pattern` — Unit of Work coordinates multiple repository writes atomically
- `@Transactional` — Spring's way of demarcating Unit of Work boundaries
- `Hibernate Session` — JPA's built-in Unit of Work implementation
- `Identity Map` — prevents loading the same object twice in one Unit of Work
- `Dirty Checking` — Hibernate's mechanism for detecting modified entities within a Session

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ KEY IDEA     │ Track all changes during a business      │
│              │ operation; write them all atomically     │
│              │ at commit. One transaction, no partial   │
│              │ state, batch writes.                     │
├──────────────┼───────────────────────────────────────────┤
│ USE WHEN     │ Multiple entities must change together   │
│              │ atomically; Hibernate (built-in);        │
│              │ @Transactional (Spring)                 │
├──────────────┼───────────────────────────────────────────┤
│ AVOID WHEN   │ Read-only operations (use readOnly=true);│
│              │ very long-running processes (keep UoW    │
│              │ short; use batch processing instead)     │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "Shopping: pick up items all session,   │
│              │  pay once at checkout."                 │
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ Repository Pattern → Hibernate Session  │
│              │ → @Transactional → Dirty Checking →    │
│              │ Entity Framework DbContext              │
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** A service method annotated with `@Transactional` calls `orderService.findById()` which is annotated with `@Transactional(readOnly = true)`. Spring uses a proxy-based mechanism for transactions. Does the inner `findById()` call create a new transaction or join the outer one? What is the `propagation` setting that controls this? If the inner method runs in a read-only transaction and the outer method modifies data, what happens?

**Q2.** Hibernate's dirty checking stores a snapshot of each loaded entity. Your service loads 5,000 entities in a single transaction (reporting job). Memory impact: each entity is 1KB of data → 5MB for entities + 5MB for snapshots = 10MB total. For 100 concurrent such jobs: 1GB of memory for snapshots alone. How do you solve this: what Hibernate feature prevents dirty checking for bulk read operations, and what is the trade-off?
